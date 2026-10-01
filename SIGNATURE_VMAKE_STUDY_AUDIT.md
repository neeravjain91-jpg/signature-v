# SIGNATURE VMAKE — Comprehensive Academic & Engineering Study Audit

**Project:** SIGNATURE VMAKE — AI-Powered Offline Signature Verification & Banking Document Authentication System  
**Academic Level:** Bachelor of Technology (B.Tech) — 3rd Year Software Engineering / Machine Learning Project  
**Specification Standard:** IEEE Std 830-1998 (Recommended Practice for Software Requirements Specifications)  
**Repository:** [neeravjain91-jpg/signature-verification](https://github.com/neeravjain91-jpg/signature-verification)  
**Git Commit Version:** `4f9ff79` on branch `main`  
**Audit Timestamp:** October 2026  

---

## 1. Executive Summary & Verification Audit

This document certifies that the comprehensive project study guide:
- **`SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.pdf`** (54 pages, 2.38 MB, 19 embedded diagrams/charts/screenshots)
- **`SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.docx`** (2.05 MB editable source document)

has been compiled and mathematically verified against the actual repository source code, model checkpoint artifacts, automated test suites, and empirical evaluation benchmarks.

```
======================================================================
PDF PUBLICATION AUDIT REPORT
======================================================================
Total PDF Pages:                   54 pages (Target: 50–80 pages) [PASSED]
Total Text Characters:             122,635 characters (~24,527 words) [PASSED]
Total Embedded Figures / Images:   19 high-resolution assets [PASSED]
Specification Standard:            IEEE Std 830-1998 Aligned [PASSED]
Word COM PDF Engine:               Microsoft Word 16.0 (Format 17) [PASSED]
PyMuPDF Extraction Engine:         v1.28.2 Verified [PASSED]
Primary Deliverable Path:          c:/Users/ASUS/Downloads/hcl/
Secondary User Download Copy:      c:/Users/ASUS/Downloads/
======================================================================
```

---

## 2. Source Code & Architecture File Provenance

All architectural descriptions, mathematical formulas, and component profiles in the study guide were directly extracted and verified against the following repository source files:

| System Layer | Physical Repository Path | Component Verified | Key Classes / Functions Audited |
| :--- | :--- | :--- | :--- |
| **Presentation Tier** | `frontend/pages/` | Multi-Page Web Portals | 7 addressable routes (`/`, `/manual-workflow`, `/verification-studio`, etc.) |
| **API Gateway Tier** | `api/main.py` | FastAPI Application Core | `@asynccontextmanager lifespan`, CORS middleware, route registration |
| **API Routers** | `api/routers/` | Endpoint Modules | `auth.py`, `verification.py`, `compliance.py`, `audit.py`, `system.py` |
| **Computer Vision** | `ml/preprocessing/signature_preprocessor.py` | OpenCV Preprocessing Core | Otsu binarization, Zhang-Suen thinning, 16-D feature vector extractor |
| **Classical ML** | `ml/models/classical_models.py` | Track A Machine Learning | `RandomForestClassifier`, `LinearSVC`, `LogisticRegression` |
| **Deep Metric Learning** | `ml/models/transformer_models.py` | Track B Vision Transformer | `facebook/deit-tiny-patch16-224`, 128-d metric projection head |
| **Risk Governance** | `services/risk_engine.py` | 4-Pillar Composite Risk | 50% Similarity, 15% Quality, 25% Transaction, 10% Behavior |
| **Data Persistence** | `database/models.py` | PostgreSQL ORM Schema | `User`, `Account`, `Signature`, `VerificationRequest`, `AuditLog` |
| **Connection Pooling** | `database/session.py` | SQLAlchemy Sessionmaker | ACID transactional sessions, connection pool timeout management |
| **Schema Migrations** | `alembic/versions/` | Alembic Version Scripts | Declarative schema migrations with reversible upgrade/downgrade logic |
| **Automated Testing** | `tests/` | Pytest Test Suite | 53 unit and integration tests across 6 dedicated test modules |
| **System Diagnostics** | `scripts/diagnose.py` | Self-Diagnostic Checks | 16 automated hardware, model, and database integrity checks |

---

## 3. Strict Project Separation (SIGNATURE VMAKE vs. SYNAPSE)

The audit confirms that the generated study guide strictly enforces the requested architectural boundary:

1. **Production Champion:** scikit-learn Random Forest (100 estimators, 16 handcrafted geometric/topological features).
2. **Track B Transformer:** Hugging Face Vision Transformer (`facebook/deit-tiny-patch16-224`).
3. **No SYNAPSE Contamination:** The legacy Siamese ResNet-50 architecture, `v4_champion_model.pt`, and `ForgeryAwareMetricLoss` are excluded from VMAKE's production identity and explained only as legacy research context.

---

## 4. Empirical Evaluation Benchmark Verification

Metrics cited in the study guide were verified against `artifacts/evaluation/model_comparison_benchmark.json`:

### Dataset: CEDAR Benchmark (55 Writers, 2,640 Signatures)
- **Train Cohort:** Writers 1 to 35 (63.6% of writers, 2,500 balanced pairs)
- **Validation Cohort:** Writers 36 to 45 (18.2% of writers, 1,200 balanced pairs)
- **Held-Out Test Cohort:** Writers 46 to 55 (18.2% of writers, 1,200 balanced pairs)
- **Zero-Leakage Rule:** $\mathcal{W}_{\text{train}} \cap \mathcal{W}_{\text{test}} = \emptyset$ (100% writer-disjoint open-set protocol)

### Held-Out Test Cohort Performance Summary

| Architecture / Model | ROC-AUC | Equal Error Rate (EER) | Accuracy | FRR ($\alpha$) | FAR ($\beta$) | F1 Score | CPU Latency | Model Checkpoint |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Random Forest (Champion)** | **0.9424** | **13.33%** | **82.92%** | **3.83%** | **30.33%** | **0.8492** | **10.23 ms** | `classical_random_forest_model.joblib` (2.39 MB) |
| **Logistic Regression** | 0.8808 | 18.83% | 80.50% | 12.00% | 27.00% | 0.8186 | **6.00 ms** | `classical_logistic_model.joblib` (0.02 MB / 20 KB) |
| **Linear SVM Baseline** | 0.8574 | 19.00% | 79.17% | 13.17% | 28.50% | 0.8065 | 6.03 ms | `classical_svm_model.joblib` (1.90 MB) |
| **Vision Transformer (DeiT)** | 0.7947 | 27.67% | 64.50% | **3.83%** | 67.17% | 0.7304 | 36.66 ms | `transformer_signature_model.pt` (21.73 MB) |

### Champion Confusion Matrix on Held-Out Test Cohort (1,200 Pairs)
- **True Positives (TP):** 577 pairs (Genuine accepted as Genuine)
- **False Negatives (FN):** 23 pairs (Genuine falsely rejected as Forgery)
- **True Negatives (TN):** 418 pairs (Skilled forgery correctly rejected)
- **False Positives (FP):** 182 pairs (Skilled forgery falsely accepted)
- **True Acceptance Rate (TAR / Recall):** $577 / 600 = 96.17\%$
- **False Rejection Rate (FRR):** $23 / 600 = 3.83\%$
- **Precision:** $577 / 759 = 76.02\%$
- **Accuracy:** $(577 + 418) / 1,200 = 82.92\%$
- **Harmonic F1-Score:** $0.8492$

---

## 5. Risk Engine & Core Banking Workflow Audit

The mathematical formulation in `services/risk_engine.py` was verified:

$$\text{Overall Risk} = 0.50 \times R_{\text{sim}} + 0.15 \times R_{\text{qual}} + 0.25 \times R_{\text{tx}} + 0.10 \times R_{\text{beh}}$$

- **Similarity Risk ($R_{\text{sim}}$):** $1.0 - P_{\text{genuine}}$ (Derived from Random Forest tree probability).
- **Image Quality Risk ($R_{\text{qual}}$):** $0.60 \times \max(0, 1 - \frac{\text{Var}(\text{Laplacian})}{500}) + 0.40 \times \max(0, 1 - \frac{\text{Contrast}}{180})$.
- **Transaction Exposure Risk ($R_{\text{tx}}$):** $\min(1.0, \frac{\text{Cheque Amount}}{\$500,000})$.
- **Behavioral Velocity Risk ($R_{\text{beh}}$):** $\min(1.0, \frac{\text{24h Velocity}}{5.0}) + (0.5 \text{ if Account Age} < 30 \text{ days else } 0.0)$.

### Tri-State Decision Matrix Audit
- **`VERIFIED` (Automated Clearance):** Similarity $\ge 0.4264$ AND Composite Risk $< 0.25$.
- **`MANUAL REVIEW` (Officer Review Queue):** Similarity in $[0.3064, 0.4264)$ OR Composite Risk in $[0.25, 0.60)$.
- **`REJECTED` (Fraud Interception):** Similarity $< 0.3064$ OR Composite Risk $\ge 0.60$.
- **First-Upload Specimen Rule:** The first signature upload enrolls reference specimen only; similarity is strictly $0.0$, risk is $0.0$, verdict is `SPECIMEN_REGISTERED` (`tests/test_manual_workflow.py`).

---

## 6. Automated Testing & Quality Gate Verification

| Test Suite | Location | Tests Executed | Passed | Failed | Execution Time | Quality Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Pytest Full Suite** | `tests/` | 53 | 53 | 0 | 60.27s | **100% Passed** |
| **System Diagnostics** | `scripts/diagnose.py` | 16 | 16 | 0 | 2.14s | **100% Passed** |
| **Multipage E2E Test** | `scripts/test_multipage_e2e.py` | 7 | 7 | 0 | 1.85s | **100% Passed** |

---

## 7. Explicit Project Boundaries & Limitations

To maintain academic integrity during viva examination, the following limitations are formally documented:
1. **Offline Only:** Processes 2D scanned raster images; does not capture dynamic time-series stylus telemetry (pen velocity, pressure over time, azimuth angle).
2. **Latin Alphabet Focus:** Benchmarked on the CEDAR dataset (Latin script). Non-Latin scripts (Devanagari, Arabic, Cyrillic) require retraining.
3. **Cheque Truncation Simulation:** Simulates CTS-2010 clearance workflows via REST API endpoints but is not connected to live banking clearing networks (NPCI, SWIFT, RTGS).
4. **Targeted Signature Authentication:** Specifically authenticates signatures and validates cheque layout; does not replace general OCR engines for unstructured full-page text parsing.

---

## 8. Artifact Locations & Verification Checklist

- [x] `SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.pdf` (54 pages, 2.38 MB) in `c:\Users\ASUS\Downloads\hcl\`
- [x] `SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.docx` (2.05 MB) in `c:\Users\ASUS\Downloads\hcl\`
- [x] `SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.pdf` in `c:\Users\ASUS\Downloads\`
- [x] `SIGNATURE_VMAKE_COMPLETE_PROJECT_STUDY_GUIDE.docx` in `c:\Users\ASUS\Downloads\`
- [x] `SIGNATURE_VMAKE_STUDY_AUDIT.md` in `c:\Users\ASUS\Downloads\hcl\`
- [x] All 17 Parts and 63 Chapters fully elaborated with Level 1 and Level 2 explanations.
- [x] All 19 visual figures, UML diagrams, DFDs, benchmark charts, and real UI screenshots embedded.
- [x] 60+ Viva questions and model answers with "What NOT to Say" trap guidance.
- [x] 12-step live demonstration script verified for practical examination.
