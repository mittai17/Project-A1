import json
import vosk
import sounddevice as sd
import sys
import queue
import numpy as np
import noisereduce as nr
import time
from colorama import Fore, Style

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

def listen_for_command(vosk_model, timeout=10):
    """
    Listens for a command.
    """
    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    try:
        rec = vosk.KaldiRecognizer(vosk_model, 16000)
        
        # Use int16 directly for Vosk (Simpler, less latency)
        with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                               channels=1, callback=callback):
            
            start_time = time.time()
            print(f"{Fore.CYAN}[LISTEN] Listening...{Style.RESET_ALL}")
            
            while True:
                # Check for GUI Input (Text)
                import os
                if os.path.exists("gui_input.txt"):
                    try:
                        with open("gui_input.txt", "r") as f:
                            text = f.read().strip()
                        os.remove("gui_input.txt")
                        if text:
                            print(f"{Fore.GREEN}        [GUI INPUT]: {text}{Style.RESET_ALL}")
                            return text
                    except:
                        pass

                if time.time() - start_time > timeout:
                    return None
                
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = res.get("text", "")
                        if text:
                            print(f"{Fore.GREEN}        [USER]: {text}{Style.RESET_ALL}")
                            # Update Overlay Final
                            try:
                                from core.overlay import get_overlay
                                get_overlay().update_captions(user_text=text)
                            except: pass
                            return text
                    else:
                        # Partial Result (Debug)
                        partial = json.loads(rec.PartialResult())
                        if partial.get("partial"):
                             p_text = partial['partial']
                             sys.stdout.write(f"\r{Fore.BLUE}[PARTIAL]: {p_text}{Style.RESET_ALL}")
                             sys.stdout.flush()
                             # Update Overlay Partial
                             try:
                                from core.overlay import get_overlay
                                get_overlay().update_captions(user_text=p_text)
                             except: pass
                             
                             # Reset timeout on activity
                             start_time = time.time()

    except Exception as e:
        print(f"{Fore.RED}[LISTEN ERROR] {e}{Style.RESET_ALL}")
    
    return None
