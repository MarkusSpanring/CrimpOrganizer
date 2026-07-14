/**
 * Editor View Module
 * Handles workspace setup, contacts listing, crimp tool selections,
 * annotation workflow, and instruction tables.
 */
import { state, copyObject } from '../state.js';
import { apiSaveInstructions, apiFetchInstructions } from '../api.js';
import { openContactEditor, deleteContact } from '../modals/contactEditor.js';
import { openToolEditor } from '../modals/toolEditor.js';
import { openAnnotationModal, openReannotateModal } from '../modals/annotate.js';
import { openOrderDetailsModal } from '../modals/orderDetails.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';
import { showContextMenu } from '../contextMenu.js';
import { switchView } from '../router.js';

// DOM Elements
let elContactsTable;
let elToolsTable;
let elToolSummaryTable;
let elInstructionsTable;

let elFilterBanner;
let elFilterName;
let btnClearFilter;

let btnSaveDraft;
let btnPrintEditor;
let btnClearEditor;

let elSchemeNr;
let elSchemeRev;

export function initEditor() {
    elContactsTable = document.getElementById('contacts-table-body');
    elToolsTable = document.getElementById('tools-table-body');
    elToolSummaryTable = document.getElementById('tool-summary-body');
    elInstructionsTable = document.getElementById('instructions-table-body');
    elFilterBanner = document.getElementById('filter-banner');
    elFilterName = document.getElementById('filter-name');
    btnClearFilter = document.getElementById('btn-clear-filter');
    btnSaveDraft = document.getElementById('btn-save-draft');
    btnPrintEditor = document.getElementById('btn-print-editor');
    btnClearEditor = document.getElementById('btn-clear-editor');
    elSchemeNr = document.getElementById('scheme-nr');
    elSchemeRev = document.getElementById('scheme-rev');

    // Contact list controls
    const searchContact = document.getElementById('search-contact');
    if (searchContact) {
        searchContact.addEventListener('input', (e) => {
            populateContacts(e.target.value);
        });
    }

    const btnNewContact = document.getElementById('btn-new-contact');
    if (btnNewContact) {
        btnNewContact.addEventListener('click', () => openContactEditor());
    }

    // Tool list controls
    const searchTool = document.getElementById('search-tool');
    if (searchTool) {
        searchTool.addEventListener('input', (e) => {
            populateTools(e.target.value);
        });
    }

    const btnNewTool = document.getElementById('btn-new-tool');
    if (btnNewTool) {
        btnNewTool.addEventListener('click', () => openToolEditor());
    }

    // Clear filter banner
    if (btnClearFilter) {
        btnClearFilter.addEventListener('click', () => {
            state.selectedToolRef = "";
            elFilterBanner.style.display = "none";
            populateContacts();
        });
    }

    // Workspace buttons
    if (btnSaveDraft) {
        btnSaveDraft.addEventListener('click', onSaveDraftClicked);
    }
    if (btnPrintEditor) {
        btnPrintEditor.addEventListener('click', () => {
            if (Object.keys(state.fullInstructions).length > 0) {
                openOrderDetailsModal();
            }
        });
    }
    if (btnClearEditor) {
        btnClearEditor.addEventListener('click', clearEditor);
    }

    // Deselect contact by clicking empty space
    const colContacts = document.getElementById('col-contacts');
    if (colContacts) {
        colContacts.addEventListener('click', (e) => {
            if (e.target.tagName !== 'TD' && e.target.tagName !== 'BUTTON' && !e.target.closest('button')) {
                state.selectedContactRef = "";
                document.querySelectorAll('#contacts-table-body tr').forEach(r => r.classList.remove('selected'));
                populateTools();
            }
        });
    }

    // Wire context menus clicks
    wireContextMenus();
}

function wireContextMenus() {
    // Contacts right click
    if (elContactsTable) {
        elContactsTable.addEventListener('contextmenu', (e) => {
            const tr = e.target.closest('tr');
            if (!tr) return;
            e.preventDefault();
            
            const ref = tr.getAttribute('data-ref');
            state.activeCtxContact = ref;
            
            const menu = document.getElementById('contact-context-menu');
            showContextMenu(menu, e.clientX, e.clientY);
        });
    }
    
    // Tools right click
    if (elToolsTable) {
        elToolsTable.addEventListener('contextmenu', (e) => {
            const tr = e.target.closest('tr');
            if (!tr) return;
            e.preventDefault();
            
            const ref = tr.getAttribute('data-ref');
            state.activeCtxTool = ref;
            
            const menu = document.getElementById('tool-context-menu');
            showContextMenu(menu, e.clientX, e.clientY);
        });
    }
    
    // Instructions right click
    if (elInstructionsTable) {
        elInstructionsTable.addEventListener('contextmenu', (e) => {
            const tr = e.target.closest('tr');
            if (!tr) return;
            e.preventDefault();
            
            const idx = parseInt(tr.getAttribute('data-idx'));
            state.activeCtxInstruction = idx;
            
            const menu = document.getElementById('instruction-context-menu');
            showContextMenu(menu, e.clientX, e.clientY);
        });
    }
    
    // Wire context menu items
    const ctxEditContact = document.getElementById('ctx-edit-contact');
    if (ctxEditContact) ctxEditContact.onclick = () => openContactEditor(state.activeCtxContact);
    
    const ctxDeleteContact = document.getElementById('ctx-delete-contact');
    if (ctxDeleteContact) ctxDeleteContact.onclick = () => deleteContact(state.activeCtxContact);
    
    const ctxEditTool = document.getElementById('ctx-edit-tool');
    if (ctxEditTool) ctxEditTool.onclick = () => openToolEditor(state.activeCtxTool);
    
    const ctxDeleteTool = document.getElementById('ctx-delete-tool');
    if (ctxDeleteTool) ctxDeleteTool.onclick = () => {
        openToolEditor(state.activeCtxTool);
        setTimeout(() => {
            const btnDel = document.getElementById('btn-tool-delete');
            if (btnDel) btnDel.click();
        }, 150);
    };
    
    const ctxEditInstruction = document.getElementById('ctx-edit-instruction');
    if (ctxEditInstruction) ctxEditInstruction.onclick = () => openReannotateModal(state.activeCtxInstruction);
    
    const ctxDeleteInstruction = document.getElementById('ctx-delete-instruction');
    if (ctxDeleteInstruction) ctxDeleteInstruction.onclick = () => removeInstruction(state.activeCtxInstruction);
}

export function populateContacts(searchPattern = "") {
    elContactsTable.innerHTML = '';
    
    const thead = document.getElementById('contacts-thead');
    if (thead) {
        if (state.selectedToolRef) {
            thead.innerHTML = `
                <tr>
                    <th style="width: 30%;">RefNr</th>
                    <th style="width: 30%;">Serie</th>
                    <th style="width: 40%; text-align: right;">Querschnitt</th>
                </tr>
            `;
        } else {
            thead.innerHTML = `
                <tr>
                    <th style="width: 30%;">RefNr</th>
                    <th style="width: 30%;">Hersteller</th>
                    <th style="width: 25%;">Serie</th>
                    <th style="width: 15%; text-align: right;">Aktion</th>
                </tr>
            `;
        }
    }
    
    // Sort contacts alphabetically
    const refs = Object.keys(state.contacts).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    
    let count = 0;
    refs.forEach(ref => {
        const c = state.contacts[ref];
        
        // Search filter (RefNr, producer, series)
        if (searchPattern) {
            const match = ref.toLowerCase().includes(searchPattern.toLowerCase()) ||
                          (c.producer || "").toLowerCase().includes(searchPattern.toLowerCase()) ||
                          (c.series || "").toLowerCase().includes(searchPattern.toLowerCase());
            if (!match) return;
        }
        
        // Tool-based filter (active selectedToolRef in Phase 2/3)
        if (state.selectedToolRef) {
            const cross = c.crosssection || {};
            Object.keys(cross).forEach(xs => {
                if (cross[xs].tool === state.selectedToolRef) {
                    count++;
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-ref', ref);
                    
                    tr.innerHTML = `
                        <td style="font-weight: 600;">${ref}</td>
                        <td>${c.series || ''}</td>
                        <td class="row-actions text-right">
                            <button class="btn btn-secondary btn-sm btn-add-instruction" style="padding: 2px 8px;">+ ${xs} mm² hinzufügen</button>
                        </td>
                    `;
                    
                    tr.querySelector('.btn-add-instruction').addEventListener('click', (e) => {
                        e.stopPropagation();
                        addInstructionKey(`${xs}#${ref}`);
                    });
                    
                    tr.addEventListener('click', () => {
                        addInstructionKey(`${xs}#${ref}`);
                    });
                    
                    elContactsTable.appendChild(tr);
                }
            });
            return;
        }
        
        count++;
        const tr = document.createElement('tr');
        tr.setAttribute('data-ref', ref);
        if (ref === state.selectedContactRef) {
            tr.className = 'selected';
        }
        
        tr.innerHTML = `
            <td style="font-weight: 600;">${ref}</td>
            <td>${c.producer || ''}</td>
            <td>${c.series || ''}</td>
            <td class="row-actions text-right">
                <button class="action-icon-btn btn-edit-contact" title="Bearbeiten">✏️</button>
                <button class="action-icon-btn danger btn-delete-contact" title="Löschen">🗑️</button>
            </td>
        `;
        
        tr.querySelector('.btn-edit-contact').addEventListener('click', (e) => {
            e.stopPropagation();
            openContactEditor(ref);
        });
        
        tr.querySelector('.btn-delete-contact').addEventListener('click', (e) => {
            e.stopPropagation();
            deleteContact(ref);
        });
        
        tr.addEventListener('click', () => {
            selectContact(ref);
        });
        
        tr.addEventListener('dblclick', () => {
            openContactEditor(ref);
        });
        
        elContactsTable.appendChild(tr);
    });
    
    if (count === 0) {
        elContactsTable.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine Kontakte gefunden.</td></tr>`;
    }
}

export function selectContact(ref) {
    if (state.selectedContactRef === ref) {
        state.selectedContactRef = "";
    } else {
        state.selectedContactRef = ref;
        state.selectedToolRef = "";
        const elFilterBanner = document.getElementById('filter-banner');
        if (elFilterBanner) elFilterBanner.style.display = "none";
    }
    
    document.querySelectorAll('#contacts-table-body tr').forEach(tr => {
        if (tr.getAttribute('data-ref') === state.selectedContactRef) {
            tr.classList.add('selected');
        } else {
            tr.classList.remove('selected');
        }
    });
    
    populateTools();
}

export function populateTools(searchPattern = "") {
    elToolsTable.innerHTML = '';
    
    const thead = document.getElementById('tools-thead');
    if (thead) {
        if (state.selectedContactRef) {
            thead.innerHTML = `
                <tr>
                    <th style="width: 25%;">Hersteller</th>
                    <th style="width: 25%;">Serie</th>
                    <th style="width: 20%;">IDs</th>
                    <th style="width: 30%; text-align: right;">Querschnitt</th>
                </tr>
            `;
        } else {
            thead.innerHTML = `
                <tr>
                    <th style="width: 30%;">Hersteller</th>
                    <th style="width: 30%;">Serie</th>
                    <th style="width: 25%;">IDs</th>
                    <th style="width: 15%; text-align: right;">Aktion</th>
                </tr>
            `;
        }
    }
    
    const toolRefs = Object.keys(state.tools).sort((a, b) => a.toLowerCase().localeCompare(b.toLowerCase()));
    let count = 0;
    
    toolRefs.forEach(ref => {
        const t = state.tools[ref];
        
        if (searchPattern) {
            const match = (t.producer || "").toLowerCase().includes(searchPattern.toLowerCase()) ||
                          (t.series || "").toLowerCase().includes(searchPattern.toLowerCase()) ||
                          (t.IDs || []).some(id => id.toLowerCase().includes(searchPattern.toLowerCase()));
            if (!match) return;
        }
        
        // If a contact is selected, filter tools to only show tools assigned to this contact
        if (state.selectedContactRef) {
            const c = state.contacts[state.selectedContactRef];
            if (c) {
                const cross = c.crosssection || {};
                const sortedXs = Object.keys(cross).sort((a, b) => parseFloat(a) - parseFloat(b));
                
                sortedXs.forEach(xs => {
                    const item = cross[xs];
                    const toolRef = item.tool;
                    if (toolRef !== ref) return;
                    
                    count++;
                    const tr = document.createElement('tr');
                    tr.setAttribute('data-ref', toolRef);
                    
                    const ids = t.IDs && t.IDs.length > 0 ? t.IDs.join(", ") : "";
                    tr.innerHTML = `
                        <td style="font-weight: 600;">${t.producer}</td>
                        <td>${t.series}</td>
                        <td>${ids}</td>
                        <td class="row-actions text-right">
                            <button class="btn btn-secondary btn-sm btn-add-instruction" style="padding: 2px 8px;">+ ${xs} mm² hinzufügen</button>
                        </td>
                    `;
                    
                    tr.querySelector('.btn-add-instruction').addEventListener('click', (e) => {
                        e.stopPropagation();
                        addInstructionKey(`${xs}#${state.selectedContactRef}`);
                    });
                    
                    tr.addEventListener('click', () => {
                        addInstructionKey(`${xs}#${state.selectedContactRef}`);
                    });
                    
                    elToolsTable.appendChild(tr);
                });
            }
            return;
        }
        
        count++;
        const tr = document.createElement('tr');
        tr.setAttribute('data-ref', ref);
        if (ref === state.selectedToolRef) {
            tr.className = 'selected';
        }
        
        const ids = t.IDs && t.IDs.length > 0 ? t.IDs.join(", ") : "";
        tr.innerHTML = `
            <td style="font-weight: 600;">${t.producer}</td>
            <td>${t.series}</td>
            <td>${ids}</td>
            <td class="row-actions text-right">
                <button class="action-icon-btn btn-edit-tool" title="Bearbeiten">✏️</button>
                <button class="action-icon-btn danger btn-delete-tool" title="Löschen">🗑️</button>
            </td>
        `;
        
        tr.querySelector('.btn-edit-tool').addEventListener('click', (e) => {
            e.stopPropagation();
            openToolEditor(ref);
        });
        
        tr.querySelector('.btn-delete-tool').addEventListener('click', (e) => {
            e.stopPropagation();
            openToolEditor(ref);
            setTimeout(() => {
                const btnDel = document.getElementById('btn-tool-delete');
                if (btnDel) btnDel.click();
            }, 150);
        });
        
        tr.addEventListener('click', () => {
            selectTool(ref);
        });
        
        tr.addEventListener('dblclick', () => {
            openToolEditor(ref);
        });
        
        elToolsTable.appendChild(tr);
    });
    
    if (count === 0) {
        elToolsTable.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine Werkzeuge gefunden.</td></tr>`;
    }
}

export function selectTool(ref) {
    if (state.selectedToolRef === ref) {
        state.selectedToolRef = "";
        elFilterBanner.style.display = "none";
    } else {
        state.selectedToolRef = ref;
        state.selectedContactRef = ""; // Clear contact selection
        
        const t = state.tools[ref];
        const ids = t.IDs && t.IDs.length > 0 ? ` (z.B. ${t.IDs.join(", ")})` : "";
        elFilterName.textContent = `${t.producer} | ${t.series}${ids}`;
        elFilterBanner.style.display = "flex";
    }
    
    document.querySelectorAll('#tools-table-body tr').forEach(tr => {
        if (tr.getAttribute('data-ref') === state.selectedToolRef) {
            tr.classList.add('selected');
        } else {
            tr.classList.remove('selected');
        }
    });
    
    // Refresh contact list highlights and trigger contacts search filter refresh
    document.querySelectorAll('#contacts-table-body tr').forEach(tr => {
        tr.classList.remove('selected');
    });
    
    populateContacts();
}

function addInstructionKey(key) {
    if (!state.fullInstructions[key]) {
        openAnnotationModal([key]);
    } else {
        showToast("Bereits in der Anleitung vorhanden.", "info");
    }
}

export function populateCrimpInstructions() {
    elInstructionsTable.innerHTML = '';
    const entries = Object.keys(state.fullInstructions);
    
    if (entries.length === 0) {
        elInstructionsTable.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-secondary); padding: 20px;">Noch keine Zuweisungen vorgenommen.</td></tr>`;
    } else {
        // Sort entries by position value if numeric, or alphabetically
        entries.sort((a, b) => {
            const posA = state.fullInstructions[a].pos || "";
            const posB = state.fullInstructions[b].pos || "";
            const numA = parseInt(posA);
            const numB = parseInt(posB);
            
            if (!isNaN(numA) && !isNaN(numB)) return numA - numB;
            return posA.localeCompare(posB);
        });
        
        entries.forEach((entry, idx) => {
            const [xs, contactRef] = entry.split("#");
            const details = state.fullInstructions[entry];
            const pos = details.pos || "";
            const housing = details.name || "";
            
            const contactObj = state.contacts[contactRef] || {};
            const crimpung = contactObj.series ? `${contactRef} / ${contactObj.series}` : contactRef;
            
            const tr = document.createElement('tr');
            tr.setAttribute('data-idx', idx);
            if (idx === state.selectedInstructionRow) {
                tr.className = 'selected';
            }
            
            tr.innerHTML = `
                <td>${pos}</td>
                <td>${crimpung}</td>
                <td>${xs} mm²</td>
                <td>${housing}</td>
                <td class="row-actions">
                    <button class="action-icon-btn btn-edit-instr" data-idx="${idx}" title="Bearbeiten">✏️</button>
                    <button class="action-icon-btn danger btn-delete-instr" data-idx="${idx}" title="Entfernen">🗑️</button>
                </td>
            `;
            
            // Edit row click
            tr.querySelector('.btn-edit-instr').addEventListener('click', (e) => {
                e.stopPropagation();
                openReannotateModal(idx);
            });
            
            // Delete row click
            tr.querySelector('.btn-delete-instr').addEventListener('click', (e) => {
                e.stopPropagation();
                removeInstruction(idx);
            });
            
            tr.addEventListener('click', () => {
                state.selectedInstructionRow = idx;
                document.querySelectorAll('#instructions-table-body tr').forEach((row, rIdx) => {
                    if (rIdx === idx) row.classList.add('selected');
                    else row.classList.remove('selected');
                });
            });
            
            elInstructionsTable.appendChild(tr);
        });
    }
    
    updateSaveDraftButtonState();
}

export function removeInstruction(idx) {
    const entries = Object.keys(state.fullInstructions);
    if (idx >= 0 && idx < entries.length) {
        const key = entries[idx];
        delete state.fullInstructions[key];
        state.editorHasChanges = true;
        
        if (state.selectedInstructionRow === idx) {
            state.selectedInstructionRow = -1;
        }
        
        populateCrimpInstructions();
    }
}

export function loadDrawingIntoEditor(schemeNr, rev) {
    clearEditor();
    
    elSchemeNr.value = schemeNr;
    elSchemeRev.value = rev;
    
    state.fullInstructions = copyObject(state.instructions[schemeNr][rev]);
    state.editorHasChanges = false;
    
    populateCrimpInstructions();
    
    // Switch to editor view
    switchView('view-editor');
    showToast(`Vorlage "${schemeNr}-Rev. ${rev}" geladen`, "success");
}

function updateSaveDraftButtonState() {
    const count = Object.keys(state.fullInstructions).length;
    btnSaveDraft.disabled = count === 0;
    btnPrintEditor.disabled = count === 0;
}

function onSaveDraftClicked() {
    const schemeNr = elSchemeNr.value.trim();
    const schemeRev = elSchemeRev.value.trim();
    
    if (!schemeNr || !schemeRev) {
        // Open Save Template details modal
        openSaveTemplateDetailsModal();
    } else {
        saveDraftTemplate(false);
    }
}

function openSaveTemplateDetailsModal() {
    const modalEl = document.getElementById('modal-save-template');
    const inputNr = document.getElementById('t-save-scheme-nr');
    const inputRev = document.getElementById('t-save-scheme-rev');
    
    inputNr.value = elSchemeNr.value.trim();
    inputRev.value = elSchemeRev.value.trim() || "1";
    
    const btnConfirm = document.getElementById('btn-save-template-confirm');
    btnConfirm.onclick = async () => {
        const nr = inputNr.value.trim();
        const rev = inputRev.value.trim();
        
        if (!nr || !rev) {
            showToast("Bitte Zeichnungsnummer und Revision angeben.", "warning");
            return;
        }
        
        elSchemeNr.value = nr;
        elSchemeRev.value = rev;
        closeModal(modalEl);
        
        await saveDraftTemplate(false);
    };
    
    openModal(modalEl);
}

async function saveDraftTemplate(override = false) {
    const schemeNr = elSchemeNr.value.trim();
    const schemeRev = elSchemeRev.value.trim();
    const scheme = `${schemeNr}-${schemeRev}`;
    
    const payload = {
        scheme: scheme,
        full_instructions: state.fullInstructions,
        override: override
    };
    
    try {
        const res = await apiSaveInstructions(payload);
        if (res.status === "exists") {
            // Store pending payload in state
            state.pendingSavePayload = payload;
            
            // Show overwrite confirmation modal
            showOverwriteConfirmation(res.message);
        } else if (res.success) {
            showToast("Vorlage erfolgreich gespeichert", "success");
            state.editorHasChanges = false;
            
            // Reload instructions list
            const updated = await apiFetchInstructions();
            state.instructions = updated;
            
            // Force redraw of overview listing
            import('./overview.js').then(ov => {
                ov.populateDrawingsList();
                if (state.selectedDrawingNr) {
                    ov.populateRevisionsList(state.selectedDrawingNr);
                }
            });
        } else {
            showToast(res.error || "Fehler beim Speichern der Vorlage.", "error");
        }
    } catch (e) {
        console.error("Save draft failed", e);
    }
}

function showOverwriteConfirmation(message) {
    const modalEl = document.getElementById('modal-confirm-overwrite');
    const msgEl = document.getElementById('confirm-overwrite-message');
    msgEl.textContent = message;
    
    const btnYes = document.getElementById('btn-confirm-overwrite-yes');
    btnYes.onclick = async () => {
        closeModal(modalEl);
        if (state.pendingSavePayload) {
            state.pendingSavePayload.override = true;
            await saveDraftTemplate(true);
            state.pendingSavePayload = null;
        }
    };
    
    openModal(modalEl);
}

export function clearEditor() {
    elSchemeNr.value = "";
    elSchemeRev.value = "";
    state.fullInstructions = {};
    state.editorHasChanges = false;
    state.selectedInstructionRow = -1;
    
    populateCrimpInstructions();
}
