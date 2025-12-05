# Contributing to Minmatar Rebellion

Thank you for your interest in contributing to Minmatar Rebellion! This document provides guidelines for extending the game's quality-of-life systems.

## Table of Contents

- [Getting Started](#getting-started)
- [Extending the Options System](#extending-the-options-system)
- [Extending the Save System](#extending-the-save-system)
- [Extending the Tutorial System](#extending-the-tutorial-system)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Install dependencies:
   ```bash
   pip install pygame numpy
   ```
4. Run the game to ensure everything works:
   ```bash
   python main.py
   ```

## Extending the Options System

The options system is implemented in `core/pause_menu.py` and stores settings in `config/options.json`.

### Adding a New Option

1. **Update the default options** in `core/pause_menu.py`:
   ```python
   DEFAULT_OPTIONS = {
       "music_volume": 0.5,
       "sfx_volume": 0.7,
       "difficulty": "normal",
       "your_new_option": default_value  # Add your option here
   }
   ```

2. **Add validation** in the `load_options()` and `save_options()` functions to ensure your option is properly validated and sanitized.

3. **Update the PauseMenu class**:
   - Add an attribute for your option in `__init__()`
   - Add getter/setter methods as needed
   - Update `options_list` if it should appear in the menu
   - Add handling in `handle_input()` for user interaction

4. **Update `config/options.json`** with the new default value.

### Example: Adding a Screen Shake Toggle

```python
# In DEFAULT_OPTIONS:
"screen_shake": True

# In PauseMenu.__init__():
self.screen_shake = options['screen_shake']

# Add setter method:
def set_screen_shake(self, enabled):
    self.screen_shake = bool(enabled)
```

## Extending the Save System

The save system is implemented in `core/save_manager.py` and stores save files in the `saves/` directory.

### Adding New Player State Fields

1. **Update `extract_player_state()`** in `SaveManager` class to include your new field:
   ```python
   def extract_player_state(self, player):
       return {
           # ... existing fields ...
           'your_new_field': getattr(player, 'your_new_field', default_value)
       }
   ```

2. **Update `apply_player_state()`** to restore your field:
   ```python
   player.your_new_field = state.get('your_new_field', default_value)
   ```

### Adding New Game State Fields

1. When calling `save_game()`, include your new fields in the `game_state` dictionary:
   ```python
   game_state = {
       'current_stage': self.current_stage,
       'current_wave': self.current_wave,
       'difficulty': self.difficulty,
       'your_new_field': self.your_new_field  # Add here
   }
   ```

2. When loading, retrieve your field from the `game_state` dictionary returned by `load_game()`.

### Save File Format

Save files are JSON with this structure:
```json
{
    "player": {
        "score": 1500,
        "refugees": 25,
        ...
    },
    "game": {
        "current_stage": 1,
        "current_wave": 3,
        "difficulty": "normal"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Extending the Tutorial System

The tutorial system is implemented in `core/tutorial.py` and loads data from `data/tutorial.json`.

### Adding New Tutorial Steps

Edit `data/tutorial.json` to add new steps:

```json
{
    "steps": [
        {
            "id": "unique_step_id",
            "message": "Your tutorial message here",
            "duration": 4.0
        }
    ]
}
```

Each step requires:
- `id` (string): Unique identifier for the step
- `message` (string): Text displayed to the player
- `duration` (float): How long the message displays in seconds

### Adding Tutorial Features

To add features like conditions or triggers:

1. **Extend the step schema** in `data/tutorial.json`:
   ```json
   {
       "id": "rockets_unlocked",
       "message": "You've unlocked rockets! Press SHIFT to fire.",
       "duration": 4.0,
       "trigger": "rockets_unlocked"
   }
   ```

2. **Update validation** in `load_tutorial_data()` to include new fields.

3. **Update the Tutorial class** to handle the new features in `update()` or add new methods.

### Conditional Tutorial Steps

To implement conditional steps:

```python
# In Tutorial class:
def should_show_step(self, step_id):
    """Check if a step should be shown based on game state."""
    # Add your conditions here
    return True

def update(self, delta_time, game_state=None):
    """Update with optional game state for conditional logic."""
    # ... existing update logic ...
    # Add conditional checks as needed
```

## Code Style

- Follow PEP 8 guidelines
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Include type hints where beneficial
- Keep functions focused and single-purpose

## Submitting Changes

1. Create a new branch for your changes
2. Make your changes with clear commit messages
3. Test your changes thoroughly
4. Update documentation if needed
5. Submit a pull request with a description of your changes

Thank you for contributing!
