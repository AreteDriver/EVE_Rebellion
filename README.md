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

## Requirements

- Python 3.8 or higher (tested with Python 3.12)
- Pygame 2.0 or higher
- NumPy (for procedural sound generation)

## Installation

### Option 1: Quick Install (Global)

```bash
pip install pygame numpy
```

### Option 2: Virtual Environment (Recommended)

Using a virtual environment keeps your project dependencies isolated:

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install pygame numpy
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install pygame numpy
```

### Option 3: From requirements.txt

If a `requirements.txt` file is present:
```bash
pip install -r requirements.txt
```

## Running the Game

Make sure you have activated your virtual environment (if using one), then run:

```bash
python main.py
```

**On macOS/Linux:**
```bash
python3 main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

**Note:** If you see audio-related warnings on systems without audio output, the game will continue to run with sound disabled.

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
EVE_Rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic, states, rendering
├── sprites.py           # All game entities (player, enemies, bullets, etc.)
├── constants.py         # Configuration, stats, stage definitions
├── sounds.py            # Procedural sound generation
├── upgrade_screen.py    # Skill point upgrade system
├── core/                # Core utilities and loaders
│   ├── __init__.py
│   └── loader.py        # JSON data loader for game content
├── enemies/             # Enemy class implementations
│   └── __init__.py
├── stages/              # Stage class implementations
│   └── __init__.py
├── powerups/            # Power-up class implementations
│   └── __init__.py
├── expansion/           # Expansion/DLC content
│   └── capital_ship_enemy.py
├── data/                # JSON data files for game content
│   ├── enemies/         # Enemy definitions (*.json)
│   ├── stages/          # Stage definitions (*.json)
│   ├── powerups/        # Power-up definitions (*.json)
│   └── upgrades.json    # Upgrade definitions
├── docs/                # Documentation
│   └── development.md   # Development guide
├── CONTRIBUTING.md      # Contribution guidelines
└── README.md            # This file
```

**Note on Graphics:** All ship graphics and visual elements are **procedurally generated** using Pygame drawing functions. No external image files are required. Ship sprites are created at runtime using geometric shapes and colors defined in `sprites.py` and `constants.py`.

## Customization

Edit `constants.py` to adjust:
- Player stats and speed
- Weapon damage and fire rates
- Enemy health and behavior
- Stage composition
- Upgrade costs
- Difficulty multipliers
- Screen shake intensity

## Troubleshooting

### Ship Graphics Not Displaying

**This game does not use external image files.** All ship graphics are procedurally generated at runtime using Pygame's drawing functions. If ships are not visible:

1. **Check Pygame installation:**
   ```bash
   python -c "import pygame; print(pygame.version.ver)"
   ```
   Should print version 2.0 or higher.

2. **Verify display initialization:**
   - The game requires a display output. If running on a headless server, you may need to set up a virtual display (Xvfb).
   - Make sure your system supports the screen resolution (default is 800x600).

3. **Graphics rendering issues:**
   - Ships are created using `pygame.Surface` with `pygame.SRCALPHA` for transparency.
   - If you see blank sprites, check that your graphics drivers support alpha blending.

4. **Color constants:**
   - Ship colors are defined in `constants.py` (e.g., `COLOR_MINMATAR_HULL`, `COLOR_AMARR_ACCENT`).
   - Enemy ships use the `_create_image()` method in the `Enemy` class in `sprites.py`.
   - Player ships use `_create_ship_image()` method in the `Player` class.

### Common Issues

**"ModuleNotFoundError: No module named 'pygame'"**
- Make sure you installed pygame: `pip install pygame numpy`
- If using a virtual environment, ensure it's activated.

**"ModuleNotFoundError: No module named 'progression'"**
- The `progression` module is referenced in `upgrade_screen.py` but not currently included in the repository.
- This affects the skill point upgrade system only. The main game and upgrade shop functionality work without it.
- If you encounter this error when the game tries to load the upgrade screen, you may need to create a stub `progression.py` module with basic save/load functions.

**No sound/Audio warnings or crashes**
- Sound generation requires NumPy: `pip install numpy`
- On systems without audio devices (e.g., headless servers, Docker containers), pygame.mixer.init() may fail.
- Current workaround: The game initializes audio in `game.py` using pygame.mixer.init(). On systems without audio, you may need to wrap this in a try-except block or set SDL environment variable:
  ```bash
  export SDL_AUDIODRIVER=dummy
  python main.py
  ```
- The `SoundGenerator` class in `sounds.py` handles missing audio gracefully, but the main game initialization may still fail without an audio device.

**Game runs slowly**
- Try reducing the screen resolution in `constants.py` (change `SCREEN_WIDTH` and `SCREEN_HEIGHT`).
- Disable screen shake by setting `SHAKE_DECAY = 0` in `constants.py`.

**"Permission denied" when running ./main.py**
- Run `chmod +x main.py` first to make it executable.
- Or use `python main.py` or `python3 main.py` instead.

**Import errors about game modules**
- Make sure you're running the game from the repository root directory.
- The game expects to find `sprites.py`, `constants.py`, etc., in the same directory as `main.py`.

### Development & Modding

For information about adding custom content (enemies, stages, power-ups) using JSON data files, see:
- `docs/development.md` - Data-driven design documentation
- `CONTRIBUTING.md` - Contribution guidelines

You can create new enemies, stages, and power-ups by adding JSON files to the `data/` directory structure without modifying Python code.

## IP Notice

This is a personal/fan project. Ship designs and names are inspired by CCP Games' EVE Online. For any commercial use, original designs would need to be created or licensing obtained.

---

*"We were slaves once. Never again."*
— Minmatar Rebellion motto
