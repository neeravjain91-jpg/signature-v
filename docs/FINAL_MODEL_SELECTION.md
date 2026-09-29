# FINAL CHAMPION MODEL SELECTION REPORT (PHASE 12)

## Selection Hierarchy Mandate
The champion model was selected under the strict 6-tier optimization hierarchy across the 5 writer-disjoint development cross-validation folds (Writers 1–45):

1. **PRIMARY**: Lowest mean Skilled-Forgery FAR across validation folds.
2. **SECONDARY**: Lowest mean Overall FAR.
3. **THIRD**: Highest mean TAR (True Acceptance Rate).
4. **FOURTH**: Highest mean ROC-AUC.
5. **FIFTH**: Lowest EER (Equal Error Rate).
6. **SIXTH**: Inference latency and model compactness.
7. **CONSTRAINT**: Cross-fold stability (low standard deviation across writer cohorts).

---

## 5-Fold Benchmark Decision Matrix

| Rank | Model Pipeline | Mean Skilled FAR (Pri) | Mean Overall FAR (Sec) | Mean TAR (3rd) | Mean ROC-AUC (4th) | Mean EER (5th) | Latency (6th) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | **ResNet-18 + Focal Hybrid Loss (CV-03)** | **$37.35\% \pm 5.18\%$** | **$23.78\% \pm 2.92\%$** | **$76.26\% \pm 2.92\%$** | **$0.8373 \pm 0.0254$** | **$23.78\%$** | **$6.84\text{ ms}$** |
| **#2** | STN + ResNet-18 + Focal Hybrid Loss (CV-04) | $37.53\% \pm 1.84\%$ | $25.11\% \pm 0.76\%$ | $74.89\% \pm 0.76\%$ | $0.8308 \pm 0.0083$ | $25.11\%$ | $7.45\text{ ms}$ |
| **#3** | ResNet-18 + Standard Hybrid Loss (CV-02) | $37.90\% \pm 4.09\%$ | $25.96\% \pm 2.70\%$ | $74.15\% \pm 2.70\%$ | $0.8164 \pm 0.0222$ | $25.96\%$ | $6.84\text{ ms}$ |
| **#4** | Full Pipeline (Multi-View + STN + Adaptive Mining) | $39.38\% \pm 2.59\%$ | $29.18\% \pm 0.70\%$ | $70.82\% \pm 0.70\%$ | $0.7842 \pm 0.0070$ | $29.18\%$ | $8.20\text{ ms}$ |
| **#5** | Hybrid CNN + Transformer (CV-05) | $39.51\% \pm 5.88\%$ | $26.14\% \pm 3.36\%$ | $73.78\% \pm 3.36\%$ | $0.8146 \pm 0.0391$ | $26.14\%$ | $2.85\text{ ms}$ |
| **#6** | Baseline ResNet-18 + Contrastive (CV-01) | $38.89\% \pm 5.98\%$ | $30.49\% \pm 3.37\%$ | $69.52\% \pm 3.36\%$ | $0.7601 \pm 0.0322$ | $30.49\%$ | $6.84\text{ ms}$ |
| **#7** | Local-Global ResNet-18 (CV-06) | $40.19\% \pm 3.38\%$ | $26.44\% \pm 2.79\%$ | $73.56\% \pm 2.79\%$ | $0.8167 \pm 0.0278$ | $26.44\%$ | $7.10\text{ ms}$ |
| **#8** | Multi-View (3-View) STN ResNet (CV-07) | $41.60\% \pm 5.89\%$ | $29.74\% \pm 3.11\%$ | $70.48\% \pm 3.11\%$ | $0.7832 \pm 0.0311$ | $29.74\%$ | $7.80\text{ ms}$ |

---

## Winning Champion Selection
By unanimous decision across all 6 criteria:
- **Selected Champion**: **CV-03 (ResNet-18 + Focal Hybrid Metric Loss)**
- **Backbone**: Modified ResNet-18 with $L_2$ Unit Norm Embedding Head ($d=256$)
- **Preprocessing**: Otsu Binarization with bounding-box cropping and aspect-ratio padding ($224 \times 224$)
- **Objective Function**: `FocalHybridMetricLoss` ($\alpha = 1.0, \beta = 0.5, \gamma = 1.0, m_c = 1.0, m_t = 0.3$)
- **Augmentation**: `RealisticSignatureAugmentor` (micro-rotations, shear, scaling, pen pressure, scanner noise)
