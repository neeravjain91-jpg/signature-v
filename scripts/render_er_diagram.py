"""
Renders a visual architecture diagram of the Banking Database ER structure.
Saves to docs/ER_DIAGRAM.png.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches

def draw_er_diagram(output_path="docs/ER_DIAGRAM.png"):
    fig, ax = plt.subplots(figsize=(18, 12), dpi=200)
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # Colors
    c_header = "#1E293B"
    c_bg = "#F8FAFC"
    c_border = "#334155"
    c_text = "#0F172A"
    c_badge_pk = "#DC2626"
    c_badge_fk = "#2563EB"

    # Entities and their layout coordinates: (x, y, w, h, title, fields)
    entities = [
        # Col 1: Users & Customers & Accounts
        (0.8, 8.2, 3.2, 3.2, "USERS", [
            ("user_id", "UUID [PK]"),
            ("username", "VARCHAR(64) [UQ]"),
            ("email", "VARCHAR(255) [UQ]"),
            ("password_hash", "VARCHAR(255)"),
            ("role", "ENUM(CUST,OFFICER,ADMIN)"),
            ("status", "VARCHAR(32)"),
            ("created_at", "TIMESTAMPTZ")
        ]),
        (0.8, 4.4, 3.2, 3.2, "CUSTOMERS", [
            ("customer_id", "UUID [PK]"),
            ("user_id", "UUID [FK nullable]"),
            ("customer_reference", "VARCHAR(64) [UQ]"),
            ("full_name", "VARCHAR(128)"),
            ("phone_reference", "VARCHAR(64)"),
            ("status", "VARCHAR(32)"),
            ("created_at", "TIMESTAMPTZ")
        ]),
        (0.8, 0.6, 3.2, 3.2, "ACCOUNTS", [
            ("account_id", "UUID [PK]"),
            ("customer_id", "UUID [FK]"),
            ("account_reference", "VARCHAR(64) [UQ]"),
            ("account_type", "VARCHAR(32)"),
            ("status", "VARCHAR(32)"),
            ("created_at", "TIMESTAMPTZ")
        ]),

        # Col 2: Transactions & Verifications
        (5.0, 0.6, 3.6, 3.5, "TRANSACTIONS", [
            ("transaction_id", "UUID [PK]"),
            ("account_id", "UUID [FK]"),
            ("transaction_reference", "VARCHAR(64) [UQ]"),
            ("transaction_type", "VARCHAR(32)"),
            ("amount", "NUMERIC(15,2)"),
            ("currency", "CHAR(3)"),
            ("status", "VARCHAR(32)"),
            ("created_at", "TIMESTAMPTZ")
        ]),
        (5.0, 5.0, 3.6, 3.8, "VERIFICATION_ATTEMPTS", [
            ("verification_id", "UUID [PK]"),
            ("transaction_id", "UUID [FK]"),
            ("customer_id", "UUID [FK]"),
            ("submitted_signature_id", "UUID [FK]"),
            ("enrolled_signature_id", "UUID [FK null]"),
            ("similarity_score", "NUMERIC(5,4)"),
            ("threshold_used", "NUMERIC(5,4)"),
            ("decision", "VARCHAR(32)"),
            ("model_version_id", "UUID [FK]"),
            ("created_at", "TIMESTAMPTZ")
        ]),

        # Col 3: Signatures & Embeddings & Models
        (9.6, 7.8, 3.6, 3.6, "SIGNATURES", [
            ("signature_id", "UUID [PK]"),
            ("customer_id", "UUID [FK]"),
            ("signature_type", "VARCHAR(32)"),
            ("storage_reference", "VARCHAR(512)"),
            ("file_hash", "CHAR(64) [SHA256]"),
            ("image_quality_score", "NUMERIC(5,4)"),
            ("status", "VARCHAR(32)"),
            ("created_at", "TIMESTAMPTZ")
        ]),
        (9.6, 4.0, 3.6, 3.2, "SIGNATURE_EMBEDDINGS", [
            ("embedding_id", "UUID [PK]"),
            ("signature_id", "UUID [FK]"),
            ("model_version_id", "UUID [FK]"),
            ("embedding_reference", "VARCHAR(512)"),
            ("embedding_hash", "CHAR(64)"),
            ("vector_dim", "INT (512)"),
            ("created_at", "TIMESTAMPTZ")
        ]),
        (9.6, 0.4, 3.6, 3.2, "MODEL_VERSIONS", [
            ("model_version_id", "UUID [PK]"),
            ("model_name", "VARCHAR(64)"),
            ("version", "VARCHAR(32) [UQ]"),
            ("architecture", "VARCHAR(64)"),
            ("threshold", "NUMERIC(5,4)"),
            ("performance_summary", "JSONB"),
            ("status", "VARCHAR(32)")
        ]),

        # Col 4: Risk Assessments, Manual Reviews, Audit Logs
        (14.0, 7.8, 3.4, 3.6, "RISK_ASSESSMENTS", [
            ("risk_id", "UUID [PK]"),
            ("verification_id", "UUID [FK 1:1]"),
            ("similarity_comp", "NUMERIC(5,4)"),
            ("quality_comp", "NUMERIC(5,4)"),
            ("txn_risk_comp", "NUMERIC(5,4)"),
            ("overall_risk_score", "NUMERIC(5,4)"),
            ("risk_level", "VARCHAR(16)")
        ]),
        (14.0, 4.2, 3.4, 3.0, "MANUAL_REVIEWS", [
            ("review_id", "UUID [PK]"),
            ("verification_id", "UUID [FK]"),
            ("reviewer_user_id", "UUID [FK]"),
            ("decision", "VARCHAR(32)"),
            ("review_comment", "TEXT"),
            ("reviewed_at", "TIMESTAMPTZ")
        ]),
        (14.0, 0.6, 3.4, 3.0, "AUDIT_LOGS", [
            ("audit_id", "UUID [PK]"),
            ("user_id", "UUID [FK nullable]"),
            ("action", "VARCHAR(64)"),
            ("entity_type", "VARCHAR(64)"),
            ("entity_id", "UUID"),
            ("result", "VARCHAR(32)"),
            ("timestamp", "TIMESTAMPTZ")
        ])
    ]

    # Draw boxes
    for x, y, w, h, title, fields in entities:
        # Background rect
        rect = patches.FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=c_bg, edgecolor=c_border, linewidth=1.5
        )
        ax.add_patch(rect)

        # Header rect
        header_h = 0.45
        header_rect = patches.FancyBboxPatch(
            (x, y + h - header_h), w, header_h, boxstyle="round,pad=0.08,rounding_size=0.15",
            facecolor=c_header, edgecolor=c_border, linewidth=1.5
        )
        ax.add_patch(header_rect)

        # Title text
        ax.text(x + w / 2, y + h - header_h / 2, title, color="white", weight="bold",
                fontsize=10, ha="center", va="center")

        # Fields text
        line_y = y + h - header_h - 0.25
        for col, col_type in fields:
            is_pk = "[PK]" in col_type
            is_fk = "[FK" in col_type
            prefix_color = c_badge_pk if is_pk else (c_badge_fk if is_fk else c_text)
            weight = "bold" if (is_pk or is_fk) else "normal"

            ax.text(x + 0.15, line_y, col, color=prefix_color, fontsize=7.5, weight=weight, va="center")
            ax.text(x + w - 0.15, line_y, col_type, color="#64748B", fontsize=7.0, ha="right", va="center")
            line_y -= 0.35

    # Connectors (Relationship Arrows)
    arrows = [
        # USER -> CUSTOMER
        ((2.4, 8.2), (2.4, 7.6), "0..1 has"),
        # CUSTOMER -> ACCOUNT
        ((2.4, 4.4), (2.4, 3.8), "1..N owns"),
        # ACCOUNT -> TRANSACTION
        ((4.0, 2.2), (5.0, 2.2), "1..N contains"),
        # TRANSACTION -> VERIFICATION_ATTEMPT
        ((6.8, 4.1), (6.8, 5.0), "1..N triggers"),
        # CUSTOMER -> SIGNATURE
        ((4.0, 6.0), (9.6, 9.6), "1..N registers"),
        # SIGNATURE -> SIGNATURE_EMBEDDING
        ((11.4, 7.8), (11.4, 7.2), "1..N generates"),
        # MODEL_VERSION -> SIGNATURE_EMBEDDING
        ((11.4, 3.6), (11.4, 4.0), "1..N encodes"),
        # MODEL_VERSION -> VERIFICATION_ATTEMPT
        ((9.6, 2.0), (8.6, 5.5), "1..N evaluates"),
        # VERIFICATION_ATTEMPT -> RISK_ASSESSMENT
        ((8.6, 7.5), (14.0, 9.6), "1..1 evaluates"),
        # VERIFICATION_ATTEMPT -> MANUAL_REVIEW
        ((8.6, 6.5), (14.0, 5.7), "0..N refers")
    ]

    for (x1, y1), (x2, y2), label in arrows:
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="->", color="#0284C7", lw=1.5, ls="--",
                            shrinkA=4, shrinkB=4, connectionstyle="arc3,rad=0.05")
        )

    plt.title("Intelligent Signature Verification & Fraud Risk Assessment — PostgreSQL Database Architecture",
              fontsize=14, weight="bold", color="#0F172A", pad=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"[+] ER diagram successfully saved to: {output_path}")

if __name__ == "__main__":
    draw_er_diagram()
