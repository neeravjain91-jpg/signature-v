/**
 * SIGNATURE VMAKE — Overview Dashboard Logic
 */

async function loadOverviewDashboard() {
    try {
        const data = await apiGet('/api/v1/dashboard/metrics');
        const s = data.summary;
        document.getElementById('stat-total-verif').innerText = s.total_verifications.toLocaleString();
        document.getElementById('stat-verified-rate').innerText = s.pass_rate_pct.toFixed(1) + '%';
        document.getElementById('stat-rejected-rate').innerText = s.rejection_rate_pct.toFixed(1) + '%';
        document.getElementById('stat-pending-reviews').innerText = s.manual_review_count;

        if (data.active_model) {
            document.getElementById('overview-active-model-name').innerText = data.active_model.model_name || 'HF Vision Transformer';
            document.getElementById('overview-active-model-thresh').innerText = formatScore(data.active_model.threshold);
            document.getElementById('overview-active-model-arch').innerText = data.active_model.architecture || 'facebook/deit-tiny-patch16-224';
        }
    } catch (err) {
        console.warn('Failed to load dashboard metrics:', err);
        document.getElementById('stat-total-verif').innerText = '--';
        document.getElementById('stat-verified-rate').innerText = '--';
        document.getElementById('stat-rejected-rate').innerText = '--';
        document.getElementById('stat-pending-reviews').innerText = '--';
    }

    try {
        const healthData = await apiGet('/api/v1/health');
        if (healthData) {
            document.getElementById('overview-db-status').innerText = healthData.database || 'CONNECTED';
            document.getElementById('overview-service-status').innerText = healthData.status || 'HEALTHY';
        }
    } catch (_) {}
}

window.addEventListener('DOMContentLoaded', async () => {
    renderGlobalNavigation('nav-overview');
    renderGlobalFooter();
    await checkBackendHealth();
    await loadOverviewDashboard();
});
