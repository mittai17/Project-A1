import os
import time
import requests
import uuid
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from colorama import Fore, Style

# Configuration
MEMORY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "memory_db")
COLLECTION_NAME = "a1_memories"
EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_API_URL = "http://localhost:11434/api/embeddings"
VECTOR_SIZE = 768  # nomic-embed-text is 768d

class MemorySystem:
    def __init__(self):
        print(f"{Fore.CYAN}[MEMORY] Initializing Qdrant Memory System...{Style.RESET_ALL}")
        # Initialize local Qdrant instance
        self.client = QdrantClient(path=MEMORY_PATH)
        
        # Ensure collection exists
        self._init_collection()

    def _init_collection(self):
        """Creates the collection if it doesn't exist."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == COLLECTION_NAME for c in collections)
            
            if not exists:
                print(f"{Fore.YELLOW}[MEMORY] Creating new collection '{COLLECTION_NAME}'...{Style.RESET_ALL}")
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                )
        except Exception as e:
            print(f"{Fore.RED}[MEMORY ERROR] Could not verify collection: {e}{Style.RESET_ALL}")

    def _get_embedding(self, text: str) -> List[float]:
        """Generates embedding via Ollama."""
        try:
            response = requests.post(
                OLLAMA_API_URL,
                json={
                    "model": EMBEDDING_MODEL,
                    "prompt": text
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("embedding", [])
            else:
                print(f"{Fore.RED}[MEMORY ERROR] Embedding failed: {response.text}{Style.RESET_ALL}")
                return []
        except Exception as e:
            print(f"{Fore.RED}[MEMORY ERROR] Embedding request failed: {e}{Style.RESET_ALL}")
            return []

    def add_memory(self, text: str, source: str = "user", memory_type: str = "fact"):
        """
        Stores a new semantic memory.
        """
        vector = self._get_embedding(text)
        if not vector:
            return False

        metadata = {
            "text": text,  # Store text in payload since we use vector search
            "timestamp": time.time(),
            "source": source,
            "type": memory_type,
            "date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        point_id = str(uuid.uuid4())
        
        try:
            self.client.upsert(
                collection_name=COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=metadata
                    )
                ]
            )
            print(f"{Fore.GREEN}[MEMORY] Stored: '{text}'{Style.RESET_ALL}")
            return True
        except Exception as e:
            print(f"{Fore.RED}[MEMORY ERROR] Failed to add memory: {e}{Style.RESET_ALL}")
            return False

    def retrieve_relevant(self, query: str, limit: int = 3) -> List[str]:
        """
        Retrieves the most relevant memories for a given query.
        """
        vector = self._get_embedding(query)
        if not vector:
            return []

        try:
            results = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=vector,
                limit=limit
            ).points
            
            # Extract text from payload
            memories = []
            for res in results:
                # Only return relevant matches
                if res.score > 0.4:  # Threshold for relevance
                    text = res.payload.get("text", "")
                    memories.append(text)
            
            if memories:
                print(f"{Fore.CYAN}[MEMORY] Found {len(memories)} relevant facts.{Style.RESET_ALL}")
            return memories
            
        except Exception as e:
            print(f"{Fore.RED}[MEMORY ERROR] Search failed: {e}{Style.RESET_ALL}")
            return []

    def get_stats(self):
        try:
            info = self.client.get_collection(COLLECTION_NAME)
            return info
        except:
            return None

# Global instance
memory = MemorySystem()

