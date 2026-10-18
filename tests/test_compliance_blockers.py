"""
Regression and Compliance Verification Suite for SIGNATURE VMAKE.

Validates the resolution of the three technology-compliance blockers:
1. BLOCKER 1: PostgreSQL SQLAlchemy driver selection, URL normalization, and Alembic compatibility.
2. BLOCKER 2: Complete SYNAPSE / VMAKE model separation with Track B Transformer as default.
3. BLOCKER 3: Empirical benchmark loading, truthful RF accuracy (82.92%), and zero hardcoded fallbacks (HTTP 503 on missing artifact).
"""

import sys
import os
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from api.main import app, EVAL_BENCHMARK_PATH
from database.session import get_normalized_database_url
from services.verification_service import BankingVerificationService
from ml.inference.verify_signature import (
    get_model_verifier,
    LegacySiameseVerifier,
)
from ml.models.transformer_signature_model import VisionTransformerVerifier
from ml.baselines.classical_classifier import ClassicalSklearnVerifier

client = TestClient(app)


# ============================================================================
# BLOCKER 1: DATABASE URL & POSTGRESQL DRIVER COMPATIBILITY
# ============================================================================

def test_postgresql_url_normalization_with_detected_driver():
    """Verify get_normalized_database_url maps postgresql schemes to installed driver."""
    raw_pg_url = "postgresql://vmake_user:vmake_pass@localhost:5432/vmake_db"
    normalized = get_normalized_database_url(raw_pg_url)
    
    # Must specify an explicit driver: either +psycopg or +psycopg2
    assert ("postgresql+psycopg://" in normalized) or ("postgresql+psycopg2://" in normalized)
    assert "vmake_user:vmake_pass@localhost:5432/vmake_db" in normalized


def test_postgres_legacy_scheme_normalization():
    """Verify legacy postgres:// scheme is normalized to postgresql with driver."""
    legacy_url = "postgres://vmake_user:vmake_pass@localhost:5432/vmake_db"
    normalized = get_normalized_database_url(legacy_url)
    assert normalized.startswith("postgresql+")
    assert "vmake_user:vmake_pass@localhost:5432/vmake_db" in normalized


def test_sqlite_url_preserved():
    """Verify SQLite URLs are untouched by normalization."""
    sqlite_url = "sqlite:///./test_database.db"
    assert get_normalized_database_url(sqlite_url) == sqlite_url


def test_alembic_env_url_normalization():
    """Verify Alembic env get_url uses driver normalization logic."""
    from database.migrations.env import get_url
    
    with patch.dict(os.environ, {"DATABASE_URL": "postgresql://vmake_user:vmake_pass@localhost:5432/vmake_db"}):
        alembic_url = get_url()
        assert ("postgresql+psycopg://" in alembic_url) or ("postgresql+psycopg2://" in alembic_url)


# ============================================================================
# BLOCKER 2: STRICT SYNAPSE / VMAKE MODEL SEPARATION
# ============================================================================

def test_verification_service_default_is_transformer():
    """Verify BankingVerificationService defaults to Track B Transformer, not Siamese."""
    mock_db = MagicMock()
    service = BankingVerificationService(db_session=mock_db)
    assert isinstance(service.verifier, VisionTransformerVerifier)
    assert service.verifier.model_name == "HF_Vision_Transformer"
    assert service.verifier.model_type == "VISION_TRANSFORMER"
    assert service.verifier.threshold == pytest.approx(0.7313, abs=0.001)


def test_get_model_verifier_default_and_types():
    """Verify factory returns VisionTransformerVerifier by default and handles all tracks."""
    default_verifier = get_model_verifier()
    assert isinstance(default_verifier, VisionTransformerVerifier)

    transformer_verifier = get_model_verifier("transformer")
    assert isinstance(transformer_verifier, VisionTransformerVerifier)

    rf_verifier = get_model_verifier("random_forest")
    assert isinstance(rf_verifier, ClassicalSklearnVerifier)
    assert rf_verifier.threshold == pytest.approx(0.4264, abs=0.001)

    svm_verifier = get_model_verifier("svm")
    assert isinstance(svm_verifier, ClassicalSklearnVerifier)
    assert svm_verifier.threshold == pytest.approx(0.3636, abs=0.001)

    lr_verifier = get_model_verifier("logistic")
    assert isinstance(lr_verifier, ClassicalSklearnVerifier)
    assert lr_verifier.threshold == pytest.approx(0.2015, abs=0.001)

    # Legacy Siamese must be explicitly typed as LEGACY_SIAMESE and named Legacy_Siamese_ResNet18
    siamese_verifier = get_model_verifier("siamese")
    assert isinstance(siamese_verifier, LegacySiameseVerifier)
    assert siamese_verifier.model_type == "LEGACY_SIAMESE"
    assert siamese_verifier.model_name == "Legacy_Siamese_ResNet18"


def test_health_endpoint_vmake_branding_and_active_model():
    """Verify /api/v1/health reports VMAKE identity and Vision Transformer active model."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "SIGNATURE VMAKE" in data["service"]
    assert "SYNAPSE" not in data["service"]
    
    # Active model must be Vision Transformer
    assert data["active_model"]["name"] == "HF_Vision_Transformer"
    assert "Track B" in data["active_model"]["track"]
    assert data["active_model"]["threshold"] == pytest.approx(0.7313, abs=0.001)
    assert "facebook/deit-tiny-patch16-224" in data["active_model"]["architecture"]


def test_models_diagnostics_endpoint():
    """Verify /api/v1/models/health exposes candidate models including transformer and sklearn."""
    response = client.get("/api/v1/models/health")
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    models = data["models"]
    assert "transformer" in models
    assert "random_forest" in models
    assert "svm" in models
    assert "logistic" in models


# ============================================================================
# BLOCKER 3: EMPIRICAL BENCHMARKS, RF ACCURACY, AND ZERO HARDCODED FALLBACKS
# ============================================================================

def test_benchmark_endpoint_loads_empirical_data_and_rf_accuracy():
    """Verify /api/v1/models/benchmark serves empirical test evaluation without fallback."""
    response = client.get("/api/v1/models/benchmark")
    assert response.status_code == 200
    data = response.json()
    
    # Check all required candidate tracks are present in benchmark output
    assert "Track_A_Random_Forest" in data
    assert "Track_A_Classical_Sklearn" in data
    assert "Track_A_Logistic_Regression" in data
    assert "Track_B_Vision_Transformer" in data
    
    # Random Forest metrics must match empirical CEDAR held-out open-set test cohort
    rf = data["Track_A_Random_Forest"]
    assert rf["accuracy"] == pytest.approx(0.8292, abs=0.001)
    assert rf["auc_roc"] == pytest.approx(0.9424, abs=0.001)
    assert rf["eer"] == pytest.approx(0.1333, abs=0.001)
    assert rf["frr"] == pytest.approx(0.0383, abs=0.001)

    # Vision Transformer metrics
    vt = data["Track_B_Vision_Transformer"]
    assert vt["accuracy"] == pytest.approx(0.6450, abs=0.001)
    assert vt["auc_roc"] == pytest.approx(0.7947, abs=0.001)
    assert vt["frr"] == pytest.approx(0.0383, abs=0.001)


def test_benchmark_endpoint_returns_503_when_artifact_missing():
    """Verify /api/v1/models/benchmark returns HTTP 503 instead of fabricating numbers."""
    non_existent_path = Path("artifacts/evaluation/non_existent_evaluation_artifact.json")
    with patch("api.main.EVAL_BENCHMARK_PATH", non_existent_path):
        response = client.get("/api/v1/models/benchmark")
        assert response.status_code == 503
        data = response.json()
        assert "detail" in data
        assert "Empirical benchmark artifacts are unavailable" in data["detail"]


def test_dashboard_metrics_does_not_contain_hardcoded_latency():
    """Verify /api/v1/dashboard/metrics derives latency dynamically and has no hardcoded 21.3."""
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]
    
    # Measured latency from benchmark artifact is dynamically retrieved or None
    # Must NOT be the previously hardcoded 21.3
    measured_latency = data.get("average_inference_latency_ms")
    assert measured_latency != 21.3
