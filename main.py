import os
import sys
import vosk
import sounddevice as sd
from colorama import init, Fore, Style

# Initialize colorama
init()

# Import core modules
# ... imports ...
try:
    from core import wake, listen, listen_whisper, brain, speak, router, vision, adaptive_asr
    from skills import app_control, web, arch, foss
except ImportError as e:
    print(f"{Fore.RED}Error importing modules: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Configuration
MODEL_PATH = "models/vosk-model-small-en-us-0.15"

def check_model():
    if not os.path.exists(MODEL_PATH):
        print(f"{Fore.RED}[ERROR] Model not found at {MODEL_PATH}{Style.RESET_ALL}")
        print("Please download 'vosk-model-small-en-us-0.15' and unpack it in the 'models/' directory.")
        print("Download link: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        sys.exit(1)
    return vosk.Model(MODEL_PATH)

def main():
    print(f"{Fore.CYAN}========================================")
    print(f"       A1 VOICE ASSISTANT v1.0")
    print(f"========================================{Style.RESET_ALL}")

    # 1. Load Model (Vosk Wake Word)
    print(f"{Fore.YELLOW}[SYSTEM] Loading Vosk (Wake Word)...{Style.RESET_ALL}")
    try:
        vosk_model = check_model()
    except Exception as e:
        print(f"{Fore.RED}[SYSTEM] Failed to load Vosk: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # 2. Check Audio
    try:
        sd.query_devices(kind='input')
        print(f"{Fore.GREEN}[SYSTEM] Audio input devices found.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[SYSTEM] No audio input found: {e}{Style.RESET_ALL}")
        sys.exit(1)

    # 3. Initialize Whisper (Ear)
    # ear = listen_whisper.Ear()
    print(f"{Fore.YELLOW}[SYSTEM] Initializing Adaptive AI Ear...{Style.RESET_ALL}")
    ear = adaptive_asr.AdaptiveEar()

    # 4. Startup Sound
    speak.speak("A one online. High-Accuracy Mode.")

    # 4. Main Loop
    while True:
        try:
            # Wait for wake word (Vosk)
            if wake.listen_for_wake_word(vosk_model):
                # Continuous Conversation Mode
                next_command = speak.speak("Listening.", vosk_model)
                
                while True:
                    # Check if we already have a command from interruption
                    if next_command:
                        command = next_command
                        next_command = None
                        print(f"{Fore.MAGENTA}[CHAINED COMMAND]: {command}{Style.RESET_ALL}")
                    else:
                        # Listen for command (Whisper)
                        command = ear.listen(timeout=8)
                    
                    if command:
                        # Route
                        route = router.route_query(command)
                        intent = route["intent"]
                        args = route["args"]
                        
                        response = ""
                        
                        if intent == "app_open":
                            response = app_control.open_app(args)
                        elif intent == "app_close":
                            response = app_control.close_app(args)
                        elif intent == "app_focus":
                            response = app_control.focus_app(args)
                        elif intent == "web_search":
                            speak.speak(f"Searching for {args}...", vosk_model)
                            summary = web.search_web(args)
                            # Ask brain to summarize the search result safely
                            response = brain.think(f"Summarize this search result for the user query '{args}': {summary}")
                        elif intent == "arch_update":
                            response = arch.update_system()
                        elif intent == "arch_install":
                            response = arch.install_package(args)
                        elif intent == "system_stats":
                            response = arch.get_system_stats()
                        elif intent == "foss_search":
                            speak.speak(f"Searching GitHub for {args}...", vosk_model)
                            response = foss.find_opensource(args)
                        elif intent == "vision_query":
                            speak.speak("Checking screen...", vosk_model)
                            response = vision.analyze_screen(args)
                        else:
                            # Conversation
                            response = brain.think(args)
                            
                        # Speak response
                        speak.speak(response, vosk_model)
                        
                        # Go back to Sleep (break inner loop) to wait for Wake Word again
                        # This prevents the system from staying open and timing out constantly
                        # logic: Wake -> Listen -> Act -> Sleep
                        next_command = None 
                        break
                    else:
                        print(f"{Fore.YELLOW}[SYSTEM] Timeout.{Style.RESET_ALL}")
                        speak.speak("Offline.")
                        break

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[SYSTEM] Stopping...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Critical Loop Error: {e}{Style.RESET_ALL}")
            speak.speak("System error.")

if __name__ == "__main__":
    main()
