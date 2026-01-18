/* ============================================================
   A1 Siri-Style Overlay - JavaScript Controller
   ============================================================
   
   This module controls the overlay behavior and communication
   with the Tauri backend.
   
   Key Features:
   - State management (idle, listening, thinking, speaking, error)
   - Toggle between interactive and click-through modes
   - Communication with Python backend via Tauri commands
   ============================================================ */

// Wait for Tauri to be available
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

// ============================================================
// DOM Elements
// ============================================================
const container = document.getElementById('overlay-container');
const orb = document.getElementById('orb');
const waveform = document.getElementById('waveform');
const centerIcon = document.getElementById('center-icon');
const statusText = document.getElementById('status-text');

// ============================================================
// State Management
// ============================================================
const OverlayState = {
    IDLE: 'idle',
    LISTENING: 'listening',
    THINKING: 'thinking',
    SPEAKING: 'speaking',
    ERROR: 'error'
};

let currentState = OverlayState.IDLE;
let isInteractive = false;

// ============================================================
// State Control Functions
// ============================================================

/**
 * Set the visual state of the overlay orb
 * @param {string} state - One of: idle, listening, thinking, speaking, error
 */
function setState(state) {
    // Remove all state classes
    orb.classList.remove('idle', 'listening', 'thinking', 'speaking', 'error');

    // Add the new state class
    orb.classList.add(state);
    currentState = state;

    // Update status text
    const stateLabels = {
        idle: 'A1',
        listening: 'Listening...',
        thinking: 'Thinking...',
        speaking: 'Speaking...',
        error: 'Error'
    };
    statusText.textContent = stateLabels[state] || 'A1';

    console.log(`[A1 Overlay] State changed to: ${state}`);
}

/**
 * Enable interactive mode - window accepts mouse/keyboard input
 */
async function enableInteraction() {
    try {
        await invoke('enable_interaction');
        isInteractive = true;
        container.classList.add('interactive');
        console.log('[A1 Overlay] Interactive mode enabled');
    } catch (error) {
        console.error('[A1 Overlay] Failed to enable interaction:', error);
    }
}

/**
 * Disable interactive mode - window becomes click-through
 */
async function disableInteraction() {
    try {
        await invoke('disable_interaction');
        isInteractive = false;
        container.classList.remove('interactive');
        console.log('[A1 Overlay] Interactive mode disabled');
    } catch (error) {
        console.error('[A1 Overlay] Failed to disable interaction:', error);
    }
}

/**
 * Toggle between interactive and click-through modes
 */
async function toggleInteraction() {
    if (isInteractive) {
        await disableInteraction();
    } else {
        await enableInteraction();
    }
}

// ============================================================
// Event Listeners
// ============================================================

// Listen for state changes from Rust backend
listen('overlay-state', (event) => {
    setState(event.payload);
});

// Listen for interaction mode changes
listen('interaction-mode', (event) => {
    isInteractive = event.payload;
    if (isInteractive) {
        container.classList.add('interactive');
    } else {
        container.classList.remove('interactive');
    }
});

// ============================================================
// Keyboard Shortcuts (only work in interactive mode)
// ============================================================
document.addEventListener('keydown', async (e) => {
    if (!isInteractive) return;

    switch (e.key) {
        case 'Escape':
            // Return to click-through mode
            await disableInteraction();
            break;
        case ' ':
            // Spacebar to toggle listening
            if (currentState === OverlayState.LISTENING) {
                setState(OverlayState.IDLE);
            } else {
                setState(OverlayState.LISTENING);
            }
            break;
    }
});

// ============================================================
// Click Handler (only works in interactive mode)
// ============================================================
orb.addEventListener('click', async () => {
    if (!isInteractive) return;

    // Toggle between idle and listening on click
    if (currentState === OverlayState.IDLE) {
        setState(OverlayState.LISTENING);
    } else if (currentState === OverlayState.LISTENING) {
        setState(OverlayState.IDLE);
    }
});

// ============================================================
// Double-click to enable interaction (if temporarily enabled)
// ============================================================
orb.addEventListener('dblclick', async () => {
    if (isInteractive) {
        await disableInteraction();
    }
});

// ============================================================
// Expose functions to window for external access
// ============================================================
window.A1Overlay = {
    setState,
    enableInteraction,
    disableInteraction,
    toggleInteraction,
    getState: () => currentState,
    isInteractive: () => isInteractive,
    OverlayState
};

// ============================================================
// Initialization
// ============================================================
console.log('============================================================');
console.log('[A1 Overlay] Frontend initialized');
console.log('  - Default state: IDLE');
console.log('  - Click-through: ENABLED');
console.log('  - Use window.A1Overlay.enableInteraction() to interact');
console.log('============================================================');

// Set initial state
setState(OverlayState.IDLE);

// ============================================================
// State Server Polling (IPC with Python backend)
// ============================================================
// The Python backend runs an HTTP server on port 9877
// that returns the current overlay state

const STATE_SERVER_URL = 'http://127.0.0.1:9877';
let lastState = 'idle';

async function pollStateServer() {
    try {
        const response = await fetch(STATE_SERVER_URL);
        if (response.ok) {
            const newState = (await response.text()).trim();
            if (newState && newState !== lastState) {
                lastState = newState;
                setState(newState);
                console.log(`[A1 Overlay] State updated: ${newState}`);
            }
        }
    } catch (error) {
        // Server not running yet, that's OK - Python will start it
    }
}

// Poll for state changes every 100ms (responsive updates)
setInterval(pollStateServer, 100);

// Initial poll
pollStateServer();

// ============================================================
// Demo: Cycle through states (remove in production)
// ============================================================
/*
const states = ['idle', 'listening', 'thinking', 'speaking'];
let stateIndex = 0;
setInterval(() => {
    setState(states[stateIndex]);
    stateIndex = (stateIndex + 1) % states.length;
}, 3000);
*/
