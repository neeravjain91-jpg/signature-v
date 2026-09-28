"""
Hard Negative Mining Pipeline for Siamese Signature Verification.

Identifies forged signature pairs within the TRAINING cohort (Writers 1-35)
that the current model checkpoint incorrectly assigns high similarity to (hard negatives).
Injects or re-weights these pairs in training mini-batches to force the metric space
to separate skilled forgeries from genuine reference signatures.

STRICT PROTOCOL:
- Hard negatives are mined EXCLUSIVELY from training data (Writers 1-35).
- Test data (Writers 46-55) is NEVER accessed during mining.
- Validation data (Writers 36-45) is NEVER accessed during mining.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import torch
from torch.utils.data import DataLoader

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.dataset import SignaturePairDataset


class HardNegativeMiner:
    """
    Mines hard negative pairs from training data using a frozen or active model checkpoint.
    """

    def __init__(
        self,
        model: SiameseSignatureNet,
        device: torch.device,
        hard_threshold: float = 0.70,
        top_k: Optional[int] = 1000
    ):
        """
        Args:
            model: Current Siamese neural network.
            device: Computation device (CPU or CUDA).
            hard_threshold: Minimum similarity score for a negative pair to be considered 'hard'.
            top_k: Maximum number of hard negatives to mine.
        """
        self.model = model
        self.device = device
        self.hard_threshold = hard_threshold
        self.top_k = top_k

    def mine_from_dataframe(
        self,
        df: pd.DataFrame,
        batch_size: int = 128
    ) -> pd.DataFrame:
        """
        Evaluates negative pairs in `df` (where label == 0) and returns the subset
        with similarity >= self.hard_threshold, sorted descending by similarity.
        """
        neg_df = df[df["label"] == 0].reset_index(drop=True)
        if len(neg_df) == 0:
            return pd.DataFrame()

        dataset = SignaturePairDataset(neg_df, cache_in_memory=True, augment=False)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        self.model.eval()
        sims = []
        with torch.no_grad():
            for batch in loader:
                img1 = batch["image_1"].to(self.device)
                img2 = batch["image_2"].to(self.device)
                emb1, emb2 = self.model(img1, img2)
                dist = self.model.compute_distance(emb1, emb2)
                sim = self.model.compute_similarity(dist)
                sims.extend(sim.cpu().numpy().tolist())

        neg_df = neg_df.copy()
        neg_df["mined_similarity"] = sims

        # Filter hard negatives: where similarity is above threshold
        hard_df = neg_df[neg_df["mined_similarity"] >= self.hard_threshold].copy()
        hard_df = hard_df.sort_values(by="mined_similarity", ascending=False).reset_index(drop=True)

        if self.top_k and len(hard_df) > self.top_k:
            hard_df = hard_df.iloc[:self.top_k]

        return hard_df

    def create_hard_negative_augmented_dataset(
        self,
        original_train_df: pd.DataFrame,
        hard_negative_ratio: float = 0.30
    ) -> pd.DataFrame:
        """
        Combines original training pairs with mined hard negatives.
        `hard_negative_ratio`: Fraction of negative pairs that will be hard negatives.
        Maintains an overall 50% genuine, 50% negative balance.
        """
        hard_negatives = self.mine_from_dataframe(original_train_df)
        print(f"[HardNegativeMiner] Mined {len(hard_negatives)} hard negatives (sim >= {self.hard_threshold:.2f})")

        genuine_df = original_train_df[original_train_df["label"] == 1].reset_index(drop=True)
        regular_neg_df = original_train_df[original_train_df["label"] == 0].reset_index(drop=True)

        num_positives = len(genuine_df)
        num_negatives = num_positives

        num_hard = int(num_negatives * hard_negative_ratio)
        num_regular = num_negatives - num_hard

        # Sample hard negatives (with replacement if needed)
        if len(hard_negatives) > 0:
            if len(hard_negatives) >= num_hard:
                selected_hard = hard_negatives.iloc[:num_hard]
            else:
                selected_hard = hard_negatives.sample(n=num_hard, replace=True, random_state=42)
        else:
            selected_hard = pd.DataFrame()
            num_regular = num_negatives

        selected_regular = regular_neg_df.sample(n=num_regular, replace=False, random_state=42)

        combined_neg = pd.concat([selected_hard, selected_regular], ignore_index=True)
        if "mined_similarity" in combined_neg.columns:
            combined_neg = combined_neg.drop(columns=["mined_similarity"])

        combined_df = pd.concat([genuine_df, combined_neg], ignore_index=True)
        # Shuffle
        combined_df = combined_df.sample(frac=1.0, random_state=42).reset_index(drop=True)
        return combined_df
