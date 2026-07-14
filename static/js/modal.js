/**
 * Generic Modal Overlay manager
 */

export function openModal(modalElement) {
    if (!modalElement) return;
    modalElement.style.display = 'flex';
    // Allow transitions to fire
    setTimeout(() => {
        modalElement.classList.add('active');
    }, 10);
    
    // Accessibility: set focus trap if needed
    trapFocus(modalElement);
}

export function closeModal(modalElement) {
    if (!modalElement) return;
    modalElement.classList.remove('active');
    setTimeout(() => {
        modalElement.style.display = 'none';
    }, 300);
}

// Trap focus inside modal for better accessibility (Phase 2.7)
function trapFocus(modal) {
    const focusableElements = modal.querySelectorAll('button, [href], input, select, textarea, [tabindex="0"]');
    if (focusableElements.length === 0) return;
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    // Focus first element
    setTimeout(() => {
        firstElement.focus();
    }, 50);
    
    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            if (e.shiftKey) { // Shift + Tab
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else { // Tab
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        }
    });
}
