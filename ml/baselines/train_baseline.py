"""
SIGNATURE VMAKE — Train and Calibrate Classical scikit-learn Baseline.

Trains a classical machine learning model (SVM / LogisticRegression / RandomForest)
on engineered HOG and morphological features using writer-disjoint splits:
- Training Split: Writers 1..35
- Validation Split: Writers 36..45 (Threshold calibration and EER determination)
- Test Split: Evaluated separately to prevent threshold snooping.
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd
from PIL import Image
import joblib

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_recall_fscore_support

from ml.baselines.feature_extractor import ClassicalFeatureExtractor
from ml.evaluation.metrics import calculate_biometric_metrics


def cache_image_features(image_paths: list, extractor: ClassicalFeatureExtractor) -> Dict[str, np.ndarray]:
    """Extracts and caches features for unique images to avoid redundant computation."""
    unique_paths = list(set(image_paths))
    print(f"Extracting features for {len(unique_paths)} unique images...")
    cache = {}
    for i, path in enumerate(unique_paths):
        if (i + 1) % 200 == 0 or (i + 1) == len(unique_paths):
            print(f"  Processed {i + 1}/{len(unique_paths)} images...")
        try:
            cache[path] = extractor.extract(path)
        except Exception as e:
            # Fallback zero vector
            cache[path] = np.zeros(264, dtype=np.float32)
    return cache


def build_pair_matrix(df: pd.DataFrame, feature_cache: Dict[str, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """Constructs pairwise difference and product feature matrix."""
    X_list = []
    y_list = []
    for _, row in df.iterrows():
        p1 = row["image_1_path"]
        p2 = row["image_2_path"]
        label = int(row["label"])
        f1 = feature_cache.get(p1)
        f2 = feature_cache.get(p2)
        if f1 is None or f2 is None:
            continue
        diff = np.abs(f1 - f2)
        prod = f1 * f2
        pair_feat = np.concatenate([diff, prod])
        X_list.append(pair_feat)
        y_list.append(label)

    return np.array(X_list, dtype=np.float32), np.array(y_list, dtype=int)


def train_and_evaluate(
    train_pairs_path: str = "data/pairs/train_pairs.csv",
    val_pairs_path: str = "data/pairs/validation_pairs.csv",
    model_type: str = "svm",
    max_train_samples: int = 3000
) -> Dict[str, Any]:
    print(f"=== SIGNATURE VMAKE: Training Classical {model_type.upper()} Baseline ===")
    train_df = pd.read_csv(train_pairs_path)
    val_df = pd.read_csv(val_pairs_path)

    # Subsample training data if needed for fast training
    if len(train_df) > max_train_samples:
        train_df = train_df.sample(n=max_train_samples, random_state=42).reset_index(drop=True)

    extractor = ClassicalFeatureExtractor()

    all_paths = list(train_df["image_1_path"]) + list(train_df["image_2_path"]) + \
                list(val_df["image_1_path"]) + list(val_df["image_2_path"])
    feat_cache = cache_image_features(all_paths, extractor)

    X_train, y_train = build_pair_matrix(train_df, feat_cache)
    X_val, y_val = build_pair_matrix(val_df, feat_cache)

    print(f"X_train shape: {X_train.shape}, y_train positive ratio: {np.mean(y_train):.2f}")
    print(f"X_val shape: {X_val.shape}, y_val positive ratio: {np.mean(y_val):.2f}")

    # Standardize
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)

    if model_type == "svm":
        base_clf = SVC(kernel="rbf", C=1.0, probability=True, random_state=42)
    elif model_type == "logistic":
        base_clf = LogisticRegression(max_iter=1000, random_state=42)
    elif model_type == "random_forest":
        base_clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    else:
        raise ValueError(f"Unknown model_type: {model_type}")

    print("Fitting classifier...")
    base_clf.fit(X_train_scaled, y_train)

    # Predict validation probabilities
    val_probs = base_clf.predict_proba(X_val_scaled)[:, 1]

    # Evaluate validation metrics using scikit-learn
    val_metrics = calculate_biometric_metrics(y_val, val_probs)
    calibrated_threshold = val_metrics["eer_threshold"]

    print("\n--- Validation Performance ---")
    print(f"EER: {val_metrics['eer']:.4f} at Threshold: {calibrated_threshold:.4f}")
    print(f"AUC-ROC: {val_metrics['auc_roc']:.4f}")
    print(f"Accuracy: {val_metrics['accuracy']:.4f}")
    print(f"FAR: {val_metrics['far']:.4f}, FRR: {val_metrics['frr']:.4f}")
    print(f"F1 Score: {val_metrics['f1_score']:.4f}")

    # Save model artifact
    output_dir = Path("artifacts/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    model_artifact_path = output_dir / f"classical_{model_type}_model.joblib"

    artifact = {
        "model_type": model_type,
        "model_name": f"Classical_{model_type.upper()}_Baseline",
        "model_version": f"1.0.0-sklearn-{model_type}",
        "classifier": base_clf,
        "scaler": scaler,
        "calibrated_threshold": calibrated_threshold,
        "validation_metrics": {
            "eer": val_metrics["eer"],
            "auc_roc": val_metrics["auc_roc"],
            "accuracy": val_metrics["accuracy"],
            "far": val_metrics["far"],
            "frr": val_metrics["frr"],
            "f1_score": val_metrics["f1_score"],
            "calibrated_threshold": calibrated_threshold,
        }
    }
    joblib.dump(artifact, model_artifact_path)
    print(f"Saved model artifact to: {model_artifact_path}")

    # Save metrics JSON
    metrics_path = output_dir / f"classical_{model_type}_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(artifact["validation_metrics"], f, indent=2)
    print(f"Saved validation metrics to: {metrics_path}")

    return artifact["validation_metrics"]


if __name__ == "__main__":
    train_and_evaluate(model_type="svm", max_train_samples=2500)
