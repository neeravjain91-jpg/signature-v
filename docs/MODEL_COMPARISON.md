# Model Benchmark & Comparative Analysis Report
## SIGNATURE VMAKE: Track A (scikit-learn) vs. Track B (Hugging Face Vision Transformer)

---

### 1. Executive Summary

In strict compliance with the **SIGNATURE VMAKE** technology mandate, the platform evaluates two distinct paradigm architectures for offline banking signature verification:
1. **Track A — Classical Machine Learning Baseline (`scikit-learn`)**:
   - 264-dimensional handcrafted computer-vision features (Sobel HOG gradient histograms, 8x8 spatial grid stroke densities, horizontal/vertical projection profiles, morphological aspect ratio/occupancy invariants).
   - Pairwise metric classifier: Support Vector Machine (Linear SVM with probability calibration).
2. **Track B — Modern Vision Transformer (`Hugging Face Transformers`)**:
   - Deep Computer-Vision Vision Transformer (`facebook/deit-tiny-patch16-224` backbone).
   - Multi-head self-attention over $16 \times 16$ spatial stroke patches with a trained metric projection head mapping to a 256-dimensional unit hypersphere ($\|u\|_2 = 1.0$).

> [!IMPORTANT]
> **Strict Writer-Disjoint Open-Set Protocol:**
> All models are trained on **Writers 1–35** (7,000 pairs), calibrated for operating threshold and EER on **Writers 36–45** (1,200 pairs), and evaluated on the strictly held-out test cohort of **Writers 46–55** (1,200 pairs). Zero writer overlap exists across any split ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).

---

### 2. Empirical Performance Comparison on Held-Out Test Cohort (Writers 46–55)

The table below presents the verified, reproducible test metrics evaluated on 1,200 test pairs:

| Performance Metric | Track A: Classical `scikit-learn` SVM | Track B: `Hugging Face` Vision Transformer | Delta / Advantage |
| :--- | :---: | :---: | :---: |
| **Model Type** | Classical ML (HOG + Morphology) | Deep Vision Transformer (ViT) | Different Paradigms |
| **Model Version** | `1.0.0-sklearn-svm` | `1.0.0-transformers-vit` | Independent Lineages |
| **Checkpoint File** | `artifacts/models/classical_svm_model.joblib` | `artifacts/models/transformer_signature_model.pt` | Verified on Disk |
| **Model Size** | **5.4 MB** | 21.7 MB | **Track A is 75% smaller** |
| **Average Latency** | **6.03 ms** | 36.66 ms | **Track A is 6.1x faster** |
| **Operating Threshold ($\tau^*$)** | **0.3636** | **0.7313** | Validation EER Calibrated |
| **Area Under ROC (AUC-ROC)** | **0.8574** | 0.7947 | **Track A (+6.27%)** |
| **Equal Error Rate (EER)** | **19.00%** | 27.67% | **Track A (+8.67% lower error)** |
| **Classification Accuracy** | **79.17%** | 64.50% | **Track A (+14.67%)** |
| **False Acceptance Rate (FAR)** | **28.50%** | 67.17% | **Track A (+38.67% lower)** |
| **False Rejection Rate (FRR)** | 13.17% | **3.83%** | **Track B (+9.34% lower FRR)** |
| **F1 Score** | **0.8065** | 0.7304 | **Track A (+0.076)** |

---

### 3. Detailed Architectural Tradeoff Analysis

```mermaid
flowchart TD
    subgraph TrackA["Track A: scikit-learn Classical Baseline"]
        A1["Input Signatures<br/>(Ref & Query)"] --> A2["OpenCV Preprocessor<br/>(Denoise, Otsu, BBox Crop)"]
        A2 --> A3["Feature Extractor<br/>(264-d HOG + Spatial Density)"]
        A3 --> A4["Pairwise Matrix<br/>(|u-v|, u*v, dist, cos)"]
        A4 --> A5["StandardScaler + Linear SVM<br/>artifacts/models/classical_svm_model.joblib"]
        A5 --> A6["P(genuine) Output<br/>(Latency: 6.03ms, AUC: 0.8574)"]
    end

    subgraph TrackB["Track B: Hugging Face Vision Transformer"]
        B1["Input Signatures<br/>(Ref & Query)"] --> B2["OpenCV Preprocessor<br/>(Centered 224x224 3-Ch)"]
        B2 --> B3["ViT Backbone<br/>(facebook/deit-tiny-patch16-224)"]
        B3 --> B4["Self-Attention Tokens<br/>([CLS] + 196 Patch Embeddings)"]
        B4 --> B5["Metric Projection Head<br/>(256-d Unit Hypersphere)"]
        B5 --> B6["Hypersphere Distance<br/>(Latency: 36.66ms, FRR: 3.83%)"]
    end
```

#### 3.1 Track A (scikit-learn SVM)
- **Strengths:**
  - Exceptional CPU throughput (6.03 ms per verification), making it ideal for high-volume batch cheque clearing.
  - Superior overall discrimination on skilled forgeries (AUC-ROC 0.8574, EER 19.00%) due to rigid spatial projection profiles and stroke density histograms.
  - Very small memory footprint (5.4 MB).
- **Tradeoffs:**
  - Requires explicit handcrafted feature engineering.
  - Higher False Rejection Rate (13.17%) when genuine customer signatures exhibit high intra-writer variation.

#### 3.2 Track B (Hugging Face Vision Transformer)
- **Strengths:**
  - Exceptional genuine acceptance: False Rejection Rate is only **3.83%**, meaning legitimate bank customers almost never suffer false rejection.
  - Dense spatial self-attention captures micro-stroke continuities and pen-lift stroke dynamics across image patches without manual feature engineering.
  - Outputs a standardized 256-dimensional biometric embedding vector suitable for customer gallery vector search.
- **Tradeoffs:**
  - Higher latency (36.66 ms on CPU) due to 12 layers of multi-head self-attention.
  - More permissive on skilled forgeries (FAR 67.17% at validation threshold), requiring tighter operating thresholds or manual review triggers.

---

### 4. Tri-State Banking Decision Boundaries

To bridge biometric similarity scores with banking risk management, both models feed into the **Tri-State Decision Engine**:

| Decision | Track A Condition | Track B Condition | Banking Action |
| :--- | :--- | :--- | :--- |
| **VERIFIED** | Score $\ge 0.3636$ | Score $\ge 0.7313$ | Automated straight-through transaction processing. Clear genuine signature. |
| **MANUAL REVIEW** | $0.3036 \le \text{Score} < 0.3636$ | $0.6813 \le \text{Score} < 0.7313$ | Routed to Compliance Officer Queue. Signature is borderline or high intra-writer variance. |
| **REJECTED** | Score $< 0.3036$ | Score $< 0.6813$ | Autonomous transaction block. Impostor or signature mismatch detected. |

---

### 5. Provenance & Artifact Verification

- **Evaluation Script:** [`ml/evaluation/evaluate_vmake_test.py`](../ml/evaluation/evaluate_vmake_test.py)
- **Evaluation Output Manifest:** [`artifacts/evaluation/vmake_test_evaluation.json`](../artifacts/evaluation/vmake_test_evaluation.json)
- **Model Checkpoints:**
  - Track A: [`artifacts/models/classical_svm_model.joblib`](../artifacts/models/classical_svm_model.joblib)
  - Track B: [`artifacts/models/transformer_signature_model.pt`](../artifacts/models/transformer_signature_model.pt)
- **Legacy Material Action:** Siamese ResNet networks and SYNAPSE-derived artifacts have been decommissioned from the production path.
