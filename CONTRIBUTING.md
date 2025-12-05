# Contributing to Minmatar Rebellion

Thank you for your interest in contributing to Minmatar Rebellion! This document provides guidelines and instructions for contributing to the project.

## Project Structure

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic, states, rendering
├── sprites.py           # All game entities (player, enemies, bullets)
├── constants.py         # Configuration, stats, stage definitions
├── sounds.py            # Procedural sound generation
├── core/                # Core utilities and loaders
│   ├── __init__.py
│   └── loader.py        # JSON data loader for game content
├── enemies/             # Enemy class implementations
│   └── __init__.py
├── stages/              # Stage class implementations
│   └── __init__.py
├── powerups/            # Power-up class implementations
│   └── __init__.py
├── data/                # JSON data files for game content
│   ├── enemies/         # Enemy definitions (*.json)
│   ├── stages/          # Stage definitions (*.json)
│   └── powerups/        # Power-up definitions (*.json)
├── docs/                # Documentation
│   └── development.md   # Development guide
├── CONTRIBUTING.md      # This file
└── README.md            # Project overview
```

## Adding New Content

The game uses a data-driven approach where game content (enemies, stages, power-ups) is defined in JSON files. This makes it easy to add new content without modifying Python code.

### Adding a New Enemy

1. Create a new JSON file in `data/enemies/` (e.g., `data/enemies/my_enemy.json`)
2. Define the enemy properties following this structure:

```json
{
    "name": "Enemy Name",
    "description": "Brief description of the enemy.",
    "health": 100,
    "shields": 30,
    "armor": 40,
    "hull": 30,
    "speed": 2.0,
    "fire_rate": 1500,
    "score": 100,
    "size": [30, 40],
    "behavior": {
        "pattern": "zigzag",
        "aggressive": true,
        "shoots": true
    },
    "drops": {
        "powerup_chance": 0.15,
        "refugees": 0
    },
    "visual": {
        "sprite": "enemy_sprite_name",
        "color": [180, 60, 60]
    }
}
```

### Adding a New Stage

1. Create a new JSON file in `data/stages/` (e.g., `data/stages/my_stage.json`)
2. Define the stage properties:

```json
{
    "name": "Stage Name",
    "description": "Stage description.",
    "waves": 5,
    "enemies": ["enemy_id_1", "enemy_id_2"],
    "industrial_chance": 0.1,
    "boss": null,
    "background": "background_name",
    "difficulty_modifier": 1.0,
    "rewards": {
        "base_score": 500,
        "refugee_bonus": 10
    }
}
```

### Adding a New Power-up

1. Create a new JSON file in `data/powerups/` (e.g., `data/powerups/my_powerup.json`)
2. Define the power-up properties:

```json
{
    "name": "Power-up Name",
    "description": "What this power-up does.",
    "effect": "effect_id",
    "duration": 5000,
    "color": [255, 200, 50],
    "stats": {
        "custom_stat": "value"
    },
    "rarity": "common",
    "drop_weight": 1.0
}
```

## Adding New Features

When adding new features that require Python code changes:

1. **Follow existing code style**: Match the formatting and naming conventions used in the existing codebase.
2. **Keep modules focused**: Place enemy-related code in `enemies/`, stage-related code in `stages/`, etc.
3. **Use the loader**: Leverage `core/loader.py` for loading any new JSON data.
4. **Update documentation**: Add relevant documentation to `docs/` if needed.

## Pull Request Guidelines

### Before Submitting

1. **Test your changes**: Run the game and verify your additions work correctly.
2. **Check for errors**: Ensure there are no Python syntax errors or runtime exceptions.
3. **Validate JSON**: Make sure all JSON files are valid (use a JSON validator if needed).

### Submitting a PR

1. **Fork the repository** and create a new branch for your feature.
2. **Make your changes** following the guidelines above.
3. **Write a clear PR description** explaining:
   - What the PR adds or changes
   - Why the change is needed
   - How to test the changes
4. **Keep PRs focused**: One feature or fix per PR is preferred.
5. **Reference any related issues** in your PR description.

### PR Title Format

Use a descriptive title that summarizes the change:
- `Add new enemy: Destroyer class ship`
- `Add power-up: Speed boost`
- `Fix bug in stage transition`
- `Update documentation for enemy creation`

## Code Style

- Use 4 spaces for indentation (no tabs)
- Use descriptive variable and function names
- Add docstrings to new functions and classes
- Keep lines under 100 characters when practical

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.

---

*"We were slaves once. Never again."* — Minmatar Rebellion motto
