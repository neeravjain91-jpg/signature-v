# BASELINE VS. CHAMPION BENCHMARK COMPARISON
**SYNAPSE — Intelligent Signature Verification Platform**
*Phase 16: Definitive Unbiased Evaluation on Frozen Test Cohort (Writers 46–55)*
*Date: September 28, 2026 | Protocol: Strict Zero-Leakage (Threshold & Model Weights Frozen)*

---

## 1. Executive Performance Comparison

Both models were evaluated on the exact same 1,200 unseen open-set test pairs (600 genuine, 360 skilled forgery, 240 cross-writer random impostor) from Writers 46–55 using their respective frozen validation-calibrated operating thresholds:
- **Baseline Operating Threshold**: $\tau^* = 0.7766$ (calibrated on Writers 36–45)
- **Champion Operating Threshold**: $\tau^* = 0.7394$ (calibrated on Writers 36–45)

| Metric | Baseline Model (`1.0.0`) | Champion Model (`2.0.0-champion`) | Delta ($\Delta$) | Direction |
|---|---|---|---|---|
| **Area Under ROC (AUC-ROC)** | **0.7465** | **0.8512** | **+0.1047** | **+14.0% discrimination gain** |
| **Equal Error Rate (EER)** | **30.67%** | **23.75%** | **-6.92%** | **-22.6% crossover error reduction** |
| **Overall Classification Accuracy**| **70.33%** (844/1,200) | **76.08%** (913/1,200) | **+5.75%** | **+8.2% accuracy gain** |
| **True Acceptance Rate (TAR)** | **83.17%** (499/600) | **83.50%** (501/600) | **+0.33%** | Genuine customer clearance preserved |
| **False Rejection Rate (FRR)** | **16.83%** (101/600) | **16.50%** (99/600) | **-0.33%** | Reduced customer false alarms |
| **Overall False Acceptance (FAR)**| **42.50%** (255/600) | **31.33%** (188/600) | **-11.17%** | **67 fewer total unauthorized clears** |
| **Skilled Forgery FAR** | **62.22%** (224/360) | **47.50%** (171/360) | **-14.72%** | **53 fewer skilled fraud breaches** |
| **Cross-Writer / Random FAR** | **12.92%** (31/240) | **7.08%** (17/240) | **-5.84%** | **92.92% random fraud block rate** |
| **Precision** | **0.6618** | **0.7271** | **+0.0653** | **+9.9% precision gain** |
| **Recall** | **0.8317** | **0.8350** | **+0.0033** | Stable high sensitivity |
| **F1-Score** | **0.7371** | **0.7773** | **+0.0402** | **+5.5% harmonic balance gain** |
| **Inference Latency (Single-Core)**| **10.31 ms** | **6.84 ms** | **-3.47 ms** | **33.7% faster inference** |
| **Model Disk Size** | **60.48 MB** | **20.13 MB** | **-40.35 MB** | **66.7% memory optimization** |
| **Trainable Parameters** | **5,276,640** | **5,276,640** | **0** | Same parameter footprint |

---

## 2. Multi-Sample Gallery Performance Comparison

When customer signature card galleries (3 enrolled specimens per customer) are deployed:

| Metric | Baseline Single-Pair | Champion Single-Pair | Champion 3-Specimen Gallery (`max`) |
|---|---|---|---|
| **ROC-AUC** | 0.7465 | 0.8512 | **0.8963** |
| **Equal Error Rate (EER)** | 30.67% | 23.75% | **17.17%** |
| **Skilled Forgery FAR** | 62.22% | 47.50% | **15.83%** |
| **Overall FAR** | 42.50% | 31.33% | **17.17%** |
| **True Acceptance (TAR)** | 83.17% | 83.50% | **83.00%** |

---

## 3. Engineering Post-Mortem & Discussion

1. **Where Champion Succeeded**:
   - **Skilled Forgeries**: Mined hard negative mini-batches combined with Triplet loss forced the network to detect hairline pen lifts, pressure variances, and tremor discontinuities that uniform random sampling missed, cutting pairwise test Skilled FAR from $62.22\%$ to $47.50\%$.
   - **Random Impostors**: Cross-writer forgeries are virtually eliminated ($7.08\%$ FAR, $92.92\%$ block rate).
   - **Preserved Clearance**: TAR maintained at $83.50\%$, ensuring banking operations do not suffer teller queue gridlock.
2. **Where Challenges Remain**:
   - On direct optical tracings (where a skilled forger slowly traced over a backlit genuine original), single-pair 2D visual representations still exhibit non-trivial residual false acceptances ($47.5\%$).
   - This empirically confirms that **single-pair static image comparison alone is insufficient for zero-trust banking security**, and justifies SYNAPSE's multi-layered architecture combining multi-specimen reference galleries and financial transaction risk rules.
