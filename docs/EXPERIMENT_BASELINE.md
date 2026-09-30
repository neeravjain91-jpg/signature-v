# EXPERIMENT BASELINE REPORT
**SIGNATURE VMAKE — Siamese Signature Verification & Fraud Detection Platform**
*Phase 1: Baseline Reproduction & Experimental Groundwork*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu, Windows x64*

---

## 1. Baseline Architectural & Hyperparameter Specification

The baseline model is a dual-branch shared-weight Convolutional Neural Network trained with metric learning (Contrastive Loss) on pairwise Euclidean distances on the unit hypersphere $\mathbb{S}^{255}$.

| Parameter / Component | Specification |
|---|---|
| **Model Class** | `SiameseSignatureNet` ([`ml/models/siamese_network.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/siamese_network.py)) |
| **Backbone Architecture** | Modified ResNet-18 (1-channel grayscale input, 4 residual stages) |
| **Embedding Dimension** | $d = 256$ (L2 unit-normalized, $\|\mathbf{z}\|_2 = 1.0$) |
| **Distance Metric** | Euclidean distance $D(\mathbf{z}_1, \mathbf{z}_2) = \|\mathbf{z}_1 - \mathbf{z}_2\|_2 \in [0.0, 2.0]$ |
| **Similarity Function** | $S = \text{clamp}(1.0 - D/2.0, 0.0, 1.0)$ |
| **Loss Function** | Contrastive Loss ($L = y \cdot D^2 + (1-y) \cdot \max(0, m - D)^2$, margin $m = 1.0$) |
| **Optimizer** | AdamW ($\beta_1 = 0.9, \beta_2 = 0.999$, weight decay $= 10^{-4}$) |
| **Base Learning Rate** | $\eta = 3 \times 10^{-4}$ with `ReduceLROnPlateau` (factor $= 0.5$, patience $= 1$) |
| **Batch Size** | 32 pairs per mini-batch |
| **Training Epochs** | 4 epochs (best checkpoint saved at epoch 3 based on validation loss) |
| **Image Preprocessing** | Otsu binarization + bounding box crop + aspect-ratio pad + resize to $224 \times 224$ |
| **Baseline Augmentation** | Slight affine rotation ($\pm 5^\circ$) |
| **Dataset Splits** | Train: Writers 1–35 (7,000 pairs), Val: Writers 36–45 (1,200 pairs), Test: Writers 46–55 (1,200 pairs) |
| **Total Parameters** | 5,276,640 (100% trainable) |
| **Model Artifact Size** | 60.48 MB (`artifacts/models/best_siamese_model.pt`) |
| **Inference Latency** | 10.31 ms $\pm$ 0.91 ms per pair (Intel CPU single-thread benchmark) |

---

## 2. Reproduced Baseline Validation Metrics (Writers 36–45, 1,200 Pairs)

The operating threshold was calibrated strictly on the validation cohort using Equal Error Rate minimization ($\text{FPR} = \text{FNR}$):

- **Calibrated Operating Cutoff ($\tau^*$):** **`0.776638`** ($\approx \mathbf{0.7766}$)
- **Validation Equal Error Rate (EER):** **27.58%**
- **Validation Area Under ROC (AUC-ROC):** **0.7853**
- **Validation Overall Accuracy:** **72.42%**
- **Validation False Acceptance Rate (FAR):** **27.50%**
- **Validation False Rejection Rate (FRR):** **27.67%**
- **Validation True Acceptance Rate (TAR):** **72.33%**
- **Validation Skilled Forgery FAR:** **37.78%**
- **Validation Random Impostor FAR:** **12.08%**
- **Validation Precision / Recall / F1:** **0.7245 / 0.7233 / 0.7239**
- **Validation Confusion Matrix:** $\text{TP} = 434, \ \text{FP} = 165, \ \text{TN} = 435, \ \text{FN} = 166$ (Total $= 1,200$)

---

## 3. Reproduced Baseline Test Metrics (Writers 46–55, 1,200 Pairs at Frozen $\tau^* = 0.7766$)

With model weights and threshold permanently frozen, evaluation on the unseen test cohort yielded:

- **Operating Threshold (Frozen):** **0.7766**
- **True Acceptance Rate (TAR):** **83.17%**
- **False Rejection Rate (FRR):** **16.83%**
- **Overall False Acceptance Rate (FAR):** **42.50%**
- **Cross-Writer (Random Impostor) FAR:** **12.92%** (Cross-Writer Impostor Block Rate: **87.08%**)
- **Skilled Forgery FAR:** **62.22%** (Skilled Forgery Block Rate: **37.78%**)
- **Test EER Reference Point:** **30.67%**
- **Test Area Under ROC (AUC-ROC):** **0.7465**
- **Overall Accuracy:** **70.33%**
- **Precision:** **0.6618**
- **Recall:** **0.8317**
- **F1-Score:** **0.7371**
- **Test Confusion Matrix:** $\text{TP} = 499, \ \text{FP} = 255, \ \text{TN} = 345, \ \text{FN} = 101$ (Total $= 1,200$)

---

## 4. Key Experimental Observations & Primary Weakness

1. **Reproduction Fidelity:** The reproduced validation and test metrics match the documented baseline in [`docs/FINAL_ML_VALIDATION_REPORT.md`](file:///c:/Users/ASUS/Downloads/hcl/docs/FINAL_ML_VALIDATION_REPORT.md) exactly ($100\%$ numerical concordance).
2. **Primary Failure Mode:** **Skilled Forgery False Acceptance Rate is 62.22% on the test set** and 37.78% on the validation set. Random cross-writer impostors are effectively blocked ($87.08\%$ block rate), but practiced human imitations deceive the baseline CNN.
3. **Research Mandate:** All subsequent phases will target skilled-forgery discrimination using validation data only, without compromising genuine pass rate ($\text{TAR} \ge 80\%$) or inference latency ($< 30\text{ ms}$).
