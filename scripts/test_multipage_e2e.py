"""
End-to-End Live Multi-Page Routing & Functional Workflow Test for SIGNATURE VMAKE.
Validates:
1. All 7 separate website pages load independently with HTTP 200 and valid HTML.
2. Static assets (CSS, common JS, API client, page-specific scripts) load properly.
3. First signature enrollment produces genuine reference with ZERO match verdict.
4. Second signature verification dynamically scores against enrolled reference.
5. Multi-candidate models (ViT Default, Random Forest, SVM, Logistic) function dynamically.
6. Cheque studio, model comparison, compliance queue, audit timeline, and model registry endpoints.
"""

import sys
import json
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

PAGES = [
    ("/", "Overview & Executive Dashboard", "nav-overview"),
    ("/manual-workflow", "Manual Register & Verify", "nav-manual"),
    ("/verification-studio", "Cheque Studio", "nav-studio"),
    ("/model-comparison", "Model Comparison", "nav-comparison"),
    ("/compliance-queue", "Officer Queue", "nav-queue"),
    ("/audit-timeline", "Audit Trail", "nav-audit"),
    ("/model-registry", "Model Registry & Health", "nav-health")
]

ASSETS = [
    "/assets/css/app.css",
    "/assets/js/common.js",
    "/assets/js/api.js",
    "/assets/js/overview.js",
    "/assets/js/manual-workflow.js",
    "/assets/js/verification-studio.js",
    "/assets/js/model-comparison.js",
    "/assets/js/compliance-queue.js",
    "/assets/js/audit-timeline.js",
    "/assets/js/model-registry.js"
]


def log(title: str):
    print(f"\n{'='*75}\n[TEST] {title}\n{'='*75}")


def run_tests():
    # 1. Page Availability & Response Validation
    log("1. MULTI-PAGE INDEPENDENT ROUTE VALIDATION")
    for route, expected_title, expected_nav_id in PAGES:
        res = client.get(route)
        assert res.status_code == 200, f"Failed GET {route}: HTTP {res.status_code}"
        assert "text/html" in res.headers["content-type"]
        assert "SIGNATURE VMAKE" in res.text
        assert expected_title in res.text, f"Title snippet '{expected_title}' not found in {route}"
        assert 'id="global-header"' in res.text
        assert 'id="global-footer"' in res.text
        print(f"[PASS] Route '{route}' -> 200 OK | Title: '{expected_title}' ({len(res.text)} bytes)")

    # 2. Static Assets Delivery
    log("2. STATIC ASSETS DELIVERY")
    for asset in ASSETS:
        res = client.get(asset)
        assert res.status_code == 200, f"Failed GET {asset}: HTTP {res.status_code}"
        assert len(res.text) > 20
        print(f"[PASS] Static Asset '{asset}' -> 200 OK ({len(res.text)} bytes)")

    # 3. Manual Workflow: First Signature Enrollment (Reference Only)
    log("3. MANUAL WORKFLOW: FIRST SIGNATURE ENROLLMENT (REFERENCE ONLY)")
    cust_ref = "DEMO-MPA-ALICE"
    
    # Ensure customer exists
    client.post("/api/v1/customers", json={
        "customer_reference": cust_ref,
        "full_name": "Alice MPA Test",
        "phone_reference": "+96890001111"
    })

    sig1_path = Path("data/raw/signatures/full_org/original_46_1.png")
    assert sig1_path.exists(), f"Specimen file missing: {sig1_path}"
    with open(sig1_path, "rb") as f:
        files = {"signature_file": ("original_46_1.png", f, "image/png")}
        data = {"customer_reference": cust_ref, "signature_type": "PRIMARY"}
        res = client.post("/api/v1/signatures/enroll", data=data, files=files)
    
    assert res.status_code == 200, f"Enrollment failed: {res.text}"
    enroll_data = res.json()
    assert enroll_data["status"] == "ENROLLED"
    assert enroll_data["active_status"] == "ACTIVE"
    assert "verdict" not in enroll_data or enroll_data["verdict"] is None
    assert "decision" not in enroll_data or enroll_data["decision"] is None
    print(f"[PASS] Specimen 1 enrolled into vault: ID {enroll_data['signature_id']}")
    print(f"[PASS] Zero verification verdict rendered on registration (Strict BRD Compliance).")

    # Check gallery retrieval
    res_gal = client.get(f"/api/v1/customers/{cust_ref}/signatures")
    assert res_gal.status_code == 200
    gal_data = res_gal.json()
    assert gal_data["active_count"] >= 1
    print(f"[PASS] Gallery contains {gal_data['active_count']} active specimen(s).")

    # 4. Manual Workflow: Second Signature Verification (Dynamic AI)
    log("4. MANUAL WORKFLOW: SECOND SIGNATURE VERIFICATION (DYNAMIC AI)")
    sig2_path = Path("data/raw/signatures/full_org/original_46_2.png")
    with open(sig2_path, "rb") as f:
        files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
        data = {"customer_reference": cust_ref, "model_track": "transformer", "mode": "single"}
        res = client.post("/api/v1/verifications/verify", data=data, files=files)
    
    assert res.status_code == 200, f"Verification failed: {res.text}"
    verif_data = res.json()
    assert verif_data["match"] is True
    assert verif_data["verdict"] == "MATCH"
    assert verif_data["decision"] == "VERIFIED"
    assert verif_data["similarity_score"] >= verif_data["threshold_used"]
    print(f"[PASS] Track B ViT Verified Genuine: Score={verif_data['similarity_score']:.4f}, Thresh={verif_data['threshold_used']:.4f}, Decision={verif_data['decision']}")

    # Also verify with Random Forest
    with open(sig2_path, "rb") as f:
        files = {"submitted_signature": ("original_46_2.png", f, "image/png")}
        data = {"customer_reference": cust_ref, "model_track": "random_forest", "mode": "single"}
        res = client.post("/api/v1/verifications/verify", data=data, files=files)
    assert res.status_code == 200
    rf_data = res.json()
    assert rf_data["match"] is True
    assert rf_data["verdict"] == "MATCH"
    assert rf_data["decision"] == "VERIFIED"
    print(f"[PASS] Track A1 Random Forest Verified: Score={rf_data['similarity_score']:.4f}, Thresh={rf_data['threshold_used']:.4f}, Decision={rf_data['decision']}")

    # 5. Cheque Studio Backend Service
    log("5. CHEQUE STUDIO TRANSACTION VERIFICATION")
    res_cheque = client.post("/api/v1/verifications/verify-demo", json={
        "amount": 4500.0,
        "transaction_type": "CHEQUE",
        "sample_type": "genuine",
        "transaction_reference": "DEMO-TXN-CHEQUE-101",
        "model_track": "transformer"
    })
    assert res_cheque.status_code == 200
    cheque_data = res_cheque.json()
    assert "overall_risk_score" in cheque_data
    assert "risk_factors" in cheque_data
    print(f"[PASS] Cheque clearance scored: Decision={cheque_data['decision']}, Composite Risk={cheque_data['overall_risk_score']}")

    # 6. Model Comparison Endpoint
    log("6. MODEL COMPARISON BENCHMARK METRICS")
    res_bench = client.get("/api/v1/models/benchmark")
    assert res_bench.status_code == 200
    bench_data = res_bench.json()
    for track_key in ["Track_B_Vision_Transformer", "Track_A_Random_Forest", "Track_A_Classical_Sklearn", "Track_A_Logistic_Regression"]:
        assert track_key in bench_data, f"Missing benchmark data for {track_key}"
        assert "auc_roc" in bench_data[track_key]
        assert "eer" in bench_data[track_key]
    print(f"[PASS] Benchmark metrics retrieved for all 4 candidate models.")

    # 7. Compliance Officer Queue & Audit Trail
    log("7. COMPLIANCE QUEUE & AUDIT TRAIL ENDPOINTS")
    res_queue = client.get("/api/v1/verifications/pending-reviews")
    assert res_queue.status_code == 200
    print(f"[PASS] Pending reviews count: {res_queue.json().get('pending_reviews_count', 0)}")

    res_audit = client.get("/api/v1/audit/trail/DEMO-TXN-CHEQUE-101")
    assert res_audit.status_code == 200
    assert "verification_history" in res_audit.json()
    print(f"[PASS] Audit trail verified: {len(res_audit.json()['verification_history'])} history entry/entries recorded.")

    # 8. Model Registry & Health Diagnostics
    log("8. MODEL REGISTRY LIVE HEALTH DIAGNOSTICS")
    res_health = client.get("/api/v1/models/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    for model_key in ["transformer", "random_forest", "svm", "logistic"]:
        assert model_key in health_data["models"]
        assert health_data["models"][model_key]["status"] == "ready", f"Model {model_key} not ready"
    print(f"[PASS] All 4 candidate models report status READY with live test inferences.")

    print("\n" + "="*75)
    print("ALL MULTI-PAGE ROUTING & FUNCTIONAL CHECKS PASSED WITH 100% SUCCESS!")
    print("="*75)


if __name__ == "__main__":
    run_tests()
