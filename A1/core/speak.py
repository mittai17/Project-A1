import subprocess
import os
import sys
import time
import queue
import sounddevice as sd
import vosk
import json
import torch
import torchaudio
import numpy as np
from colorama import Fore, Style
import re
import soundfile as sf

# Try to import TTS (XTTS v2)
try:
    from TTS.api import TTS
    XTTS_AVAILABLE = True
except ImportError:
    XTTS_AVAILABLE = False
    print(f"{Fore.YELLOW}[WARNING] Coqui TTS not installed. XTTS v2 disabled.{Style.RESET_ALL}")

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPER_BIN = os.path.join(BASE_DIR, "piper", "piper")
MODELS_DIR = os.path.join(BASE_DIR, "models")
SPEAKER_WAV = os.path.join(MODELS_DIR, "speaker.wav")
TEMP_AUDIO_PATH = os.path.join(MODELS_DIR, "temp_output.wav")

# Multi-Voice Configuration
VOICES = {
    "en": os.path.join(BASE_DIR, "piper", "voice.onnx"),
    "ta": os.path.join(BASE_DIR, "piper", "voice_te.onnx")
}

# Global XTTS Model Holder
xtts_model = None

def detect_language(text):
    """
    Returns 'ta' if Tamil characters are found, else 'en'.
    Tamil Unicode Range: 0B80–0BFF
    """
    if re.search(r'[\u0b80-\u0bff]', text):
        return "ta"
    return "en"

def load_xtts():
    global xtts_model
    if not XTTS_AVAILABLE:
        return None
        
    if xtts_model is None:
        print(f"{Fore.CYAN}[XTTS] Loading Neural Model (v2)... This may take a moment.{Style.RESET_ALL}")
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            # Using the official XTTS v2 model
            xtts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
            print(f"{Fore.GREEN}[XTTS] Model Online ({device.upper()}).{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[XTTS ERROR] Failed to load model: {e}{Style.RESET_ALL}")
            xtts_model = None
    return xtts_model

def play_audio_numpy(audio_data, sample_rate, vosk_model=None):
    """
    Plays audio data (numpy array) and handles interruption.
    """
    if audio_data is None or len(audio_data) == 0:
        return None

    duration = len(audio_data) / sample_rate
    
    # Start playback
    sd.play(audio_data, sample_rate)
    
    start_time = time.time()
    
    # If no interruption handling needed
    if not vosk_model:
        sd.wait()
        return None

    # Interruption Loop
    q = queue.Queue()
    def callback(indata, frames, time, status):
        q.put(bytes(indata))

    trigger_words = ["stop", "cancel", "wait", "change", "hey"]
    rec = vosk.KaldiRecognizer(vosk_model, 16000)

    try:
        with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                               channels=1, callback=callback):
            
            while (time.time() - start_time) < duration:
                # Check for active playback
                if not sd.get_stream().active:
                    break
                    
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        t = res.get("text", "")
                        if any(w in t for w in trigger_words):
                            print(f"{Fore.YELLOW}[INTERRUPT] Heard: '{t}'{Style.RESET_ALL}")
                            sd.stop()
                            return t
                time.sleep(0.05)
                
    except Exception as e:
        print(f"{Fore.RED}[PLAYBACK ERROR] {e}{Style.RESET_ALL}")
        sd.stop()
    
    return None

def speak(text, vosk_model=None):
    """
    Speaks text using XTTS v2 (English) or Piper (Tamil/Fallback).
    """
    if not text:
        return None

    text_clean = text.replace("*", "").replace("#", "").replace("`", "").strip()
    lang = detect_language(text_clean)
    
    lang_name = "TAMIL" if lang == "ta" else "ENGLISH"
    print(f"{Fore.GREEN}[A1 ({lang_name})]: {text_clean}{Style.RESET_ALL}")

    # --- STRATEGY: XTTS v2 for English ---
    if lang == "en" and XTTS_AVAILABLE:
        # Check for speaker reference
        if not os.path.exists(SPEAKER_WAV):
            print(f"{Fore.YELLOW}[XTTS] 'models/speaker.wav' not found. Creating default reference...{Style.RESET_ALL}")
            # Try to find ANY wav file to use as temporary reference or fallback to Piper
            # For now, we fallback to Piper if no speaker wav
            pass 
        else:
            model = load_xtts()
            if model:
                try:
                    # Generate to file (XTTS works best this way compared to pure stream)
                    # We can use tts_to_file
                    model.tts_to_file(
                        text=text_clean,
                        file_path=TEMP_AUDIO_PATH,
                        speaker_wav=SPEAKER_WAV,
                        language="en"
                    )
                    
                    # Load and play
                    data, samplerate = sf.read(TEMP_AUDIO_PATH)
                    return play_audio_numpy(data, samplerate, vosk_model)
                    
                except Exception as e:
                    print(f"{Fore.RED}[XTTS FAIL] {e}. Falling back to Piper.{Style.RESET_ALL}")

    # --- FALLBACK / TAMIL: Piper TTS ---
    # (Original Logic Modified)
    
    model_path = VOICES.get(lang, VOICES["en"])
    if not os.path.exists(model_path):
        # Last resort fallback if piper models missing
        if lang == "en" and not os.path.exists(PIPER_BIN):
             # Just print if no audio engine available
             print(f"{Fore.RED}[TTS] No TTS engine available.{Style.RESET_ALL}")
             return None

    # ... Piper Subprocess Logic ...
    if not os.path.exists(PIPER_BIN) or not os.path.exists(model_path):
        return None

    aplay_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"]
    speed = "1.2" if lang == "ta" else "1.0"
    
    pipeline_cmd = [
        PIPER_BIN, 
        "--model", model_path, 
        "--output_raw", 
        "--length_scale", speed,
        "--sentence_silence", "0.2"
    ]
    
    try:
        p_echo = subprocess.Popen(["echo", text_clean], stdout=subprocess.PIPE)
        p_piper = subprocess.Popen(pipeline_cmd, stdin=p_echo.stdout, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        if p_echo.stdout: p_echo.stdout.close() 
        
        p_aplay = subprocess.Popen(aplay_cmd, stdin=p_piper.stdout, stderr=subprocess.DEVNULL)
        if p_piper.stdout: p_piper.stdout.close()

        # Monitor Piper Playback
        if not vosk_model:
            p_aplay.wait()
            return None

        # Interruption logic for Piper (Process based)
        q = queue.Queue()
        def callback(indata, frames, time, status):
            q.put(bytes(indata))

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
        print(f"{Fore.RED}[PIPER ERROR] {e}{Style.RESET_ALL}")

    return None

if __name__ == "__main__":
    # Test
    speak("System Check. XTTS capability enabled.")
