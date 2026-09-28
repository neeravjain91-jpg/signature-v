"""
Synthetic Demo Data Seeder for Banking Signature Verification System.

Strictly separates research dataset (CEDAR) from banking production entities.
All seeded records use explicit synthetic identifiers (e.g. DEMO-CUST-001, DEMO-TXN-101).
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import uuid
import hashlib
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import (
    Base, User, Customer, Account, Signature, ModelVersion,
    SignatureEmbedding, Transaction, VerificationAttempt,
    RiskAssessment, ManualReview, AuditLog
)


def hash_pw(pw: str) -> str:
    # PBKDF2/SHA256 mock hash for demo
    return hashlib.sha256(pw.encode()).hexdigest()


def seed_database(db_url: str = None) -> Session:
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "sqlite:///database/banking_system_demo.db")
    
    print(f"[*] Initializing database engine at: {db_url}")
    engine = create_engine(db_url, echo=False)
    
    # If SQLite, ensure foreign keys are enabled
    if "sqlite" in db_url:
        from sqlalchemy import event
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    Base.metadata.create_all(engine)
    session = Session(engine)

    # Check if already seeded
    if session.query(Customer).filter_by(customer_reference="DEMO-CUST-001").first():
        print("[!] Demo data already seeded. Skipping.")
        return session

    print("[*] Seeding Model Version...")
    model_v1 = ModelVersion(
        model_version_id=uuid.uuid4(),
        model_name="SiameseSignatureNet",
        version="v1.0.0",
        architecture="Siamese-ResNet-Contrastive",
        training_dataset="CEDAR (Writer-Independent 35-Writer Split)",
        training_date=datetime(2026, 9, 28, tzinfo=timezone.utc),
        threshold=Decimal("0.7691"),
        performance_summary={
            "eer": 0.3067,
            "auc_roc": 0.7465,
            "accuracy": 0.6900,
            "far": 0.4667,
            "frr": 0.1533,
            "random_impostor_block_rate": 0.8375,
            "eval_protocol": "writer_independent_open_set"
        },
        artifact_reference="artifacts/models/best_siamese_model.pt",
        status="PRODUCTION"
    )
    session.add(model_v1)

    print("[*] Seeding System Users...")
    admin_user = User(
        user_id=uuid.uuid4(),
        username="admin_sarah",
        email="sarah.admin@securebank-demo.internal",
        password_hash=hash_pw("AdminSecure!2026"),
        role="ADMIN",
        status="ACTIVE"
    )
    officer_user = User(
        user_id=uuid.uuid4(),
        username="officer_marcus",
        email="marcus.compliance@securebank-demo.internal",
        password_hash=hash_pw("OfficerSecure!2026"),
        role="OFFICER",
        status="ACTIVE"
    )
    cust_user_alice = User(
        user_id=uuid.uuid4(),
        username="alice_walker",
        email="alice.walker@example-demo.com",
        password_hash=hash_pw("AlicePass!2026"),
        role="CUSTOMER",
        status="ACTIVE"
    )
    session.add_all([admin_user, officer_user, cust_user_alice])
    session.flush()

    print("[*] Seeding Synthetic Bank Customers...")
    cust1 = Customer(
        customer_id=uuid.uuid4(),
        user_id=cust_user_alice.user_id,
        customer_reference="DEMO-CUST-001",
        full_name="Alice Walker",
        phone_reference="sha256:d8a2...3b1f",
        status="ACTIVE"
    )
    cust2 = Customer(
        customer_id=uuid.uuid4(),
        user_id=None,  # Offline banking customer without web portal user
        customer_reference="DEMO-CUST-002",
        full_name="Robert Vance (Commercial)",
        phone_reference="sha256:7c4e...9a22",
        status="ACTIVE"
    )
    session.add_all([cust1, cust2])
    session.flush()

    print("[*] Seeding Accounts...")
    acc1 = Account(
        account_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        account_reference="DEMO-ACC-SAV-8801",
        account_type="SAVINGS",
        status="ACTIVE"
    )
    acc2 = Account(
        account_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        account_reference="DEMO-ACC-CHK-8802",
        account_type="CHECKING",
        status="ACTIVE"
    )
    acc3 = Account(
        account_id=uuid.uuid4(),
        customer_id=cust2.customer_id,
        account_reference="DEMO-ACC-CORP-9901",
        account_type="CORPORATE",
        status="ACTIVE"
    )
    session.add_all([acc1, acc2, acc3])
    session.flush()

    print("[*] Seeding Enrolled Signatures & Embeddings...")
    sig1_enrolled = Signature(
        signature_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        signature_type="ENROLLED",
        storage_reference="vault://signatures/enrolled/DEMO-CUST-001/primary_specimen.png",
        file_hash="a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0",
        image_quality_score=Decimal("0.9650"),
        status="ACTIVE"
    )
    session.add(sig1_enrolled)
    session.flush()

    embed1 = SignatureEmbedding(
        embedding_id=uuid.uuid4(),
        signature_id=sig1_enrolled.signature_id,
        model_version_id=model_v1.model_version_id,
        embedding_reference="vault://embeddings/DEMO-CUST-001/primary_specimen_v1.npy",
        embedding_hash="e4d3c2b1a0f9e8d7c6b5a4938271605f4e3d2c1b0a9f8e7d6c5b4a3928170615",
        vector_dim=512
    )
    session.add(embed1)

    print("[*] Seeding Prototype Transactions & Verification Cycles...")
    
    # -------------------------------------------------------------
    # Scenario 1: Authentic Cheque -> Auto-Verified (Low Risk)
    # -------------------------------------------------------------
    txn1 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=acc2.account_id,
        transaction_reference="DEMO-TXN-CHEQUE-101",
        transaction_type="CHEQUE",
        amount=Decimal("4500.00"),
        currency="USD",
        status="VERIFIED"
    )
    session.add(txn1)
    session.flush()

    sig_sub1 = Signature(
        signature_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        signature_type="VERIFICATION_SUBMISSION",
        storage_reference="vault://signatures/submissions/DEMO-TXN-CHEQUE-101/extracted_sig.png",
        file_hash="f0e1d2c3b4a5968778695a4b3c2d1e0fa1b2c3d4e5f60718293a4b5c6d7e8f90",
        image_quality_score=Decimal("0.9400"),
        status="ACTIVE"
    )
    session.add(sig_sub1)
    session.flush()

    verif1 = VerificationAttempt(
        verification_id=uuid.uuid4(),
        transaction_id=txn1.transaction_id,
        customer_id=cust1.customer_id,
        submitted_signature_id=sig_sub1.signature_id,
        enrolled_signature_id=sig1_enrolled.signature_id,
        similarity_score=Decimal("0.9420"),
        threshold_used=model_v1.threshold,
        decision="VERIFIED",
        model_version_id=model_v1.model_version_id
    )
    session.add(verif1)
    session.flush()

    risk1 = RiskAssessment(
        risk_id=uuid.uuid4(),
        verification_id=verif1.verification_id,
        similarity_component=Decimal("0.0580"),   # (1 - 0.9420)
        image_quality_component=Decimal("0.0600"),
        transaction_risk_component=Decimal("0.1200"),
        behavioral_component=Decimal("0.0500"),
        overall_risk_score=Decimal("0.0720"),
        risk_level="LOW",
        risk_factors=[{"code": "NORMAL_PATTERN", "desc": "Signature highly correlated with enrolled specimen"}]
    )
    session.add(risk1)

    audit1 = AuditLog(
        audit_id=uuid.uuid4(),
        user_id=None,
        action="AUTOMATED_VERIFICATION_PASS",
        entity_type="VERIFICATION_ATTEMPT",
        entity_id=verif1.verification_id,
        result="SUCCESS",
        request_reference="REQ-CORR-7701",
        details={"txn_ref": txn1.transaction_reference, "similarity": 0.9420, "risk_level": "LOW"}
    )
    session.add(audit1)

    # -------------------------------------------------------------
    # Scenario 2: High-Value Wire -> Borderline Sig -> Manual Review -> Approved
    # -------------------------------------------------------------
    txn2 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=acc1.account_id,
        transaction_reference="DEMO-TXN-WIRE-102",
        transaction_type="WIRE_TRANSFER",
        amount=Decimal("48000.00"),
        currency="USD",
        status="APPROVED"
    )
    session.add(txn2)
    session.flush()

    sig_sub2 = Signature(
        signature_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        signature_type="VERIFICATION_SUBMISSION",
        storage_reference="vault://signatures/submissions/DEMO-TXN-WIRE-102/form_sig.png",
        file_hash="99887766554433221100aabbccddeeff99887766554433221100aabbccddeeff",
        image_quality_score=Decimal("0.8100"),
        status="ACTIVE"
    )
    session.add(sig_sub2)
    session.flush()

    verif2 = VerificationAttempt(
        verification_id=uuid.uuid4(),
        transaction_id=txn2.transaction_id,
        customer_id=cust1.customer_id,
        submitted_signature_id=sig_sub2.signature_id,
        enrolled_signature_id=sig1_enrolled.signature_id,
        similarity_score=Decimal("0.7250"),
        threshold_used=model_v1.threshold,
        decision="MANUAL_REVIEW",
        model_version_id=model_v1.model_version_id
    )
    session.add(verif2)
    session.flush()

    risk2 = RiskAssessment(
        risk_id=uuid.uuid4(),
        verification_id=verif2.verification_id,
        similarity_component=Decimal("0.2750"),
        image_quality_component=Decimal("0.1900"),
        transaction_risk_component=Decimal("0.6500"),  # High amount
        behavioral_component=Decimal("0.3000"),
        overall_risk_score=Decimal("0.4650"),
        risk_level="MEDIUM",
        risk_factors=[
            {"code": "BORDERLINE_SIMILARITY", "desc": "Score 0.7250 slightly below threshold 0.7850"},
            {"code": "HIGH_VALUE_TRANSACTION", "desc": "Amount $48,000 exceeds standard retail tier"}
        ]
    )
    session.add(risk2)

    review2 = ManualReview(
        review_id=uuid.uuid4(),
        verification_id=verif2.verification_id,
        reviewer_user_id=officer_user.user_id,
        decision="APPROVED",
        review_comment="Customer contacted via registered phone challenge-response. Natural variation observed in terminal flourish. Authenticity confirmed."
    )
    session.add(review2)

    audit2 = AuditLog(
        audit_id=uuid.uuid4(),
        user_id=officer_user.user_id,
        action="MANUAL_REVIEW_OVERRIDE_APPROVE",
        entity_type="MANUAL_REVIEW",
        entity_id=review2.review_id,
        result="SUCCESS",
        request_reference="REQ-CORR-7702",
        details={"txn_ref": txn2.transaction_reference, "reviewer": officer_user.username, "decision": "APPROVED"}
    )
    session.add(audit2)

    # -------------------------------------------------------------
    # Scenario 3: Counter Forgery -> High Risk -> Rejection
    # -------------------------------------------------------------
    txn3 = Transaction(
        transaction_id=uuid.uuid4(),
        account_id=acc2.account_id,
        transaction_reference="DEMO-TXN-WITHDRAW-103",
        transaction_type="WITHDRAWAL",
        amount=Decimal("15000.00"),
        currency="USD",
        status="REJECTED"
    )
    session.add(txn3)
    session.flush()

    sig_sub3 = Signature(
        signature_id=uuid.uuid4(),
        customer_id=cust1.customer_id,
        signature_type="VERIFICATION_SUBMISSION",
        storage_reference="vault://signatures/submissions/DEMO-TXN-WITHDRAW-103/counter_slip.png",
        file_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
        image_quality_score=Decimal("0.8900"),
        status="REJECTED"
    )
    session.add(sig_sub3)
    session.flush()

    verif3 = VerificationAttempt(
        verification_id=uuid.uuid4(),
        transaction_id=txn3.transaction_id,
        customer_id=cust1.customer_id,
        submitted_signature_id=sig_sub3.signature_id,
        enrolled_signature_id=sig1_enrolled.signature_id,
        similarity_score=Decimal("0.2840"),
        threshold_used=model_v1.threshold,
        decision="REJECTED",
        model_version_id=model_v1.model_version_id
    )
    session.add(verif3)
    session.flush()

    risk3 = RiskAssessment(
        risk_id=uuid.uuid4(),
        verification_id=verif3.verification_id,
        similarity_component=Decimal("0.7160"),
        image_quality_component=Decimal("0.1100"),
        transaction_risk_component=Decimal("0.5500"),
        behavioral_component=Decimal("0.7800"),
        overall_risk_score=Decimal("0.8120"),
        risk_level="HIGH",
        risk_factors=[
            {"code": "DISCREPANT_STROKE_DYNAMICS", "desc": "Severe deviation in stroke contours"},
            {"code": "HIGH_FRAUD_PROBABILITY", "desc": "Similarity 0.2840 is far below threshold 0.7850"}
        ]
    )
    session.add(risk3)

    audit3 = AuditLog(
        audit_id=uuid.uuid4(),
        user_id=None,
        action="AUTOMATED_FRAUD_BLOCK",
        entity_type="VERIFICATION_ATTEMPT",
        entity_id=verif3.verification_id,
        result="DENIED",
        request_reference="REQ-CORR-7703",
        details={"txn_ref": txn3.transaction_reference, "similarity": 0.2840, "risk_level": "HIGH"}
    )
    session.add(audit3)

    session.commit()
    print("[+] Successfully seeded banking demo records.")
    return session


if __name__ == "__main__":
    seed_database()
