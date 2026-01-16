import os
import base64
import requests
import pyautogui
from io import BytesIO
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv()

# Configuration
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
# Using a vision-capable model. Gemini 2.0 Flash is multimodal.
VISION_MODEL = "google/gemini-2.0-flash-exp:free" 

def load_system_prompt():
    try:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VISION_SYSTEM_PROMPT.md")
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"{Fore.RED}[VISION] Error loading system prompt: {e}{Style.RESET_ALL}")
        return "You are A1-Vision. Analyze the screen."

SYSTEM_PROMPT = load_system_prompt()

def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def capture_screen():
    print(f"{Fore.CYAN}[VISION] Capturing screen...{Style.RESET_ALL}")
    try:
        # PyAutoGUI screenshot works on X11 and some Wayland setups (with XWayland)
        # If this fails, we might need a specific Linux tool like gnome-screenshot or scrot
        screenshot = pyautogui.screenshot()
        return screenshot
    except Exception as e:
        print(f"{Fore.RED}[VISION] Screenshot failed: {e}{Style.RESET_ALL}")
        return None

def analyze_screen(user_query):
    if not OPENROUTER_KEY:
        return "Vision capabilities unavailable. No OpenRouter API key found."

    screenshot = capture_screen()
    if not screenshot:
        return "Could not capture screen."

    base64_image = encode_image(screenshot)
    
    print(f"{Fore.MAGENTA}[VISION] Analyzing with {VISION_MODEL}...{Style.RESET_ALL}")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "A1-Vision"
    }

    # OpenRouter / OpenAI compatible payload for Vision
    payload = {
        "model": VISION_MODEL,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return content
            else:
                return "No response from vision model."
        else:
            print(f"{Fore.RED}[VISION] API Error: {response.text}{Style.RESET_ALL}")
            return f"Vision API refused connection: {response.status_code}"
    except Exception as e:
        print(f"{Fore.RED}[VISION] Request failed: {e}{Style.RESET_ALL}")
        return "Network error processing vision request."
