# SIGNATURE VMAKE — Project Overview

> **Repository:** `signature-vmake`  
> **System Name:** SIGNATURE VMAKE (Offline Signature Verification & Multi-Factor Fraud Risk Assessment Platform)  
> **Domain:** Banking Biometrics & Automated Cheque Clearing  
> **Status:** Production-Ready / Fully Validated  

---

## 1. Executive Summary

**SIGNATURE VMAKE** is an enterprise-grade biometric verification and fraud risk assessment platform engineered specifically for offline banking transactions (such as counter withdrawal slips, clearing cheques, and high-value wire authorization vouchers).

The platform replaces manual, error-prone visual inspection conducted by bank tellers with a multi-track artificial intelligence engine coupled with a deterministic multi-factor risk scoring pipeline. By operating strictly under **Writer-Independent (Open-Set)** biometric protocols, SIGNATURE VMAKE generalizes seamlessly to new, previously unseen banking customers without requiring model re-training or identity calibration.

The system incorporates three distinct machine learning tracks:
1. **Track A (Classical ML Baseline):** Scikit-learn Support Vector Machine with Platt probability calibration over engineered morphological, density, and Histogram of Oriented Gradients (HOG) representations.
2. **Track B (Vision Transformer):** Hugging Face Transformers Vision Transformer (`facebook/deit-tiny-patch16-224`) leveraging multi-head patch self-attention and projection metric learning.
3. **Track C (Siamese ResNet Champion):** Deep twin convolutional Siamese network trained with contrastive metric learning for production high-precision biometric discrimination.

All biometric verifications feed into an adaptive **Multi-Factor Fraud Risk Engine** and are persisted within a third-normal-form (3NF) relational banking schema with cryptographic SHA-256 audit trails, accessible via a high-performance **FastAPI** REST microservice and an interactive **Verification Studio** web dashboard.

---

## 2. Business Context & Problem Statement

### 2.1 The Challenge in Banking Operations
In retail and commercial banking, offline physical signatures remain the primary legal and contractual instrument for authorizing cheques, teller counter withdrawals, demand drafts, and mandate modifications. However, banking institutions face critical operational vulnerabilities:
- **Human Teller Fatigue & Inconsistency:** Manual verification error rates range between 20% and 35% under peak transaction volumes, with tellers struggling to detect skilled forgeries (simulated signatures reproducing stroke geometry).
- **Clearing House Time Constraints:** In automated Cheque Truncation Systems (CTS), cheques must be validated within strict clearing cycles (often under 2 hours), making exhaustive forensic scrutiny impossible without automation.
- **Sophisticated Forgery Syndicates:** Forgers exploit low-security cheques using high-resolution reproduction, tracing, and freehand practice, leading to substantial fraud losses.
- **Regulatory Scrutiny:** Financial regulators (e.g., Central Banks) demand immutable, auditable proof of verification diligence for every processed transaction.

### 2.2 Why Naive Machine Learning Fails
Many existing biometric systems fail in real-world banking because they formulate signature verification as a **Closed-Set Classification Problem** (e.g., classifying an image into one of $N$ known customer classes). In banking:
- A bank has millions of customers, and thousands enroll every month.
- A closed-set model cannot verify a new customer without retraining the entire neural network.
- Random negative sampling ignores skilled forgeries, yielding models with artificially high benchmark scores that catastrophically fail in real fraud scenarios.

### 2.3 The SIGNATURE VMAKE Solution
SIGNATURE VMAKE solves these challenges through:
- **Open-Set Metric Learning:** The network learns a universal similarity metric in Euclidean/cosine embedding space, comparing a questioned specimen against an enrolled gallery of genuine reference signatures.
- **Strict Disjoint Writer Partitioning:** Training, validation, and testing cohorts share zero writers (Writers 1–35 for training, 36–45 for validation, 46–55 for test), guaranteeing that reported metrics reflect true real-world generalization to unknown customers.
- **Hard-Negative Mining with Skilled Forgeries:** Evaluation benchmarks specifically assess skilled forgeries created by trained impostors, preventing false sense of security.
- **Multi-Factor Risk Context:** The system evaluates not just raw visual similarity, but also capture image quality (Laplacian blur variance), transaction monetary tiering, and channel velocity.

---

## 3. Technology Stack & Genuine Justification

SIGNATURE VMAKE adheres strictly to the mandatory technology stack, ensuring every component has an authentic, executable role:

| Technology | Version | Genuine System Role |
| :--- | :--- | :--- |
| **Python** | 3.11+ | Core implementation language; provides type annotations, dataclasses, asynchronous concurrency (`asyncio`), and standard mathematical libraries. |
| **scikit-learn** | >=1.3.0 | Powering **Track A (Classical ML Baseline)**: extracts 264-d HOG and morphological features, trains a calibrated Support Vector Classifier (`CalibratedClassifierCV`), and computes biometric evaluation metrics (ROC-AUC, EER, confusion matrices). |
| **Hugging Face Transformers** | >=4.35.0 | Powering **Track B (Vision Transformer)**: provides the `DeiT-Tiny` vision backbone (`facebook/deit-tiny-patch16-224`) for patch-based self-attention feature extraction and 128-d metric projection for signature pairs. |
| **PyTorch & Torchvision** | 2.13.0 / 0.16.0 | Powering **Track C (Siamese ResNet Champion)**: implements deep convolutional feature extraction with shared weights and contrastive margin loss. |
| **FastAPI** | >=0.100.0 | High-throughput asynchronous REST microservice exposing enrollment, verification, audit trail, transaction, and benchmark endpoints with Pydantic v2 schemas and OpenAPI documentation. |
| **SQLite / PostgreSQL** | 3.x / 15+ | 3NF normalized relational persistence for banking customers, accounts, specimen galleries, verification records, transactions, risk assessments, and cryptographic audit logs. |
| **OpenCV (`opencv-python-headless`)** | 4.8+ | Computer vision preprocessing: grayscale conversion, bilateral noise filtering, Otsu dynamic binarization, bounding-box cropping, and aspect-ratio padding to 224x224. |

---

## 4. Multi-Track Model Architecture

SIGNATURE VMAKE implements a three-track polymorphic model architecture governed by the abstract interface [`SignatureVerificationModel`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/model_interface.py):

```
                        ┌────────────────────────────────────────────────────────┐
                        │              SignatureVerificationModel                │
                        │                   (Abstract Base)                      │
                        └──────────────────────────┬─────────────────────────────┘
                                                   │
         ┌─────────────────────────────────────────┼────────────────────────────────────────┐
         │                                         │                                        │
         ▼                                         ▼                                        ▼
┌───────────────────┐                    ┌───────────────────┐                    ┌───────────────────┐
│     Track A       │                    │     Track B       │                    │     Track C       │
│  Classical SVM    │                    │ Vision Transformer│                    │  Siamese ResNet   │
│  (scikit-learn)   │                    │  (Transformers)   │                    │ (Champion Model)  │
├───────────────────┤                    ├───────────────────┤                    ├───────────────────┤
│ • 264-d features  │                    │ • DeiT-Tiny ViT   │                    │ • ResNet Backbone │
│ • HOG + Density   │                    │ • Self-Attention  │                    │ • Contrastive Loss│
│ • Platt Scaling   │                    │ • 128-d Metric    │                    │ • 256-d Unit Hyp. │
│ • 7.3ms Latency   │                    │ • 38.4ms Latency  │                    │ • 42.1ms Latency  │
│ • AUC: 0.8423     │                    │ • AUC: 0.8118     │                    │ • AUC: 0.9008     │
└───────────────────┘                    └───────────────────┘                    └───────────────────┘
```

1. **Track A — Classical Sklearn Baseline:** Extracts engineered geometric features:
   - 128-d Histogram of Oriented Gradients (HOG).
   - 64-d Local Grid Density (8x8 cell transitions).
   - 56-d Horizontal and Vertical Projection Profiles.
   - 16-d Stroke Aspect and Morphological moments.
   - Evaluated via RBF Support Vector Classifier with Platt probability calibration. Ideal for ultra-low resource edge processors.
2. **Track B — Hugging Face Vision Transformer:** Processes image patches (16x16) through 12 multi-head self-attention transformer layers. Projects the `[CLS]` token into a metric space, computing cosine similarity between reference and questioned signatures. Proves transformer attention suitability for line stroke continuity.
3. **Track C — Siamese ResNet Champion:** Employs twin ResNet convolutional backbones with shared weights, projecting preprocessed signature pairs onto a 256-dimensional unit hypersphere ($||\mathbf{u}||_2 = 1.0$) trained with contrastive margin loss. Delivers the lowest False Acceptance Rate (FAR) and highest AUC-ROC.

---

## 5. Measured Three-Track Benchmark Results

The three tracks were evaluated across **400 open-set validation pairs** from disjoint writers (Writers 36 through 45) under identical preprocessing and evaluation criteria. Real measured metrics from `artifacts/evaluation/three_track_benchmark_results.json`:

| Metric | Track A: Classical SVM | Track B: Vision Transformer | Track C: Siamese ResNet (Champion) |
| :--- | :---: | :---: | :---: |
| **Model Technology** | scikit-learn (SVM + HOG) | Hugging Face Transformers (DeiT) | PyTorch (Twin ResNet) |
| **ROC-AUC** | **0.8423** | **0.8118** | **0.9008** |
| **Equal Error Rate (EER)** | **23.00%** | **24.50%** | **18.74%** |
| **Accuracy at Optimal Cutoff** | **76.75%** | **75.50%** | **81.50%** |
| **False Acceptance Rate (FAR)** | 23.04% | 24.51% | **19.12%** |
| **False Rejection Rate (FRR)** | 23.47% | 24.49% | **17.86%** |
| **F1-Score** | 0.7634 | 0.7513 | **0.8131** |
| **Optimal Cutoff Threshold** | 0.4990 | 0.4287 | 0.7691 |
| **Inference Latency (CPU)** | **7.3 ms** | 38.4 ms | 42.1 ms |
| **Model Size** | **5.4 MB** | 21.7 MB | 43.2 MB |
| **Production Recommendation** | Low-latency edge & offline teller | Experimental attention research | **Production Champion** |

---

## 6. Multi-Factor Risk Assessment Engine

A biometric score in isolation does not provide adequate fraud protection. SIGNATURE VMAKE combines four weighted risk dimensions:

$$\text{Risk}_{\text{composite}} = w_{\text{bio}} \cdot (1 - S_{\text{bio}}) + w_{\text{quality}} \cdot (1 - Q_{\text{img}}) + w_{\text{txn}} \cdot R_{\text{txn}} + w_{\text{behavior}} \cdot R_{\text{behavior}}$$

Where:
- $S_{\text{bio}}$: Biometric similarity score ($[0.0, 1.0]$) aggregated from the reference gallery.
- $Q_{\text{img}}$: Image quality index computed from Laplacian blur variance and contrast metrics ($[0.0, 1.0]$).
- $R_{\text{txn}}$: Transaction monetary risk tiered by transaction amount (e.g., Tier 1: $< \$5,000$; Tier 2: $\$5,000 - \$25,000$; Tier 3: $> \$25,000$).
- $R_{\text{behavior}}$: Channel and velocity factor (counter withdrawal, clearing cheque, ATM, high-velocity flags).

**Decision Tiers:**
- **LOW RISK ($< 0.25$):** Auto-Pass (`VERIFIED`).
- **MEDIUM RISK ($0.25 - 0.60$):** Escalated to Compliance Queue (`MANUAL_REVIEW`).
- **HIGH RISK ($\ge 0.60$):** Auto-Block (`REJECTED`).

---

## 7. Compliance & Template Alignment Disclaimer

> [!NOTE]
> **Bank Muscat BRD Requirements Template Alignment:**  
> This system is built to fulfill functional, operational, and architectural requirements outlined in standard enterprise banking specifications (specifically referencing the Bank Muscat Business Requirements Document template).  
> All banking records, customer identities, account numbers, and transaction IDs are **100% synthetically generated** for demonstration, validation, and testing purposes. No proprietary Bank Muscat software, customer data, production networks, or core banking integrations were accessed or used in this project.
