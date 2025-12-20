@echo off
echo ========================================
echo   MINMATAR REBELLION
echo   Windows Launcher
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python detected!
echo.

REM Check if pygame is installed
python -c "import pygame" >nul 2>&1
if errorlevel 1 (
    echo Installing game dependencies...
    echo This only needs to happen once.
    echo.
    pip install pygame numpy cairosvg
    echo.
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies!
        echo Try running: pip install pygame numpy cairosvg
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully!
    echo.
)

echo Starting game...
echo.
echo Controls:
echo   WASD / Arrow Keys - Move
echo   Space - Fire
echo   Shift - Rockets
echo   ESC - Pause
echo.
echo ========================================
echo.

REM Launch the game
python main.py

REM If game exits with error
if errorlevel 1 (
    echo.
    echo ========================================
    echo Game exited with an error.
    echo Check the error message above.
    echo ========================================
    echo.
)

pause
