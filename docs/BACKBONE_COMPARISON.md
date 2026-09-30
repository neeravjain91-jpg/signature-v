# BACKBONE ARCHITECTURE & EMBEDDING DIMENSION ABLATION
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Phase 9 & 10: Neural Backbone & Feature Vector Dimension Exploration*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Backbone Architecture Comparison (Phase 9)

Evaluated under identical training protocols and contrastive objectives:

| Backbone Model | Architecture Details | Parameters | Model Size | Val AUC | Val EER | Skilled FAR | Latency (CPU) |
|---|---|---|---|---|---|---|---|
| **Custom CNN** | 4-Stage Conv-BN-ReLU without residual connections | 412,416 | 1.57 MB | 0.7784 | 30.83% | 43.61% | **3.25 ms** |
| **ResNet-18 (Champion)** | 4-Stage Residual Blocks + Projection Head | 5,276,640 | 20.13 MB | **0.8277** | **24.33%** | **27.78%** | **6.84 ms** |
| **ResNet-18 Pretrained** | Torchvision ImageNet weights adapted to 1-ch | 11,438,912 | 43.64 MB | 0.8115 | 26.50% | 34.17% | 12.40 ms |

### Architectural Insights
- **Custom CNN**: Highly lightweight and fast (3.25 ms latency), but lacked sufficient representational depth to discriminate skilled forgeries from genuine signatures (Skilled FAR remained high at 43.61%).
- **ResNet-18**: The residual skip connections preserve high-frequency stroke edge features across downsampling stages, yielding superior boundary sensitivity on skilled imitations while maintaining sub-7ms latency.
- **Pretrained Weights**: Natural image ImageNet filters (textures, dogs, cars) do not transfer perfectly to binary handwritten stroke skeletons without extensive domain adaptation, performing slightly below the natively trained ResNet-18.

---

## 2. Embedding Dimension Ablation (Phase 10)

Keeping the ResNet-18 backbone constant, the metric projection head dimension was varied:

| Dimension $d$ | Hypersphere $\mathbb{S}^{d-1}$ | Parameter Count | Val AUC | Val EER | Skilled FAR | Hardware Impact |
|---|---|---|---|---|---|---|
| **$d = 128$** | $\mathbb{S}^{127}$ | 5,210,880 | 0.7156 | 35.33% | 45.00% | Lowest vector memory footprint |
| **$d = 256$ (Champion)**| **$\mathbb{S}^{255}$** | **5,276,640** | **0.8277** | **24.33%** | **27.78%** | **Optimal discrimination & speed** |
| **$d = 512$** | $\mathbb{S}^{511}$ | 5,408,160 | 0.7251 | 32.83% | 41.94% | Slight over-parameterization on small splits |

### Conclusion
$d = 256$ provides the ideal mathematical capacity for handwritten stroke dynamics on $\mathbb{S}^{255}$, balancing geometric expressive power with compact storage (1,024 bytes per vector).
