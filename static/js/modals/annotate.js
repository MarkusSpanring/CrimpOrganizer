/**
 * Annotation Modal Module
 */
import { state } from '../state.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';
import { populateCrimpInstructions } from '../views/editor.js';

let modal;
let elFields;

let localKeys = []; // Array of "#" keys (xs#contactRef) being annotated

export function initAnnotate() {
    modal = document.getElementById('modal-annotate');
    elFields = document.getElementById('annotation-fields');
    const btnApply = document.getElementById('btn-apply-annotations');
    if (btnApply) {
        btnApply.addEventListener('click', onApplyAnnotationsClicked);
    }
}

export function openAnnotationModal(keys = []) {
    localKeys = keys;
    elFields.innerHTML = '';
    
    keys.forEach(key => {
        const [xs, contactRef] = key.split("#");
        const contactObj = state.contacts[contactRef] || {};
        const contactName = contactObj.series ? `${contactRef} / ${contactObj.series}` : contactRef;
        
        // Find existing annotation values if present
        const currentVal = state.fullInstructions[key] || {};
        const currentPos = currentVal.pos || "";
        const currentName = currentVal.name || "";
        
        const row = document.createElement('div');
        row.className = 'annotation-row-fields';
        row.innerHTML = `
            <span class="annotation-label" title="${contactName} (${xs} mm²)">
                ${contactName} (${xs} mm²)
            </span>
            <input type="text" class="pos-input" data-key="${key}" placeholder="z.B. 1" value="${currentPos}">
            <input type="text" class="housing-input" data-key="${key}" placeholder="z.B. X1" value="${currentName}">
        `;
        
        elFields.appendChild(row);
    });
    
    openModal(modal);
}

function onApplyAnnotationsClicked() {
    const posInputs = elFields.querySelectorAll('.pos-input');
    const housingInputs = elFields.querySelectorAll('.housing-input');
    
    let error = false;
    
    // Check validation for positions
    posInputs.forEach(input => {
        const val = input.value.trim();
        if (!val) {
            showToast("Bitte alle Positionsnummern ausfüllen.", "warning");
            error = true;
        }
    });
    
    if (error) return;
    
    // Check validation for housing names
    housingInputs.forEach(input => {
        const val = input.value.trim();
        if (!val) {
            showToast("Bitte alle Gehäusebezeichnungen ausfüllen.", "warning");
            error = true;
        }
    });
    
    if (error) return;
    
    // Apply values to state.fullInstructions
    posInputs.forEach((input, index) => {
        const key = input.getAttribute('data-key');
        const pos = input.value.trim();
        const housing = housingInputs[index].value.trim();
        
        state.fullInstructions[key] = {
            pos: pos,
            name: housing
        };
    });
    
    state.editorHasChanges = true;
    closeModal(modal);
    populateCrimpInstructions();
    showToast("Zuweisung übernommen", "success");
}

export function openReannotateModal(index) {
    // Re-annotate a single instruction row from context menu or row action
    const entries = Object.keys(state.fullInstructions);
    if (index >= 0 && index < entries.length) {
        const key = entries[index];
        openAnnotationModal([key]);
    }
}
