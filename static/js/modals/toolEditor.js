/**
 * Tool Editor Modal Module
 */
import { state, copyObject } from '../state.js';
import { apiSaveTool, apiDeleteTool, apiFetchTools } from '../api.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';
import { populateTools } from '../views/editor.js';

let modal;
let modalTitle;

// Inputs
let elProducer;
let elSeries;
let elProdNr;

// Lists container
let elSlotsSelect;
let elIdsSelect;

// Dynamic adding
let elNewSlotAwg;
let elNewSlotXs;
let elNewId;

// Save/Delete Buttons
let btnSave;
let btnDelete;

let currentToolRef = ""; // If empty, we are creating a new tool
let isEditingUnlocked = false; // "Bearbeiten" label toggle indicator

let localSlots = [];
let localIds = [];

export function initToolEditor() {
    modal = document.getElementById('modal-tool-editor');
    modalTitle = document.getElementById('modal-tool-title');
    elProducer = document.getElementById('t-hersteller');
    elSeries = document.getElementById('t-serie');
    elProdNr = document.getElementById('t-hersteller-nr');
    elSlotsSelect = document.getElementById('t-slots');
    elIdsSelect = document.getElementById('t-ids');
    elNewSlotAwg = document.getElementById('t-new-slot-awg');
    elNewSlotXs = document.getElementById('t-new-slot-xs');
    elNewId = document.getElementById('t-new-id');
    btnSave = document.getElementById('btn-tool-save');
    btnDelete = document.getElementById('btn-tool-delete');
    // Add slot click
    const btnAddSlot = document.getElementById('btn-tool-add-slot');
    if (btnAddSlot) {
        btnAddSlot.addEventListener('click', onToolEditorAddSlotClicked);
    }
    
    // Add ID click
    const btnAddId = document.getElementById('btn-tool-add-id');
    if (btnAddId) {
        btnAddId.addEventListener('click', onToolEditorAddIdClicked);
    }
    
    // Save button click
    if (btnSave) {
        btnSave.addEventListener('click', onToolEditorSaveClicked);
    }
    
    // Delete tool button click
    if (btnDelete) {
        btnDelete.addEventListener('click', onToolEditorDeleteClicked);
    }

    // Wire input changes to enable/disable Save button
    [elProducer, elSeries, elProdNr].forEach(input => {
        if (input) {
            input.addEventListener('input', checkToolChanges);
        }
    });
}

function checkToolChanges() {
    if (!btnSave) return;
    const producer = elProducer.value.trim();
    const series = elSeries.value.trim();
    const producerNr = elProdNr.value.trim();

    if (!currentToolRef) {
        // New tool: require producer, series, producerNr, ≥1 slot, ≥1 ID (matching legacy)
        const hasInputs = producer !== "" && series !== "" && producerNr !== ""
                          && localSlots.length > 0 && localIds.length > 0;
        btnSave.disabled = !hasInputs;
        return;
    }

    const t = state.tools[currentToolRef] || {};
    // Compare against normalized stored slots for a stable diff
    const changed =
        producer !== (t.producer || "") ||
        series !== (t.series || "") ||
        producerNr !== (t.producerNr || "") ||
        JSON.stringify(localSlots) !== JSON.stringify((t.slots || []).map(parseSlot)) ||
        JSON.stringify(localIds) !== JSON.stringify(t.IDs || []);

    btnSave.disabled = !changed;
}

function formatSlot(slot) {
    if (Array.isArray(slot)) {
        const awg = slot[0] ? `AWG ${slot[0]}` : "";
        const met = slot[1] ? `${slot[1]} mm²` : "";
        if (awg && met) {
            return `${awg} | ${met}`;
        }
        return awg || met;
    }
    return String(slot);
}

/**
 * Parse any slot representation into a canonical [awg, met] string pair.
 * Handles legacy tuple format, flat strings like "AWG 20 | 0.50 mm²", etc.
 */
function parseSlot(slot) {
    if (Array.isArray(slot) && slot.length >= 2) {
        return [String(slot[0]), String(slot[1])];
    }
    const str = String(slot).trim();
    if (str.includes(" | ")) {
        const parts = str.split(" | ", 2);
        return [parts[0].replace("AWG ", "").trim(), parts[1].replace(" mm²", "").trim()];
    }
    if (str.startsWith("AWG ")) {
        return [str.replace("AWG ", "").trim(), ""];
    }
    if (str.endsWith(" mm²")) {
        return ["", str.replace(" mm²", "").trim()];
    }
    return [str, ""];
}

export function openToolEditor(ref = "") {
    currentToolRef = ref;
    
    // Clear inputs
    elProducer.value = "";
    elSeries.value = "";
    elProdNr.value = "";
    elNewSlotAwg.value = "";
    elNewSlotXs.value = "";
    elNewId.value = "";
    
    localSlots = [];
    localIds = [];
    
    if (ref && state.tools[ref]) {
        // Editing existing tool
        const t = state.tools[ref];
        modalTitle.textContent = `Crimpzange: ${t.producer} | ${t.series}`;

        elProducer.value = t.producer || "";
        elSeries.value = t.series || "";
        elProdNr.value = t.producerNr || "";

        // Normalize all slots to [awg, met] pairs regardless of their stored format
        localSlots = (t.slots || []).map(parseSlot);
        localIds = copyObject(t.IDs || []);

        btnSave.textContent = "Speichern";
        btnDelete.style.display = "inline-flex";
    } else {
        // Creating new tool
        modalTitle.textContent = "Neue Crimpzange anlegen";
        btnSave.textContent = "Speichern";
        btnDelete.style.display = "none";
    }
    
    updateToolLists();
    checkToolChanges();
    openModal(modal);
}

function updateToolLists() {
    // Populate slots list div — localSlots stores [awg, met] pairs
    elSlotsSelect.innerHTML = '';
    localSlots.forEach((slot, idx) => {
        const row = document.createElement('div');
        row.className = 'list-item-row';
        row.innerHTML = `
            <span>${formatSlot(slot)}</span>
            <button class="btn-delete-item" title="Löschen">&times;</button>
        `;
        row.querySelector('.btn-delete-item').addEventListener('click', () => {
            localSlots.splice(idx, 1);
            updateToolLists();
            checkToolChanges();
        });
        elSlotsSelect.appendChild(row);
    });

    // Populate IDs list div
    elIdsSelect.innerHTML = '';
    localIds.forEach((id, idx) => {
        const row = document.createElement('div');
        row.className = 'list-item-row';
        row.innerHTML = `
            <span>${id}</span>
            <button class="btn-delete-item" title="Löschen">&times;</button>
        `;
        row.querySelector('.btn-delete-item').addEventListener('click', () => {
            localIds.splice(idx, 1);
            updateToolLists();
            checkToolChanges();
        });
        elIdsSelect.appendChild(row);
    });
}

function onToolEditorAddSlotClicked() {
    const awg = elNewSlotAwg.value.trim();
    const xs = elNewSlotXs.value.trim();

    if (!awg && !xs) {
        showToast("Bitte Slot-Bezeichnung oder Querschnitt eingeben.", "warning");
        return;
    }

    // Store as [awg, met] pair — duplicate check on normalized form
    const newPair = [awg, xs];
    const exists = localSlots.some(s => s[0] === awg && s[1] === xs);
    if (exists) {
        showToast("Slot existiert bereits.", "warning");
        return;
    }

    localSlots.push(newPair);
    updateToolLists();
    checkToolChanges();

    elNewSlotAwg.value = "";
    elNewSlotXs.value = "";
}

function onToolEditorAddIdClicked() {
    const newId = elNewId.value.trim();
    if (!newId) {
        showToast("Bitte Zangen-Identifikationsnummer eingeben.", "warning");
        return;
    }
    
    if (localIds.includes(newId)) {
        showToast("Identifikationsnummer existiert bereits.", "warning");
        return;
    }
    
    localIds.push(newId);
    updateToolLists();
    checkToolChanges();
    elNewId.value = "";
}

async function onToolEditorSaveClicked() {
    const producer = elProducer.value.trim();
    const series = elSeries.value.trim();
    const producerNr = elProdNr.value.trim();

    if (!producer) {
        showToast("Bitte Hersteller angeben.", "warning");
        return;
    }
    if (!series) {
        showToast("Bitte Zangenserie angeben.", "warning");
        return;
    }
    if (!producerNr) {
        showToast("Bitte Hersteller-Artikelnummer angeben.", "warning");
        return;
    }
    if (localSlots.length === 0) {
        showToast("Bitte mindestens einen Einsatz (Slot) hinzufügen.", "warning");
        return;
    }
    if (localIds.length === 0) {
        showToast("Bitte mindestens eine Identifikationsnummer hinzufügen.", "warning");
        return;
    }

    const toolPayload = {
        producer: producer,
        series: series,
        producerNr: producerNr,
        slots: localSlots,   // sent as [awg, met] pairs; backend normalizes on write
        IDs: localIds
    };

    try {
        const res = await apiSaveTool(toolPayload, currentToolRef);
        if (res.success) {
            showToast("Zange erfolgreich gespeichert", "success");
            closeModal(modal);

            // Reload tools list
            const updated = await apiFetchTools();
            state.tools = updated;
            populateTools();
        } else {
            showToast(res.error || "Fehler beim Speichern der Zange.", "error");
        }
    } catch (e) {
        console.error("Save tool failed", e);
    }
}

export async function onToolEditorDeleteClicked() {
    if (!currentToolRef) return;
    if (!confirm(`Soll die Crimpzange "${currentToolRef}" gelöscht werden?`)) {
        return;
    }
    try {
        const ok = await apiDeleteTool(currentToolRef);
        if (ok) {
            showToast("Crimpzange erfolgreich gelöscht", "success");
            closeModal(modal);
            
            // Reload tools list
            const updated = await apiFetchTools();
            state.tools = updated;
            
            if (state.selectedToolRef === currentToolRef) {
                state.selectedToolRef = "";
            }
            populateTools();
        } else {
            showToast("Fehler beim Löschen der Zange.", "error");
        }
    } catch (e) {
        console.error("Delete tool error", e);
    }
}
