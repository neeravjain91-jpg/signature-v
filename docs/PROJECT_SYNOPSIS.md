# PROJECT SYNOPSIS

## Project Title
**AI-Based Signature Verification and Fraud Detection System for Banking Transactions**

## Proposed System Name
**SYNAPSE — Intelligent Signature Verification Platform**

---

## 1. Introduction
The banking sector processes a large number of transactions and signed documents such as cheques, withdrawal forms, authorization forms, and account-related documents. Signature verification is an important part of validating such transactions. Traditional verification methods depend heavily on manual inspection, which can be time-consuming and may be affected by variations in human judgment.

This project proposes an AI-based signature verification system that automatically analyzes a submitted handwritten signature and compares it with the customer's registered signature samples. The system uses computer vision and deep learning to extract meaningful signature features and determine the similarity between signatures.

The proposed system includes a risk-assessment layer that considers the verification result along with transaction-related information. Cases with high confidence are automatically verified, while uncertain cases are forwarded to an authorized banking officer for manual review.

The project is an internship-level prototype demonstrating the application of Artificial Intelligence, Machine Learning, Computer Vision, Backend Development, Database Management, and Security in a banking environment.

---

## 2. Problem Statement
Manual signature verification in banking workflows can be slow and difficult to scale. A signature naturally varies between different signing instances because of writing speed, pressure, position, size, and other factors.

A robust automated system is required to compare signatures based on learned visual representations rather than relying only on pixel-level similarity.

SYNAPSE aims to develop an intelligent signature verification platform that can:
* process handwritten signature images;
* compare submitted signatures with registered signatures;
* identify probable genuine and forged signatures;
* generate a similarity score;
* assess transaction-level risk;
* route uncertain cases for manual verification; and
* maintain a secure, immutable audit trail.

---

## 3. Objectives
1. Develop an automated handwritten-signature verification system.
2. Apply computer vision techniques for signature preprocessing.
3. Implement a deep-learning-based signature comparison model.
4. Use a Siamese neural network for learning signature similarity.
5. Evaluate the model using FAR, FRR, EER, ROC-AUC, precision, recall, and F1-score.
6. Integrate the ML model with a banking-oriented backend application.
7. Implement transaction and risk-assessment workflows.
8. Provide a manual-review mechanism for uncertain cases.
9. Maintain database records and audit logs.
10. Implement authentication, authorization, and secure file handling.

---

## 4. Proposed Methodology
The project follows the end-to-end pipeline:
**Signature Dataset → Image Preprocessing → Pair Generation → Model Training → Model Evaluation → Signature Verification → Risk Assessment → Banking Decision**

* **Step 1: Dataset Preparation:** Benchmark CEDAR dataset (55 writers, 1,320 genuine, 1,320 forged) partitioned via a writer-independent open-set protocol (Train: Writers 1-35, Val: 36-45, Test: 46-55; 0% identity leakage).
* **Step 2: Image Preprocessing:** OpenCV pipeline with Gaussian denoising, Otsu adaptive binarization, stroke bounding-box tight cropping, aspect-ratio preserved scaling to $224 \times 224$, and float32 normalization.
* **Step 3: Deep Learning Model:** Twin Siamese ResNet with shared weights and 256-dimensional unit hypersphere embedding space trained via Hadsell Contrastive Loss.
* **Step 4: Verification:** Pair inference computing Euclidean distance $D \in [0, 2]$ and similarity $S = 1 - D/2 \in [0, 1]$.
* **Step 5: Risk Assessment:** Multi-factor risk engine combining similarity score ($1 - S$), image quality score (Laplacian blur variance), transaction amount tier, channel severity, and customer behavioral flags.
* **Step 6: Manual Review:** Compliance officer escalation queue for borderline cases ($S \approx \text{threshold}$ or elevated transaction risk).

---

## 5. System Architecture
* **Frontend:** Interactive Web Dashboard (HTML5, TailwindCSS, TypeScript/ES6)
* **Backend:** Python + FastAPI
* **Machine Learning:** PyTorch + Siamese Neural Network (ResNet Backbone)
* **Computer Vision:** OpenCV
* **Database:** PostgreSQL 14+ (SQLAlchemy 2.0 ORM + Alembic Migrations)
* **Security:** JWT Authentication + Role-Based Access Control (`CUSTOMER`, `OFFICER`, `ADMIN`)
* **Deployment:** Docker & Docker Compose
* **CI/CD:** GitHub Actions

---

## 6. Major Modules Summary
* **A. Authentication Module:** Token-based security and RBAC.
* **B. Customer Management Module:** Customer profiles and account association.
* **C. Signature Enrollment Module:** Multiple genuine reference specimens per customer.
* **D. Signature Verification Module:** Feature extraction, embedding generation, and similarity scoring.
* **E. Transaction Module:** Simulated banking voucher workflows (cheques, withdrawals, wires).
* **F. Risk Assessment Module:** Multi-factor composite risk scoring (`LOW`, `MEDIUM`, `HIGH`).
* **G. Manual Review Module:** Officer adjudication queue with mandatory audit commentary.
* **H. Audit Module:** Tamper-evident regulatory event logs.
* **I. Model Management Module:** Model registry, threshold calibration, and EER metrics.
* **J. Dashboard Module:** Live operational metrics, verification distribution, and latency tracking.

---

## 7. Status & Implementation Verification
* **Core ML System:** Fully trained and evaluated (`artifacts/models/best_siamese_model.pt`, EER 30.67% on open-set test cohort, AUC 0.7465, random impostor defense 83.75%).
* **Relational Database:** 11 entities implemented in `database/schema.sql` and `database/models.py`.
* **API & Orchestrator:** FastAPI service in `api/main.py` and `services/verification_service.py`.
* **Traceability & Tests:** End-to-end integration tests verified in `tests/test_traceability.py` and `tests/test_siamese_system.py`.
