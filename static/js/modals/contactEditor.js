/**
 * Contact Editor Modal Module
 */
import { state, copyObject } from '../state.js';
import { apiSaveContact, apiDeleteContact, apiFetchContacts } from '../api.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';
import { populateContacts } from '../views/editor.js';

let modal;
let elRef;
let elProducer;
let elSeries;
let elType;
let elProdNr;
let elXsSelect;
let elToolSelect;
let elSlotSelect;
let elSollInput;
let elXsecList;

let currentContactRef = ""; // If empty, we are creating a new contact
let localCrosssections = {}; // Local cross-sections cache for the active editor session

export function initContactEditor() {
    modal = document.getElementById('modal-contact-editor');
    elRef = document.getElementById('c-refnr');
    elProducer = document.getElementById('c-hersteller');
    elSeries = document.getElementById('c-serie');
    elType = document.getElementById('c-crimp-type');
    elProdNr = document.getElementById('c-hersteller-nr');
    
    elXsSelect = document.getElementById('c-add-xs');
    elToolSelect = document.getElementById('c-add-tool');
    elSlotSelect = document.getElementById('c-add-slot');
    elSollInput = document.getElementById('c-add-soll');
    elXsecList = document.getElementById('contact-xsec-list');

    // Xs dropdown change
    if (elXsSelect) {
        elXsSelect.addEventListener('change', onContactEditorXsChanged);
    }
    
    // Wire Save button
    const btnSave = document.getElementById('btn-save-contact');
    if (btnSave) {
        btnSave.addEventListener('click', onContactEditorSaveClicked);
    }
    
    // Wire Add Cross-section button
    const btnAddXs = document.getElementById('btn-contact-add-xs');
    if (btnAddXs) {
        btnAddXs.addEventListener('click', onContactEditorAddXsClicked);
    }
    
    // Wire radio buttons click (open/closed)
    const radioOpen = document.getElementById('type-open');
    const radioClosed = document.getElementById('type-closed');
    if (radioOpen) radioOpen.addEventListener('change', onContactEditorXsChanged);
    if (radioClosed) radioClosed.addEventListener('change', onContactEditorXsChanged);

    // Wire input changes to enable/disable Save button
    [elRef, elProducer, elSeries, elProdNr].forEach(input => {
        if (input) {
            input.addEventListener('input', checkContactChanges);
        }
    });
    if (radioOpen) radioOpen.addEventListener('change', checkContactChanges);
    if (radioClosed) radioClosed.addEventListener('change', checkContactChanges);

    // Wire listeners to highlight Hinzufügen button when all fields are filled
    [elXsSelect, elToolSelect, elSlotSelect].forEach(select => {
        if (select) {
            select.addEventListener('change', updateAddXsButtonHighlight);
        }
    });
    if (elSollInput) {
        elSollInput.addEventListener('input', updateAddXsButtonHighlight);
    }
}

function updateAddXsButtonHighlight() {
    const btnAddXs = document.getElementById('btn-contact-add-xs');
    if (!btnAddXs) return;
    
    const xs = elXsSelect.value;
    const tool = elToolSelect.value;
    const slot = elSlotSelect.value;
    const soll = elSollInput.value.trim();
    
    const isComplete = xs && tool && slot && soll !== "";
    if (isComplete) {
        btnAddXs.className = 'btn btn-primary';
    } else {
        btnAddXs.className = 'btn btn-secondary';
    }
}

function checkContactChanges() {
    const btnSave = document.getElementById('btn-save-contact');
    if (!btnSave) return;
    
    const ref = elRef.value.trim();
    const producer = elProducer.value.trim();
    const series = elSeries.value.trim();
    const prodNr = elProdNr.value.trim();
    const typeClosed = document.getElementById('type-closed')?.checked || false;
    const crimpType = typeClosed ? "closed" : "open";
    
    if (!currentContactRef) {
        const hasInputs = ref !== "" && producer !== "" && series !== "";
        btnSave.disabled = !hasInputs;
        return;
    }
    
    const c = state.contacts[currentContactRef] || {};
    const changed =
        ref !== currentContactRef ||
        producer !== (c.producer || "") ||
        series !== (c.series || "") ||
        prodNr !== (c.producerNr || "") ||
        crimpType !== (c.crimpType || "open") ||
        JSON.stringify(localCrosssections) !== JSON.stringify(c.crosssection || {});
        
    btnSave.disabled = !changed;
}

export function openContactEditor(ref = "") {
    currentContactRef = ref;
    localCrosssections = {};
    
    // Clear inputs
    elRef.value = "";
    elRef.removeAttribute('disabled');
    elProducer.value = "";
    elSeries.value = "";
    elProdNr.value = "";
    document.getElementById('type-open').checked = true;
    
    // Populate tools dropdown
    populateContactEditorToolsDropdown();
    
    if (ref && state.contacts[ref]) {
        // Editing existing contact
        const c = state.contacts[ref];
        elRef.value = ref;
        elRef.setAttribute('disabled', 'true'); // Ref is unique key
        elProducer.value = c.producer || "";
        elSeries.value = c.series || "";
        elProdNr.value = c.producerNr || "";
        
        if (c.crimpType === "closed") {
            document.getElementById('type-closed').checked = true;
        } else {
            document.getElementById('type-open').checked = true;
        }
        
        localCrosssections = copyObject(c.crosssection || {});
    }
    
    updateContactEditorXsecList();
    populateContactEditorXsecDropdown();
    checkContactChanges();
    updateAddXsButtonHighlight();
    
    openModal(modal);
}

function populateContactEditorToolsDropdown() {
    if (!elToolSelect) return;
    elToolSelect.innerHTML = '<option value="">-- Zange auswählen --</option>';
    
    // Sort tools alphabetically
    const toolRefs = Object.keys(state.tools).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    
    toolRefs.forEach(ref => {
        const t = state.tools[ref];
        const ids = t.IDs && t.IDs.length > 0 ? ` (${t.IDs.join(", ")})` : "";
        const option = document.createElement('option');
        option.value = ref;
        option.textContent = `${t.producer} | ${t.series}${ids}`;
        elToolSelect.appendChild(option);
    });
    
    // Listen to tool change to populate slots dropdown
    elToolSelect.onchange = (e) => {
        populateContactEditorSlotsDropdown(e.target.value);
    };
    
    // Clear slots
    populateContactEditorSlotsDropdown("");
}

function populateContactEditorSlotsDropdown(toolRef) {
    if (!elSlotSelect) return;
    elSlotSelect.innerHTML = '<option value="">-- Slot --</option>';
    
    if (!toolRef || !state.tools[toolRef]) return;
    
    const slots = state.tools[toolRef].slots || [];
    slots.forEach(slot => {
        const option = document.createElement('option');
        option.value = slot;
        option.textContent = slot;
        elSlotSelect.appendChild(option);
    });
}

function populateContactEditorXsecDropdown() {
    if (!elXsSelect) return;
    elXsSelect.innerHTML = '<option value="">-- Querschnitt --</option>';
    
    const settingsVals = state.settings.xsec_soll_values || [];
    settingsVals.forEach(valObj => {
        const xs = valObj[0];
        // Exclude cross-sections already defined in this contact
        if (!localCrosssections[xs]) {
            const option = document.createElement('option');
            option.value = xs;
            option.textContent = `${xs} mm²`;
            elXsSelect.appendChild(option);
        }
    });
    
    onContactEditorXsChanged();
}

function onContactEditorXsChanged() {
    const xs = elXsSelect.value;
    if (!xs) {
        elSollInput.value = "";
        updateAddXsButtonHighlight();
        return;
    }
    
    const isClosed = document.getElementById('type-closed').checked;
    
    // Search in settings
    const settingsVals = state.settings.xsec_soll_values || [];
    const match = settingsVals.find(v => v[0] === xs);
    if (match) {
        // match format: [xs, openSoll, closedSoll]
        elSollInput.value = isClosed ? match[2] : match[1];
    } else {
        elSollInput.value = "";
    }
    updateAddXsButtonHighlight();
}

function onContactEditorAddXsClicked() {
    const xs = elXsSelect.value;
    const tool = elToolSelect.value;
    const slot = elSlotSelect.value;
    const soll = parseInt(elSollInput.value) || 0;
    
    if (!xs) {
        showToast("Bitte Querschnitt auswählen.", "warning");
        return;
    }
    if (!tool) {
        showToast("Bitte Zange auswählen.", "warning");
        return;
    }
    if (!slot) {
        showToast("Bitte Slot auswählen.", "warning");
        return;
    }
    
    localCrosssections[xs] = {
        tool: tool,
        slot: slot,
        soll: soll
    };
    
    updateContactEditorXsecList();
    populateContactEditorXsecDropdown();
    checkContactChanges();
}

function updateContactEditorXsecList() {
    elXsecList.innerHTML = '';
    const sortedXsecs = Object.keys(localCrosssections).sort((a, b) => parseFloat(a) - parseFloat(b));
    
    if (sortedXsecs.length === 0) {
        elXsecList.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-secondary); padding: 12px;">Keine Querschnitte definiert.</td></tr>`;
        return;
    }
    
    sortedXsecs.forEach(xs => {
        const item = localCrosssections[xs];
        const tr = document.createElement('tr');
        
        const toolObj = state.tools[item.tool] || {};
        const toolIDs = toolObj.IDs ? toolObj.IDs.join(", ") : item.tool;
        const toolLabel = toolObj.producer ? `${toolIDs} (${toolObj.producer})` : toolIDs;
        
        tr.innerHTML = `
            <td>${xs} mm²</td>
            <td>${toolLabel}</td>
            <td>${item.slot}</td>
            <td>${item.soll} N</td>
            <td class="row-actions">
                <button class="action-icon-btn danger btn-delete-xs" data-xs="${xs}" title="Löschen">&times;</button>
            </td>
        `;
        
        tr.querySelector('.btn-delete-xs').addEventListener('click', (e) => {
            const deleteXs = e.target.getAttribute('data-xs');
            delete localCrosssections[deleteXs];
            updateContactEditorXsecList();
            populateContactEditorXsecDropdown();
            checkContactChanges();
        });
        
        elXsecList.appendChild(tr);
    });
}

async function onContactEditorSaveClicked() {
    const ref = elRef.value.trim();
    const producer = elProducer.value.trim();
    const series = elSeries.value.trim();
    const crimpType = document.getElementById('type-closed').checked ? "closed" : "open";
    const producerNr = elProdNr.value.trim();
    
    if (!ref) {
        showToast("Bitte Artikelnummer (Referenz) angeben.", "warning");
        return;
    }
    if (!producer) {
        showToast("Bitte Hersteller angeben.", "warning");
        return;
    }
    if (!series) {
        showToast("Bitte Serie/Bezeichnung angeben.", "warning");
        return;
    }
    
    const contactPayload = {
        refNr: ref,
        producer: producer,
        series: series,
        crimpType: crimpType,
        producerNr: producerNr,
        crosssection: localCrosssections
    };
    
    try {
        const res = await apiSaveContact(contactPayload, currentContactRef);
        if (res.success) {
            showToast("Kontakt erfolgreich gespeichert", "success");
            closeModal(modal);
            
            // Reload contacts list
            const updated = await apiFetchContacts();
            state.contacts = updated;
            populateContacts();
        } else {
            showToast(res.error || "Fehler beim Speichern des Kontakts.", "error");
        }
    } catch (e) {
        console.error("Save contact failed", e);
    }
}

export async function deleteContact(ref) {
    if (!confirm(`Soll der Kontakt "${ref}" gelöscht werden?`)) {
        return;
    }
    try {
        const ok = await apiDeleteContact(ref);
        if (ok) {
            showToast("Kontakt erfolgreich gelöscht", "success");
            const updated = await apiFetchContacts();
            state.contacts = updated;
            
            if (state.selectedContactRef === ref) {
                state.selectedContactRef = "";
            }
            populateContacts();
        } else {
            showToast("Fehler beim Löschen des Kontakts.", "error");
        }
    } catch (e) {
        console.error("Delete contact error", e);
    }
}
