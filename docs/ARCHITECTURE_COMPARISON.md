# ARCHITECTURE COMPARISON REPORT (PHASE 3)

## Architectural Candidates
We systematically implemented and benchmarked three distinct Siamese network backbones across all 5 writer-disjoint development folds (Writers 1–45):

1. **Architecture A: Siamese ResNet-18 Baseline**
   - Modified ResNet-18 with 1-channel stem, residual skip connections, and a 256-D hyperspherical projection head.
   - Parameters: $11,302,080$ ($43.1\text{ MB}$).
   - Inference latency: $6.84\text{ ms}$ on CPU.

2. **Architecture B: STN + Siamese ResNet-18**
   - Adds an affine Spatial Transformer Network (STN) front-end that learns to canonicalize signature tilt, translation, and scale before feeding into the CNN.
   - Parameters: $11,349,030$ ($43.3\text{ MB}$).
   - Inference latency: $7.45\text{ ms}$ on CPU.

3. **Architecture C: Hybrid CNN + Lightweight Transformer**
   - 4-layer convolutional stem capturing local stroke strokelets followed by 2 Multi-Head Self-Attention layers ($d=128$, 4 heads) capturing global stroke dependencies, global average pooling, and a 256-D linear projection.
   - Parameters: $417,216$ ($1.6\text{ MB}$).
   - Inference latency: $2.85\text{ ms}$ on CPU.

---

## 5-Fold Development Cross-Validation Benchmark

| Architecture | Mean Skilled FAR | Mean Overall FAR | Mean TAR | Mean ROC-AUC | Parameters | Latency (CPU) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ResNet-18 (Arch A)** | **$37.35\% \pm 5.18\%$** | **$23.78\% \pm 2.92\%$** | **$76.26\% \pm 2.92\%$** | **$0.8373 \pm 0.0254$** | $11.3\text{M}$ | $6.84\text{ ms}$ |
| **STN + ResNet-18 (Arch B)** | $37.53\% \pm \mathbf{1.84\%}$ | $25.11\% \pm \mathbf{0.76\%}$ | $74.89\% \pm \mathbf{0.76\%}$ | $0.8308 \pm \mathbf{0.0083}$ | $11.3\text{M}$ | $7.45\text{ ms}$ |
| **CNN + Transformer (Arch C)** | $39.51\% \pm 5.88\%$ | $26.14\% \pm 3.36\%$ | $73.78\% \pm 3.36\%$ | $0.8146 \pm 0.0391$ | **$0.42\text{M}$** | **$2.85\text{ ms}$** |

---

## Architectural Findings
1. **ResNet-18 Residual Depth Advantage**: ResNet-18 achieved the highest biometric verification accuracy and the lowest skilled forgery false acceptance rate ($37.35\%$). Its deep residual blocks effectively capture multi-scale stroke topologies.
2. **STN Invariance**: While STN did not lower the absolute skilled FAR compared to clean Otsu ResNet ($37.53\%$ vs $37.35\%$), it reduced cross-fold standard deviation by over **$64\%$** ($\pm 1.84\%$ vs $\pm 5.18\%$), proving valuable when customer signature angle varies widely.
3. **Lightweight Transformer Efficiency**: The CNN+Transformer model demonstrated incredible computational efficiency ($0.42\text{M}$ parameters, $2.85\text{ ms}$ latency), but suffered a $+2.16\%$ penalty in skilled forgery false acceptance due to the difficulty of training self-attention mechanisms on modest signature cohorts without massive pretraining.
