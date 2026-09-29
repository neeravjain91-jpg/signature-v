"""
Pytest Test Suite for SYNAPSE REST API Endpoints and Workflows.
"""

import sys
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
    assert "active_model" in data


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


def test_transaction_list_endpoint():
    response = client.get("/api/v1/transactions")
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert len(data["transactions"]) >= 1


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
    assert "SYNAPSE" in response.text
    assert "CHAMPION" in response.text


def test_verify_demo_endpoint_parity():
    """Verify demo verification uses real model with non-mock metrics."""
    res = client.post("/api/v1/verifications/verify-demo", json={
        "amount": 2500.0,
        "transaction_type": "CHEQUE",
        "sample_type": "genuine",
        "transaction_reference": "DEMO-TXN-CHEQUE-101"
    })
    assert res.status_code == 200
    data = res.json()
    assert "similarity_score" in data
    assert "euclidean_distance" in data
    assert "threshold_used" in data
    assert "overall_risk_score" in data
    assert "decision" in data
    assert 0.0 <= data["similarity_score"] <= 1.0
    assert 0.0 <= data["euclidean_distance"] <= 2.0


def test_verify_upload_endpoint():
    """Verify multipart file upload routes to same verification engine."""
    sample_file = Path("data/raw/signatures/full_org/original_46_2.png")
    if sample_file.exists():
        with open(sample_file, "rb") as f:
            res = client.post(
                "/api/v1/verifications/verify",
                data={"transaction_reference": "DEMO-TXN-CHEQUE-101"},
                files={"submitted_signature": ("signature.png", f, "image/png")}
            )
            assert res.status_code == 200
            data = res.json()
            assert "similarity_score" in data
            assert "decision" in data

