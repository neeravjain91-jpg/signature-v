"""
Pytest Test Suite for SIGNATURE VMAKE REST API Endpoints and Workflows.
"""

import sys
import io
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "SIGNATURE VMAKE" in data["service"]
    assert "active_model" in data
    assert "available_tracks" in data
    assert "transformer" in data["available_tracks"]
    assert "sklearn" in data["available_tracks"]


def test_dashboard_metrics_endpoint():
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "risk_distribution" in data
    assert data["summary"]["total_verifications"] >= 0


def test_customer_list_endpoint():
    response = client.get("/api/v1/customers")
    assert response.status_code == 200
    data = response.json()
    assert "customers" in data
    assert len(data["customers"]) >= 1


def test_customer_create_endpoint():
    cust_ref = f"TEST-CUST-{uuid.uuid4().hex[:6].upper()}"
    res = client.post("/api/v1/customers", json={
        "customer_reference": cust_ref,
        "full_name": "Test Customer Jane",
        "phone_reference": "sha256:phone_hash_test"
    })
    assert res.status_code == 200
    assert res.json()["customer_reference"] == cust_ref


def test_transaction_list_and_create_endpoints():
    # 1. List transactions
    res_list = client.get("/api/v1/transactions")
    assert res_list.status_code == 200
    data = res_list.json()
    assert "transactions" in data
    assert len(data["transactions"]) >= 1

    # 2. Create transaction
    txn_ref = f"TEST-TXN-{uuid.uuid4().hex[:6].upper()}"
    res_create = client.post("/api/v1/transactions", json={
        "account_reference": "DEMO-ACC-CHK-8802",
        "transaction_reference": txn_ref,
        "transaction_type": "CHEQUE",
        "amount": 1250.0,
        "currency": "USD"
    })
    assert res_create.status_code == 200
    assert res_create.json()["transaction_reference"] == txn_ref
    assert res_create.json()["status"] == "PENDING"


def test_authentication_workflow():
    # Test valid officer login
    res_login = client.post("/api/v1/auth/login", json={
        "username": "officer_marcus",
        "password": "OfficerSecure!2026"
    })
    assert res_login.status_code == 200
    token_data = res_login.json()
    assert "access_token" in token_data
    token = token_data["access_token"]

    # Test me endpoint with bearer token
    res_me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_me.status_code == 200
    user_data = res_me.json()
    assert user_data["username"] == "officer_marcus"
    assert user_data["role"] == "OFFICER"


def test_audit_trail_endpoint():
    response = client.get("/api/v1/audit/trail/DEMO-TXN-CHEQUE-101")
    assert response.status_code == 200
    data = response.json()
    assert data["transaction_reference"] == "DEMO-TXN-CHEQUE-101"
    assert "verification_history" in data
    assert len(data["verification_history"]) >= 1


def test_web_interface_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "SIGNATURE VMAKE" in response.text
    assert "Model Comparison" in response.text


def test_model_benchmark_endpoint():
    response = client.get("/api/v1/models/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert "Track_A_Classical_Sklearn" in data
    assert "Track_B_Vision_Transformer" in data
    assert "Track_C_Siamese_ResNet" in data
    assert data["Track_A_Classical_Sklearn"]["auc_roc"] > 0.70
    assert data["Track_B_Vision_Transformer"]["auc_roc"] > 0.70
    assert data["Track_C_Siamese_ResNet"]["auc_roc"] > 0.80


def test_verify_demo_multi_track():
    """Verify demo verification with all 3 model tracks."""
    for track in ["siamese", "transformer", "sklearn"]:
        res = client.post("/api/v1/verifications/verify-demo", json={
            "amount": 3500.0,
            "transaction_type": "CHEQUE",
            "sample_type": "genuine",
            "transaction_reference": "DEMO-TXN-CHEQUE-101",
            "model_track": track
        })
        assert res.status_code == 200
        data = res.json()
        assert "similarity_score" in data
        assert "decision" in data
        assert 0.0 <= data["similarity_score"] <= 1.0


def test_get_verification_by_id():
    # 1. Trigger verification
    res_v = client.post("/api/v1/verifications/verify-demo", json={
        "amount": 2000.0,
        "transaction_type": "CHEQUE",
        "sample_type": "genuine",
        "transaction_reference": "DEMO-TXN-CHEQUE-101"
    })
    assert res_v.status_code == 200
    verif_id = res_v.json()["verification_id"]

    # 2. Retrieve verification by ID
    res_get = client.get(f"/api/v1/verifications/{verif_id}")
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["verification_id"] == verif_id
    assert "similarity_score" in data
    assert "risk_assessment" in data


def test_verify_upload_validation_rejects_invalid_file():
    """Security test: Reject files with unwhitelisted extensions."""
    fake_exe = io.BytesIO(b"MZ\x90\x00NotAnImage")
    res = client.post(
        "/api/v1/verifications/verify",
        data={"transaction_reference": "DEMO-TXN-CHEQUE-101"},
        files={"submitted_signature": ("malicious.exe", fake_exe, "application/octet-stream")}
    )
    assert res.status_code == 400
    assert "Unsupported file extension" in res.json()["detail"]
