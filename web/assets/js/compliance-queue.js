/**
 * SIGNATURE VMAKE — Compliance Officer Adjudication Queue Logic
 */

let currentVerificationId = null;

async function loadPendingReviewsPage() {
    const tableBody = document.getElementById('queue-table-body');
    const countBadge = document.getElementById('queue-count-badge');
    if (!tableBody) return;

    try {
        const data = await apiGet('/api/v1/verifications/pending-reviews');
        if (countBadge) countBadge.innerText = `${data.pending_reviews_count || 0} Pending Case(s)`;

        if (!data.queue || data.queue.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="8" class="py-8 text-center text-muted font-medium">No pending transactions currently requiring officer adjudication.</td></tr>';
            return;
        }

        tableBody.innerHTML = data.queue.map(item => `
            <tr class="hover:bg-surface font-mono text-xs transition">
                <td class="py-3.5 px-4 text-brand font-semibold">${item.transaction_reference}</td>
                <td class="py-3.5 px-4 text-foreground font-medium font-sans">${item.customer_name}</td>
                <td class="py-3.5 px-4 text-foreground font-bold">${formatCurrency(item.amount)}</td>
                <td class="py-3.5 px-4 text-foreground">${formatScore(item.similarity_score)}</td>
                <td class="py-3.5 px-4">
                    <span class="badge-review font-sans">
                        ${formatScore(item.overall_risk_score)} (${item.risk_level || 'ESCALATED'})
                    </span>
                </td>
                <td class="py-3.5 px-4 text-muted font-sans">Biometric or monetary threshold escalation</td>
                <td class="py-3.5 px-4 text-muted text-[11px]">${formatDate(item.created_at)}</td>
                <td class="py-3.5 px-4 text-right">
                    <button onclick="openReviewModal('${item.transaction_reference}', '${item.customer_name}', ${item.amount}, ${item.similarity_score}, '${item.verification_id}')" class="btn-primary text-xs py-1.5 px-3">
                        <i class="fa-solid fa-gavel mr-1"></i> Adjudicate
                    </button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tableBody.innerHTML = `<tr><td colspan="8" class="py-6 text-center text-danger">Unable to load review queue: ${e.message}</td></tr>`;
    }
}

function openReviewModal(txnRef, custName, amount, sim, verifId) {
    currentVerificationId = verifId;
    document.getElementById('modal-txn-ref').innerText = txnRef;
    document.getElementById('modal-cust-name').innerText = custName;
    document.getElementById('modal-amount').innerText = formatCurrency(amount);
    document.getElementById('modal-sim').innerText = formatScore(sim);
    document.getElementById('modal-comment').value = '';
    document.getElementById('review-modal').classList.remove('hidden');
}

function closeReviewModal() {
    document.getElementById('review-modal').classList.add('hidden');
}

async function submitReview(decision) {
    const comment = document.getElementById('modal-comment').value.trim();
    if (!comment) {
        alert('Mandatory compliance requirement: Please enter an officer justification comment.');
        return;
    }

    try {
        const payload = {
            reviewer_username: 'compliance_officer_1',
            decision: decision,
            review_comment: comment
        };

        await apiPost(`/api/v1/verifications/${currentVerificationId}/adjudicate`, payload);
        alert(`Transaction successfully adjudicated as: ${decision}`);
        closeReviewModal();
        await loadPendingReviewsPage();
    } catch (err) {
        alert(`Adjudication error: ${err.message}`);
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    if (typeof renderPrimaryRail === 'function') {
        renderPrimaryRail('queue');
    }
    if (typeof renderTopBar === 'function') {
        renderTopBar('Compliance / Officer Adjudication Queue / Pending Verification Items');
    }
    await checkBackendHealth();
    await loadPendingReviewsPage();
});
