-- =============================================================================
-- INTELLIGENT SIGNATURE VERIFICATION & FRAUD RISK ASSESSMENT SYSTEM
-- PostgreSQL Production-Grade Relational Schema
-- =============================================================================

-- Enable pgcrypto for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- 1. USERS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL CHECK (role IN ('CUSTOMER', 'OFFICER', 'ADMIN')),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'LOCKED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMPTZ NULL
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users (username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role_status ON users (role, status);

-- =============================================================================
-- 2. CUSTOMERS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS customers (
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(user_id) ON DELETE SET NULL,
    customer_reference VARCHAR(64) NOT NULL UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    phone_reference VARCHAR(64) NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'UNDER_REVIEW', 'BLOCKED', 'CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customers_customer_ref ON customers (customer_reference);
CREATE INDEX IF NOT EXISTS idx_customers_user_id ON customers (user_id);
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers (status);

-- =============================================================================
-- 3. ACCOUNTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    account_reference VARCHAR(64) NOT NULL UNIQUE,
    account_type VARCHAR(32) NOT NULL CHECK (account_type IN ('SAVINGS', 'CHECKING', 'CURRENT', 'CORPORATE', 'WEALTH_MANAGEMENT')),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'FROZEN', 'DORMANT', 'CLOSED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_accounts_customer_id ON accounts (customer_id);
CREATE INDEX IF NOT EXISTS idx_accounts_account_ref ON accounts (account_reference);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts (status);

-- =============================================================================
-- 4. SIGNATURES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS signatures (
    signature_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    signature_type VARCHAR(32) NOT NULL CHECK (signature_type IN ('ENROLLED', 'VERIFICATION_SUBMISSION')),
    storage_reference VARCHAR(512) NOT NULL,
    file_hash CHAR(64) NOT NULL,
    image_quality_score NUMERIC(5, 4) NOT NULL CHECK (image_quality_score >= 0.0000 AND image_quality_score <= 1.0000),
    status VARCHAR(32) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUPERSEDED', 'REVOKED', 'REJECTED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_signatures_customer_id ON signatures (customer_id);
CREATE INDEX IF NOT EXISTS idx_signatures_type_status ON signatures (signature_type, status);
CREATE INDEX IF NOT EXISTS idx_signatures_file_hash ON signatures (file_hash);

-- =============================================================================
-- 5. MODEL_VERSIONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS model_versions (
    model_version_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name VARCHAR(64) NOT NULL,
    version VARCHAR(32) NOT NULL,
    architecture VARCHAR(64) NOT NULL,
    training_dataset VARCHAR(128) NOT NULL,
    training_date DATE NOT NULL,
    threshold NUMERIC(5, 4) NOT NULL CHECK (threshold >= 0.0000 AND threshold <= 1.0000),
    performance_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    artifact_reference VARCHAR(512) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'PRODUCTION' CHECK (status IN ('STAGING', 'PRODUCTION', 'DEPRECATED', 'ARCHIVED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_model_name_version UNIQUE (model_name, version)
);

CREATE INDEX IF NOT EXISTS idx_model_versions_status ON model_versions (status);

-- =============================================================================
-- 6. SIGNATURE_EMBEDDINGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS signature_embeddings (
    embedding_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    signature_id UUID NOT NULL REFERENCES signatures(signature_id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL REFERENCES model_versions(model_version_id) ON DELETE RESTRICT,
    embedding_reference VARCHAR(512) NOT NULL,
    embedding_hash CHAR(64) NOT NULL,
    vector_dim INT NOT NULL DEFAULT 512 CHECK (vector_dim > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_signature_model_embedding UNIQUE (signature_id, model_version_id)
);

CREATE INDEX IF NOT EXISTS idx_sig_embed_signature_id ON signature_embeddings (signature_id);
CREATE INDEX IF NOT EXISTS idx_sig_embed_model_version ON signature_embeddings (model_version_id);

-- =============================================================================
-- 7. TRANSACTIONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
    transaction_reference VARCHAR(64) NOT NULL UNIQUE,
    transaction_type VARCHAR(32) NOT NULL CHECK (transaction_type IN ('CHEQUE', 'WITHDRAWAL', 'AUTHORIZATION', 'FORM_VERIFICATION', 'WIRE_TRANSFER')),
    amount NUMERIC(15, 2) NOT NULL CHECK (amount >= 0.00),
    currency CHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'VERIFIED', 'MANUAL_REVIEW', 'APPROVED', 'REJECTED', 'SETTLED', 'CANCELLED')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_account_id ON transactions (account_id);
CREATE INDEX IF NOT EXISTS idx_transactions_ref ON transactions (transaction_reference);
CREATE INDEX IF NOT EXISTS idx_transactions_status_created ON transactions (status, created_at);

-- =============================================================================
-- 8. VERIFICATION_ATTEMPTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS verification_attempts (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL REFERENCES transactions(transaction_id) ON DELETE RESTRICT,
    customer_id UUID NOT NULL REFERENCES customers(customer_id) ON DELETE RESTRICT,
    submitted_signature_id UUID NOT NULL REFERENCES signatures(signature_id) ON DELETE RESTRICT,
    enrolled_signature_id UUID NULL REFERENCES signatures(signature_id) ON DELETE RESTRICT,
    similarity_score NUMERIC(5, 4) NOT NULL CHECK (similarity_score >= 0.0000 AND similarity_score <= 1.0000),
    threshold_used NUMERIC(5, 4) NOT NULL CHECK (threshold_used >= 0.0000 AND threshold_used <= 1.0000),
    decision VARCHAR(32) NOT NULL CHECK (decision IN ('VERIFIED', 'MANUAL_REVIEW', 'REJECTED')),
    model_version_id UUID NOT NULL REFERENCES model_versions(model_version_id) ON DELETE RESTRICT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_verifications_transaction_id ON verification_attempts (transaction_id);
CREATE INDEX IF NOT EXISTS idx_verifications_customer_id ON verification_attempts (customer_id);
CREATE INDEX IF NOT EXISTS idx_verifications_decision ON verification_attempts (decision);
CREATE INDEX IF NOT EXISTS idx_verifications_created_at ON verification_attempts (created_at);

-- =============================================================================
-- 9. RISK_ASSESSMENTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS risk_assessments (
    risk_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL UNIQUE REFERENCES verification_attempts(verification_id) ON DELETE CASCADE,
    similarity_component NUMERIC(5, 4) NOT NULL CHECK (similarity_component >= 0.0000 AND similarity_component <= 1.0000),
    image_quality_component NUMERIC(5, 4) NOT NULL CHECK (image_quality_component >= 0.0000 AND image_quality_component <= 1.0000),
    transaction_risk_component NUMERIC(5, 4) NOT NULL CHECK (transaction_risk_component >= 0.0000 AND transaction_risk_component <= 1.0000),
    behavioral_component NUMERIC(5, 4) NOT NULL CHECK (behavioral_component >= 0.0000 AND behavioral_component <= 1.0000),
    overall_risk_score NUMERIC(5, 4) NOT NULL CHECK (overall_risk_score >= 0.0000 AND overall_risk_score <= 1.0000),
    risk_level VARCHAR(16) NOT NULL CHECK (risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    risk_factors JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_level ON risk_assessments (risk_level);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_score ON risk_assessments (overall_risk_score);

-- =============================================================================
-- 10. MANUAL_REVIEWS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS manual_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    verification_id UUID NOT NULL REFERENCES verification_attempts(verification_id) ON DELETE RESTRICT,
    reviewer_user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE RESTRICT,
    decision VARCHAR(32) NOT NULL CHECK (decision IN ('APPROVED', 'REJECTED')),
    review_comment TEXT NOT NULL,
    reviewed_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_manual_reviews_verification_id ON manual_reviews (verification_id);
CREATE INDEX IF NOT EXISTS idx_manual_reviews_reviewer ON manual_reviews (reviewer_user_id);
CREATE INDEX IF NOT EXISTS idx_manual_reviews_reviewed_at ON manual_reviews (reviewed_at);

-- =============================================================================
-- 11. AUDIT_LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NULL REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(64) NOT NULL,
    entity_type VARCHAR(64) NOT NULL,
    entity_id UUID NOT NULL,
    result VARCHAR(32) NOT NULL CHECK (result IN ('SUCCESS', 'FAILURE', 'WARNING', 'DENIED')),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    request_reference VARCHAR(64) NOT NULL,
    details JSONB NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON audit_logs (entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_request_ref ON audit_logs (request_reference);

-- =============================================================================
-- AUTOMATIC TIMESTAMPS TRIGGERS
-- =============================================================================
CREATE OR REPLACE FUNCTION update_timestamp_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_column();

DROP TRIGGER IF EXISTS trg_customers_updated_at ON customers;
CREATE TRIGGER trg_customers_updated_at
BEFORE UPDATE ON customers
FOR EACH ROW
EXECUTE FUNCTION update_timestamp_column();
