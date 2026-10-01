# SIGNATURE VMAKE — Presentation Forensic Audit Report
**Document**: B.Tech 3rd-Year Project Software Requirements Specification Presentation Audit  
**Target Project**: SIGNATURE VMAKE (AI-Powered Signature Verification & Banking Document Authentication System)  
**Date**: October 2026  
**Auditor**: Academic Presentation Design & Verification Specialist  

---

### 1. Presentation Metadata
- **Slide Count**: 17 Slides (Strict 1:1 alignment with IEEE Std 830-1998 Academic SRS Template).
- **Aspect Ratio**: 16:9 Widescreen (13.333 inches × 7.500 inches).
- **Target Audience**: B.Tech 3rd-Year University Evaluation Committee, Internal Examiner, Project Guide, Department HOD.
- **Output PowerPoint File**: `SIGNATURE_VMAKE_BTech_3rd_Year_Project_Presentation.pptx` (1,234,800+ bytes).
- **Output Speaker Notes**: `docs/PRESENTATION_VIVA_NOTES.md` (370+ lines, comprehensive viva questions).

---

### 2. Repository Sources & Commit Identification
- **Primary Git Repository**: `https://github.com/neeravjain91-jpg/signature-verification`
- **Secondary Git Repository**: `https://github.com/neeravjain91-jpg/signature-v`
- **Latest Commit Verified**: `4f9ff79` — *feat(frontend): convert single-page tabs into independent multi-page web application with dedicated routes*
- **Working Tree Status**: Clean, zero uncommitted or untracked changes.
- **Academic SRS Template**: `BTech_3rd_Year_SRS_Template.pdf` (Extracted and analyzed across all 7 pages).

---

### 3. Source Files Inspected & Verified
1. **Model Checkpoints**:
   - `artifacts/models/classical_random_forest_model.joblib` (SHA-256 verified, 2.39 MB)
   - `artifacts/models/classical_svm_model.joblib` (SHA-256 verified, 1.90 MB)
   - `artifacts/models/classical_logistic_model.joblib` (SHA-256 verified, 0.02 MB)
   - `artifacts/models/transformer_signature_model.pt` (SHA-256 verified, 21.73 MB)
2. **Benchmark Evaluation Artifacts**:
   - `artifacts/evaluation/model_comparison_benchmark.json` (Exact metrics source)
   - `artifacts/evaluation/vmake_test_evaluation.json` (Test evaluation summary)
   - `docs/MODEL_COMPARISON.md` (Comparative analysis documentation)
3. **Computer Vision & Inference Code**:
   - `ml/preprocessing/signature_preprocessor.py` (8-stage OpenCV pipeline)
   - `ml/inference/verify_signature.py` (Model Verifier Factory & verification dispatch)
   - `services/risk_engine.py` (Multi-factor fraud risk formula & decision logic)
   - `services/verification_service.py` (Orchestration & specimen gallery management)
4. **API & Database Architecture**:
   - `api/main.py` (42 registered endpoints, static mount, page routes)
   - `database/models.py` (11 relational entities in 3NF)
   - `database/schema.sql` (PostgreSQL 14+ DDL schema)
5. **Frontend Multi-Page Application**:
   - `web/index.html` (Overview Dashboard `/`)
   - `web/manual-workflow.html` (Manual Register & Verify `/manual-workflow`)
   - `web/verification-studio.html` (Cheque Clearance Studio `/verification-studio`)
   - `web/model-comparison.html` (Model Comparison Matrix `/model-comparison`)
   - `web/compliance-queue.html` (Officer Review Queue `/compliance-queue`)
   - `web/audit-timeline.html` (Regulatory Audit Trail `/audit-timeline`)
   - `web/model-registry.html` (Model Health & Diagnostics `/model-registry`)

---

### 4. Verified Benchmark Metrics (Held-Out Test Cohort: Writers 46–55)

| Metric | Random Forest (Champion) | Logistic Regression | Linear SVM Baseline | Vision Transformer (ViT) |
| :--- | :---: | :---: | :---: | :---: |
| **Model Version** | `1.0.0-sklearn-random_forest` | `1.0.0-sklearn-logistic` | `1.0.0-sklearn-svm` | `1.0.0-transformers-vit` |
| **ROC-AUC** | **0.9424** | **0.8808** | **0.8574** | 0.7947 |
| **Equal Error Rate (EER)** | **13.33%** | 18.83% | 19.00% | 27.67% |
| **Accuracy** | **82.92%** | 80.50% | 79.17% | 64.50% |
| **False Acceptance Rate (FAR)** | 30.33% | **27.00%** | 28.50% | 67.17% |
| **False Rejection Rate (FRR)** | **3.83%** | 12.00% | 13.17% | **3.83%** |
| **True Acceptance Rate (TAR)** | **96.17%** | 88.00% | 86.83% | **96.17%** |
| **F1 Score** | **0.8492** | 0.8186 | 0.8065 | 0.7304 |
| **Operating Threshold ($	au^*$)** | **0.4264** | **0.2015** | **0.3636** | **0.7313** |
| **Single-Pair Latency** | 10.23 ms | **6.00 ms** | **6.03 ms** | 36.66 ms |
| **Model Disk Size** | 2.39 MB | **0.02 MB** (20 KB) | 1.90 MB | 21.73 MB |

*All values verified against `artifacts/evaluation/model_comparison_benchmark.json`.*

---

### 5. Verified Test & Diagnostic Evidence
- **Pytest Automated Test Suite**: **53 passed / 53 total (100% pass rate)** in 60.27s.
  - `tests/test_api.py`: 12 tests passed
  - `tests/test_manual_workflow.py`: 12 tests passed
  - `tests/test_model_suite.py`: 9 tests passed
  - `tests/test_page_routing.py`: 10 tests passed
  - `tests/test_siamese_system.py`: 9 tests passed
  - `tests/test_traceability.py`: 1 test passed
- **Authoritative System Diagnostics**: **16 checks passed / 16 total (100% healthy)** via `scripts/diagnose.py`.
- **Live Multi-Page Routing**: 7/7 independent clean URL pages verified on `https://signature-verification-rho.vercel.app`.

---

### 6. Screenshots & Visual Assets Used
1. `screenshot_manual.png`: Hero screenshot of Manual Register & Verify interface (`/manual-workflow`).
2. `screenshot_overview.png`: Executive KPI Dashboard (`/`).
3. `screenshot_comparison.png`: Model Benchmark & Comparison matrix (`/model-comparison`).
4. `screenshot_queue.png`: Officer Compliance Review Queue (`/compliance-queue`).
5. `screenshot_studio.png`: Cheque Clearance Studio (`/verification-studio`).
6. `screenshot_audit.png`: Regulatory Audit Trail (`/audit-timeline`).
7. `screenshot_registry.png`: Model Health & Diagnostics (`/model-registry`).
8. `roc_auc_chart.png`: Custom high-res horizontal bar chart comparing ROC-AUC.
9. `eer_chart.png`: Custom high-res horizontal bar chart comparing EER.
10. `risk_weights_chart.png`: Custom donut chart illustrating the 4 risk engine dimensions.
11. `pipeline_diagram.png`: End-to-end horizontal dataflow pipeline schematic.
12. `architecture_diagram.png`: 4-tier block architecture diagram.
13. `dual_step_workflow.png`: Dual-step registration versus verification diagram.
14. `use_case_diagram.png`: IEEE 830 Use Case diagram mapping actors to capabilities.
15. `dfd_level_0.png`: DFD Level 0 Context Diagram showing external dataflows.
16. `sequence_diagram.png`: UML Sequence Diagram detailing message interactions.
17. `er_diagram.png`: Relational Entity-Relationship schema with 11 3NF entities.

---

### 7. Explicitly Labeled "Planned / Proposed" Items
To maintain complete academic honesty and adhere strictly to the project source of truth, the following items are explicitly marked as **Planned Future Scope** in the presentation:
1. Multilingual Indian signature dataset support (BHSig260 Hindi/Bengali scripts).
2. Full-cheque forgery localization heatmaps using Grad-CAM.
3. Automated OCR & MICR E-13B magnetic ink character parsing.
4. Online dynamic biometrics (pen velocity, pressure, azimuth angles).
5. Continuous model drift monitoring and retraining pipelines via MLflow.
6. Hardware Security Module (HSM) biometric template encryption at rest.
7. Direct core-banking network integration (SWIFT, RTGS, NEFT).

---

### 8. Project Independence Verification
- **Separation from SYNAPSE**: CONFIRMED.
- Siamese ResNet is NOT presented as the main model of SIGNATURE VMAKE.
- The presentation centers strictly on:
  - `scikit-learn` Classical ML: Random Forest (Champion), Linear SVM, Logistic Regression.
  - `Hugging Face Transformers`: Vision Transformer (`facebook/deit-tiny-patch16-224`).
  - `OpenCV`: Preprocessing pipeline.
  - `FastAPI`: REST gateway.
  - `PostgreSQL`: 11 relational entities in 3NF.
