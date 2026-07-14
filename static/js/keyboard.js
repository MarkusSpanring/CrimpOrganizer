/**
 * Keyboard Shortcuts Module (Phase 2.2)
 * Handles global key events to accelerate navigation and editor actions.
 */
import { state } from './state.js';
import { switchView } from './router.js';
import { openContactEditor } from './modals/contactEditor.js';
import { clearEditor } from './views/editor.js';
import { closeModal } from './modal.js';

export function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // ESC -> Close active modal or deselect
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal-overlay.active');
            if (activeModal) {
                closeModal(activeModal);
                e.preventDefault();
            } else if (state.activeView === 'view-editor' && state.selectedContactRef) {
                state.selectedContactRef = "";
                document.querySelectorAll('#contacts-table-body tr').forEach(r => r.classList.remove('selected'));
                import('./views/editor.js').then(ed => ed.populateTools());
                e.preventDefault();
            }
        }

        // Ctrl + 1/2/3 -> Switch views
        if (e.ctrlKey && !e.shiftKey && !e.altKey) {
            if (e.key === '1') {
                switchView('view-overview');
                e.preventDefault();
            } else if (e.key === '2') {
                switchView('view-editor');
                e.preventDefault();
            } else if (e.key === '3') {
                switchView('view-orders');
                e.preventDefault();
            }
        }

        // Editor specific shortcuts
        if (state.activeView === 'view-editor') {
            // Ctrl + S -> Save draft
            if (e.ctrlKey && e.key === 's') {
                const btnSave = document.getElementById('btn-save-draft');
                if (btnSave && !btnSave.disabled) {
                    btnSave.click();
                    e.preventDefault();
                }
            }

            // Ctrl + N -> New contact
            if (e.ctrlKey && e.key === 'n') {
                openContactEditor();
                e.preventDefault();
            }

            // Delete key -> Remove selected instruction row
            if (e.key === 'Delete' && state.selectedInstructionRow > -1) {
                // Confirm cursor is not inside an input box to prevent interference
                if (document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'SELECT') {
                    import('./views/editor.js').then(ed => {
                        ed.removeInstruction(state.selectedInstructionRow);
                    });
                    e.preventDefault();
                }
            }
        }
    });
}
