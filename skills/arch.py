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

def install_package(package_name):
    """Installs a package."""
    print(f"{Fore.CYAN}[ARCH] Installing {package_name}...{Style.RESET_ALL}")
    
    cmd = f"sudo pacman -S {package_name}"
    if is_installed("yay"):
        cmd = f"yay -S {package_name}"
        
    term = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("kitty")
    
    if term:
        try:
             if "gnome-terminal" in term:
                subprocess.Popen([term, "--", "bash", "-c", f"{cmd}; echo 'Press Enter to close.'; read"])
             else:
                subprocess.Popen([term, "-e", f"bash -c '{cmd}; read'"])
             return f"Installing {package_name}."
        except:
            return "Failed to open terminal."
    return "No terminal found."
