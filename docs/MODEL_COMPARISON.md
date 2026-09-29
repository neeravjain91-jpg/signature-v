# SIGNATURE VMAKE — Multi-Model Track Comparative Analysis & Selection Report

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Evaluation Protocol:** Open-Set (Writer-Independent) on Validation Partition (Writers 36..45)  
**Artifact:** `artifacts/evaluation/three_track_benchmark_results.json`  

---

## 1. Executive Summary & Scientific Purpose

The core principle of SIGNATURE VMAKE is **empirical verification over architectural bias**. Rather than blindly deploying a Vision Transformer or assuming a deep neural network is universally superior, the platform implements, trains, and validates **three distinct technological tracks**:

1. **Track A (Classical Machine Learning):** scikit-learn Support Vector Machine with 264-d handcrafted HOG, projection, and morphological features.
2. **Track B (Computer Vision Transformer):** Hugging Face Vision Transformer (`facebook/deit-tiny-patch16-224`) with multi-head self-attention and metric projection head.
3. **Track C (Deep Siamese Neural Network):** Twin ResNet backbone with L2-normalized metric learning hypersphere embeddings.

---

## 2. Quantitative Benchmark Results

All three models were evaluated under identical conditions on 400 validation pairs drawn from the disjoint validation cohort (Writers `36` to `45`):

| Evaluation Metric | Track A: Classical Sklearn (SVM) | Track B: HF Vision Transformer (ViT) | Track C: Siamese ResNet (Metric Learning) | Scientific Winner |
| :--- | :---: | :---: | :---: | :---: |
| **Area Under ROC (AUC-ROC)** | $0.8423$ | $0.8118$ | **$0.9008$** | **Track C (+0.0585)** |
| **Equal Error Rate (EER)** | $23.00\%$ ($0.2300$) | $24.50\%$ ($0.2450$) | **$18.74\%$ ($0.1874$)** | **Track C (-4.26%)** |
| **Validation Accuracy** | $76.75\%$ | $75.50\%$ | **$81.50\%$** | **Track C (+4.75%)** |
| **False Acceptance Rate (FAR)** | $23.04\%$ | $24.51\%$ | **$19.12\%$** | **Track C (-3.92%)** |
| **False Rejection Rate (FRR)** | $23.47\%$ | $24.49\%$ | **$17.86\%$** | **Track C (-5.61%)** |
| **True Acceptance Rate (TAR)** | $76.53\%$ | $75.51\%$ | **$82.14\%$** | **Track C (+5.61%)** |
| **F1 Score** | $0.7634$ | $0.7513$ | **$0.8131$** | **Track C (+0.0497)** |
| **Inference Latency (CPU)** | **$7.3\text{ ms}$** | $38.4\text{ ms}$ | $42.1\text{ ms}$ | **Track A (5.7x faster)** |
| **Model Disk Footprint** | **$5.4\text{ MB}$** | $21.7\text{ MB}$ | $43.2\text{ MB}$ | **Track A (8x smaller)** |

---

## 3. Explicit Model Selection Criteria

In accordance with strict banking risk standards, the production model is selected via a deterministic, multi-criterion hierarchy:

1. **Criterion 1 (Primary): Lowest False Acceptance Rate (FAR):** In high-value banking (cheques, counter withdrawals, high-value wire transfers), accepting a fraudulent forged signature costs orders of magnitude more than manual review escalation. Track C achieves the lowest FAR ($19.12\%$).
2. **Criterion 2: Highest Area Under the Curve (AUC-ROC):** Track C leads with $\text{AUC} = 0.9008$, proving superior class separability across all possible operating thresholds.
3. **Criterion 3: Lowest Equal Error Rate (EER):** Track C achieves an EER of $18.74\%$, surpassing both the Classical Baseline ($23.00\%$) and the Vision Transformer ($24.50\%$).
4. **Criterion 4: Acceptable Operational Latency:** The production SLA requires transaction response times under $200\text{ ms}$. Track C executes in $42.1\text{ ms}$ on CPU, well within banking performance requirements.

### Final Production Champion Selection
$$\textbf{Selected Production Model:} \quad \text{Model Track C (Siamese ResNet Champion)}$$

---

## 4. Deep Architectural Insights

### Why the Vision Transformer did not outperform the Siamese ResNet
* **Inductive Bias:** Vision Transformers lack translation equivariance and local spatial inductive bias. Handwriting analysis relies heavily on micro-stroke continuity, pen-stop hesitation, and curvature gradients across small spatial neighborhoods.
* **Data Scale:** ViT architectures excel when trained on tens of millions of samples (e.g. ImageNet-21k, JFT-300M). On smaller forensic datasets (CEDAR: 2,640 images), convolutional networks preserve local stroke topology much more effectively.

### The Value of the Classical scikit-learn Baseline
* Track A demonstrates remarkable performance ($\text{AUC} = 0.8423$, Accuracy $76.75\%$) with near-zero latency ($7.3\text{ ms}$) and tiny memory overhead ($5.4\text{ MB}$).
* It proves that engineered directional gradients (Sobel HOG) and projection profiles capture strong geometric discriminability, providing an ultra-lightweight fallback for edge or offline mobile devices.
