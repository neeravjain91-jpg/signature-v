# SIGNATURE VMAKE — Classical scikit-learn Baseline Report

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Component:** Model Track A — Classical Machine Learning Baseline  
**Artifact:** `artifacts/models/classical_svm_model.joblib`  
**Metrics:** `artifacts/models/classical_svm_metrics.json`  

---

## 1. Executive Summary & Objective

In compliance with the project charter, **scikit-learn** is utilized not merely for metrics calculation, but as an independent, fully functioning machine-learning model track (**Model Track A**). 

The classical baseline serves as an essential scientific control against which more complex deep learning and Transformer models are benchmarked. It demonstrates how far handcrafted biometric feature engineering can solve open-set signature verification before incurring the compute overhead of deep neural networks.

---

## 2. Feature Engineering Pipeline

The feature extraction pipeline is implemented in [`ml/baselines/feature_extractor.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/baselines/feature_extractor.py). For every input image, the preprocessor outputs a standardized $224 \times 224$ float32 stroke map, from which **264 statistical, directional, and morphological features** are extracted:

```
Raw Signature Image
       │
       ▼
[SignaturePreprocessor] (Otsu binarization, bounding box crop, 224x224 aspect-preserving pad)
       │
       ├─► 1. Spatial Grid Densities (8x8 grid cells)               ──►  64 features
       ├─► 2. Directional Gradient Orientation Histograms (Sobel HOG) ──► 128 features
       ├─► 3. Horizontal Projection Profile (32 binned row sums)     ──►  32 features
       ├─► 4. Vertical Projection Profile (32 binned column sums)    ──►  32 features
       └─► 5. Morphological & Geometric Invariants                  ──►   8 features
                                                                    ────────────
                                               Total Feature Vector: 264 dimensions
```

### 2.1 Feature Definitions
1. **Spatial Grid Densities (64-d):** Image divided into an $8 \times 8$ uniform grid. The mean ink concentration in each cell captures spatial stroke layout.
2. **Directional HOG (128-d):** Horizontal ($G_x$) and vertical ($G_y$) Sobel filters calculate gradient angles and magnitudes. Features are organized into a $4 \times 4$ spatial quadrant grid with 8 orientation bins ($0^\circ$ to $360^\circ$) per block, capturing stroke trajectory and pen movement angles.
3. **Projection Profiles (64-d):** Row-wise and column-wise integrals of pixel intensities binned into 32 equal buckets, encoding vertical stroke distribution and horizontal letter spacing.
4. **Morphological Invariants (8-d):** Ink density ratio, vertical/horizontal normalized centroids ($C_y, C_x$), spatial standard deviations ($\sigma_y, \sigma_x$), aspect ratio ($\frac{W}{H}$), and bounding box occupancy.

---

## 3. Pairwise Formulation & Classifier Architecture

Given two signature feature vectors $\mathbf{f}_1, \mathbf{f}_2 \in \mathbb{R}^{264}$, a pairwise representation vector $\mathbf{x}_{\text{pair}} \in \mathbb{R}^{528}$ is constructed:

$$\mathbf{x}_{\text{pair}} = \left[ |\mathbf{f}_1 - \mathbf{f}_2| \;,\; \mathbf{f}_1 \odot \mathbf{f}_2 \right]$$

where:
* $|\mathbf{f}_1 - \mathbf{f}_2|$ is the absolute difference vector (capturing feature deviations).
* $\mathbf{f}_1 \odot \mathbf{f}_2$ is the elementwise Hadamard product (capturing mutual alignment).

### 3.1 scikit-learn Pipeline
The classifier pipeline consists of:
1. `sklearn.preprocessing.StandardScaler`: Standardizes the 528 pairwise features to zero mean and unit variance.
2. `sklearn.svm.SVC(kernel='rbf', C=1.0, probability=True)`: A Support Vector Machine with Radial Basis Function kernel and Platt scaling to produce well-calibrated posterior probabilities $P(y = 1 \mid \mathbf{x}_{\text{pair}})$.

---

## 4. Empirical Training & Validation Protocol

The model was trained strictly adhering to the **Writer-Disjoint (Open-Set)** protocol:
* **Training Partition:** Writers `1` to `35` (2,500 balanced training pairs, 50% positive / 50% negative).
* **Validation Partition:** Writers `36` to `45` (1,200 balanced validation pairs). **Zero writer overlap.**
* **Threshold Calibration:** Optimal decision threshold was selected at the Equal Error Rate (EER) of the validation curve.

### 4.1 Measured Validation Results

| Biometric Performance Metric | Measured Value | Interpretation |
| :--- | :---: | :--- |
| **Equal Error Rate (EER)** | **22.92%** ($0.2292$) | Point where False Acceptance Rate equals False Rejection Rate. |
| **Optimal Operating Threshold** | **0.4265** | Calibrated posterior probability threshold for production decisions. |
| **Area Under ROC Curve (AUC-ROC)**| **0.8471** | Good discriminatory power for a non-deep classical baseline. |
| **Validation Accuracy** | **77.08%** | High baseline accuracy on unseen writers without representation learning. |
| **False Acceptance Rate (FAR)** | **23.00%** ($0.2300$) | Rate of impostors mistakenly accepted at optimal threshold. |
| **False Rejection Rate (FRR)** | **22.83%** ($0.2283$) | Rate of genuine signers mistakenly rejected at optimal threshold. |
| **F1 Score** | **0.7710** | Harmonized precision and recall. |
| **Inference Latency** | **~8.4 ms** | CPU inference time per signature pair. |
| **Model Disk Size** | **3.8 MB** | Highly compact, zero-GPU requirement. |

---

## 5. Architectural Analysis & Role in SIGNATURE VMAKE

1. **Why It Works:** Handcrafted features like directional Sobel histograms and projection profiles effectively detect coarse and random forgeries where stroke density or general layout differs.
2. **Where It Reaches Its Limit:** On skilled forgeries where a practiced human replicator matches the macro-geometry of the signature, linear/RBF feature combinations cannot capture sub-pixel micro-hesitations or stroke velocity curvature.
3. **System Role:** The classical baseline is fully integrated via `ml/baselines/classical_classifier.py` into the `SignatureVerificationModel` interface and is surfaced in the comparative research dashboard.
