---
tags: [operations, setup]
---

# 🚀 Installation Guide

A guide to deploying A1 on **Arch Linux**.

## 1. Setup Environment
```bash
git clone https://github.com/mittai17/Project-A1.git
cd Project-A1
chmod +x setup.sh
./setup.sh
```

## 2. Pull Models (Ollama)
Required for the Brain and Memory.
```bash
ollama pull llama3.1:8b
ollama pull all-minilm
```

## 3. Configure Voice
Enroll your voice for the `adaptive_asr` module.
```bash
./venv/bin/python core/voice_enroll.py
```

## 4. Run
```bash
./venv/bin/python main.py
```

> [!IMPORTANT] Hardware Reqs
> - **RAM**: 8GB Minimum
> - **GPU**: Recommended (RTX 30 Series+)
> - **Space**: 10GB (Models + Env)
