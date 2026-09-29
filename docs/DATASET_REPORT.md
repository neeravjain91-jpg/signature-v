# SIGNATURE VMAKE — Dataset Evaluation & Benchmark Report

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Domain:** Offline Signature Verification for Banking Transaction Workflows  

---

## 1. Executive Summary & Benchmark Dataset Selection

Offline signature verification requires a benchmark dataset containing authentic human signatures alongside deliberate, skilled forgeries (signers attempting to replicate another's stroke dynamics and trajectory).

To evaluate candidate datasets legitimately without fabricating samples or violating data access agreements, we evaluated four established public datasets:

| Candidate Dataset | Writers | Genuine / Writer | Forged / Writer | Total Images | Script | Licensing & Availability | Suitability Evaluation |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **CEDAR** | **55** | **24** | **24** | **2,640** | **Latin / Western** | Open academic research (SUNY Buffalo / NIJ); direct public mirror available. | **SELECTED BENCHMARK**: Gold-standard, perfectly balanced, verifiable, immediate reproducible acquisition. |
| **GPDS-960 / GPDS-300** | 300–960 | 24 | 30 | 16,200+ | Latin | University of Las Palmas; requires written institutional application and signed DUA. | Valid for extended research; acquisition blocked by institutional credentialing delay. |
| **MCYT-75** | 75 | 15 | 15 | 2,250 | Latin | Universidad Autónoma de Madrid; requires biometric research license application. | High quality; delayed access protocols. |
| **BHSig260** | 260 | 24 | 30 | 14,040 | Bengali & Hindi | Open academic research (IIT Kharagpur); Indic scripts. | Excellent complement for multi-script evaluation; selected CEDAR first for Western banking alignment. |

**Selected Primary Dataset:** The **CEDAR (Center of Excellence for Document Analysis and Recognition)** offline handwritten signature dataset.

---

## 2. Dataset Specifications: CEDAR Benchmark

### 2.1 Origin and Academic Citation
* **Origin:** Center of Excellence for Document Analysis and Recognition, University at Buffalo, The State University of New York (SUNY Buffalo).
* **Funding:** National Institute of Justice (NIJ) grant `2001-RC-CX-K011`.
* **Seminal Citation:**  
  > Kalera, M. K., Srihari, S., & Xu, A. (2004). *Offline signature verification and identification using distance statistics*. **IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)**, 26(10), 1390–1396.

### 2.2 Licensing and Academic Compliance
* **License:** Released freely for non-commercial academic research, benchmarking, and forensic scientific study.
* **Commercial Restrictions:** Direct commercial redistribution or resale of the biometric image specimens is prohibited. The dataset is used here strictly to train, evaluate, and benchmark signature verification algorithms.
* **Customer Data Separation:** The project does **NOT** use proprietary Bank Muscat customer data, nor does it claim real customer data was accessed. The CEDAR dataset provides the sole biometric data source.

### 2.3 Writers and Sample Counts
* **Total Writers ($W$):** 55 distinct human signers (Writers `1` to `55`).
* **Genuine Specimens per Writer:** 24 authentic signatures per writer.
* **Skilled Forgeries per Writer:** 24 practiced forgeries per writer (forgers studied authentic specimens before attempting replications).
* **Total Genuine Images:** $55 \times 24 = 1,320$ images.
* **Total Forged Images:** $55 \times 24 = 1,320$ images.
* **Total Dataset Volume:** **2,640 images**.
* **Zero Missing Data:** All 55 writers contain exactly 24 genuine and 24 forged specimens.

---

## 3. Data Acquisition and Directory Structure

### 3.1 Automated Pipeline
The acquisition and verification pipeline is implemented in:
* Acquisition: [`ml/data/download_dataset.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/data/download_dataset.py)
* Inspection: [`ml/data/inspect_dataset.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/data/inspect_dataset.py)
* Validation: [`ml/data/validate_dataset.py`](file:///c:/Users/ASUS/Downloads/hcl/ml/data/validate_dataset.py)

### 3.2 Expected Physical Directory Layout
```
data/
├── raw/
│   └── signatures/
│       ├── full_org/                 # 1,320 Genuine signatures
│       │   ├── original_1_1.png
│       │   ├── original_1_2.png
│       │   └── ...
│       │   └── original_55_24.png
│       └── full_forg/                # 1,320 Skilled forgeries
│           ├── forgeries_1_1.png
│           ├── forgeries_1_2.png
│           └── ...
│           └── forgeries_55_24.png
├── metadata/
│   ├── dataset_inventory.csv         # File paths, writer IDs, hashes, dimensions
│   ├── split_manifest.json           # Writer-independent split definitions
│   └── validation_report.json        # Checksum and integrity validation outputs
└── pairs/
    ├── train_pairs.csv               # 5,740 training pairs (Writers 1-35)
    ├── validation_pairs.csv          # 1,640 validation pairs (Writers 36-45)
    └── test_pairs.csv                # 1,640 test pairs (Writers 46-55)
```

---

## 4. Verification and Integrity Check

Dataset integrity is guaranteed by running `python ml/data/validate_dataset.py`. The validation executes:
1. **Readable Format Verification:** Confirms all 2,640 images can be parsed by OpenCV and Pillow.
2. **Dimension & Aspect Ratio Checks:** Ensures bounding boxes adhere to standard signature envelopes (aspect ratios 0.78 to 3.65).
3. **Identity & Label Parsing:** Verifies regular expression patterns:
   - Genuine: `^original_(\d+)_(\d+)\.png$`
   - Forgery: `^forgeries_(\d+)_(\d+)\.png$`
4. **Duplicate Detection:** Confirms zero duplicate file hashes across differing writers.

The verification confirmed:
- Total valid files: 2,640
- Corrupted images: 0
- Missing writers: 0
- Status: **100% Verified Valid**
