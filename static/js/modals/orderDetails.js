/**
 * Order Details / Print Modal Module
 */
import { state } from '../state.js';
import { apiExportPdf } from '../api.js';
import { openModal, closeModal } from '../modal.js';
import { showToast } from '../toast.js';

let modal;
let elBestellNr;
let elAuftragsNr;
let elProtokollNr;
let btnPrint;

export function initOrderDetails() {
    modal = document.getElementById('modal-order-details');
    elBestellNr = document.getElementById('o-bestellnr');
    elAuftragsNr = document.getElementById('o-auftragsnr');
    elProtokollNr = document.getElementById('o-protokollnr');
    btnPrint = document.getElementById('btn-order-print');
    
    if (btnPrint) {
        btnPrint.addEventListener('click', onOrderDetailsPrintClicked);
    }
}

export function openOrderDetailsModal() {
    // Clear inputs on open
    elBestellNr.value = "";
    elAuftragsNr.value = "";
    elProtokollNr.value = "";
    
    openModal(modal);
}

async function onOrderDetailsPrintClicked() {
    const schemeNr = document.getElementById('scheme-nr') ? document.getElementById('scheme-nr').value.trim() : "";
    const schemeRev = document.getElementById('scheme-rev') ? document.getElementById('scheme-rev').value.trim() : "";
    const scheme = `${schemeNr}-${schemeRev}`;
    
    if (!schemeNr || !schemeRev) {
        showToast("Zeichnungsnummer und Revision müssen im Editor gefüllt sein.", "warning");
        return;
    }
    
    const orderDetails = [
        elBestellNr.value.trim(),
        elAuftragsNr.value.trim(),
        elProtokollNr.value.trim(),
        schemeNr
    ];
    
    const payload = {
        scheme: scheme,
        order_details: orderDetails,
        full_instructions: Object.keys(state.fullInstructions)
    };
    
    btnPrint.disabled = true;
    btnPrint.textContent = "Generiere PDF...";
    
    try {
        const blob = await apiExportPdf(payload);
        closeModal(modal);
        showToast("PDF erfolgreich generiert. Druckdialog wird geöffnet.", "success");
        
        // Print PDF using hidden iframe
        const url = URL.createObjectURL(blob);
        const iframe = document.createElement('iframe');
        iframe.style.display = 'none';
        iframe.src = url;
        document.body.appendChild(iframe);
        iframe.onload = () => {
            iframe.contentWindow.focus();
            iframe.contentWindow.print();
        };
    } catch (e) {
        console.error("Print export failed", e);
    } finally {
        btnPrint.disabled = false;
        btnPrint.textContent = "Drucken";
    }
}
