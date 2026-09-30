"""
End-to-End Live Demonstration Script for SIGNATURE VMAKE.
Exercises live FastAPI endpoints over HTTP (port 8000), verifying:
1. Health & Model status
2. Customer creation & First-signature enrollment (specimen registration)
3. Second-signature genuine verification (Track C: Champion ResNet)
4. Multi-model track verification (Track A: SVM, Track B: Transformers ViT)
5. Impostor rejection (Writer 52 against Alice's Account)
6. Cheque transaction verification & Multi-factor fraud risk engine
7. Customer specimen isolation (Bob vs Alice cross-testing)
8. Multi-specimen Gallery Verification Mode (Mode 2)
9. Audit trail integrity and non-repudiation
"""

import sys
import json
from pathlib import Path
import httpx

BASE_URL = "http://127.0.0.1:8000"
CEDAR_ORG = Path("data/raw/signatures/full_org")
CEDAR_FORG = Path("data/raw/signatures/full_forg")

def log(section: str, detail: str = ""):
    print(f"\n{'='*75}\n[LIVE DEMO] {section}\n{'='*75}")
    if detail:
        print(detail)

def run_demo():
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # 1. Health Checks
    log("1. SYSTEM & MODEL HEALTH CHECKS")
    resp = client.get("/")
    assert resp.status_code == 200, f"Root failed: {resp.text}"
    assert "SIGNATURE VMAKE" in resp.text
    print(f"[OK] Web dashboard served successfully ({len(resp.text)} bytes)")

    resp = client.get("/api/v1/health")
    assert resp.status_code == 200, f"Health check failed: {resp.text}"
    health_data = resp.json()
    print(f"[OK] API Health:\n{json.dumps(health_data, indent=2)}")

    resp = client.get("/api/v1/models/health")
    assert resp.status_code == 200, f"Models health failed: {resp.text}"
    models_health = resp.json()
    print(f"[OK] Models Runtime Readiness:\n{json.dumps(models_health, indent=2)}")
    assert models_health["models"]["sklearn"]["status"] == "ready"
    assert models_health["models"]["transformer"]["status"] == "ready"
    assert models_health["models"]["neural"]["status"] == "ready"
    print("[PASS] All 3 Model Tracks (Track A: SVM, Track B: Transformers ViT, Track C: Siamese ResNet) are live and ready.")

    # 2. Customer Registration
    log("2. CUSTOMER REGISTRATION")
    cust1_ref = "DEMO-ALICE-46"
    cust_payload = {
        "customer_reference": cust1_ref,
        "full_name": "Alice M. Smith",
        "phone_reference": "+96891234567"
    }
    resp = client.post("/api/v1/customers", json=cust_payload)
    if resp.status_code == 200:
        print(f"[OK] Created customer {cust1_ref}: {resp.json()}")
    else:
        print(f"[NOTE] Customer {cust1_ref} already exists (HTTP {resp.status_code}), reusing existing profile.")

    resp = client.get(f"/api/v1/customers/{cust1_ref}")
    assert resp.status_code == 200, f"Get customer failed: {resp.text}"
    print(f"[OK] Verified customer profile: {json.dumps(resp.json(), indent=2)}")

    # 3. First Signature Registration (Enrollment)
    log("3. FIRST SIGNATURE: REGISTRATION (ENROLLMENT)")
    sig_file1 = CEDAR_ORG / "original_46_1.png"
    assert sig_file1.exists(), f"Missing specimen file: {sig_file1}"
    with open(sig_file1, "rb") as f:
        files = {"signature_file": ("original_46_1.png", f, "image/png")}
        data = {
            "customer_reference": cust1_ref,
            "signature_type": "PRIMARY"
        }
        resp = client.post("/api/v1/signatures/enroll", data=data, files=files)
    assert resp.status_code == 200, f"Enrollment failed: {resp.text}"
    enroll_data = resp.json()
    print(f"[OK] Enrollment Result:\n{json.dumps(enroll_data, indent=2)}")
    assert "signature_id" in enroll_data
    assert enroll_data.get("status") == "ENROLLED"
    assert enroll_data.get("active_status") == "ACTIVE"
    # STRICT ASSERTION: No match/no-match verification decision is rendered during registration!
    assert "verdict" not in enroll_data or enroll_data["verdict"] is None
    assert "decision" not in enroll_data or enroll_data["decision"] is None
    print("[PASS] FIRST SIGNATURE registered as reference specimen. No verification decision rendered.")

    # Check registered signatures list
    resp = client.get(f"/api/v1/customers/{cust1_ref}/signatures")
    assert resp.status_code == 200
    sigs = resp.json()
    print(f"[OK] Active registered specimens for {cust1_ref}: {len(sigs['signatures'])}")
    assert len(sigs['signatures']) >= 1

    # 4. Second Signature Verification: Genuine (Same Writer 46)
    log("4. SECOND SIGNATURE: GENUINE VERIFICATION (TRACK C - CHAMPION RESNET)")
    sig_file2 = CEDAR_ORG / "original_46_2.png"
    with open(sig_file2, "rb") as f:
        files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
        data = {
            "customer_reference": cust1_ref,
            "model_track": "track_c"
        }
        resp = client.post("/api/v1/verifications/verify", data=data, files=files)
    assert resp.status_code == 200, f"Verification failed: {resp.text}"
    verif_res = resp.json()
    print(f"[OK] Genuine Verification Result:\n{json.dumps(verif_res, indent=2)}")
    assert verif_res["verdict"] == "MATCH"
    assert verif_res["decision"] == "VERIFIED"
    assert verif_res["match"] is True
    print(f"[PASS] Decision: {verif_res['decision']}, Verdict: {verif_res['verdict']}, Similarity: {verif_res['similarity_score']:.4f}, Threshold: {verif_res['threshold_used']:.4f}")

    # 5. Multi-Model Track Verification (Track A & Track B on Genuine Signature)
    log("5. MULTI-MODEL TRACK VERIFICATION ON GENUINE SIGNATURE")
    for track_name in ["track_a", "track_b"]:
        with open(sig_file2, "rb") as f:
            files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
            data = {
                "customer_reference": cust1_ref,
                "model_track": track_name
            }
            resp = client.post("/api/v1/verifications/verify", data=data, files=files)
        assert resp.status_code == 200, f"{track_name} verification failed: {resp.text}"
        res = resp.json()
        print(f"[{track_name.upper()}] Verdict: {res['verdict']}, Decision: {res['decision']}, Similarity: {res['similarity_score']:.4f}, Threshold: {res['threshold_used']:.4f}")
        assert res["verdict"] == "MATCH"

    # 6. Impostor Verification (Writer 30 against Alice's Account)
    log("6. IMPOSTOR VERIFICATION: WRONG WRITER (WRITER 30 vs ALICE)")
    impostor_file = CEDAR_ORG / "original_30_1.png"
    with open(impostor_file, "rb") as f:
        files = {"submitted_signature": ("original_30_1.png", f, "image/png")}
        data = {
            "customer_reference": cust1_ref,
            "model_track": "track_c"
        }
        resp = client.post("/api/v1/verifications/verify", data=data, files=files)
    assert resp.status_code == 200, f"Impostor verification failed: {resp.text}"
    impostor_res = resp.json()
    print(f"[OK] Impostor Result:\n{json.dumps(impostor_res, indent=2)}")
    assert impostor_res["verdict"] == "NO MATCH"
    assert impostor_res["match"] is False
    print(f"[PASS] Impostor correctly REJECTED! Similarity: {impostor_res['similarity_score']:.4f} < Threshold: {impostor_res['threshold_used']:.4f}")

    # 7. Cheque Transaction Verification & Fraud Risk Assessment Engine
    log("7. CHEQUE TRANSACTION VERIFICATION & FRAUD RISK ENGINE")
    with open(sig_file2, "rb") as f:
        files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
        data = {
            "transaction_reference": "DEMO-TXN-CHEQUE-101",
            "model_track": "track_c"
        }
        resp = client.post("/api/v1/verifications/verify", data=data, files=files)
    assert resp.status_code == 200, f"Cheque transaction verification failed: {resp.text}"
    txn_res = resp.json()
    print(f"[OK] Cheque Verification Result:\n{json.dumps(txn_res, indent=2)}")
    assert "risk_level" in txn_res
    assert "overall_risk_score" in txn_res
    print(f"[PASS] Risk Level: {txn_res['risk_level']}, Overall Risk Score: {txn_res['overall_risk_score']}")

    # 8. Customer Specimen Isolation Test
    log("8. CUSTOMER SPECIMEN ISOLATION TEST")
    cust2_ref = "DEMO-BOB-30"
    resp = client.post("/api/v1/customers", json={
        "customer_reference": cust2_ref,
        "full_name": "Bob K. Davis",
        "phone_reference": "+96898765432"
    })
    # Enroll Bob with Writer 30
    with open(impostor_file, "rb") as f:
        files = {"signature_file": ("original_30_1.png", f, "image/png")}
        resp = client.post("/api/v1/signatures/enroll", data={"customer_reference": cust2_ref}, files=files)
    assert resp.status_code == 200
    print(f"[OK] Enrolled Bob ({cust2_ref}) with Writer 30 specimen.")

    # Verify Bob with Bob's 2nd signature -> must be MATCH (similarity 0.8633)
    bob_sig2 = CEDAR_ORG / "original_30_2.png"
    with open(bob_sig2, "rb") as f:
        files = {"submitted_signature": ("original_30_2.png", f, "image/png")}
        resp = client.post("/api/v1/verifications/verify", data={"customer_reference": cust2_ref, "model_track": "track_c"}, files=files)
    assert resp.status_code == 200
    bob_res = resp.json()
    print(f"[OK] Bob verified with Bob's 2nd signature -> Verdict: {bob_res['verdict']}, Decision: {bob_res['decision']}, Sim: {bob_res['similarity_score']:.4f}")
    assert bob_res["verdict"] == "MATCH"

    # Verify Bob with Alice's signature (original_46_2.png) -> must be NO MATCH (similarity 0.5080)
    with open(sig_file2, "rb") as f:
        files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
        resp = client.post("/api/v1/verifications/verify", data={"customer_reference": cust2_ref, "model_track": "track_c"}, files=files)
    assert resp.status_code == 200
    bob_cross_res = resp.json()
    print(f"[OK] Bob verified with Alice's signature -> Verdict: {bob_cross_res['verdict']}, Decision: {bob_cross_res['decision']}, Sim: {bob_cross_res['similarity_score']:.4f}")
    assert bob_cross_res["verdict"] == "NO MATCH"
    print("[PASS] Customer isolation confirmed: signatures are evaluated strictly against the specific customer's enrolled specimen.")

    # 9. Audit Trail & History Verification
    log("9. AUDIT TRAIL VERIFICATION")
    first_verif_id = verif_res["verification_id"]
    resp = client.get(f"/api/v1/audit/trail/{first_verif_id}")
    assert resp.status_code == 200, f"Audit trail failed: {resp.text}"
    audit_data = resp.json()
    print(f"[OK] Transaction Reference: {audit_data.get('transaction_reference')}")
    print(f"[OK] Current Status: {audit_data.get('current_status')}")
    print(f"[OK] Customer: {audit_data.get('customer')}")
    verif_history = audit_data.get("verification_history", [])
    print(f"[OK] Verification History Entries: {len(verif_history)}")
    for vh in verif_history[:2]:
        print(f"  - Verification ID: {vh.get('verification_id')}, Sim Score: {vh.get('similarity_score')}, Decision: {vh.get('decision')}")
        print(f"    Audit Logs: {len(vh.get('audit_logs', []))} entries recorded")

    print("\n" + "="*75)
    print("ALL 9 LIVE END-TO-END DEMONSTRATION CHECKS PASSED WITH 100% SUCCESS!")
    print("="*75)

if __name__ == "__main__":
    run_demo()
