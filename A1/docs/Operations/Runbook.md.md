---
tags: [operations, guide, runbook]
aliases: [User Manual, Operational Guide]
---

# 📖 A1 Operations Runbook

> [!ABSTRACT]
> This runbook covers the daily operation, command usage, and workflow management for the A1 Assistant.

## 🚀 Startup Procedure

### Standard Launch
To start the assistant in standard mode (Background + Voice):

```bash
cd ~/path/to/Project-A1
source venv/bin/activate
python main.py
```

> [!TIP] Headless Mode
> A1 does not require a monitor. It can run on a server or Raspberry Pi, managing systems via SSH commands if configured.

---

## 🗣️ Voice Command Commands

A1 supports **Code-Switching** (English / Tanglish).

### 1. App Control
| Action | English Command | Tanglish Command |
| :--- | :--- | :--- |
| **Start** | "Open VS Code" | "VS Code open pannu" |
| **Stop** | "Close Firefox" | "Firefox close seiyu" |
| **Switch** | "Focus Terminal" | "Terminal focus karo" |

### 2. System Operations
These commands execute `arch.py` skills.

- **Update System**: *"System update pannu"* -> Runs `yay -Syu`
- **Install Package**: *"Install htop"* -> Runs `pacman -S htop`
- **Check Status**: *"Status check pannu"* -> Runs `btop` summary

### 3. Visual Analysis (Gemini)
- **Trigger**: "Look at this", "Screen analyze pannu"
- **Action**: Takes screenshot -> Encodes -> Sends to Cloud -> Speaks Output.

---

## 🛑 Emergency Stop (Barge-In)
If A1 is speaking too much or you need to cancel an action:

> **Say**: "Stop!", "Wait!", "Cancel!"

This triggers the atomic `stop_event` in the Audio Output thread, instantly silencing the TTS.

---

## 💾 Memory Management
A1 remembers interactions in `Qdrant`.

- **Explicit Save**: *"Remember that the server IP is 10.0.0.5"*
- **Explicit Recall**: *"What is the server IP?"*
- **Context Window**: It also remembers the last ~10 turns of conversation automatically.

---

## 🔄 Maintenance

### Updating Models
To update the underlying AI brains:

```bash
ollama pull llama3.1:8b
ollama pull all-minilm
```

### Logs & Debugging
Logs are printed to `stdout` with color coding.
- 🟢 **[ADAPTIVE]**: Hearing/STT events.
- 🔵 **[BRAIN]**: Thinking/LLM events.
- 🟣 **[ROUTER]**: fast-path Regex matches.
- 🔴 **[ERROR]**: System failures.

---
## 🕸️ Connections
- See [[Operations/Installation|Installation Guide]] for setup.
- Commands act on [[Skills/Skill_App_Control|Apps]] and [[Skills/Skill_Arch_Linux|Arch Linux]].
- Check [[Roadmap/Roadmap|Roadmap]] for upcoming features.

[[00_Index|🔙 Return to Index]]
