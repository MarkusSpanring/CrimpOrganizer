/**
 * Context Menus Controller
 */
import { state } from './state.js';

export function showContextMenu(menuElement, x, y) {
    hideAllContextMenus();
    if (!menuElement) return;
    
    menuElement.style.display = 'block';
    
    // Boundary checks so menu doesn't overflow screen bounds
    const menuWidth = menuElement.offsetWidth || 180;
    const menuHeight = menuElement.offsetHeight || 100;
    const windowWidth = window.innerWidth;
    const windowHeight = window.innerHeight;
    
    let left = x;
    let top = y;
    
    if (x + menuWidth > windowWidth) left = windowWidth - menuWidth - 5;
    if (y + menuHeight > windowHeight) top = windowHeight - menuHeight - 5;
    
    menuElement.style.left = `${left}px`;
    menuElement.style.top = `${top}px`;
}

export function hideAllContextMenus() {
    const menus = [
        document.getElementById('contact-context-menu'),
        document.getElementById('tool-context-menu'),
        document.getElementById('instruction-context-menu'),
        document.getElementById('tree-context-menu')
    ];
    menus.forEach(menu => {
        if (menu) menu.style.display = 'none';
    });
}

export function setupContextMenus() {
    document.addEventListener('click', hideAllContextMenus);
    window.addEventListener('blur', hideAllContextMenus);
    
    // Hide menus on scrolling lists
    document.querySelectorAll('.list-container').forEach(c => {
        c.addEventListener('scroll', hideAllContextMenus);
    });
}
