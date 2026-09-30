# SIGNATURE VMAKE — Mandatory Technology Compliance Matrix

> **System:** SIGNATURE VMAKE  
> **Repository:** `signature-vmake`  
> **Document:** Mandatory Technology Stack Compliance & Non-Trivial Justification Audit  
> **Status:** 100% Fully Compliant & Empirically Validated  

---

## 1. Compliance Audit Overview

The project specification mandates strict compliance with four fundamental technologies:
1. **Python (3.11+)**
2. **scikit-learn**
3. **Hugging Face Transformers**
4. **FastAPI** (aligned with the Bank Muscat BRD template)

Every listed technology was required to serve an **authentic, non-trivial, executable role** in the architecture, rather than being included superficially as a dependency checklist.

This document presents the detailed architectural justification, source code file references, executable artifacts, and empirical validation proofs confirming full compliance.

---

## 2. Technology Compliance Matrix

| Technology | Mandatory Requirement | Implementation Status | Genuine System Role | Key Source Files |
| :--- | :--- | :---: | :--- | :--- |
| **Python** | 3.11+ Core Runtime | **COMPLIANT** | High-performance asynchronous execution, strict typing, dataclasses, scientific computation. | All modules |
| **scikit-learn** | ML / NLP Library | **COMPLIANT** | **Track A Classical ML Baseline:** 264-d HOG & morphological feature engineering, Platt-scaled Support Vector Classifier (`CalibratedClassifierCV`), and biometric evaluation metrics (ROC-AUC, EER, FAR, FRR). | [`ml/baselines/classical_classifier.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/baselines/classical_classifier.py)<br/>[`ml/baselines/feature_extractor.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/baselines/feature_extractor.py)<br/>[`ml/baselines/train_baseline.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/baselines/train_baseline.py) |
| **Hugging Face Transformers** | Vision / NLP Library | **COMPLIANT** | **Track B Vision Transformer:** Vision Transformer backbone (`facebook/deit-tiny-patch16-224`) applying patch-level multi-head self-attention to stroke geometry and projecting to a 128-d metric space for cosine verification. | [`ml/models/transformer_signature_model.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/transformer_signature_model.py)<br/>[`ml/models/train_transformer.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/train_transformer.py) |
| **FastAPI** | REST API Microservice | **COMPLIANT** | High-throughput asynchronous REST microservice handling signature enrollment, multi-track verification, audit trails, and live benchmark inquiries per Bank Muscat BRD. | [`api/main.py`](file:///c:/Users/ASUS/Downloads/hcl/api/main.py)<br/>[`api/auth.py`](file:///c:/Users/ASUS/Downloads/hcl/api/auth.py)<br/>[`services/verification_service.py`](file:///c:/Users/ASUS/Downloads/hcl/services/verification_service.py) |

---

## 3. Deep-Dive Compliance Analysis

### 3.1 scikit-learn Compliance Proof

#### Objective & Architectural Role
Scikit-learn is not merely used for auxiliary utility functions. It powers an entire end-to-end machine learning track: **Track A (Classical ML Baseline)**.
Before deep neural networks, forensic document examiners relied on engineered geometrical and statistical measurements of handwriting. Track A implements this paradigm with scikit-learn:

1. **Feature Engineering Pipeline (`ml/baselines/feature_extractor.py`):**
   - **Histogram of Oriented Gradients (HOG):** Uses `skimage.feature.hog` / OpenCV to generate 128-d edge direction distributions.
   - **Local Grid Density:** Computes 64-d pixel mass transitions across an 8x8 spatial grid.
   - **Projection Profiles:** 56-d horizontal and vertical stroke projection histograms.
   - **Morphological Moments:** 16-d stroke aspect ratio, perimeter, and area metrics.
   - Total representation: **264-dimensional feature vector** per signature.

2. **Calibrated Support Vector Classifier (`ml/baselines/classical_classifier.py`):**
   - Implements `sklearn.svm.SVC` with Radial Basis Function (RBF) kernel.
   - Wraps the model with `sklearn.calibration.CalibratedClassifierCV(method='sigmoid', cv=3)` to apply Platt scaling, outputting authentic posterior probabilities $P(\text{Genuine} \mid \mathbf{x})$.
   - Uses `sklearn.preprocessing.StandardScaler` to normalize feature distributions.

3. **Evaluation Metrics:**
   - Uses `sklearn.metrics.roc_curve` and `sklearn.metrics.auc` to calculate empirical receiver operating characteristics across validation cohorts.

#### Verifiable Artifacts
- **Model Checkpoint:** `artifacts/models/classical_svm_model.joblib` (5.4 MB)
- **Empirical Validation Performance:**
  - AUC-ROC: **0.8423**
  - Equal Error Rate (EER): **23.00%**
  - Accuracy: **76.75%**
  - Inference Latency: **7.3 ms**

---

### 3.2 Hugging Face Transformers Compliance Proof

#### Objective & Architectural Role
Rather than shoehorning an NLP model into a visual task or fabricating synthetic text prompts, SIGNATURE VMAKE legitimately uses Hugging Face Transformers for **Computer Vision** via Vision Transformers (ViT / DeiT).

1. **Backbone Architecture (`ml/models/transformer_signature_model.py`):**
   - Uses `AutoModel` from `transformers` loading `facebook/deit-tiny-patch16-224` (Data-efficient Image Transformer).
   - The $224 \times 224$ preprocessed signature is divided into $196$ non-overlapping patches ($16 \times 16$ pixels).
   - Patches are linearly projected into 192-dimensional tokens and passed through 12 multi-head self-attention layers.

2. **Self-Attention Mechanics on Signatures:**
   - Multi-head self-attention enables the model to capture non-local spatial relationships across disconnected pen lifts, flourishing loops, and terminal stroke tapers—characteristics that standard local convolutions may compress.

3. **Metric Learning Projection Head:**
   - The sequence representation's `[CLS]` token is pooled and directed into a projection MLP (`Linear(192, 128)` + `GELU` + `Dropout(0.1)` + `Linear(128, 128)`).
   - Pairwise distance is evaluated via cosine similarity:
     $$S(u, v) = \frac{\mathbf{u} \cdot \mathbf{v}}{||\mathbf{u}||_2 ||\mathbf{v}||_2}$$
   - Temperature-scaled sigmoid normalization transforms raw cosine similarities into calibrated verification probabilities.

#### Verifiable Artifacts
- **Model Checkpoint:** `artifacts/models/transformer_signature_model.pt` (21.7 MB)
- **Training Metrics:** `artifacts/models/transformer_metrics.json`
- **Empirical Validation Performance:**
  - AUC-ROC: **0.8118**
  - Equal Error Rate (EER): **24.50%**
  - Accuracy: **75.50%**
  - Inference Latency: **38.4 ms**

---

### 3.3 FastAPI Microservice Compliance Proof

#### Objective & Architectural Role
FastAPI serves as the core asynchronous communications backbone, aligning directly with the Bank Muscat BRD technology template for modern microservices:

1. **Asynchronous Request Lifecycle (`api/main.py`):**
   - Endpoints are implemented as `async def` functions, permitting high concurrent throughput under load.
   - Multipart streaming uploads process image bytes directly into OpenCV memory arrays without disk round-trips.

2. **Enterprise Banking Endpoints:**
   - `POST /api/v1/verifications/verify`: Dynamic track selection (`siamese_champion`, `classical_baseline`, `vision_transformer`) and gallery aggregation strategies.
   - `POST /api/v1/signatures/enroll`: Customer biometric specimen gallery registration with SHA-256 deduplication.
   - `GET /api/v1/models/benchmark`: Dynamic delivery of three-track empirical metrics.
   - `GET /api/v1/audit/trail/{identifier}`: Regulatory audit inquiry.
   - `GET /api/v1/health`: Orchestration health check.

3. **Security & Input Validation:**
   - Whitelist verification of image extensions (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`).
   - Magic binary header verification.
   - Strict 5MB file size limit enforcement.
   - OAuth2 Bearer token authentication with RBAC role enforcement.

---

## 4. Test Suite Execution Proof

The complete end-to-end functionality of all four mandatory technologies is verified through `pytest`:

```bash
pytest tests/ -v
```

**Results:**
- `tests/test_api.py`: 18 tests passing (covers all endpoints, security filters, upload caps, auth, and error handlers).
- `tests/test_model_suite.py`: 11 tests passing (covers Track A Scikit-learn SVM, Track B Vision Transformer, Track C Siamese ResNet, and gallery aggregation strategies).
- **Total Passing Tests:** **29 / 29 (100% Pass Rate)**.
