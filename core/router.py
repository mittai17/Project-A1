import re

def route_query(text):
    """
    Classifies intent based on text patterns.
    Returns dict: {"intent": str, "args": str}
    """
    text_lower = text.lower().strip()
    
    # App Control: Open
    match = re.search(r"open (.+)", text_lower)
    if match:
        return {"intent": "app_open", "args": match.group(1)}
    
    # App Control: Close
    match = re.search(r"close (.+)", text_lower)
    if match:
        return {"intent": "app_close", "args": match.group(1)}
        
    # App Control: Focus
    match = re.search(r"(focus|switch to) (.+)", text_lower)
    if match:
        return {"intent": "app_focus", "args": match.group(2)}

    # Web Search
    if "search for" in text_lower or "google" in text_lower or "lookup" in text_lower:
        query = text_lower.replace("search for", "").replace("google", "").replace("lookup", "").strip()
        return {"intent": "web_search", "args": query}

    # Arch Linux / System
    if "update system" in text_lower or "update the system" in text_lower or "full update" in text_lower:
        return {"intent": "arch_update", "args": ""}
    
    if "install" in text_lower:
        pkg = text_lower.split("install")[-1].strip()
        return {"intent": "arch_install", "args": pkg}
        
    if "system status" in text_lower or "cpu usage" in text_lower or "ram usage" in text_lower or "stats" in text_lower:
        return {"intent": "system_stats", "args": ""}

    # FOSS / Open Source
    if "find opensource" in text_lower or "open source" in text_lower or "fos" in text_lower or "github" in text_lower:
        query = text_lower.replace("find opensource", "").replace("open source", "").replace("search github for", "").replace("github", "").strip()
        return {"intent": "foss_search", "args": query}
        
    # Default
    return {"intent": "conversation", "args": text}
