#!/bin/bash

# RajXStars Bot Runner Script

echo "🌟 Starting RajXStars Telegram Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies."
        exit 1
    fi
    echo "✅ Dependencies installed successfully."
else
    echo "⚠️  requirements.txt not found. Make sure all dependencies are installed."
fi

# Check if config.py exists
if [ ! -f "config.py" ]; then
    echo "❌ config.py not found. Please create config.py with your bot credentials."
    exit 1
fi

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ main.py not found. Please ensure all bot files are present."
    exit 1
fi

# Run the bot
echo "🚀 Starting bot..."
python3 main.py

# If bot stops, show message
echo "🔄 Bot stopped. Check logs for any errors."