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

- Python 3.8+
- Pygame 2.0+
- NumPy (for sound generation)

## Installation

```bash
pip install pygame numpy
```

## Running the Game

```bash
python main.py
```

Or on Linux:
```bash
chmod +x main.py
./main.py
```

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

The game includes 5 core campaign stages plus 3 expansion stages:

#### Core Campaign
1. **Asteroid Belt Escape** - Tutorial, basic enemies
2. **Amarr Patrol Interdiction** - Introduces cruisers, mini-boss
3. **Slave Colony Liberation** - High refugee opportunity
4. **Gate Assault** - Boss: Apocalypse Battleship
5. **Final Push** - Boss: Abaddon Dreadnought

#### Expansion Stages
6. **Capital Ship Assault** - Boss: Golden Supercarrier (amarr_capital)
7. **Sisters Rescue** - Boss: Stratios (Sisters of EVE cruiser)
8. **Pirate Invasion** - Boss: Machariel (Angel Cartel battleship)

Expansion stages are automatically loaded from `data/stages/` directory. See the **Expansion Content** section below for details.

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
├── core/
│   └── loader.py        # JSON data loader for enemies, stages, powerups
├── data/
│   ├── enemies/         # Enemy definitions (JSON)
│   ├── stages/          # Stage/level definitions (JSON)
│   └── powerups/        # Power-up definitions (JSON)
├── expansion/
│   └── capital_ship_enemy.py  # CapitalShipEnemy boss class
├── docs/
│   └── development.md   # Developer guide for adding content
└── README.md            # This file
```

## Expansion Content

The game supports **expansion content** through a data-driven architecture. Expansion stages, enemies, and bosses are automatically loaded from JSON files in the `data/` directory.

### How Expansion Integration Works

1. **Stage Loading**: All JSON files in `data/stages/` are loaded and converted to the game's stage format
2. **Enemy Integration**: New enemies like `amarr_capital`, `machariel`, and `stratios` are defined in both:
   - `data/enemies/*.json` (visual and behavior properties)
   - `constants.py` ENEMY_STATS (core stats for game engine)
3. **Boss Classes**: Specialized boss classes (like `CapitalShipEnemy`) can be added to the `expansion/` directory

### Currently Available Expansion Content

- **Capital Ship Assault** stage with the `amarr_capital` boss (Golden Supercarrier)
  - Uses the specialized `CapitalShipEnemy` class with multi-turret firing
- **Sisters Rescue** stage with `stratios` boss
- **Pirate Invasion** stage with `machariel` boss

### Adding Your Own Expansion Content

See `docs/development.md` for detailed instructions on:
- Creating new stage JSON files
- Defining new enemies
- Adding specialized boss behaviors
- Extending the loader system

## Customization

Edit `constants.py` to adjust:
- Player stats and speed
- Weapon damage and fire rates
- Enemy health and behavior
- Stage composition
- Upgrade costs
- Difficulty multipliers
- Screen shake intensity

## IP Notice

This is a personal/fan project. Ship designs and names are inspired by CCP Games' EVE Online. For any commercial use, original designs would need to be created or licensing obtained.

---

*"We were slaves once. Never again."*
— Minmatar Rebellion motto
