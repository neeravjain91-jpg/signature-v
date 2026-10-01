/**
 * SIGNATURE VMAKE — Audit Trail & Timeline Logic
 */

async function fetchAuditTrailPage() {
    const txnRef = document.getElementById('lookup-txn-ref').value.trim();
    const container = document.getElementById('audit-trail-container');
    if (!txnRef || !container) return;

    container.innerHTML = `
        <div class="py-8 text-center text-slate-500">
            <i class="fa-solid fa-spinner fa-spin mr-2 text-cyan-400"></i> Fetching non-repudiation audit trail for "${txnRef}"...
        </div>
    `;

    try {
        const data = await apiGet(`/api/v1/audit/trail/${encodeURIComponent(txnRef)}`);
        
        let historyHtml = '';
        if (data.verification_history && data.verification_history.length > 0) {
            historyHtml = data.verification_history.map((vh, i) => {
                const logsHtml = (vh.audit_logs && vh.audit_logs.length > 0)
                    ? vh.audit_logs.map(al => `
                        <div class="bg-slate-950/80 p-2.5 rounded-lg border border-slate-800 text-[11px] font-mono space-y-0.5">
                            <div class="flex justify-between text-slate-300">
                                <span class="font-bold text-cyan-400">${al.action}</span>
                                <span class="px-1.5 py-0.2 rounded text-[10px] ${al.result === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400' : 'bg-amber-950 text-amber-400'}">${al.result}</span>
                            </div>
                            <div class="text-slate-400 flex justify-between">
                                <span>Ref: ${al.request_reference || 'N/A'}</span>
                                <span>${formatDate(al.timestamp)}</span>
                            </div>
                        </div>
                    `).join('')
                    : '<p class="text-[11px] text-slate-500">No raw event logs</p>';

                const reviewsHtml = (vh.manual_reviews && vh.manual_reviews.length > 0)
                    ? vh.manual_reviews.map(mr => `
                        <div class="relative pl-6 border-l-2 border-amber-500/50 mt-2 space-y-1">
                            <span class="absolute -left-[7px] top-1.5 w-3 h-3 rounded-full bg-amber-400"></span>
                            <p class="font-semibold text-white text-xs">Officer Review Adjudication: <span class="mono text-amber-400 font-bold">${mr.decision}</span></p>
                            <p class="text-xs text-slate-300">Commentary: "${mr.comment || 'Approved after document verification'}"</p>
                            <p class="text-[10px] text-slate-500">Reviewer: ${mr.reviewer} &bull; ${formatDate(mr.reviewed_at)}</p>
                        </div>
                    `).join('')
                    : '';

                return `
                    <div class="relative pl-6 border-l-2 border-slate-800 ml-4 space-y-3 pb-6">
                        <span class="absolute -left-[7px] top-0 w-3 h-3 rounded-full bg-cyan-500"></span>
                        
                        <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-1">
                            <p class="font-bold text-white text-sm">
                                Verification Attempt #${i + 1} &bull; Decision: 
                                <span class="mono ${vh.decision === 'VERIFIED' ? 'text-emerald-400' : (vh.decision === 'MANUAL_REVIEW' ? 'text-amber-400' : 'text-rose-400')}">
                                    ${vh.decision}
                                </span>
                            </p>
                            <span class="mono text-[11px] text-slate-500">ID: ${vh.verification_id}</span>
                        </div>

                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                                <span class="text-[10px] text-slate-400 font-sans block">Similarity</span>
                                <span class="text-white font-bold">${formatScore(vh.similarity_score)}</span>
                            </div>
                            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                                <span class="text-[10px] text-slate-400 font-sans block">Threshold</span>
                                <span class="text-cyan-400">${formatScore(vh.threshold_used)}</span>
                            </div>
                            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                                <span class="text-[10px] text-slate-400 font-sans block">Risk Score</span>
                                <span class="text-amber-400">${vh.risk_assessment ? formatScore(vh.risk_assessment.overall_risk_score) : 'N/A'}</span>
                            </div>
                            <div class="bg-slate-950 p-2 rounded-lg border border-slate-800">
                                <span class="text-[10px] text-slate-400 font-sans block">Risk Level</span>
                                <span class="text-slate-300 font-sans">${vh.risk_assessment ? vh.risk_assessment.risk_level : 'STANDARD'}</span>
                            </div>
                        </div>

                        ${reviewsHtml}

                        <div class="space-y-1.5 pt-2">
                            <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Tamper-Evident Audit Ledger Events:</span>
                            <div class="space-y-1.5">
                                ${logsHtml}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            historyHtml = '<p class="text-slate-500 pl-4 py-4 text-xs">No verification history recorded for this voucher yet.</p>';
        }

        container.innerHTML = `
            <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                <div class="flex items-center space-x-3 text-xs">
                    <span class="text-slate-400 font-medium">Voucher:</span>
                    <span class="mono font-bold text-white text-sm">${data.transaction_reference}</span>
                    <span class="text-[10px] px-2 py-0.5 rounded font-bold ${data.current_status === 'VERIFIED' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'}">
                        ${data.current_status}
                    </span>
                </div>
                <div class="text-xs text-slate-400 mono">
                    Amount: <strong class="text-white">${formatCurrency(data.amount, data.currency)}</strong> &bull; Type: <strong>${data.type}</strong>
                </div>
            </div>

            <div class="mt-6 space-y-4">
                ${historyHtml}
            </div>
        `;
    } catch (e) {
        container.innerHTML = `
            <div class="p-6 rounded-xl border border-rose-900/60 bg-rose-950/20 text-center text-xs text-rose-400">
                <i class="fa-solid fa-triangle-exclamation text-base mb-1 block"></i>
                Audit Lookup Error: ${e.message || 'Transaction not found'}
            </div>
        `;
    }
}

function setAuditLookupPreset(ref) {
    document.getElementById('lookup-txn-ref').value = ref;
    fetchAuditTrailPage();
}

window.addEventListener('DOMContentLoaded', async () => {
    renderGlobalNavigation('nav-audit');
    renderGlobalFooter();
    await checkBackendHealth();
    await fetchAuditTrailPage();
});
