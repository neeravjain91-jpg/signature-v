# MODEL GENERALIZATION & RECONCILIATION AUDIT (PHASE 1)

## Executive Summary
This audit reconciles the empirical divergence between the previous candidate model (**Champion A**, commit `5633043`) and the recently trained model (**Champion B**, commit `e1ea966`), establishes why single-split validation caused selection instability, and introduces the formal writer-disjoint development cross-validation framework.

---

## 1. Direct Comparison: Champion A vs. Champion B

| Attribute | Champion A (commit `5633043`) | Champion B (commit `e1ea966`) | Discrepancy / Root Cause |
| :--- | :---: | :---: | :--- |
| **Checkpoint Path** | `artifacts/models/champion_candidate_model.pt` | `artifacts/models/champion_siamese_model.pt` | Distinct binary checkpoints |
| **SHA-256 Hash** | `9950842f9754770325b5d6461a87e5f81a266c851b74160e06ed593b4af931dd` | `4ce23874c1091a0bde492768ef884eaf09fb13390045cf09590e72071cf0b550` | Different parameter weights |
| **Backbone Architecture** | Modified ResNet-18 ($d=256$) | Modified ResNet-18 ($d=256$) | Identical structure |
| **Loss Objective** | `HybridMetricLoss` ($\alpha=1.0, \beta=0.5, m_c=1.0, m_t=0.3$) | `HybridMetricLoss` ($\alpha=1.0, \beta=0.5, m_c=1.0, m_t=0.3$) | Identical loss formulation |
| **Preprocessing** | Otsu binarization, bbox crop, aspect-ratio padding ($224\times 224$) | Otsu binarization, bbox crop, aspect-ratio padding ($224\times 224$) | Identical preprocessor |
| **Data Augmentation** | `RealisticSignatureAugmentor` (rotation, shear, scale, noise, blur) | `RealisticSignatureAugmentor` (rotation, shear, scale, noise, blur) | Identical configuration |
| **Training Cohort** | Writers 1–35 (CEDAR) | Writers 1–35 (CEDAR) | Identical training writers |
| **Validation Cohort** | Writers 36–45 (CEDAR, 1,200 pairs) | Writers 36–45 (CEDAR, 1,200 pairs) | Identical validation cohort |
| **Test Cohort** | Writers 46–55 (CEDAR, 1,200 pairs) | Writers 46–55 (CEDAR, 1,200 pairs) | Identical test pairs |
| **RNG & Training Process** | Trained as experiment 12 in `run_experiments.py` after 11 runs; PyTorch RNG drifted through $>50\text{k}$ operations | Retrained standalone from fresh `torch.manual_seed(42)` in `train_champion.py` | **RNG state and mini-batch sequence diverged completely** |
| **Val EER Threshold (\(\tau^*\))** | $\mathbf{0.7382}$ | $\mathbf{0.7394}$ | $+0.0012$ threshold shift |
| **Validation AUC** | $0.8277$ | $\mathbf{0.8631}$ | **Champion B appeared +0.0354 superior on validation** |
| **Validation Skilled FAR** | $\mathbf{27.78\%}$ | $31.67\%$ | Champion B had $+3.89\%$ higher skilled false acceptance on validation |
| **Validation Random FAR** | $19.17\%$ | $\mathbf{6.25\%}$ | Champion B learned to heavily penalize random impostors |
| **Validation TAR** | $75.67\%$ | $\mathbf{78.33\%}$ | Champion B predicted higher similarities overall |
| **Test AUC (Writers 46–55)** | $\mathbf{0.8756}$ | $0.8512$ | **Champion A generalized better to test writers** |
| **Test Skilled FAR** | $\mathbf{21.94\%}$ (79/360) | $47.50\%$ (171/360) | **$+25.56\%$ skilled FAR surge in Champion B** |
| **Test Overall FAR** | $\mathbf{15.17\%}$ (91/600) | $31.33\%$ (188/600) | $+16.16\%$ overall FAR increase |
| **Test TAR** | $75.50\%$ | $\mathbf{83.50\%}$ | Champion B operated at a more permissive operating point |

---

## 2. Forensic Breakdown: Why Did Skilled FAR Double from 21.94% to 47.50%?

### A. The Validation Metric Illusion
When evaluating on the 10 validation writers (Writers 36–45):
- Champion B achieved a higher validation AUC ($0.8631$ vs $0.8277$).
- However, this AUC gain was **entirely driven by cross-writer random impostors**, where Champion B achieved an exceptional $6.25\%$ Random FAR (vs $19.17\%$ for Champion A).
- In reality, Champion B was already **inferior on skilled forgeries** during validation ($31.67\%$ vs $27.78\%$).
- The model-selection logic prioritized validation AUC, erroneously selecting Champion B despite its worse skilled-forgery rejection.

### B. High Writer-to-Writer Variance on Single-Split Validation
Evaluating writer-by-writer performance across Writers 36–45 reveals extreme volatility:
- **Writer 37**: Champion A skilled FAR was $13.9\%$; Champion B skilled FAR exploded to $69.4\%$ (mean forgery similarity jumped from $0.5647$ to $0.7595$, breaching the threshold $\tau^* = 0.7394$).
- **Writer 38**: Champion A skilled FAR was $27.8\%$; Champion B skilled FAR was $0.0\%$.
- **Writer 41**: Champion A TAR was $16.7\%$; Champion B TAR was $43.3\%$.
- **Writer 42**: Champion A skilled FAR was $55.6\%$; Champion B skilled FAR dropped to $19.4\%$.

Because a single 10-writer split contains only 10 writer handwriting styles, small changes in the weight initialization and batch ordering cause drastic shifts on specific writers. Selecting a model based on a single 10-writer validation set constitutes **validation overfitting**.

### C. Operating Point Shift
Champion A operated at a conservative threshold where TAR was $75.50\%$ and skilled FAR was $21.94\%$. Champion B operated at a permissive point where TAR was $83.50\%$, allowing $92$ additional skilled forgeries to breach the verification gate ($171$ vs $79$ false acceptances).

---

## 3. Methodological Mandate for Phase 2–16

1. **Abandon Single-Split Validation**: Never evaluate candidate models against a single fixed 10-writer cohort.
2. **Implement 5-Fold Writer-Disjoint Cross-Validation**: Partition all 45 development writers (Writers 1–45) into 5 writer-disjoint folds (9 writers per fold).
3. **Primary Selection Metric**: The primary model selection metric must strictly be **mean Skilled-Forgery FAR across all 5 validation folds**, with cross-fold stability ($\sigma_{\text{skilled FAR}}$) as an essential constraint.
4. **Preserve Test Cohort Integrity**: Writers 46–55 remain cryptographically isolated until the winning architecture and hyperparameters are selected, cross-validated, and frozen.
