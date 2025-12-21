@echo off
title Minmatar Rebellion
echo ========================================
echo   MINMATAR REBELLION
echo ========================================
echo.
echo Starting game...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   ERROR: Python not found!
    echo ========================================
    echo.
    echo Please install Python from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH"
    echo during installation!
    echo.
    pause
) else (
    echo.
    echo Game closed.
    pause
)
