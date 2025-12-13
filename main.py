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
"""

from game import Game


def main():
    """Main entry point for the game"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
