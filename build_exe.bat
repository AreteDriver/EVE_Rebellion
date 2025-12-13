@echo off
REM Build script for EVE Rebellion Windows Executable
REM This script creates a standalone .exe file of the game

echo ========================================
echo EVE Rebellion Build Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building executable...
pyinstaller --clean EVE_Rebellion.spec

if errorlevel 1 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo The executable can be found at:
echo   dist\EVE_Rebellion.exe
echo.
echo You can now distribute this file to users.
echo They don't need Python or any dependencies installed.
echo.
pause
