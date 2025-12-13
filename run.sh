#!/bin/bash
# Quick start script for Minmatar Rebellion on Linux/macOS

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if dependencies are installed
echo "Checking dependencies..."
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "pygame not found. Installing dependencies..."
    pip3 install -r requirements.txt || {
        echo "Failed to install dependencies. Please run: pip3 install -r requirements.txt"
        exit 1
    }
fi

# Run the game
echo "Starting Minmatar Rebellion..."
python3 main.py
