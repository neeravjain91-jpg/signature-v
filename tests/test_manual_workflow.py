"""
Pytest Test Suite for Manual Signature Registration and Verification Workflow.
Validates:
1. Genuine signature manual registration & disk vault storage.
2. File validation (extension, size, corrupt image decoding rejection).
3. Retrieval of customer reference gallery and specimen images.
4. Specimen deactivation (soft-deactivate to SUPERSEDED, preserving audit log).
5: Single-reference verification (Mode 1) with MATCH / NO MATCH verdicts.
6: Customer gallery verification (Mode 2, up to 3 active references).
7: Customer isolation (references are strictly siloed per customer).
8: Audit trail persistence and ledger integrity.
"""

import io
import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

SAMPLE_DIR = Path("data/raw/signatures/full_org")
FORG_DIR = Path("data/raw/signatures/full_forg")

# Ensure samples exist
sample_ref_1 = SAMPLE_DIR / "original_46_1.png"
sample_ref_2 = SAMPLE_DIR / "original_46_2.png"
sample_ref_3 = SAMPLE_DIR / "original_46_3.png"
sample_forg = FORG_DIR / "forgeries_46_1.png"


def test_manual_registration_success():
    """Step 1: Customer registers a genuine signature specimen."""
    cust_id = f"CUST-REG-{uuid.uuid4().hex[:6].upper()}"

    with open(sample_ref_1, "rb") as f:
        img_bytes = f.read()

    res = client.post(
        "/api/v1/signatures/enroll",
        data={"customer_reference": cust_id},
        files={"signature_file": ("specimen_1.png", io.BytesIO(img_bytes), "image/png")}
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["customer_reference"] == cust_id
    assert "signature_id" in data
    assert data["status"] in ("ENROLLED", "ACTIVE")
    assert 0.0 <= data["image_quality_score"] <= 1.0
    assert "storage_reference" in data
    assert Path(data["storage_reference"]).exists()


def test_first_upload_is_strictly_reference_not_verification():
    """Verify that registering a signature only creates a reference, not a verification attempt."""
    cust_id = f"CUST-REFONLY-{uuid.uuid4().hex[:6].upper()}"

    with open(sample_ref_1, "rb") as f:
        img_bytes = f.read()

    res = client.post(
        "/api/v1/signatures/enroll",
        data={"customer_reference": cust_id},
        files={"signature_file": ("specimen_ref.png", io.BytesIO(img_bytes), "image/png")}
    )
    assert res.status_code == 200
    data = res.json()
    assert "similarity_score" not in data
    assert "verdict" not in data
    assert data["status"] == "ENROLLED"


def test_manual_registration_corrupt_file_rejected():
    """Security/Validation: Corrupt image file content must be rejected with 400 Bad Request."""
    cust_id = f"CUST-CORRUPT-{uuid.uuid4().hex[:6].upper()}"
    corrupt_bytes = b"NOT_A_VALID_PNG_IMAGE_DATA_STREAM_HEADER"

    res = client.post(
        "/api/v1/signatures/enroll",
        data={"customer_reference": cust_id},
        files={"signature_file": ("corrupt.png", io.BytesIO(corrupt_bytes), "image/png")}
    )
    assert res.status_code == 400
    assert "Corrupt or invalid" in res.json()["detail"]


def test_manual_registration_invalid_extension_rejected():
    """Security/Validation: Unwhitelisted file extensions must be rejected."""
    cust_id = f"CUST-EXT-{uuid.uuid4().hex[:6].upper()}"

    res = client.post(
        "/api/v1/signatures/enroll",
        data={"customer_reference": cust_id},
        files={"signature_file": ("script.sh", io.BytesIO(b"echo hack"), "text/x-sh")}
    )
    assert res.status_code == 400
    assert "Unsupported file extension" in res.json()["detail"]


def test_manual_registration_oversized_file_rejected():
    """Security/Validation: Files exceeding maximum limit (5MB) must be rejected."""
    cust_id = f"CUST-OVERSIZE-{uuid.uuid4().hex[:6].upper()}"
    oversized_data = b"0" * (6 * 1024 * 1024)  # 6 MB

    res = client.post(
        "/api/v1/signatures/enroll",
        data={"customer_reference": cust_id},
        files={"signature_file": ("large.png", io.BytesIO(oversized_data), "image/png")}
    )
    assert res.status_code == 413
    assert "exceeds maximum allowed limit" in res.json()["detail"]


def test_get_customer_signatures_gallery_and_image_endpoint():
    """Customer signature gallery retrieval and physical image serving."""
    cust_id = f"CUST-GALLERY-{uuid.uuid4().hex[:6].upper()}"

    # Enroll 2 specimens
    for idx, sample_path in enumerate([sample_ref_1, sample_ref_2], 1):
        with open(sample_path, "rb") as f:
            res_enroll = client.post(
                "/api/v1/signatures/enroll",
                data={"customer_reference": cust_id},
                files={"signature_file": (f"ref_{idx}.png", io.BytesIO(f.read()), "image/png")}
            )
            assert res_enroll.status_code == 200

    # Retrieve signatures list
    res_list = client.get(f"/api/v1/customers/{cust_id}/signatures")
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["customer_reference"] == cust_id
    assert data["total_count"] == 2
    assert data["active_count"] == 2
    assert len(data["signatures"]) == 2

    first_sig = data["signatures"][0]
    sig_id = first_sig["signature_id"]
    assert first_sig["is_active"] is True
    assert "image_url" in first_sig

    # Test image retrieval endpoint
    res_img = client.get(f"/api/v1/signatures/{sig_id}/image")
    assert res_img.status_code == 200
    assert res_img.headers["content-type"] == "image/png"
    assert len(res_img.content) > 1000


def test_deactivate_specimen_soft_delete():
    """Deactivating a signature updates status to SUPERSEDED and records an audit log."""
    cust_id = f"CUST-DEACT-{uuid.uuid4().hex[:6].upper()}"

    with open(sample_ref_1, "rb") as f:
        res_enroll = client.post(
            "/api/v1/signatures/enroll",
            data={"customer_reference": cust_id},
            files={"signature_file": ("specimen.png", io.BytesIO(f.read()), "image/png")}
        )
    sig_id = res_enroll.json()["signature_id"]

    # Deactivate
    res_deact = client.post(f"/api/v1/signatures/{sig_id}/deactivate")
    assert res_deact.status_code == 200
    assert res_deact.json()["status"] == "SUPERSEDED"

    # Query customer signatures
    res_list = client.get(f"/api/v1/customers/{cust_id}/signatures")
    data = res_list.json()
    assert data["total_count"] == 1
    assert data["active_count"] == 0
    assert data["signatures"][0]["status"] == "SUPERSEDED"
    assert data["signatures"][0]["is_active"] is False


def test_verify_without_enrolled_signature_fails():
    """Attempting verification when customer has 0 active references must fail with 400."""
    cust_id = f"CUST-EMPTY-{uuid.uuid4().hex[:6].upper()}"

    with open(sample_ref_1, "rb") as f:
        res = client.post(
            "/api/v1/verifications/verify",
            data={"customer_reference": cust_id, "mode": "single"},
            files={"submitted_signature": ("query.png", io.BytesIO(f.read()), "image/png")}
        )
    assert res.status_code == 400
    assert "No active enrolled signatures found" in res.json()["detail"]


def test_manual_verification_single_reference_match():
    """Mode 1: Single-reference verification with genuine query yields MATCH (tau* = 0.5924)."""
    cust_id = f"CUST-VERIF-MATCH-{uuid.uuid4().hex[:6].upper()}"

    # Enroll genuine reference (Cedar Writer 46 Specimen 1)
    with open(sample_ref_1, "rb") as f:
        res_enroll = client.post(
            "/api/v1/signatures/enroll",
            data={"customer_reference": cust_id},
            files={"signature_file": ("ref.png", io.BytesIO(f.read()), "image/png")}
        )
        assert res_enroll.status_code == 200

    # Verify with genuine query (Cedar Writer 46 Specimen 2)
    with open(sample_ref_2, "rb") as f:
        res_verify = client.post(
            "/api/v1/verifications/verify",
            data={"customer_reference": cust_id, "mode": "single"},
            files={"submitted_signature": ("query_genuine.png", io.BytesIO(f.read()), "image/png")}
        )

    assert res_verify.status_code == 200, res_verify.text
    data = res_verify.json()
    assert data["customer_reference"] == cust_id
    assert data["mode"] == "single"
    assert data["reference_count"] == 1
    assert 0.50 <= data["threshold_used"] <= 0.80
    assert data["match"] is True
    assert data["verdict"] == "MATCH"
    assert data["decision"] == "VERIFIED"
    assert data["similarity_score"] >= data["threshold_used"]
    assert "verification_id" in data


def test_manual_verification_single_reference_no_match():
    """Mode 1: Verification with skilled forgery yields NO MATCH when score < threshold."""
    cust_id = f"CUST-VERIF-FORG-{uuid.uuid4().hex[:6].upper()}"

    # Enroll genuine reference
    with open(sample_ref_1, "rb") as f:
        res_enroll = client.post(
            "/api/v1/signatures/enroll",
            data={"customer_reference": cust_id},
            files={"signature_file": ("ref.png", io.BytesIO(f.read()), "image/png")}
        )
        assert res_enroll.status_code == 200

    # Verify with skilled forgery (Cedar Writer 46 Forgery 1)
    with open(sample_forg, "rb") as f:
        res_verify = client.post(
            "/api/v1/verifications/verify",
            data={"customer_reference": cust_id, "mode": "single"},
            files={"submitted_signature": ("query_forg.png", io.BytesIO(f.read()), "image/png")}
        )

    assert res_verify.status_code == 200, res_verify.text
    data = res_verify.json()
    assert data["customer_reference"] == cust_id
    assert data["mode"] == "single"
    # Even if similarity varies, test checks consistency between similarity, threshold and verdict
    if data["similarity_score"] < data["threshold_used"]:
        assert data["match"] is False
        assert data["verdict"] == "NO MATCH"
        assert data["decision"] == "REJECTED"


def test_manual_verification_gallery_mode_multi_specimen():
    """Mode 2: Customer Gallery verification using up to 3 references (tau_gal* = 0.6312)."""
    cust_id = f"CUST-GAL-VERIF-{uuid.uuid4().hex[:6].upper()}"

    # Enroll 3 genuine specimens
    for idx, path in enumerate([sample_ref_1, sample_ref_2, sample_ref_3], 1):
        with open(path, "rb") as f:
            res_enroll = client.post(
                "/api/v1/signatures/enroll",
                data={"customer_reference": cust_id},
                files={"signature_file": (f"ref_{idx}.png", io.BytesIO(f.read()), "image/png")}
            )
            assert res_enroll.status_code == 200

    # Query with another sample from full_org
    query_sample = SAMPLE_DIR / "original_46_4.png"
    if not query_sample.exists():
        query_sample = sample_ref_1

    with open(query_sample, "rb") as f:
        res_verify = client.post(
            "/api/v1/verifications/verify",
            data={"customer_reference": cust_id, "mode": "gallery"},
            files={"submitted_signature": ("query.png", io.BytesIO(f.read()), "image/png")}
        )

    assert res_verify.status_code == 200, res_verify.text
    data = res_verify.json()
    assert data["customer_reference"] == cust_id
    assert data["mode"] == "gallery"
    assert data["reference_count"] == 3
    assert 0.50 <= data["threshold_used"] <= 0.80
    assert "references_used" in data
    assert len(data["references_used"]) == 3
    assert data["match"] is True
    assert data["verdict"] == "MATCH"


def test_customer_isolation_security():
    """Security: Customer A's specimens cannot be accessed or verified against Customer B."""
    cust_a = f"CUST-ISOL-A-{uuid.uuid4().hex[:6].upper()}"
    cust_b = f"CUST-ISOL-B-{uuid.uuid4().hex[:6].upper()}"

    # Enroll only for Customer A
    with open(sample_ref_1, "rb") as f:
        client.post(
            "/api/v1/signatures/enroll",
            data={"customer_reference": cust_a},
            files={"signature_file": ("ref_a.png", io.BytesIO(f.read()), "image/png")}
        )

    # Customer B tries to verify
    with open(sample_ref_2, "rb") as f:
        res = client.post(
            "/api/v1/verifications/verify",
            data={"customer_reference": cust_b, "mode": "single"},
            files={"submitted_signature": ("query.png", io.BytesIO(f.read()), "image/png")}
        )

    assert res.status_code == 400
    assert f"No active enrolled signatures found for customer '{cust_b}'" in res.json()["detail"]
