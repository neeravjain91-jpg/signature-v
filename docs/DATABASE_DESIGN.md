# Database Architecture & Normalization Report

## 1. Overview and Design Philosophy

The database architecture is designed for an enterprise-grade banking transaction and biometric verification environment. It adheres to **Third Normal Form (3NF)** with explicit, justified denormalizations where financial auditability, biometric determinism, and high-throughput query performance demand immutable historical snapshots.

Key design imperatives:
* **Cryptographic Traceability:** Foreign keys and SHA-256 hashes connect every transaction and verification event back to exact model versions and raw image specimens.
* **UUID Primary Keys:** All tables utilize 128-bit UUIDs (`gen_random_uuid()`) instead of auto-incrementing integers. This eliminates sequential identifier enumeration attacks, facilitates distributed horizontal sharding, and prevents cross-tenant data harvesting.
* **Strict Constraint Enforcement:** All state transitions and numerical thresholds are constrained via SQL `CHECK` expressions and domain enums.
* **Separation of Concerns:** Heavy binary assets (signature images and latent embedding vectors) are referenced via external object storage handles (`storage_reference`, `embedding_reference`) rather than being stored in row-level BLOBs, preventing PostgreSQL buffer pool cache pollution.

---

## 2. Normalization Analysis

### First Normal Form (1NF)
* **Atomic Columns:** All attributes contain atomic, scalar values. Complex structures (such as `risk_factors` in `risk_assessments` and `performance_summary` in `model_versions`) are stored using PostgreSQL `JSONB` with structured internal schemas rather than unindexed delimited strings.
* **Primary Keys:** Every entity has a distinct, non-nullable primary key (`UUID`).
* **Repeating Groups:** No repeating groups or array columns represent entities; relationships are modeled via independent relational association tables.

### Second Normal Form (2NF)
* **Full Functional Dependency:** All candidate keys consist of single attributes (UUIDs) or composite natural keys (`(model_name, version)`, `(signature_id, model_version_id)`).
* All non-key attributes are fully functionally dependent on the entire primary key, eliminating partial key dependencies.

### Third Normal Form (3NF)
* **No Transitive Dependencies:** Non-key attributes depend solely on the primary key, not on other non-key attributes.
* Example: `account_type` is an attribute of `accounts`, not repeated inside `transactions`.
* Example: `customer_reference` resides in `customers`, while `transactions` references `account_id` and derives customer ownership through the relational join `accounts.customer_id = customers.customer_id`.

---

## 3. Deliberate Denormalization & Audit Justifications

In financial compliance and regulatory audit trails (e.g. Basel III, SOC2, PCI-DSS), **strict 3NF can create severe legal vulnerabilities if historical states can be modified by downstream updates**. Two critical denormalizations are deliberately incorporated:

### 1. `customer_id` Denormalization in `verification_attempts`
* **Form:** `verification_attempts` contains both `transaction_id` (which already links to `account_id` $\rightarrow$ `customer_id`) and an explicit `customer_id` column.
* **Justification:** High-throughput risk queries require instant indexing by customer identity (`WHERE customer_id = :id`) without multi-table relational joins across `transactions` and `accounts`. Furthermore, in scenarios where a verification attempt is initiated during customer onboarding before an account is opened, the customer identity is preserved directly.

### 2. Snapshotting `threshold_used` in `verification_attempts`
* **Form:** `verification_attempts` records `threshold_used` at the exact millisecond of decision, even though `model_versions` contains a `threshold` attribute.
* **Justification:** If an ML engineering team retunes or updates the operational threshold on `model_versions` in production, past historical verifications must **never** reflect retroactive threshold changes. The decision recorded on a \$50,000 cheque must remain immutable forever.

### 3. Snapshotting `similarity_component` and `image_quality_component` in `risk_assessments`
* **Form:** The risk components are stored as frozen numeric values in `risk_assessments` rather than calculated on-the-fly during reports.
* **Justification:** Regulatory non-repudiation requires banks to show auditors the exact component breakdown that yielded an automated block or manual referral.

---

## 4. Entity Specifications & Constraints

### 1. `users`
* `user_id` (UUID PK): Unique system identity.
* `username`, `email`: Unique indexed strings.
* `role`: CHECK constraint `('CUSTOMER', 'OFFICER', 'ADMIN')`.
* `status`: CHECK constraint `('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED')`.

### 2. `customers`
* `customer_id` (UUID PK): Unique customer identifier.
* `user_id` (UUID FK nullable): Relates to login user if enrolled in digital banking.
* `customer_reference`: Unique business identifier (e.g. `CUST-2026-00129`).
* `phone_reference`: Tokenized or hashed telephone number for out-of-band challenge verification.

### 3. `accounts`
* `account_id` (UUID PK).
* `customer_id` (UUID FK $\rightarrow$ `customers`).
* `account_type`: CHECK `('SAVINGS', 'CHECKING', 'CURRENT', 'CORPORATE', 'WEALTH_MANAGEMENT')`.
* `status`: CHECK `('ACTIVE', 'FROZEN', 'DORMANT', 'CLOSED')`.

### 4. `signatures`
* `signature_id` (UUID PK).
* `customer_id` (UUID FK $\rightarrow$ `customers`).
* `signature_type`: CHECK `('ENROLLED', 'VERIFICATION_SUBMISSION')`.
* `file_hash`: Fixed `CHAR(64)` storing SHA-256 for bitwise tamper detection.
* `image_quality_score`: Numeric with CHECK `(image_quality_score >= 0.0000 AND image_quality_score <= 1.0000)`.

### 5. `model_versions`
* `model_version_id` (UUID PK).
* `model_name`, `version`: Unique composite constraint `(model_name, version)`.
* `threshold`: CHECK `(threshold BETWEEN 0.0000 AND 1.0000)`.
* `performance_summary`: JSONB containing EER, FAR, FRR, AUC.
* `status`: CHECK `('STAGING', 'PRODUCTION', 'DEPRECATED', 'ARCHIVED')`.

### 6. `signature_embeddings`
* `embedding_id` (UUID PK).
* `signature_id` (UUID FK $\rightarrow$ `signatures`).
* `model_version_id` (UUID FK $\rightarrow$ `model_versions`).
* Unique constraint: `(signature_id, model_version_id)` ensuring exactly one embedding per model version per signature.
* `embedding_hash`: `CHAR(64)` SHA-256 digest of the latent vector.
* `vector_dim`: Default 512, CHECK `(vector_dim > 0)`.

### 7. `transactions`
* `transaction_id` (UUID PK).
* `account_id` (UUID FK $\rightarrow$ `accounts`).
* `transaction_reference`: Unique transaction voucher ID.
* `amount`: Numeric(15, 2) with CHECK `(amount >= 0.00)`.
* `status`: CHECK `('PENDING', 'VERIFIED', 'MANUAL_REVIEW', 'APPROVED', 'REJECTED', 'SETTLED', 'CANCELLED')`.

### 8. `verification_attempts`
* `verification_id` (UUID PK).
* `transaction_id` (UUID FK $\rightarrow$ `transactions`).
* `submitted_signature_id` (UUID FK $\rightarrow$ `signatures`).
* `enrolled_signature_id` (UUID FK nullable $\rightarrow$ `signatures`).
* `similarity_score`: Numeric(5, 4) with CHECK `(0.0000 to 1.0000)`.
* `decision`: CHECK `('VERIFIED', 'MANUAL_REVIEW', 'REJECTED')`.

### 9. `risk_assessments`
* `risk_id` (UUID PK).
* `verification_id` (UUID FK $\rightarrow$ `verification_attempts` UNIQUE, enforcing 1-to-1).
* Components: `similarity_component`, `image_quality_component`, `transaction_risk_component`, `behavioral_component`, `overall_risk_score` (all 0.0000 to 1.0000).
* `risk_level`: CHECK `('LOW', 'MEDIUM', 'HIGH')`.

### 10. `manual_reviews`
* `review_id` (UUID PK).
* `verification_id` (UUID FK $\rightarrow$ `verification_attempts`).
* `reviewer_user_id` (UUID FK $\rightarrow$ `users`).
* `decision`: CHECK `('APPROVED', 'REJECTED')`.
* `review_comment`: Mandatory non-empty text justification.

### 11. `audit_logs`
* `audit_id` (UUID PK).
* `user_id` (UUID FK nullable $\rightarrow$ `users`).
* `action`, `entity_type`, `entity_id`: Immutable audit trail.
* `result`: CHECK `('SUCCESS', 'FAILURE', 'WARNING', 'DENIED')`.
* `request_reference`: Unique request correlation ID for tracing.

---

## 5. Indexing & Query Optimization Strategy

| Index Name | Table | Target Columns | Purpose |
| :--- | :--- | :--- | :--- |
| `idx_users_role_status` | `users` | `(role, status)` | Fast lookup of active compliance officers for routing reviews |
| `idx_customers_customer_ref` | `customers` | `customer_reference` | Unique index for customer reference lookups |
| `idx_accounts_account_ref` | `accounts` | `account_reference` | High-frequency account transaction routing |
| `idx_signatures_customer_id` | `signatures` | `customer_id` | Quick retrieval of customer's enrolled signature specimens |
| `idx_signatures_file_hash` | `signatures` | `file_hash` | Prevents replay attacks using duplicate raw image files |
| `idx_transactions_status_created` | `transactions` | `(status, created_at)` | Time-series query optimization for pending transaction queues |
| `idx_verifications_decision` | `verification_attempts` | `decision` | Filtering verifications requiring officer manual review |
| `idx_verifications_created_at` | `verification_attempts` | `created_at` | Audit reporting and temporal risk trend analysis |
| `idx_risk_level` | `risk_assessments` | `risk_level` | Alert monitoring and high-risk dashboard aggregation |
| `idx_audit_logs_timestamp` | `audit_logs` | `timestamp` | Compliance timeline reconstruction and SIEM ingestion |
| `idx_audit_logs_entity` | `audit_logs` | `(entity_type, entity_id)` | Complete lifecycle query for any specific entity |
