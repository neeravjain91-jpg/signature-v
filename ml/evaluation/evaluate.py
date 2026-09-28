"""
Final Unbiased Model Evaluation Pipeline for Siamese Signature Verification.

Methodology Protocol:
- Model weights: FROZEN (artifacts/models/best_siamese_model.pt)
- Operating threshold: FROZEN (calibrated strictly on validation data via ml/evaluation/calibrate_threshold.py)
- Evaluation cohort: TEST DATA ONLY (Writers 46 through 55, 1200 open-set pairs)
- Zero Identity Leakage: Disjoint writer sets across Train (1-35), Val (36-45), Test (46-55).
- Zero Threshold Leakage: Test data NEVER used to tune, calibrate, or adjust the threshold.

Generates:
- Standard Biometric Metrics: FAR, FRR, TAR, EER, ROC-AUC, Accuracy, Precision, Recall, F1
- Granular Forgery Breakdown: Skilled Forgery FAR vs. Random Impostor FAR
- Forensic Error Case Extraction: False Acceptances (FA) and False Rejections (FR)
- Diagnostic Visual Plots: ROC Curve, FAR/FRR Curve, and Genuine/Impostor Score Distributions
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


def evaluate_test_cohort(
    checkpoint_path: str = "artifacts/models/best_siamese_model.pt",
    calibrated_threshold_path: str = "artifacts/models/calibrated_threshold.json",
    test_pairs_path: str = "data/pairs/test_pairs.csv",
    output_results_path: str = "artifacts/evaluation/test_evaluation_results.json",
    fa_cases_path: str = "artifacts/evaluation/false_acceptance_cases.json",
    fr_cases_path: str = "artifacts/evaluation/false_rejection_cases.json",
    roc_plot_path: str = "docs/ROC_CURVE.png",
    far_frr_plot_path: str = "docs/FAR_FRR_CURVE.png",
    dist_plot_path: str = "docs/SCORE_DISTRIBUTIONS.png",
    batch_size: int = 32
) -> dict:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("==================================================")
    print("   UNBIASED SIAMESE NETWORK TEST EVALUATION")
    print("==================================================")
    print(f"[*] Device                   : {device}")
    print(f"[*] Checkpoint               : {checkpoint_path}")
    print(f"[*] Calibrated Threshold Src : {calibrated_threshold_path}")
    print(f"[*] Test Pairs Source        : {test_pairs_path}")

    # 1. Load Frozen Calibrated Threshold
    thresh_file = Path(calibrated_threshold_path)
    if not thresh_file.exists():
        raise FileNotFoundError(
            f"Calibrated threshold artifact not found at '{calibrated_threshold_path}'. "
            "Run ml/evaluation/calibrate_threshold.py first on validation data!"
        )

    with open(thresh_file, "r") as f:
        calib_data = json.load(f)
    frozen_threshold = float(calib_data.get("frozen_threshold", calib_data.get("calibrated_threshold")))
    print(f"[+] Loaded FROZEN threshold from validation calibration: {frozen_threshold:.4f}")

    # 2. Load Frozen Model Checkpoint
    checkpoint = torch.load(checkpoint_path, map_location=device)
    embedding_dim = checkpoint.get("embedding_dim", 256)

    model = SiameseSignatureNet(embedding_dim=embedding_dim)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()

    # 3. Load Test Dataset (Writers 46-55)
    test_dataset = SignaturePairDataset(test_pairs_path, cache_in_memory=True, augment=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    print(f"[+] Loaded {len(test_dataset)} open-set test pairs (Writers 46-55).")

    all_labels = []
    all_distances = []
    all_sims = []
    all_img1 = []
    all_img2 = []
    all_pair_types = []
    all_w1 = []
    all_w2 = []

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
            all_pair_types.extend(batch["pair_type"])
            all_w1.extend(batch["writer_1"].numpy().tolist() if torch.is_tensor(batch["writer_1"]) else batch["writer_1"])
            all_w2.extend(batch["writer_2"].numpy().tolist() if torch.is_tensor(batch["writer_2"]) else batch["writer_2"])

    all_img1 = test_dataset.df["image_1_path"].tolist()
    all_img2 = test_dataset.df["image_2_path"].tolist()

    y_true = np.array(all_labels, dtype=int)
    sims = np.array(all_sims, dtype=float)
    dists = np.array(all_distances, dtype=float)

    # 4. Compute Test Set ROC & Test EER (For Diagnostic Comparison with Frozen Threshold)
    fpr, tpr, thresholds = roc_curve(y_true, sims, pos_label=1)
    fnr = 1.0 - tpr
    test_roc_auc = float(auc(fpr, tpr))
    test_eer_idx = int(np.nanargmin(np.absolute(fpr - fnr)))
    test_eer = float((fpr[test_eer_idx] + fnr[test_eer_idx]) / 2.0)
    test_eer_threshold = float(thresholds[test_eer_idx])

    # 5. Evaluate Performance STRICTLY at the Frozen Calibrated Threshold
    y_pred = (sims >= frozen_threshold).astype(int)

    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    far = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    frr = float(fn / (tp + fn)) if (tp + fn) > 0 else 0.0
    tar = float(1.0 - frr)
    acc = float(accuracy_score(y_true, y_pred))
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)

    # 6. Granular Breakdown by Impostor Subtype
    skilled_indices = [i for i, pt in enumerate(all_pair_types) if pt == "skilled_forgery"]
    random_indices = [i for i, pt in enumerate(all_pair_types) if pt == "random_forgery"]
    genuine_indices = [i for i, pt in enumerate(all_pair_types) if pt == "genuine_genuine"]

    skilled_far = float(np.mean(sims[skilled_indices] >= frozen_threshold)) if skilled_indices else 0.0
    random_far = float(np.mean(sims[random_indices] >= frozen_threshold)) if random_indices else 0.0
    random_block_rate = float(1.0 - random_far)
    skilled_block_rate = float(1.0 - skilled_far)

    print("\n---------------- UNBIASED TEST RESULTS ----------------")
    print(f"Operating Threshold (FROZEN) : {frozen_threshold:.4f}")
    print(f"Test Equal Error Rate (EER)  : {test_eer * 100:.2f}%")
    print(f"Test Area Under ROC (AUC-ROC): {test_roc_auc:.4f}")
    print(f"Overall Accuracy             : {acc * 100:.2f}%")
    print(f"False Acceptance Rate (FAR)  : {far * 100:.2f}% (Total impostors wrongly accepted)")
    print(f"False Rejection Rate (FRR)   : {frr * 100:.2f}% (Genuine signatures wrongly blocked)")
    print(f"True Acceptance Rate (TAR)   : {tar * 100:.2f}% (Genuine signatures cleared)")
    print(f"  -> Skilled Forgery FAR     : {skilled_far * 100:.2f}% (Hard Negatives: Imitations)")
    print(f"  -> Random Impostor FAR     : {random_far * 100:.2f}% (Cross-Writer Unskilled)")
    print(f"  -> Random Impostor Block   : {random_block_rate * 100:.2f}% (1 - FAR_random)")
    print(f"Precision / Recall / F1      : {prec:.4f} / {rec:.4f} / {f1:.4f}")
    print(f"Confusion Matrix: TP={tp}, FP={fp}, TN={tn}, FN={fn} (Total={len(y_true)})")
    print("-------------------------------------------------------\n")

    # 7. Forensic Extraction of False Acceptance (FA) & False Rejection (FR) Cases
    fa_cases = []
    fr_cases = []

    for i in range(len(y_true)):
        case_info = {
            "index": i,
            "image_1": all_img1[i],
            "image_2": all_img2[i],
            "writer_1": all_w1[i],
            "writer_2": all_w2[i],
            "pair_type": all_pair_types[i],
            "ground_truth_label": int(y_true[i]),
            "predicted_label": int(y_pred[i]),
            "similarity_score": round(float(sims[i]), 4),
            "euclidean_distance": round(float(dists[i]), 4),
            "threshold_used": round(frozen_threshold, 4)
        }
        # False Acceptance: Actual Forged (0), but Predicted Genuine (1)
        if y_true[i] == 0 and y_pred[i] == 1:
            fa_cases.append(case_info)
        # False Rejection: Actual Genuine (1), but Predicted Forged (0)
        elif y_true[i] == 1 and y_pred[i] == 0:
            fr_cases.append(case_info)

    # Sort FA cases by highest similarity (most severe false approvals)
    fa_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
    # Sort FR cases by lowest similarity (most severe false blocks)
    fr_cases.sort(key=lambda x: x["similarity_score"])

    # Save FA and FR cases
    Path(fa_cases_path).parent.mkdir(parents=True, exist_ok=True)
    with open(fa_cases_path, "w") as f:
        json.dump({
            "total_false_acceptances": len(fa_cases),
            "total_impostor_pairs": len(skilled_indices) + len(random_indices),
            "far": round(far, 4),
            "skilled_far": round(skilled_far, 4),
            "random_far": round(random_far, 4),
            "top_false_acceptances": fa_cases[:25]
        }, f, indent=2)
    print(f"[+] Saved {len(fa_cases)} False Acceptance cases to: {fa_cases_path}")

    Path(fr_cases_path).parent.mkdir(parents=True, exist_ok=True)
    with open(fr_cases_path, "w") as f:
        json.dump({
            "total_false_rejections": len(fr_cases),
            "total_genuine_pairs": len(genuine_indices),
            "frr": round(frr, 4),
            "tar": round(tar, 4),
            "top_false_rejections": fr_cases[:25]
        }, f, indent=2)
    print(f"[+] Saved {len(fr_cases)} False Rejection cases to: {fr_cases_path}")

    # 8. Save Machine-Readable Test Results
    test_results = {
        "frozen_threshold_used": round(frozen_threshold, 6),
        "calibration_provenance": "Validation Cohort (Writers 36-45), Zero Test Leakage",
        "test_eer": round(test_eer, 6),
        "test_eer_threshold": round(test_eer_threshold, 6),
        "auc_roc": round(test_roc_auc, 6),
        "accuracy": round(acc, 6),
        "far": round(far, 6),
        "frr": round(frr, 6),
        "tar": round(tar, 6),
        "precision": round(float(prec), 6),
        "recall": round(float(rec), 6),
        "f1_score": round(float(f1), 6),
        "skilled_forgery_far": round(skilled_far, 6),
        "skilled_forgery_block_rate": round(skilled_block_rate, 6),
        "random_impostor_far": round(random_far, 6),
        "random_impostor_block_rate": round(random_block_rate, 6),
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "total_samples": len(y_true)
        },
        "writer_cohorts": {
            "training_writers": list(range(1, 36)),
            "validation_writers": list(range(36, 46)),
            "test_writers": list(range(46, 56)),
            "writer_leakage_present": False
        },
        "test_sample_breakdown": {
            "genuine_pairs": len(genuine_indices),
            "skilled_forgery_pairs": len(skilled_indices),
            "random_forgery_pairs": len(random_indices),
            "total_test_pairs": len(y_true)
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat()
    }

    Path(output_results_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_results_path, "w") as f:
        json.dump(test_results, f, indent=2)
    print(f"[+] Saved complete test evaluation results to: {output_results_path}")

    # 9. Generate Diagnostic Visualizations
    # Plot A: ROC Curve
    try:
        Path(roc_plot_path).parent.mkdir(parents=True, exist_ok=True)
        plt.figure(figsize=(8, 6), dpi=150)
        plt.plot(fpr, tpr, color="#2563EB", lw=2.2, label=f"Siamese ResNet Test ROC (AUC = {test_roc_auc:.4f})")
        plt.plot([0, 1], [0, 1], color="#94A3B8", lw=1.5, linestyle="--", label="Random Chance (AUC = 0.50)")
        plt.scatter([far], [tar], color="#10B981", s=75, zorder=5,
                    label=f"Frozen Operating Point (Thresh = {frozen_threshold:.4f})\nFAR = {far * 100:.2f}%, TAR = {tar * 100:.2f}%")
        plt.scatter([fpr[test_eer_idx]], [tpr[test_eer_idx]], color="#DC2626", s=60, zorder=4,
                    label=f"Test EER Ref Point ({test_eer * 100:.2f}%)")
        plt.xlim([-0.02, 1.02])
        plt.ylim([-0.02, 1.02])
        plt.xlabel("False Acceptance Rate (FAR)", fontsize=11, fontweight="medium")
        plt.ylabel("True Acceptance Rate (TAR)", fontsize=11, fontweight="medium")
        plt.title("Receiver Operating Characteristic (ROC) — Unseen Test Cohort", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="lower right", frameon=True)
        plt.tight_layout()
        plt.savefig(roc_plot_path)
        plt.close()
        print(f"[+] Saved ROC curve to: {roc_plot_path}")
    except Exception as e:
        print(f"[-] Could not plot ROC: {e}")

    # Plot B: FAR and FRR vs. Threshold Curve
    try:
        Path(far_frr_plot_path).parent.mkdir(parents=True, exist_ok=True)
        threshold_range = np.linspace(0.40, 0.95, 200)
        test_far_curve = [float(np.mean(sims[y_true == 0] >= t)) for t in threshold_range]
        test_frr_curve = [float(np.mean(sims[y_true == 1] < t)) for t in threshold_range]

        plt.figure(figsize=(8, 6), dpi=150)
        plt.plot(threshold_range, test_far_curve, color="#DC2626", lw=2, label="False Acceptance Rate (FAR)")
        plt.plot(threshold_range, test_frr_curve, color="#2563EB", lw=2, label="False Rejection Rate (FRR)")
        plt.axvline(x=frozen_threshold, color="#10B981", linestyle="--", lw=2,
                    label=f"Frozen Operating Threshold ({frozen_threshold:.4f})")
        plt.xlabel("Decision Similarity Threshold", fontsize=11, fontweight="medium")
        plt.ylabel("Error Rate", fontsize=11, fontweight="medium")
        plt.title("FAR / FRR Error Trade-off Curves (Unseen Test Cohort)", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper center", frameon=True)
        plt.tight_layout()
        plt.savefig(far_frr_plot_path)
        plt.close()
        print(f"[+] Saved FAR/FRR curve to: {far_frr_plot_path}")
    except Exception as e:
        print(f"[-] Could not plot FAR/FRR curve: {e}")

    # Plot C: Genuine vs. Impostor Score Distributions
    try:
        Path(dist_plot_path).parent.mkdir(parents=True, exist_ok=True)
        genuine_scores = sims[y_true == 1]
        skilled_scores = sims[skilled_indices]
        random_scores = sims[random_indices]

        plt.figure(figsize=(9, 5.5), dpi=150)
        bins = np.linspace(0.4, 1.0, 45)
        plt.hist(genuine_scores, bins=bins, alpha=0.55, color="#10B981", label=f"Genuine Pairs (N={len(genuine_scores)})", density=True)
        plt.hist(skilled_scores, bins=bins, alpha=0.55, color="#DC2626", label=f"Skilled Forgeries (N={len(skilled_scores)})", density=True)
        plt.hist(random_scores, bins=bins, alpha=0.55, color="#F59E0B", label=f"Random Impostors (N={len(random_scores)})", density=True)
        plt.axvline(x=frozen_threshold, color="#1E293B", linestyle="--", lw=2.2,
                    label=f"Calibrated Threshold ({frozen_threshold:.4f})")

        plt.xlabel("Siamese Similarity Score", fontsize=11, fontweight="medium")
        plt.ylabel("Probability Density", fontsize=11, fontweight="medium")
        plt.title("Similarity Score Distributions: Genuine vs. Skilled vs. Random", fontsize=12, fontweight="bold")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.legend(loc="upper left", frameon=True)
        plt.tight_layout()
        plt.savefig(dist_plot_path)
        plt.close()
        print(f"[+] Saved score distribution plot to: {dist_plot_path}")
    except Exception as e:
        print(f"[-] Could not plot score distributions: {e}")

    return test_results


def main():
    parser = argparse.ArgumentParser(description="Evaluate Siamese verification model on unbiased test cohort")
    parser.add_argument("--checkpoint", default="artifacts/models/best_siamese_model.pt", help="Path to model checkpoint")
    parser.add_argument("--calibrated-threshold", default="artifacts/models/calibrated_threshold.json", help="Path to calibrated threshold JSON")
    parser.add_argument("--test-pairs", default="data/pairs/test_pairs.csv", help="Path to test pairs CSV")
    parser.add_argument("--output", default="artifacts/evaluation/test_evaluation_results.json", help="Path to output results JSON")
    parser.add_argument("--roc-plot", default="docs/ROC_CURVE.png", help="Path to save ROC curve plot")
    parser.add_argument("--far-frr-plot", default="docs/FAR_FRR_CURVE.png", help="Path to save FAR/FRR curve plot")
    parser.add_argument("--dist-plot", default="docs/SCORE_DISTRIBUTIONS.png", help="Path to save score distributions plot")
    parser.add_argument("--fa-cases", default="artifacts/evaluation/false_acceptance_cases.json", help="Path to save FA cases JSON")
    parser.add_argument("--fr-cases", default="artifacts/evaluation/false_rejection_cases.json", help="Path to save FR cases JSON")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size for evaluation")
    args = parser.parse_args()

    evaluate_test_cohort(
        checkpoint_path=args.checkpoint,
        calibrated_threshold_path=args.calibrated_threshold,
        test_pairs_path=args.test_pairs,
        output_results_path=args.output,
        fa_cases_path=args.fa_cases,
        fr_cases_path=args.fr_cases,
        roc_plot_path=args.roc_plot,
        far_frr_plot_path=args.far_frr_plot,
        dist_plot_path=args.dist_plot,
        batch_size=args.batch_size
    )


if __name__ == "__main__":
    main()
