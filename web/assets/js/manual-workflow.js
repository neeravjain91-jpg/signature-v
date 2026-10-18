/**
 * SYNAPSE — Manual Registration & Biometric Verification Logic
 * Intelligent Signature Verification & Fraud Risk Assessment System
 */

let selectedGenuineFile = null;
let selectedQueryFile = null;

function setCustomerId(id) {
    document.getElementById('manual-customer-id').value = id;
    loadCustomerGallery();
}

function setRandomCustomer() {
    const randId = 'CUST-' + Math.floor(1000 + Math.random() * 9000);
    document.getElementById('manual-customer-id').value = randId;
    loadCustomerGallery();
}

function handleGenuineFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    selectedGenuineFile = file;

    document.getElementById('genuine-file-name').innerText = file.name;
    document.getElementById('genuine-file-size').innerText = (file.size / 1024).toFixed(1) + ' KB';
    document.getElementById('genuine-file-label').innerText = 'Selected: ' + file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        const thumb = document.getElementById('genuine-thumb-preview');
        const workbenchImg = document.getElementById('ref-workbench-img');
        if (thumb) thumb.src = e.target.result;
        if (workbenchImg) workbenchImg.src = e.target.result;
        document.getElementById('genuine-preview-container').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function handleQueryFileSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    selectedQueryFile = file;

    document.getElementById('query-file-name').innerText = file.name;
    document.getElementById('query-file-size').innerText = (file.size / 1024).toFixed(1) + ' KB';
    document.getElementById('query-file-label').innerText = 'Selected: ' + file.name;

    const reader = new FileReader();
    reader.onload = (e) => {
        const thumb = document.getElementById('query-thumb-preview');
        const workbenchImg = document.getElementById('query-workbench-img');
        if (thumb) thumb.src = e.target.result;
        if (workbenchImg) workbenchImg.src = e.target.result;
        document.getElementById('query-preview-container').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function toggleCanvasInvert(frameId) {
    const frame = document.getElementById(frameId);
    if (frame) {
        frame.classList.toggle('invert-view');
    }
}

function toggleCanvasOtsu(imgId) {
    const img = document.getElementById(imgId);
    if (!img) return;
    // Toggle visual binarization filter (high-contrast threshold simulation)
    if (img.style.filter.includes('contrast(200%)')) {
        img.style.filter = 'invert(1) opacity(0.95)';
    } else {
        img.style.filter = 'invert(1) contrast(300%) grayscale(100%)';
    }
}

function updateModeUI() {
    const modeEl = document.querySelector('input[name="verif-mode"]:checked');
    const mode = modeEl ? modeEl.value : 'single';
    const modelTrackEl = document.getElementById('select-manual-model-track');
    const modelTrack = modelTrackEl ? modelTrackEl.value : 'siamese';
    const threshEl = document.getElementById('res-manual-threshold');
    const modeBadge = document.getElementById('res-manual-mode-badge');
    const singleThreshLabel = document.getElementById('label-single-thresh');
    const galleryThreshLabel = document.getElementById('label-gallery-thresh');

    let baseThresh = 0.5924;
    let galThresh = 0.6312;
    let modelLabel = 'SYNAPSE Siamese ResNet-18';

    if (modelTrack === 'siamese') {
        baseThresh = 0.5924;
        galThresh = 0.6312;
        modelLabel = 'SYNAPSE Siamese ResNet-18 v4';
    } else if (modelTrack === 'transformer') {
        baseThresh = 0.7313;
        galThresh = 0.7600;
        modelLabel = 'Vision Transformer';
    } else if (modelTrack === 'svm' || modelTrack === 'sklearn') {
        baseThresh = 0.3636;
        galThresh = 0.4000;
        modelLabel = 'Classical SVM';
    } else if (modelTrack === 'random_forest') {
        baseThresh = 0.4264;
        galThresh = 0.4600;
        modelLabel = 'Random Forest';
    } else if (modelTrack === 'logistic') {
        baseThresh = 0.2015;
        galThresh = 0.2400;
        modelLabel = 'Logistic Reg.';
    }

    if (singleThreshLabel) singleThreshLabel.innerText = `\u03c4* = ${baseThresh.toFixed(4)}`;
    if (galleryThreshLabel) galleryThreshLabel.innerText = `\u03c4_gal* = ${galThresh.toFixed(4)} (Max-Sim)`;

    if (threshEl) {
        threshEl.innerText = (mode === 'gallery') ? galThresh.toFixed(4) : baseThresh.toFixed(4);
    }
    if (modeBadge) {
        modeBadge.innerText = (mode === 'gallery')
            ? `Mode 2: Customer Gallery Verification (Max-Sim, ${modelLabel})`
            : `Mode 1: Single Reference Verification (${modelLabel})`;
    }
}

async function loadCustomerGallery() {
    const custId = document.getElementById('manual-customer-id').value.trim();
    if (!custId) return;

    const container = document.getElementById('gallery-cards-container');
    const badge = document.getElementById('gallery-count-badge');
    const refWorkbenchImg = document.getElementById('ref-workbench-img');
    if (!container) return;

    try {
        const data = await apiGet(`/api/v1/customers/${encodeURIComponent(custId)}/signatures`);
        if (badge) badge.innerText = `${data.active_count || 0} Active Specimen(s)`;

        if (!data.signatures || data.signatures.length === 0) {
            container.innerHTML = `
                <div class="p-4 rounded-xl border border-slate-800 text-center text-xs text-slate-500 bg-[#080C14]">
                    <i class="fa-solid fa-folder-open text-xl mb-1.5 text-slate-600 block"></i>
                    No registered signature specimens found for <strong class="text-slate-400">${custId}</strong>.<br/>
                    Enroll a genuine signature in Step 1.
                </div>
            `;
            if (refWorkbenchImg) {
                refWorkbenchImg.src = '/api/v1/sample-image?type=genuine_ref';
            }
            return;
        }

        // Set the primary active reference image in the workbench canvas
        const primarySig = data.signatures.find(s => s.is_active) || data.signatures[0];
        if (refWorkbenchImg && primarySig) {
            refWorkbenchImg.src = `${API_BASE}${primarySig.image_url}`;
        }

        container.innerHTML = data.signatures.map((sig, idx) => {
            const isActive = sig.is_active;
            const statusClass = isActive ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-slate-900 text-slate-400 border-slate-800';
            const imgSrc = `${API_BASE}${sig.image_url}`;
            return `
                <div class="bg-[#080C14] p-3 rounded-xl border ${isActive ? 'border-sky-900/60' : 'border-slate-800 opacity-60'} flex flex-col justify-between space-y-2">
                    <div class="flex justify-between items-center text-[10px]">
                        <span class="font-bold text-slate-200">Specimen #${idx + 1}</span>
                        <span class="px-1.5 py-0.5 rounded border ${statusClass} font-semibold uppercase">${sig.status}</span>
                    </div>
                    <div class="h-16 bg-[#04060A] rounded border border-slate-800 flex items-center justify-center overflow-hidden p-1">
                        <img src="${imgSrc}" alt="Specimen" class="max-h-full max-w-full object-contain filter invert opacity-90" onerror="this.onerror=null; this.src='/api/v1/sample-image?type=genuine_ref';">
                    </div>
                    <div class="text-[10px] text-slate-400 space-y-0.5 mono">
                        <div class="flex justify-between">
                            <span>Quality:</span>
                            <span class="text-sky-400">${(sig.image_quality_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>ID:</span>
                            <span class="text-slate-300 truncate max-w-[120px]">${sig.signature_id.substring(0, 8)}...</span>
                        </div>
                    </div>
                    ${isActive ? `
                        <button type="button" onclick="deactivateSpecimen('${sig.signature_id}')" class="w-full py-1 text-[10px] rounded bg-slate-900 hover:bg-rose-950 hover:text-rose-400 text-slate-400 border border-slate-800 hover:border-rose-900 transition flex items-center justify-center gap-1 cursor-pointer">
                            <i class="fa-solid fa-ban"></i> Deactivate
                        </button>
                    ` : `
                        <div class="py-1 text-[10px] text-center text-slate-600 font-mono">SUPERSEDED</div>
                    `}
                </div>
            `;
        }).join('');
    } catch (err) {
        console.warn('Failed to load customer gallery:', err);
    }
}

async function registerGenuineSignature() {
    const custId = document.getElementById('manual-customer-id').value.trim();
    const alertBox = document.getElementById('enroll-alert');
    const btn = document.getElementById('btn-register-sig');

    if (!custId) {
        alertBox.className = 'text-xs p-3 rounded-xl border bg-rose-950/60 border-rose-800 text-rose-400 block';
        alertBox.innerText = 'Please specify a Customer Reference before registering a signature.';
        return;
    }

    if (!selectedGenuineFile) {
        alertBox.className = 'text-xs p-3 rounded-xl border bg-rose-950/60 border-rose-800 text-rose-400 block';
        alertBox.innerText = 'Please select a genuine signature image file to upload.';
        return;
    }

    const origHtml = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Enrolling into Vault...';
    btn.disabled = true;

    const formData = new FormData();
    formData.append('customer_reference', custId);
    formData.append('signature_file', selectedGenuineFile);

    try {
        const data = await apiPost('/api/v1/signatures/enroll', formData, true);
        alertBox.className = 'text-xs p-3 rounded-xl border bg-emerald-950/60 border-emerald-800 text-emerald-400 block space-y-1';
        alertBox.innerHTML = `
            <div class="flex items-center gap-1.5 font-bold">
                <i class="fa-solid fa-circle-check"></i> Genuine Reference Specimen Enrolled Successfully!
            </div>
            <div class="text-[11px] text-emerald-300 mono">
                Specimen ID: <span>${data.signature_id}</span> &bull; Quality Score: <strong>${(data.image_quality_score * 100).toFixed(1)}%</strong>
            </div>
            <div class="text-[10px] text-slate-400 italic">
                Strict Biometric Protocol: First upload enrolled strictly as baseline reference. No verification score rendered.
            </div>
        `;
        
        selectedGenuineFile = null;
        document.getElementById('file-genuine-upload').value = '';
        document.getElementById('genuine-preview-container').classList.add('hidden');
        document.getElementById('genuine-file-label').innerText = 'Click or drop genuine signature card (PNG, JPG, TIFF)';
        
        await loadCustomerGallery();
    } catch (err) {
        alertBox.className = 'text-xs p-3 rounded-xl border bg-rose-950/60 border-rose-800 text-rose-400 block';
        alertBox.innerText = `Registration Failed: ${err.message || 'Upload error'}`;
    } finally {
        btn.innerHTML = origHtml;
        btn.disabled = false;
    }
}

async function deactivateSpecimen(sigId) {
    if (!confirm('Are you sure you want to deactivate this signature reference? Historical audit logs will remain intact.')) {
        return;
    }

    try {
        await apiPost(`/api/v1/signatures/${sigId}/deactivate`, {});
        await loadCustomerGallery();
    } catch (err) {
        alert(`Deactivation failed: ${err.message}`);
    }
}

async function verifyQuestionedSignature() {
    const custId = document.getElementById('manual-customer-id').value.trim();
    const btn = document.getElementById('btn-verify-manual');
    const modeEl = document.querySelector('input[name="verif-mode"]:checked');
    const mode = modeEl ? modeEl.value : 'single';

    if (!custId) {
        alert('Please specify a target Customer ID for verification.');
        return;
    }

    if (!selectedQueryFile) {
        alert('Please select a questioned signature image file to verify.');
        return;
    }

    const origHtml = btn.innerHTML;
    const t0 = performance.now();
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Biometric Inference...';
    btn.disabled = true;

    const modelTrackEl = document.getElementById('select-manual-model-track');
    const modelTrack = modelTrackEl ? modelTrackEl.value : 'siamese';

    const formData = new FormData();
    formData.append('customer_reference', custId);
    formData.append('submitted_signature', selectedQueryFile);
    formData.append('mode', mode);
    formData.append('model_track', modelTrack);

    try {
        const data = await apiPost('/api/v1/verifications/verify', formData, true);
        const t1 = performance.now();
        const latencyMs = (t1 - t0).toFixed(1);
        renderManualVerificationResults(data, latencyMs);
    } catch (err) {
        alert(`Verification Error: ${err.message || 'Inference error'}`);
        const banner = document.getElementById('verdict-banner');
        if (banner) {
            banner.className = 'verdict-banner verdict-nomatch';
            banner.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="fa-solid fa-circle-xmark text-2xl text-rose-400"></i>
                    <div>
                        <div class="text-base font-bold text-white">Verification Engine Error</div>
                        <div class="text-xs text-rose-300">${err.message || 'Execution error'}</div>
                    </div>
                </div>
            `;
        }
    } finally {
        btn.innerHTML = origHtml;
        btn.disabled = false;
    }
}

function renderManualVerificationResults(data, latencyMs = '8.5') {
    const banner = document.getElementById('verdict-banner');
    const simEl = document.getElementById('res-manual-similarity');
    const distEl = document.getElementById('res-manual-distance');
    const threshEl = document.getElementById('res-manual-threshold');
    const marginEl = document.getElementById('res-manual-margin');
    const riskEl = document.getElementById('res-manual-risk');
    const tierEl = document.getElementById('res-manual-tier');
    const verifIdEl = document.getElementById('res-manual-verif-id');
    const refCountEl = document.getElementById('res-manual-ref-count');
    const timeEl = document.getElementById('res-manual-timestamp');
    const modeBadge = document.getElementById('res-manual-mode-badge');
    const modelUsedEl = document.getElementById('res-manual-model-used');
    const matchVerdictEl = document.getElementById('res-manual-match-verdict');
    const latencyEl = document.getElementById('workbench-latency-val');

    const sim = Number(data.similarity_score || 0);
    const thresh = Number(data.threshold_used || 0.5924);
    const dist = Number(data.euclidean_distance || 0);
    const margin = sim - thresh;

    if (simEl) simEl.innerText = formatScore(sim);
    if (distEl) distEl.innerText = formatScore(dist);
    if (threshEl) threshEl.innerText = formatScore(thresh);
    if (marginEl) {
        const sign = margin >= 0 ? '+' : '';
        marginEl.innerText = `${sign}${margin.toFixed(4)} Margin`;
        marginEl.className = margin >= 0 ? 'metric-subtext text-emerald-400 mono' : 'metric-subtext text-rose-400 mono';
    }
    if (riskEl) riskEl.innerText = formatScore(data.overall_risk_score || 0.05);
    if (tierEl) tierEl.innerText = `Tier: ${data.risk_level || 'LOW RISK'}`;
    if (verifIdEl) verifIdEl.innerText = data.verification_id;
    if (refCountEl) refCountEl.innerText = `${data.reference_count || 1} Specimen(s)`;
    if (timeEl) timeEl.innerText = formatDate(data.timestamp || new Date().toISOString());
    if (latencyEl) latencyEl.innerText = `${latencyMs} ms`;
    if (modeBadge) modeBadge.innerText = (data.mode === 'gallery') ? 'Mode 2: Customer Gallery Verification' : 'Mode 1: Single Reference Verification';

    // Model track name
    const modelTrackEl = document.getElementById('select-manual-model-track');
    const selectedModelName = modelTrackEl ? modelTrackEl.options[modelTrackEl.selectedIndex].text : 'SYNAPSE Siamese ResNet-18';
    if (modelUsedEl) modelUsedEl.innerText = selectedModelName;

    // Biometric Result: MATCH / NO MATCH
    const isMatch = Boolean(data.match !== undefined ? data.match : (sim >= thresh));
    if (matchVerdictEl) {
        matchVerdictEl.innerText = isMatch ? 'MATCH' : 'NO MATCH';
        matchVerdictEl.className = isMatch ? 'mono font-bold text-emerald-400 text-xl' : 'mono font-bold text-rose-400 text-xl';
    }

    if (banner) {
        if (data.decision === 'VERIFIED') {
            banner.className = 'verdict-banner verdict-match';
            banner.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="fa-solid fa-circle-check text-2xl text-emerald-400"></i>
                    <div>
                        <div class="text-lg font-bold text-white">Biometric Verdict: MATCH (VERIFIED)</div>
                        <div class="text-xs text-emerald-300/80">Questioned signature stroke characteristics match registered customer specimen vault.</div>
                    </div>
                </div>
                <div class="text-right hidden sm:block">
                    <span class="text-[10px] text-slate-400 uppercase mono block">BIOMETRIC VERDICT</span>
                    <span class="text-xl font-bold mono text-emerald-400">MATCH</span>
                </div>
            `;
        } else if (data.decision === 'MANUAL_REVIEW') {
            banner.className = 'verdict-banner verdict-review';
            banner.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="fa-solid fa-triangle-exclamation text-2xl text-amber-400"></i>
                    <div>
                        <div class="text-lg font-bold text-white">Biometric Verdict: BORDERLINE (MANUAL REVIEW)</div>
                        <div class="text-xs text-amber-300/80">Similarity score is near operational decision threshold. Escalated to forensic analyst queue.</div>
                    </div>
                </div>
                <div class="text-right hidden sm:block">
                    <span class="text-[10px] text-slate-400 uppercase mono block">BIOMETRIC VERDICT</span>
                    <span class="text-xl font-bold mono text-amber-400">BORDERLINE</span>
                </div>
            `;
        } else {
            banner.className = 'verdict-banner verdict-nomatch';
            banner.innerHTML = `
                <div class="flex items-center gap-3">
                    <i class="fa-solid fa-circle-xmark text-2xl text-rose-400"></i>
                    <div>
                        <div class="text-lg font-bold text-white">Biometric Verdict: NO MATCH (REJECTED)</div>
                        <div class="text-xs text-rose-300/80">Discrepancy detected in stroke trajectory and ballistic pressure against reference vault.</div>
                    </div>
                </div>
                <div class="text-right hidden sm:block">
                    <span class="text-[10px] text-slate-400 uppercase mono block">BIOMETRIC VERDICT</span>
                    <span class="text-xl font-bold mono text-rose-400">NO MATCH</span>
                </div>
            `;
        }
    }
}

window.addEventListener('DOMContentLoaded', async () => {
    renderGlobalNavigation('nav-manual');
    renderGlobalFooter();
    await checkBackendHealth();
    updateModeUI();
    await loadCustomerGallery();
});
