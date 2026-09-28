"""
SQLAlchemy 2.0 ORM Models for Intelligent Signature Verification & Risk Assessment.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    String, Numeric, Integer, ForeignKey, Text, CheckConstraint,
    UniqueConstraint, Index, DateTime
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="user", uselist=False)
    manual_reviews: Mapped[List["ManualReview"]] = relationship("ManualReview", back_populates="reviewer")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        CheckConstraint("role IN ('CUSTOMER', 'OFFICER', 'ADMIN')", name="chk_user_role"),
        CheckConstraint("status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED')", name="chk_user_status"),
        Index("idx_users_role_status", "role", "status"),
    )


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    customer_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    phone_reference: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="customer")
    accounts: Mapped[List["Account"]] = relationship("Account", back_populates="customer")
    signatures: Mapped[List["Signature"]] = relationship("Signature", back_populates="customer")
    verification_attempts: Mapped[List["VerificationAttempt"]] = relationship("VerificationAttempt", back_populates="customer")

    __table_args__ = (
        CheckConstraint("status IN ('ACTIVE', 'UNDER_REVIEW', 'BLOCKED', 'CLOSED')", name="chk_customer_status"),
        Index("idx_customers_customer_ref", "customer_reference"),
        Index("idx_customers_status", "status"),
    )


class Account(Base):
    __tablename__ = "accounts"

    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False)
    account_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    account_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="accounts")
    transactions: Mapped[List["Transaction"]] = relationship("Transaction", back_populates="account")

    __table_args__ = (
        CheckConstraint("account_type IN ('SAVINGS', 'CHECKING', 'CURRENT', 'CORPORATE', 'WEALTH_MANAGEMENT')", name="chk_account_type"),
        CheckConstraint("status IN ('ACTIVE', 'FROZEN', 'DORMANT', 'CLOSED')", name="chk_account_status"),
        Index("idx_accounts_account_ref", "account_reference"),
    )


class Signature(Base):
    __tablename__ = "signatures"

    signature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False)
    signature_type: Mapped[str] = mapped_column(String(32), nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    image_quality_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="signatures")
    embeddings: Mapped[List["SignatureEmbedding"]] = relationship("SignatureEmbedding", back_populates="signature", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("signature_type IN ('ENROLLED', 'VERIFICATION_SUBMISSION')", name="chk_signature_type"),
        CheckConstraint("status IN ('ACTIVE', 'SUPERSEDED', 'REVOKED', 'REJECTED')", name="chk_signature_status"),
        CheckConstraint("image_quality_score >= 0.0000 AND image_quality_score <= 1.0000", name="chk_sig_quality"),
        Index("idx_signatures_customer_id", "customer_id"),
        Index("idx_signatures_file_hash", "file_hash"),
    )


class ModelVersion(Base):
    __tablename__ = "model_versions"

    model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name: Mapped[str] = mapped_column(String(64), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    architecture: Mapped[str] = mapped_column(String(64), nullable=False)
    training_dataset: Mapped[str] = mapped_column(String(128), nullable=False)
    training_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    threshold: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    performance_summary: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    artifact_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PRODUCTION")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    embeddings: Mapped[List["SignatureEmbedding"]] = relationship("SignatureEmbedding", back_populates="model_version")
    verification_attempts: Mapped[List["VerificationAttempt"]] = relationship("VerificationAttempt", back_populates="model_version")

    __table_args__ = (
        UniqueConstraint("model_name", "version", name="uq_model_name_version"),
        CheckConstraint("status IN ('STAGING', 'PRODUCTION', 'DEPRECATED', 'ARCHIVED')", name="chk_model_status"),
        CheckConstraint("threshold >= 0.0000 AND threshold <= 1.0000", name="chk_model_threshold"),
    )


class SignatureEmbedding(Base):
    __tablename__ = "signature_embeddings"

    embedding_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    signature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("signatures.signature_id", ondelete="CASCADE"), nullable=False)
    model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.model_version_id", ondelete="RESTRICT"), nullable=False)
    embedding_reference: Mapped[str] = mapped_column(String(512), nullable=False)
    embedding_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    vector_dim: Mapped[int] = mapped_column(Integer, nullable=False, default=512)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    signature: Mapped["Signature"] = relationship("Signature", back_populates="embeddings")
    model_version: Mapped["ModelVersion"] = relationship("ModelVersion", back_populates="embeddings")

    __table_args__ = (
        UniqueConstraint("signature_id", "model_version_id", name="uq_signature_model_embedding"),
        CheckConstraint("vector_dim > 0", name="chk_vector_dim"),
    )


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("accounts.account_id", ondelete="RESTRICT"), nullable=False)
    transaction_reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
    verification_attempts: Mapped[List["VerificationAttempt"]] = relationship("VerificationAttempt", back_populates="transaction")

    __table_args__ = (
        CheckConstraint("transaction_type IN ('CHEQUE', 'WITHDRAWAL', 'AUTHORIZATION', 'FORM_VERIFICATION', 'WIRE_TRANSFER')", name="chk_txn_type"),
        CheckConstraint("amount >= 0.00", name="chk_txn_amount"),
        CheckConstraint("status IN ('PENDING', 'VERIFIED', 'MANUAL_REVIEW', 'APPROVED', 'REJECTED', 'SETTLED', 'CANCELLED')", name="chk_txn_status"),
        Index("idx_transactions_status_created", "status", "created_at"),
    )


class VerificationAttempt(Base):
    __tablename__ = "verification_attempts"

    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("transactions.transaction_id", ondelete="RESTRICT"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("customers.customer_id", ondelete="RESTRICT"), nullable=False)
    submitted_signature_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("signatures.signature_id", ondelete="RESTRICT"), nullable=False)
    enrolled_signature_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("signatures.signature_id", ondelete="RESTRICT"), nullable=True)
    similarity_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    threshold_used: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    model_version_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("model_versions.model_version_id", ondelete="RESTRICT"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="verification_attempts")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="verification_attempts")
    submitted_signature: Mapped["Signature"] = relationship("Signature", foreign_keys=[submitted_signature_id])
    enrolled_signature: Mapped[Optional["Signature"]] = relationship("Signature", foreign_keys=[enrolled_signature_id])
    model_version: Mapped["ModelVersion"] = relationship("ModelVersion", back_populates="verification_attempts")
    risk_assessment: Mapped[Optional["RiskAssessment"]] = relationship("RiskAssessment", back_populates="verification_attempt", uselist=False, cascade="all, delete-orphan")
    manual_reviews: Mapped[List["ManualReview"]] = relationship("ManualReview", back_populates="verification_attempt")

    __table_args__ = (
        CheckConstraint("similarity_score >= 0.0000 AND similarity_score <= 1.0000", name="chk_sim_score"),
        CheckConstraint("threshold_used >= 0.0000 AND threshold_used <= 1.0000", name="chk_threshold_used"),
        CheckConstraint("decision IN ('VERIFIED', 'MANUAL_REVIEW', 'REJECTED')", name="chk_verif_decision"),
        Index("idx_verifications_decision", "decision"),
        Index("idx_verifications_created_at", "created_at"),
    )


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    risk_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("verification_attempts.verification_id", ondelete="CASCADE"), unique=True, nullable=False)
    similarity_component: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    image_quality_component: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    transaction_risk_component: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    behavioral_component: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    overall_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 4), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    risk_factors: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    verification_attempt: Mapped["VerificationAttempt"] = relationship("VerificationAttempt", back_populates="risk_assessment")

    __table_args__ = (
        CheckConstraint("similarity_component >= 0.0000 AND similarity_component <= 1.0000", name="chk_risk_sim"),
        CheckConstraint("image_quality_component >= 0.0000 AND image_quality_component <= 1.0000", name="chk_risk_img"),
        CheckConstraint("transaction_risk_component >= 0.0000 AND transaction_risk_component <= 1.0000", name="chk_risk_txn"),
        CheckConstraint("behavioral_component >= 0.0000 AND behavioral_component <= 1.0000", name="chk_risk_beh"),
        CheckConstraint("overall_risk_score >= 0.0000 AND overall_risk_score <= 1.0000", name="chk_risk_overall"),
        CheckConstraint("risk_level IN ('LOW', 'MEDIUM', 'HIGH')", name="chk_risk_level"),
        Index("idx_risk_level", "risk_level"),
        Index("idx_risk_overall_score", "overall_risk_score"),
    )


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    review_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("verification_attempts.verification_id", ondelete="RESTRICT"), nullable=False)
    reviewer_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="RESTRICT"), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    review_comment: Mapped[str] = mapped_column(Text, nullable=False)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relationships
    verification_attempt: Mapped["VerificationAttempt"] = relationship("VerificationAttempt", back_populates="manual_reviews")
    reviewer: Mapped["User"] = relationship("User", back_populates="manual_reviews")

    __table_args__ = (
        CheckConstraint("decision IN ('APPROVED', 'REJECTED')", name="chk_review_decision"),
        Index("idx_manual_reviews_reviewed_at", "reviewed_at"),
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    result: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    request_reference: Mapped[str] = mapped_column(String(64), nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        CheckConstraint("result IN ('SUCCESS', 'FAILURE', 'WARNING', 'DENIED')", name="chk_audit_result"),
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_entity", "entity_type", "entity_id"),
        Index("idx_audit_logs_request_ref", "request_reference"),
    )
