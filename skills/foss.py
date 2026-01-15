import requests
from colorama import Fore, Style

def find_opensource(query):
    """
    Searches GitHub for open source repositories.
    """
    print(f"{Fore.CYAN}[FOSS] Searching GitHub for '{query}'...{Style.RESET_ALL}")
    try:
        # Search GitHub API
        url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
        res = requests.get(url, timeout=10)
        
        if res.status_code != 200:
             return f"GitHub API Error: {res.status_code}"

        data = res.json()
        items = data.get("items", [])[:3]
        
        if not items:
            return f"I couldn't find any open source projects for '{query}'."
            
        summary = f"Here are the top open source projects for '{query}':\n\n"
        for item in items:
            name = item['full_name']
            desc = item.get('description', 'No description')
            stars = item.get('stargazers_count', 0)
            url = item.get('html_url', '#')
            summary += f"- **{name}** ({stars} stars)\n  {desc}\n  Link: {url}\n\n"
            
        return summary
    except Exception as e:
        print(f"{Fore.RED}[FOSS ERROR] {e}{Style.RESET_ALL}")
        return "I encountered an error accessing GitHub."

def find_alternatives(tool_name):
    """
    Uses generic web search to find open source alternatives.
    """
    # This can be routed to brain or web search, but having a helper is nice.
    # For now, we will just use the main search logic via the assistant.
    pass
