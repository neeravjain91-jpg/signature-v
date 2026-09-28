"""
Validation Threshold Sweep and Trade-Off Sensitivity Analysis.

Evaluates decision thresholds exclusively on the VALIDATION COHORT (Writers 36–45).
Generates:
- docs/VALIDATION_THRESHOLD_SWEEP.csv
- docs/VALIDATION_THRESHOLD_SWEEP.png
- Detailed trade-off comparison at critical operational points.
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import precision_recall_fscore_support

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.dataset import SignaturePairDataset


def run_threshold_sweep(
    checkpoint_path: str = "artifacts/models/best_siamese_model.pt",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    output_csv_path: str = "docs/VALIDATION_THRESHOLD_SWEEP.csv",
    output_plot_path: str = "docs/VALIDATION_THRESHOLD_SWEEP.png",
    batch_size: int = 32
):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("==================================================")
    print("   VALIDATION THRESHOLD SENSITIVITY SWEEP")
    print("==================================================")
    print(f"[*] Device                : {device}")
    print(f"[*] Checkpoint            : {checkpoint_path}")
    print(f"[*] Validation Pairs Src  : {val_pairs_path}")

    # 1. Load Model Checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    embedding_dim = checkpoint.get("embedding_dim", 256)
    model = SiameseSignatureNet(embedding_dim=embedding_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # 2. Load Validation Dataset
    val_dataset = SignaturePairDataset(val_pairs_path, cache_in_memory=True, augment=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    print(f"[+] Loaded {len(val_dataset)} validation pairs.")

    all_labels = []
    all_sims = []
    all_pair_types = []

    with torch.no_grad():
        for batch in val_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            emb1, emb2 = model(img1, img2)
            dist = model.compute_distance(emb1, emb2)
            sim = model.compute_similarity(dist)

            all_labels.extend(labels.cpu().numpy().tolist())
            all_sims.extend(sim.cpu().numpy().tolist())
            all_pair_types.extend(batch["pair_type"])

    y_true = np.array(all_labels, dtype=int)
    sims = np.array(all_sims, dtype=float)

    skilled_mask = np.array([pt == "skilled_forgery" for pt in all_pair_types])
    random_mask = np.array([pt == "random_forgery" for pt in all_pair_types])
    genuine_mask = (y_true == 1)

    n_gen = int(np.sum(genuine_mask))
    n_skilled = int(np.sum(skilled_mask))
    n_random = int(np.sum(random_mask))
    n_imp = n_skilled + n_random

    # 3. Generate Evaluation Thresholds
    explicit_thresholds = [0.70, 0.72, 0.74, 0.76, 0.7766, 0.78, 0.80, 0.82, 0.84, 0.85, 0.87, 0.90]
    dense_grid = np.linspace(0.50, 0.95, 91).round(4).tolist()
    all_thresholds = sorted(list(set(dense_grid + explicit_thresholds)))

    sweep_records = []

    for t in all_thresholds:
        y_pred = (sims >= t).astype(int)

        tp = int(np.sum((y_true == 1) & (y_pred == 1)))
        fp = int(np.sum((y_true == 0) & (y_pred == 1)))
        tn = int(np.sum((y_true == 0) & (y_pred == 0)))
        fn = int(np.sum((y_true == 1) & (y_pred == 0)))

        far = fp / n_imp if n_imp > 0 else 0.0
        frr = fn / n_gen if n_gen > 0 else 0.0
        tar = 1.0 - frr
        tnr = 1.0 - far
        balanced_acc = (tar + tnr) / 2.0
        overall_acc = (tp + tn) / len(y_true)

        # Subtype error rates
        fp_skilled = int(np.sum(skilled_mask & (y_pred == 1)))
        fp_random = int(np.sum(random_mask & (y_pred == 1)))
        skilled_far = fp_skilled / n_skilled if n_skilled > 0 else 0.0
        random_far = fp_random / n_random if n_random > 0 else 0.0

        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)
        eer_discrepancy = abs(far - frr)

        sweep_records.append({
            "threshold": round(float(t), 4),
            "far": round(far, 4),
            "frr": round(frr, 4),
            "tar": round(tar, 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "accuracy": round(overall_acc, 4),
            "balanced_accuracy": round(balanced_acc, 4),
            "skilled_forgery_far": round(skilled_far, 4),
            "random_impostor_far": round(random_far, 4),
            "skilled_block_rate": round(1.0 - skilled_far, 4),
            "random_block_rate": round(1.0 - random_far, 4),
            "eer_discrepancy": round(eer_discrepancy, 4),
            "tp": tp,
            "fp": fp,
            "tn": tn,
            "fn": fn
        })

    df_sweep = pd.DataFrame(sweep_records)
    Path(output_csv_path).parent.mkdir(parents=True, exist_ok=True)
    df_sweep.to_csv(output_csv_path, index=False)
    print(f"[+] Saved complete validation threshold sweep CSV to: {output_csv_path}")

    # 4. Display Explicit Key Operating Thresholds
    print("\n---------------- KEY OPERATING THRESHOLDS TABLE ----------------")
    df_key = df_sweep[df_sweep["threshold"].isin(explicit_thresholds)].copy()
    format_cols = ["threshold", "tar", "frr", "far", "skilled_forgery_far", "random_impostor_far", "precision", "f1_score", "balanced_accuracy"]
    print(df_key[format_cols].to_string(index=False))
    print("----------------------------------------------------------------\n")

    # 5. Generate Multi-Panel Sweep Visualization Plot
    Path(output_plot_path).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5.5), dpi=150)

    # Subplot 1: Biometric Error Trade-off
    axes[0].plot(df_sweep["threshold"], df_sweep["far"] * 100, color="#DC2626", lw=2, label="FAR (Impostor Approval)")
    axes[0].plot(df_sweep["threshold"], df_sweep["frr"] * 100, color="#2563EB", lw=2, label="FRR (Customer Rejection)")
    axes[0].plot(df_sweep["threshold"], df_sweep["tar"] * 100, color="#10B981", lw=1.8, linestyle=":", label="TAR (Customer Pass)")
    axes[0].plot(df_sweep["threshold"], df_sweep["balanced_accuracy"] * 100, color="#8B5CF6", lw=1.5, linestyle="--", label="Balanced Accuracy")
    axes[0].axvline(x=0.7766, color="#059669", linestyle="-.", lw=1.8, label="Calibrated Cutoff (0.7766)")
    axes[0].axvline(x=0.85, color="#D97706", linestyle="-.", lw=1.5, label="High Cutoff (0.8500)")
    axes[0].set_xlabel("Decision Threshold", fontsize=11, fontweight="medium")
    axes[0].set_ylabel("Rate (%)", fontsize=11, fontweight="medium")
    axes[0].set_title("Biometric Error Rates vs. Threshold", fontsize=12, fontweight="bold")
    axes[0].grid(True, linestyle=":", alpha=0.6)
    axes[0].legend(loc="center right", fontsize=9, frameon=True)

    # Subplot 2: Precision, Recall & F1
    axes[1].plot(df_sweep["threshold"], df_sweep["precision"], color="#F59E0B", lw=2, label="Precision")
    axes[1].plot(df_sweep["threshold"], df_sweep["recall"], color="#3B82F6", lw=2, label="Recall (TAR)")
    axes[1].plot(df_sweep["threshold"], df_sweep["f1_score"], color="#10B981", lw=2.2, label="F1-Score")
    axes[1].axvline(x=0.7766, color="#059669", linestyle="-.", lw=1.8, label="Optimal EER (0.7766)")
    axes[1].axvline(x=0.85, color="#D97706", linestyle="-.", lw=1.5, label="Cutoff 0.8500")
    axes[1].set_xlabel("Decision Threshold", fontsize=11, fontweight="medium")
    axes[1].set_ylabel("Score [0.0 - 1.0]", fontsize=11, fontweight="medium")
    axes[1].set_title("Precision, Recall & F1 vs. Threshold", fontsize=12, fontweight="bold")
    axes[1].grid(True, linestyle=":", alpha=0.6)
    axes[1].legend(loc="lower left", fontsize=9, frameon=True)

    # Subplot 3: Skilled Forgery FAR vs. Random Impostor FAR
    axes[2].plot(df_sweep["threshold"], df_sweep["skilled_forgery_far"] * 100, color="#EF4444", lw=2.2, label="Skilled Forgery FAR")
    axes[2].plot(df_sweep["threshold"], df_sweep["random_impostor_far"] * 100, color="#F97316", lw=2, label="Random Impostor FAR")
    axes[2].axvline(x=0.7766, color="#059669", linestyle="-.", lw=1.8, label="Calibrated Cutoff (0.7766)")
    axes[2].axvline(x=0.85, color="#D97706", linestyle="-.", lw=1.5, label="Cutoff 0.8500")
    axes[2].set_xlabel("Decision Threshold", fontsize=11, fontweight="medium")
    axes[2].set_ylabel("False Acceptance Rate (%)", fontsize=11, fontweight="medium")
    axes[2].set_title("Skilled vs. Random Forgery Vulnerability", fontsize=12, fontweight="bold")
    axes[2].grid(True, linestyle=":", alpha=0.6)
    axes[2].legend(loc="upper right", fontsize=9, frameon=True)

    plt.tight_layout()
    plt.savefig(output_plot_path)
    plt.close()
    print(f"[+] Saved threshold sweep visualization plot to: {output_plot_path}")

    return df_sweep


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run validation threshold sweep")
    parser.add_argument("--checkpoint", default="artifacts/models/best_siamese_model.pt", help="Path to checkpoint")
    parser.add_argument("--val-pairs", default="data/pairs/validation_pairs.csv", help="Path to val pairs CSV")
    parser.add_argument("--output-csv", default="docs/VALIDATION_THRESHOLD_SWEEP.csv", help="Output CSV path")
    parser.add_argument("--output-plot", default="docs/VALIDATION_THRESHOLD_SWEEP.png", help="Output plot path")
    args = parser.parse_args()

    run_threshold_sweep(
        checkpoint_path=args.checkpoint,
        val_pairs_path=args.val_pairs,
        output_csv_path=args.output_csv,
        output_plot_path=args.output_plot
    )
