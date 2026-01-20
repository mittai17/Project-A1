import torch
import torchaudio

# Monkey-patch torchaudio for compatibility with SpeechBrain on newer versions
if not hasattr(torchaudio, "list_audio_backends"):
    torchaudio.list_audio_backends = lambda: ["soundfile"] 

from speechbrain.inference.speaker import EncoderClassifier
import os
import numpy as np
from colorama import Fore, Style

class SpeakerEncoder:
    def __init__(self, savedir=None):
        """
        Initialize the SpeakerEncoder with ECAPA-TDNN.
        """
        if savedir is None:
            # Default to a models directory in the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            savedir = os.path.join(base_dir, "models", "speaker_encoder")
            
        print(f"{Fore.CYAN}[SPEAKER] Loading ECAPA-TDNN model...{Style.RESET_ALL}")
        
        # Force CPU for lightweight usage if requested, but check availability
        # User requested CPU-friendly. 
        self.device = "cpu" 
        
        try:
            self.classifier = EncoderClassifier.from_hparams(
                source="speechbrain/spkrec-ecapa-voxceleb",
                savedir=savedir,
                run_opts={"device": self.device}
            )
            print(f"{Fore.GREEN}[SPEAKER] Model loaded successfully.{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}[SPEAKER ERROR] Could not load model: {e}{Style.RESET_ALL}")
            raise e

    def embed_file(self, wav_path):
        """
        Extract speaker embedding from a WAV file.
        Returns: numpy array
        """
        try:
            # Load audio
            signal, fs = torchaudio.load(wav_path)
            
            # Resample if necessary (ECAPA-TDNN expects 16k)
            if fs != 16000:
                resampler = torchaudio.transforms.Resample(fs, 16000)
                signal = resampler(signal)
            
            # Move to device
            signal = signal.to(self.device)
            
            # Extract embedding
            # encode_batch returns [batch, 1, embedding_dim]
            embeddings = self.classifier.encode_batch(signal)
            
            # Squeeze and convert to numpy
            return embeddings.squeeze().cpu().detach().numpy()
            
        except Exception as e:
            print(f"{Fore.RED}[SPEAKER ERROR] Extraction failed: {e}{Style.RESET_ALL}")
            return None

    def compute_similarity(self, embed1, embed2):
        """
        Compute Cosine Similarity between two embeddings.
        Returns: float score (-1.0 to 1.0)
        """
        if embed1 is None or embed2 is None:
            return 0.0
            
        # Ensure tensors
        t1 = torch.tensor(embed1).to(self.device)
        t2 = torch.tensor(embed2).to(self.device)
        
        score = torch.nn.functional.cosine_similarity(t1, t2, dim=0)
        return score.item()

    def update_listing_embedding(self, current_avg, new_embedding, alpha=0.1):
        """
        Update the running average of the user's embedding.
        alpha: Weight of the new embedding (default 0.1 for slow adaptation)
        """
        if current_avg is None:
            return new_embedding
            
        # Simple weighted average
        updated = (1 - alpha) * current_avg + alpha * new_embedding
        
        # Normalize (important for cosine similarity)
        norm = np.linalg.norm(updated)
        if norm > 0:
            updated = updated / norm
            
        return updated
