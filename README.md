# A1 - Local AI Assistant

<div align="center">

![Status](https://img.shields.io/badge/Status-Beta-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge)

**A production-grade, privacy-first voice assistant inspired by Jarvis.**  
*Runs entirely offline on consumer hardware with optional cloud vision capabilities.*

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture) • [History](#-project-history)

</div>

---

## ⚡ What is A1?

A1 is an intelligent agent designed for **Linux Power Users**. Unlike Alexa or Siri, A1 is deeply integrated into your OS. It can control applications, see your screen, manage system updates, and remember your preferences using a local vector database.

### Core Capabilities

| Feature | Description | Tech Stack |
| :--- | :--- | :--- |
| **🧠 Offline Brain** | Powered by **Llama 3.2** running locally. Fast, private, smart. | `Ollama` |
| **�️ Vision** | Screen analysis & visual Q&A. | `Gemini 2.0 Flash` (via OpenRouter) |
| **🗣️ Hearing** | Adaptive speech recognition that learns your voice. | `Whisper` + `Vosk` |
| **🎙️ Voice ID** | Biometric speaker verification. | `SpeechBrain` / `ECAPA-TDNN` |
| **🔊 Voice** | Fast, clear, low-latency text-to-speech. | `pyttsx3` / `espeak-ng` |
| **💾 Memory** | Remembers facts, preferences, and context long-term. | `Qdrant` |
| **🛠️ Skills** | Controls Apps, Updates Arch Linux, Searches Web/GitHub. | `Python` |

---

## 🚀 Installation

### Prerequisites
- **OS**: Linux (Arch Linux recommended, tested on Ubuntu).
- **GPU**: NVIDIA GPU recommended for LLM speed.
- **Dependencies**: `scrot` (for screen capture on some Linux distros).

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mittai17/Project-A1.git
cd Project-A1

# 2. Run the Setup Wizard
chmod +x setup.sh
./setup.sh

# 3. Add API Keys (Optional)
# Edit .env to add OPENROUTER_API_KEY for Vision support.
nano .env

# 4. Pull Needed Models
ollama pull llama3.1:8b
ollama pull all-minilm

# 5. Enroll Your Voice (Recommended)
# Records samples to learn your voice for higher accuracy.
./venv/bin/python core/voice_enroll.py
```

The script will:
1.  Install system dependencies (Python, PortAudio, etc).
2.  Install **Ollama** and pull the `llama3.2:3b` model.
3.  Download the **Vosk** speech model.
4.  Create a virtual environment and install Python packages.

---

## 🎮 Usage

Start the assistant:

```bash
./venv/bin/python main.py
```

### Voice Commands

**Wake Word:** "Hey A1", "Computer", "System"

| Intent | Example Command | Action |
| :--- | :--- | :--- |
| **Vision** | "Look at this error", "What is on my screen?" | Captures screen & analyzes it. |
| **App Control** | "Open Firefox", "Close Terminal" | Launches/Closes apps. |
| **Web Search** | "Search for latest Linux news" | Searches DuckDuckGo & Summarizes. |
| **FOSS Discovery** | "Find open source alternative to Photoshop" | Searches GitHub for tools. |
| **System (Arch)** | "Update system", "System stats" | Runs `yay -Syu` or checks RAM/CPU. |
| **Memory** | "Remember that my API key is 123" | Stores fact in Qdrant. |
| **Chat** | "Explain Quantum Physics" | Multi-turn conversation. |

### Interruption
You can interrupt A1 at any time by saying **"Stop"**, **"Wait"**, or **"Cancel"**.

---

## 🏗️ Architecture

A1 follows a modular **Router-Skill** architecture with a ReAct loop for complex tasks.

```mermaid
graph TD
    User((User)) -->|Voice| Mic[Microphone]
    Mic -->|Audio| Wake["Wake Word (Vosk)"]
    Wake -->|Trigger| Listen["Adaptive Ear (Whisper + SpeakerID)"]
    Listen -->|Text| Router{"Intent Router"}
    
    Router -->|"Vision"| Vision[Vision Skill (Gemini)]
    Router -->|"Update System"| SkillArch[Arch Linux Skill]
    Router -->|"Open App"| SkillApp[App Control]
    Router -->|"Search"| SkillWeb[Web Tools]
    Router -->|"General Chat"| Brain[LLM Brain]
    
    Brain -->|Query| Memory[("Qdrant DB")]
    Vision -->|Analysis| Brain
    
    SkillArch -->|Output| TTS[Text-to-Speech]
    Brain -->|Output| TTS
    TTS --> Speaker
```

---

## 🔧 Technical Details

<details>
<summary><strong>🧠 Brain (Llama 3.1)</strong></summary>

- **Model:** `llama3.1:8b` (Quantized 4-bit) for general chat.
- **Inference:** Ollama API.
- **Agentic Loop:** Implements ReAct pattern for tool usage.
</details>

<details>
<summary><strong>👁️ Vision (Gemini 2.0)</strong></summary>

- **Model:** `google/gemini-2.0-flash-exp:free` via OpenRouter.
- **Input:** Full resolution screenshots.
- **Latency:** ~2-4s depending on network.
</details>

<details>
<summary><strong>🗣️ Ears (Adaptive ASR)</strong></summary>

- **Wake Word:** Vosk Small (Low Power).
- **Transcription:** OpenAI Whisper `small` (Prompted for Multilingual).
- **Identity:** SpeechBrain `ECAPA-TDNN` (Speaker Verification).
- **Adaptation:** Learns user voice profile over time.
</details>

<details>
<summary><strong>🔊 Mouth (TTS)</strong></summary>

- **Engine:** `Piper Neural TTS` (Offline).
- **Voice:** Indian Accent (Telugu `te_IN` model proxy).
- **Latency:** Low-latency stream via `aplay`.
</details>

<details>
<summary><strong>💾 Memory (Qdrant)</strong></summary>

- **Type:** Vector Database.
- **Embedding:** `all-minilm` (via Ollama).
- **Usage:** Semantic search for relevant context.
</details>

---

## 📜 Project History

### v1.1.0 - Visual Intelligence & Adaptive Hearing
*   **Vision Module**: Added ability to "see" the screen using Gemini 2.0 Flash. Triggers include "look at screen", "analyze this".
*   **Adaptive ASR**: Integrated `Whisper` for transcription and `SpeechBrain` for speaker identification. A1 now learns who is speaking.
*   **Voice Enrollment**: New tool `voice_enroll.py` to capture user voice signatures.

### v0.2.x - Feature Enhancement
*   **Agentic Core**: Refactored `brain.py` to use a ReAct loop for better reasoning and tool use.
*   **MCP Integration**: Added Model Context Protocol support.
*   **Documentation**: Migrated to MDX-style README and added `DOCUMENTATION.md`.

### v0.1.x - Foundations
*   **Blocker Bypass**: Implemented logic to bypass restricted application detection.
*   **IPC Interception**: Code injection for renderer security bypasses.
*   **Core Systems**: Established basic Wake/Listen/Speak loop with Llama 3.2.

---

## ❓ Troubleshooting

<details>
<summary><strong>Microphone not hearing me</strong></summary>

- Check the VU meter in the terminal `[MIC]`.
- If it stays empty, check system PulseAudio/PipeWire settings.
- Ensure `portaudio` is installed: `sudo pacman -S portaudio`.
</details>

<details>
<summary><strong>Vision queries fail</strong></summary>

- Ensure `OPENROUTER_API_KEY` is set in `.env`.
- Ensure you have internet access (Vision uses cloud API).
- On Linux, install `scrot`: `sudo pacman -S scrot` or `sudo apt install scrot`.
</details>

<details>
<summary><strong>Voice is too fast / Robotic</strong></summary>

- Edit `core/speak.py`.
- Lower the rate: `engine.setProperty('rate', 125)`.
</details>

---

## 🤝 Contributing

We welcome contributions!
1.  Fork the repo.
2.  Create a new feature branch.
3.  Add your skill in `skills/`.
4.  Register it in `core/router.py`.
5.  Submit a Pull Request.

## 📄 License

MIT License. Free and Open Source.

---
<div align="center">
Built with ❤️ by <a href="https://github.com/mittai17">Mittai</a>
</div>
