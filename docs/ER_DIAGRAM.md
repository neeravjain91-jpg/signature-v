# Entity-Relationship (ER) Diagram

## 1. System Overview

This ER diagram models the complete operational, biometric, and risk assessment lifecycle for the **Intelligent Signature Verification & Fraud Risk Assessment System for Banking Transactions**.

It guarantees strict relational integrity between system security users, retail/commercial bank customers, multi-currency accounts, transactions, biometric signature specimens, versioned ML embeddings, automated risk assessments, manual compliance reviews, and immutable audit logs.

---

## 2. Mermaid ER Diagram

```mermaid
erDiagram
    USER ||--o| CUSTOMER : "has (0..1 self-service login)"
    CUSTOMER ||--o{ ACCOUNT : "owns (1..N)"
    CUSTOMER ||--o{ SIGNATURE : "registers (1..N)"
    SIGNATURE ||--o{ SIGNATURE_EMBEDDING : "generates (1..N)"
    MODEL_VERSION ||--o{ SIGNATURE_EMBEDDING : "encodes (1..N)"
    ACCOUNT ||--o{ TRANSACTION : "contains (1..N)"
    TRANSACTION ||--o{ VERIFICATION_ATTEMPT : "triggers (1..N)"
    CUSTOMER ||--o{ VERIFICATION_ATTEMPT : "submits (1..N)"
    SIGNATURE ||--o{ VERIFICATION_ATTEMPT : "submitted_in (1..N)"
    SIGNATURE ||--o{ VERIFICATION_ATTEMPT : "compared_against (0..N enrolled)"
    MODEL_VERSION ||--o{ VERIFICATION_ATTEMPT : "evaluates (1..N)"
    VERIFICATION_ATTEMPT ||--|| RISK_ASSESSMENT : "evaluates_to (1..1)"
    VERIFICATION_ATTEMPT ||--o{ MANUAL_REVIEW : "may_require (0..N)"
    USER ||--o{ MANUAL_REVIEW : "adjudicates (1..N)"
    USER ||--o{ AUDIT_LOG : "triggers (0..N)"

    USER {
        uuid user_id PK "Primary Key (gen_random_uuid)"
        string username UK "Unique login handle"
        string email UK "Unique email address"
        string password_hash "Salted hash (argon2/bcrypt)"
        string role "CUSTOMER | OFFICER | ADMIN"
        string status "ACTIVE | INACTIVE | SUSPENDED"
        timestamptz created_at "Account creation timestamp"
        timestamptz updated_at "Record modification timestamp"
        timestamptz last_login_at "Last session authentication"
    }

    CUSTOMER {
        uuid customer_id PK "Primary Key"
        uuid user_id FK "Nullable FK -> USER.user_id"
        string customer_reference UK "Unique Bank CID (e.g. CUST-2026-001)"
        string full_name "Customer legal name"
        string phone_reference "Hashed/tokenized phone for 2FA"
        string status "ACTIVE | UNDER_REVIEW | BLOCKED"
        timestamptz created_at "Onboarding timestamp"
        timestamptz updated_at "Profile update timestamp"
    }

    ACCOUNT {
        uuid account_id PK "Primary Key"
        uuid customer_id FK "FK -> CUSTOMER.customer_id"
        string account_reference UK "Unique IBAN / Account Number"
        string account_type "SAVINGS | CHECKING | CORPORATE"
        string status "ACTIVE | FROZEN | DORMANT"
        timestamptz created_at "Account opening timestamp"
    }

    SIGNATURE {
        uuid signature_id PK "Primary Key"
        uuid customer_id FK "FK -> CUSTOMER.customer_id"
        string signature_type "ENROLLED | VERIFICATION_SUBMISSION"
        string storage_reference "Vault / Object Store URI"
        char64 file_hash "SHA-256 binary hash"
        numeric image_quality_score "Quality metric (0.0000 - 1.0000)"
        string status "ACTIVE | SUPERSEDED | REVOKED | REJECTED"
        timestamptz created_at "Capture timestamp"
    }

    MODEL_VERSION {
        uuid model_version_id PK "Primary Key"
        string model_name "Model family identifier"
        string version "Semantic version (v1.0.0)"
        string architecture "Siamese-ResNet18-Contrastive"
        string training_dataset "CEDAR Open-Set Split"
        timestamptz training_date "Training date"
        numeric threshold "Operational decision cutoff"
        jsonb performance_summary "EER, FAR, FRR, AUC metrics"
        string artifact_reference "Model weights storage URI"
        string status "STAGING | PRODUCTION | DEPRECATED"
        timestamptz created_at "Deployment timestamp"
    }

    SIGNATURE_EMBEDDING {
        uuid embedding_id PK "Primary Key"
        uuid signature_id FK "FK -> SIGNATURE.signature_id"
        uuid model_version_id FK "FK -> MODEL_VERSION.model_version_id"
        string embedding_reference "Vector store URI or NPY path"
        char64 embedding_hash "SHA-256 of latent vector representation"
        int vector_dim "Embedding dimension (512)"
        timestamptz created_at "Inference timestamp"
    }

    TRANSACTION {
        uuid transaction_id PK "Primary Key"
        uuid account_id FK "FK -> ACCOUNT.account_id"
        string transaction_reference UK "Unique transaction ID"
        string transaction_type "CHEQUE | WITHDRAWAL | WIRE_TRANSFER"
        numeric amount "Transaction monetary amount"
        char3 currency "ISO 4217 Currency Code (USD)"
        string status "PENDING | VERIFIED | MANUAL_REVIEW | APPROVED | REJECTED"
        timestamptz created_at "Transaction initiation timestamp"
    }

    VERIFICATION_ATTEMPT {
        uuid verification_id PK "Primary Key"
        uuid transaction_id FK "FK -> TRANSACTION.transaction_id"
        uuid customer_id FK "FK -> CUSTOMER.customer_id"
        uuid submitted_signature_id FK "FK -> SIGNATURE.signature_id"
        uuid enrolled_signature_id FK "Nullable FK -> SIGNATURE.signature_id"
        numeric similarity_score "Siamese cosine/contrastive similarity (0..1)"
        numeric threshold_used "Model threshold at inference time"
        string decision "VERIFIED | MANUAL_REVIEW | REJECTED"
        uuid model_version_id FK "FK -> MODEL_VERSION.model_version_id"
        timestamptz created_at "Verification execution timestamp"
    }

    RISK_ASSESSMENT {
        uuid risk_id PK "Primary Key"
        uuid verification_id FK "Unique 1:1 FK -> VERIFICATION_ATTEMPT"
        numeric similarity_component "Similarity risk penalty (0..1)"
        numeric image_quality_component "Image degradation penalty (0..1)"
        numeric transaction_risk_component "Amount & velocity factor (0..1)"
        numeric behavioral_component "Customer transaction pattern factor (0..1)"
        numeric overall_risk_score "Weighted composite risk (0..1)"
        string risk_level "LOW | MEDIUM | HIGH"
        jsonb risk_factors "Specific triggers / rule violations"
        timestamptz created_at "Assessment timestamp"
    }

    MANUAL_REVIEW {
        uuid review_id PK "Primary Key"
        uuid verification_id FK "FK -> VERIFICATION_ATTEMPT.verification_id"
        uuid reviewer_user_id FK "FK -> USER.user_id (OFFICER)"
        string decision "APPROVED | REJECTED"
        text review_comment "Officer forensic notes and reasoning"
        timestamptz reviewed_at "Adjudication timestamp"
    }

    AUDIT_LOG {
        uuid audit_id PK "Primary Key"
        uuid user_id FK "Nullable FK -> USER.user_id (Actor)"
        string action "Event action name"
        string entity_type "Target entity name"
        uuid entity_id "Target entity UUID"
        string result "SUCCESS | FAILURE | WARNING | DENIED"
        timestamptz timestamp "Event timestamp"
        string request_reference "Correlation ID / HTTP Request ID"
        jsonb details "Redacted event context metadata"
    }
```

---

## 3. Relationship Cardinality Breakdown

1. **USER (1) to CUSTOMER (0..1):** A user account may represent an internal bank officer/admin (no customer profile) or a retail customer. A customer may be an offline entity without online credentials.
2. **CUSTOMER (1) to ACCOUNT (1..N):** A bank customer may open multiple accounts (Checking, Savings, Corporate).
3. **CUSTOMER (1) to SIGNATURE (1..N):** A customer maintains multiple signatures over time (baseline enrolled specimens and historical submission specimens).
4. **SIGNATURE (1) to SIGNATURE_EMBEDDING (1..N):** When new model versions are deployed, an enrolled signature can be re-embedded under the new model without re-requesting the physical specimen.
5. **MODEL_VERSION (1) to SIGNATURE_EMBEDDING (1..N):** Each embedding is irrevocably bound to the specific model version that created it.
6. **ACCOUNT (1) to TRANSACTION (1..N):** An account is the ledger container for transactions.
7. **TRANSACTION (1) to VERIFICATION_ATTEMPT (1..N):** High-risk or re-attempted transactions may trigger verification checks.
8. **CUSTOMER (1) to VERIFICATION_ATTEMPT (1..N):** Directly identifies the claiming customer identity being verified.
9. **VERIFICATION_ATTEMPT (1) to RISK_ASSESSMENT (1..1):** Every verification attempt receives exactly one comprehensive risk assessment.
10. **VERIFICATION_ATTEMPT (1) to MANUAL_REVIEW (0..N):** Attempts that evaluate to `MANUAL_REVIEW` are routed to compliance officers for adjudication.
11. **USER (1) to MANUAL_REVIEW (1..N):** Only users with role `OFFICER` or `ADMIN` can adjudicate reviews.
12. **MODEL_VERSION (1) to VERIFICATION_ATTEMPT (1..N):** Every verification attempt records the active model version and its decision threshold at run-time.
13. **USER (1) to AUDIT_LOG (0..N):** Tracks both user actions and automated system actions (`user_id = NULL`).
