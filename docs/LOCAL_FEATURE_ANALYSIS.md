# LOCAL & PART-BASED FEATURE ANALYSIS (PHASE 8)

## Overview
Skilled forgers frequently reproduce the holistic, global shape of a signature successfully, but fail on local micro-details (e.g., initial stroke attack angles, loop intersection curvature, and terminal flourishing strokes). 

To test whether explicit local part features improve skilled-forgery discrimination, we implemented `SiameseLocalGlobalNet`:
- **Global Feature Branch**: Features pooled across the full feature map ($512 \to 128\text{-D}$).
- **Local Left Branch**: Features pooled from the left half of the spatial feature map ($512 \to 64\text{-D}$), capturing stroke initiation and signature prefix structure.
- **Local Right Branch**: Features pooled from the right half of the spatial feature map ($512 \to 64\text{-D}$), capturing terminal flourishing and punctuation.
- **Fused Embedding**: Concatenation $[v_{\text{global}}, v_{\text{left}}, v_{\text{right}}] \in \mathbb{R}^{256}$ followed by Batch Normalization and $L_2$ hyperspherical projection.

---

## 5-Fold Cross-Validation Empirical Results

| Representation | Mean Skilled FAR | Mean Overall FAR | Mean TAR | Mean ROC-AUC | Mean EER |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Holistic ResNet-18 (Global)** | **$37.35\% \pm 5.18\%$** | **$23.78\% \pm 2.92\%$** | **$76.26\% \pm 2.92\%$** | **$0.8373 \pm 0.0254$** | **$23.78\%$** |
| **Local-Global Part-Based Net** | $40.19\% \pm 3.38\%$ | $26.44\% \pm 2.79\%$ | $73.56\% \pm 2.79\%$ | $0.8167 \pm 0.0278$ | $26.44\%$ |

---

## Forensic Analysis & Limitations
1. **Signature Aspect Ratio & Length Variability**: Signatures vary wildly in horizontal aspect ratio (from short, single-initial stamps to elongated cursive names). Splitting feature maps along fixed vertical spatial coordinates arbitrarily cuts through middle characters, severing connected cursive ligatures.
2. **Receptive Field Overlap**: Because ResNet-18's layer 4 features already possess a large effective receptive field covering significant portions of the input image, global adaptive pooling naturally incorporates local stroke contextual cues without artificial boundary artifacts.
3. **Decision**: The holistic ResNet-18 architecture remains superior to rigid spatial partitioning.
