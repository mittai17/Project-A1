# GUI Overlay (Tauri v2)

> **Module**: `gui-overlay/` + `core/overlay.py`  
> **Technology**: Tauri v2, Rust, HTML/CSS/JS  
> **Added**: v1.4.0 (January 2026)

---

## Overview

A1 features a **Siri-style visual overlay** that provides real-time feedback without interrupting your workflow. Built with **Tauri v2** (Rust backend, WebView frontend), it behaves exactly like Apple's Siri overlay.

## Key Features

- ✅ **Always on top** - Visible at all times
- ✅ **Click-through** - Mouse clicks pass through to apps behind
- ✅ **Non-focusable** - Keyboard input goes to your active app
- ✅ **Transparent** - No window decorations
- ✅ **Responsive** - 100ms state updates via HTTP polling

## Visual States

| State | Color | Animation | Trigger |
| :--- | :--- | :--- | :--- |
| **Idle** | 🟣 Purple | Gentle pulse | Waiting for wake word |
| **Listening** | 🟢 Green | Waveform bars | Wake word detected |
| **Thinking** | 🟠 Orange | Spinning glow | Processing command |
| **Speaking** | 🔵 Blue | Wave animation | TTS active |
| **Error** | 🔴 Red | Shake | System error |

## Why It Doesn't Interrupt Your Work

The overlay uses Tauri v2's window configuration:

```json
{
  "alwaysOnTop": true,      // Stays visible
  "decorations": false,     // No title bar
  "transparent": true,      // See-through
  "focus": false,           // Never steals focus
  "skipTaskbar": true       // Not in taskbar
}
```

And critically, in Rust:

```rust
window.set_ignore_cursor_events(true);
```

This makes **all mouse clicks pass through** to whatever app is behind the overlay.

## Architecture

```
┌─────────────────┐         ┌──────────────────┐
│   Python        │         │   Tauri v2       │
│   main.py       │         │   gui-overlay/   │
├─────────────────┤         ├──────────────────┤
│ overlay.start() │────────►│ Spawn process    │
│                 │         │                  │
│ overlay.        │  HTTP   │ app.js polls     │
│ listening()     │────────►│ :9877/           │
│                 │         │                  │
│                 │         │ setState()       │
│                 │         │ CSS animation    │
└─────────────────┘         └──────────────────┘
```

## File Structure

```
gui-overlay/
├── Cargo.toml              # Workspace config
├── README.md               # Documentation
├── dist/                   # Frontend
│   ├── index.html         # Orb HTML structure
│   ├── styles.css         # Siri-style animations
│   └── app.js             # Tauri IPC + state polling
└── src-tauri/
    ├── Cargo.toml         # Rust dependencies
    ├── tauri.conf.json    # Window configuration
    └── src/
        └── main.rs        # Click-through setup
```

## Python Controller

The `core/overlay.py` module provides:

```python
import overlay

overlay.start()      # Start overlay + HTTP server
overlay.idle()       # Purple, gentle pulse
overlay.listening()  # Green, waveform
overlay.thinking()   # Orange, spinning
overlay.speaking()   # Blue, wave
overlay.error()      # Red, shake
overlay.stop()       # Stop overlay
```

## Building

```bash
cd gui-overlay
cargo build --release
```

Binary: `gui-overlay/target/release/a1-overlay`

## Integration with main.py

```python
from core import overlay

def main():
    overlay.start()
    overlay.idle()
    
    while True:
        if wake_word_detected():
            overlay.listening()
            command = listen()
            
            overlay.thinking()
            response = process(command)
            
            overlay.speaking()
            speak(response)
            
            overlay.idle()
```

## Toggling Interaction Mode

If you need to temporarily enable mouse/keyboard input:

```python
# From Python (planned)
overlay.enable_interaction()
overlay.disable_interaction()
```

```javascript
// From JavaScript (Tauri IPC)
await invoke('enable_interaction');
await invoke('disable_interaction');
```

---

## Related Docs

- [[Core_TTS]] - Voice synthesis
- [[Core_ASR]] - Speech recognition
- [[Main_Loop]] - Integration point
