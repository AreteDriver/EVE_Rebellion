# Installation and Dependency Setup

This document describes the dependencies and installation process for EVE Rebellion.

## Required Dependencies

### Python Version
- Python 3.8 or higher

### Core Dependencies

The game requires the following Python packages:

1. **pygame** (2.0+)
   - Used for: Graphics, input handling, display management
   - Install: `pip install pygame`

2. **numpy**
   - Used for: Procedural sound generation
   - Install: `pip install numpy`

### Installation

To install all dependencies at once:

```bash
pip install pygame numpy
```

Or if you prefer using pip3:

```bash
pip3 install pygame numpy
```

## Module Structure

The game consists of the following modules:

- `main.py` - Entry point for the game
- `game.py` - Main game logic and state management
- `upgrade_screen.py` - Skill point upgrade screen (requires `progression` module)
- `progression.py` - Player progression save/load system (NEW)
- `sprites.py` - Game entities (player, enemies, bullets, etc.)
- `sounds.py` - Procedural sound generation
- `constants.py` - Game configuration and constants
- `core/` - Core utilities and data loaders

## Save Files

The progression system creates a save file to track player progress:

- **File**: `player_progress.json`
- **Location**: Game root directory
- **Purpose**: Stores skill points, purchased upgrades, unlocked ships, total kills, and highest stage reached
- **Note**: This file is automatically created and managed by the `progression` module

The save file is excluded from version control via `.gitignore`.

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError` for `pygame` or `numpy`:
```bash
pip install pygame numpy
```

If you get `ModuleNotFoundError` for game modules:
- Ensure you're running the game from the repository root directory
- The directory structure should have all .py files in the same directory

### Audio Issues

If you encounter audio errors when running headless (e.g., in CI/CD):
```bash
export SDL_AUDIODRIVER=dummy
export SDL_VIDEODRIVER=dummy
python main.py
```

### Missing progression Module

If you see `ModuleNotFoundError: No module named 'progression'`:
- Ensure `progression.py` exists in the game directory
- This module was added to fix upgrade_screen.py dependencies
- It should be included in the repository

## Running the Game

After installing dependencies:

```bash
python main.py
```

or

```bash
python3 main.py
```

On Linux, you can also make it executable:

```bash
chmod +x main.py
./main.py
```

## Verifying Installation

To verify all modules can be imported correctly:

```python
python3 -c "import game, upgrade_screen, progression, constants, sprites, sounds; print('All modules imported successfully')"
```

This should output "All modules imported successfully" if everything is set up correctly.
