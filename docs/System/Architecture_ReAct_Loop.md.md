---
tags: [system, react, logic]
---

# 🔄 The ReAct Loop Architecture

**ReAct** stands for **Reason + Act**. It is the logic pattern that allows A1 to use tools.

## The Prompt Structure
The Brain is fed a system prompt that enforces this loop:

```text
Thought: [Internal Monologue]
Action: [Tool Name]
Input: [Arguments]
Observation: [Result from Tool]
... (Repeat) ...
Final Answer: [Response to User]
```

## Trace Example: "What is the weather?"

1.  **User**: "Check the weather in Chennai."
2.  **Brain**:
    ```text
    Thought: The user wants weather data. I should use the search tool.
    Action: search_web
    Input: {"query": "weather in Chennai right now"}
    ```
3.  **System (Python)**:
    -   Intercepts `search_web`.
    -   Calls DuckDuckGo API.
    -   Returns: `"Chennai: 32°C, Sunny, Humidity 70%"`
4.  **Brain**:
    ```text
    Observation: Chennai: 32°C, Sunny, Humidity 70%
    Thought: I have the data. I can answer now.
    Final Answer: It is currently 32°C and Sunny in Chennai.
    ```
5.  **TTS**: Speaks the "Final Answer".

## Handling Failures
If a tool fails (e.g., No Internet), the system injects an error message into the Observation.
-   **Observation**: `Error: Connection Timeout`
-   **Brain**: "Thought: Search failed. I will apologize." -> "Final Answer: I cannot check the weather right now."
