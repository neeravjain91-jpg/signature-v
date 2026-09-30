# SIGNATURE VMAKE — Forensic Runnability Audit & Root-Cause Analysis

> **Repository:** `signature-vmake`  
> **System Name:** SIGNATURE VMAKE (Offline Signature Verification & Multi-Factor Fraud Risk Assessment Platform)  
> **Audit Date:** September 2026  
> **Audit Status:** COMPLETED & RESOLVED  

---

## 1. Executive Summary

This forensic audit identifies the actual runtime failures, dependency conflicts, missing API contracts, and interface incompatibilities discovered during clean startup reproduction on a Windows development system. Rather than reviewing static code, the application and its test suites were executed live, tracing runtime exceptions down to their exact origin.

All identified root causes have been systematically diagnosed, repaired, and validated across 41 automated tests and end-to-end live inference demonstrations.

---

## 2. Startup Command & Observed Failures

### 2.1 Failure 1: Alembic Database Migration Failure
* **Command Executed:** `alembic upgrade head` (standard production migration command in Docker and CI).
* **Observed Traceback:**
  ```text
  File "C:\Users\ASUS\AppData\Local\Programs\Python\Python311\Lib\site-packages\sqlalchemy\engine\create.py", line 602, in create_engine
      dbapi = dbapi_meth(**dbapi_args)
  File "C:\Users\ASUS\AppData\Local\Programs\Python\Python311\Lib\site-packages\sqlalchemy\dialects\postgresql\psycopg2.py", line 691, in import_dbapi
      import psycopg2
  ModuleNotFoundError: No module named 'psycopg2'
  ```
* **Follow-up Migration Crash:**
  ```text
  sqlite3.OperationalError: (sqlite3.OperationalError) table users already exists
  [SQL: CREATE TABLE users (...)]
  ```
* **Root Cause:**
  1. `alembic.ini` hardcoded a PostgreSQL connection URI (`postgresql+psycopg2://...`), and `database/migrations/env.py` directly fell back to it without checking if `DATABASE_URL` was provided or if `psycopg2` was installed. On Windows workstations without an active PostgreSQL service, this caused an immediate crash.
  2. The SQLite database `banking_system_demo.db` was seeded via SQLAlchemy `create_all()`, but Alembic's `alembic_version` table was never stamped, causing subsequent migration commands to attempt re-creating existing tables.
* **Remediation:**
  1. Updated `database/migrations/env.py` to dynamically inspect `DATABASE_URL`, check for `psycopg2` availability, and safely default to the local SQLite database URI for zero-config Windows development.
  2. Stamped Alembic revision `001_initial_schema` into the database (`alembic stamp head`) so migrations and upgrades now execute with exit code 0.
  3. Added `connect_args={"check_same_thread": False}` in `database/session.py` to prevent SQLite multi-threading exceptions in concurrent ASGI contexts.

---

### 2.2 Failure 2: Polymorphic Model Interface Incompatibility
* **Command Executed:** Live model inference via `get_model_verifier(track).verify(ref, sub)`.
* **Observed Tracebacks:**
  ```text
  [sklearn] FAILED: 'ClassicalSklearnVerifier' object has no attribute 'verify'
  [transformer] FAILED: 'VisionTransformerVerifier' object has no attribute 'verify'
  [siamese] FAILED: 'dict' object has no attribute 'similarity_score'
  ```
* **Root Cause:**
  1. The base class `SignatureVerificationModel` defined `verify_pair(ref, query)` and `verify_gallery(gallery, query)`, but did not expose `.verify(...)` as an alias.
  2. `ClassicalSklearnVerifier` and `VisionTransformerVerifier` implemented `verify_pair(...)`, so calling `.verify(...)` raised an `AttributeError`.
  3. Conversely, `SignatureVerifier` (Track C) implemented a legacy method `verify(...)` returning a raw Python `dict`, whereas callers expecting a polymorphic `VerificationOutput` object failed with `'dict' object has no attribute 'similarity_score'`.
  4. Parameter naming mismatch: `SignatureVerifier.verify()` expected `reference_input, submitted_input`, whereas `SignatureVerificationModel.verify()` used `ref_image, query_image`. Calling with mismatched keyword arguments caused `TypeError: got an unexpected keyword argument 'ref_image'`.
* **Remediation:**
  1. Enhanced `VerificationOutput` in `ml/models/model_interface.py` to support dual access: both object attributes (`.similarity_score`, `.distance`, `.is_match`) and dictionary indexing (`out["similarity_score"]`, `"decision" in out`, `out.get(...)`).
  2. Implemented universal argument resolution in `SignatureVerificationModel.verify` and `SignatureVerifier.verify` accepting either `reference_input, submitted_input` or `ref_image, query_image`.
  3. Updated `SignatureVerifier.verify()` to return a complete, standardized `VerificationOutput` instance.

---

### 2.3 Failure 3: Missing Required FastAPI Endpoints (404 Not Found)
* **Endpoints Tested:**
  - `GET /api/v1/models/health` -> returned `404 Not Found`
  - `GET /api/v1/customers/{customer_id}` -> returned `404 Not Found`
* **Root Cause:**
  1. The required model health check endpoint specified in Phase 4 was not registered in `api/main.py`.
  2. The single-customer lookup route `GET /api/v1/customers/{customer_id}` required by Phase 14 was missing from `api/main.py`.
* **Remediation:**
  1. Implemented `GET /api/v1/models/health` in `api/main.py`, actively inspecting checkpoint presence and executing real runtime inference across all 3 tracks (`sklearn`, `transformer`, `neural`).
  2. Implemented `GET /api/v1/customers/{customer_id}` returning profile metadata, account references, and active signature specimen counts.

---

### 2.4 Failure 4: Deprecation Warning & Customer Reference Fallback
* **Observed Warnings:**
  `StarletteDeprecationWarning: 'HTTP_413_REQUEST_ENTITY_TOO_LARGE' is deprecated. Use 'HTTP_413_CONTENT_TOO_LARGE' instead.`
* **Customer Isolation Risk:**
  In `services/verification_service.py`, if a customer's enrolled reference specimen path was not found on disk, the system fell back to `data/raw/signatures/full_org/original_46_1.png`. This risked cross-customer contamination if an invalid path was queried.
* **Remediation:**
  1. Updated file size validation in `api/main.py` to use direct HTTP status code `413`.
  2. Implemented strict `_resolve_specimen_file()` resolution in `services/verification_service.py` that raises an explicit `FileNotFoundError` if a customer's registered file is missing, eliminating silent cross-writer fallbacks.
  3. Ensured genuine signature specimens are copied to physical vault locations (`data/vault/signatures/enrolled/{customer_id}/primary_specimen.png`) for all demo customers.

---

## 3. Subsystem Availability Matrix

| Subsystem | Requirement | Status | Verification Evidence |
| :--- | :--- | :---: | :--- |
| **Python Runtime** | 3.11+ | **AVAILABLE** | Verified on Python 3.11.9. |
| **FastAPI Microservice** | REST API | **AVAILABLE** | Starts cleanly on `http://127.0.0.1:8000`; 34 endpoints registered. |
| **Web Dashboard** | Single-Page App | **AVAILABLE** | Served at `/` from `web/index.html`; live API communications verified. |
| **Relational DB** | SQLite / Postgres | **AVAILABLE** | `database/banking_system_demo.db` connected; 81 customers, 4 models. |
| **Alembic Migrations** | Schema versioning | **AVAILABLE** | `alembic upgrade head` completes with 0 errors. |
| **CEDAR Dataset** | 2,640 signatures | **AVAILABLE** | 1,320 genuine, 1,320 forged; 0 malformed images verified via `validate_dataset.py`. |
| **Track A (Sklearn SVM)** | Classical ML | **AVAILABLE** | `classical_svm_model.joblib` (5.4 MB); latency: 14.2 ms; AUC: 0.8423. |
| **Track B (HF ViT)** | Vision Transformer | **AVAILABLE** | `transformer_signature_model.pt` (21.7 MB); latency: 39.0 ms; AUC: 0.8118. |
| **Track C (Siamese)** | ResNet Champion | **AVAILABLE** | `v4_champion_model.pt` (43.2 MB); latency: 43.3 ms; AUC: 0.9008. |
| **Test Suite** | Unit & Integration | **PASSING** | 41 of 41 tests passing in 16.35s. |

---

## 4. Verification Checklist & Current Health

1. `python scripts/diagnose.py`: **[PASS] All 15 checks passing.**
2. `python scripts/validate_dataset.py`: **[PASS] 2,640 images verified.**
3. `python -m pytest`: **[PASS] 41 / 41 tests passing.**
4. `python -m uvicorn api.main:app`: **[PASS] Running on http://127.0.0.1:8000.**
