# FINAL ML VALIDATION & SYSTEM IMPROVEMENT REPORT
**SIGNATURE VMAKE — Intelligent Signature Verification & Banking Fraud Detection Platform**
*Audit & Evaluation Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu, Windows x64*

---

## 1. Executive Summary & Improvement Highlights

This report documents the rigorous, leakage-free upgrade of the **SIGNATURE VMAKE Siamese Neural Network ML system** from the initial baseline (`artifacts/models/best_siamese_model.pt`) to the production **Champion Model** (`artifacts/models/champion_siamese_model.pt`, `2.0.0-champion`).

### Primary Objectives & Outcomes
1. **Targeted Skilled Forgery Mitigation**:
   - The primary weakness of the baseline model was its high skilled-forgery false acceptance rate on unseen writers ($62.22\%$ on the test cohort).
   - Through **Hard Negative Mining (35% ratio)**, **Realistic Biomechanical Augmentation**, and **Hybrid Metric Loss (Contrastive + Triplet)**, the Champion model reduced test Skilled Forgery FAR from **62.22% down to 21.94%** (a 40.28 percentage point absolute drop, 64.7% relative reduction).
2. **Overall Fraud False Acceptance Reduction**:
   - Overall test impostor FAR plummeted from **45.67% down to 15.17%** (183 fewer unauthorized cheques accepted).
   - Random cross-writer impostor FAR dropped from $20.83\%$ down to **$5.00\%$** (a 95.00% fraud block rate).
3. **Preservation of Genuine Customer Clearance**:
   - True Acceptance Rate ($\text{TAR}$) remained strong at **$75.50\%$** (pairwise) and surged to **$83.00\%$** in multi-specimen banking gallery mode.
4. **Overall Model Quality Boost**:
   - Unseen Test ROC-AUC expanded from **0.7410 to 0.8756** (+13.46 percentage points).
   - Test Equal Error Rate (EER) improved from **32.42% down to 19.50%**.
   - Classification accuracy increased from **64.83% to 80.17%**.
5. **Strict 3-Stage Scientific Protocol Adherence**:
   - **TRAIN (Writers 1–35)**: Zero overlap with validation or test writers.
   - **VALIDATION (Writers 36–45)**: All hyperparameter sweeps, architecture selections, loss formulations, and threshold calibrations occurred strictly on validation data.
   - **FINAL TEST (Writers 46–55)**: Evaluated only once with the frozen model and frozen threshold ($\tau^* = 0.7382$). Zero test snooping or post-hoc threshold adjustment occurred.

---

## 2. Final Frozen Test Results: Baseline vs. Champion

Evaluated on the open-set **Test Cohort (Writers 46–55, 1,200 pairs: 600 genuine, 360 skilled forgery, 240 random impostor)**:

| Metric | BASELINE MODEL (`1.0.0`) | CHAMPION MODEL (`2.0.0-champion`) | Absolute Change | Relative Improvement |
|---|---|---|---|---|
| **Model Checkpoint** | `best_siamese_model.pt` | `champion_siamese_model.pt` | Upgraded weights | — |
| **Operating Threshold** | $\tau^* = 0.7766$ (val frozen) | $\tau^* = 0.7382$ (val frozen) | Calibrated leak-free | — |
| **ROC-AUC (Test)** | **0.7410** | **0.8756** | **+0.1346** | **+18.16%** |
| **Test EER** | **32.42%** | **19.50%** | **-12.92%** | **-39.85%** |
| **Overall Accuracy** | **64.83%** (778/1,200) | **80.17%** (962/1,200) | **+15.34%** | **+23.66%** |
| **Overall False Acceptance (FAR)**| **45.67%** (274/600) | **15.17%** (91/600) | **-30.50%** | **-66.78%** |
| **Skilled Forgery FAR** | **62.22%** (224/360) | **21.94%** (79/360) | **-40.28%** | **-64.74%** |
| **Random Impostor FAR** | **20.83%** (50/240) | **5.00%** (12/240) | **-15.83%** | **-76.00%** |
| **True Acceptance Rate (TAR)** | **75.33%** (452/600) | **75.50%** (453/600) | **+0.17%** | Maintained $\ge 75\%$ |
| **False Rejection Rate (FRR)** | **24.67%** (148/600) | **24.50%** (147/600) | **-0.17%** | Stable |
| **Precision** | **0.6226** | **0.8327** | **+0.2101** | **+33.74%** |
| **Recall** | **0.7533** | **0.7550** | **+0.0017** | Stable |
| **F1-Score** | **0.6817** | **0.7920** | **+0.1103** | **+16.18%** |
| **Inference Latency (CPU)** | **10.31 ms** | **6.84 ms** | **-3.47 ms** | **-33.66% faster** |
| **Model Size** | 60.48 MB | **20.13 MB** | -40.35 MB | **-66.72% compact** |

---

## 3. Systematic Validation Ablation Leaderboard (Phases 4–14)

All candidate models were trained strictly on **Writers 1–35** and compared strictly on the **Validation Cohort (Writers 36–45, 1,200 pairs)**:

| Experiment ID | Primary Hypothesis / Configuration | Val AUC | Val EER | Skilled FAR | Val TAR | Latency | Outcome |
|---|---|---|---|---|---|---|---|
| **EXP-001** | Baseline Replica (ResNet18, Cont. Loss, Otsu) | 0.6728 | 38.58% | 50.00% | 61.33% | 7.12 ms | Reference baseline |
| **EXP-002** | + Hard Negative Mining (35% ratio) | 0.7976 | 28.75% | 37.78% | 71.17% | 7.15 ms | Major discrimination jump |
| **EXP-003** | Pair Balancing A (50% gen / 25% sk / 25% rnd) | 0.7725 | 30.67% | 37.50% | 69.33% | 7.10 ms | Moderate gain |
| **EXP-004** | Pair Balancing B (40% gen / 40% sk / 20% rnd) | 0.7418 | 32.75% | 39.44% | 67.33% | 7.08 ms | Sub-optimal |
| **EXP-005** | + Realistic Offline Augmentation | 0.7608 | 31.50% | 39.72% | 68.50% | 7.18 ms | High regularization |
| **EXP-006** | Adaptive Gaussian Preprocessing | 0.8020 | 27.67% | 36.67% | 72.33% | 9.40 ms | Viable alternative |
| **EXP-007** | Morphological Background Subtraction | 0.5000 | 50.00% | 0.00% | 0.00% | 11.2 ms | **Failed hypothesis** (eroded strokes) |
| **EXP-008** | Custom CNN Backbone (4 Conv layers) | 0.7784 | 30.83% | 43.61% | 69.33% | 3.25 ms | Fast, but weaker FAR |
| **EXP-009** | Embedding Dimension $d = 128$ | 0.7156 | 35.33% | 45.00% | 64.67% | 6.50 ms | Under-parameterized |
| **EXP-010** | Embedding Dimension $d = 512$ | 0.7251 | 32.83% | 41.94% | 67.33% | 7.45 ms | Over-fitting risk |
| **EXP-011** | Hybrid Metric Loss ($\alpha=1.0, \beta=0.5$) | 0.8326 | 23.75% | 33.33% | 76.33% | 7.15 ms | Best single loss |
| **EXP-012** | **Champion: ResNet18 + HNM 35% + Aug + Hybrid** | **0.8277** | **24.33%** | **27.78%** | **75.67%** | **6.84 ms** | **SELECTED CHAMPION** |

---

## 4. Multi-Sample Reference Banking Aggregation (Phase 13)

When evaluating customer galleries with 3 enrolled signature specimens on the validation cohort:

| Aggregation Strategy | Formulation | Val AUC | Val EER | Skilled FAR | Val TAR | Banking Recommendation |
|---|---|---|---|---|---|---|
| **Max Similarity (`max`)** | $\max_i S(q, r_i)$ | **0.8963** | **17.17%** | **15.83%** | **83.00%** | **PRODUCTION STANDARD** |
| **Centroid Embedding (`centroid`)**| $S(q, \text{norm}(\sum_i r_i))$ | 0.8839 | 20.50% | 24.44% | 79.17% | Solid alternative |
| **Top-$2$ Mean (`top_k`)** | $\frac{1}{2}(S_{(1)} + S_{(2)})$ | 0.8822 | 20.83% | 25.00% | 79.00% | Noise-resistant |
| **Mean Similarity (`mean`)** | $\frac{1}{K}\sum_i S(q, r_i)$ | 0.8691 | 23.50% | 28.61% | 76.50% | Baseline multi-ref |
| **Median Similarity (`median`)**| $\text{median}_i S(q, r_i)$ | 0.8622 | 22.50% | 26.94% | 77.83% | Outlier resistant |

---

## 5. False Acceptance Review: Writer 46 Case Study (Phase 25)

The forensic case study for test Writer 46 was re-evaluated under identical conditions:
- **Reference Specimen**: `data/raw/signatures/full_org/original_46_1.png`
- **Genuine Questioned**: `data/raw/signatures/full_org/original_46_2.png`
- **Skilled Forgery**: `data/raw/signatures/full_forg/forgeries_46_1.png`

| Metric / Decision | Baseline Model ($\tau^*=0.7766$) | Champion Model ($\tau^*=0.7382$) |
|---|---|---|
| **Genuine Distance / Similarity** | $D = 0.2288, \ S = 0.8856$ | $D = 0.2106, \ S = 0.8947$ |
| **Genuine Decision** | `VERIFIED` | `VERIFIED` |
| **Forgery Distance / Similarity** | $D = 0.3321, \ S = 0.8339$ | $D = 0.2657, \ S = 0.8672$ |
| **Forgery Decision** | `VERIFIED` (False Acceptance) | `VERIFIED` (False Acceptance) |
| **Separation Margin** | $+0.0517$ | $+0.0275$ |

### Scientific Finding
While the Champion model achieved an unprecedented $40.28\%$ reduction in skilled forgery false acceptances across the entire test cohort (from $62.22\%$ to $21.94\%$), on this individual extreme optical tracing (`original_46_1` vs `forgeries_46_1`), the 2D visual letterform trajectory remains too close to genuine specimens for single-pair static vision alone to reject it without rejecting genuine handwriting.
This demonstrates the absolute necessity of **SIGNATURE VMAKE's multi-layered defense**:
1. Multi-specimen gallery matching (Phase 13), which reduces skilled FAR to $15.83\%$.
2. Multi-factor banking risk scoring (Phase 19), which flags high-monetary-tier transactions ($>\$10,000$) or atypical transaction channels for mandatory officer review.

---

## 6. Full Diagnostic Plots & Visual Artifacts

The complete visual diagnostic suite has been updated with final champion test evaluations:
- **Champion ROC Curve**: [`docs/CHAMPION_ROC_CURVE.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/CHAMPION_ROC_CURVE.png) ($\text{AUC} = 0.8756$)
- **Champion FAR/FRR Curve**: [`docs/CHAMPION_FAR_FRR_CURVE.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/CHAMPION_FAR_FRR_CURVE.png)
- **Champion Score Distributions**: [`docs/CHAMPION_SCORE_DISTRIBUTIONS.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/CHAMPION_SCORE_DISTRIBUTIONS.png)
- **Validation Score Distributions**: [`docs/VALIDATION_SCORE_DISTRIBUTIONS.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/VALIDATION_SCORE_DISTRIBUTIONS.png)
- **Validation Threshold Sweep**: [`docs/VALIDATION_THRESHOLD_SWEEP.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/VALIDATION_THRESHOLD_SWEEP.png)
- **Writer-Level Analysis Manifest**: [`docs/VALIDATION_WRITER_ANALYSIS.csv`](file:///c:/Users/ASUS/Downloads/hcl/docs/VALIDATION_WRITER_ANALYSIS.csv)
- **Machine-Readable Experiment Registry**: [`ml/experiments/experiment_registry.json`](file:///c:/Users/ASUS/Downloads/hcl/ml/experiments/experiment_registry.json)
- **Champion Config & Metadata**: [`artifacts/models/champion_config.json`](file:///c:/Users/ASUS/Downloads/hcl/artifacts/models/champion_config.json)

---

## 7. Verification & Attestation

The entire software and ML test suite passes with **17/17 successful automated tests** (`pytest -v tests/`):
- Threshold calibration loading: **PASSED**
- Frozen Champion model loading: **PASSED**
- Zero writer leakage across splits: **PASSED**
- Multi-reference aggregation logic: **PASSED**
- Anti-hardcoding test: **PASSED**
- API health & verification endpoints: **PASSED**
- Audit trail & database ledger persistence: **PASSED**
