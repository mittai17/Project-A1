"""
A1 Overlay Controller
Communicates with the Tauri overlay via a simple HTTP server.

States:
- idle: Purple orb, gentle pulse
- listening: Green orb, waveform animation
- thinking: Orange orb, spinning glow  
- speaking: Blue orb, wave animation
- error: Red orb, shake effect
"""

import subprocess
import os
import time
import threading
import http.server
import socketserver
from pathlib import Path
from colorama import Fore, Style

# Path to the overlay binary
BASE_DIR = Path(__file__).parent.parent
OVERLAY_BINARY = BASE_DIR / "gui-overlay" / "target" / "release" / "a1-overlay"

# HTTP Server for state communication
STATE_PORT = 9877
current_state = "idle"

class StateHandler(http.server.BaseHTTPRequestHandler):
    """Simple HTTP handler that returns the current overlay state"""
    
    def log_message(self, format, *args):
        pass  # Suppress logging
    
    def do_GET(self):
        global current_state
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')  # CORS
        self.end_headers()
        self.wfile.write(current_state.encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.end_headers()

class OverlayController:
    """Controls the A1 Siri-style overlay"""
    
    def __init__(self, auto_start=True):
        self.process = None
        self.is_running = False
        self.server = None
        self.server_thread = None
        
        if auto_start:
            self.start()
    
    def _start_state_server(self):
        """Start the HTTP server for state communication"""
        try:
            self.server = socketserver.TCPServer(("127.0.0.1", STATE_PORT), StateHandler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            print(f"{Fore.GREEN}[OVERLAY] State server running on port {STATE_PORT}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[OVERLAY] Failed to start state server: {e}{Style.RESET_ALL}")
    
    def start(self):
        """Start the overlay application and state server"""
        if self.is_running:
            return True
        
        # Start state server first
        self._start_state_server()
            
        if not OVERLAY_BINARY.exists():
            print(f"{Fore.YELLOW}[OVERLAY] Binary not found at {OVERLAY_BINARY}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[OVERLAY] Please build with: cd gui-overlay && cargo build --release{Style.RESET_ALL}")
            return False
        
        try:
            # Start the overlay process
            self.process = subprocess.Popen(
                [str(OVERLAY_BINARY)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True  # Detach from parent
            )
            self.is_running = True
            print(f"{Fore.GREEN}[OVERLAY] Started (PID: {self.process.pid}){Style.RESET_ALL}")
            
            # Give it a moment to initialize
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[OVERLAY] Failed to start: {e}{Style.RESET_ALL}")
            return False
    
    def stop(self):
        """Stop the overlay application"""
        if self.server:
            self.server.shutdown()
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
                print(f"{Fore.YELLOW}[OVERLAY] Stopped{Style.RESET_ALL}")
            except:
                self.process.kill()
            self.process = None
            self.is_running = False
    
    def set_state(self, state: str):
        """
        Set the overlay visual state.
        Updates the global state variable that the HTTP server returns.
        
        States: idle, listening, thinking, speaking, error
        """
        global current_state
        current_state = state
    
    def idle(self):
        """Set to idle state (purple, gentle pulse)"""
        self.set_state("idle")
        
    def listening(self):
        """Set to listening state (green, waveform)"""
        self.set_state("listening")
        
    def thinking(self):
        """Set to thinking state (orange, spinning)"""
        self.set_state("thinking")
        
    def speaking(self):
        """Set to speaking state (blue, wave)"""
        self.set_state("speaking")
        
    def error(self):
        """Set to error state (red, shake)"""
        self.set_state("error")
    
    def __del__(self):
        """Cleanup on destruction"""
        pass


# Global instance for easy access
_overlay = None

def get_overlay() -> OverlayController:
    """Get or create the global overlay controller"""
    global _overlay
    if _overlay is None:
        _overlay = OverlayController(auto_start=True)
    return _overlay

def start():
    """Start the overlay"""
    return get_overlay().start()

def stop():
    """Stop the overlay"""
    return get_overlay().stop()

def idle():
    """Set to idle state"""
    get_overlay().idle()

def listening():
    """Set to listening state"""
    get_overlay().listening()

def thinking():
    """Set to thinking state"""
    get_overlay().thinking()

def speaking():
    """Set to speaking state"""
    get_overlay().speaking()

def error():
    """Set to error state"""
    get_overlay().error()


if __name__ == "__main__":
    # Test the overlay
    print("Testing overlay states...")
    
    overlay = get_overlay()
    
    print("Idle...")
    overlay.idle()
    time.sleep(2)
    
    print("Listening...")
    overlay.listening()
    time.sleep(2)
    
    print("Thinking...")
    overlay.thinking()
    time.sleep(2)
    
    print("Speaking...")
    overlay.speaking()
    time.sleep(2)
    
    print("Idle...")
    overlay.idle()
    time.sleep(2)
    
    print("Done! Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        overlay.stop()
