"""
Adaptive Hard Negative Mining 2.0 Pipeline for SIGNATURE VMAKE.

Key Capabilities:
1. Strictly mines EXCLUSIVELY from training writers (Writers 1-45 or active fold train writers).
2. Category separation:
   - hard_skilled_forgeries: skilled imitators scoring above hardness threshold
   - hard_random_impostors: cross-writer samples with high visual coincidences
   - false_accepting_negatives: any negative sample crossing the operational threshold
3. Adaptive frequency-penalized queue:
   Penalizes repeatedly sampled instances to enforce diversity and prevent overfitting to a few pairs.
4. Comprehensive forensic telemetry:
   Tracks unique mined count, sampling frequency histogram, and similarity distribution stats.
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader
from collections import Counter

from ml.models.dataset import SignaturePairDataset


class AdaptiveHardNegativeMiner:
    def __init__(
        self,
        hard_threshold: float = 0.65,
        target_hard_ratio: float = 0.35,
        max_queue_size: int = 1500
    ):
        self.hard_threshold = hard_threshold
        self.target_hard_ratio = target_hard_ratio
        self.max_queue_size = max_queue_size
        self.usage_counter = Counter()

    def mine_and_assemble(
        self,
        model: torch.nn.Module,
        train_df: pd.DataFrame,
        preprocessor,
        device: torch.device,
        batch_size: int = 128
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Evaluates training negatives, mines hard samples across categories, and updates frequency penalties.
        """
        neg_df = train_df[train_df["label"] == 0].reset_index(drop=True)
        if len(neg_df) == 0:
            return train_df, {}

        dataset = SignaturePairDataset(neg_df, preprocessor=preprocessor, cache_in_memory=True, augment=False)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        model.eval()
        sims = []
        with torch.no_grad():
            for batch in loader:
                img1 = batch["image_1"].to(device)
                img2 = batch["image_2"].to(device)
                emb1, emb2 = model(img1, img2)
                dist = model.compute_distance(emb1, emb2)
                sim = model.compute_similarity(dist)
                sims.extend(sim.cpu().numpy().tolist())

        neg_df = neg_df.copy()
        neg_df["mined_similarity"] = sims

        # Categorize
        hard_skilled = neg_df[(neg_df["pair_type"] == "skilled_forgery") & (neg_df["mined_similarity"] >= self.hard_threshold)]
        hard_random = neg_df[(neg_df["pair_type"] == "random_forgery") & (neg_df["mined_similarity"] >= self.hard_threshold)]
        false_accepts = neg_df[neg_df["mined_similarity"] >= 0.73]

        all_hard = pd.concat([hard_skilled, hard_random]).drop_duplicates().reset_index(drop=True)

        # Apply frequency penalty weighting
        weights = []
        for idx, row in all_hard.iterrows():
            pair_key = f"{row['image_1_path']}|{row['image_2_path']}"
            freq = self.usage_counter[pair_key]
            # Higher similarity = higher weight; higher frequency = lower weight
            w = (row["mined_similarity"] ** 2) / (1.0 + 0.5 * freq)
            weights.append(w)

        all_hard["sample_weight"] = weights

        genuine_df = train_df[train_df["label"] == 1].reset_index(drop=True)
        n_pos = len(genuine_df)
        n_hard = int(n_pos * self.target_hard_ratio)
        n_reg = n_pos - n_hard

        if len(all_hard) > 0:
            probs = all_hard["sample_weight"] / all_hard["sample_weight"].sum()
            sample_count = min(n_hard, len(all_hard))
            selected_hard = all_hard.sample(n=sample_count, replace=False, weights=probs, random_state=42)
            # Update frequency counter
            for _, r in selected_hard.iterrows():
                self.usage_counter[f"{r['image_1_path']}|{r['image_2_path']}"] += 1
        else:
            selected_hard = pd.DataFrame()
            n_reg = n_pos

        regular_neg = neg_df.sample(n=min(n_reg, len(neg_df)), replace=False, random_state=42)

        cols_to_drop = [c for c in ["mined_similarity", "sample_weight"] if c in selected_hard.columns]
        selected_hard = selected_hard.drop(columns=cols_to_drop)

        cols_to_drop_reg = [c for c in ["mined_similarity", "sample_weight"] if c in regular_neg.columns]
        regular_neg = regular_neg.drop(columns=cols_to_drop_reg)

        balanced_df = pd.concat([genuine_df, selected_hard, regular_neg], ignore_index=True)
        balanced_df = balanced_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

        telemetry = {
            "total_mined_hard": len(all_hard),
            "unique_hard_skilled": len(hard_skilled),
            "unique_hard_random": len(hard_random),
            "false_accepts_count": len(false_accepts),
            "selected_hard_count": len(selected_hard),
            "similarity_p50": float(np.percentile(sims, 50)),
            "similarity_p90": float(np.percentile(sims, 90)),
            "similarity_p99": float(np.percentile(sims, 99)),
            "unique_keys_in_queue": len(self.usage_counter)
        }

        return balanced_df, telemetry
