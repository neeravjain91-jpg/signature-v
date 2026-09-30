# DATASET AND PAIR-CONSTRUCTION AUDIT
**SIGNATURE VMAKE — Intelligent Signature Verification & Fraud Detection System**
*Phase 3: Formal Data & Pair Construction Verification*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Executive Summary

This forensic audit examines the pair construction pipeline (`ml/data/create_pairs.py`), manifest composition across training, validation, and test splits, and empirical difficulty distributions produced by the baseline Siamese model (`artifacts/models/best_siamese_model.pt`).

### Key Findings
1. **Zero Data Leakage Across Splits**: The 55 total writers are split in a strictly disjoint writer-independent configuration:
   - **Training**: Writers 1–35 (35 writers, 63.6% of identities, 7,000 pairs)
   - **Validation**: Writers 36–45 (10 writers, 18.2% of identities, 1,200 pairs)
   - **Test**: Writers 46–55 (10 writers, 18.2% of identities, 1,200 pairs)
   - Zero writer overlap exists between any two splits.
2. **Zero Duplicate Pairs**: Both direct ordered duplicates `(image_1, image_2)` and unordered symmetric duplicates `(image_2, image_1)` were audited. There are **0 direct duplicates** and **0 inverted duplicates** across all three manifests.
3. **Rigorous Class Balance**:
   - Every split contains an exact 50% positive (`genuine_genuine`) and 50% negative (`skilled_forgery` + `random_forgery`) ratio.
   - Negative splits are explicitly partitioned into 60% skilled forgeries (same claimed writer identity forged by another person) and 40% random/cross-writer forgeries (different legitimate writer signatures).
4. **Uniform Writer Allocation**:
   - Training: Exactly 200 pairs per writer (100 genuine, 60 skilled forgery, 40 random forgery).
   - Validation: Exactly 120 pairs per writer (60 genuine, 36 skilled forgery, 24 random forgery).
   - Test: Exactly 120 pairs per writer (60 genuine, 36 skilled forgery, 24 random forgery).
5. **Empirical Difficulty Spectrum**:
   - In training, 37.43% (786/2,100) of skilled forgeries are scored above the frozen verification threshold ($\tau = 0.7766$), acting as hard negatives.
   - In validation, 37.78% (136/360) of skilled forgeries breach the threshold.
   - The primary weakness of the baseline model is not class imbalance or duplicate contamination; rather, it is the uniform random pair sampling during training which fails to sufficiently focus gradients on the 37.4% hard skilled negatives.

---

## 2. Manifest Inventory and Composition

| Split | Writers | Total Pairs | Genuine Pairs ($y=1$) | Skilled Forgery ($y=0$) | Random Forgery ($y=0$) | Negative Total ($y=0$) | Pairs / Writer | Direct Duplicates |
|---|---|---|---|---|---|---|---|---|
| **Train** | 1–35 (35) | 7,000 | 3,500 (50.0%) | 2,100 (30.0%) | 1,400 (20.0%) | 3,500 (50.0%) | 200 | 0 |
| **Validation** | 36–45 (10) | 1,200 | 600 (50.0%) | 360 (30.0%) | 240 (20.0%) | 600 (50.0%) | 120 | 0 |
| **Test** | 46–55 (10) | 1,200 | 600 (50.0%) | 360 (30.0%) | 240 (20.0%) | 600 (50.0%) | 120 | 0 |
| **Total** | 1–55 (55) | 9,400 | 4,700 (50.0%) | 2,820 (30.0%) | 1,880 (20.0%) | 4,700 (50.0%) | — | 0 |

---

## 3. Empirical Baseline Similarity Distribution by Pair Type

Evaluated using `artifacts/models/best_siamese_model.pt` without data augmentation:

### Training Cohort (Writers 1–35, 7,000 pairs)
| Pair Type | Count | Mean Sim | Std Dev | Median Sim | Min Sim | Max Sim | Threshold Violations ($\tau=0.7766$) | Classification Category |
|---|---|---|---|---|---|---|---|---|
| **Genuine-Genuine** | 3,500 | 0.8671 | 0.0907 | 0.8953 | 0.4290 | 0.9866 | 549 (15.69%) $< \tau$ | Hard Positives (False Rejections) |
| **Skilled Forgery** | 2,100 | 0.7250 | 0.1225 | 0.7309 | 0.4194 | 0.9670 | 786 (37.43%) $> \tau$ | Hard Negatives (False Acceptances) |
| **Random Forgery** | 1,400 | 0.6087 | 0.1257 | 0.5874 | 0.3770 | 0.9714 | 169 (12.07%) $> \tau$ | False Acceptances (Cross-Writer) |

### Validation Cohort (Writers 36–45, 1,200 pairs)
| Pair Type | Count | Mean Sim | Std Dev | Median Sim | Min Sim | Max Sim | Threshold Violations ($\tau=0.7766$) | Classification Category |
|---|---|---|---|---|---|---|---|---|
| **Genuine-Genuine** | 600 | 0.8146 | 0.1087 | 0.8375 | 0.4430 | 0.9680 | 166 (27.67%) $< \tau$ | FRR = 27.67% ($\text{TAR} = 72.33\%$) |
| **Skilled Forgery** | 360 | 0.7298 | 0.1102 | 0.7423 | 0.4429 | 0.9620 | 136 (37.78%) $> \tau$ | Skilled FAR = 37.78% |
| **Random Forgery** | 240 | 0.6166 | 0.1270 | 0.5934 | 0.4080 | 0.9424 | 29 (12.08%) $> \tau$ | Random FAR = 12.08% |
| **All Impostors** | 600 | 0.6845 | 0.1306 | 0.6898 | 0.4080 | 0.9620 | 165 (27.50%) $> \tau$ | Overall FAR = 27.50% |

---

## 4. Easy vs. Hard Example Stratification

Based on the distribution of baseline pairwise similarities:
1. **Easy Pairs**:
   - *Easy Genuine* ($S \ge 0.90$): 1,675 / 3,500 train pairs (47.86%). Zero contrastive loss gradient ($\max(0, D)^2 \to 0$).
   - *Easy Impostors* ($S \le 0.60$, $D \ge 0.80$): 902 / 2,100 skilled (42.95%) and 781 / 1,400 random (55.79%). Zero or near-zero negative loss gradient.
2. **Medium Pairs**:
   - Genuine pairs with $0.78 \le S < 0.90$ and impostors with $0.60 < S \le 0.75$. These contribute small but steady regularization gradients.
3. **Hard Pairs (The Critical Discriminators)**:
   - *Hard Skilled Negatives* ($S > 0.7766$): 786 training pairs. In these pairs, an unauthorized forger carefully traced or simulated the victim's letterforms, and the CNN backbone focused on coarse global geometry rather than fine stroke micro-structure.
   - *Extreme Hard Negatives* ($S > 0.85$): 332 training pairs. These represent the most severe failure mode where forgery similarity matches or exceeds genuine signatures.

---

## 5. Architectural Recommendations for Phase 4–12

1. **Hard Negative Mining (Phase 4)**:
   - Random sampling dilutes mini-batches with easy cross-writer negatives ($S \approx 0.60$).
   - Mining the top-$k$ hard negatives from the 786 training candidates and interleaving them into mini-batches will penalize impostor proximity directly.
2. **Loss Function Reformulation (Phase 11–12)**:
   - Standard contrastive loss with margin $m=1.0$ treats all negatives equally once $D \ge 1.0$.
   - Triplet Loss with hard negative mining forces relative ordering: $D(a, n) > D(a, p) + \alpha$, which directly addresses cases where genuine and forged distances are in the same band.
3. **Pair Balancing (Phase 6)**:
   - While the 50/30/20 balance is structurally sound, increasing the skilled forgery share to 40% (40% genuine, 40% skilled, 20% random) in training could direct more capacity towards high-fidelity forgery discrimination.
