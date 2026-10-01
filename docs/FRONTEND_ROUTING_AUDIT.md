# SIGNATURE VMAKE — FRONTEND & ROUTING ARCHITECTURE AUDIT

**Audit Date:** October 2026  
**Auditor:** Antigravity AI Engineering Assistant  
**Repository:** `neeravjain91-jpg/signature-verification`  
**Current Frontend Status:** Monolithic Single-Page Application (SPA) with In-Page Hash-Anchor Navigation  

---

## 1. Executive Summary

This audit assesses the current frontend implementation of **SIGNATURE VMAKE** to guide its transition from a monolithic single-page interface using hash anchors (`#overview`, `#manual-workflow`, `#verification-studio`, `#model-comparison`, `#compliance-queue`, `#audit-timeline`, `#model-registry`) into a clean, multi-page web application with dedicated URLs and route-specific interfaces.

---

## 2. Current Frontend Entrypoint & File Inspection

### Inspected Files:
1. **`web/index.html` (1,608 lines, 107.4 KB, SHA-256: `5b12ab24db04...`):**
   - The primary interactive frontend delivered by FastAPI.
   - Contains all seven system sections inlined inside one large document.
2. **`index.html` (Root duplicate, 1,608 lines, 107.4 KB, identical SHA-256):**
   - A mirror of `web/index.html` kept at the repository root.
3. **`api/main.py` (Line 102–109):**
   - Route `@app.get("/", response_class=HTMLResponse)` explicitly reads and returns `web/index.html`:
     ```python
     @app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
     def serve_dashboard():
         html_path = Path("web/index.html")
         if html_path.exists():
             with open(html_path, "r", encoding="utf-8") as f:
                 return f.read()
         return "<h1>SIGNATURE VMAKE Platform API Live. Visit /docs for Swagger UI</h1>"
     ```
   - Currently, no static files directory is mounted with `app.mount("/static", ...)` or `app.mount("/assets", ...)`.
   - No sub-routes exist for individual pages (`/manual-workflow`, `/verification-studio`, `/model-comparison`, `/compliance-queue`, `/audit-timeline`, `/model-registry`).
4. **`vercel.json`:**
   - Pre-configured with `"outputDirectory": "web"` and `"cleanUrls": true`.
   - Contains a catch-all rewrite rule (`{"source": "/(.*)", "destination": "/index.html"}`), which routes all paths to the monolithic `index.html`.
5. **`.vercelignore`:**
   - Ignores backend code (`api/`, `ml/`, `services/`, `database/`, `data/`, etc.) so Vercel builds only the static UI.

---

## 3. Current Navigation Mechanism & Limitations

### The Problem: Single-Page Hash Anchors
Currently, the top navigation bar (`<header>`) inside `web/index.html` uses in-page anchor links:
```html
<nav class="hidden md:flex items-center space-x-6 text-sm font-medium">
    <a href="#overview">Overview</a>
    <a href="#manual-workflow">Manual Register & Verify</a>
    <a href="#verification-studio">Cheque Studio</a>
    <a href="#model-comparison">Model Comparison</a>
    <a href="#compliance-queue">Officer Queue</a>
    <a href="#audit-timeline">Audit Trail</a>
    <a href="#model-registry">Model Health</a>
</nav>
```

### Critical Flaws of Current Approach:
1. **No Real URL Routing:** Browsing to `http://127.0.0.1:8000/manual-workflow` returns a `404 Not Found`. Users cannot bookmark or directly link to specific operational tools.
2. **Page Bloat & Clutter:** A teller or compliance officer loading the interface downloads all DOM elements, tables, forms, canvases, and modal dialogs simultaneously, regardless of the task they need to perform.
3. **Broken Browser History:** Navigating between hash anchors does not create independent page contexts, complicating browser Back/Forward behavior and bookmarking.
4. **Duplicate Initialization:** On DOM content load, JavaScript queries all endpoints simultaneously (`checkBackendHealth`, `loadDashboardMetrics`, `loadPendingReviews`, `loadModelBenchmark`, `loadCustomerGallery`), creating unnecessary load on the backend.

---

## 4. Current Page Sections & Content Breakdown

The single file `web/index.html` is partitioned into the following logical sections:

| Section ID | Name / Role | Main Elements |
| :--- | :--- | :--- |
| `overview` | Executive KPI Cards | Total Verifications, Pass Rate, Fraud Block Rate, Officer Escalations. |
| `manual-workflow` | Manual Registration & Verification | Target customer selector, genuine specimen upload & vault enrollment, registered specimen gallery with soft deactivation, questioned signature upload, model track selector (ViT, RF, SVM, Logistic), mode selector (Single vs Gallery), live result badge, forensic metrics. |
| `verification-studio`| Cheque Transaction Studio | Amount, transaction type, sample preset selector (genuine vs forgery), run verification button, fraud risk progress bars, explainable factor badges. |
| `compliance-queue` | Officer Review Queue | Pending escalated transactions table, action button opening adjudication modal (`APPROVE`/`REJECT`). |
| `audit-timeline` | Regulatory Audit Ledger | Voucher reference lookup input, timeline showing historical attempts and officer reviews. |
| `model-comparison` | Model Benchmark Table | 4-model candidate evaluation table (AUC, EER, Accuracy, FAR, FRR, F1, Latency, Size), deterministic selection rationale. |
| *(Navbar only)* | Model Health | Currently lacks a dedicated section; linked to `#model-registry`. |

---

## 5. Current API Communication Analysis

- **API Base Configuration:**
  - Dynamic discovery via `localStorage.getItem('vmake_api_base')` or query parameter `?api=...`.
  - If running on port `8000`, uses root-relative paths (`""`), so API calls go to `/api/v1/...`.
  - Modal `#api-config-modal` allows switching backend hosts (for Vercel deployment pointing to Render/Railway).
- **Existing Endpoints Utilized by Frontend:**
  - `GET /api/v1/health`: Liveness & active model status.
  - `GET /api/v1/dashboard/metrics`: Total verifications, pass/reject rates, pending count.
  - `GET /api/v1/customers/{ref}/signatures`: Registered gallery specimens.
  - `POST /api/v1/signatures/enroll`: First signature enrollment into vault.
  - `POST /api/v1/signatures/{id}/deactivate`: Soft-delete specimen (`SUPERSEDED`).
  - `POST /api/v1/verifications/verify`: Questioned signature verification (Single/Gallery).
  - `POST /api/v1/verifications/verify-demo`: Preset cheque verification.
  - `GET /api/v1/verifications/pending-reviews`: Escalated transactions queue.
  - `POST /api/v1/verifications/{id}/adjudicate`: Officer approve/reject.
  - `GET /api/v1/audit/trail/{txn_ref}`: Non-repudiation audit ledger.
  - `GET /api/v1/models/benchmark`: Official test cohort evaluation metrics.
  - `GET /api/v1/models/health`: Runtime readiness across all 4 models.

---

## 6. Target Multi-Page Architecture & Route Mapping

The frontend will be transformed into dedicated, focused HTML pages with shared navigation and common assets:

```
web/
├── index.html                   --> / (Overview / System Dashboard)
├── manual-workflow.html         --> /manual-workflow (Manual Register & Verify)
├── verification-studio.html     --> /verification-studio (Cheque Studio)
├── model-comparison.html        --> /model-comparison (Candidate Benchmark Table & Charts)
├── compliance-queue.html        --> /compliance-queue (Officer Review Queue & Adjudication)
├── audit-timeline.html          --> /audit-timeline (Regulatory Audit Ledger)
├── model-registry.html          --> /model-registry (Live Model Health & Readiness)
└── assets/
    ├── css/
    │   └── app.css              (Shared styling, fonts, glass-card classes, glowing accents)
    └── js/
        ├── common.js            (Shared navigation builder, active route highlighter, connection badge, API config modal)
        ├── api.js               (Centralized API client for all /api/v1/ requests)
        ├── overview.js          (Overview KPI metrics loader)
        ├── manual-workflow.js   (Specimen enrollment, gallery display, second-sig verification)
        ├── verification-studio.js (Cheque studio, preset loading, risk factor decomposition)
        ├── model-comparison.js  (Benchmark metrics retrieval and comparison presentation)
        ├── compliance-queue.js  (Pending reviews queue and adjudication modal)
        ├── audit-timeline.js    (Transaction audit lookup and chronological timeline rendering)
        └── model-registry.js    (Live model runtime ping and readiness status cards)
```

### Route Mapping in FastAPI:
- `GET /` $\rightarrow$ `web/index.html`
- `GET /manual-workflow` $\rightarrow$ `web/manual-workflow.html`
- `GET /verification-studio` $\rightarrow$ `web/verification-studio.html`
- `GET /model-comparison` $\rightarrow$ `web/model-comparison.html`
- `GET /compliance-queue` $\rightarrow$ `web/compliance-queue.html`
- `GET /audit-timeline` $\rightarrow$ `web/audit-timeline.html`
- `GET /model-registry` $\rightarrow$ `web/model-registry.html`
- `GET /assets/{filepath:path}` $\rightarrow$ `StaticFiles(directory="web/assets")` mounted at `/assets`.

### Vercel Deployment Mapping:
In `vercel.json`:
- `cleanUrls: true` enables clean paths like `/manual-workflow` mapping directly to `manual-workflow.html`.
- Rewrites map API calls to the backend if configured, while static pages resolve automatically.

---

## 7. Action Plan

1. **Create Shared Assets:**
   - `web/assets/css/app.css`: Extract shared styles (`glass-card`, typography, scrollbars).
   - `web/assets/js/common.js`: Shared top navbar rendering with active route highlighting, API connection indicator, API URL configuration modal, and footer.
   - `web/assets/js/api.js`: Unified API fetch helper respecting `API_BASE` and root-relative endpoints.
2. **Construct Dedicated Pages:**
   - `web/index.html`: Clean Overview page with KPI cards, quick action cards, and system status.
   - `web/manual-workflow.html`: Focused on customer selection, specimen enrollment, gallery cards, and live biometric verification.
   - `web/verification-studio.html`: Cheque transaction verification with multi-factor risk engine breakdown.
   - `web/model-comparison.html`: Real candidate benchmark comparison table and deterministic selection rationale.
   - `web/compliance-queue.html`: Officer review queue with real adjudication modal.
   - `web/audit-timeline.html`: Regulatory audit trail lookup with chronological history.
   - `web/model-registry.html`: Live model health and readiness cards querying `/api/v1/models/health`.
3. **Mount Routes & Static Assets in FastAPI (`api/main.py`):**
   - Mount `/assets` via `StaticFiles(directory="web/assets")`.
   - Add explicit page endpoints returning HTML responses for all 7 routes.
4. **Update Root `index.html` & `vercel.json`:**
   - Synchronize root mirror and update Vercel configuration for clean multi-page URL routing.
5. **Add Comprehensive Routing & Page Tests:**
   - Ensure all 7 page routes return `200 OK`, valid HTML, correct page titles, and SIGNATURE VMAKE branding.
6. **Execute Live Verification & End-to-End Validation.**
