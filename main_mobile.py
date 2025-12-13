#!/usr/bin/env python3
"""
MINMATAR REBELLION - MOBILE EDITION
A Top-Down Arcade Space Shooter for Mobile/Web

This version includes:
- Touch controls (virtual joystick + buttons)
- Mobile-optimized screen size
- Web/mobile deployment via Pygbag

To build for web/mobile:
    pip install pygbag
    pygbag main_mobile.py

Controls (Touch):
    Left Joystick - Move
    FIRE Button - Fire Autocannons
    RKT Button - Fire Rockets
    1-5 Buttons - Select Ammo Type
    Pause Button - Pause Game
"""

import asyncio
from game_mobile import MobileGame


async def main():
    """Async main entry point for Pygbag compatibility"""
    game = MobileGame()
    await game.run_async()


if __name__ == "__main__":
    asyncio.run(main())
