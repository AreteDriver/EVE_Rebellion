#!/bin/bash
#
# EVE Rebellion - Portable Launcher Script
#
# This script allows the game to be run directly after unpacking,
# without requiring installation via pip.
#
# Usage:
#   ./run_game.sh              - Run the game
#   ./run_game.sh --wayland    - Force Wayland mode
#   ./run_game.sh --x11        - Force X11 mode
#   ./run_game.sh --debug      - Show platform debug info
#
# Environment variables:
#   SDL_VIDEODRIVER    - Override video driver (wayland, x11)
#   EVE_REBELLION_DEBUG - Enable debug output
#

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Export the game root for portable path resolution
export EVE_REBELLION_ROOT="$SCRIPT_DIR"

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --wayland)
            export SDL_VIDEODRIVER=wayland
            echo "Forcing Wayland video driver"
            ;;
        --x11)
            export SDL_VIDEODRIVER=x11
            echo "Forcing X11 video driver"
            ;;
        --debug)
            export EVE_REBELLION_DEBUG=1
            ;;
        --help|-h)
            echo "EVE Rebellion - Portable Launcher"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --wayland    Force Wayland video driver"
            echo "  --x11        Force X11 video driver"
            echo "  --debug      Show platform debug information"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Environment Variables:"
            echo "  SDL_VIDEODRIVER     Override video driver"
            echo "  EVE_REBELLION_DEBUG Enable debug output"
            echo ""
            exit 0
            ;;
    esac
done

# Find Python interpreter
find_python() {
    # Check for python3 first, then python
    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            # Verify it's Python 3.9+
            version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
            major=$(echo "$version" | cut -d. -f1)
            minor=$(echo "$version" | cut -d. -f2)
            if [ "$major" -ge 3 ] && [ "$minor" -ge 9 ]; then
                echo "$cmd"
                return 0
            fi
        fi
    done
    return 1
}

PYTHON=$(find_python)
if [ -z "$PYTHON" ]; then
    echo "Error: Python 3.9+ is required but not found."
    echo "Please install Python 3.9 or later."
    exit 1
fi

# Check for required dependencies
check_deps() {
    "$PYTHON" -c "import pygame" 2>/dev/null || return 1
    "$PYTHON" -c "import numpy" 2>/dev/null || return 1
    return 0
}

if ! check_deps; then
    echo "Missing dependencies. Attempting to install..."

    # Try to install from requirements.txt
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        "$PYTHON" -m pip install --user -r "$SCRIPT_DIR/requirements.txt"
    else
        "$PYTHON" -m pip install --user pygame numpy
    fi

    # Verify installation
    if ! check_deps; then
        echo "Error: Failed to install required dependencies."
        echo "Please run: pip install pygame numpy"
        exit 1
    fi
fi

# Change to game directory and run
cd "$SCRIPT_DIR"
exec "$PYTHON" main.py "$@"
