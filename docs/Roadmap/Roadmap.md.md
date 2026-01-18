---
tags: [roadmap, future, planning]
---

# 🛣️ Project Roadmap

> [!ABSTRACT]
> A1 is currently in **v1.4.0 (Beta)**. This document outlines the trajectory towards v2.0 and beyond, focusing on eliminating cloud dependencies and enhancing agentic capabilities.

## 📅 Version History

| Version | Status | Key Features |
| :--- | :--- | :--- |
| **v0.1** | ✅ | Basic Vosk Wake Word + Llama 3.2 Chat |
| **v1.0** | ✅ | ReAct Loop, System Control, App Control |
| **v1.1** | ✅ | Vision (Cloud), Adaptive Hearing (Speaker ID) |
| **v1.2** | ✅ | Multilingual (Tanglish), Piper TTS, Llama 3.1 |
| **v1.3** | ✅ | XTTS v2 Voice Cloning, Python 3.11 |
| **v1.4** | 🚧 | **Current**: Siri-Style GUI Overlay (Tauri v2) |

---

## 🔮 Phase 2: The "Offline Vision" Update (Q1 2026)

**Goal**: Remove the dependency on `OpenRouter/Gemini`.

- [ ] **Local Vision Model**: Integrate `LLaVA-v1.6-7b` or `BakLLaVA` running via Ollama.
- [ ] **Screen Context**: Enable "Continuous Watch" mode where A1 passively monitors the screen for context (like finding buttons without being asked).
- [ ] **UI Navigation**: Use `ShowUI` or `Ferret` models to generate precise X/Y coordinates for clicking elements.

## 🔮 Phase 3: The "Full Agent" Update (Q2 2026)

**Goal**: A1 should be able to perform long-running, multi-step tasks autonomously.

- [ ] **Project Management**: "Create a React App" -> A1 creates folder, runs `npx`, installs deps, and opens VS Code.
- [ ] **Research Agent**: "Research AGI" -> A1 searches web, reads 5 papers, and writes a markdown summary to disk.
- [ ] **Self-Correction**: If a shell command fails (e.g., `pacman error`), A1 reads the error and tries to fix it (e.g., `rm /var/lib/pacman/db.lck`).

## 🔮 Phase 4: Voice & Personality (Long Term)

**Goal**: Indistinguishable from human interaction.

- [x] **Voice Cloning**: XTTS v2 for personalized voice synthesis ✅
- [ ] **Emotional TTS**: Integrate `StyleTTS2` for expressive speech (Happy, Sad, Urgent).
- [ ] **Full Duplex Audio**: Real-time interruption without explicit "Stop" commands (Echo cancellation).
- [ ] **Indian Language Finetuning**: Train a LoRA adapter for Llama 3 to speak/write native Tamil script.

---

## 🧪 Experimental Notes
- **Testing**: We are currently testing `Phi-3-Mini` as a potential faster replacement for the Router logic.
- **Hardware**: Targeting optimization for 6GB VRAM GPUs (RTX 3050/4050 mobile).

---

## 🏗️ Global Task Tracker
> [!NOTE] Auto-Generated
> Scans the entire vault for `#todo` or uncompleted checkboxes.

```dataview
TASK
FROM ""
WHERE !completed AND file.name != "Roadmap"
GROUP BY file.name
```
