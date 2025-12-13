#!/bin/bash
# Build script for EVE Rebellion
# This script creates a standalone executable of the game

echo "========================================"
echo "EVE Rebellion Build Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Building executable..."
pyinstaller --clean EVE_Rebellion.spec

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Build completed successfully!"
echo "========================================"
echo ""
echo "The executable can be found at:"
echo "  dist/EVE_Rebellion"
echo ""
echo "You can now distribute this file to users."
echo ""
