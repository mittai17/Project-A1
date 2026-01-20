import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from colorama import Fore, Style
import sys
import torch

# Configuration
# 'base' is a good balance. 'small' or 'medium' for better accuracy but slower.
MODEL_SIZE = "medium.en" 

class Ear:
    def __init__(self):
        print(f"{Fore.YELLOW}[WHISPER] Loading model '{MODEL_SIZE}'...{Style.RESET_ALL}")
        try:
            # Check for CUDA
            device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"{Fore.BLUE}[WHISPER] Using device: {device}{Style.RESET_ALL}")
            
            self.model = whisper.load_model(MODEL_SIZE, device=device)
            print(f"{Fore.GREEN}[WHISPER] Model loaded.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[WHISPER ERROR] Failed to load model: {e}{Style.RESET_ALL}")
            sys.exit(1)

    def listen(self, timeout=8):
        """
        Records audio until silence is detected, then transcribes.
        """
        SAMPLE_RATE = 16000
        THRESHOLD = 500  # Silence threshold (adjust based on mic)
        SILENCE_LIMIT = 2.0  # Seconds of silence to stop recording
        
        print(f"{Fore.BLUE}[WHISPER] Listening...{Style.RESET_ALL}")
        
        audio_buffer = []
        silence_start = time.time()
        recording_start = time.time()
        has_spoken = False
        
        # 1. Record
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while True:
                # Global timeout check
                if not has_spoken and (time.time() - recording_start > timeout):
                    return None
                
                # Read audio chunk
                data, overflow = stream.read(1024)
                audio_chunk = data.flatten()
                audio_buffer.append(audio_chunk)
                
                # Calculate volume for VAD (Voice Activity Detection)
                volume = np.linalg.norm(audio_chunk) / len(audio_chunk)
                
                # Visual Feedback
                bars = "█" * int(volume // 50)
                sys.stdout.write(f"\r{Fore.CYAN}[REC] {bars:<10} {Style.RESET_ALL}")
                sys.stdout.flush()

                # VAD Logic
                if volume > THRESHOLD:
                    silence_start = time.time()
                    has_spoken = True
                else:
                    if has_spoken and (time.time() - silence_start > SILENCE_LIMIT):
                        break # Stop recording
        
        # 2. Transcribe
        print(f"\n{Fore.CYAN}[WHISPER] Transcribing...{Style.RESET_ALL}")
        
        # Save temp file
        full_audio = np.concatenate(audio_buffer)
        wav.write("temp_command.wav", SAMPLE_RATE, full_audio)
        
        try:
            # Method A: Language-Model Biasing (Contextual Priming)
            # We provide a prompt with common vocabulary to bias the decoder towards correct system commands.
            # This fixes "fire" vs "firefox" and improves accuracy for technical terms.
            system_context = "A1 system commands. Linux Arch. Keywords: open firefox, google chrome, vs code, terminal, alacritty, kitty, hyprland, wayland, update system, pacman, yay, install, search weather, news, python, code, script, github, clone, push, pull."
            
            # OpenAI Whisper Transcribe with Context
            result = self.model.transcribe("temp_command.wav", fp16=False, initial_prompt=system_context)
            text = result["text"].strip()
            
            # Clean up
            if os.path.exists("temp_command.wav"):
                os.remove("temp_command.wav")
            
            if text:
                print(f"{Fore.MAGENTA}[USER]: {text}{Style.RESET_ALL}")
                return text
                
        except Exception as e:
            print(f"{Fore.RED}[WHISPER ERROR] Transcription failed: {e}{Style.RESET_ALL}")
            return None
            
        return None

if __name__ == "__main__":
    ear = Ear()
    res = ear.listen()
    print(res)
