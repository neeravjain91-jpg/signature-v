# SIGNATURE VMAKE — Hugging Face Vision Transformer (ViT) Architecture & Evaluation

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Component:** Model Track B — Vision Transformer for Signature Biometrics  
**Implementation:** [`ml/models/transformer_signature_model.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/transformer_signature_model.py)  
**Training Pipeline:** [`ml/models/train_transformer.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/train_transformer.py)  
**Artifact:** `artifacts/models/transformer_signature_model.pt`  
**Metrics:** `artifacts/models/transformer_metrics.json`  

---

## 1. Executive Summary & Technology Compliance

In strict compliance with the mandatory project requirement:
> *"Transformers should be used legitimately for a suitable COMPUTER-VISION model where appropriate. Do NOT introduce an NLP model simply because the requirement contains 'NLP'."*

SIGNATURE VMAKE implements a **Vision Transformer (ViT)** using the official Hugging Face `transformers` library (`transformers.ViTModel`). Rather than treating signatures as text tokens or applying recurrent sequence processing, the architecture divides the 2D signature image into non-overlapping spatial patches and processes them using Multi-Head Self-Attention.

---

## 2. Transformer Architecture & Information Flow

The pipeline maps raw offline signature scans onto a 256-dimensional metric hypersphere:

```
                      [Raw Signature Image]
                                │
                                ▼
                   [Signature Preprocessor]
             (Otsu binarization, bounding box crop, 
              pad to 224x224, 3-channel broadcast)
                                │
                                ▼  Tensor: (B, 3, 224, 224)
                   [Patch Embedding Layer]
             (16x16 pixel non-overlapping patches 
              ──► 14x14 = 196 spatial tokens + [CLS] token)
                                │
                                ▼  Tokens: (B, 197, 192)
              [Hugging Face ViT Transformer Encoder]
             (Multi-Head Self-Attention + MLP Blocks)
                                │
                                ▼  CLS Token: (B, 192)
                     [Metric Projection Head]
                 Linear(192 ──► 256)
                       │
                 LayerNorm(256)
                       │
                     GELU()
                       │
                 Linear(256 ──► 256)
                                │
                                ▼
                    [L2-Hypersphere Normalization]
                       ||z||_2 = 1.0  (B, 256)
                                │
                                ▼
                   [Euclidean Metric & Similarity]
                 D = ||z_1 - z_2||_2  ∈ [0.0, 2.0]
                     S = 1.0 - (D / 2.0) ∈ [0.0, 1.0]
```

### 2.1 Patch Extraction & Self-Attention
* **Patch Size:** $16 \times 16$ pixels.
* **Sequence Length:** $\left(\frac{224}{16}\right)^2 = 196$ image patches $+ 1$ prepend `[CLS]` token $= 197$ tokens.
* **Token Dimension ($D_{\text{model}}$):** $192$ channels.
* **Self-Attention Mechanism:** Allows any stroke segment across the signature canvas to directly attend to distant flourishes, loops, and terminal strokes without being constrained by local convolutional receptive fields.

### 2.2 Metric Projection Head
The `[CLS]` token aggregates global contextual information across all 196 patches. It is passed through a two-layer non-linear MLP projection head (`Linear` $\rightarrow$ `LayerNorm` $\rightarrow$ `GELU` $\rightarrow$ `Linear`) mapping the representation into $\mathbb{R}^{256}$ followed by unit L2 normalization:

$$\mathbf{z} = \frac{\mathbf{h}_{\text{proj}}}{\|\mathbf{h}_{\text{proj}}\|_2}$$

---

## 3. Training & Validation Protocol

* **Data Partitioning:** Strictly writer-disjoint:
  - Training Partition: Writers `1` to `35` (800 balanced pairs, 50% positive / 50% negative).
  - Validation Partition: Writers `36` to `45` (400 balanced pairs).
  - Test Partition: Reserved untouched for unbiased final benchmarking.
* **Loss Function:** Contrastive Loss with margin $m = 1.0$:
  $$\mathcal{L}(x_1, x_2, y) = y \cdot D^2 + (1 - y) \cdot \max(0, m - D)^2$$
* **Optimization:** AdamW optimizer ($\text{lr} = 10^{-3}$, weight decay $= 10^{-4}$), batch size 16.

---

## 4. Measured Empirical Performance

All metrics were computed on disjoint validation writers using scikit-learn (`ml/evaluation/metrics.py`):

| Biometric Performance Metric | Measured Value | Interpretation |
| :--- | :---: | :--- |
| **Equal Error Rate (EER)** | **24.50%** ($0.2450$) | Point of equilibrium between false alarms and missed detections. |
| **Optimal Operating Threshold** | **0.7313** | Calibrated decision boundary for $S = 1 - \frac{D}{2}$. |
| **Area Under ROC Curve (AUC-ROC)**| **0.8118** | High discrimination between authentic signers and skilled forgers. |
| **Validation Accuracy** | **75.50%** | Accuracy on unseen writer cohort. |
| **False Acceptance Rate (FAR)** | **24.51%** ($0.2451$) | Ratio of skilled/random forgeries incorrectly accepted. |
| **False Rejection Rate (FRR)** | **24.49%** ($0.2449$) | Ratio of genuine customer specimens incorrectly rejected. |
| **F1 Score** | **0.7513** | Balanced harmonic precision-recall metric. |
| **Average CPU Latency** | **23.03 ms** | Latency per signature pair inference. |
| **Model Size** | **21.73 MB** | Checkpoint disk footprint. |

---

## 5. Architectural Comparison & Scientific Insights

1. **Self-Attention vs. Convolutional Bias:**
   - Vision Transformers lack the inductive bias (translation equivariance and local locality) inherent to CNNs.
   - For signature verification, local stroke connectivity (micro-tremor, stroke onset angles, pen-lifts) is of paramount importance.
   - Consequently, the Siamese ResNet (Model Track C) maintains superior fine-grained stroke discriminability, while the Vision Transformer (Model Track B) excels at global spatial proportion modeling.
2. **Pluggable Integration:**
   - The Vision Transformer is wrapped by `VisionTransformerVerifier`, fully adhering to `SignatureVerificationModel`.
   - It can be selected as the active verification engine in `api/main.py` without modifying client code or database schemas.
