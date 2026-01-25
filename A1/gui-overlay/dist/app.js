/* ============================================================
   A1 - Advanced Intelligence - Controller
   ============================================================ */

const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

// UI Elements
const orb = document.getElementById('main-orb');
const statusLabel = document.getElementById('mode-label');
const statusDot = document.querySelector('.status-dot');
const captionContainer = document.getElementById('caption-container');
const userText = document.getElementById('user-text');
const aiText = document.getElementById('ai-text');
const fileZone = document.getElementById('file-zone');
const previewGrid = document.getElementById('preview-grid');
const quickActions = document.getElementById('quick-actions');
const filePreview = document.getElementById('file-preview');

// State Enums
const State = {
    IDLE: 'idle',
    LISTENING: 'listening',
    THINKING: 'thinking',
    SPEAKING: 'speaking',
    ERROR: 'error'
};

let currentState = State.IDLE;
let isInteractive = false;
let uploadedFiles = [];

// ============================================================
// STATE MANAGEMENT
// ============================================================

/**
 * Set the visual state of the UI
 */
function setState(state) {
    // Remove all state classes
    orb.classList.remove('idle', 'listening', 'thinking', 'speaking', 'error');

    // Add new state class
    orb.classList.add(state);
    currentState = state;

    // Update labels
    const labels = {
        idle: 'IDLE',
        listening: 'LISTENING',
        thinking: 'PROCESSING',
        speaking: 'SPEAKING',
        error: 'SYSTEM ERROR'
    };

    statusLabel.textContent = labels[state] || 'UNKNOWN';

    // Toggle status dot
    if (state === State.ERROR) {
        statusDot.classList.add('offline');
        statusDot.classList.remove('online');
    } else {
        statusDot.classList.add('online');
        statusDot.classList.remove('offline');
    }

    console.log(`[A1] State: ${state}`);
}

// ============================================================
// CAPTION HANDLING
// ============================================================

/**
 * Update caption text
 */
function setCaption(type, text) {
    if (!text) return;

    captionContainer.style.opacity = '1';

    if (type === 'user') {
        userText.textContent = text;
        // Clear AI text when user speaks
        aiText.textContent = '';
    } else if (type === 'ai') {
        userText.textContent = ''; // Optional: clear user text
        typewriterEffect(aiText, text);
    }
}

/**
 * Typewriter effect for AI response
 */
function typewriterEffect(element, text, speed = 30) {
    element.textContent = '';
    let i = 0;

    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    type();
}

// ============================================================
// FILE DROP HANDLING
// ============================================================

fileZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileZone.classList.add('dragover');
});

fileZone.addEventListener('dragleave', () => {
    fileZone.classList.remove('dragover');
});

fileZone.addEventListener('drop', (e) => {
    e.preventDefault();
    fileZone.classList.remove('dragover');

    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
});

function handleFiles(files) {
    if (files.length > 0) {
        filePreview.style.display = 'block';
        files.forEach(file => {
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    const img = document.createElement('div');
                    img.className = 'preview-item';
                    img.innerHTML = `<img src="${e.target.result}">`;
                    previewGrid.appendChild(img);
                    uploadedFiles.push(file);
                };
                reader.readAsDataURL(file);
            }
        });

        // Notify backend (mock)
        console.log(`[A1] ${files.length} files attached`);
    }
}

// ============================================================
// QUICK ACTIONS
// ============================================================

document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        console.log(`[A1] Action triggered: ${action}`);

        // Flash feedback
        btn.style.borderColor = 'var(--primary)';
        setTimeout(() => btn.style.borderColor = '', 200);

        // Send to backend via fetch for now (until Tauri IPC is fully linked)
        // In real app, use invoke(action)
    });
});

// ============================================================
// STATE POLLING (BACKEND SYNC)
// ============================================================
const STATE_SERVER_URL = 'http://127.0.0.1:9877';
let lastState = 'idle';

async function pollState() {
    try {
        const response = await fetch(STATE_SERVER_URL);
        if (response.ok) {
            const newState = (await response.text()).trim();
            if (newState && newState !== lastState) {
                lastState = newState;
                setState(newState);

                // Mock captions for demo based on state
                if (newState === State.LISTENING) {
                    setCaption('user', 'Listening...');
                } else if (newState === State.THINKING) {
                    setCaption('ai', 'Processing request...');
                }
            }
        }
    } catch (e) {
        // Ignored
    }
}

setInterval(pollState, 100);

// Initialize
setState(State.IDLE);
console.log('[A1] UI Initialized');

// ============================================================
// INPUT HANDLING
// ============================================================
const inputContainer = document.getElementById('input-container');
const commandInput = document.getElementById('command-input');

document.addEventListener('keydown', (e) => {
    // Toggle input on Space (if idle and not focused)
    if (e.code === 'Space' && document.activeElement !== commandInput) {
        if (currentState === State.IDLE) {
            // Prevent scrolling if needed, but risky.
            inputContainer.classList.add('active');
            commandInput.focus();
            e.preventDefault();
        }
    }
    // Escape to closes
    if (e.code === 'Escape') {
        inputContainer.classList.remove('active');
        commandInput.blur();
    }
});

commandInput.addEventListener('keydown', async (e) => {
    if (e.key === 'Enter') {
        const text = commandInput.value.trim();
        if (text) {
            console.log(`[Input] Sending: ${text}`);
            try {
                await fetch(STATE_SERVER_URL, {
                    method: 'POST',
                    body: text
                });
                // Immediate feedback
                setCaption('user', text);
                setState(State.THINKING);

            } catch (err) {
                console.error("Failed to send input", err);
            }
            commandInput.value = '';
            inputContainer.classList.remove('active');
            commandInput.blur();
        }
    }
});
