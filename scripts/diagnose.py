#!/usr/bin/env python3
"""
SIGNATURE VMAKE — Comprehensive Startup & Runtime Diagnostic Utility.

Inspects Python environment, dependency availability, database connectivity,
dataset integrity, model checkpoints, inference capabilities, and API entrypoints.
"""

import sys
import os
from pathlib import Path
import importlib
import time

# Ensure project root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def check_status(name: str, fn) -> bool:
    try:
        msg = fn()
        details = f" ({msg})" if msg else ""
        print(f"[PASS] {name}{details}")
        return True
    except Exception as e:
        print(f"[FAIL] {name}: {e}")
        return False


def main():
    print("=" * 65)
    print("       SIGNATURE VMAKE — SYSTEM DIAGNOSTIC RUNNER")
    print("=" * 65)

    all_passed = True

    # 1. Python Version
    def check_py():
        v = sys.version_info
        if v.major < 3 or (v.major == 3 and v.minor < 10):
            raise RuntimeError(f"Python 3.10+ required, found {v.major}.{v.minor}.{v.micro}")
        return f"{v.major}.{v.minor}.{v.micro}"
    all_passed &= check_status("Python Runtime", check_py)

    # 2. Dependencies
    pkgs = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("SQLAlchemy", "sqlalchemy"),
        ("scikit-learn", "sklearn"),
        ("PyTorch", "torch"),
        ("Transformers", "transformers"),
        ("OpenCV", "cv2"),
        ("Pillow", "PIL"),
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("Alembic", "alembic"),
    ]
    for label, mod in pkgs:
        def check_mod(m=mod):
            m_obj = importlib.import_module(m)
            return getattr(m_obj, "__version__", "installed")
        all_passed &= check_status(f"Dependency: {label}", check_mod)

    # 3. Database
    def check_db():
        from database.session import SessionLocal, DB_URL
        from database.models import Customer, ModelVersion
        db = SessionLocal()
        try:
            cust_count = db.query(Customer).count()
            models_count = db.query(ModelVersion).count()
            db_type = "PostgreSQL" if "postgres" in DB_URL else "SQLite (Local Dev/Test Fallback)"
            return f"{db_type} at {DB_URL.split('?')[0]} | Customers: {cust_count}, Models: {models_count}"
        finally:
            db.close()
    all_passed &= check_status("Database Connectivity", check_db)

    # 4. Dataset
    def check_data():
        p_org = Path("data/raw/signatures/full_org")
        p_forg = Path("data/raw/signatures/full_forg")
        if not p_org.exists() or not p_forg.exists():
            raise FileNotFoundError("CEDAR raw dataset directories missing")
        org_c = len(list(p_org.glob("*.png")))
        forg_c = len(list(p_forg.glob("*.png")))
        return f"CEDAR Benchmark ({org_c} genuine, {forg_c} forged)"
    all_passed &= check_status("Dataset Availability", check_data)

    # 5. Checkpoints & Model Inference (All 4 Synopsis Candidates)
    models = [
        ("Candidate 1: Classical SVM Baseline", "svm", "artifacts/models/classical_svm_model.joblib"),
        ("Candidate 2: Classical Random Forest", "random_forest", "artifacts/models/classical_random_forest_model.joblib"),
        ("Candidate 3: Classical Logistic Regression", "logistic", "artifacts/models/classical_logistic_model.joblib"),
        ("Candidate 4: HF Vision Transformer (Production Default)", "transformer", "artifacts/models/transformer_signature_model.pt"),
    ]
    for label, track_id, ckpt_path in models:
        def check_model(t=track_id, ckpt=ckpt_path):
            p = Path(ckpt)
            if not p.exists():
                raise FileNotFoundError(f"Checkpoint not found at {ckpt}")
            from ml.inference.verify_signature import get_model_verifier
            v = get_model_verifier(t)
            # Run real sample inference
            ref = "data/raw/signatures/full_org/original_46_1.png"
            sub = "data/raw/signatures/full_org/original_46_2.png"
            out = v.verify(ref, sub)
            return f"Loaded ({p.stat().st_size / (1024*1024):.2f} MB) | Inf Sim: {out.similarity_score:.4f} | Dec: {out.decision}"
        all_passed &= check_status(f"Model: {label}", check_model)

    # 6. Frontend Files
    def check_web():
        p = Path("web/index.html")
        if not p.exists():
            raise FileNotFoundError("web/index.html not found")
        return f"{p.stat().st_size / 1024:.1f} KB"
    all_passed &= check_status("Frontend UI Assets", check_web)

    # 7. API Entrypoint
    def check_api():
        from api.main import app
        routes = [r.path for r in app.routes]
        required = ["/api/v1/health", "/api/v1/models/health", "/api/v1/customers", "/api/v1/verifications/verify"]
        missing = [r for r in required if r not in routes]
        if missing:
            raise ValueError(f"Missing routes: {missing}")
        return f"{len(routes)} routes registered"
    all_passed &= check_status("FastAPI Application Entrypoint", check_api)

    print("-" * 65)
    if all_passed:
        print("[SUCCESS] All system diagnostics passed! SIGNATURE VMAKE is fully operational.")
        sys.exit(0)
    else:
        print("[WARNING] One or more diagnostic checks failed. Review errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
