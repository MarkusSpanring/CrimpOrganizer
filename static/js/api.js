/**
 * API Service for Backend Communication
 */
import { showToast } from './toast.js';

async function request(url, options = {}) {
    try {
        const res = await fetch(url, options);
        if (!res.ok) {
            let errMsg = `Request failed: ${res.statusText}`;
            try {
                const errData = await res.json();
                if (errData && errData.error) errMsg = errData.error;
            } catch (e) {}
            throw new Error(errMsg);
        }
        return res;
    } catch (e) {
        showToast(e.message || "Netzwerkfehler", "error");
        throw e;
    }
}

// Contacts
export async function apiFetchContacts() {
    const res = await request('/api/contacts');
    return await res.json();
}

export async function apiSaveContact(contact, oldRef) {
    const url = `/api/contacts?oldRef=${encodeURIComponent(oldRef)}`;
    const res = await request(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(contact)
    });
    return await res.json();
}

export async function apiDeleteContact(ref) {
    const url = `/api/contacts/${encodeURIComponent(ref)}`;
    const res = await request(url, { method: 'DELETE' });
    return res.ok;
}

// Tools
export async function apiFetchTools() {
    const res = await request('/api/tools');
    return await res.json();
}

export async function apiSaveTool(tool, oldRef) {
    const url = `/api/tools?oldRef=${encodeURIComponent(oldRef)}`;
    const res = await request(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(tool)
    });
    return await res.json();
}

export async function apiDeleteTool(ref) {
    const url = `/api/tools/${encodeURIComponent(ref)}`;
    const res = await request(url, { method: 'DELETE' });
    return res.ok;
}

// Settings
export async function apiFetchSettings() {
    const res = await request('/api/settings');
    return await res.json();
}

export async function apiSaveSettings(settingsData) {
    const res = await request('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settingsData)
    });
    return await res.json();
}

// Instructions
export async function apiFetchInstructions() {
    const res = await request('/api/instructions');
    return await res.json();
}

export async function apiSaveInstructions(payload) {
    const res = await request('/api/instructions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    return await res.json();
}

export async function apiDeleteInstructions(schemeKey) {
    const url = `/api/instructions/${encodeURIComponent(schemeKey)}`;
    const res = await request(url, { method: 'DELETE' });
    return res.ok;
}

// Orders
export async function apiFetchOrders() {
    const res = await request('/api/orders');
    return await res.json();
}

export async function apiExportPdf(exportPayload) {
    const res = await request('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(exportPayload)
    });
    return await res.blob();
}

export async function apiTriggerUpdate() {
    const res = await request('/api/update', {
        method: 'POST'
    });
    return await res.json();
}
