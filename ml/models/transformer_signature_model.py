"""
SIGNATURE VMAKE — Vision Transformer (ViT) Signature Verification Model.

Implements Hugging Face Transformers for Computer Vision:
Signature Image
    ↓
AutoImageProcessor / SignaturePreprocessor (224x224, 3 channels)
    ↓
Hugging Face Vision Transformer (ViTModel: facebook/deit-tiny-patch16-224 or ViTConfig)
    ↓
Multi-Head Self-Attention Tokens ([CLS] token + Patch Embeddings)
    ↓
Projection Head (Linear -> LayerNorm -> GELU -> Linear)
    ↓
L2-Normalized Signature Embedding (256-d hypersphere, ||u|| = 1.0)
    ↓
Pairwise Metric / Distance / Similarity Computation
"""

import sys
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Any
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F

from transformers import ViTModel, ViTConfig, AutoImageProcessor

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.model_interface import SignatureVerificationModel, VerificationOutput
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor


class VisionTransformerSignatureNet(nn.Module):
    """
    Hugging Face Vision Transformer (ViT) adapted for offline signature verification.
    Projects spatial stroke patch representations to a 256-d unit metric hypersphere.
    """

    def __init__(
        self,
        pretrained_model_name: str = "facebook/deit-tiny-patch16-224",
        embedding_dim: int = 256,
        use_pretrained: bool = True
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.pretrained_model_name = pretrained_model_name

        try:
            if use_pretrained:
                self.vit = ViTModel.from_pretrained(pretrained_model_name)
                hidden_dim = self.vit.config.hidden_size
            else:
                config = ViTConfig(
                    image_size=224,
                    patch_size=16,
                    num_channels=3,
                    hidden_size=192,
                    num_hidden_layers=4,
                    num_attention_heads=3,
                    intermediate_size=768
                )
                self.vit = ViTModel(config)
                hidden_dim = 192
        except Exception as e:
            # Fallback to local ViT configuration if offline or hub unavailable
            config = ViTConfig(
                image_size=224,
                patch_size=16,
                num_channels=3,
                hidden_size=192,
                num_hidden_layers=4,
                num_attention_heads=3,
                intermediate_size=768
            )
            self.vit = ViTModel(config)
            hidden_dim = 192

        # Metric Projection Head: Maps ViT CLS representation to L2-normalized embedding
        self.projection_head = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.LayerNorm(256),
            nn.GELU(),
            nn.Linear(256, embedding_dim)
        )

    def forward_once(self, pixel_values: torch.Tensor) -> torch.Tensor:
        """
        Extracts 256-d L2-normalized embedding for a batch of images.
        pixel_values: (B, 3, 224, 224)
        """
        outputs = self.vit(pixel_values=pixel_values)
        # Extract [CLS] token representation
        cls_token = outputs.last_hidden_state[:, 0, :]  # (B, hidden_dim)
        projected = self.projection_head(cls_token)     # (B, embedding_dim)
        return F.normalize(projected, p=2, dim=1)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.forward_once(x1), self.forward_once(x2)


class VisionTransformerVerifier(SignatureVerificationModel):
    """
    Polymorphic verifier using Hugging Face Vision Transformer.
    Conforms to SignatureVerificationModel interface.
    """

    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        threshold: float = 0.70,
        model_version: str = "1.0.0-transformers-vit",
        device: Optional[str] = None
    ):
        super().__init__(
            model_name="HF_Vision_Transformer",
            model_version=model_version,
            model_type="VISION_TRANSFORMER",
            threshold=threshold,
            review_margin=0.05
        )
        self.device = torch.device(device if device else ("cuda" if torch.cuda.is_available() else "cpu"))
        self.model = VisionTransformerSignatureNet(embedding_dim=256)
        self.preprocessor = SignaturePreprocessor(target_size=(224, 224), invert_colors=False)

        if checkpoint_path and Path(checkpoint_path).exists():
            ckpt = torch.load(checkpoint_path, map_location=self.device)
            if "model_state_dict" in ckpt:
                self.model.load_state_dict(ckpt["model_state_dict"], strict=False)
            elif isinstance(ckpt, dict):
                self.model.load_state_dict(ckpt, strict=False)
            if "calibrated_threshold" in ckpt:
                self.threshold = float(ckpt["calibrated_threshold"])
            if "model_version" in ckpt:
                self.model_version = str(ckpt["model_version"])

        self.model.to(self.device)
        self.model.eval()

    def _prepare_tensor(self, image: Union[str, Path, np.ndarray, Image.Image]) -> torch.Tensor:
        """Prepares image as a (1, 3, 224, 224) float32 tensor."""
        proc = self.preprocessor.preprocess(image)
        if hasattr(proc, "numpy"):
            proc = proc.numpy()
        if proc.ndim == 2:
            proc = np.expand_dims(proc, axis=0)  # (1, 224, 224)
        if proc.shape[0] == 1:
            proc = np.repeat(proc, 3, axis=0)    # (3, 224, 224)

        tensor = torch.from_numpy(proc).unsqueeze(0).float().to(self.device)
        return tensor

    def extract_features(self, image: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
        """Extracts 256-d unit embedding using Hugging Face ViT."""
        tensor = self._prepare_tensor(image)
        with torch.no_grad():
            emb = self.model.forward_once(tensor)
        return emb.cpu().squeeze(0).numpy()

    def compute_distance(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """Computes Euclidean distance between L2-normalized embeddings."""
        return float(np.linalg.norm(feat1 - feat2))

    def compute_similarity(self, distance: float) -> float:
        """
        Transforms Euclidean distance on unit hypersphere to similarity in [0.0, 1.0].
        Since ||u||=1 and ||v||=1, maximum Euclidean distance is 2.0.
        Similarity = 1.0 - (D / 2.0).
        """
        return float(np.clip(1.0 - (distance / 2.0), 0.0, 1.0))
