import sys
import os
import time
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import json
from colorama import Fore, Style

# Ensure we can import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.speaker_embed import SpeakerEncoder

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voice_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    return {}

def record_audio(duration=5, fs=16000):
    print(f"{Fore.CYAN}Recording for {duration} seconds...{Style.RESET_ALL}")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    return recording

def main():
    print(f"{Fore.GREEN}=== A1 Voice Enrollment ==={Style.RESET_ALL}")
    print("This script will create a speaker profile for Adaptive ASR.")
    print("We will record multiple samples of your voice to build a robust profile.")
    
    config = load_config()
    output_file = config.get("enrollment_file", "user_profile.npy")
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), output_file)
    
    # Initialize component
    try:
        encoder = SpeakerEncoder()
    except Exception as e:
        print(f"Failed to init encoder: {e}")
        return

    embeddings = []
    
    print(f"\n{Fore.YELLOW}Instructions:{Style.RESET_ALL}")
    print("1. Speak clearly and naturally.")
    print("2. Read random sentences or just talk about your day.")
    print("3. We need at least 5-10 good samples.")
    
    sample_count = 0
    
    try:
        while True:
            input(f"\n{Fore.MAGENTA}Press ENTER to record a 10-second sample (or Ctrl+C to finish)...{Style.RESET_ALL}")
            
            # Record
            duration = 10
            audio_data = record_audio(duration)
            
            # Save temp wav
            temp_wav = "temp_enroll.wav"
            wav.write(temp_wav, 16000, audio_data)
            
            # Extract
            print("Extracting embedding...")
            emb = encoder.embed_file(temp_wav)
            
            if emb is not None:
                embeddings.append(emb)
                sample_count += 1
                print(f"{Fore.GREEN}Sample {sample_count} captured.{Style.RESET_ALL}")
            
            # Cleanup
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            # Suggestion to continue
            if sample_count >= 5:
                print(f"{Fore.BLUE}Good amount of data collected. You can stop now or continue for better accuracy.{Style.RESET_ALL}")

    except KeyboardInterrupt:
        print("\nStopping enrollment...")
    
    if not embeddings:
        print(f"{Fore.RED}No samples collected. Exiting.{Style.RESET_ALL}")
        return

    # Average embeddings
    print(f"\nProcessing {len(embeddings)} samples...")
    # Stack: [N, 192] -> mean -> [192]
    # ECAPA-TDNN usually outputs 192-dim vectors
    
    mat = np.array(embeddings)
    mean_emb = np.mean(mat, axis=0)
    
    # Normalize
    norm = np.linalg.norm(mean_emb)
    if norm > 0:
        mean_emb = mean_emb / norm
        
    # Save
    np.save(output_path, mean_emb)
    print(f"{Fore.GREEN}Success! Profile saved to: {output_path}{Style.RESET_ALL}")
    print(f"Vector shape: {mean_emb.shape}")

if __name__ == "__main__":
    main()
