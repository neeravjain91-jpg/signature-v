# CROSS-DATASET GENERALIZATION & ACCESS AUDIT (PHASE 10)

## Objective & Compliance Mandate
To assess the feasibility and impact of expanding development training with external public signature benchmarks (GPDS, BHSig260, MCYT, UTSig) while adhering strictly to:
- No fabricated dataset access or metrics.
- Respecting intellectual property, data protection, and university research distribution licenses.

---

## 1. Candidate Offline Signature Benchmark Investigation

| Dataset | Origin / Custodian | Availability & License | Status in Workspace |
| :--- | :--- | :--- | :---: |
| **CEDAR Offline Signatures** | University at Buffalo (CEDAR) | Public academic benchmark for offline signature verification. | **Locally Available (55 writers, 2,640 signatures)** |
| **GPDS (GPDS-300 / GPDS-960)** | Universidad de Las Palmas de Gran Canaria | Restricted academic access. Requires formal signed institutional academic request form sent to Ceani. | Restricted / Not locally downloaded |
| **MCYT-75 / MCYT-100** | Biometric Recognition Group (ATVS), Universidad Autónoma de Madrid | Restricted academic distribution under bilateral NDA. | Restricted / Not locally downloaded |
| **BHSig260** | Indian Statistical Institute (Bengali & Hindi) | Academic distribution via authorized research repository. | Not locally present |
| **UTSig** | University of Tehran | Public academic repository (Persian script). | Not locally present |

---

## 2. Cross-Dataset Generalization Findings
1. **Academic Access Protocols**: In compliance with university ethics and dataset access agreements, no external datasets were fabricated or synthesized. The local CEDAR benchmark serves as the verified, legally compliant offline dataset for the SIGNATURE VMAKE project.
2. **Generalization Strategy**: Because cross-dataset training on GPDS is restricted, domain generalization was reinforced using:
   - **Realistic Biomechanical Data Augmentations** (simulating pen speed, slant, micro-shearing, and scanner artifacts).
   - **Focal Hybrid Metric Learning** (preventing overfitting to CEDAR-specific ink artifacts).
   - **5-Fold Writer-Disjoint Validation** across Writers 1–45.
