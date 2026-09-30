# SIGNATURE VMAKE — Forensic Project Independence Audit

**Date of Audit:** September 30, 2026  
**Auditor Role:** Lead Software Architect, ML Engineer, and Security Auditor  
**Repository Target:** `signature-vmake` (`c:\Users\ASUS\Downloads\hcl`)  
**Audit Mandate:** Perform a strict, unsparing forensic audit to determine whether SIGNATURE VMAKE is genuinely independent from the legacy project `SYNAPSE`, or whether it utilizes copied, shared, or renamed checkpoints, thresholds, code, and benchmark results.

---

## 1. Executive Forensic Findings

> [!CRITICAL]
> **Forensic Verdict: Deep Historical Entanglement & Provenance Discovered**  
> An exhaustive forensic analysis of the git commit history, file metadata, model dictionaries, and serialized artifacts proves conclusively that **the current repository was originally created and developed as `SYNAPSE`**, and that the Siamese ResNet checkpoints, manifests, and thresholds present in `artifacts/models/` originated directly from the SYNAPSE project iterations.

### Git Commit History Provenance
The commit log of `origin/main` establishes the exact chronological lineage:

```
commit 2042ae364cacb8ef5b629e674dd6fcc08c85abee (HEAD -> main, origin/main)
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Tue Sep 29 14:06:28 2026 +0530
    feat(ml): complete SYNAPSE v4 customer-conditioned champion model with frozen test benchmarks

commit 26d35c942eb127c5bbdc5cb76d8b0a996f015ffc
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Tue Sep 29 08:08:44 2026 +0530
    feat(ml): complete generalization audit, 5-fold CV benchmarks, and frozen final champion

commit e1ea96696b95d03a1fc6c528437eb9431e5f8f8b
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Mon Sep 28 16:15:37 2026 +0530
    feat(ml): deploy champion siamese pipeline, frozen test evaluation, and reproducibility suite

commit 5633043834375b4855d0a6ea5a76985f43db48ae
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Mon Sep 28 15:47:05 2026 +0530
    feat(ml): complete all 30 phases of SYNAPSE ML system improvement and forensic audit

commit fa7e894080ca33cbf9ba46d843be732890520448
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Mon Sep 28 14:48:32 2026 +0530
    fix(ml): eliminate test-set threshold leakage with validation calibration and unbiased evaluation

commit 8fad681a95e7b41e3d36005c56d78707447eb596
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Mon Sep 28 12:35:10 2026 +0530
    feat(audit): frontend-to-backend integration audit and live API binding

commit 8b0bf7ee475657ef9a2c32cf9ef961e6047eb97c
Author: Neerav Jain <neeravjain91@gmail.com>
Date:   Mon Sep 28 12:12:47 2026 +0530
    feat(synapse): complete AI-based signature verification and fraud detection platform
```

### Forensic Proof:
1. **Initial Commit (`8b0bf7e`):** The repository was initialized with the commit title `feat(synapse): complete AI-based signature verification and fraud detection platform`.
2. **Siamese Model Lineage:**
   - Commit `8b0bf7e`: Created `best_siamese_model.pt` (SYNAPSE v1 baseline).
   - Commit `e1ea966`: Created `champion_siamese_model.pt` and `champion_config.json` (SYNAPSE v2).
   - Commit `26d35c9`: Created `final_champion_model.pt` and `FINAL_CHAMPION_MANIFEST.json` (SYNAPSE v3).
   - Commit `2042ae3`: Created `v4_champion_model.pt`, `v4_champion_config.json`, and `V4_CHAMPION_MANIFEST.json` (SYNAPSE v4).
3. **Artifact Configurations:** The configuration files committed alongside the checkpoints explicitly state:
   - `artifacts/models/v4_champion_config.json`: `"model_name": "SYNAPSE v4 Customer-Conditioned Champion"`
   - `artifacts/models/V4_CHAMPION_MANIFEST.json`: `"model_name": "SYNAPSE v4 Customer-Conditioned Champion"`
   - `artifacts/models/final_champion_config.json`: `"model_name": "SYNAPSE Final Champion Verifier"`
   - `artifacts/models/FINAL_CHAMPION_MANIFEST.json`: `"model_name": "SYNAPSE Final Champion Verifier v3.0.0"`
   - `artifacts/models/champion_config.json`: `"model_name": "SYNAPSE Champion Siamese Verifier"`

---

## 2. Exhaustive Suspicious Artifacts Catalog

Below is the complete itemized forensic inventory of every model checkpoint, manifest, configuration, and documentation artifact investigated during this audit:

| Artifact Path | Purpose | Determinable Origin | Belongs to VMAKE? | Replacement / Remediation Requirement |
| :--- | :--- | :--- | :---: | :--- |
| `artifacts/models/v4_champion_model.pt` | Track C Neural Checkpoint | Trained in commit `2042ae3` as SYNAPSE v4 | **NO (Legacy SYNAPSE)** | Must NOT simply be renamed. A dedicated VMAKE model lineage must be established. |
| `artifacts/models/v4_champion_config.json` | Model configuration & metadata | Contains `"SYNAPSE v4 Customer-Conditioned Champion"` | **NO (Legacy SYNAPSE)** | Must be replaced with independent VMAKE configuration. |
| `artifacts/models/V4_CHAMPION_MANIFEST.json` | Cryptographic SHA-256 manifest | Contains `"SYNAPSE v4 Customer-Conditioned Champion"` | **NO (Legacy SYNAPSE)** | Must be replaced with independent VMAKE manifest. |
| `artifacts/models/v4_champion_threshold.json` | Single (0.5924) & Gallery (0.6312) thresholds | Calibrated during SYNAPSE v4 training | **NO (Legacy SYNAPSE)** | Must be re-calibrated under VMAKE lineage. |
| `artifacts/models/final_champion_model.pt` | Track C v3 Neural Checkpoint | Trained in commit `26d35c9` as SYNAPSE v3 | **NO (Legacy SYNAPSE)** | Historical artifact; superseded. |
| `artifacts/models/final_champion_config.json` | v3 Model configuration | Contains `"SYNAPSE Final Champion Verifier"` | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/FINAL_CHAMPION_MANIFEST.json` | v3 Cryptographic manifest | Contains `"SYNAPSE Final Champion Verifier v3.0.0"` | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/final_champion_threshold.json` | v3 Threshold (0.7060) | Calibrated during SYNAPSE v3 training | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/champion_siamese_model.pt` | Track C v2 Neural Checkpoint | Trained in commit `e1ea966` as SYNAPSE v2 | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/champion_config.json` | v2 Model configuration | Contains `"SYNAPSE Champion Siamese Verifier"` | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/CHAMPION_MANIFEST.json` | v2 Cryptographic manifest | Contains `"SYNAPSE Champion Siamese Verifier"` | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/champion_threshold.json` | v2 Threshold (0.7394) | Calibrated during SYNAPSE v2 training | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/best_siamese_model.pt` | Initial baseline Siamese checkpoint | Trained in commit `8b0bf7e` as SYNAPSE v1 | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/calibrated_threshold.json` | v1 Threshold (0.7691) | Calibrated during SYNAPSE v1 training | **NO (Legacy SYNAPSE)** | Legacy artifact; superseded. |
| `artifacts/models/classical_svm_model.joblib` | Track A scikit-learn SVM model | Created in commit `2042ae3` | **YES (VMAKE Track A)** | Genuine scikit-learn model; retained and validated. |
| `artifacts/models/classical_svm_metrics.json` | Track A baseline metrics (0.8471 AUC) | Evaluated on validation cohort | **YES (VMAKE Track A)** | Retained and verified. |
| `artifacts/models/transformer_signature_model.pt` | Track B Hugging Face ViT model | Created in commit `2042ae3` | **YES (VMAKE Track B)** | Genuine Hugging Face Transformers model; retained and validated. |
| `artifacts/models/transformer_metrics.json` | Track B ViT metrics (0.8118 AUC) | Evaluated on validation cohort | **YES (VMAKE Track B)** | Retained and verified. |
| `docs/MANUAL_WORKFLOW_GUIDE.md` | Manual signature workflow guide | Authored with SYNAPSE headers & references | **NO (Legacy SYNAPSE)** | Must be purged of all SYNAPSE references and aligned with VMAKE. |
| `docs/CURRENT_PROJECT_AUDIT.md` | Legacy rebranding audit | Documents migration from SYNAPSE | **Reference Only** | Kept as documentation of past gap analysis. |

---

## 3. Technology Alignment & Multi-Track Status

The project requires genuine executable roles for:
1. **Python 3.11:** Core execution runtime, type hinting, asynchronous FastAPI endpoints.
2. **scikit-learn:** Track A Classical Classifier (`ml/baselines/classical_classifier.py`), utilizing 264-d HOG and morphological features with Platt-scaled Support Vector Machines (`CalibratedClassifierCV`).
3. **Hugging Face Transformers:** Track B Vision Transformer (`ml/models/transformer_signature_model.py`), fine-tuning DeiT-Tiny (`facebook/deit-tiny-patch16-224`) patch attention for signature verification.
4. **PyTorch / Deep Metric Learning:** Track C Siamese Neural Network (`ml/models/siamese_network.py` and `ml/models/architectures.py`), projecting signature strokes onto a 256-d unit hypersphere.
5. **FastAPI:** Asynchronous enterprise banking microservice (`api/main.py`) with 34 endpoints and auto-generated OpenAPI 3.1.0 specifications.

None of these technologies are stubs or checklist items; all three models execute real feature extraction and mathematical inference.

---

## 4. Remediation Plan: Establishing Independent SIGNATURE VMAKE Lineage

Per user requirement:
> "If the current VMAKE Track C is actually the SYNAPSE v4 model, do not merely rename `v4_champion_model.pt` to `vmake_champion_model.pt`. That is insufficient. SIGNATURE VMAKE needs its own reproducible model lineage."

### Actions Required:
1. **Define VMAKE-Native Model Architecture & Specification:**
   - Model Name: `SIGNATURE VMAKE Siamese Champion`
   - Model Version: `1.0.0-vmake-champion`
   - Backbone: `SiameseResNet18` (1-channel input, 256-d L2 hyperspherical projection)
   - Loss Function: `ForgeryAwareMetricLoss` (margin for random forgeries: 1.0, margin for skilled forgeries: 1.25)
2. **Native Training Execution:**
   - Execute a dedicated training script `ml/training/train_vmake_model.py` operating strictly on Writers 1–35.
   - Calibrate thresholds strictly on Writers 36–45.
   - Preserve Writers 46–55 as strictly frozen and untouched.
3. **Export Independent VMAKE Artifacts:**
   - `artifacts/models/vmake_champion_model.pt` (new weights and state dictionary)
   - `artifacts/models/vmake_champion_config.json` (explicit VMAKE lineage metadata)
   - `artifacts/models/vmake_champion_threshold.json` (calibrated operating cutoff)
   - `artifacts/models/VMAKE_CHAMPION_MANIFEST.json` (cryptographic SHA-256 attestation)
4. **Update Inference Engine & Service Dispatch:**
   - Configure `ml/inference/verify_signature.py` and `services/verification_service.py` to prioritize `vmake_champion_model.pt` as the primary production champion.
5. **Purge Documentation of Legacy SYNAPSE References:**
   - Clean `docs/MANUAL_WORKFLOW_GUIDE.md` and related documentation to remove lingering SYNAPSE branding.
