# A1 - Advanced Offline Voice Assistant

A1 is a production-grade, privacy-first voice assistant built for Linux systems. It runs entirely offline, leveraging local LLMs (Llama 3.2) and high-accuracy speech recognition models.

**Version:** 1.2 (Indian Accent Edition)
**Engine:** Python 3.14 + Ollama + Vosk Pro

---

## 🚀 Features

### 1. **Offline Intelligence**
   - **Brain**: Powered by `llama3.2:3b` running locally via Ollama.
   - **Memory**: Remembers conversation context (last 10 turns).
   - **Error Correction**: Automatically infers meaning from accent mistranscriptions (e.g., "The clinics" -> "Linux").

### 2. **High-Fidelity Hearing**
   - **Wake Word**: Always-on listening for **"Hey A1"**, **"Computer"**, **"System"**, or **"Wake Up"**.
   - **Speech Recognition**: Uses the **Vosk En-US 0.22 (1.8GB)** professional model for high accuracy.
   - **Feedback**: Visual VU meter and real-time "What I'm hearing" text for debugging.

### 3. **Voice Response**
   - **Engine**: `espeak-ng` via `pyttsx3`.
   - **Accent**: Configured for **Indian English** (`inc/hi`).
   - **Optimization**: Tuned speech rate (125wpm) for maximum clarity.

### 4. **System Integration**
   - **Hardware Acceleration**: Automatically uses NVIDIA RTX 3050 for LLM inference.
   - **Latency**: Sub-second wake response; ~3s full LLM thought generation.

---

## 🛠️ Architecture

```mermaid
graph LR
    Mic[Microphone] --> Wake[Wake Word Engine (Vosk Small)]
    Wake --> |Trigger| Listen[Command Listener (Vosk Large)]
    Listen --> |Text| Brain[Contextual Brain (Llama 3.2)]
    Brain --> |Response| TTS[Text-to-Speech (Indian Accent)]
    TTS --> Speaker[Speaker]
```

- **`core/wake.py`**: Lightweight listener. Scans for triggers while ignoring background noise.
- **`core/listen.py`**: Heavyweight transcriber. Activates only after wake word to save resources.
- **`core/brain.py`**: Manages chat history and sanitizes input before sending to Ollama.
- **`core/speak.py`**: Handles audio output, forcing specific voice IDs and speech rates.

---

## 📦 Installation guide

### 1. Prerequisites (Arch Linux)
```bash
sudo pacman -S python python-pip portaudio espeak-ng ollama
```

### 2. Automated Setup
We have provided scripts to handle the heavy lifting.

```bash
# 1. Base Setup (Deps, Venv, Small Models)
chmod +x setup.sh
./setup.sh

# 2. Upgrade to Pro Models (Reliable Hearing)
chmod +x upgrade.sh
./upgrade.sh
```

### 3. Manual Model Check
Ensure your `models/` directory looks like this:
```
A1/models/
├── vosk-model-en-us-0.22/  (Large 1.8GB model)
└── vosk-model-small-en-us-0.15/ (Small wake model - optional)
```

---

## 🎮 Usage

1. **Start the Brain**:
   Ensure Ollama is running in the background.
   ```bash
   ollama serve
   ```

2. **Run A1**:
   ```bash
   source venv/bin/activate
   python main.py
   ```

3. **Interact**:
   - **Say**: "Computer" or "Hey A1"
   - **Wait for**: "I'm listening"
   - **Ask**: "What is the capital of India?"
   - **Reply**: It will answer in an Indian English voice.

4. **Continuous Mode**:
   A1 stays awake after the first question. You can ask follow-ups immediately. It goes back to sleep after 8 seconds of silence.

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **"NameError: np not defined"** | Occurs in older code. Fixed in v1.1. Run `git pull` or check `core/wake.py`. |
| **Microphone not hearing me** | Check the VU meter in the terminal. If it stays empty `[MIC]`, check system PulseAudio settings. |
| **Too Fast/Robotic Voice** | Edit `core/speak.py` and lower `engine.setProperty('rate', 125)`. |
| **"Connection Refused"** | Run `ollama serve` in a separate terminal. |

---

## 📜 Update Log

- **v1.0**: Initial Release (Vosk Small, Standard TTS).
- **v1.1**: Added continuous conversation & simplified wake words ("Computer").
- **v1.2**: Switched to "Large" Vosk model for accent handling. Added Contextual Memory to Brain. Changed Voice to Indian English. Reverted Whisper due to Python 3.14 conflict.
