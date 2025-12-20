# MINMATAR REBELLION

A top-down arcade space shooter inspired by EVE Online, featuring the iconic Rifter frigate in a fight for freedom against the Amarr Empire.

## Quick Start

```bash
# Install dependencies
pip install pygame numpy

# Run the game
python main.py
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

## Features

- **Modular Data-Driven Architecture** - Easy to add new enemies, stages, and power-ups via JSON
- **Procedural Sound Effects** - Retro-style synthesized sounds
- **Advanced Enemy AI** - Multiple movement patterns (sine wave, zigzag, swoop, flank, circle)
- **4 Difficulty Levels** - Easy, Normal, Hard, Nightmare
- **5 Ammo Types** - Tactical rock-paper-scissors mechanics
- **Upgrade System** - Spend rescued refugees on ship improvements

## Project Structure

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic
├── sprites.py           # All game entities
├── sounds.py            # Procedural sound generation
├── constants.py         # Configuration
├── core/                # Core utilities
│   └── loader.py        # JSON data loader
├── data/                # JSON data files
│   ├── enemies/         # Enemy definitions
│   ├── stages/          # Stage definitions
│   └── powerups/        # Power-up definitions
├── enemies/             # Enemy implementations
├── stages/              # Stage implementations
└── powerups/            # Power-up implementations
```

## Adding New Content

See `CONTRIBUTING.md` for details on adding new enemies, stages, and power-ups via JSON files.

## License

Personal/fan project inspired by CCP Games' EVE Online.

---

*"We were slaves once. Never again."*
