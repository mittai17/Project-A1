import subprocess
import time
import os
import glob
import difflib
from colorama import Fore, Style

# Cache for app paths
APP_CACHE = {}

def build_app_cache():
    """Scans .desktop files to build a map of {app_name: exec_cmd}."""
    global APP_CACHE
    if APP_CACHE:
        return

    print(f"{Fore.CYAN}[APP] building app cache...{Style.RESET_ALL}")
    
    # Common locations for .desktop files
    paths = [
        "/usr/share/applications/*.desktop",
        os.path.expanduser("~/.local/share/applications/*.desktop"),
        "/var/lib/snapd/desktop/applications/*.desktop"
    ]
    
    for path_glob in paths:
        for filepath in glob.glob(path_glob):
            try:
                name = None
                exec_cmd = None
                with open(filepath, "r", errors='ignore') as f:
                    for line in f:
                        if line.startswith("Name=") and not name:
                            name = line.strip().replace("Name=", "").lower()
                        if line.startswith("Exec=") and not exec_cmd:
                            exec_cmd = line.strip().replace("Exec=", "")
                            # Cleanup exec (remove %u, %F etc)
                            exec_cmd = exec_cmd.split("%")[0].strip()
                
                if name and exec_cmd:
                    APP_CACHE[name] = exec_cmd
            except:
                continue
                
    # Add manual aliases
    APP_CACHE["code"] = "code"
    APP_CACHE["vscode"] = "code"
    APP_CACHE["terminal"] = "gnome-terminal"

def find_best_match(app_name):
    """Finds the closest matching app name."""
    build_app_cache()
    matches = difflib.get_close_matches(app_name.lower(), APP_CACHE.keys(), n=1, cutoff=0.6)
    return matches[0] if matches else None

def open_app(app_name: str):
    """Opens an application by name (fuzzy matched)."""
    print(f"{Fore.CYAN}[APP] Finding {app_name}...{Style.RESET_ALL}")
    
    # 1. Check exact or fuzzy match in .desktop cache
    match = find_best_match(app_name)
    
    if match:
        cmd = APP_CACHE[match]
        print(f"{Fore.GREEN}[APP] Found match: {match} -> {cmd}{Style.RESET_ALL}")
        try:
            subprocess.Popen(cmd, shell=True, start_new_session=True)
            return f"Opening {match}."
        except Exception as e:
            return f"Failed to open {match}."
            
    # 2. Fallback: Try running as direct command
    if subprocess.call(f"which {app_name}", shell=True, stdout=subprocess.DEVNULL) == 0:
        try:
            subprocess.Popen(app_name, shell=True, start_new_session=True)
            return f"Opening {app_name}."
        except:
            pass
            
    return f"I couldn't find an app called {app_name}."

def close_app(app_name: str):
    """Closes an application by name (SIGTERM)."""
    print(f"{Fore.CYAN}[APP] Closing {app_name}...{Style.RESET_ALL}")
    
    # 1. Try to find the executable name from our cache
    # E.g. "VS Code" -> "code"
    match = find_best_match(app_name)
    target = app_name
    
    if match:
        # Get the actual command/executable
        # exec_cmd might be "code --url ..." or "/usr/bin/spotify %U"
        full_cmd = APP_CACHE[match]
        # We generally want the binary name for pkill (e.g. "spotify", "code")
        # Split by space and take the first part, then basename
        target = os.path.basename(full_cmd.split()[0])
        print(f"{Fore.GREEN}[APP] Resolved '{app_name}' -> kill '{target}'{Style.RESET_ALL}")

    if not target or len(target) < 2:
        return f"I couldn't identify the process for {app_name}."

    try:
        # Try pkill -x (exact match) first for safety if we resolved it
        if match:
            subprocess.run(["pkill", "-x", target], check=False)
            # Find and kill might be async, wait a tiny bit to check? 
            # Nah, fire and forget for UI responsiveness.
        
        # Fallback to fuzzy kill pkill -f if the first failed or if we didn't match
        # But be careful not to kill system processes if target is generic
        subprocess.run(["pkill", "-f", target], check=False)
        
        return f"Closing {app_name}."
    except Exception as e:
        return f"I could not close {app_name}: {e}"

def focus_app(app_name: str):
    """Focuses a window (requires wmctrl)."""
    try:
        match = find_best_match(app_name)
        target = match if match else app_name
        subprocess.run(f"wmctrl -a '{target}'", shell=True)
        return f"Focusing {target}."
    except:
        return "I can't manage windows yet (wmctrl missing?)."
