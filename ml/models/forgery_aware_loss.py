"""
Forgery-Aware Metric Loss for SIGNATURE VMAKE v4.

Specifically addresses the skilled-forgery false acceptance problem:
1. Category-differentiated margins:
   - Genuine pairs (label=1): target distance = 0
   - Random impostors (label=0, random): margin m_random = 1.0
   - Skilled forgeries (label=0, skilled): elevated margin m_skilled = 1.25
2. Skilled-forgery focal multiplier:
   Skilled forgeries receive a 2.0x loss multiplier and focal hardness exponent (gamma=1.5),
   forcing the feature extractor to prioritize penalizing subtle stroke imitations.
3. In-batch hardest triplet mining for fine-grained boundary sharpening.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ForgeryAwareMetricLoss(nn.Module):
    def __init__(
        self,
        margin_random: float = 1.0,
        margin_skilled: float = 1.25,
        skilled_multiplier: float = 2.0,
        triplet_margin: float = 0.35,
        alpha: float = 1.0,
        beta: float = 0.5,
        gamma: float = 1.5
    ):
        super().__init__()
        self.margin_random = margin_random
        self.margin_skilled = margin_skilled
        self.skilled_multiplier = skilled_multiplier
        self.triplet_margin = triplet_margin
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma

    def forward(
        self,
        emb1: torch.Tensor,
        emb2: torch.Tensor,
        labels: torch.Tensor,
        pair_types: list = None
    ) -> torch.Tensor:
        """
        Args:
            emb1: Normalized embeddings (B, D)
            emb2: Normalized embeddings (B, D)
            labels: 1 for genuine, 0 for impostor (B,)
            pair_types: List of strings: 'genuine_genuine', 'skilled_forgery', 'random_forgery'
        """
        distances = F.pairwise_distance(emb1, emb2, p=2)

        # 1. Positive Pairs (Genuine-Genuine)
        pos_norm = torch.clamp(distances / 2.0, 0.0, 1.0)
        pos_weight = torch.clamp(pos_norm ** 1.0, 0.2, 3.0)
        pos_loss = 0.5 * torch.pow(distances, 2) * pos_weight

        # 2. Negative Pairs
        if pair_types is not None:
            is_skilled = torch.tensor([pt == "skilled_forgery" for pt in pair_types], device=emb1.device, dtype=torch.bool)
            is_random = torch.tensor([pt == "random_forgery" for pt in pair_types], device=emb1.device, dtype=torch.bool)
        else:
            is_skilled = (labels == 0)
            is_random = torch.zeros_like(is_skilled)

        # Skilled Negative Loss
        violating_sk = torch.clamp(self.margin_skilled - distances, min=0.0)
        hard_sk = torch.clamp(violating_sk / self.margin_skilled, 0.0, 1.0)
        sk_weight = self.skilled_multiplier * torch.clamp(hard_sk ** self.gamma, 0.2, 5.0)
        sk_loss = 0.5 * torch.pow(violating_sk, 2) * sk_weight

        # Random Negative Loss
        violating_rnd = torch.clamp(self.margin_random - distances, min=0.0)
        hard_rnd = torch.clamp(violating_rnd / self.margin_random, 0.0, 1.0)
        rnd_loss = 0.5 * torch.pow(violating_rnd, 2)

        neg_loss = torch.where(is_skilled, sk_loss, rnd_loss)

        loss_contrastive = labels * pos_loss + (1.0 - labels) * neg_loss

        # 3. Batch Hardest Triplet Loss
        all_embeddings = torch.cat([emb1, emb2], dim=0)
        batch_size = emb1.size(0)
        pair_ids = torch.arange(batch_size, device=emb1.device)
        sample_ids = torch.cat([pair_ids, pair_ids], dim=0)

        dist_matrix = torch.cdist(all_embeddings, all_embeddings, p=2)
        pos_mask = (sample_ids.unsqueeze(1) == sample_ids.unsqueeze(0)).fill_diagonal_(False)
        neg_mask = (sample_ids.unsqueeze(1) != sample_ids.unsqueeze(0))

        pos_dists = dist_matrix.clone()
        pos_dists[~pos_mask] = -1.0
        hardest_pos, _ = pos_dists.max(dim=1)

        neg_dists = dist_matrix.clone()
        neg_dists[~neg_mask] = 1e6
        hardest_neg, _ = neg_dists.min(dim=1)

        triplet_loss = F.relu(hardest_pos - hardest_neg + self.triplet_margin).mean()

        total_loss = self.alpha * loss_contrastive.mean() + self.beta * triplet_loss
        return total_loss
