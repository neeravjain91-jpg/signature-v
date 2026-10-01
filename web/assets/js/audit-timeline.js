/**
 * SIGNATURE VMAKE — Audit Trail & Timeline Logic
 */

async function fetchAuditTrailPage() {
    const txnRef = document.getElementById('lookup-txn-ref').value.trim();
    const container = document.getElementById('audit-trail-container');
    if (!txnRef || !container) return;

    container.innerHTML = `
        <div class="py-8 text-center text-muted">
            <i class="fa-solid fa-spinner fa-spin mr-2 text-brand"></i> Fetching non-repudiation audit trail for "${txnRef}"...
        </div>
    `;

    try {
        const data = await apiGet(`/api/v1/audit/trail/${encodeURIComponent(txnRef)}`);
        
        let historyHtml = '';
        if (data.verification_history && data.verification_history.length > 0) {
            historyHtml = data.verification_history.map((vh, i) => {
                const logsHtml = (vh.audit_logs && vh.audit_logs.length > 0)
                    ? vh.audit_logs.map(al => `
                        <div class="bg-surface p-2.5 rounded-md border border-border text-[11px] font-mono space-y-1">
                            <div class="flex justify-between items-center text-foreground">
                                <span class="font-bold text-brand">${al.action}</span>
                                <span class="${al.result === 'SUCCESS' ? 'badge-verified' : 'badge-review'} text-[10px]">${al.result}</span>
                            </div>
                            <div class="text-muted flex justify-between text-[10px]">
                                <span>Ref: ${al.request_reference || 'N/A'}</span>
                                <span>${formatDate(al.timestamp)}</span>
                            </div>
                        </div>
                    `).join('')
                    : '<p class="text-[11px] text-muted">No raw event logs</p>';

                const reviewsHtml = (vh.manual_reviews && vh.manual_reviews.length > 0)
                    ? vh.manual_reviews.map(mr => `
                        <div class="relative pl-5 border-l-2 border-warning/80 mt-2.5 space-y-1 bg-warning/5 p-3 rounded-r-md">
                            <div class="flex items-center gap-2">
                                <span class="badge-review text-[10px]">OFFICER SIGN-OFF</span>
                                <span class="font-semibold text-foreground text-xs">Decision: <span class="font-mono text-warning font-bold">${mr.decision}</span></span>
                            </div>
                            <p class="text-xs text-foreground/90">Commentary: "${mr.comment || 'Approved after document verification'}"</p>
                            <p class="text-[11px] text-muted font-mono">Reviewer: ${mr.reviewer} &bull; ${formatDate(mr.reviewed_at)}</p>
                        </div>
                    `).join('')
                    : '';

                const decBadge = vh.decision === 'VERIFIED' ? 'badge-verified' : (vh.decision === 'MANUAL_REVIEW' ? 'badge-review' : 'badge-blocked');

                return `
                    <div class="relative pl-6 border-l-2 border-border ml-3 space-y-3 pb-6">
                        <span class="absolute -left-[7px] top-0 w-3 h-3 rounded-full bg-brand"></span>
                        
                        <div class="flex flex-col sm:flex-row justify-between sm:items-center gap-1">
                            <p class="font-bold text-foreground text-sm flex items-center gap-2">
                                <span>Verification Attempt #${i + 1}</span>
                                <span class="${decBadge} text-[10px] font-mono">${vh.decision}</span>
                            </p>
                            <span class="font-mono text-[11px] text-muted">ID: ${vh.verification_id}</span>
                        </div>

                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs font-mono">
                            <div class="bg-surface p-2.5 rounded-md border border-border">
                                <span class="text-[10px] text-muted font-sans block">Similarity</span>
                                <span class="text-foreground font-bold text-sm">${formatScore(vh.similarity_score)}</span>
                            </div>
                            <div class="bg-surface p-2.5 rounded-md border border-border">
                                <span class="text-[10px] text-muted font-sans block">Threshold</span>
                                <span class="text-brand font-medium text-sm">${formatScore(vh.threshold_used)}</span>
                            </div>
                            <div class="bg-surface p-2.5 rounded-md border border-border">
                                <span class="text-[10px] text-muted font-sans block">Risk Score</span>
                                <span class="text-foreground font-bold text-sm">${vh.risk_assessment ? formatScore(vh.risk_assessment.overall_risk_score) : 'N/A'}</span>
                            </div>
                            <div class="bg-surface p-2.5 rounded-md border border-border">
                                <span class="text-[10px] text-muted font-sans block">Risk Level</span>
                                <span class="text-foreground font-sans font-medium text-xs">${vh.risk_assessment ? vh.risk_assessment.risk_level : 'STANDARD'}</span>
                            </div>
                        </div>

                        ${reviewsHtml}

                        <div class="space-y-1.5 pt-2">
                            <span class="text-[10px] font-semibold text-muted uppercase tracking-wider block">Tamper-Evident Audit Ledger Events:</span>
                            <div class="space-y-1.5">
                                ${logsHtml}
                            </div>
                        </div>
                    </div>
                `;
            }).join('');
        } else {
            historyHtml = '<p class="text-muted pl-4 py-4 text-xs">No verification history recorded for this voucher yet.</p>';
        }

        const statusBadge = data.current_status === 'VERIFIED' ? 'badge-verified' : 'badge-review';

        container.innerHTML = `
            <div class="bg-surface p-4 rounded-lg border border-border flex flex-col sm:flex-row justify-between sm:items-center gap-2">
                <div class="flex items-center space-x-3 text-xs">
                    <span class="text-muted font-medium">Voucher Reference:</span>
                    <span class="font-mono font-bold text-foreground text-sm">${data.transaction_reference}</span>
                    <span class="${statusBadge} text-[10px] font-mono">
                        ${data.current_status}
                    </span>
                </div>
                <div class="text-xs text-muted font-mono">
                    Amount: <strong class="text-foreground">${formatCurrency(data.amount, data.currency)}</strong> &bull; Channel: <strong>${data.type}</strong>
                </div>
            </div>

            <div class="mt-6 space-y-4">
                ${historyHtml}
            </div>
        `;
    } catch (e) {
        container.innerHTML = `
            <div class="p-6 rounded-lg border border-danger/30 bg-danger/5 text-center text-xs text-danger">
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
    if (typeof renderPrimaryRail === 'function') {
        renderPrimaryRail('audit');
    }
    if (typeof renderTopBar === 'function') {
        renderTopBar('Compliance / Forensic Audit Trail / Non-Repudiation Ledger');
    }
    await checkBackendHealth();
    await fetchAuditTrailPage();
});
