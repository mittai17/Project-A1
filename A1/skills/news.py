import feedparser
from colorama import Fore, Style

# RSS Feeds
FEEDS = {
    "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "tech": "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "hackernews": "https://hnrss.org/frontpage"
}

def get_latest_news(category="world", limit=3):
    """
    Fetches the latest news headlines from RSS feeds.
    Args:
        category: 'world', 'tech', or 'hackernews'
        limit: Number of headlines to return
    """
    url = FEEDS.get(category, FEEDS["world"])
    print(f"{Fore.CYAN}[NEWS] Fetching {category} news...{Style.RESET_ALL}")
    
    try:
        feed = feedparser.parse(url)
        if not feed.entries:
            return "No news found currently."
            
        headlines = []
        for i, entry in enumerate(feed.entries):
            if i >= limit:
                break
            headlines.append(f"- {entry.title}")
            
        return f"Here are the top {category} headlines:\n" + "\n".join(headlines)
    except Exception as e:
        return f"Failed to fetch news: {e}"

def get_tech_news():
    return get_latest_news("tech")
