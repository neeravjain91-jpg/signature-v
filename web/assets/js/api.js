/**
 * SIGNATURE VMAKE — API Client & Formatting Helpers
 * Standardized client for all /api/v1/ endpoints.
 */

async function apiGet(endpoint) {
    const targetUrl = (API_BASE || '') + endpoint;
    const response = await fetch(targetUrl);
    if (!response.ok) {
        let errText = '';
        try {
            const errJson = await response.json();
            errText = errJson.detail || JSON.stringify(errJson);
        } catch (_) {
            errText = await response.text();
        }
        const error = new Error(errText || `HTTP ${response.status}`);
        error.status = response.status;
        throw error;
    }
    return response.json();
}

async function apiPost(endpoint, data, isFormData = false) {
    const targetUrl = (API_BASE || '') + endpoint;
    const options = {
        method: 'POST'
    };

    if (isFormData) {
        options.body = data;
    } else {
        options.headers = { 'Content-Type': 'application/json' };
        options.body = JSON.stringify(data);
    }

    const response = await fetch(targetUrl, options);
    if (!response.ok) {
        let errText = '';
        try {
            const errJson = await response.json();
            errText = errJson.detail || JSON.stringify(errJson);
        } catch (_) {
            errText = await response.text();
        }
        const error = new Error(errText || `HTTP ${response.status}`);
        error.status = response.status;
        throw error;
    }
    return response.json();
}

function formatScore(score, decimals = 4) {
    if (score === undefined || score === null || isNaN(score)) return '--';
    return Number(score).toFixed(decimals);
}

function formatCurrency(amount, currency = 'USD') {
    if (amount === undefined || amount === null || isNaN(amount)) return '$0.00';
    return '$' + Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function formatDate(isoString) {
    if (!isoString) return '--';
    try {
        const d = new Date(isoString);
        return d.toLocaleTimeString() + ' (' + d.toLocaleDateString() + ')';
    } catch (_) {
        return isoString;
    }
}
