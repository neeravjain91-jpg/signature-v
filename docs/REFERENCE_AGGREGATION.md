# MULTI-SAMPLE REFERENCE AGGREGATION & TTA
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Phase 13 & 14: Multi-Specimen Banking Gallery & Inference Dynamics*
*Date: September 28, 2026 | Environment: Python 3.11.9, PyTorch 2.13.0+cpu*

---

## 1. Multi-Sample Reference Aggregation (Phase 13)

In retail banking workflows, customer signature card agreements often contain multiple legitimate signature specimens (e.g. 3 enrolled specimens). Rather than verifying a questioned cheque against a single arbitrary reference image, multi-specimen gallery inference leverages the full spectrum of customer handwriting variability.

### Aggregation Strategies Tested on Validation Cohort (Writers 36–45)
Five strategies were evaluated using the frozen Champion model across 1,200 questioned validation signatures against 3 enrolled customer reference signatures:

| Aggregation Strategy | Mathematical Formulation | Val AUC | Val EER | Skilled FAR | Val TAR | Operational Recommendation |
|---|---|---|---|---|---|---|
| **Max Similarity (`max`)** | $S_{\text{final}} = \max_i S(q, r_i)$ | **0.8963** | **17.17%** | **15.83%** | **83.00%** | **RECOMMENDED FOR BANKING DEPLOYMENT** |
| **Centroid Embedding (`centroid`)**| $S_{\text{final}} = S(q, \text{norm}(\sum_i r_i))$ | 0.8839 | 20.50% | 24.44% | 79.17% | Strong alternative |
| **Top-$k$ Mean (`top_k`, $k=2$)** | $S_{\text{final}} = \frac{1}{2} \sum_{i=1}^2 S_{(i)}$ | 0.8822 | 20.83% | 25.00% | 79.00% | Robust to 1 corrupted specimen |
| **Arithmetic Mean (`mean`)** | $S_{\text{final}} = \frac{1}{K} \sum_i S(q, r_i)$ | 0.8691 | 23.50% | 28.61% | 76.50% | Traditional baseline |
| **Median (`median`)** | $S_{\text{final}} = \text{median}_i S(q, r_i)$ | 0.8622 | 22.50% | 26.94% | 77.83% | Robust outlier rejection |

### Key Banking Impact
1. **Dramatic Skilled FAR Reduction**: When comparing against a 3-specimen gallery using `max` similarity, the **Skilled Forgery False Acceptance Rate plummets to 15.83%** (down from $27.78\%$ in single-reference mode, and down from $50.00\%$ in baseline).
2. **True Acceptance Expansion**: Customer clearance rate reaches **$83.00\%$**, resolving teller false alarm concerns while maintaining strong fraud security.

---

## 2. Test-Time Augmentation (TTA) Evaluation (Phase 14)

TTA was evaluated by averaging embeddings across the raw questioned image plus 2 micro-transformed variants ($\pm 2^\circ$ rotation, $\pm 2$ px shift):
- **Single-Pass Inference**: Val AUC = 0.8277, Val EER = 24.33%, Skilled FAR = 27.78%, Latency = **6.84 ms**
- **3-Pass TTA Inference**: Val AUC = 0.8302, Val EER = 24.50%, Skilled FAR = 28.33%, Latency = **20.52 ms**

### Conclusion on TTA
TTA provides negligible metric difference (+0.0025 AUC) at the expense of a 3x increase in inference computation time. Consequently, **single-pass inference is retained for real-time banking transactions**, reserving multi-pass verification exclusively for compliance manual review escalations.
