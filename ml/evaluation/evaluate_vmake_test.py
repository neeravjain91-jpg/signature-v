"""
SIGNATURE VMAKE — Final Model Evaluation on Held-Out Test Cohort.

Evaluates only the two approved VMAKE models:
- Track A: scikit-learn Classical Baseline (SVM)
- Track B: Hugging Face Vision Transformer (ViT)

Evaluates on the locked test set (Writers 46..55, 1,200 pairs)
with zero writer overlap with training (1..35) or validation (36..45).
"""

import sys
import os
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.baselines.classical_classifier import ClassicalSklearnVerifier
from ml.models.transformer_signature_model import VisionTransformerVerifier
from ml.evaluation.metrics import calculate_biometric_metrics


def evaluate_vmake_models(test_csv_path: str = "data/pairs/test_pairs.csv"):
    print("=" * 70)
    print("      SIGNATURE VMAKE — DUAL-TRACK TEST COHORT EVALUATION")
    print("=" * 70)

    test_df = pd.read_csv(test_csv_path)
    print(f"Loaded {len(test_df)} test pairs from {test_csv_path}")

    # Track A: scikit-learn
    print("\n--- Evaluating Track A: scikit-learn Classical SVM Baseline ---")
    v_a = ClassicalSklearnVerifier("artifacts/models/classical_svm_model.joblib")
    sims_a = []
    latencies_a = []
    t0_a = time.time()
    for _, row in test_df.iterrows():
        p1 = row["image_1_path"]
        p2 = row["image_2_path"]
        t_start = time.time()
        res = v_a.verify(p1, p2)
        latencies_a.append((time.time() - t_start) * 1000.0)
        sims_a.append(res.similarity_score)

    y_test = test_df["label"].values.astype(int)
    sims_a = np.array(sims_a, dtype=float)
    metrics_a = calculate_biometric_metrics(y_test, sims_a, optimal_threshold=float(v_a.threshold))
    metrics_a["average_latency_ms"] = float(np.mean(latencies_a))
    metrics_a["model_name"] = v_a.model_name
    metrics_a["model_version"] = v_a.model_version
    metrics_a["threshold_used"] = float(v_a.threshold)

    print(f"Track A Test AUC-ROC : {metrics_a['auc_roc']:.4f}")
    print(f"Track A Test EER     : {metrics_a['eer']:.4f}")
    print(f"Track A Test Accuracy: {metrics_a['accuracy']:.4f}")
    print(f"Track A Test FAR     : {metrics_a['far']:.4f}")
    print(f"Track A Test FRR     : {metrics_a['frr']:.4f}")
    print(f"Track A Test F1      : {metrics_a['f1_score']:.4f}")
    print(f"Track A Avg Latency  : {metrics_a['average_latency_ms']:.2f} ms")

    # Track B: Hugging Face Vision Transformer
    print("\n--- Evaluating Track B: Hugging Face Vision Transformer ---")
    v_b = VisionTransformerVerifier("artifacts/models/transformer_signature_model.pt")
    sims_b = []
    latencies_b = []
    for _, row in test_df.iterrows():
        p1 = row["image_1_path"]
        p2 = row["image_2_path"]
        t_start = time.time()
        res = v_b.verify(p1, p2)
        latencies_b.append((time.time() - t_start) * 1000.0)
        sims_b.append(res.similarity_score)

    sims_b = np.array(sims_b, dtype=float)
    metrics_b = calculate_biometric_metrics(y_test, sims_b, optimal_threshold=float(v_b.threshold))
    metrics_b["average_latency_ms"] = float(np.mean(latencies_b))
    metrics_b["model_name"] = v_b.model_name
    metrics_b["model_version"] = v_b.model_version
    metrics_b["threshold_used"] = float(v_b.threshold)

    print(f"Track B Test AUC-ROC : {metrics_b['auc_roc']:.4f}")
    print(f"Track B Test EER     : {metrics_b['eer']:.4f}")
    print(f"Track B Test Accuracy: {metrics_b['accuracy']:.4f}")
    print(f"Track B Test FAR     : {metrics_b['far']:.4f}")
    print(f"Track B Test FRR     : {metrics_b['frr']:.4f}")
    print(f"Track B Test F1      : {metrics_b['f1_score']:.4f}")
    print(f"Track B Avg Latency  : {metrics_b['average_latency_ms']:.2f} ms")

    # Save evaluation report
    results = {
        "evaluation_dataset": "CEDAR Test Cohort (Writers 46-55)",
        "test_pairs_count": len(test_df),
        "protocol": "Strictly Writer-Disjoint Open-Set Evaluation",
        "Track_A_Classical_Sklearn": metrics_a,
        "Track_B_Vision_Transformer": metrics_b
    }

    out_path = Path("artifacts/evaluation/vmake_test_evaluation.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[SUCCESS] Saved comprehensive test evaluation to {out_path}")

    return results


if __name__ == "__main__":
    evaluate_vmake_models()
