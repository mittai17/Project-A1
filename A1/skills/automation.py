import subprocess
from colorama import Fore, Style

def type_text(text: str):
    """Types text using xdotool."""
    print(f"{Fore.CYAN}[AUTO] Typing: {text}{Style.RESET_ALL}")
    try:
        subprocess.run(["xdotool", "type", "--delay", "50", text], check=True)
        return "Typed text."
    except Exception as e:
        return f"Failed to type: {e}"

def press_key(key: str):
    """Presses a key or combo (e.g. 'Return', 'ctrl+c')."""
    print(f"{Fore.CYAN}[AUTO] Pressing: {key}{Style.RESET_ALL}")
    try:
        subprocess.run(["xdotool", "key", key], check=True)
        return f"Pressed {key}."
    except Exception as e:
        return f"Failed to press key: {e}"

def mouse_click(button: int = 1):
    """Clicks mouse button (1=Left, 3=Right)."""
    try:
        subprocess.run(["xdotool", "click", str(button)], check=True)
        return "Clicked mouse."
    except Exception as e:
        return f"Failed to click: {e}"

def send_notification(title: str, message: str):
    """Sends a desktop notification via DBus (notify-send)."""
    try:
        subprocess.run(["notify-send", title, message], check=True)
        return "Notification sent."
    except Exception as e:
        return f"Failed to notify: {e}"
