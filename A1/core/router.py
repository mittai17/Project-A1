import requests
import re

# Configuration
# Custom Fine-Tuned Model for A1
ROUTER_MODEL = "A1-Router_llm" 
API_URL = "http://localhost:11434/api/generate"

def route_query_ai(user_input):
    """
    Uses A1-Router_llm for sub-millisecond intent classification.
    """
    # System prompt is BAKED into the model, just send input
    prompt = user_input
    
    try:
        req = {
            "model": ROUTER_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.0, # Reinforce deterministic behavior
                "num_predict": 5  
            }
        }
        res = requests.post(API_URL, json=req, timeout=1.0) # Strict 1s timeout
        if res.status_code == 200:
            result = res.json()['response'].strip().lower()
            if "search" in result: return "search"
            if "vision" in result: return "vision"
            if "code" in result: return "code"
            if "system" in result: return "system"
            if "chat" in result: return "chat"
    except:
        pass
    
    return None 

def route_query(text):
    """
    Hybrid Routing: Regex Fast-Path -> AI Router -> Default.
    """
    text_lower = text.lower().strip()
    
    # --- 1. Regex Fast-Path (0 Latency) ---
    
    # Clean noise (repetition, politeness)
    # Remove duplicates like "open terminal open terminal" -> "open terminal"
    # Simple de-duplication of the whole string space-wise? No, risky. 
    # Just fix the specific case of repeated command phrase.
    if "open terminal" in text_lower and text_lower.count("open terminal") > 1:
        text_lower = "open terminal"
    
    # --- FILE MANAGER (must be before generic open/close) ---
    if "open file manager" in text_lower or "open files" in text_lower or "file explorer" in text_lower:
        return {"intent": "file_manager", "args": ""}
    
    if "open downloads" in text_lower or "downloads folder" in text_lower:
        return {"intent": "open_downloads", "args": ""}
    
    if "open documents" in text_lower or "documents folder" in text_lower:
        return {"intent": "open_documents", "args": ""}
    
    match = re.search(r"^(?:please )?(open|close) (.+)", text_lower)
    if match:
         action_word = match.group(1)
         raw_app = match.group(2)
         
         # Cleanup arg: remove repeated action words at the end
         # e.g., "terminal open terminal" -> "terminal"
         raw_app = raw_app.replace(f"open {raw_app}", "").replace(action_word, "").strip()
         raw_app = raw_app.replace(".", "").strip()

         action = "app_open" if action_word == "open" else "app_close"
         return {"intent": action, "args": raw_app}

    # App Control (Open/Close) - Tanglish/Suffix (e.g., "Firefox open pannu", "Firefox open")
    match_suffix = re.search(r"^(.+) (open|close)( pannu| seiyu| karo)?$", text_lower)
    if match_suffix:
         app = match_suffix.group(1).replace(".", "").strip()
         action = "app_open" if match_suffix.group(2) == "open" else "app_close"
         return {"intent": action, "args": app}

    # Lock Screen (must be before vision which catches "screen")
    lock_triggers = ["lock screen", "lock computer", "lock the screen", "lock my computer"]
    if any(t in text_lower for t in lock_triggers):
        return {"intent": "system_lock", "args": ""}

    # Vision
    vision_triggers = ["look at", "what is on screen", "what is on my screen", "analyze", "see my screen"]
    if any(t in text_lower for t in vision_triggers):
        return {"intent": "vision_query", "args": text}

    # --- Weather Detection (Open-Meteo) ---
    weather_triggers = ["weather", "temperature", "forecast", "raining", "rain", "umbrella", "sunny", "cloudy", "humidity"]
    if any(t in text_lower for t in weather_triggers):
        # Extract location from query
        import re as re_mod
        location = ""
        
        # Multiple patterns for location extraction
        patterns = [
            r"(?:weather|raining|rain|forecast|temperature|humidity) (?:in|at|for|of) ([a-zA-Z\s]+?)(?:\?|$|\s*today|\s*tomorrow|\s*now)",  # "weather in Tokyo?"
            r"(?:in|at) ([a-zA-Z\s]+?)(?:\?|$)",  # "raining in Mumbai?"
            r"([a-zA-Z\s]+?) (?:weather|forecast)",  # "London weather"
            r"forecast for ([a-zA-Z\s]+?)(?:\?|$)",  # "forecast for London"
            r"(?:umbrella|rain) .*?(?:in|at) ([a-zA-Z\s]+?)(?:\?|$)",  # "umbrella in Chennai"
        ]
        
        for pattern in patterns:
            loc_match = re_mod.search(pattern, text_lower)
            if loc_match:
                location = loc_match.group(1).strip()
                # Clean up common words that aren't locations
                cleanup_words = ["the", "today", "tomorrow", "now", "is", "it", "should", "i", "carry", "an"]
                for word in cleanup_words:
                    if location.lower() == word:
                        location = ""
                        break
                if location:
                    break
        
        # Check for forecast request
        if "forecast" in text_lower:
            # Try to extract days
            days_match = re_mod.search(r"(\d+)[- ]day", text_lower)
            days = int(days_match.group(1)) if days_match else 3
            return {"intent": "weather_forecast", "args": {"location": location, "days": days}}
        
        # Check for rain/umbrella questions
        if "rain" in text_lower or "umbrella" in text_lower:
            return {"intent": "weather_rain", "args": location}
        
        # Default: current weather
        return {"intent": "weather", "args": location}

    # Search (Fast-Path) - Now without weather
    search_triggers = ["search", "google", "news", "price", "stock", "when is", "who is", "what is the date"]
    if any(t in text_lower for t in search_triggers):
        # Cleanup "search for" etc
        clean_text = text_lower.replace("search for", "").replace("search", "").strip()
        return {"intent": "web_search", "args": clean_text if clean_text else text}

    # --- COMPLETE SYSTEM CONTROL ---
    
    # Power Management
    shutdown_triggers = ["shutdown", "shut down", "power off", "turn off computer", "switch off"]
    if any(t in text_lower for t in shutdown_triggers):
        return {"intent": "system_shutdown", "args": ""}
    
    reboot_triggers = ["reboot", "restart", "restart computer", "restart system"]
    if any(t in text_lower for t in reboot_triggers):
        return {"intent": "system_reboot", "args": ""}
    
    suspend_triggers = ["suspend", "sleep", "go to sleep", "hibernate"]
    if any(t in text_lower for t in suspend_triggers):
        return {"intent": "system_suspend", "args": ""}
    
    lock_triggers = ["lock", "lock screen", "lock computer", "lock the screen"]
    if any(t in text_lower for t in lock_triggers):
        return {"intent": "system_lock", "args": ""}
    
    # Audio Control
    if "volume up" in text_lower or "increase volume" in text_lower or "louder" in text_lower:
        return {"intent": "volume_up", "args": ""}
    
    if "volume down" in text_lower or "decrease volume" in text_lower or "quieter" in text_lower or "softer" in text_lower:
        return {"intent": "volume_down", "args": ""}
    
    if "mute" in text_lower or "unmute" in text_lower:
        return {"intent": "mute_toggle", "args": ""}
    
    # Brightness Control
    if "brightness up" in text_lower or "increase brightness" in text_lower or "brighter" in text_lower:
        return {"intent": "brightness_up", "args": ""}
    
    if "brightness down" in text_lower or "decrease brightness" in text_lower or "dimmer" in text_lower or "dim" in text_lower:
        return {"intent": "brightness_down", "args": ""}
    
    # WiFi Control
    if "wifi on" in text_lower or "enable wifi" in text_lower or "turn on wifi" in text_lower or "connect wifi" in text_lower:
        return {"intent": "wifi_on", "args": ""}
    
    if "wifi off" in text_lower or "disable wifi" in text_lower or "turn off wifi" in text_lower or "disconnect wifi" in text_lower:
        return {"intent": "wifi_off", "args": ""}
    
    if "wifi status" in text_lower or "wifi connection" in text_lower or "connected to wifi" in text_lower:
        return {"intent": "wifi_status", "args": ""}
    
    # System Status
    if "system status" in text_lower or "system stats" in text_lower or "how is my system" in text_lower:
        return {"intent": "system_status", "args": ""}
    
    if "check ram" in text_lower or "cpu usage" in text_lower or "memory usage" in text_lower:
        return {"intent": "system_stats", "args": ""}
    
    if "uptime" in text_lower or "how long has" in text_lower:
        return {"intent": "uptime", "args": ""}
    
    if "what time" in text_lower or "current time" in text_lower:
        return {"intent": "current_time", "args": ""}
    
    # Package Management
    if "update system" in text_lower or "system update" in text_lower:
        return {"intent": "arch_update", "args": ""}

    match_install = re.search(r"^install (.+)", text_lower)
    if match_install:
        package = match_install.group(1).strip()
        return {"intent": "arch_install", "args": package}
    
    match_uninstall = re.search(r"^(?:uninstall|remove) (.+)", text_lower)
    if match_uninstall:
        package = match_uninstall.group(1).strip()
        return {"intent": "arch_uninstall", "args": package}
    
    # --- BLUETOOTH CONTROL ---
    if "bluetooth on" in text_lower or "enable bluetooth" in text_lower or "turn on bluetooth" in text_lower:
        return {"intent": "bluetooth_on", "args": ""}
    
    if "bluetooth off" in text_lower or "disable bluetooth" in text_lower or "turn off bluetooth" in text_lower:
        return {"intent": "bluetooth_off", "args": ""}
    
    if "bluetooth status" in text_lower or "bluetooth connected" in text_lower:
        return {"intent": "bluetooth_status", "args": ""}
    
    # --- SCREENSHOT ---
    if "screenshot" in text_lower or "take a picture" in text_lower or "capture screen" in text_lower:
        if "area" in text_lower or "select" in text_lower or "region" in text_lower:
            return {"intent": "screenshot_area", "args": ""}
        return {"intent": "screenshot", "args": ""}
    
    # --- NIGHT MODE ---
    if "night mode on" in text_lower or "enable night mode" in text_lower or "warm screen" in text_lower or "blue light" in text_lower:
        return {"intent": "night_mode_on", "args": ""}
    
    if "night mode off" in text_lower or "disable night mode" in text_lower or "normal screen" in text_lower:
        return {"intent": "night_mode_off", "args": ""}
    
    # --- SYSTEM CLEANUP ---
    if "clean cache" in text_lower or "clear cache" in text_lower or "clean package cache" in text_lower:
        return {"intent": "clean_cache", "args": ""}
    
    if "remove orphan" in text_lower or "clean orphan" in text_lower:
        return {"intent": "remove_orphans", "args": ""}
    
    if "clear logs" in text_lower or "clean logs" in text_lower:
        return {"intent": "clear_logs", "args": ""}
    
    if "empty trash" in text_lower or "clear trash" in text_lower:
        return {"intent": "empty_trash", "args": ""}
    
    # --- DO NOT DISTURB ---
    if "do not disturb" in text_lower or "dnd on" in text_lower or "silence notifications" in text_lower:
        if "off" in text_lower or "disable" in text_lower:
            return {"intent": "dnd_off", "args": ""}
        return {"intent": "dnd_on", "args": ""}
    
    # --- CLIPBOARD ---
    if "clear clipboard" in text_lower or "empty clipboard" in text_lower:
        return {"intent": "clear_clipboard", "args": ""}
    
    if "what is in clipboard" in text_lower or "clipboard content" in text_lower or "read clipboard" in text_lower:
        return {"intent": "get_clipboard", "args": ""}
    
    # --- PROCESS CONTROL ---
    match_kill = re.search(r"(?:kill|terminate|stop|force quit) (?:the )?(?:process |app )?(.+)", text_lower)
    if match_kill:
        process = match_kill.group(1).strip()
        if "force" in text_lower:
            return {"intent": "force_kill", "args": process}
        return {"intent": "kill_process", "args": process}
    
    # --- FILE MANAGER ---
    if "open file manager" in text_lower or "open files" in text_lower or "file explorer" in text_lower:
        return {"intent": "file_manager", "args": ""}
    
    if "open downloads" in text_lower or "downloads folder" in text_lower:
        return {"intent": "open_downloads", "args": ""}
    
    if "open documents" in text_lower or "documents folder" in text_lower:
        return {"intent": "open_documents", "args": ""}
    
    # --- TIMER ---
    match_timer = re.search(r"(?:set |start )?(?:a )?timer (?:for )?(\d+)(?: )?(?:minute|min)", text_lower)
    if match_timer:
        minutes = int(match_timer.group(1))
        return {"intent": "set_timer", "args": minutes}
    
    # --- MEDIA CONTROLS ---
    if "play" in text_lower and "pause" in text_lower:
        return {"intent": "media_play_pause", "args": ""}
    
    if "pause music" in text_lower or "pause media" in text_lower or "play music" in text_lower:
        return {"intent": "media_play_pause", "args": ""}
    
    if "next track" in text_lower or "next song" in text_lower or "skip song" in text_lower:
        return {"intent": "media_next", "args": ""}
    
    if "previous track" in text_lower or "previous song" in text_lower or "go back" in text_lower:
        return {"intent": "media_previous", "args": ""}
    
    if "stop music" in text_lower or "stop media" in text_lower:
        return {"intent": "media_stop", "args": ""}
    
    # --- POWER PROFILE ---
    if "performance mode" in text_lower or "high performance" in text_lower:
        return {"intent": "power_profile", "args": "performance"}
    
    if "power saver" in text_lower or "battery saver" in text_lower or "save battery" in text_lower:
        return {"intent": "power_profile", "args": "power-saver"}
    
    if "balanced mode" in text_lower:
        return {"intent": "power_profile", "args": "balanced"}
    
    if "power profile" in text_lower and "status" not in text_lower:
        return {"intent": "power_profile_status", "args": ""}

    # --- PERSONAL ASSISTANT (JARVIS) ---
    if "good morning" in text_lower or "morning report" in text_lower or "morning protocol" in text_lower or "status report" in text_lower:
        return {"intent": "morning_protocol", "args": ""}
    
    if "focus mode" in text_lower or "concentration mode" in text_lower:
        return {"intent": "focus_mode", "args": ""}
    
    if "read notes" in text_lower or "what are my notes" in text_lower or "read note" in text_lower:
        return {"intent": "read_notes", "args": ""}
    
    match_note = re.search(r"(?:take|make|save|add) (?:a )?note:? (.+)", text_lower)
    if match_note:
        content = match_note.group(1).strip()
        return {"intent": "take_note", "args": content}

    # --- SENTRY MODE ---
    if "sentry mode" in text_lower or "security protocol" in text_lower or "lock down" in text_lower:
        return {"intent": "sentry_mode", "args": ""}

    # --- YOUTUBE ---
    if "youtube" in text_lower:
        if "search" in text_lower or "play" in text_lower or "find" in text_lower:
             # Extract query: "play lofi on youtube" -> "lofi"
             query = text_lower.replace("play", "").replace("search", "").replace("find", "").replace("on youtube", "").replace("for", "").replace("youtube", "").strip()
             return {"intent": "youtube_search", "args": query}


    # --- 2. AI Router (Optimized Qwen) ---
    ai_route = route_query_ai(text)
    
    if ai_route == "code":
        # Route to coding agent (Bytez/Local)
        return {"intent": "conversation", "args": text + " [MODE: CODE]"}
    
    if ai_route == "search":
        return {"intent": "web_search", "args": text}
        
    if ai_route == "system":
        return {"intent": "conversation", "args": text + " [MODE: SYSTEM]"} # Let Brain handle system details

    # --- 3. Default ---
    return {"intent": "conversation", "args": text}
