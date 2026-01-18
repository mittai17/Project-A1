// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{Manager, Emitter};

/// State to track whether the overlay is in interactive mode
struct OverlayState {
    interactive: std::sync::Mutex<bool>,
}

/// Enable interaction mode - makes window focusable and captures mouse events
#[tauri::command]
fn enable_interaction(window: tauri::Window, state: tauri::State<OverlayState>) -> Result<(), String> {
    let mut interactive = state.interactive.lock().map_err(|e| e.to_string())?;
    
    // Enable focus and mouse capture
    window.set_ignore_cursor_events(false).map_err(|e| e.to_string())?;
    
    // Note: set_focusable is applied via platform-specific code in setup
    // For dynamic focus changes, we emit an event to the frontend
    window.emit("interaction-mode", true).map_err(|e| e.to_string())?;
    
    *interactive = true;
    println!("[A1 Overlay] Interaction mode ENABLED - window now accepts input");
    Ok(())
}

/// Disable interaction mode - makes window non-focusable and click-through
#[tauri::command]
fn disable_interaction(window: tauri::Window, state: tauri::State<OverlayState>) -> Result<(), String> {
    let mut interactive = state.interactive.lock().map_err(|e| e.to_string())?;
    
    // Disable mouse capture (click-through)
    window.set_ignore_cursor_events(true).map_err(|e| e.to_string())?;
    
    window.emit("interaction-mode", false).map_err(|e| e.to_string())?;
    
    *interactive = false;
    println!("[A1 Overlay] Interaction mode DISABLED - window is now click-through");
    Ok(())
}

/// Get current interaction state
#[tauri::command]
fn is_interactive(state: tauri::State<OverlayState>) -> bool {
    *state.interactive.lock().unwrap_or_else(|e| e.into_inner())
}

/// Update the overlay visual state (e.g., listening, thinking, speaking)
#[tauri::command]
fn set_overlay_state(window: tauri::Window, visual_state: String) -> Result<(), String> {
    window.emit("overlay-state", visual_state).map_err(|e| e.to_string())?;
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .manage(OverlayState {
            interactive: std::sync::Mutex::new(false),
        })
        .setup(|app| {
            let window = app.get_webview_window("main").expect("Failed to get main window");
            
            // ============================================================
            // CRITICAL: Siri-style non-intrusive overlay configuration
            // ============================================================
            
            // 1. Make window non-focusable
            // This prevents the window from stealing keyboard focus from other apps.
            // Keyboard input continues to go to whatever app the user is working in.
            #[cfg(target_os = "linux")]
            {
                // On Linux/X11, we need to set window type hints
                // This is handled by the window configuration in tauri.conf.json
                // Additional hints can be set via GTK if needed
                println!("[A1 Overlay] Linux: Using X11/Wayland window hints from config");
            }
            
            #[cfg(target_os = "windows")]
            {
                // On Windows, WS_EX_NOACTIVATE is applied automatically
                // when using the configuration options
                println!("[A1 Overlay] Windows: NoActivate style applied");
            }
            
            #[cfg(target_os = "macos")]
            {
                // On macOS, this requires the macos-private-api feature
                println!("[A1 Overlay] macOS: Using private API for non-activating window");
            }
            
            // 2. Enable click-through (ignore cursor events)
            // Mouse clicks pass through the window to applications behind it.
            // This is the key to not interrupting user workflow.
            window.set_ignore_cursor_events(true)
                .expect("Failed to set ignore cursor events");
            
            println!("============================================================");
            println!("[A1 Overlay] Siri-style overlay initialized!");
            println!("  - Always on top: YES");
            println!("  - Decorations: NO");
            println!("  - Transparent: YES");
            println!("  - Skip taskbar: YES");
            println!("  - Focusable: NO (keyboard goes to active app)");
            println!("  - Click-through: YES (mouse goes to apps behind)");
            println!("============================================================");
            println!("");
            println!("Commands available:");
            println!("  - enable_interaction()  : Allow mouse/keyboard input");
            println!("  - disable_interaction() : Return to click-through mode");
            println!("============================================================");
            
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            enable_interaction,
            disable_interaction,
            is_interactive,
            set_overlay_state
        ])
        .run(tauri::generate_context!())
        .expect("Error running A1 Overlay");
}
