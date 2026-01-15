import subprocess
import time
from colorama import Fore, Style

APP_ALIASES = {
    "code": "code",
    "vscode": "code",
    "browser": "firefox",
    "firefox": "firefox",
    "chrome": "google-chrome",
    "terminal": "gnome-terminal",
    "files": "nautilus",
    "explorer": "nautilus",
    "calculator": "gnome-calculator",
    "spotify": "spotify",
    "discord": "discord"
}

def open_app(app_name: str):
    """Opens an application by name."""
    print(f"{Fore.CYAN}[APP] Opening {app_name}...{Style.RESET_ALL}")
    
    # 1. Resolve alias
    cmd = APP_ALIASES.get(app_name.lower(), app_name.lower())
    
    # 2. Try to launch
    try:
        subprocess.Popen(cmd, shell=True, start_new_session=True)
        return f"Opening {app_name}."
    except Exception as e:
        print(f"{Fore.RED}[APP ERROR] Failed to open {app_name}: {e}{Style.RESET_ALL}")
        return f"I failed to open {app_name}."

def close_app(app_name: str):
    """Closes an application by name (SIGTERM)."""
    print(f"{Fore.CYAN}[APP] Closing {app_name}...{Style.RESET_ALL}")
    
    # Resolving alias might be tricky for pkill, usually we need actual process name
    # We'll use the alias value if present, else input
    process_name = APP_ALIASES.get(app_name.lower(), app_name.lower())
    
    try:
        subprocess.run(["pkill", "-f", process_name], check=False)
        return f"Closing {app_name}."
    except Exception as e:
        return f"I could not close {app_name}."

def focus_app(app_name: str):
    """Focuses a window (requires wmctrl)."""
    # Needs: sudo apt-get install wmctrl
    process_name = APP_ALIASES.get(app_name.lower(), app_name.lower())
    try:
        subprocess.run(f"wmctrl -a '{process_name}'", shell=True)
        return f"Focusing {app_name}."
    except:
        return "I can't manage windows yet (wmctrl missing?)."
