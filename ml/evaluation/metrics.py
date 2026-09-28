"""
Biometric Performance Metrics for Signature Verification Systems.

Calculates:
- False Acceptance Rate (FAR)
- False Rejection Rate (FRR)
- Equal Error Rate (EER) and optimal operating threshold
- Area Under ROC Curve (AUC-ROC)
- Precision, Recall, F1, and Accuracy
"""

from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import roc_curve, auc, precision_recall_fscore_support, accuracy_score


def calculate_biometric_metrics(
    y_true: np.ndarray,
    similarities: np.ndarray,
    optimal_threshold: float = None
) -> Dict[str, Any]:
    """
    Computes comprehensive biometric verification metrics.
    Args:
        y_true: 1D array of ground truth labels (1.0 for genuine, 0.0 for forged).
        similarities: 1D array of similarity scores in [0.0, 1.0].
        optimal_threshold: If provided, metrics are calculated at this threshold.
                           If None, the threshold is computed at the Equal Error Rate (EER).
    """
    y_true = np.asarray(y_true, dtype=int)
    similarities = np.asarray(similarities, dtype=float)

    # Compute ROC Curve
    # Since similarities are positive metrics (higher = genuine), we use similarities as score
    fpr, tpr, thresholds = roc_curve(y_true, similarities, pos_label=1)
    fnr = 1.0 - tpr
    roc_auc = auc(fpr, tpr)

    # Calculate Equal Error Rate (EER)
    # EER occurs where FPR == FNR (i.e. |FPR - FNR| is minimized)
    eer_idx = np.nanargmin(np.absolute(fpr - fnr))
    eer = (fpr[eer_idx] + fnr[eer_idx]) / 2.0
    eer_threshold = float(thresholds[eer_idx])

    # Choose evaluation threshold
    eval_threshold = optimal_threshold if optimal_threshold is not None else eer_threshold

    # Binary predictions at evaluation threshold
    y_pred = (similarities >= eval_threshold).astype(int)

    # Confusion matrix components
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))

    far = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    frr = fn / (tp + fn) if (tp + fn) > 0 else 0.0
    acc = accuracy_score(y_true, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="binary", zero_division=0)

    return {
        "eer": float(eer),
        "eer_threshold": float(eer_threshold),
        "evaluated_threshold": float(eval_threshold),
        "auc_roc": float(roc_auc),
        "accuracy": float(acc),
        "far": float(far),
        "frr": float(frr),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "confusion_matrix": {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "total_samples": len(y_true)
        },
        "roc_curve": {
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist()
        }
    }
