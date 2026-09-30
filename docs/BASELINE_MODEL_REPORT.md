# BASELINE MODEL EVALUATION REPORT
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Benchmark Baseline Architecture & Empirical Evaluation*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Baseline Model Specifications

The baseline model is a dual-branch shared-weight Convolutional Neural Network trained with metric learning (Contrastive Loss) on pairwise Euclidean distances on the unit hypersphere $\mathbb{S}^{255}$.

| Parameter / Component | Specification |
|---|---|
| **Model Class** | `SiameseSignatureNet` ([`ml/models/siamese_network.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/siamese_network.py)) |
| **Backbone Architecture** | Modified ResNet-18 (1-channel grayscale input, 4 residual stages) |
| **Embedding Dimension** | $d = 256$ (L2 unit-normalized, $\|\mathbf{z}\|_2 = 1.0$) |
| **Distance Metric** | Euclidean distance $D(\mathbf{z}_1, \mathbf{z}_2) = \|\mathbf{z}_1 - \mathbf{z}_2\|_2 \in [0.0, 2.0]$ |
| **Similarity Function** | $S = \text{clamp}(1.0 - D/2.0, 0.0, 1.0)$ |
| **Loss Function** | Contrastive Loss ($L = 0.5 \cdot y \cdot D^2 + 0.5 \cdot (1-y) \cdot \max(0, m - D)^2$, margin $m = 1.0$) |
| **Optimizer** | AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay $= 10^{-4}$) |
| **Base Learning Rate** | $\eta = 3 \times 10^{-4}$ with `ReduceLROnPlateau` |
| **Batch Size** | 32 pairs per mini-batch |
| **Total Parameters** | 5,276,640 (100% trainable) |
| **Model Artifact Size** | 60.48 MB (`artifacts/models/best_siamese_model.pt`) |
| **Inference Latency** | 10.31 ms / pair (Intel CPU single-core) |
| **Data Splits** | Train: Writers 1–35 (7,000 pairs), Val: Writers 36–45 (1,200 pairs), Test: Writers 46–55 (1,200 pairs) |

---

## 2. Validation Calibration Metrics (Writers 36–45)

Calibrated strictly using validation predictions via `ml/evaluation/calibrate_threshold.py`:
- **Optimal Operating Threshold ($\tau^*$):** $0.776638$
- **Validation EER:** $27.50\%$
- **Validation ROC-AUC:** $0.7766$
- **Validation TAR ($\text{Sim} \ge \tau^*$):** $72.33\%$ (FRR: $27.67\%$)
- **Validation Overall FAR:** $27.50\%$
- **Validation Skilled Forgery FAR:** $37.78\%$ (136/360 accepted)
- **Validation Random Impostor FAR:** $12.08\%$ (29/240 accepted)

---

## 3. Final Unbiased Baseline Test Metrics (Writers 46–55)

Evaluated strictly at frozen threshold $\tau^* = 0.7766$ using `ml/evaluation/evaluate.py`:

| Test Metric | Value | Description |
|---|---|---|
| **Area Under ROC (AUC)** | **0.7410** | Open-set discrimination across unseen writers |
| **Equal Error Rate (EER)** | **32.42%** | Crossover error rate on test cohort |
| **Overall Accuracy** | **64.83%** | Unbiased classification accuracy (778/1,200) |
| **True Acceptance Rate (TAR)** | **75.33%** | Legitimate customer clearance (452/600 genuine pairs) |
| **False Rejection Rate (FRR)** | **24.67%** | Erroneously blocked genuine customers (148/600) |
| **Overall False Acceptance (FAR)**| **45.67%** | Total unauthorized pairs accepted (274/600) |
| **Skilled Forgery FAR** | **62.22%** | **CRITICAL WEAKNESS**: 224/360 skilled forgeries accepted |
| **Random Impostor FAR** | **20.83%** | Unskilled cross-writer impostors accepted (50/240) |
| **Precision / Recall / F1** | **0.6226 / 0.7533 / 0.6817** | Positive class detection statistics |

---

## 4. Identified Failure Modes of Baseline

1. **Skilled Forgery Blindspot ($62.22\%$ Test FAR)**: Uniform random pair generation during training failed to penalize skilled imitations adequately.
2. **Margin Inadequacy in Metric Space**: Margin $m=1.0$ allowed genuine intra-writer variations and skilled forgeries to overlap in the $[0.70, 0.85]$ similarity band.
3. **Threshold Fragility**: Shifting the baseline threshold upward to eliminate skilled forgeries caused catastrophic False Rejections (FRR exploded to $54.67\%$ at $\tau=0.85$).
