#!/bin/bash
set -e
RED="[0;31m"; GREEN="[0;32m"; YELLOW="[1;33m"
BLUE="[0;34m"; PURPLE="[0;35m"; CYAN="[0;36m"; NC="[0m"

clear
echo -e ""
echo "========================================="
echo "  🎬 Anime WhatsApp Bot - Auto Setup"
echo "========================================="
echo -e ""

echo -e "[1/4] Updating packages..."
if [ -d "/data/data/com.termux" ]; then
    yes | pkg update -y 2>/dev/null
    yes | pkg upgrade -y 2>/dev/null
    pkg install -y python git ffmpeg chromium wget curl build-essential libxml2 libxslt 2>/dev/null
else
    sudo apt update -y && sudo apt install -y python3 python3-pip git ffmpeg chromium-browser wget 2>/dev/null
fi

echo -e "[2/4] Installing Python packages..."
pip install --upgrade pip 2>/dev/null
pip install -r requirements.txt 2>/dev/null

echo -e "[3/4] Creating directories..."
mkdir -p downloads compressed temp session logs

echo -e "[4/4] Done!"
echo ""
echo -e "✅ Installation complete!"
echo ""
echo "🚀 To start: python main.py"
echo "   Or: bash run.sh"
echo ""
read -p "Start now? (y/n): " -n 1 -r
echo
if [[ \ =~ ^[Yy]\$ ]]; then bash run.sh; fi