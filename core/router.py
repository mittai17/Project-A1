import requests
import re

# Configuration
# Point this to a Qwen2.5-0.5B-GGUF (or similar small/fast model)
# running on llama.cpp server.
ROUTER_MODEL = "qwen2.5:0.5b" # Adjust if your local model name is different
API_URL = "http://localhost:11434/api/generate"

# Optimized Qwen2.5 Router Prompt with Few-Shot Examples for accuracy
SYSTEM_PROMPT = """You are a query router.
Classify user input into exactly one of these routes:

Routes:
- search: weather, news, current events, stock prices, fact lookups.
- vision: look at screen, what is on screen, describe image, OCR.
- code: write code, debug, script, programming questions.
- system: update system, install packages, cpu/ram stats, open/close apps.
- chat: greetings, general conversation, philosophy, jokes.

Examples:
Input: "What is the weather in Tokyo?"
Output: {"route":"search"}

Input: "Look at this error."
Output: {"route":"vision"}

Input: "Write a python script to sort a list."
Output: {"route":"code"}

Input: "Install firefox."
Output: {"route":"system"}

Input: "Tell me a joke."
Output: {"route":"chat"}

Input: "Search for latest AI news."
Output: {"route":"search"}

Input: "{USER_INPUT}"
Output:"""

def route_query_ai(user_input):
    """
    Disabled in favor of logic-based routing (Spec Requirement).
    """
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

    # Vision
    vision_triggers = ["look at", "screen", "what is on", "analyze", "see"]
    if any(t in text_lower for t in vision_triggers):
        return {"intent": "vision_query", "args": text}

    # Search / Weather (Fast-Path)
    search_triggers = ["search", "google", "weather", "news", "price", "stock", "when is", "who is", "what is the date"]
    if any(t in text_lower for t in search_triggers):
        # Cleanup "search for" etc
        clean_text = text_lower.replace("search for", "").replace("search", "").strip()
        return {"intent": "web_search", "args": clean_text if clean_text else text}

    # --- System Control (Install / Update) ---
    if "update system" in text_lower:
         return {"intent": "arch_update", "args": ""}

    match_install = re.search(r"^install (.+)", text_lower)
    if match_install:
         package = match_install.group(1).strip()
         return {"intent": "arch_install", "args": package}

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
