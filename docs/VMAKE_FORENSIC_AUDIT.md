# SIGNATURE VMAKE — Forensic Project Audit Report
**Date:** September 30, 2026  
**Auditor:** Lead Systems Architect, ML Engineer & QA Lead  
**Repository:** `neeravjain91-jpg/signature-verification`  
**Platform Identity:** SIGNATURE VMAKE (AI-Powered Signature Verification & Banking Document Authentication System)

---

### 1. Executive Summary & Objective

This forensic audit rigorously evaluates the current state of the **SIGNATURE VMAKE** repository against the approved project specification and technology requirements:
- **Mandatory Technologies:** Python, scikit-learn, Hugging Face Transformers, FastAPI.
- **Supporting Technologies:** OpenCV, NumPy, Pandas, PostgreSQL (with documented local SQLite fallback), SQLAlchemy, Alembic, PyTorch (strictly as execution backend for Transformers), Pytest/HTTPX, Docker.
- **Strict Constraint:** Absolute independence from legacy project `SYNAPSE`. PyTorch/Siamese ResNet metric learning must **NOT** be the primary project identity, and SYNAPSE-derived artifacts, lineages, and branding must be removed from the VMAKE production path.

---

### 2. Forensic Audit Findings by Subsystem

#### 2.1 Machine Learning Models & Checkpoints
| Model Track | Technology | Checkpoint File | Status | Genuine Inference | Notes / Discovered Issues |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Track A** | scikit-learn | `artifacts/models/classical_svm_model.joblib` | **Trained** | **Needs Normalization Fix** | Uses 264-d HOG and morphology. Forensic analysis discovered an RBF kernel distance saturation issue caused by standard scaling on low-variance features, causing out-of-distribution pairs to hit intercept. Must be refactored with bounded pairwise features. |
| **Track B** | Hugging Face Transformers | `artifacts/models/transformer_signature_model.pt` | **Trained** | **Operational** | Uses `facebook/deit-tiny-patch16-224` vision backbone with metric projection head to 256-d unit hypersphere. Genuinely executes on CPU/GPU. Needs calibrated validation threshold integration. |
| **Track C (Legacy)** | PyTorch Siamese ResNet | `artifacts/models/vmake_champion_model.pt` & `v4_champion_model.pt` | **Active in Code** | **Violation of Project Mandate** | **SYNAPSE Overlap:** Siamese ResNet was previously treated as the "champion" model in `ml/inference/verify_signature.py`, `api/main.py`, and `web/index.html`. Per BRD compliance, Track C must be decommissioned from the primary production path. |

#### 2.2 Suspicious Legacy SYNAPSE Overlap
The audit identified multiple artifacts and code segments derived from the legacy SYNAPSE project:
1. **Model Checkpoints:**
   - `artifacts/models/v4_champion_model.pt`
   - `artifacts/models/final_champion_model.pt`
   - `artifacts/models/champion_siamese_model.pt`
   - `artifacts/models/best_siamese_model.pt`
2. **Loss Functions & Architectures:**
   - `ml/models/forgery_aware_loss.py` (`ForgeryAwareMetricLoss`)
   - `ml/models/siamese_network.py` (`SiameseSignatureNet`)
   - `ml/training/train_v4_champion.py`, `train_final_champion.py`, `train_champion.py`
3. **Inference & Dispatch Defaults:**
   - `ml/inference/verify_signature.py`: default verifier factory returned `SignatureVerifier` (Siamese ResNet).
   - `services/verification_service.py`: default verifier was `SignatureVerifier`.
   - `api/main.py`: health endpoint inspected `models_status["neural"]` alongside Track A and Track B.
   - `web/index.html`: UI dropdown advertised "Model Track C: Siamese ResNet Champion (Production)".
4. **Remediation Action:**
   Decommission Siamese ResNet from all primary production entry points. The VMAKE primary architecture is strictly **Dual-Track: Track A (scikit-learn classical baseline) vs. Track B (Hugging Face Vision Transformer)**.

#### 2.3 Dataset & Partition Integrity
- **Dataset:** CEDAR Offline Signature Benchmark located in `data/raw/signatures/`.
  - Genuine specimens: 1,320 images across 55 writers (`original_{writer}_{specimen}.png`).
  - Skilled forgeries: 1,320 images across 55 writers (`forgeries_{writer}_{specimen}.png`).
  - Total: 2,640 images. Malformed images: 0.
- **Partitioning Strategy:**
  - **Train:** Writers 1–35 (35 writers, 7,000 pairs).
  - **Validation:** Writers 36–45 (10 writers, 1,200 pairs) used for threshold calibration and EER determination.
  - **Test:** Writers 46–55 (10 writers, 1,200 pairs) strictly held out for final evaluation.
  - **Leakage Audit:** Confirmed zero writer overlap ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).
- **Discovered Preprocessing Bug:**
  `data/processed/` images were pre-inverted by `prepare_dataset.py`. When `SignaturePreprocessor` ran on them with `invert_colors=True`, it double-inverted them, producing background-dominated masks (mean ~0.53) compared to raw images (mean ~0.017).
  **Fix:** Implement background-adaptive Otsu thresholding in `SignaturePreprocessor` to ensure identical normalized stroke masks regardless of source.

#### 2.4 FastAPI Backend & Health Verification
- `api/main.py` implements all 10 core banking modules: Authentication (JWT), Customer Profiles, Signature Enrollment, Multi-Track Verification, Transaction Ledgers, Fraud Risk Assessment, Compliance Queue, Immutable Audit Trail, Model Registry, and Dashboard Analytics.
- `/api/v1/models/health` executes live test-pair inferences on real image files before declaring `ready`.
- Must be updated to evaluate only the two official VMAKE tracks: Track A (`sklearn`) and Track B (`transformer`).

#### 2.5 Database & Ledger Persistence
- Uses SQLAlchemy 2.0 with PostgreSQL compatibility and local SQLite development fallback (`database/banking_system_demo.db`).
- Seed data (`database/seed_demo_data.py`) previously seeded Siamese ResNet as production champion. Must be updated to seed Track B (`HF_Vision_Transformer`) as Production and Track A (`Classical_SVM_Baseline`) as Baseline.

#### 2.6 Frontend Alignment (`web/index.html`)
- UI contains full banking studio capabilities with live fetch calls.
- Model selection dropdown currently features Track C as "Production". Must be refactored to focus exclusively on:
  1. **Track B: Hugging Face Vision Transformer** (Primary Deep Vision Architecture)
  2. **Track A: scikit-learn Classical Baseline** (Handcrafted SVM Baseline)
- Verification display must present the tri-state banking action: `VERIFIED`, `MANUAL REVIEW`, or `REJECTED`, alongside the biometric match verdict (`MATCH` / `NO MATCH`).

---

### 3. Step-by-Step Remediation Plan

1. **Preprocessing Pipeline Refactor:**
   Update [`ml/preprocessing/signature_preprocessor.py`](../ml/preprocessing/signature_preprocessor.py) with adaptive background polarity detection so raw scans and processed images produce identical stroke representations.
2. **Track A (scikit-learn SVM) Pipeline Repair:**
   Refactor [`ml/baselines/classical_classifier.py`](../ml/baselines/classical_classifier.py) and [`ml/baselines/train_baseline.py`](../ml/baselines/train_baseline.py) with unit-normalized pairwise features (absolute difference, cosine similarity, Euclidean distance) and train a robust, calibrated SVM on Writers 1–35, validating on Writers 36–45.
3. **Track B (Hugging Face Vision Transformer) Calibration:**
   Validate and calibrate [`ml/models/transformer_signature_model.py`](../ml/models/transformer_signature_model.py) and [`ml/models/train_transformer.py`](../ml/models/train_transformer.py) using the writer-disjoint split.
4. **Decommission Track C (Siamese ResNet) from Production:**
   - Update [`ml/inference/verify_signature.py`](../ml/inference/verify_signature.py): Remove Siamese ResNet as primary production engine. Default to Track B (HF ViT) with Track A (scikit-learn) selectable.
   - Update [`services/verification_service.py`](../services/verification_service.py): Route through Track B and Track A.
   - Archive legacy Siamese checkpoints and training scripts into [`ml/legacy_synapse/`](../ml/legacy_synapse/).
5. **FastAPI & Database Updates:**
   - Update `api/main.py`: Restrict model health and benchmarks to Track A and Track B.
   - Update `database/seed_demo_data.py`: Seed Track A and Track B model versions.
6. **Frontend Refactor (`web/index.html`):**
   - Update model selector to offer Track A and Track B.
   - Display tri-state banking decision (`VERIFIED`, `MANUAL REVIEW`, `REJECTED`).
7. **Testing, Diagnostics & Documentation:**
   - Create [`scripts/diagnose.py`](../scripts/diagnose.py) validating all 11 core subsystems.
   - Update [`docs/MODEL_COMPARISON.md`](../docs/MODEL_COMPARISON.md) and all documentation.
   - Execute full test suite and live end-to-end demonstration.
