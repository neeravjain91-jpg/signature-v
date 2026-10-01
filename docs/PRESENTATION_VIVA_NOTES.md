# SIGNATURE VMAKE — Presentation Speaker Notes & Viva Defense Guide

**Project Title**: SIGNATURE VMAKE: AI-Powered Signature Verification & Banking Document Authentication System  
**Author / Presenter**: Neerav Jain  
**Domain**: Artificial Intelligence / Machine Learning / Computer Vision / FinTech  
**Approved Core Stack**: Python 3.11.9, scikit-learn 1.6.1, Hugging Face Transformers 4.49.0, FastAPI 0.115.11  
**Target Repository**: `neeravjain91-jpg/signature-verification`  
**Live Production URL**: [https://signature-verification-rho.vercel.app](https://signature-verification-rho.vercel.app)

---

## PART 1: SLIDE-BY-SLIDE SPEAKER TRANSCRIPT & DEFENSE NOTES

### Slide 1: Title Slide & Executive Identity
- **Slide Title**: SIGNATURE VMAKE — AI-Powered Signature Verification & Banking Document Authentication System
- **What to Explain**:
  - Introduce yourself as Neerav Jain and state the project name: **SIGNATURE VMAKE**.
  - Frame the domain: Applied AI, Computer Vision, and Enterprise Banking / FinTech.
  - State the core technology mandate: Python, scikit-learn classical models, Hugging Face Vision Transformers, and FastAPI.
  - Clarify that SIGNATURE VMAKE is an independent, BRD-aligned banking verification system engineered for high-value cheque clearance and transaction settlement.
- **Key Technical Takeaway**:
  - The project combines classical machine-learning interpretability and compute efficiency with deep visual representations in an auditable banking architecture.
- **Likely Viva Question**:
  - *"What is the primary industry objective of SIGNATURE VMAKE?"*
- **Concise Answer**:
  - *"To replace slow, error-prone manual signature checking in banks with an automated, sub-second, auditable AI verification engine that detects skilled forgeries while minimizing false rejections for legitimate customers."*

---

### Slide 2: Problem Statement & Industrial Context
- **Slide Title**: Problem Statement & Banking Verification Challenges
- **What to Explain**:
  - Explain that commercial banks process thousands of signed documents daily (cheques, withdrawals, wire authorizations).
  - Discuss the twin challenges: **natural intra-writer variability** (genuine signatures never match pixel-for-pixel across signings due to posture, speed, or fatigue) and **skilled forgeries** (fraudsters deliberately mimic global geometric shapes).
  - Contrast traditional manual inspection (hours/days of delay, human fatigue, subjective bias) with SIGNATURE VMAKE (instant scan, standardized preprocessing, dual-track AI scoring, multi-factor risk routing, and sub-second settlement).
- **Key Technical Takeaway**:
  - Naive template subtraction or pixel matching fails; robust biometric authentication requires learned feature representations that tolerate natural variation while isolating stroke forgeries.
- **Likely Viva Question**:
  - *"Why is handwritten signature verification more difficult than facial recognition or fingerprint matching?"*
- **Concise Answer**:
  - *"Fingerprints and irises are physiological biometrics with static physical minütiae. Signatures are behavioral biometrics that change naturally with writing speed, pen pressure, and mood, while skilled forgers actively attempt to imitate them."*

---

### Slide 3: Project Objectives & Scope of Work
- **Slide Title**: Project Objectives & Scope of Work
- **What to Explain**:
  - Walk through the 6 core objectives from the approved synopsis:
    1. Automated offline handwritten signature verification.
    2. Computer vision preprocessing pipeline with aspect-preserved normalization.
    3. Dual-track evaluation of classical ML (scikit-learn) and modern Vision Transformers (Hugging Face).
    4. Calibrated biometric metrics (ROC-AUC, EER, FAR, FRR, Platt scaling).
    5. Multi-factor fraud risk assessment engine combining biometrics with financial exposure.
    6. Production-grade FastAPI REST services, 11 PostgreSQL 3NF entities, and immutable audit logs.
- **Key Technical Takeaway**:
  - SIGNATURE VMAKE is a complete full-stack engineered system encompassing computer vision, machine learning, financial risk analysis, and relational data governance.
- **Likely Viva Question**:
  - *"What is the difference between verification and identification in biometrics?"*
- **Concise Answer**:
  - *"Identification is a 1-to-N search asking 'Who is this person?'. Verification is a 1-to-1 comparison asking 'Is this signature truly from customer X?'. SIGNATURE VMAKE is a 1-to-1 (and 1-to-gallery) verification system."*

---

### Slide 4: Solution Overview & End-to-End Pipeline
- **Slide Title**: Solution Overview: End-to-End Verification Pipeline
- **What to Explain**:
  - Explain the 3-phase horizontal dataflow:
    - **Phase 1: Ingestion & CV Preprocessing**: Magic-byte inspection, Gaussian smoothing, Otsu adaptive binarization, contour bounding box extraction, and aspect-preserved padding to $224 	imes 224$.
    - **Phase 2: Representation & Inference**: Extracting 264-d HOG descriptors for scikit-learn classifiers vs 196 self-attention patch tokens mapped to a 128-d unit hypersphere for the Vision Transformer.
    - **Phase 3: Risk Assessment & Action**: Evaluating similarity score alongside image blur variance, transaction monetary tier, and channel risk to yield a tri-state banking action.
- **Key Technical Takeaway**:
  - Verification is an end-to-end pipeline: raw scans must be standardized before feature extraction, and biometric scores must be contextualized with transaction risk.
- **Likely Viva Question**:
  - *"Why is aspect-ratio preserved scaling critical during preprocessing?"*
- **Concise Answer**:
  - *"If you naively stretch or squash a signature to 224x224, you distort its stroke slant, aspect ratio, and loop shapes—which are critical forensic identifiers for distinguishing genuine handwriting from forgeries."*

---

### Slide 5: Multi-Tier System Architecture
- **Slide Title**: Multi-Tier System Architecture
- **What to Explain**:
  - Explain the 4 architectural layers:
    1. **Presentation Layer**: 7 independent HTML pages (Overview, Manual Workflow, Cheque Studio, Model Comparison, Compliance Queue, Audit Trail, Model Registry).
    2. **API Gateway & Security Layer**: FastAPI REST service with 42 endpoints, JWT token authentication (HS256), and RBAC (`ADMIN`, `OFFICER`, `AUDITOR`).
    3. **Application & ML Engine**: Authoritative OpenCV preprocessor, Model Verifier Factory, Multi-Factor Fraud Risk Engine, and Maker-Checker adjudication queue.
    4. **Storage & Audit Layer**: PostgreSQL 14+ database with 11 3NF entities, encrypted document vault, and SHA-256 tamper-evident event ledger.
- **Key Technical Takeaway**:
  - The architecture enforces strict separation of concerns, non-blocking asynchronous throughput, and enterprise banking security.
- **Likely Viva Question**:
  - *"Why did you choose FastAPI over Flask or Django for this banking system?"*
- **Concise Answer**:
  - *"FastAPI is built on Starlette and Pydantic, offering native asynchronous I/O (ASGI), sub-millisecond serialization overhead, automatic OpenAPI 3.1.0 interactive documentation, and robust request validation, making it ideal for high-concurrency banking APIs."*

---

### Slide 6: Technology Stack & Architectural Roles
- **Slide Title**: Technology Stack & Architectural Roles
- **What to Explain**:
  - Review the technology table with verified versions:
    - Python 3.11.9, scikit-learn 1.6.1, Hugging Face Transformers 4.49.0, FastAPI 0.115.11, OpenCV 4.11.0, PyTorch 2.6.0, NumPy 1.26.4, Pandas 2.2.3, PostgreSQL 14+, Pytest 9.1.1, Docker.
  - Reiterate that PyTorch is strictly the execution backend for Hugging Face Transformers, not an independent Siamese project identity.
- **Key Technical Takeaway**:
  - Every technology has an explicit, verified architectural role without bloated or redundant frameworks.
- **Likely Viva Question**:
  - *"Why is scikit-learn included alongside deep learning Hugging Face Transformers?"*
- **Concise Answer**:
  - *"In banking, classical models like Random Forest and SVM provide extreme compute efficiency (6–10 ms latency, 2 MB size) and strong interpretability on handcrafted features, while Vision Transformers provide deep visual patch representations that capture stroke continuity without manual engineering."*

---

### Slide 7: Dataset Architecture & Open-Set Validation Protocol
- **Slide Title**: Dataset Architecture & Open-Set Validation Protocol
- **What to Explain**:
  - Describe the CEDAR benchmark: 55 writers, 2,640 signatures (1,320 genuine, 1,320 skilled forgeries), scanned at 300 DPI.
  - Explain the **Writer-Disjoint Protocol**:
    - Train: Writers 1 to 35 (2,500 pairs)
    - Validation: Writers 36 to 45 (1,200 pairs) — for threshold calibration
    - Test: Writers 46 to 55 (1,200 pairs) — locked for final evaluation
  - Emphasize the open-set mathematical mandate: $	ext{Train} \cap 	ext{Val} = \emptyset$, $	ext{Train} \cap 	ext{Test} = \emptyset$, $	ext{Val} \cap 	ext{Test} = \emptyset$.
- **Key Technical Takeaway**:
  - Zero identity leakage guarantees that evaluation metrics reflect true generalization to new bank customers whose handwriting was never seen during training.
- **Likely Viva Question**:
  - *"What happens if a signature verification model is evaluated on a random split instead of a writer-disjoint split?"*
- **Concise Answer**:
  - *"A random split leaks signatures of the same writer into both train and test sets. The model ends up memorizing specific individual handwriting styles rather than learning genuine-versus-forgery visual discrepancies, producing overly optimistic, non-generalizable results."*

---

### Slide 8: Authoritative Computer Vision Preprocessing Pipeline
- **Slide Title**: Authoritative Computer Vision Preprocessing Pipeline
- **What to Explain**:
  - Walk through the 8 sequential steps: Loading -> Grayscale -> Gaussian Denoising ($3 	imes 3$) -> Otsu Adaptive Binarization -> Contour Stroke Extraction -> Tight Cropping (10px padding) -> Aspect-Ratio Preserved Scaling ($224 	imes 224$) -> Float32 Normalization ($[0.0, 1.0]$).
  - Explain that this exact preprocessor is universal across training, enrollment, and inference.
- **Key Technical Takeaway**:
  - Computer vision preprocessing removes scanner background grain, ink color variations, and document borders, feeding pure normalized stroke geometry into the models.
- **Likely Viva Question**:
  - *"Why use Otsu binarization instead of a fixed threshold like 128?"*
- **Concise Answer**:
  - *"Cheques and vouchers have different paper background colors, watermark textures, and scanner exposure levels. A fixed threshold fails on dark paper or faded ink, whereas Otsu calculates the optimal bimodal threshold dynamically based on image histogram variance."*

---

### Slide 9: Machine Learning Architecture: Classical ML vs. Vision Transformer
- **Slide Title**: Machine Learning Architecture: Classical ML vs. Vision Transformer
- **What to Explain**:
  - **Track A (scikit-learn)**: Handcrafted 264-d feature vector: Sobel HOG gradient histograms, 8x8 spatial grid densities, horizontal/vertical projection profiles, morphological invariants.
    - Candidate 1: Random Forest (100 ensemble trees, Track A Champion: AUC 0.9424, EER 13.33%).
    - Candidate 2: Linear SVM (Convex margin separation with Platt scaling: AUC 0.8574).
    - Candidate 3: Logistic Regression (L2-regularized linear baseline, 20 KB size: AUC 0.8808).
  - **Track B (Hugging Face)**: `facebook/deit-tiny-patch16-224` vision backbone. 196 spatial tokens ($16 	imes 16$ patches), 12 self-attention layers, 128-d metric projection head ($\|u\|_2 = 1.0$).
    - False Rejection Rate: **3.83%** (True Acceptance Rate: **96.17%**).
- **Key Technical Takeaway**:
  - Random Forest achieves superior overall discrimination, while Vision Transformer excels in low false rejection, protecting authentic bank customers from false fraud flags.
- **Likely Viva Question**:
  - *"How does a Vision Transformer process a 2D signature image?"*
- **Concise Answer**:
  - *"It divides the 224x224 image into a grid of 196 patches (each 16x16 pixels). Each patch is linearly projected into a vector and treated as a visual token. 12 layers of multi-head self-attention allow every token to interact with all other tokens, capturing stroke trajectory and connectivity across the entire signature."*

---

### Slide 10: Manual Signature Registration & Two-Step Verification Workflow
- **Slide Title**: Manual Signature Registration & Two-Step Verification Workflow
- **What to Explain**:
  - Walk through Step 1: Customer Profile Creation and Genuine Specimen Enrollment.
  - State the **Mandatory Banking Specification**:
    > *"The first signature is registered as the reference specimen and does NOT receive a verification verdict."*
  - Explain the Specimen Gallery: Customers can enroll up to 3 authentic reference specimens; soft-deactivation (`SUPERSEDED`) retains full non-repudiation history.
  - Walk through Step 2: Questioned Signature Verification. Operators can choose Single Reference (Mode 1) or Gallery Mode (Mode 2) with dynamic model dispatch across ViT, Random Forest, SVM, or Logistic Regression.
- **Key Technical Takeaway**:
  - Banking logic requires clean separation between enrollment (vault creation) and verification (dynamic scoring of questioned documents).
- **Likely Viva Question**:
  - *"Why shouldn't the first uploaded signature receive a verification score?"*
- **Concise Answer**:
  - *"Because verification requires comparing a questioned signature against an existing authentic reference specimen. During initial registration, there is no existing reference to compare against. Claiming a match on the very first upload would be a logical contradiction in biometric authentication."*

---

### Slide 11: Empirical Model Comparison & Benchmark Evaluation
- **Slide Title**: Empirical Model Comparison & Benchmark Evaluation
- **What to Explain**:
  - Review the verified performance table evaluated on the locked held-out test cohort (Writers 46 to 55, 1,200 pairs):
    - **Random Forest (Champion)**: ROC-AUC **0.9424**, EER **13.33%**, Accuracy **82.92%**, Latency **10.23 ms**, Size **2.39 MB**.
    - **Logistic Regression**: ROC-AUC **0.8808**, EER **18.83%**, Accuracy **80.50%**, Latency **6.00 ms**, Size **0.02 MB**.
    - **Linear SVM**: ROC-AUC **0.8574**, EER **19.00%**, Accuracy **79.17%**, Latency **6.03 ms**, Size **1.90 MB**.
    - **Vision Transformer**: ROC-AUC **0.7947**, EER **27.67%**, FRR **3.83%**, TAR **96.17%**, Latency **36.66 ms**, Size **21.73 MB**.
  - Present the ROC-AUC and EER comparison bar charts.
- **Key Technical Takeaway**:
  - Random Forest provides the highest overall discrimination on HOG features, while Vision Transformer provides deep representation learning with minimal false rejections.
- **Likely Viva Question**:
  - *"What is Equal Error Rate (EER) and why is it used as the primary biometric evaluation metric?"*
- **Concise Answer**:
  - *"EER is the operating point where the False Acceptance Rate (FAR) equals the False Rejection Rate (FRR). A lower EER indicates superior overall discriminatory ability because it balances security against customer convenience."*

---

### Slide 12: Multi-Factor Fraud Risk Engine & Tri-State Banking Actions
- **Slide Title**: Multi-Factor Fraud Risk Engine & Tri-State Banking Actions
- **What to Explain**:
  - Walk through the exact composite risk formula from `services/risk_engine.py`:
    $$	ext{Overall Risk} = 0.50 	imes 	ext{Similarity Risk} + 0.15 	imes 	ext{Quality Risk} + 0.25 	imes 	ext{Transaction Risk} + 0.10 	imes 	ext{Behavioral Risk}$$
  - Explain each factor: Biometric similarity relative to threshold $	au^*$, Laplacian blur variance / contrast, monetary tiers ($\le \$1	ext{k}$ to $>\$100	ext{k}$), channel severity (Cheque 0.25, Wire 0.70), and account anomaly history.
  - Present the Tri-State Banking Actions:
    - **VERIFIED**: $S \ge 	au^*$ and Risk $< 0.25$ (`LOW`). Straight-through clearing.
    - **MANUAL REVIEW**: Borderline similarity or Risk $0.25 - 0.60$ (`MEDIUM`). Escalated to maker-checker queue.
    - **REJECTED**: $S < 	au^* - 0.12$ or Risk $\ge 0.60$ (`HIGH`). Auto-blocked with fraud audit alert.
- **Key Technical Takeaway**:
  - Biometric similarity is only one input into financial decisioning; composite risk scoring prevents catastrophic losses on high-value cheques even if visual similarity is borderline.
- **Likely Viva Question**:
  - *"Can a signature have a biometric MATCH but still be routed to MANUAL REVIEW?"*
- **Concise Answer**:
  - *"Yes! If an authentic signature appears on a $250,000 wire transfer or has a blurred scan (low Laplacian variance), the elevated transaction risk factor increases the composite risk score into the MEDIUM tier, triggering mandatory officer maker-checker review."*

---

### Slide 13: FastAPI Backend, Relational Database & Enterprise Security
- **Slide Title**: FastAPI Backend, Relational Database & Enterprise Security
- **What to Explain**:
  - Review the FastAPI backend: 42 async endpoints, OpenAPI 3.1.0 specifications, Pydantic data contracts.
  - Review the 11 relational entities in `database/models.py`: User, Customer, Account, Signature, SignatureEmbedding, Transaction, VerificationAttempt, RiskAssessment, ManualReview, AuditLog, ModelVersion.
  - Detail banking security: RFC 7519 JWT tokens (HS256), RBAC, magic-byte upload inspection, 5MB file limit, and SHA-256 immutable audit ledger.
- **Key Technical Takeaway**:
  - The system satisfies banking non-repudiation mandates: every attempt is recorded with an immutable correlation ID (`REQ-XXXXXXXX`).
- **Likely Viva Question**:
  - *"How does the system prevent malicious file uploads disguised as signatures?"*
- **Concise Answer**:
  - *"It implements multi-layer defense: first, checking file size (< 5MB); second, validating file extensions; third, reading actual file magic bytes via Python to verify legitimate image headers (PNG, JPEG, TIFF); fourth, sanitizing filenames to block path traversal attacks."*

---

### Slide 14: System Results & Engineering Validation Evidence
- **Slide Title**: System Results & Engineering Validation Evidence
- **What to Explain**:
  - Present the verified evidence from testing:
    - **53 / 53 pytest tests passed (100%)** in 60.27s across API, manual workflow, model suite, page routing, and traceability.
    - **16 / 16 system diagnostic checks passed (100%)** via `scripts/diagnose.py`.
    - **7 / 7 multi-page routes verified** with clean URL resolution on local FastAPI and Vercel serverless CDN.
    - Biometric invariants proven: 0% identity leakage, customer isolation, and soft-deactivation auditability.
- **Key Technical Takeaway**:
  - All claims are backed by executable code and passing automated test suites.
- **Likely Viva Question**:
  - *"How did you test that the first uploaded signature doesn't produce a verification verdict?"*
- **Concise Answer**:
  - *"We have an explicit automated test `test_first_upload_is_strictly_reference_not_verification` in `tests/test_manual_workflow.py` that uploads a specimen to `/api/v1/customers/{id}/signatures` and asserts that the response contains no similarity score, no decision verdict, and returns HTTP 201 Created with status ACTIVE."*

---

### Slide 15: Live Web Application Interface Demonstration
- **Slide Title**: Live Web Application Interface Demonstration
- **What to Explain**:
  - Tour the live web application:
    - Primary interface: **Manual Register & Verify** (`/manual-workflow`) showing customer vault selection, Step 1 enrollment, active specimen cards, candidate model dropdown, and Step 2 dynamic verification.
    - Secondary interfaces: Overview Dashboard (`/`), Cheque Studio (`/verification-studio`), Model Comparison Matrix (`/model-comparison`), Officer Adjudication Queue (`/compliance-queue`), Audit Trail (`/audit-timeline`), Model Registry (`/model-registry`).
  - Provide live URLs: [https://signature-verification-rho.vercel.app](https://signature-verification-rho.vercel.app).
- **Key Technical Takeaway**:
  - The application is deployed and operational in production, featuring clean URL routing and modular page controllers.
- **Likely Viva Question**:
  - *"How does the web application connect to the backend if the frontend is hosted on Vercel and the backend is running locally or in Docker?"*
- **Concise Answer**:
  - *"The frontend uses a standardized API client (`api.js`) that automatically resolves `window.location.origin` when hosted together, or reads a configurable backend base URL from `localStorage` via the built-in API Configuration modal when decoupled."*

---

### Slide 16: Conclusion, Key Achievements & Future Scope
- **Slide Title**: Conclusion, Key Achievements & Future Scope
- **What to Explain**:
  - Summarize achievements: BRD alignment, dual-track AI, writer-disjoint splitting, multi-factor risk scoring, and 53/53 passing tests.
  - Present clearly labeled future scope items from the approved synopsis:
    1. Multilingual Indian Signature Datasets (BHSig260 Hindi/Bengali scripts).
    2. Document / Cheque Forgery Localization Heatmaps (Grad-CAM).
    3. Automated OCR & MICR E-13B magnetic ink character recognition.
    4. Online Dynamic Biometric Fusion (tablet pen pressure, stroke velocity, azimuth).
    5. Continuous Model Drift Monitoring & MLOps (MLflow / Prometheus).
    6. Cloud-Native Kubernetes & Hardware Security Module (HSM) key management.
- **Key Technical Takeaway**:
  - SIGNATURE VMAKE bridges academic machine learning and enterprise banking compliance into a production-grade, extensible biometric platform.
- **Likely Viva Question**:
  - *"What is the single most valuable technical lesson you learned from this project?"*
- **Concise Answer**:
  - *"That building an AI system for banking requires far more than training a model. Real-world success depends on rigorous computer vision preprocessing, open-set dataset splitting with zero leakage, calibrating decision thresholds to business risk, and wrapping models in secure, auditable, high-throughput REST APIs."*

---

## PART 2: COMPREHENSIVE VIVA VOCE EXAMINATION QUESTIONS & ANSWERS (25+ Q&A)

### Section A: Machine Learning & Biometrics

**Q1: What is the primary difference between Track A (scikit-learn) and Track B (Hugging Face Transformers) in your system?**  
*Answer:* Track A uses handcrafted computer-vision feature engineering (264-d vector of Sobel HOG gradient histograms, spatial grid densities, projection profiles, and morphological invariants) fed into classical classifiers like Random Forest and SVM. Track B uses a deep Vision Transformer (`facebook/deit-tiny-patch16-224`) that tokenizes the image into 196 spatial patches and applies 12 multi-head self-attention layers to learn end-to-end visual representations directly from pixels.

**Q2: Why did Random Forest outperform the Vision Transformer in ROC-AUC on your test dataset?**  
*Answer:* Random Forest operates on directional HOG gradients and spatial stroke occupancy descriptors specifically engineered for handwriting stroke orientation. The ensemble of 100 decorrelated decision trees effectively partitions non-linear feature interactions on moderate-sized datasets (2,500 training pairs). Vision Transformers typically require tens of thousands of samples to learn global inductive biases from scratch without overfitting. However, the Vision Transformer matched Random Forest's ultra-low False Rejection Rate (3.83%), making both highly complementary.

**Q3: What is Platt scaling and why did you use it with the Linear SVM?**  
*Answer:* A standard Linear SVM outputs a raw uncalibrated geometric distance from the separating hyperplane ($f(x) \in (-\infty, +\infty)$). Platt scaling fits a sigmoid function $P(y=1|f(x)) = rac{1}{1 + \exp(A f(x) + B)}$ over the validation set to transform this uncalibrated margin into a true posterior probability between 0.0 and 1.0, enabling direct threshold comparison.

**Q4: Explain how Equal Error Rate (EER) is determined.**  
*Answer:* As you vary the decision threshold $	au$ from 0 to 1, the False Acceptance Rate (FAR) decreases while the False Rejection Rate (FRR) increases. The threshold where $	ext{FAR}(	au^*) = 	ext{FRR}(	au^*)$ is the Equal Error Rate operating point. We determine this threshold on the validation cohort (Writers 36–45) and lock it before evaluating on the test cohort.

**Q5: What is the difference between random forgeries and skilled forgeries?**  
*Answer:* A random forgery (or random impostor) is when a signature from Writer B is presented as belonging to Writer A without attempting to copy Writer A's signature. A skilled forgery is created by a professional or trained individual who observes Writer A's authentic signature and intentionally imitates its geometric shape, slant, and loops. Skilled forgeries are vastly harder to detect.

---

### Section B: Computer Vision Preprocessing

**Q6: What specific kernel size and parameters did you use for Gaussian smoothing, and why?**  
*Answer:* We used a $3 	imes 3$ Gaussian smoothing kernel with standard deviation computed automatically ($\sigma=0$). A small $3 	imes 3$ kernel effectively suppresses high-frequency scanner CCD sensor grain and paper texture noise without blurring fine stroke boundaries or thinning pen strokes.

**Q7: How does Otsu's thresholding algorithm work?**  
*Answer:* Otsu's algorithm iterates through all possible pixel intensity thresholds ($t \in [0, 255]$) and calculates the between-class variance $\sigma_B^2(t) = \omega_0(t)\omega_1(t)[\mu_0(t) - \mu_1(t)]^2$ between foreground and background pixel distributions. The threshold that maximizes between-class variance (equivalent to minimizing intra-class variance) is selected as the optimal bimodal separation boundary.

**Q8: Why is polarity inversion necessary after binarization?**  
*Answer:* In scanned paper documents, ink strokes are dark (pixel values near 0) and the paper background is white (pixel values near 255). For neural network feature extraction and spatial stroke density calculation, we need foreground strokes to represent non-zero signal (255 / 1.0) and empty background to represent zero (0.0). We check the background polarity dynamically and invert colors so that ink strokes are always positive activations.

**Q9: How do you prevent division-by-zero during image normalization?**  
*Answer:* In `ml/preprocessing/signature_preprocessor.py`, we convert uint8 images to float32 and scale by $1.0 / 255.0$. If normalizing by dynamic range, an epsilon value ($\epsilon = 1	imes 10^{-6}$) is added to the denominator: $(x - 	ext{min}) / (	ext{max} - 	ext{min} + \epsilon)$.

---

### Section C: Dataset & Splitting Methodology

**Q10: Why is the CEDAR dataset partitioned as Writers 1–35, 36–45, and 46–55?**  
*Answer:* CEDAR contains 55 writers. Following open-set biometric evaluation standards:
- 35 writers (63.6%) are allocated to training representation learning.
- 10 writers (18.2%) are allocated to validation for operating threshold calibration.
- 10 writers (18.2%) are locked for held-out test evaluation.
This ensures sufficient statistical power (1,200 evaluation pairs each) while maintaining zero writer identity leakage.

**Q11: What is the open-set protocol and why is it mandatory for banking?**  
*Answer:* In an open-set protocol, no subject in the test cohort has ever been seen by the model during training. In a commercial bank, thousands of new customers open accounts and register signatures after the AI model is deployed. A closed-set model that only works on enrolled training subjects would be completely useless in production banking.

---

### Section D: Banking Risk Engine & Decisioning

**Q12: Explain the four components of your fraud risk formula.**  
*Answer:*
1. **Similarity Risk (50% weight)**: Measures deficit relative to model threshold $	au^*$. If $S \ge 	au^*$, risk is low ($0.0 - 0.20$). If $S < 	au^*$, risk scales up to $1.0$.
2. **Image Quality Risk (15% weight)**: $1.0 - 	ext{Quality Score}$, where quality is computed from Laplacian variance (blur detection) and dynamic contrast range.
3. **Transaction Risk (25% weight)**: $0.65 	imes 	ext{amount tier} + 0.35 	imes 	ext{channel severity}$. Amount tiers scale from $\$1,000$ to $>\$100,000$; channels scale from Form (0.10) to Wire Transfer (0.70).
4. **Behavioral Risk (10% weight)**: Baseline 0.05, increased by 0.20 for each recorded account verification anomaly in the last 90 days.

**Q13: What happens when a transaction receives a 'MANUAL REVIEW' decision?**  
*Answer:* The transaction is temporarily held in the database with status `MANUAL_REVIEW`. It is automatically pushed to the Compliance Officer Review Queue (`/compliance-queue`). A designated bank officer inspects the questioned signature side-by-side with the customer's enrolled reference specimens, reviews the risk decomposition factors, and adjudicates the case by clicking 'Approve' or 'Reject' with mandatory commentary, creating a maker-checker audit record.

---

### Section E: Software Engineering, Security & APIs

**Q14: Explain how Role-Based Access Control (RBAC) is enforced in your FastAPI application.**  
*Answer:* We define three roles in `api/auth.py`: `ADMIN`, `OFFICER`, and `AUDITOR`. When a user logs in, their JWT token payload contains their role claim. Protected endpoints use FastAPI's dependency injection system with `require_role(["OFFICER", "ADMIN"])`. If a user with role `AUDITOR` attempts to approve a pending review, the dependency intercepts the request before controller execution and returns an HTTP 403 Forbidden exception.

**Q15: How does your database maintain non-repudiation when a customer replaces an old signature?**  
*Answer:* We enforce soft-deactivation. The old specimen record is never deleted (`DELETE FROM signatures`). Instead, its status is updated to `SUPERSEDED`, and an immutable event is written to `AuditLog`. Past verification attempts referencing the old signature maintain intact foreign-key referential integrity, preventing any audit trail tampering.

**Q16: Why did you convert the frontend into 7 independent pages instead of keeping it as a single-page hash application?**  
*Answer:* Single-page hash navigation (`#overview`, `#manual-workflow`) suffered from fragile browser refresh behavior, inability to deep-link or bookmark specific workflows, global JavaScript namespace collisions, and larger initial page weight (107 KB). Converting to 7 independent pages (`/`, `/manual-workflow`, `/verification-studio`, etc.) with modular scripts provides true browser URL addressability, isolated failure domains, faster initial paint, and aligns with enterprise banking portal architectures.

---

### Section F: Examiner Project Defense Wrap-Up

**Q17: What was the most significant bug or architectural challenge you encountered during implementation, and how did you resolve it?**  
*Answer:* A critical architectural challenge was FastAPI route shadowing. The parameterized route `/api/v1/verifications/{verification_id}` was declared before the static route `/api/v1/verifications/pending-reviews`. FastAPI matched `"pending-reviews"` against `{verification_id}` and failed with a 404 UUID lookup error. Reordering the static sub-path before the parameterized path resolved the issue cleanly and was verified by our 53-test automated test suite.

**Q18: If you were given 3 more months of engineering budget, what would you build next?**  
*Answer:* I would integrate an Optical Character Recognition (OCR) pipeline using PaddleOCR to automatically extract MICR codes, account numbers, and handwritten cheque amounts directly from full cheque scans, and train on Indian regional signature scripts (BHSig260) to support multilingual banking.

---

*Document compiled in strict accordance with the approved SIGNATURE VMAKE Project Synopsis and verified codebase implementation.*
