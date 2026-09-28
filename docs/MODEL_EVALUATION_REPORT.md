# Siamese Neural Network: Model Evaluation Report

> [!NOTE]
> Evaluation performed strictly on the **Unseen Test Cohort** (CEDAR Writers 46 through 55).
> **Writer-Independent (Open-Set)** protocol ensures zero identity leakage between training and testing.

## 1. High-Level Performance Metrics

| Metric | Measured Value | Standard Target | Interpretation |
| :--- | :--- | :--- | :--- |
| **Equal Error Rate (EER)** | **30.67%** | $< 10.0\%$ | Industry benchmark for biometric accuracy |
| **AUC-ROC** | **0.7465** | $> 0.9000$ | Overall discrimination capability across all thresholds |
| **Operating Threshold** | **0.7691** | $[0.50 - 0.85]$ | Balanced decision cutoff |
| **Overall Accuracy** | **69.00%** | $> 85.0\%$ | Total correct verification decisions |
| **False Acceptance Rate (FAR)**| **46.67%** | $< 8.0\%$ | Unauthorized signatures mistakenly approved |
| **False Rejection Rate (FRR)**| **15.33%** | $< 8.0\%$ | Genuine customer signatures mistakenly blocked |
| **Precision** | **0.6447** | $> 0.85$ | Reliability of an approval decision |
| **Recall / True Positive Rate**| **0.8467** | $> 0.85$ | Genuine customer pass rate |
| **F1-Score** | **0.7320** | $> 0.85$ | Harmonic mean of precision and recall |

## 2. Granular Fraud Analysis: Skilled vs. Random Forgery

In banking transactions, forgeries fall into two distinct forensic classes:

| Forgery Type | Sample Count | False Acceptance Rate (FAR) | Defense Effectiveness |
| :--- | :--- | :--- | :--- |
| **Skilled Forgeries** (Practiced mimicry of victim) | 360 | **66.94%** | 33.06% Block Rate |
| **Random Impostors** (Cross-writer foreign signatures) | 240 | **16.25%** | 83.75% Block Rate |
| **Genuine Customers** (Legitimate account holder) | 600 | **15.33% FRR** | 84.67% Pass Rate |

## 3. Confusion Matrix

| Actual \ Predicted | Predicted: Genuine (Score $\ge 0.7691$) | Predicted: Forged (Score $< 0.7691$) | Total |
| :--- | :--- | :--- | :--- |
| **Actual Genuine** | **508 (TP)** | 92 (FN - False Rejection) | 600 |
| **Actual Forged** | 280 (FP - False Acceptance) | **320 (TN)** | 600 |
| **Total** | 788 | 412 | **1200** |

## 4. Visual Artifacts

* **ROC Curve Plot:** `docs/ROC_CURVE.png`
* **Model Checkpoint:** `artifacts/models/best_siamese_model.pt`
* **Test Dataset Source:** `data/pairs/test_pairs.csv`
