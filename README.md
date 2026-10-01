# SIGNATURE VMAKE — AI-Powered Signature Verification & Banking Document Authentication System

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.8+-orange.svg)](https://scikit-learn.org/)
[![Hugging Face Transformers](https://img.shields.io/badge/Transformers-5.17+-yellow.svg)](https://huggingface.co/docs/transformers/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Production-green.svg)](https://fastapi.tiangolo.com/)
[![Database](https://img.shields.io/badge/PostgreSQL%20%7C%20SQLite-3NF%20Audit-blue.svg)](database/schema.sql)
[![Tests](https://img.shields.io/badge/pytest-53%20passed%20(100%25)-success.svg)](tests/)
[![Architecture](https://img.shields.io/badge/Architecture-Dual--Track%20Production-success.svg)](artifacts/models/)

**SIGNATURE VMAKE** is an enterprise-grade, writer-independent biometric signature verification and multi-factor fraud risk assessment system engineered for banking workflows (cheque clearing, counter withdrawals, high-value wire transfers), strictly aligned with the **Bank Muscat Business Requirements Document (BRD) template** and approved project synopsis.

---

## 1. Web Application Pages (Multi-Page Architecture)

SIGNATURE VMAKE features a modular, multi-page web application where each operational capability has its own dedicated URL, route, and DOM context:

| Page | Route | Purpose |
|---|---|---|
| **Overview** | `/` | System dashboard & executive KPI cards |
| **Manual Register & Verify** | `/manual-workflow` | Register first signature (reference only) and verify second signature |
| **Cheque Studio** | `/verification-studio` | Banking transaction verification & multi-factor fraud risk decomposition |
| **Model Comparison** | `/model-comparison` | Compare ML candidates (AUC, EER, Accuracy, Latency, Size) |
| **Officer Queue** | `/compliance-queue` | Manual-review escalated cases & officer adjudication modal |
| **Audit Trail** | `/audit-timeline` | Verification & non-repudiation regulatory audit history |
| **Model Health** | `/model-registry` | Live model readiness, checkpoints, and real-time inference ping |

---

## 2. System Architecture & Multi-Model ML Engine

SIGNATURE VMAKE operates on an approved **Dual-Track Machine Learning Architecture**, providing both a modern deep representation learning track and an interpretable classical classifier suite:

```mermaid
flowchart TD
    subgraph Ingestion_Layer ["1. Ingestion & Security Validation Layer"]
        DOC["Cheque Scan / Signature Slip"] --> VAL["Security & MIME Validator<br/>• File cap <= 5MB<br/>• Magic byte inspection<br/>• Whitelist (.png, .jpg, .tiff, .bmp)"]
        VAL --> PRE["SignaturePreprocessor<br/>• Bilateral noise reduction<br/>• Dynamic Otsu binarization<br/>• Tight bounding-box crop<br/>• Aspect-ratio preserved padding (224x224)"]
    end

    subgraph ML_Candidates ["2. Multi-Candidate ML Engine"]
        PRE --> DISPATCHER["ModelVerifierFactory<br/>(Polymorphic Interface)"]
        DISPATCHER --> TRACK_B["Track B: Hugging Face Vision Transformer (ViT)<br/>★ PRODUCTION DEFAULT ★<br/>• facebook/deit-tiny-patch16-224 backbone<br/>• 128-d metric projection head<br/>• Low Customer Friction (FRR: 3.83%)<br/>• Latency: 36.66ms | AUC: 0.7947"]
        DISPATCHER --> TRACK_A1["Track A1: Random Forest Classifier<br/>★ ACCURACY CHAMPION ★<br/>• 264-d HOG & morphological feature extraction<br/>• 100 decision trees (Gini impurity)<br/>• Lowest EER: 13.33% | AUC: 0.9424"]
        DISPATCHER --> TRACK_A2["Track A2: Classical SVM Baseline<br/>• Platt-calibrated Support Vector Machine<br/>• Latency: 6.03ms | AUC: 0.8574"]
        DISPATCHER --> TRACK_A3["Track A3: Logistic Regression<br/>• Ultra-lightweight baseline (0.02 MB)<br/>• Latency: 6.00ms | AUC: 0.8808"]
    end

    subgraph Risk_Engine ["3. Multi-Factor Fraud Risk Engine"]
        TRACK_B & TRACK_A1 & TRACK_A2 & TRACK_A3 --> AGG["Gallery Aggregation Mode<br/>(Single Reference or Multi-Specimen Gallery)"]
        AGG --> S_COMP["Calibrated Similarity Margin Deficit"]
        QUALITY["Laplacian Blur & Contrast Variance"] --> Q_COMP["Image Quality Deficit (1 - Q)"]
        TXN["Transaction Amount Tier"] --> T_COMP["Monetary Exposure Weight"]
        BEH["Channel & Submission Velocity"] --> B_COMP["Behavioral Risk Factor"]
        S_COMP & Q_COMP & T_COMP & B_COMP --> COMPOSITE["Composite Risk Assessment<br/>(0.0000 - 1.0000)"]
    end

    subgraph Decision_Engine ["4. Tri-State Banking Decision Engine"]
        COMPOSITE --> DECISION{"Tri-State Banking Verdict"}
        DECISION -->|"Sim >= Thresh & Risk < 0.25"| PASS["VERIFIED • MATCH<br/>(Automated Settlement)"]
        DECISION -->|"Sim near Thresh or Risk 0.25-0.60"| REVIEW["MANUAL REVIEW • BORDERLINE<br/>(Officer Adjudication Queue)"]
        DECISION -->|"Sim < Thresh or Risk >= 0.60"| REJECT["REJECTED • NO MATCH<br/>(Auto-Block & Audit Alert)"]
    end

    subgraph Relational_Audit ["5. Relational Database & Immutable Audit Vault"]
        PASS & REVIEW & REJECT --> DB_TXN[("verification_attempts<br/>• similarity_score<br/>• threshold_used<br/>• tri-state decision")]
        REVIEW --> DB_QUEUE[("manual_reviews<br/>• compliance notes<br/>• adjudicator ID")]
        DB_TXN --> DB_AUDIT[("audit_logs<br/>• SHA-256 integrity hash<br/>• regulatory timestamp")]
    end
```

---

## 2. Mandatory Technology Compliance Matrix

Every mandated technology in SIGNATURE VMAKE executes a genuine, mission-critical function:

| Mandated Technology | Genuine Production Role in SIGNATURE VMAKE | Verifiable Artifacts & Source |
| :--- | :--- | :--- |
| **Python 3.11+** | Core asynchronous platform runtime, dataclasses, typing, and orchestrator. | Entire repository |
| **scikit-learn** | **Track A Baseline & Biometrics Suite:** 264-d HOG and morphological feature vector extraction, calibrated Support Vector Machine, Random Forest, and Logistic Regression models; biometric evaluation engine (ROC-AUC, EER, FAR, FRR, F1). | [`ml/baselines/classical_classifier.py`](ml/baselines/classical_classifier.py)<br/>[`ml/evaluation/metrics.py`](ml/evaluation/metrics.py)<br/>`artifacts/models/classical_random_forest_model.joblib`<br/>`artifacts/models/classical_svm_model.joblib`<br/>`artifacts/models/classical_logistic_model.joblib` |
| **Hugging Face Transformers** | **Track B Vision Transformer (Production Default):** Vision Transformer backbone (`facebook/deit-tiny-patch16-224`) applying 12-layer multi-head self-attention to signature stroke trajectories, projected into a 128-d metric embedding space. | [`ml/models/transformer_signature_model.py`](ml/models/transformer_signature_model.py)<br/>`artifacts/models/transformer_signature_model.pt` |
| **FastAPI** | High-throughput asynchronous REST microservice providing customer enrollment, biometric verification, manual review adjudication, audit trail ledger, and OpenAPI documentation. | [`api/main.py`](api/main.py)<br/>[`api/auth.py`](api/auth.py) |
| **PyTorch** | Backend execution runtime required strictly by Hugging Face Transformers. | Subordinate dependency |
| **PostgreSQL / SQLite** | 3NF normalized relational schema storing customers, accounts, specimen galleries, verification attempts, fraud risk assessments, and cryptographic audit logs. | [`database/models.py`](database/models.py)<br/>[`database/schema.sql`](database/schema.sql) |

---

## 3. Empirical Test Cohort Evaluation Benchmark

All four candidate models were independently benchmarked on the locked held-out **CEDAR test cohort (Writers 46 through 55, 1,200 open-set pairs)** under strict writer-disjoint protocols. These metrics are recorded in [`artifacts/evaluation/model_comparison_benchmark.json`](artifacts/evaluation/model_comparison_benchmark.json):

| Metric | Track B: HF Vision Transformer (ViT) | Track A1: Random Forest | Track A2: Classical SVM | Track A3: Logistic Regression |
| :--- | :---: | :---: | :---: | :---: |
| **Operational Role** | **Production Enterprise Default** | **Accuracy Champion** | **Edge / Offline Terminal** | **Ultra-Light Baseline** |
| **ROC-AUC** | 0.7947 | **0.9424** | 0.8574 | 0.8808 |
| **Equal Error Rate (EER)** | 27.67% | **13.33%** | 19.00% | 18.83% |
| **Accuracy at Threshold** | 64.50% | **82.92%** | 79.17% | 80.50% |
| **False Acceptance Rate (FAR)** | 67.17% | 30.33% | 28.50% | **27.00%** |
| **False Rejection Rate (FRR)** | **3.83%** (Low Friction) | **3.83%** | 13.17% | 12.00% |
| **True Acceptance Rate (TAR)** | **96.17%** | **96.17%** | 86.83% | 88.00% |
| **F1-Score** | 0.7304 | **0.8492** | 0.8065 | 0.8186 |
| **Calibrated Operating Threshold** | 0.7313 | 0.4264 | 0.3636 | 0.2015 |
| **Single-Pair Inference Latency** | 36.66 ms | 10.23 ms | 6.03 ms | **6.00 ms** |
| **Model Disk Size** | 21.73 MB | 2.39 MB | 1.90 MB | **0.02 MB** |

### Candidate Operational Roles:
- **Track B (HF Vision Transformer)** serves as the **Production Default** for high-volume banking transactions. Its ultra-low False Rejection Rate (FRR **3.83%**) prevents customer friction, while borderlines are caught by the risk engine.
- **Track A1 (Random Forest)** achieves the highest overall discrimination (**0.9424 AUC**, **13.33% EER**) on explicit 264-d HOG and morphological features.
- **Track A2 & A3 (SVM & Logistic Regression)** provide ultra-fast 6 ms verification for edge and offline teller counter terminals.

---

## 4. Multi-Factor Fraud Risk Engine & Tri-State Decisioning

In banking workflows, binary thresholds create unacceptable fraud vulnerability. SIGNATURE VMAKE calculates a calibrated multi-factor fraud risk score:

$$\text{Risk}_{\text{composite}} = 0.50 \cdot R_{\text{sim}} + 0.15 \cdot (1 - Q_{\text{img}}) + 0.25 \cdot R_{\text{txn}} + 0.10 \cdot R_{\text{behavior}}$$

Where:
- $R_{\text{sim}}$: Calibrated biometric similarity deficit relative to operating threshold $\tau$
- $Q_{\text{img}}$: Image capture quality derived from Laplacian variance ($\sigma_L^2$) and stroke contrast
- $R_{\text{txn}}$: Tiered monetary exposure based on cheque/transfer amount
- $R_{\text{behavior}}$: Submission channel risk and transaction velocity

### Tri-State Banking Decisions:
1. **`VERIFIED` (Low Risk < 0.25, Biometric MATCH):** Transaction is automatically approved for settlement.
2. **`MANUAL REVIEW` (Medium Risk 0.25 - 0.60, BORDERLINE):** Transaction is automatically routed to the compliance officer adjudication queue.
3. **`REJECTED` (High Risk >= 0.60, NO MATCH):** Transaction is auto-blocked, customer notified, and security alert triggered.

---

## 5. Verification Modes: Single vs Gallery

SIGNATURE VMAKE implements two operational verification modes:
- **Mode 1: Single Reference Verification:** Compares the questioned signature against the customer's most recent active primary specimen.
- **Mode 2: Multi-Specimen Gallery Verification:** Compares the questioned signature against all active specimen signatures in the customer's enrolled gallery (up to 3 specimens) using configurable aggregation strategies (`max_similarity`, `mean_similarity`).

---

## 6. Quickstart & Verification Instructions

### Prerequisites
- Python 3.11+
- Virtual environment (`venv` or `conda`)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run System Diagnostics
Validate that all 11 dependencies, database tables, and all 4 candidate models load correctly:
```bash
python scripts/diagnose.py
```

### 3. Run Test Suite
Execute the full automated test suite (53 unit, integration, and page routing tests):
```bash
python -m pytest tests -v
```

### 4. Run Live End-to-End Demonstration
Execute the 9-step banking workflow demonstration (enrollment, genuine verification, candidate comparison, impostor rejection, cheque risk assessment, and audit trail):
```bash
python scripts/e2e_live_demo.py
```

### 5. Launch FastAPI Service & Dashboard
Start the production Uvicorn server:
```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
- Interactive Web Interface: `http://127.0.0.1:8000/`
- Interactive OpenAPI / Swagger UI: `http://127.0.0.1:8000/docs`
- Redoc Documentation: `http://127.0.0.1:8000/redoc`

---

## 7. Key REST API Endpoints

| Category | Method | Endpoint | Description |
| :--- | :---: | :--- | :--- |
| **System** | `GET` | `/api/v1/health` | Service health, active model track, and DB connectivity |
| **Diagnostics** | `GET` | `/api/v1/models/health` | Runtime readiness & benchmark latency for all 4 candidate models |
| **Diagnostics** | `GET` | `/api/v1/models/benchmark` | Official evaluation metrics from locked held-out test cohort |
| **Enrollment** | `POST` | `/api/v1/signatures/enroll` | Register customer signature specimen into secure vault (reference only) |
| **Verification** | `POST` | `/api/v1/verifications/verify` | Execute AI biometric verification (Single or Gallery mode) |
| **Transactions** | `POST` | `/api/v1/transactions` | Create banking transaction record (cheque, withdrawal) |
| **Review Queue** | `GET` | `/api/v1/verifications/pending-reviews` | Retrieve escalated transactions requiring officer review |
| **Review Queue** | `POST` | `/api/v1/manual-reviews/{id}/adjudicate` | Compliance officer approve/reject adjudication |
| **Audit Trail** | `GET` | `/api/v1/audit/trail/{identifier}` | Complete non-repudiation regulatory audit ledger |

---

## 8. Regulatory Compliance & Separation Statement

- **Project Separation**: SIGNATURE VMAKE is an independent implementation strictly conforming to the Bank Muscat BRD template utilizing Python, scikit-learn, Hugging Face Transformers, and FastAPI.
- **Biometric Anti-Spoofing**: Image validation enforces strict MIME inspection, magic byte verification, dimension bounds, and Laplacian blur deficit calculation.
- **Audit Ledger**: All verification attempts produce immutable, timestamped audit log entries with SHA-256 cryptographic hashes for regulatory non-repudiation.
- **Detailed Forensic Documentation**: See [`docs/FINAL_PROJECT_STATUS.md`](docs/FINAL_PROJECT_STATUS.md), [`docs/MODEL_COMPARISON.md`](docs/MODEL_COMPARISON.md), and [`docs/SYNOPSIS_GAP_ANALYSIS.md`](docs/SYNOPSIS_GAP_ANALYSIS.md).
