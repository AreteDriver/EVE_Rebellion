#!/usr/bin/env python3
"""
MINMATAR REBELLION
A Top-Down Arcade Space Shooter

Inspired by EVE Online - Personal Project

Controls:
  WASD / Arrow Keys - Move
  Space / Left Click - Fire Autocannons
  Shift / Right Click - Fire Rockets
  1-5 - Select Ammo Type
  Q / Tab - Cycle Ammo
  ESC - Pause

Environment Variables:
  SDL_VIDEODRIVER - Override video driver (wayland, x11, etc.)
  EVE_REBELLION_DEBUG - Show platform debug info on startup
"""

import os
import sys

# Show platform info if debug mode is requested
if os.environ.get("EVE_REBELLION_DEBUG") or "--debug" in sys.argv:
    from platform_init import init_platform, print_platform_info

    init_platform()
    print_platform_info()

from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
