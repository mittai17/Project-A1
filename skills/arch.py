import subprocess
import psutil
import shutil
from colorama import Fore, Style

def get_system_stats():
    """Returns CPU and RAM usage."""
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        return f"CPU is at {cpu}%, RAM is at {ram}%."
    except Exception as e:
        return f"Could not get stats: {e}"

def is_installed(tool):
    return shutil.which(tool) is not None

def update_system():
    """Updates Arch Linux system using pacman or yay."""
    print(f"{Fore.CYAN}[ARCH] Updating System...{Style.RESET_ALL}")
    
    cmd = None
    if is_installed("yay"):
        # Use yay if available (handles AUR)
        # We need to run this in a visible terminal because of sudo password
        # Auto-detect terminal?
        cmd = "yay -Syu"
    else:
        cmd = "sudo pacman -Syu"
        
    # Launch in new terminal
    # Try generic terminals
    term = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("kitty") or shutil.which("alacritty") or shutil.which("xterm")
    
    if term:
        try:
            # Most terminals accept -e or similar. gnome-terminal uses --
            if "gnome-terminal" in term:
                subprocess.Popen([term, "--", "bash", "-c", f"{cmd}; echo 'Done. Press Enter to close.'; read"])
            elif "konsole" in term:
                subprocess.Popen([term, "-e", "bash", "-c", f"{cmd}; echo 'Done. Press Enter to close.'; read"])
            else:
                 subprocess.Popen([term, "-e", f"bash -c '{cmd}; read'"])
            return "I've launched the system update in a new terminal."
        except Exception as e:
            return f"Failed to launch terminal: {e}"
    else:
        return "I couldn't find a terminal emulator to run the update."

def resolve_package(query):
    """
    Tries to find the exact package name using yay/pacman search.
    Returns the best match or the original query.
    """
    print(f"{Fore.CYAN}[ARCH] Resolving package '{query}'...{Style.RESET_ALL}")
    
    # Clean query
    query = query.replace(" ", "-").lower()
    
    # Search command
    search_cmd = "yay -Ss" if is_installed("yay") else "pacman -Ss"
    
    try:
        # Get top 5 results
        result = subprocess.check_output(f"{search_cmd} {query} | head -n 10", shell=True).decode('utf-8')
        lines = result.split('\n')
        
        # Parse results: "aur/visual-studio-code-bin 1.96-1 (+1234 5.6) ...\n    Description"
        # We look for the package name line (every 2nd line usually, or lines starting with repo/)
        candidates = []
        for line in lines:
            if "/" in line and "(" in line: # simplistic heuristics for pacman -Ss output
                parts = line.split('/')
                if len(parts) > 1:
                    pkg_name = parts[1].split(' ')[0]
                    candidates.append(pkg_name)
                    
        if candidates:
            # Prefer exact match if exists in candidates
            if query in candidates:
                return query
            
            # Prefer 'bin' versions for proprietaries (e.g. spotify)
            bin_matches = [c for c in candidates if c.endswith("-bin")]
            if bin_matches:
                return bin_matches[0]
                
            # Otherwise return first candidate
            print(f"{Fore.GREEN}[ARCH] Resolved '{query}' -> '{candidates[0]}'{Style.RESET_ALL}")
            return candidates[0]
            
    except Exception as e:
        print(f"{Fore.RED}[ARCH] Resolution failed: {e}{Style.RESET_ALL}")
        
    return query

def install_package(package_name):
    """Installs a package after resolving its name."""
    
    real_package = resolve_package(package_name)
    
    print(f"{Fore.CYAN}[ARCH] Installing {real_package} (originally {package_name})...{Style.RESET_ALL}")
    
    cmd = f"sudo pacman -S {real_package}"
    if is_installed("yay"):
        cmd = f"yay -S {real_package}"
        
    term = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("kitty") or shutil.which("alacritty") or shutil.which("xterm")
    
    if term:
        try:
             # Similar logic to before, but using resolved name
             term_flag = "-e"
             shell_cmd = f"bash -c '{cmd}; echo \"Done. Press Enter to close.\"; read'"
             
             if "gnome-terminal" in term:
                 subprocess.Popen([term, "--", "bash", "-c", f"{cmd}; echo 'Done. Press Enter to close.'; read"])
             elif "konsole" in term:
                subprocess.Popen([term, "-e", "bash", "-c", f"{cmd}; echo 'Done. Press Enter to close.'; read"])
             else:
                subprocess.Popen([term, "-e", shell_cmd])
                
             return f"I've started installing {real_package}."
        except Exception as e:
            return f"Failed to open terminal: {e}"
    
    # Fallback if no terminal
    return "No terminal emulator found. Cannot install."
