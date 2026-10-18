/**
 * SYNAPSE — Biometric Analysis Lab Common Infrastructure
 * Intelligent Signature Verification & Fraud Risk Assessment System
 * Provides:
 * - Level 1: Deep Navy / Charcoal Biometric Navigation Rail
 * - Level 3: Forensic Workspace Top Bar with Model Telemetry & Status
 * - API Client Configuration & Connection Health Monitor
 * - Shared Modals & Utilities
 */

// 1. Dynamic API Base Discovery & Resolution
const urlParams = new URLSearchParams(window.location.search);
let storedApi = localStorage.getItem('synapse_api_base') || localStorage.getItem('vmake_api_base');
let queryApi = urlParams.get('api');
if (queryApi) {
    localStorage.setItem('synapse_api_base', queryApi);
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
    { title: 'Signature Analysis Lab', path: '/manual-workflow', id: 'nav-manual', icon: 'fa-solid fa-fingerprint' },
    { title: 'Fraud Risk Studio', path: '/verification-studio', id: 'nav-studio', icon: 'fa-solid fa-microscope' },
    { title: 'Model Evaluation', path: '/model-comparison', id: 'nav-comparison', icon: 'fa-solid fa-chart-simple' },
    { title: 'Verification History', path: '/compliance-queue', id: 'nav-queue', icon: 'fa-solid fa-clock-rotate-left' },
    { title: 'Evidence & Traceability', path: '/audit-timeline', id: 'nav-audit', icon: 'fa-solid fa-shield-halved' },
    { title: 'Model Registry & Health', path: '/model-registry', id: 'nav-health', icon: 'fa-solid fa-heart-pulse' }
];

// Primary Navigation Definition (Level 1 Rail)
const RAIL_ITEMS = [
    { title: 'Overview', path: '/', id: 'nav-cases', icon: 'fa-solid fa-chart-line' },
    { title: 'Lab', path: '/manual-workflow', id: 'nav-register', icon: 'fa-solid fa-fingerprint' },
    { title: 'Studio', path: '/verification-studio', id: 'nav-studio', icon: 'fa-solid fa-microscope' },
    { title: 'Evaluation', path: '/model-comparison', id: 'nav-model', icon: 'fa-solid fa-chart-simple' },
    { title: 'History', path: '/compliance-queue', id: 'nav-queue', icon: 'fa-solid fa-clock-rotate-left' },
    { title: 'Traceability', path: '/audit-timeline', id: 'nav-audit', icon: 'fa-solid fa-shield-halved' },
    { title: 'Health', path: '/model-registry', id: 'nav-health', icon: 'fa-solid fa-heart-pulse' }
];

/**
 * Renders the Deep Charcoal Biometric Analysis Navigation Rail.
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
        <a href="/" class="rail-logo" title="SIGNATURE VMAKE — AI Biometric Operations">
            <i class="fa-solid fa-signature"></i>
        </a>

        <div class="rail-nav-list">
            ${navItemsHtml}
        </div>

        <div class="rail-bottom">
            <button type="button" onclick="openApiConfigModal()" class="rail-nav-item" title="Diagnostics & API Engine" id="nav-settings">
                <i class="fa-solid fa-gear"></i>
                <span>Config</span>
            </button>
        </div>
    `;
}

/**
 * Renders the Forensic Workspace Top Bar with Model Telemetry & Status.
 */
function renderTopBar(breadcrumbsText = 'Cases / Signature verification / Case review') {
    const topbarEl = document.getElementById('workspace-topbar');
    if (!topbarEl) return;

    const parts = breadcrumbsText.split('/').map(p => p.trim());
    const crumbHtml = parts.map((part, idx) => {
        if (idx === parts.length - 1) {
            return `<span class="crumb-active">${part}</span>`;
        }
        return `<span>${part}</span> <span class="text-slate-400">/</span>`;
    }).join(' ');

    topbarEl.innerHTML = `
        <div class="breadcrumbs">
            ${crumbHtml}
        </div>

        <div class="topbar-right">
            <div class="flex items-center gap-2">
                <button type="button" class="topbar-icon-btn" onclick="openSearchModal()" title="Search cases">
                    <i class="fa-solid fa-magnifying-glass"></i>
                </button>
                <button type="button" class="topbar-icon-btn" onclick="openApiConfigModal()" title="API Engine Diagnostics">
                    <i class="fa-solid fa-gear"></i>
                </button>
            </div>

            <div class="user-profile-badge" onclick="openApiConfigModal()" title="Verification Officer Session">
                <div class="user-avatar">AM</div>
                <div class="user-info">
                    <span class="user-name">Alex Morgan</span>
                    <span class="user-role">Verification Officer</span>
                </div>
            </div>
        </div>
    `;
}
    `;
}

/**
 * Backward compatibility: renderGlobalNavigation called by existing page scripts.
 */
function renderGlobalNavigation(activeId) {
    let railKey = activeId;
    if (activeId === 'nav-overview') railKey = 'nav-cases';
    else if (activeId === 'nav-manual') railKey = 'nav-register';
    else if (activeId === 'nav-studio') railKey = 'nav-studio';
    else if (activeId === 'nav-comparison') railKey = 'nav-model';
    else if (activeId === 'nav-queue') railKey = 'nav-queue';
    else if (activeId === 'nav-audit') railKey = 'nav-audit';
    else if (activeId === 'nav-health') railKey = 'nav-health';

    renderPrimaryRail(railKey);

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
        <div id="api-config-modal" class="fixed inset-0 bg-black/80 backdrop-blur-md z-50 hidden flex items-center justify-center p-4">
            <div class="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl text-slate-100">
                <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-lg bg-emerald-950 border border-emerald-600/40 text-emerald-400 flex items-center justify-center">
                            <i class="fa-solid fa-server"></i>
                        </div>
                        <div>
                            <h3 class="text-base font-bold text-white">SIGNATURE VMAKE Engine Diagnostics</h3>
                            <p class="text-xs text-slate-400">Configure connection to FastAPI verification microservice</p>
                        </div>
                    </div>
                    <button onclick="closeApiConfigModal()" class="text-slate-400 hover:text-white text-lg cursor-pointer">&times;</button>
                </div>

                <div class="space-y-1">
                    <label class="block text-xs font-semibold text-slate-300">Backend Base URL:</label>
                    <input id="api-url-input" type="text" placeholder="http://localhost:8000 or empty for relative proxy" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-xs text-emerald-300 mono focus:outline-none focus:border-emerald-500">
                    <span class="text-[11px] text-slate-500">Leave blank to use root-relative endpoints (/api/v1/...).</span>
                </div>
                
                <div class="space-y-1.5">
                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Quick Presets:</span>
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" onclick="setApiPreset('http://localhost:8000')" class="px-2.5 py-2 bg-slate-800 hover:bg-slate-750 text-slate-200 rounded-lg border border-slate-700 text-xs text-left transition flex items-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-laptop text-emerald-400"></i> Localhost (8000)
                        </button>
                        <button type="button" onclick="setApiPreset('')" class="px-2.5 py-2 bg-slate-800 hover:bg-slate-750 text-slate-200 rounded-lg border border-slate-700 text-xs text-left transition flex items-center gap-2 cursor-pointer">
                            <i class="fa-solid fa-cloud text-emerald-400"></i> Relative (/api Proxy)
                        </button>
                    </div>
                </div>

                <div id="api-test-result" class="hidden text-xs p-2.5 rounded-lg border"></div>

                <div class="flex justify-between items-center pt-3 border-t border-slate-800">
                    <button type="button" onclick="testCurrentApiUrl()" id="btn-test-conn" class="btn-secondary text-xs">
                        <i class="fa-solid fa-plug"></i> Test Engine Connection
                    </button>
                    <div class="flex gap-2">
                        <button type="button" onclick="closeApiConfigModal()" class="btn-secondary text-xs">Cancel</button>
                        <button type="button" onclick="saveApiUrl()" class="btn-primary text-xs">
                            <i class="fa-solid fa-floppy-disk"></i> Save & Apply
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
    if (!modal) return;
    modal.classList.add('hidden');
}

function setApiPreset(url) {
    const input = document.getElementById('api-url-input');
    if (input) input.value = url;
}

async function testCurrentApiUrl() {
    const input = document.getElementById('api-url-input');
    const resultBox = document.getElementById('api-test-result');
    if (!input || !resultBox) return;

    const testUrl = (input.value || '').trim().replace(/\/$/, '');
    resultBox.classList.remove('hidden', 'bg-emerald-950/60', 'border-emerald-600/40', 'text-emerald-300', 'bg-rose-950/60', 'border-rose-600/40', 'text-rose-300');
    resultBox.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Testing SIGNATURE VMAKE backend connection...';

    try {
        const resp = await fetch((testUrl || '') + '/api/v1/health');
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        resultBox.classList.add('bg-emerald-950/60', 'border-emerald-600/40', 'text-emerald-300');
        resultBox.innerHTML = `
            <div class="font-bold flex items-center gap-1.5"><i class="fa-solid fa-circle-check"></i> Connection Succeeded</div>
            <div class="text-[11px] text-emerald-200/80 mt-1">Status: ${data.status} | Service: ${data.service}</div>
            <div class="text-[11px] text-emerald-200/80 mono">Model: ${data.active_model ? data.active_model.name : 'Ready'}</div>
        `;
    } catch (err) {
        resultBox.classList.add('bg-rose-950/60', 'border-rose-600/40', 'text-rose-300');
        resultBox.innerHTML = `
            <div class="font-bold flex items-center gap-1.5"><i class="fa-solid fa-circle-xmark"></i> Connection Failed</div>
            <div class="text-[11px] text-rose-200/80 mt-1">${err.message || 'Could not connect to FastAPI server.'}</div>
        `;
    }
}

function saveApiUrl() {
    const input = document.getElementById('api-url-input');
    if (!input) return;
    const newBase = input.value.trim().replace(/\/$/, '');
    localStorage.setItem('vmake_api_base', newBase);
    API_BASE = newBase;
    closeApiConfigModal();
    window.location.reload();
}

// Global Search Modal placeholder
function openSearchModal() {
    const searchInput = document.getElementById('case-search-input');
    if (searchInput) {
        searchInput.focus();
        searchInput.scrollIntoView({ behavior: 'smooth' });
    } else {
        alert('SIGNATURE VMAKE Case Search: Please use the search input in the operations sidebar.');
    }
}
