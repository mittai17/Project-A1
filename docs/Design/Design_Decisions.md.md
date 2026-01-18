---
tags: [design, architecture, decision-log]
---

# 📐 Design Decisions

> [!NOTE] Philosophy
> "Privacy > Latency > Features". A1 is designed to run on **your** hardware, not a server.

## 1. Why Llama 3.1 8B?
We initially tested `Llama 3.2 3B` and `Qwen 2.5 7B`.

- **Vs 3B Models**: 3B models (like Llama 3.2) hallucinated heavily during tool use. They would invent tool arguments.
- **Vs Qwen**: Qwen is excellent at coding but its "Generic Chat" personality is robotic.
- **Decision**: **Llama 3.1 8B** (Quantized q4_0) offers the best balance. It follows ReAct instructions perfectly and fits in 6GB VRAM.

## 2. Why Piper TTS?
We tried `Coqui XTTS v2` and `Bark`.

- **Coqui XTTS**: Amazing quality, but ~2-3s latency on CPU. Needs GPU for real-time.
- **Piper**: <200ms latency on CPU. " Robotic" but functional.
- **Decision**: **Piper** is the only viable option for a "Snappy" assistant on consumer hardware. We use the `te_IN` model to mitigate the "American Robot" feel.

## 3. Why Rule-Based Router?
We removed the "AI Router" (using a small BERT model) in v1.2.

- **Reason**: Latency. An AI classification step adds ~500ms.
- **Solution**: **Regex**. It is instant (0ms).
- **Trade-off**: Slightly less flexible (user must say specific keywords), but the speed gain makes the system feel much more responsive.

## 4. Why Qdrant?
- **Vs ChromaDB**: Chroma is easier to setup but significantly slower at scale.
- **Vs JSON Files**: Qdrant offers vector similarity search, which is essential for "Fuzzy Memory" (finding facts that are *similar*, not just identical).
