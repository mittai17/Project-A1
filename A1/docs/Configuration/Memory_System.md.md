---
tags: [configuration, memory, qdrant]
---

# 🧠 Configuration: Memory System

A1 uses **Vector Memory** to retain information indefinitely.

## 🏗️ Schema
Stored in `Qdrant` under the collection `a1_memory`.

| Field | Description | Type |
| :--- | :--- | :--- |
| **id** | UUID | String |
| **vector** | 384-dim embedding | Float Array |
| **payload** | Metadata | JSON |
| **payload.text** | The raw fact | String |
| **payload.timestamp** | Creation time | ISO Date |

## 🧬 Embedding Model
We use **all-minilm** (via Ollama).
- **Dimensions**: 384
- **Size**: ~300MB
- **Speed**: Very fast (<20ms per sentence).

## 🔄 Interaction Flow
1.  **Storage**: User says "My name is Mittai".
    -   A1 extracts "My name is Mittai".
    -   Embeds -> `[0.1, -0.4, ...]`
    -   Upserts to Qdrant.
2.  **Retrieval**: User says "Who am I?"
    -   A1 Embeds "Who am I?" -> `[0.1, -0.3, ...]`
    -   Queries Qdrant for nearest vector.
    -   Retrieves "My name is Mittai".
    -   Feeds into LLM Context.

## 📂 Physical Location
The database is persistent on disk:
`~/Documents/vs-code/Project-a1/A1/memory_db/`

---
## 🕸️ Connections
- Utilized by [[Core/Core_Brain_LLM|Brain]].
- See [[Design/Design_Decisions#4. Why Qdrant?|Design Rationale]].
- Configured via `core/memory.py`.

[[00_Index|🔙 Return to Index]]
