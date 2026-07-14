/**
 * Orders Browser View Module
 * Handles loading, searching, sorting and printing previous orders.
 */
import { state } from '../state.js';
import { apiFetchOrders } from '../api.js';
import { showToast } from '../toast.js';

const elOrdersTable = document.getElementById('orders-table-body');
const elOrdersSearch = document.getElementById('search-orders');

export function initOrders() {
    if (elOrdersSearch) {
        elOrdersSearch.addEventListener('input', () => {
            populateOrdersList();
        });
    }

    // Set up column sorting click handlers (Phase 2.5)
    document.querySelectorAll('#table-orders th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const key = th.getAttribute('data-sort');
            handleHeaderSort(key);
        });
    });
}

export async function loadOrdersView() {
    try {
        const orders = await apiFetchOrders();
        state.orders = orders;
        populateOrdersList();
    } catch (e) {
        console.error("Load orders view failed", e);
    }
}

function handleHeaderSort(key) {
    if (state.ordersSortKey === key) {
        // Toggle direction
        state.ordersSortDirection = state.ordersSortDirection === "asc" ? "desc" : "asc";
    } else {
        state.ordersSortKey = key;
        state.ordersSortDirection = "desc"; // Default desc for new key
    }

    // Update th headers UI
    document.querySelectorAll('#table-orders th.sortable').forEach(th => {
        const sortIcon = th.querySelector('.sort-icon');
        if (!sortIcon) return;
        
        if (th.getAttribute('data-sort') === key) {
            sortIcon.textContent = state.ordersSortDirection === "asc" ? " ▲" : " ▼";
        } else {
            sortIcon.textContent = " ↕";
        }
    });

    populateOrdersList();
}

function populateOrdersList() {
    elOrdersTable.innerHTML = '';
    
    let filtered = [...state.orders];
    const searchPattern = elOrdersSearch ? elOrdersSearch.value.trim().toLowerCase() : "";
    
    if (searchPattern) {
        filtered = filtered.filter(ord => {
            return ord.filename.toLowerCase().includes(searchPattern) ||
                   ord.protocol_nr.toLowerCase().includes(searchPattern);
        });
    }
    
    // Sort logic
    filtered.sort((a, b) => {
        let valA = a[state.ordersSortKey];
        let valB = b[state.ordersSortKey];
        
        if (typeof valA === 'string') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
            return state.ordersSortDirection === "asc" 
                ? valA.localeCompare(valB) 
                : valB.localeCompare(valA);
        } else {
            return state.ordersSortDirection === "asc"
                ? valA - valB
                : valB - valA;
        }
    });
    
    if (filtered.length === 0) {
        elOrdersTable.innerHTML = `<tr><td colspan="4" class="text-center" style="color: var(--text-secondary); padding: 20px;">Keine gedruckten Aufträge vorhanden.</td></tr>`;
        return;
    }
    
    filtered.forEach(ord => {
        const tr = document.createElement('tr');
        
        // Format size
        const sizeKb = (ord.size / 1024).toFixed(1);
        
        tr.innerHTML = `
            <td>${ord.formatted_date}</td>
            <td style="font-weight: 600;">${ord.protocol_nr}</td>
            <td>${ord.filename}</td>
            <td class="text-right">${sizeKb} KB</td>
        `;
        
        tr.addEventListener('click', () => {
            printOrderPDF(ord.filepath);
        });
        
        elOrdersTable.appendChild(tr);
    });
}

function printOrderPDF(filepath) {
    const url = `/api/orders/download/${encodeURIComponent(filepath)}`;
    showToast("Auftrag wird zum Drucker gesendet...", "info");
    
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = url;
    document.body.appendChild(iframe);
    
    iframe.onload = () => {
        iframe.contentWindow.focus();
        iframe.contentWindow.print();
        
        // Cleanup after print dialog opens
        setTimeout(() => {
            iframe.remove();
        }, 1000);
    };
}
