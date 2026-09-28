"""
Siamese Neural Network Architecture for Writer-Independent Offline Signature Verification.

Guarantees weight sharing across reference and questioned signature branches:
Reference Signature   ───► Shared CNN Encoder ───► Embedding A
                                                        │──► Distance & Verification Score
Questioned Signature  ───► Same Shared Encoder ──► Embedding B
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """Basic residual block with Batch Normalization and ReLU."""
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.shortcut(x)
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return self.relu(out)


class SignatureEncoder(nn.Module):
    """
    Deep Convolutional Feature Extractor for single-channel offline signature images.
    Extracts high-frequency stroke dynamics, pen-lift contours, and geometric features.
    """
    def __init__(self, embedding_dim: int = 256, dropout_rate: float = 0.3):
        super().__init__()
        self.embedding_dim = embedding_dim

        # Initial feature intake (B, 1, 224, 224) -> (B, 32, 56, 56)
        self.conv_in = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=7, stride=2, padding=3, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=3, stride=2, padding=1)
        )

        # Residual Feature Stages
        self.stage1 = ResidualBlock(32, 64, stride=2)   # -> (B, 64, 28, 28)
        self.stage2 = ResidualBlock(64, 128, stride=2)  # -> (B, 128, 14, 14)
        self.stage3 = ResidualBlock(128, 256, stride=2) # -> (B, 256, 7, 7)
        self.stage4 = ResidualBlock(256, 512, stride=2) # -> (B, 512, 4, 4)

        # Global Pooling
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1)) # -> (B, 512, 1, 1)

        # Metric Projection Head
        self.projector = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.conv_in(x)
        features = self.stage1(features)
        features = self.stage2(features)
        features = self.stage3(features)
        features = self.stage4(features)
        pooled = self.global_pool(features)
        raw_embedding = self.projector(pooled)
        # Project onto the unit hypersphere for stable metric comparison
        normalized_embedding = F.normalize(raw_embedding, p=2, dim=1)
        return normalized_embedding


class CustomCNNEncoder(nn.Module):
    """
    Standard sequential CNN feature extractor without residual shortcuts.
    Traditional baseline architecture for signature verification.
    """
    def __init__(self, embedding_dim: int = 256, dropout_rate: float = 0.3):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=2, padding=2, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),

            nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),

            nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),

            nn.AdaptiveAvgPool2d((1, 1))
        )
        self.projector = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(256, embedding_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.features(x)
        raw_emb = self.projector(feat)
        return F.normalize(raw_emb, p=2, dim=1)


class PretrainedResNet18Encoder(nn.Module):
    """
    Torchvision ResNet-18 adapted for single-channel grayscale input and unit-sphere projection.
    """
    def __init__(self, embedding_dim: int = 256, dropout_rate: float = 0.3, pretrained: bool = True):
        super().__init__()
        self.embedding_dim = embedding_dim
        import torchvision.models as models

        try:
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            base_model = models.resnet18(weights=weights)
        except Exception:
            base_model = models.resnet18(weights=None)

        # Adapt first conv from 3-channels to 1-channel
        orig_conv = base_model.conv1
        new_conv = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        with torch.no_grad():
            if pretrained and orig_conv.weight is not None:
                # Average weights across RGB channels
                new_conv.weight.copy_(orig_conv.weight.mean(dim=1, keepdim=True))
        base_model.conv1 = new_conv

        # Replace fc with identity and use custom projection head
        num_features = base_model.fc.in_features
        base_model.fc = nn.Identity()
        self.backbone = base_model

        self.projector = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate),
            nn.Linear(512, embedding_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.backbone(x)
        raw_emb = self.projector(feat)
        return F.normalize(raw_emb, p=2, dim=1)


class SiameseSignatureNet(nn.Module):
    """
    Twin Siamese Neural Network for Signature Verification.
    Maintains a single shared SignatureEncoder to guarantee identical feature representations.
    """

    def __init__(
        self,
        embedding_dim: int = 256,
        dropout_rate: float = 0.3,
        default_threshold: float = 0.7500,
        backbone: str = "resnet18"
    ):
        super().__init__()
        self.embedding_dim = embedding_dim
        self.default_threshold = default_threshold
        self.backbone_name = backbone

        # Single shared CNN encoder instance
        if backbone == "custom_cnn":
            self.encoder = CustomCNNEncoder(embedding_dim=embedding_dim, dropout_rate=dropout_rate)
        elif backbone == "resnet18_pretrained":
            self.encoder = PretrainedResNet18Encoder(embedding_dim=embedding_dim, dropout_rate=dropout_rate, pretrained=True)
        else:
            self.encoder = SignatureEncoder(embedding_dim=embedding_dim, dropout_rate=dropout_rate)

    def forward_one(self, x: torch.Tensor) -> torch.Tensor:
        """Encodes a single signature image into a normalized embedding vector."""
        return self.encoder(x)

    def forward(
        self,
        x1: torch.Tensor,
        x2: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Passes reference signature x1 and questioned signature x2 through
        the SAME shared CNN encoder.
        """
        embedding1 = self.forward_one(x1)
        embedding2 = self.forward_one(x2)
        return embedding1, embedding2

    @staticmethod
    def compute_distance(embedding1: torch.Tensor, embedding2: torch.Tensor) -> torch.Tensor:
        """
        Computes pairwise Euclidean distance between L2-normalized embeddings.
        Since embeddings have unit norm ||u|| = ||v|| = 1, distance is strictly in [0.0, 2.0].
        """
        return F.pairwise_distance(embedding1, embedding2)

    @staticmethod
    def compute_similarity(distance: torch.Tensor) -> torch.Tensor:
        """
        Converts Euclidean distance on unit hypersphere to a normalized similarity score in [0.0, 1.0].
        When distance = 0.0 -> similarity = 1.0 (identical)
        When distance = 2.0 -> similarity = 0.0 (diametrically opposed)
        """
        similarity = torch.clamp(1.0 - (distance / 2.0), min=0.0, max=1.0)
        return similarity

    def verify(
        self,
        x1: torch.Tensor,
        x2: torch.Tensor,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Inference method returning embeddings, distance, similarity score, and verification decision.
        """
        thresh = threshold if threshold is not None else self.default_threshold
        self.eval()
        with torch.no_grad():
            emb1, emb2 = self.forward(x1, x2)
            distance = self.compute_distance(emb1, emb2)
            similarity = self.compute_similarity(distance)

            decisions = []
            for sim in similarity:
                sim_val = sim.item()
                if sim_val >= thresh:
                    decisions.append("VERIFIED")
                elif sim_val >= (thresh - 0.12):
                    decisions.append("MANUAL_REVIEW")
                else:
                    decisions.append("REJECTED")

        return {
            "embedding_a": emb1,
            "embedding_b": emb2,
            "distance": distance,
            "similarity_score": similarity,
            "decision": decisions if len(decisions) > 1 else decisions[0],
            "threshold_used": thresh
        }
