/**
 * SIGNATURE VMAKE — Cheque Verification Studio Logic
 */

let currentPreset = 'genuine';

function loadPreset(type) {
    currentPreset = type;
    const amountInput = document.getElementById('input-amount');
    const typeInput = document.getElementById('input-type');
    const previewRef = document.getElementById('preview-ref');
    const previewSub = document.getElementById('preview-sub');
    const subBadge = document.getElementById('label-sub-badge');
    const subType = document.getElementById('label-sub-type');

    if (type === 'genuine') {
        amountInput.value = '4500.00';
        typeInput.value = 'CHEQUE';
        previewRef.src = `${API_BASE}/api/v1/sample-image?type=genuine_ref`;
        previewSub.src = `${API_BASE}/api/v1/sample-image?type=genuine_sub`;
        if (subBadge) {
            subBadge.className = 'text-[9px] px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800';
            subBadge.innerText = 'Genuine Sample';
        }
        if (subType) subType.innerText = 'Questioned Voucher (Genuine)';
    } else {
        amountInput.value = '15000.00';
        typeInput.value = 'WITHDRAWAL';
        previewRef.src = `${API_BASE}/api/v1/sample-image?type=genuine_ref`;
        previewSub.src = `${API_BASE}/api/v1/sample-image?type=forged_sub`;
        if (subBadge) {
            subBadge.className = 'text-[9px] px-1.5 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800';
            subBadge.innerText = 'Skilled Forgery';
        }
        if (subType) subType.innerText = 'Questioned Voucher (Forgery)';
    }
}

async function executeChequeVerification() {
    const btn = document.getElementById('btn-verify');
    const originalBtnHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Biometric & Fraud Risk Engine...';
    btn.disabled = true;

    try {
        const amount = parseFloat(document.getElementById('input-amount').value);
        const txnType = document.getElementById('input-type').value;
        const modelTrackEl = document.getElementById('select-model-track');
        const modelTrack = modelTrackEl ? modelTrackEl.value : 'transformer';

        const payload = {
            amount: amount,
            transaction_type: txnType,
            sample_type: currentPreset,
            transaction_reference: 'DEMO-TXN-CHEQUE-101',
            model_track: modelTrack
        };

        const data = await apiPost('/api/v1/verifications/verify-demo', payload);
        renderChequeResults(data);
    } catch (err) {
        alert(`Verification Error: ${err.message || 'API connection failed'}`);
        const badge = document.getElementById('decision-badge');
        if (badge) {
            badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800';
            badge.innerText = 'VERIFICATION FAILED';
        }
    } finally {
        btn.innerHTML = originalBtnHtml;
        btn.disabled = false;
    }
}

function renderChequeResults(data) {
    document.getElementById('res-similarity').innerText = formatScore(data.similarity_score);
    document.getElementById('res-distance').innerText = formatScore(data.euclidean_distance);
    document.getElementById('res-overall-risk').innerText = formatScore(data.overall_risk_score);
    document.getElementById('res-risk-tier').innerText = `Tier: ${data.risk_level || 'STANDARD'}`;
    document.getElementById('trace-id').innerText = data.request_reference || 'N/A';

    if (data.threshold_used) {
        const threshEl = document.getElementById('active-threshold-val');
        if (threshEl) threshEl.innerText = formatScore(data.threshold_used);
    }

    const badge = document.getElementById('decision-badge');
    if (badge) {
        if (data.decision === 'VERIFIED') {
            badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800';
            badge.innerText = 'VERIFIED (AUTONOMOUS SETTLEMENT)';
        } else if (data.decision === 'MANUAL_REVIEW') {
            badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-amber-950 text-amber-400 border border-amber-800';
            badge.innerText = 'MANUAL REVIEW (OFFICER ESCALATION)';
        } else {
            badge.className = 'px-3 py-1 rounded-full text-xs font-bold bg-rose-950 text-rose-400 border border-rose-800';
            badge.innerText = 'REJECTED (FRAUD BLOCKED)';
        }
    }

    // Decomposition progress bars
    const simComp = data.similarity_component !== undefined ? Number(data.similarity_component) : Math.max(0, 1 - Number(data.similarity_score));
    const simPct = Math.min(100, Math.max(0, simComp * 100));
    document.getElementById('bar-val-sim').innerText = simComp.toFixed(4);
    document.getElementById('bar-fill-sim').style.width = simPct + '%';

    const qualComp = data.image_quality_component !== undefined ? Number(data.image_quality_component) : 0.08;
    const qualPct = Math.min(100, Math.max(0, qualComp * 100));
    document.getElementById('bar-val-quality').innerText = qualComp.toFixed(4);
    document.getElementById('bar-fill-quality').style.width = qualPct + '%';

    const txnComp = data.transaction_risk_component !== undefined ? Number(data.transaction_risk_component) : 0.20;
    const txnPct = Math.min(100, Math.max(0, txnComp * 100));
    document.getElementById('bar-val-txn').innerText = txnComp.toFixed(4);
    document.getElementById('bar-fill-txn').style.width = txnPct + '%';

    // Explainable Audit Rationale Codes from Backend
    const tagContainer = document.getElementById('factor-tags');
    if (tagContainer) {
        if (data.risk_factors && data.risk_factors.length > 0) {
            tagContainer.innerHTML = data.risk_factors.map(f => {
                const isSevere = f.code.includes('SEVERE') || f.code.includes('POOR') || f.code.includes('FRAUD') || f.code.includes('IRREVERSIBLE');
                const isWarn = f.code.includes('BORDERLINE') || f.code.includes('HIGH_VALUE');
                const cls = isSevere ? 'bg-rose-950/80 text-rose-400 border-rose-800' :
                            isWarn ? 'bg-amber-950/80 text-amber-400 border-amber-800' :
                            'bg-emerald-950/80 text-emerald-400 border-emerald-800';
                return `<span title="${f.description}" class="px-2.5 py-1 rounded-md border text-xs cursor-help ${cls}">${f.code}</span>`;
            }).join('');
        } else if (data.decision === 'VERIFIED') {
            tagContainer.innerHTML = '<span class="px-2.5 py-1 rounded-md bg-emerald-950/80 text-emerald-400 border border-emerald-800">AUTHENTIC_STROKE_CORRELATION</span>';
        } else {
            tagContainer.innerHTML = '<span class="px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 border border-slate-700">NO_ABNORMAL_FACTORS</span>';
        }
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    renderGlobalNavigation('nav-studio');
    renderGlobalFooter();
    await checkBackendHealth();
    loadPreset('genuine');
});
