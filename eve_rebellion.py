"""
EVE Rebellion - Entry point module for installed package.

This module serves as the entry point when the game is installed via pip.
"""

from platform_init import init_platform


def main():
    """Main entry point for the game."""
    init_platform()

    from game import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
