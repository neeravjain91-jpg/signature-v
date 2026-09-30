# SIGNATURE VMAKE — API Specification & Contract Reference

> **System:** SIGNATURE VMAKE  
> **Repository:** `signature-vmake`  
> **Version:** 2.0.0  
> **Base URL:** `http://localhost:8000/api/v1`  
> **Interactive Documentation:** `/docs` (Swagger UI), `/redoc` (ReDoc)  

---

## 1. Authentication & Security

All private endpoints require an OAuth2 Bearer token in the `Authorization` header:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

For development and testing, endpoints default gracefully if no token is provided, but in production, RBAC permissions are enforced based on assigned roles (`teller`, `fraud_analyst`, `compliance_auditor`, `system_admin`).

---

## 2. Core Endpoints Reference

### 2.1 System Health
`GET /api/v1/health`

Returns service health, database status, and active ML model tracks.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

**Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "service": "SIGNATURE VMAKE Verification Platform",
  "version": "2.0.0",
  "timestamp": "2026-09-29T17:00:00.000000",
  "database": "CONNECTED",
  "models_available": [
    "classical_baseline",
    "vision_transformer",
    "siamese_champion"
  ]
}
```

---

### 2.2 Model Benchmark Comparison
`GET /api/v1/models/benchmark`

Retrieves the empirical three-track validation benchmark results comparing Track A (Classical SVM), Track B (Vision Transformer), and Track C (Siamese ResNet Champion).

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/models/benchmark"
```

**Response (200 OK):**
```json
{
  "benchmark_suite": "SIGNATURE VMAKE Three-Track Open-Set Evaluation",
  "dataset": "CEDAR Benchmark (Disjoint Validation Cohort Writers 36-45)",
  "num_pairs": 400,
  "champion_track": "Track C (Siamese ResNet Champion)",
  "results": {
    "Track A (Classical Sklearn SVM)": {
      "auc_roc": 0.8423,
      "eer": 0.23,
      "accuracy": 0.7675,
      "far": 0.2304,
      "frr": 0.2347,
      "f1_score": 0.7634,
      "optimal_threshold": 0.499,
      "latency_ms": 7.3,
      "model_size_mb": 5.4
    },
    "Track B (HF Vision Transformer)": {
      "auc_roc": 0.8118,
      "eer": 0.245,
      "accuracy": 0.755,
      "far": 0.2451,
      "frr": 0.2449,
      "f1_score": 0.7513,
      "optimal_threshold": 0.4287,
      "latency_ms": 38.4,
      "model_size_mb": 21.7
    },
    "Track C (Siamese ResNet Champion)": {
      "auc_roc": 0.9008,
      "eer": 0.1874,
      "accuracy": 0.815,
      "far": 0.1912,
      "frr": 0.1786,
      "f1_score": 0.8131,
      "optimal_threshold": 0.7691,
      "latency_ms": 42.1,
      "model_size_mb": 43.2
    }
  }
}
```

---

### 2.3 Verify Signature
`POST /api/v1/verifications/verify`

Verifies a questioned signature image against the enrolled specimen gallery for an account or customer.

**Request (Multipart Form-Data):**
- `file`: Binary image file (JPEG, PNG, BMP, TIFF $\le$ 5MB).
- `account_number`: String (e.g. `ACC-100482-OMR`).
- `transaction_amount`: Optional Float (e.g. `12500.00`).
- `channel_type`: Optional String (`BRANCH_COUNTER`, `CTS_CLEARING`, `ATM_DEPOSIT`).
- `model_track`: Optional String (`siamese_champion` [default], `classical_baseline`, `vision_transformer`).
- `aggregation_strategy`: Optional String (`max_similarity` [default], `mean_similarity`, `top_k_mean`, `centroid_distance`).

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/verifications/verify" \
  -F "file=@cheque_sample_46.png;type=image/png" \
  -F "account_number=ACC-100482-OMR" \
  -F "transaction_amount=12500.00" \
  -F "channel_type=BRANCH_COUNTER" \
  -F "model_track=siamese_champion" \
  -F "aggregation_strategy=max_similarity"
```

**Response (200 OK):**
```json
{
  "verification_id": "v-9e2b1f84-18ca-429a",
  "decision": "VERIFIED",
  "similarity_score": 0.8856,
  "threshold_used": 0.7691,
  "distance": 0.2288,
  "model_version": "Siamese_ResNet_Champion_v2.0",
  "model_track": "siamese_champion",
  "risk_assessment": {
    "composite_risk_score": 0.1245,
    "risk_level": "LOW",
    "factor_breakdown": {
      "biometric_deficit": 0.1144,
      "image_quality_deficit": 0.052,
      "monetary_risk": 0.18,
      "behavioral_risk": 0.1
    },
    "flags": []
  },
  "execution_time_ms": 42.1,
  "timestamp": "2026-09-29T17:00:00.000000"
}
```

---

### 2.4 Enroll Signature Specimen
`POST /api/v1/signatures/enroll`

Enrolls a new genuine reference signature specimen into the customer's active gallery.

**Request (Multipart Form-Data):**
- `customer_id`: String (e.g. `CUST-00100482`).
- `file`: Binary signature image.
- `specimen_source`: String (`MANDATE_CARD`, `BRANCH_PAD`, `ONBOARDING_SCAN`).

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/signatures/enroll" \
  -F "file=@specimen_ref1.png;type=image/png" \
  -F "customer_id=CUST-00100482" \
  -F "specimen_source=MANDATE_CARD"
```

**Response (201 Created):**
```json
{
  "specimen_id": "spec-4819a3b0-2b9a-41e8",
  "customer_id": "CUST-00100482",
  "sha256_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "status": "ACTIVE",
  "created_at": "2026-09-29T17:00:00.000000"
}
```

---

### 2.5 Inquire Verification Details
`GET /api/v1/verifications/{verification_id}`

Retrieves the persisted verification attempt record, biometric score, threshold, and risk assessment breakdown.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/verifications/v-9e2b1f84-18ca-429a"
```

**Response (200 OK):**
```json
{
  "verification_id": "v-9e2b1f84-18ca-429a",
  "account_number": "ACC-100482-OMR",
  "decision": "VERIFIED",
  "similarity_score": 0.8856,
  "distance": 0.2288,
  "threshold_used": 0.7691,
  "risk_level": "LOW",
  "composite_risk_score": 0.1245,
  "model_version": "Siamese_ResNet_Champion_v2.0",
  "created_at": "2026-09-29T17:00:00.000000"
}
```

---

### 2.6 Regulatory Audit Trail Inquiry
`GET /api/v1/audit/trail/{identifier}`

Returns the immutable cryptographic audit trail associated with a given verification ID, account number, or customer ID.

**Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/audit/trail/v-9e2b1f84-18ca-429a"
```

**Response (200 OK):**
```json
[
  {
    "audit_id": "aud-00192834-ff81",
    "event_type": "SIGNATURE_VERIFICATION_ATTEMPT",
    "entity_type": "VERIFICATION",
    "entity_id": "v-9e2b1f84-18ca-429a",
    "actor_user": "teller_om_01",
    "ip_address": "10.14.88.22",
    "similarity_score": 0.8856,
    "composite_risk_score": 0.1245,
    "decision": "VERIFIED",
    "hash_digest": "7d2b8e3a...",
    "timestamp": "2026-09-29T17:00:00.000000"
  }
]
```

---

### 2.7 Customer Profile Management
- `GET /api/v1/customers`: Lists enrolled banking customer profiles.
- `POST /api/v1/customers`: Registers a new customer profile with CIF, full name, KYC status, and risk classification.

### 2.8 Transaction Management
- `GET /api/v1/transactions`: Lists recent banking transactions.
- `POST /api/v1/transactions`: Initiates a financial transaction linked to an account.

---

## 3. Standard HTTP Status & Error Codes

| Status Code | Reason | Description |
| :---: | :--- | :--- |
| `200 OK` | Success | Request succeeded and response payload returned. |
| `201 Created` | Resource Created | Specimen or customer enrolled successfully. |
| `400 Bad Request` | Validation Failure | Invalid file format, missing field, or file exceeding 5MB ceiling. |
| `401 Unauthorized` | Invalid Authentication | Missing or expired JWT Bearer token. |
| `403 Forbidden` | Insufficient Permissions | User does not possess the requisite RBAC role. |
| `404 Not Found` | Entity Missing | Customer, account, or verification ID does not exist. |
| `422 Unprocessable` | Schema Error | Pydantic schema validation failed on input types. |
| `500 Internal Error` | Server Exception | Internal failure safely caught; generic error returned without leaking stack traces. |
