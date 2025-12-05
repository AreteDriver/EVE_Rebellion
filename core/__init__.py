"""Core module for Minmatar Rebellion.

This module provides foundational functionality including:
- Control bindings management (keyboard/gamepad)
- Configuration loading/saving
"""

from .controls import (
    ControlsManager,
    load_controls,
    save_controls,
    get_keyboard_keys,
    get_mouse_button,
    get_gamepad_binding,
    get_gamepad_deadzone,
    DEFAULT_CONTROLS
)

__all__ = [
    'ControlsManager',
    'load_controls',
    'save_controls',
    'get_keyboard_keys',
    'get_mouse_button',
    'get_gamepad_binding',
    'get_gamepad_deadzone',
    'DEFAULT_CONTROLS'
]
