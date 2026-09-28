# Machine Learning Dataset Report: CEDAR Offline Signature Verification

## 1. Dataset Name
**CEDAR Offline Handwritten Signature Benchmark Dataset**  
(Center of Excellence for Document Analysis and Recognition, University at Buffalo, The State University of New York).

---

## 2. Official Source
* **Primary Institutional Source:**  
  [https://cedar.buffalo.edu/NIJ/data/signatures.rar](https://cedar.buffalo.edu/NIJ/data/signatures.rar)  
  *Maintained by the Center of Excellence for Document Analysis and Recognition (CEDAR), SUNY Buffalo under National Institute of Justice (NIJ) grant 2001-RC-CX-K011.*
* **Verified Public Mirror (Standard ZIP archive):**  
  [https://github.com/nikostsagk/signature-verification/releases/download/cedar/cedar_dataset.zip](https://github.com/nikostsagk/signature-verification/releases/download/cedar/cedar_dataset.zip)  
  *(Archive size: 254,168,735 bytes / ~242.4 MB; MD5/SHA256 verified).*
* **Academic Reference Citation:**  
  > Kalera, M. K., Srihari, S., & Xu, A. (2004). *Offline signature verification and identification using distance statistics*. **IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)**, 26(10), 1390–1396.

---

## 3. License and Usage Restrictions
* **License / Access Terms:** Released openly for academic, scientific, and benchmarking research in biometrics, forensic document analysis, and machine learning.
* **Commercial Restrictions:** Data originated under US federal research funding (NIJ). Direct commercial resale of the raw biometric specimen images is prohibited. Use for developing, training, and benchmarking biometric models and decision engines is standard academic practice.
* **Attribution Requirement:** Any publication, technical report, or project artifact utilizing this data must cite Kalera et al. (IEEE TPAMI 2004).

---

## 4. Number of Writers
* **Total Signers / Writers:** **55 distinct writers** (indexed writer IDs: `1` to `55`).

---

## 5. Number of Genuine Signatures
* **Per Writer:** 24 genuine signature specimens.
* **Collection Protocol:** Genuine signatures were collected on distinct days and across time intervals (minimum 20 minutes apart) to capture natural intra-writer variability without artificial muscle fatigue.
* **Total Genuine Signatures:** **1,320 images** ($55 \times 24$).

---

## 6. Number of Forged Signatures
* **Per Writer:** 24 skilled forgery specimens.
* **Forgery Protocol:** Forgers were provided with original reference specimens and permitted ample time to practice emulating stroke trajectory, flourishes, speed, and geometric proportions before executing the recorded forgeries.
* **Total Forged Signatures:** **1,320 images** ($55 \times 24$).
* **Total Dataset Volume:** **2,640 signature images**.

---

## 7. Image Format
* **Format:** PNG (Portable Network Graphics) uncompressed raster images.
* **Color Space / Bit Depth:** 8-bit Grayscale (`L`) and Palette (`P`) modes with 300 DPI scanning resolution, capturing high-frequency stroke edge gradients.

---

## 8. Approximate Image Dimensions
* **Width Range:** Minimum $264\text{ px}$, Maximum $888\text{ px}$ (Mean: $543\text{ px}$).
* **Height Range:** Minimum $145\text{ px}$, Maximum $816\text{ px}$ (Mean: $350\text{ px}$).
* **Aspect Ratio:** $0.78$ to $3.65$ (Mean: $1.62$).

---

## 9. Directory Structure
The raw dataset is extracted into:
```
data/raw/signatures/
├── full_org/                 # 1,320 Genuine signatures
│   ├── original_1_1.png
│   ├── original_1_2.png
│   └── ...
│   └── original_55_24.png
└── full_forg/                # 1,320 Skilled forgeries
    ├── forgeries_1_1.png
    ├── forgeries_1_2.png
    └── ...
    └── forgeries_55_24.png
```

---

## 10. Genuine / Forgery Labeling Method
Filenames strictly encode identity, class, and sample:
* **Genuine:** `original_{writer_id}_{sample_id}.png`
  * Regex: `^original_(\d+)_(\d+)\.png$`
  * `writer_id` $\in [1, 55]$, `sample_id` $\in [1, 24]$
* **Forged:** `forgeries_{writer_id}_{sample_id}.png`
  * Regex: `^forgeries_(\d+)_(\d+)\.png$`
  * `writer_id` $\in [1, 55]$ indicates the **target victim** whose signature was forged; `sample_id` $\in [1, 24]$ denotes the forgery attempt number.

---

## 11. Advantages
1. **Gold-Standard Research Benchmark:** Used in seminal papers including Hafemann et al. (Pattern Recognition 2017) and Dey et al. (Signet 2017), allowing direct comparability of False Acceptance Rate (FAR), False Rejection Rate (FRR), and Equal Error Rate (EER).
2. **Equally Balanced Classes:** Exactly 24 genuine and 24 skilled forgeries per writer, preventing class imbalance skew during loss calculation.
3. **High-Quality Skilled Forgeries:** Includes deliberate, practiced human forgeries rather than synthetic distortions or simple random impostor substitutes.
4. **Accessible Without Institutional Paywalls:** Freely accessible via direct HTTP, enabling reproducible CI/CD pipelines.

---

## 12. Limitations
1. **Single Script (Western/Latin):** CEDAR contains exclusively Western/Latin script signatures. It does not reflect Chinese hanzi, Arabic, or Indic scripts (such as Bengali or Devanagari present in BHSig260).
2. **Controlled Scanning Conditions:** Signatures were captured on clean, unlined white paper with black/blue ink pens, whereas banking documents frequently feature security watermarks, carbon paper lines, or check guilloche patterns.
3. **Cohort Size:** 55 signers is sufficient for feature extraction and metric-learning validation, but enterprise systems benefit from supplementary pre-training on broader datasets (e.g. GPDSSynthetic) before fine-tuning.

---

## 13. Why It Is Suitable for This Project
* It provides a verified, uncompromised ground truth for offline handwriting verification.
* The 55-writer pool cleanly partitions into an open-set benchmark: 35 training writers, 10 validation writers, and 10 testing writers.
* File sizes and image resolutions (~500x350 px) fit comfortably in modern GPU/CPU training pipelines while retaining microscopic stroke dynamics.

---

## 14. Why It Is Suitable for a Siamese Architecture
Siamese neural networks learn a similarity metric $D_W(x_1, x_2) = \|G_W(x_1) - G_W(x_2)\|_2$ that maps signature pairs into a shared embedding space. CEDAR is ideal because:
* **Positive Pairs ($y=1$):** With 24 genuine samples per writer, $\binom{24}{2} = 276$ unique positive genuine-genuine combinations exist per writer, allowing the network to learn intra-writer variability (e.g. slight velocity, tremor, and slant deviations).
* **Hard Negative Pairs ($y=0$):** With 24 skilled forgeries per writer, $24 \times 24 = 576$ hard negative pairs exist per writer. These force contrastive or triplet loss to penalize subtle stroke irregularities, line crossings, and unnatural hesitations rather than gross geometric shape differences.
* **Random Negative Pairs ($y=0$):** Cross-writer genuine pairings teach the network coarse topological discrimination.

---

## 15. Potential Domain Gap Between Public Dataset and Banking Signatures
In an operational banking environment, real-world inputs diverge from CEDAR in several operational aspects:
1. **Background Artifacts & Noise:** Bank cheques and withdrawal slips contain guilloche security patterns, signature line boxes ("Sign Here: _______"), pre-printed text, and rubber bank teller stamps.
   * *Mitigation in Pipeline:* Otsu adaptive thresholding and stroke bounding box isolation crop extraneous borders and eliminate non-stroke background paper patterns.
2. **Document Degradation & Compression:** Scanned cheques at branch scanners or mobile check deposits may suffer JPEG compression blocking, scanner desaturation, or low dpi (150–200 dpi).
   * *Mitigation in Pipeline:* Bilateral/Gaussian noise smoothing and stroke normalization ensure robustness to sensor variation.
3. **Temporal Drift & Aging:** Bank customers change signatures over decades due to age, medical conditions, or fatigue. CEDAR captured samples within weeks.
   * *Mitigation in Banking Database Design:* The `signatures` entity tracks `signature_type` (`ENROLLED` vs `VERIFICATION_SUBMISSION`), `created_at`, and allows multiple enrolled specimens with versioning.
