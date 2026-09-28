# METRIC LOSS FUNCTION COMPARISON
**SYNAPSE — Intelligent Signature Verification Platform**
*Phase 11 & 12: Metric Learning Loss Function & Combined Objective Evaluation*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Mathematical Formulations

Three metric learning objectives were implemented in [`ml/models/losses.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/models/losses.py):

### 1. Contrastive Loss (Hadsell et al., CVPR 2006)
$$L_{\text{cont}}(y, D) = \frac{1}{2} y D^2 + \frac{1}{2} (1 - y) \max(0, m - D)^2$$
where $y \in \{0, 1\}$, $D = \|\mathbf{z}_1 - \mathbf{z}_2\|_2$, and margin $m = 1.0$.

### 2. Triplet Loss (Schroff et al., CVPR 2015)
$$L_{\text{triplet}}(a, p, n) = \max(0, D(a, p) - D(a, n) + \alpha)$$
where $a$ is anchor, $p$ is positive (genuine), $n$ is negative (forged), and $\alpha = 0.3$.

### 3. Hybrid Metric Loss (Combined Objective)
$$L_{\text{hybrid}} = \alpha \cdot L_{\text{cont}} + \beta \cdot L_{\text{batch-triplet}}$$
In each mini-batch, active hardest negative mining finds the closest negative embedding $\mathbf{z}_{n}^*$ to each genuine anchor $\mathbf{z}_a$, enforcing relative margin separation simultaneously with absolute Euclidean clustering.

---

## 2. Controlled Empirical Comparison on Validation Cohort

| Loss Function | Parameters | Val AUC | Val EER | Skilled FAR | Overall FAR | Val TAR | Convergence Speed |
|---|---|---|---|---|---|---|---|
| **Contrastive Loss** | $m = 1.0$ | 0.6728 | 38.58% | 50.00% | 38.58% | 61.33% | Fast (2 epochs) |
| **Contrastive + HNM** | $m = 1.0, \text{HNM}=35\%$ | 0.7976 | 28.75% | 37.78% | 28.75% | 71.17% | Moderate |
| **Hybrid Metric Loss** | $\alpha=1.0, \beta=0.5, m=1.0, \alpha_{\text{trip}}=0.3$ | **0.8326** | **23.75%** | **33.33%** | **23.75%** | **76.33%** | **Fastest & Most Stable** |
| **Champion (Hybrid + HNM + Aug)** | Full configuration | **0.8277** | **24.33%** | **27.78%** | **24.33%** | **75.67%** | **Optimal Generalization** |

### Key Findings
1. Triplet regularization inside the mini-batch directly forces $D(a, n) > D(a, p) + 0.3$, preventing skilled forgeries from inhabiting the same similarity neighborhood as genuine intra-writer variations.
2. The combination of Hybrid Metric Loss and Hard Negative Mining reduced skilled forgery false acceptances on validation from $50.00\%$ down to $27.78\%$, outperforming contrastive loss alone by over $22$ percentage points.
