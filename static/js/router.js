/**
 * Frontend Router and Navigation Controller
 */
import { state } from './state.js';
import { loadOrdersView } from './views/orders.js';

export function setupRouter() {
    const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            const targetView = item.getAttribute('data-view');
            if (targetView) {
                switchView(targetView);
            }
        });
    });
    
    // Sidebar toggle listener (Phase 2.6 collapse support)
    const toggleBtn = document.getElementById('sidebar-toggle-btn');
    const sidebar = document.getElementById('sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            
            // Persist preference in localStorage
            localStorage.setItem('sidebar-collapsed', sidebar.classList.contains('collapsed'));
        });
        
        // Restore collapse preference
        if (localStorage.getItem('sidebar-collapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }
    }
}

export function switchView(targetViewId) {
    if (state.activeView === targetViewId) return;
    
    // Unsaved changes check when leaving editor view (Phase 1 router guard)
    if (state.activeView === 'view-editor' && state.editorHasChanges) {
        const leave = confirm("Sie haben ungespeicherte Änderungen im Editor. Möchten Sie diesen Ansicht trotzdem verlassen?");
        if (!leave) return;
    }
    
    // De-activate old nav item
    const currentNavItem = document.querySelector(`.sidebar-nav .nav-item[data-view="${state.activeView}"]`);
    if (currentNavItem) currentNavItem.classList.remove('active');
    
    // Hide old view panel
    const currentViewEl = document.getElementById(state.activeView);
    if (currentViewEl) currentViewEl.classList.add('hidden');
    
    // Activate new nav item
    const newNavItem = document.querySelector(`.sidebar-nav .nav-item[data-view="${targetViewId}"]`);
    if (newNavItem) newNavItem.classList.add('active');
    
    // Show new view panel
    const newViewEl = document.getElementById(targetViewId);
    if (newViewEl) newViewEl.classList.remove('hidden');
    
    state.activeView = targetViewId;
    
    // Trigger callbacks per view loading
    if (targetViewId === 'view-orders') {
        loadOrdersView();
    } else if (targetViewId === 'view-overview') {
        // Redraw overview lists
        import('./views/overview.js').then(ov => {
            ov.populateDrawingsList();
            if (state.selectedDrawingNr) {
                ov.populateRevisionsList(state.selectedDrawingNr);
            }
        });
    }
}
