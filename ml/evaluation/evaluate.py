"""
Model Evaluation Pipeline for Siamese Signature Verification.

Evaluates the trained Siamese model on the unseen open-set test cohort (Writers 46-55).
Generates biometric metrics (FAR, FRR, EER, AUC-ROC), produces docs/MODEL_EVALUATION_REPORT.md,
and plots docs/ROC_CURVE.png.
"""

import sys
import json
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import numpy as np
import matplotlib.pyplot as plt
import torch
from torch.utils.data import DataLoader

from ml.models.siamese_network import SiameseSignatureNet
from ml.models.dataset import SignaturePairDataset
from ml.evaluation.metrics import calculate_biometric_metrics


def evaluate_model(
    checkpoint_path: str = "artifacts/models/best_siamese_model.pt",
    test_pairs_path: str = "data/pairs/test_pairs.csv",
    docs_report_path: str = "docs/MODEL_EVALUATION_REPORT.md",
    roc_plot_path: str = "docs/ROC_CURVE.png",
    batch_size: int = 32
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("==================================================")
    print("   SIAMESE SIGNATURE VERIFICATION EVALUATION")
    print("==================================================")
    print(f"[*] Device                 : {device}")
    print(f"[*] Checkpoint             : {checkpoint_path}")
    print(f"[*] Test Pairs Source      : {test_pairs_path}")

    # 1. Load Checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    embedding_dim = checkpoint.get("embedding_dim", 256)
    threshold = checkpoint.get("optimal_threshold", 0.75)

    model = SiameseSignatureNet(embedding_dim=embedding_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # 2. Load Test Data
    test_dataset = SignaturePairDataset(test_pairs_path, cache_in_memory=True, augment=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    print(f"[+] Loaded {len(test_dataset)} open-set test pairs.")

    all_labels = []
    all_distances = []
    all_sims = []
    pair_types = []

    with torch.no_grad():
        for batch in test_loader:
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

    y_true = np.array(all_labels)
    sims = np.array(all_sims)
    dists = np.array(all_distances)

    # 3. Overall Biometric Metrics
    metrics = calculate_biometric_metrics(y_true, sims, optimal_threshold=threshold)

    # Breakdown by negative pair type
    skilled_indices = [i for i, pt in enumerate(pair_types) if pt == "skilled_forgery"]
    random_indices = [i for i, pt in enumerate(pair_types) if pt == "random_forgery"]
    genuine_indices = [i for i, pt in enumerate(pair_types) if pt == "genuine_genuine"]

    skilled_preds = (sims[skilled_indices] >= threshold).astype(int) if skilled_indices else []
    random_preds = (sims[random_indices] >= threshold).astype(int) if random_indices else []
    genuine_preds = (sims[genuine_indices] >= threshold).astype(int) if genuine_indices else []

    # Skilled forgery FAR: % of skilled forgeries wrongly accepted
    skilled_far = float(np.mean(skilled_preds)) if len(skilled_preds) > 0 else 0.0
    # Random impostor FAR: % of random signatures wrongly accepted
    random_far = float(np.mean(random_preds)) if len(random_preds) > 0 else 0.0
    # Genuine FRR: % of genuine signatures wrongly rejected
    genuine_frr = float(1.0 - np.mean(genuine_preds)) if len(genuine_preds) > 0 else 0.0

    print("\n---------------- EVALUATION RESULTS ----------------")
    print(f"Equal Error Rate (EER)     : {metrics['eer']*100:.2f}%")
    print(f"Operational Threshold      : {threshold:.4f}")
    print(f"Area Under ROC (AUC-ROC)   : {metrics['auc_roc']:.4f}")
    print(f"Overall Accuracy           : {metrics['accuracy']*100:.2f}%")
    print(f"False Acceptance Rate (FAR): {metrics['far']*100:.2f}%")
    print(f"False Rejection Rate (FRR) : {metrics['frr']*100:.2f}%")
    print(f"  -> Skilled Forgery FAR   : {skilled_far*100:.2f}% (Hard Negatives)")
    print(f"  -> Random Impostor FAR   : {random_far*100:.2f}% (Cross-Writer)")
    print(f"Precision / Recall / F1    : {metrics['precision']:.4f} / {metrics['recall']:.4f} / {metrics['f1_score']:.4f}")
    print("----------------------------------------------------\n")

    # 4. Generate ROC Curve Plot
    try:
        fpr = metrics["roc_curve"]["fpr"]
        tpr = metrics["roc_curve"]["tpr"]
        plt.figure(figsize=(8, 6), dpi=150)
        plt.plot(fpr, tpr, color="#2563EB", lw=2, label=f"Siamese ResNet (AUC = {metrics['auc_roc']:.4f})")
        plt.plot([0, 1], [0, 1], color="#94A3B8", lw=1.5, linestyle="--", label="Random Classifier")
        plt.scatter([metrics["far"]], [metrics["recall"]], color="#DC2626", s=60, zorder=5,
                    label=f"EER Operating Point ({metrics['eer']*100:.2f}%)")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Acceptance Rate (FAR)", fontsize=11)
        plt.ylabel("True Acceptance Rate (1 - FRR)", fontsize=11)
        plt.title("Receiver Operating Characteristic (ROC) — Signature Verification", fontsize=12, weight="bold")
        plt.legend(loc="lower right")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()
        plt.savefig(roc_plot_path, bbox_inches="tight")
        plt.close()
        print(f"[+] ROC Curve plot saved to: {roc_plot_path}")
    except Exception as e:
        print(f"[-] Warning: Failed to render ROC plot: {e}")

    # 5. Generate Markdown Report
    cm = metrics["confusion_matrix"]
    md_report = f"""# Siamese Neural Network: Model Evaluation Report

> [!NOTE]
> Evaluation performed strictly on the **Unseen Test Cohort** (CEDAR Writers 46 through 55).
> **Writer-Independent (Open-Set)** protocol ensures zero identity leakage between training and testing.

## 1. High-Level Performance Metrics

| Metric | Measured Value | Standard Target | Interpretation |
| :--- | :--- | :--- | :--- |
| **Equal Error Rate (EER)** | **{metrics['eer']*100:.2f}%** | $< 10.0\%$ | Industry benchmark for biometric accuracy |
| **AUC-ROC** | **{metrics['auc_roc']:.4f}** | $> 0.9000$ | Overall discrimination capability across all thresholds |
| **Operating Threshold** | **{threshold:.4f}** | $[0.50 - 0.85]$ | Balanced decision cutoff |
| **Overall Accuracy** | **{metrics['accuracy']*100:.2f}%** | $> 85.0\%$ | Total correct verification decisions |
| **False Acceptance Rate (FAR)**| **{metrics['far']*100:.2f}%** | $< 8.0\%$ | Unauthorized signatures mistakenly approved |
| **False Rejection Rate (FRR)**| **{metrics['frr']*100:.2f}%** | $< 8.0\%$ | Genuine customer signatures mistakenly blocked |
| **Precision** | **{metrics['precision']:.4f}** | $> 0.85$ | Reliability of an approval decision |
| **Recall / True Positive Rate**| **{metrics['recall']:.4f}** | $> 0.85$ | Genuine customer pass rate |
| **F1-Score** | **{metrics['f1_score']:.4f}** | $> 0.85$ | Harmonic mean of precision and recall |

## 2. Granular Fraud Analysis: Skilled vs. Random Forgery

In banking transactions, forgeries fall into two distinct forensic classes:

| Forgery Type | Sample Count | False Acceptance Rate (FAR) | Defense Effectiveness |
| :--- | :--- | :--- | :--- |
| **Skilled Forgeries** (Practiced mimicry of victim) | {len(skilled_indices)} | **{skilled_far*100:.2f}%** | {100.0 - skilled_far*100:.2f}% Block Rate |
| **Random Impostors** (Cross-writer foreign signatures) | {len(random_indices)} | **{random_far*100:.2f}%** | {100.0 - random_far*100:.2f}% Block Rate |
| **Genuine Customers** (Legitimate account holder) | {len(genuine_indices)} | **{genuine_frr*100:.2f}% FRR** | {100.0 - genuine_frr*100:.2f}% Pass Rate |

## 3. Confusion Matrix

| Actual \\ Predicted | Predicted: Genuine (Score $\\ge {threshold:.4f}$) | Predicted: Forged (Score $< {threshold:.4f}$) | Total |
| :--- | :--- | :--- | :--- |
| **Actual Genuine** | **{cm['true_positives']} (TP)** | {cm['false_negatives']} (FN - False Rejection) | {cm['true_positives'] + cm['false_negatives']} |
| **Actual Forged** | {cm['false_positives']} (FP - False Acceptance) | **{cm['true_negatives']} (TN)** | {cm['false_positives'] + cm['true_negatives']} |
| **Total** | {cm['true_positives'] + cm['false_positives']} | {cm['false_negatives'] + cm['true_negatives']} | **{cm['total_samples']}** |

## 4. Visual Artifacts

* **ROC Curve Plot:** `docs/ROC_CURVE.png`
* **Model Checkpoint:** `{checkpoint_path}`
* **Test Dataset Source:** `{test_pairs_path}`
"""
    with open(docs_report_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"[+] Markdown Evaluation Report saved to: {docs_report_path}")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate Siamese Signature Verification Network")
    parser.add_argument("--checkpoint", default="artifacts/models/best_siamese_model.pt", help="Model checkpoint path")
    parser.add_argument("--test-pairs", default="data/pairs/test_pairs.csv", help="Test pairs CSV")
    args = parser.parse_args()

    evaluate_model(checkpoint_path=args.checkpoint, test_pairs_path=args.test_pairs)


if __name__ == "__main__":
    main()
