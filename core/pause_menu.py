"""Pause menu infrastructure with volume sliders and difficulty toggle.

Settings are stored in config/options.json.
"""

import json
from pathlib import Path

# Default options
DEFAULT_OPTIONS = {"music_volume": 0.5, "sfx_volume": 0.7, "difficulty": "normal"}

# Valid difficulties
VALID_DIFFICULTIES = ["easy", "normal", "hard", "nightmare"]


def get_config_path():
    """Get the path to the options.json config file."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "config" / "options.json"


def load_options():
    """Load options from config/options.json.

    Returns:
        dict: Options dictionary with keys 'music_volume', 'sfx_volume', 'difficulty'.
              Returns default options if file doesn't exist or is invalid.
    """
    config_path = get_config_path()

    if not config_path.exists():
        return DEFAULT_OPTIONS.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            options = json.load(f)

        # Validate and sanitize options
        validated = DEFAULT_OPTIONS.copy()

        if "music_volume" in options:
            vol = options["music_volume"]
            if isinstance(vol, (int, float)):
                validated["music_volume"] = max(0.0, min(1.0, float(vol)))

        if "sfx_volume" in options:
            vol = options["sfx_volume"]
            if isinstance(vol, (int, float)):
                validated["sfx_volume"] = max(0.0, min(1.0, float(vol)))

        if "difficulty" in options:
            diff = options["difficulty"]
            if diff in VALID_DIFFICULTIES:
                validated["difficulty"] = diff

        return validated
    except (json.JSONDecodeError, IOError):
        return DEFAULT_OPTIONS.copy()


def save_options(options):
    """Save options to config/options.json.

    Args:
        options: dict with keys 'music_volume', 'sfx_volume', 'difficulty'.

    Returns:
        bool: True if save was successful, False otherwise.
    """
    config_path = get_config_path()

    # Ensure config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate before saving
    validated = DEFAULT_OPTIONS.copy()

    if "music_volume" in options:
        vol = options["music_volume"]
        if isinstance(vol, (int, float)):
            validated["music_volume"] = max(0.0, min(1.0, float(vol)))

    if "sfx_volume" in options:
        vol = options["sfx_volume"]
        if isinstance(vol, (int, float)):
            validated["sfx_volume"] = max(0.0, min(1.0, float(vol)))

    if "difficulty" in options:
        diff = options["difficulty"]
        if diff in VALID_DIFFICULTIES:
            validated["difficulty"] = diff

    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(validated, f, indent=4)
        return True
    except IOError:
        return False


class PauseMenu:
    """Pause menu with volume sliders and difficulty toggle.

    Attributes:
        music_volume (float): Music volume from 0.0 to 1.0.
        sfx_volume (float): Sound effects volume from 0.0 to 1.0.
        difficulty (str): Current difficulty setting.
        is_active (bool): Whether the pause menu is currently displayed.
    """

    def __init__(self):
        """Initialize pause menu and load saved options."""
        options = load_options()
        self.music_volume = options["music_volume"]
        self.sfx_volume = options["sfx_volume"]
        self.difficulty = options["difficulty"]
        self.is_active = False

        # Menu navigation
        self.selected_option = 0
        self.options_list = ["music_volume", "sfx_volume", "difficulty", "resume"]

    def toggle(self):
        """Toggle the pause menu on/off."""
        self.is_active = not self.is_active
        if not self.is_active:
            # Save options when closing
            self.save()

    def show(self):
        """Show the pause menu."""
        self.is_active = True

    def hide(self):
        """Hide the pause menu and save options."""
        self.is_active = False
        self.save()

    def save(self):
        """Save current options to config file."""
        options = {
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "difficulty": self.difficulty,
        }
        save_options(options)

    def set_music_volume(self, volume):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, float(volume)))

    def set_sfx_volume(self, volume):
        """Set SFX volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, float(volume)))

    def adjust_music_volume(self, delta):
        """Adjust music volume by delta amount."""
        self.set_music_volume(self.music_volume + delta)

    def adjust_sfx_volume(self, delta):
        """Adjust SFX volume by delta amount."""
        self.set_sfx_volume(self.sfx_volume + delta)

    def toggle_difficulty(self):
        """Cycle through difficulty options."""
        try:
            idx = VALID_DIFFICULTIES.index(self.difficulty)
        except ValueError:
            idx = 0  # Default to first difficulty if current is invalid
        idx = (idx + 1) % len(VALID_DIFFICULTIES)
        self.difficulty = VALID_DIFFICULTIES[idx]

    def set_difficulty(self, difficulty):
        """Set difficulty if valid."""
        if difficulty in VALID_DIFFICULTIES:
            self.difficulty = difficulty

    def navigate_up(self):
        """Move selection up in the menu."""
        self.selected_option = (self.selected_option - 1) % len(self.options_list)

    def navigate_down(self):
        """Move selection down in the menu."""
        self.selected_option = (self.selected_option + 1) % len(self.options_list)

    def get_selected_option(self):
        """Get the currently selected menu option."""
        return self.options_list[self.selected_option]

    def handle_input(self, key_left, key_right, key_select):
        """Handle menu input.

        Args:
            key_left: True if left key pressed (decrease value).
            key_right: True if right key pressed (increase value).
            key_select: True if select/enter key pressed.

        Returns:
            str or None: 'resume' if resume selected, None otherwise.
        """
        current = self.get_selected_option()

        if current == "music_volume":
            if key_left:
                self.adjust_music_volume(-0.1)
            elif key_right:
                self.adjust_music_volume(0.1)
        elif current == "sfx_volume":
            if key_left:
                self.adjust_sfx_volume(-0.1)
            elif key_right:
                self.adjust_sfx_volume(0.1)
        elif current == "difficulty":
            if key_left or key_right or key_select:
                self.toggle_difficulty()
        elif current == "resume":
            if key_select:
                self.hide()
                return "resume"

        return None

    def get_display_data(self):
        """Get menu data for rendering.

        Returns:
            dict: Menu state for rendering including all options and selection.
        """
        return {
            "music_volume": self.music_volume,
            "sfx_volume": self.sfx_volume,
            "difficulty": self.difficulty,
            "selected_option": self.selected_option,
            "options_list": self.options_list,
            "is_active": self.is_active,
        }
