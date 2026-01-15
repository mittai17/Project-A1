from faster_whisper import WhisperModel
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
from colorama import Fore, Style
import sys

# Configuration
MODEL_SIZE = "small.en" # 'tiny.en', 'small.en', 'base.en', 'medium.en'
COMPUTE_TYPE = "float16" # 'float16' for GPU, 'int8' for CPU
DEVICE = "cuda" # 'cuda' or 'cpu'. Auto-fallback handled below.

class Ear:
    def __init__(self):
        print(f"{Fore.YELLOW}[WHISPER] Loading model '{MODEL_SIZE}'...{Style.RESET_ALL}")
        try:
            self.model = WhisperModel(MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
            print(f"{Fore.GREEN}[WHISPER] Model loaded on {DEVICE}.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[WHISPER WARNING] GPU failed ({e}). Fallback to CPU/INT8.{Style.RESET_ALL}")
            self.model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

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
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while True:
                # Check global timeout (if nothing ever spoken)
                if not has_spoken and (time.time() - recording_start > timeout):
                    return None
                
                # Read audio chunk
                data, overflow = stream.read(1024)
                audio_chunk = data.flatten()
                audio_buffer.append(audio_chunk)
                
                # Calculate volume
                volume = np.linalg.norm(audio_chunk) / len(audio_chunk)
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
        
        # Transcribe
        print(f"\n{Fore.CYAN}[WHISPER] Transcribing...{Style.RESET_ALL}")
        
        # Save temp file (FasterWhisper requires file or complex generator)
        full_audio = np.concatenate(audio_buffer)
        wav.write("temp_command.wav", SAMPLE_RATE, full_audio)
        
        segments, info = self.model.transcribe("temp_command.wav", beam_size=5)
        
        text = " ".join([segment.text for segment in segments]).strip()
        os.remove("temp_command.wav")
        
        if text:
            print(f"{Fore.MAGENTA}[USER]: {text}{Style.RESET_ALL}")
            return text
        return None

if __name__ == "__main__":
    ear = Ear()
    res = ear.listen()
    print(res)
