---
tags: [core, tts, audio]
---

# 🔊 Core: Text-To-Speech

A1 uses **Piper Neural TTS** for low-latency, high-quality audio output.

## ⚙️ Configuration

| Parameter | Value | Reason |
| :--- | :--- | :--- |
| **Engine** | `piper` (Binary) | Runs on CPU, instant startup time compared to Coqui. |
| **Model** | `te_IN-maya-medium` | A Telugu model that speaks English with a natural **Indian Accent**. |
| **Output** | `aplay` | Pipes raw PCM audio directly to ALSA. |

## 🗣️ Language Support Limitation

> [!WARNING] English Only Output
> While A1 **understands** Tamil/Tanglish, it **speaks** back in English (or Romanized Tanglish).
>
> *   **Bad**: "வணக்கம்" (Result: Static noise)
> *   **Good**: "Vanakkam" (Result: Speaks correctly)

## flow

```mermaid
graph LR
    Brain[🧠 Llama 3.1] -->|Text| Cleaner[🧹 Text Cleaner]
    Cleaner -->|echo "Text"| Piper[🗣️ Piper Process]
    Piper -->|PCM Stream| Aplay[🔈 Speaker]
```

---
## 🕸️ Connections
- Receives text from [[Core/Core_Brain_LLM|Brain]].
- Receives commands from [[Core/Core_Router|Router]].
- See [[Design/Design_Decisions#2. Why Piper TTS?|Design Rationale]].

[[00_Index|🔙 Return to Index]]
