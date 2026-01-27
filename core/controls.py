"""Control bindings manager for Minmatar Rebellion.

This module provides infrastructure for loading, saving, and managing
keyboard and gamepad control bindings from config/controls.json.
"""

import json
import os
from pathlib import Path

# Maximum allowed config file size (64KB should be plenty for control bindings)
MAX_CONFIG_SIZE = 65536


# Default control bindings used when config file is missing or invalid
DEFAULT_CONTROLS = {
    "version": "1.0",
    "keyboard": {
        "move_left": ["K_LEFT", "K_a"],
        "move_right": ["K_RIGHT", "K_d"],
        "move_up": ["K_UP", "K_w"],
        "move_down": ["K_DOWN", "K_s"],
        "fire": ["K_SPACE"],
        "fire_rocket": ["K_LSHIFT", "K_RSHIFT"],
        "special_ammo_1": ["K_1"],
        "special_ammo_2": ["K_2"],
        "special_ammo_3": ["K_3"],
        "special_ammo_4": ["K_4"],
        "special_ammo_5": ["K_5"],
        "cycle_ammo": ["K_q", "K_TAB"],
        "pause": ["K_ESCAPE"],
    },
    "mouse": {"fire": "BUTTON_LEFT", "fire_rocket": "BUTTON_RIGHT"},
    "gamepad": {
        "move_left": {"type": "axis", "axis": 0, "direction": -1},
        "move_right": {"type": "axis", "axis": 0, "direction": 1},
        "move_up": {"type": "axis", "axis": 1, "direction": -1},
        "move_down": {"type": "axis", "axis": 1, "direction": 1},
        "fire": {"type": "button", "button": 0},
        "fire_rocket": {"type": "button", "button": 1},
        "cycle_ammo": {"type": "button", "button": 2},
        "pause": {"type": "button", "button": 7},
    },
    "gamepad_deadzone": 0.15,
}


def _get_config_path():
    """Get the path to the controls configuration file."""
    module_dir = Path(__file__).parent.parent
    return module_dir / "config" / "controls.json"


def _get_config_dir():
    """Get the path to the config directory."""
    module_dir = Path(__file__).parent.parent
    return module_dir / "config"


def _is_safe_path(config_path, base_dir=None):
    """Check if config_path is within the allowed directory.

    Args:
        config_path: Path to validate.
        base_dir: Base directory that config_path must be within.
                  If None, uses the default config directory.

    Returns:
        bool: True if path is safe, False otherwise.
    """
    if base_dir is None:
        base_dir = _get_config_dir()

    try:
        config_path = Path(config_path).resolve()
        base_dir = Path(base_dir).resolve()
        return str(config_path).startswith(str(base_dir))
    except (ValueError, OSError):
        return False


def load_controls(config_path=None):
    """Load control bindings from the config file.

    Args:
        config_path: Optional path to config file. If None, uses default location.

    Returns:
        dict: Control bindings dictionary with keyboard, mouse, and gamepad mappings.
    """
    if config_path is None:
        config_path = _get_config_path()

    try:
        # Validate file size to prevent memory exhaustion
        file_size = os.path.getsize(config_path)
        if file_size > MAX_CONFIG_SIZE:
            return DEFAULT_CONTROLS.copy()

        with open(config_path, "r", encoding="utf-8") as f:
            controls = json.load(f)
        # Validate required sections exist
        if not all(key in controls for key in ["keyboard", "mouse", "gamepad"]):
            return DEFAULT_CONTROLS.copy()
        return controls
    except (FileNotFoundError, json.JSONDecodeError, IOError, OSError):
        return DEFAULT_CONTROLS.copy()


def save_controls(controls, config_path=None):
    """Save control bindings to the config file.

    Args:
        controls: Control bindings dictionary to save.
        config_path: Optional path to config file. If None, uses default location.

    Returns:
        bool: True if save was successful, False otherwise.
    """
    if config_path is None:
        config_path = _get_config_path()

    # Validate path is within allowed directory
    if not _is_safe_path(config_path):
        return False

    try:
        config_path = Path(config_path)
        # Ensure config directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(controls, f, indent=4)
        return True
    except (IOError, OSError):
        return False


def get_keyboard_keys(controls, action):
    """Get the list of keyboard keys bound to an action.

    Args:
        controls: Control bindings dictionary.
        action: Action name (e.g., 'move_left', 'fire').

    Returns:
        list: List of pygame key constant names (e.g., ['K_LEFT', 'K_a']).
    """
    return controls.get("keyboard", {}).get(action, [])


def get_mouse_button(controls, action):
    """Get the mouse button bound to an action.

    Args:
        controls: Control bindings dictionary.
        action: Action name.

    Returns:
        str or None: Mouse button name or None if not bound.
    """
    return controls.get("mouse", {}).get(action)


def get_gamepad_binding(controls, action):
    """Get the gamepad binding for an action.

    Args:
        controls: Control bindings dictionary.
        action: Action name.

    Returns:
        dict or None: Gamepad binding dict with 'type', 'axis'/'button', etc.
    """
    return controls.get("gamepad", {}).get(action)


def get_gamepad_deadzone(controls):
    """Get the gamepad stick deadzone value.

    Args:
        controls: Control bindings dictionary.

    Returns:
        float: Deadzone value (0.0 to 1.0).
    """
    return controls.get("gamepad_deadzone", 0.15)


class ControlsManager:
    """Manager class for handling control bindings.

    This class provides a convenient interface for loading, accessing,
    and modifying control bindings at runtime.

    Usage:
        manager = ControlsManager()
        manager.load()

        # Get keyboard keys for an action
        move_left_keys = manager.get_keyboard_keys('move_left')

        # Check if a gamepad is configured for an action
        fire_binding = manager.get_gamepad_binding('fire')
    """

    def __init__(self):
        self._controls = DEFAULT_CONTROLS.copy()
        self._loaded = False

    def load(self, config_path=None):
        """Load controls from config file.

        Args:
            config_path: Optional custom config file path.
        """
        self._controls = load_controls(config_path)
        self._loaded = True

    def save(self, config_path=None):
        """Save current controls to config file.

        Args:
            config_path: Optional custom config file path.

        Returns:
            bool: True if save was successful.
        """
        return save_controls(self._controls, config_path)

    def get_keyboard_keys(self, action):
        """Get keyboard keys for an action."""
        return get_keyboard_keys(self._controls, action)

    def get_mouse_button(self, action):
        """Get mouse button for an action."""
        return get_mouse_button(self._controls, action)

    def get_gamepad_binding(self, action):
        """Get gamepad binding for an action."""
        return get_gamepad_binding(self._controls, action)

    def get_gamepad_deadzone(self):
        """Get gamepad deadzone value."""
        return get_gamepad_deadzone(self._controls)

    def set_keyboard_binding(self, action, keys):
        """Set keyboard binding for an action.

        Args:
            action: Action name.
            keys: List of pygame key constant names.
        """
        if "keyboard" not in self._controls:
            self._controls["keyboard"] = {}
        self._controls["keyboard"][action] = keys

    def set_gamepad_binding(self, action, binding):
        """Set gamepad binding for an action.

        Args:
            action: Action name.
            binding: Gamepad binding dict.
        """
        if "gamepad" not in self._controls:
            self._controls["gamepad"] = {}
        self._controls["gamepad"][action] = binding

    def reset_to_defaults(self):
        """Reset all bindings to defaults."""
        self._controls = DEFAULT_CONTROLS.copy()

    @property
    def controls(self):
        """Get the raw controls dictionary."""
        return self._controls

    @property
    def is_loaded(self):
        """Check if controls have been loaded from file."""
        return self._loaded
