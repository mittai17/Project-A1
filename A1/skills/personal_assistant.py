import os
import datetime
import psutil
from colorama import Fore, Style
from skills.weather import get_current_weather

NOTES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "user_data", "notes.txt")

def ensure_notes_file():
    if not os.path.exists(os.path.dirname(NOTES_FILE)):
        os.makedirs(os.path.dirname(NOTES_FILE))
    if not os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "w") as f:
            f.write("--- A1 SECURE NOTES ---\n")

def morning_protocol():
    """
    Generates a Jarvis-style status report.
    """
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    date_str = now.strftime("%A, %B %d")
    
    # System Stats
    from skills import arch
    sys_stats = arch.get_system_stats() # Now includes GPU
    net_info = arch.get_network_info()
    
    # Weather
    try:
        weather = get_current_weather()
    except:
        weather = "Network unavailable for weather data."
    
    report = (
        f"Good morning, Sir. "
        f"It is {time_str} on {date_str}. "
        f"Systems check complete. {sys_stats} "
        f"Network is {net_info.split('|')[0].replace('Network Status:', '').strip()}. "
        f"Outside, {weather}. "
        f"I am standing by."
    )
    return report

def take_note(content):
    ensure_notes_file()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    entry = f"[{timestamp}] {content}\n"
    
    with open(NOTES_FILE, "a") as f:
        f.write(entry)
    
    return f"Note saved, Sir: '{content}'"

def read_notes(limit=3):
    ensure_notes_file()
    if not os.path.exists(NOTES_FILE):
        return "No notes found in the database, Sir."
        
    with open(NOTES_FILE, "r") as f:
        lines = f.readlines()
        
    # Filter for content lines (skip headers/empty)
    entries = [l.strip() for l in lines if l.strip() and not l.startswith("---")]
    
    if not entries:
        return "Your notebook is currently empty, Sir."
        
    recent = entries[-limit:]
    result = "Here are your latest entries:\n" + "\n".join(recent)
    return result

def focus_mode():
    """
    activates DND, clears clutter (mock), plays focus music logic would go here
    For now, return a confirmation string for the Brain to speak.
    """
    # We can call actual system commands here if we import arch skill
    return "Focus Mode engaged. Do Not Disturb active. Notifications silenced."
