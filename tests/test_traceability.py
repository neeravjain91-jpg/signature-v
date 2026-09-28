"""
Automated Test for End-to-End Verification Traceability and Integrity.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from database.models import (
    Customer, Account, Transaction, VerificationAttempt,
    RiskAssessment, ManualReview, AuditLog, ModelVersion, Signature
)


def test_verification_traceability():
    db_path = "sqlite:///database/banking_system_demo.db"
    engine = create_engine(db_path)
    session = Session(engine)

    print("[*] Testing Verification Traceability on Seeded Data...")

    verifications = session.query(VerificationAttempt).all()
    assert len(verifications) >= 3, f"Expected at least 3 verifications, found {len(verifications)}"

    for v in verifications:
        print(f"\n--- Tracing Verification: {v.verification_id} ---")
        
        # 1. Customer
        cust = v.customer
        assert cust is not None, "Missing Customer relationship!"
        print(f"  [1] Customer: {cust.full_name} ({cust.customer_reference})")

        # 2. Transaction & Account
        txn = v.transaction
        assert txn is not None, "Missing Transaction relationship!"
        acc = txn.account
        assert acc is not None, "Missing Account relationship!"
        print(f"  [2] Account & Txn: {acc.account_reference} -> {txn.transaction_reference} ({txn.transaction_type} {txn.amount} {txn.currency})")

        # 3. Submitted Signature
        sub_sig = v.submitted_signature
        assert sub_sig is not None, "Missing Submitted Signature!"
        print(f"  [3] Submitted Signature: {sub_sig.storage_reference} (Quality: {sub_sig.image_quality_score})")

        # 4. Model Version
        model = v.model_version
        assert model is not None, "Missing Model Version!"
        print(f"  [4] Model: {model.model_name} {model.version} (Threshold: {model.threshold})")

        # 5. Similarity Score & Decision
        print(f"  [5] Verification Metrics: Score={v.similarity_score}, Threshold={v.threshold_used}, Decision={v.decision}")

        # 6. Risk Assessment (1-to-1)
        risk = v.risk_assessment
        assert risk is not None, "Missing Risk Assessment!"
        print(f"  [6] Risk Assessment: Level={risk.risk_level}, Overall Score={risk.overall_risk_score}")

        # 7. Manual Review (if applicable)
        if v.decision == "MANUAL_REVIEW":
            reviews = v.manual_reviews
            assert len(reviews) > 0, "Verification marked MANUAL_REVIEW without any ManualReview record!"
            review = reviews[0]
            print(f"  [7] Manual Review: Decision={review.decision} by Reviewer ID {review.reviewer_user_id} - Comment: '{review.review_comment}'")
        else:
            print(f"  [7] Manual Review: Not required (Autonomous {v.decision})")

        # 8. Audit Log
        audit = session.query(AuditLog).filter_by(entity_id=v.verification_id).first()
        if not audit:
            # Check manual review audit if applicable
            if v.manual_reviews:
                audit = session.query(AuditLog).filter_by(entity_id=v.manual_reviews[0].review_id).first()
        assert audit is not None, f"Audit log entry missing for verification {v.verification_id}!"
        print(f"  [8] Audit Log: Action='{audit.action}', Result='{audit.result}', ReqRef='{audit.request_reference}'")

    print("\n[+] Traceability Test PASSED for all verification scenarios!")


if __name__ == "__main__":
    test_verification_traceability()
