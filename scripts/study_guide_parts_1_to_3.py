#!/usr/bin/env python3
"""
SIGNATURE VMAKE Study Guide — Parts 1 to 3 Builder
Contains Chapters 1 through 16:
- Part 1: Project Foundations & SRS Overview
- Part 2: Architecture & System Design (SRS Section 2 & 3 Aligned)
- Part 3: Computer Vision & Feature Engineering Pipeline
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


def build_parts_1_to_3(doc):
    """Builds Parts 1, 2, and 3 into the provided Word Document."""

    # =========================================================================
    # PART 1: PROJECT FOUNDATIONS & SRS OVERVIEW
    # =========================================================================
    add_part_heading(doc, 1, "Project Foundations & SRS Overview")

    # -------------------------------------------------------------------------
    # CHAPTER 1
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 1, "Project Identity, Academic Context & Origin Story")
    add_body_p(
        doc,
        "SIGNATURE VMAKE is an enterprise-grade, artificial intelligence-powered offline signature verification "
        "and banking document authentication system engineered specifically to resolve the acute financial crime "
        "vulnerabilities inherent in manual cheque clearing, high-value commercial remittances, and KYC account onboarding.",
        bold_prefix="System Definition: "
    )
    add_dual_level_explanation(
        doc,
        beginner_text=(
            "Imagine a bank branch where an elderly customer or a large corporate accountant presents a cheque for $50,000. "
            "A human teller has approximately 3 to 5 seconds to look at the paper cheque, glance at a tiny specimen signature "
            "scanned ten years ago on a computer screen, and decide whether the signature is genuine. If the teller makes a mistake, "
            "the customer loses their life savings or the bank faces massive legal liability. SIGNATURE VMAKE acts like a pair of "
            "superhuman digital glasses for the teller: it analyzes stroke geometry, line thickness, curvature, and pressure patterns "
            "in milliseconds, checks whether the cheque has high fraud risk, and gives the teller an objective, mathematically proven verdict."
        ),
        technical_text=(
            "Offline signature verification is classified mathematically as an open-set, fine-grained pattern recognition challenge. "
            "Unlike closed-set face recognition where the set of target identities is fixed during training, a commercial banking system "
            "must verify signatures from unseen account holders whose handwriting patterns were never part of the training distribution. "
            "SIGNATURE VMAKE operationalizes this via a pairwise differential metric learning paradigm: rather than training a classifier "
            "to recognize specific individuals, the system extracts a 16-dimensional multi-domain handcrafted descriptor vector from both "
            "the registered SPECIMEN and the candidate QUERY signature. The system computes their element-wise absolute difference vector "
            "and passes it through a calibrated scikit-learn Random Forest classifier (ROC-AUC: 0.9424, FRR: 3.83%) alongside a parallel "
            "Hugging Face Vision Transformer (facebook/deit-tiny-patch16-224) metric head."
        )
    )

    add_component_profile(
        doc,
        what="SIGNATURE VMAKE — AI-Powered Signature Verification & Banking Document Authentication System.",
        why="Eliminate manual teller fatigue, defeat skilled calligraphic forgeries, and satisfy stringent banking audit guidelines.",
        how="Combines OpenCV document segmentation, a dual-track ML/DL verification engine, and a 4-pillar risk engine behind FastAPI.",
        inputs="Scanned cheque or signature slip (PNG, JPG, TIFF, 300 DPI recommended), Account ID, Transaction Amount, Velocity flags.",
        outputs="Tri-state verification decision (VERIFIED, MANUAL REVIEW, REJECTED), Similarity Score [0-1], Composite Risk Score [0-1], Audit Log ID.",
        connections="Integrates core banking databases via SQLAlchemy/PostgreSQL, exposes REST APIs for branch portals, and logs tamper-evident trails.",
        location="Project Root: repository root (`api/main.py`, `services/`, `ml/`, `database/`)."
    )

    add_callout(
        doc,
        "VIVA TIP",
        "The Critical Distinction Between SYNAPSE and SIGNATURE VMAKE",
        "If the external examiner asks: 'What is the relationship between this project and SYNAPSE?', answer with absolute precision:\n"
        "'SYNAPSE was an exploratory research prototype focused on deep Siamese metric learning using PyTorch ResNet backbones. "
        "SIGNATURE VMAKE is the approved, production-grade B.Tech software engineering system built strictly on Python, scikit-learn, "
        "Hugging Face Transformers, and FastAPI. In VMAKE, our production champion is a scikit-learn Random Forest operating on "
        "16 handcrafted computer vision features (ROC-AUC 0.9424), supplemented by a lightweight Hugging Face Vision Transformer. "
        "We deliberately separated the projects to satisfy enterprise latency (<11 ms) and regulatory auditability requirements.'"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 2
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 2, "Executive Summary & System Overview")
    add_body_p(
        doc,
        "Modern banking environments face dual competing pressures: the imperative to accelerate transaction processing through "
        "Straight-Through Processing (STP) and the regulatory necessity to prevent escalating cheque fraud. "
        "Traditional banks either rely on exhausted human inspection or rigid, brittle pixel-matching algorithms that reject legitimate "
        "clients whose signatures naturally vary over time."
    )
    add_body_p(
        doc,
        "SIGNATURE VMAKE resolves this dilemma by implementing a multi-stage verification architecture. "
        "The system decouples identity authentication into two independent, corroborating tracks: Track A (Classical Feature Extraction & Ensemble Classification) "
        "and Track B (Hugging Face Vision Transformer Embeddings). Furthermore, VMAKE recognizes that visual similarity alone cannot "
        "safeguard financial assets; therefore, it fuses the visual similarity score into a multi-factor Composite Risk Engine that factors in "
        "Image Quality, Transaction Value Exposure, and Historical Account Velocity before rendering a final automated action."
    )

    add_callout(
        doc,
        "REMEMBER",
        "The Three Fundamental Output States of SIGNATURE VMAKE",
        "1. VERIFIED (Automated Clearance): Similarity Score >= tau* (0.4264) AND Composite Risk < 0.25.\n"
        "2. MANUAL REVIEW (Officer Inspection Queue): Similarity Score in uncertainty margin [tau* - 0.12, tau*) OR Composite Risk in [0.25, 0.60).\n"
        "3. REJECTED (High Fraud Risk Interception): Similarity Score < (tau* - 0.12) OR Composite Risk >= 0.60."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 3
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 3, "Problem Statement, Market Pain Points & Banking Fraud Landscape")
    add_body_p(
        doc,
        "According to financial crime monitoring reports from the Reserve Bank of India (RBI) and global banking consortiums, "
        "cheque fraud accounts for billions of dollars in annual losses. The underlying vulnerability stems from three structural realities:"
    )
    add_bullet_p(doc, "Human cognitive limitations: Bank tellers reviewing hundreds of cheques per shift experience visual fatigue, leading to a False Acceptance Rate (FAR) of skilled forgeries exceeding 35% in manual clearing houses.", bold_prefix="Cognitive Fatigue: ")
    add_bullet_p(doc, "Natural Intra-Writer Variability: Every individual's signature exhibits organic variation depending on pen type, seated posture, emotional state, fatigue, and chronological aging. Naive automated systems trigger an unacceptably high False Rejection Rate (FRR), alienating genuine customers.", bold_prefix="Intra-Writer Variance: ")
    add_bullet_p(doc, "Skilled vs. Random Forgeries: While random forgeries (an amateur scribbling an arbitrary name) are easily detected, skilled forgeries (where a fraudster practices copying the exact geometric loops and flourishes of a victim) mimic global shape almost flawlessly.", bold_prefix="Skilled Forgeries: ")

    add_styled_table(
        doc,
        headers=["Forgery Category", "Description", "Visual Similarity to Genuine", "Difficulty Level", "Detection Mechanism in VMAKE"],
        data=[
            ["Random Forgery", "Fraudster signs without knowing victim's signature", "Very Low (< 15%)", "Trivial", "Geometric Aspect Ratio & Stroke Density"],
            ["Unskilled Forgery", "Fraudster glances at victim's signature briefly", "Moderate (30% - 55%)", "Intermediate", "Contour Curvature & Hu Moments"],
            ["Skilled Forgery", "Fraudster practices victim's style repeatedly", "Very High (> 75%)", "Extremely Hard", "Zhang-Suen Skeleton, Hu Invariants, Differential Vectors"]
        ],
        col_widths=[Inches(1.3), Inches(1.8), Inches(1.1), Inches(1.0), Inches(1.27)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 4
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 4, "Scope of the System & Explicit Out-of-Scope Boundaries")
    add_body_p(
        doc,
        "To ensure absolute engineering rigor and prevent academic over-promising during technical viva examination, the boundaries "
        "of SIGNATURE VMAKE are formally demarcated below in compliance with IEEE Std 830-1998 Section 1.2."
    )
    add_section_heading(doc, "In-Scope Implemented Capabilities")
    add_bullet_p(doc, "Automated extraction and bounding-box segmentation of signatures from standard banking documents and cheque leaves.")
    add_bullet_p(doc, "Dual-track offline verification using classical feature engineering (scikit-learn) and Hugging Face Vision Transformers.")
    add_bullet_p(doc, "First-signature specimen registration protocol enforcing ZERO similarity score and SPECIMEN enrollment status.")
    add_bullet_p(doc, "4-pillar composite risk engine computing financial, image quality, behavioral, and similarity risks.")
    add_bullet_p(doc, "FastAPI asynchronous REST API with Swagger documentation and comprehensive schema validation.")
    add_bullet_p(doc, "PostgreSQL relational persistence with Alembic migrations, foreign key cascading, and complete audit logging.")
    add_bullet_p(doc, "Multi-page responsive frontend supporting 7 dedicated operational workspaces.")

    add_section_heading(doc, "Explicit Out-of-Scope Boundaries (Honest Academic Disclosure)")
    add_bullet_p(doc, "Online/Dynamic Signature Verification: VMAKE does not process temporal trajectory data (pen velocity, pressure over time, azimuth angle) from digitizer tablets; it is strictly an offline static image system.", bold_prefix="Online Dynamics: ")
    add_bullet_p(doc, "Complex Non-Latin Scripts: While the structural features generalize, the current benchmarked models were trained on CEDAR (Latin alphabet signatures). Indic, Cyrillic, or Arabic calligraphy requires re-calibration.", bold_prefix="Non-Latin Scripts: ")
    add_bullet_p(doc, "Live Real-Time Interbank Clearing Networks: VMAKE simulates CTS (Cheque Truncation System) integration via REST endpoints but does not connect to live SWIFT, RTGS, or NPCI production clearing pipelines.", bold_prefix="Live Interbank Feeds: ")
    add_bullet_p(doc, "General Optical Character Recognition (OCR): VMAKE extracts signatures and parses cheque metadata; it does not replace general OCR engines like Tesseract for full unstructured document text parsing.", bold_prefix="Full Document OCR: ")

    add_callout(
        doc,
        "COMMON MISTAKE",
        "Do Not Claim Online Dynamic Verification in Viva!",
        "Examiners frequently test students by asking: 'Does your system measure pen pressure during signing?' "
        "If you say 'Yes, we measure how hard the customer pushed on the glass screen', you will immediately fail the question! "
        "Always state clearly: 'No, SIGNATURE VMAKE is an OFFLINE signature verification system. We operate on scanned 2D images. "
        "We approximate stroke intensity from pixel grayscale density and thickness, but we do NOT capture real-time time-series telemetry.'"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 5
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 5, "Technologies Used — Deep-Dive Architectural Rationale")
    add_body_p(
        doc,
        "Every library and framework in SIGNATURE VMAKE was selected according to strict enterprise criteria: execution speed, "
        "mathematical transparency, deployment footprint, and long-term maintainability."
    )
    add_styled_table(
        doc,
        headers=["Technology", "Version", "Role in VMAKE", "Why Selected Over Alternatives", "Artifact / File Location"],
        data=[
            ["Python", "3.11+", "Core runtime language", "Rich CV/ML ecosystem, asynchronous async/await support", "System environment"],
            ["scikit-learn", "1.5.2", "Production ML engine", "Blazing inference (<11 ms), tree interpretability, joblib serialization", "`ml/models/classical_models.py`"],
            ["Hugging Face", "4.44+", "Vision Transformer (Track B)", "Pre-trained vision transformer representations (DeiT-Tiny), easy fine-tuning", "`ml/models/transformer_models.py`"],
            ["FastAPI", "0.115+", "Asynchronous REST API", "Pydantic data validation, automatic OpenAPI/Swagger generation, high throughput", "`api/main.py`, `api/routers/`"],
            ["OpenCV", "4.10+", "Computer vision pipeline", "C++ optimized image processing, Otsu thresholding, morphological filters", "`ml/preprocessing/`"],
            ["PostgreSQL", "16+", "Relational database", "ACID guarantees, foreign key integrity, robust JSONB audit trail support", "`database/models.py`"],
            ["SQLAlchemy", "2.0+", "Object Relational Mapper", "Clean declarative schemas, connection pooling, Alembic migration compatibility", "`database/session.py`"],
            ["Pytest", "8.3+", "Automated testing suite", "Fixtures, parameterized testing, HTTPX integration for full API test coverage", "`tests/` (53 passing tests)"]
        ],
        col_widths=[Inches(1.1), Inches(0.7), Inches(1.3), Inches(2.1), Inches(1.27)]
    )

    # =========================================================================
    # PART 2: ARCHITECTURE & SYSTEM DESIGN
    # =========================================================================
    add_part_heading(doc, 2, "Architecture & System Design (SRS Aligned)")

    # -------------------------------------------------------------------------
    # CHAPTER 6
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 6, "High-Level System Architecture & Component Interactions")
    add_body_p(
        doc,
        "The SIGNATURE VMAKE architecture is structured into four decoupled horizontal tiers: "
        "(1) Presentation Tier, (2) Application & API Gateway Tier, (3) Computer Vision & Machine Learning Inference Tier, "
        "and (4) Enterprise Data Persistence Tier.",
        bold_prefix="Architectural Topology: "
    )

    img_arch = ASSET_DIR / "architecture_diagram.png"
    add_figure(doc, img_arch, "Figure 2.1: SIGNATURE VMAKE Four-Tier Enterprise Architecture Diagram", width_inches=6.0)

    add_body_p(
        doc,
        "When an officer uploads a cheque image via the frontend web portal, the request traverses the following lifecycle: "
        "The HTTP multipart payload hits FastAPI's `/api/v1/verification/verify` endpoint. "
        "The Signature Preprocessor crops the signature region of interest (ROI), converts the image to grayscale, applies Otsu binarization, "
        "removes scanning artifacts, normalizes dimensions to 220x150 pixels, and extracts the 16-dimensional feature vector. "
        "In parallel, the database retrieves the customer's enrolled SPECIMEN feature vector. "
        "The element-wise absolute difference vector is fed to the Random Forest model. "
        "Concurrently, the Risk Engine evaluates cheque amount, image quality metrics, and transaction history. "
        "The resulting decision is committed to PostgreSQL and returned to the officer in under 15 milliseconds."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 7
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 7, "Dual-Track Verification Engine — Random Forest vs. Vision Transformer")
    add_body_p(
        doc,
        "A central innovation of SIGNATURE VMAKE is its Dual-Track Verification Engine. Rather than relying on a single monolithic "
        "neural network, VMAKE implements two distinct paradigms that can be evaluated independently or in ensemble.",
        bold_prefix="Architectural Duality: "
    )

    add_styled_table(
        doc,
        headers=["Dimension", "Track A: Production Champion", "Track B: Deep Metric Learning"],
        data=[
            ["Underlying Framework", "scikit-learn (RandomForestClassifier)", "Hugging Face Transformers (DeiT-Tiny)"],
            ["Input Representation", "16 handcrafted morphological & geometric features", "Raw normalized 224x224 RGB image patches"],
            ["Feature Engineering", "Otsu thresholding, Zhang-Suen skeleton, Hu moments", "Self-attention transformer patch embeddings (16x16)"],
            ["Model Checkpoint Size", "2.39 MB (classical_random_forest_model.joblib)", "21.73 MB (transformer_signature_model.pt)"],
            ["Inference Latency", "10.23 ms per signature pair", "36.66 ms per signature pair"],
            ["Operating Threshold (tau*)", "0.4264 (optimal F1/EER operating point)", "0.7313 (cosine similarity operating point)"],
            ["Test ROC-AUC (Held-Out)", "0.9424 (Superb discriminative power)", "0.7947 (Promising deep baseline)"],
            ["Equal Error Rate (EER)", "13.33%", "27.67%"],
            ["False Rejection Rate (FRR)", "3.83% (Preserves customer trust)", "3.83% (Identical low rejection of genuine)"],
            ["False Acceptance Rate (FAR)", "30.33% (Skilled forgery test set)", "67.17% (Skilled forgery test set)"],
            ["Hardware Requirements", "Zero GPU required; runs on modest CPU core", "Runs on CPU; benefits from lightweight CUDA/MPS"]
        ],
        col_widths=[Inches(1.8), Inches(2.33), Inches(2.34)]
    )

    add_callout(
        doc,
        "TECHNICAL DEEP DIVE",
        "Why Handcrafted Features Beat Vision Transformers in Offline Signature Verification",
        "Examiners may be surprised that Random Forest outperforms Vision Transformers on this dataset. "
        "The scientific reason is straightforward: Transformers are data-hungry architectures that rely on broad semantic context "
        "(e.g., distinguishing dogs from cats). However, offline signature verification is a fine-grained structural problem. "
        "A skilled forgery differs from a genuine signature not by high-level semantic tokens, but by microscopic stroke hesitations, "
        "abnormal curvature variance, and aspect ratio distortions. Handcrafted geometric and topological algorithms (Otsu, Zhang-Suen, Hu) "
        "directly measure these exact physical handwriting properties, whereas a small Transformer trained on limited offline pairs "
        "struggles to learn fine-grained stroke physics without millions of training images."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 8
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 8, "The 4-Pillar Composite Risk Assessment Framework")
    add_body_p(
        doc,
        "In commercial banking, verifying visual signature similarity is necessary but insufficient. If a forged cheque passes the ML "
        "model with a borderline similarity score of 0.45, approving a $20 cheque is a minor operational incident, but approving a $2,000,000 "
        "cheque can bankrupt a regional branch. SIGNATURE VMAKE therefore implements a 4-Pillar Composite Risk Engine.",
        bold_prefix="Business Risk Alignment: "
    )

    add_math_formula(
        doc,
        "Overall Risk = 0.50 * R_sim + 0.15 * R_quality + 0.25 * R_transaction + 0.10 * R_behavior",
        "Formula 2.1: SIGNATURE VMAKE Multi-Factor Banking Risk Formulation (Implemented in services/risk_engine.py)"
    )

    add_styled_table(
        doc,
        headers=["Pillar", "Weight", "Component Variables", "Mathematical Formulation", "Role in Fraud Prevention"],
        data=[
            ["Similarity Risk (R_sim)", "50%", "ML Model Probability (P_gen)", "R_sim = 1.0 - P_gen", "Inversely reflects machine learning confidence"],
            ["Quality Risk (R_quality)", "15%", "Laplacian blur variance, contrast range", "R_qual = 0.60 * (1 - Blur/500) + 0.40 * (1 - Contrast/180)", "Penalizes blurry scans, smudges, and faded ink"],
            ["Transaction Risk (R_tx)", "25%", "Cheque Face Value ($)", "R_tx = min(1.0, Amount / 500,000)", "Higher financial exposure demands higher security clearance"],
            ["Behavioral Risk (R_beh)", "10%", "24h Cheque Velocity, Account Age", "R_beh = min(1.0, Velocity / 5.0) + (1.0 if Fresh_Acct else 0.0)", "Detects rapid-fire fraudulent cheque cashing runs"]
        ],
        col_widths=[Inches(1.5), Inches(0.6), Inches(1.5), Inches(1.6), Inches(1.27)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 9
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 9, "Database Schema, Relational Integrity & Audit Logging")
    add_body_p(
        doc,
        "Banking compliance (Sarbanes-Oxley, Basel III, RBI Audit Guidelines) mandates that every automated credit/debit verification "
        "must be fully reconstructible years after the event. SIGNATURE VMAKE enforces this via a fully relational PostgreSQL database "
        "managed by SQLAlchemy and Alembic migrations.",
        bold_prefix="Regulatory Auditability: "
    )

    img_er = ASSET_DIR / "er_diagram.png"
    add_figure(doc, img_er, "Figure 2.2: SIGNATURE VMAKE Relational Database Entity-Relationship (ER) Diagram", width_inches=6.0)

    add_bullet_p(doc, "Users Table: Stores banking officer credentials, PBKDF2-hashed passwords, role-based access control (TELLER, COMPLIANCE_OFFICER, ADMIN), and active session state.", bold_prefix="Authentication: ")
    add_bullet_p(doc, "Accounts Table: Represents customer bank accounts, CIF (Customer Information File) numbers, account branch codes, and current ledger status.", bold_prefix="Core Entities: ")
    add_bullet_p(doc, "Signatures Table: Stores enrolled reference SPECIMEN signatures and ad-hoc verification attempts, referencing SHA-256 hashes of the raw image bytes.", bold_prefix="Specimen Management: ")
    add_bullet_p(doc, "Verification_Requests Table: Master transaction ledger recording every verification call, model similarity scores, pillar risk weights, officer override comments, and timestamps.", bold_prefix="Audit Ledger: ")

    # -------------------------------------------------------------------------
    # CHAPTER 10
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 10, "Multi-Page Web Frontend Architecture & Real-Time REST Integration")
    add_body_p(
        doc,
        "Historically, prototype academic systems cram all user interface controls into a single cluttered webpage that hides/shows divs "
        "using CSS anchors. SIGNATURE VMAKE breaks this mold by providing a clean, enterprise-ready Multi-Page Application (MPA) "
        "where each operational banking workflow possesses an independent URL route, isolated JavaScript state, and dedicated REST bindings.",
        bold_prefix="Frontend Decoupling: "
    )
    add_bullet_p(doc, "GET / -> System Overview & Live Processing Metrics Dashboard", bold_prefix="Page 1: ")
    add_bullet_p(doc, "GET /manual-workflow -> Manual Register (Specimen) & Verify (Candidate) Workspace", bold_prefix="Page 2: ")
    add_bullet_p(doc, "GET /verification-studio -> Cheque Studio for Bounding-Box Cropping and Cheque Inspection", bold_prefix="Page 3: ")
    add_bullet_p(doc, "GET /model-comparison -> Benchmark Dashboard with Interactive ROC-AUC and Latency Charts", bold_prefix="Page 4: ")
    add_bullet_p(doc, "GET /compliance-queue -> Officer Review Queue for Triaging Borderline Signatures", bold_prefix="Page 5: ")
    add_bullet_p(doc, "GET /audit-timeline -> Complete Chronological Audit Trail with Hash Verification", bold_prefix="Page 6: ")
    add_bullet_p(doc, "GET /model-registry -> Model Health, Diagnostics, and Production Checkpoint Status", bold_prefix="Page 7: ")

    # =========================================================================
    # PART 3: COMPUTER VISION & FEATURE ENGINEERING PIPELINE
    # =========================================================================
    add_part_heading(doc, 3, "Computer Vision & Feature Engineering Pipeline")

    # -------------------------------------------------------------------------
    # CHAPTER 11
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 11, "Document Ingestion, Bounding-Box Cropping & Binarization")
    add_body_p(
        doc,
        "The computer vision subsystem (implemented in `ml/preprocessing/signature_preprocessor.py`) is the foundational "
        "bedrock of SIGNATURE VMAKE. Input banking documents are received as raw uncompressed byte streams. "
        "The ingestion pipeline converts the image to grayscale and applies adaptive segmentation.",
        bold_prefix="Image Conditioning: "
    )

    img_pipe = ASSET_DIR / "pipeline_diagram.png"
    add_figure(doc, img_pipe, "Figure 3.1: Five-Stage Computer Vision & Feature Extraction Pipeline", width_inches=6.0)

    add_dual_level_explanation(
        doc,
        beginner_text=(
            "When someone signs a cheque, the paper often has background watermarks, coloured security lines, or a printed line that says 'Authorized Signatory'. "
            "If the computer looked at the whole cheque, it would be confused by the bank's logo. In step 1, VMAKE acts like a digital pair of scissors: "
            "it finds the signature box, cuts away the rest of the cheque, and converts the image from millions of colors into pure black ink on pure white paper."
        ),
        technical_text=(
            "The image is first converted from BGR color space to an 8-bit single-channel grayscale representation I(x, y) in [0, 255]. "
            "To separate ink foreground pixels from heterogeneous paper backgrounds, Otsu's Global Adaptive Thresholding algorithm is executed. "
            "Otsu's method computes the normalized image histogram p(i) for gray level i in [0, 255]. For any candidate threshold t, "
            "the image pixels are divided into background class C_0 = [0, t-1] and foreground class C_1 = [t, 255]. "
            "Class probabilities: omega_0(t) = sum_{i=0}^{t-1} p(i) and omega_1(t) = sum_{i=t}^{255} p(i). "
            "Class means: mu_0(t) = sum_{i=0}^{t-1} i*p(i)/omega_0(t) and mu_1(t) = sum_{i=t}^{255} i*p(i)/omega_1(t). "
            "The between-class variance is: sigma_B^2(t) = omega_0(t) * omega_1(t) * [mu_0(t) - mu_1(t)]^2. "
            "The optimal threshold t* is the exact value that maximizes sigma_B^2(t). "
            "Foreground pixels are inverted so that active stroke pixels have intensity 255 and background paper pixels have intensity 0."
        )
    )

    add_math_formula(
        doc,
        "t* = argmax_{0 <= t < 256} { omega_0(t) * omega_1(t) * [mu_0(t) - mu_1(t)]^2 }",
        "Equation 3.1: Otsu's Optimal Between-Class Variance Objective Function"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 12
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 12, "Noise Removal, Thinning (Zhang-Suen Skeletonization) & Contour Extraction")
    add_body_p(
        doc,
        "Scanned documents frequently contain physical dust, paper grain, salt-and-pepper noise, and ink bleed. "
        "Furthermore, different pens (fine gel pens vs. thick felt markers) produce dramatically different stroke widths for the exact same writer. "
        "To ensure invariant feature representations, VMAKE applies morphological denoising and iterative skeletonization.",
        bold_prefix="Morphological Standardization: "
    )

    add_component_profile(
        doc,
        what="Zhang-Suen Thinning & Morphological Clean-up Engine.",
        why="Eliminates the confounding effect of pen stroke thickness so the model evaluates handwriting topology rather than pen choice.",
        how="Iterative 2-sub-iteration pixel deletion algorithm removing boundary pixels that do not break 8-connected stroke topology.",
        inputs="Binarized inverted signature image (foreground = 255, background = 0).",
        outputs="1-pixel-wide topological skeleton representing the core stroke trajectory of the writer.",
        connections="Feeds directly into the contour extraction and loop-counting feature extractors.",
        location="`ml/preprocessing/signature_preprocessor.py`"
    )

    add_code_block(
        doc,
        code_str=(
            "# 3x3 Neighborhood Pixel Ordering for Zhang-Suen Thinning:\n"
            "#   [P9, P2, P3]\n"
            "#   [P8, P1, P4]\n"
            "#   [P7, P6, P5]\n"
            "#\n"
            "# Sub-iteration 1 (North/East boundary deletion):\n"
            "#   Condition 1: 2 <= B(P1) <= 6  (where B(P1) = sum(P2..P9))\n"
            "#   Condition 2: A(P1) == 1       (0-to-1 transitions in sequence P2..P9..P2)\n"
            "#   Condition 3: P2 * P4 * P6 == 0\n"
            "#   Condition 4: P4 * P6 * P8 == 0\n"
            "#\n"
            "# Sub-iteration 2 (South/West boundary deletion):\n"
            "#   Condition 1: 2 <= B(P1) <= 6\n"
            "#   Condition 2: A(P1) == 1\n"
            "#   Condition 3: P2 * P4 * P8 == 0\n"
            "#   Condition 4: P2 * P6 * P8 == 0"
        ),
        caption="Complete 2-Sub-Iteration Algorithmic Criteria for Zhang-Suen Iterative Thinning"
    )

    # -------------------------------------------------------------------------
    # CHAPTER 13
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 13, "Aspect Ratio Standardization & Canvas Normalization")
    add_body_p(
        doc,
        "Signatures vary widely in physical dimensions—some account holders write small, compact signatures (e.g., 80x40 pixels), "
        "while others sign with sprawling executive flourishes spanning 800x300 pixels. "
        "Directly resizing a signature without preserving aspect ratio severely distorts stroke angles and loops.",
        bold_prefix="Geometric Invariance: "
    )
    add_body_p(
        doc,
        "VMAKE enforces a rigorous Canvas Normalization Protocol: the signature foreground is bounded by its minimum enclosing "
        "bounding rectangle [x_min, y_min, w, h]. The aspect ratio AR = w / h is computed and preserved. "
        "The cropped signature is scaled proportionally to fit within a fixed canonical canvas of 220 x 150 pixels, and centered with "
        "symmetric zero-padding. This ensures all spatial feature grids are strictly comparable across all clients."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 14
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 14, "Handcrafted Feature Extraction — Geometric & Structural Vectors")
    add_body_p(
        doc,
        "Track A's superior performance stems from its 16-dimensional multi-domain handcrafted feature vector. "
        "Each feature was engineered to capture a specific biometric invariant of human handwriting.",
        bold_prefix="Biometric Feature Space: "
    )

    add_styled_table(
        doc,
        headers=["Idx", "Feature Name", "Domain", "Mathematical Description", "Biometric Significance"],
        data=[
            ["0", "aspect_ratio", "Geometry", "Width / Height of bounding box", "Reflects writer's macro horizontal spread"],
            ["1", "area_ratio", "Geometry", "Foregound Pixels / (W * H)", "Reflects overall stroke ink occupancy"],
            ["2", "stroke_density", "Topological", "Skeleton Pixels / Bounding Box Area", "Measures handwriting compactness"],
            ["3", "contour_count", "Topological", "Number of distinct disconnected strokes", "Identifies pen lifts during signing"],
            ["4", "max_contour_area", "Geometry", "Area of largest continuous stroke", "Measures dominant flourish size"],
            ["5", "mean_contour_area", "Statistical", "Sum of contour areas / contour count", "Average stroke segment volume"],
            ["6", "contour_perimeter", "Geometry", "Total perimeter length of all contours", "Indicates edge complexity and jaggedness"],
            ["7", "horizontal_transitions", "Structural", "0-to-1 pixel changes across rows", "Measures vertical stroke frequency"],
            ["8", "vertical_transitions", "Structural", "0-to-1 pixel changes across cols", "Measures horizontal baseline crossings"],
            ["9", "hu_moment_0", "Invariant", "log(abs(eta_20 + eta_02))", "Scale, translation & rotation invariant shape moment 1"],
            ["10", "hu_moment_1", "Invariant", "log(abs((eta_20 - eta_02)^2 + 4*eta_11^2))", "Scale, translation & rotation invariant shape moment 2"],
            ["11", "hu_moment_2", "Invariant", "log(abs((eta_30 - 3*eta_12)^2 + ...))", "High-order skewness invariant moment 3"],
            ["12", "center_of_gravity_x", "Centroid", "Normalized X coordinate of centroid", "Measures horizontal center of mass"],
            ["13", "center_of_gravity_y", "Centroid", "Normalized Y coordinate of centroid", "Measures vertical center of mass"],
            ["14", "curvature_variance", "Dynamic", "Variance of contour angle tangents", "Detects trembling / hesitation in forgeries"],
            ["15", "baseline_slant_angle", "Structural", "Linear regression slope of stroke points", "Captures characteristic handwriting tilt"]
        ],
        col_widths=[Inches(0.4), Inches(1.5), Inches(0.9), Inches(2.2), Inches(1.47)]
    )

    # -------------------------------------------------------------------------
    # CHAPTER 15
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 15, "Texture, Statistical & Frequency Domain Descriptors")
    add_body_p(
        doc,
        "Beyond macro geometry, skilled calligraphic forgeries are revealed by microscopic tremor and hesitation. "
        "A genuine writer executes their signature with rapid, fluid ballistic motor movements, producing smooth continuous curvatures. "
        "A forger, by contrast, cautiously traces the path of another person's signature, causing microscopic deceleration, "
        "pen tremors, and unnatural curvature variance.",
        bold_prefix="Micro-Kinematic Signatures: "
    )
    add_body_p(
        doc,
        "VMAKE captures this via curvature variance (Feature 14): along each extracted contour, tangent vectors are computed at step intervals "
        "delta_s = 5 pixels. The angular derivative d theta / ds is evaluated. Genuine signatures display consistent, low-variance angular acceleration, "
        "whereas skilled forgeries exhibit sharp, sporadic angular oscillations caused by visual monitoring and motor hesitation."
    )

    # -------------------------------------------------------------------------
    # CHAPTER 16
    # -------------------------------------------------------------------------
    add_chapter_heading(doc, 16, "Image Quality Assessment Engine")
    add_body_p(
        doc,
        "A frequent failure mode in automated banking verification occurs when customers submit severely blurred, low-resolution, "
        "or over-exposed mobile phone photos of cheques. Feeding poor-quality images to a machine learning model produces 'garbage in, "
        "garbage out'. VMAKE's Image Quality Assessment Engine intercepts degraded images prior to ML inference.",
        bold_prefix="Quality Assurance Pre-Flight: "
    )

    add_styled_table(
        doc,
        headers=["Quality Metric", "Algorithm", "Target Healthy Threshold", "Failure Impact on System"],
        data=[
            ["Blur Deficit", "Variance of Laplacian: Var(Laplacian(I))", ">= 500.0 (Sharp focus)", "Severe blur drops Var < 100, triggering high Quality Risk"],
            ["Contrast Deficit", "Dynamic Range: I_max - I_min", ">= 180.0 (High dynamic range)", "Faint pencil/faded ink drops range < 80, masking stroke edges"],
            ["Dimensions", "Pixel Bounding Box Height x Width", ">= 60x100 pixels", "Images under minimum resolution are rejected immediately"],
            ["Aspect Ratio", "W / H Ratio Check", "0.2 <= AR <= 12.0", "Detects corrupted scans, inverted crops, or blank pages"]
        ],
        col_widths=[Inches(1.3), Inches(2.0), Inches(1.6), Inches(1.57)]
    )

    add_callout(
        doc,
        "VIVA TIP",
        "How Laplacian Variance Measures Image Blur",
        "If the examiner asks: 'How does your code detect whether an image is blurry?', give this precise mathematical answer:\n"
        "'We convolve the grayscale image with the standard 3x3 Laplacian operator kernel [[0, 1, 0], [1, -4, 1], [0, 1, 0]]. "
        "The Laplacian computes the second spatial derivative of the image, highlighting sharp intensity discontinuities (edges). "
        "We then calculate the variance of the resulting response matrix. A crisp, sharp signature has thousands of rapid black-to-white "
        "edge transitions, producing a high variance (typically > 500). A blurry image smooths out edges into gradual gradients, "
        "causing the variance to collapse toward zero. We use this variance directly in our Quality Risk formula.'"
    )


print("study_guide_parts_1_to_3 loaded successfully.")
