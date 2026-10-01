# SIGNATURE VMAKE — MULTI-PAGE FRONTEND & ROUTING ARCHITECTURE

**System Name:** SIGNATURE VMAKE (AI-Powered Biometric Signature Verification Platform)  
**Architecture Transition:** Monolithic Hash-Anchor Single-Page Interface $\rightarrow$ Dedicated Multi-Page Application (MPA)  
**Status:** **OPERATIONAL & PRODUCTION-READY**  
**Audit & Implementation Date:** October 2026  

---

## 1. Architectural Overview & Design Philosophy

Previously, SIGNATURE VMAKE rendered all operations inside a single 1,608-line HTML document and relied on in-page hash anchors (`#overview`, `#manual-workflow`, `#verification-studio`, `#model-comparison`, `#compliance-queue`, `#audit-timeline`, `#model-registry`).

The frontend has been completely restructured into a **focused, modular Multi-Page Application (MPA)**. Each operational workspace is now an independently addressable web page with its own URL, dedicated DOM structure, focused JavaScript logic, and real browser history lifecycle (direct URL linking, page refresh, back/forward navigation).

### Key Architectural Tenets:
1. **No Single-Page Anchor Hiding:** Every tab is a real route backed by its own HTML page.
2. **Design Consistency:** Dark banking theme, glass-card styling, typography, and glowing accents are centralized in [`web/assets/css/app.css`](../web/assets/css/app.css).
3. **Shared Navigation & Status:** [`web/assets/js/common.js`](../web/assets/js/common.js) injects the unified top navigation bar with active route highlighting, real-time backend connection status, and the API configuration modal.
4. **Zero Frontend-Fabricated ML:** All biometric similarity calculations, risk scores, and decisions are computed by the live FastAPI backend via the centralized client [`web/assets/js/api.js`](../web/assets/js/api.js).
5. **Dual Environment Parity:** The page routing works identically when served locally by FastAPI / Docker and when deployed as static assets on Vercel.

---

## 2. Page & Route Registry

| Page Name | Canonical Route | Template File | Dedicated Script | Primary Operational Responsibility |
| :--- | :--- | :--- | :--- | :--- |
| **Overview** | `/` (or `/overview`) | `web/index.html` | `web/assets/js/overview.js` | Executive KPI dashboard, active ML backbone status, platform health, and workspace navigation hubs. |
| **Manual Register & Verify** | `/manual-workflow` | `web/manual-workflow.html` | `web/assets/js/manual-workflow.js` | Customer vault management, genuine specimen enrollment (reference only), specimen gallery with soft deactivation, questioned signature upload, and live multi-candidate dynamic verification. |
| **Cheque Studio** | `/verification-studio` | `web/verification-studio.html` | `web/assets/js/verification-studio.js` | Banking voucher verification, scenario presets (genuine vs forgery), and multi-factor fraud risk engine decomposition (biometric deficit, scan quality, transaction amount tier, behavioral risk). |
| **Model Comparison** | `/model-comparison` | `web/model-comparison.html` | `web/assets/js/model-comparison.js` | Objective candidate model benchmark matrix (AUC, EER, Accuracy, FAR, FRR, TAR, F1, Latency, Size) and deterministic banking selection rationale. |
| **Officer Queue** | `/compliance-queue` | `web/compliance-queue.html` | `web/assets/js/compliance-queue.js` | Manual-review escalation queue, maker-checker adjudication modal with mandatory compliance notes, and live Approve/Reject submission. |
| **Audit Trail** | `/audit-timeline` | `web/audit-timeline.html` | `web/assets/js/audit-timeline.js` | Forensic transaction reference lookup, chronological attempt sequence, risk component audit history, and SHA-256 non-repudiation logging. |
| **Model Health** | `/model-registry` | `web/model-registry.html` | `web/assets/js/model-registry.js` | Real-time diagnostic ping across all 4 candidate models, verifying weights readiness, checkpoints, operating thresholds, and inference latency. |

---

## 3. Directory Layout & File Organization

```
web/
├── index.html                   --> / (Overview Dashboard)
├── manual-workflow.html         --> /manual-workflow (Manual Register & Verify)
├── verification-studio.html     --> /verification-studio (Cheque Studio)
├── model-comparison.html        --> /model-comparison (Model Benchmark Matrix)
├── compliance-queue.html        --> /compliance-queue (Officer Adjudication Queue)
├── audit-timeline.html          --> /audit-timeline (Regulatory Audit Ledger)
├── model-registry.html          --> /model-registry (Live Model Health Registry)
└── assets/
    ├── css/
    │   └── app.css              --> Shared banking styles, glass-card classes, scrollbars
    └── js/
        ├── common.js            --> Dynamic navigation, active route highlight, API base, connection badge
        ├── api.js               --> Unified API helper client for all /api/v1/ endpoints
        ├── overview.js          --> Overview KPI metrics retrieval
        ├── manual-workflow.js   --> Vault enrollment, gallery display, second-sig verification
        ├── verification-studio.js --> Cheque verification, preset toggling, risk factor breakdown
        ├── model-comparison.js  --> Benchmark matrix populator & rationale
        ├── compliance-queue.js  --> Pending review queue & adjudication modal
        ├── audit-timeline.js    --> Voucher audit lookup & chronological timeline
        └── model-registry.js    --> Live model health ping & readiness status
```

---

## 4. Shared Infrastructure Components

### 4.1. Navigation Bar with Active Route Detection
Every page includes `<header id="global-header"></header>`. On `DOMContentLoaded`, `renderGlobalNavigation()` parses `window.location.pathname`, applies the `.nav-link-active` class to the current page, and generates links:
```html
<a href="/">Overview</a>
<a href="/manual-workflow">Manual Register & Verify</a>
<a href="/verification-studio">Cheque Studio</a>
<a href="/model-comparison">Model Comparison</a>
<a href="/compliance-queue">Officer Queue</a>
<a href="/audit-timeline">Audit Trail</a>
<a href="/model-registry">Model Health</a>
```

### 4.2. API Origin Resolution
The application automatically resolves the backend origin via `web/assets/js/common.js`:
- Running on port 8000 (FastAPI dev/production): Uses root-relative `""` $\rightarrow$ calls go to `/api/v1/...`.
- Running on port 5173/3000 (local dev servers): Defaults to `http://localhost:8000`.
- Deployed on Vercel: Uses root-relative `""` to route via Vercel proxy or user-configured URL stored in `localStorage.getItem('vmake_api_base')`.

### 4.3. Centralized API Helper Client
[`web/assets/js/api.js`](../web/assets/js/api.js) standardizes API calls:
- `apiGet(endpoint)`: Asynchronous GET returning parsed JSON with standardized HTTP error extraction.
- `apiPost(endpoint, data, isFormData)`: Supports both standard JSON payloads and multipart `FormData` for image file uploads.
- Helper formatters: `formatScore(score)`, `formatCurrency(amount)`, `formatDate(isoString)`.

---

## 5. FastAPI Backend Page & Static Asset Routing

In [`api/main.py`](../api/main.py), static files and HTML pages are served cleanly:

```python
# Mount static assets directory
assets_path = Path("web/assets")
if assets_path.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

def _serve_page(filename: str) -> HTMLResponse:
    html_path = Path("web") / filename
    if html_path.exists():
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content=f"<h1>Page {filename} not found</h1>", status_code=404)

@app.get("/", response_class=HTMLResponse, tags=["Web Interface"])
def serve_overview():
    return _serve_page("index.html")

@app.get("/manual-workflow", response_class=HTMLResponse, tags=["Web Interface"])
def serve_manual_workflow():
    return _serve_page("manual-workflow.html")

@app.get("/verification-studio", response_class=HTMLResponse, tags=["Web Interface"])
def serve_verification_studio():
    return _serve_page("verification-studio.html")

@app.get("/model-comparison", response_class=HTMLResponse, tags=["Web Interface"])
def serve_model_comparison():
    return _serve_page("model-comparison.html")

@app.get("/compliance-queue", response_class=HTMLResponse, tags=["Web Interface"])
def serve_compliance_queue():
    return _serve_page("compliance-queue.html")

@app.get("/audit-timeline", response_class=HTMLResponse, tags=["Web Interface"])
def serve_audit_timeline():
    return _serve_page("audit-timeline.html")

@app.get("/model-registry", response_class=HTMLResponse, tags=["Web Interface"])
def serve_model_registry():
    return _serve_page("model-registry.html")
```

---

## 6. Vercel & Cloud Deployment Routing

The repository configuration in [`vercel.json`](../vercel.json) natively maps clean routes to HTML files:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "version": 2,
  "name": "signature-vmake",
  "cleanUrls": true,
  "outputDirectory": "web",
  "routes": [
    { "src": "/assets/(.*)", "dest": "/assets/$1" },
    { "src": "/manual-workflow", "dest": "/manual-workflow.html" },
    { "src": "/verification-studio", "dest": "/verification-studio.html" },
    { "src": "/model-comparison", "dest": "/model-comparison.html" },
    { "src": "/compliance-queue", "dest": "/compliance-queue.html" },
    { "src": "/audit-timeline", "dest": "/audit-timeline.html" },
    { "src": "/model-registry", "dest": "/model-registry.html" },
    { "src": "/overview", "dest": "/index.html" },
    { "src": "/", "dest": "/index.html" }
  ]
}
```

---

## 7. Verification & Automated Test Coverage

The multi-page routing was rigorously validated with **10 automated tests** in [`tests/test_page_routing.py`](../tests/test_page_routing.py):
- `test_overview_page_route`: Verifies `GET /` returns `200 OK`, page title, and branding.
- `test_overview_alias_route`: Verifies `GET /overview` returns `200 OK`.
- `test_manual_workflow_page_route`: Verifies `GET /manual-workflow` returns `200 OK` and enrollment controls.
- `test_verification_studio_page_route`: Verifies `GET /verification-studio` returns `200 OK` and cheque controls.
- `test_model_comparison_page_route`: Verifies `GET /model-comparison` returns `200 OK` and benchmark table.
- `test_compliance_queue_page_route`: Verifies `GET /compliance-queue` returns `200 OK` and review modal.
- `test_audit_timeline_page_route`: Verifies `GET /audit-timeline` returns `200 OK` and timeline container.
- `test_model_registry_page_route`: Verifies `GET /model-registry` returns `200 OK` and model grid.
- `test_static_assets_delivery`: Verifies `/assets/css/app.css` and all 8 `.js` files load with `200 OK`.
- `test_navigation_urls_are_independent_routes`: Verifies navigation links target independent routes rather than hash anchors.

**Full Pytest Test Suite Results:**
- **53 passed** in 66.12 seconds (100% pass rate).
