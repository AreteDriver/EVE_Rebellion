# Build & Development Guide

## Overview

EVE Rebellion is a pure Python game built with Pygame. All graphics and audio are procedurally generated at runtime - no external assets required.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AreteDriver/EVE_Rebellion.git
cd EVE_Rebellion
```

### 2. Install Dependencies

#### Using pip (recommended)

```bash
pip install -r requirements.txt
```

#### Manual installation

```bash
pip install pygame>=2.0.0 numpy>=1.20.0
```

### 3. Verify Installation

```bash
python3 -c "import pygame; import numpy; print('Dependencies OK')"
```

## Running the Game

### Standard Launch

```bash
python3 main.py
```

### Linux/Unix (with executable permissions)

```bash
chmod +x main.py
./main.py
```

### Development Mode

For debugging or testing specific features, you can modify `constants.py` before running:

```python
# Set debug flags in constants.py
DEBUG_MODE = True
START_STAGE = 1  # Skip to specific stage
INVINCIBLE = True  # Test without dying
```

## Build Configuration

All game configuration is in `constants.py`:

- Screen resolution and FPS
- Difficulty multipliers
- Ship stats and upgrade values
- Stage composition
- Color schemes
- Sound sample rates

## Performance Optimization

### For Low-End Systems

Edit `constants.py`:

```python
FPS = 30  # Reduce from 60
SCREEN_WIDTH = 800  # Reduce from 1280
SCREEN_HEIGHT = 600  # Reduce from 720
PARTICLE_LIMIT = 50  # Reduce particle effects
```

### For High-End Systems

```python
FPS = 144  # Increase for high refresh rate monitors
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
```

## Testing

The game includes procedural generation which means testing focuses on:

1. **Visual Testing**: Run the game and verify all sprites render correctly
2. **Audio Testing**: Verify all sound effects play without distortion
3. **Gameplay Testing**: Verify mechanics work across all difficulty levels

### Quick Test Run

```bash
# Test game launches successfully
python3 main.py &
PID=$!
sleep 5
kill $PID
```

## Platform-Specific Notes

### Linux

**Audio Issues**: If you see ALSA warnings, they're harmless:

```bash
# Suppress ALSA warnings
SDL_AUDIODRIVER=dummy python3 main.py
```

**Display Issues**: If no window appears:

```bash
# Try software rendering
SDL_VIDEODRIVER=x11 python3 main.py
```

### macOS

Pygame works best with Python installed via Homebrew:

```bash
brew install python3
pip3 install -r requirements.txt
```

### Windows

Use Command Prompt or PowerShell:

```cmd
python main.py
```

For better performance, ensure hardware acceleration is enabled in your graphics driver settings.

## Troubleshooting

### ModuleNotFoundError: No module named 'pygame'

Install dependencies:
```bash
pip install -r requirements.txt
```

### Audio initialization failed

The game will continue with audio disabled. To force audio mode:

```bash
SDL_AUDIODRIVER=alsa python3 main.py  # Linux
```

### Black screen on startup

1. Update graphics drivers
2. Try software rendering: `SDL_VIDEODRIVER=software python3 main.py`
3. Check Python version: `python3 --version` (must be 3.8+)

## Development Workflow

### Code Structure

- `main.py` - Entry point
- `game.py` - Main game loop and state management
- `sprites.py` - All game entities (player, enemies, bullets, etc.)
- `constants.py` - Configuration and game balance
- `sounds.py` - Procedural audio synthesis
- `upgrade_screen.py` - Between-stage upgrade interface

### Making Changes

1. Edit the relevant Python file
2. Run the game to test: `python3 main.py`
3. Iterate

No build step required - Python is interpreted.

## Distribution

### Creating a Standalone Executable (Optional)

Using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "Minmatar_Rebellion" main.py
```

Output will be in `dist/` directory.

### Source Distribution

The entire game can be distributed as source:

```bash
zip -r minmatar_rebellion.zip *.py core/ data/ enemies/ expansion/ powerups/ stages/ README.md LICENSE requirements.txt
```

## Contributing

See `CONTRIBUTING.md` for contribution guidelines.

## License

See `LICENSE` file for details.
