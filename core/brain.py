import requests
import json
import time
import os
from colorama import Fore, Style
from dotenv import load_dotenv
from core.memory import memory

# Load environment keys
load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
BYTEZ_KEY = os.getenv("BYTEZ_API_KEY")
LOCAL_MODEL = "llama3.2:3b"
API_URL = "http://localhost:11434/api/generate"

# Short-term history
history = []
MAX_HISTORY = 10

def load_system_prompt():
    """Loads the core identity from the markdown file."""
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SYSTEM_PROMPT.md")
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"{Fore.RED}[ERROR] Could not load SYSTEM_PROMPT.md: {e}{Style.RESET_ALL}")
        return "You are A1, a helpful AI assistant."

# Load once at startup
SYSTEM_PROMPT_TEXT = load_system_prompt()

def classify_complexity(prompt):
    """
    Uses Local LLM to classify task complexity (1-5) and type.
    """
    # Fast path for very short queries
    if len(prompt.split()) < 5:
        return {"complexity": 1, "type": "small_chat"}

    req = {
        "model": LOCAL_MODEL,
        "prompt": f"Analyze this user request: '{prompt}'. Return strictly JSON: {{\"complexity\": <int 1-5>, \"type\": \"<coding|reasoning|chat|system>\"}}. JSON ONLY, NO TEXT.",
        "stream": False,
        "format": "json"
    }
    try:
        # Lower timeout for routing to be fast
        res = requests.post(API_URL, json=req, timeout=3)
        if res.status_code == 200:
            return json.loads(res.json()['response'])
    except:
        pass
    return {"complexity": 1, "type": "chat"} # Default

def call_local(prompt, system_prompt, context_memories):
    print(f"{Fore.GREEN}[BRAIN] Routing to LOCAL ({LOCAL_MODEL})...{Style.RESET_ALL}")
    
    full_prompt = f"System: {system_prompt}\nMemories: {context_memories}\nUser: {prompt}"
    
    req = {
        "model": LOCAL_MODEL,
        "prompt": full_prompt,
        "stream": False
    }
    try:
        start = time.time()
        res = requests.post(API_URL, json=req, timeout=120)
        dt = time.time() - start
        print(f"{Fore.GREEN}[BRAIN] Local generated in {dt:.2f}s{Style.RESET_ALL}")
        if res.status_code == 200:
             return res.json()['response']
        return "Local LLM Error."
    except Exception as e:
        return f"Local Error: {e}"

def call_bytez(prompt, system_prompt, context_memories):
    print(f"{Fore.CYAN}[BRAIN] Routing to BYTEZ (Mid-Tier)...{Style.RESET_ALL}")
    
    # Generic wrapper for Bytez
    headers = {"Authorization": f"Bearer {BYTEZ_KEY}", "Content-Type": "application/json"}
    
    # Using generic chat completion endpoint structure
    url = "https://api.bytez.com/v1/chat/completions" 
    
    full_system = f"{system_prompt}\n\nContext Memories:\n{context_memories}"
    
    data = {
        "model": "meta-llama/Llama-3-70b-instruct", 
        "messages": [
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        res = requests.post(url, json=data, headers=headers, timeout=40)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            # If Bytez fails (e.g. invalid endpoint), throw to trigger fallback
            raise Exception(f"Bytez Status {res.status_code}: {res.text}")
            
    except Exception as e:
        print(f"{Fore.RED}[BRAIN] Bytez failed ({e}). Falling back to Local.{Style.RESET_ALL}")
        return call_local(prompt, system_prompt, context_memories)

def call_openrouter(prompt, system_prompt, context_memories):
    print(f"{Fore.MAGENTA}[BRAIN] Routing to OPENROUTER (High-Tier)...{Style.RESET_ALL}")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "A1 Assistant"
    }
    
    # High-tier model: Claude 3.5 Sonnet or similar
    model = "anthropic/claude-3-haiku" 
    
    full_system = f"{system_prompt}\n\nContext Memories:\n{context_memories}"
    
    data = {
        "model": model, 
        "messages": [
            {"role": "system", "content": full_system},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers, timeout=60)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
             raise Exception(f"OpenRouter Status {res.status_code}")
    except Exception as e:
        print(f"{Fore.RED}[BRAIN] OpenRouter failed ({e}). Falling back to Local.{Style.RESET_ALL}")
        return call_local(prompt, system_prompt, context_memories)

def think(prompt):
    """
    Main Thinking Logic:
    1. Memory Lookup
    2. Complexity Classification
    3. Model Routing
    4. Execution
    """
    global history
    print(f"{Fore.CYAN}[BRAIN] Analyzing intent...{Style.RESET_ALL}")

    # 0. Basic internal commands
    if prompt.lower().startswith("remember that") or prompt.lower().startswith("remember:"):
        fact = prompt.replace("remember that", "").replace("remember:", "").strip()
        if memory.add_memory(fact):
            return f"I remembered: {fact}"
        return "Failed to save memory."

    # 1. Retrieve Memories
    relevant = memory.retrieve_relevant(prompt)
    mem_context = "\n".join([f"- {m}" for m in relevant]) if relevant else "No relevant memories."
    
    # 2. Classify Complexity
    meta = classify_complexity(prompt)
    complexity = meta.get('complexity', 1)
    task_type = meta.get('type', 'chat')
    
    print(f"{Fore.BLUE}[BRAIN] Task: {task_type} | Complexity: {complexity}/5{Style.RESET_ALL}")
    
    # 3. Route
    response = ""
    
    if complexity >= 4 and OPENROUTER_KEY:
        response = call_openrouter(prompt, SYSTEM_PROMPT_TEXT, mem_context)
    elif complexity == 3 and BYTEZ_KEY:
        response = call_bytez(prompt, SYSTEM_PROMPT_TEXT, mem_context)
    else:
        # Default to Local
        response = call_local(prompt, SYSTEM_PROMPT_TEXT, mem_context)

    # 4. Update History
    history.append({"role": "User", "content": prompt})
    history.append({"role": "Assistant", "content": response})
    if len(history) > MAX_HISTORY:
        history.pop(0)
        
    return response

if __name__ == "__main__":
    print(think("Hello A1"))
