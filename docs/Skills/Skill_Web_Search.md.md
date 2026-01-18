---
tags: [skill, web, search]
---

# 🌐 Skill: Web Search

Allows A1 to query the internet for real-time information.

## ⚙️ Backend
- **Provider**: DuckDuckGo (DDG)
- **Library**: `duckduckgo_search` (Python)
- **Privacy**: High (No tracking).

## 🔄 Workflow

1.  **Query Generation**: The Brain converts "What's the score of the match?" into a search keyword: `cricket match score live`.
2.  **Execution**:
    -   `ddgs.text(keywords, max_results=3)`
3.  **Parses**:
    -   Title
    -   URL
    -   Snippet (Summary)
4.  **Synthesis**: The Brain reads the snippets and constructs a fluent answer.

## 📝 Example
**User**: "Who won the 2024 F1 championship?"
**Tool Output**:
> 1. Max Verstappen secures 2024 title...
> 2. F1 Standings 2024...
**Brain**: "Max Verstappen won the 2024 Formula 1 Championship."

---
## 🕸️ Connections
- Used by [[Core/Core_Brain_LLM|Brain]] via MCP/Tools.
- Part of the [[System/Architecture_ReAct_Loop|ReAct Loop]].

[[00_Index|🔙 Return to Index]]
