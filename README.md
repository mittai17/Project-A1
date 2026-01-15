# A1 - Local AI Assistant

<div align="center">

![Status](https://img.shields.io/badge/Status-Beta-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge)

**A production-grade, privacy-first voice assistant inspired by Jarvis.**  
*Runs entirely offline on consumer hardware.*

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture)

</div>

---

## ⚡ What is A1?

A1 is an intelligent agent designed for **Linux Power Users**. Unlike Alexa or Siri, A1 is deeply integrated into your OS. It can control applications, manage system updates (Arch Linux), search GitHub for open-source tools, and remember your preferences using a local vector database.

### Core Capabilities

| Feature | Description | Tech Stack |
| :--- | :--- | :--- |
| **🧠 Offline Brain** | Powered by **Llama 3.2** running locally. Fast, private, smart. | `Ollama` |
| **🗣️ Hearing** | Professional-grade speech recognition. | `Vosk Pro (1.8GB)` |
| **🔊 Voice** | Fast, clear, low-latency text-to-speech. | `pyttsx3` / `espeak-ng` |
| **💾 Memory** | Remembers facts, preferences, and context long-term. | `Qdrant` |
| **🛠️ Skills** | Controls Apps, Updates Arch Linux, Searches Web/GitHub. | `Python` |

---

## 🚀 Installation

### Prerequisites
- **OS**: Linux (Arch Linux recommended, tested on Ubuntu).
- **GPU**: NVIDIA GPU recommended for LLM speed (optional).

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/mittai17/Project-A1.git
cd Project-A1

# 2. Run the Setup Wizard
chmod +x setup.sh
./setup.sh
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

A1 follows a modular **Router-Skill** architecture.

```mermaid
graph TD
    User((User)) -->|Voice| Mic[Microphone]
    Mic -->|Audio| Wake[Wake Word (Vosk Small)]
    Wake -->|Trigger| Listen[Command Listener (Vosk Large)]
    Listen -->|Text| Router{Intent Router}
    
    Router -->|'Update System'| SkillArch[Arch Linux Skill]
    Router -->|'Open App'| SkillApp[App Control]
    Router -->|'Search GitHub'| SkillFOSS[GitHub Skill]
    Router -->|'General Chat'| Brain[LLM Brain]
    
    Brain -->|Query| Memory[(Qdrant DB)]
    SkillArch -->|Output| TTS[Text-to-Speech]
    SkillApp -->|Output| TTS
    Brain -->|Output| TTS
    TTS --> Speaker
```

---

## 🤝 Contributing

We welcome contributions!
1.  Fork the repo.
2.  Create a new feature branch (`git checkout -b feature/amazing-skill`).
3.  Add your skill in `skills/`.
4.  Register it in `core/router.py` and `main.py`.
5.  Submit a Pull Request.

## 📄 License

MIT License. Free and Open Source.

---
<div align="center">
Built with ❤️ by <a href="https://github.com/mittai17">Mittai</a>
</div>
