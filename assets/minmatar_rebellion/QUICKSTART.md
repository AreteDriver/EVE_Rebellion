# QUICK START GUIDE

## Windows Installation (Easy!)

### Option 1: Double-Click Launch
1. Extract the game folder
2. **Double-click `PLAY.bat`**
3. Game launches automatically!

### Option 2: Command Line
```batch
# Install dependencies (one time only)
pip install pygame numpy

# Run the game
python main.py
```

## Linux/Mac Installation

```bash
# Install dependencies
pip install pygame numpy

# Run the game
python main.py
```

## Controls

### Keyboard & Mouse
- **WASD / Arrow Keys** - Move ship
- **Space / Left Click** - Fire autocannons  
- **Shift / Right Click** - Fire rockets
- **1-5** - Select ammo type
- **Q / Tab** - Cycle ammo
- **ESC** - Pause

### Controller/Gamepad (Xbox, PlayStation, etc.)
- **Left Stick** - Move ship
- **A / Right Trigger** - Fire autocannons
- **B / Left Trigger** - Fire rockets
- **X / Left Bumper** - Cycle ammo
- **Start** - Pause

*Controller auto-detected on startup!*

## Features

- Modular data-driven architecture
- 267 EVE ship silhouettes included
- Procedural sound effects
- 5 difficulty levels
- Advanced enemy AI with 6 movement patterns

## Next Steps

1. Play the game and test mechanics
2. Add custom JSON enemies/stages in `data/` folders
3. Modify ship images in `svg/top/` folder
4. Check `CONTRIBUTING.md` for mod creation guide

## Building a Standalone .exe (Optional)

Want to share the game without requiring Python?

```batch
# Run this to create MinmatarRebellion.exe
build_exe.bat
```

See `BUILD_EXE.md` for detailed instructions!

---

*For CCP Games pitch demo*
