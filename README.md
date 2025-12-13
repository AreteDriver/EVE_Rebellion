# MINMATAR REBELLION

A top-down arcade space shooter inspired by EVE Online, featuring the iconic Rifter frigate in a fight for freedom against the Amarr Empire.

## Features

- **Procedural Sound Effects** - Retro-style synthesized sounds for weapons, explosions, pickups
- **Ambient Music** - Generated space ambient background music
- **Screen Shake** - Impact feedback for explosions and damage
- **4 Difficulty Levels** - Easy, Normal, Hard, Nightmare
- **Advanced Enemy AI** - Multiple movement patterns (sine wave, zigzag, swoop, flank, circle)
- **5 Ammo Types** - Swappable ammunition with tactical rock-paper-scissors mechanics
- **Upgrade System** - Spend rescued refugees on ship improvements

## Getting Started

### Option 1: Windows Executable (Recommended for Windows Users)

**No Python installation required!**

1. Download the latest `EVE_Rebellion-Windows.zip` from the [Releases](https://github.com/AreteDriver/EVE_Rebellion/releases) page
2. Extract the ZIP file
3. Double-click `EVE_Rebellion.exe` to play!

The executable includes all necessary dependencies and game assets bundled into a single file.

### Option 2: Run from Source

**Requirements:**
- Python 3.8+
- Pygame 2.0+
- NumPy (for sound generation)

**Installation:**

```bash
pip install -r requirements.txt
```

Or install manually:
Or install minimal dependencies for gameplay only:

```bash
pip install pygame numpy
```

**Running the Game:**

```bash
python main.py
```

Or on Linux:
```bash
chmod +x main.py
./main.py
```

### Building Your Own Executable

If you want to build the Windows executable yourself:

**On Windows:**
```bash
build_exe.bat
```

**On Linux/Mac:**
```bash
chmod +x build_exe.sh
./build_exe.sh
```

The executable will be created in the `dist/` directory.

## Controls

| Action | Keys |
|--------|------|
| Move | WASD or Arrow Keys |
| Fire Autocannons | Space or Left Mouse Button |
| Fire Rockets | Shift or Right Mouse Button |
| Select Ammo | 1-5 |
| Cycle Ammo | Q or Tab |
| Pause | ESC |

### Menu Controls

| Action | Key |
|--------|-----|
| Toggle Sound | S |
| Toggle Music | M |

## Difficulty Levels

| Level | Description |
|-------|-------------|
| Easy | 30% less enemy health/damage, more powerups |
| Normal | Standard experience |
| Hard | 30% more enemy health/damage, faster attacks |
| Nightmare | 60% more health, 50% more damage, very fast attacks |

## Ammo Types

| Type | Key | Color | Best Against |
|------|-----|-------|--------------|
| Titanium Sabot | 1 | Gray | Starter ammo |
| EMP | 2 | Blue | Shields |
| Phased Plasma | 3 | Orange | Armor |
| Fusion | 4 | Red | High damage (slower fire) |
| Barrage | 5 | Yellow | Range/accuracy (fast fire) |

Ammo types must be unlocked at the Rebel Station between stages.

## Gameplay

### Objective
Fight through 5 stages of Amarr forces, liberating enslaved Minmatar refugees along the way. Refugees serve as currency for upgrades.

### Refugee System
- Destroy Amarr industrial ships (Bestowers, Sigils) to release escape pods
- Collect pods before they drift away
- Spend refugees at the Rebel Station on upgrades

### Stages

1. **Asteroid Belt Escape** - Tutorial, basic enemies
2. **Amarr Patrol Interdiction** - Introduces cruisers, mini-boss
3. **Slave Colony Liberation** - High refugee opportunity
4. **Gate Assault** - Boss: Apocalypse Battleship
5. **Final Push** - Boss: Abaddon Dreadnought

### Upgrades

| Upgrade | Cost | Effect |
|---------|------|--------|
| Gyrostabilizer | 10 | +30% fire rate |
| Armor Plate | 15 | +30 max armor |
| Tracking Enhancer | 20 | +1 gun spread |
| EMP Ammo | 25 | Unlock EMP rounds |
| Phased Plasma | 35 | Unlock Plasma rounds |
| Fusion Ammo | 45 | Unlock Fusion rounds |
| Barrage Ammo | 55 | Unlock Barrage rounds |
| **Wolf Upgrade** | 50 | T2 Assault Frigate! |

### Power-ups (dropped by enemies)

- **Nanite Paste** (green) - Repairs hull
- **Capacitor Booster** (blue) - Refills rockets
- **Overdrive** (yellow) - Temporary speed boost
- **Shield Booster** (light blue) - Temporary damage reduction + shield repair

## Enemy Types

### Frigates
- **Executioner** - Fast, shield-heavy. Use EMP. Aggressive movement patterns.
- **Punisher** - Slow, armor-tanked. Use Plasma. Steady movement.

### Cruisers
- **Omen** - Mid-boss. Balanced defenses. Tactical flanking.
- **Maller** - Heavy armor brick. Circular strafing patterns.

### Industrials
- **Bestower/Sigil** - Non-combat. Drops refugees!

### Bosses
- **Apocalypse** - Battleship. Spread fire pattern. Phase-based fight.
- **Abaddon** - Final boss. Multiple phases, increases aggression at low health.

## Sound System

The game generates all sounds procedurally using numpy waveform synthesis:

- **Autocannons** - Punchy low-frequency burst
- **Rockets** - Whooshing launch sound
- **Lasers** - High-frequency Amarr beam
- **Explosions** - Scaled by enemy size (small/medium/large)
- **Shield/Armor/Hull hits** - Distinct damage feedback
- **Pickups** - Hopeful arpeggio for refugees, bright sweep for powerups
- **UI sounds** - Menu selection, purchase confirmation, error buzzer

Sound gracefully disables if no audio device is available.

## File Structure

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic, states, rendering
├── sprites.py           # All game entities (player, enemies, bullets)
├── constants.py         # Configuration, stats, stage definitions
├── sounds.py            # Procedural sound generation
├── requirements.txt     # Python dependencies
├── tests/               # Unit tests
├── .github/workflows/   # CI/CD workflows
└── README.md            # This file
```

## Development & CI/CD

This project uses GitHub Actions for automated testing and deployment:

- **Continuous Integration**: Tests run automatically on every push and pull request
- **Continuous Deployment**: Releases are built automatically when you push a tag

For more information, see [docs/WORKFLOWS.md](docs/WORKFLOWS.md).

### Running Tests

```bash
pip install -r requirements.txt
pytest -v
```

### Code Linting

```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Building Standalone Executables

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MinmatarRebellion main.py
```

The executable will be in the `dist/` directory.

## Graphics

All ship graphics and visual effects are **procedurally generated** using Pygame's drawing primitives. The game does not use or require any external image files (PNG, JPG, etc.). Ships, bullets, explosions, and UI elements are all drawn programmatically at runtime.

This design choice means:
- ✓ No missing image files
- ✓ No path configuration needed
- ✓ Lightweight distribution
- ✓ Easy customization via code

Ship designs are created in `sprites.py`:
- Player ships (Rifter/Wolf): `Player._create_ship_image()`
- Enemy ships: `Enemy._create_image()`

## Customization

Edit `constants.py` to adjust:
- Player stats and speed
- Weapon damage and fire rates
- Enemy health and behavior
- Stage composition
- Upgrade costs
- Difficulty multipliers
- Screen shake intensity

Edit `sprites.py` to modify ship visuals:
- Change ship colors by modifying `COLOR_*` constants
- Adjust ship shapes in the `_create_ship_image()` and `_create_image()` methods
- Modify bullet, explosion, and powerup visuals

## Troubleshooting

### Windows Executable Issues

#### "Windows protected your PC" SmartScreen warning

This is normal for unsigned applications. To run the game:

1. Click "More info"
2. Click "Run anyway"

The game is open source - you can review the code on GitHub or build it yourself to verify it's safe.

#### Anti-virus blocking the executable

Some anti-virus software may flag PyInstaller executables as suspicious. This is a false positive. You can:

1. Add an exception for `EVE_Rebellion.exe` in your anti-virus settings
2. Download the source code and build the executable yourself
3. Run from source using Python (see "Option 2: Run from Source")

#### Executable won't start or crashes immediately

1. **Check system requirements**: Windows 7 or later, 64-bit
2. **Run as Administrator**: Right-click `EVE_Rebellion.exe` and select "Run as administrator"
3. **Install Visual C++ Redistributable**: Download from [Microsoft](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads)
4. **Check the error**: If running from command prompt shows an error message, it can help diagnose the issue:
   ```
   cmd
   cd path\to\game
   EVE_Rebellion.exe
   ```

#### Missing DLL errors

The executable should be self-contained, but if you get missing DLL errors:

1. Install [Visual C++ Redistributable 2015-2022](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. Update Windows to the latest version
3. Try running from source instead

#### Game runs but no sound

1. Check Windows sound settings - ensure output device is working
2. Press 'S' in the game menu to toggle sound
3. Press 'M' to toggle music
4. Update audio drivers

#### Performance issues with the executable

The executable may run slightly slower than Python source due to unpacking overhead:

1. Close other applications to free up resources
2. Update graphics drivers
3. For best performance, run from source (see "Option 2: Run from Source")

### Python Source Code Issues

### Ships or graphics not displaying

If you don't see ships or other graphics:

1. **Check Pygame version**: Ensure you have Pygame 2.0+ installed
   ```bash
   python3 -c "import pygame; print(pygame.__version__)"
   ```

2. **Verify display initialization**: Make sure your system can create a display window
   ```bash
   python3 -c "import pygame; pygame.init(); pygame.display.set_mode((100,100))"
   ```

3. **Update graphics drivers**: Outdated graphics drivers can cause rendering issues
   - Linux: Update mesa/graphics drivers via your package manager
   - Windows: Update via Device Manager or GPU manufacturer's site
   - macOS: Keep system updated

4. **Try software rendering** (if hardware acceleration fails):
   ```bash
   SDL_VIDEODRIVER=software python3 main.py    # Linux/macOS
   set SDL_VIDEODRIVER=software && python3 main.py  # Windows
   ```

### Audio warnings (ALSA errors on Linux)

ALSA warnings like "cannot find card '0'" are harmless and don't affect gameplay. They occur when audio hardware is unavailable. The game will continue with audio disabled. To suppress these warnings:

```bash
SDL_AUDIODRIVER=dummy python3 main.py
```

Or disable sound in-game by pressing 'S' in the menu.

### Performance issues

If the game runs slowly:
- Lower `FPS` in `constants.py` (default: 60)
- Reduce `SCREEN_WIDTH` and `SCREEN_HEIGHT` for lower resolution
- Disable screen shake by setting shake constants to 0

### Black screen or crash on startup

1. **Ensure dependencies are installed**:
   ```bash
   pip install --upgrade pygame numpy
   ```

2. **Check Python version**: Requires Python 3.8 or higher
   ```bash
   python3 --version
   ```

3. **Run from the correct directory**: Always run from the game's root directory
   ```bash
   cd /path/to/EVE_Rebellion
   python3 main.py
   ```

## IP Notice

This is a personal/fan project. Ship designs and names are inspired by CCP Games' EVE Online. For any commercial use, original designs would need to be created or licensing obtained.

---

*"We were slaves once. Never again."*
— Minmatar Rebellion motto
