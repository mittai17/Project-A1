# A1 Siri-Style Overlay

A non-intrusive, always-visible voice assistant overlay built with Tauri v2.

## Features

- 🎯 **Always on Top** - Stays visible without blocking your work
- 👻 **Click-Through** - Mouse clicks pass through to apps behind
- ⌨️ **No Focus Stealing** - Keyboard input goes to your active app
- 🎨 **Beautiful Orb UI** - Animated Siri-style visualization
- 🔄 **State-Aware** - Visual feedback for idle/listening/thinking/speaking

## Quick Start

```bash
# Install dependencies
cd gui-overlay
cargo build

# Run in development
cargo tauri dev

# Build for production
cargo tauri build
```

## Architecture

```
gui-overlay/
├── dist/                    # Frontend assets
│   ├── index.html          # Main HTML
│   ├── styles.css          # Siri-style animations
│   └── app.js              # Tauri IPC & state management
└── src-tauri/
    ├── tauri.conf.json     # Window configuration
    ├── Cargo.toml          # Rust dependencies
    └── src/
        └── main.rs         # Rust backend
```

## How It Works

### Why It Doesn't Interrupt Your Work

1. **`alwaysOnTop: true`** - Window stays visible above other apps
2. **`decorations: false`** - No title bar or borders
3. **`transparent: true`** - Background is see-through
4. **`focus: false`** - Window doesn't take focus on creation
5. **`set_ignore_cursor_events(true)`** - Mouse clicks pass through
6. **`skipTaskbar: true`** - Doesn't appear in taskbar

The key is `set_ignore_cursor_events(true)` in the Rust setup:
- All mouse events go to whatever app is behind the overlay
- The overlay is purely visual - it cannot intercept input

### Enabling Interaction (When Needed)

To temporarily enable mouse/keyboard input:

```javascript
// From JavaScript
window.A1Overlay.enableInteraction();

// From Rust/Python backend
invoke('enable_interaction');
```

To return to click-through mode:

```javascript
window.A1Overlay.disableInteraction();
```

## Visual States

| State | Color | Animation |
|-------|-------|-----------|
| Idle | Purple | Gentle pulse |
| Listening | Green | Waveform bars |
| Thinking | Orange | Spinning glow |
| Speaking | Blue | Wave animation |
| Error | Red | Shake effect |

## Integration with Python Backend

The overlay can be controlled from your Python A1 backend:

```python
import subprocess

# Start the overlay
overlay_process = subprocess.Popen(['./gui-overlay/target/release/a1-overlay'])

# Send state updates via Tauri events (implement WebSocket or IPC)
```

## License

MIT
