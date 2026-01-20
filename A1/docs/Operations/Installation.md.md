---
tags: [operations, setup, installation]
---

# 🚀 Installation Guide

A guide to deploying A1 on **Arch Linux** with full XTTS v2 voice cloning support.

## Prerequisites

| Requirement | Version | Notes |
| :--- | :--- | :--- |
| **OS** | Arch Linux | (or Manjaro, EndeavourOS) |
| **Python** | 3.11.x | Required for XTTS v2 |
| **RAM** | 8GB+ | 16GB recommended |
| **GPU** | RTX 30+ | Optional, but speeds up TTS |
| **Storage** | 15GB+ | Models + Environment |

---

## 1. Install pyenv (Python Version Manager)

```bash
# Install pyenv
yay -S pyenv

# Add to shell (add these to ~/.zshrc or ~/.bashrc)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

## 2. Install Python 3.11

```bash
# Install Python 3.11.11
pyenv install 3.11.11

# Verify installation
~/.pyenv/versions/3.11.11/bin/python --version
```

## 3. Clone & Setup Project

```bash
git clone https://github.com/mittai17/Project-A1.git
cd Project-A1/A1

# Create virtual environment with Python 3.11
~/.pyenv/versions/3.11.11/bin/python -m venv venv

# Activate and install dependencies
./venv/bin/pip install --upgrade pip wheel setuptools
./venv/bin/pip install -r requirements.txt
```

## 4. Pull Ollama Models

```bash
# LLM Brain
ollama pull llama3.1:8b

# Embedding Model (for Memory)
ollama pull all-minilm
```

## 5. Configure Voice Enrollment

```bash
# Enroll your voice for speaker recognition
./venv/bin/python core/voice_enroll.py
```

## 6. Setup XTTS Voice Cloning (Optional)

> [!TIP] For Personalized Voice
> Record a **5-15 second WAV file** of your voice and place it at:
> ```
> A1/models/speaker.wav
> ```
> See [[XTTS_Setup|XTTS Setup Guide]] for detailed instructions.

## 7. Run A1

```bash
./venv/bin/python main.py
```

---

## 🔧 Quick Verify

```bash
# Check Python version
./venv/bin/python --version  # Should be 3.11.x

# Check TTS is available
./venv/bin/python -c "from TTS.api import TTS; print('XTTS Ready!')"

# Check Ollama
ollama list  # Should show llama3.1:8b
```

---

## 🕸️ Connections
- [[XTTS_Setup|XTTS Voice Cloning Setup]]
- [[Operations/Troubleshooting|Troubleshooting]]
- [[Operations/Runbook|Daily Usage]]

[[00_Index|🔙 Return to Index]]
