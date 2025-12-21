@echo off
echo ========================================
echo   MINMATAR REBELLION - INSTALLER
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is NOT installed
    echo.
    echo Please install Python first:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download Python 3.8 or newer
    echo 3. Run installer and CHECK "Add Python to PATH"
    echo 4. Run this installer again
    echo.
    pause
    exit /b 1
) else (
    echo [OK] Python is installed
)

echo.
echo Installing game dependencies...
echo This will install: pygame, numpy, and cairosvg
echo (cairosvg enables actual EVE ship graphics!)
echo.

pip install pygame numpy cairosvg

if errorlevel 1 (
    echo.
    echo [X] Installation failed!
    echo.
    echo Try running Command Prompt as Administrator
    echo and run this installer again.
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [OK] Installation complete!
echo ========================================
echo.
echo You can now run the game by:
echo   - Double-clicking PLAY_GAME.bat
echo   - Or running: python main.py
echo.
echo Have fun, pilot!
echo.
pause
