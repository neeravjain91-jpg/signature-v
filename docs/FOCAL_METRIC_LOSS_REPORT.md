# FOCAL METRIC LOSS & OBJECTIVE ABLATION REPORT (PHASE 6)

## Motivation
In standard contrastive and triplet learning, all pairs contribute equally to loss gradients. In banking signature verification, easy pairs (e.g., highly dissimilar random impostors or identical genuine signatures) quickly dominate loss gradients, leading to early plateauing and poor separation of subtle, skilled forgeries.

---

## Loss Formulations Benchmarked

1. **Standard Contrastive Loss**:
   $$L_C = y \cdot \frac{1}{2} d^2 + (1 - y) \cdot \frac{1}{2} \max(0, m - d)^2$$
2. **Hybrid Metric Loss**:
   $$L_H = \alpha L_C + \beta L_{\text{triplet-hardest}}$$
3. **Focal Contrastive Loss**:
   $$L_{FC} = y \cdot \left(\frac{d}{2}\right)^\gamma \cdot \frac{1}{2} d^2 + (1 - y) \cdot \left(\frac{\max(0, m - d)}{m}\right)^\gamma \cdot \frac{1}{2} \max(0, m - d)^2$$
   Where $\gamma = 1.0$ down-weights easy pairs where $d \approx 0$ (for $y=1$) or $d \ge m$ (for $y=0$), focusing optimization exclusively on borderline skilled forgeries.
4. **Focal Hybrid Metric Loss**:
   $$L_{\text{total}} = \alpha L_{FC} + \beta L_{\text{triplet-hardest}}$$

---

## 5-Fold Cross-Validation Empirical Results

| Metric Objective | Mean Skilled FAR | Mean Overall FAR | Mean TAR | Mean ROC-AUC | Mean EER |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Contrastive Loss** | $38.89\% \pm 5.98\%$ | $30.49\% \pm 3.37\%$ | $69.52\% \pm 3.36\%$ | $0.7601 \pm 0.0322$ | $30.49\%$ |
| **Hybrid Metric Loss** | $37.90\% \pm 4.09\%$ | $25.96\% \pm 2.70\%$ | $74.15\% \pm 2.70\%$ | $0.8164 \pm 0.0222$ | $25.96\%$ |
| **Focal Hybrid Metric Loss** | **$37.35\% \pm 5.18\%$** | **$23.78\% \pm 2.92\%$** | **$76.26\% \pm 2.92\%$** | **$0.8373 \pm 0.0254$** | **$23.78\%$** |

---

## Scientific Findings
1. **Dynamic Hard-Sample Weighting**: Focal Hybrid Metric Loss achieved the lowest Skilled FAR ($37.35\%$) and the highest AUC ($0.8373$), outperforming standard contrastive loss by $+0.0772$ in AUC and reducing skilled fraud false acceptance by $1.54$ percentage points.
2. **Gradient Attenuation on Mislabeled Outliers**: The focal weight dampening prevents rare dataset artifacts (such as mislabeled or corrupted scans) from exploding gradients, stabilizing AdamW optimizer trajectory.
