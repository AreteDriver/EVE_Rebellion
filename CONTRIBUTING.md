# Contributing to Minmatar Rebellion

Thank you for your interest in contributing to Minmatar Rebellion! This document provides guidelines for contributing code, documentation, and other improvements.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies: `pip install pygame numpy`
4. Run the game: `python main.py`

## Code Style

- Follow PEP 8 guidelines for Python code
- Use descriptive variable and function names
- Add docstrings to modules, classes, and functions
- Keep functions focused and reasonably sized

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request with a clear description

## Adding Control Schemes

The game supports customizable controls through `config/controls.json`. To add or modify control schemes:

### Keyboard Bindings

Edit the `keyboard` section in `config/controls.json`:

```json
{
    "keyboard": {
        "move_left": ["K_LEFT", "K_a"],
        "move_right": ["K_RIGHT", "K_d"],
        "fire": ["K_SPACE"]
    }
}
```

- Keys use pygame constant names (e.g., `K_LEFT`, `K_SPACE`, `K_a`)
- Each action can have multiple keys bound to it as an array
- See [pygame key constants](https://www.pygame.org/docs/ref/key.html) for available keys

### Gamepad Bindings

Edit the `gamepad` section for controller support:

```json
{
    "gamepad": {
        "move_left": {"type": "axis", "axis": 0, "direction": -1},
        "fire": {"type": "button", "button": 0}
    }
}
```

- Use `"type": "axis"` for analog sticks with `"axis"` number and `"direction"` (-1 or 1)
- Use `"type": "button"` for buttons with `"button"` number
- Adjust `gamepad_deadzone` (0.0 to 1.0) for stick sensitivity

### Using the Controls Manager

```python
from core.controls import ControlsManager

manager = ControlsManager()
manager.load()

# Get keyboard keys for an action
move_keys = manager.get_keyboard_keys('move_left')

# Get gamepad binding
fire_binding = manager.get_gamepad_binding('fire')
```

## Adding Accessibility Options

Accessibility settings are stored in `config/accessibility.json`. To add new options:

### Available Settings

```json
{
    "colorblind_mode": {
        "enabled": false,
        "type": "none",
        "options": ["none", "protanopia", "deuteranopia", "tritanopia"]
    },
    "high_contrast_ui": {
        "enabled": false,
        "text_scale": 1.0
    },
    "screen_shake": {
        "enabled": true,
        "intensity": 1.0
    }
}
```

### Guidelines for New Accessibility Features

1. **Colorblind Support**: When adding new visual elements, consider how they appear to users with different types of color blindness. Use shape and pattern in addition to color.

2. **Motion Sensitivity**: Allow users to disable or reduce screen shake and flash effects.

3. **Audio Cues**: Provide audio feedback for important game events so players aren't solely dependent on visual cues.

4. **Text Scaling**: Support adjustable text sizes where feasible.

5. **High Contrast**: Ensure UI elements are distinguishable with high contrast settings enabled.

### Implementing Accessibility Features

When implementing features that use accessibility settings:

1. Load settings from `config/accessibility.json`
2. Check the relevant setting before applying effects
3. Provide fallbacks when settings are disabled
4. Test with various setting combinations

## Reporting Issues

- Use GitHub Issues for bug reports and feature requests
- Include steps to reproduce bugs
- Specify your operating system and Python version
- Attach screenshots or error logs when helpful

## Questions?

Feel free to open an issue for questions about contributing.
