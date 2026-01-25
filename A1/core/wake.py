import json
import vosk
import sounddevice as sd
import sys
import os
from colorama import Fore, Style

# Tuning parameters
SAMPLE_RATE = 16000
BLOCK_SIZE = 8000
WAKE_PHRASES = [
    "hey a1", "hey a one", "hey anyone", "hey everyone", "hey one", "hey on", 
    "a1", "a one", "ay one", "anyone", "everyone",
    "computer", "system", "assistant", "listen", "wake up"
]

import numpy as np

def listen_for_wake_word(model, input_device_index=None):
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    
    print(f"{Fore.YELLOW}[WAKE] Listening... (Say 'A1' or 'Hey A1'){Style.RESET_ALL}")

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, device=input_device_index, dtype='int16',
                           channels=1, callback=None) as stream:
        
        while True:
            data, overflowed = stream.read(BLOCK_SIZE)
            
            # --- CHECK GUI INPUT ---
            if os.path.exists("gui_input.txt"):
                 try:
                     with open("gui_input.txt", "r") as f:
                         gui_text = f.read().strip()
                     os.remove("gui_input.txt")
                     if gui_text:
                         sys.stdout.write("\r" + " " * 80 + "\r")
                         print(f"{Fore.GREEN}[GUI INPUT]: {gui_text}{Style.RESET_ALL}")
                         return gui_text # Return text directly
                 except: pass

            # --- VU METER & DEBUG ---
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.linalg.norm(audio_data) / len(audio_data)
            bars = "█" * int(volume // 50)
            
            # Get partial for debug
            partial_check = ""
            if rec.AcceptWaveform(bytes(data)):
                res = json.loads(rec.Result())
                text = res.get("text", "").lower()
                # If we get a final result, check it immediately
                if any(phrase in text for phrase in WAKE_PHRASES):
                     sys.stdout.write("\r" + " " * 80 + "\r")
                     print(f"{Fore.GREEN}[WAKE] Wake word detected: '{text}'{Style.RESET_ALL}")
                     return True
            else:
                partial = json.loads(rec.PartialResult())
                partial_check = partial.get("partial", "").lower()
                if any(phrase in partial_check for phrase in WAKE_PHRASES):
                    rec.Reset()
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    print(f"{Fore.GREEN}[WAKE] Wake word detected (Partial): '{partial_check}'{Style.RESET_ALL}")
                    return True

            # Print Meter + What it hears
            debug_text = f"Heard: '{partial_check}'" if partial_check else "..."
            sys.stdout.write(f"\r{Fore.CYAN}[MIC] {bars:<10} {Style.DIM}{debug_text:<40}{Style.RESET_ALL}")
            sys.stdout.flush()
            # ------------------------
