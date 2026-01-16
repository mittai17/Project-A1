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
    Uses a small, ultra-fast LLM to route queries deterministically.
    """
    try:
        req = {
            "model": ROUTER_MODEL,
            "prompt": SYSTEM_PROMPT.replace("{USER_INPUT}", user_input),
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 10, # Max tokens
                "num_ctx": 256,
                "top_p": 1,
            }
        }
        res = requests.post(API_URL, json=req, timeout=3)
        if res.status_code == 200:
            result = res.json()['response'].strip()
            
            # Simple heuristic parsing since model is deterministic
            if '"route":"code"' in result or "'route': 'code'" in result or "route: code" in result or result == "code":
                return "code"
            if '"route":"search"' in result or "search" in result:
                return "search"
            if '"route":"vision"' in result or "vision" in result:
                return "vision"
            if '"route":"system"' in result or "system" in result:
                return "system"
            
            # Default fallback
            return "chat"
            
    except Exception as e:
        # Fallback to regex if AI router fails (timeout/offline)
        return None 

def route_query(text):
    """
    Hybrid Routing: Regex Fast-Path -> AI Router -> Default.
    """
    text_lower = text.lower().strip()
    
    # --- 1. Regex Fast-Path (0 Latency) ---
    
    # App Control (Open/Close)
    match = re.search(r"(open|close) (.+)", text_lower)
    if match:
         app = match.group(2).replace(".", "").strip()
         action = "app_open" if match.group(1) == "open" else "app_close"
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
