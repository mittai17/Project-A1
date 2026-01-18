# A1 Technical Documentation

> **Version**: 1.4.0 (Siri-Style Overlay)  
> **Date**: January 2026

This documentation provides a comprehensive technical overview of the A1 Voice Assistant, detailing its modules, data flow, and configuration options.

---

## 1. System Overview

A1 is designed as a **Local-First, Hybrid-Cloud** assistant. 
- **Local**: Speech-to-Text, Wake Word, Text-to-Speech (XTTS v2 + Piper), Reasoning (Llama), Memory, and System Control.
- **Cloud**: Vision Analysis (Gemini 2.0) via OpenRouter (optional).

The system operates on a **ReAct (Reason + Act)** loop, allowing it to dynamically decide when to use tools (like searching the web or checking system stats) versus when to rely on its internal knowledge.

---

## 2. Directory Structure

The project is organized into modular components within the `A1/` directory:

```text
A1/
├── core/                  # The Central Nervous System
│   ├── main.py            # Entry point & State Machine
│   ├── wake.py            # Vosk Wake Word Detection
│   ├── adaptive_asr.py    # Whisper STT + Speaker ID
│   ├── brain.py           # Llama 3.1 Logic & Tool Use
│   ├── router.py          # Regex/Logic Intent Router
│   ├── speak.py           # XTTS v2 + Piper TTS Dual Engine
│   ├── vision.py          # Screen Capture & Gemini API
│   ├── memory.py          # Qdrant Vector DB Manager
│   └── mcp_manager.py     # Model Context Protocol Handler
│
├── gui-overlay/           # Siri-Style Visual Overlay (Tauri v2)
│   ├── src-tauri/         # Rust backend
│   │   ├── src/main.rs    # Click-through + state control
│   │   └── tauri.conf.json# Window configuration
│   └── dist/              # Frontend (HTML/CSS/JS)
│       ├── index.html     # Orb structure
│       ├── styles.css     # Animations & states
│       └── app.js         # State polling
│
├── skills/                # Action Modules
│   ├── app_control.py     # Window Management (Hyprland/X11)
│   ├── arch.py            # Arch Linux System Management
│   └── web.py             # DuckDuckGo Search
│
├── piper/                 # TTS Engine (Binaries & Models)
├── models/                # Local ML Models (Vosk, SpeakerID, speaker.wav)
└── memory_db/             # Qdrant Persistence Storage
```

---

## 3. Module Deep Dive

### 👂 Hearing (Adaptive ASR)
**File**: `core/adaptive_asr.py`

This module is the "Ear" of A1. It uses a **Hybrid Pipeline**:
1.  **Vosk (`wake.py`)**: Listens continuously for "Hey A1" using a lightweight model. Low CPU usage.
2.  **Whisper Small**: Once triggered, it records audio and transcribes it.
    -   *Code-Switching*: The model is primed with a custom system prompt containing Tamil/Tanglish examples (e.g., "Firefox open pannu") to ensure it transcribes mixed languages correctly.
3.  **Speaker Verification**: Uses `SpeechBrain` (ECAPA-TDNN) to verify if the speaker is the owner. If verified, it tags the text with `[VERIFIED]`.

### 🧠 The Brain (Llama 3.1)
**File**: `core/brain.py`

The "Brain" is an agent powered by **Llama 3.1 8B**.
-   **Inference**: Relies on `ollama serve` running on `localhost:11434`.
-   **Context**: It retrieves the last 10 conversation turns + relevant semantic memories from Qdrant.
-   **Tool Use**: It can emit special tokens `[[CALL:tool_name(args)]]` which are intercepted by the system to execute Python functions or MCP tools.

### 🗣️ Speech (Dual-Engine TTS)
**File**: `core/speak.py`

A1 now uses a **dual-engine TTS system**:

| Engine | Use Case | Quality |
| :--- | :--- | :--- |
| **XTTS v2** | English (Voice Cloning) | ⭐⭐⭐⭐⭐ |
| **Piper** | Tamil/Fallback | ⭐⭐⭐⭐ |

#### XTTS v2 (Voice Cloning)
-   **Model**: `tts_models/multilingual/multi-dataset/xtts_v2`
-   **Reference Audio**: `models/speaker.wav` (5-15 seconds of your voice)
-   **Device**: CUDA (GPU) preferred, CPU fallback
-   **First Run**: Auto-downloads ~1.5GB model

#### Piper (Fallback)
-   **Why Piper?**: Fast, CPU-friendly, instant startup
-   **Voice**: Indian Accent model (`te_IN` - Telugu) for English
-   **Audio Output**: Streams raw PCM audio to `aplay`

### 🔀 The Router
**File**: `core/router.py`

Before asking the heavy LLM, A1 checks for "Reflex" commands using Regex.
-   **English**: `^open firefox$`
-   **Tanglish**: `^firefox open pannu$` (Suffix matching)
-   **Vision**: `^look at.*`

If a regex matches, the action is executed instantly (<10ms). If not, the query goes to Llama 3.1.

### 🎨 GUI Overlay (Siri-Style)
**Files**: `gui-overlay/` + `core/overlay.py`

A1 features a **Siri-style visual overlay** built with **Tauri v2** (Rust + WebView). This overlay provides visual feedback without interrupting your work.

#### Why It Doesn't Interrupt Your Work

| Setting | Effect |
| :--- | :--- |
| `alwaysOnTop: true` | Stays visible above all windows |
| `decorations: false` | No title bar or borders |
| `transparent: true` | See-through background |
| `focus: false` | Never steals keyboard focus |
| `set_ignore_cursor_events(true)` | **All mouse clicks pass through** |

#### Visual States

| State | Color | Animation | Trigger |
| :--- | :--- | :--- | :--- |
| **Idle** | 🟣 Purple | Gentle pulse | Waiting for wake word |
| **Listening** | 🟢 Green | Waveform bars | Wake word detected |
| **Thinking** | 🟠 Orange | Spinning glow | Processing command |
| **Speaking** | 🔵 Blue | Wave animation | TTS active |
| **Error** | 🔴 Red | Shake | System error |

#### Architecture

```
Python (main.py)                    Tauri (gui-overlay/)
     │                                    │
     │  overlay.listening()              │
     ├──────────────────────►  HTTP :9877 ──► app.js polls
     │                                    │
     │                                    ▼
     │                           setState("listening")
     │                                    │
     │                                    ▼
     │                           CSS Animation Change
```

#### Building the Overlay

```bash
cd gui-overlay
cargo build --release
```

The overlay binary is at `gui-overlay/target/release/a1-overlay`.

---

## 4. Configuration Guide

### Requirements
| Requirement | Value |
| :--- | :--- |
| **Python** | 3.11.x (via pyenv) |
| **RAM** | 8GB+ (16GB recommended) |
| **GPU** | RTX 30+ (optional, speeds up TTS) |
| **Storage** | 15GB+ |

### Setting Up Python 3.11
```bash
# Install pyenv
yay -S pyenv

# Install Python 3.11
pyenv install 3.11.11

# Create venv
~/.pyenv/versions/3.11.11/bin/python -m venv venv
./venv/bin/pip install -r requirements.txt
```

### Voice Cloning Setup
1. Record a **5-15 second WAV file** of your voice
2. Save it to `A1/models/speaker.wav`
3. A1 will automatically use XTTS v2 for English speech

### Adding Support for Another Language
To add Hindi or Malayalam support:
1.  **Update `adaptive_asr.py`**: Add language-specific examples to the `system_context` string.
2.  **Update `router.py`**: Add regex patterns for the new language's grammar (e.g., `(.*) kholo` for Hindi).
3.  **Update `speak.py`**: Download a compatible Piper voice model (`hi_IN`, etc.) and update `VOICES` dict.

### Enrolling Your Voice
To make A1 recognize YOU specifically:
1.  Run the enrollment script:
    ```bash
    ./venv/bin/python core/voice_enroll.py
    ```
2.  Speak the 3 prompt phrases clearly.
3.  A1 will generate `user_profile.npy`. Future commands will be marked as `[VERIFIED USER]`.

### Extending Memories
The memory system is automatic. However, you can manually inspect memories by opening the `memory_db` folder using a Qdrant viewer or via the Python API in `core/memory.py`.

---

## 5. Troubleshooting

**Issue: "XTTS/TTS not loading"**
-   Ensure Python 3.11 is being used: `./venv/bin/python --version`
-   Verify TTS is installed: `./venv/bin/python -c "from TTS.api import TTS; print('OK')"`

**Issue: "Piper/Model not found"**
-   Ensure you have the Piper binary in `A1/piper/piper`.
-   Ensure `voice.onnx` and `voice_te.onnx` exist in `A1/piper/`.

**Issue: "Ollama Connection Refused"**
-   Make sure Ollama is running: `ollama serve`.
-   Verify you pulled the model: `ollama list` should show `llama3.1:8b`.

**Issue: "Microphone Input Empty"**
-   Arch Linux Audio (PipeWire/PulseAudio) can be tricky.
-   Install `pavucontrol` and check if the recording tab shows the "python" process moving the VU meter.

---

## 6. Version History

| Version | Date | Features |
| :--- | :--- | :--- |
| **v1.4.0** | Jan 2026 | Siri-Style Overlay (Tauri v2), Click-through |
| **v1.3.0** | Jan 2026 | XTTS v2 Voice Cloning, Python 3.11 |
| **v1.2.0** | Jan 2026 | Multilingual (Tanglish), Piper TTS |
| **v1.1.0** | Jan 2026 | Vision, Adaptive Hearing, Speaker ID |
| **v1.0.0** | Jan 2026 | ReAct Loop, System Control |
