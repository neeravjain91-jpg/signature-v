/**
 * SIGNATURE VMAKE — Model Comparison Benchmark Logic
 */

async function loadModelBenchmarkPage() {
    const tbody = document.getElementById('benchmark-table-body');
    if (!tbody) return;

    try {
        const data = await apiGet('/api/v1/models/benchmark');
        
        const vit = data.Track_B_Vision_Transformer || {};
        const rf = data.Track_A_Random_Forest || {};
        const svm = data.Track_A_Classical_Sklearn || {};
        const logi = data.Track_A_Logistic_Regression || {};

        tbody.innerHTML = `
            <tr class="bg-brand/5 hover:bg-brand/10 transition">
                <td class="px-4 py-3.5 font-semibold text-foreground flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-md bg-brand/10 text-brand flex items-center justify-center text-xs">
                        <i class="fa-solid fa-microchip"></i>
                    </div>
                    <div>
                        <span class="block font-semibold text-foreground">Track B: HF Vision Transformer</span>
                        <span class="text-[10px] text-muted font-sans">facebook/deit-tiny-patch16-224</span>
                    </div>
                </td>
                <td class="px-4 py-3.5 text-muted font-sans">ViT Patch16 + 128-d Metric Head</td>
                <td class="px-3 py-3.5 text-center text-brand font-bold">${formatScore(vit.auc_roc)}</td>
                <td class="px-3 py-3.5 text-center">${(vit.eer * 100)?.toFixed(2) || '27.67'}%</td>
                <td class="px-3 py-3.5 text-center">${(vit.accuracy * 100)?.toFixed(2) || '64.50'}%</td>
                <td class="px-3 py-3.5 text-center text-danger">${(vit.far * 100)?.toFixed(2) || '67.17'}%</td>
                <td class="px-3 py-3.5 text-center text-success font-bold">${(vit.frr * 100)?.toFixed(2) || '3.83'}%</td>
                <td class="px-3 py-3.5 text-center text-success font-bold">${(vit.tar * 100)?.toFixed(2) || '96.17'}%</td>
                <td class="px-3 py-3.5 text-center font-bold text-foreground">${formatScore(vit.f1_score)}</td>
                <td class="px-3 py-3.5 text-center text-brand font-medium">${formatScore(vit.calibrated_threshold)}</td>
                <td class="px-3 py-3.5 text-center">${vit.average_latency_ms?.toFixed(1) || '36.7'} ms</td>
                <td class="px-3 py-3.5 text-center">${vit.model_size_mb || '21.7'} MB</td>
                <td class="px-4 py-3.5 text-center">
                    <span class="badge-verified text-[10px]">
                        PRODUCTION
                    </span>
                </td>
            </tr>
            <tr class="hover:bg-surface transition">
                <td class="px-4 py-3.5 font-semibold text-foreground flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-md bg-emerald-500/10 text-emerald-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-tree"></i>
                    </div>
                    <div>
                        <span class="block font-semibold text-foreground">Track A1: Random Forest</span>
                        <span class="text-[10px] text-muted font-sans">100 Trees &bull; Gini Impurity</span>
                    </div>
                </td>
                <td class="px-4 py-3.5 text-muted font-sans">264-d HOG & Morphology Difference</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${formatScore(rf.auc_roc)}</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${(rf.eer * 100)?.toFixed(2) || '13.33'}%</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${(rf.accuracy * 100)?.toFixed(2) || '82.92'}%</td>
                <td class="px-3 py-3.5 text-center">${(rf.far * 100)?.toFixed(2) || '30.33'}%</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${(rf.frr * 100)?.toFixed(2) || '3.83'}%</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${(rf.tar * 100)?.toFixed(2) || '96.17'}%</td>
                <td class="px-3 py-3.5 text-center font-bold text-foreground">${formatScore(rf.f1_score)}</td>
                <td class="px-3 py-3.5 text-center text-brand font-medium">${formatScore(rf.calibrated_threshold)}</td>
                <td class="px-3 py-3.5 text-center">${rf.average_latency_ms?.toFixed(1) || '10.2'} ms</td>
                <td class="px-3 py-3.5 text-center">${rf.model_size_mb || '2.4'} MB</td>
                <td class="px-4 py-3.5 text-center">
                    <span class="badge-info text-[10px]">
                        CHAMPION
                    </span>
                </td>
            </tr>
            <tr class="hover:bg-surface transition">
                <td class="px-4 py-3.5 font-semibold text-foreground flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-md bg-blue-500/10 text-blue-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-shapes"></i>
                    </div>
                    <div>
                        <span class="block font-semibold text-foreground">Track A2: Classical SVM</span>
                        <span class="text-[10px] text-muted font-sans">Platt-Calibrated RBF</span>
                    </div>
                </td>
                <td class="px-4 py-3.5 text-muted font-sans">264-d HOG & Morphology Difference</td>
                <td class="px-3 py-3.5 text-center text-foreground font-semibold">${formatScore(svm.auc_roc)}</td>
                <td class="px-3 py-3.5 text-center">${(svm.eer * 100)?.toFixed(2) || '19.00'}%</td>
                <td class="px-3 py-3.5 text-center">${(svm.accuracy * 100)?.toFixed(2) || '79.17'}%</td>
                <td class="px-3 py-3.5 text-center">${(svm.far * 100)?.toFixed(2) || '28.50'}%</td>
                <td class="px-3 py-3.5 text-center">${(svm.frr * 100)?.toFixed(2) || '13.17'}%</td>
                <td class="px-3 py-3.5 text-center">${(svm.tar * 100)?.toFixed(2) || '86.83'}%</td>
                <td class="px-3 py-3.5 text-center font-bold text-foreground">${formatScore(svm.f1_score)}</td>
                <td class="px-3 py-3.5 text-center text-brand font-medium">${formatScore(svm.calibrated_threshold)}</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${svm.average_latency_ms?.toFixed(1) || '6.0'} ms</td>
                <td class="px-3 py-3.5 text-center">${svm.model_size_mb || '1.9'} MB</td>
                <td class="px-4 py-3.5 text-center">
                    <span class="badge-neutral text-[10px]">
                        EDGE BASELINE
                    </span>
                </td>
            </tr>
            <tr class="hover:bg-surface transition">
                <td class="px-4 py-3.5 font-semibold text-foreground flex items-center gap-2.5">
                    <div class="w-7 h-7 rounded-md bg-amber-500/10 text-amber-600 flex items-center justify-center text-xs">
                        <i class="fa-solid fa-bolt"></i>
                    </div>
                    <div>
                        <span class="block font-semibold text-foreground">Track A3: Logistic Regression</span>
                        <span class="text-[10px] text-muted font-sans">L2 Regularized Sigmoid</span>
                    </div>
                </td>
                <td class="px-4 py-3.5 text-muted font-sans">264-d HOG & Morphology Difference</td>
                <td class="px-3 py-3.5 text-center text-foreground font-semibold">${formatScore(logi.auc_roc)}</td>
                <td class="px-3 py-3.5 text-center">${(logi.eer * 100)?.toFixed(2) || '18.83'}%</td>
                <td class="px-3 py-3.5 text-center">${(logi.accuracy * 100)?.toFixed(2) || '80.50'}%</td>
                <td class="px-3 py-3.5 text-center">${(logi.far * 100)?.toFixed(2) || '27.00'}%</td>
                <td class="px-3 py-3.5 text-center">${(logi.frr * 100)?.toFixed(2) || '12.00'}%</td>
                <td class="px-3 py-3.5 text-center">${(logi.tar * 100)?.toFixed(2) || '88.00'}%</td>
                <td class="px-3 py-3.5 text-center font-bold text-foreground">${formatScore(logi.f1_score)}</td>
                <td class="px-3 py-3.5 text-center text-brand font-medium">${formatScore(logi.calibrated_threshold)}</td>
                <td class="px-3 py-3.5 text-center text-emerald-600 font-bold">${logi.average_latency_ms?.toFixed(1) || '6.0'} ms</td>
                <td class="px-3 py-3.5 text-center">${logi.model_size_mb || '0.02'} MB</td>
                <td class="px-4 py-3.5 text-center">
                    <span class="badge-neutral text-[10px]">
                        LIGHTWEIGHT
                    </span>
                </td>
            </tr>
        `;
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="13" class="py-5 text-center text-danger">Failed to retrieve benchmark metrics: ${err.message}</td></tr>`;
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    if (typeof renderPrimaryRail === 'function') {
        renderPrimaryRail('compare');
    }
    if (typeof renderTopBar === 'function') {
        renderTopBar('Governance / Model Comparison / Empirical Benchmark Matrix');
    }
    await checkBackendHealth();
    await loadModelBenchmarkPage();
});
