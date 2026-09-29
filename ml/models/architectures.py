"""
Advanced Model Architectures for Offline Siamese Signature Verification:
1. SiameseResNet18 (Baseline)
2. SiameseSTNResNet (Spatial Transformer Network + ResNet)
3. SiameseCNNTransformer (Hybrid CNN Feature Extractor + Lightweight Transformer Global Self-Attention)
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import models


class SpatialTransformerNetwork(nn.Module):
    """
    Spatial Transformer Network (STN) for signature canonicalization.
    Predicts an affine transformation matrix (2x3) to align, de-slant, and center signatures.
    """
    def __init__(self, in_channels: int = 1):
        super().__init__()
        # Localization network
        self.localization = nn.Sequential(
            nn.Conv2d(in_channels, 16, kernel_size=7, stride=2, padding=3),
            nn.BatchNorm2d(16),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(16, 32, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.AdaptiveAvgPool2d((4, 4))
        )
        self.fc_loc = nn.Sequential(
            nn.Linear(32 * 4 * 4, 64),
            nn.ReLU(True),
            nn.Linear(64, 6)
        )
        # Initialize affine transformation to identity: [[1, 0, 0], [0, 1, 0]]
        self.fc_loc[2].weight.data.zero_()
        self.fc_loc[2].bias.data.copy_(torch.tensor([1, 0, 0, 0, 1, 0], dtype=torch.float))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        xs = self.localization(x)
        xs = xs.view(xs.size(0), -1)
        theta = self.fc_loc(xs).view(-1, 2, 3)
        grid = F.affine_grid(theta, x.size(), align_corners=False)
        x_aligned = F.grid_sample(x, grid, align_corners=False)
        return x_aligned


class SiameseResNet18(nn.Module):
    """Modified ResNet-18 Siamese Network with single-channel or multi-channel input."""
    def __init__(self, embedding_dim: int = 256, in_channels: int = 1, pretrained: bool = False):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        base = models.resnet18(weights=weights)

        if in_channels != 3:
            self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
            if pretrained:
                with torch.no_grad():
                    self.conv1.weight.copy_(base.conv1.weight.mean(dim=1, keepdim=True))
        else:
            self.conv1 = base.conv1

        self.bn1 = base.bn1
        self.relu = base.relu
        self.maxpool = base.maxpool
        self.layer1 = base.layer1
        self.layer2 = base.layer2
        self.layer3 = base.layer3
        self.layer4 = base.layer4
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

        self.embedding_head = nn.Sequential(
            nn.Linear(512, embedding_dim),
            nn.BatchNorm1d(embedding_dim)
        )

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)

        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        emb = self.embedding_head(x)
        return F.normalize(emb, p=2, dim=1)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        return self.forward_once(x1), self.forward_once(x2)

    @staticmethod
    def compute_distance(emb1: torch.Tensor, emb2: torch.Tensor) -> torch.Tensor:
        return torch.norm(emb1 - emb2, p=2, dim=1)

    @staticmethod
    def compute_similarity(distance: torch.Tensor) -> torch.Tensor:
        return 1.0 / (1.0 + distance)


class SiameseSTNResNet(nn.Module):
    """
    STN + Siamese ResNet:
    Passes signatures through a Spatial Transformer Network before CNN feature extraction.
    """
    def __init__(self, embedding_dim: int = 256, in_channels: int = 1, pretrained: bool = False):
        super().__init__()
        self.stn = SpatialTransformerNetwork(in_channels=in_channels)
        self.encoder = SiameseResNet18(embedding_dim=embedding_dim, in_channels=in_channels, pretrained=pretrained)

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        x_aligned = self.stn(x)
        return self.encoder.forward_once(x_aligned)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        return self.forward_once(x1), self.forward_once(x2)

    @staticmethod
    def compute_distance(emb1: torch.Tensor, emb2: torch.Tensor) -> torch.Tensor:
        return torch.norm(emb1 - emb2, p=2, dim=1)

    @staticmethod
    def compute_similarity(distance: torch.Tensor) -> torch.Tensor:
        return 1.0 / (1.0 + distance)


class SiameseCNNTransformer(nn.Module):
    """
    Hybrid CNN + Lightweight Transformer Siamese Verifier:
    Extracts fine-grained stroke features using CNN layers, then applies Multi-Head Self-Attention
    to capture long-range stroke trajectory relationships and global signature topology.
    """
    def __init__(
        self,
        embedding_dim: int = 256,
        in_channels: int = 1,
        transformer_dim: int = 128,
        num_heads: int = 4,
        num_transformer_layers: int = 2
    ):
        super().__init__()
        # 1. CNN Feature Extractor
        self.cnn = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(True),
            nn.MaxPool2d(2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.Conv2d(64, transformer_dim, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(transformer_dim),
            nn.ReLU(True)
        )
        # Expected spatial map after 224x224 input: ~ 14x14 = 196 tokens

        # 2. Positional Encoding
        self.pos_embedding = nn.Parameter(torch.randn(1, 196, transformer_dim) * 0.02)

        # 3. Lightweight Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=transformer_dim,
            nhead=num_heads,
            dim_feedforward=transformer_dim * 2,
            dropout=0.1,
            activation="gelu",
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_transformer_layers)

        # 4. Pooling & Fusion Head
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.fc_out = nn.Sequential(
            nn.Linear(transformer_dim, embedding_dim),
            nn.BatchNorm1d(embedding_dim)
        )

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        feat = self.cnn(x)  # (B, D, H, W)
        b, c, h, w = feat.shape
        tokens = feat.view(b, c, h * w).permute(0, 2, 1)  # (B, N, D)

        # Add positional embedding
        if tokens.size(1) == self.pos_embedding.size(1):
            tokens = tokens + self.pos_embedding
        else:
            # Handle variable input sizes if any
            pos_emb = F.interpolate(
                self.pos_embedding.permute(0, 2, 1),
                size=tokens.size(1),
                mode="linear",
                align_corners=False
            ).permute(0, 2, 1)
            tokens = tokens + pos_emb

        # Transformer Self-Attention
        attn_out = self.transformer(tokens)  # (B, N, D)

        # Global average pool over token sequence
        pooled = attn_out.mean(dim=1)  # (B, D)
        emb = self.fc_out(pooled)
        return F.normalize(emb, p=2, dim=1)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        return self.forward_once(x1), self.forward_once(x2)

    @staticmethod
    def compute_distance(emb1: torch.Tensor, emb2: torch.Tensor) -> torch.Tensor:
        return torch.norm(emb1 - emb2, p=2, dim=1)

    @staticmethod
    def compute_similarity(distance: torch.Tensor) -> torch.Tensor:
        return 1.0 / (1.0 + distance)


class SiameseLocalGlobalNet(nn.Module):
    """
    Local / Part-Based + Global Siamese Architecture.
    Extracts global signature envelope representation fused with local sub-region features
    (stroke onset/prefix and flourishing/terminal regions) to catch fine skilled-forgery deviations.
    """
    def __init__(self, embedding_dim: int = 256, in_channels: int = 1, pretrained: bool = False):
        super().__init__()
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        base = models.resnet18(weights=weights)

        if in_channels != 3:
            self.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
            if pretrained:
                with torch.no_grad():
                    self.conv1.weight.copy_(base.conv1.weight.mean(dim=1, keepdim=True))
        else:
            self.conv1 = base.conv1

        self.bn1 = base.bn1
        self.relu = base.relu
        self.maxpool = base.maxpool
        self.layer1 = base.layer1
        self.layer2 = base.layer2
        self.layer3 = base.layer3
        self.layer4 = base.layer4

        # Global branch: 512 -> 128
        self.global_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc_global = nn.Linear(512, 128)

        # Local branches: Left half and Right half -> each 512 -> 64
        self.local_pool = nn.AdaptiveAvgPool2d((1, 1))
        self.fc_local_left = nn.Linear(512, 64)
        self.fc_local_right = nn.Linear(512, 64)

        self.bn_out = nn.BatchNorm1d(embedding_dim)

    def forward_once(self, x: torch.Tensor) -> torch.Tensor:
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)

        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        feat_map = self.layer4(x)  # (B, 512, H, W) e.g. (B, 512, 7, 7)

        # Global feature
        g_feat = self.global_pool(feat_map).flatten(1)
        v_global = F.relu(self.fc_global(g_feat))

        # Local part features: left half and right half
        w = feat_map.size(3)
        left_map = feat_map[:, :, :, : w // 2 + 1]
        right_map = feat_map[:, :, :, w // 2 :]

        v_left = F.relu(self.fc_local_left(self.local_pool(left_map).flatten(1)))
        v_right = F.relu(self.fc_local_right(self.local_pool(right_map).flatten(1)))

        # Fuse global and local embeddings: 128 + 64 + 64 = 256
        fused = torch.cat([v_global, v_left, v_right], dim=1)
        emb = self.bn_out(fused)
        return F.normalize(emb, p=2, dim=1)

    def forward(self, x1: torch.Tensor, x2: torch.Tensor):
        return self.forward_once(x1), self.forward_once(x2)

    @staticmethod
    def compute_distance(emb1: torch.Tensor, emb2: torch.Tensor) -> torch.Tensor:
        return torch.norm(emb1 - emb2, p=2, dim=1)

    @staticmethod
    def compute_similarity(distance: torch.Tensor) -> torch.Tensor:
        return 1.0 / (1.0 + distance)

