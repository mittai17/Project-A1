# A1 Technical Documentation

> **Version**: 1.2.0 (Multilingual Beta)  
> **Date**: January 2026

This documentation provides a comprehensive technical overview of the A1 Voice Assistant, detailing its modules, data flow, and configuration options.

---

## 1. System Overview

A1 is designed as a **Local-First, Hybrid-Cloud** assistant. 
- **Local**: Speech-to-Text, Wake Word, Text-to-Speech, Reasoning (Llama), Memory, and System Control.
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
│   ├── speak.py           # Piper TTS Wrapper
│   ├── vision.py          # Screen Capture & Gemini API
│   ├── memory.py          # Qdrant Vector DB Manager
│   └── mcp_manager.py     # Model Context Protocol Handler
│
├── skills/                # Action Modules
│   ├── app_control.py     # Window Management (Hyprland/X11)
│   ├── arch.py            # Arch Linux System Management
│   └── web.py             # DuckDuckGo Search
│
├── piper/                 # TTS Engine (Binaries & Models)
├── models/                # Local ML Models (Vosk, SpeakerID)
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

### 🗣️ Speech (Piper TTS)
**File**: `core/speak.py`

A1 uses **Piper Neural TTS** for output.
-   **Why Piper?**: Coqui XTTS was too heavy/slow for this specific CPU setup. Piper is instant.
-   **Voice**: Configured to use an **Indian Accent** model (`te_IN` - Telugu) which serves as a neutral Indian English proxy, pronouncing Indian names/terms much better than US/UK voices.
-   **Audio Output**: Streams raw PCM audio to `aplay` for minimum latency.

### 🔀 The Router
**File**: `core/router.py`

Before asking the heavy LLM, A1 checks for "Reflex" commands using Regex.
-   **English**: `^open firefox$`
-   **Tanglish**: `^firefox open pannu$` (Suffix matching)
-   **Vision**: `^look at.*`

If a regex matches, the action is executed instantly (<10ms). If not, the query goes to Llama 3.1.

---

## 4. Configuration Guide

### Adding Support for Another Language
To add Hindi or Malayalam support:
1.  **Update `adaptive_asr.py`**: Add language-specific examples to the `system_context` string.
2.  **Update `router.py`**: Add regex patterns for the new language's grammar (e.g., `(.*) kholo` for Hindi).
3.  **Update `speak.py`**: Download a compatible Piper voice model (`hi_IN`, etc.) and update `MODEL_PATH`.

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

**Issue: "Piper/Model not found"**
-   Ensure you have the Piper binary in `A1/piper/piper`.
-   Ensure `voice_te.onnx` and `voice_te.onnx.json` exist in `A1/piper/`.

**Issue: "Ollama Connection Refused"**
-   Make sure Ollama is running: `ollama serve`.
-   Verify you pulled the model: `ollama list` should show `llama3.1:8b`.

**Issue: "Microphone Input Empty"**
-   Arch Linux Audio (PipeWire/PulseAudio) can be tricky.
-   Install `pavucontrol` and check if the recording tab shows the "python" process moving the VU meter.
