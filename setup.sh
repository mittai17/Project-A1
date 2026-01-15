#!/bin/bash
set -e

# A1 Assistant Setup Script
# Handles: System deps, Ollama, Models (LLM + Vosk), Python Venv

echo "========================================="
echo "       A1 SYSTEM SETUP ASSISTANT"
echo "========================================="

# 1. Detect Distro and Install System Deps
echo "[1/6] Installing System Dependencies..."
if [ -f /etc/arch-release ]; then
    echo "Detected Arch Linux."
    # Check if yay or paru exists for AUR (optional better handling) but stick to pacman
    sudo pacman -Sy --noconfirm python python-pip portaudio espeak-ng unzip curl
elif [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv portaudio19-dev espeak-ng curl unzip
else
    echo "Unsupported Distro. Please install 'portaudio' and 'espeak' manually."
fi

# 2. Install Ollama
echo "[2/6] Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama is already installed."
fi

# 3. Start Ollama and Pull Model
echo "[3/6] Setting up AI Brain (Llama 3.2)..."
# Start ollama server in background if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve > /dev/null 2>&1 &
    PID_OLLAMA=$!
    sleep 5 # Give it time to start
else
    echo "Ollama server is running."
fi

echo "Pulling llama3.2:3b (this may take a while)..."
ollama pull llama3.2:3b

# 4. Download Vosk Model
echo "[4/6] Setting up Ear (Vosk Model)..."
mkdir -p models
if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
    cd models
    echo "Downloading model..."
    wget -nc https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    echo "Unzipping..."
    unzip -o vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    cd ..
else
    echo "Vosk model already exists."
fi

# 5. Python Environment
echo "[5/6] Setting up Python Environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate and Install
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Final Check
echo "[6/6] Verifying..."
echo "-----------------------------------------"
echo "System Audio:"
if command -v espeak-ng &> /dev/null; then echo " [OK] espeak-ng"; else echo " [FAIL] espeak-ng missing"; fi

echo "AI Models:"
if ollama list | grep -q "llama3.2:3b"; then echo " [OK] Llama 3.2"; else echo " [FAIL] Llama 3.2 missing"; fi
if [ -d "models/vosk-model-small-en-us-0.15" ]; then echo " [OK] Vosk Model"; else echo " [FAIL] Vosk Model missing"; fi
echo "-----------------------------------------"

echo "SETUP COMPLETE!"
echo "To run A1:"
echo "  source venv/bin/activate"
echo "  python main.py"
