import sys
import os
from qdrant_client import QdrantClient
from colorama import init, Fore, Style

init()

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_PATH = os.path.join(BASE_DIR, "memory_db")
COLLECTION_NAME = "a1_memories_v2"

def view_memories():
    if not os.path.exists(MEMORY_PATH):
        print(f"{Fore.RED}No memory database found at {MEMORY_PATH}{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}Connecting to Qdrant at: {MEMORY_PATH}{Style.RESET_ALL}")
    try:
        client = QdrantClient(path=MEMORY_PATH)
        
        print(f"{Fore.YELLOW}--- A1 Memory Dump ({COLLECTION_NAME}) ---{Style.RESET_ALL}")
        
        # Scroll API to get all points (Batch 100)
        records, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=100,
            with_payload=True,
            with_vectors=False
        )
        
        if not records:
            print("Memory is empty.")
            return

        print(f"{Fore.GREEN}Found {len(records)} memories:{Style.RESET_ALL}\n")

        for record in records:
            p = record.payload
            date = p.get('date', 'No Date')
            m_type = p.get('type', 'fact')
            text = p.get('text', '')
            
            # Color code types
            color = Fore.WHITE
            if m_type == "fact": color = Fore.BLUE
            elif m_type == "feedback": color = Fore.MAGENTA
            
            print(f"{Fore.CYAN}[{date}]{Style.RESET_ALL} {color}({m_type}){Style.RESET_ALL} : {text}")
            
    except Exception as e:
        print(f"{Fore.RED}Error reading memory: {e}\n(Ensure A1 is not locking the DB if using SQLite mode?){Style.RESET_ALL}")
        # Note: Local Qdrant (SQLite) usually handles concurrency okay for reads, but good to note.

if __name__ == "__main__":
    view_memories()
