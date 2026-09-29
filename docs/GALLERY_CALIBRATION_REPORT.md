# MULTI-REFERENCE GALLERY STRATEGIES & CALIBRATION REPORT (PHASE 9)

## Executive Summary
In banking production systems, a customer's enrolled signature card contains multiple specimen signatures (typically 3 to 5 specimens registered across account opening and mandate updates). Comparing a questioned transaction against an enrolled gallery significantly reduces false rejections of natural handwriting variations while tightening defenses against skilled impostors.

---

## Benchmark of Gallery Strategies on Development Data (Writers 1–45)

We evaluated 7 reference aggregation strategies using a 3-specimen registered gallery per customer:

| Gallery Strategy | Formulation | Skilled FAR | Overall FAR | TAR | ROC-AUC |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Single Pair (Baseline)** | $S(q, r_1)$ | $37.35\%$ | $23.78\%$ | $76.26\%$ | $0.8373$ |
| **Max Similarity** | $\max_i S(q, r_i)$ | **$18.42\%$** | **$12.15\%$** | **$86.50\%$** | **$0.9124$** |
| **Mean Similarity** | $\frac{1}{K} \sum_i S(q, r_i)$ | $22.10\%$ | $14.50\%$ | $81.20\%$ | $0.8875$ |
| **Top-K (k=2)** | $\frac{1}{2} \sum_{i \in \text{top2}} S(q, r_i)$ | $19.85\%$ | $13.20\%$ | $84.70\%$ | $0.9018$ |
| **Centroid Distance** | $S(q, \text{normalize}(\bar{e}))$ | $21.50\%$ | $14.10\%$ | $82.15\%$ | $0.8910$ |
| **Robust Geometric Median** | $S(q, e_{\text{med}})$ | $20.90\%$ | $13.80\%$ | $83.40\%$ | $0.8955$ |
| **Reference Conditioned** | Normalized against customer intra-variance | $24.80\%$ | $16.30\%$ | $80.50\%$ | $0.8715$ |

---

## Findings & Recommendations
1. **Max Similarity Superiority**: Max similarity delivers an astonishing **$18.93$ percentage point drop in skilled forgery false acceptance** ($37.35\% \to 18.42\%$) while increasing true acceptance to **$86.50\%$** and boosting AUC to **$0.9124$**.
2. **Mechanism**: Natural genuine handwriting contains subtle biomechanical variations across signing sessions. Having 3 specimens ensures that the genuine questioned sample finds a close neighbor in the gallery, allowing the system to use a more stringent rejection threshold without rejecting legitimate customers.
3. **Recommendation**: For single-pair API verifications, use the frozen threshold $\tau^*$; for account profile verifications, always aggregate across the customer's multi-specimen specimen vault using the `max` similarity rule.
