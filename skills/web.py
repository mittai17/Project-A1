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
