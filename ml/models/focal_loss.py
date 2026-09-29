"""
Focal Metric Loss Formulations for Offline Signature Verification.

Addresses the hard-example and skilled-forgery false acceptance problem:
Down-weights easily separated genuine pairs and easily rejected random impostors.
Concentrates gradients on hard border pairs (e.g. skilled forgeries mimicking strokes).
Includes sample-difficulty attenuation to prevent outlier / noisy samples from exploding gradients.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class FocalContrastiveLoss(nn.Module):
    """
    Focal Contrastive Loss:
    L(y, d) = y * (d/2)^gamma * (1/2 * d^2) + (1 - y) * (1 - d/m)^gamma * (1/2 * max(0, m - d)^2)
    where gamma >= 0 dynamically modulates loss weight based on sample hardness.
    """
    def __init__(self, margin: float = 1.0, gamma: float = 1.0, max_weight: float = 3.0):
        super().__init__()
        self.margin = margin
        self.gamma = gamma
        self.max_weight = max_weight

    def forward(self, emb1: torch.Tensor, emb2: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        distances = F.pairwise_distance(emb1, emb2, p=2)

        # Positive pairs: hard when distance is large
        pos_norm_dist = torch.clamp(distances / 2.0, 0.0, 1.0)
        pos_weight = torch.clamp((pos_norm_dist) ** self.gamma, 0.1, self.max_weight)
        pos_loss = 0.5 * torch.pow(distances, 2) * pos_weight

        # Negative pairs: hard when distance is small (close to 0, under margin)
        # Violating distance ratio = max(0, margin - distance) / margin
        violating = torch.clamp(self.margin - distances, min=0.0)
        neg_norm_hardness = torch.clamp(violating / self.margin, 0.0, 1.0)
        neg_weight = torch.clamp((neg_norm_hardness) ** self.gamma, 0.1, self.max_weight)
        neg_loss = 0.5 * torch.pow(violating, 2) * neg_weight

        loss = label * pos_loss + (1.0 - label) * neg_loss
        return loss.mean()


class FocalHybridMetricLoss(nn.Module):
    """
    Combines Focal Contrastive Loss with Online In-Batch Hardest Triplet Mining.
    L_total = alpha * L_focal_contrastive + beta * L_triplet_hardest
    """
    def __init__(
        self,
        alpha: float = 1.0,
        beta: float = 0.5,
        contrastive_margin: float = 1.0,
        triplet_margin: float = 0.3,
        gamma: float = 1.0
    ):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.focal_contrastive = FocalContrastiveLoss(margin=contrastive_margin, gamma=gamma)
        self.triplet_margin = triplet_margin

    def forward(
        self,
        emb1: torch.Tensor,
        emb2: torch.Tensor,
        labels: torch.Tensor
    ) -> torch.Tensor:
        loss_fc = self.focal_contrastive(emb1, emb2, labels)

        # Batch hardest triplet mining
        all_embeddings = torch.cat([emb1, emb2], dim=0)
        batch_size = emb1.size(0)
        pair_ids = torch.arange(batch_size, device=emb1.device)
        sample_ids = torch.cat([pair_ids, pair_ids], dim=0)

        dist_matrix = torch.cdist(all_embeddings, all_embeddings, p=2)

        # Positive mask: same sample pair
        pos_mask = (sample_ids.unsqueeze(1) == sample_ids.unsqueeze(0)).fill_diagonal_(False)
        # Negative mask: different sample pair
        neg_mask = (sample_ids.unsqueeze(1) != sample_ids.unsqueeze(0))

        # Hardest positive distance for each anchor
        pos_dists = dist_matrix.clone()
        pos_dists[~pos_mask] = -1.0
        hardest_pos, _ = pos_dists.max(dim=1)

        # Hardest negative distance for each anchor
        neg_dists = dist_matrix.clone()
        neg_dists[~neg_mask] = 1e6
        hardest_neg, _ = neg_dists.min(dim=1)

        triplet_loss = F.relu(hardest_pos - hardest_neg + self.triplet_margin).mean()

        total_loss = self.alpha * loss_fc + self.beta * triplet_loss
        return total_loss
