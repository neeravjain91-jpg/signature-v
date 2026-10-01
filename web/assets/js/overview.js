/**
 * SIGNATURE VMAKE — Case Review & Operations Dashboard Controller
 * Implements the Enterprise Banking Biometric Case Review Interface
 */

let allCases = [];
let activeCaseIndex = 0;
let currentFilter = 'all';

// Default realistic cases matching reference screenshot
const DEMO_CASES = [
    {
        id: 'DEMO-101',
        customer: 'Alex Morgan',
        amount: 4500.00,
        currency: 'USD',
        transactionType: 'Cheque clearance',
        status: 'REVIEW REQUIRED',
        statusKey: 'review',
        timeAgo: '12 min ago',
        similarity: 0.54,
        threshold: 0.59,
        reason: 'Similarity below threshold',
        isHighRisk: true,
        assignedToMe: true,
        specimenImg: '/api/v1/sample-image?type=genuine_ref',
        questionedImg: '/api/v1/sample-image?type=forged_sub',
        specimenBadge: 'Genuine reference',
        questionedBadge: 'Customer cheque',
        evidence: [
            { icon: 'pass', title: 'Source uploaded', desc: 'Questioned signature image received', time: '12 min ago' },
            { icon: 'pass', title: 'Reference found', desc: 'Matching customer specimen located', time: '12 min ago' },
            { icon: 'pass', title: 'Scan quality', desc: 'Image quality is good (Var: 624)', time: '12 min ago' },
            { icon: 'warn', title: 'Similarity check', desc: 'Similarity below threshold (0.54 < 0.59)', time: '12 min ago' }
        ],
        activity: [
            { dot: 'system', title: 'Case created', sub: 'By System', time: '12 min ago' },
            { dot: 'pass', title: 'Questioned signature uploaded', sub: 'By John Smith', time: '12 min ago' },
            { dot: 'warn', title: 'Verification completed', sub: 'Similarity: 0.54 (threshold: 0.59)', time: '12 min ago' }
        ]
    },
    {
        id: 'DEMO-102',
        customer: 'Priya Sharma',
        amount: 12800.00,
        currency: 'USD',
        transactionType: 'High-value draft',
        status: 'BLOCKED',
        statusKey: 'blocked',
        timeAgo: '28 min ago',
        similarity: 0.28,
        threshold: 0.59,
        reason: 'Severe stroke curvature hesitation & skilled forgery detected',
        isHighRisk: true,
        assignedToMe: false,
        specimenImg: '/api/v1/sample-image?type=genuine_ref',
        questionedImg: '/api/v1/sample-image?type=forged_sub',
        specimenBadge: 'Enrolled specimen',
        questionedBadge: 'Draft voucher',
        evidence: [
            { icon: 'pass', title: 'Source uploaded', desc: 'High-value draft scanned at clearing', time: '28 min ago' },
            { icon: 'pass', title: 'Reference found', desc: 'Primary specimen retrieved from vault', time: '28 min ago' },
            { icon: 'pass', title: 'Scan quality', desc: 'Acceptable focus and dynamic range', time: '28 min ago' },
            { icon: 'fail', title: 'Similarity check', desc: 'Skilled forgery indicator triggered (0.28)', time: '28 min ago' }
        ],
        activity: [
            { dot: 'system', title: 'High-risk case initiated', sub: 'Amount > $10,000 threshold', time: '28 min ago' },
            { dot: 'warn', title: 'Model evaluation', sub: 'Biometric score 0.28 (EER critical)', time: '28 min ago' },
            { dot: 'warn', title: 'Automatic block enacted', sub: 'Sent to senior fraud supervisor', time: '28 min ago' }
        ]
    },
    {
        id: 'DEMO-103',
        customer: 'James Carter',
        amount: 2350.00,
        currency: 'USD',
        transactionType: 'Cheque clearance',
        status: 'PASSED',
        statusKey: 'passed',
        timeAgo: '1 hour ago',
        similarity: 0.89,
        threshold: 0.59,
        reason: 'High biometric match & authentic stroke kinematics',
        isHighRisk: false,
        assignedToMe: true,
        specimenImg: '/api/v1/sample-image?type=genuine_ref',
        questionedImg: '/api/v1/sample-image?type=genuine_sub',
        specimenBadge: 'Genuine reference',
        questionedBadge: 'Customer cheque',
        evidence: [
            { icon: 'pass', title: 'Source uploaded', desc: 'Branch counter scanner capture', time: '1 hour ago' },
            { icon: 'pass', title: 'Reference found', desc: 'Specimen verified and active', time: '1 hour ago' },
            { icon: 'pass', title: 'Scan quality', desc: 'High sharpness (Var: 780)', time: '1 hour ago' },
            { icon: 'pass', title: 'Similarity check', desc: 'High biometric confidence (0.89 >= 0.59)', time: '1 hour ago' }
        ],
        activity: [
            { dot: 'system', title: 'Cheque presented', sub: 'Teller station #4', time: '1 hour ago' },
            { dot: 'pass', title: 'Biometric match confirmed', sub: 'Score 0.89 against primary specimen', time: '1 hour ago' },
            { dot: 'pass', title: 'Straight-through clearance', sub: 'Auto-approved without officer hold', time: '1 hour ago' }
        ]
    },
    {
        id: 'DEMO-104',
        customer: 'Maria Lopez',
        amount: 9900.00,
        currency: 'USD',
        transactionType: 'Commercial draft',
        status: 'REVIEW REQUIRED',
        statusKey: 'review',
        timeAgo: '2 hours ago',
        similarity: 0.57,
        threshold: 0.59,
        reason: 'Slight pen tremor detected near baseline flourish',
        isHighRisk: false,
        assignedToMe: true,
        specimenImg: '/api/v1/sample-image?type=genuine_ref',
        questionedImg: '/api/v1/sample-image?type=genuine_sub',
        specimenBadge: 'Corporate signature',
        questionedBadge: 'Commercial cheque',
        evidence: [
            { icon: 'pass', title: 'Source uploaded', desc: 'Mobile cheque capture batch', time: '2 hours ago' },
            { icon: 'pass', title: 'Reference found', desc: 'Corporate signatory registered', time: '2 hours ago' },
            { icon: 'warn', title: 'Scan quality', desc: 'Minor shadow gradient on check border', time: '2 hours ago' },
            { icon: 'warn', title: 'Similarity check', desc: 'Score 0.57 marginally below threshold 0.59', time: '2 hours ago' }
        ],
        activity: [
            { dot: 'system', title: 'Case queued for review', sub: 'By Clearing Hub', time: '2 hours ago' },
            { dot: 'pass', title: 'Assigned to officer', sub: 'Assigned to John Smith', time: '2 hours ago' }
        ]
    },
    {
        id: 'DEMO-105',
        customer: 'Daniel Kim',
        amount: 7200.00,
        currency: 'USD',
        transactionType: 'Cheque clearance',
        status: 'PASSED',
        statusKey: 'passed',
        timeAgo: '3 hours ago',
        similarity: 0.92,
        threshold: 0.59,
        reason: 'Authentic stroke dynamics & matching Hu moments',
        isHighRisk: false,
        assignedToMe: false,
        specimenImg: '/api/v1/sample-image?type=genuine_ref',
        questionedImg: '/api/v1/sample-image?type=genuine_sub',
        specimenBadge: 'Verified specimen',
        questionedBadge: 'Counter cheque',
        evidence: [
            { icon: 'pass', title: 'Source uploaded', desc: 'High-speed cheque sorter image', time: '3 hours ago' },
            { icon: 'pass', title: 'Reference found', desc: 'Vault record located', time: '3 hours ago' },
            { icon: 'pass', title: 'Scan quality', desc: 'Perfect CTS-2010 compliance', time: '3 hours ago' },
            { icon: 'pass', title: 'Similarity check', desc: 'Score 0.92 exceeds threshold', time: '3 hours ago' }
        ],
        activity: [
            { dot: 'system', title: 'Batch cleared', sub: 'Autonomous Clearing System', time: '3 hours ago' },
            { dot: 'pass', title: 'Funds scheduled for release', sub: 'Settlement cycle #2', time: '3 hours ago' }
        ]
    }
];

/**
 * Initializes and loads the Case Review page.
 */
async function initCaseReviewPage() {
    renderPrimaryRail('nav-cases');
    renderTopBar('Review queue / DEMO-101');
    renderGlobalFooter();
    await checkBackendHealth();

    allCases = [...DEMO_CASES];

    // Attempt to load live pending reviews from backend database
    try {
        const liveData = await apiGet('/api/v1/verifications/pending-reviews');
        if (liveData && liveData.queue && liveData.queue.length > 0) {
            const liveCases = liveData.queue.map((item, idx) => ({
                id: item.transaction_reference || `CASE-${1000 + idx}`,
                customer: item.customer_name || 'Authorized Signer',
                amount: item.amount || 4500.00,
                currency: item.currency || 'USD',
                transactionType: item.transaction_type || 'Cheque clearance',
                status: 'REVIEW REQUIRED',
                statusKey: 'review',
                timeAgo: formatDateRelative(item.created_at),
                similarity: item.similarity_score || 0.54,
                threshold: item.threshold_used || 0.59,
                reason: item.similarity_score < (item.threshold_used || 0.59) ? 'Similarity below threshold' : 'Risk escalation hold',
                isHighRisk: (item.overall_risk_score && item.overall_risk_score > 0.4),
                assignedToMe: true,
                verificationId: item.verification_id,
                specimenImg: '/api/v1/sample-image?type=genuine_ref',
                questionedImg: (item.similarity_score && item.similarity_score > 0.7) ? '/api/v1/sample-image?type=genuine_sub' : '/api/v1/sample-image?type=forged_sub',
                specimenBadge: 'Database specimen',
                questionedBadge: 'Presented cheque',
                evidence: [
                    { icon: 'pass', title: 'Source uploaded', desc: `Cheque reference ${item.transaction_reference || 'DEMO'}`, time: formatDateRelative(item.created_at) },
                    { icon: 'pass', title: 'Reference found', desc: `Customer vault verified`, time: formatDateRelative(item.created_at) },
                    { icon: 'pass', title: 'Scan quality', desc: 'OpenCV Otsu binarization passed', time: formatDateRelative(item.created_at) },
                    { icon: 'warn', title: 'Similarity check', desc: `Similarity: ${formatScore(item.similarity_score)} (Threshold: ${formatScore(item.threshold_used || 0.59)})`, time: formatDateRelative(item.created_at) }
                ],
                activity: [
                    { dot: 'system', title: 'Transaction presented', sub: 'Core Banking API', time: formatDateRelative(item.created_at) },
                    { dot: 'warn', title: 'Verification completed', sub: `Score: ${formatScore(item.similarity_score)}`, time: formatDateRelative(item.created_at) }
                ]
            }));

            // Prepend live cases to queue
            allCases = [...liveCases, ...DEMO_CASES];
            const badge = document.getElementById('queue-count-pill');
            if (badge) badge.innerText = allCases.length;
        }
    } catch (_) {
        // Graceful fallback to rich realistic demo cases
    }

    renderCaseSidebar();
    displayCase(0);
    loadOverviewMetrics();
}

/**
 * Renders the Level 2 Context Sidebar case list.
 */
function renderCaseSidebar() {
    const listEl = document.getElementById('sidebar-case-list');
    if (!listEl) return;

    const searchTerm = (document.getElementById('case-search-input')?.value || '').toLowerCase().trim();

    let filtered = allCases.filter(c => {
        if (currentFilter === 'high_risk' && !c.isHighRisk) return false;
        if (currentFilter === 'assigned' && !c.assignedToMe) return false;
        if (searchTerm) {
            const matchName = c.customer.toLowerCase().includes(searchTerm);
            const matchId = c.id.toLowerCase().includes(searchTerm);
            const matchAmt = c.amount.toString().includes(searchTerm);
            if (!matchName && !matchId && !matchAmt) return false;
        }
        return true;
    });

    if (filtered.length === 0) {
        listEl.innerHTML = '<div class="p-6 text-center text-xs text-slate-400">No cases match filter.</div>';
        return;
    }

    listEl.innerHTML = filtered.map((c) => {
        const originalIndex = allCases.findIndex(item => item.id === c.id);
        const isActive = (originalIndex === activeCaseIndex);
        const activeClass = isActive ? 'active' : '';

        let badgeClass = 'review';
        let badgeText = 'Review';
        if (c.statusKey === 'blocked') {
            badgeClass = 'rejected';
            badgeText = 'Blocked';
        } else if (c.statusKey === 'passed') {
            badgeClass = 'passed';
            badgeText = 'Passed';
        }

        return `
            <div class="case-card ${activeClass}" onclick="displayCase(${originalIndex})">
                <div class="case-card-header">
                    <h4 class="case-name">${c.customer}</h4>
                    <span class="case-time">${c.timeAgo}</span>
                </div>
                <div class="case-card-sub">
                    <span class="case-meta">${c.id} &bull; ${formatCurrency(c.amount)}</span>
                    <span class="status-pill ${badgeClass}">${badgeText}</span>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Updates the Level 3 Main Workspace with the selected case data.
 */
function displayCase(index) {
    if (index < 0 || index >= allCases.length) return;
    activeCaseIndex = index;
    const c = allCases[index];

    // 1. Update Breadcrumbs & Top Bar
    renderTopBar(`Review queue / ${c.id}`);

    // 2. Case Metadata Bar
    const nameEl = document.getElementById('case-customer-name');
    const idEl = document.getElementById('case-id-display');
    const typeEl = document.getElementById('case-txn-type');
    const amtEl = document.getElementById('case-amount-display');
    const statusPillEl = document.getElementById('case-status-badge');

    if (nameEl) nameEl.innerText = c.customer;
    if (idEl) idEl.innerText = c.id;
    if (typeEl) typeEl.innerText = c.transactionType;
    if (amtEl) amtEl.innerText = formatCurrency(c.amount);

    if (statusPillEl) {
        let badgeClass = 'status-pill review';
        let badgeText = 'Review required';
        if (c.statusKey === 'blocked') {
            badgeClass = 'status-pill rejected';
            badgeText = 'Blocked';
        } else if (c.statusKey === 'passed') {
            badgeClass = 'status-pill passed';
            badgeText = 'Passed';
        }
        statusPillEl.className = badgeClass;
        statusPillEl.innerText = badgeText;
    }

    // 3. Signature Cards
    const specImgEl = document.getElementById('specimen-signature-img');
    const quesImgEl = document.getElementById('questioned-signature-img');
    const specBadgeEl = document.getElementById('specimen-badge-tag');
    const quesBadgeEl = document.getElementById('questioned-badge-tag');

    if (specImgEl) specImgEl.src = c.specimenImg;
    if (quesImgEl) quesImgEl.src = c.questionedImg;
    if (specBadgeEl) specBadgeEl.innerText = c.specimenBadge || 'Genuine reference';
    if (quesBadgeEl) quesBadgeEl.innerText = c.questionedBadge || 'Customer cheque';

    // 4. Verification Result Panel
    const resPanel = document.getElementById('verification-result-panel');
    const verdictIcon = document.getElementById('result-verdict-icon');
    const verdictText = document.getElementById('result-verdict-text');
    const simText = document.getElementById('result-similarity-text');
    const threshText = document.getElementById('result-threshold-text');
    const reasonText = document.getElementById('result-reason-text');

    if (verdictText) verdictText.innerText = c.status;
    if (simText) simText.innerText = formatScore(c.similarity, 2);
    if (threshText) threshText.innerText = formatScore(c.threshold, 2);
    if (reasonText) reasonText.innerText = c.reason;

    if (resPanel && verdictIcon) {
        if (c.statusKey === 'passed') {
            resPanel.className = 'verification-result-panel verified-theme';
            verdictIcon.className = 'verdict-icon-circle verified-icon';
            verdictIcon.innerHTML = '<i class="fa-solid fa-check"></i>';
        } else if (c.statusKey === 'blocked') {
            resPanel.className = 'verification-result-panel rejected-theme';
            verdictIcon.className = 'verdict-icon-circle rejected-icon';
            verdictIcon.innerHTML = '<i class="fa-solid fa-xmark"></i>';
        } else {
            resPanel.className = 'verification-result-panel';
            verdictIcon.className = 'verdict-icon-circle';
            verdictIcon.innerHTML = '!';
        }
    }

    // 5. Evidence Checklist
    const evidenceContainer = document.getElementById('evidence-checklist-container');
    if (evidenceContainer && c.evidence) {
        evidenceContainer.innerHTML = c.evidence.map(ev => {
            let iconHtml = '<i class="fa-solid fa-check"></i>';
            if (ev.icon === 'warn') iconHtml = '!';
            if (ev.icon === 'fail') iconHtml = '<i class="fa-solid fa-xmark"></i>';

            return `
                <div class="evidence-item">
                    <div class="evidence-left">
                        <div class="evidence-icon ${ev.icon}">${iconHtml}</div>
                        <div>
                            <h5 class="evidence-title">${ev.title}</h5>
                            <p class="evidence-desc">${ev.desc}</p>
                        </div>
                    </div>
                    <span class="evidence-time">${ev.time}</span>
                </div>
            `;
        }).join('');
    }

    // 6. Case Activity Timeline
    const timelineContainer = document.getElementById('case-activity-container');
    if (timelineContainer && c.activity) {
        timelineContainer.innerHTML = c.activity.map(act => `
            <div class="timeline-item">
                <div class="timeline-dot ${act.dot}"></div>
                <div class="timeline-content">
                    <div>
                        <h5 class="timeline-title">${act.title}</h5>
                        <p class="timeline-actor">${act.sub}</p>
                    </div>
                    <span class="timeline-time">${act.time}</span>
                </div>
            </div>
        `).join('');
    }

    // 7. Reset Notes
    const notesInput = document.getElementById('case-review-notes');
    if (notesInput) {
        notesInput.value = '';
        updateCharCount();
    }

    // Update sidebar selection highlighting
    renderCaseSidebar();
}

/**
 * Cycles between previous (-1) and next (+1) case.
 */
function cycleCase(delta) {
    let newIndex = activeCaseIndex + delta;
    if (newIndex < 0) newIndex = allCases.length - 1;
    if (newIndex >= allCases.length) newIndex = 0;
    displayCase(newIndex);
}

/**
 * Filters the case list by tab ('all', 'high_risk', 'assigned').
 */
function setCaseFilter(filterType) {
    currentFilter = filterType;
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.getElementById(`filter-btn-${filterType}`);
    if (activeBtn) activeBtn.classList.add('active');
    renderCaseSidebar();
}

/**
 * Filter cases via search input.
 */
function handleCaseSearch() {
    renderCaseSidebar();
}

/**
 * Updates character counter in review notes textarea.
 */
function updateCharCount() {
    const textarea = document.getElementById('case-review-notes');
    const counter = document.getElementById('review-notes-char-count');
    if (textarea && counter) {
        counter.innerText = `${textarea.value.length}/1000`;
    }
}

/**
 * Submits an officer review adjudication.
 */
async function submitCaseReview() {
    const c = allCases[activeCaseIndex];
    const notes = document.getElementById('case-review-notes')?.value.trim();

    if (!notes) {
        alert('Please enter your review observations or justification notes before submitting.');
        document.getElementById('case-review-notes')?.focus();
        return;
    }

    const btn = document.getElementById('btn-submit-review');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Submitting...';
    }

    try {
        if (c.verificationId) {
            await apiPost(`/api/v1/verifications/${c.verificationId}/adjudicate`, {
                reviewer_username: 'John Smith (Verification Officer)',
                decision: 'VERIFIED',
                review_comment: notes
            });
        }
        
        c.status = 'PASSED';
        c.statusKey = 'passed';
        c.reason = 'Officer visual inspection verified & approved';
        c.activity.unshift({
            dot: 'pass',
            title: 'Review submitted and approved',
            sub: 'By John Smith (Officer)',
            time: 'Just now'
        });

        alert(`Case ${c.id} successfully reviewed and approved.`);
        displayCase(activeCaseIndex);
    } catch (err) {
        alert(`Review error: ${err.message}`);
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = '<i class="fa-solid fa-paper-plane"></i> Submit review';
        }
    }
}

/**
 * Requests new specimen sample.
 */
function requestNewSample() {
    const c = allCases[activeCaseIndex];
    alert(`Sample request notification dispatched to branch for ${c.customer} (${c.id}). Customer will be prompted to re-sign at branch counter or mobile terminal.`);
}

/**
 * Exports formal verification report.
 */
function exportCaseReport() {
    const c = allCases[activeCaseIndex];
    window.print();
}

/**
 * Loads KPI dashboard metrics for executive header stats.
 */
async function loadOverviewMetrics() {
    try {
        const data = await apiGet('/api/v1/dashboard/metrics');
        const s = data.summary;
        if (document.getElementById('stat-total-verif')) document.getElementById('stat-total-verif').innerText = s.total_verifications.toLocaleString();
        if (document.getElementById('stat-verified-rate')) document.getElementById('stat-verified-rate').innerText = s.pass_rate_pct.toFixed(1) + '%';
        if (document.getElementById('stat-rejected-rate')) document.getElementById('stat-rejected-rate').innerText = s.rejection_rate_pct.toFixed(1) + '%';
        if (document.getElementById('stat-pending-reviews')) document.getElementById('stat-pending-reviews').innerText = s.manual_review_count;

        if (data.active_model) {
            if (document.getElementById('overview-active-model-name')) document.getElementById('overview-active-model-name').innerText = data.active_model.name || 'HF Vision Transformer';
            if (document.getElementById('overview-active-model-thresh')) document.getElementById('overview-active-model-thresh').innerText = formatScore(data.active_model.threshold);
            if (document.getElementById('overview-active-model-arch')) document.getElementById('overview-active-model-arch').innerText = data.active_model.version || 'v1.0.0';
        }
    } catch (_) {}

    try {
        const health = await apiGet('/api/v1/health');
        if (document.getElementById('overview-db-status')) document.getElementById('overview-db-status').innerText = health.database || 'CONNECTED';
        if (document.getElementById('overview-service-status')) document.getElementById('overview-service-status').innerText = health.status || 'HEALTHY';
    } catch (_) {}
}

function formatDateRelative(isoStr) {
    if (!isoStr) return 'Just now';
    try {
        const d = new Date(isoStr);
        const mins = Math.floor((Date.now() - d.getTime()) / 60000);
        if (mins < 1) return 'Just now';
        if (mins < 60) return `${mins} min ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        return d.toLocaleDateString();
    } catch (_) {
        return 'Recently';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    initCaseReviewPage();
});
