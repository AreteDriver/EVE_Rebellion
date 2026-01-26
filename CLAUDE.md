# EVE_Rebellion - Project Instructions

## Project Overview
EVE Online arcade shooter with procedural audio, data-driven enemy AI, and faction-based progression.

**Stack**: Python, Pygame
**Future**: Rust/Bevy rewrite planned (see ~/Documents/Prompts/ARETE_Development_Prompts_Collection.md)

---

## Architecture

### Core Systems
- **arcade_combat.py** — Combat loop and collision
- **ai_behaviors.py** — Enemy AI state machines
- **controller_input.py** — Gamepad/keyboard input
- **asset_manager.py** — Sprite and audio loading

### EVE-Style Mechanics
- Health: Shield → Armor → Hull (damage flows through layers)
- Capacitor system (energy for weapons/modules)
- Faction-based ships and enemies

---

## Development Workflow

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e .

# Run
python main.py

# Test
pytest
```

---

## Current Priorities
- [x] Improve powerup visuals (rarity system, orbital effects, pickup animations)
- [x] Improve weapon/damage visuals (animated glow, bullet trails, rocket exhaust)
- [ ] Add ships flying in background with random space backdrops
- [ ] Steam Deck optimized controls
- [ ] Leaderboard system

---

## CCP Attribution (Required)
```
EVE Online and the EVE logo are registered trademarks of CCP hf.
All ship images and EVE-related content are property of CCP.
Used in accordance with EVE Online Content Creation Terms of Use.
This is a fan project, not affiliated with or endorsed by CCP hf.
```

---

## Code Conventions
- Snake_case for functions/variables
- Type hints required
- Docstrings for public functions
- Keep game loop logic in arcade_combat.py
- Enemy behaviors are state machines in ai_behaviors.py
