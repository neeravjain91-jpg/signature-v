#!/usr/bin/env python3
"""
SIGNATURE VMAKE — Comprehensive PowerPoint Presentation & Speaker Notes Generator
Builds:
- SIGNATURE_VMAKE_Project_Presentation.pptx (16 Slides with embedded notes, diagrams, charts, screenshots)
- docs/PRESENTATION_VIVA_NOTES.md (Complete transcript, technical takeaways, and 25+ viva Q&As)
"""

import os
import sys
import tempfile
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Root and output paths
ROOT_DIR = Path(__file__).resolve().parent.parent
PPTX_OUTPUT = ROOT_DIR / "SIGNATURE_VMAKE_Project_Presentation.pptx"
VIVA_OUTPUT = ROOT_DIR / "docs" / "PRESENTATION_VIVA_NOTES.md"
ASSET_DIR = Path(tempfile.gettempdir()) / "vmake_ppt_assets"

# Color Palette (Dark Professional Banking & AI Theme)
C_BG_DARK = RGBColor(11, 17, 32)        # #0B1120 (Slate 950 deep navy)
C_CARD_BG = RGBColor(20, 29, 47)        # #141D2F (Card background)
C_CARD_BORDER = RGBColor(38, 52, 79)    # #26344F (Subtle border)
C_TEXT_WHITE = RGBColor(255, 255, 255)  # #FFFFFF
C_TEXT_MUTED = RGBColor(148, 163, 184)  # #94A3B8 (Slate 400)
C_TEXT_DIM = RGBColor(100, 116, 139)    # #64748B (Slate 500)
C_CYAN = RGBColor(56, 189, 248)         # #38BDF8 (Sky/Cyan 400)
C_EMERALD = RGBColor(16, 185, 129)      # #10B981 (Emerald 500)
C_AMBER = RGBColor(245, 158, 11)        # #F59E0B (Amber 500)
C_ROSE = RGBColor(244, 63, 94)          # #F43F5E (Rose 500)
C_PURPLE = RGBColor(168, 85, 247)       # #A855F7 (Purple 500)
C_INDIGO = RGBColor(99, 102, 241)       # #6366F1 (Indigo 500)

FONT_HEADING = "Calibri"
FONT_BODY = "Calibri"


def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def add_base_slide(prs, title: str, category: str, slide_num: int):
    """Creates a slide with the dark canvas and unified header."""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # Dark background fill
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG_DARK
    bg.line.fill.background()

    # Header top bar container
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = RGBColor(15, 23, 42)
    top_bar.line.color.rgb = C_CARD_BORDER
    top_bar.line.width = Pt(1)

    # Category badge & Slide Title
    txbox = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(9.5), Inches(0.95))
    tf = txbox.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

    p_cat = tf.paragraphs[0]
    p_cat.text = f"SIGNATURE VMAKE  •  {category.upper()}"
    p_cat.font.name = FONT_HEADING
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = C_CYAN
    p_cat.space_after = Pt(2)

    p_title = tf.add_paragraph()
    p_title.text = title
    p_title.font.name = FONT_HEADING
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = C_TEXT_WHITE

    # Slide Counter
    counter_box = slide.shapes.add_textbox(Inches(10.5), Inches(0.35), Inches(2.0), Inches(0.5))
    tf_c = counter_box.text_frame
    p_c = tf_c.paragraphs[0]
    p_c.alignment = PP_ALIGN.RIGHT
    p_c.text = f"Slide {slide_num} of 16"
    p_c.font.name = FONT_BODY
    p_c.font.size = Pt(11)
    p_c.font.bold = True
    p_c.font.color.rgb = C_TEXT_MUTED

    return slide


def add_card(slide, left, top, width, height, border_color=C_CARD_BORDER, bg_color=C_CARD_BG):
    """Draws a card background shape."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    card.line.color.rgb = border_color
    card.line.width = Pt(1.5)
    return card


def set_speaker_notes(slide, notes_dict):
    """Embeds formatted speaker notes into the PowerPoint slide."""
    text_frame = slide.notes_slide.notes_text_frame
    text_frame.text = f"SLIDE {notes_dict['slide_num']}: {notes_dict['title'].upper()}\n"
    text_frame.text += "=" * 65 + "\n\n"
    text_frame.text += "1. WHAT TO EXPLAIN:\n"
    for pt in notes_dict["explain"]:
        text_frame.text += f"   • {pt}\n"
    text_frame.text += "\n2. KEY TECHNICAL TAKEAWAY:\n"
    text_frame.text += f"   {notes_dict['takeaway']}\n\n"
    text_frame.text += "3. LIKELY VIVA QUESTION:\n"
    text_frame.text += f"   \"{notes_dict['question']}\"\n\n"
    text_frame.text += "4. CONCISE ANSWER:\n"
    text_frame.text += f"   \"{notes_dict['answer']}\"\n"


# -------------------------------------------------------------
# SLIDE BUILDERS (1 to 16)
# -------------------------------------------------------------

def build_slide_1(prs):
    """Slide 1: Title Slide"""
    blank_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_layout)

    # Dark background fill
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = C_BG_DARK
    bg.line.fill.background()

    # Outer hero card
    add_card(slide, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), border_color=C_CYAN, bg_color=C_CARD_BG)

    # Title content
    tb = slide.shapes.add_textbox(Inches(1.2), Inches(1.2), Inches(11.0), Inches(3.2))
    tf = tb.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "BANK MUSCAT BRD ALIGNED  •  ENTERPRISE BIOMETRIC AUTHENTICATION"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(10)

    p1 = tf.add_paragraph()
    p1.text = "SIGNATURE VMAKE"
    p1.font.name = FONT_HEADING
    p1.font.size = Pt(40)
    p1.font.bold = True
    p1.font.color.rgb = C_TEXT_WHITE
    p1.space_after = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "AI-Powered Signature Verification & Banking Document Authentication System"
    p2.font.name = FONT_BODY
    p2.font.size = Pt(18)
    p2.font.color.rgb = C_TEXT_MUTED
    p2.space_after = Pt(16)

    p3 = tf.add_paragraph()
    p3.text = "Presenter: Neerav Jain    |    Domain: AI / ML  •  Computer Vision  •  Banking / FinTech\nProject Type: Internship-Level AI/ML & Backend System    |    Core Stack: Python • scikit-learn • Hugging Face • FastAPI"
    p3.font.name = FONT_BODY
    p3.font.size = Pt(12)
    p3.font.color.rgb = C_EMERALD

    # 3 Pill Cards at bottom
    pills = [
        ("0% Identity Leakage", "Strict writer-disjoint open-set evaluation protocol (Writers 1-35 / 36-45 / 46-55).", C_CYAN),
        ("Dual-Track AI Architecture", "scikit-learn Random Forest (94.24% AUC) + Hugging Face Vision Transformer (DeiT).", C_AMBER),
        ("Regulatory Compliance", "Maker-checker escalation queue, tri-state decisions, and SHA-256 immutable audit ledger.", C_EMERALD)
    ]
    w = Inches(3.55)
    gap = Inches(0.24)
    for i, (title, desc, col) in enumerate(pills):
        x = Inches(1.2) + i * (w + gap)
        add_card(slide, x, Inches(4.7), w, Inches(1.6), border_color=col, bg_color=RGBColor(15, 23, 42))
        tb_p = slide.shapes.add_textbox(x + Inches(0.15), Inches(4.8), w - Inches(0.3), Inches(1.4))
        tf_p = tb_p.text_frame
        tf_p.word_wrap = True
        pt = tf_p.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(4)
        pd = tf_p.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(10)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 1,
        "title": "Title & Executive Overview",
        "explain": [
            "Introduce yourself as Neerav Jain presenting SIGNATURE VMAKE.",
            "State project domain: AI/ML, Computer Vision, and FinTech Banking Document Authentication.",
            "Emphasize the approved core stack: Python, scikit-learn, Hugging Face Transformers, and FastAPI.",
            "Clarify that this is an independent, BRD-aligned banking verification platform."
        ],
        "takeaway": "SIGNATURE VMAKE combines classical ML baselines with modern Vision Transformers into a secure, production-ready banking verification service.",
        "question": "What is the primary industry objective of SIGNATURE VMAKE?",
        "answer": "To replace slow, error-prone manual signature checking in banks with an automated, sub-second, auditable AI verification engine that detects skilled forgeries while minimizing false rejections for legitimate customers."
    }
    set_speaker_notes(slide, notes)


def build_slide_2(prs):
    """Slide 2: Problem Statement & Industrial Context"""
    slide = add_base_slide(prs, "Problem Statement & Banking Verification Challenges", "Industrial Context", 2)

    # Left Card: The Problem
    add_card(slide, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_ROSE)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "THE BANKING & BIOMETRIC CHALLENGE"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = C_ROSE
    p0.space_after = Pt(12)

    challenges = [
        ("High Volume, High Value:", "Banks clear thousands of cheques, wire transfers, and withdrawal mandates daily. Manual verification is slow and creates settlement bottlenecks."),
        ("Human Cognitive Fatigue:", "Manual inspection is prone to subjective bias, eye fatigue, and inconsistent human judgment, leading to undetected forgeries."),
        ("Intra-Writer Variability:", "Genuine signatures naturally vary between signing attempts due to writing speed, pen angle, pressure, fatigue, and physical posture."),
        ("Skilled Forgeries:", "Professional fraudsters mimic the overall geometric shape of a signature. Superficial inspection fails to distinguish authentic flow from traced lines."),
        ("Failure of Pixel Matching:", "Naive template subtraction or pixel-level correlation fails due to paper scan rotation, ink bleeding, and line thickness differences.")
    ]
    for title, desc in challenges:
        p = tf_l.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # Right Card: Traditional vs AI Solution
    add_card(slide, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_CYAN)
    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "TRADITIONAL WORKFLOW VS. AI-ASSISTED SOLUTION"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(14)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_CYAN
    p_r0.space_after = Pt(12)

    # Traditional Box
    p_t = tf_r.add_paragraph()
    p_t.text = "[ Traditional Manual Verification ]\n"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(12)
    p_t.font.bold = True
    p_t.font.color.rgb = C_AMBER
    p_t_body = p_t.add_run()
    p_t_body.text = "Paper Cheque / Form Submission\n  → Manual Inspection by Branch Clerk (Hours/Days delay)\n  → High Human Variability & Subjective Guesswork\n  → Weak, Non-Standardized Audit Records\n  → Vulnerable to Skilled Forgery & Social Engineering\n"
    p_t_body.font.name = FONT_BODY
    p_t_body.font.size = Pt(10)
    p_t_body.font.color.rgb = C_TEXT_MUTED

    # AI Solution Box
    p_ai = tf_r.add_paragraph()
    p_ai.text = "[ SIGNATURE VMAKE AI-Assisted Verification ]\n"
    p_ai.font.name = FONT_HEADING
    p_ai.font.size = Pt(12)
    p_ai.font.bold = True
    p_ai.font.color.rgb = C_EMERALD
    p_ai_body = p_ai.add_run()
    p_ai_body.text = "Digital Ingestion & OpenCV Normalization (Aspect-ratio preserved)\n  → Dual-Track Inference: scikit-learn Classifiers + Vision Transformer\n  → Objective Calibrated Similarity Score (0.0000 - 1.0000)\n  → Multi-Factor Risk Assessment (Biometrics + Amount + Channel)\n  → Autonomous Settlement (<0.25 Risk) or Maker-Checker Adjudication\n  → Immutable SHA-256 Non-Repudiation Audit Ledger"
    p_ai_body.font.name = FONT_BODY
    p_ai_body.font.size = Pt(10)
    p_ai_body.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 2,
        "title": "Problem Statement & Banking Verification Challenges",
        "explain": [
            "Explain that signature verification is the frontline authentication mechanism in commercial banking.",
            "Discuss the twin challenges: natural intra-writer variation (genuine signatures never match pixel-for-pixel) and skilled forgeries (fraudsters deliberately mimic visual outlines).",
            "Contrast the slow, subjective manual inspection process with automated AI-assisted verification.",
            "Highlight how SIGNATURE VMAKE solves this with sub-second objective scoring and multi-factor risk routing."
        ],
        "takeaway": "Simple pixel matching fails; robust biometric authentication requires machine learning representations that tolerate intra-writer variation while exposing skilled forgeries.",
        "question": "Why is signature verification harder than facial recognition or fingerprinting?",
        "answer": "Fingerprints and irises are rigid physiological biometrics with static minütiae. Signatures are behavioral biometrics that change naturally with writing speed, pen pressure, and mood, while skilled forgers actively attempt to imitate them."
    }
    set_speaker_notes(slide, notes)


def build_slide_3(prs):
    """Slide 3: Project Objectives"""
    slide = add_base_slide(prs, "Project Objectives & Scope of Work", "Synopsis Alignment", 3)

    objectives = [
        ("1. Automated Signature Verification", "Develop an offline handwritten signature verification engine capable of detecting genuine vs forged specimens in sub-second latency.", C_CYAN),
        ("2. Computer Vision Preprocessing", "Implement an OpenCV pipeline (noise suppression, Otsu binarization, contour bbox crop, aspect-ratio preserved padding to 224x224).", C_INDIGO),
        ("3. Dual-Track ML Evaluation", "Train, evaluate, and benchmark scikit-learn classical models (Random Forest, Linear SVM, Logistic) and modern Hugging Face Vision Transformer.", C_PURPLE),
        ("4. Calibrated Biometric Metrics", "Calibrate decision boundaries on validation writers using Equal Error Rate (EER) and Platt scaling; measure FAR, FRR, TAR, and ROC-AUC.", C_EMERALD),
        ("5. Multi-Factor Risk Engine", "Synthesize biometric similarity with forensic image quality, monetary transaction tiers, and channel severity into an explainable composite risk score.", C_AMBER),
        ("6. Enterprise Backend & Relational Storage", "Deliver high-performance FastAPI REST services, 11 PostgreSQL 3NF relational entities, JWT RBAC security, and an immutable audit ledger.", C_ROSE)
    ]

    card_w = Inches(3.64)
    card_h = Inches(2.6)
    gap_x = Inches(0.4)
    gap_y = Inches(0.3)

    for i, (title, desc, col) in enumerate(objectives):
        row = i // 3
        col_idx = i % 3
        x = Inches(0.8) + col_idx * (card_w + gap_x)
        y = Inches(1.45) + row * (card_h + gap_y)

        add_card(slide, x, y, card_w, card_h, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(10.5)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 3,
        "title": "Project Objectives & Scope of Work",
        "explain": [
            "Walk through the 6 core objectives directly derived from the approved project synopsis.",
            "Highlight that the project spans the entire full-stack lifecycle: Computer Vision preprocessing, ML modeling, Biometric evaluation, Risk synthesis, Backend engineering, and Database auditability.",
            "Emphasize the dual-track machine learning approach: evaluating both classical scikit-learn models and modern Hugging Face Transformers."
        ],
        "takeaway": "SIGNATURE VMAKE is an end-to-end engineered system, not just an isolated ML script, delivering a fully integrated banking solution.",
        "question": "What is the difference between verification and identification in biometrics?",
        "answer": "Identification is a 1-to-N search asking 'Who is this person?'. Verification is a 1-to-1 comparison asking 'Is this signature truly from customer X?'. SIGNATURE VMAKE is a 1-to-1 (and 1-to-gallery) verification system."
    }
    set_speaker_notes(slide, notes)


def build_slide_4(prs):
    """Slide 4: Solution Overview & End-to-End Pipeline"""
    slide = add_base_slide(prs, "Solution Overview: End-to-End Verification Pipeline", "System Pipeline", 4)

    # Top Pipeline Diagram Image
    pipe_img = ASSET_DIR / "pipeline_diagram.png"
    if pipe_img.exists():
        slide.shapes.add_picture(str(pipe_img), Inches(0.8), Inches(1.4), Inches(11.733), Inches(2.2))

    # Bottom 3 Detailed Explanatory Cards
    cards = [
        ("Phase 1: Ingestion & CV Preprocessing",
         "• Strict magic-byte and MIME whitelist validation (.png, .jpg, .tiff, .bmp)\n• Bilateral/Gaussian smoothing filter suppresses paper grain\n• Otsu adaptive thresholding isolates ink strokes from background\n• Contour bounding-box extraction with 10px boundary margin\n• Aspect-ratio preserved scaling to 224x224 with symmetric zero padding",
         C_CYAN),
        ("Phase 2: Representation & Inference",
         "• Track A (scikit-learn): 264-d handcrafted feature vector (Sobel HOG gradients, 8x8 spatial stroke density, projections, aspect ratio invariants)\n• Track B (Hugging Face): 196 self-attention patch tokens (16x16) via DeiT-Tiny backbone mapped to 128-d unit hypersphere\n• Validation-calibrated operating threshold comparison",
         C_AMBER),
        ("Phase 3: Risk Assessment & Action",
         "• Multi-Factor Fraud Risk Engine combines similarity score with forensic image blur variance, transaction monetary tier, and channel risk\n• Tri-State Banking Output:\n  - VERIFIED: Autonomous clearance (<0.25 Risk)\n  - MANUAL REVIEW: Escalated to officer maker-checker queue\n  - REJECTED: Auto-blocked transaction with audit event",
         C_EMERALD)
    ]

    cw = Inches(3.64)
    ch = Inches(3.2)
    gap = Inches(0.4)
    for i, (title, desc, col) in enumerate(cards):
        x = Inches(0.8) + i * (cw + gap)
        y = Inches(3.8)
        add_card(slide, x, y, cw, ch, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.18), y + Inches(0.18), cw - Inches(0.36), ch - Inches(0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 4,
        "title": "Solution Overview & End-to-End Pipeline",
        "explain": [
            "Present the horizontal dataflow from document scan upload to final regulatory clearance.",
            "Explain Phase 1: Image normalization ensures that lighting, paper color, and scanner resolution do not distort the AI model.",
            "Explain Phase 2: Feature extraction maps pixels into mathematical representations (HOG gradients or ViT attention tokens).",
            "Explain Phase 3: The decision engine combines biometrics with business context to make safe banking decisions."
        ],
        "takeaway": "Verification is not merely comparing two images; it requires rigorous preprocessing, dual-track representation extraction, and business-aware risk scoring.",
        "question": "Why is aspect-ratio preserved scaling critical during preprocessing?",
        "answer": "If you naively stretch or squash a signature to 224x224, you distort its stroke slant, aspect ratio, and loop shapes—which are critical forensic identifiers for distinguishing genuine handwriting from forgeries."
    }
    set_speaker_notes(slide, notes)


def build_slide_5(prs):
    """Slide 5: System Architecture"""
    slide = add_base_slide(prs, "Multi-Tier System Architecture", "System Design", 5)

    # Top Architecture Diagram Image
    arch_img = ASSET_DIR / "architecture_diagram.png"
    if arch_img.exists():
        slide.shapes.add_picture(str(arch_img), Inches(0.8), Inches(1.4), Inches(11.733), Inches(2.6))

    # Bottom 4 Component Detail Cards
    layers = [
        ("Presentation Layer", "7 independent HTML pages with clean URL routing:\n• Overview Dashboard (/)\n• Manual Workflow (/manual-workflow)\n• Cheque Studio (/verification-studio)\n• Model Comparison (/model-comparison)\n• Compliance Queue (/compliance-queue)\n• Audit Trail (/audit-timeline)\n• Model Registry (/model-registry)", C_CYAN),
        ("API Gateway & Security", "FastAPI Asynchronous Gateway (42 REST endpoints):\n• JWT HS256 Token Auth & RBAC (ADMIN, OFFICER, AUDITOR)\n• Upload Validation (MIME whitelist, magic bytes, 5MB ceiling)\n• CORS Middleware & OpenAPI 3.1.0 Interactive Docs", C_INDIGO),
        ("Application & ML Engine", "Autonomous Verification Orchestration:\n• OpenCV Authoritative Preprocessor Pipeline\n• Model Verifier Factory (ViT Default, RF Champion, SVM, Logistic)\n• Multi-Factor Fraud Risk Engine (4 dimensions)\n• Maker-Checker Adjudication Modal & Override Flow", C_EMERALD),
        ("Storage & Audit Layer", "Enterprise Relational Persistence:\n• PostgreSQL 14+ Relational DB with SQLAlchemy 2.0 ORM\n• 11 3NF Entities with Cascade & Referential Integrity\n• Local Encrypted Document Vault (Enrolled & Submitted)\n• Cryptographic SHA-256 Tamper-Evident Audit Ledger", C_AMBER)
    ]

    cw = Inches(2.7)
    ch = Inches(2.8)
    gap = Inches(0.31)
    for i, (title, desc, col) in enumerate(layers):
        x = Inches(0.8) + i * (cw + gap)
        y = Inches(4.2)
        add_card(slide, x, y, cw, ch, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), cw - Inches(0.3), ch - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(4)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(8.5)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 5,
        "title": "Multi-Tier System Architecture",
        "explain": [
            "Walk through the four architectural tiers: Presentation, API Gateway, Application/ML Engine, and Storage/Audit.",
            "Explain that the frontend consists of 7 real, independently addressable pages, eliminating hash-based navigation.",
            "Detail the FastAPI gateway with 42 asynchronous endpoints, JWT security, and RBAC.",
            "Highlight the PostgreSQL database containing 11 3NF relational entities and the SHA-256 immutable audit ledger."
        ],
        "takeaway": "The system follows enterprise software engineering principles: clean separation of concerns, asynchronous throughput, strict RBAC, and relational referential integrity.",
        "question": "Why did you choose FastAPI over Flask or Django for this banking system?",
        "answer": "FastAPI is built on Starlette and Pydantic, offering native asynchronous I/O (ASGI), sub-millisecond serialization overhead, automatic OpenAPI 3.1.0 interactive documentation, and robust request validation, making it ideal for high-concurrency banking APIs."
    }
    set_speaker_notes(slide, notes)


def build_slide_6(prs):
    """Slide 6: Technology Stack"""
    slide = add_base_slide(prs, "Technology Stack & Architectural Roles", "Implementation Details", 6)

    # Technology Table
    table_shape = slide.shapes.add_table(11, 4, Inches(0.8), Inches(1.4), Inches(11.733), Inches(5.6))
    table = table_shape.table
    table.columns[0].width = Inches(1.8)
    table.columns[1].width = Inches(2.5)
    table.columns[2].width = Inches(1.4)
    table.columns[3].width = Inches(6.033)

    headers = ["Category", "Technology", "Version", "Specific Architectural Role & Implementation"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

    rows_data = [
        ("Core Runtime", "Python", "3.11.9", "Asynchronous service execution, model runtime, and pipeline orchestration."),
        ("Classical ML", "scikit-learn", "1.6.1", "Random Forest (100 trees), Linear SVM, Logistic Regression, Platt scaling, and ROC/EER metrics."),
        ("Deep Learning", "Hugging Face Transformers", "4.49.0", "Vision Transformer (facebook/deit-tiny-patch16-224) patch self-attention visual backbone."),
        ("REST API", "FastAPI", "0.115.11", "Asynchronous REST gateway, 42 endpoints, Pydantic validation, and OpenAPI 3.1.0 documentation."),
        ("Computer Vision", "OpenCV (opencv-python)", "4.11.0.86", "Image preprocessing, Otsu binarization, contour bounding box, aspect-preserved padding, and blur variance."),
        ("Execution Backend", "PyTorch", "2.6.0", "Underlying tensor computation and execution backend required by Hugging Face Transformers."),
        ("Matrix & Data", "NumPy & Pandas", "1.26.4 / 2.2.3", "High-performance vector operations, distance metrics, and dataset pair manifest processing."),
        ("Relational Database", "PostgreSQL / SQLAlchemy", "14+ / 2.0.38", "Enterprise 3NF relational database with 11 entities, foreign keys, and Alembic migrations."),
        ("Automated Testing", "Pytest & HTTPX", "9.1.1 / 0.28.1", "Complete automated test suite (53 tests passed) and asynchronous HTTP integration client."),
        ("Containerization", "Docker & Docker Compose", "v2+", "Multi-container orchestration for FastAPI web service and PostgreSQL database.")
    ]

    for row_idx, rdata in enumerate(rows_data, start=1):
        for col_idx, text in enumerate(rdata):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(15, 23, 42) if row_idx % 2 == 1 else RGBColor(20, 29, 47)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_BODY
            p.font.size = Pt(9)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_AMBER
            elif col_idx == 1:
                p.font.bold = True
                p.font.color.rgb = C_TEXT_WHITE
            elif col_idx == 2:
                p.font.color.rgb = C_EMERALD
            else:
                p.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 6,
        "title": "Technology Stack & Architectural Roles",
        "explain": [
            "Review each technology in the stack and explain its exact role.",
            "Highlight the four core technologies required by the project mandate: Python, scikit-learn, Hugging Face Transformers, and FastAPI.",
            "Clarify that PyTorch is strictly utilized as the tensor execution backend for the Hugging Face Vision Transformer, not as an unrelated Siamese network identity.",
            "Emphasize the production-ready supporting technologies: PostgreSQL 3NF storage, OpenCV image processing, and Pytest automated validation."
        ],
        "takeaway": "Every technology selected has a distinct, verified role in the architecture, strictly adhering to the approved project specification.",
        "question": "Why is scikit-learn included alongside deep learning Hugging Face Transformers?",
        "answer": "In banking, classical models like Random Forest and SVM provide extreme compute efficiency (6–10 ms latency, 2 MB size) and strong interpretability on handcrafted features, while Vision Transformers provide deep visual patch representations that capture stroke continuity without manual engineering."
    }
    set_speaker_notes(slide, notes)


def build_slide_7(prs):
    """Slide 7: Dataset & Writer-Disjoint Open-Set Protocol"""
    slide = add_base_slide(prs, "Dataset Architecture & Open-Set Validation Protocol", "Biometric Forensics", 7)

    # Left Card: CEDAR Benchmark
    add_card(slide, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_CYAN)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "CEDAR SIGNATURE BENCHMARK"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(12)

    specs = [
        ("Benchmark Source:", "Center of Excellence for Document Analysis and Recognition (CEDAR), University at Buffalo."),
        ("Distinct Writers:", "55 human subjects (Writers 1 to 55)."),
        ("Total Signatures:", "2,640 offline scanned signature specimens."),
        ("Genuine Signatures:", "1,320 authentic specimens (exactly 24 genuine signatures per writer)."),
        ("Skilled Forgeries:", "1,320 forged specimens (exactly 24 skilled forgeries per writer created by imitating authentic writing)."),
        ("Capture Standard:", "Scanned at 300 DPI, 8-bit grayscale, representing standard commercial banking document capture quality.")
    ]
    for title, desc in specs:
        p = tf_l.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # Right Card: Writer-Disjoint Protocol
    add_card(slide, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_EMERALD)
    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "STRICT WRITER-DISJOINT OPEN-SET PROTOCOL"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(14)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_EMERALD
    p_r0.space_after = Pt(12)

    splits = [
        ("Training Cohort (Writers 1 to 35):", "2,500 pairs generated exclusively from the first 35 writers. Used strictly to learn visual representations and classical feature discriminators."),
        ("Validation Cohort (Writers 36 to 45):", "1,200 pairs generated from 10 separate writers. Used strictly to determine Equal Error Rate (EER) and calibrate operational decision thresholds."),
        ("Held-out Test Cohort (Writers 46 to 55):", "1,200 pairs generated from 10 completely unseen writers. Locked strictly for final unbiased empirical evaluation."),
        ("THE OPEN-SET MANDATE (0% Leakage):", "Train Writers ≠ Validation Writers ≠ Test Writers\n(Train ∩ Val = ∅, Train ∩ Test = ∅, Val ∩ Test = ∅). Zero writer identity leakage across splits.")
    ]
    for title, desc in splits:
        p = tf_r.add_paragraph()
        p.text = f"{title}\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_AMBER if "MANDATE" in title else C_TEXT_WHITE
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = f"{desc}\n"
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    p_why = tf_r.add_paragraph()
    p_why.text = "Why this is critical for banking:\nIn a closed-set test, signatures from the same writer appear in both training and test sets, leading to identity memorization and artificially high metrics. A true banking system must verify new, unseen customers writer-independently."
    p_why.font.name = FONT_BODY
    p_why.font.size = Pt(9.5)
    p_why.font.color.rgb = C_CYAN

    notes = {
        "slide_num": 7,
        "title": "Dataset Architecture & Open-Set Validation Protocol",
        "explain": [
            "Detail the CEDAR dataset: 55 writers, 2,640 signatures evenly divided between genuine and skilled forgeries.",
            "Explain writer-disjoint open-set splitting: Writers 1-35 for Training, 36-45 for Validation, and 46-55 for Testing.",
            "Emphasize the mathematical rule: Train ∩ Val = ∅, Train ∩ Test = ∅, Val ∩ Test = ∅.",
            "Explain why closed-set splitting is unacceptable in banking: banks verify new accounts that the AI has never encountered before."
        ],
        "takeaway": "Writer-disjoint splitting guarantees zero identity leakage, ensuring that test benchmarks reflect true real-world generalization to new banking customers.",
        "question": "What happens if a signature verification model is evaluated on a random split instead of a writer-disjoint split?",
        "answer": "A random split leaks signatures of the same writer into both train and test sets. The model ends up memorizing specific individual handwriting styles rather than learning genuine-versus-forgery visual discrepancies, producing overly optimistic, non-generalizable results."
    }
    set_speaker_notes(slide, notes)


def build_slide_8(prs):
    """Slide 8: Computer Vision Preprocessing Pipeline"""
    slide = add_base_slide(prs, "Authoritative Computer Vision Preprocessing Pipeline", "Image Preprocessing", 8)

    stages = [
        ("Step 1: Multi-Format Ingestion", "Decodes scanned documents in PNG, JPEG, TIFF, or BMP formats from bank branch capture devices.", C_CYAN),
        ("Step 2: Grayscale & Polarity Normalization", "Converts multi-channel RGB/RGBA into single-channel 8-bit luminance, flattening transparency channels.", C_INDIGO),
        ("Step 3: Gaussian Noise Suppression", "Applies 3x3 Gaussian smoothing filter to eliminate paper scanner grain, fiber noise, and dust artifacts.", C_PURPLE),
        ("Step 4: Otsu Adaptive Binarization", "Calculates optimal bimodal threshold separating ink strokes from background; inverts polarity (ink=255, bg=0).", C_EMERALD),
        ("Step 5: Morphological Stroke Extraction", "Applies contour detection to find the exact perimeter of ink strokes, filtering out pre-printed cheque guide lines.", C_AMBER),
        ("Step 6: Tight Cropping with Safety Padding", "Crops bounding box directly around signature strokes with a 10px perimeter safety margin.", C_ROSE),
        ("Step 7: Aspect-Ratio Preserved Scaling", "Proportionally scales longest stroke dimension to fit 224px, adding symmetric zero padding to reach 224x224.", C_CYAN),
        ("Step 8: Float32 Pixel Normalization", "Scales integer pixel intensities [0, 255] into normalized float32 tensor range [0.0, 1.0] for model inference.", C_EMERALD)
    ]

    card_w = Inches(2.7)
    card_h = Inches(2.6)
    gap_x = Inches(0.31)
    gap_y = Inches(0.3)

    for i, (title, desc, col) in enumerate(stages):
        row = i // 4
        col_idx = i % 4
        x = Inches(0.8) + col_idx * (card_w + gap_x)
        y = Inches(1.45) + row * (card_h + gap_y)

        add_card(slide, x, y, card_w, card_h, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.15), y + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(4)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(9)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 8,
        "title": "Authoritative Computer Vision Preprocessing Pipeline",
        "explain": [
            "Walk through the 8 sequential stages of the authoritative OpenCV preprocessor pipeline.",
            "Explain that this exact pipeline is universally utilized across dataset generation, training, customer enrollment, and real-time verification.",
            "Explain Otsu binarization: it automatically finds the threshold that minimizes intra-class variance between ink and paper.",
            "Highlight aspect-ratio preserved scaling: preserves the biometric geometry of signatures without stretching or distortion."
        ],
        "takeaway": "Standardized preprocessing isolates pure biometric stroke characteristics from document background noise, lighting variations, and scanning resolution differences.",
        "question": "Why use Otsu binarization instead of a fixed threshold like 128?",
        "answer": "Cheques and vouchers have different paper background colors, watermark textures, and scanner exposure levels. A fixed threshold fails on dark paper or faded ink, whereas Otsu calculates the optimal bimodal threshold dynamically based on image histogram variance."
    }
    set_speaker_notes(slide, notes)


def build_slide_9(prs):
    """Slide 9: Machine Learning Models: Classical ML vs. Vision Transformer"""
    slide = add_base_slide(prs, "Machine Learning Architecture: Classical ML vs. Vision Transformer", "ML Architecture", 9)

    # Left Card: Track A Classical ML
    add_card(slide, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_AMBER)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "TRACK A — SCIKIT-LEARN CLASSICAL ML"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = C_AMBER
    p0.space_after = Pt(10)

    p_feat = tf_l.add_paragraph()
    p_feat.text = "264-Dimensional Handcrafted Feature Engineering:\n• Directional HOG Histograms (Sobel gradient angles across 8 orientation bins)\n• 8x8 Spatial Grid Stroke Densities (local ink distribution)\n• Horizontal & Vertical Projection Profiles (stroke projection dynamics)\n• Morphological Invariants (aspect ratio, perimeter occupancy, compactness)\n"
    p_feat.font.name = FONT_BODY
    p_feat.font.size = Pt(9.5)
    p_feat.font.color.rgb = C_TEXT_MUTED
    p_feat.space_after = Pt(8)

    models_a = [
        ("Candidate 1: Random Forest Classifier (Track A Champion)",
         "Ensemble of 100 decorrelated decision trees. Exceptional at capturing non-linear interactions between stroke density and gradient directions.\nAUC: 0.9424 | EER: 13.33% | Accuracy: 82.92% | Latency: 10.23 ms", C_EMERALD),
        ("Candidate 2: Linear Support Vector Machine (SVM)",
         "Finds optimal maximum-margin hyperplane separating genuine and forged feature differences with Platt probability scaling.\nAUC: 0.8574 | EER: 19.00% | Accuracy: 79.17% | Latency: 6.03 ms", C_CYAN),
        ("Candidate 3: Logistic Regression (Ultra-Lightweight Baseline)",
         "L2-regularized linear model. Extremely compact (20 KB) with fast inference.\nAUC: 0.8808 | EER: 18.83% | Accuracy: 80.50% | Latency: 6.00 ms", C_PURPLE)
    ]
    for title, desc, col in models_a:
        p = tf_l.add_paragraph()
        p.text = f"{title}\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = col
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.size = Pt(9)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(6)

    # Right Card: Track B Vision Transformer
    add_card(slide, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_CYAN)
    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "TRACK B — HUGGING FACE VISION TRANSFORMER"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(14)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_CYAN
    p_r0.space_after = Pt(10)

    vit_points = [
        ("Architecture & Visual Backbone:",
         "Utilizes facebook/deit-tiny-patch16-224 (Data-efficient Image Transformer) pre-trained on ImageNet and fine-tuned for signature metric learning."),
        ("Patch Self-Attention Tokenization:",
         "Deconstructs standardized 224x224 signature image into 196 non-overlapping 16x16 spatial patches. Linear projection maps patches into embedding sequences."),
        ("12 Multi-Head Attention Layers:",
         "Captures global stroke trajectory continuity, loop curvature, and stroke pressure gradients across the entire canvas without manual feature engineering."),
        ("Metric Projection Head:",
         "Dense projection head maps visual transformer representations into a compact 128-dimensional unit hypersphere (||u||_2 = 1.0) for cosine similarity comparison."),
        ("Empirical Biometric Profile:",
         "• False Rejection Rate (FRR): 3.83% (True Acceptance Rate: 96.17%)\n• Operating Threshold: 0.7313 (Cosine similarity threshold)\n• Single-Pair Latency: 36.66 ms | Checkpoint Size: 21.73 MB\n• Role: Production Default Model prioritizing authentic customer experience.")
    ]
    for title, desc in vit_points:
        p = tf_r.add_paragraph()
        p.text = f"{title}\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.size = Pt(9)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(6)

    notes = {
        "slide_num": 9,
        "title": "Machine Learning Models: Classical ML vs. Vision Transformer",
        "explain": [
            "Detail Track A: Handcrafted 264-d feature engineering capturing HOG gradients, spatial grid stroke densities, and aspect ratio invariants.",
            "Explain that Random Forest achieved the highest overall open-set discrimination (AUC: 0.9424, EER: 13.33%) by modeling non-linear interactions across stroke regions.",
            "Detail Track B: The Hugging Face Vision Transformer (DeiT-Tiny) uses patch self-attention to understand stroke trajectories globally without manual feature design.",
            "Highlight that the Vision Transformer achieves an ultra-low False Rejection Rate of 3.83% (96.17% True Acceptance), ensuring legitimate bank customers are virtually never falsely rejected."
        ],
        "takeaway": "SIGNATURE VMAKE leverages the best of both worlds: classical ML for ultra-fast, high-precision forensic discrimination and Vision Transformers for deep global stroke representation.",
        "question": "How does a Vision Transformer process a 2D signature image?",
        "answer": "It divides the 224x224 image into a grid of 196 patches (each 16x16 pixels). Each patch is linearly projected into a vector and treated as a visual token. 12 layers of multi-head self-attention allow every token to interact with all other tokens, capturing stroke trajectory and connectivity across the entire signature."
    }
    set_speaker_notes(slide, notes)


def build_slide_10(prs):
    """Slide 10: Manual Registration & Two-Step Verification Workflow"""
    slide = add_base_slide(prs, "Manual Signature Registration & Two-Step Verification Workflow", "Banking Workflow", 10)

    # Top Workflow Diagram
    wf_img = ASSET_DIR / "dual_step_workflow.png"
    if wf_img.exists():
        slide.shapes.add_picture(str(wf_img), Inches(0.8), Inches(1.35), Inches(11.733), Inches(2.7))

    # Bottom 2 Detailed Process Cards
    add_card(slide, Inches(0.8), Inches(4.2), Inches(5.7), Inches(2.8), border_color=C_CYAN)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(4.3), Inches(5.3), Inches(2.5))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "STEP 1: CUSTOMER & REFERENCE SPECIMEN ENROLLMENT"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(4)

    p_l_body = tf_l.add_paragraph()
    p_l_body.text = "1. Customer Profile Association: Officer enters customer ID and selects account.\n2. Specimen Upload (POST /api/v1/customers/{id}/signatures): Scanned reference is uploaded, validated, and normalized via OpenCV.\n3. Vault Storage & Feature Indexing: Biometric feature vector is computed and stored.\n4. MANDATORY BANKING RULE: First upload enrolls the reference specimen ONLY. It receives ZERO similarity score, ZERO verdict, and ZERO verification decision.\n5. Specimen Gallery Management: Supports up to 3 active enrolled specimens; soft-deactivation (SUPERSEDED) preserves complete audit history."
    p_l_body.font.name = FONT_BODY
    p_l_body.font.size = Pt(9)
    p_l_body.font.color.rgb = C_TEXT_MUTED

    add_card(slide, Inches(6.8), Inches(4.2), Inches(5.7), Inches(2.8), border_color=C_AMBER)
    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(4.3), Inches(5.3), Inches(2.5))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "STEP 2: QUESTIONED SIGNATURE DYNAMIC VERIFICATION"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(12)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_AMBER
    p_r0.space_after = Pt(4)

    p_r_body = tf_r.add_paragraph()
    p_r_body.text = "1. Questioned Ingestion (POST /api/v1/verifications/verify-manual): Cheque voucher or withdrawal form signature is uploaded.\n2. Comparison Mode Selection:\n   • Mode 1: Compares against a specific enrolled reference specimen ID.\n   • Mode 2 (Gallery Mode): Evaluates against all active customer specimens using Max/Mean/Min similarity aggregation.\n3. Dynamic Model Dispatch: Operator chooses ViT Default, RF Champion, SVM, or Logistic.\n4. Real-Time Scoring: Computes calibrated score, compares to operating threshold, evaluates multi-factor risk, and yields banking action (VERIFIED / REVIEW / REJECTED)."
    p_r_body.font.name = FONT_BODY
    p_r_body.font.size = Pt(9)
    p_r_body.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 10,
        "title": "Manual Signature Registration & Two-Step Verification Workflow",
        "explain": [
            "Emphasize the strict banking separation between Step 1 (Registration) and Step 2 (Verification).",
            "Quote the key banking specification: 'The first signature is registered as the reference specimen and does not receive a verification verdict.'",
            "Explain that the specimen gallery allows customers to have multiple authentic reference specimens (e.g. formal vs quick signature).",
            "Explain Step 2: Verification dynamically tests the questioned signature against the reference gallery and calculates both biometric match and multi-factor risk."
        ],
        "takeaway": "Registration establishes the baseline identity vault without premature verdicts; verification evaluates questioned documents dynamically with full auditability.",
        "question": "Why shouldn't the first uploaded signature receive a verification score?",
        "answer": "Because verification requires comparing a questioned signature against an existing authentic reference specimen. During initial registration, there is no existing reference to compare against. Claiming a match on the very first upload would be a logical contradiction in biometric authentication."
    }
    set_speaker_notes(slide, notes)


def build_slide_11(prs):
    """Slide 11: Empirical Model Comparison & Benchmark Results"""
    slide = add_base_slide(prs, "Empirical Model Comparison & Benchmark Evaluation", "Model Evaluation", 11)

    # Benchmark Table on Held-Out Test Cohort (Writers 46-55, 1,200 pairs)
    table_shape = slide.shapes.add_table(5, 11, Inches(0.8), Inches(1.35), Inches(11.733), Inches(2.2))
    table = table_shape.table
    col_widths = [Inches(1.8), Inches(1.1), Inches(0.9), Inches(1.0), Inches(0.9), Inches(1.0), Inches(0.9), Inches(0.9), Inches(1.0), Inches(1.0), Inches(1.233)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w

    headers = ["Model Candidate", "Size", "Latency", "Threshold", "ROC-AUC", "EER", "Accuracy", "FAR", "FRR", "TAR", "F1 Score"]
    for col_idx, h in enumerate(headers):
        cell = table.cell(0, col_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(30, 41, 59)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = FONT_HEADING
        p.font.size = Pt(8.5)
        p.font.bold = True
        p.font.color.rgb = C_CYAN

    data = [
        ("Random Forest (Champion)", "2.39 MB", "10.23 ms", "0.4264", "0.9424", "13.33%", "82.92%", "30.33%", "3.83%", "96.17%", "0.8492"),
        ("Logistic Regression", "0.02 MB", "6.00 ms", "0.2015", "0.8808", "18.83%", "80.50%", "27.00%", "12.00%", "88.00%", "0.8186"),
        ("Linear SVM Baseline", "1.90 MB", "6.03 ms", "0.3636", "0.8574", "19.00%", "79.17%", "28.50%", "13.17%", "86.83%", "0.8065"),
        ("Vision Transformer (ViT)", "21.73 MB", "36.66 ms", "0.7313", "0.7947", "27.67%", "64.50%", "67.17%", "3.83%", "96.17%", "0.7304")
    ]
    for row_idx, rdata in enumerate(data, start=1):
        for col_idx, text in enumerate(rdata):
            cell = table.cell(row_idx, col_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(15, 23, 42) if row_idx % 2 == 1 else RGBColor(20, 29, 47)
            p = cell.text_frame.paragraphs[0]
            p.text = text
            p.font.name = FONT_BODY
            p.font.size = Pt(8)
            if col_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_EMERALD if "Champion" in text else C_TEXT_WHITE
            elif col_idx in [4, 5, 9, 10]:
                p.font.bold = True
                p.font.color.rgb = C_CYAN
            else:
                p.font.color.rgb = C_TEXT_MUTED

    # Bottom Two Comparison Charts (ROC-AUC & EER)
    auc_img = ASSET_DIR / "roc_auc_chart.png"
    if auc_img.exists():
        slide.shapes.add_picture(str(auc_img), Inches(0.8), Inches(3.7), Inches(5.7), Inches(3.3))

    eer_img = ASSET_DIR / "eer_chart.png"
    if eer_img.exists():
        slide.shapes.add_picture(str(eer_img), Inches(6.8), Inches(3.7), Inches(5.7), Inches(3.3))

    notes = {
        "slide_num": 11,
        "title": "Empirical Model Comparison & Benchmark Results",
        "explain": [
            "Present the verified test benchmark table evaluated on the locked held-out test cohort of 1,200 pairs (Writers 46 to 55).",
            "Highlight Random Forest as the Track A Champion with an outstanding ROC-AUC of 0.9424 and Equal Error Rate of 13.33%.",
            "Explain that the Vision Transformer achieves an ultra-low False Rejection Rate of 3.83% (96.17% True Acceptance Rate), matching Random Forest in customer satisfaction.",
            "Discuss the trade-offs: Random Forest provides superior forgery discrimination on HOG features; Vision Transformer captures deep visual representations with zero manual feature engineering."
        ],
        "takeaway": "Random Forest achieves the highest biometric discrimination (0.9424 AUC), while Vision Transformer matches its ultra-low False Rejection Rate (3.83%) to prevent legitimate customer friction.",
        "question": "What is Equal Error Rate (EER) and why is it used as the primary biometric evaluation metric?",
        "answer": "EER is the operating point where the False Acceptance Rate (FAR) equals the False Rejection Rate (FRR). A lower EER indicates superior overall discriminatory ability because it balances security against customer convenience."
    }
    set_speaker_notes(slide, notes)


def build_slide_12(prs):
    """Slide 12: Decision & Fraud Risk Engine"""
    slide = add_base_slide(prs, "Multi-Factor Fraud Risk Engine & Tri-State Banking Actions", "Risk Engine", 12)

    # Left Card: Risk Formulation & Donut Chart
    add_card(slide, Inches(0.8), Inches(1.4), Inches(6.0), Inches(5.6), border_color=C_CYAN)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(1.5), Inches(5.6), Inches(2.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "MULTI-FACTOR COMPOSITE RISK FORMULATION"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(4)

    p_form = tf_l.add_paragraph()
    p_form.text = "Overall Risk = 0.50 × Similarity Risk + 0.15 × Quality Risk\n             + 0.25 × Transaction Risk + 0.10 × Behavioral Risk"
    p_form.font.name = "Consolas"
    p_form.font.size = Pt(9.5)
    p_form.font.bold = True
    p_form.font.color.rgb = C_AMBER
    p_form.space_after = Pt(4)

    p_desc = tf_l.add_paragraph()
    p_desc.text = "• Similarity Risk (50%): Calibrated to model threshold τ*. (Low 0.0-0.20 if S >= τ*; High 0.50-1.0 if S < τ*).\n• Image Quality Risk (15%): Evaluates Laplacian blur variance and dynamic contrast (1.0 - Quality Score).\n• Transaction Risk (25%): Tiered amount scaling (≤$1k to >$100k) + settlement channel severity (Cheque 0.25, Wire 0.70).\n• Behavioral Risk (10%): Flags repeat historical verification anomalies."
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(8.5)
    p_desc.font.color.rgb = C_TEXT_MUTED

    # Donut Chart Image
    donut_img = ASSET_DIR / "risk_weights_chart.png"
    if donut_img.exists():
        slide.shapes.add_picture(str(donut_img), Inches(1.4), Inches(3.9), Inches(4.8), Inches(2.9))

    # Right Card: Tri-State Banking Decisions
    add_card(slide, Inches(7.1), Inches(1.4), Inches(5.4), Inches(5.6), border_color=C_EMERALD)
    tb_r = slide.shapes.add_textbox(Inches(7.3), Inches(1.5), Inches(5.0), Inches(5.3))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "TRI-STATE OPERATIONAL BANKING DECISIONS"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(13)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_EMERALD
    p_r0.space_after = Pt(8)

    tiers = [
        ("TIER 1: VERIFIED (Straight-Through Clearance)",
         "Condition: Biometric Similarity S ≥ τ* AND Composite Risk < 0.25 (LOW).\nAction: Transaction clears instantly without human intervention. Straight-through clearing and settlement.", C_EMERALD),
        ("TIER 2: MANUAL REVIEW (Maker-Checker Queue)",
         "Condition: Borderline Similarity (S ≥ τ* - 0.12) OR Composite Risk 0.25 ≤ Risk < 0.60 (MEDIUM).\nAction: Transaction held. Escalated to officer compliance queue with side-by-side inspection and mandatory commentary.", C_AMBER),
        ("TIER 3: REJECTED (Automated Fraud Block)",
         "Condition: Similarity S < τ* - 0.12 OR Composite Risk ≥ 0.60 (HIGH).\nAction: Transaction auto-blocked, account flagged, and immutable fraud incident recorded in regulatory audit trail.", C_ROSE)
    ]
    for title, desc, col in tiers:
        p = tf_r.add_paragraph()
        p.text = f"{title}\n"
        p.font.name = FONT_HEADING
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.size = Pt(9)
        run.font.color.rgb = C_TEXT_MUTED
        p.space_after = Pt(10)

    p_note = tf_r.add_paragraph()
    p_note.text = "Biometric Result vs Banking Decision:\nBiometric output is binary (MATCH / NO MATCH). The banking decision (VERIFIED / REVIEW / REJECTED) is a contextual business judgment combining biometrics with financial exposure."
    p_note.font.name = FONT_BODY
    p_note.font.size = Pt(8.5)
    p_note.font.color.rgb = C_CYAN

    notes = {
        "slide_num": 12,
        "title": "Multi-Factor Fraud Risk Engine & Tri-State Banking Actions",
        "explain": [
            "Detail the exact multi-factor formula implemented in `services/risk_engine.py`.",
            "Explain the four weighted dimensions: Biometric Similarity (50%), Transaction Exposure (25%), Physical Image Quality (15%), and Customer Behavioral History (10%).",
            "Clearly distinguish between the biometric verdict (MATCH / NO MATCH) and the regulatory banking decision (VERIFIED / MANUAL REVIEW / REJECTED).",
            "Explain the Maker-Checker workflow: borderline cases or high-value cheques are escalated to compliance officers for manual adjudication."
        ],
        "takeaway": "Biometric similarity alone is insufficient for banking; the multi-factor risk engine contextualizes similarity with cheque value and document quality to prevent fraud.",
        "question": "Can a signature have a biometric MATCH but still be routed to MANUAL REVIEW?",
        "answer": "Yes! If an authentic signature appears on a $250,000 wire transfer or has a blurred scan (low Laplacian variance), the elevated transaction risk factor increases the composite risk score into the MEDIUM tier, triggering mandatory officer maker-checker review."
    }
    set_speaker_notes(slide, notes)


def build_slide_13(prs):
    """Slide 13: FastAPI Backend, Relational Database & Enterprise Security"""
    slide = add_base_slide(prs, "FastAPI Backend, Relational Database & Enterprise Security", "Enterprise Architecture", 13)

    pillars = [
        ("FastAPI REST Gateway",
         "• High-Performance ASGI Engine: Non-blocking asynchronous event loop for sub-second verification throughput.\n• 42 Endpoints across 7 Routers: Pages, Auth, Customers, Signatures, Transactions, Verifications, Models, Audit.\n• Interactive OpenAPI 3.1.0 Docs: Automatically exposed at /docs (Swagger UI) and /redoc.\n• Strict Pydantic Data Contracts: Strong typing, request schema validation, and serialized response schemas.\n• CORS & Reverse Proxy Ready: Configured for production deployment with Docker and cloud CDNs.",
         C_CYAN),
        ("Relational Database (11 Entities)",
         "• PostgreSQL 14+ Relational Storage: Full 3NF schema engineered for financial integrity and compliance.\n• 11 Relational Entities:\n  1. User (Auth & RBAC)\n  2. Customer (Master profile)\n  3. Account (Ledger balances)\n  4. Signature (Vault specimens)\n  5. SignatureEmbedding (Vectors)\n  6. Transaction (Vouchers)\n  7. VerificationAttempt (Logs)\n  8. RiskAssessment (4 components)\n  9. ManualReview (Adjudications)\n  10. AuditLog (Event ledger)\n  11. ModelVersion (ML registry)\n• SQLAlchemy 2.0 ORM & Alembic Migrations.",
         C_INDIGO),
        ("Banking Security & Governance",
         "• JWT Authentication (RFC 7519): Secure token signing with HS256 algorithm and configurable expiration.\n• Role-Based Access Control (RBAC): Strict permission boundaries across ADMIN, OFFICER, and AUDITOR.\n• Multi-Layer Upload Defense:\n  - Magic-byte inspection & MIME whitelist (.png, .jpg, .jpeg, .tiff, .bmp)\n  - 5MB maximum file size ceiling\n  - Path traversal and null-byte sanitization\n• Tamper-Evident SHA-256 Ledger: Immutable audit log linking every attempt to a unique request reference (REQ-XXXXXXXX).",
         C_EMERALD)
    ]

    card_w = Inches(3.64)
    card_h = Inches(5.6)
    gap = Inches(0.4)

    for i, (title, desc, col) in enumerate(pillars):
        x = Inches(0.8) + i * (card_w + gap)
        y = Inches(1.4)
        add_card(slide, x, y, card_w, card_h, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.18), y + Inches(0.18), card_w - Inches(0.36), card_h - Inches(0.36))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(13)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(8)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 13,
        "title": "FastAPI Backend, Relational Database & Enterprise Security",
        "explain": [
            "Review the FastAPI architecture hosting 42 endpoints with OpenAPI 3.1.0 specifications.",
            "Explain the 11 relational entities in `database/models.py` designed in Third Normal Form (3NF).",
            "Detail the security layer: JWT tokens with HS256, Role-Based Access Control, magic-byte upload validation, and path traversal defense.",
            "Highlight the non-repudiation audit ledger: every single verification, registration, and adjudication creates an immutable log entry with SHA-256 integrity."
        ],
        "takeaway": "SIGNATURE VMAKE satisfies real-world banking compliance with robust relational modeling, strict role-based authorization, and tamper-evident audit logging.",
        "question": "How does the system prevent malicious file uploads disguised as signatures?",
        "answer": "It implements multi-layer defense: first, checking file size (< 5MB); second, validating file extensions; third, reading actual file magic bytes via Python to verify legitimate image headers (PNG, JPEG, TIFF); fourth, sanitizing filenames to block path traversal attacks."
    }
    set_speaker_notes(slide, notes)


def build_slide_14(prs):
    """Slide 14: System Results & Engineering Validation"""
    slide = add_base_slide(prs, "System Results & Engineering Validation Evidence", "Verification Evidence", 14)

    results = [
        ("Automated Test Suite: 53 / 53 Passed (100%)",
         "Full pytest suite executed in 60.27s across 6 test suites:\n• test_api.py (12 tests) - Endpoints, health, JWT auth, benchmarks\n• test_manual_workflow.py (12 tests) - Enrollment reference rule, gallery, soft-delete\n• test_model_suite.py (9 tests) - HOG extraction, SVM, RF, Logistic, ViT verifiers\n• test_page_routing.py (10 tests) - Independent routes & static asset delivery\n• test_siamese_system.py (9 tests) - Preprocessing, dataset pairing, inference\n• test_traceability.py (1 test) - Full regulatory audit non-repudiation trace",
         C_EMERALD),
        ("System Diagnostics: 16 / 16 Passed (100%)",
         "Authoritative diagnose.py verification across 16 critical health gates:\n• [1-4] Python 3.11.9, 10 dependencies, 4 model checkpoints ready & functional\n• [5-8] CEDAR dataset split, benchmark JSON, SQLite/PostgreSQL, 42 API routes\n• [9-12] Multi-model inference consistency, 5-stage OpenCV pipeline, registration rule\n• [13-16] Manual verification, audit trail integrity, no fake mocks, 7-page MPA",
         C_CYAN),
        ("Multi-Page Routing Parity (7/7 Independent Pages)",
         "Verified clean URL resolution without hash fragments across environments:\n• Local/Docker FastAPI: Direct FileResponse serving dedicated HTML\n• Vercel Serverless CDN: cleanUrls enabled with exact rewrite mappings\n• Persistent Active Route Highlighting across refresh & browser navigation\n• Decentralized modular scripts isolating page failure domains",
         C_PURPLE),
        ("Biometric Security & Regulatory Isolation",
         "Strict empirical validation of security invariants:\n• 0% Identity Leakage: Proven writer-disjoint open-set protocol\n• Customer Vault Isolation: Prohibits cross-customer specimen contamination\n• Soft-Deactivation Auditability: Deactivated specimens marked SUPERSEDED\n• Genuine Acceptance: 96.17% TAR ensuring frictionless legitimate clearance",
         C_AMBER)
    ]

    card_w = Inches(5.6)
    card_h = Inches(2.65)
    gap_x = Inches(0.533)
    gap_y = Inches(0.25)

    for i, (title, desc, col) in enumerate(results):
        row = i // 2
        col_idx = i % 2
        x = Inches(0.8) + col_idx * (card_w + gap_x)
        y = Inches(1.45) + row * (card_h + gap_y)

        add_card(slide, x, y, card_w, card_h, border_color=col)
        tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.name = FONT_HEADING
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = desc
        pd.font.name = FONT_BODY
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 14,
        "title": "System Results & Engineering Validation Evidence",
        "explain": [
            "Present the factual verification evidence proven by tests and diagnostic runs.",
            "Highlight the 53 / 53 pytest test results (100% pass rate) covering APIs, models, workflows, routing, and traceability.",
            "Review the 16 / 16 system diagnostic checks confirming zero broken checkpoints and zero mock/fake implementations.",
            "Confirm multi-page routing parity between local FastAPI and the live Vercel cloud deployment."
        ],
        "takeaway": "Every technical claim is backed by reproducible automated tests and diagnostic execution logs, demonstrating true engineering rigor.",
        "question": "How did you test that the first uploaded signature doesn't produce a verification verdict?",
        "answer": "We have an explicit automated test `test_first_upload_is_strictly_reference_not_verification` in `tests/test_manual_workflow.py` that uploads a specimen to `/api/v1/customers/{id}/signatures` and asserts that the response contains no similarity score, no decision verdict, and returns HTTP 201 Created with status ACTIVE."
    }
    set_speaker_notes(slide, notes)


def build_slide_15(prs):
    """Slide 15: Live Application Demonstration"""
    slide = add_base_slide(prs, "Live Web Application Interface Demonstration", "Application Demo", 15)

    # Hero Screenshot (Manual Workflow)
    hero_img = ASSET_DIR / "screenshot_manual.png"
    if hero_img.exists():
        slide.shapes.add_picture(str(hero_img), Inches(0.8), Inches(1.35), Inches(7.5), Inches(4.3))

    # Right Column: 3 Secondary Screenshots
    right_imgs = [
        ("Overview Dashboard (/)", "screenshot_overview.png"),
        ("Model Comparison Matrix (/model-comparison)", "screenshot_comparison.png"),
        ("Officer Review Queue (/compliance-queue)", "screenshot_queue.png")
    ]
    ry = Inches(1.35)
    rw = Inches(3.9)
    rh = Inches(1.35)
    for title, fname in right_imgs:
        img_path = ASSET_DIR / fname
        if img_path.exists():
            slide.shapes.add_picture(str(img_path), Inches(8.6), ry, rw, rh)
        ry += rh + Inches(0.12)

    # Bottom Banner: Live URL
    add_card(slide, Inches(0.8), Inches(5.8), Inches(11.733), Inches(1.2), border_color=C_CYAN, bg_color=RGBColor(15, 23, 42))
    tb_b = slide.shapes.add_textbox(Inches(1.0), Inches(5.9), Inches(11.3), Inches(1.0))
    tf_b = tb_b.text_frame
    tf_b.word_wrap = True

    p0 = tf_b.paragraphs[0]
    p0.text = "LIVE CLOUD DEPLOYMENT & PRODUCTION REPOSITORIES"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = C_CYAN
    p0.space_after = Pt(2)

    p1 = tf_b.add_paragraph()
    p1.text = "• Production URL: https://signature-verification-rho.vercel.app  (7 independent clean URL pages)\n• GitHub Repositories: neeravjain91-jpg/signature-verification  &  neeravjain91-jpg/signature-v  (Clean working tree, commit 4f9ff79)"
    p1.font.name = FONT_BODY
    p1.font.size = Pt(9.5)
    p1.font.color.rgb = C_TEXT_WHITE

    notes = {
        "slide_num": 15,
        "title": "Live Web Application Interface Demonstration",
        "explain": [
            "Demonstrate the real multi-page banking interface captured live from the production deployment.",
            "Point out the primary hero interface: Manual Register & Verify (`/manual-workflow`), showing Step 1 enrollment, active specimen cards, candidate model dropdown, and Step 2 verification.",
            "Show the secondary interfaces: Executive KPI Dashboard (`/`), Model Benchmark Comparison matrix (`/model-comparison`), and Officer Adjudication Queue (`/compliance-queue`).",
            "Provide the live Vercel URL and GitHub repository links for live examiner inspection."
        ],
        "takeaway": "The frontend is fully operational as an enterprise multi-page application with real API connectivity, live diagnostics, and clean URL routing.",
        "question": "How does the web application connect to the backend if the frontend is hosted on Vercel and the backend is running locally or in Docker?",
        "answer": "The frontend uses a standardized API client (`api.js`) that automatically resolves `window.location.origin` when hosted together, or reads a configurable backend base URL from `localStorage` via the built-in API Configuration modal when decoupled."
    }
    set_speaker_notes(slide, notes)


def build_slide_16(prs):
    """Slide 16: Conclusion & Future Scope"""
    slide = add_base_slide(prs, "Conclusion, Key Achievements & Future Scope", "Project Summary", 16)

    # Left Card: Achievements
    add_card(slide, Inches(0.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_EMERALD)
    tb_l = slide.shapes.add_textbox(Inches(1.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p0 = tf_l.paragraphs[0]
    p0.text = "CONCLUSION & CORE ACHIEVEMENTS"
    p0.font.name = FONT_HEADING
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = C_EMERALD
    p0.space_after = Pt(10)

    achievements = [
        ("BRD-Compliant Architecture:", "Built a complete, production-ready AI signature verification system strictly adhering to Bank Muscat BRD specifications."),
        ("Dual-Track Machine Learning:", "Successfully synthesized classical ML (scikit-learn Random Forest champion: 94.24% AUC) and modern deep visual representations (Hugging Face Vision Transformer: 3.83% FRR)."),
        ("Writer-Disjoint Generalization:", "Enforced 0% identity leakage on the CEDAR benchmark, proving genuine model generalization to unseen banking customers."),
        ("Multi-Factor Fraud Governance:", "Operationalized a 4-dimensional risk engine and maker-checker queue combining biometric similarity with financial exposure."),
        ("Enterprise Full-Stack Backend:", "Delivered 42 FastAPI endpoints, 11 PostgreSQL 3NF relational entities, and a 7-page responsive web application passing 53/53 automated tests.")
    ]
    for title, desc in achievements:
        p = tf_l.add_paragraph()
        p.text = f"• {title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p.space_after = Pt(6)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    # Right Card: Future Scope
    add_card(slide, Inches(6.8), Inches(1.4), Inches(5.7), Inches(5.6), border_color=C_CYAN)
    tb_r = slide.shapes.add_textbox(Inches(7.0), Inches(1.6), Inches(5.3), Inches(5.2))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_r0 = tf_r.paragraphs[0]
    p_r0.text = "FUTURE SCOPE & INDUSTRIAL EXTENSIONS"
    p_r0.font.name = FONT_HEADING
    p_r0.font.size = Pt(14)
    p_r0.font.bold = True
    p_r0.font.color.rgb = C_CYAN
    p_r0.space_after = Pt(10)

    p_tag = tf_r.add_paragraph()
    p_tag.text = "[ Clearly Labeled as Planned Future Scope ]\n"
    p_tag.font.name = FONT_HEADING
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = C_AMBER
    p_tag.space_after = Pt(6)

    future = [
        ("1. Multilingual Indian Datasets:", "Incorporate BHSig260 (Hindi and Bengali scripts) and regional Indian bank signature corpora to support multilingual verification."),
        ("2. Document Forgery Localization:", "Generate spatial heatmaps (Grad-CAM) highlighting exact forged strokes and pen-lift tampering on full-page scanned cheques."),
        ("3. Optical Character Recognition (OCR):", "Integrate automated Tesseract / PaddleOCR to read payee names, written monetary amounts, and E-13B MICR cheque codes."),
        ("4. Online Dynamic Biometric Fusion:", "Fuse offline visual scans with dynamic tablet biometrics (stroke velocity, pen pressure, acceleration, and azimuth angles)."),
        ("5. Continuous Learning & MLOps:", "Implement automated model drift monitoring (Evidently AI / Prometheus) with continuous retraining pipelines managed in MLflow."),
        ("6. Hardware Security Modules (HSM):", "Deploy in enterprise Kubernetes clusters with HSM-backed key management for biometric template encryption at rest.")
    ]
    for title, desc in future:
        p = tf_r.add_paragraph()
        p.text = f"{title} "
        p.font.name = FONT_HEADING
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = C_TEXT_WHITE
        p.space_after = Pt(4)
        run = p.add_run()
        run.text = desc
        run.font.name = FONT_BODY
        run.font.bold = False
        run.font.color.rgb = C_TEXT_MUTED

    notes = {
        "slide_num": 16,
        "title": "Conclusion, Key Achievements & Future Scope",
        "explain": [
            "Conclude the presentation by summarizing the core achievements: BRD alignment, dual-track AI, writer-disjoint splitting, multi-factor risk scoring, and 53/53 passing tests.",
            "Clearly present the future scope items from the approved synopsis: multilingual Indian scripts, document forgery localization, OCR/MICR integration, and MLOps pipelines.",
            "Reiterate that all future scope items are explicitly labeled as planned extensions.",
            "Thank the evaluators and open the floor for questions."
        ],
        "takeaway": "SIGNATURE VMAKE successfully bridges academic machine learning and enterprise banking compliance into a production-grade, extensible biometric platform.",
        "question": "What is the single most valuable technical lesson you learned from this project?",
        "answer": "That building an AI system for banking requires far more than training a model. Real-world success depends on rigorous computer vision preprocessing, open-set dataset splitting with zero leakage, calibrating decision thresholds to business risk, and wrapping models in secure, auditable, high-throughput REST APIs."
    }
    set_speaker_notes(slide, notes)


def generate_viva_markdown():
    """Generates docs/PRESENTATION_VIVA_NOTES.md with full speaker notes and 25+ viva Q&As."""
    md_content = """# SIGNATURE VMAKE — Presentation Speaker Notes & Viva Defense Guide

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
    - **Phase 1: Ingestion & CV Preprocessing**: Magic-byte inspection, Gaussian smoothing, Otsu adaptive binarization, contour bounding box extraction, and aspect-preserved padding to $224 \times 224$.
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
  - Emphasize the open-set mathematical mandate: $\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$.
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
  - Walk through the 8 sequential steps: Loading -> Grayscale -> Gaussian Denoising ($3 \times 3$) -> Otsu Adaptive Binarization -> Contour Stroke Extraction -> Tight Cropping (10px padding) -> Aspect-Ratio Preserved Scaling ($224 \times 224$) -> Float32 Normalization ($[0.0, 1.0]$).
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
  - **Track B (Hugging Face)**: `facebook/deit-tiny-patch16-224` vision backbone. 196 spatial tokens ($16 \times 16$ patches), 12 self-attention layers, 128-d metric projection head ($\|u\|_2 = 1.0$).
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
    $$\text{Overall Risk} = 0.50 \times \text{Similarity Risk} + 0.15 \times \text{Quality Risk} + 0.25 \times \text{Transaction Risk} + 0.10 \times \text{Behavioral Risk}$$
  - Explain each factor: Biometric similarity relative to threshold $\tau^*$, Laplacian blur variance / contrast, monetary tiers ($\le \$1\text{k}$ to $>\$100\text{k}$), channel severity (Cheque 0.25, Wire 0.70), and account anomaly history.
  - Present the Tri-State Banking Actions:
    - **VERIFIED**: $S \ge \tau^*$ and Risk $< 0.25$ (`LOW`). Straight-through clearing.
    - **MANUAL REVIEW**: Borderline similarity or Risk $0.25 - 0.60$ (`MEDIUM`). Escalated to maker-checker queue.
    - **REJECTED**: $S < \tau^* - 0.12$ or Risk $\ge 0.60$ (`HIGH`). Auto-blocked with fraud audit alert.
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
*Answer:* A standard Linear SVM outputs a raw uncalibrated geometric distance from the separating hyperplane ($f(x) \in (-\infty, +\infty)$). Platt scaling fits a sigmoid function $P(y=1|f(x)) = \frac{1}{1 + \exp(A f(x) + B)}$ over the validation set to transform this uncalibrated margin into a true posterior probability between 0.0 and 1.0, enabling direct threshold comparison.

**Q4: Explain how Equal Error Rate (EER) is determined.**  
*Answer:* As you vary the decision threshold $\tau$ from 0 to 1, the False Acceptance Rate (FAR) decreases while the False Rejection Rate (FRR) increases. The threshold where $\text{FAR}(\tau^*) = \text{FRR}(\tau^*)$ is the Equal Error Rate operating point. We determine this threshold on the validation cohort (Writers 36–45) and lock it before evaluating on the test cohort.

**Q5: What is the difference between random forgeries and skilled forgeries?**  
*Answer:* A random forgery (or random impostor) is when a signature from Writer B is presented as belonging to Writer A without attempting to copy Writer A's signature. A skilled forgery is created by a professional or trained individual who observes Writer A's authentic signature and intentionally imitates its geometric shape, slant, and loops. Skilled forgeries are vastly harder to detect.

---

### Section B: Computer Vision Preprocessing

**Q6: What specific kernel size and parameters did you use for Gaussian smoothing, and why?**  
*Answer:* We used a $3 \times 3$ Gaussian smoothing kernel with standard deviation computed automatically ($\sigma=0$). A small $3 \times 3$ kernel effectively suppresses high-frequency scanner CCD sensor grain and paper texture noise without blurring fine stroke boundaries or thinning pen strokes.

**Q7: How does Otsu's thresholding algorithm work?**  
*Answer:* Otsu's algorithm iterates through all possible pixel intensity thresholds ($t \in [0, 255]$) and calculates the between-class variance $\sigma_B^2(t) = \omega_0(t)\omega_1(t)[\mu_0(t) - \mu_1(t)]^2$ between foreground and background pixel distributions. The threshold that maximizes between-class variance (equivalent to minimizing intra-class variance) is selected as the optimal bimodal separation boundary.

**Q8: Why is polarity inversion necessary after binarization?**  
*Answer:* In scanned paper documents, ink strokes are dark (pixel values near 0) and the paper background is white (pixel values near 255). For neural network feature extraction and spatial stroke density calculation, we need foreground strokes to represent non-zero signal (255 / 1.0) and empty background to represent zero (0.0). We check the background polarity dynamically and invert colors so that ink strokes are always positive activations.

**Q9: How do you prevent division-by-zero during image normalization?**  
*Answer:* In `ml/preprocessing/signature_preprocessor.py`, we convert uint8 images to float32 and scale by $1.0 / 255.0$. If normalizing by dynamic range, an epsilon value ($\epsilon = 1\times 10^{-6}$) is added to the denominator: $(x - \text{min}) / (\text{max} - \text{min} + \epsilon)$.

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
1. **Similarity Risk (50% weight)**: Measures deficit relative to model threshold $\tau^*$. If $S \ge \tau^*$, risk is low ($0.0 - 0.20$). If $S < \tau^*$, risk scales up to $1.0$.
2. **Image Quality Risk (15% weight)**: $1.0 - \text{Quality Score}$, where quality is computed from Laplacian variance (blur detection) and dynamic contrast range.
3. **Transaction Risk (25% weight)**: $0.65 \times \text{amount tier} + 0.35 \times \text{channel severity}$. Amount tiers scale from $\$1,000$ to $>\$100,000$; channels scale from Form (0.10) to Wire Transfer (0.70).
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
"""
    with open(VIVA_OUTPUT, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Viva notes markdown successfully created at: {VIVA_OUTPUT}")


def main():
    print("=" * 65)
    print("       SIGNATURE VMAKE — PPTX & VIVA NOTES BUILDER")
    print("=" * 65)

    prs = create_presentation()

    # Build 16 Slides
    print("[1/16] Building Slide 1: Title Slide...")
    build_slide_1(prs)

    print("[2/16] Building Slide 2: Problem Statement...")
    build_slide_2(prs)

    print("[3/16] Building Slide 3: Project Objectives...")
    build_slide_3(prs)

    print("[4/16] Building Slide 4: Solution Overview...")
    build_slide_4(prs)

    print("[5/16] Building Slide 5: System Architecture...")
    build_slide_5(prs)

    print("[6/16] Building Slide 6: Technology Stack...")
    build_slide_6(prs)

    print("[7/16] Building Slide 7: Dataset & Open-Set Protocol...")
    build_slide_7(prs)

    print("[8/16] Building Slide 8: Computer Vision Preprocessing...")
    build_slide_8(prs)

    print("[9/16] Building Slide 9: Machine Learning Models...")
    build_slide_9(prs)

    print("[10/16] Building Slide 10: Manual Registration & Two-Step Verification...")
    build_slide_10(prs)

    print("[11/16] Building Slide 11: Empirical Model Comparison...")
    build_slide_11(prs)

    print("[12/16] Building Slide 12: Decision & Fraud Risk Engine...")
    build_slide_12(prs)

    print("[13/16] Building Slide 13: FastAPI + Database + Security...")
    build_slide_13(prs)

    print("[14/16] Building Slide 14: Results & Validation Evidence...")
    build_slide_14(prs)

    print("[15/16] Building Slide 15: Live Application Demonstration...")
    build_slide_15(prs)

    print("[16/16] Building Slide 16: Conclusion & Future Scope...")
    build_slide_16(prs)

    # Save presentation
    prs.save(str(PPTX_OUTPUT))
    print(f"\n[SUCCESS] PowerPoint presentation saved at:\n  {PPTX_OUTPUT} ({os.path.getsize(PPTX_OUTPUT)} bytes)")

    # Generate Viva Notes
    generate_viva_markdown()
    print("=" * 65)
    print("   PRESENTATION & DEFENSE ARTIFACTS SUCCESSFULLY GENERATED!")
    print("=" * 65)


if __name__ == "__main__":
    main()
