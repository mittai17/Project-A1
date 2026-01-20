import subprocess
import psutil
import shutil
from colorama import Fore, Style

# ============================================================
# SYSTEM STATUS & STATS
# ============================================================

def get_system_stats():
    """
    Returns CPU, RAM, and GPU usage (if Nvidia).
    """
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        ram = psutil.virtual_memory().percent
        
        # GPU Stats (Nvidia)
        gpu_stats = ""
        try:
            # Check for nvidia-smi
            result = subprocess.run(['nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                util, temp, mem_used, mem_total = result.stdout.strip().split(', ')
                gpu_stats = f", GPU: {util}% used at {temp}°C ({mem_used}/{mem_total}MB VRAM)"
        except:
            pass # No Nvidia GPU or error

        return f"CPU: {cpu}%, RAM: {ram}%{gpu_stats}."
    except Exception as e:
        return f"Could not get stats: {e}"

def get_network_info():
    """Returns detailed network diagnostics."""
    try:
        # Get Local IP
        ip_cmd = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
        ip = ip_cmd.stdout.strip().split()[0] if ip_cmd.stdout.strip() else "Unknown"
        
        # Ping Google for latency
        ping_cmd = subprocess.run(['ping', '-c', '1', '8.8.8.8'], capture_output=True, text=True)
        if ping_cmd.returncode == 0:
            import re
            match = re.search(r"time=([\d\.]+) ms", ping_cmd.stdout)
            latency = f"{match.group(1)}ms" if match else "Online"
            status = f"Connected ({latency})"
        else:
            status = "Offline"
            
        return f"Network Status: {status} | Local IP: {ip}"
    except Exception as e:
        return f"Network scan failed: {e}"

def get_full_system_status():
    """Returns comprehensive system status including GPU and Network."""
    try:
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # GPU
        gpu_info = "N/A"
        try:
            res = subprocess.run(['nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu', '--format=csv,noheader'], capture_output=True, text=True)
            if res.returncode == 0:
                gpu_info = res.stdout.strip()
        except:
            pass

        # Battery info if available
        battery = psutil.sensors_battery()
        battery_str = ""
        if battery:
            battery_str = f"Battery: {battery.percent}%"
            if battery.power_plugged:
                battery_str += " (charging)"
            else:
                mins = battery.secsleft // 60
                battery_str += f" ({mins} min remaining)"
        
        # Network
        net_info = get_network_info()
        
        status = f"""System Status:
• CPU: {cpu}%
• RAM: {ram.percent}% ({ram.used // (1024**3):.1f}/{ram.total // (1024**3):.1f} GB)
• GPU: {gpu_info}
• Disk: {disk.percent}% ({disk.used // (1024**3):.0f}/{disk.total // (1024**3):.0f} GB)
• {net_info}"""
        
        if battery_str:
            status += f"\n• {battery_str}"
            
        return status
    except Exception as e:
        return f"Could not get full stats: {e}"

# ============================================================
# POWER MANAGEMENT
# ============================================================

def shutdown():
    """Shuts down the system."""
    print(f"{Fore.RED}[ARCH] Initiating shutdown...{Style.RESET_ALL}")
    try:
        subprocess.run(["systemctl", "poweroff"], check=True)
        return "Shutting down now. Goodbye!"
    except Exception as e:
        return f"Could not shutdown: {e}"

def reboot():
    """Reboots the system."""
    print(f"{Fore.YELLOW}[ARCH] Initiating reboot...{Style.RESET_ALL}")
    try:
        subprocess.run(["systemctl", "reboot"], check=True)
        return "Rebooting now. See you soon!"
    except Exception as e:
        return f"Could not reboot: {e}"

def suspend():
    """Suspends the system (sleep mode)."""
    print(f"{Fore.CYAN}[ARCH] Suspending system...{Style.RESET_ALL}")
    try:
        subprocess.run(["systemctl", "suspend"], check=True)
        return "Suspending now. Goodnight!"
    except Exception as e:
        return f"Could not suspend: {e}"

def lock_screen():
    """Locks the screen using available lock programs."""
    print(f"{Fore.CYAN}[ARCH] Locking screen...{Style.RESET_ALL}")
    
    # Try different lock programs
    lockers = ["hyprlock", "swaylock", "i3lock", "gnome-screensaver-command -l", 
               "loginctl lock-session", "xdg-screensaver lock"]
    
    for locker in lockers:
        cmd = locker.split()[0]
        if shutil.which(cmd):
            try:
                subprocess.Popen(locker, shell=True)
                return "Screen locked."
            except:
                continue
    
    return "No screen locker found. Please install hyprlock, swaylock, or i3lock."

def sentry_mode():
    """Confirms security protocol: Locks screen and mutes audio."""
    # Mute Audio
    try:
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"], check=False)
    except:
        pass
        
    # Lock Screen
    return lock_screen()

# ============================================================
# AUDIO CONTROL (PulseAudio/PipeWire via pactl)
# ============================================================

def volume_up(amount: int = 5):
    """Increases volume by specified percentage."""
    print(f"{Fore.GREEN}[ARCH] Volume up by {amount}%{Style.RESET_ALL}")
    try:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{amount}%"], check=True)
        vol = _get_current_volume()
        return f"Volume increased to {vol}%."
    except Exception as e:
        # Try wpctl for WirePlumber
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{amount}%+"], check=True)
            return f"Volume increased."
        except:
            return f"Could not change volume: {e}"

def volume_down(amount: int = 5):
    """Decreases volume by specified percentage."""
    print(f"{Fore.GREEN}[ARCH] Volume down by {amount}%{Style.RESET_ALL}")
    try:
        subprocess.run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{amount}%"], check=True)
        vol = _get_current_volume()
        return f"Volume decreased to {vol}%."
    except Exception as e:
        try:
            subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{amount}%-"], check=True)
            return f"Volume decreased."
        except:
            return f"Could not change volume: {e}"

def mute_toggle():
    """Toggles mute on/off."""
    print(f"{Fore.YELLOW}[ARCH] Toggling mute...{Style.RESET_ALL}")
    try:
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"], check=True)
        # Check current mute state
        result = subprocess.check_output(["pactl", "get-sink-mute", "@DEFAULT_SINK@"]).decode()
        is_muted = "yes" in result.lower()
        return "Audio muted." if is_muted else "Audio unmuted."
    except Exception as e:
        try:
            subprocess.run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"], check=True)
            return "Audio mute toggled."
        except:
            return f"Could not toggle mute: {e}"

def _get_current_volume():
    """Get current volume percentage."""
    try:
        result = subprocess.check_output(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]).decode()
        # Parse "Volume: front-left: 65536 / 100% / ..."
        import re
        match = re.search(r'(\d+)%', result)
        if match:
            return int(match.group(1))
    except:
        pass
    return "unknown"

# ============================================================
# DISPLAY BRIGHTNESS (using brightnessctl)
# ============================================================

def brightness_up(amount: int = 10):
    """Increases screen brightness."""
    print(f"{Fore.GREEN}[ARCH] Brightness up by {amount}%{Style.RESET_ALL}")
    try:
        subprocess.run(["brightnessctl", "set", f"+{amount}%"], check=True)
        return f"Brightness increased."
    except FileNotFoundError:
        return "brightnessctl not found. Install it with: yay -S brightnessctl"
    except Exception as e:
        return f"Could not change brightness: {e}"

def brightness_down(amount: int = 10):
    """Decreases screen brightness."""
    print(f"{Fore.GREEN}[ARCH] Brightness down by {amount}%{Style.RESET_ALL}")
    try:
        subprocess.run(["brightnessctl", "set", f"{amount}%-"], check=True)
        return f"Brightness decreased."
    except FileNotFoundError:
        return "brightnessctl not found. Install it with: yay -S brightnessctl"
    except Exception as e:
        return f"Could not change brightness: {e}"

# ============================================================
# NETWORK / WIFI CONTROL (using nmcli)
# ============================================================

def wifi_on():
    """Enables WiFi."""
    print(f"{Fore.GREEN}[ARCH] Enabling WiFi...{Style.RESET_ALL}")
    try:
        subprocess.run(["nmcli", "radio", "wifi", "on"], check=True)
        return "WiFi enabled."
    except FileNotFoundError:
        return "NetworkManager not found. Install it with: yay -S networkmanager"
    except Exception as e:
        return f"Could not enable WiFi: {e}"

def wifi_off():
    """Disables WiFi."""
    print(f"{Fore.RED}[ARCH] Disabling WiFi...{Style.RESET_ALL}")
    try:
        subprocess.run(["nmcli", "radio", "wifi", "off"], check=True)
        return "WiFi disabled."
    except FileNotFoundError:
        return "NetworkManager not found."
    except Exception as e:
        return f"Could not disable WiFi: {e}"

def wifi_status():
    """Gets WiFi status and connected network."""
    try:
        # Check if WiFi is on
        result = subprocess.check_output(["nmcli", "radio", "wifi"]).decode().strip()
        if result == "disabled":
            return "WiFi is disabled."
        
        # Get connected network
        result = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid", "dev", "wifi"]).decode()
        for line in result.split('\n'):
            if line.startswith("yes:"):
                ssid = line.split(":")[1]
                return f"WiFi is on, connected to '{ssid}'."
        
        return "WiFi is on but not connected to any network."
    except Exception as e:
        return f"Could not get WiFi status: {e}"

# ============================================================
# PACKAGE MANAGEMENT (Existing functions)
# ============================================================

def is_installed(tool):
    return shutil.which(tool) is not None

def update_system():
    """Updates Arch Linux system using pacman or yay."""
    print(f"{Fore.CYAN}[ARCH] Updating System...{Style.RESET_ALL}")
    
    cmd = None
    if is_installed("yay"):
        cmd = "yay -Syu"
    else:
        cmd = "sudo pacman -Syu"
        
    # Launch in new terminal
    term = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("kitty") or shutil.which("alacritty") or shutil.which("xterm")
    
    if term:
        try:
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
    """Tries to find the exact package name using yay/pacman search."""
    print(f"{Fore.CYAN}[ARCH] Resolving package '{query}'...{Style.RESET_ALL}")
    
    query = query.replace(" ", "-").lower()
    search_cmd = "yay -Ss" if is_installed("yay") else "pacman -Ss"
    
    try:
        result = subprocess.check_output(f"{search_cmd} {query} | head -n 10", shell=True).decode('utf-8')
        lines = result.split('\n')
        
        candidates = []
        for line in lines:
            if "/" in line and "(" in line:
                parts = line.split('/')
                if len(parts) > 1:
                    pkg_name = parts[1].split(' ')[0]
                    candidates.append(pkg_name)
                    
        if candidates:
            if query in candidates:
                return query
            
            bin_matches = [c for c in candidates if c.endswith("-bin")]
            if bin_matches:
                return bin_matches[0]
                
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
    
    return "No terminal emulator found. Cannot install."

def uninstall_package(package_name):
    """Uninstalls a package."""
    print(f"{Fore.RED}[ARCH] Uninstalling {package_name}...{Style.RESET_ALL}")
    
    cmd = f"sudo pacman -Rs {package_name}"
    if is_installed("yay"):
        cmd = f"yay -Rs {package_name}"
    
    term = shutil.which("gnome-terminal") or shutil.which("konsole") or shutil.which("kitty") or shutil.which("alacritty") or shutil.which("xterm")
    
    if term:
        try:
            if "gnome-terminal" in term:
                subprocess.Popen([term, "--", "bash", "-c", f"{cmd}; echo 'Done. Press Enter to close.'; read"])
            else:
                subprocess.Popen([term, "-e", f"bash -c '{cmd}; read'"])
            return f"I've started uninstalling {package_name}."
        except Exception as e:
            return f"Failed: {e}"
    
    return "No terminal found."

# ============================================================
# BLUETOOTH CONTROL (using bluetoothctl)
# ============================================================

def bluetooth_on():
    """Enables Bluetooth."""
    print(f"{Fore.CYAN}[ARCH] Enabling Bluetooth...{Style.RESET_ALL}")
    try:
        subprocess.run(["bluetoothctl", "power", "on"], check=True)
        return "Bluetooth enabled."
    except FileNotFoundError:
        return "bluetoothctl not found. Install bluez: yay -S bluez bluez-utils"
    except Exception as e:
        return f"Could not enable Bluetooth: {e}"

def bluetooth_off():
    """Disables Bluetooth."""
    print(f"{Fore.RED}[ARCH] Disabling Bluetooth...{Style.RESET_ALL}")
    try:
        subprocess.run(["bluetoothctl", "power", "off"], check=True)
        return "Bluetooth disabled."
    except Exception as e:
        return f"Could not disable Bluetooth: {e}"

def bluetooth_status():
    """Gets Bluetooth status."""
    try:
        result = subprocess.check_output(["bluetoothctl", "show"], timeout=5).decode()
        powered = "Powered: yes" in result
        
        if not powered:
            return "Bluetooth is off."
        
        # Check connected devices
        devices = subprocess.check_output(["bluetoothctl", "devices", "Connected"], timeout=5).decode()
        if devices.strip():
            device_names = [line.split(" ", 2)[2] for line in devices.strip().split("\n") if line]
            return f"Bluetooth is on. Connected to: {', '.join(device_names)}"
        
        return "Bluetooth is on but no devices connected."
    except Exception as e:
        return f"Could not get Bluetooth status: {e}"

# ============================================================
# SCREENSHOT & RECORDING
# ============================================================

def take_screenshot(filename: str = None):
    """Takes a screenshot and saves it."""
    import os
    from datetime import datetime
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.expanduser(f"~/Pictures/screenshot_{timestamp}.png")
    
    print(f"{Fore.CYAN}[ARCH] Taking screenshot...{Style.RESET_ALL}")
    
    # Try different screenshot tools
    tools = [
        ["grimblast", "save", "screen", filename],  # Hyprland
        ["grim", filename],  # Wayland
        ["scrot", filename],  # X11
        ["gnome-screenshot", "-f", filename],  # GNOME
        ["spectacle", "-b", "-n", "-o", filename],  # KDE
    ]
    
    for tool in tools:
        if shutil.which(tool[0]):
            try:
                subprocess.run(tool, check=True)
                return f"Screenshot saved to {filename}"
            except:
                continue
    
    return "No screenshot tool found. Install grim (Wayland) or scrot (X11)."

def take_screenshot_area():
    """Takes a screenshot of selected area."""
    print(f"{Fore.CYAN}[ARCH] Select area for screenshot...{Style.RESET_ALL}")
    
    tools = [
        ["grimblast", "save", "area"],  # Hyprland
        ["grim", "-g", "$(slurp)"],  # Wayland with slurp
        ["scrot", "-s"],  # X11 select
        ["gnome-screenshot", "-a"],  # GNOME area
    ]
    
    for tool in tools:
        if shutil.which(tool[0]):
            try:
                subprocess.Popen(" ".join(tool), shell=True)
                return "Select the area to capture."
            except:
                continue
    
    return "No screenshot tool found."

# ============================================================
# NIGHT MODE / BLUE LIGHT FILTER
# ============================================================

def night_mode_on(temperature: int = 4500):
    """Enables night mode (warm screen)."""
    print(f"{Fore.YELLOW}[ARCH] Enabling night mode...{Style.RESET_ALL}")
    
    # Try different tools
    if shutil.which("gammastep"):
        subprocess.Popen(["gammastep", "-O", str(temperature)])
        return f"Night mode enabled at {temperature}K."
    elif shutil.which("redshift"):
        subprocess.Popen(["redshift", "-O", str(temperature)])
        return f"Night mode enabled at {temperature}K."
    elif shutil.which("wlsunset"):
        subprocess.Popen(["wlsunset", "-t", str(temperature)])
        return "Night mode enabled."
    
    return "No night mode tool found. Install gammastep or redshift."

def night_mode_off():
    """Disables night mode."""
    print(f"{Fore.CYAN}[ARCH] Disabling night mode...{Style.RESET_ALL}")
    
    # Kill any running instances
    subprocess.run(["pkill", "-x", "gammastep"], capture_output=True)
    subprocess.run(["pkill", "-x", "redshift"], capture_output=True)
    subprocess.run(["pkill", "-x", "wlsunset"], capture_output=True)
    
    # Reset gamma
    if shutil.which("gammastep"):
        subprocess.run(["gammastep", "-x"], capture_output=True)
    elif shutil.which("redshift"):
        subprocess.run(["redshift", "-x"], capture_output=True)
    
    return "Night mode disabled."

# ============================================================
# SYSTEM CLEANUP
# ============================================================

def clean_package_cache():
    """Cleans pacman package cache."""
    print(f"{Fore.CYAN}[ARCH] Cleaning package cache...{Style.RESET_ALL}")
    try:
        # Keep only last version
        result = subprocess.run(["sudo", "paccache", "-r"], capture_output=True, text=True)
        return "Package cache cleaned. Kept only the last version of each package."
    except FileNotFoundError:
        return "paccache not found. Install pacman-contrib: yay -S pacman-contrib"
    except Exception as e:
        return f"Could not clean cache: {e}"

def remove_orphan_packages():
    """Removes orphaned packages."""
    print(f"{Fore.CYAN}[ARCH] Removing orphan packages...{Style.RESET_ALL}")
    
    term = shutil.which("alacritty") or shutil.which("kitty") or shutil.which("gnome-terminal") or shutil.which("xterm")
    cmd = "sudo pacman -Rns $(pacman -Qdtq)"
    
    if term:
        subprocess.Popen([term, "-e", f"bash -c '{cmd}; read'"])
        return "Checking for orphan packages..."
    
    return "No terminal found."

def clear_system_logs():
    """Clears old system logs."""
    print(f"{Fore.CYAN}[ARCH] Clearing old logs...{Style.RESET_ALL}")
    try:
        # Keep only last 3 days of logs
        subprocess.run(["sudo", "journalctl", "--vacuum-time=3d"], check=True)
        return "Cleared logs older than 3 days."
    except Exception as e:
        return f"Could not clear logs: {e}"

def empty_trash():
    """Empties the trash."""
    import os
    trash_paths = [
        os.path.expanduser("~/.local/share/Trash/files"),
        os.path.expanduser("~/.local/share/Trash/info"),
    ]
    
    print(f"{Fore.CYAN}[ARCH] Emptying trash...{Style.RESET_ALL}")
    
    try:
        for path in trash_paths:
            if os.path.exists(path):
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isfile(item_path):
                        os.remove(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
        return "Trash emptied."
    except Exception as e:
        return f"Could not empty trash: {e}"

# ============================================================
# DO NOT DISTURB / NOTIFICATIONS
# ============================================================

def do_not_disturb_on():
    """Enables do not disturb mode."""
    print(f"{Fore.YELLOW}[ARCH] Enabling Do Not Disturb...{Style.RESET_ALL}")
    
    # Try dunst (common notification daemon)
    if shutil.which("dunstctl"):
        subprocess.run(["dunstctl", "set-paused", "true"])
        return "Do Not Disturb enabled. Notifications paused."
    
    # Try mako (Wayland)
    if shutil.which("makoctl"):
        subprocess.run(["makoctl", "set-mode", "do-not-disturb"])
        return "Do Not Disturb enabled."
    
    return "No supported notification daemon found (dunst/mako)."

def do_not_disturb_off():
    """Disables do not disturb mode."""
    print(f"{Fore.GREEN}[ARCH] Disabling Do Not Disturb...{Style.RESET_ALL}")
    
    if shutil.which("dunstctl"):
        subprocess.run(["dunstctl", "set-paused", "false"])
        return "Do Not Disturb disabled. Notifications resumed."
    
    if shutil.which("makoctl"):
        subprocess.run(["makoctl", "set-mode", "default"])
        return "Do Not Disturb disabled."
    
    return "No supported notification daemon found."

# ============================================================
# CLIPBOARD MANAGEMENT
# ============================================================

def clear_clipboard():
    """Clears the clipboard."""
    print(f"{Fore.CYAN}[ARCH] Clearing clipboard...{Style.RESET_ALL}")
    
    # Wayland
    if shutil.which("wl-copy"):
        subprocess.run(["wl-copy", "--clear"])
        return "Clipboard cleared."
    
    # X11
    if shutil.which("xclip"):
        subprocess.run(["xclip", "-selection", "clipboard", "/dev/null"])
        return "Clipboard cleared."
    
    if shutil.which("xsel"):
        subprocess.run(["xsel", "--clipboard", "--clear"])
        return "Clipboard cleared."
    
    return "No clipboard tool found (wl-copy, xclip, or xsel)."

def get_clipboard():
    """Gets clipboard contents."""
    try:
        if shutil.which("wl-paste"):
            result = subprocess.check_output(["wl-paste"], timeout=2).decode().strip()
            return f"Clipboard contains: {result[:200]}..." if len(result) > 200 else f"Clipboard contains: {result}"
        
        if shutil.which("xclip"):
            result = subprocess.check_output(["xclip", "-selection", "clipboard", "-o"], timeout=2).decode().strip()
            return f"Clipboard contains: {result[:200]}..." if len(result) > 200 else f"Clipboard contains: {result}"
    except:
        pass
    
    return "Could not read clipboard."

# ============================================================
# PROCESS MANAGEMENT
# ============================================================

def kill_process(process_name: str):
    """Kills a process by name."""
    print(f"{Fore.RED}[ARCH] Killing {process_name}...{Style.RESET_ALL}")
    try:
        subprocess.run(["pkill", "-f", process_name], check=True)
        return f"Killed {process_name}."
    except subprocess.CalledProcessError:
        return f"No process named {process_name} found."
    except Exception as e:
        return f"Could not kill {process_name}: {e}"

def force_kill_process(process_name: str):
    """Force kills a process."""
    print(f"{Fore.RED}[ARCH] Force killing {process_name}...{Style.RESET_ALL}")
    try:
        subprocess.run(["pkill", "-9", "-f", process_name])
        return f"Force killed {process_name}."
    except Exception as e:
        return f"Could not kill {process_name}: {e}"

# ============================================================
# FILE MANAGER
# ============================================================

def open_file_manager(path: str = None):
    """Opens the file manager."""
    import os
    
    if not path:
        path = os.path.expanduser("~")
    
    print(f"{Fore.CYAN}[ARCH] Opening file manager at {path}...{Style.RESET_ALL}")
    
    # Try different file managers
    managers = ["nautilus", "dolphin", "thunar", "pcmanfm", "nemo", "caja", "xdg-open"]
    
    for fm in managers:
        if shutil.which(fm):
            subprocess.Popen([fm, path])
            return f"Opening file manager at {path}."
    
    return "No file manager found."

def open_downloads():
    """Opens the Downloads folder."""
    import os
    return open_file_manager(os.path.expanduser("~/Downloads"))

def open_documents():
    """Opens the Documents folder."""
    import os
    return open_file_manager(os.path.expanduser("~/Documents"))

# ============================================================
# UPTIME & TIME
# ============================================================

def get_uptime():
    """Returns system uptime."""
    try:
        uptime_seconds = psutil.boot_time()
        import time
        boot_time = time.time() - uptime_seconds
        
        # Calculate days, hours, minutes
        days = int(boot_time // 86400)
        hours = int((boot_time % 86400) // 3600)
        minutes = int((boot_time % 3600) // 60)
        
        if days > 0:
            return f"System has been running for {days} days, {hours} hours, and {minutes} minutes."
        elif hours > 0:
            return f"System has been running for {hours} hours and {minutes} minutes."
        else:
            return f"System has been running for {minutes} minutes."
    except Exception as e:
        return f"Could not get uptime: {e}"

def get_current_time():
    """Returns current time."""
    from datetime import datetime
    now = datetime.now()
    return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."

# ============================================================
# TIMER & REMINDERS
# ============================================================

def set_timer(minutes: int = 5, message: str = "Timer finished!"):
    """Sets a timer that sends a notification."""
    print(f"{Fore.CYAN}[ARCH] Setting timer for {minutes} minutes...{Style.RESET_ALL}")
    
    # Use sleep and notify-send in background
    cmd = f"sleep {minutes * 60} && notify-send 'A1 Timer' '{message}' && paplay /usr/share/sounds/freedesktop/stereo/complete.oga"
    subprocess.Popen(cmd, shell=True)
    
    return f"Timer set for {minutes} minutes. I'll notify you when it's done."

# ============================================================
# MEDIA CONTROLS (MPRIS)
# ============================================================

def media_play_pause():
    """Toggles play/pause for media."""
    print(f"{Fore.CYAN}[ARCH] Toggling media playback...{Style.RESET_ALL}")
    try:
        subprocess.run(["playerctl", "play-pause"], check=True)
        return "Media play/pause toggled."
    except FileNotFoundError:
        return "playerctl not found. Install it: yay -S playerctl"
    except Exception as e:
        return f"No active media player found."

def media_next():
    """Skips to next track."""
    try:
        subprocess.run(["playerctl", "next"], check=True)
        return "Skipped to next track."
    except:
        return "No active media player or playerctl not installed."

def media_previous():
    """Goes to previous track."""
    try:
        subprocess.run(["playerctl", "previous"], check=True)
        return "Went to previous track."
    except:
        return "No active media player or playerctl not installed."

def media_stop():
    """Stops media playback."""
    try:
        subprocess.run(["playerctl", "stop"], check=True)
        return "Media stopped."
    except:
        return "No active media player."

# ============================================================
# POWER PROFILES
# ============================================================

def set_power_profile(profile: str = "balanced"):
    """Sets power profile (performance/balanced/power-saver)."""
    print(f"{Fore.CYAN}[ARCH] Setting power profile to {profile}...{Style.RESET_ALL}")
    
    # Try power-profiles-daemon
    if shutil.which("powerprofilesctl"):
        try:
            subprocess.run(["powerprofilesctl", "set", profile], check=True)
            return f"Power profile set to {profile}."
        except Exception as e:
            return f"Could not set profile: {e}"
    
    # Try TLP
    if shutil.which("tlp"):
        if profile == "performance":
            subprocess.run(["sudo", "tlp", "ac"])
            return "Switched to AC (performance) mode."
        else:
            subprocess.run(["sudo", "tlp", "bat"])
            return "Switched to battery (power-saver) mode."
    
    return "No power management tool found (power-profiles-daemon or tlp)."

def get_power_profile():
    """Gets current power profile."""
    if shutil.which("powerprofilesctl"):
        try:
            result = subprocess.check_output(["powerprofilesctl", "get"]).decode().strip()
            return f"Current power profile: {result}"
        except:
            pass
    return "Could not get power profile."

# ============================================================
# QUICK TEST
# ============================================================

if __name__ == "__main__":
    print("Testing Arch Control...")
    print(get_full_system_status())
    print(wifi_status())
    print(bluetooth_status())
    print(get_uptime())
    print(get_current_time())
