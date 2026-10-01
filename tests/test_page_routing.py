"""
Tests for SIGNATURE VMAKE Multi-Page Frontend Routing and Static Asset Delivery.
Validates:
1. Real independent page routes for all 7 application sections.
2. HTTP 200 OK responses, HTML content-type, page titles, and branding.
3. Static asset availability for CSS and modular JavaScript files.
4. Navigation structure without hash-anchor dependency.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_overview_page_route():
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>SIGNATURE VMAKE — Overview & Executive Dashboard</title>" in res.text
    assert 'id="global-header"' in res.text
    assert 'id="global-footer"' in res.text
    assert "/assets/css/app.css" in res.text
    assert "/assets/js/overview.js" in res.text


def test_overview_alias_route():
    res = client.get("/overview")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text


def test_manual_workflow_page_route():
    res = client.get("/manual-workflow")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Manual Register & Verify — SIGNATURE VMAKE</title>" in res.text
    assert "Manual Signature Registration & AI Verification" in res.text
    assert 'id="manual-customer-id"' in res.text
    assert 'id="btn-register-sig"' in res.text
    assert 'id="btn-verify-manual"' in res.text
    assert "/assets/js/manual-workflow.js" in res.text


def test_verification_studio_page_route():
    res = client.get("/verification-studio")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Cheque Studio — SIGNATURE VMAKE</title>" in res.text
    assert "Banking Cheque & Voucher Verification Studio" in res.text
    assert 'id="input-amount"' in res.text
    assert 'id="btn-verify"' in res.text
    assert "/assets/js/verification-studio.js" in res.text


def test_model_comparison_page_route():
    res = client.get("/model-comparison")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Model Comparison — SIGNATURE VMAKE</title>" in res.text
    assert "Machine Learning Candidate Model Benchmark" in res.text
    assert 'id="benchmark-table-body"' in res.text
    assert "/assets/js/model-comparison.js" in res.text


def test_compliance_queue_page_route():
    res = client.get("/compliance-queue")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Officer Queue — SIGNATURE VMAKE</title>" in res.text
    assert "Officer Adjudication Queue" in res.text
    assert 'id="queue-table-body"' in res.text
    assert 'id="review-modal"' in res.text
    assert "/assets/js/compliance-queue.js" in res.text


def test_audit_timeline_page_route():
    res = client.get("/audit-timeline")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Audit Trail — SIGNATURE VMAKE</title>" in res.text
    assert "Forensic Audit Trail & Verification History" in res.text
    assert 'id="lookup-txn-ref"' in res.text
    assert 'id="audit-trail-container"' in res.text
    assert "/assets/js/audit-timeline.js" in res.text


def test_model_registry_page_route():
    res = client.get("/model-registry")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "SIGNATURE VMAKE" in res.text
    assert "<title>Model Registry & Health — SIGNATURE VMAKE</title>" in res.text
    assert "Machine Learning Model Registry & Live Health" in res.text
    assert 'id="models-health-grid"' in res.text
    assert "/assets/js/model-registry.js" in res.text


def test_static_assets_delivery():
    # CSS
    res_css = client.get("/assets/css/app.css")
    assert res_css.status_code == 200
    assert "glass-card" in res_css.text

    # Global JS
    res_common = client.get("/assets/js/common.js")
    assert res_common.status_code == 200
    assert "renderGlobalNavigation" in res_common.text
    assert "NAV_ITEMS" in res_common.text

    # API Helper JS
    res_api = client.get("/assets/js/api.js")
    assert res_api.status_code == 200
    assert "apiGet" in res_api.text
    assert "apiPost" in res_api.text

    # Page JS
    for js_name in [
        "overview.js", "manual-workflow.js", "verification-studio.js",
        "model-comparison.js", "compliance-queue.js", "audit-timeline.js", "model-registry.js"
    ]:
        res_page_js = client.get(f"/assets/js/{js_name}")
        assert res_page_js.status_code == 200, f"Failed loading /assets/js/{js_name}"
        assert len(res_page_js.text) > 50


def test_navigation_urls_are_independent_routes():
    # Verify common.js defines real URL routes and not hash-anchor routes
    res = client.get("/assets/js/common.js")
    assert res.status_code == 200
    assert "path: '/manual-workflow'" in res.text
    assert "path: '/verification-studio'" in res.text
    assert "path: '/model-comparison'" in res.text
    assert "path: '/compliance-queue'" in res.text
    assert "path: '/audit-timeline'" in res.text
    assert "path: '/model-registry'" in res.text
    # Ensure hash anchors like href="#manual-workflow" are not in common.js
    assert "href=\"#manual-workflow\"" not in res.text
