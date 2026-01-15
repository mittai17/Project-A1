import subprocess
import os
import sys
import time
import queue
import sounddevice as sd
import vosk
import json
from colorama import Fore, Style

# Configuration
USE_PIPER = False 

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODEL_PATH = os.path.join(BASE_DIR, "piper", "voice.onnx")

def speak(text, vosk_model=None):
    """
    Speaks text using Piper Neural TTS (High Quality, Offline).
    Supports 'barge-in' interruption.
    """
    if not text:
        return None

    # Clean text (remove markdown asterisks which pipeline might read literally)
    text_clean = text.replace("*", "").replace("#", "").replace("`", "").strip()
    print(f"{Fore.GREEN}[A1]: {text_clean}{Style.RESET_ALL}")

    if not os.path.exists(PIPER_BIN) or not os.path.exists(MODEL_PATH):
        print(f"{Fore.RED}[TTS ERROR] Piper or Model not found at {PIPER_BIN}{Style.RESET_ALL}")
        return None

    # Pipeline: echo "text" | piper ... | aplay ...
    # We use aplay for raw PCM streaming (low latency)
    
    # 1. Prepare Command
    # 22050Hz is standard for 'medium' quality models in Piper
    aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"]
    piper_cmd = [PIPER_BIN, "--model", MODEL_PATH, "--output_raw"]
    
    try:
        # Start the pipeline
        p_echo = subprocess.Popen(["echo", text_clean], stdout=subprocess.PIPE)
        p_piper = subprocess.Popen(piper_cmd, stdin=p_echo.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        p_echo.stdout.close() # Allow p_echo to receive SIGPIPE if p_piper exits
        
        # We start aplay independently to be able to kill it easily
        p_aplay = subprocess.Popen(aplay_cmd, stdin=p_piper.stdout, stderr=subprocess.DEVNULL)
        p_piper.stdout.close() # Allow p_piper to receive SIGPIPE if p_aplay exits

        # --- INTERRUPTION MONITORING ---
        if not vosk_model:
            p_aplay.wait()
            return None

        # Custom interruption logic
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        # Words that trigger immediate stop
        # "wait", "A1", "stop", "change"
        trigger_words = ["stop", "cancel", "wait", "change", "hey"]
        
        rec = vosk.KaldiRecognizer(vosk_model, 16000)

        with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                               channels=1, callback=callback):
            
            while p_aplay.poll() is None:
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        t = res.get("text", "")
                        if any(w in t for w in trigger_words) or len(t) > 10:
                            print(f"{Fore.YELLOW}[INTERRUPT] Heard: '{t}'{Style.RESET_ALL}")
                            p_aplay.kill()
                            p_piper.kill()
                            return t
                    else:
                        # Partial check for faster reaction
                        # partial = json.loads(rec.PartialResult())
                        # pt = partial.get("partial", "")
                        # if "stop" in pt: 
                        #    p_aplay.kill(); return "stop"
                        pass
                time.sleep(0.01)
                
    except Exception as e:
        print(f"{Fore.RED}[TTS ERROR] {e}{Style.RESET_ALL}")

    return None

if __name__ == "__main__":
    speak("System online. Neural voice active.")
