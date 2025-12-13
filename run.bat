@echo off
REM Quick start script for Minmatar Rebellion on Windows

echo Checking dependencies...

python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

python -c "import pygame" 2>nul
if errorlevel 1 (
    echo pygame not found. Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Failed to install dependencies.
        echo Please run manually: pip install -r requirements.txt
        pause
        exit /b 1
    )
)

echo Starting Minmatar Rebellion...
python main.py
pause
