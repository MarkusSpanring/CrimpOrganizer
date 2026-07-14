// Application State
let contacts = {};
let tools = {};
let instructions = {};
let orders = [];
let ordersSortKey = "mtime";
let ordersSortDirection = "desc";
let settings = { xsec_soll_values: [] };
let pendingSavePayload = null;

let selectedContactRef = "";
let selectedToolRef = "";
let selectedToolSummaryRows = []; // indices of selected rows in middle column
let selectedInstructionRow = -1; // index of selected row in right column
let selectedScheme = ""; // Current active "Scheme-Rev" from the tree
let selectedDrawingNr = "";
let fullInstructions = {}; // Map of xs#contactRef -> { pos, name }

// UI Elements References
const elContactsList = document.getElementById('contacts-list');
const elToolSummaryList = document.getElementById('tool-summary-list');
const elDrawingsList = document.getElementById('drawings-list');
const elCrimpInstructionsList = document.getElementById('crimp-instructions-list');
const elSearchContact = document.getElementById('search-contact');
const elBtnClearSearch = document.getElementById('btn-clear-search');
const elSearchTool = document.getElementById('search-tool');
const elBtnClearSearchTool = document.getElementById('btn-clear-search-tool');
const elSchemeNr = document.getElementById('scheme-nr');
const elSchemeRev = document.getElementById('scheme-rev');
const elBtnSaveDraft = document.getElementById('btn-save-draft');

// Empty State Elements
const elToolsEmptyState = document.getElementById('tools-empty-state');
const elTableToolSummary = document.getElementById('table-tool-summary');
const elInstructionsEmptyState = document.getElementById('instructions-empty-state');
const elTableCrimpInstructions = document.getElementById('table-crimp-instructions');

// Context Menus
const ctxContactMenu = document.getElementById('contact-context-menu');
const ctxToolMenu = document.getElementById('tool-context-menu');
const ctxInstructionMenu = document.getElementById('instruction-context-menu');
const ctxTreeMenu = document.getElementById('tree-context-menu');

// Active context elements
let activeCtxContact = "";
let activeCtxTool = null; // index
let activeCtxInstruction = null; // index
let activeCtxTreeScheme = ""; // "schemeNr-schemeRev"

let activeView = "view-overview";
let editorHasChanges = false;

// --- Initial Setup & Data Fetching ---

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    await fetchSettings();
    await fetchContacts();
    await fetchTools();
    await fetchInstructions();

    // Trigger initial empty states
    populateToolSummary();
    populateCrimpInstructions();

    setupGlobalEventListeners();
}

async function fetchContacts() {
    try {
        const res = await fetch('/api/contacts');
        contacts = await res.json();
        populateContacts();
    } catch (e) {
        console.error("Failed to fetch contacts", e);
    }
}

async function fetchTools() {
    try {
        const res = await fetch('/api/tools');
        tools = await res.json();
    } catch (e) {
        console.error("Failed to fetch tools", e);
    }
}

async function fetchSettings() {
    try {
        const res = await fetch('/api/settings');
        settings = await res.json();
    } catch (e) {
        console.error("Failed to fetch settings", e);
    }
}

async function fetchInstructions() {
    try {
        const res = await fetch('/api/instructions');
        instructions = await res.json();
        populateDrawingsList();
    } catch (e) {
        console.error("Failed to fetch instructions", e);
    }
}


// --- Global Events Registration ---

function setupGlobalEventListeners() {
    // Search contacts handler
    elSearchContact.addEventListener('input', () => {
        populateContacts(elSearchContact.value);
        elBtnClearSearch.style.display = elSearchContact.value ? 'inline-block' : 'none';
    });

    elBtnClearSearch.addEventListener('click', () => {
        elSearchContact.value = '';
        populateContacts();
        elBtnClearSearch.style.display = 'none';
    });

    // Search tools handler
    elSearchTool.addEventListener('input', () => {
        populateToolSummary(elSearchTool.value);
        elBtnClearSearchTool.style.display = elSearchTool.value ? 'inline-block' : 'none';
    });

    elBtnClearSearchTool.addEventListener('click', () => {
        elSearchTool.value = '';
        populateToolSummary();
        elBtnClearSearchTool.style.display = 'none';
    });

    // New/Manage Buttons in Editor
    document.getElementById('btn-new-contact').addEventListener('click', () => {
        openContactEditor();
    });

    const btnNewTool = document.getElementById('btn-new-tool');
    if (btnNewTool) {
        btnNewTool.addEventListener('click', () => {
            openToolEditor("__new__");
        });
    }

    const btnClearToolFilter = document.getElementById('btn-clear-tool-filter');
    if (btnClearToolFilter) {
        btnClearToolFilter.addEventListener('click', () => {
            selectTool(""); // Deselect (clear filter)
        });
    }

    // Editor inputs
    elSchemeNr.addEventListener('input', onSchemeInputsChanged);
    elSchemeRev.addEventListener('input', onSchemeInputsChanged);

    // Save template button inside Editor
    elBtnSaveDraft.addEventListener('click', () => {
        openSaveTemplateModal();
    });

    document.getElementById('btn-cancel-save').addEventListener('click', () => {
        closeModal(document.getElementById('modal-save-template'));
    });

    document.getElementById('btn-confirm-save').addEventListener('click', () => {
        const saveNr = document.getElementById('save-scheme-nr').value.trim();
        const saveRev = document.getElementById('save-scheme-rev').value.trim();
        if (!saveNr || !saveRev) {
            alert("Bitte Zeichnungsnummer und Revision angeben.");
            return;
        }
        elSchemeNr.value = saveNr;
        elSchemeRev.value = saveRev;
        closeModal(document.getElementById('modal-save-template'));
        saveDraftTemplate(false);
    });

    document.getElementById('btn-cancel-overwrite').addEventListener('click', () => {
        closeModal(document.getElementById('modal-confirm-overwrite'));
        pendingSavePayload = null;
    });

    document.getElementById('btn-confirm-overwrite').addEventListener('click', async () => {
        if (pendingSavePayload) {
            closeModal(document.getElementById('modal-confirm-overwrite'));
            // Re-attempt saving with override = true
            const overridePayload = { ...pendingSavePayload, override: true };
            try {
                const res = await fetch('/api/instructions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(overridePayload)
                });
                
                const data = await res.json();
                if (res.ok && data.success) {
                    alert("Vorlage erfolgreich gespeichert!");
                    editorHasChanges = false;
                    selectedScheme = overridePayload.scheme;
                    
                    await fetchInstructions();
                    switchView("view-overview");
                } else {
                    alert(data.error || "Überschreiben fehlgeschlagen.");
                }
            } catch (e) {
                console.error("Override save error", e);
                alert("Fehler beim Überschreiben: " + e);
            }
            pendingSavePayload = null;
        }
    });

    // Back to Overview button in Editor header
    document.getElementById('btn-editor-back').addEventListener('click', () => {
        switchView("view-overview");
    });

    // Sidebar navigation clicks
    document.getElementById('nav-overview').addEventListener('click', () => {
        switchView("view-overview");
    });
    document.getElementById('nav-editor').addEventListener('click', () => {
        createNewDrawingInEditor();
    });
    document.getElementById('nav-orders').addEventListener('click', () => {
        switchView("view-orders");
    });
    document.getElementById('nav-settings').addEventListener('click', () => {
        openSettingsModal();
    });

    // Printed Orders Event Listeners
    document.getElementById('search-orders').addEventListener('input', () => {
        populateOrdersList();
    });
    document.getElementById('btn-refresh-orders').addEventListener('click', () => {
        fetchOrders();
    });

    function handleHeaderSort(key) {
        if (ordersSortKey === key) {
            ordersSortDirection = ordersSortDirection === "asc" ? "desc" : "asc";
        } else {
            ordersSortKey = key;
            ordersSortDirection = key === "mtime" ? "desc" : "asc";
        }
        updateSortIcons();
        populateOrdersList();
    }

    document.getElementById('th-order-date').addEventListener('click', () => handleHeaderSort('mtime'));
    document.getElementById('th-order-proto').addEventListener('click', () => handleHeaderSort('protocol_nr'));
    document.getElementById('th-order-file').addEventListener('click', () => handleHeaderSort('filename'));
    document.getElementById('th-order-size').addEventListener('click', () => handleHeaderSort('size'));

    // Overview Search
    document.getElementById('search-drawing').addEventListener('input', (e) => {
        populateDrawingsList(e.target.value);
    });

    // Overview Preview actions
    document.getElementById('btn-print-drawing').addEventListener('click', () => {
        if (selectedScheme) {
            const [sNr, sRev] = selectedScheme.split("-");
            elSchemeNr.value = sNr;
            elSchemeRev.value = sRev;
            fullInstructions = copyObject(instructions[sNr][sRev]);
            
            // Open modal order details
            openOrderDetailsModal();
        }
    });

    document.getElementById('btn-edit-drawing-template').addEventListener('click', () => {
        if (selectedScheme) {
            const [sNr, sRev] = selectedScheme.split("-");
            loadDrawingIntoEditor(sNr, sRev);
        }
    });

    document.getElementById('btn-delete-drawing-template').addEventListener('click', () => {
        if (selectedScheme) {
            deleteScheme(selectedScheme);
        }
    });

    // Close Modals
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            closeModal(e.target.closest('.modal-overlay'));
        });
    });

    // Context Menu Buttons
    document.addEventListener('click', hideAllContextMenus);
    window.addEventListener('blur', hideAllContextMenus);

    document.getElementById('ctx-edit-contact').addEventListener('click', () => {
        if (activeCtxContact) openContactEditor(activeCtxContact);
    });

    document.getElementById('ctx-delete-contact').addEventListener('click', () => {
        if (activeCtxContact) deleteContact(activeCtxContact);
    });

    document.getElementById('ctx-add-instruction').addEventListener('click', () => {
        onUseToolsClicked();
    });

    document.getElementById('ctx-remove-instruction').addEventListener('click', () => {
        if (activeCtxInstruction !== null) {
            removeInstruction(activeCtxInstruction);
        }
    });

    // Deselect contact when clicking on the container empty space
    document.querySelector('#col-contacts .list-container').addEventListener('click', (e) => {
        if (e.target === e.currentTarget || e.target.tagName === 'TABLE' || e.target.tagName === 'TBODY') {
            selectedContactRef = "";
            document.querySelectorAll('#contacts-list tr').forEach(r => r.classList.remove('selected'));
            populateToolSummary();
        }
    });
}

function onSchemeInputsChanged() {
    editorHasChanges = true;
    updateSaveDraftButtonState();
}

function updateSaveDraftButtonState() {
    const count = elCrimpInstructionsList.children.length;
    
    if (count > 0) {
        elBtnSaveDraft.removeAttribute('disabled');
    } else {
        elBtnSaveDraft.setAttribute('disabled', 'true');
    }
}


// --- DOM Rendering Helpers ---

function populateContacts(searchPattern = "") {
    elContactsList.innerHTML = '';
    const sortedKeys = Object.keys(contacts).sort();
    
    sortedKeys.forEach(ref => {
        const contact = contacts[ref];
        const producer = contact.producer || "";
        const series = contact.series || "";
        
        let toolMatches = true;
        if (selectedToolRef) {
            const xsecs = contact.crosssection || {};
            toolMatches = Object.values(xsecs).some(entry => entry.tool === selectedToolRef);
        }
        
        const matches = (searchPattern === "" || 
            ref.toLowerCase().includes(searchPattern.toLowerCase()) ||
            producer.toLowerCase().includes(searchPattern.toLowerCase()) ||
            series.toLowerCase().includes(searchPattern.toLowerCase())) && toolMatches;
            
        if (matches) {
            const tr = document.createElement('tr');
            if (ref === selectedContactRef) {
                tr.classList.add('selected');
            }
            
            if (selectedToolRef) {
                // Tool-filter mode: show Hinzufügen button(s) for matching crosssections
                const xsecs = contact.crosssection || {};
                const matchingXs = Object.entries(xsecs)
                    .filter(([, entry]) => entry.tool === selectedToolRef)
                    .map(([xs]) => xs)
                    .sort((a, b) => parseFloat(a) - parseFloat(b));
                
                const btnsHtml = matchingXs.map(xs =>
                    `<button type="button" class="btn btn-secondary btn-sm btn-hinzufuegen" data-xs="${xs}" title="${xs} mm² hinzufügen">+ ${xs} mm²</button>`
                ).join('');
                
                tr.innerHTML = `
                    <td>${ref}</td>
                    <td>${producer}</td>
                    <td>${series}</td>
                    <td class="text-right"><div class="row-actions">${btnsHtml}</div></td>
                `;
                
                tr.querySelectorAll('.btn-hinzufuegen').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const xs = btn.dataset.xs;
                        openAnnotationModal([`${xs}#${ref}`]);
                    });
                });
                
                tr.addEventListener('click', () => selectContact(ref, tr));
            } else {
                // Normal mode: show edit / delete buttons
                tr.innerHTML = `
                    <td>${ref}</td>
                    <td>${producer}</td>
                    <td>${series}</td>
                    <td class="text-right">
                        <div class="row-actions">
                            <button type="button" class="action-icon-btn btn-edit" title="Bearbeiten">✏️</button>
                            <button type="button" class="action-icon-btn danger btn-delete" title="Löschen">🗑️</button>
                        </div>
                    </td>
                `;
                
                tr.addEventListener('click', () => selectContact(ref, tr));
                
                tr.querySelector('.btn-edit').addEventListener('click', (e) => {
                    e.stopPropagation();
                    openContactEditor(ref);
                });
                
                tr.querySelector('.btn-delete').addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteContact(ref);
                });
                
                tr.addEventListener('dblclick', () => openContactEditor(ref));
                
                tr.addEventListener('contextmenu', (e) => {
                    e.preventDefault();
                    selectContact(ref, tr);
                    showContextMenu(ctxContactMenu, e.clientX, e.clientY);
                    activeCtxContact = ref;
                });
            }
            
            elContactsList.appendChild(tr);
        }
    });
}

function selectContact(ref, trElement) {
    if (selectedContactRef === ref) {
        selectedContactRef = "";
        document.querySelectorAll('#contacts-list tr').forEach(r => r.classList.remove('selected'));
    } else {
        selectedContactRef = ref;
        selectedToolRef = ""; // Clear tool selection
        document.querySelectorAll('#contacts-list tr').forEach(r => r.classList.remove('selected'));
        if (trElement) trElement.classList.add('selected');
    }
    
    populateToolSummary();
}

function selectTool(ref) {
    if (!ref || selectedToolRef === ref) {
        selectedToolRef = "";
    } else {
        selectedToolRef = ref;
        selectedContactRef = ""; // Clear contact selection
        document.querySelectorAll('#contacts-list tr').forEach(r => r.classList.remove('selected'));
    }
    
    // Update filter banner
    const banner = document.getElementById('contacts-filter-banner');
    const label = document.getElementById('contacts-filter-label');
    if (banner && label) {
        if (selectedToolRef && tools[selectedToolRef]) {
            label.textContent = `🔎 Filter: ${getReadableToolName(selectedToolRef)}`;
            banner.style.display = 'flex';
        } else {
            banner.style.display = 'none';
        }
    }
    
    populateContacts();
    populateToolSummary();
}

function populateToolSummary(searchPattern = (elSearchTool ? elSearchTool.value.trim() : "")) {
    elToolSummaryList.innerHTML = '';
    selectedToolSummaryRows = [];
    
    const tableHeader = elTableToolSummary.querySelector('thead');
    
    if (!selectedContactRef || !contacts[selectedContactRef]) {
        // Change table header to show all tools
        tableHeader.innerHTML = `
            <tr>
                <th>Crimpzange</th>
                <th>Zangen-IDs</th>
                <th>Einsätze</th>
                <th class="text-right">Aktion</th>
            </tr>
        `;
        
        elToolsEmptyState.style.display = 'none';
        elTableToolSummary.style.display = 'table';
        
        const sortedRefs = Object.keys(tools).sort();
        if (sortedRefs.length === 0) {
            elToolSummaryList.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine Crimpzangen vorhanden.</td></tr>`;
            return;
        }
        
        const filteredRefs = sortedRefs.filter(ref => {
            if (!searchPattern) return true;
            const t = tools[ref];
            if (!t) return false;
            const name = `${t.producer} | ${t.series} ${t.producerNr ? '(Nr. ' + t.producerNr + ')' : ''}`;
            const ids = t.IDs ? t.IDs.join(", ") : "";
            const slotsText = t.slots ? t.slots.map(s => {
                let sParts = [];
                if (s[0]) sParts.push('AWG ' + s[0]);
                if (s[1]) sParts.push(s[1] + ' mm²');
                return sParts.join(" / ");
            }).filter(s => s).join(", ") : "";
            
            const p = searchPattern.toLowerCase();
            return name.toLowerCase().includes(p) ||
                   ids.toLowerCase().includes(p) ||
                   slotsText.toLowerCase().includes(p) ||
                   ref.toLowerCase().includes(p);
        });

        if (filteredRefs.length === 0) {
            elToolSummaryList.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine passenden Crimpzangen gefunden.</td></tr>`;
            return;
        }
        
        filteredRefs.forEach(ref => {
            const t = tools[ref];
            const name = `${t.producer} | ${t.series} ${t.producerNr ? '(Nr. ' + t.producerNr + ')' : ''}`;
            const ids = t.IDs ? t.IDs.join(", ") : "";
            const slotsText = t.slots ? t.slots.map(s => {
                let sParts = [];
                if (s[0]) sParts.push('AWG ' + s[0]);
                if (s[1]) sParts.push(s[1] + ' mm²');
                return sParts.join(" / ");
            }).filter(s => s).join(", ") : "";
            
            const tr = document.createElement('tr');
            if (ref === selectedToolRef) {
                tr.classList.add('selected');
            }
            tr.innerHTML = `
                <td>${name}</td>
                <td>${ids}</td>
                <td>${slotsText}</td>
                <td class="text-right">
                    <div class="row-actions">
                        <button type="button" class="action-icon-btn btn-edit-tool" title="Bearbeiten">✏️</button>
                        <button type="button" class="action-icon-btn danger btn-delete-tool" title="Löschen">🗑️</button>
                    </div>
                </td>
            `;
            
            tr.querySelector('.btn-edit-tool').addEventListener('click', (e) => {
                e.stopPropagation();
                openToolEditor(ref);
            });
            
            tr.querySelector('.btn-delete-tool').addEventListener('click', async (e) => {
                e.stopPropagation();
                if (confirm(`Möchten Sie die Crimpzange "${name}" wirklich löschen?`)) {
                    try {
                        const res = await fetch(`/api/tools/${encodeURIComponent(ref)}`, { method: 'DELETE' });
                        if (res.ok) {
                            await fetchTools();
                            populateToolSummary();
                        } else {
                            alert("Löschen fehlgeschlagen.");
                        }
                    } catch (err) {
                        console.error("Error deleting tool", err);
                    }
                }
            });
            
            tr.addEventListener('click', () => {
                selectTool(ref);
            });
            
            elToolSummaryList.appendChild(tr);
        });
        return;
    }
    
    // Restore table header for selected contact details
    tableHeader.innerHTML = `
        <tr>
            <th>Ø</th>
            <th>Crimpzange</th>
            <th>Einsatz</th>
            <th class="text-right">Aktion</th>
        </tr>
    `;
    
    elToolsEmptyState.style.display = 'none';
    elTableToolSummary.style.display = 'table';
    
    const contact = contacts[selectedContactRef];
    const crosssections = contact.crosssection || {};
    const sortedXs = Object.keys(crosssections).sort((a,b) => parseFloat(a) - parseFloat(b));
    
    sortedXs.forEach((xs, idx) => {
        const entry = crosssections[xs];
        const toolRef = entry.tool;
        const slot = entry.slot;
        
        let toolIDs = "";
        if (tools[toolRef] && tools[toolRef].IDs) {
            toolIDs = tools[toolRef].IDs.join(", ");
        }
        
        if (searchPattern) {
            const toolName = tools[toolRef] ? `${tools[toolRef].producer} | ${tools[toolRef].series}` : "";
            const p = searchPattern.toLowerCase();
            const matches = xs.toLowerCase().includes(p) ||
                            toolIDs.toLowerCase().includes(p) ||
                            slot.toLowerCase().includes(p) ||
                            toolName.toLowerCase().includes(p);
            if (!matches) return;
        }
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${xs} mm²</td>
            <td>${toolIDs}</td>
            <td>${slot}</td>
            <td class="text-right">
                <button type="button" class="btn btn-secondary btn-sm btn-add-instruction" title="Zu Anleitung hinzufügen">+ Hinzufügen</button>
            </td>
        `;
        
        tr.querySelector('.btn-add-instruction').addEventListener('click', (e) => {
            e.stopPropagation();
            selectedToolSummaryRows = [idx];
            onUseToolsClicked();
        });
        
        tr.addEventListener('click', (e) => {
            handleToolRowSelection(idx, tr, e);
        });
        
        tr.addEventListener('dblclick', () => {
            selectedToolSummaryRows = [idx];
            onUseToolsClicked();
        });
        
        tr.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            if (!selectedToolSummaryRows.includes(idx)) {
                selectedToolSummaryRows = [idx];
                document.querySelectorAll('#tool-summary-list tr').forEach((r, rIdx) => {
                    if (rIdx === idx) r.classList.add('selected');
                    else r.classList.remove('selected');
                });
            }
            showContextMenu(ctxToolMenu, e.clientX, e.clientY);
        });
        
        elToolSummaryList.appendChild(tr);
    });
}

function handleToolRowSelection(idx, trElement, event) {
    if (event.ctrlKey || event.metaKey) {
        // Multi-select
        const index = selectedToolSummaryRows.indexOf(idx);
        if (index > -1) {
            selectedToolSummaryRows.splice(index, 1);
            trElement.classList.remove('selected');
        } else {
            selectedToolSummaryRows.push(idx);
            trElement.classList.add('selected');
        }
    } else if (event.shiftKey && selectedToolSummaryRows.length > 0) {
        // Range select
        const start = selectedToolSummaryRows[selectedToolSummaryRows.length - 1];
        const end = idx;
        const min = Math.min(start, end);
        const max = Math.max(start, end);
        
        selectedToolSummaryRows = [];
        const rows = document.querySelectorAll('#tool-summary-list tr');
        rows.forEach((r, rIdx) => {
            if (rIdx >= min && rIdx <= max) {
                selectedToolSummaryRows.push(rIdx);
                r.classList.add('selected');
            } else {
                r.classList.remove('selected');
            }
        });
    } else {
        // Single select
        selectedToolSummaryRows = [idx];
        document.querySelectorAll('#tool-summary-list tr').forEach((r, rIdx) => {
            if (rIdx === idx) r.classList.add('selected');
            else r.classList.remove('selected');
        });
    }
}


function populateDrawingsList(searchPattern = "") {
    elDrawingsList.innerHTML = '';
    
    // Get unique sorted list of drawing numbers
    const uniqueDrawings = Object.keys(instructions).sort((a, b) => {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    });
    
    uniqueDrawings.forEach(schemeNr => {
        if (searchPattern && !schemeNr.toLowerCase().includes(searchPattern.toLowerCase())) {
            return;
        }
        
        const li = document.createElement('li');
        if (schemeNr === selectedDrawingNr) {
            li.className = 'selected';
        }
        
        li.innerHTML = `
            <span>📁</span>
            <span style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${schemeNr}</span>
        `;
        
        li.addEventListener('click', () => {
            selectDrawingNr(schemeNr);
        });
        
        elDrawingsList.appendChild(li);
    });
}

function selectDrawingNr(schemeNr) {
    selectedDrawingNr = schemeNr;
    
    // Highlight selected drawing item
    document.querySelectorAll('#drawings-list li').forEach(li => {
        const titleSpan = li.querySelector('span:nth-child(2)');
        if (titleSpan && titleSpan.textContent === schemeNr) {
            li.classList.add('selected');
        } else {
            li.classList.remove('selected');
        }
    });
    
    // If the active scheme belongs to this drawing, keep it, otherwise clear selectedScheme
    if (selectedScheme && !selectedScheme.startsWith(`${schemeNr}-`)) {
        selectedScheme = "";
    }
    
    populateRevisionsList(schemeNr);
    
    // Update preview visibility
    if (selectedScheme) {
        const [_, rev] = selectedScheme.split("-");
        selectDrawing(schemeNr, rev);
    } else {
        document.getElementById('overview-empty-state').style.display = 'flex';
        document.getElementById('overview-preview-panel').style.display = 'none';
    }
}

function populateRevisionsList(schemeNr) {
    const elRevisionsList = document.getElementById('revisions-list');
    elRevisionsList.innerHTML = '';
    
    if (!schemeNr || !instructions[schemeNr]) return;
    
    const revs = Object.keys(instructions[schemeNr]).sort((a, b) => {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    });
    
    revs.forEach(rev => {
        const li = document.createElement('li');
        const key = `${schemeNr}-${rev}`;
        if (key === selectedScheme) {
            li.className = 'selected';
        }
        
        li.innerHTML = `
            <span>📄</span>
            <span style="font-weight: 600;">Rev. ${rev}</span>
        `;
        
        li.addEventListener('click', () => {
            selectDrawing(schemeNr, rev);
        });
        
        elRevisionsList.appendChild(li);
    });
}

function selectDrawing(schemeNr, rev) {
    selectedScheme = `${schemeNr}-${rev}`;
    selectedDrawingNr = schemeNr;
    
    // Highlight drawing list element
    document.querySelectorAll('#drawings-list li').forEach(li => {
        const titleSpan = li.querySelector('span:nth-child(2)');
        if (titleSpan && titleSpan.textContent === schemeNr) {
            li.classList.add('selected');
        } else {
            li.classList.remove('selected');
        }
    });
    
    // Highlight revision list element
    document.querySelectorAll('#revisions-list li').forEach(li => {
        const titleSpan = li.querySelector('span:nth-child(2)');
        if (titleSpan && titleSpan.textContent === `Rev. ${rev}`) {
            li.classList.add('selected');
        } else {
            li.classList.remove('selected');
        }
    });
    
    const emptyState = document.getElementById('overview-empty-state');
    const previewPanel = document.getElementById('overview-preview-panel');
    const previewTitle = document.getElementById('preview-title');
    const previewStepsList = document.getElementById('preview-steps-list');
    
    emptyState.style.display = 'none';
    previewPanel.style.display = 'flex';
    previewTitle.textContent = `Zeichnung: ${schemeNr} (Rev. ${rev})`;
    
    previewStepsList.innerHTML = '';
    const steps = instructions[schemeNr][rev];
    const entries = Object.keys(steps);
    
    if (entries.length === 0) {
        previewStepsList.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine Schritte in dieser Anleitung.</td></tr>`;
    } else {
        entries.forEach(entry => {
            const [xs, contactRef] = entry.split("#");
            const details = steps[entry];
            const pos = details.pos || "";
            const slotName = details.name || "";
            
            const contactObj = contacts[contactRef] || {};
            const series = contactObj.series || "";
            const xsecData = contactObj.crosssection && contactObj.crosssection[xs] || {};
            
            const slot = xsecData.slot || "";
            const soll = xsecData.soll || "";
            const toolRef = xsecData.tool || "";
            
            const toolObj = tools[toolRef] || {};
            const toolIDs = toolObj.IDs ? toolObj.IDs.join(", ") : "";
            const toolProducer = toolObj.producer || "";
            
            const crimpung = series ? `${contactRef} / ${series}` : contactRef;
            const zange = toolProducer ? `${toolIDs} (${toolProducer})` : toolIDs;
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${pos}</td>
                <td>${slotName}</td>
                <td>${crimpung}</td>
                <td>${xs} mm²</td>
                <td>${slot}</td>
                <td>${zange}</td>
                <td>${soll ? soll + " N" : ""}</td>
            `;
            previewStepsList.appendChild(tr);
        });
    }
}

function switchView(viewId) {
    if (activeView === viewId) return;
    
    if (activeView === "view-editor" && editorHasChanges) {
        if (!confirm("Sie haben ungespeicherte Änderungen in der Vorlage. Möchten Sie diese verwerfen?")) {
            return;
        }
    }
    
    // Deactivate all nav items
    document.getElementById('nav-overview').classList.remove('active');
    document.getElementById('nav-editor').classList.remove('active');
    document.getElementById('nav-orders').classList.remove('active');
    
    // Hide all view panels
    document.getElementById('view-overview').classList.add('hidden');
    document.getElementById('view-editor').classList.add('hidden');
    document.getElementById('view-orders').classList.add('hidden');
    
    if (viewId === "view-overview") {
        document.getElementById('nav-overview').classList.add('active');
        document.getElementById('view-overview').classList.remove('hidden');
        
        activeView = "view-overview";
        editorHasChanges = false;
        
        // Reset search bar value
        const elSearch = document.getElementById('search-drawing');
        if (elSearch) elSearch.value = "";
        
        populateDrawingsList();
        
        if (selectedDrawingNr && instructions[selectedDrawingNr]) {
            populateRevisionsList(selectedDrawingNr);
        } else {
            const elRevs = document.getElementById('revisions-list');
            if (elRevs) elRevs.innerHTML = '';
        }
        
        if (selectedScheme) {
            const [sNr, sRev] = selectedScheme.split("-");
            if (instructions[sNr] && instructions[sNr][sRev]) {
                selectDrawing(sNr, sRev);
            } else {
                selectedScheme = "";
                document.getElementById('overview-empty-state').style.display = 'flex';
                document.getElementById('overview-preview-panel').style.display = 'none';
            }
        } else {
            document.getElementById('overview-empty-state').style.display = 'flex';
            document.getElementById('overview-preview-panel').style.display = 'none';
        }
    } else if (viewId === "view-editor") {
        document.getElementById('nav-editor').classList.add('active');
        document.getElementById('view-editor').classList.remove('hidden');
        
        activeView = "view-editor";
        editorHasChanges = false;
    } else if (viewId === "view-orders") {
        document.getElementById('nav-orders').classList.add('active');
        document.getElementById('view-orders').classList.remove('hidden');
        
        activeView = "view-orders";
        editorHasChanges = false;
        
        // Reset search bar value and sorting indicator
        const elSearch = document.getElementById('search-orders');
        if (elSearch) elSearch.value = "";
        ordersSortKey = "mtime";
        ordersSortDirection = "desc";
        updateSortIcons();
        
        fetchOrders();
    }
}

function loadDrawingIntoEditor(schemeNr, rev) {
    elSchemeNr.value = schemeNr;
    elSchemeRev.value = rev;
    
    fullInstructions = copyObject(instructions[schemeNr][rev]);
    populateCrimpInstructions();
    
    document.getElementById('editor-view-title').textContent = `Vorlage bearbeiten: ${schemeNr} - Rev. ${rev}`;
    
    activeView = "view-overview"; 
    switchView("view-editor");
    editorHasChanges = false;
}

function createNewDrawingInEditor() {
    elSchemeNr.value = "";
    elSchemeRev.value = "";
    
    fullInstructions = {};
    populateCrimpInstructions();
    
    document.getElementById('editor-view-title').textContent = "Neue Vorlage anlegen";
    
    activeView = "view-overview";
    switchView("view-editor");
    editorHasChanges = false;
}

async function saveDraftTemplate(override = false) {
    const schemeNr = elSchemeNr.value.trim();
    const schemeRev = elSchemeRev.value.trim();
    if (!schemeNr || !schemeRev) {
        alert("Bitte Zeichnungsnummer und Revision angeben.");
        return;
    }
    const scheme = `${schemeNr}-${schemeRev}`;
    
    const payload = {
        scheme: scheme,
        full_instructions: fullInstructions,
        override: override
    };
    
    try {
        const res = await fetch('/api/instructions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if (res.ok) {
            if (data.status === "exists") {
                pendingSavePayload = payload;
                document.getElementById('overwrite-modal-message').textContent = data.message || `Die Vorlage "${scheme}" ist bereits vorhanden. Überschreiben?`;
                openModal(document.getElementById('modal-confirm-overwrite'));
                return;
            }
            
            alert("Vorlage erfolgreich gespeichert!");
            editorHasChanges = false;
            selectedScheme = scheme;
            
            await fetchInstructions();
            switchView("view-overview");
        } else {
            alert(data.error || "Speichern fehlgeschlagen.");
        }
    } catch (e) {
        console.error("Save template error", e);
        alert("Fehler beim Speichern: " + e);
    }
}

function populateCrimpInstructions() {
    elCrimpInstructionsList.innerHTML = '';
    selectedInstructionRow = -1;
    
    const entries = Object.keys(fullInstructions);
    
    if (entries.length === 0) {
        elInstructionsEmptyState.style.display = 'flex';
        elTableCrimpInstructions.style.display = 'none';
    } else {
        elInstructionsEmptyState.style.display = 'none';
        elTableCrimpInstructions.style.display = 'table';
    }
    
    entries.forEach((entry, idx) => {
        const [xs, contact] = entry.split("#");
        const details = fullInstructions[entry];
        const pos = details.pos || "";
        const name = details.name || "";
        
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${pos}</td>
            <td>${contact}</td>
            <td>${xs} mm²</td>
            <td>${name}</td>
            <td class="text-right">
                <div class="row-actions">
                    <button type="button" class="action-icon-btn btn-edit-instruction" title="Bearbeiten">✏️</button>
                    <button type="button" class="action-icon-btn danger btn-remove" title="Entfernen">🗑️</button>
                </div>
            </td>
        `;
        
        tr.querySelector('.btn-edit-instruction').addEventListener('click', (e) => {
            e.stopPropagation();
            editSingleInstruction(entry);
        });
        
        tr.querySelector('.btn-remove').addEventListener('click', (e) => {
            e.stopPropagation();
            removeInstruction(idx);
        });
        
        tr.addEventListener('click', () => {
            selectedInstructionRow = idx;
            document.querySelectorAll('#crimp-instructions-list tr').forEach((r, rIdx) => {
                if (rIdx === idx) r.classList.add('selected');
                else r.classList.remove('selected');
            });
        });
        
        tr.addEventListener('contextmenu', (e) => {
            e.preventDefault();
            selectedInstructionRow = idx;
            activeCtxInstruction = idx;
            document.querySelectorAll('#crimp-instructions-list tr').forEach((r, rIdx) => {
                if (rIdx === idx) r.classList.add('selected');
                else r.classList.remove('selected');
            });
            showContextMenu(ctxInstructionMenu, e.clientX, e.clientY);
        });
        
        elCrimpInstructionsList.appendChild(tr);
    });
    
    updateSaveDraftButtonState();
}


// --- Context Menus Controlling ---

function showContextMenu(menuElement, x, y) {
    hideAllContextMenus();
    menuElement.style.display = 'block';
    
    // Boundary check so menu doesn't go offscreen
    const menuWidth = menuElement.offsetWidth || 180;
    const menuHeight = menuElement.offsetHeight || 100;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    if (x + menuWidth > windowWidth) x = windowWidth - menuWidth - 5;
    if (y + menuHeight > windowHeight) y = windowHeight - menuHeight - 5;
    
    menuElement.style.left = `${x}px`;
    menuElement.style.top = `${y}px`;
}

function hideAllContextMenus() {
    ctxContactMenu.style.display = 'none';
    ctxToolMenu.style.display = 'none';
    ctxInstructionMenu.style.display = 'none';
    ctxTreeMenu.style.display = 'none';
}


// --- Modal Window Helper Functions ---

function openModal(modalElement) {
    modalElement.style.display = 'flex';
    // Small timeout to allow transitions to fire
    setTimeout(() => {
        modalElement.classList.add('active');
    }, 10);
}

function closeModal(modalElement) {
    modalElement.classList.remove('active');
    setTimeout(() => {
        modalElement.style.display = 'none';
    }, 300);
}


// --- DELETE Contact API ---

async function deleteContact(ref) {
    if (!confirm(`Soll der Kontakt "${ref}" unwiderruflich gelöscht werden?`)) {
        return;
    }
    try {
        const res = await fetch(`/api/contacts/${encodeURIComponent(ref)}`, { method: 'DELETE' });
        if (res.ok) {
            if (selectedContactRef === ref) {
                selectedContactRef = "";
                elToolSummaryList.innerHTML = '';
            }
            await fetchContacts();
        } else {
            alert("Fehler beim Löschen des Kontakts.");
        }
    } catch (e) {
        console.error("Delete contact error", e);
    }
}


// --- DELETE Instruction Scheme API ---

async function deleteScheme(key) {
    if (!confirm(`Soll die Anweisung für "${key}" unwiderruflich gelöscht werden?`)) {
        return;
    }
    try {
        const res = await fetch(`/api/instructions/${encodeURIComponent(key)}`, { method: 'DELETE' });
        if (res.ok) {
            if (selectedScheme === key) {
                selectedScheme = "";
                fullInstructions = {};
                elCrimpInstructionsList.innerHTML = '';
                elSchemeNr.value = "";
                elSchemeRev.value = "";
            }
            await fetchInstructions();
            
            if (selectedDrawingNr) {
                if (instructions[selectedDrawingNr]) {
                    populateRevisionsList(selectedDrawingNr);
                } else {
                    selectedDrawingNr = "";
                    const elRevs = document.getElementById('revisions-list');
                    if (elRevs) elRevs.innerHTML = '';
                }
            }
            if (!selectedScheme) {
                document.getElementById('overview-empty-state').style.display = 'flex';
                document.getElementById('overview-preview-panel').style.display = 'none';
            }
        } else {
            alert("Fehler beim Löschen der Zeichnung.");
        }
    } catch (e) {
        console.error("Delete scheme error", e);
    }
}


// --- USE TOOLS (Trigger annotation flow) ---

function onUseToolsClicked() {
    if (selectedToolSummaryRows.length === 0 || !selectedContactRef) return;
    
    // Find crosssections and tools selected
    const contact = contacts[selectedContactRef];
    const crosssections = contact.crosssection || {};
    const sortedXs = Object.keys(crosssections).sort((a,b) => parseFloat(a) - parseFloat(b));
    
    const listToAnnotate = [];
    selectedToolSummaryRows.forEach(rowIdx => {
        if (rowIdx < sortedXs.length) {
            const xs = sortedXs[rowIdx];
            const identifier = `${xs}#${selectedContactRef}`;
            listToAnnotate.push(identifier);
        }
    });
    
    openAnnotationModal(listToAnnotate);
}

function removeInstruction(idx) {
    const entries = Object.keys(fullInstructions);
    if (idx < entries.length) {
        const key = entries[idx];
        delete fullInstructions[key];
        populateCrimpInstructions();
        editorHasChanges = true;
    }
}

function editSingleInstruction(entry) {
    openAnnotationModal([entry]);
    annotationModeIsReannotate = true;
}


// ==================== 1. CONTACT EDITOR MODAL ====================

let contactEditorOldRef = "";
let contactEditorAddedXsecs = []; // List of { xs, tool, slot, soll }

function openContactEditor(preloadRef = "") {
    const modal = document.getElementById('modal-contact-editor');
    const title = document.getElementById('contact-editor-title');
    const form = document.getElementById('form-contact');
    
    form.reset();
    document.getElementById('c-refnr').removeAttribute('disabled');
    contactEditorAddedXsecs = [];
    contactEditorOldRef = preloadRef;
    
    // Clear Select boxes
    const selXs = document.getElementById('add-xs-section');
    const selTool = document.getElementById('add-xs-tool');
    const selSlot = document.getElementById('add-xs-slot');
    const inputSoll = document.getElementById('add-xs-soll');
    
    selXs.innerHTML = '<option value="">--Wählen--</option>';
    selTool.innerHTML = '';
    selTool.setAttribute('disabled', 'true');
    selSlot.innerHTML = '';
    selSlot.setAttribute('disabled', 'true');
    inputSoll.value = '';
    inputSoll.setAttribute('disabled', 'true');
    
    document.getElementById('btn-add-xsec').setAttribute('disabled', 'true');
    document.getElementById('btn-delete-xsec').setAttribute('disabled', 'true');
    document.getElementById('btn-save-contact').setAttribute('disabled', 'true');
    
    if (preloadRef && contacts[preloadRef]) {
        title.textContent = "Crimpkontakt bearbeiten";
        const c = contacts[preloadRef];
        
        document.getElementById('c-refnr').value = c.refNr || "";
        document.getElementById('c-refnr').setAttribute('disabled', 'true'); // RefNr acts as ID once saved
        document.getElementById('c-series').value = c.series || "";
        document.getElementById('c-producer').value = c.producer || "";
        document.getElementById('c-producernr').value = c.producerNr || "";
        
        if (c.crimpType === "closed") {
            document.getElementById('c-type-closed').checked = true;
        } else {
            document.getElementById('c-type-open').checked = true;
        }
        
        // Add existing cross sections
        const xsList = c.crosssection || {};
        Object.keys(xsList).forEach(xs => {
            contactEditorAddedXsecs.push({
                xs: xs,
                tool: xsList[xs].tool,
                slot: xsList[xs].slot,
                soll: xsList[xs].soll
            });
        });
    } else {
        title.textContent = "Crimpkontakt anlegen";
    }
    
    populateContactEditorXsecsTable();
    populateContactEditorXsecDropdown();
    
    // Bind change listeners to validate and populate selects
    selXs.onchange = onContactEditorXsChanged;
    selTool.onchange = onContactEditorToolChanged;
    selSlot.onchange = onContactEditorInfoChanged;
    inputSoll.oninput = onContactEditorInfoChanged;
    
    // Bind info validators for text controls
    const textCtrls = ['c-refnr', 'c-series', 'c-producer', 'c-producernr'];
    textCtrls.forEach(id => {
        document.getElementById(id).oninput = onContactEditorInfoChanged;
    });
    
    document.getElementById('c-type-open').onchange = onContactEditorXsChanged;
    document.getElementById('c-type-closed').onchange = onContactEditorXsChanged;
    
    // Buttons
    document.getElementById('btn-add-xsec').onclick = onContactEditorAddXsecClicked;
    document.getElementById('btn-delete-xsec').onclick = onContactEditorDeleteXsecClicked;
    document.getElementById('btn-save-contact').onclick = onContactEditorSaveClicked;
    
    openModal(modal);
}

function populateContactEditorXsecDropdown() {
    const selXs = document.getElementById('add-xs-section');
    selXs.innerHTML = '<option value="">--Wählen--</option>';
    
    // Exclude already added cross sections
    const usedXs = contactEditorAddedXsecs.map(x => x.xs);
    const sortedSettingsXs = settings.xsec_soll_values.map(x => x[0]);
    
    sortedSettingsXs.forEach(xs => {
        if (!usedXs.includes(xs)) {
            const opt = document.createElement('option');
            opt.value = xs;
            opt.textContent = `${xs} mm²`;
            selXs.appendChild(opt);
        }
    });
}

function getReadableToolName(toolRef) {
    if (!tools[toolRef]) return toolRef;
    const t = tools[toolRef];
    const ids = t.IDs && t.IDs.length > 0 ? `(z.B. ${t.IDs.join(", ")})` : "";
    return `${t.producer} | ${t.series} ${ids}`;
}

function onContactEditorXsChanged() {
    const selXs = document.getElementById('add-xs-section');
    const selTool = document.getElementById('add-xs-tool');
    const selSlot = document.getElementById('add-xs-slot');
    const inputSoll = document.getElementById('add-xs-soll');
    
    const xs = selXs.value;
    
    // Reset secondary fields
    selTool.innerHTML = '<option value="">--Wählen--</option>';
    selSlot.innerHTML = '';
    selSlot.setAttribute('disabled', 'true');
    inputSoll.value = '';
    inputSoll.setAttribute('disabled', 'true');
    
    if (!xs) {
        selTool.setAttribute('disabled', 'true');
        onContactEditorInfoChanged();
        return;
    }
    
    // Populate tools dropdown with tools available
    const sortedToolKeys = Object.keys(tools).sort();
    let count = 0;
    
    sortedToolKeys.forEach(tRef => {
        const option = document.createElement('option');
        option.value = tRef;
        option.textContent = getReadableToolName(tRef);
        selTool.appendChild(option);
        count++;
    });
    
    selTool.removeAttribute('disabled');
    
    // Autofill target soll force value based on selected xs and crimp type
    let sollVal = "";
    const isClosed = document.getElementById('c-type-closed').checked;
    settings.xsec_soll_values.forEach(row => {
        if (row[0] === xs) {
            sollVal = isClosed ? row[2] : row[1];
        }
    });
    
    inputSoll.value = sollVal;
    inputSoll.removeAttribute('disabled');
    
    onContactEditorInfoChanged();
}

function onContactEditorToolChanged() {
    const selTool = document.getElementById('add-xs-tool');
    const selSlot = document.getElementById('add-xs-slot');
    
    const toolRef = selTool.value;
    selSlot.innerHTML = '<option value="">--Wählen--</option>';
    
    if (!toolRef || !tools[toolRef]) {
        selSlot.setAttribute('disabled', 'true');
        onContactEditorInfoChanged();
        return;
    }
    
    // Populate slots list for this tool
    const slots = tools[toolRef].slots || [];
    slots.forEach(slot => {
        const awg = slot[0] ? `AWG ${slot[0]}` : "";
        const met = slot[1] ? `${slot[1]} mm²` : "";
        
        let label = "";
        if (slot[0] && slot[1]) {
            label = `${awg} | ${met}`;
        } else {
            label = awg + met;
        }
        
        const opt = document.createElement('option');
        opt.value = label;
        opt.textContent = label;
        selSlot.appendChild(opt);
    });
    
    selSlot.removeAttribute('disabled');
    onContactEditorInfoChanged();
}

function onContactEditorInfoChanged() {
    const refNr = document.getElementById('c-refnr').value.trim();
    const series = document.getElementById('c-series').value.trim();
    const producer = document.getElementById('c-producer').value.trim();
    const producerNr = document.getElementById('c-producernr').value.trim();
    
    const validBase = refNr !== "" && series !== "" && producer !== "" && producerNr !== "";
    
    // Validate Cross Section addition form
    const selXs = document.getElementById('add-xs-section').value;
    const selTool = document.getElementById('add-xs-tool').value;
    const selSlot = document.getElementById('add-xs-slot').value;
    const inputSoll = document.getElementById('add-xs-soll').value.trim();
    
    const validAdd = selXs !== "" && selTool !== "" && selSlot !== "" && inputSoll !== "";
    
    if (validAdd) {
        document.getElementById('btn-add-xsec').removeAttribute('disabled');
    } else {
        document.getElementById('btn-add-xsec').setAttribute('disabled', 'true');
    }
    
    // Validate overall save
    if (validBase && contactEditorAddedXsecs.length > 0) {
        document.getElementById('btn-save-contact').removeAttribute('disabled');
    } else {
        document.getElementById('btn-save-contact').setAttribute('disabled', 'true');
    }
}

function populateContactEditorXsecsTable() {
    const tbody = document.getElementById('added-xsecs-list');
    tbody.innerHTML = '';
    
    contactEditorAddedXsecs.forEach((item, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.xs} mm²</td>
            <td>${getReadableToolName(item.tool)}</td>
            <td>${item.slot}</td>
            <td>${item.soll}</td>
        `;
        
        tr.onclick = () => {
            tbody.querySelectorAll('tr').forEach((r, idx) => {
                if (idx === index) r.classList.add('selected');
                else r.classList.remove('selected');
            });
            
            const delBtn = document.getElementById('btn-delete-xsec');
            delBtn.removeAttribute('disabled');
            // Store selected index on delete button attributes
            delBtn.dataset.index = index;
        };
        
        tbody.appendChild(tr);
    });
}

function onContactEditorAddXsecClicked() {
    const xs = document.getElementById('add-xs-section').value;
    const tool = document.getElementById('add-xs-tool').value;
    const slot = document.getElementById('add-xs-slot').value;
    const soll = document.getElementById('add-xs-soll').value;
    
    contactEditorAddedXsecs.push({
        xs, tool, slot, soll
    });
    
    populateContactEditorXsecsTable();
    populateContactEditorXsecDropdown();
    
    // Reset Add Form
    document.getElementById('add-xs-section').value = "";
    onContactEditorXsChanged();
}

function onContactEditorDeleteXsecClicked(e) {
    const index = parseInt(e.target.dataset.index);
    if (!isNaN(index) && index >= 0 && index < contactEditorAddedXsecs.length) {
        contactEditorAddedXsecs.splice(index, 1);
        populateContactEditorXsecsTable();
        populateContactEditorXsecDropdown();
        e.target.setAttribute('disabled', 'true');
        onContactEditorInfoChanged();
    }
}

async function onContactEditorSaveClicked() {
    const isClosed = document.getElementById('c-type-closed').checked;
    
    const contact = {
        refNr: document.getElementById('c-refnr').value.trim(),
        series: document.getElementById('c-series').value.trim(),
        producer: document.getElementById('c-producer').value.trim(),
        producerNr: document.getElementById('c-producernr').value.trim(),
        crimpType: isClosed ? "closed" : "open",
        crosssection: {}
    };
    
    contactEditorAddedXsecs.forEach(item => {
        contact.crosssection[item.xs] = {
            tool: item.tool,
            slot: item.slot,
            soll: item.soll
        };
    });
    
    try {
        const url = `/api/contacts?oldRef=${encodeURIComponent(contactEditorOldRef)}`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(contact)
        });
        
        if (res.ok) {
            closeModal(document.getElementById('modal-contact-editor'));
            await fetchContacts();
            // Automatically select saved item
            selectContact(contact.refNr);
        } else {
            alert("Speichern fehlgeschlagen.");
        }
    } catch (e) {
        console.error("Save contact error", e);
    }
}


// ==================== 2. TOOL EDITOR MODAL ====================

let toolEditorSelectedRef = "";
let toolEditorSlots = []; // List of [awg, met]
let toolEditorIDs = []; // List of string

function openToolEditor(ref = "__new__") {
    const modal = document.getElementById('modal-tool-editor');
    
    // Clear elements
    document.getElementById('form-tool').reset();
    document.getElementById('t-awg-slot').value = '';
    document.getElementById('t-met-slot').value = '';
    document.getElementById('t-id').value = '';
    document.getElementById('tool-ids-list').innerHTML = '';
    document.getElementById('tool-slots-list').innerHTML = '';
    
    toolEditorSelectedRef = ref;
    toolEditorSlots = [];
    toolEditorIDs = [];
    
    // Update modal title
    const titleEl = document.getElementById('modal-tool-editor-title');
    if (ref === "__new__") {
        titleEl.textContent = "Neue Crimpzange";
    } else if (ref && tools[ref]) {
        titleEl.textContent = `Bearbeiten: ${getReadableToolName(ref)}`;
    }
    
    // Load the tool form directly
    if (ref === "__new__") {
        enableToolEditorPane();
        populateToolEditorSlotsTable();
        populateToolEditorIdsList();
        document.getElementById('btn-edit-save-tool').textContent = "Speichern";
        document.getElementById('btn-edit-save-tool').setAttribute('disabled', 'true');
        document.getElementById('btn-delete-tool').setAttribute('disabled', 'true');
        const fieldIds = ['t-prod', 't-series', 't-prodnr'];
        fieldIds.forEach(id => {
            document.getElementById(id).oninput = onToolEditorDetailsChanged;
        });
    } else if (ref && tools[ref]) {
        const t = tools[ref];
        document.getElementById('t-prod').value = t.producer || "";
        document.getElementById('t-series').value = t.series || "";
        document.getElementById('t-prodnr').value = t.producerNr || "";
        toolEditorSlots = copyObject(t.slots || []);
        toolEditorIDs = copyObject(t.IDs || []);
        populateToolEditorSlotsTable();
        populateToolEditorIdsList();
        disableToolEditorPane();
        const saveBtn = document.getElementById('btn-edit-save-tool');
        saveBtn.textContent = "Bearbeiten";
        saveBtn.removeAttribute('disabled');
        document.getElementById('btn-delete-tool').removeAttribute('disabled');
    }
    
    // Actions binding
    document.getElementById('t-awg-slot').oninput = onToolEditorSlotInputsChanged;
    document.getElementById('t-met-slot').oninput = onToolEditorSlotInputsChanged;
    document.getElementById('t-id').oninput = onToolEditorIdInputChanged;
    
    document.getElementById('btn-add-slot').onclick = onToolEditorAddSlotClicked;
    document.getElementById('btn-delete-slot').onclick = onToolEditorDeleteSlotClicked;
    document.getElementById('btn-add-id').onclick = onToolEditorAddIdClicked;
    document.getElementById('btn-remove-id').onclick = onToolEditorRemoveIdClicked;
    
    document.getElementById('btn-edit-save-tool').onclick = onToolEditorSaveClicked;
    document.getElementById('btn-delete-tool').onclick = onToolEditorDeleteClicked;
    
    openModal(modal);
}



function enableToolEditorPane() {
    const inputs = ['t-prod', 't-series', 't-prodnr', 't-awg-slot', 't-met-slot', 't-id'];
    inputs.forEach(id => document.getElementById(id).removeAttribute('disabled'));
    
    // Selects and tables enabling is simulated by browser interactivity
    document.getElementById('tool-ids-list').removeAttribute('disabled');
}

function disableToolEditorPane() {
    const inputs = ['t-prod', 't-series', 't-prodnr', 't-awg-slot', 't-met-slot', 't-id'];
    inputs.forEach(id => document.getElementById(id).setAttribute('disabled', 'true'));
    
    document.getElementById('tool-ids-list').setAttribute('disabled', 'true');
    document.getElementById('btn-add-slot').setAttribute('disabled', 'true');
    document.getElementById('btn-delete-slot').setAttribute('disabled', 'true');
    document.getElementById('btn-add-id').setAttribute('disabled', 'true');
    document.getElementById('btn-remove-id').setAttribute('disabled', 'true');
}

function populateToolEditorSlotsTable() {
    const tbody = document.getElementById('tool-slots-list');
    tbody.innerHTML = '';
    
    toolEditorSlots.forEach((slot, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${slot[0] ? 'AWG ' + slot[0] : ''}</td>
            <td>${slot[1] ? slot[1] + ' mm²' : ''}</td>
        `;
        
        tr.onclick = () => {
            if (document.getElementById('t-prod').hasAttribute('disabled')) return; // read-only mode
            
            tbody.querySelectorAll('tr').forEach((r, idx) => {
                if (idx === index) r.classList.add('selected');
                else r.classList.remove('selected');
            });
            
            const delBtn = document.getElementById('btn-delete-slot');
            delBtn.removeAttribute('disabled');
            delBtn.dataset.index = index;
        };
        
        tbody.appendChild(tr);
    });
}

function populateToolEditorIdsList() {
    const select = document.getElementById('tool-ids-list');
    select.innerHTML = '';
    
    toolEditorIDs.forEach(id => {
        const opt = document.createElement('option');
        opt.value = id;
        opt.textContent = id;
        select.appendChild(opt);
    });
    
    select.onchange = () => {
        if (document.getElementById('t-prod').hasAttribute('disabled')) return; // read-only mode
        
        const btn = document.getElementById('btn-remove-id');
        if (select.selectedIndex > -1) {
            btn.removeAttribute('disabled');
        } else {
            btn.setAttribute('disabled', 'true');
        }
    };
}

function onToolEditorSlotInputsChanged() {
    const awg = document.getElementById('t-awg-slot').value.trim();
    const met = document.getElementById('t-met-slot').value.trim();
    const btn = document.getElementById('btn-add-slot');
    
    if (awg !== "" || met !== "") {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

function onToolEditorIdInputChanged() {
    const id = document.getElementById('t-id').value.trim();
    const btn = document.getElementById('btn-add-id');
    
    if (id !== "") {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

function onToolEditorAddSlotClicked() {
    const awg = document.getElementById('t-awg-slot').value.trim();
    const met = document.getElementById('t-met-slot').value.trim();
    
    toolEditorSlots.push([awg, met]);
    populateToolEditorSlotsTable();
    
    document.getElementById('t-awg-slot').value = '';
    document.getElementById('t-met-slot').value = '';
    document.getElementById('btn-add-slot').setAttribute('disabled', 'true');
    
    onToolEditorDetailsChanged();
}

function onToolEditorDeleteSlotClicked(e) {
    const index = parseInt(e.target.dataset.index);
    if (!isNaN(index) && index >= 0 && index < toolEditorSlots.length) {
        toolEditorSlots.splice(index, 1);
        populateToolEditorSlotsTable();
        e.target.setAttribute('disabled', 'true');
        onToolEditorDetailsChanged();
    }
}

function onToolEditorAddIdClicked() {
    const id = document.getElementById('t-id').value.trim();
    if (id && !toolEditorIDs.includes(id)) {
        toolEditorIDs.push(id);
        populateToolEditorIdsList();
    }
    
    document.getElementById('t-id').value = '';
    document.getElementById('btn-add-id').setAttribute('disabled', 'true');
    
    onToolEditorDetailsChanged();
}

function onToolEditorRemoveIdClicked() {
    const select = document.getElementById('tool-ids-list');
    const index = select.selectedIndex;
    if (index > -1) {
        toolEditorIDs.splice(index, 1);
        populateToolEditorIdsList();
        document.getElementById('btn-remove-id').setAttribute('disabled', 'true');
        onToolEditorDetailsChanged();
    }
}

function onToolEditorDetailsChanged() {
    const prod = document.getElementById('t-prod').value.trim();
    const series = document.getElementById('t-series').value.trim();
    const prodNr = document.getElementById('t-prodnr').value.trim();
    
    const valid = prod !== "" && series !== "" && prodNr !== "" && 
                  toolEditorSlots.length > 0 && toolEditorIDs.length > 0;
                  
    const btn = document.getElementById('btn-edit-save-tool');
    if (valid) {
        btn.textContent = "Speichern";
        btn.removeAttribute('disabled');
    } else {
        // Keep it as Save or Bearbeiten appropriately
        if (toolEditorSelectedRef === "__new__") {
            btn.textContent = "Speichern";
            btn.setAttribute('disabled', 'true');
        } else {
            btn.textContent = "Bearbeiten";
        }
    }
}

async function onToolEditorSaveClicked() {
    const btn = document.getElementById('btn-edit-save-tool');
    
    if (btn.textContent === "Bearbeiten") {
        enableToolEditorPane();
        btn.textContent = "Speichern";
        
        // Setup details change listeners
        const ids = ['t-prod', 't-series', 't-prodnr'];
        ids.forEach(id => {
            document.getElementById(id).oninput = onToolEditorDetailsChanged;
        });
        
        return;
    }
    
    // Save operation
    const tool = {
        producer: document.getElementById('t-prod').value.trim(),
        series: document.getElementById('t-series').value.trim(),
        producerNr: document.getElementById('t-prodnr').value.trim(),
        slots: toolEditorSlots,
        IDs: toolEditorIDs
    };
    
    try {
        const isNew = toolEditorSelectedRef === "__new__";
        const oldRef = isNew ? "" : toolEditorSelectedRef;
        const url = `/api/tools?oldRef=${encodeURIComponent(oldRef)}`;
        
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(tool)
        });
        
        if (res.ok) {
            const data = await res.json();
            await fetchTools();
            closeModal(document.getElementById('modal-tool-editor'));
            
            // Reload main window contacts/lists since tools changed
            await fetchContacts();
            populateToolSummary();
        } else {
            alert("Speichern des Tools fehlgeschlagen.");
        }
    } catch (e) {
        console.error("Save tool error", e);
    }
}

async function onToolEditorDeleteClicked() {
    if (!toolEditorSelectedRef || toolEditorSelectedRef === "__new__") return;
    
    if (!confirm(`Möchtest du das Tool "${getReadableToolName(toolEditorSelectedRef)}" wirklich löschen?`)) {
        return;
    }
    
    try {
        const res = await fetch(`/api/tools/${encodeURIComponent(toolEditorSelectedRef)}`, { method: 'DELETE' });
        if (res.ok) {
            toolEditorSelectedRef = "";
            await fetchTools();
            closeModal(document.getElementById('modal-tool-editor'));
            
            // Reload main lists
            await fetchContacts();
            populateToolSummary();
        } else {
            alert("Fehler beim Löschen des Tools.");
        }
    } catch (e) {
        console.error("Delete tool error", e);
    }
}


// ==================== 3. ANNOTATE CONTACTS MODAL ====================

let activeAnnotationsList = []; // List of strings (xs#contactRef)
let annotationModeIsReannotate = false;

function openAnnotationModal(identifiers) {
    const modal = document.getElementById('modal-annotate');
    const container = document.getElementById('annotation-fields-container');
    
    container.innerHTML = '';
    activeAnnotationsList = identifiers;
    annotationModeIsReannotate = false;
    
    document.getElementById('btn-apply-annotations').setAttribute('disabled', 'true');
    
    identifiers.forEach((entry, index) => {
        const [xs, contact] = entry.split("#");
        const displayLabel = `${xs} mm²: ${contact}`;
        
        // Find existing value if it is already present in fullInstructions
        const existingPos = fullInstructions[entry] ? fullInstructions[entry].pos : "";
        const existingName = fullInstructions[entry] ? fullInstructions[entry].name : "";
        
        const row = document.createElement('div');
        row.className = 'annotation-row-fields';
        row.innerHTML = `
            <div class="annotation-label" title="${displayLabel}">${displayLabel}</div>
            <input type="text" id="ann-pos-${index}" placeholder="z.B. 1" value="${existingPos}">
            <input type="text" id="ann-name-${index}" placeholder="z.B. Stecker A" value="${existingName}">
        `;
        
        // Validate on input
        row.querySelectorAll('input').forEach(input => {
            input.oninput = onAnnotationFieldsChanged;
        });
        
        container.appendChild(row);
    });
    
    onAnnotationFieldsChanged();
    
    // Bind Apply button click
    document.getElementById('btn-apply-annotations').onclick = onApplyAnnotationsClicked;
    
    openModal(modal);
}

function onAnnotationFieldsChanged() {
    let allFilled = true;
    for (let i = 0; i < activeAnnotationsList.length; i++) {
        const pos = document.getElementById(`ann-pos-${i}`).value.trim();
        const name = document.getElementById(`ann-name-${i}`).value.trim();
        if (pos === "" || name === "") {
            allFilled = false;
            break;
        }
    }
    
    const btn = document.getElementById('btn-apply-annotations');
    if (allFilled) {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

function onApplyAnnotationsClicked() {
    if (!annotationModeIsReannotate) {
        // Clear summary list selections
        selectedToolSummaryRows = [];
        document.querySelectorAll('#tool-summary-list tr').forEach(r => r.classList.remove('selected'));
        elToolSummaryList.innerHTML = '';
        elCrimpInstructionsList.innerHTML = '';
    }
    
    activeAnnotationsList.forEach((entry, index) => {
        const pos = document.getElementById(`ann-pos-${index}`).value.trim();
        const name = document.getElementById(`ann-name-${index}`).value.trim();
        
        fullInstructions[entry] = { pos, name };
    });
    
    populateCrimpInstructions();
    closeModal(document.getElementById('modal-annotate'));
    
    editorHasChanges = true;
}

function openReannotateModal(schemeKey) {
    const parts = schemeKey.split("-");
    if (parts.length !== 2) return;
    
    const [schemeNr, schemeRev] = parts;
    const items = instructions[schemeNr][schemeRev];
    
    const identifiers = Object.keys(items);
    if (identifiers.length === 0) return;
    
    openAnnotationModal(identifiers);
    annotationModeIsReannotate = true;
}


// ==================== 4. ORDER DETAILS / PRINT MODAL ====================

function openOrderDetailsModal() {
    const modal = document.getElementById('modal-order-details');
    
    document.getElementById('form-order').reset();
    document.getElementById('btn-print-order').setAttribute('disabled', 'true');
    
    const inputs = ['o-ordernr', 'o-jobnr', 'o-protocolnr'];
    inputs.forEach(id => {
        document.getElementById(id).oninput = onOrderDetailsInputsChanged;
    });
    
    document.getElementById('btn-print-order').onclick = onOrderDetailsPrintClicked;
    
    openModal(modal);
}

function onOrderDetailsInputsChanged() {
    const orderNr = document.getElementById('o-ordernr').value.trim();
    const jobNr = document.getElementById('o-jobnr').value.trim();
    const protocolNr = document.getElementById('o-protocolnr').value.trim();
    
    const valid = orderNr !== "" && jobNr !== "" && protocolNr !== "";
    const btn = document.getElementById('btn-print-order');
    if (valid) {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

async function onOrderDetailsPrintClicked() {
    const schemeNr = elSchemeNr.value.trim();
    const schemeRev = elSchemeRev.value.trim();
    const scheme = `${schemeNr}-${schemeRev}`;
    
    const orderDetails = [
        document.getElementById('o-ordernr').value.trim(),
        document.getElementById('o-jobnr').value.trim(),
        document.getElementById('o-protocolnr').value.trim()
    ];
    
    // Proceed directly with actual PDF generation (do not check or save templates)
    const exportPayload = {
        scheme: scheme,
        order_details: orderDetails,
        full_instructions: fullInstructions,
        override: true
    };
    
    try {
        const exportRes = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(exportPayload)
        });
        
        if (exportRes.ok) {
            // Get PDF blob and print directly from the browser
            const blob = await exportRes.blob();
            const pdfUrl = URL.createObjectURL(blob);
            
            const iframe = document.createElement('iframe');
            iframe.style.display = 'none';
            iframe.src = pdfUrl;
            document.body.appendChild(iframe);
            
            iframe.onload = () => {
                try {
                    iframe.contentWindow.focus();
                    iframe.contentWindow.print();
                } catch (e) {
                    console.error("Direct print failed, falling back to new tab", e);
                    window.open(pdfUrl, '_blank');
                }
                // Clean up iframe and revoke object URL after print dialog is shown
                setTimeout(() => {
                    if (iframe.parentNode) {
                        document.body.removeChild(iframe);
                    }
                    URL.revokeObjectURL(pdfUrl);
                }, 60000);
            };
            
            closeModal(document.getElementById('modal-order-details'));
        } else {
            const err = await exportRes.json();
            alert(`Export fehlgeschlagen: ${err.error || 'Serverfehler'}`);
        }
        
    } catch (e) {
        console.error("Export PDF error", e);
    }
}


// ==================== 5. SETTINGS DIALOG MODAL ====================

let settingsLocalValues = [];

function openSettingsModal() {
    const modal = document.getElementById('modal-settings');
    
    settingsLocalValues = copyObject(settings.xsec_soll_values);
    
    // Reset Form
    document.getElementById('s-xsec').value = '';
    document.getElementById('s-soll-open').value = '';
    document.getElementById('s-soll-closed').value = '';
    
    document.getElementById('btn-save-settings-entry').setAttribute('disabled', 'true');
    document.getElementById('btn-delete-settings-entry').setAttribute('disabled', 'true');
    document.getElementById('btn-apply-settings').setAttribute('disabled', 'true');
    
    // Event listeners
    const inputs = ['s-xsec', 's-soll-open', 's-soll-closed'];
    inputs.forEach(id => {
        document.getElementById(id).oninput = onSettingsInputsChanged;
    });
    
    document.getElementById('btn-save-settings-entry').onclick = onSettingsSaveEntryClicked;
    document.getElementById('btn-delete-settings-entry').onclick = onSettingsDeleteEntryClicked;
    document.getElementById('btn-apply-settings').onclick = onSettingsApplyClicked;
    
    populateSettingsTable();
    openModal(modal);
}

function populateSettingsTable() {
    const tbody = document.getElementById('settings-xsecs-list');
    tbody.innerHTML = '';
    
    settingsLocalValues.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${row[0]} mm²</td>
            <td>${row[1]} N</td>
            <td>${row[2]} N</td>
        `;
        
        tr.onclick = () => {
            tbody.querySelectorAll('tr').forEach((r, idx) => {
                if (idx === index) r.classList.add('selected');
                else r.classList.remove('selected');
            });
            
            // Set inputs
            document.getElementById('s-xsec').value = row[0];
            document.getElementById('s-soll-open').value = row[1];
            document.getElementById('s-soll-closed').value = row[2];
            
            document.getElementById('btn-save-settings-entry').textContent = "Ändern";
            document.getElementById('btn-save-settings-entry').removeAttribute('disabled');
            
            const delBtn = document.getElementById('btn-delete-settings-entry');
            delBtn.removeAttribute('disabled');
            delBtn.dataset.index = index;
        };
        
        tbody.appendChild(tr);
    });
}

function onSettingsInputsChanged() {
    const xs = document.getElementById('s-xsec').value.trim();
    const btn = document.getElementById('btn-save-settings-entry');
    
    if (xs !== "") {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

function onSettingsSaveEntryClicked() {
    const xs = document.getElementById('s-xsec').value.trim();
    const openVal = document.getElementById('s-soll-open').value.trim();
    const closedVal = document.getElementById('s-soll-closed').value.trim();
    
    // Bugfix: Parse & Validate numeric input values before converting with int() equivalents in settings
    const parsedOpen = parseInt(openVal);
    const parsedClosed = parseInt(closedVal);
    
    if (isNaN(parsedOpen) || isNaN(parsedClosed)) {
        alert("Bitte nur ganzzahlige Werte für die Soll-Werte eingeben.");
        return;
    }
    
    // Check if exists
    let index = -1;
    for (let i = 0; i < settingsLocalValues.length; i++) {
        if (settingsLocalValues[i][0] === xs) {
            index = i;
            break;
        }
    }
    
    if (index > -1) {
        settingsLocalValues.splice(index, 1);
    }
    
    settingsLocalValues.push([xs, parsedOpen, parsedClosed]);
    // Sort by pull force open value (index 1)
    settingsLocalValues.sort((a, b) => a[1] - b[1]);
    
    populateSettingsTable();
    
    // Reset Form
    document.getElementById('s-xsec').value = '';
    document.getElementById('s-soll-open').value = '';
    document.getElementById('s-soll-closed').value = '';
    
    document.getElementById('btn-save-settings-entry').textContent = "Speichern";
    document.getElementById('btn-save-settings-entry').setAttribute('disabled', 'true');
    document.getElementById('btn-delete-settings-entry').setAttribute('disabled', 'true');
    document.getElementById('btn-apply-settings').removeAttribute('disabled');
}

function onSettingsDeleteEntryClicked(e) {
    const index = parseInt(e.target.dataset.index);
    if (!isNaN(index) && index >= 0 && index < settingsLocalValues.length) {
        settingsLocalValues.splice(index, 1);
        populateSettingsTable();
        
        document.getElementById('s-xsec').value = '';
        document.getElementById('s-soll-open').value = '';
        document.getElementById('s-soll-closed').value = '';
        
        document.getElementById('btn-save-settings-entry').textContent = "Speichern";
        document.getElementById('btn-save-settings-entry').setAttribute('disabled', 'true');
        e.target.setAttribute('disabled', 'true');
        document.getElementById('btn-apply-settings').removeAttribute('disabled');
    }
}

async function onSettingsApplyClicked() {
    const payload = {
        xsec_soll_values: settingsLocalValues
    };
    
    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (res.ok) {
            settings = payload;
            closeModal(document.getElementById('modal-settings'));
        } else {
            alert("Fehler beim Speichern der Einstellungen.");
        }
    } catch (e) {
        console.error("Apply settings error", e);
    }
}


// --- Utility Helpers ---

function copyObject(obj) {
    return JSON.parse(JSON.stringify(obj));
}


// --- Printed Orders Management ---

async function fetchOrders() {
    try {
        const res = await fetch('/api/orders');
        if (res.ok) {
            orders = await res.json();
            populateOrdersList();
        } else {
            console.error("Failed to fetch orders");
        }
    } catch (e) {
        console.error("Fetch orders error", e);
    }
}

function updateSortIcons() {
    const headers = [
        { id: 'th-order-date', key: 'mtime' },
        { id: 'th-order-proto', key: 'protocol_nr' },
        { id: 'th-order-file', key: 'filename' },
        { id: 'th-order-size', key: 'size' }
    ];
    
    headers.forEach(h => {
        const el = document.getElementById(h.id);
        if (!el) return;
        const iconSpan = el.querySelector('.sort-icon');
        if (!iconSpan) return;
        
        if (ordersSortKey === h.key) {
            iconSpan.textContent = ordersSortDirection === 'asc' ? ' ▲' : ' ▼';
            iconSpan.style.color = 'var(--accent)';
        } else {
            iconSpan.textContent = '';
            iconSpan.style.color = 'var(--text-secondary)';
        }
    });
}

function populateOrdersList() {
    const tbody = document.getElementById('orders-list-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    const searchVal = document.getElementById('search-orders').value.toLowerCase().trim();
    
    // 1. Filter
    let filteredOrders = orders.filter(ord => {
        return ord.filename.toLowerCase().includes(searchVal) ||
               ord.protocol_nr.toLowerCase().includes(searchVal);
    });
    
    // 2. Sort
    filteredOrders.sort((a, b) => {
        let valA, valB;
        if (ordersSortKey === "mtime" || ordersSortKey === "size") {
            valA = a[ordersSortKey];
            valB = b[ordersSortKey];
            return ordersSortDirection === "asc" ? valA - valB : valB - valA;
        } else {
            valA = a[ordersSortKey].toLowerCase();
            valB = b[ordersSortKey].toLowerCase();
            if (valA < valB) return ordersSortDirection === "asc" ? -1 : 1;
            if (valA > valB) return ordersSortDirection === "asc" ? 1 : -1;
            return 0;
        }
    });
    
    // 3. Render
    if (filteredOrders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine gedruckten Aufträge gefunden.</td></tr>`;
        return;
    }
    
    filteredOrders.forEach(ord => {
        const tr = document.createElement('tr');
        const sizeKB = (ord.size / 1024).toFixed(1) + " KB";
        
        tr.innerHTML = `
            <td>${ord.formatted_date}</td>
            <td style="font-weight: 500;">${ord.protocol_nr}</td>
            <td>${ord.filename}</td>
            <td style="color: var(--text-secondary);">${sizeKB}</td>
            <td style="text-align: center;">
                <button class="btn btn-secondary btn-sm btn-print-row-pdf" data-filepath="${ord.filepath}">🖨️ Drucken</button>
            </td>
        `;
        
        tr.querySelector('.btn-print-row-pdf').addEventListener('click', (e) => {
            const filepath = e.target.getAttribute('data-filepath');
            printOrderPDF(filepath);
        });
        
        tbody.appendChild(tr);
    });
}

function printOrderPDF(filepath) {
    const pdfUrl = `/api/orders/download/${encodeURIComponent(filepath)}`;
    
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = pdfUrl;
    document.body.appendChild(iframe);
    
    iframe.onload = () => {
        try {
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        } catch (e) {
            console.error("Direct print failed, falling back to new tab", e);
            window.open(pdfUrl, '_blank');
        }
        setTimeout(() => {
            if (iframe.parentNode) {
                document.body.removeChild(iframe);
            }
        }, 60000);
    };
}

function openSaveTemplateModal() {
    document.getElementById('save-scheme-nr').value = elSchemeNr.value;
    document.getElementById('save-scheme-rev').value = elSchemeRev.value;
    openModal(document.getElementById('modal-save-template'));
}
