/**
 * Central State Store for CrimpOrganizer
 */

export const state = {
    // Loaded JSON data
    contacts: {},
    tools: {},
    instructions: {},
    orders: [],
    
    // Sort configurations for orders list
    ordersSortKey: "mtime",
    ordersSortDirection: "desc",
    
    // Loaded application settings
    settings: { xsec_soll_values: [] },
    
    // Pending draft payload if override modal was shown
    pendingSavePayload: null,
    
    // UI state selections
    selectedContactRef: "",
    selectedToolRef: "",
    selectedToolSummaryRows: [], // indices of selected rows in middle column
    selectedInstructionRow: -1, // index of selected row in right column
    selectedScheme: "", // Current active "Scheme-Rev" from the tree
    selectedDrawingNr: "",
    fullInstructions: {}, // Map of xs#contactRef -> { pos, name }
    
    // Right-click context values
    activeCtxContact: "",
    activeCtxTool: null, // index
    activeCtxInstruction: null, // index
    activeCtxTreeScheme: "", // "schemeNr-schemeRev"
    
    // Navigation state
    activeView: "view-overview",
    editorHasChanges: false,
};

// State Helper Functions
export function copyObject(obj) {
    return JSON.parse(JSON.stringify(obj));
}
