"""
SIGNATURE VMAKE — Classical scikit-learn Baseline Classifier.

Implements SignatureVerificationModel using scikit-learn:
- Engineered features: 264-d HOG, grid densities, projection profiles, morphology
- Metric learning / Decision head: Support Vector Machine (SVM) or Random Forest
- Fallback: Cosine/Euclidean similarity on normalized engineered vectors
"""

import sys
from pathlib import Path
from typing import Union, Optional, Any
import numpy as np
from PIL import Image
import joblib

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.model_interface import SignatureVerificationModel, VerificationOutput
from ml.baselines.feature_extractor import ClassicalFeatureExtractor


class ClassicalSklearnVerifier(SignatureVerificationModel):
    """
    Classical Machine Learning Baseline implementing the SignatureVerificationModel interface.
    Extracts 264-d computer-vision features and applies scikit-learn estimators or metric distance.
    """

    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        threshold: float = 0.65,
        model_version: str = "1.0.0-sklearn-svm"
    ):
        super().__init__(
            model_name="Classical_SVM_Baseline",
            model_version=model_version,
            model_type="CLASSICAL_SKLEARN",
            threshold=threshold,
            review_margin=0.06
        )
        self.feature_extractor = ClassicalFeatureExtractor()
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.classifier = None
        self.scaler = None

        if self.checkpoint_path and self.checkpoint_path.exists():
            self._load_checkpoint()

        self.default_threshold = self.threshold
        self.gallery_threshold = round(min(1.0, self.threshold + 0.04), 4)

    def _load_checkpoint(self):
        """Loads trained scikit-learn pipeline from disk."""
        data = joblib.load(self.checkpoint_path)
        if isinstance(data, dict):
            self.classifier = data.get("classifier")
            self.scaler = data.get("scaler")
            self.threshold = float(data.get("calibrated_threshold", self.threshold))
            self.model_version = str(data.get("model_version", self.model_version))
        else:
            self.classifier = data

    def extract_features(self, image: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """Extracts 264-d unit-normalized feature vector."""
        return self.feature_extractor.extract(image)

    extract_embedding = extract_features


    def compute_distance(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Computes Euclidean distance between unit-normalized feature vectors."""
        n1 = feat1 / (np.linalg.norm(feat1) + 1e-8)
        n2 = feat2 / (np.linalg.norm(feat2) + 1e-8)
        return float(np.linalg.norm(n1 - n2))

    def compute_similarity(self, distance: float) -> float:
        """
        Converts Euclidean distance on unit hypersphere (range [0.0, 2.0])
        into normalized similarity in [0.0, 1.0].
        """
        return float(np.clip(1.0 - (distance / 2.0), 0.0, 1.0))

    def predict_pair_probability(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """
        If a trained scikit-learn classifier exists, predicts calibrated probability P(genuine).
        Otherwise falls back to compute_similarity(compute_distance).
        """
        if self.classifier is not None:
            n1 = feat1 / (np.linalg.norm(feat1) + 1e-8)
            n2 = feat2 / (np.linalg.norm(feat2) + 1e-8)
            diff = np.abs(n1 - n2)
            prod = n1 * n2
            d = float(np.linalg.norm(n1 - n2))
            cos = float(np.dot(n1, n2))
            pair_feat = np.concatenate([diff, prod, [d, cos]]).reshape(1, -1)
            if self.scaler is not None:
                pair_feat = self.scaler.transform(pair_feat)

            if hasattr(self.classifier, "predict_proba"):
                prob = self.classifier.predict_proba(pair_feat)[0, 1]
                return float(prob)
            elif hasattr(self.classifier, "decision_function"):
                score = self.classifier.decision_function(pair_feat)[0]
                # Sigmoid scaling
                return float(1.0 / (1.0 + np.exp(-score)))

        dist = self.compute_distance(feat1, feat2)
        return self.compute_similarity(dist)

    def verify_pair(
        self,
        ref_image: Union[str, Path, np.ndarray, Image.Image],
        query_image: Union[str, Path, np.ndarray, Image.Image],
        threshold: Optional[float] = None
    ) -> VerificationOutput:
        thresh = self.threshold if threshold is None else float(threshold)
        feat_ref = self.extract_features(ref_image)
        feat_query = self.extract_features(query_image)

        distance = self.compute_distance(feat_ref, feat_query)
        similarity = self.predict_pair_probability(feat_ref, feat_query)
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
