#!/bin/bash
set -e

echo "========================================"
echo "       A1 QUALITY UPGRADE SCRIPT"
echo "========================================"

# 1. Upgrade STT (Vosk Large Model)
# ---------------------------------
echo "[1/2] Upgrading Hearing (Downloading High-Accuracy Model 1.8GB)..."
mkdir -p models
cd models

if [ -d "vosk-model-en-us-0.22" ]; then
    echo "High-accuracy model already exists."
else
    echo "Downloading Vosk Model (1.8GB) - This may take a few minutes..."
    wget -c https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
    echo "Unzipping..."
    unzip -q -o vosk-model-en-us-0.22.zip
    rm vosk-model-en-us-0.22.zip
fi
cd ..

# 2. Upgrade TTS (Piper Neural Voice)
# -----------------------------------
echo "[2/2] Upgrading Voice (Installing Piper Neural TTS)..."
mkdir -p piper
cd piper

# Download Piper Binary (Linux amd64)
if [ ! -f "piper" ]; then
    echo "Downloading Piper Engine..."
    wget -O piper.tar.gz https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz
    tar -xzf piper.tar.gz
    mv piper/piper .
    mv piper/lib* .
    rm -rf piper piper.tar.gz
fi

# Download Voice Model (Ryan - Medium - Very Human)
VOICE_FILE="en_US-ryan-medium.onnx"
if [ ! -f "$VOICE_FILE" ]; then
    echo "Downloading Neural Voice (Ryan)..."
    wget -O "$VOICE_FILE" https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx
    wget -O "$VOICE_FILE.json" https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/medium/en_US-ryan-medium.onnx.json
fi

cd ..

echo "========================================"
echo "       UPGRADE COMPLETE"
echo "========================================"
