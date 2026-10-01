/**
 * SIGNATURE VMAKE — Manual Registration & Biometric Verification Logic
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
        document.getElementById('genuine-thumb-preview').src = e.target.result;
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
        document.getElementById('query-thumb-preview').src = e.target.result;
        document.getElementById('query-preview-container').classList.remove('hidden');
    };
    reader.readAsDataURL(file);
}

function updateModeUI() {
    const modeEl = document.querySelector('input[name="verif-mode"]:checked');
    const mode = modeEl ? modeEl.value : 'single';
    const modelTrackEl = document.getElementById('select-manual-model-track');
    const modelTrack = modelTrackEl ? modelTrackEl.value : 'transformer';
    const threshEl = document.getElementById('res-manual-threshold');
    const modeBadge = document.getElementById('res-manual-mode-badge');
    const singleThreshLabel = document.getElementById('label-single-thresh');
    const galleryThreshLabel = document.getElementById('label-gallery-thresh');

    let baseThresh = 0.7313;
    let galThresh = 0.7600;
    let modelLabel = 'ViT Default';

    if (modelTrack === 'svm' || modelTrack === 'sklearn') {
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

    if (singleThreshLabel) singleThreshLabel.innerText = `Latest specimen (\u03c4* = ${baseThresh.toFixed(4)})`;
    if (galleryThreshLabel) galleryThreshLabel.innerText = `Max similarity (\u03c4_gal* = ${galThresh.toFixed(4)})`;

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
    if (!container) return;

    try {
        const data = await apiGet(`/api/v1/customers/${encodeURIComponent(custId)}/signatures`);
        if (badge) badge.innerText = `${data.active_count || 0} Active Specimen(s)`;

        if (!data.signatures || data.signatures.length === 0) {
            container.innerHTML = `
                <div class="p-6 rounded-xl border border-slate-800 text-center col-span-3 text-xs text-slate-500 bg-slate-950/40">
                    <i class="fa-solid fa-folder-open text-2xl mb-2 text-slate-600 block"></i>
                    No registered signature specimens found for <strong class="text-slate-400">${custId}</strong>.<br/>
                    Enroll a genuine signature in Step 1 below.
                </div>
            `;
            return;
        }

        container.innerHTML = data.signatures.map((sig, idx) => {
            const isActive = sig.is_active;
            const statusClass = isActive ? 'bg-emerald-950 text-emerald-400 border-emerald-800' : 'bg-slate-800 text-slate-400 border-slate-700';
            const imgSrc = `${API_BASE}${sig.image_url}`;
            return `
                <div class="bg-slate-950 p-3 rounded-xl border ${isActive ? 'border-cyan-900/50' : 'border-slate-800 opacity-60'} flex flex-col justify-between space-y-2">
                    <div class="flex justify-between items-center text-[10px]">
                        <span class="font-bold text-slate-300">Specimen #${idx + 1}</span>
                        <span class="px-1.5 py-0.5 rounded border ${statusClass} font-semibold uppercase">${sig.status}</span>
                    </div>
                    <div class="h-20 bg-black/80 rounded border border-slate-800 flex items-center justify-center overflow-hidden p-1">
                        <img src="${imgSrc}" alt="Specimen" class="max-h-full max-w-full object-contain filter invert opacity-90" onerror="this.onerror=null; this.src='${API_BASE}/api/v1/sample-image?type=genuine_ref';">
                    </div>
                    <div class="text-[10px] text-slate-400 space-y-0.5">
                        <div class="flex justify-between">
                            <span>Quality:</span>
                            <span class="mono text-cyan-400">${(sig.image_quality_score * 100).toFixed(1)}%</span>
                        </div>
                        <div class="flex justify-between">
                            <span>ID:</span>
                            <span class="mono text-slate-300 truncate max-w-[90px]">${sig.signature_id.substring(0, 8)}...</span>
                        </div>
                    </div>
                    ${isActive ? `
                        <button onclick="deactivateSpecimen('${sig.signature_id}')" class="w-full py-1 text-[10px] rounded bg-slate-900 hover:bg-rose-950 hover:text-rose-400 text-slate-400 border border-slate-800 hover:border-rose-900 transition flex items-center justify-center gap-1 cursor-pointer">
                            <i class="fa-solid fa-ban"></i> Deactivate
                        </button>
                    ` : `
                        <div class="py-1 text-[10px] text-center text-slate-500 font-mono">SUPERSEDED</div>
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
                <i class="fa-solid fa-circle-check"></i> First Signature Enrolled Successfully!
            </div>
            <div class="text-[11px] text-emerald-300">
                Specimen ID: <span class="mono">${data.signature_id}</span> &bull; Quality Score: <strong>${(data.image_quality_score * 100).toFixed(1)}%</strong>
            </div>
            <div class="text-[10px] text-slate-400 italic">
                Strict BRD Compliance: First upload is registered strictly as reference specimen. No verification verdict rendered.
            </div>
        `;
        
        // Reset selected file & re-fetch gallery
        selectedGenuineFile = null;
        document.getElementById('file-genuine-upload').value = '';
        document.getElementById('genuine-preview-container').classList.add('hidden');
        document.getElementById('genuine-file-label').innerText = 'Click to select genuine signature image (PNG, JPG, TIFF)';
        
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
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running Biometric Inference...';
    btn.disabled = true;

    const modelTrackEl = document.getElementById('select-manual-model-track');
    const modelTrack = modelTrackEl ? modelTrackEl.value : 'transformer';

    const formData = new FormData();
    formData.append('customer_reference', custId);
    formData.append('submitted_signature', selectedQueryFile);
    formData.append('mode', mode);
    formData.append('model_track', modelTrack);

    try {
        const data = await apiPost('/api/v1/verifications/verify', formData, true);
        renderManualVerificationResults(data);
    } catch (err) {
        alert(`Verification Error: ${err.message || 'Inference error'}`);
        const banner = document.getElementById('verdict-banner');
        if (banner) {
            banner.className = 'px-4 py-1.5 rounded-full text-sm font-bold bg-rose-950 text-rose-400 border border-rose-800';
            banner.innerText = 'VERIFICATION FAILED: ' + (err.message || 'Error');
        }
    } finally {
        btn.innerHTML = origHtml;
        btn.disabled = false;
    }
}

function renderManualVerificationResults(data) {
    const banner = document.getElementById('verdict-banner');
    const simEl = document.getElementById('res-manual-similarity');
    const distEl = document.getElementById('res-manual-distance');
    const threshEl = document.getElementById('res-manual-threshold');
    const riskEl = document.getElementById('res-manual-risk');
    const tierEl = document.getElementById('res-manual-tier');
    const verifIdEl = document.getElementById('res-manual-verif-id');
    const refCountEl = document.getElementById('res-manual-ref-count');
    const timeEl = document.getElementById('res-manual-timestamp');
    const modeBadge = document.getElementById('res-manual-mode-badge');
    const modelUsedEl = document.getElementById('res-manual-model-used');
    const matchVerdictEl = document.getElementById('res-manual-match-verdict');

    if (simEl) simEl.innerText = formatScore(data.similarity_score);
    if (distEl) distEl.innerText = formatScore(data.euclidean_distance);
    if (threshEl) threshEl.innerText = formatScore(data.threshold_used);
    if (riskEl) riskEl.innerText = formatScore(data.overall_risk_score);
    if (tierEl) tierEl.innerText = `Tier: ${data.risk_level || 'STANDARD'}`;
    if (verifIdEl) verifIdEl.innerText = data.verification_id;
    if (refCountEl) refCountEl.innerText = `${data.reference_count || 1} Specimen(s)`;
    if (timeEl) timeEl.innerText = formatDate(data.timestamp);
    if (modeBadge) modeBadge.innerText = (data.mode === 'gallery') ? 'Mode 2: Customer Gallery Verification' : 'Mode 1: Single Reference Verification';

    // Model track name
    const modelTrackEl = document.getElementById('select-manual-model-track');
    const selectedModelName = modelTrackEl ? modelTrackEl.options[modelTrackEl.selectedIndex].text : 'HF Vision Transformer';
    if (modelUsedEl) modelUsedEl.innerText = selectedModelName;

    // Biometric Result: MATCH / NO MATCH
    const isMatch = Boolean(data.match !== undefined ? data.match : (Number(data.similarity_score) >= Number(data.threshold_used)));
    if (matchVerdictEl) {
        matchVerdictEl.innerText = isMatch ? 'MATCH' : 'NO MATCH';
        matchVerdictEl.className = isMatch ? 'mono font-bold text-emerald-400' : 'mono font-bold text-rose-400';
    }

    if (banner) {
        if (data.decision === 'VERIFIED') {
            banner.className = 'px-4 py-2 rounded-xl text-sm font-bold bg-emerald-950 text-emerald-400 border border-emerald-800 shadow-lg shadow-emerald-950/40 flex items-center gap-2';
            banner.innerHTML = '<i class="fa-solid fa-circle-check text-base"></i> Decision: VERIFIED &bull; Biometric: MATCH';
        } else if (data.decision === 'MANUAL_REVIEW') {
            banner.className = 'px-4 py-2 rounded-xl text-sm font-bold bg-amber-950 text-amber-400 border border-amber-800 shadow-lg shadow-amber-950/40 flex items-center gap-2';
            banner.innerHTML = '<i class="fa-solid fa-triangle-exclamation text-base"></i> Decision: MANUAL REVIEW &bull; Biometric: ' + (isMatch ? 'BORDERLINE' : 'NO MATCH');
        } else {
            banner.className = 'px-4 py-2 rounded-xl text-sm font-bold bg-rose-950 text-rose-400 border border-rose-800 shadow-lg shadow-rose-950/40 flex items-center gap-2';
            banner.innerHTML = '<i class="fa-solid fa-circle-xmark text-base"></i> Decision: REJECTED &bull; Biometric: NO MATCH';
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
