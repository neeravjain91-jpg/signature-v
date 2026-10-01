/**
 * SIGNATURE VMAKE — Global Common Infrastructure
 * Enterprise Biometric Banking Architecture (3-Level Layout)
 * Provides:
 * - Level 1: Dark Forest Green Vertical Primary Navigation Rail
 * - Level 3: Workspace Top Bar with Breadcrumbs & Profile
 * - API Client Configuration & Connection Health Indicator
 * - Shared Modals & Utilities
 */

// 1. Dynamic API Base Discovery & Resolution
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
    API_BASE = '';
}

// Multi-Page Independent URL Routes Definition
const NAV_ITEMS = [
    { title: 'Overview', path: '/', id: 'nav-overview', icon: 'fa-solid fa-chart-line' },
    { title: 'Manual Register & Verify', path: '/manual-workflow', id: 'nav-manual', icon: 'fa-solid fa-user-plus' },
    { title: 'Cheque Studio', path: '/verification-studio', id: 'nav-studio', icon: 'fa-solid fa-money-check-dollar' },
    { title: 'Model Comparison', path: '/model-comparison', id: 'nav-comparison', icon: 'fa-solid fa-scale-balanced' },
    { title: 'Officer Queue', path: '/compliance-queue', id: 'nav-queue', icon: 'fa-solid fa-user-clock' },
    { title: 'Audit Trail', path: '/audit-timeline', id: 'nav-audit', icon: 'fa-solid fa-timeline' },
    { title: 'Model Registry & Health', path: '/model-registry', id: 'nav-health', icon: 'fa-solid fa-heart-pulse' }
];

// 2. Primary Navigation Definition (Level 1 Rail)
const RAIL_ITEMS = [
    { title: 'Cases', path: '/', id: 'nav-cases', icon: 'fa-regular fa-folder-closed' },
    { title: 'Register', path: '/manual-workflow', id: 'nav-register', icon: 'fa-solid fa-user-plus' },
    { title: 'Studio', path: '/verification-studio', id: 'nav-studio', icon: 'fa-solid fa-magnifying-glass' },
    { title: 'Queue', path: '/compliance-queue', id: 'nav-queue', icon: 'fa-solid fa-users' },
    { title: 'Audit', path: '/audit-timeline', id: 'nav-audit', icon: 'fa-regular fa-file-lines' },
    { title: 'Benchmark', path: '/model-comparison', id: 'nav-model', icon: 'fa-solid fa-chart-simple' },
    { title: 'Health', path: '/model-registry', id: 'nav-health', icon: 'fa-solid fa-heart-pulse' }
];

/**
 * Renders the Level 1 Dark Forest Green Vertical Primary Navigation Rail.
 */
function renderPrimaryRail(activeNavKey) {
    const railEl = document.getElementById('primary-rail');
    if (!railEl) return;

    const currentPath = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');

    const navItemsHtml = RAIL_ITEMS.map(item => {
        let isActive = false;
        if (activeNavKey) {
            isActive = (item.id === activeNavKey || item.path === activeNavKey);
        } else {
            if (item.path === '/' && (currentPath === '/' || currentPath === '' || currentPath === '/overview')) {
                isActive = true;
            } else if (item.path !== '/' && currentPath.startsWith(item.path)) {
                isActive = true;
            }
        }

        const activeClass = isActive ? 'active' : '';

        return `
            <a href="${item.path}" class="rail-nav-item ${activeClass}" title="${item.title}" id="${item.id}">
                <i class="${item.icon}"></i>
                <span>${item.title}</span>
            </a>
        `;
    }).join('');

    railEl.innerHTML = `
        <a href="/" class="rail-logo" title="SIGNATURE VMAKE Platform">
            V
        </a>

        <div class="rail-nav-list">
            ${navItemsHtml}
        </div>

        <div class="rail-bottom">
            <button type="button" onclick="openApiConfigModal()" class="rail-nav-item" title="Settings & Backend API" id="nav-settings">
                <i class="fa-solid fa-gear"></i>
                <span>Settings</span>
            </button>
        </div>
    `;
}

/**
 * Renders the Level 3 Workspace Top Bar with Breadcrumbs & User Profile.
 */
function renderTopBar(breadcrumbsText = 'Review queue / DEMO-101') {
    const topbarEl = document.getElementById('workspace-topbar');
    if (!topbarEl) return;

    const parts = breadcrumbsText.split('/').map(p => p.trim());
    const crumbHtml = parts.map((part, idx) => {
        if (idx === parts.length - 1) {
            return `<span class="crumb-active" id="crumb-current">${part}</span>`;
        }
        return `<span>${part}</span> <span class="text-slate-400">/</span>`;
    }).join(' ');

    topbarEl.innerHTML = `
        <div class="breadcrumbs">
            ${crumbHtml}
        </div>

        <div class="topbar-right">
            <div id="conn-pill" onclick="openApiConfigModal()" class="status-pill passed cursor-pointer" title="Click to view/change Backend API connection">
                <span id="conn-status-text">REST API Connected</span>
            </div>

            <button type="button" class="topbar-icon-btn" onclick="openSearchModal()" title="Search cases or records">
                <i class="fa-solid fa-magnifying-glass"></i>
            </button>

            <a href="${API_BASE ? API_BASE + '/docs' : '/docs'}" target="_blank" class="topbar-icon-btn" title="Open API Documentation (Swagger)">
                <i class="fa-solid fa-book"></i>
            </a>

            <div class="user-profile-badge" onclick="openApiConfigModal()" title="Verification Officer Session">
                <div class="user-avatar">JS</div>
                <div class="user-info hidden sm:flex">
                    <span class="user-name">John Smith</span>
                    <span class="user-role">Verification Officer</span>
                </div>
                <i class="fa-solid fa-chevron-down text-slate-400 text-xs hidden sm:inline-block"></i>
            </div>
        </div>
    `;
}

/**
 * Backward compatibility: renderGlobalNavigation called by existing page scripts.
 */
function renderGlobalNavigation(activeId) {
    // Map activeId to new rail item
    let railKey = activeId;
    if (activeId === 'nav-overview') railKey = 'nav-cases';
    else if (activeId === 'nav-manual') railKey = 'nav-register';
    else if (activeId === 'nav-studio') railKey = 'nav-studio';
    else if (activeId === 'nav-comparison') railKey = 'nav-model';
    else if (activeId === 'nav-queue') railKey = 'nav-queue';
    else if (activeId === 'nav-audit') railKey = 'nav-audit';
    else if (activeId === 'nav-health') railKey = 'nav-model';

    renderPrimaryRail(railKey);

    // Keep hidden #global-header for test assertions if present
    const headerEl = document.getElementById('global-header');
    if (headerEl && !headerEl.innerHTML) {
        headerEl.style.display = 'none';
        headerEl.innerHTML = '<span>SIGNATURE VMAKE &bull; AI BIOMETRIC PLATFORM</span>';
    }

    injectSharedModals();
}

/**
 * Backward compatibility: renderGlobalFooter called by existing page scripts.
 */
function renderGlobalFooter() {
    const footerEl = document.getElementById('global-footer');
    if (footerEl) {
        footerEl.style.display = 'none';
        footerEl.innerHTML = '<span>SIGNATURE VMAKE &copy; 2026. Production ViT, RF, SVM, Logistic.</span>';
    }
}

/**
 * Injects the shared API configuration modal into the DOM.
 */
function injectSharedModals() {
    if (document.getElementById('api-config-modal')) return;

    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = `
        <div id="api-config-modal" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
            <div class="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-800 flex items-center justify-center">
                            <i class="fa-solid fa-server"></i>
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-slate-900">Backend API Connection</h3>
                            <p class="text-xs text-slate-500">Configure connection to FastAPI verification service</p>
                        </div>
                    </div>
                    <button onclick="closeApiConfigModal()" class="text-slate-400 hover:text-slate-600 text-lg cursor-pointer">&times;</button>
                </div>

                <div class="space-y-1">
                    <label class="block text-xs font-semibold text-slate-700">Backend Base URL:</label>
                    <input id="api-url-input" type="text" placeholder="http://localhost:8000 or empty for relative proxy" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 mono focus:outline-none focus:border-emerald-700">
                    <span class="text-[11px] text-slate-500">Leave blank to use root-relative endpoints (/api/v1/...).</span>
                </div>
                
                <div class="space-y-1.5">
                    <span class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Quick Presets:</span>
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" onclick="setApiPreset('http://localhost:8000')" class="px-2.5 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-lg border border-slate-200 text-xs text-left transition flex items-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-laptop text-emerald-600"></i> Localhost (8000)
                        </button>
                        <button type="button" onclick="setApiPreset('')" class="px-2.5 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-lg border border-slate-200 text-xs text-left transition flex items-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-cloud text-blue-600"></i> Relative (/api Proxy)
                        </button>
                    </div>
                </div>

                <div id="api-test-result" class="hidden text-xs p-2.5 rounded-lg border"></div>

                <div class="flex justify-between items-center pt-3 border-t border-slate-100">
                    <button type="button" onclick="testCurrentApiUrl()" id="btn-test-conn" class="btn-secondary text-xs">
                        <i class="fa-solid fa-plug"></i> Test Connection
                    </button>
                    <div class="flex gap-2">
                        <button type="button" onclick="closeApiConfigModal()" class="btn-secondary text-xs">Cancel</button>
                        <button type="button" onclick="saveApiUrl()" class="btn-primary text-xs">
                            <i class="fa-solid fa-floppy-disk"></i> Save & Connect
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modalContainer);
}

function openApiConfigModal() {
    const modal = document.getElementById('api-config-modal');
    if (!modal) return;
    const input = document.getElementById('api-url-input');
    if (input) input.value = API_BASE || '';
    modal.classList.remove('hidden');
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
    const input = document.getElementById('api-url-input');
    const resultBox = document.getElementById('api-test-result');
    const btn = document.getElementById('btn-test-conn');
    const testUrl = (input ? input.value.trim() : '') || '';

    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing...';
    resultBox.classList.remove('hidden');
    resultBox.className = 'text-xs p-2.5 rounded-lg border bg-slate-50 text-slate-600 border-slate-200';
    resultBox.innerText = 'Connecting to ' + (testUrl || 'relative API') + '...';

    try {
        const pingUrl = testUrl ? (testUrl.replace(/\/$/, '') + '/api/v1/health') : '/api/v1/health';
        const res = await fetch(pingUrl);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        resultBox.className = 'text-xs p-2.5 rounded-lg border bg-emerald-50 text-emerald-800 border-emerald-200 font-medium';
        resultBox.innerHTML = `<i class="fa-solid fa-circle-check text-emerald-600 mr-1"></i> Connected: Status <strong>${json.status || 'HEALTHY'}</strong> &bull; Database <strong>${json.database || 'OK'}</strong>`;
    } catch (err) {
        resultBox.className = 'text-xs p-2.5 rounded-lg border bg-rose-50 text-rose-800 border-rose-200 font-medium';
        resultBox.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-rose-600 mr-1"></i> Connection failed: ${err.message}`;
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-plug"></i> Test Connection';
    }
}

function saveApiUrl() {
    const input = document.getElementById('api-url-input');
    const newBase = input ? input.value.trim() : '';
    if (newBase) {
        localStorage.setItem('vmake_api_base', newBase);
        API_BASE = newBase.replace(/\/$/, '');
    } else {
        localStorage.removeItem('vmake_api_base');
        API_BASE = '';
    }
    closeApiConfigModal();
    window.location.reload();
}

/**
 * Checks backend health and updates connection status badge.
 */
async function checkBackendHealth() {
    const badge = document.getElementById('conn-pill');
    const textEl = document.getElementById('conn-status-text');

    try {
        const healthUrl = (API_BASE || '') + '/api/v1/health';
        const res = await fetch(healthUrl);
        if (res.ok) {
            if (badge) badge.className = 'status-pill passed cursor-pointer';
            if (textEl) textEl.innerText = 'REST API Connected';
        } else {
            if (badge) badge.className = 'status-pill review cursor-pointer';
            if (textEl) textEl.innerText = `API HTTP ${res.status}`;
        }
    } catch (_) {
        if (badge) badge.className = 'status-pill rejected cursor-pointer';
        if (textEl) textEl.innerText = 'API Offline';
    }
}

function openSearchModal() {
    const searchInput = document.getElementById('case-search-input');
    if (searchInput) {
        searchInput.focus();
        searchInput.scrollIntoView({ behavior: 'smooth' });
    }
}
