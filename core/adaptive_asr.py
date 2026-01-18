import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import os
import time
import json
import sys
import torch
from colorama import Fore, Style

# Import core modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.speaker_embed import SpeakerEncoder

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "voice_config.json")

class AdaptiveEar:
    def __init__(self, model_size="small"):
        self.config = self._load_config()
        self.model_size = model_size
        
        print(f"{Fore.YELLOW}[ADAPTIVE] Loading Whisper '{model_size}' + Speaker Encoder...{Style.RESET_ALL}")
        
        # Load Whisper
        # Load Whisper (Force CPU to save VRAM for Llama 3.1)
        device = "cpu"
        self.asr_model = whisper.load_model(model_size, device=device)
        
        # Load Speaker Encoder
        self.speaker_encoder = SpeakerEncoder()
        
        # Load User Profile
        self.profile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                       self.config.get("enrollment_file", "user_profile.npy"))
        self.user_embedding = self._load_profile()
        
        # Adaptation params
        self.similarity_threshold = self.config.get("similarity_threshold", 0.25)
        self.adaptation_rate = self.config.get("adaptation_rate", 0.05)
        
        print(f"{Fore.GREEN}[ADAPTIVE] System Ready.{Style.RESET_ALL}")

    def _load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def _load_profile(self):
        if os.path.exists(self.profile_path):
            try:
                emb = np.load(self.profile_path)
                print(f"{Fore.BLUE}[ADAPTIVE] User profile loaded.{Style.RESET_ALL}")
                return emb
            except Exception as e:
                print(f"{Fore.RED}[ADAPTIVE] Failed to load profile: {e}{Style.RESET_ALL}")
        return None

    def listen(self, timeout=10):
        """
        Record and Transcribe with Speaker Adaptation.
        """
        SAMPLE_RATE = 16000
        THRESHOLD = 300  # More sensitive mic
        SILENCE_LIMIT = 2.5 # Wait longer for user to finish thought
        
        print(f"{Fore.BLUE}[ADAPTIVE] Listening...{Style.RESET_ALL}")
        
        audio_buffer = []
        silence_start = time.time()
        recording_start = time.time()
        has_spoken = False
        
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16') as stream:
            while True:
                if not has_spoken and (time.time() - recording_start > timeout):
                    return None
                
                data, overflow = stream.read(1024)
                audio_chunk = data.flatten()
                audio_buffer.append(audio_chunk)
                
                volume = np.linalg.norm(audio_chunk) / len(audio_chunk)
                
                # feedback
                # bars = "█" * int(volume // 50)
                # sys.stdout.write(f"\r{Fore.CYAN}[REC] {bars:<10} {Style.RESET_ALL}")
                # sys.stdout.flush()

                if volume > THRESHOLD:
                    silence_start = time.time()
                    has_spoken = True
                else:
                    if has_spoken and (time.time() - silence_start > SILENCE_LIMIT):
                        break
        
        # Process Audio
        print(f"\n{Fore.CYAN}[ADAPTIVE] Processing...{Style.RESET_ALL}")
        full_audio = np.concatenate(audio_buffer)
        
        # Save temp for tool usage
        temp_file = "temp_adaptive.wav"
        wav.write(temp_file, SAMPLE_RATE, full_audio)
        
        user_identified = False
        similarity = 0.0
        
        # 1. Speaker Verification / Adaptation
        if self.user_embedding is not None:
            # Extract current embedding
            current_emb = self.speaker_encoder.embed_file(temp_file)
            
            if current_emb is not None:
                # Compare
                similarity = self.speaker_encoder.compute_similarity(current_emb, self.user_embedding)
                print(f"{Fore.MAGENTA}[ADAPTIVE] Speaker Similarity: {similarity:.4f}{Style.RESET_ALL}")
                
                if similarity > self.similarity_threshold:
                    user_identified = True
                    # Gradual Adaptation
                    self._update_profile(current_emb)

        # 2. Transcribe with Bias
        # Simplified prompt: Focus on VOCABULARY, not instructions.
        tanglish_vocab = "A1, pannu, seiyu, enna, irukku, open, close, update, system, terminal, firefox, code, install, weather, news."
        
        if user_identified:
            print(f"{Fore.GREEN}[ADAPTIVE] Verified. Using Tanglish bias.{Style.RESET_ALL}")
            prompt = f"Conversational Tamil English. Tanglish. Vocab: {tanglish_vocab}"
        else:
            print(f"{Fore.YELLOW}[ADAPTIVE] Standard Mode.{Style.RESET_ALL}")
            prompt = f"English. Vocab: {tanglish_vocab}"

        try:
            result = self.asr_model.transcribe(temp_file, fp16=False, initial_prompt=prompt)
            text = result["text"].strip()
            
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
            if text:
                prefix = f"{Fore.GREEN}[USER (Verified)]" if user_identified else f"{Fore.MAGENTA}[USER]"
                print(f"{prefix}: {text}{Style.RESET_ALL}")
                return text
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Transcription failed: {e}{Style.RESET_ALL}")
            
        return None

    def _update_profile(self, new_emb):
        """
        Mix new embedding into profile with low alpha.
        """
        try:
            self.user_embedding = self.speaker_encoder.update_listing_embedding(
                self.user_embedding, new_emb, alpha=self.adaptation_rate
            )
            # Save (maybe throttle this in production to avoid disk I/O every time)
            np.save(self.profile_path, self.user_embedding)
            # print(f"{Fore.BLACK}[DEBUG] Profile updated.{Style.RESET_ALL}")
        except Exception as e:
            print(f"Update failed: {e}")

if __name__ == "__main__":
    ear = AdaptiveEar(model_size="base.en")
    while True:
        ear.listen()
