"""
SIGNATURE VMAKE — Inference Engine & Biometric Verifier.

Implements the SignatureVerificationModel interface for Siamese Deep Metric Learning,
with unified factory dispatch for all three model tracks:
- Model A: Classical scikit-learn (SVM / Random Forest)
- Model B: Hugging Face Vision Transformer (ViT)
- Model C: Siamese Deep Neural Network (Metric Learning ResNet)
"""

import sys
import os
import json
from pathlib import Path
from typing import Union, Dict, Any, Optional, List
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.model_interface import SignatureVerificationModel, VerificationOutput
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.models.siamese_network import SiameseSignatureNet


class SignatureVerifier(SignatureVerificationModel):
    """
    Production Siamese Deep Neural Verifier conforming to SignatureVerificationModel interface.
    Backward-compatible with existing enrollment and verification services.
    """

    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        threshold: Optional[float] = None,
        device: Optional[str] = None
    ):
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self.preprocessor = SignaturePreprocessor(target_size=(224, 224))

        # 1. Resolve Checkpoint Priority: VMAKE Champion > v4 Champion > Final Champion > Champion > Baseline
        vmake_path = Path("artifacts/models/vmake_champion_model.pt")
        v4_path = Path("artifacts/models/v4_champion_model.pt")
        final_champ_path = Path("artifacts/models/final_champion_model.pt")
        champ_path = Path("artifacts/models/champion_siamese_model.pt")
        base_path = Path("artifacts/models/best_siamese_model.pt")

        if checkpoint_path is not None:
            self.checkpoint_path = Path(checkpoint_path)
        elif vmake_path.exists():
            self.checkpoint_path = vmake_path
        elif v4_path.exists():
            self.checkpoint_path = v4_path
        elif final_champ_path.exists():
            self.checkpoint_path = final_champ_path
        elif champ_path.exists():
            self.checkpoint_path = champ_path
        elif base_path.exists():
            self.checkpoint_path = base_path
        else:
            raise FileNotFoundError("No Siamese model checkpoint found in artifacts/models/")

        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        embedding_dim = checkpoint.get("embedding_dim", 256)
        backbone = checkpoint.get("backbone", "resnet18")
        model_arch = str(checkpoint.get("model_architecture", "")).lower()

        # 2. Resolve Threshold and Model Version
        resolved_threshold = 0.5924
        self.gallery_threshold = 0.6312
        model_version = "1.0.0-vmake-champion" if "vmake" in str(self.checkpoint_path).lower() else "4.0.0-champion"
        vmake_thresh_file = Path("artifacts/models/vmake_champion_threshold.json")
        v4_thresh_file = Path("artifacts/models/v4_champion_threshold.json")
        final_config_file = Path("artifacts/models/final_champion_config.json")
        champ_config_file = Path("artifacts/models/champion_config.json")
        calib_file = Path("artifacts/models/calibrated_threshold.json")

        if threshold is not None:
            resolved_threshold = float(threshold)
        elif vmake_thresh_file.exists() and "vmake" in str(self.checkpoint_path).lower():
            try:
                with open(vmake_thresh_file, "r") as f:
                    tdata = json.load(f)
                    resolved_threshold = float(tdata.get("calibrated_threshold", 0.5924))
                    self.gallery_threshold = float(tdata.get("gallery_threshold", resolved_threshold))
                    model_version = tdata.get("model_version", "1.0.0-vmake-champion")
            except Exception:
                resolved_threshold = float(checkpoint.get("calibrated_threshold", 0.5924))
                model_version = "1.0.0-vmake-champion"
        elif v4_thresh_file.exists() and "v4" in str(self.checkpoint_path).lower():
            try:
                with open(v4_thresh_file, "r") as f:
                    tdata = json.load(f)
                    resolved_threshold = float(tdata.get("single_pair_threshold", 0.5924))
                    self.gallery_threshold = float(tdata.get("gallery_threshold", 0.6312))
                    model_version = "4.0.0-champion"
            except Exception:
                resolved_threshold = float(checkpoint.get("optimal_threshold", 0.5924))
        elif final_config_file.exists() and "final_champion" in str(self.checkpoint_path).lower():
            try:
                with open(final_config_file, "r") as f:
                    cdata = json.load(f)
                    resolved_threshold = float(cdata.get("frozen_calibrated_threshold", cdata.get("frozen_threshold", 0.7060)))
                    model_version = cdata.get("model_version", "3.0.0-final-champion")
            except Exception:
                resolved_threshold = float(checkpoint.get("calibrated_threshold", 0.7060))
        elif champ_config_file.exists() and "champion" in str(self.checkpoint_path).lower():
            try:
                with open(champ_config_file, "r") as f:
                    cdata = json.load(f)
                    resolved_threshold = float(cdata.get("frozen_threshold", 0.7382))
                    model_version = cdata.get("model_version", "2.0.0-champion")
            except Exception:
                resolved_threshold = float(checkpoint.get("optimal_threshold", 0.7382))
        elif calib_file.exists():
            try:
                with open(calib_file, "r") as f:
                    resolved_threshold = float(json.load(f).get("calibrated_threshold", 0.7766))
            except Exception:
                resolved_threshold = float(checkpoint.get("optimal_threshold", 0.7766))
        else:
            resolved_threshold = float(checkpoint.get("optimal_threshold", 0.7500))

        chosen_model_name = "VMAKE_Siamese_Champion" if "vmake" in str(self.checkpoint_path).lower() else "Siamese_ResNet_Champion"
        super().__init__(
            model_name=chosen_model_name,
            model_version=model_version,
            model_type="SIAMESE_RESNET",
            threshold=resolved_threshold,
            review_margin=0.05
        )
        self.default_threshold = resolved_threshold

        # 3. Instantiate Neural Architecture
        if "resnet" in model_arch:
            from ml.models.architectures import SiameseResNet18
            self.model = SiameseResNet18(embedding_dim=embedding_dim, in_channels=1)
            self.model.default_threshold = self.default_threshold
        else:
            self.model = SiameseSignatureNet(
                embedding_dim=embedding_dim,
                default_threshold=self.default_threshold,
                backbone=backbone
            )

        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        elif isinstance(checkpoint, dict):
            self.model.load_state_dict(checkpoint)

        self.model.to(self.device)
        self.model.eval()

    def extract_features(self, image: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """Extracts 256-d unit hypersphere embedding."""
        return self.extract_embedding(image)

    def extract_embedding(
        self,
        image_input: Union[str, Path, np.ndarray, Image.Image]
    ) -> np.ndarray:
        """
        Generates a 256-dimensional L2-normalized feature embedding for a signature.
        Used for database enrollment and metric comparison.
        """
        tensor = self.preprocessor.preprocess(image_input, as_tensor=True).to(self.device)
        if tensor.dim() == 3:
            tensor = tensor.unsqueeze(0)
        with torch.no_grad():
            forward_fn = getattr(self.model, "forward_one", getattr(self.model, "forward_once", None))
            embedding = forward_fn(tensor)
        return embedding.squeeze(0).cpu().numpy()

    def compute_distance(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Euclidean distance between two unit embeddings."""
        return float(np.linalg.norm(feat1 - feat2))

    def compute_similarity(self, distance: float) -> float:
        """Non-linear metric similarity S = 1 / (1 + D)."""
        return float(1.0 / (1.0 + distance))

    def verify(
        self,
        reference_input: Optional[Union[str, Path, np.ndarray, Image.Image]] = None,
        submitted_input: Optional[Union[str, Path, np.ndarray, Image.Image]] = None,
        threshold: Optional[float] = None,
        ref_image: Optional[Union[str, Path, np.ndarray, Image.Image]] = None,
        query_image: Optional[Union[str, Path, np.ndarray, Image.Image]] = None,
        **kwargs
    ) -> VerificationOutput:
        """
        Verification call returning VerificationOutput (supporting both attribute and dictionary access).
        """
        ref = reference_input if reference_input is not None else ref_image
        sub = submitted_input if submitted_input is not None else query_image
        if ref is None or sub is None:
            raise ValueError("Both reference and query/submitted images must be provided to verify().")

        thresh = threshold if threshold is not None else self.default_threshold

        t1 = self.preprocessor.preprocess(ref, as_tensor=True).to(self.device)
        t2 = self.preprocessor.preprocess(sub, as_tensor=True).to(self.device)
        if t1.dim() == 3:
            t1 = t1.unsqueeze(0)
        if t2.dim() == 3:
            t2 = t2.unsqueeze(0)

        with torch.no_grad():
            emb1, emb2 = self.model.forward(t1, t2)
            distance = float(self.model.compute_distance(emb1, emb2).item())
            similarity = float(self.model.compute_similarity(torch.tensor([distance])).item())

        # Decision Logic with Borderline Manual Review Buffer
        manual_review_buffer = self.review_margin
        if similarity >= thresh:
            decision = "VERIFIED"
            risk_level = "LOW"
        elif similarity >= (thresh - manual_review_buffer):
            decision = "MANUAL_REVIEW"
            risk_level = "MEDIUM"
        else:
            decision = "REJECTED"
            risk_level = "HIGH"

        return VerificationOutput(
            similarity_score=round(similarity, 4),
            distance=round(distance, 4),
            decision=decision,
            confidence=round(self.calculate_confidence(similarity, thresh), 4),
            model_name=self.model_name,
            model_version=self.model_version,
            model_type=self.model_type,
            threshold_used=round(thresh, 4),
            reference_count=1,
            embedding_a=emb1.squeeze(0).cpu().tolist(),
            embedding_b=emb2.squeeze(0).cpu().tolist(),
            metadata={
                "risk_recommendation": risk_level,
                "review_margin": manual_review_buffer
            }
        )

    def verify_pair(
        self,
        ref_image: Union[str, Path, np.ndarray, Image.Image],
        query_image: Union[str, Path, np.ndarray, Image.Image],
        threshold: Optional[float] = None
    ) -> VerificationOutput:
        return self.verify(ref_image, query_image, threshold)



def get_model_verifier(
    model_type: str = "transformer",
    checkpoint_path: Optional[str] = None,
    threshold: Optional[float] = None,
    device: Optional[str] = None
) -> SignatureVerificationModel:
    """
    Factory function returning a concrete SignatureVerificationModel instance.
    Supports VMAKE Dual-Track production architecture:
    - 'transformer' / 'track_b': Hugging Face Vision Transformer (Default Production)
    - 'sklearn' / 'classical' / 'track_a': Classical SVM with 264-d HOG/morphological features
    - 'siamese' / 'track_c': Legacy Siamese ResNet (retained for backward compatibility)
    """
    m_type = model_type.lower()
    if m_type in ("transformer", "vit", "track_b"):
        from ml.models.transformer_signature_model import VisionTransformerVerifier
        ckpt = checkpoint_path or "artifacts/models/transformer_signature_model.pt"
        return VisionTransformerVerifier(checkpoint_path=ckpt, threshold=threshold or 0.7313, device=device)
    elif m_type in ("svm", "classical_svm", "sklearn", "classical", "track_a"):
        from ml.baselines.classical_classifier import ClassicalSklearnVerifier
        ckpt = checkpoint_path or "artifacts/models/classical_svm_model.joblib"
        return ClassicalSklearnVerifier(checkpoint_path=ckpt, threshold=threshold or 0.3636)
    elif m_type in ("random_forest", "rf", "forest"):
        from ml.baselines.classical_classifier import ClassicalSklearnVerifier
        ckpt = checkpoint_path or "artifacts/models/classical_random_forest_model.joblib"
        return ClassicalSklearnVerifier(checkpoint_path=ckpt, threshold=threshold or 0.4264)
    elif m_type in ("logistic", "logistic_regression", "lr"):
        from ml.baselines.classical_classifier import ClassicalSklearnVerifier
        ckpt = checkpoint_path or "artifacts/models/classical_logistic_model.joblib"
        return ClassicalSklearnVerifier(checkpoint_path=ckpt, threshold=threshold or 0.2015)
    elif m_type in ("siamese", "resnet", "champion", "track_c", "neural"):
        return SignatureVerifier(checkpoint_path=checkpoint_path, threshold=threshold, device=device)
    else:
        raise ValueError(f"Unknown model_type: '{model_type}'. Choose from 'transformer', 'svm', 'random_forest', 'logistic'.")

