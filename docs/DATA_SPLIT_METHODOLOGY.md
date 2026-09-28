# Data Split Methodology & Anti-Leakage Protocol

## 1. Executive Summary

In biometrics and automated handwriting verification for banking, evaluation integrity hinges on the split design. Randomly shuffling signature images across splits—a common mistake in student and naive ML projects—causes **catastrophic identity leakage**. 

This system enforces a **Writer-Independent (Open-Set)** partitioning protocol across all training, validation, and testing workflows.

---

## 2. Writer-Dependent vs. Writer-Independent Evaluation

### Writer-Dependent (Closed-Set) — Why It Fails in Banking
* In a writer-dependent setting, samples from every person are distributed across train, validation, and test sets.
* The neural network memorizes individual writer characteristics (specific letter connections, specific name spellings, individual stylistic flourishes).
* **Why this is unacceptable in banking:** A retail bank constantly onboards new customers. When customer "Jane Doe" opens an account today, the deployed Siamese network has never seen Jane Doe's signature during training. A system evaluated only writer-dependently exhibits drastically degraded performance (often dropping from >95% to <65% accuracy) when confronted with unseen signers.

### Writer-Independent (Open-Set) — The Banking Standard
* The network is trained on writer cohort $\mathcal{W}_{\text{train}}$, tuned on disjoint cohort $\mathcal{W}_{\text{val}}$, and evaluated on unseen cohort $\mathcal{W}_{\text{test}}$.
* The model cannot memorize names or specific writer handwriting. Instead, it must learn **domain-general metric invariants**: stroke consistency, line curvature, acceleration profiles, pen lifts, and micro-tremors characteristic of hesitation.
* This mirrors true banking operations: zero prior knowledge of newly enrolled customer signatures.

---

## 3. Strict Cohort Partitioning

The 55 writers in the CEDAR dataset are partitioned deterministically as follows:

| Split Role | Writer ID Range | Number of Writers | Percentage | Genuine Samples | Forged Samples | Total Images |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Train Set** | Writers `1` through `35` | 35 | 63.6% | 840 | 840 | 1,680 |
| **Validation Set** | Writers `36` through `45` | 10 | 18.2% | 240 | 240 | 480 |
| **Test Set** | Writers `46` through `55` | 10 | 18.2% | 240 | 240 | 480 |
| **Total** | Writers `1` through `55` | 55 | 100.0% | 1,320 | 1,320 | 2,640 |

### Mathematical Proof of Disjointness
$$\mathcal{W}_{\text{train}} \cap \mathcal{W}_{\text{val}} = \emptyset$$
$$\mathcal{W}_{\text{train}} \cap \mathcal{W}_{\text{test}} = \emptyset$$
$$\mathcal{W}_{\text{val}} \cap \mathcal{W}_{\text{test}} = \emptyset$$
$$\mathcal{W}_{\text{train}} \cup \mathcal{W}_{\text{val}} \cup \mathcal{W}_{\text{test}} = \{1, 2, \dots, 55\}$$

This guarantees that:
1. No signature image from a test writer appears in the training or validation splits.
2. No pair constructed in the test set contains any image or writer identity present in the training set.

---

## 4. Pair Generation Methodology

Siamese architectures require paired inputs $(x_1, x_2)$ with binary ground truth $y \in \{0, 1\}$. Pairs are constructed **strictly within each partition**.

### A. Positive Pairs ($y = 1$: Same Signer)
* **Definition:** A pair of distinct genuine signatures $(g_i^{(a)}, g_i^{(b)})$ belonging to the same signer $i$ where $a \neq b$.
* **Objective:** Teaches the network intra-writer invariance (tolerance for natural variations in signing angle, speed, and size).
* **Generation:** Combinations $\binom{24}{2} = 276$ per writer. A uniform random subsample (100 pairs per writer for train, 60 pairs per writer for validation/test) is sampled using random seed `42`.

### B. Skilled Negative Pairs ($y = 0$: Skilled Forgery Impostor)
* **Definition:** A genuine signature paired with a skilled forgery targeting that exact signer: $(g_i^{(a)}, f_i^{(k)})$.
* **Objective:** Critical for fraud detection. Skilled forgers replicate the general shape and name of the victim. This forces the model to attend to high-frequency stroke details (pen-stops, tremor, line crossing speed, stroke thickness fluctuations) rather than overall name geometry.
* **Allocation:** Constitutes 60% of all generated negative pairs.

### C. Random Negative Pairs ($y = 0$: Cross-Writer Impostor)
* **Definition:** A genuine signature of writer $i$ paired with a genuine signature of writer $j$, where $i \neq j$ and both $i, j$ reside within the same split partition.
* **Objective:** Simulates random banking fraud (e.g. an impostor signing their own name or an unrelated scribble on a victim's stolen cheque).
* **Allocation:** Constitutes 40% of all generated negative pairs.

---

## 5. Pair Summary & Class Balance

By aligning positive and negative pairs 1:1, the dataset avoids decision threshold bias:

```
Train Split:
  - 3,500 Positive Pairs (Genuine-Genuine)
  - 3,500 Negative Pairs (2,100 Skilled Forgery + 1,400 Random Impostor)
  - Class Ratio = 1.00 (Balanced)

Validation Split:
  - 600 Positive Pairs
  - 600 Negative Pairs (360 Skilled Forgery + 240 Random Impostor)
  - Class Ratio = 1.00 (Balanced)

Test Split:
  - 600 Positive Pairs
  - 600 Negative Pairs (360 Skilled Forgery + 240 Random Impostor)
  - Class Ratio = 1.00 (Balanced)
```

---

## 6. Verification and Reproducibility

* **Deterministic Random Seed:** All subsampling, pair shuffling, and cross-writer selections use `seed = 42`.
* **Manifest Verification:** The exact split manifest is recorded in `data/metadata/split_manifest.json` and generated pair indices are preserved in `data/pairs/{train,validation,test}_pairs.csv`.
* **Zero Leakage Assertion:** Validated via automated unit and integration tests (`tests/test_traceability.py` and pair integrity checks).
