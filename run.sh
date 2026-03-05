#!/bin/bash
cd "."
echo "🎬 Starting Anime Bot..."
while true; do
    python main.py 2>&1 | tee -a logs/bot.log
    echo "⚠️ Restarting in 5s..."
    sleep 5
done