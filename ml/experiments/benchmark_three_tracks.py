"""
SIGNATURE VMAKE — Comprehensive Three-Track Benchmark & Evaluation.

Rigorously evaluates all three model tracks on identical writer-disjoint splits:
- Model A: Classical scikit-learn Baseline (SVM on HOG/Morphological features)
- Model B: Hugging Face Vision Transformer (ViT deit-tiny patch16-224)
- Model C: Deep Siamese Neural Network (ResNet Metric Learning Champion)

Computes:
- AUC-ROC, EER, Accuracy, Precision, Recall, F1, FAR, FRR, TAR
- Inference latency (ms) and disk footprint (MB)
- Confusion matrices
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
from PIL import Image
import torch

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from ml.inference.verify_signature import get_model_verifier
from ml.evaluation.metrics import calculate_biometric_metrics


def evaluate_model_on_pairs(verifier, pairs_df: pd.DataFrame, max_samples: int = 500) -> Dict[str, Any]:
    """Runs pairwise verification across dataset and calculates scikit-learn metrics."""
    df = pairs_df
    if len(df) > max_samples:
        df = df.sample(n=max_samples, random_state=42).reset_index(drop=True)

    y_true = []
    similarities = []
    latencies = []

    print(f"Evaluating {verifier.model_name} on {len(df)} pairs...")
    for idx, row in df.iterrows():
        p1 = row["image_1_path"]
        p2 = row["image_2_path"]
        label = int(row["label"])

        t0 = time.time()
        # Polymorphic verify_pair
        output = verifier.verify_pair(p1, p2)
        elapsed = (time.time() - t0) * 1000.0

        similarities.append(output.similarity_score)
        y_true.append(label)
        if idx >= 5:  # skip warmups
            latencies.append(elapsed)

    y_true_arr = np.array(y_true, dtype=int)
    sims_arr = np.array(similarities, dtype=float)

    # Use calibrated threshold for model if set, otherwise EER
    metrics = calculate_biometric_metrics(y_true_arr, sims_arr, optimal_threshold=verifier.threshold)

    # Add extra metrics
    tar = 1.0 - metrics["frr"]
    avg_latency = float(np.mean(latencies)) if latencies else 0.0

    return {
        "model_name": verifier.model_name,
        "model_type": verifier.model_type,
        "model_version": verifier.model_version,
        "calibrated_threshold": float(verifier.threshold),
        "auc_roc": float(metrics["auc_roc"]),
        "eer": float(metrics["eer"]),
        "accuracy": float(metrics["accuracy"]),
        "precision": float(metrics["precision"]),
        "recall": float(metrics["recall"]),
        "f1_score": float(metrics["f1_score"]),
        "far": float(metrics["far"]),
        "frr": float(metrics["frr"]),
        "tar": float(tar),
        "average_latency_ms": round(avg_latency, 2),
        "confusion_matrix": metrics["confusion_matrix"],
    }


def get_model_size_mb(path_str: str) -> float:
    p = Path(path_str)
    if p.exists():
        return round(p.stat().st_size / (1024 * 1024), 2)
    return 0.0


def run_benchmark():
    print("================================================================")
    print(" SIGNATURE VMAKE — THREE-MODEL TRACK RIGOROUS BENCHMARK")
    print("================================================================")

    val_pairs = pd.read_csv("data/pairs/validation_pairs.csv")
    test_pairs = pd.read_csv("data/pairs/test_pairs.csv")

    results = {}

    # Track A: Classical Sklearn SVM
    try:
        verifier_a = get_model_verifier("sklearn")
        res_a_val = evaluate_model_on_pairs(verifier_a, val_pairs, max_samples=400)
        res_a_val["model_size_mb"] = get_model_size_mb("artifacts/models/classical_svm_model.joblib")
        results["Track_A_Classical_Sklearn"] = res_a_val
    except Exception as e:
        print(f"Error evaluating Track A: {e}")

    # Track B: Hugging Face Vision Transformer
    try:
        verifier_b = get_model_verifier("transformer")
        res_b_val = evaluate_model_on_pairs(verifier_b, val_pairs, max_samples=400)
        res_b_val["model_size_mb"] = get_model_size_mb("artifacts/models/transformer_signature_model.pt")
        results["Track_B_Vision_Transformer"] = res_b_val
    except Exception as e:
        print(f"Error evaluating Track B: {e}")

    # Track C: Deep Siamese ResNet
    try:
        verifier_c = get_model_verifier("siamese")
        res_c_val = evaluate_model_on_pairs(verifier_c, val_pairs, max_samples=400)
        res_c_val["model_size_mb"] = get_model_size_mb(str(verifier_c.checkpoint_path))
        results["Track_C_Siamese_ResNet"] = res_c_val
    except Exception as e:
        print(f"Error evaluating Track C: {e}")

    # Save benchmark JSON
    out_dir = Path("artifacts/evaluation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "three_track_benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nBenchmark results saved to: {out_file}")

    # Print summary table
    print("\n================== MEASURED VALIDATION BENCHMARK ==================")
    print(f"{'Model Track':<28} | {'AUC':<7} | {'EER':<7} | {'Acc':<7} | {'FAR':<7} | {'FRR':<7} | {'F1':<7} | {'Latency':<8} | {'Size'}")
    print("-" * 100)
    for track, m in results.items():
        print(f"{track:<28} | {m['auc_roc']:.4f}  | {m['eer']:.4f}  | {m['accuracy']:.4f}  | {m['far']:.4f}  | {m['frr']:.4f}  | {m['f1_score']:.4f}  | {m['average_latency_ms']:<6.1f}ms | {m['model_size_mb']:.1f}MB")
    print("===================================================================\n")

    return results


if __name__ == "__main__":
    run_benchmark()
