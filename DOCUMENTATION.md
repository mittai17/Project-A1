# A1 Technical Documentation

This document provides a deep dive into the code architecture, module interactions, and customization guides for the A1 Voice Assistant.

## 1. Directory Structure & Modules

### `/core` Directory
The core logic is split into single-responsibility modules:

- **`wake.py`**
  - **Purpose**: Low-latency keyword detection.
  - **Key Function**: `listen_for_wake_word(model)`
  - **Logic**: Uses Vosk `KaldiRecognizer` on raw audio chunks. Lightweight and runs locally on CPU.
  - **Customization**: Edit `WAKE_PHRASES` list to add new trigger words.

- **`adaptive_asr.py`**
  - **Purpose**: Main hearing module with speaker identification.
  - **Key Classes**: `AdaptiveEar`
  - **Logic**: 
    - **Transcription**: Uses **OpenAI Whisper** (small) with specific prompting to support **English/Tamil/Tanglish**.
    - **Identification**: Uses **SpeechBrain** (ECAPA-TDNN) to generate embeddings from audio and compare them against `user_profile.npy`.
    - **Result**: Returns text annotated with `[VERIFIED USER]` if the voice matches.

- **`router.py`**
  - **Purpose**: Intent classification and query routing.
  - **Logic**: **Rule-based**.
    - **Regex Fast-Path**: Instantly catches commands like "Open Firefox", "Look at screen", "Search", "Install".
    - **Tanglish Support**: Handles suffix-based commands (e.g., "Firefox open pannu", "Terminal close seiyu").
    - **Fallback**: Defaults to conversation mode if no rule matches.

- **`brain.py`**
  - **Purpose**: The intelligent core (Agentic).
  - **Architecture**: **ReAct Loop** (Reason + Act).
  - **Logic**: 
    - **Model**: **LLaMA 3.1 8B** (via Ollama).
    - **Context**: Maintains conversation history and retrieves relevant memories from Qdrant.
    - **Tool Use**: Can dynamically call tools via the **Model Context Protocol (MCP)**.

- **`vision.py`**
  - **Purpose**: Visual understanding.
  - **Logic**: 
    - Captures a screenshot using `pyautogui` or `scrot`.
    - Encodes image to Base64.
    - Sends to **Gemini 2.0 Flash** (via OpenRouter) with a specialized system prompt.
  - **Capabilities**: OCR, UI analysis, error debugging.

- **`mcp_manager.py`**
  - **Purpose**: Manages connections to external MCP servers.
  - **Logic**: reads `mcp_config.json`, starts subprocesses (e.g., GitHub MCP server), and proxies tool calls from `brain.py` to these servers.

- **`memory.py`**
  - **Purpose**: Long-term memory.
  - **Logic**: Embeds text using **MiniLM** (via Ollama) and stores vectors in a local **Qdrant** instance. Allows semantic retrieval of facts.

- **`speak.py`**
  - **Purpose**: Audio output (TTS).
  - **Logic**: Uses **Piper Neural TTS** (Local Binary).
  - **Configuration**: Defaults to **Indian Accent** (Telugu `te_IN` model) as a proxy for Tamil/Indian English.


### Root Files
- **`main.py`**: State machine orchestrator (Sleeping -> Listening -> Routing -> Thinking/Acting -> Speaking).
- **`mcp_config.json`**: Configuration for external tools (MCP servers).

---

## 2. Data Flows

### A. Standard Voice Conversation
1. **Wake**: `wake.py` detects "Hey A1".
2. **Listen**: `adaptive_asr.py` records audio, transcribes it to text ("Who is Linus Torvalds?"), and verifies speaker identity.
3. **Route**: `router.py` sees no special command -> routes to **Chat**.
4. **Think**: `brain.py` (Local Llama) receives text + context -> Generates answer.
5. **Speak**: `speak.py` reads the text aloud.

### B. Visual Query ("Look at this")
1. **User**: "Look at this error."
2. **Route**: `router.py` regex matches "look at" -> Intent: **Vision**.
3. **Action**: `vision.py` captures screenshot -> Sends to **Gemini 2.0**.
4. **Result**: Gemini describes the error.
5. **Speak**: A1 reads the explanation.

### C. Agentic Tool Use (MCP)
1. **User**: "Find a python library for PDF parsing on GitHub."
2. **Brain**: Llama/Qwen decides to call tool: `[[CALL:search_repositories({"query": "python pdf parser"})]]`.
3. **MCP Manager**: Intercepts call -> Forwards to **GitHub MCP Server**.
4. **Result**: GitHub Server returns JSON list of repos.
5. **Brain**: Receives JSON -> Summarizes top 3 results for the user.
6. **Speak**: "I found PyPDF2, PDFMiner, and..."

---

## 3. Customization Guide

### Adding New Tools (MCP)
To give A1 new capabilities, add MCP servers to `mcp_config.json`.
Example: Adding a Filesystem server.
```json
"filesystem": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem", "/home/user"]
}
```

### Changing the Personality
Edit `SYSTEM_PROMPT.md` to change how A1 behaves (e.g., make it polite, sarcastic, or concise).

### Using Cloud Models
Edit `.env` to enable cloud tiers:
```bash
OPENROUTER_API_KEY=sk-or-v1-...  # For Vision & Smarter Chat
BYTEZ_API_KEY=bz-...             # For Specialized Coding
```

## 4. Troubleshooting Models

- **Ollama**: Ensure it's running (`ollama serve`). Check `localhost:11434`.
- **Vision**: Requires Internet. Check `Vision API refused` errors in logs if it fails.
- **Audio**: If `adaptive_asr.py` fails to initialize, check `portaudio` installation.

## 5. Deployment

- **Systemd**: Create a user service to run `main.py` in the background.
- **Headless**: A1 works without a monitor, but Vision features will capture a black screen (or fail) depending on the display server (X11 vs Wayland).
