import os
import sys
import signal
import atexit
import vosk
import sounddevice as sd
import time
from colorama import init, Fore, Style

# Initialize colorama
init()

# Import core modules
# ... imports ...
try:
    from core import wake, listen, listen_whisper, brain, speak, router, vision, adaptive_asr, overlay, memory, hotkeys
    from skills import app_control, web, arch, foss, weather, personal_assistant, news, automation
except ImportError as e:
    print(f"{Fore.RED}Error importing modules: {e}{Style.RESET_ALL}")
    sys.exit(1)

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "vosk-model-small-en-us-0.15")

def cleanup():
    """Clean up overlay when exiting"""
    print(f"\n{Fore.YELLOW}[SYSTEM] Cleaning up...{Style.RESET_ALL}")
    try:
        overlay.stop()
        print(f"{Fore.GREEN}[SYSTEM] Overlay stopped.{Style.RESET_ALL}")
    except:
        pass

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    cleanup()
    sys.exit(0)

# Register cleanup handlers
atexit.register(cleanup)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_model():
    if not os.path.exists(MODEL_PATH):
        print(f"{Fore.RED}[ERROR] Model not found at {MODEL_PATH}{Style.RESET_ALL}")
        print("Please download 'vosk-model-small-en-us-0.15' and unpack it in the 'models/' directory.")
        print("Download link: https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        sys.exit(1)
    return vosk.Model(MODEL_PATH)

# --- GLOBAL TOGGLE ---
LISTENING_ENABLED = True

def toggle_listening():
    global LISTENING_ENABLED
    LISTENING_ENABLED = not LISTENING_ENABLED
    if LISTENING_ENABLED:
        try:
            overlay.idle()
            print(f"{Fore.GREEN}[SYSTEM] SENSORS ONLINE{Style.RESET_ALL}")
            speak.speak("Systems Online.", None)
        except: pass
    else:
        try:
            overlay.error() # Visual feedback for offline
            print(f"{Fore.RED}[SYSTEM] SENSORS OFFLINE (Muted){Style.RESET_ALL}")
            speak.speak("Sensors Disabled.", None)
        except: pass

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

    # 4. Start Overlay
    overlay.start()
    overlay.idle()

    # 5. Startup Sound
    overlay.speaking()
    speak.speak("A one online. High-Accuracy Mode.")
    overlay.idle()

    # 6. Start Hotkeys
    try:
        hk = hotkeys.GlobalHotKeys(toggle_listening)
        hk.start()
    except Exception as e:
        print(f"{Fore.RED}[HOTKEY ERROR] {e}{Style.RESET_ALL}")

    # 7. Main Loop
    while True:
        try:
            # Check Toggle
            if not LISTENING_ENABLED:
                time.sleep(0.5)
                continue

            # Wait for wake word (Vosk) or GUI Input
            wake_result = wake.listen_for_wake_word(vosk_model)
            
            command_to_process = None
            
            if isinstance(wake_result, str):
                # Typed Input - Skip "Listening" prompt
                command_to_process = wake_result
            elif wake_result is True:
                # Wake Word detected! Switch to listening state
                overlay.listening()
                
                # Continuous Conversation Mode
                next_command = speak.speak("Listening.", vosk_model)
                if next_command:
                    command_to_process = next_command
            else:
                continue

            # Enter Conversation Loop
            while True:
                # Check if we already have a command
                if command_to_process:
                    command = command_to_process
                    command_to_process = None
                    print(f"{Fore.MAGENTA}[PROCESSING]: {command}{Style.RESET_ALL}")
                else:
                    # Listen for command (Whisper)
                    overlay.listening()
                    command = ear.listen(timeout=8)
                
                if command:
                    # Thinking state while processing
                    overlay.thinking()
                    
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
                    elif intent == "weather":
                        speak.speak("Checking the weather...", vosk_model)
                        response = weather.get_weather(args)
                    elif intent == "weather_forecast":
                        location = args.get("location", "") if isinstance(args, dict) else args
                        days = args.get("days", 3) if isinstance(args, dict) else 3
                        speak.speak(f"Getting the {days} day forecast...", vosk_model)
                        response = weather.get_weather_forecast(location, days)
                    elif intent == "weather_rain":
                        speak.speak("Let me check...", vosk_model)
                        response = weather.should_i_carry_umbrella(args)
                    # --- SYSTEM CONTROL ---
                    elif intent == "system_shutdown":
                        speak.speak("Shutting down. Goodbye!", vosk_model)
                        response = arch.shutdown()
                    elif intent == "system_reboot":
                        speak.speak("Rebooting now. See you soon!", vosk_model)
                        response = arch.reboot()
                    elif intent == "system_suspend":
                        speak.speak("Going to sleep. Goodnight!", vosk_model)
                        response = arch.suspend()
                    elif intent == "system_lock":
                        response = arch.lock_screen()
                    elif intent == "system_status":
                        response = arch.get_full_system_status()
                    # --- AUDIO CONTROL ---
                    elif intent == "volume_up":
                        response = arch.volume_up()
                    elif intent == "volume_down":
                        response = arch.volume_down()
                    elif intent == "mute_toggle":
                        response = arch.mute_toggle()
                    # --- BRIGHTNESS CONTROL ---
                    elif intent == "brightness_up":
                        response = arch.brightness_up()
                    elif intent == "brightness_down":
                        response = arch.brightness_down()
                    # --- WIFI CONTROL ---
                    elif intent == "wifi_on":
                        response = arch.wifi_on()
                    elif intent == "wifi_off":
                        response = arch.wifi_off()
                    elif intent == "wifi_status":
                        response = arch.wifi_status()
                    # --- PACKAGE MANAGEMENT ---
                    elif intent == "arch_uninstall":
                        speak.speak(f"Uninstalling {args}...", vosk_model)
                        response = arch.uninstall_package(args)
                    # --- BLUETOOTH ---
                    elif intent == "bluetooth_on":
                        response = arch.bluetooth_on()
                    elif intent == "bluetooth_off":
                        response = arch.bluetooth_off()
                    elif intent == "bluetooth_status":
                        response = arch.bluetooth_status()
                    # --- SCREENSHOT ---
                    elif intent == "screenshot":
                        response = arch.take_screenshot()
                    elif intent == "screenshot_area":
                        response = arch.take_screenshot_area()
                    # --- NIGHT MODE ---
                    elif intent == "night_mode_on":
                        response = arch.night_mode_on()
                    elif intent == "night_mode_off":
                        response = arch.night_mode_off()
                    # --- SYSTEM CLEANUP ---
                    elif intent == "clean_cache":
                        response = arch.clean_package_cache()
                    elif intent == "remove_orphans":
                        response = arch.remove_orphan_packages()
                    elif intent == "clear_logs":
                        response = arch.clear_system_logs()
                    elif intent == "empty_trash":
                        response = arch.empty_trash()
                    # --- DO NOT DISTURB ---
                    elif intent == "dnd_on":
                        response = arch.do_not_disturb_on()
                    elif intent == "dnd_off":
                        response = arch.do_not_disturb_off()
                    # --- CLIPBOARD ---
                    elif intent == "clear_clipboard":
                        response = arch.clear_clipboard()
                    elif intent == "get_clipboard":
                        response = arch.get_clipboard()
                    # --- PROCESS CONTROL ---
                    elif intent == "kill_process":
                        response = arch.kill_process(args)
                    elif intent == "force_kill":
                        response = arch.force_kill_process(args)
                    # --- FILE MANAGER ---
                    elif intent == "file_manager":
                        response = arch.open_file_manager()
                    elif intent == "open_downloads":
                        response = arch.open_downloads()
                    elif intent == "open_documents":
                        response = arch.open_documents()
                    # --- TIMER ---
                    elif intent == "set_timer":
                        response = arch.set_timer(int(args) if args else 5)
                    # --- MEDIA CONTROLS ---
                    elif intent == "media_play_pause":
                        response = arch.media_play_pause()
                    elif intent == "media_next":
                        response = arch.media_next()
                    elif intent == "media_previous":
                        response = arch.media_previous()
                    elif intent == "media_stop":
                        response = arch.media_stop()
                    # --- POWER PROFILE ---
                    elif intent == "power_profile":
                        response = arch.set_power_profile(args)
                    elif intent == "power_profile_status":
                        response = arch.get_power_profile()
                    # --- TIME & UPTIME ---
                    elif intent == "uptime":
                        response = arch.get_uptime()
                    elif intent == "current_time":
                        response = arch.get_current_time()
                    # --- PERSONAL ASSISTANT (JARVIS) ---
                    elif intent == "morning_protocol":
                        response = personal_assistant.morning_protocol()
                    elif intent == "take_note":
                        response = personal_assistant.take_note(args)
                    elif intent == "read_notes":
                        response = personal_assistant.read_notes()
                    elif intent == "focus_mode":
                        # Combine arch + personal assistant
                        arch.do_not_disturb_on()
                        response = personal_assistant.focus_mode()
                    # --- SECURITY & MEDIA ---
                    elif intent == "sentry_mode":
                        speak.speak("Engaging Sentry Protocol.", vosk_model)
                        response = arch.sentry_mode()
                    elif intent == "youtube_search":
                        response = web.play_youtube(args)
                    elif intent == "apple_music_search":
                        response = web.play_apple_music(args)
                    # --- NEWS ---
                    elif intent == "news_general":
                         speak.speak("Fetching the latest headlines.", vosk_model)
                         response = news.get_latest_news("world")
                    elif intent == "news_tech":
                         speak.speak("Checking tech news.", vosk_model)
                         response = news.get_latest_news("tech")
                    # --- AUTOMATION ---
                    elif intent == "auto_type":
                        response = automation.type_text(args)
                    elif intent == "auto_press":
                        response = automation.press_key(args)
                    # --- LEARNING ---
                    elif intent == "learn_fact":
                        memory.memory.add_memory(args, source="user", memory_type="fact")
                        response = f"I have committed that to memory: {args}"
                    elif intent == "feedback_positive":
                        # ideally log the last interaction
                        response = "Thank you, Sir. Protocols reinforced."
                    elif intent == "feedback_negative":
                        response = "I apologize, Sir. I will mark that as a failure for analysis."
                    elif intent == "tune_self":
                        speak.speak("Initiating self-optimization logic.", vosk_model)
                        try:
                            subprocess.Popen(["python", "scripts/adaptive_tuning.py"], cwd=BASE_DIR)
                            response = "Optimization process started in background."
                        except Exception as e:
                            response = f"Failed to start optimization: {e}"
                    else:
                        # Conversation
                        response = brain.think(args)
                            
                    # Speak response
                    overlay.speaking()
                    speak.speak(response, vosk_model)
                    overlay.idle()
                    
                    # Go back to Sleep (break inner loop) to wait for Wake Word again
                    next_command = None 
                    break
                else:
                    print(f"{Fore.YELLOW}[SYSTEM] Timeout.{Style.RESET_ALL}")
                    overlay.speaking()
                    speak.speak("Offline.")
                    overlay.idle()
                    break

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[SYSTEM] Stopping...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Critical Loop Error: {e}{Style.RESET_ALL}")
            overlay.error()
            speak.speak("System error.")
            overlay.idle()
    
    # Cleanup when main loop exits
    cleanup()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Fore.RED}[FATAL] {e}{Style.RESET_ALL}")
        cleanup()
        sys.exit(1)
