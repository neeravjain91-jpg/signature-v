# MULTI-VIEW INPUT ANALYSIS (PHASE 4)

## Overview
We investigated whether augmenting the input representation with complementary visual channels improves handwriting authentication and skilled forgery discrimination:

1. **Single-View (1-Channel)**:
   - Clean Otsu binarization with bounding box crop and aspect-ratio padding ($224 \times 224$).
2. **Two-View (2-Channel)**:
   - Channel 0: Inverted normalized grayscale (capturing pen pressure variations, ballpoint ink accumulation, and stroke density).
   - Channel 1: Otsu binarization (capturing pure stroke geometry).
3. **Three-View (3-Channel)**:
   - Channel 0: Inverted normalized grayscale.
   - Channel 1: Otsu binarization.
   - Channel 2: Sobel gradient magnitude edge representation (capturing stroke perimeter curvature and micro-hesitations).

---

## 5-Fold Development Cross-Validation Results

| Input Modality | Mean Skilled FAR | Mean Overall FAR | Mean TAR | Mean ROC-AUC | Mean EER |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Single-View (Otsu Binary)** | **$37.35\% \pm 5.18\%$** | **$23.78\% \pm 2.92\%$** | **$76.26\% \pm 2.92\%$** | **$0.8373 \pm 0.0254$** | **$23.78\%$** |
| **Two-View (Gray + Otsu)** | $39.81\% \pm 4.45\%$ | $27.12\% \pm 2.80\%$ | $72.88\% \pm 2.80\%$ | $0.8012 \pm 0.0210$ | $27.12\%$ |
| **Three-View (Gray + Otsu + Edge)**| $41.60\% \pm 5.89\%$ | $29.74\% \pm 3.11\%$ | $70.48\% \pm 3.11\%$ | $0.7832 \pm 0.0311$ | $29.74\%$ |

---

## Key Findings & Engineering Decision
1. **Grayscale Sensor Artifacts**: Adding raw grayscale introduced non-biometric noise (scanner flatbed illumination non-uniformities, paper fiber texture, and ink bleed). Because skilled forgeries are often created with different pen models than genuine specimens, the network overfit to pen ink characteristics rather than handwriting motion geometry.
2. **Sobel Edge Redundancy**: Sobel edge maps amplified paper grain boundary noise without adding structural information beyond the binary stroke perimeter.
3. **Decision**: Retain **Single-View Otsu Binarization** as the primary visual pipeline. It provides clean, invariant stroke geometry that maximizes skilled forgery separation.
