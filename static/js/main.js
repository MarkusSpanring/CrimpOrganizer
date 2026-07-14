/**
 * Application Entry Point
 * Bootstraps CrimpOrganizer, registers all modules, and handles initial data load.
 */
import { state } from './state.js';
import { 
    apiFetchSettings, 
    apiFetchContacts, 
    apiFetchTools, 
    apiFetchInstructions,
    apiTriggerUpdate
} from './api.js';

// Setup Helpers
import { setupRouter } from './router.js';
import { setupContextMenus } from './contextMenu.js';
import { setupKeyboardShortcuts } from './keyboard.js';

// Views
import { initOverview, populateDrawingsList } from './views/overview.js';
import { initEditor, populateContacts, populateTools } from './views/editor.js';
import { initOrders } from './views/orders.js';

// Modals
import { initContactEditor } from './modals/contactEditor.js';
import { initToolEditor } from './modals/toolEditor.js';
import { initSettingsDialog, openSettingsModal } from './modals/settingsDialog.js';
import { initAnnotate } from './modals/annotate.js';
import { initOrderDetails } from './modals/orderDetails.js';
import { openModal, closeModal } from './modal.js';
import { showToast } from './toast.js';

function instantiateTemplates() {
    const templates = document.querySelectorAll('template[id^="tmpl-"]');
    templates.forEach(tmpl => {
        const clone = tmpl.content.cloneNode(true);
        document.body.appendChild(clone);
    });
}

async function bootstrap() {
    instantiateTemplates();
    // Show toast loader status
    showToast("Lade Anwendungsdaten...", "info", 1500);

    try {
        // Fetch all primary resources in parallel
        const [settings, contacts, tools, instructions] = await Promise.all([
            apiFetchSettings(),
            apiFetchContacts(),
            apiFetchTools(),
            apiFetchInstructions()
        ]);

        // Assign to global state store
        state.settings = settings;
        state.contacts = contacts;
        state.tools = tools;
        state.instructions = instructions;

        // Initialize Modals Event Listeners
        initContactEditor();
        initToolEditor();
        initSettingsDialog();
        initAnnotate();
        initOrderDetails();

        // Initialize Views Event Listeners
        initOverview();
        initEditor();
        initOrders();

        // Setup generic overlay actions (close modals on overlay click or cancel button)
        setupModalCloseTriggers();

        // Setup routing, context menus, and keyboard shortcuts
        setupRouter();
        setupContextMenus();
        setupKeyboardShortcuts();

        // Render initial UI data
        populateDrawingsList();
        populateContacts();
        populateTools();

        // Setup settings sidebar action trigger
        const btnSettingsNav = document.getElementById('btn-settings-nav');
        if (btnSettingsNav) {
            btnSettingsNav.addEventListener('click', (e) => {
                e.preventDefault();
                openSettingsModal();
            });
        }

        // Setup update sidebar action trigger
        const btnUpdateNav = document.getElementById('btn-update-nav');
        if (btnUpdateNav) {
            btnUpdateNav.addEventListener('click', async (e) => {
                e.preventDefault();
                if (!confirm("Möchten Sie die Anwendung jetzt aktualisieren? Dabei wird der neueste Code aus dem Git-Repository heruntergeladen und die Anwendung neu gestartet.")) {
                    return;
                }
                
                const modal = document.getElementById('modal-update-status');
                if (!modal) return;
                
                // Reset elements to initial loading state
                const elSpinner = document.getElementById('update-loader-spinner');
                const elStatusText = document.getElementById('update-status-text');
                const elOutputContainer = document.getElementById('update-output-container');
                const elConsoleLog = document.getElementById('update-console-log');
                const elCountdownText = document.getElementById('update-countdown-text');
                const elSecondsLeft = document.getElementById('update-seconds-left');
                const elFooter = document.getElementById('update-status-footer');
                const btnClose = document.getElementById('btn-close-update-modal');
                
                if (elSpinner) elSpinner.style.display = 'block';
                if (elStatusText) elStatusText.textContent = 'Repository-Änderungen werden abgerufen...';
                if (elOutputContainer) elOutputContainer.style.display = 'none';
                if (elConsoleLog) elConsoleLog.textContent = '';
                if (elCountdownText) elCountdownText.style.display = 'none';
                if (elFooter) elFooter.style.display = 'none';
                
                // Set up close button listener
                if (btnClose) {
                    btnClose.onclick = () => closeModal(modal);
                }
                
                openModal(modal);
                
                try {
                    const res = await apiTriggerUpdate();
                    
                    if (elSpinner) elSpinner.style.display = 'none';
                    if (elOutputContainer) elOutputContainer.style.display = 'flex';
                    
                    if (res && res.success) {
                        if (elConsoleLog) elConsoleLog.textContent = res.message || "Git Pull erfolgreich.";
                        if (elCountdownText) elCountdownText.style.display = 'block';
                        
                        // Start 3 seconds countdown
                        let seconds = 3;
                        if (elSecondsLeft) elSecondsLeft.textContent = seconds;
                        const interval = setInterval(() => {
                            seconds--;
                            if (elSecondsLeft) elSecondsLeft.textContent = seconds;
                            if (seconds <= 0) {
                                clearInterval(interval);
                                window.location.reload();
                            }
                        }, 1000);
                        
                    } else {
                        if (elConsoleLog) elConsoleLog.textContent = "Fehler: " + (res.error || "Unbekannter Fehler");
                        if (elFooter) elFooter.style.display = 'flex';
                    }
                } catch (err) {
                    if (elSpinner) elSpinner.style.display = 'none';
                    if (elOutputContainer) elOutputContainer.style.display = 'flex';
                    if (elConsoleLog) elConsoleLog.textContent = "Verbindung verloren oder Fehler beim Neustart.\nDie Anwendung startet wahrscheinlich gerade neu. Lade in Kürze neu...";
                    if (elCountdownText) {
                        elCountdownText.style.display = 'block';
                        elCountdownText.innerHTML = 'Seite wird in Kürze neu geladen...';
                    }
                    
                    setTimeout(() => {
                        window.location.reload();
                    }, 5000);
                }
            });
        }

        showToast("Bereit", "success", 1000);

    } catch (e) {
        console.error("Application bootstrap failed", e);
        showToast("Kritischer Ladefehler. Bitte Seite neu laden.", "error", 10000);
    }
}

function setupModalCloseTriggers() {
    // Wire all elements with class .modal-close to close their parent modal
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const overlay = e.target.closest('.modal-overlay');
            if (overlay) closeModal(overlay);
        });
    });
    
    // Clicking cancel button inside footers
    document.querySelectorAll('.modal-footer .btn-secondary').forEach(btn => {
        btn.addEventListener('click', (e) => {
            // Only if it doesn't have inline custom handler
            if (!btn.id || btn.id === 'btn-cancel-contact' || btn.id === 'btn-cancel-tool' || btn.id === 'btn-cancel-settings') {
                const overlay = e.target.closest('.modal-overlay');
                if (overlay) closeModal(overlay);
            }
        });
    });

    // Clicking overlay backdrop directly closes modal
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                closeModal(overlay);
            }
        });
    });
}

// Bootstrap once the DOM content is ready
document.addEventListener('DOMContentLoaded', bootstrap);
