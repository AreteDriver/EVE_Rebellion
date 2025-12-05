# Development Guide

This document provides detailed technical information for developers working on Minmatar Rebellion's quality-of-life systems.

## Project Structure

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic, states, rendering
├── sprites.py           # All game entities (player, enemies, bullets)
├── constants.py         # Configuration, stats, stage definitions
├── sounds.py            # Procedural sound generation
├── core/                # Quality-of-life feature modules
│   ├── __init__.py
│   ├── pause_menu.py    # Pause menu with volume/difficulty options
│   ├── save_manager.py  # Save/load game state
│   └── tutorial.py      # Data-driven tutorial system
├── config/              # Configuration files
│   └── options.json     # User settings (volume, difficulty)
├── data/                # Game data files
│   └── tutorial.json    # Tutorial steps and messages
├── saves/               # Save game files
│   └── save1.json       # Example save file
└── docs/                # Documentation
    └── development.md   # This file
```

## Options System (`core/pause_menu.py`)

### Overview

The options system provides persistent user settings stored in JSON format. It includes a `PauseMenu` class for in-game access and standalone functions for direct file operations.

### Key Components

#### `load_options()` / `save_options()`

Low-level functions for reading/writing `config/options.json`:

```python
from core.pause_menu import load_options, save_options

# Load current options
options = load_options()
print(f"Music volume: {options['music_volume']}")

# Modify and save
options['sfx_volume'] = 0.8
save_options(options)
```

#### `PauseMenu` Class

High-level interface for in-game settings management:

```python
from core.pause_menu import PauseMenu

menu = PauseMenu()

# Toggle visibility
menu.toggle()

# Adjust settings
menu.set_music_volume(0.6)
menu.toggle_difficulty()

# Get current state for rendering
display_data = menu.get_display_data()
```

### Configuration Schema

`config/options.json`:
```json
{
    "music_volume": 0.5,    // 0.0 to 1.0
    "sfx_volume": 0.7,      // 0.0 to 1.0
    "difficulty": "normal"  // "easy", "normal", "hard", "nightmare"
}
```

### Validation

All options are validated on load and save:
- Volume values are clamped to [0.0, 1.0]
- Difficulty must be one of the valid options
- Invalid or missing options fall back to defaults

## Save System (`core/save_manager.py`)

### Overview

The save system persists game state to JSON files in the `saves/` directory. It supports multiple save slots and provides both low-level functions and a high-level `SaveManager` class.

### Key Components

#### Low-Level Functions

```python
from core.save_manager import save_game, load_game, list_saves, delete_save

# List all saves
saves = list_saves()
for filename, metadata in saves:
    print(f"{filename}: Stage {metadata['stage']}, Score {metadata['score']}")

# Save game
player_state = {...}
game_state = {...}
save_game('save1.json', player_state, game_state)

# Load game
player_state, game_state = load_game('save1.json')

# Delete save
delete_save('save1.json')
```

#### `SaveManager` Class

High-level interface with Player object integration:

```python
from core.save_manager import SaveManager

manager = SaveManager()

# Save current game
player_state = manager.extract_player_state(player)
game_state = {'current_stage': 1, 'current_wave': 2, 'difficulty': 'normal'}
manager.save(player_state, game_state)

# Load and apply
player_state, game_state = manager.load()
manager.apply_player_state(player, player_state)
```

### Save File Schema

`saves/save1.json`:
```json
{
    "player": {
        "score": 1500,
        "refugees": 25,
        "total_refugees": 45,
        "shields": 80,
        "armor": 100,
        "hull": 50,
        "max_shields": 100,
        "max_armor": 100,
        "max_hull": 50,
        "rockets": 8,
        "current_ammo": "sabot",
        "unlocked_ammo": ["sabot", "emp"],
        "has_gyro": true,
        "has_tracking": false,
        "is_wolf": false
    },
    "game": {
        "current_stage": 1,
        "current_wave": 3,
        "difficulty": "normal"
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

### Security

- Filenames are sanitized using `os.path.basename()` to prevent path traversal
- All JSON parsing is wrapped in try/except to handle malformed files
- Missing or invalid fields fall back to safe defaults

## Tutorial System (`core/tutorial.py`)

### Overview

The tutorial system displays sequential messages loaded from a JSON data file, enabling designers to modify tutorial content without code changes.

### Key Components

#### `load_tutorial_data()`

Loads and validates tutorial steps from `data/tutorial.json`:

```python
from core.tutorial import load_tutorial_data

data = load_tutorial_data()
for step in data['steps']:
    print(f"{step['id']}: {step['message']} ({step['duration']}s)")
```

#### `Tutorial` Class

Manages tutorial state and progression:

```python
from core.tutorial import Tutorial

tutorial = Tutorial()

# Start tutorial
tutorial.start()

# In game loop (delta_time in seconds)
step_changed = tutorial.update(1/60)

# Get current message
message = tutorial.get_current_message()

# Get rendering data
display_data = tutorial.get_display_data()

# Skip tutorial
tutorial.skip()
```

### Tutorial Data Schema

`data/tutorial.json`:
```json
{
    "steps": [
        {
            "id": "unique_id",      // Required: unique identifier
            "message": "Text here", // Required: display text
            "duration": 4.0         // Optional: seconds (default 3.0)
        }
    ]
}
```

### Integration Example

```python
# In Game class
from core.tutorial import Tutorial

class Game:
    def __init__(self):
        self.tutorial = Tutorial()
    
    def start_new_game(self):
        # Start tutorial on first stage
        if self.current_stage == 0:
            self.tutorial.start()
    
    def update(self, delta_time):
        # Update tutorial
        if self.tutorial.is_active:
            self.tutorial.update(delta_time)
    
    def draw(self):
        # Draw tutorial message
        if self.tutorial.is_active:
            message = self.tutorial.get_current_message()
            if message:
                self.draw_tutorial_message(message)
```

## Testing

While there is no formal test suite, you can verify the systems work correctly:

```python
# Test pause menu
from core.pause_menu import PauseMenu, load_options, save_options

menu = PauseMenu()
assert menu.music_volume >= 0.0 and menu.music_volume <= 1.0
menu.set_music_volume(0.8)
menu.save()
reloaded = load_options()
assert reloaded['music_volume'] == 0.8

# Test save manager
from core.save_manager import SaveManager, save_game, load_game

save_game('test.json', {'score': 100}, {'stage': 1})
p, g = load_game('test.json')
assert p['score'] == 100
assert g['stage'] == 1

# Test tutorial
from core.tutorial import Tutorial

tutorial = Tutorial()
tutorial.start()
assert tutorial.is_active
assert tutorial.get_current_message() is not None
```

## Best Practices

1. **Always validate external data**: JSON files can be edited by users; validate all loaded data.

2. **Use defaults for missing values**: Never assume a field exists; always provide fallbacks.

3. **Handle file I/O errors gracefully**: Wrap file operations in try/except blocks.

4. **Keep state serializable**: Only store JSON-compatible types (strings, numbers, lists, dicts, bools, null).

5. **Document data schemas**: Keep this document updated when adding new fields.

6. **Test with corrupted files**: Ensure the game handles missing or malformed configuration gracefully.
