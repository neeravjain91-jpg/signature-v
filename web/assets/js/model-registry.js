/**
 * SIGNATURE VMAKE — Model Registry & Health Diagnostics Logic
 */

async function loadModelHealthPage() {
    const container = document.getElementById('models-health-grid');
    const overallBadge = document.getElementById('overall-health-badge');
    if (!container) return;

    container.innerHTML = `
        <div class="col-span-full py-12 text-center text-muted">
            <i class="fa-solid fa-spinner fa-spin text-2xl text-brand mb-2 block"></i>
            Executing live diagnostic inference across all candidate models...
        </div>
    `;

    try {
        const data = await apiGet('/api/v1/models/health');
        const models = data.models || {};
        
        if (overallBadge) {
            if (data.status === 'ready') {
                overallBadge.className = 'badge-verified text-xs font-semibold px-3 py-1';
                overallBadge.innerHTML = '<i class="fa-solid fa-circle-check mr-1"></i> ALL CANDIDATES LIVE & READY';
            } else {
                overallBadge.className = 'badge-review text-xs font-semibold px-3 py-1';
                overallBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-1"></i> PARTIAL STATUS';
            }
        }

        const candidateOrder = [
            { key: 'transformer', title: 'Track B: Hugging Face Vision Transformer', role: 'PRODUCTION DEFAULT', icon: 'fa-microchip', colorText: 'text-brand', colorBg: 'bg-brand/10', roleBadge: 'badge-verified' },
            { key: 'random_forest', title: 'Track A1: Random Forest Classifier', role: 'ACCURACY CHAMPION', icon: 'fa-tree', colorText: 'text-emerald-600', colorBg: 'bg-emerald-500/10', roleBadge: 'badge-info' },
            { key: 'svm', title: 'Track A2: Support Vector Machine', role: 'EDGE BASELINE', icon: 'fa-shapes', colorText: 'text-blue-600', colorBg: 'bg-blue-500/10', roleBadge: 'badge-neutral' },
            { key: 'logistic', title: 'Track A3: Classical Logistic Regression', role: 'ULTRA-LIGHT BASELINE', icon: 'fa-bolt', colorText: 'text-amber-600', colorBg: 'bg-amber-500/10', roleBadge: 'badge-neutral' }
        ];

        container.innerHTML = candidateOrder.map(c => {
            const m = models[c.key] || { status: 'unavailable', reason: 'Model not returned by backend' };
            const isReady = (m.status === 'ready');
            const testInf = m.test_inference || {};

            return `
                <div class="card p-5 space-y-4 hover:border-brand/40 transition">
                    <div class="flex justify-between items-start">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-lg ${c.colorBg} ${c.colorText} flex items-center justify-center font-bold">
                                <i class="fa-solid ${c.icon} text-lg"></i>
                            </div>
                            <div>
                                <h3 class="text-sm font-semibold text-foreground">${c.title}</h3>
                                <span class="text-[11px] text-muted font-mono">${m.model_type || 'Biometric Verifier'}</span>
                            </div>
                        </div>
                        <span class="${isReady ? 'badge-verified' : 'badge-blocked'} text-[10px] font-mono">
                            ${isReady ? 'READY' : 'UNAVAILABLE'}
                        </span>
                    </div>

                    <div class="bg-surface p-3.5 rounded-lg border border-border text-xs font-mono space-y-2">
                        <div class="flex justify-between">
                            <span class="text-muted font-sans">Model Name:</span>
                            <span class="text-foreground font-medium">${m.model_name || c.key}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-muted font-sans">Operating Threshold (&tau;):</span>
                            <span class="text-brand font-bold">${formatScore(m.threshold)}</span>
                        </div>
                        <div class="flex justify-between items-center">
                            <span class="text-muted font-sans">Checkpoint File:</span>
                            <span class="text-muted truncate max-w-[200px]" title="${m.checkpoint || ''}">${m.checkpoint ? m.checkpoint.split('/').pop().split('\\').pop() : 'N/A'}</span>
                        </div>
                    </div>

                    <!-- Live Inference Diagnostic Result -->
                    <div class="space-y-1.5 pt-1">
                        <span class="text-[10px] font-semibold text-muted uppercase tracking-wider block">Live Verification Self-Test</span>
                        ${isReady ? `
                            <div class="bg-surface p-2.5 rounded-lg border border-border text-xs font-mono grid grid-cols-3 gap-2 text-center">
                                <div>
                                    <span class="text-[10px] text-muted font-sans block">Decision</span>
                                    <span class="font-bold text-success">${testInf.decision || 'VERIFIED'}</span>
                                </div>
                                <div>
                                    <span class="text-[10px] text-muted font-sans block">Similarity</span>
                                    <span class="text-foreground font-semibold">${formatScore(testInf.similarity_score)}</span>
                                </div>
                                <div>
                                    <span class="text-[10px] text-muted font-sans block">Latency</span>
                                    <span class="text-brand font-semibold">${testInf.latency_ms || '--'} ms</span>
                                </div>
                            </div>
                        ` : `
                            <div class="p-2.5 rounded-lg bg-danger/5 border border-danger/20 text-xs text-danger font-mono">
                                Error: ${m.reason || 'Failed to initialize weights'}
                            </div>
                        `}
                    </div>

                    <div class="flex justify-between items-center text-[11px] text-muted pt-2 border-t border-border">
                        <span class="${c.roleBadge} text-[10px]">${c.role}</span>
                        <span>Version: <code class="font-mono text-foreground font-medium">${m.model_version || 'v1.0.0'}</code></span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `
            <div class="col-span-full p-8 rounded-lg border border-danger/30 bg-danger/5 text-center text-xs text-danger space-y-2">
                <i class="fa-solid fa-circle-exclamation text-2xl mb-1 block"></i>
                <p class="font-bold">Failed to connect to backend model health endpoint.</p>
                <p class="text-muted">Ensure the FastAPI server is running on http://127.0.0.1:8000.</p>
            </div>
        `;
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    if (typeof renderPrimaryRail === 'function') {
        renderPrimaryRail('model');
    }
    if (typeof renderTopBar === 'function') {
        renderTopBar('Governance / Model Registry & Health / Diagnostic Runtime Monitor');
    }
    await checkBackendHealth();
    await loadModelHealthPage();
});
