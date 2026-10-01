/**
 * SIGNATURE VMAKE — Model Registry & Health Diagnostics Logic
 */

async function loadModelHealthPage() {
    const container = document.getElementById('models-health-grid');
    const overallBadge = document.getElementById('overall-health-badge');
    if (!container) return;

    container.innerHTML = `
        <div class="col-span-full py-12 text-center text-slate-500">
            <i class="fa-solid fa-spinner fa-spin text-2xl text-cyan-400 mb-2 block"></i>
            Executing live diagnostic inference across all candidate models...
        </div>
    `;

    try {
        const data = await apiGet('/api/v1/models/health');
        const models = data.models || {};
        
        if (overallBadge) {
            if (data.status === 'ready') {
                overallBadge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800';
                overallBadge.innerHTML = '<i class="fa-solid fa-circle-check mr-1"></i> ALL CANDIDATES LIVE & READY';
            } else {
                overallBadge.className = 'px-3 py-1 rounded-full text-xs font-semibold bg-amber-950 text-amber-400 border border-amber-800';
                overallBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation mr-1"></i> PARTIAL STATUS';
            }
        }

        const candidateOrder = [
            { key: 'transformer', title: 'Track B: Hugging Face Vision Transformer', role: 'PRODUCTION DEFAULT', icon: 'fa-microchip', color: 'cyan' },
            { key: 'random_forest', title: 'Track A1: Random Forest Classifier', role: 'ACCURACY CHAMPION', icon: 'fa-tree', color: 'emerald' },
            { key: 'svm', title: 'Track A2: Support Vector Machine', role: 'EDGE BASELINE', icon: 'fa-shapes', color: 'blue' },
            { key: 'logistic', title: 'Track A3: Classical Logistic Regression', role: 'ULTRA-LIGHT BASELINE', icon: 'fa-bolt', color: 'amber' }
        ];

        container.innerHTML = candidateOrder.map(c => {
            const m = models[c.key] || { status: 'unavailable', reason: 'Model not returned by backend' };
            const isReady = (m.status === 'ready');
            const testInf = m.test_inference || {};

            return `
                <div class="glass-card rounded-2xl p-6 border-slate-800 space-y-4 hover:border-${c.color}-500/50 transition">
                    <div class="flex justify-between items-start">
                        <div class="flex items-center gap-3">
                            <div class="w-10 h-10 rounded-xl bg-${c.color}-500/10 text-${c.color}-400 flex items-center justify-center font-bold">
                                <i class="fa-solid ${c.icon} text-lg"></i>
                            </div>
                            <div>
                                <h3 class="text-sm font-bold text-white">${c.title}</h3>
                                <span class="text-[10px] text-slate-400 mono">${m.model_type || 'Biometric Verifier'}</span>
                            </div>
                        </div>
                        <span class="px-2 py-0.5 rounded text-[10px] font-bold ${isReady ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-rose-950 text-rose-400 border border-rose-800'}">
                            ${isReady ? 'READY' : 'UNAVAILABLE'}
                        </span>
                    </div>

                    <div class="bg-slate-950/80 p-3.5 rounded-xl border border-slate-800 text-xs font-mono space-y-2">
                        <div class="flex justify-between">
                            <span class="text-slate-400 font-sans">Model Name:</span>
                            <span class="text-white">${m.model_name || c.key}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-slate-400 font-sans">Operating Threshold (&tau;):</span>
                            <span class="text-cyan-400 font-bold">${formatScore(m.threshold)}</span>
                        </div>
                        <div class="flex justify-between">
                            <span class="text-slate-400 font-sans">Checkpoint Path:</span>
                            <span class="text-slate-300 truncate max-w-[200px]" title="${m.checkpoint || ''}">${m.checkpoint || 'N/A'}</span>
                        </div>
                    </div>

                    <!-- Live Inference Diagnostic Result -->
                    <div class="space-y-1.5 pt-1">
                        <span class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Real Diagnostic Inference Test:</span>
                        ${isReady ? `
                            <div class="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-[11px] font-mono grid grid-cols-3 gap-2 text-center">
                                <div>
                                    <span class="text-[9px] text-slate-500 font-sans block">Decision</span>
                                    <span class="font-bold text-emerald-400">${testInf.decision || 'VERIFIED'}</span>
                                </div>
                                <div>
                                    <span class="text-[9px] text-slate-500 font-sans block">Score</span>
                                    <span class="text-white">${formatScore(testInf.similarity_score)}</span>
                                </div>
                                <div>
                                    <span class="text-[9px] text-slate-500 font-sans block">Latency</span>
                                    <span class="text-cyan-400">${testInf.latency_ms || '--'} ms</span>
                                </div>
                            </div>
                        ` : `
                            <div class="p-2.5 rounded-lg bg-rose-950/20 border border-rose-900/60 text-xs text-rose-400 font-mono">
                                Error: ${m.reason || 'Failed to initialize weights'}
                            </div>
                        `}
                    </div>

                    <div class="flex justify-between items-center text-[10px] text-slate-500 pt-2 border-t border-slate-800/80">
                        <span>Role: <strong class="text-slate-400 font-sans">${c.role}</strong></span>
                        <span>Version: <code class="mono text-slate-300">${m.model_version || 'v1.0.0'}</code></span>
                    </div>
                </div>
            `;
        }).join('');
    } catch (err) {
        container.innerHTML = `
            <div class="col-span-full p-8 rounded-2xl border border-rose-900/60 bg-rose-950/20 text-center text-xs text-rose-400 space-y-2">
                <i class="fa-solid fa-circle-exclamation text-2xl mb-1 block"></i>
                <p class="font-bold">Failed to connect to backend model health endpoint.</p>
                <p class="text-slate-400">Ensure the FastAPI server is running on http://127.0.0.1:8000.</p>
            </div>
        `;
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    renderGlobalNavigation('nav-health');
    renderGlobalFooter();
    await checkBackendHealth();
    await loadModelHealthPage();
});
