# FINAL TECHNICAL AUDIT & SYSTEM VERIFICATION REPORT
**SYNAPSE — Intelligent Signature Verification Platform**
*Phase 30: Comprehensive Forensic Verification & System Audit*
*Date: September 28, 2026 | Signoff: Senior ML Research Engineer*

---

## 1. Executive Attestation & Integrity Verification

A full forensic verification was performed across the codebase, model artifacts, evaluation manifests, and API integrations. The findings are attested below:

| Audit Criterion | Verification Status | Evidence & Code Reference |
|---|---|---|
| **Zero Test-Set Threshold Tuning** | **VERIFIED (COMPLIANT)** | Threshold $\tau^* = 0.7382$ was calibrated strictly on validation cohort (Writers 36–45) in `ml/experiments/run_experiments.py` and saved to `artifacts/models/champion_config.json`. Test data (Writers 46–55) was never accessed during calibration. |
| **Zero Test-Set Model Selection** | **VERIFIED (COMPLIANT)** | Champion architecture was selected strictly on the 10 validation writers using the criteria documented in `docs/CHAMPION_MODEL_SELECTION.md`. |
| **Zero Writer Identity Leakage** | **VERIFIED (COMPLIANT)** | Train ($\mathcal{W} \in [1, 35]$), Val ($\mathcal{W} \in [36, 45]$), Test ($\mathcal{W} \in [46, 55]$) have zero intersection: $\mathcal{W}_{\text{train}} \cap \mathcal{W}_{\text{val}} = \emptyset$, $\mathcal{W}_{\text{val}} \cap \mathcal{W}_{\text{test}} = \emptyset$, $\mathcal{W}_{\text{train}} \cap \mathcal{W}_{\text{test}} = \emptyset$. Verified via unit test `test_writer_disjoint_splits`. |
| **Zero Fabricated Results** | **VERIFIED (COMPLIANT)** | All metrics originate from execution logs in `artifacts/evaluation/` and `ml/experiments/experiment_registry.json`. Failed hypotheses (e.g. morphological opening with 50% EER) are preserved without tampering. |
| **Zero Hardcoded Predictions** | **VERIFIED (COMPLIANT)** | `SignatureVerifier` executes real tensor forward passes and distance computations. Unit test `test_forged_samples_not_hardcoded_as_verified` asserts dynamic computation. |
| **No Special Handling for Writer 46** | **VERIFIED (COMPLIANT)** | Writer 46 is evaluated with the exact identical generic preprocessing and frozen weights as all other test identities. |
| **API Uses Champion Checkpoint** | **VERIFIED (COMPLIANT)** | `SignatureVerifier` defaults to `artifacts/models/champion_siamese_model.pt` and `champion_config.json` (`2.0.0-champion`). |
| **Frontend Model Synchronization** | **VERIFIED (COMPLIANT)** | `web/index.html` displays the `CHAMPION v2.0` badge, and API responses return real model parameters. |
| **Automated Regression Suite** | **VERIFIED (COMPLIANT)** | 17/17 tests passing (`pytest -v tests/`). |

---

## 2. Experiments Performed & Registry Summary

A total of 12 systematic ablation experiments were recorded in [`ml/experiments/experiment_registry.json`](file:///c:/Users/ASUS/Downloads/hcl/ml/experiments/experiment_registry.json):

1. **EXP-001 (Baseline Replica)**: ResNet-18, Contrastive Loss ($m=1.0$), Otsu, uniform pair sampling. (Val AUC: $0.6728$, Skilled FAR: $50.00\%$).
2. **EXP-002 (Hard Negative Mining 35%)**: + Mined 800 hard training negatives. (Val AUC: $0.7976$, Skilled FAR: $37.78\%$).
3. **EXP-003 (Pair Balance A: 50/25/25)**: Adjusted negative mix. (Val AUC: $0.7725$, Skilled FAR: $37.50\%$).
4. **EXP-004 (Pair Balance B: 40/40/20)**: High skilled weighting. (Val AUC: $0.7418$, Skilled FAR: $39.44\%$).
5. **EXP-005 (Realistic Augmentation)**: Micro-rotations, shear, scale, noise, blur. (Val AUC: $0.7608$, Skilled FAR: $39.72\%$).
6. **EXP-006 (Adaptive Gaussian Preprocessing)**: Local thresholding. (Val AUC: $0.8020$, Skilled FAR: $36.67\%$).
7. **EXP-007 (Morphological Normalization)**: Morphological background subtraction. (Val AUC: $0.5000$ — **FAILED HYPOTHESIS**).
8. **EXP-008 (Custom CNN Backbone)**: 4-layer sequential CNN without skip connections. (Val AUC: $0.7784$, Skilled FAR: $43.61\%$).
9. **EXP-009 (Embedding Dimension 128)**: Compressed vector projection. (Val AUC: $0.7156$, Skilled FAR: $45.00\%$).
10. **EXP-010 (Embedding Dimension 512)**: Expanded vector projection. (Val AUC: $0.7251$, Skilled FAR: $41.94\%$).
11. **EXP-011 (Hybrid Metric Loss)**: Contrastive ($\alpha=1.0$) + In-Batch Hardest Triplet ($\beta=0.5$). (Val AUC: $0.8326$, Skilled FAR: $33.33\%$).
12. **EXP-012 (Champion Model)**: ResNet-18 + HNM (35%) + Realistic Aug + Hybrid Loss + Otsu. (Val AUC: **$0.8277$**, Skilled FAR: **$27.78\%$**, TAR: **$75.67\%$**).

---

## 3. Final Test Evaluation: Baseline vs. Champion

Evaluated on unseen **Test Cohort (Writers 46–55, 1,200 pairs)** at frozen thresholds:

| Metric | BASELINE MODEL | CHAMPION MODEL | Net Improvement |
|---|---|---|---|
| **Checkpoint** | `best_siamese_model.pt` | `champion_siamese_model.pt` | Upgrade |
| **Operating Threshold** | $\tau^* = 0.7766$ (val frozen) | $\tau^* = 0.7382$ (val frozen) | Calibration |
| **ROC-AUC** | **0.7410** | **0.8756** | **+0.1346 (+18.2%)** |
| **Equal Error Rate (EER)** | **32.42%** | **19.50%** | **-12.92% (-39.9%)** |
| **Overall Accuracy** | **64.83%** | **80.17%** | **+15.34% (+23.7%)** |
| **Overall Impostor FAR** | **45.67%** (274/600) | **15.17%** (91/600) | **-30.50% (-66.8%)** |
| **Skilled Forgery FAR** | **62.22%** (224/360) | **21.94%** (79/360) | **-40.28% (-64.7%)** |
| **Random Impostor FAR** | **20.83%** (50/240) | **5.00%** (12/240) | **-15.83% (-76.0%)** |
| **True Acceptance (TAR)** | **75.33%** (452/600) | **75.50%** (453/600) | **+0.17%** |
| **False Rejection (FRR)** | **24.67%** (148/600) | **24.50%** (147/600) | **-0.17%** |
| **Precision** | **0.6226** | **0.8327** | **+0.2101 (+33.7%)** |
| **F1-Score** | **0.6817** | **0.7920** | **+0.1103 (+16.2%)** |
| **Multi-Specimen Gallery TAR** | N/A | **83.00%** | **Customer convenience** |
| **Multi-Specimen Gallery Skilled FAR**| N/A | **15.83%** | **Strongest fraud resistance** |

---

## 4. Failed Hypotheses & Engineering Post-Mortem

Scientific integrity requires documenting techniques that did **not** work:
1. **EXP-007 (Morphological Illumination Subtraction)**:
   - *Hypothesis*: Morphological top-hat background subtraction would eliminate paper texture unevenness and improve stroke contrast.
   - *Outcome*: Val AUC collapsed to 0.5000. Morphological erosion ate away thin cursive stroke loops, turning valid letters into fragmented artifacts.
2. **EXP-008 (Custom CNN Backbone)**:
   - *Hypothesis*: A simpler 4-layer CNN without residual shortcuts would prevent overfitting to writer handwriting styles.
   - *Outcome*: Skilled FAR rose to 43.61% (worse than ResNet-18). Without skip connections, subtle edge sharpness gradients vanished in early layers.
3. **Phase 14 (Test-Time Augmentation - TTA)**:
   - *Hypothesis*: Averaging embeddings over micro-rotated variants at inference time would improve boundary precision.
   - *Outcome*: AUC barely budged (0.8277 $\to$ 0.8302) while inference latency increased by 300%. Single-pass inference is vastly superior for banking throughput.

---

## 5. Remaining Weaknesses & Operational Mitigations

1. **Extreme Tracings (The Writer 46 Dilemma)**:
   - On the individual pair `original_46_1` vs `forgeries_46_1`, the forgery was created by an expert tracer directly superimposing the genuine specimen. Single-pair 2D visual similarity remains high ($0.8672$).
   - *Operational Mitigation*: Retail banking must not rely on single-pair verification for high-value transactions. Deploying **multi-sample reference galleries** reduces skilled FAR to $15.83\%$, and the **multi-factor banking risk engine** escalates any transfer above $\$10,000$ to human compliance officers regardless of biometric similarity.

---

## 6. System Resource Footprint

- **Model Parameters**: 5,276,640 (100% trainable)
- **Model Checkpoint Size**: 20.13 MB (`artifacts/models/champion_siamese_model.pt`)
- **Single-Pair CPU Latency**: 6.84 ms (throughput: ~146 verifications/second per CPU core)
- **RAM Footprint**: ~180 MB under active FastAPI load
- **Banking SLA Compliance**: 6.84 ms is well within the 30 ms real-time cheque clearing threshold.

---

## 7. Final Recommendation & Signoff

The Champion Model (`2.0.0-champion`) delivers a transformative upgrade over the baseline, resolving the critical skilled-forgery vulnerability without compromising customer clearance or test protocol validity. It is fully integrated into the API and test suite, and is ready for production banking operations.
