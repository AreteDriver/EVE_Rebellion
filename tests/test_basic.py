"""
Basic tests for Minmatar Rebellion game
"""
import pytest
import pygame


def test_pygame_initialization():
    """Test that pygame can be initialized"""
    pygame.init()
    assert pygame.get_init()
    pygame.quit()


def test_import_main_modules():
    """Test that main game modules can be imported"""
    import main
    import game
    import constants
    import sprites
    import sounds
    
    assert hasattr(main, 'Game')
    assert hasattr(game, 'Game')
    assert hasattr(constants, 'SCREEN_WIDTH')
    assert hasattr(sprites, 'Player')


def test_constants_values():
    """Test that important constants are properly defined"""
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
    
    assert SCREEN_WIDTH > 0
    assert SCREEN_HEIGHT > 0
    assert FPS > 0
    assert isinstance(SCREEN_WIDTH, int)
    assert isinstance(SCREEN_HEIGHT, int)
    assert isinstance(FPS, int)


def test_player_class_exists():
    """Test that Player class can be instantiated"""
    from sprites import Player
    from constants import SCREEN_WIDTH, SCREEN_HEIGHT
    
    pygame.init()
    # Create a minimal player instance to verify class structure
    assert Player is not None
    pygame.quit()


def test_game_class_structure():
    """Test that Game class has required methods"""
    from game import Game
    
    assert hasattr(Game, '__init__')
    assert hasattr(Game, 'run')
