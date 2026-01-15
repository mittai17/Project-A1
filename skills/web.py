from duckduckgo_search import DDGS
from colorama import Fore, Style

def search_web(query: str):
    """Performs a web search and returns a summary."""
    print(f"{Fore.CYAN}[WEB] Searching for: {query}...{Style.RESET_ALL}")
    
    try:
        results = DDGS().text(query, max_results=3)
        if not results:
            return "No results found."
        
        summary = "Here is what I found:\n"
        for r in results:
            summary += f"- {r['title']}: {r['body']}\n"
            
        return summary
    except Exception as e:
        print(f"{Fore.RED}[WEB ERROR] Search failed: {e}{Style.RESET_ALL}")
        return "I cannot access the internet right now."
