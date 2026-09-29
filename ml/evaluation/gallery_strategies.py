"""
Multi-Reference Signature Gallery Strategies.

Implements banking-grade specimen gallery aggregations:
1. max: Maximum similarity across enrolled reference specimens.
2. mean: Mean similarity across enrolled specimens.
3. top_k: Average of top-k closest specimens (k=2 for a 3-5 specimen gallery).
4. centroid: Distance to the normalized centroid of the enrolled embedding gallery.
5. robust_centroid: Distance to the geometric median / trimmed centroid of enrolled specimens.
6. variance_normalized: Similarity z-score relative to the customer's intra-specimen variance.
7. reference_conditioned: Score normalized against the enrolled specimen similarity baseline.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
import torch
import torch.nn.functional as F


def aggregate_gallery_scores(
    query_emb: torch.Tensor,
    gallery_embs: torch.Tensor,
    strategy: str = "max",
    top_k: int = 2
) -> float:
    """
    Args:
        query_emb: Tensor of shape (1, D) - L2 normalized.
        gallery_embs: Tensor of shape (K, D) - L2 normalized enrolled specimens.
        strategy: Aggregation strategy.
    Returns:
        Scalar similarity score in [0, 1].
    """
    # Pairwise distances from query to all gallery specimens
    dists = torch.norm(gallery_embs - query_emb, p=2, dim=1)  # (K,)
    sims = 1.0 / (1.0 + dists)  # (K,)

    if strategy == "max":
        return float(sims.max().item())
    elif strategy == "mean":
        return float(sims.mean().item())
    elif strategy == "top_k":
        k_val = min(top_k, sims.size(0))
        topk_sims, _ = torch.topk(sims, k=k_val)
        return float(topk_sims.mean().item())
    elif strategy == "centroid":
        mean_emb = gallery_embs.mean(dim=0, keepdim=True)
        norm_centroid = F.normalize(mean_emb, p=2, dim=1)
        dist = torch.norm(norm_centroid - query_emb, p=2, dim=1)
        return float((1.0 / (1.0 + dist)).item())
    elif strategy == "robust_centroid":
        # Geometric median approximation: specimen closest to all other specimens
        if gallery_embs.size(0) <= 2:
            norm_centroid = F.normalize(gallery_embs.mean(dim=0, keepdim=True), p=2, dim=1)
        else:
            intra_dists = torch.cdist(gallery_embs, gallery_embs, p=2).sum(dim=1)
            med_idx = intra_dists.argmin()
            norm_centroid = gallery_embs[med_idx:med_idx+1]
        dist = torch.norm(norm_centroid - query_emb, p=2, dim=1)
        return float((1.0 / (1.0 + dist)).item())
    elif strategy == "reference_conditioned":
        # Pairwise intra-gallery similarities
        if gallery_embs.size(0) > 1:
            intra_pw = torch.cdist(gallery_embs, gallery_embs, p=2)
            # Take upper triangle non-zero distances
            mask = torch.triu(torch.ones_like(intra_pw), diagonal=1).bool()
            intra_sims = 1.0 / (1.0 + intra_pw[mask])
            intra_mean = intra_sims.mean().item()
            intra_std = max(intra_sims.std().item(), 0.02)
        else:
            intra_mean = 0.85
            intra_std = 0.05

        raw_max = float(sims.max().item())
        # Conditioned ratio: how close query is to the customer's typical self-similarity
        conditioned = 0.5 + 0.5 * ((raw_max - (intra_mean - intra_std)) / max(2 * intra_std, 0.05))
        return float(np.clip(conditioned, 0.0, 1.0))
    elif strategy == "variance_normalized":
        if gallery_embs.size(0) > 1:
            intra_pw = torch.cdist(gallery_embs, gallery_embs, p=2)
            mask = torch.triu(torch.ones_like(intra_pw), diagonal=1).bool()
            intra_sims = 1.0 / (1.0 + intra_pw[mask])
            sigma = max(float(intra_sims.std().item()), 0.01)
            mu = float(intra_sims.mean().item())
        else:
            mu, sigma = 0.85, 0.05
        raw_mean = float(sims.mean().item())
        z_score = (raw_mean - mu) / sigma
        # Sigmoid map z-score to [0, 1]
        normed = 1.0 / (1.0 + np.exp(-z_score))
        return float(normed)
    else:
        return float(sims.max().item())
