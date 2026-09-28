"""
Loss functions for Siamese Signature Verification.

Implements classic Contrastive Loss (Hadsell et al., CVPR 2006):
    L(y, D) = 0.5 * y * D^2 + 0.5 * (1 - y) * max(0, margin - D)^2

where y = 1 for genuine pairs, y = 0 for forged pairs, and D is Euclidean distance.
"""

from typing import Tuple, Dict
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


class TripletLoss(nn.Module):
    """
    Standard Triplet Margin Loss for metric learning.
    L(a, p, n) = max(0, ||a - p||_2 - ||a - n||_2 + margin)
    """

    def __init__(self, margin: float = 0.3, p: float = 2.0):
        super().__init__()
        self.margin = margin
        self.p = p

    def forward(
        self,
        anchor: torch.Tensor,
        positive: torch.Tensor,
        negative: torch.Tensor
    ) -> torch.Tensor:
        d_pos = F.pairwise_distance(anchor, positive, p=self.p)
        d_neg = F.pairwise_distance(anchor, negative, p=self.p)
        loss = torch.clamp(d_pos - d_neg + self.margin, min=0.0)
        return torch.mean(loss)


class HybridMetricLoss(nn.Module):
    """
    Combined Objective: Contrastive Loss + Triplet Regularization.
    L_total = alpha * L_contrastive + beta * L_triplet

    During pairwise batch execution, mines hard negatives within the mini-batch
    to form active triplets: for each genuine pair (a, p), finds the closest negative n
    and enforces d(a, p) < d(a, n) - margin.
    """

    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 0.5,
        contrastive_margin: float = 1.0,
        triplet_margin: float = 0.3
    ):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.contrastive = ContrastiveLoss(margin=contrastive_margin)
        self.triplet_margin = triplet_margin

    def forward(
        self,
        embedding1: torch.Tensor,
        embedding2: torch.Tensor,
        labels: torch.Tensor
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        labels = labels.view(-1)
        # 1. Contrastive Loss component
        l_cont = self.contrastive(embedding1, embedding2, labels)

        # 2. Batch-level Triplet Mining component
        pos_mask = (labels == 1)
        neg_mask = (labels == 0)

        l_trip = torch.tensor(0.0, device=embedding1.device, requires_grad=True)

        if pos_mask.sum() > 0 and neg_mask.sum() > 0:
            pos_emb1 = embedding1[pos_mask]
            pos_emb2 = embedding2[pos_mask]
            neg_emb2 = embedding2[neg_mask]

            # Pairwise distance matrix between genuine anchors and negative samples
            d_pos = F.pairwise_distance(pos_emb1, pos_emb2)  # (N_pos,)
            # Distance from pos_emb1 to all neg_emb2
            # dist_matrix: (N_pos, N_neg)
            dist_matrix = torch.cdist(pos_emb1, neg_emb2, p=2)
            # Semi-hard / hard negative: closest negative to each anchor
            min_neg_dist, _ = torch.min(dist_matrix, dim=1)  # (N_pos,)

            triplet_loss = torch.clamp(d_pos - min_neg_dist + self.triplet_margin, min=0.0)
            l_trip = torch.mean(triplet_loss)

        total_loss = self.alpha * l_cont + self.beta * l_trip
        loss_breakdown = {
            "total_loss": total_loss.item(),
            "contrastive_loss": l_cont.item(),
            "triplet_loss": l_trip.item()
        }
        return total_loss, loss_breakdown

