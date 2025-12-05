# Development Guide

This document explains the data-driven architecture and conventions used in Minmatar Rebellion.

## Data-Driven Design

Minmatar Rebellion uses a **data-driven approach** for defining game content. This means that enemies, stages, and power-ups are defined in JSON files rather than hardcoded in Python. This architecture provides several benefits:

- **Easy content creation**: Add new content by creating JSON files without modifying code.
- **Modding support**: Players can create custom content by adding their own JSON files.
- **Separation of concerns**: Game logic is separate from game data.
- **Rapid iteration**: Tweak values without recompiling or modifying code.

## The Loader System

The `core/loader.py` module provides utilities for loading JSON data from the `data/` directory.

### Basic Usage

```python
from core.loader import load_enemies, load_stages, load_powerups, load_all_game_data

# Load specific data types
enemies = load_enemies()       # Returns dict of enemy definitions
stages = load_stages()         # Returns dict of stage definitions
powerups = load_powerups()     # Returns dict of power-up definitions

# Or load everything at once
all_data = load_all_game_data()
enemies = all_data['enemies']
stages = all_data['stages']
powerups = all_data['powerups']
```

### Loader Functions

| Function | Description |
|----------|-------------|
| `load_enemies()` | Load all JSON files from `data/enemies/` |
| `load_stages()` | Load all JSON files from `data/stages/` |
| `load_powerups()` | Load all JSON files from `data/powerups/` |
| `load_all_game_data()` | Load all game data at once |
| `load_json_file(path)` | Load a single JSON file |
| `load_all_from_directory(dir)` | Load all JSON files from a directory |

### Running the Loader Demo

You can test the loader by running it directly:

```bash
python core/loader.py
```

This will display all loaded game data, useful for verifying your JSON files are correct.

## Data Directory Structure

```
data/
├── enemies/           # Enemy definitions
│   ├── asteroid.json
│   └── pirate_frigate.json
├── stages/            # Stage/level definitions
│   └── example_stage.json
└── powerups/          # Power-up definitions
    ├── shield.json
    └── triple_shot.json
```

## JSON Schema Conventions

### Enemy Schema

```json
{
    "name": "Display Name",
    "description": "Description text",
    "health": 100,                    // Total health (or use shields/armor/hull)
    "shields": 30,                    // Shield points
    "armor": 40,                      // Armor points
    "hull": 30,                       // Hull points
    "speed": 2.0,                     // Movement speed multiplier
    "fire_rate": 1500,                // Milliseconds between shots (0 = no shooting)
    "score": 100,                     // Points awarded on kill
    "size": [width, height],          // Sprite dimensions
    "behavior": {
        "pattern": "drift|sine|zigzag|circle|swoop|flank",
        "aggressive": true,           // Actively targets player
        "shoots": true                // Can fire projectiles
    },
    "drops": {
        "powerup_chance": 0.15,       // Chance to drop power-up (0.0-1.0)
        "refugees": 0                 // Number of refugee pods dropped
    },
    "visual": {
        "sprite": "sprite_name",      // Reference to sprite asset
        "color": [r, g, b]            // RGB color values (0-255)
    }
}
```

### Stage Schema

```json
{
    "name": "Stage Name",
    "description": "Stage description",
    "waves": 5,                       // Number of enemy waves
    "enemies": ["enemy_id", ...],     // List of enemy types that can spawn
    "industrial_chance": 0.1,         // Chance for industrial ships (0.0-1.0)
    "boss": "boss_enemy_id",          // Boss enemy ID (null for no boss)
    "background": "background_name",  // Background asset reference
    "difficulty_modifier": 1.0,       // Multiplier for difficulty scaling
    "rewards": {
        "base_score": 500,            // Score for completing stage
        "refugee_bonus": 10           // Bonus refugees on completion
    }
}
```

### Power-up Schema

```json
{
    "name": "Power-up Name",
    "description": "What it does",
    "effect": "effect_id",            // Effect identifier
    "duration": 5000,                 // Duration in milliseconds
    "color": [r, g, b],               // Display color
    "icon": "icon_name",              // Icon asset reference
    "stats": {                        // Effect-specific stats
        "custom_key": "value"
    },
    "rarity": "common|uncommon|rare", // Drop rarity tier
    "drop_weight": 1.0,               // Weight for random selection
    "sound": "sound_name"             // Pickup sound effect
}
```

## Module Organization

### Code Modules

| Module | Purpose |
|--------|---------|
| `core/` | Core utilities (loader, helpers) |
| `enemies/` | Enemy class implementations |
| `stages/` | Stage class implementations |
| `powerups/` | Power-up class implementations |

### Extending the System

When adding new functionality:

1. **Add JSON schema** for the new content type in `data/`
2. **Add loader function** in `core/loader.py` if needed
3. **Add Python module** in the appropriate directory
4. **Update documentation** in `docs/`

## Best Practices

### JSON Files

- Use descriptive filenames (e.g., `pirate_frigate.json`, not `enemy1.json`)
- Include `name` and `description` fields for clarity
- Validate JSON syntax before committing
- Use consistent formatting (2 or 4 space indentation)

### Code Integration

- Load data at startup, not during gameplay
- Cache loaded data to avoid repeated file I/O
- Handle missing files gracefully with defaults
- Log warnings for malformed or missing data

### Testing

- Run `python core/loader.py` to verify JSON files load correctly
- Test new content in-game before submitting

## Troubleshooting

### Common Issues

**JSON not loading:**
- Check for syntax errors (missing commas, quotes, brackets)
- Ensure file extension is `.json`
- Verify file is in the correct `data/` subdirectory

**Enemy/Stage not appearing:**
- Verify the enemy/stage ID matches the filename (without `.json`)
- Check that the content is referenced in the appropriate stage or spawn system

**Power-up not working:**
- Ensure the `effect` ID matches a handler in the game code
- Verify `duration` is a positive number

## Future Improvements

Planned enhancements to the data system:

- JSON schema validation
- Hot-reloading of data files during development
- Data file encryption for distribution builds
- Custom sprite loading from data definitions
