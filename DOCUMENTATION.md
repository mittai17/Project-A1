# A1 Technical Documentation

This document provides a deep dive into the code architecture, module interactions, and customization guides for the A1 Voice Assistant.

## 1. Directory Structure & Modules

### `/core` Directory
The core logic is split into single-responsibility modules:

- **`wake.py`**
  - **Purpose**: Low-latency keyword detection.
  - **Key Function**: `listen_for_wake_word(model)`
  - **Logic**: Uses a continuous loop with `sounddevice.RawInputStream`. It processes audio in 8000-byte chunks. It uses the Vosk `KaldiRecognizer` in partial mode for speed.
  - **Customization**: Edit `WAKE_PHRASES` list to add new trigger words.

- **`listen.py`**
  - **Purpose**: High-accuracy command transcription.
  - **Key Function**: `listen_for_command(model, timeout)`
  - **Logic**: Similar to `wake.py` but uses a larger, more accurate model. It implements a silence timeout mechanism: if no speech is detected for `timeout` seconds, it returns `None` to end the session.

- **`brain.py`**
  - **Purpose**: Intelligence & Context management.
  - **Key Function**: `think(prompt)`
  - **Logic**: 
    - Maintains a `history` list (global variable) for conversational context.
    - Constructs a sophisticated prompt containing the System Instruction (persona), History, and current User Input.
    - Sends a POST request to the local Ollama instance (`localhost:11434`).
    - Handles phonetic correction instructions in the system prompt.

- **`speak.py`**
  - **Purpose**: Audio output (TTS).
  - **Key Function**: `speak(text)`
  - **Logic**: 
    - Initializes `pyttsx3` driver (wrapping `espeak-ng` on Linux).
    - Scans system voices for "India" or "en-in" tags.
    - Sets rate to 125 WPM for clarity.
  - **Customization**: Change `engine.setProperty('rate', ...)` to speed up/slow down.

- **`router.py`**
  - **Purpose**: Intent classification (Stub).
  - **Current State**: Returns "local" for all queries.
  - **Future Use**: Will analyze text to decide if it should go to Local Brain (Llama) or Cloud API (Weather, Spotify, etc.).

### Root Files
- **`main.py`**: The orchestrator. It loads models once at startup and manages the state machine (Sleeping -> Listening -> Thinking -> Speaking).

## 2. Data Flow

1. **State: SLEEPING**
   - `main.py` calls `wake.listen_for_wake_word()`.
   - `wake.py` reads mic stream.
   - If "Computer" is heard -> Return `True`.

2. **State: LISTENING (Session Start)**
   - `speak.py` says "I'm listening".
   - `main.py` enters `while True` loop.

3. **State: ACTIVE CONVERSATION**
   - `listen.py` records command ("What is Linux?").
   - **Input**: Audio bytes -> **Output**: Text "What is Linux".
   - `brain.py` takes text.
     - Appends to history.
     - Calls Ollama.
     - **Output**: "Linux is an open source OS..."
   - `speak.py` reads the response.

4. **State: TIMEOUT**
   - If `listen.py` hears silence for 8s, it returns `None`.
   - `main.py` breaks loop and returns to **State: SLEEPING**.

## 3. Customization Guide

### Changing the Wake Word
Open `core/wake.py`:
```python
# Add your phrase to this list
WAKE_PHRASES = ["hey a1", "computer", "my phrase here"]
```

### Changing the AI Personality
Open `core/brain.py` and edit the `system_prompt`:
```python
system_prompt = (
    "You are Jarvis, a sarcastic butler..."
)
```

### Swapping Models
To use a different STT model (e.g., French), download it to `models/` and update `main.py`:
```python
MODEL_PATH = "models/vosk-model-fr-0.22"
```

## 4. API Reference (Ollama)

A1 relies on the Ollama API.
- **Endpoint**: `http://localhost:11434/api/generate`
- **Payload**:
  ```json
  {
    "model": "llama3.2:3b",
    "prompt": "...",
    "stream": false
  }
  ```
- **Troubleshooting**: If A1 says "Thinking... Connection Failed", ensure Ollama is running (`ollama serve`).

## 5. Deployment Notes

- **System Service**: To run A1 on boot, create a systemd service file pointing to the `venv/bin/python` executable and `main.py`.
- **Audio Output**: Uses ALSA/PulseAudio. If running headless (no monitor), ensure the user has permission to access audio groups (`audio`).
