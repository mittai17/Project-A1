import json
import vosk
import sounddevice as sd
import sys
from colorama import Fore, Style

SAMPLE_RATE = 16000
BLOCK_SIZE = 8000

def listen_for_command(model, input_device_index=None, timeout=10):
    """
    Listens for a single command.
    Returns the recognized text or None if no command heard/timeout.
    """
    rec = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    
    print(f"{Fore.BLUE}[LISTEN] Listening for command...{Style.RESET_ALL}")
    
    # Timeout logic: Silence for 'timeout' seconds ends the listening session
    import time
    last_activity = time.time()
    
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=BLOCK_SIZE, device=input_device_index, dtype='int16',
                           channels=1, callback=None) as stream:
        
        while True:
            # Check timeout
            if time.time() - last_activity > timeout:
                return None

            data, overflowed = stream.read(BLOCK_SIZE)
            if overflowed:
                pass
            
            if rec.AcceptWaveform(bytes(data)):
                res = json.loads(rec.Result())
                text = res.get("text", "").strip()
                if text:
                    sys.stdout.write("\r" + " " * 80 + "\r")
                    print(f"{Fore.MAGENTA}[USER]: {text}{Style.RESET_ALL}")
                    return text
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "").strip()
                if partial_text:
                     # Update activity if hearing something
                     last_activity = time.time()
                     sys.stdout.write(f"\r{Fore.BLUE}[HEARING]: {partial_text}{Style.RESET_ALL}")
                     sys.stdout.flush()
