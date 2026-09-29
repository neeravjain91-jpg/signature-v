"""
SIGNATURE VMAKE — Training and Validation Calibration for Hugging Face Vision Transformer.

Fine-tunes the metric projection head of the Hugging Face ViT on writer-disjoint training pairs
and validates on disjoint validation pairs:
- Training Split: Writers 1..35
- Validation Split: Writers 36..45
- Prevents identity leakage and tunes operating threshold at validation EER.
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.models.transformer_signature_model import VisionTransformerSignatureNet, VisionTransformerVerifier
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor
from ml.evaluation.metrics import calculate_biometric_metrics


class SignaturePairDataset(Dataset):
    def __init__(self, pairs_df: pd.DataFrame, preprocessor: SignaturePreprocessor):
        self.df = pairs_df.reset_index(drop=True)
        self.preprocessor = preprocessor

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        p1 = row["image_1_path"]
        p2 = row["image_2_path"]
        label = float(row["label"])

        t1 = self._load_tensor(p1)
        t2 = self._load_tensor(p2)
        return t1, t2, torch.tensor(label, dtype=torch.float32)

    def _load_tensor(self, path: str) -> torch.Tensor:
        try:
            proc = self.preprocessor.preprocess(path)
            if hasattr(proc, "numpy"):
                proc = proc.numpy()
            if proc.ndim == 2:
                proc = np.expand_dims(proc, axis=0)
            if proc.shape[0] == 1:
                proc = np.repeat(proc, 3, axis=0)
            return torch.from_numpy(proc).float()
        except Exception:
            return torch.zeros((3, 224, 224), dtype=torch.float32)


class ContrastiveLoss(nn.Module):
    def __init__(self, margin: float = 1.0):
        super().__init__()
        self.margin = margin

    def forward(self, emb1: torch.Tensor, emb2: torch.Tensor, label: torch.Tensor) -> torch.Tensor:
        # label: 1 for genuine (similar), 0 for forged (dissimilar)
        dist = torch.norm(emb1 - emb2, p=2, dim=1)
        loss_pos = label * torch.pow(dist, 2)
        loss_neg = (1.0 - label) * torch.pow(torch.clamp(self.margin - dist, min=0.0), 2)
        return torch.mean(loss_pos + loss_neg)


def train_vision_transformer(
    train_pairs_path: str = "data/pairs/train_pairs.csv",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    epochs: int = 2,
    batch_size: int = 16,
    max_train_samples: int = 800,
    max_val_samples: int = 400
) -> Dict[str, Any]:
    print("=== SIGNATURE VMAKE: Training Hugging Face Vision Transformer ===")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    train_df = pd.read_csv(train_pairs_path)
    val_df = pd.read_csv(val_pairs_path)

    if len(train_df) > max_train_samples:
        train_df = train_df.sample(n=max_train_samples, random_state=42).reset_index(drop=True)
    if len(val_df) > max_val_samples:
        val_df = val_df.sample(n=max_val_samples, random_state=42).reset_index(drop=True)

    preprocessor = SignaturePreprocessor(target_size=(224, 224), invert_colors=False)
    train_ds = SignaturePairDataset(train_df, preprocessor)
    val_ds = SignaturePairDataset(val_df, preprocessor)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)

    model = VisionTransformerSignatureNet(embedding_dim=256, use_pretrained=True)
    # Freeze ViT encoder backbone; train metric projection head for fast CPU convergence
    for param in model.vit.parameters():
        param.requires_grad = False

    model.to(device)

    criterion = ContrastiveLoss(margin=1.0)
    optimizer = optim.AdamW(model.projection_head.parameters(), lr=1e-3, weight_decay=1e-4)

    start_time = time.time()
    for epoch in range(1, epochs + 1):
        model.train()
        total_loss = 0.0
        for i, (t1, t2, labels) in enumerate(train_loader):
            t1, t2, labels = t1.to(device), t2.to(device), labels.to(device)
            optimizer.zero_grad()
            emb1, emb2 = model(t1, t2)
            loss = criterion(emb1, emb2, labels)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()

            if (i + 1) % 10 == 0 or (i + 1) == len(train_loader):
                print(f"  Epoch [{epoch}/{epochs}] Batch [{i+1}/{len(train_loader)}] Loss: {loss.item():.4f}")

    training_time = time.time() - start_time
    print(f"Training completed in {training_time:.2f} seconds.")

    # Validation evaluation
    print("\nEvaluating on Validation Partition (Writers 36..45)...")
    model.eval()
    all_sims = []
    all_labels = []

    with torch.no_grad():
        for t1, t2, labels in val_loader:
            t1, t2 = t1.to(device), t2.to(device)
            emb1, emb2 = model(t1, t2)
            dists = torch.norm(emb1 - emb2, p=2, dim=1).cpu().numpy()
            sims = np.clip(1.0 - (dists / 2.0), 0.0, 1.0)
            all_sims.extend(sims.tolist())
            all_labels.extend(labels.numpy().tolist())

    y_val = np.array(all_labels, dtype=int)
    sims_val = np.array(all_sims, dtype=float)

    val_metrics = calculate_biometric_metrics(y_val, sims_val)
    calibrated_threshold = val_metrics["eer_threshold"]

    print("\n--- ViT Validation Metrics ---")
    print(f"EER: {val_metrics['eer']:.4f} at Threshold: {calibrated_threshold:.4f}")
    print(f"AUC-ROC: {val_metrics['auc_roc']:.4f}")
    print(f"Accuracy: {val_metrics['accuracy']:.4f}")
    print(f"FAR: {val_metrics['far']:.4f}, FRR: {val_metrics['frr']:.4f}")
    print(f"F1 Score: {val_metrics['f1_score']:.4f}")

    # Benchmark single inference latency
    dummy_input = torch.randn(1, 3, 224, 224).to(device)
    latencies = []
    for _ in range(10):
        t0 = time.time()
        with torch.no_grad():
            _ = model.forward_once(dummy_input)
        latencies.append((time.time() - t0) * 1000.0)
    avg_latency = float(np.mean(latencies[2:]))

    # Save artifacts
    output_dir = Path("artifacts/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / "transformer_signature_model.pt"

    torch.save({
        "model_state_dict": model.state_dict(),
        "model_architecture": "Hugging Face ViT (deit-tiny-patch16-224)",
        "embedding_dim": 256,
        "calibrated_threshold": calibrated_threshold,
        "model_version": "1.0.0-transformers-vit",
        "validation_metrics": {
            "eer": val_metrics["eer"],
            "auc_roc": val_metrics["auc_roc"],
            "accuracy": val_metrics["accuracy"],
            "far": val_metrics["far"],
            "frr": val_metrics["frr"],
            "f1_score": val_metrics["f1_score"],
            "calibrated_threshold": calibrated_threshold,
            "average_latency_ms": avg_latency
        }
    }, model_path)
    print(f"Saved Transformer weights to: {model_path}")

    # Save metrics JSON
    metrics_path = output_dir / "transformer_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump({
            "model_name": "HF_Vision_Transformer",
            "model_version": "1.0.0-transformers-vit",
            "eer": val_metrics["eer"],
            "auc_roc": val_metrics["auc_roc"],
            "accuracy": val_metrics["accuracy"],
            "far": val_metrics["far"],
            "frr": val_metrics["frr"],
            "f1_score": val_metrics["f1_score"],
            "calibrated_threshold": calibrated_threshold,
            "average_latency_ms": avg_latency,
            "model_size_mb": round(os.path.getsize(model_path) / (1024 * 1024), 2)
        }, f, indent=2)
    print(f"Saved Transformer metrics to: {metrics_path}")

    return val_metrics


if __name__ == "__main__":
    train_vision_transformer()
