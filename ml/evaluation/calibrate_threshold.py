"""
Threshold Calibration Pipeline for Siamese Signature Verification.

Calibration Principle:
- Strictly utilizes the VALIDATION cohort (Writers 36 through 45).
- Zero exposure to the Test cohort (Writers 46 through 55).
- Determines the operating threshold at the validation Equal Error Rate (EER).
- Saves the calibrated threshold to a machine-readable JSON artifact.
- The frozen threshold is subsequently loaded for unbiased, leakage-free test evaluation.
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import roc_curve, auc, precision_recall_fscore_support, accuracy_score

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.dataset import SignaturePairDataset


def calibrate_threshold(
    checkpoint_path: str = "artifacts/models/best_siamese_model.pt",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    output_artifact_path: str = "artifacts/models/calibrated_threshold.json",
    plot_path: str = "docs/VAL_CALIBRATION_CURVES.png",
    batch_size: int = 32
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("==================================================")
    print("   SIAMESE NETWORK THRESHOLD CALIBRATION")
    print("==================================================")
    print(f"[*] Device                   : {device}")
    print(f"[*] Checkpoint               : {checkpoint_path}")
    print(f"[*] Validation Pairs Source  : {val_pairs_path}")
    print(f"[*] Output Artifact          : {output_artifact_path}")

    # 1. Load Checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    embedding_dim = checkpoint.get("embedding_dim", 256)

    model = SiameseSignatureNet(embedding_dim=embedding_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # 2. Load Validation Dataset
    val_dataset = SignaturePairDataset(val_pairs_path, cache_in_memory=True, augment=False)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    print(f"[+] Loaded {len(val_dataset)} validation pairs (Writers 36-45).")

    all_labels = []
    all_distances = []
    all_sims = []
    pair_types = []

    with torch.no_grad():
        for batch in val_loader:
            img1 = batch["image_1"].to(device)
            img2 = batch["image_2"].to(device)
            labels = batch["label"].to(device)

            emb1, emb2 = model(img1, img2)
            dist = model.compute_distance(emb1, emb2)
            sim = model.compute_similarity(dist)

            all_labels.extend(labels.cpu().numpy().tolist())
            all_distances.extend(dist.cpu().numpy().tolist())
            all_sims.extend(sim.cpu().numpy().tolist())
            pair_types.extend(batch["pair_type"])

    y_true = np.array(all_labels, dtype=int)
    sims = np.array(all_sims, dtype=float)
    dists = np.array(all_distances, dtype=float)

    # 3. Compute ROC Curve and Equal Error Rate (EER) on Validation Data
    fpr, tpr, thresholds = roc_curve(y_true, sims, pos_label=1)
    fnr = 1.0 - tpr
    roc_auc = auc(fpr, tpr)

    # Optimal operating point where False Positive Rate == False Negative Rate
    eer_idx = int(np.nanargmin(np.absolute(fpr - fnr)))
    val_eer = float((fpr[eer_idx] + fnr[eer_idx]) / 2.0)
    calibrated_threshold = float(thresholds[eer_idx])

    # 4. Evaluate Validation Performance at Calibrated Threshold
    y_pred = (sims >= calibrated_threshold).astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    frr = float(fn / (tp + fn)) if (tp + fn) > 0 else 0.0
    tar = float(1.0 - frr)
    acc = float(accuracy_score(y_true, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)

    # Granular breakdown by pair type
    skilled_indices = [i for i, pt in enumerate(pair_types) if pt == "skilled_forgery"]
    random_indices = [i for i, pt in enumerate(pair_types) if pt == "random_forgery"]
    genuine_indices = [i for i, pt in enumerate(pair_types) if pt == "genuine_genuine"]

    skilled_far = float(np.mean(sims[skilled_indices] >= calibrated_threshold)) if skilled_indices else 0.0
    random_far = float(np.mean(sims[random_indices] >= calibrated_threshold)) if random_indices else 0.0

    print("\n---------------- CALIBRATION RESULTS ----------------")
    print(f"Validation EER               : {val_eer * 100:.2f}%")
    print(f"Calibrated Optimal Threshold : {calibrated_threshold:.4f}")
    print(f"Validation AUC-ROC           : {roc_auc:.4f}")
    print(f"Validation Accuracy          : {acc * 100:.2f}%")
    print(f"Validation FAR               : {far * 100:.2f}%")
    print(f"Validation FRR               : {frr * 100:.2f}%")
    print(f"Validation TAR (1 - FRR)     : {tar * 100:.2f}%")
    print(f"  -> Skilled Forgery FAR     : {skilled_far * 100:.2f}%")
    print(f"  -> Random Impostor FAR     : {random_far * 100:.2f}%")
    print(f"Validation Precision / Recall: {prec:.4f} / {rec:.4f} (F1: {f1:.4f})")
    print("-----------------------------------------------------\n")

    # 5. Save Machine-Readable Calibration Artifact
    out_file = Path(output_artifact_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    calibration_artifact = {
        "calibrated_threshold": round(calibrated_threshold, 6),
        "calibration_method": "validation_eer_minimization",
        "validation_eer": round(val_eer, 6),
        "validation_auc_roc": round(float(roc_auc), 6),
        "validation_accuracy": round(acc, 6),
        "validation_far": round(far, 6),
        "validation_frr": round(frr, 6),
        "validation_tar": round(tar, 6),
        "validation_precision": round(float(prec), 6),
        "validation_recall": round(float(rec), 6),
        "validation_f1_score": round(float(f1), 6),
        "skilled_forgery_far": round(skilled_far, 6),
        "random_impostor_far": round(random_far, 6),
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "total_samples": len(y_true)
        },
        "dataset_split": {
            "validation_pairs_count": len(val_dataset),
            "validation_writers": list(range(36, 46)),
            "protocol": "writer_independent_open_set",
            "leakage_free": True
        },
        "checkpoint_evaluated": str(checkpoint_path),
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

    with open(out_file, "w") as f:
        json.dump(calibration_artifact, f, indent=2)
    print(f"[+] Saved calibrated threshold artifact to: {out_file}")

    # 6. Plot Validation Calibration Curves
    try:
        plot_p = Path(plot_path)
        plot_p.parent.mkdir(parents=True, exist_ok=True)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)

        # Plot 1: Validation ROC Curve
        ax1.plot(fpr, tpr, color="#2563EB", lw=2, label=f"Validation ROC (AUC = {roc_auc:.4f})")
        ax1.plot([0, 1], [0, 1], color="#94A3B8", lw=1.5, linestyle="--", label="Chance Level")
        ax1.scatter([fpr[eer_idx]], [tpr[eer_idx]], color="#DC2626", s=60, zorder=5,
                    label=f"EER = {val_eer * 100:.2f}% (Thresh = {calibrated_threshold:.4f})")
        ax1.set_xlim([-0.02, 1.02])
        ax1.set_ylim([-0.02, 1.02])
        ax1.set_xlabel("False Positive Rate (FAR)", fontsize=11, fontweight="medium")
        ax1.set_ylabel("True Positive Rate (TAR)", fontsize=11, fontweight="medium")
        ax1.set_title("Validation ROC Curve", fontsize=12, fontweight="bold")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="lower right", frameon=True)

        # Plot 2: FAR and FRR vs. Threshold
        eval_thresh_range = np.linspace(0.4, 0.95, 200)
        far_curve = [float(np.mean(sims[y_true == 0] >= t)) for t in eval_thresh_range]
        frr_curve = [float(np.mean(sims[y_true == 1] < t)) for t in eval_thresh_range]

        ax2.plot(eval_thresh_range, far_curve, color="#DC2626", lw=2, label="FAR (False Acceptance)")
        ax2.plot(eval_thresh_range, frr_curve, color="#2563EB", lw=2, label="FRR (False Rejection)")
        ax2.axvline(x=calibrated_threshold, color="#10B981", linestyle="--", lw=1.8,
                    label=f"Calibrated Cutoff ({calibrated_threshold:.4f})")
        ax2.set_xlabel("Similarity Threshold", fontsize=11, fontweight="medium")
        ax2.set_ylabel("Error Rate", fontsize=11, fontweight="medium")
        ax2.set_title("Validation FAR / FRR vs. Threshold", fontsize=12, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="upper center", frameon=True)

        plt.tight_layout()
        plt.savefig(plot_p)
        plt.close()
        print(f"[+] Saved validation calibration curves to: {plot_p}")
    except Exception as e:
        print(f"[-] Could not generate calibration plot: {e}")

    return calibration_artifact


def main():
    parser = argparse.ArgumentParser(description="Calibrate Siamese threshold on validation cohort")
    parser.add_argument("--checkpoint", default="artifacts/models/best_siamese_model.pt", help="Path to model checkpoint")
    parser.add_argument("--val-pairs", default="data/pairs/validation_pairs.csv", help="Path to validation pairs CSV")
    parser.add_argument("--output", default="artifacts/models/calibrated_threshold.json", help="Path to output JSON artifact")
    parser.add_argument("--plot", default="docs/VAL_CALIBRATION_CURVES.png", help="Path to output plot PNG")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for evaluation")
    args = parser.parse_args()

    calibrate_threshold(
        checkpoint_path=args.checkpoint,
        val_pairs_path=args.val_pairs,
        output_artifact_path=args.output,
        plot_path=args.plot,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
