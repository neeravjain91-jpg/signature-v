"""
Loss functions for Siamese Signature Verification.

Implements classic Contrastive Loss (Hadsell et al., CVPR 2006):
    L(y, D) = 0.5 * y * D^2 + 0.5 * (1 - y) * max(0, margin - D)^2

where y = 1 for genuine pairs, y = 0 for forged pairs, and D is Euclidean distance.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ContrastiveLoss(nn.Module):
    """
    Contrastive loss for metric learning in Siamese networks.
    Pull genuine signatures together (D -> 0) and push forged signatures apart (D >= margin).
    """

    def __init__(self, margin: float = 1.0, eps: float = 1e-9):
        super().__init__()
        self.margin = margin
        self.eps = eps

    def forward(
        self,
        embedding1: torch.Tensor,
        embedding2: torch.Tensor,
        label: torch.Tensor
    ) -> torch.Tensor:
        """
        Args:
            embedding1: Tensor of shape (B, D)
            embedding2: Tensor of shape (B, D)
            label: Tensor of shape (B,) or (B, 1), where 1 = genuine, 0 = forged
        """
        label = label.view(-1)
        # Compute Euclidean distance between embeddings with numerical stability
        euclidean_distance = F.pairwise_distance(embedding1, embedding2, eps=self.eps)

        # Genuine loss: pulls similar pairs together
        loss_genuine = label * torch.pow(euclidean_distance, 2)

        # Forged loss: pushes dissimilar pairs outside the margin
        loss_forged = (1.0 - label) * torch.pow(
            torch.clamp(self.margin - euclidean_distance, min=0.0), 2
        )

        # Total mean loss
        loss = 0.5 * torch.mean(loss_genuine + loss_forged)
        return loss


class CosineContrastiveLoss(nn.Module):
    """
    Cosine-based contrastive loss utilizing cosine similarity.
    """

    def __init__(self, margin: float = 0.3):
        super().__init__()
        self.margin = margin

    def forward(
        self,
        embedding1: torch.Tensor,
        embedding2: torch.Tensor,
        label: torch.Tensor
    ) -> torch.Tensor:
        label = label.view(-1)
        cos_sim = F.cosine_similarity(embedding1, embedding2)

        # Label 1 (genuine) -> maximize cosine similarity -> minimize (1 - cos_sim)
        loss_genuine = label * (1.0 - cos_sim)

        # Label 0 (forged) -> penalize when cos_sim > margin
        loss_forged = (1.0 - label) * torch.clamp(cos_sim - self.margin, min=0.0)

        return torch.mean(loss_genuine + loss_forged)
