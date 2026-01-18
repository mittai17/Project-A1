import subprocess
import os
import sys
import time
import queue
import sounddevice as sd
import vosk
import json
from colorama import Fore, Style

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODEL_PATH = os.path.join(BASE_DIR, "piper", "voice_te.onnx")

def speak(text, vosk_model=None):
    """
    Speaks text using Piper Neural TTS (High Quality, Offline).
    Supports 'barge-in' interruption.
    Falls back to Piper binary which must be present in A1/piper/.
    """
    if not text:
        return None

    # Clean text
    text_clean = text.replace("*", "").replace("#", "").replace("`", "").strip()
    print(f"{Fore.GREEN}[A1]: {text_clean}{Style.RESET_ALL}")

    if not os.path.exists(PIPER_BIN) or not os.path.exists(MODEL_PATH):
        print(f"{Fore.RED}[TTS ERROR] Piper or Model not found at {PIPER_BIN}{Style.RESET_ALL}")
        return None

    # Pipeline: echo "text" | piper ... | aplay ...
    # We use aplay for raw PCM streaming (low latency)
    
    # 22050Hz is standard for 'medium' quality models in Piper
    # Ensure aplay is installed (usually is on Linux)
    aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"]
    piper_cmd = [PIPER_BIN, "--model", MODEL_PATH, "--output_raw"]
    
    try:
        # Start the pipeline
        p_echo = subprocess.Popen(["echo", text_clean], stdout=subprocess.PIPE)
        p_piper = subprocess.Popen(piper_cmd, stdin=p_echo.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if p_echo.stdout:
            p_echo.stdout.close() 
        
        # We start aplay independently to be able to kill it easily
        p_aplay = subprocess.Popen(aplay_cmd, stdin=p_piper.stdout, stderr=subprocess.DEVNULL)
        if p_piper.stdout:
            p_piper.stdout.close()

        # --- INTERRUPTION MONITORING ---
        if not vosk_model:
            p_aplay.wait()
            return None

        # Queue for mic data
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        # Words that trigger immediate stop
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
                        if any(w in t for w in trigger_words):
                            print(f"{Fore.YELLOW}[INTERRUPT] Heard: '{t}'{Style.RESET_ALL}")
                            p_aplay.kill()
                            p_piper.kill()
                            return t
                time.sleep(0.01)
                
    except Exception as e:
        print(f"{Fore.RED}[TTS ERROR] {e}{Style.RESET_ALL}")

    return None

if __name__ == "__main__":
    speak("System online. Neural voice active.")
