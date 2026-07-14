/**
 * Settings Dialog Modal Module
 */
import { state } from '../state.js';
import { apiSaveSettings } from '../api.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';

let modal;
let elSettingsList;

let elXs;
let elOpenSoll;
let elClosedSoll;

let btnSaveEntry;
let btnDeleteEntry;

let localSollValues = [];

export function initSettingsDialog() {
    modal = document.getElementById('modal-settings');
    elSettingsList = document.getElementById('settings-xsec-list');
    
    elXs = document.getElementById('s-xs');
    elOpenSoll = document.getElementById('s-open-soll');
    elClosedSoll = document.getElementById('s-closed-soll');
    
    btnSaveEntry = document.getElementById('btn-settings-save-entry');
    btnDeleteEntry = document.getElementById('btn-settings-delete-entry');
    // Add change listeners to inputs to toggle Speichern / Ändern button text
    if (elXs) elXs.addEventListener('input', onSettingsInputsChanged);
    if (elXs) elXs.addEventListener('change', onSettingsInputsChanged);
    
    // Save entry button click
    if (btnSaveEntry) {
        btnSaveEntry.addEventListener('click', onSettingsSaveEntryClicked);
    }
    
    // Delete entry button click
    if (btnDeleteEntry) {
        btnDeleteEntry.addEventListener('click', onSettingsDeleteEntryClicked);
    }
    
    // Apply (Speichern & Schließen) settings button click
    const btnApply = document.getElementById('btn-settings-apply');
    if (btnApply) {
        btnApply.addEventListener('click', onSettingsApplyClicked);
    }
}

export function openSettingsModal() {
    localSollValues = JSON.parse(JSON.stringify(state.settings.xsec_soll_values || []));
    
    // Clear inputs
    elXs.value = "";
    elOpenSoll.value = "";
    elClosedSoll.value = "";
    
    onSettingsInputsChanged();
    updateSettingsList();
    openModal(modal);
}

function updateSettingsList() {
    elSettingsList.innerHTML = '';
    
    localSollValues.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item[0]} mm²</td>
            <td>${item[1]} N</td>
            <td>${item[2]} N</td>
        `;
        
        tr.addEventListener('click', () => {
            selectSettingsEntry(index);
        });
        
        elSettingsList.appendChild(tr);
    });
}

function selectSettingsEntry(index) {
    const item = localSollValues[index];
    elXs.value = item[0];
    elOpenSoll.value = item[1];
    elClosedSoll.value = item[2];
    
    // Highlight selected row
    document.querySelectorAll('#settings-xsec-list tr').forEach((tr, i) => {
        if (i === index) tr.classList.add('selected');
        else tr.classList.remove('selected');
    });
    
    onSettingsInputsChanged();
}

function onSettingsInputsChanged() {
    const xs = elXs.value.trim();
    if (!xs) {
        btnSaveEntry.textContent = "Hinzufügen";
        btnDeleteEntry.style.display = "none";
        return;
    }
    
    const exists = localSollValues.some(item => item[0] === xs);
    if (exists) {
        btnSaveEntry.textContent = "Ändern";
        btnDeleteEntry.style.display = "inline-flex";
    } else {
        btnSaveEntry.textContent = "Hinzufügen";
        btnDeleteEntry.style.display = "none";
    }
}

function onSettingsSaveEntryClicked() {
    const xs = elXs.value.trim();
    const openValStr = elOpenSoll.value.trim();
    const closedValStr = elClosedSoll.value.trim();
    
    if (!xs) {
        showToast("Bitte Querschnitt angeben.", "warning");
        return;
    }
    
    const openVal = parseInt(openValStr);
    const closedVal = parseInt(closedValStr);
    
    if (isNaN(openVal) || isNaN(closedVal)) {
        showToast("Bitte nur ganzzahlige Werte für Abzugswerte eingeben.", "warning");
        return;
    }
    
    const existingIndex = localSollValues.findIndex(item => item[0] === xs);
    
    if (existingIndex > -1) {
        // Edit entry
        localSollValues[existingIndex] = [xs, openVal, closedVal];
    } else {
        // Add new entry
        localSollValues.push([xs, openVal, closedVal]);
    }
    
    // Sort by cross section ascending (parse as floats)
    localSollValues.sort((a, b) => parseFloat(a[0]) - parseFloat(b[0]));
    
    updateSettingsList();
    
    // Clear inputs
    elXs.value = "";
    elOpenSoll.value = "";
    elClosedSoll.value = "";
    
    onSettingsInputsChanged();
}

function onSettingsDeleteEntryClicked() {
    const xs = elXs.value.trim();
    if (!xs) return;
    
    localSollValues = localSollValues.filter(item => item[0] !== xs);
    updateSettingsList();
    
    elXs.value = "";
    elOpenSoll.value = "";
    elClosedSoll.value = "";
    
    onSettingsInputsChanged();
}

async function onSettingsApplyClicked() {
    const settingsPayload = {
        xsec_soll_values: localSollValues
    };
    try {
        const res = await apiSaveSettings(settingsPayload);
        if (res.success) {
            showToast("Einstellungen erfolgreich gespeichert und angewendet", "success");
            state.settings = settingsPayload;
            closeModal(modal);
        } else {
            showToast(res.error || "Fehler beim Anwenden der Einstellungen.", "error");
        }
    } catch (e) {
        console.error("Save settings error", e);
    }
}
