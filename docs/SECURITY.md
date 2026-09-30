# SIGNATURE VMAKE — Security, Authentication & Non-Repudiation Architecture

**Document Version:** 1.0.0  
**Project:** SIGNATURE VMAKE (`signature-vmake`)  
**Domain:** Security Architecture for Banking Document & Signature Biometrics  

---

## 1. Threat Model & Defense-in-Depth Architecture

Biometric banking verification platforms face distinct security threats:
1. **Presentation Attacks / Forgery Uploads:** Malicious actors submitting skilled forgeries or synthetic artifacts to execute unauthorized withdrawals.
2. **Identity Snooping / Privilege Escalation:** Unauthorized users attempting to approve transactions or view another customer's biometric signature specimens.
3. **Arbitrary File Upload & RCE:** Attackers uploading malicious executables or polyglot image scripts disguised as signatures.
4. **Audit Tampering:** Attempts to delete or alter logs to conceal unauthorized transaction overrides.

SIGNATURE VMAKE implements a 6-layer defense-in-depth security model:

```
[Layer 1: Network & CORS Gateway] ──► Host Whitelisting, SSL/TLS, Size Throttling
          │
[Layer 2: Authentication & RBAC]   ──► RFC 7519 JWT, Bcrypt Salted Hashes, Role Verification
          │
[Layer 3: File Upload Validation]  ──► 5MB Size Cap, Extension Whitelist, Header Verification
          │
[Layer 4: Biometric Model Defense] ──► Open-Set Metric Distance, Multi-Factor Risk Assessment
          │
[Layer 5: Vaulted Storage Isolation]─► Protected URI Scheme, Unexposed Filesystem Paths
          │
[Layer 6: Immutable Audit Trail]   ──► Cryptographic SHA-256 Hashes, Relational Event Logs
```

---

## 2. Authentication & Credential Security

Implemented in [`api/auth.py`](file:///c:/Users/ASUS/Downloads/hcl/api/auth.py):

### 2.1 Salted Bcrypt Password Hashing
* Plaintext passwords are never persisted.
* Uses the Blowfish-based bcrypt algorithm with an adaptive cost factor of 12 rounds ($2^{12} = 4,096$ iterations):
  $$\text{hash} = \text{bcrypt}(\text{password}, \text{gensalt}(rounds=12))$$
* Defends against rainbow-table attacks and ASIC/GPU hardware cracking.

### 2.2 RFC 7519 JSON Web Token (JWT) Issuance
* Authenticated users receive a cryptographically signed HMAC-SHA256 (HS256) JWT token.
* **Payload Structure:**
  - `sub`: Username identifier
  - `role`: Role authorization level (`CUSTOMER`, `OFFICER`, `ADMIN`)
  - `uid`: Unique UUID string
  - `exp`: Explicit expiration timestamp (default: 8 hours)
* Protected endpoints enforce token signature and expiration verification via `require_authenticated_user`.

### 2.3 Role-Based Access Control (RBAC)
* Three standardized roles:
  - **`CUSTOMER`**: Restricted to initiating personal transactions and viewing self profile.
  - **`OFFICER`**: Authorized to adjudicate manual review queues, review flagged signatures, and inspect risk breakdowns.
  - **`ADMIN`**: Authorized to register model versions, inspect system health, and review compliance audit trails.
* Enforced via the `RoleChecker(["OFFICER", "ADMIN"])` dependency wrapper.

---

## 3. Secure File Upload & Storage Protocol

### 3.1 Upload Size & Format Enforcement
Implemented in [`api/main.py`](file:///c:/Users/ASUS/Downloads/hcl/api/main.py):
* **Hard Size Cap:** Payloads exceeding $5\text{ MB}$ ($5,242,880\text{ bytes}$) are immediately aborted before disk writing with HTTP 413 (`REQUEST_ENTITY_TOO_LARGE`).
* **Extension Whitelist:** Only validated image extensions (`.png`, `.jpg`, `.jpeg`, `.tiff`, `.bmp`) are accepted.
* **Temporary Processing Isolation:** Uploads are written to isolated OS temporary files (`tempfile.NamedTemporaryFile`), processed for embedding generation and quality scoring, and immediately deleted upon request completion.

### 3.2 Protected Vault Storage
* Biometric signature specimens are never placed in public web document roots (e.g. `public/` or `static/`).
* Registered reference images are referenced via an internal abstract URI scheme (`vault://signatures/...`), preventing direct URL traversal or scraping.

---

## 4. Cryptographic Hashing & Immutable Audit Trail

### 4.1 SHA-256 Biometric Specimen Fingerprinting
Every enrolled or submitted signature undergoes cryptographic SHA-256 hashing:
$$\text{hash} = \text{SHA256}(\text{raw\_bytes})$$
The resulting 64-character hexadecimal digest is recorded in `signatures.file_hash`. This guarantees non-repudiation: if a signature specimen is ever contested in a legal or regulatory dispute, its hash confirms whether the specimen analyzed matches the physical cheque scanned.

### 4.2 Append-Only Audit Logging
All critical operations write to the `audit_logs` table:
* `audit_id`: Cryptographically unique UUIDv4
* `action`: Standardized event code (`CUSTOMER_SIGNATURE_ENROLLED`, `AUTOMATED_VERIFICATION_PASS`, `VERIFICATION_REFERRED_TO_OFFICER`, `AUTOMATED_FRAUD_REJECTION`, `OFFICER_REVIEW_APPROVED`)
* `entity_type`: Target domain entity (`SIGNATURE`, `TRANSACTION`, `VERIFICATION_ATTEMPT`)
* `request_reference`: End-to-end correlation ID (e.g. `REQ-XXXXXXXX`)
* `timestamp`: Immutable UTC timestamp
* Database constraints prevent row updates on audit logs, providing tamper-evident traceability.

---

## 5. Secrets Management
* Production secrets (`SIGNATURE_VMAKE_JWT_SECRET`, `DATABASE_URL`) are loaded strictly from OS environment variables.
* Default fallback secrets are restricted to local demonstration and testing environments.
