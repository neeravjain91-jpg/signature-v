/**
 * SIGNATURE VMAKE — Global Common Infrastructure
 * Provides:
 * - Dynamic API Base Discovery & Configuration
 * - Shared Top Navigation with Active Route Highlighting
 * - Real-Time Backend Liveness & Health Indicator
 * - Shared Footer & API Configuration Modal
 */

// 1. API Base Resolution
const urlParams = new URLSearchParams(window.location.search);
let storedApi = localStorage.getItem('vmake_api_base');
let queryApi = urlParams.get('api');
if (queryApi) {
    localStorage.setItem('vmake_api_base', queryApi);
    storedApi = queryApi;
}

let API_BASE = '';
if (storedApi) {
    API_BASE = storedApi.replace(/\/$/, '');
} else if (window.location.port === '8000') {
    API_BASE = '';
} else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    API_BASE = 'http://localhost:8000';
} else {
    // Cloud / Vercel deployment: relative path to route through Vercel rewrites proxy
    API_BASE = '';
}

// 2. Navigation Item Definitions
const NAV_ITEMS = [
    { title: 'Overview', path: '/', id: 'nav-overview' },
    { title: 'Manual Register & Verify', path: '/manual-workflow', id: 'nav-manual', icon: 'fa-id-card-clip' },
    { title: 'Cheque Studio', path: '/verification-studio', id: 'nav-studio' },
    { title: 'Model Comparison', path: '/model-comparison', id: 'nav-comparison' },
    { title: 'Officer Queue', path: '/compliance-queue', id: 'nav-queue' },
    { title: 'Audit Trail', path: '/audit-timeline', id: 'nav-audit' },
    { title: 'Model Health', path: '/model-registry', id: 'nav-health' }
];

/**
 * Initializes and injects the global top navbar with active state detection.
 */
function renderGlobalNavigation(activeId) {
    const headerEl = document.getElementById('global-header');
    if (!headerEl) return;

    // Detect active page based on pathname if not explicitly passed
    const currentPath = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    
    const navLinksHtml = NAV_ITEMS.map(item => {
        let isActive = false;
        if (activeId) {
            isActive = (item.id === activeId);
        } else {
            if (item.path === '/' && (currentPath === '/' || currentPath === '')) {
                isActive = true;
            } else if (item.path !== '/' && currentPath.startsWith(item.path)) {
                isActive = true;
            }
        }

        const activeClasses = isActive 
            ? 'nav-link-active text-cyan-400 font-semibold' 
            : 'text-slate-300 hover:text-white transition';

        const iconHtml = item.icon ? `<i class="fa-solid ${item.icon} mr-1.5"></i>` : '';

        return `
            <a href="${item.path}" class="${activeClasses} text-sm flex items-center">
                ${iconHtml}${item.title}
            </a>
        `;
    }).join('');

    headerEl.className = 'border-b border-slate-800 bg-slate-900/80 sticky top-0 z-50 backdrop-blur-md';
    headerEl.innerHTML = `
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <a href="/" class="flex items-center space-x-3 group">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-bold text-white shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
                        <i class="fa-solid fa-signature text-xl"></i>
                    </div>
                    <div>
                        <span class="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-cyan-400">SIGNATURE VMAKE</span>
                        <span class="hidden sm:inline-block text-xs ml-2 px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-400 border border-cyan-800/60 font-semibold">
                            <i class="fa-solid fa-trophy mr-1 text-amber-400"></i>AI BIOMETRIC PLATFORM
                        </span>
                    </div>
                </a>
            </div>

            <nav class="hidden lg:flex items-center space-x-6 text-sm font-medium">
                ${navLinksHtml}
            </nav>

            <div class="flex items-center space-x-3">
                <div id="conn-badge" onclick="configureApiEndpoint()" title="Click to view or change backend API connection" class="flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-emerald-400 text-xs cursor-pointer hover:border-cyan-500 transition">
                    <span id="conn-dot" class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                    <span id="conn-status-text" class="font-medium">REST API CONNECTED</span>
                </div>
                <button onclick="configureApiEndpoint()" title="Configure Backend API URL" class="px-2.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition flex items-center gap-1.5 cursor-pointer">
                    <i class="fa-solid fa-server text-cyan-400"></i> <span class="hidden sm:inline">API URL</span>
                </button>
                <a id="api-docs-link" href="${API_BASE ? API_BASE + '/docs' : '/docs'}" target="_blank" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition flex items-center gap-1.5">
                    <i class="fa-solid fa-book"></i> API Docs
                </a>
            </div>
        </div>

        <!-- Mobile Secondary Nav Scrollbar -->
        <div class="lg:hidden flex items-center space-x-4 overflow-x-auto px-4 py-2 bg-slate-950/60 border-t border-slate-800/80 text-xs">
            ${navLinksHtml}
        </div>
    `;

    // Inject shared modal into body if not already present
    injectSharedModals();
}

/**
 * Injects the shared API configuration modal into the DOM.
 */
function injectSharedModals() {
    if (document.getElementById('api-config-modal')) return;

    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = `
        <div id="api-config-modal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center gap-2">
                        <i class="fa-solid fa-server text-cyan-400"></i>
                        <h3 class="text-base font-bold text-white">Backend API Connection</h3>
                    </div>
                    <button onclick="closeApiConfigModal()" class="text-slate-400 hover:text-white text-lg">&times;</button>
                </div>
                <p class="text-xs text-slate-400 leading-relaxed">
                    Connect this Web Application to your FastAPI ML backend instance. Enter your backend host URL below or select a preset.
                </p>
                <div>
                    <label class="block text-xs font-semibold text-slate-300 mb-1.5">Backend Base URL:</label>
                    <input id="api-url-input" type="text" placeholder="https://signature-vmake-api.onrender.com or http://localhost:8000" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white mono focus:outline-none focus:border-cyan-500">
                    <span class="text-[10px] text-slate-500 mt-1 block">Leave empty to use root-relative paths (/api/v1/...).</span>
                </div>
                
                <div class="space-y-1.5">
                    <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Quick Presets:</span>
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" onclick="setApiPreset('http://localhost:8000')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-[11px] text-left transition flex items-center gap-1.5">
                            <i class="fa-solid fa-laptop text-emerald-400"></i> Localhost (8000)
                        </button>
                        <button type="button" onclick="setApiPreset('')" class="px-2.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 text-[11px] text-left transition flex items-center gap-1.5">
                            <i class="fa-solid fa-cloud text-cyan-400"></i> Relative (/api Proxy)
                        </button>
                    </div>
                </div>

                <div id="api-test-result" class="hidden text-xs p-2.5 rounded-lg border"></div>

                <div class="flex justify-between items-center pt-3 border-t border-slate-800">
                    <button type="button" onclick="testCurrentApiUrl()" id="btn-test-conn" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold border border-slate-700 transition flex items-center gap-1.5">
                        <i class="fa-solid fa-plug"></i> Test Connection
                    </button>
                    <div class="flex gap-2">
                        <button type="button" onclick="closeApiConfigModal()" class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-lg text-xs font-semibold transition">Cancel</button>
                        <button type="button" onclick="saveApiUrl()" class="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold transition flex items-center gap-1.5">
                            <i class="fa-solid fa-floppy-disk"></i> Save & Connect
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modalContainer);
}

/**
 * Injects the shared footer into `<footer id="global-footer">`.
 */
function renderGlobalFooter() {
    const footerEl = document.getElementById('global-footer');
    if (!footerEl) return;
    footerEl.className = 'border-t border-slate-800 bg-slate-950/60 py-6 text-center text-xs text-slate-500 mt-auto';
    footerEl.innerHTML = `
        <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p>SIGNATURE VMAKE &bull; AI-Powered Biometric Signature Verification Platform &copy; 2026.</p>
            <div class="flex items-center space-x-4 text-slate-400">
                <span>Production ViT &bull; RF &bull; SVM &bull; Logistic</span>
                <span>&bull;</span>
                <a href="/api/v1/health" target="_blank" class="hover:text-cyan-400 transition">API Health</a>
                <span>&bull;</span>
                <a href="${API_BASE ? API_BASE + '/docs' : '/docs'}" target="_blank" class="hover:text-cyan-400 transition">Swagger</a>
            </div>
        </div>
    `;
}

// 3. API Modal Controller
function configureApiEndpoint() {
    const input = document.getElementById('api-url-input');
    if (input) input.value = localStorage.getItem('vmake_api_base') || (API_BASE || '');
    const resultBox = document.getElementById('api-test-result');
    if (resultBox) {
        resultBox.className = 'hidden text-xs p-2.5 rounded-lg border';
        resultBox.innerHTML = '';
    }
    const modal = document.getElementById('api-config-modal');
    if (modal) modal.classList.remove('hidden');
}

function closeApiConfigModal() {
    const modal = document.getElementById('api-config-modal');
    if (modal) modal.classList.add('hidden');
}

function setApiPreset(url) {
    const input = document.getElementById('api-url-input');
    if (input) input.value = url;
}

async function testCurrentApiUrl() {
    const inputVal = (document.getElementById('api-url-input')?.value || '').trim().replace(/\/$/, '');
    const targetUrl = (inputVal ? `${inputVal}` : (API_BASE || '')) + '/api/v1/health';
    const resultBox = document.getElementById('api-test-result');
    const testBtn = document.getElementById('btn-test-conn');

    if (!resultBox || !testBtn) return;

    testBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
    resultBox.classList.remove('hidden');
    resultBox.className = 'text-xs p-2.5 rounded-lg border bg-slate-950 border-slate-800 text-slate-300 flex items-center gap-2';
    resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-cyan-400"></i> Pinging ' + (inputVal || 'relative (/api/v1)') + '...';

    try {
        const t0 = performance.now();
        const res = await fetch(targetUrl);
        const latency = Math.round(performance.now() - t0);
        if (res.ok) {
            const data = await res.json();
            resultBox.className = 'text-xs p-2.5 rounded-lg border bg-emerald-950/60 border-emerald-800 text-emerald-400 flex items-center gap-2';
            resultBox.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> Connected! Status: ${data.status} (Latency: ${latency}ms)`;
        } else {
            resultBox.className = 'text-xs p-2.5 rounded-lg border bg-amber-950/60 border-amber-800 text-amber-400 flex items-center gap-2';
            resultBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-amber-400"></i> Server reached but returned HTTP status ${res.status}.`;
        }
    } catch (e) {
        resultBox.className = 'text-xs p-2.5 rounded-lg border bg-rose-950/60 border-rose-800 text-rose-400 flex items-center gap-2';
        resultBox.innerHTML = `<i class="fa-solid fa-circle-xmark text-rose-400"></i> Connection failed: ${e.message}. Ensure backend is running.`;
    } finally {
        testBtn.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
    }
}

function saveApiUrl() {
    const inputVal = (document.getElementById('api-url-input')?.value || '').trim().replace(/\/$/, '');
    if (inputVal) {
        localStorage.setItem('vmake_api_base', inputVal);
    } else {
        localStorage.removeItem('vmake_api_base');
    }
    window.location.reload();
}

// 4. Global Backend Health & Connection Checker
async function checkBackendHealth() {
    const badge = document.getElementById('conn-badge');
    const dot = document.getElementById('conn-dot');
    const text = document.getElementById('conn-status-text');
    if (!badge || !dot || !text) return;

    try {
        const healthUrl = (API_BASE ? `${API_BASE}` : '') + '/api/v1/health';
        const startTime = performance.now();
        const res = await fetch(healthUrl);
        const latency = Math.round(performance.now() - startTime);

        if (res.ok) {
            const data = await res.json();
            badge.className = 'flex items-center space-x-2 px-3 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/50 text-emerald-400 text-xs cursor-pointer hover:border-cyan-500 transition';
            dot.className = 'w-2 h-2 rounded-full bg-emerald-400 animate-pulse';
            const hostLabel = API_BASE ? API_BASE.replace(/^https?:\/\//, '') : (window.location.port === '8000' ? 'PORT 8000' : 'LIVE API');
            text.innerText = `REST API LIVE (${hostLabel}, ${latency}ms)`;
            return data;
        } else {
            throw new Error('Non-200 status');
        }
    } catch (err) {
        badge.className = 'flex items-center space-x-2 px-3 py-1 rounded-full bg-rose-950/60 border border-rose-800/50 text-rose-400 text-xs cursor-pointer hover:border-rose-500 transition';
        dot.className = 'w-2 h-2 rounded-full bg-rose-500';
        text.innerText = 'BACKEND OFFLINE (CLICK API URL)';
        return null;
    }
}
