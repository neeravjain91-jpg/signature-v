"""
SIGNATURE VMAKE — Unified Model Interface Architecture.

Defines the abstract contract for all signature verification models in the platform:
- Model A: Classical scikit-learn Baseline (SVM / Random Forest on HOG/Morphological features)
- Model B: Vision Transformer (Hugging Face ViT)
- Model C: Siamese Deep Neural Network (Metric Learning ResNet)

This interface ensures complete decoupling between the ML inference models and
the FastAPI backend, allowing models to be replaced, upgraded, or benchmarked
without altering business logic or database layers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Union, List, Dict, Any, Optional
import numpy as np
from PIL import Image


@dataclass
class VerificationOutput:
    """Standardized output schema for all signature verification models."""
    similarity_score: float
    distance: float
    decision: str  # "VERIFIED", "REJECTED", "MANUAL_REVIEW"
    confidence: float
    model_name: str
    model_version: str
    model_type: str  # "CLASSICAL_SKLEARN", "VISION_TRANSFORMER", "SIAMESE_RESNET"
    threshold_used: float
    reference_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "similarity_score": round(float(self.similarity_score), 4),
            "distance": round(float(self.distance), 4),
            "decision": self.decision,
            "confidence": round(float(self.confidence), 4),
            "model_name": self.model_name,
            "model_version": self.model_version,
            "model_type": self.model_type,
            "threshold_used": round(float(self.threshold_used), 4),
            "reference_count": self.reference_count,
            "metadata": self.metadata,
        }


class SignatureVerificationModel(ABC):
    """
    Polymorphic abstract base class for offline signature verification models.
    Enforces a uniform lifecycle: feature extraction, metric computation,
    confidence calibration, and gallery evidence aggregation.
    """

    def __init__(
        self,
        model_name: str,
        model_version: str,
        model_type: str,
        threshold: float,
        review_margin: float = 0.05
    ):
        self.model_name = model_name
        self.model_version = model_version
        self.model_type = model_type
        self.threshold = float(threshold)
        self.review_margin = float(review_margin)

    @abstractmethod
    def extract_features(self, image: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """
        Extracts a 1-D numerical feature representation/embedding from an input signature image.
        Returns a normalized 1-D numpy array.
        """
        pass

    @abstractmethod
    def compute_distance(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Computes metric distance between two feature vectors."""
        pass

    @abstractmethod
    def compute_similarity(self, distance: float) -> float:
        """Transforms a distance metric into a normalized similarity score in [0.0, 1.0]."""
        pass

    def calculate_decision(self, similarity: float, threshold: Optional[float] = None) -> str:
        """
        Computes 3-way banking verification decision:
        - VERIFIED: similarity >= threshold + margin
        - MANUAL_REVIEW: threshold - margin <= similarity < threshold + margin
        - REJECTED: similarity < threshold - margin
        """
        t = self.threshold if threshold is None else float(threshold)
        high_bound = min(1.0, t + self.review_margin)
        low_bound = max(0.0, t - self.review_margin)

        if similarity >= high_bound:
            return "VERIFIED"
        elif similarity < low_bound:
            return "REJECTED"
        else:
            return "MANUAL_REVIEW"

    def calculate_confidence(self, similarity: float, threshold: Optional[float] = None) -> float:
        """
        Calculates verification confidence based on distance from the decision boundary.
        Scales from 0.5 (at threshold boundary) to 1.0 (far from boundary).
        """
        t = self.threshold if threshold is None else float(threshold)
        delta = abs(similarity - t)
        max_delta = max(t, 1.0 - t) if max(t, 1.0 - t) > 0 else 0.5
        conf = 0.5 + 0.5 * min(1.0, (delta / max_delta))
        return float(np.clip(conf, 0.0, 1.0))

    def verify_pair(
        self,
        ref_image: Union[str, Path, np.ndarray, Image.Image],
        query_image: Union[str, Path, np.ndarray, Image.Image],
        threshold: Optional[float] = None
    ) -> VerificationOutput:
        """
        Executes standard pairwise signature verification between a single reference
        specimen and a questioned query specimen.
        """
        thresh = self.threshold if threshold is None else float(threshold)
        feat_ref = self.extract_features(ref_image)
        feat_query = self.extract_features(query_image)

        distance = self.compute_distance(feat_ref, feat_query)
        similarity = self.compute_similarity(distance)
        decision = self.calculate_decision(similarity, thresh)
        confidence = self.calculate_confidence(similarity, thresh)

        return VerificationOutput(
            similarity_score=float(similarity),
            distance=float(distance),
            decision=decision,
            confidence=float(confidence),
            model_name=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            threshold_used=float(thresh),
            reference_count=1,
            metadata={
                "ref_feature_dim": int(feat_ref.shape[0]),
                "query_feature_dim": int(feat_query.shape[0]),
            }
        )

    def verify_gallery(
        self,
        gallery_images: List[Union[str, Path, np.ndarray, Image.Image]],
        query_image: Union[str, Path, np.ndarray, Image.Image],
        strategy: str = "max_similarity",
        threshold: Optional[float] = None
    ) -> VerificationOutput:
        """
        Verifies a questioned signature against a customer reference gallery (multiple specimens).
        Supported aggregation strategies:
        - 'max_similarity': Optimistic matching against best registered specimen
        - 'mean_similarity': Average similarity across all registered specimens
        - 'top_k_mean': Mean of top-k highest similarity scores (k=min(2, N))
        - 'centroid_distance': Distance between query embedding and average gallery embedding
        """
        if not gallery_images:
            raise ValueError("Gallery must contain at least one reference signature specimen.")

        thresh = self.threshold if threshold is None else float(threshold)
        feat_query = self.extract_features(query_image)
        gallery_feats = [self.extract_features(img) for img in gallery_images]

        distances = [self.compute_distance(gf, feat_query) for gf in gallery_feats]
        similarities = [self.compute_similarity(d) for d in distances]

        if strategy == "max_similarity":
            best_idx = int(np.argmax(similarities))
            agg_sim = float(similarities[best_idx])
            agg_dist = float(distances[best_idx])
        elif strategy == "mean_similarity":
            agg_sim = float(np.mean(similarities))
            agg_dist = float(np.mean(distances))
        elif strategy == "top_k_mean":
            k = min(2, len(similarities))
            top_k_indices = np.argsort(similarities)[-k:]
            agg_sim = float(np.mean([similarities[i] for i in top_k_indices]))
            agg_dist = float(np.mean([distances[i] for i in top_k_indices]))
        elif strategy == "centroid_distance":
            centroid = np.mean(gallery_feats, axis=0)
            norm = np.linalg.norm(centroid)
            if norm > 1e-7:
                centroid = centroid / norm
            agg_dist = self.compute_distance(centroid, feat_query)
            agg_sim = self.compute_similarity(agg_dist)
        else:
            raise ValueError(f"Unsupported gallery aggregation strategy: {strategy}")

        decision = self.calculate_decision(agg_sim, thresh)
        confidence = self.calculate_confidence(agg_sim, thresh)

        return VerificationOutput(
            similarity_score=float(agg_sim),
            distance=float(agg_dist),
            decision=decision,
            confidence=float(confidence),
            model_name=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            threshold_used=float(thresh),
            reference_count=len(gallery_images),
            metadata={
                "strategy": strategy,
                "all_similarities": [round(float(s), 4) for s in similarities],
                "all_distances": [round(float(d), 4) for d in distances],
            }
        )
