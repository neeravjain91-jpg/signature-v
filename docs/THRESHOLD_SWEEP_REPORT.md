# THRESHOLD SWEEP VALIDATION REPORT
**SIGNATURE VMAKE — Intelligent Signature Verification Platform**
*Phase 2: Fine-Grained Operating Point Analysis on Validation Cohort*
*Date: September 28, 2026 | Dataset: Validation Cohort (Writers 36–45, 1,200 pairs)*

---

## 1. Executive Summary

A continuous operating threshold sweep was executed across 103 discrete thresholds from $\tau = 0.50$ to $\tau = 0.95$ using `ml/evaluation/threshold_sweep.py`. The resulting trade-off curves are documented in [`docs/VALIDATION_THRESHOLD_SWEEP.csv`](file:///c:/Users/ASUS/Downloads/hcl/docs/VALIDATION_THRESHOLD_SWEEP.csv) and visualized in [`docs/VALIDATION_THRESHOLD_SWEEP.png`](file:///c:/Users/ASUS/Downloads/hcl/docs/VALIDATION_THRESHOLD_SWEEP.png).

### Key Takeaway
**Threshold tuning alone cannot solve skilled forgery vulnerability in a feature-space overlap condition.**
- Lowering threshold improves TAR (customer convenience) but causes unacceptable fraud leakage.
- Raising threshold reduces skilled forgery FAR, but causes immediate catastrophic False Rejection spikes for genuine customers.
- True resolution requires metric space restructuring via **Hard Negative Mining** and **Triplet/Hybrid Regularization**.

---

## 2. Key Operating Points Table

| Operating Regime | Threshold $\tau$ | TAR | FRR | Overall FAR | Skilled Forgery FAR | Random Impostor FAR | Accuracy | F1-Score |
|---|---|---|---|---|---|---|---|---|
| **Ultra-Permissive** | $0.6000$ | 96.67% | 3.33% | 73.17% | 85.83% | 54.17% | 61.75% | 0.7164 |
| **High Clearance** | $0.7000$ | 86.33% | 13.67% | 50.17% | 65.00% | 27.92% | 68.08% | 0.7297 |
| **Optimal EER Point** | **$0.7766$** | **72.33%** | **27.67%** | **27.50%** | **37.78%** | **12.08%** | **72.42%** | **0.7242** |
| **Fraud Conservative** | $0.8200$ | 58.17% | 41.83% | 16.50% | 20.83% | 10.00% | 70.83% | 0.6667 |
| **Extreme Strict** | $0.8500$ | 45.33% | **54.67%** | 10.17% | 12.78% | 6.25% | 67.58% | 0.5824 |
| **Ultra-Strict** | $0.9000$ | 19.33% | **80.67%** | 2.50% | 3.33% | 1.25% | 58.42% | 0.3169 |

---

## 3. Forensic Analysis of Operating Trade-Offs

1. **The Fraud Cliff ($\tau < 0.75$)**:
   - Below $\tau = 0.75$, the Skilled Forgery False Acceptance Rate exceeds $50\%$. The baseline encoder cannot differentiate the macro-scale envelope of genuine vs forged signatures without additional discriminative pressure.
2. **The Clearance Collapse ($\tau > 0.82$)**:
   - As threshold is raised to suppress skilled forgeries, genuine signatures suffer extreme rejections. At $\tau = 0.85$, **more than half (54.67%) of legitimate customers are rejected**, leading to massive teller line bottlenecks and customer dissatisfaction.
3. **The Solution**:
   - Rather than forcing an impossible operational compromise along the baseline ROC curve, the underlying embedding space must be transformed so the genuine and forged score distributions separate physically.
