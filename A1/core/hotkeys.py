from pynput import keyboard
from colorama import Fore, Style
import threading

class GlobalHotkeys:
    def __init__(self, toggle_callback):
        self.toggle_callback = toggle_callback
        self.listener = None

    def on_activate(self):
        print(f"{Fore.CYAN}[HOTKEY] Ctrl+Alt+A triggered.{Style.RESET_ALL}")
        if self.toggle_callback:
            self.toggle_callback()

    def start(self):
        # Hotkey definition: Ctrl+Alt+A to toggle
        try:
            hotkeys = {
                '<ctrl>+<alt>+a': self.on_activate
            }
            
            self.listener = keyboard.GlobalHotKeys(hotkeys)
            self.listener.start()
            print(f"{Fore.GREEN}[HOTKEYS] Listening for Ctrl+Alt+A...{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[HOTKEYS ERROR] Failed to bind: {e}{Style.RESET_ALL}")

    def stop(self):
        if self.listener:
            self.listener.stop()
