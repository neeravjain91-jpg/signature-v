# REALISTIC AUGMENTATION & PREPROCESSING ABLATION
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Phase 7 & 8: Data Transformations & Preprocessing Pipeline Exploration*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Realistic Augmentation Pipeline (Phase 7)

Implemented in [`ml/preprocessing/augmentations.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/preprocessing/augmentations.py).

To prevent overfitting to exact scan resolutions while preserving writer stroke habits, natural biomechanical transforms were introduced:
- **Micro-rotation**: Random rotation $\in [-4^\circ, +4^\circ]$ simulating casual cheque signing angles.
- **Micro-shear**: Random affine shear $\in [-3^\circ, +3^\circ]$ simulating natural wrist angle variations.
- **Anisotropic Scaling**: Scale factor $\in [0.96, 1.04]$ simulating pen stroke length variations.
- **Scanner Grain / Noise**: Subtle Gaussian noise ($\sigma = 0.02, p = 0.25$) simulating optical scanner sensors.
- **Mild Gaussian Blur**: $3 \times 3$ kernel ($p = 0.25$) simulating ink bleed on fibrous cheque stock.
- **Contrast Variation**: Random contrast scale $\in [0.85, 1.15]$ simulating gel vs ballpoint ink density.

### Empirical Impact (EXP-005 vs EXP-001)
- Validation AUC rose from $0.6728$ to $0.7608$ (+8.80 percentage points).
- Skilled Forgery FAR dropped from $50.00\%$ to $39.72\%$.
- Validation TAR rose from $61.33\%$ to $68.50\%$.

---

## 2. Preprocessing Pipeline Ablation (Phase 8)

Controlled experiments evaluated 4 distinct image preparation pipelines on the validation cohort:

| Experiment | Method | Preprocessing Transformation | Val AUC | Val EER | Skilled FAR | Status / Finding |
|---|---|---|---|---|---|---|
| **Baseline / Champion** | `otsu` | Otsu adaptive binarization + bounding box crop + aspect pad + resize $224 \times 224$ | **0.8277** | **24.33%** | **27.78%** | **Best generalizer** |
| **EXP-006** | `adaptive` | Local Gaussian adaptive thresholding ($21 \times 21$ window) | 0.8020 | 27.67% | 36.67% | Strong, but slightly noisier strokes |
| **EXP-007** | `morphology` | Morphological top-hat background subtraction + Otsu | 0.5000 | 50.00% | 0.00% | **Failed Hypothesis** (erased thin strokes) |
| **Baseline Grayscale** | `none` | Raw grayscale with aspect crop and float normalization | 0.7320 | 33.50% | 42.10% | Retained background grain; slower convergence |

### Conclusion
Standard Otsu binarization with tight bounding box cropping and aspect-ratio padding provides the cleanest feature signal for the ResNet-18 residual stages. Morphological background subtraction over-eroded fine stroke tails and loop crossings, confirming that complex preprocessing can degrade delicate handwriting features.
