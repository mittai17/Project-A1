import requests
import json
import time
import os
import asyncio
import re
from colorama import Fore, Style
from dotenv import load_dotenv
from core.memory import memory
from core.mcp_manager import manager as mcp_manager

# Load environment keys
load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
BYTEZ_KEY = os.getenv("BYTEZ_API_KEY")
LOCAL_MODEL = "llama3.2:3b"
ROUTER_MODEL = "qwen2.5:0.5b" # Ultra-fast routing model
API_URL = "http://localhost:11434/api/generate"

# Short-term history
history = []
MAX_HISTORY = 10

def load_system_prompt():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "SYSTEM_PROMPT.md")
        with open(path, "r") as f:
            return f.read()
    except:
        return "You are A1, a personal assistant."

SYSTEM_PROMPT_TEXT = load_system_prompt()

# --- INTELLIGENT ROUTING (Qwen2.5) ---
def determine_model_tier(prompt):
    """
    Uses Qwen2.5-0.5B to deterministically route queries.
    Returns: 'local', 'bytez', 'openrouter'
    """
    
    # Fast regex checks first
    tokens = prompt.lower()
    if "python" in tokens or "script" in tokens or "function" in tokens:
        return 'bytez' if BYTEZ_KEY else 'local'
        
    router_prompt = f"""You are a routing model.
Your ONLY task is to decide which Model Tier should handle the input.

Rules:
- local: Simple request, chat, system command, personal question.
- openrouter: Complex analysis, reasoning, vision, web search summary, creative writing.
- bytez: Coding, specialized math, complex technical tasks.

Return exactly one word:
local
openrouter
bytez

USER INPUT
{prompt}

OUTPUT"""

    try:
        req = {
            "model": ROUTER_MODEL,
            "prompt": router_prompt,
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_predict": 5,
                "num_ctx": 256,
                "top_p": 1,
            }
        }
        res = requests.post(API_URL, json=req, timeout=2)
        if res.status_code == 200:
            result = res.json()['response'].strip().lower()
            if "openrouter" in result: return "openrouter"
            if "bytez" in result: return "bytez"
            if "local" in result: return "local"
    except:
        pass
        
    # Fallback heuristic
    p_len = len(prompt.split())
    if "analyze" in tokens or "summarize" in tokens or p_len > 30:
        return 'openrouter' if OPENROUTER_KEY else 'local'
        
    return 'local'

# --- API CALLS ---
def call_llm(model_tier, prompt, system_prompt):
    """
    Generic wrapper to call the appropriate model provider.
    """
    if model_tier == 'bytez' and BYTEZ_KEY:
        try:
            print(f"{Fore.CYAN}[BRAIN] Routing to BYTES...{Style.RESET_ALL}")
            # Placeholder implementation until correct endpoint confirmed
            # Defaulting to Local fallback to ensure stability
            pass 
        except:
            pass
            
    if model_tier == 'openrouter' and OPENROUTER_KEY:
        try:
            print(f"{Fore.MAGENTA}[BRAIN] Routing to OPENROUTER...{Style.RESET_ALL}")
            headers = {
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "A1"
            }
            data = {
                "model": "google/gemini-2.0-flash-exp:free", # Fast & Smart
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            }
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", json=data, headers=headers, timeout=10)
            if res.status_code == 200:
                result = res.json()
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
        except Exception as e:
            print(f"{Fore.RED}[BRAIN] OpenRouter failed: {e}. Fallback to Local.{Style.RESET_ALL}")

    # LOCAL (Default)
    print(f"{Fore.GREEN}[BRAIN] Routing to LOCAL ({LOCAL_MODEL})...{Style.RESET_ALL}")
    req = {
        "model": LOCAL_MODEL,
        "prompt": f"System: {system_prompt}\nUser: {prompt}",
        "stream": False,
        "options": {"num_ctx": 4096}
    }
    try:
        start = time.time()
        res = requests.post(API_URL, json=req, timeout=60)
        print(f"{Fore.GREEN}[BRAIN] Local generated in {time.time()-start:.2f}s{Style.RESET_ALL}")
        if res.status_code == 200:
            return res.json()['response']
    except Exception as e:
        return f"Brain Error: {e}"
    return "Error."

# --- TOOL USE LOOP ---
async def think_async(prompt):
    """
    ReAct Loop:
    1. Check if tools needed.
    2. Loop: Thought -> Action -> Observation -> Thought
    """
    global history
    print(f"{Fore.CYAN}[BRAIN] Thinking...{Style.RESET_ALL}")
    
    # 1. Memory
    relevant = memory.retrieve_relevant(prompt)
    mem_context = "\n".join([f"- {m}" for m in relevant]) if relevant else "None"
    
    # 2. Get Tools (MCP)
    mcp_tools = await mcp_manager.list_tools()
    tools_desc = ""
    for t in mcp_tools:
        tools_desc += f"- {t['name']}: {t.get('description', 'No desc')} (args: {t.get('inputSchema', {})})\n"
        
    full_system = f"""{SYSTEM_PROMPT_TEXT}
    
=== MEMORY ===
{mem_context}

=== AVAILABLE TOOLS (MCP) ===
{tools_desc if tools_desc else "No external tools available currently."}

=== INSTRUCTIONS ===
1. Use the above tools ONLY if they are listed in "AVAILABLE TOOLS".
2. DO NOT hallucinate or invent tools that are not listed.
3. If you need to use a tool, output specifically:
[[CALL:tool_name(json_args)]]

Example format: [[CALL:tool_name({{"arg": "value"}})]]

If no tool is needed or relevant, just answer the user directly.
"""

    # 3. Intelligent Route (Qwen)
    tier = determine_model_tier(prompt)
    
    # 4. Agent Loop (Max 3 turns)
    current_prompt = prompt
    for turn in range(3):
        response = call_llm(tier, current_prompt, full_system)
        
        # Check for tool call
        tool_match = re.search(r"\[\[CALL:(\w+)\((.*)\)\]\]", response, re.DOTALL)
        if tool_match:
            t_name = tool_match.group(1)
            t_args_str = tool_match.group(2)
            print(f"{Fore.YELLOW}[TOOL] Detected call: {t_name}({t_args_str}){Style.RESET_ALL}")
            
            # Find server
            t_def = next((t for t in mcp_tools if t['name'] == t_name), None)
            if t_def:
                try:
                    # Clean args
                    # This implies valid JSON, heuristic parsing might be needed for loose LLMs
                    import ast
                    try:
                        # Fix common LLM mistakes (like q="val")
                        # 1. Try pure JSON
                        t_args = json.loads(t_args_str)
                    except:
                        try:
                            # 2. Try Python literal (handles single quotes or q="val" if formatted as dict)
                            if "=" in t_args_str and ":" not in t_args_str:
                                # transform key="val" -> {"key": "val"}
                                t_args_str = f"dict({t_args_str})"
                            
                            t_args = ast.literal_eval(t_args_str)
                        except:
                            print(f"{Fore.RED}[TOOL ERROR] Could not parse args: {t_args_str}{Style.RESET_ALL}")
                            continue
                        
                    result = await mcp_manager.call_tool(t_def['server'], t_name, t_args)
                    print(f"{Fore.YELLOW}[TOOL] Result: {str(result)[:100]}...{Style.RESET_ALL}")
                    
                    # Feed back to LLM
                    current_prompt += f"\n\n[TOOL EXECUTION]\nCall: {t_name}\nResult: {result}\n\nContinue answering the user."
                    continue # Re-loop
                except Exception as e:
                    print(f"{Fore.RED}[TOOL ERROR] {e}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[TOOL] Unknown tool: {t_name}{Style.RESET_ALL}")
        
        # No tool call, final answer
        # Update history
        history.append({"role": "user", "content": prompt})
        history.append({"role": "assistant", "content": response})
        if len(history) > MAX_HISTORY:
            history.pop(0)
            
        return response

    return response

# Synchronous wrapper for main.py
def think(prompt):
    return asyncio.run(think_async(prompt))
