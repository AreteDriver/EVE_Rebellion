#!/bin/bash
# Minmatar Rebellion Game Launcher
cd "$(dirname "$0")"

# Force SDL to use raw joystick device (fixes Xbox Series X controller)
export SDL_JOYSTICK_DEVICE=/dev/input/js0

python3 game.py "$@"
