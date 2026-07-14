/**
 * Overview View Module
 * Handles drawing directories, revision selection, and preview controls.
 */
import { state, copyObject } from '../state.js';
import { apiFetchInstructions, apiDeleteInstructions } from '../api.js';
import { loadDrawingIntoEditor } from './editor.js';
import { openOrderDetailsModal } from '../modals/orderDetails.js';
import { showToast } from '../toast.js';

const elDrawingsList = document.getElementById('drawings-list');
const elRevisionsList = document.getElementById('revisions-list');
const elOverviewEmptyState = document.getElementById('overview-empty-state');
const elOverviewPreviewPanel = document.getElementById('overview-preview-panel');
const elPreviewTitle = document.getElementById('preview-title');
const elPreviewStepsList = document.getElementById('preview-steps-list');

export function initOverview() {
    // Search drawing filter
    const searchDrawingInput = document.getElementById('search-drawing');
    if (searchDrawingInput) {
        searchDrawingInput.addEventListener('input', (e) => {
            populateDrawingsList(e.target.value);
        });
    }

    // Overview buttons
    const btnPrintDrawing = document.getElementById('btn-print-drawing');
    if (btnPrintDrawing) {
        btnPrintDrawing.addEventListener('click', () => {
            if (state.selectedScheme) {
                const [sNr, sRev] = state.selectedScheme.split("-");
                state.fullInstructions = copyObject(state.instructions[sNr][sRev]);
                
                // Set hidden editor inputs just in case
                const elSchemeNr = document.getElementById('scheme-nr');
                const elSchemeRev = document.getElementById('scheme-rev');
                if (elSchemeNr) elSchemeNr.value = sNr;
                if (elSchemeRev) elSchemeRev.value = sRev;
                
                openOrderDetailsModal();
            }
        });
    }

    const btnEditDrawingTemplate = document.getElementById('btn-edit-drawing-template');
    if (btnEditDrawingTemplate) {
        btnEditDrawingTemplate.addEventListener('click', () => {
            if (state.selectedScheme) {
                const [sNr, sRev] = state.selectedScheme.split("-");
                loadDrawingIntoEditor(sNr, sRev);
            }
        });
    }

    const btnDeleteDrawingTemplate = document.getElementById('btn-delete-drawing-template');
    if (btnDeleteDrawingTemplate) {
        btnDeleteDrawingTemplate.addEventListener('click', () => {
            if (state.selectedScheme) {
                deleteScheme(state.selectedScheme);
            }
        });
    }
}

export function getReadableToolName(toolRef) {
    if (!state.tools[toolRef]) return toolRef;
    const t = state.tools[toolRef];
    const ids = t.IDs && t.IDs.length > 0 ? `(z.B. ${t.IDs.join(", ")})` : "";
    return `${t.producer} | ${t.series} ${ids}`;
}

export function populateDrawingsList(searchPattern = "") {
    elDrawingsList.innerHTML = '';
    
    const uniqueDrawings = Object.keys(state.instructions).sort((a, b) => {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    });
    
    uniqueDrawings.forEach(schemeNr => {
        if (searchPattern && !schemeNr.toLowerCase().includes(searchPattern.toLowerCase())) {
            return;
        }
        
        const li = document.createElement('li');
        if (schemeNr === state.selectedDrawingNr) {
            li.className = 'selected';
        }
        
        li.innerHTML = `
            <span class="nav-icon">📁</span>
            <span style="font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">${schemeNr}</span>
        `;
        
        li.addEventListener('click', () => {
            selectDrawingNr(schemeNr);
        });
        
        elDrawingsList.appendChild(li);
    });
}

export function selectDrawingNr(schemeNr) {
    state.selectedDrawingNr = schemeNr;
    
    document.querySelectorAll('#drawings-list li').forEach(li => {
        const titleSpan = li.querySelector('span:nth-child(2)');
        if (titleSpan && titleSpan.textContent === schemeNr) {
            li.classList.add('selected');
        } else {
            li.classList.remove('selected');
        }
    });
    
    if (state.selectedScheme && !state.selectedScheme.startsWith(`${schemeNr}-`)) {
        state.selectedScheme = "";
    }
    
    populateRevisionsList(schemeNr);
    
    if (state.selectedScheme) {
        const [_, rev] = state.selectedScheme.split("-");
        selectDrawing(schemeNr, rev);
    } else {
        elOverviewEmptyState.style.display = 'flex';
        elOverviewPreviewPanel.style.display = 'none';
    }
    
    updateBreadcrumbs();
}

export function populateRevisionsList(schemeNr) {
    elRevisionsList.innerHTML = '';
    if (!schemeNr || !state.instructions[schemeNr]) return;
    
    const revs = Object.keys(state.instructions[schemeNr]).sort((a, b) => {
        return a.toLowerCase().localeCompare(b.toLowerCase());
    });
    
    revs.forEach(rev => {
        const li = document.createElement('li');
        const key = `${schemeNr}-${rev}`;
        if (key === state.selectedScheme) {
            li.className = 'selected';
        }
        
        li.innerHTML = `
            <span class="nav-icon">📄</span>
            <span style="font-weight: 600;">Rev. ${rev}</span>
        `;
        
        li.addEventListener('click', () => {
            selectDrawing(schemeNr, rev);
        });
        
        elRevisionsList.appendChild(li);
    });
}

export function selectDrawing(schemeNr, rev) {
    state.selectedScheme = `${schemeNr}-${rev}`;
    state.selectedDrawingNr = schemeNr;
    
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
    
    elOverviewEmptyState.style.display = 'none';
    elOverviewPreviewPanel.style.display = 'flex';
    elPreviewTitle.textContent = `Zeichnung: ${schemeNr} (Rev. ${rev})`;
    
    elPreviewStepsList.innerHTML = '';
    const steps = state.instructions[schemeNr][rev];
    const entries = Object.keys(steps);
    
    if (entries.length === 0) {
        elPreviewStepsList.innerHTML = `<tr><td colspan="7" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine Schritte in dieser Anleitung.</td></tr>`;
    } else {
        entries.forEach(entry => {
            const [xs, contactRef] = entry.split("#");
            const details = steps[entry];
            const pos = details.pos || "";
            const slotName = details.name || "";
            
            const contactObj = state.contacts[contactRef] || {};
            const series = contactObj.series || "";
            const xsecData = contactObj.crosssection && contactObj.crosssection[xs] || {};
            
            const slot = xsecData.slot || "";
            const soll = xsecData.soll || "";
            const toolRef = xsecData.tool || "";
            
            const toolObj = state.tools[toolRef] || {};
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
            elPreviewStepsList.appendChild(tr);
        });
    }
    
    updateBreadcrumbs();
}

async function deleteScheme(key) {
    if (!confirm(`Soll die Anweisung für "${key}" unwiderruflich gelöscht werden?`)) {
        return;
    }
    try {
        const ok = await apiDeleteInstructions(key);
        if (ok) {
            showToast("Zeichnung erfolgreich gelöscht", "success");
            if (state.selectedScheme === key) {
                state.selectedScheme = "";
                state.fullInstructions = {};
                
                const elSchemeNr = document.getElementById('scheme-nr');
                const elSchemeRev = document.getElementById('scheme-rev');
                if (elSchemeNr) elSchemeNr.value = "";
                if (elSchemeRev) elSchemeRev.value = "";
            }
            
            // Reload instructions
            const res = await apiFetchInstructions();
            state.instructions = res;
            
            populateDrawingsList();
            
            if (state.selectedDrawingNr) {
                if (state.instructions[state.selectedDrawingNr]) {
                    populateRevisionsList(state.selectedDrawingNr);
                } else {
                    state.selectedDrawingNr = "";
                    elRevisionsList.innerHTML = '';
                }
            }
            if (!state.selectedScheme) {
                elOverviewEmptyState.style.display = 'flex';
                elOverviewPreviewPanel.style.display = 'none';
            }
            updateBreadcrumbs();
        } else {
            showToast("Fehler beim Löschen der Zeichnung.", "error");
        }
    } catch (e) {
        console.error("Delete scheme error", e);
    }
}

// Breadcrumb Navigation Support (Phase 2.4)
function updateBreadcrumbs() {
    let breadcrumbEl = document.getElementById('overview-breadcrumbs');
    if (!breadcrumbEl) {
        breadcrumbEl = document.createElement('div');
        breadcrumbEl.id = 'overview-breadcrumbs';
        breadcrumbEl.style.padding = '10px 16px';
        breadcrumbEl.style.fontSize = '0.85rem';
        breadcrumbEl.style.borderBottom = '1px solid var(--border-color)';
        breadcrumbEl.style.color = 'var(--text-secondary)';
        breadcrumbEl.style.backgroundColor = 'var(--bg-tertiary)';
        
        const previewPanel = document.getElementById('overview-preview-panel');
        if (previewPanel) {
            previewPanel.insertBefore(breadcrumbEl, previewPanel.firstChild);
        }
    }
    
    if (!state.selectedDrawingNr) {
        breadcrumbEl.innerHTML = 'Crimpanweisungen';
        return;
    }
    
    let html = `<span style="cursor:pointer;color:var(--accent);" id="crumb-root">Crimpanweisungen</span>`;
    html += ` &rsaquo; <span>${state.selectedDrawingNr}</span>`;
    
    if (state.selectedScheme) {
        const [_, rev] = state.selectedScheme.split("-");
        html += ` &rsaquo; <span style="font-weight:600;color:var(--text-primary);">Rev. ${rev}</span>`;
    }
    
    breadcrumbEl.innerHTML = html;
    
    const rootLink = document.getElementById('crumb-root');
    if (rootLink) {
        rootLink.addEventListener('click', () => {
            state.selectedDrawingNr = "";
            state.selectedScheme = "";
            populateDrawingsList();
            elRevisionsList.innerHTML = '';
            elOverviewEmptyState.style.display = 'flex';
            elOverviewPreviewPanel.style.display = 'none';
            updateBreadcrumbs();
        });
    }
}
