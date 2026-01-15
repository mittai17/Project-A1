import subprocess
import os
import sys
import time
import queue
import sounddevice as sd
import vosk
import json
import pyttsx3
from colorama import Fore, Style

# Configuration
USE_PIPER = False 

# Initialize Engine
try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150) # Faster for conversational feel
    
    # Attempt to find Indian English Key
    voices = engine.getProperty('voices')
    indian_voice_id = None
    for voice in voices:
        if "india" in voice.id.lower() or "en-in" in voice.id.lower():
            indian_voice_id = voice.id
            break
            
    if indian_voice_id:
        engine.setProperty('voice', indian_voice_id)
except:
    pass

def speak(text, vosk_model=None):
    """
    Speaks text with interruption support.
    If vosk_model is provided, listens for "stop/cancel" or wake word during playback to interrupt.
    """
    if not text:
        return

    print(f"{Fore.GREEN}[A1]: {text}{Style.RESET_ALL}")
    
    # File to save audio to
    output_file = "/tmp/a1_speech.wav"
    
    # 1. Generate Audio File
    try:
        # We use save_to_file to generate the WAV without playing it yet
        # This is fast for short sentences
        engine.save_to_file(text, output_file)
        engine.runAndWait()
    except Exception as e:
        print(f"{Fore.RED}[TTS ERROR] Generation failed: {e}{Style.RESET_ALL}")
        return

    # 2. Play and Monitor
    try:
        # Start playback in background
        player_process = subprocess.Popen(
            ["aplay", "-q", output_file],
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        # If no model, just wait
        if not vosk_model:
            player_process.wait()
            return

        # If model exists, monitor mic while playing
        q = queue.Queue()

        def callback(indata, frames, time, status):
            q.put(bytes(indata))

        # Custom interruption logic
        # High confidence interrupt words (safe to act on partials)
        strict_keywords = ["stop", "cancel", "shut", "silence", "enough", "terminate"]
        # Conversational interrupt words (wait for final result to concise)
        loose_keywords = ["wait", "wrong", "actually", "change", "hey a1"]
        
        rec = vosk.KaldiRecognizer(vosk_model, 16000)

        with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype='int16',
                               channels=1, callback=callback):
            while player_process.poll() is None:
                if not q.empty():
                    data = q.get()
                    if rec.AcceptWaveform(data):
                        res = json.loads(rec.Result())
                        text = res.get("text", "").lower()
                        
                        # logic: strict keyword or long sentence
                        if any(k in text for k in strict_keywords + loose_keywords) or len(text) > 20:
                            print(f"{Fore.YELLOW}[INTERRUPTED] User spoke: '{text}'{Style.RESET_ALL}")
                            player_process.kill()
                            return text
                    else:
                        partial = json.loads(rec.PartialResult())
                        p_text = partial.get("partial", "").lower()
                        
                        # Partial: Only strict keywords to avoid false positives
                        if any(k in p_text for k in strict_keywords):
                             print(f"{Fore.YELLOW}[INTERRUPTED] Detected '{p_text}'...{Style.RESET_ALL}")
                             player_process.kill()
                             return p_text
                time.sleep(0.01)

    except Exception as e:
        print(f"{Fore.RED}[TTS ERROR] Playback failed: {e}{Style.RESET_ALL}")
    
    return None

if __name__ == "__main__":
    speak("System online. Neural voice active.")
