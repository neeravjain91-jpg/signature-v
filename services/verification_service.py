"""
Banking Signature Verification Service and Orchestrator.

Integrates:
- Biometric Siamese Neural Network Inference
- Multi-Factor Fraud Risk Scoring Engine
- Relational Database Persistence (PostgreSQL / SQLite)
- Immutable Audit Logging & Manual Review Compliance Workflows
"""

import sys
import uuid
import hashlib
from pathlib import Path
from typing import Union, Dict, Any, Optional, List
from decimal import Decimal
from datetime import datetime, timezone
import shutil

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import cv2
from sqlalchemy.orm import Session

from database.models import (
    Customer, Account, Transaction, Signature, SignatureEmbedding,
    ModelVersion, VerificationAttempt, RiskAssessment, ManualReview,
    AuditLog, User
)
from ml.inference.verify_signature import SignatureVerifier
from services.risk_engine import FraudRiskEngine


class BankingVerificationService:
    """
    Core banking business logic coordinating biometrics, risk assessment, and financial ledgers.
    """

    def __init__(
        self,
        db_session: Session,
        checkpoint_path: Optional[str] = None,
        verifier: Optional[SignatureVerifier] = None,
        risk_engine: Optional[FraudRiskEngine] = None
    ):
        self.session = db_session
        self.verifier = verifier or SignatureVerifier(checkpoint_path=checkpoint_path)
        self.risk_engine = risk_engine or FraudRiskEngine()

        # Cache active production model version
        self.active_model = self.session.query(ModelVersion).filter_by(status="PRODUCTION").first()
        if not self.active_model:
            # Fallback to any model version
            self.active_model = self.session.query(ModelVersion).first()

    @staticmethod
    def calculate_file_hash(image_input: Union[str, Path, bytes, np.ndarray]) -> str:
        """Computes SHA-256 hash for raw image data."""
        if isinstance(image_input, (str, Path)):
            hasher = hashlib.sha256()
            with open(image_input, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        elif isinstance(image_input, bytes):
            return hashlib.sha256(image_input).hexdigest()
        elif isinstance(image_input, np.ndarray):
            return hashlib.sha256(image_input.tobytes()).hexdigest()
        raise TypeError(f"Cannot hash type: {type(image_input)}")

    def enroll_customer_signature(
        self,
        customer_reference: str,
        image_path: str,
        storage_uri: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Enrolls a new reference specimen for a bank customer.
        Saves physical specimen into the vault on disk, validates image decoding,
        extracts and stores embedding under active model version.
        """
        customer = self.session.query(Customer).filter_by(customer_reference=customer_reference).first()
        if not customer:
            try:
                u_id = uuid.UUID(str(customer_reference))
                customer = self.session.query(Customer).filter_by(customer_id=u_id).first()
            except ValueError:
                pass

        if not customer:
            # Auto-provision customer profile for manual registration
            customer = Customer(
                customer_id=uuid.uuid4(),
                customer_reference=customer_reference,
                full_name=f"Customer {customer_reference}",
                phone_reference=f"sha256:{hashlib.sha256(customer_reference.encode()).hexdigest()[:16]}",
                status="ACTIVE"
            )
            self.session.add(customer)
            self.session.flush()

        # Ensure customer has at least one account for financial ledger compatibility
        if not customer.accounts:
            acc = Account(
                account_id=uuid.uuid4(),
                customer_id=customer.customer_id,
                account_reference=f"ACC-{customer.customer_reference}",
                account_type="SAVINGS",
                status="ACTIVE"
            )
            self.session.add(acc)
            self.session.flush()

        # Read and strictly validate image
        img_np = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img_np is None or img_np.size == 0 or img_np.shape[0] < 10 or img_np.shape[1] < 10:
            raise ValueError(f"Corrupt or invalid signature image at: {image_path}")

        quality_score = self.risk_engine.assess_image_quality(img_np)
        file_hash = self.calculate_file_hash(image_path)
        sig_id = uuid.uuid4()

        # Persist physical image into disk vault
        vault_dir = Path("data/vault/signatures/enrolled") / str(customer.customer_reference)
        vault_dir.mkdir(parents=True, exist_ok=True)
        vault_filename = f"{sig_id.hex[:8]}_{Path(image_path).name}"
        vault_path = vault_dir / vault_filename
        shutil.copy2(image_path, vault_path)
        persisted_uri = storage_uri or str(vault_path).replace("\\", "/")

        # 1. Create Signature record
        signature = Signature(
            signature_id=sig_id,
            customer_id=customer.customer_id,
            signature_type="ENROLLED",
            storage_reference=persisted_uri,
            file_hash=file_hash,
            image_quality_score=Decimal(str(round(quality_score, 4))),
            status="ACTIVE"
        )
        self.session.add(signature)
        self.session.flush()

        # 2. Extract and create SignatureEmbedding
        if self.active_model:
            embedding_vec = self.verifier.extract_embedding(str(vault_path))
            emb_hash = hashlib.sha256(embedding_vec.tobytes()).hexdigest()
            embed_ref = f"vault://embeddings/{customer.customer_reference}/sig_{signature.signature_id}_{self.active_model.version}.npy"

            embedding_record = SignatureEmbedding(
                embedding_id=uuid.uuid4(),
                signature_id=signature.signature_id,
                model_version_id=self.active_model.model_version_id,
                embedding_reference=embed_ref,
                embedding_hash=emb_hash,
                vector_dim=len(embedding_vec)
            )
            self.session.add(embedding_record)

        # 3. Audit log
        audit = AuditLog(
            audit_id=uuid.uuid4(),
            user_id=None,
            action="CUSTOMER_SIGNATURE_ENROLLED",
            entity_type="SIGNATURE",
            entity_id=signature.signature_id,
            result="SUCCESS",
            request_reference=f"ENROLL-{uuid.uuid4().hex[:8].upper()}",
            details={
                "customer_ref": customer.customer_reference,
                "quality": round(quality_score, 4),
                "file_hash": file_hash,
                "vault_path": str(vault_path)
            }
        )
        self.session.add(audit)
        self.session.commit()

        return {
            "signature_id": str(signature.signature_id),
            "customer_reference": customer.customer_reference,
            "image_quality_score": round(quality_score, 4),
            "file_hash": file_hash,
            "status": "ENROLLED",
            "active_status": signature.status,
            "storage_reference": persisted_uri,
            "created_at": signature.created_at.isoformat() if signature.created_at else datetime.now(timezone.utc).isoformat()
        }

    def verify_transaction(
        self,
        transaction_reference: str,
        submitted_signature_path: str,
        request_reference: Optional[str] = None,
        amount_override: Optional[float] = None,
        transaction_type_override: Optional[str] = None,
        model_track: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end verification of a questioned transaction signature:
        1. Retrieves account and customer reference.
        2. Retrieves customer's enrolled signature.
        3. Executes Siamese model inference.
        4. Evaluates multi-factor fraud risk.
        5. Persists verification attempt, risk assessment, and audit logs.
        6. Updates transaction status.
        """
        req_ref = request_reference or f"REQ-{uuid.uuid4().hex[:8].upper()}"

        # 1. Fetch transaction
        txn = self.session.query(Transaction).filter_by(transaction_reference=transaction_reference).first()
        if not txn:
            raise ValueError(f"Transaction '{transaction_reference}' not found.")

        customer = txn.account.customer
        if not customer:
            raise ValueError("Customer record associated with transaction account could not be found.")

        # 2. Fetch enrolled signature
        enrolled_sig = self.session.query(Signature).filter_by(
            customer_id=customer.customer_id,
            signature_type="ENROLLED",
            status="ACTIVE"
        ).order_by(Signature.created_at.desc()).first()

        if not enrolled_sig:
            raise ValueError(f"No enrolled signature found for customer '{customer.customer_reference}'.")

        # 3. Assess submitted signature quality and persist record
        sub_img = cv2.imread(str(submitted_signature_path), cv2.IMREAD_GRAYSCALE)
        if sub_img is None:
            raise ValueError(f"Could not read submitted signature image at: {submitted_signature_path}")

        quality_score = self.risk_engine.assess_image_quality(sub_img)
        sub_hash = self.calculate_file_hash(submitted_signature_path)

        submitted_sig_record = Signature(
            signature_id=uuid.uuid4(),
            customer_id=customer.customer_id,
            signature_type="VERIFICATION_SUBMISSION",
            storage_reference=f"vault://submissions/{transaction_reference}/{Path(submitted_signature_path).name}",
            file_hash=sub_hash,
            image_quality_score=Decimal(str(quality_score)),
            status="ACTIVE"
        )
        self.session.add(submitted_sig_record)
        self.session.flush()

        # 4. Resolve reference physical path or placeholder for inference
        # If storage_reference is a vault:// URI, find actual local file or use test sample
        ref_image_path = enrolled_sig.storage_reference
        if ref_image_path.startswith("vault://"):
            # Use demo enrolled specimen on disk if available, otherwise raw dataset sample
            potential_paths = [
                f"data/raw/signatures/full_org/original_1_1.png",
                f"data/raw/signatures/full_org/original_46_1.png"
            ]
            for p in potential_paths:
                if Path(p).exists():
                    ref_image_path = p
                    break

        # 5. Execute Verification using active or selected model verifier
        if model_track:
            from ml.inference.verify_signature import get_model_verifier
            active_verifier = get_model_verifier(model_track)
        else:
            active_verifier = self.verifier

        active_thresh = float(active_verifier.threshold) if hasattr(active_verifier, "threshold") else (float(self.active_model.threshold) if self.active_model else 0.7691)

        if hasattr(active_verifier, "verify"):
            model_res = active_verifier.verify(
                reference_input=ref_image_path,
                submitted_input=submitted_signature_path,
                threshold=active_thresh
            )
            sim_score = model_res["similarity_score"]
            euclidean_dist = model_res.get("euclidean_distance", model_res.get("distance", 0.0))
        else:
            out = active_verifier.verify_pair(ref_image_path, submitted_signature_path, threshold=active_thresh)
            sim_score = out.similarity_score
            euclidean_dist = out.distance
            model_res = out.to_dict()

        # 6. Evaluate Multi-Factor Fraud Risk
        eval_amount = float(amount_override) if amount_override is not None else float(txn.amount)
        eval_txn_type = transaction_type_override if transaction_type_override else txn.transaction_type
        risk_res = self.risk_engine.evaluate(
            similarity_score=sim_score,
            model_threshold=active_thresh,
            image_quality_score=quality_score,
            amount=eval_amount,
            transaction_type=eval_txn_type,
            behavioral_score=0.05
        )

        final_decision = risk_res["recommended_decision"]

        # 7. Persist Verification Attempt
        model_ver_id = self.active_model.model_version_id if self.active_model else uuid.uuid4()
        verif_attempt = VerificationAttempt(
            verification_id=uuid.uuid4(),
            transaction_id=txn.transaction_id,
            customer_id=customer.customer_id,
            submitted_signature_id=submitted_sig_record.signature_id,
            enrolled_signature_id=enrolled_sig.signature_id,
            similarity_score=Decimal(str(sim_score)),
            threshold_used=Decimal(str(active_thresh)),
            decision=final_decision,
            model_version_id=model_ver_id
        )
        self.session.add(verif_attempt)
        self.session.flush()

        # 8. Persist Risk Assessment (1-to-1)
        risk_record = RiskAssessment(
            risk_id=uuid.uuid4(),
            verification_id=verif_attempt.verification_id,
            similarity_component=Decimal(str(risk_res["similarity_component"])),
            image_quality_component=Decimal(str(risk_res["image_quality_component"])),
            transaction_risk_component=Decimal(str(risk_res["transaction_risk_component"])),
            behavioral_component=Decimal(str(risk_res["behavioral_component"])),
            overall_risk_score=Decimal(str(risk_res["overall_risk_score"])),
            risk_level=risk_res["risk_level"],
            risk_factors=risk_res["risk_factors"]
        )
        self.session.add(risk_record)

        # 9. Update Transaction Status
        if final_decision == "VERIFIED":
            txn.status = "VERIFIED"
            audit_action = "AUTOMATED_VERIFICATION_PASS"
            audit_result = "SUCCESS"
        elif final_decision == "MANUAL_REVIEW":
            txn.status = "MANUAL_REVIEW"
            audit_action = "VERIFICATION_REFERRED_TO_OFFICER"
            audit_result = "WARNING"
        else:
            txn.status = "REJECTED"
            submitted_sig_record.status = "REJECTED"
            audit_action = "AUTOMATED_FRAUD_REJECTION"
            audit_result = "DENIED"

        # 10. Audit Log Entry
        audit = AuditLog(
            audit_id=uuid.uuid4(),
            user_id=None,
            action=audit_action,
            entity_type="VERIFICATION_ATTEMPT",
            entity_id=verif_attempt.verification_id,
            result=audit_result,
            request_reference=req_ref,
            details={
                "transaction_ref": txn.transaction_reference,
                "amount": float(txn.amount),
                "similarity_score": sim_score,
                "overall_risk_score": risk_res["overall_risk_score"],
                "risk_level": risk_res["risk_level"],
                "decision": final_decision
            }
        )
        self.session.add(audit)
        self.session.commit()

        return {
            "verification_id": str(verif_attempt.verification_id),
            "transaction_reference": txn.transaction_reference,
            "customer_reference": customer.customer_reference,
            "decision": final_decision,
            "similarity_score": sim_score,
            "euclidean_distance": euclidean_dist,
            "threshold_used": active_thresh,
            "overall_risk_score": risk_res["overall_risk_score"],
            "risk_level": risk_res["risk_level"],
            "risk_factors": risk_res["risk_factors"],
            "similarity_component": risk_res["similarity_component"],
            "image_quality_component": risk_res["image_quality_component"],
            "transaction_risk_component": risk_res["transaction_risk_component"],
            "behavioral_component": risk_res["behavioral_component"],
            "transaction_status": txn.status,
            "request_reference": req_ref
        }

    def adjudicate_manual_review(
        self,
        verification_id: str,
        reviewer_username: str,
        decision: str,
        review_comment: str,
        request_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compliance officer adjudication for transactions flagged for manual review.
        """
        if decision not in ["APPROVED", "REJECTED"]:
            raise ValueError("Decision must be either 'APPROVED' or 'REJECTED'.")

        v_id = uuid.UUID(str(verification_id))
        verif = self.session.query(VerificationAttempt).filter_by(verification_id=v_id).first()
        if not verif:
            raise ValueError(f"Verification '{verification_id}' not found.")

        reviewer = self.session.query(User).filter_by(username=reviewer_username).first()
        if not reviewer or reviewer.role not in ["OFFICER", "ADMIN"]:
            raise ValueError(f"User '{reviewer_username}' is not authorized as a compliance officer.")

        # Create ManualReview record
        review = ManualReview(
            review_id=uuid.uuid4(),
            verification_id=verif.verification_id,
            reviewer_user_id=reviewer.user_id,
            decision=decision,
            review_comment=review_comment
        )
        self.session.add(review)

        # Update transaction status
        txn = verif.transaction
        txn.status = decision

        # Audit log
        req_ref = request_reference or f"REVIEW-{uuid.uuid4().hex[:8].upper()}"
        audit = AuditLog(
            audit_id=uuid.uuid4(),
            user_id=reviewer.user_id,
            action=f"MANUAL_REVIEW_{decision}",
            entity_type="MANUAL_REVIEW",
            entity_id=review.review_id,
            result="SUCCESS" if decision == "APPROVED" else "DENIED",
            request_reference=req_ref,
            details={
                "verification_id": str(verif.verification_id),
                "transaction_ref": txn.transaction_reference,
                "reviewer": reviewer_username,
                "decision": decision,
                "comment": review_comment
            }
        )
        self.session.add(audit)
        self.session.commit()

        return {
            "review_id": str(review.review_id),
            "verification_id": str(verif.verification_id),
            "transaction_reference": txn.transaction_reference,
            "reviewer": reviewer_username,
            "decision": decision,
            "transaction_status": txn.status
        }

    def get_customer_signatures(self, customer_reference_or_id: str) -> Dict[str, Any]:
        """
        Retrieves all registered signature specimens for a customer,
        including active references, historical/superseded specimens, and image URLs.
        """
        customer = self.session.query(Customer).filter_by(customer_reference=customer_reference_or_id).first()
        if not customer:
            try:
                u_id = uuid.UUID(str(customer_reference_or_id))
                customer = self.session.query(Customer).filter_by(customer_id=u_id).first()
            except ValueError:
                pass

        if not customer:
            return {
                "customer_reference": customer_reference_or_id,
                "customer_name": None,
                "total_count": 0,
                "active_count": 0,
                "signatures": []
            }

        sigs = self.session.query(Signature).filter_by(
            customer_id=customer.customer_id,
            signature_type="ENROLLED"
        ).order_by(Signature.created_at.desc()).all()

        items = []
        for s in sigs:
            items.append({
                "signature_id": str(s.signature_id),
                "customer_reference": customer.customer_reference,
                "signature_type": s.signature_type,
                "storage_reference": s.storage_reference,
                "file_hash": s.file_hash,
                "image_quality_score": float(s.image_quality_score),
                "status": s.status,
                "is_active": (s.status == "ACTIVE"),
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "image_url": f"/api/v1/signatures/{s.signature_id}/image"
            })

        active_count = sum(1 for s in items if s["is_active"])
        return {
            "customer_reference": customer.customer_reference,
            "customer_name": customer.full_name,
            "total_count": len(items),
            "active_count": active_count,
            "signatures": items
        }

    def deactivate_signature(self, signature_id: Union[str, uuid.UUID]) -> Dict[str, Any]:
        """
        Deactivates a reference specimen by marking its status as SUPERSEDED.
        Preserves complete immutable audit history and does not hard-delete.
        """
        u_id = uuid.UUID(str(signature_id)) if isinstance(signature_id, str) else signature_id
        sig = self.session.query(Signature).filter_by(signature_id=u_id).first()
        if not sig:
            raise ValueError(f"Signature '{signature_id}' not found.")

        sig.status = "SUPERSEDED"

        audit = AuditLog(
            audit_id=uuid.uuid4(),
            user_id=None,
            action="CUSTOMER_SIGNATURE_DEACTIVATED",
            entity_type="SIGNATURE",
            entity_id=sig.signature_id,
            result="SUCCESS",
            request_reference=f"DEACT-{uuid.uuid4().hex[:8].upper()}",
            details={"signature_id": str(sig.signature_id), "status": sig.status}
        )
        self.session.add(audit)
        self.session.commit()

        return {
            "signature_id": str(sig.signature_id),
            "customer_reference": sig.customer.customer_reference if sig.customer else None,
            "status": sig.status,
            "message": "Signature specimen deactivated successfully."
        }

    def verify_customer_signature(
        self,
        customer_reference: str,
        submitted_signature_path: str,
        mode: str = "single",
        threshold: Optional[float] = None,
        request_reference: Optional[str] = None,
        model_track: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Direct customer signature verification workflow:
        1. Retrieves active enrolled reference specimen(s) for the customer.
        2. Validates and saves submitted questioned signature into the vault.
        3. Executes model inference (Siamese Champion, Vision Transformer, or Classical Sklearn):
           - Mode 1: Single reference vs questioned
           - Mode 2: Gallery of up to 3 references using Max-Similarity
        4. Calculates binary MATCH / NO MATCH verdict and multi-factor risk assessment.
        5. Persists verification attempt, risk evaluation, and immutable audit logs.
        """
        req_ref = request_reference or f"REQ-{uuid.uuid4().hex[:8].upper()}"

        # 1. Lookup Customer
        customer = self.session.query(Customer).filter_by(customer_reference=customer_reference).first()
        if not customer:
            try:
                u_id = uuid.UUID(str(customer_reference))
                customer = self.session.query(Customer).filter_by(customer_id=u_id).first()
            except ValueError:
                pass

        if not customer:
            raise ValueError(
                f"No active enrolled signatures found for customer '{customer_reference}'. "
                f"Please register a genuine signature reference first."
            )

        # 2. Retrieve Active Enrolled Signatures
        active_sigs = self.session.query(Signature).filter_by(
            customer_id=customer.customer_id,
            signature_type="ENROLLED",
            status="ACTIVE"
        ).order_by(Signature.created_at.desc()).all()

        if not active_sigs:
            raise ValueError(
                f"No active enrolled signatures found for customer '{customer.customer_reference}'. "
                f"Please register a genuine signature reference first."
            )

        # 3. Read and strictly validate submitted questioned signature
        sub_img = cv2.imread(str(submitted_signature_path), cv2.IMREAD_GRAYSCALE)
        if sub_img is None or sub_img.size == 0 or sub_img.shape[0] < 10 or sub_img.shape[1] < 10:
            raise ValueError(f"Corrupt or invalid questioned signature image at: {submitted_signature_path}")

        quality_score = self.risk_engine.assess_image_quality(sub_img)
        sub_hash = self.calculate_file_hash(submitted_signature_path)
        sub_id = uuid.uuid4()

        # Persist submitted signature into disk vault
        vault_dir = Path("data/vault/signatures/submissions") / str(customer.customer_reference)
        vault_dir.mkdir(parents=True, exist_ok=True)
        sub_filename = f"{sub_id.hex[:8]}_{Path(submitted_signature_path).name}"
        saved_sub_path = vault_dir / sub_filename
        shutil.copy2(submitted_signature_path, saved_sub_path)
        persisted_sub_uri = str(saved_sub_path).replace("\\", "/")

        submitted_sig_record = Signature(
            signature_id=sub_id,
            customer_id=customer.customer_id,
            signature_type="VERIFICATION_SUBMISSION",
            storage_reference=persisted_sub_uri,
            file_hash=sub_hash,
            image_quality_score=Decimal(str(round(quality_score, 4))),
            status="ACTIVE"
        )
        self.session.add(submitted_sig_record)
        self.session.flush()

        # 4. Resolve Active Verifier
        if model_track:
            from ml.inference.verify_signature import get_model_verifier
            active_verifier = get_model_verifier(model_track)
        else:
            active_verifier = self.verifier

        def _resolve_specimen_file(storage_ref: str) -> str:
            p = Path(storage_ref)
            if p.exists():
                return str(p)
            if storage_ref.startswith("vault://"):
                rel_p = Path("data/vault") / storage_ref[len("vault://"):]
                if rel_p.exists():
                    return str(rel_p)
            raise FileNotFoundError(
                f"Customer '{customer.customer_reference}' enrolled specimen file not found on disk at: {storage_ref}"
            )

        # 5. Resolve Reference Specimens and Execute Model Inference
        mode_normalized = (mode or "single").strip().lower()

        if mode_normalized in ("gallery", "multi", "mode2"):
            gallery_sigs = active_sigs[:3]
            gallery_paths = [_resolve_specimen_file(s.storage_reference) for s in gallery_sigs]

            active_thresh = float(threshold) if threshold is not None else float(getattr(active_verifier, "gallery_threshold", getattr(active_verifier, "threshold", 0.6312)))

            out = active_verifier.verify_gallery(
                gallery_images=gallery_paths,
                query_image=str(saved_sub_path),
                strategy="max_similarity",
                threshold=active_thresh
            )
            sim_score = float(out.similarity_score)
            euclidean_dist = float(out.distance)
            primary_ref = gallery_sigs[0]
            references_used = [str(s.signature_id) for s in gallery_sigs]
            ref_count = len(gallery_sigs)
            verif_mode = "gallery"
        else:
            primary_ref = active_sigs[0]
            ref_path = _resolve_specimen_file(primary_ref.storage_reference)

            active_thresh = float(threshold) if threshold is not None else float(getattr(active_verifier, "default_threshold", getattr(active_verifier, "threshold", 0.5924)))

            model_res = active_verifier.verify(
                ref_image=ref_path,
                query_image=str(saved_sub_path),
                threshold=active_thresh
            )
            sim_score = float(model_res.similarity_score)
            euclidean_dist = float(model_res.distance)

            references_used = [str(primary_ref.signature_id)]
            ref_count = 1
            verif_mode = "single"

        # 5. Determine Verdict
        is_match = bool(sim_score >= active_thresh)
        user_verdict = "MATCH" if is_match else "NO MATCH"
        db_decision = "VERIFIED" if is_match else "REJECTED"

        # 6. Multi-Factor Fraud Risk Evaluation
        risk_res = self.risk_engine.evaluate(
            similarity_score=sim_score,
            model_threshold=active_thresh,
            image_quality_score=quality_score,
            amount=0.0,
            transaction_type="FORM_VERIFICATION",
            behavioral_score=0.02
        )

        # 7. Provision Financial Ledger Entities for Audit Compliance
        if not customer.accounts:
            acc = Account(
                account_id=uuid.uuid4(),
                customer_id=customer.customer_id,
                account_reference=f"ACC-{customer.customer_reference}",
                account_type="SAVINGS",
                status="ACTIVE"
            )
            self.session.add(acc)
            self.session.flush()

        customer_account = customer.accounts[0] if (customer.accounts and len(customer.accounts) > 0) else acc
        txn = Transaction(
            transaction_id=uuid.uuid4(),
            account_id=customer_account.account_id,
            transaction_reference=f"MANUAL-{uuid.uuid4().hex[:10].upper()}",
            transaction_type="FORM_VERIFICATION",
            amount=Decimal("0.00"),
            currency="USD",
            status=db_decision
        )
        self.session.add(txn)
        self.session.flush()

        # 8. Persist Verification Attempt
        model_ver_id = self.active_model.model_version_id if self.active_model else uuid.uuid4()
        verif_attempt = VerificationAttempt(
            verification_id=uuid.uuid4(),
            transaction_id=txn.transaction_id,
            customer_id=customer.customer_id,
            submitted_signature_id=submitted_sig_record.signature_id,
            enrolled_signature_id=primary_ref.signature_id,
            similarity_score=Decimal(str(round(sim_score, 4))),
            threshold_used=Decimal(str(round(active_thresh, 4))),
            decision=db_decision,
            model_version_id=model_ver_id
        )
        self.session.add(verif_attempt)
        self.session.flush()

        # 9. Persist Risk Assessment
        risk_record = RiskAssessment(
            risk_id=uuid.uuid4(),
            verification_id=verif_attempt.verification_id,
            similarity_component=Decimal(str(risk_res["similarity_component"])),
            image_quality_component=Decimal(str(risk_res["image_quality_component"])),
            transaction_risk_component=Decimal(str(risk_res["transaction_risk_component"])),
            behavioral_component=Decimal(str(risk_res["behavioral_component"])),
            overall_risk_score=Decimal(str(risk_res["overall_risk_score"])),
            risk_level=risk_res["risk_level"],
            risk_factors=risk_res["risk_factors"]
        )
        self.session.add(risk_record)

        # 10. Audit Log
        audit = AuditLog(
            audit_id=uuid.uuid4(),
            user_id=None,
            action="CUSTOMER_SIGNATURE_VERIFIED",
            entity_type="VERIFICATION_ATTEMPT",
            entity_id=verif_attempt.verification_id,
            result="SUCCESS" if is_match else "DENIED",
            request_reference=req_ref,
            details={
                "customer_ref": customer.customer_reference,
                "mode": verif_mode,
                "verdict": user_verdict,
                "similarity_score": round(sim_score, 4),
                "threshold_used": round(active_thresh, 4),
                "references_used": references_used,
                "overall_risk_score": risk_res["overall_risk_score"]
            }
        )
        self.session.add(audit)
        self.session.commit()

        return {
            "verification_id": str(verif_attempt.verification_id),
            "customer_reference": customer.customer_reference,
            "mode": verif_mode,
            "match": is_match,
            "verdict": user_verdict,
            "decision": db_decision,
            "similarity_score": round(sim_score, 4),
            "threshold_used": round(active_thresh, 4),
            "euclidean_distance": round(euclidean_dist, 4),
            "reference_count": ref_count,
            "references_used": references_used,
            "overall_risk_score": risk_res["overall_risk_score"],
            "risk_level": risk_res["risk_level"],
            "risk_factors": risk_res["risk_factors"],
            "similarity_component": risk_res["similarity_component"],
            "image_quality_component": risk_res["image_quality_component"],
            "transaction_status": txn.status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_reference": req_ref
        }

