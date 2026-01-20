#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}       A1 - SYSTEM SETUP ASSISTANT       ${NC}"
echo -e "${BLUE}=========================================${NC}"

# 1. System Dependencies
echo -e "\n${GREEN}[1/5] Installing System Dependencies...${NC}"
if [ -f /etc/arch-release ]; then
    echo "Detected Arch Linux."
    sudo pacman -Sy --noconfirm python python-pip portaudio espeak-ng unzip curl git
elif [ -f /etc/debian_version ]; then
    echo "Detected Debian/Ubuntu."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv portaudio19-dev espeak-ng curl unzip git
else
    echo -e "${RED}Unsupported Distro. Please install 'python', 'portaudio', 'espeak-ng' manually.${NC}"
fi

# 2. Ollama Setup
echo -e "\n${GREEN}[2/5] Setting up AI Brain (Ollama)...${NC}"
if ! command -v ollama &> /dev/null; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Start Server if needed
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

echo "Pulling models..."
ollama pull llama3.2:3b
ollama pull nomic-embed-text

# 3. Vosk Model (Speech Recognition)
echo -e "\n${GREEN}[3/5] Setting up Hearing (Vosk)...${NC}"
mkdir -p models
cd models

# Check if Large model exists
if [ -d "vosk-model-en-us-0.22" ]; then
    echo "High-Accuracy Model found."
else
    echo -e "${BLUE}Download High-Accuracy Model (1.8GB)? [Y/n]${NC}"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]] || [[ -z "$response" ]]; then
        echo "Downloading Vosk Large Model..."
        wget -c https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
        unzip -q -o vosk-model-en-us-0.22.zip
        rm vosk-model-en-us-0.22.zip
    else
        echo "Downloading Vosk Small Model (Lightweight)..."
        wget -c https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
        unzip -q -o vosk-model-small-en-us-0.15.zip
        rm vosk-model-small-en-us-0.15.zip
    fi
fi
cd ..

# 4. Python Environment
echo -e "\n${GREEN}[4/5] Setting up Python Environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Configuration
echo -e "\n${GREEN}[5/5] Final Configuration...${NC}"
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    touch .env
    echo "# Add API Keys here if you want to use Cloud Models" >> .env
    echo "OPENROUTER_API_KEY=" >> .env
    echo "BYTEZ_API_KEY=" >> .env
fi

echo -e "\n${BLUE}=========================================${NC}"
echo -e "${GREEN}       SETUP COMPLETE! 🚀                ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "To start A1:"
echo -e "  ${GREEN}./venv/bin/python main.py${NC}"
