# End-to-End Verification Traceability Protocol

## 1. Traceability Architecture

In financial auditing, biometrics-driven decisions cannot exist as opaque predictions. Every signature verification must provide an unbroken, mathematically and relationally traceable chain from the originating customer to the final settlement or rejection.

```mermaid
flowchart TD
    C[1. CUSTOMER<br/>customer_id: DEMO-CUST-001] --> A[2. ACCOUNT<br/>account_reference: DEMO-ACC-CHK-8802]
    A --> T[3. TRANSACTION<br/>DEMO-TXN-CHEQUE-101 | $4,500.00]
    T --> S[4. SUBMITTED SIGNATURE<br/>storage_ref: vault://.../slip.png | hash: f0e1...9f0]
    S --> M[5. ML INFERENCE<br/>Model: SigNet-ResNet18 v1.0.0 | Thresh: 0.7850]
    M --> V[6. VERIFICATION ATTEMPT<br/>similarity_score: 0.9420 | decision: VERIFIED]
    V --> R[7. RISK ASSESSMENT<br/>composite_score: 0.0720 | level: LOW]
    R --> D{8. DECISION GATE}
    D -- "VERIFIED (Low Risk)" --> PASS[Autonomous Approval]
    D -- "MANUAL_REVIEW (Borderline)" --> REV[9. MANUAL REVIEW<br/>Officer Marcus: APPROVED / REJECTED]
    D -- "REJECTED (High Risk)" --> BLOCK[Immediate Fraud Block]
    PASS --> LOG[10. AUDIT LOG<br/>Action: AUTOMATED_PASS | Result: SUCCESS]
    REV --> LOG
    BLOCK --> LOG
```

---

## 2. Step-by-Step Lifecycle Trace

### Step 1: Customer Identification (`CUSTOMERS`)
* The transaction originates from or claims the identity of customer `DEMO-CUST-001` (Alice Walker).
* The customer profile is active and has registered reference specimens in the `signatures` table where `signature_type = 'ENROLLED'`.

### Step 2: Account Context (`ACCOUNTS`)
* The transaction targets checking account `DEMO-ACC-CHK-8802`.
* Foreign key: `accounts.customer_id = customers.customer_id`.
* Checks are performed on account status (`ACTIVE`, balance limits, overdraft terms).

### Step 3: Transaction Creation (`TRANSACTIONS`)
* A cheque deposit or withdrawal voucher of \$4,500.00 is submitted.
* Foreign key: `transactions.account_id = accounts.account_id`.
* The transaction status enters `PENDING`, awaiting biometric verification.

### Step 4: Physical Signature Acquisition (`SIGNATURES`)
* The signature is clipped from the document scanning system, hashed (SHA-256), and scored for image quality:
  * `storage_reference`: `vault://signatures/submissions/DEMO-TXN-CHEQUE-101/extracted_sig.png`
  * `file_hash`: `f0e1d2c3b4a5968778695a4b3c2d1e0fa1b2c3d4e5f60718293a4b5c6d7e8f90`
  * `image_quality_score`: `0.9400`
  * `signature_type`: `VERIFICATION_SUBMISSION`

### Step 5: Machine Learning Inference (`MODEL_VERSIONS` & `SIGNATURE_EMBEDDINGS`)
* The Siamese model (`SigNet-ResNet18-Siamese`, version `v1.0.0`) generates a 512-dimensional feature embedding for the submitted signature.
* The pre-computed enrolled embedding for `DEMO-CUST-001` is retrieved from `signature_embeddings`.
* The Euclidean / cosine distance is computed, yielding similarity metric $S \in [0, 1]$.

### Step 6: Verification Record Generation (`VERIFICATION_ATTEMPTS`)
* A new immutable verification attempt row is created:
  * `verification_id`: UUID
  * `similarity_score`: `0.9420`
  * `threshold_used`: `0.7850`
  * `decision`: `VERIFIED` (since $0.9420 \ge 0.7850$)
  * `model_version_id`: Links directly to model version `v1.0.0`.

### Step 7: Multi-Factor Risk Assessment (`RISK_ASSESSMENTS`)
* The fraud engine computes a 4-component weighted risk score:
  $$R_{\text{overall}} = w_1 (1 - S) + w_2 (1 - Q) + w_3 T + w_4 B$$
  * $S$: Similarity score ($0.9420$) $\rightarrow$ Risk component: $0.0580$
  * $Q$: Image quality ($0.9400$) $\rightarrow$ Risk component: $0.0600$
  * $T$: Transaction risk factor based on amount tier: $0.1200$
  * $B$: Customer behavioral anomaly factor: $0.0500$
  * $R_{\text{overall}} = 0.0720$ $\rightarrow$ `risk_level`: `LOW`.

### Step 8: Decision Execution & Branching
1. **Autonomous Approval (`VERIFIED` & `LOW` risk):**
   * Transaction status transitions to `VERIFIED` $\rightarrow$ `SETTLED`.
2. **Referral to Compliance (`MANUAL_REVIEW` or `MEDIUM` risk):**
   * If similarity is borderline (e.g. $0.7250$ vs $0.7850$ threshold) or amount exceeds high-value tier (\$48,000.00), the attempt is routed to the officer queue.
3. **Automated Fraud Block (`REJECTED` or `HIGH` risk):**
   * If similarity is low ($0.2840$) or image shows extreme distortion, the attempt is immediately rejected, locking the transaction.

### Step 9: Manual Compliance Adjudication (`MANUAL_REVIEWS`)
* For referred attempts, compliance officer (`officer_marcus`, User ID `UUID`) inspects the split screen comparing the enrolled specimen with the questioned signature.
* The officer enters a recorded justification comment (e.g., *"Customer contacted via phone challenge; natural stroke flourish confirmed"*).
* Decision: `APPROVED` or `REJECTED`.

### Step 10: Immutable Audit Logging (`AUDIT_LOGS`)
* The final action writes an append-only row to `audit_logs`:
  * `action`: `MANUAL_REVIEW_OVERRIDE_APPROVE` or `AUTOMATED_VERIFICATION_PASS`
  * `entity_type`: `VERIFICATION_ATTEMPT` or `MANUAL_REVIEW`
  * `entity_id`: Target UUID
  * `result`: `SUCCESS` or `DENIED`
  * `request_reference`: `REQ-CORR-7702` (correlation ID)
  * `timestamp`: ISO-8601 UTC timestamp.

---

## 3. Relational Query Demonstration

The entire audit trail for any transaction can be retrieved via a single SQL join query:

```sql
SELECT 
    c.customer_reference,
    c.full_name,
    a.account_reference,
    t.transaction_reference,
    t.transaction_type,
    t.amount,
    s_sub.storage_reference AS submitted_sig_path,
    mv.model_name || ' ' || mv.version AS model_used,
    va.similarity_score,
    va.threshold_used,
    va.decision AS ml_decision,
    ra.overall_risk_score,
    ra.risk_level,
    mr.decision AS officer_decision,
    u.username AS reviewed_by,
    mr.review_comment,
    al.action AS audit_action,
    al.timestamp AS audit_timestamp
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
JOIN verification_attempts va ON t.transaction_id = va.transaction_id
JOIN signatures s_sub ON va.submitted_signature_id = s_sub.signature_id
JOIN model_versions mv ON va.model_version_id = mv.model_version_id
JOIN risk_assessments ra ON va.verification_id = ra.verification_id
LEFT JOIN manual_reviews mr ON va.verification_id = mr.verification_id
LEFT JOIN users u ON mr.reviewer_user_id = u.user_id
JOIN audit_logs al ON al.entity_id = va.verification_id OR al.entity_id = mr.review_id
WHERE t.transaction_reference = 'DEMO-TXN-WIRE-102';
```

This ensures complete legal non-repudiation and regulatory compliance.
