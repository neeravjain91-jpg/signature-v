#!/usr/bin/env python3
"""
SIGNATURE VMAKE Study Guide — Parts 15 to 17 Builder
Contains Chapters 54 through 63:
- Part 15: Comprehensive Viva Questions & Answers (60+ Q&A across 5 Categories)
- Part 16: Critical Pitfalls: "What NOT to Say" & Common Mistakes
- Part 17: Master Cheat Sheet, Formula Quick Reference & Appendix
"""

from pathlib import Path
from docx.shared import Inches, Pt
from scripts.study_guide_common import (
    ASSET_DIR,
    add_part_heading,
    add_chapter_heading,
    add_section_heading,
    add_body_p,
    add_bullet_p,
    add_callout,
    add_dual_level_explanation,
    add_component_profile,
    add_styled_table,
    add_figure,
    add_code_block,
    add_math_formula
)


def build_parts_15_to_17(doc):
    """Builds Parts 15, 16, and 17 into the provided Word Document."""

    # =========================================================================
    # PART 15: COMPREHENSIVE VIVA QUESTIONS & ANSWERS (60+ Q&A)
    # =========================================================================
    add_part_heading(doc, 15, "Comprehensive Viva Questions & Answers (60+ Q&A)")

    # -------------------------------------------------------------------------
    # CHAPTER 54: Category 1 — Machine Learning & Model Architecture
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 54, "Viva Category 1: Machine Learning & Model Architecture (15 Q&A)")

    ml_qa = [
        (
            "Q1: Why did your Random Forest model outperform the Hugging Face Vision Transformer?",
            "Offline signature verification is a fine-grained biometric pattern challenge where skilled forgeries differ from genuine signatures by subtle stroke hesitations, pen tremors, and geometric distortions. Vision Transformers require massive datasets (hundreds of thousands of images) to learn low-level stroke kinematics from scratch. Our Random Forest operates on 16 engineered domain-specific features (Hu moments, curvature variance, skeleton transitions) that directly encode handwriting physics, yielding a superior ROC-AUC of 0.9424 versus 0.7947 for DeiT-Tiny on the held-out test cohort."
        ),
        (
            "Q2: How is the pairwise differential feature vector mathematically formulated?",
            "Given a registered specimen signature feature vector f_s in R^16 and a candidate query signature vector f_q in R^16, the differential vector delta is defined as their element-wise absolute difference: delta = |f_s - f_q|. This maps an open-set biometric identification problem into a binary hypothesis space where genuine pairs yield delta near zero and forgery pairs produce large positive discrepancies."
        ),
        (
            "Q3: What is the optimal operating threshold tau* and how was it selected?",
            "For our champion Random Forest model, the optimal threshold is tau* = 0.4264. It was selected on the validation ROC curve by maximizing Youden's Index J = Sensitivity + Specificity - 1, which closely coincides with the Equal Error Rate (EER = 13.33%). At this threshold, the False Rejection Rate is constrained to an ultra-low 3.83%, ensuring 96.17% of genuine customers pass without friction."
        ),
        (
            "Q4: What is Equal Error Rate (EER) and why is it the standard biometric benchmark?",
            "Equal Error Rate is the unique operating point where the False Acceptance Rate (FAR) exactly equals the False Rejection Rate (FRR): FAR(tau_EER) = FRR(tau_EER). It serves as an objective, threshold-independent metric for comparing biometric algorithms. Lower EER values indicate superior overall discrimination."
        ),
        (
            "Q5: Why is this system framed as an 'open-set' rather than a 'closed-set' problem?",
            "In closed-set recognition, all target identities are known during training (e.g., classifying 10 fixed digits). In commercial banking, new customers open accounts daily. The model cannot be retrained every time a customer registers. By learning a distance metric on differential vectors, VMAKE verifies signatures from completely unseen writers without modifying model weights."
        ),
        (
            "Q6: What does the Gini Impurity metric measure in Random Forest decision trees?",
            "Gini impurity measures the probability that a randomly chosen element from a node would be incorrectly labeled if it were randomly labeled according to the class distribution: Gini(t) = 1 - sum(p_k^2). The tree split algorithm searches for the feature and threshold that maximizes the reduction in Gini impurity across child nodes."
        ),
        (
            "Q7: Why choose 100 decision trees in the ensemble?",
            "Empirical hyperparameter tuning demonstrated that ensemble variance stabilized at approximately 80 trees. Beyond 100 trees, marginal ROC-AUC gains were less than 0.001 while inference latency scaled linearly. 100 estimators provided the ideal balance between classification robustness and sub-11ms latency."
        ),
        (
            "Q8: How does the Hugging Face DeiT-Tiny Vision Transformer process a signature image?",
            "DeiT-Tiny resizes the input to 224x224 RGB, divides it into 196 non-overlapping 16x16 pixel patches, projects each patch into a 192-dimensional linear embedding, prepends a learnable [CLS] token, adds sinusoidal positional encodings, and processes the sequence through 12 multi-head self-attention transformer blocks. The final [CLS] embedding is projected to 128-d unit sphere."
        ),
        (
            "Q9: Why are transformer embeddings L2-normalized before computing cosine similarity?",
            "L2 normalization projects all embedding vectors onto the surface of a unit hypersphere (||v||_2 = 1). In this space, Euclidean distance is monotonically related to cosine similarity: ||u - v||^2 = 2 - 2*(u dot v). This eliminates vector magnitude bias caused by varying stroke densities."
        ),
        (
            "Q10: How does the Linear Support Vector Machine establish a decision boundary?",
            "The Linear SVM solves a convex quadratic programming problem to find the separating hyperplane w^T delta + b = 0 that maximizes the geometric margin 2 / ||w|| between genuine and forged differential pairs, subject to soft-margin slack variables xi_i penalized by hyperparameter C = 1.0."
        ),
        (
            "Q11: What is the practical utility of the 20 KB Logistic Regression model?",
            "Our L2-regularized Logistic Regression model has a serialized checkpoint size of just 20 KB and an inference latency of 6.00 ms while achieving 88.08% ROC-AUC. It is ideally suited for ultra-low-power embedded edge devices, such as handheld point-of-sale terminals or offline ATM microcontrollers."
        ),
        (
            "Q12: How does the model account for natural intra-writer variability?",
            "During synthetic training pair generation, the model is trained on multiple positive pairs (G_i, G_j) drawn from the same genuine writer. This explicitly exposes the trees to natural stroke variations, preventing the model from falsely flagging organic human variability as forgery."
        ),
        (
            "Q13: Why did you not use a standard CNN like VGG-16 or ResNet-50 as the primary model?",
            "Deep CNN backbones like VGG-16 contain over 130 million parameters and require GPU acceleration, with inference latencies exceeding 150 ms on CPU. Furthermore, standard CNNs struggle with fine stroke topology without pre-segmentation. Random Forest with handcrafted features achieved 0.9424 ROC-AUC in 10.2 ms on standard CPU hardware."
        ),
        (
            "Q14: How were the classical hyperparameters optimized?",
            "Hyperparameters were tuned via 5-fold cross-validation on the training set (Writers 1-35) using grid search across n_estimators in [50, 100, 200], max_depth in [None, 10, 20], and min_samples_split in [2, 5, 10]. Evaluation strictly used writer-disjoint folds."
        ),
        (
            "Q15: How do you guarantee the model is not overfitting to the training writers?",
            "Overfitting is ruled out by our held-out test evaluation on Writers 46-55. The test cohort signatures belong to writers the model never saw during training. The test ROC-AUC of 0.9424 closely tracked the validation ROC-AUC of 0.9480, confirming true out-of-sample generalization."
        )
    ]

    for q, a in ml_qa:
        add_body_p(doc, a, bold_prefix=f"{q}\nAnswer: ")

    # -------------------------------------------------------------------------
    # CHAPTER 55: Category 2 — Computer Vision & Preprocessing
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 55, "Viva Category 2: Computer Vision & Preprocessing (12 Q&A)")

    cv_qa = [
        (
            "Q16: Why did you choose Otsu's binarization over a fixed threshold?",
            "Fixed thresholding (e.g., intensity 127) fails when cheques have varying paper colors, background watermarks, or uneven branch scanner lighting. Otsu's method is dynamically adaptive: it calculates the optimal threshold that maximizes between-class pixel intensity variance, separating ink strokes from paper regardless of illumination."
        ),
        (
            "Q17: What is the mathematical principle of the Zhang-Suen thinning algorithm?",
            "Zhang-Suen is an iterative parallel thinning algorithm consisting of two sub-iterations. It tests 8-connected neighborhood conditions (neighbor count, 0-to-1 transitions, and directional pixel products) to delete contour boundary pixels without destroying the stroke's topological connectivity or end-points, reducing strokes to a 1-pixel-wide skeleton."
        ),
        (
            "Q18: What are Hu Moments and why are they invariant to scale, rotation, and translation?",
            "Hu Moments are seven non-linear combinations of normalized central moments eta_pq. Normalization by mu_00^((p+q)/2 + 1) provides scale invariance, subtracting centroid coordinates provides translation invariance, and orthogonal algebraic combinations cancel rotational coordinate transformations."
        ),
        (
            "Q19: How do you mathematically measure handwriting curvature variance?",
            "Along each extracted contour, tangent vectors are computed across step intervals. The angular derivative d theta / ds is evaluated. Curvature variance measures the dispersion of these angular changes. Genuine signatures show smooth, low-variance curvature; skilled forgeries show high variance due to pen hesitation and visual steering."
        ),
        (
            "Q20: Why is canvas normalization to 220x150 pixels necessary?",
            "Signatures differ drastically in physical dimensions. Scaling cropped signatures proportionally to fit within a canonical 220x150 canvas while preserving aspect ratio (and zero-padding margins) standardizes spatial density and transition counts across all writers."
        ),
        (
            "Q21: How does Laplacian variance indicate an unreadable scan?",
            "The Laplacian operator computes the second spatial derivative of the image, accentuating high-frequency edges. Sharp strokes produce high variance in the response matrix (> 500). Severe blur smooths edges into gradual gradients, causing variance to drop below 100, which triggers high Image Quality Risk."
        ),
        (
            "Q22: How does the pipeline eliminate background cheque security patterns?",
            "During Otsu binarization and morphological opening with a 3x3 structuring element, faint security lines and watermarks (which have lower local optical density than ballpoint ink) are cleanly eliminated from the foreground stroke mask."
        ),
        (
            "Q23: What do horizontal and vertical transitions signify in human handwriting?",
            "A transition is counted whenever a row or column flips from white background to black stroke (0 to 1). Horizontal transitions measure vertical stroke density (flourishes, loops), while vertical transitions measure horizontal stroke complexity and baseline crossings."
        ),
        (
            "Q24: What is the significance of the signature's Center of Gravity (Centroid)?",
            "The normalized centroid (x_cg, y_cg) represents the geometric center of ink mass. Even when a forger copies the general shape of a name, their distribution of stroke weight often shifts the center of gravity relative to the genuine writer."
        ),
        (
            "Q25: Why is Zhang-Suen thinning sensitive to boundary noise?",
            "Small boundary spurs or scanning dust can create artificial skeleton branches. To counter this, VMAKE applies morphological Gaussian filtering and area-based contour filtering prior to skeletonization, removing spur artifacts under 15 pixels in area."
        ),
        (
            "Q26: How does the system handle blue ink vs. black ink ballpoint pens?",
            "The preprocessing pipeline converts input RGB/BGR images to 8-bit single-channel grayscale using standard ITU-R BT.601 luma weights: Y = 0.299*R + 0.587*G + 0.114*B. Blue ink has sufficient contrast against white paper to be captured accurately."
        ),
        (
            "Q27: Can your computer vision pipeline handle stamped cheques?",
            "Cheques with rubber stamps overlapping the signature are partially mitigated by morphological filtering. However, heavily stamped signatures are identified by anomalous area ratio and high transition counts, correctly routing them to the Officer Review Queue."
        )
    ]

    for q, a in cv_qa:
        add_body_p(doc, a, bold_prefix=f"{q}\nAnswer: ")

    # -------------------------------------------------------------------------
    # CHAPTER 56: Category 3 — System Architecture & Backend Engineering
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 56, "Viva Category 3: System Architecture & Backend Engineering (12 Q&A)")

    arch_qa = [
        (
            "Q28: Why did you choose FastAPI over Flask or Django?",
            "FastAPI is natively asynchronous (built on Starlette and asyncio), enabling non-blocking concurrent request handling essential for high-volume banking clearing. It natively integrates Pydantic v2 for data validation and automatically generates interactive Swagger OpenAPI documentation."
        ),
        (
            "Q29: What is the FastAPI lifespan protocol and why is it used?",
            "The modern `@asynccontextmanager` lifespan protocol manages startup and shutdown events cleanly. On startup, VMAKE warms the database connection pool, loads scikit-learn models into memory, and caches Hugging Face transformer weights, eliminating cold-start latency on initial requests."
        ),
        (
            "Q30: How does the multi-page frontend function without React, Angular, or Vue?",
            "VMAKE adopts modern semantic HTML5 and vanilla modular ES6+ JavaScript. Each operational workspace (/manual-workflow, /compliance-queue, etc.) is an independent HTML page served by FastAPI's Jinja2 template engine. This avoids heavy client-side node_modules, ensuring 200 ms page load times."
        ),
        (
            "Q31: How is relational database integrity maintained in PostgreSQL?",
            "Integrity is enforced via declarative SQLAlchemy models featuring foreign keys with `ON DELETE CASCADE` for parent-child relations (Accounts -> Signatures), unique constraints on account numbers, and ACID-compliant transactional sessions."
        ),
        (
            "Q32: What role does Alembic play in database maintenance?",
            "Alembic handles automated database schema version control. Any alterations to table structures are recorded as reversible Python migration scripts, allowing seamless deployment rollbacks and environment synchronization."
        ),
        (
            "Q33: What is the end-to-end latency budget of a verification request?",
            "On standard commodity quad-core CPU hardware, total latency is 10.23 ms: Image Preprocessing (3.2 ms), Zhang-Suen Thinning (3.8 ms), Feature Extraction (2.1 ms), and Random Forest Evaluation (1.1 ms). Database logging adds ~3 ms, yielding total response time under 15 ms."
        ),
        (
            "Q34: How does Pydantic v2 enforce input validation?",
            "Pydantic v2 utilizes compiled Rust-based validation schemas. All API payloads are strictly validated against strongly typed Python models (e.g., verifying `transaction_amount` is positive, `cheque_number` matches 6-digit banking regex) before handler execution."
        ),
        (
            "Q35: How does the Cheque Studio handle interactive signature cropping?",
            "The Cheque Studio uses an HTML5 Canvas coordinate overlay. When an officer selects a region, normalized bounding box coordinates [x, y, w, h] are transmitted to `/api/v1/verification/studio/crop`, where OpenCV crops the region from the uncompressed image buffer."
        ),
        (
            "Q36: How can the system be containerized with Docker?",
            "The repository includes a production Dockerfile and Docker Compose specification packaging Python 3.11, system OpenCV shared libraries (libgl1-mesa-glx), PostgreSQL 16 container, and Uvicorn ASGI server with multi-worker scaling."
        ),
        (
            "Q37: How does the system prevent memory leaks during heavy image processing?",
            "OpenCV matrix buffers and NumPy arrays are explicitly scoped within request lifecycles. After feature extraction, intermediate image arrays are dereferenced, allowing Python's garbage collector to reclaim heap memory immediately."
        ),
        (
            "Q38: What is the total memory footprint of the running FastAPI server?",
            "With all scikit-learn models and the DeiT-Tiny PyTorch weights loaded in memory, the server process consumes approximately 380 MB of RAM, making it exceptionally lightweight compared to typical LLM or deep vision systems."
        ),
        (
            "Q39: How does the system handle concurrent verification requests from multiple tellers?",
            "FastAPI runs on Uvicorn ASGI workers. Synchronous CPU-bound image processing is dispatched to thread pools via `run_in_threadpool`, preventing the main async event loop from blocking and maintaining sub-second responsiveness."
        )
    ]

    for q, a in arch_qa:
        add_body_p(doc, a, bold_prefix=f"{q}\nAnswer: ")

    # -------------------------------------------------------------------------
    # CHAPTER 57: Category 4 — Banking Risk, Security & Compliance
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 57, "Viva Category 4: Banking Risk, Security & Compliance (12 Q&A)")

    risk_qa = [
        (
            "Q40: Explain the 4-Pillar Composite Risk Engine formula.",
            "The formula is: Overall Risk = 0.50 * R_sim + 0.15 * R_qual + 0.25 * R_tx + 0.10 * R_beh. It weights visual similarity (50%), optical image clarity (15%), financial exposure amount (25%), and historical transaction velocity (10%) to compute a unified risk metric in [0, 1]."
        ),
        (
            "Q41: Why is transaction amount weighted at 25%?",
            "In commercial banking, approving a fraudulent $20 cheque is a minor operational incident, but approving a $500,000 cheque causes catastrophic loss. Factoring in financial value guarantees that large cheques face stricter scrutiny regardless of visual match."
        ),
        (
            "Q42: What happens on the very first signature upload for a customer?",
            "The first signature upload is an enrollment action. The system stores it as the reference SPECIMEN. Because there is no existing reference to compare against, similarity score is 0.0, risk is 0.0, and status is SPECIMEN_REGISTERED. No clearance decision is rendered."
        ),
        (
            "Q43: What are the exact thresholds for the Tri-State Decision Matrix?",
            "VERIFIED: Similarity >= 0.4264 AND Composite Risk < 0.25.\nMANUAL REVIEW: Similarity in [0.3064, 0.4264) OR Composite Risk in [0.25, 0.60).\nREJECTED: Similarity < 0.3064 OR Composite Risk >= 0.60."
        ),
        (
            "Q44: What is the purpose of the Compliance Officer Review Queue?",
            "It provides a human-in-the-loop review mechanism for borderline or high-value cheques. Compliance officers view side-by-side specimen overlays, examine risk pillar breakdowns, and record signed overrides with mandatory justifications."
        ),
        (
            "Q45: How does cryptographic SHA-256 hashing ensure audit trail integrity?",
            "Every verification record stores the SHA-256 digest of the raw cheque image bytes: H = SHA256(bytes). If any image file is tampered with or replaced in storage, the hash validation fails immediately, flagging evidence tampering."
        ),
        (
            "Q46: How does the system defend against rapid-fire cheque kiting fraud?",
            "The Behavioral Risk pillar (R_beh) monitors 24-hour cheque presentation velocity per account: R_beh = min(1.0, Velocity / 5.0). If more than 5 cheques are cashed within 24 hours, behavioral risk hits 1.0, forcing subsequent cheques into manual review."
        ),
        (
            "Q47: How is Role-Based Access Control (RBAC) enforced?",
            "FastAPI dependencies check the user's role extracted from the verified JWT token. Tellers are restricted to verification and specimen registration. Only users with the `COMPLIANCE_OFFICER` or `ADMIN` role can access the review queue or execute overrides."
        ),
        (
            "Q48: How does the system comply with RBI Cheque Truncation System (CTS-2010) norms?",
            "CTS-2010 requires capturing high-quality grayscale/UV images, auditability of clearing decisions, and archival for 10 years. VMAKE's image quality validation, relational ledger, and SHA-256 hashes align directly with CTS-2010 standards."
        ),
        (
            "Q49: What is the False Rejection Rate (FRR) and why is 3.83% an outstanding result?",
            "FRR is the percentage of genuine customers whose cheques are incorrectly flagged as forgeries. At 3.83%, over 96 out of 100 legitimate customers experience instant automated clearance, protecting customer trust and branch throughput."
        ),
        (
            "Q50: How does the system prevent corrupt tellers from approving fraudulent cheques?",
            "All clearing events are committed to the immutable `audit_logs` table with user UUID, timestamp, model prediction, and override notes. Tellers cannot delete records or clear cheques with high composite risk without compliance officer sign-off."
        ),
        (
            "Q51: How are user passwords secured?",
            "Passwords are never stored in plaintext. They are salted with unique cryptographic nonces and hashed using PBKDF2 (Password-Based Key Derivation Function 2) with HMAC-SHA256 and 100,000 iterations."
        )
    ]

    for q, a in risk_qa:
        add_body_p(doc, a, bold_prefix=f"{q}\nAnswer: ")

    # -------------------------------------------------------------------------
    # CHAPTER 58: Category 5 — Project Justification & Comparative Questions
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 58, "Viva Category 5: Project Justification & Comparative Questions (12 Q&A)")

    comp_qa = [
        (
            "Q52: What is the exact academic separation between SYNAPSE and SIGNATURE VMAKE?",
            "SYNAPSE was an experimental research prototype investigating deep Siamese metric learning with PyTorch ResNet backbones and custom metric losses. SIGNATURE VMAKE is the approved production software engineering project built strictly on Python, scikit-learn, Hugging Face Transformers, and FastAPI. Random Forest is VMAKE's champion model, chosen for its 0.9424 ROC-AUC, 10 ms latency, and auditable feature space."
        ),
        (
            "Q53: Why not use a dynamic signature tablet (stylus pen)?",
            "Cheque clearing is inherently paper-based. Over 99% of cheques presented at bank counters or deposited via mobile apps are physical paper documents scanned into 2D static images. Dynamic verification requires specialized biometric digitizer tablets that cannot be used on paper cheques."
        ),
        (
            "Q54: How did you mathematically guarantee zero data leakage during evaluation?",
            "We enforced a strict Writer-Disjoint Partitioning Protocol on the CEDAR benchmark: Train Set (Writers 1-35), Validation Set (Writers 36-45), and Held-Out Test Set (Writers 46-55). The set intersection between train writers and test writers is strictly empty, guaranteeing 0% identity leakage."
        ),
        (
            "Q55: Why evaluate on the CEDAR dataset rather than a proprietary bank dataset?",
            "CEDAR is an internationally recognized, peer-reviewed scientific benchmark containing genuine signatures and skilled forgeries. Using a standardized benchmark allows peer verification and fair comparisons against published academic literature."
        ),
        (
            "Q56: How does VMAKE compare to commercial tools like Parascript or Mitek?",
            "Commercial solutions are expensive proprietary black boxes that do not expose feature calculations or permit on-premise customization. VMAKE provides transparent, open-source 16-D feature vectors, dual-track ML/Transformer inference, and full PostgreSQL relational auditability at zero licensing cost."
        ),
        (
            "Q57: What was the most difficult engineering challenge in this project?",
            "Achieving high skilled-forgery discrimination without sacrificing inference speed. Deep neural networks were too slow on CPU (>150 ms), while simple template matching failed against skilled mimics. Developing the 16-D multi-domain feature pipeline achieved 0.9424 ROC-AUC in just 10.23 ms."
        ),
        (
            "Q58: What are the primary failure modes of the current implementation?",
            "The system can struggle with severely smudged ink, overlapping rubber endorsement stamps, or non-Latin calligraphic scripts (such as Hindi or Arabic) whose structural invariants differ from the Latin-based CEDAR training corpus."
        ),
        (
            "Q59: Why is offline signature verification harder than facial recognition?",
            "Facial recognition benefits from rigid 3D skull geometry and rich color textures. Signatures are 1-bit binary stroke trajectories created by variable motor movements, with high intra-writer variation and skilled forgeries deliberately mimicking genuine shape."
        ),
        (
            "Q60: How would you scale the system to process 10 million cheques per day?",
            "We would decouple the architecture using an asynchronous message broker (RabbitMQ/Apache Kafka). FastAPI gateways would ingest cheques and publish jobs to distributed worker pools running on Kubernetes with Redis caching for registered specimen vectors."
        ),
        (
            "Q61: What steps are required before deploying VMAKE in a live bank?",
            "1. Calibrate on the bank's historical cheque clearing dataset. 2. Implement CTS-2010 image format adapters. 3. Integrate with the bank's Core Banking System (e.g., Finacle). 4. Pass external penetration testing and regulatory compliance audits."
        ),
        (
            "Q62: What key engineering lessons did you learn from this project?",
            "1. Domain-specific feature engineering can outperform deep neural networks on specialized tabular/structural data. 2. Real-world systems require multi-factor risk assessment, not just raw ML probabilities. 3. Rigorous writer-disjoint protocols are essential to prevent data leakage."
        ),
        (
            "Q63: If you had 6 more months, what feature would you implement next?",
            "We would add multi-script support (Indic Devanagari and Gurmukhi signatures), implement an active learning loop allowing compliance officer overrides to re-tune tree splits, and introduce MICR E-13B magnetic font OCR validation."
        )
    ]

    for q, a in comp_qa:
        add_body_p(doc, a, bold_prefix=f"{q}\nAnswer: ")

    # =========================================================================
    # PART 16: CRITICAL PITFALLS: "WHAT NOT TO SAY" & COMMON MISTAKES
    # =========================================================================
    add_part_heading(doc, 16, "Critical Pitfalls: 'What NOT to Say' & Common Mistakes")

    # -------------------------------------------------------------------------
    # CHAPTER 59
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 59, "The 'Red Flag' Statements Examiners Hate & What to Say Instead")
    add_body_p(
        doc,
        "During technical viva defenses, examiners listen for specific buzzwords that reveal superficial understanding or fabricated results. "
        "Study the comparison table below carefully:",
        bold_prefix="Viva Defense Guidance: "
    )

    add_styled_table(
        doc,
        headers=["Dangerous 'Red Flag' Statement (DO NOT SAY)", "Why Examiners Will Penalize You", "Scientifically Rigorous Statement (SAY THIS INSTEAD)"],
        data=[
            [
                "\"Our model achieves 99.9% accuracy on signature verification.\"",
                "Unrealistic for offline skilled forgeries; proves data leakage or closed-set memorization.",
                "\"Our champion Random Forest achieves an empirical ROC-AUC of 0.9424 and an Equal Error Rate of 13.33% on a strictly held-out, writer-disjoint test cohort.\""
            ],
            [
                "\"Our system measures the pen pressure and writing speed of the customer.\"",
                "Impossible for offline 2D scans; reveals confusion between online tablets and offline static images.",
                "\"VMAKE is an offline signature verification system operating on 2D scanned images. We approximate stroke density and thickness via grayscale intensity and skeletonization, but we do not capture dynamic time-series telemetry.\""
            ],
            [
                "\"We trained a Siamese ResNet v4 champion model.\"",
                "Directly contradicts the approved VMAKE technology stack and confuses SYNAPSE with VMAKE.",
                "\"Our production champion is an auditable scikit-learn Random Forest operating on 16 handcrafted computer vision features, benchmarked alongside a Hugging Face Vision Transformer (DeiT-Tiny).\""
            ],
            [
                "\"We created our own dataset by signing 20 times on paper.\"",
                "Destroys academic credibility; student datasets lack skilled forgeries and rigorous controls.",
                "\"We benchmarked our system on the internationally recognized CEDAR offline signature dataset, comprising 55 writers, 2,640 signatures, and 1,320 genuine and 1,320 skilled forgeries.\""
            ],
            [
                "\"Our system uses deep learning because deep learning is always better.\"",
                "Shows lack of critical thinking; examiners respect data-driven model selection.",
                "\"We benchmarked both paradigms: our 16-D Random Forest achieved 0.9424 ROC-AUC in 10.2 ms, outperforming the Vision Transformer (0.7947 AUC, 36.7 ms) due to the fine-grained nature of offline stroke kinematics.\""
            ]
        ],
        col_widths=[Inches(2.1), Inches(2.0), Inches(2.37)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 60
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 60, "Examiner Trap Questions & How to Defend Them")

    traps = [
        (
            "Trap 1: 'What if a wealthy customer signs with a pencil or faded ballpoint pen?'",
            "Defense: 'Our Image Quality Assessment Engine intercepts the image before inference. It evaluates dynamic contrast range (I_max - I_min) and Laplacian variance. If the pencil stroke lacks sufficient optical density (< 80), the system flags high Image Quality Risk (R_qual) and routes the cheque to the Officer Review Queue rather than making an unreliable automated rejection.'"
        ),
        (
            "Trap 2: 'Can your system be fooled by a high-resolution color photocopy of a genuine signature?'",
            "Defense: 'A 2D photocopy reproduces macro geometry, but flatbed scanners introduce xerographic edge halftoning, background toner scatter, and loss of fine stroke tapering. Our curvature variance and skeleton density features detect these photocopy artifacts. Furthermore, when CTS-2010 UV imaging is enabled, photocopy paper lacks bank-grade security paper fluorescence.'"
        ),
        (
            "Trap 3: 'Why did you use 16 handcrafted features instead of extracting 1,000 features via SIFT or SURF?'",
            "Defense: 'Dense keypoint descriptors like SIFT generate thousands of local interest points that are highly sensitive to paper grain and ink splatter. Furthermore, SIFT point matching has O(N^2) computational complexity, causing unacceptable latencies (> 300 ms). Our 16 holistic features capture global geometry, topological structure, and Hu invariants in just 2.1 ms.'"
        )
    ]

    for title, desc in traps:
        add_body_p(doc, desc, bold_prefix=f"{title}:\n")

    # =========================================================================
    # PART 17: MASTER CHEAT SHEET, FORMULA QUICK REFERENCE & APPENDIX
    # =========================================================================
    add_part_heading(doc, 17, "Master Cheat Sheet, Formula Quick Reference & Appendix")

    # -------------------------------------------------------------------------
    # CHAPTER 61
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 61, "The 1-Page Viva Defense Master Cheat Sheet")
    add_body_p(
        doc,
        "Review this master summary sheet immediately before stepping into your viva examination room:",
        bold_prefix="Final Review: "
    )

    add_styled_table(
        doc,
        headers=["Core Dimension", "Exact Scientific Fact / Metric to State"],
        data=[
            ["Project Full Title", "SIGNATURE VMAKE: AI-Powered Signature Verification & Banking Document Authentication System"],
            ["Specification Standard", "IEEE Std 830-1998 (Recommended Practice for Software Requirements Specifications)"],
            ["Approved Tech Stack", "Python 3.11, scikit-learn 1.5.2, Hugging Face Transformers (DeiT-Tiny), FastAPI 0.115, PostgreSQL 16"],
            ["Production Champion", "scikit-learn Random Forest Classifier (100 estimators, 16 handcrafted features)"],
            ["Champion Performance", "ROC-AUC: 0.9424  •  EER: 13.33%  •  FRR: 3.83%  •  FAR: 30.33%  •  Latency: 10.23 ms"],
            ["Vision Transformer (Track B)", "facebook/deit-tiny-patch16-224 (ROC-AUC: 0.7947, EER: 27.67%, Latency: 36.66 ms)"],
            ["Optimal Operating Point", "tau* = 0.4264 (Maximizes Youden's Index J on validation cohort)"],
            ["Benchmark Dataset", "CEDAR Signature Dataset (55 Writers, 2,640 Signatures: 1,320 genuine, 1,320 skilled forgeries)"],
            ["Partitioning Protocol", "Writer-Disjoint: Train (Writers 1-35), Val (Writers 36-45), Held-Out Test (Writers 46-55). 0% Leakage"],
            ["Composite Risk Formula", "Overall Risk = 0.50 * R_sim + 0.15 * R_qual + 0.25 * R_tx + 0.10 * R_beh"],
            ["Tri-State Verdicts", "VERIFIED (Risk < 0.25, S >= tau*), MANUAL REVIEW (Risk 0.25-0.60), REJECTED (Risk >= 0.60)"],
            ["First Specimen Rule", "First signature upload enrolls reference SPECIMEN; similarity is 0.0, risk is 0.0, status is REGISTERED"],
            ["Test Suite Status", "53 / 53 Pytest Tests Passing (100%)  •  16 / 16 Diagnostic Health Checks Verified"],
            ["Frontend Architecture", "Decoupled Multi-Page Application across 7 dedicated addressable workspaces (/, /manual-workflow, etc.)"]
        ],
        col_widths=[Inches(2.2), Inches(4.27)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 62
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 62, "Complete Mathematical Formula Reference Table")
    add_body_p(
        doc,
        "Every mathematical formula implemented in the SIGNATURE VMAKE codebase is cataloged below:",
        bold_prefix="Mathematical Glossary: "
    )

    add_styled_table(
        doc,
        headers=["Formula Name", "Mathematical Expression", "Code Location"],
        data=[
            ["Composite Risk Index", "R = 0.50*R_sim + 0.15*R_qual + 0.25*R_tx + 0.10*R_beh", "`services/risk_engine.py`"],
            ["Similarity Risk", "R_sim = 1.0 - P_gen", "`services/risk_engine.py`"],
            ["Image Quality Risk", "R_qual = 0.60*(1 - Var(Lap)/500) + 0.40*(1 - Contrast/180)", "`services/risk_engine.py`"],
            ["Transaction Risk", "R_tx = min(1.0, Amount / 500,000)", "`services/risk_engine.py`"],
            ["Behavioral Risk", "R_beh = min(1.0, Velocity / 5.0) + (0.5 if Fresh else 0.0)", "`services/risk_engine.py`"],
            ["Differential Vector", "delta = | f_specimen - f_query | in R^16", "`ml/models/classical_models.py`"],
            ["Otsu Thresholding", "t* = argmax [ omega_0(t)*omega_1(t)*(mu_0(t) - mu_1(t))^2 ]", "`ml/preprocessing/signature_preprocessor.py`"],
            ["Laplacian Variance", "Var(L) = (1/N) * sum( (L(x,y) - mean(L))^2 )", "`ml/preprocessing/signature_preprocessor.py`"],
            ["Cosine Similarity", "cos(u, v) = (u dot v) / (||u||_2 * ||v||_2)", "`ml/models/transformer_models.py`"],
            ["False Rejection Rate", "FRR = FN / (TP + FN) = 1.0 - Recall", "`artifacts/evaluation/`"],
            ["False Acceptance Rate", "FAR = FP / (TN + FP)", "`artifacts/evaluation/`"],
            ["Youden's J Index", "J = Sensitivity + Specificity - 1", "`ml/models/classical_models.py`"]
        ],
        col_widths=[Inches(1.8), Inches(3.2), Inches(1.47)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 63
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 63, "Comprehensive Source Code Map & File Index")
    add_body_p(
        doc,
        "Quick reference mapping theoretical concepts to physical repository files:",
        bold_prefix="Repository Architecture Map: "
    )

    add_styled_table(
        doc,
        headers=["System Component", "Repository Path", "Primary Classes & Functions"],
        data=[
            ["FastAPI Gateway", "api/main.py", "FastAPI app instance, lifespan context, router registration"],
            ["API Routers", "api/routers/", "auth.py, verification.py, compliance.py, audit.py, system.py"],
            ["Classical ML Models", "ml/models/classical_models.py", "ClassicalSignatureModel, RandomForest, SVM, Logistic"],
            ["Vision Transformer", "ml/models/transformer_models.py", "TransformerSignatureModel, DeiT-Tiny metric head"],
            ["Computer Vision Core", "ml/preprocessing/signature_preprocessor.py", "SignaturePreprocessor, Otsu, Zhang-Suen, 16-D extractor"],
            ["Risk Assessment", "services/risk_engine.py", "RiskEngine, 4-pillar composite risk calculator"],
            ["Database Models", "database/models.py", "User, Account, Signature, VerificationRequest, AuditLog"],
            ["Database Session", "database/session.py", "SQLAlchemy engine, scoped sessionmaker, connection pool"],
            ["Pytest Test Suite", "tests/", "53 automated test cases across 6 test modules"],
            ["Diagnostics Script", "scripts/diagnose.py", "16 automated self-diagnostic health checks"],
            ["Multipage E2E Test", "scripts/test_multipage_e2e.py", "HTTP E2E test verifying all 7 addressable workspaces"],
            ["Model Checkpoints", "artifacts/models/", "classical_random_forest_model.joblib, transformer_signature_model.pt"],
            ["Evaluation Benchmark", "artifacts/evaluation/", "model_comparison_benchmark.json, evaluation plots"]
        ],
        col_widths=[Inches(1.8), Inches(2.4), Inches(2.27)]
    )


print("study_guide_parts_15_to_17 loaded successfully.")
