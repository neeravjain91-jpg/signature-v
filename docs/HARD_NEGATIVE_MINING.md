# HARD NEGATIVE MINING REPORT
**SYNAPSE — Intelligent Signature Verification Platform**
*Phase 4: Targeted Hard Forgery Mining & Metric Space Separation*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Motivation and Algorithmic Design

In naive uniform random pair sampling, the Siamese network receives predominantly easy negative pairs (cross-writer comparisons with distinct names, stroke topologies, or letter shapes). These produce zero gradient under contrastive loss once the Euclidean distance $D \ge m$. Consequently, the network fails to allocate sufficient model capacity to resolving subtle imitation artifacts in skilled forgeries.

### Hard Negative Mining Algorithm
Implemented in [`ml/training/hard_negative_mining.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/training/hard_negative_mining.py):
1. **Source Cohort Restriction**: Mined strictly from the **Training Dataset (Writers 1–35)**. Test and validation cohorts are strictly excluded to preserve leakage-free integrity.
2. **Embedding Generation**: Forward pass of all negative pairs through the existing encoder checkpoint.
3. **Similarity Threshold Filtering**: Negative pairs assigned similarity $S \ge 0.68$ are tagged as hard negatives.
4. **Ranking & Top-$k$ Selection**: Top 800 hardest negatives are ranked descending by predicted similarity.
5. **Mini-Batch Injection**: Configurable `hard_negative_ratio` (35% in Champion) mixes hard negatives into each training batch, replacing trivial cross-writer negatives while maintaining exact 50% positive / 50% negative balance.

---

## 2. Empirical Validation Results (EXP-001 vs EXP-002)

| Metric | EXP-001 (Uniform Random Sampling) | EXP-002 (Hard Negative Mining 35%) | Relative Delta |
|---|---|---|---|
| **Validation ROC-AUC** | 0.6728 | **0.7976** | **+18.55%** |
| **Validation EER** | 38.58% | **28.75%** | **-25.48%** |
| **Skilled Forgery FAR** | 50.00% | **37.78%** | **-24.44%** |
| **True Acceptance Rate (TAR)**| 61.33% | **71.17%** | **+16.04%** |
| **Overall FAR** | 38.58% | **28.75%** | **-25.48%** |

### Key Observation
Injecting 35% mined hard negatives produced an immediate $12.48$ percentage point surge in validation AUC and drove validation skilled-forgery FAR down by over 12 percentage points, validating that training mini-batches were previously starved of difficult imitation pairs.
