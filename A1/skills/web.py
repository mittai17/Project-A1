from duckduckgo_search import DDGS
from colorama import Fore, Style
import warnings

# Suppress the specific package rename warning if it appears
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")

def search_web(query: str):
    """Performs a web search and returns a summary."""
    print(f"{Fore.CYAN}[WEB] Searching for: {query}...{Style.RESET_ALL}")
    
    try:
        # DDGS().text returned a list in older versions, generator in newer
        # We convert to list to safely handle both
        results = list(DDGS().text(query, max_results=3))
        
        if not results:
            return "No results found."
        
        summary = "Here is what I found:\n"
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n"
            
        return summary
    except Exception as e:
        print(f"{Fore.RED}[WEB ERROR] Search failed: {e}{Style.RESET_ALL}")
        return "I cannot access the internet right now."

def play_youtube(query: str):
    """
    Opens YouTube with the search query.
    """
    import subprocess
    import urllib.parse
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"
    
    print(f"{Fore.CYAN}[WEB] Opening YouTube: {query}{Style.RESET_ALL}")
    
    # Try using xdg-open which works on most Linux DEs
    subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"Playing {query} on YouTube."

def play_apple_music(query: str):
    """
    Opens Apple Music with the search query.
    """
    import subprocess
    import urllib.parse
    
    encoded_query = urllib.parse.quote(query)
    url = f"https://music.apple.com/us/search?term={encoded_query}"
    
    print(f"{Fore.CYAN}[WEB] Opening Apple Music: {query}{Style.RESET_ALL}")
    
    subprocess.Popen(['xdg-open', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return f"Playing {query} on Apple Music."
