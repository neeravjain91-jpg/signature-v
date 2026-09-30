# CHAMPION MODEL SELECTION REPORT
**SIGNATURE VMAKE — Intelligent Signature Verification & Fraud Detection System**
*Phase 21 & 22: Formal Validation Selection & Model Freezing*
*Date: September 28, 2026 | Protocol: Strict Validation Selection (Writers 36–45)*

---

## 1. Formal Model Selection Criteria

In accordance with strict biometric evaluation protocol, **zero test set data (Writers 46–55) was used to select the champion model, tune hyperparameters, or calibrate decision thresholds**.

The candidate models were evaluated exclusively on the **Validation Cohort (Writers 36–45, 1,200 pairs)** using the following hierarchical decision rule:
1. **Primary Criterion**: Lowest Skilled-Forgery False Acceptance Rate ($\text{FAR}_{\text{skilled}}$).
2. **Secondary Criterion**: Lowest Overall False Acceptance Rate ($\text{FAR}_{\text{overall}}$).
3. **Tertiary Criterion**: True Acceptance Rate ($\text{TAR} \ge 75\%$).
4. **Quaternary Criterion**: Highest ROC Area Under Curve ($\text{AUC-ROC}$).
5. **Operational Constraint**: Inference latency $< 30$ ms on standard CPU hardware.

---

## 2. Validation Ablation Leaderboard

| Exp ID | Configuration | Val AUC | Val EER | Skilled FAR | Overall FAR | Val TAR | Latency (ms) | Rank / Status |
|---|---|---|---|---|---|---|---|---|
| **EXP-001** | Baseline Replica (ResNet18, Cont. Loss, Otsu) | 0.6728 | 38.58% | 50.00% | 38.58% | 61.33% | 7.12 | Baseline reference |
| **EXP-002** | + Hard Negative Mining (35%) | 0.7976 | 28.75% | 37.78% | 28.75% | 71.17% | 7.15 | Major improvement |
| **EXP-003** | Pair Balance A (50/25/25) | 0.7725 | 30.67% | 37.50% | 30.67% | 69.33% | 7.10 | Acceptable |
| **EXP-004** | Pair Balance B (40/40/20) | 0.7418 | 32.75% | 39.44% | 32.75% | 67.33% | 7.08 | Sub-optimal |
| **EXP-005** | + Realistic Augmentation | 0.7608 | 31.50% | 39.72% | 31.50% | 68.50% | 7.18 | Regularized |
| **EXP-006** | Adaptive Gaussian Preproc | 0.8020 | 27.67% | 36.67% | 27.67% | 72.33% | 9.40 | Strong alternative |
| **EXP-007** | Morphological Preproc | 0.5000 | 50.00% | 0.00% | 0.00% | 0.00% | 11.20 | **Failed Hypothesis** |
| **EXP-008** | Custom CNN Backbone (4 Conv) | 0.7784 | 30.83% | 43.61% | 30.83% | 69.33% | 3.25 | Fast, but weaker FAR |
| **EXP-009** | Embedding Dim 128 | 0.7156 | 35.33% | 45.00% | 35.33% | 64.67% | 6.50 | Underparameterized |
| **EXP-010** | Embedding Dim 512 | 0.7251 | 32.83% | 41.94% | 32.83% | 67.33% | 7.45 | Overfitting risk |
| **EXP-011** | Hybrid Metric Loss (Cont. + Triplet) | **0.8326** | **23.75%** | 33.33% | 23.75% | 76.33% | 7.15 | Best single loss |
| **EXP-012** | **Combined Champion (ResNet18 + HNM 35% + Realistic Aug + Hybrid Loss)** | **0.8277** | **24.33%** | **27.78%** | **24.33%** | **75.67%** | **6.84** | **CHAMPION SELECTED** |

### Multi-Sample Reference Aggregation Boost (Phase 13)
When evaluating the champion model using customer specimen galleries (3 genuine signatures):
- `mean` strategy: AUC = 0.8691, Skilled FAR = 28.61%, TAR = 76.50%
- `centroid` strategy: AUC = 0.8839, Skilled FAR = 24.44%, TAR = 79.17%
- **`max` strategy: AUC = 0.8963, Skilled FAR = 15.83%, TAR = 83.00%**

---

## 3. Champion Model Technical Specification

The champion model is frozen as:
- **Weights**: [`artifacts/models/champion_siamese_model.pt`](file:///c:/Users/ASUS/Downloads/hcl/artifacts/models/champion_siamese_model.pt)
- **Configuration**: [`artifacts/models/champion_config.json`](file:///c:/Users/ASUS/Downloads/hcl/artifacts/models/champion_config.json)
- **Model Version**: `2.0.0-champion`
- **Backbone**: Modified ResNet-18 (5,276,640 parameters, 20.13 MB)
- **Embedding Dimension**: $d = 256$ (L2 hypersphere normalized)
- **Objective Function**: Hybrid Metric Loss ($\alpha=1.0 \cdot L_{\text{contrastive}} + \beta=0.5 \cdot L_{\text{triplet}}$, margin $= 1.0$, triplet margin $= 0.3$)
- **Data Pipeline**: Realistic Offline Augmentor (rotation, shear, scale, scanner noise) + Otsu binarization
- **Hard Negative Mining**: 35% hard negative ratio mined strictly from training cohort
- **Frozen Validation Threshold**: $\tau^* = 0.7382$
- **Inference Latency**: 6.84 ms per pairwise comparison
