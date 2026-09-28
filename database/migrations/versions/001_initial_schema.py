"""Initial production schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-28 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('CUSTOMER', 'OFFICER', 'ADMIN')", name="chk_user_role"),
        sa.CheckConstraint("status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED')", name="chk_user_status")
    )
    op.create_index("idx_users_role_status", "users", ["role", "status"])

    # 2. customers
    op.create_table(
        "customers",
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
        sa.Column("customer_reference", sa.String(64), nullable=False, unique=True),
        sa.Column("full_name", sa.String(128), nullable=False),
        sa.Column("phone_reference", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("status IN ('ACTIVE', 'UNDER_REVIEW', 'BLOCKED', 'CLOSED')", name="chk_customer_status")
    )
    op.create_index("idx_customers_customer_ref", "customers", ["customer_reference"])
    op.create_index("idx_customers_status", "customers", ["status"])

    # 3. accounts
    op.create_table(
        "accounts",
        sa.Column("account_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("account_reference", sa.String(64), nullable=False, unique=True),
        sa.Column("account_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("account_type IN ('SAVINGS', 'CHECKING', 'CURRENT', 'CORPORATE', 'WEALTH_MANAGEMENT')", name="chk_account_type"),
        sa.CheckConstraint("status IN ('ACTIVE', 'FROZEN', 'DORMANT', 'CLOSED')", name="chk_account_status")
    )
    op.create_index("idx_accounts_account_ref", "accounts", ["account_reference"])

    # 4. signatures
    op.create_table(
        "signatures",
        sa.Column("signature_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("signature_type", sa.String(32), nullable=False),
        sa.Column("storage_reference", sa.String(512), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("image_quality_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("signature_type IN ('ENROLLED', 'VERIFICATION_SUBMISSION')", name="chk_signature_type"),
        sa.CheckConstraint("status IN ('ACTIVE', 'SUPERSEDED', 'REVOKED', 'REJECTED')", name="chk_signature_status"),
        sa.CheckConstraint("image_quality_score >= 0.0000 AND image_quality_score <= 1.0000", name="chk_sig_quality")
    )
    op.create_index("idx_signatures_customer_id", "signatures", ["customer_id"])
    op.create_index("idx_signatures_file_hash", "signatures", ["file_hash"])

    # 5. model_versions
    op.create_table(
        "model_versions",
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_name", sa.String(64), nullable=False),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("architecture", sa.String(64), nullable=False),
        sa.Column("training_dataset", sa.String(128), nullable=False),
        sa.Column("training_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("threshold", sa.Numeric(5, 4), nullable=False),
        sa.Column("performance_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("artifact_reference", sa.String(512), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PRODUCTION"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.UniqueConstraint("model_name", "version", name="uq_model_name_version"),
        sa.CheckConstraint("status IN ('STAGING', 'PRODUCTION', 'DEPRECATED', 'ARCHIVED')", name="chk_model_status"),
        sa.CheckConstraint("threshold >= 0.0000 AND threshold <= 1.0000", name="chk_model_threshold")
    )

    # 6. signature_embeddings
    op.create_table(
        "signature_embeddings",
        sa.Column("embedding_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("signature_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signatures.signature_id", ondelete="CASCADE"), nullable=False),
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("model_versions.model_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("embedding_reference", sa.String(512), nullable=False),
        sa.Column("embedding_hash", sa.String(64), nullable=False),
        sa.Column("vector_dim", sa.Integer(), nullable=False, server_default="512"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.UniqueConstraint("signature_id", "model_version_id", name="uq_signature_model_embedding"),
        sa.CheckConstraint("vector_dim > 0", name="chk_vector_dim")
    )

    # 7. transactions
    op.create_table(
        "transactions",
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("transaction_reference", sa.String(64), nullable=False, unique=True),
        sa.Column("transaction_type", sa.String(32), nullable=False),
        sa.Column("amount", sa.Numeric(15, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("transaction_type IN ('CHEQUE', 'WITHDRAWAL', 'AUTHORIZATION', 'FORM_VERIFICATION', 'WIRE_TRANSFER')", name="chk_txn_type"),
        sa.CheckConstraint("amount >= 0.00", name="chk_txn_amount"),
        sa.CheckConstraint("status IN ('PENDING', 'VERIFIED', 'MANUAL_REVIEW', 'APPROVED', 'REJECTED', 'SETTLED', 'CANCELLED')", name="chk_txn_status")
    )
    op.create_index("idx_transactions_status_created", "transactions", ["status", "created_at"])

    # 8. verification_attempts
    op.create_table(
        "verification_attempts",
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transactions.transaction_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("submitted_signature_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signatures.signature_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("enrolled_signature_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("signatures.signature_id", ondelete="RESTRICT"), nullable=True),
        sa.Column("similarity_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("threshold_used", sa.Numeric(5, 4), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("model_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("model_versions.model_version_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("similarity_score >= 0.0000 AND similarity_score <= 1.0000", name="chk_sim_score"),
        sa.CheckConstraint("threshold_used >= 0.0000 AND threshold_used <= 1.0000", name="chk_threshold_used"),
        sa.CheckConstraint("decision IN ('VERIFIED', 'MANUAL_REVIEW', 'REJECTED')", name="chk_verif_decision")
    )
    op.create_index("idx_verifications_decision", "verification_attempts", ["decision"])
    op.create_index("idx_verifications_created_at", "verification_attempts", ["created_at"])

    # 9. risk_assessments
    op.create_table(
        "risk_assessments",
        sa.Column("risk_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification_attempts.verification_id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("similarity_component", sa.Numeric(5, 4), nullable=False),
        sa.Column("image_quality_component", sa.Numeric(5, 4), nullable=False),
        sa.Column("transaction_risk_component", sa.Numeric(5, 4), nullable=False),
        sa.Column("behavioral_component", sa.Numeric(5, 4), nullable=False),
        sa.Column("overall_risk_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("risk_level", sa.String(16), nullable=False),
        sa.Column("risk_factors", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("similarity_component >= 0.0000 AND similarity_component <= 1.0000", name="chk_risk_sim"),
        sa.CheckConstraint("image_quality_component >= 0.0000 AND image_quality_component <= 1.0000", name="chk_risk_img"),
        sa.CheckConstraint("transaction_risk_component >= 0.0000 AND transaction_risk_component <= 1.0000", name="chk_risk_txn"),
        sa.CheckConstraint("behavioral_component >= 0.0000 AND behavioral_component <= 1.0000", name="chk_risk_beh"),
        sa.CheckConstraint("overall_risk_score >= 0.0000 AND overall_risk_score <= 1.0000", name="chk_risk_overall"),
        sa.CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH')", name="chk_risk_level")
    )
    op.create_index("idx_risk_level", "risk_assessments", ["risk_level"])
    op.create_index("idx_risk_overall_score", "risk_assessments", ["overall_risk_score"])

    # 10. manual_reviews
    op.create_table(
        "manual_reviews",
        sa.Column("review_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("verification_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("verification_attempts.verification_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("reviewer_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("review_comment", sa.Text(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="chk_review_decision")
    )
    op.create_index("idx_manual_reviews_reviewed_at", "manual_reviews", ["reviewed_at"])

    # 11. audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("audit_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("result", sa.String(32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.current_timestamp()),
        sa.Column("request_reference", sa.String(64), nullable=False),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.CheckConstraint("result IN ('SUCCESS', 'FAILURE', 'WARNING', 'DENIED')", name="chk_audit_result")
    )
    op.create_index("idx_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("idx_audit_logs_entity", "audit_logs", ["entity_type", "entity_id"])
    op.create_index("idx_audit_logs_request_ref", "audit_logs", ["request_reference"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("manual_reviews")
    op.drop_table("risk_assessments")
    op.drop_table("verification_attempts")
    op.drop_table("transactions")
    op.drop_table("signature_embeddings")
    op.drop_table("model_versions")
    op.drop_table("signatures")
    op.drop_table("accounts")
    op.drop_table("customers")
    op.drop_table("users")
