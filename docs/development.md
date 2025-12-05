# Development Guide

This document covers the technical implementation of controls and accessibility systems in Minmatar Rebellion.

## Project Structure

```
minmatar_rebellion/
├── main.py              # Entry point
├── game.py              # Main game logic, states, rendering
├── sprites.py           # All game entities (player, enemies, bullets)
├── constants.py         # Configuration, stats, stage definitions
├── sounds.py            # Procedural sound generation
├── core/
│   ├── __init__.py      # Core module exports
│   └── controls.py      # Control bindings manager
├── config/
│   ├── controls.json    # Key/gamepad bindings
│   └── accessibility.json # Accessibility settings
└── docs/
    └── development.md   # This file
```

## Controls System

### Overview

The controls system (`core/controls.py`) provides a flexible way to manage keyboard, mouse, and gamepad bindings. Bindings are stored in JSON format for easy editing and user customization.

### Configuration File Format

The `config/controls.json` file structure:

```json
{
    "version": "1.0",
    "keyboard": {
        "action_name": ["KEY_CONSTANT_1", "KEY_CONSTANT_2"]
    },
    "mouse": {
        "action_name": "BUTTON_NAME"
    },
    "gamepad": {
        "action_name": {"type": "button|axis", ...}
    },
    "gamepad_deadzone": 0.15
}
```

### Keyboard Bindings

Keyboard keys use pygame constant names without the `pygame.` prefix:

| Action | Default Keys | Description |
|--------|-------------|-------------|
| move_left | K_LEFT, K_a | Move ship left |
| move_right | K_RIGHT, K_d | Move ship right |
| move_up | K_UP, K_w | Move ship up |
| move_down | K_DOWN, K_s | Move ship down |
| fire | K_SPACE | Fire primary weapon |
| fire_rocket | K_LSHIFT, K_RSHIFT | Fire rockets |
| cycle_ammo | K_q, K_TAB | Cycle ammunition type |
| pause | K_ESCAPE | Pause game |

### Gamepad Bindings

Gamepad bindings support two types:

**Button bindings:**
```json
{
    "type": "button",
    "button": 0
}
```

**Axis bindings (analog sticks):**
```json
{
    "type": "axis",
    "axis": 0,
    "direction": -1
}
```

- `axis`: The axis index (0 = left stick X, 1 = left stick Y, typically)
- `direction`: -1 for negative direction, 1 for positive direction

### API Reference

#### Functions

```python
load_controls(config_path=None) -> dict
```
Load control bindings from config file. Returns default bindings if file is missing or invalid.

```python
save_controls(controls, config_path=None) -> bool
```
Save control bindings to config file. Returns True on success.

```python
get_keyboard_keys(controls, action) -> list
```
Get list of keyboard key names bound to an action.

```python
get_gamepad_binding(controls, action) -> dict
```
Get gamepad binding configuration for an action.

```python
get_gamepad_deadzone(controls) -> float
```
Get the analog stick deadzone value.

#### ControlsManager Class

```python
from core.controls import ControlsManager

manager = ControlsManager()
manager.load()  # Load from config/controls.json

# Query bindings
keys = manager.get_keyboard_keys('fire')
gamepad = manager.get_gamepad_binding('fire')
deadzone = manager.get_gamepad_deadzone()

# Modify bindings
manager.set_keyboard_binding('fire', ['K_SPACE', 'K_RETURN'])
manager.set_gamepad_binding('fire', {'type': 'button', 'button': 1})

# Save changes
manager.save()

# Reset to defaults
manager.reset_to_defaults()
```

### Integration Example

To integrate the controls system with pygame:

```python
import pygame
from core.controls import ControlsManager

# Initialize
manager = ControlsManager()
manager.load()

# Convert key names to pygame constants
def get_pygame_keys(action):
    key_names = manager.get_keyboard_keys(action)
    return [getattr(pygame, name) for name in key_names]

# In game loop
keys = pygame.key.get_pressed()
fire_keys = get_pygame_keys('fire')
if any(keys[k] for k in fire_keys):
    player.shoot()
```

## Accessibility System

### Overview

Accessibility settings in `config/accessibility.json` allow users to customize visual and audio feedback for improved accessibility.

### Configuration File Format

```json
{
    "version": "1.0",
    "colorblind_mode": {
        "enabled": false,
        "type": "none",
        "options": ["none", "protanopia", "deuteranopia", "tritanopia"]
    },
    "high_contrast_ui": {
        "enabled": false,
        "text_scale": 1.0,
        "outline_thickness": 1
    },
    "screen_shake": {
        "enabled": true,
        "intensity": 1.0
    },
    "flash_effects": {
        "enabled": true,
        "intensity": 1.0
    },
    "audio_cues": {
        "enabled": true,
        "volume": 1.0
    }
}
```

### Settings Reference

#### Colorblind Mode

| Type | Description |
|------|-------------|
| none | No color adjustment |
| protanopia | Red-blind (difficulty distinguishing red/green) |
| deuteranopia | Green-blind (most common, red/green confusion) |
| tritanopia | Blue-blind (difficulty with blue/yellow) |

When implementing colorblind support, consider:
- Use patterns or shapes in addition to color
- Ensure sufficient contrast between game elements
- Test with colorblind simulation tools

**Color palette recommendations for colorblind-friendly design:**
- Use blue and orange instead of red and green for contrasting elements
- Add texture or pattern variations to distinguish game objects
- Consider brightness differences, not just hue changes

**Example color transformations:**
```python
# Protanopia-friendly palette (avoid red-green distinctions)
COLORBLIND_PALETTES = {
    'protanopia': {
        'enemy': (0, 100, 255),      # Blue instead of red
        'friendly': (255, 200, 0),   # Yellow/orange
        'neutral': (150, 150, 150),  # Gray
    },
    'deuteranopia': {
        'enemy': (220, 100, 255),    # Magenta/purple
        'friendly': (0, 150, 255),   # Cyan/blue
        'neutral': (200, 200, 200),  # Light gray
    },
    'tritanopia': {
        'enemy': (255, 100, 100),    # Red
        'friendly': (100, 255, 100), # Green
        'neutral': (150, 150, 150),  # Gray
    }
}
```

#### High Contrast UI

- `enabled`: Toggle high contrast mode
- `text_scale`: Multiplier for text size (1.0 = 100%)
- `outline_thickness`: Pixel thickness for text/UI outlines

#### Motion Settings

- `screen_shake.enabled`: Enable/disable screen shake effects
- `screen_shake.intensity`: Scale shake intensity (0.0 to 1.0)
- `flash_effects.enabled`: Enable/disable flash effects
- `flash_effects.intensity`: Scale flash intensity (0.0 to 1.0)

#### Audio

- `audio_cues.enabled`: Enable/disable accessibility audio cues
- `audio_cues.volume`: Volume multiplier for audio cues

### Implementation Guidelines

When implementing features that respect accessibility settings:

```python
import json

# Default accessibility settings
DEFAULT_ACCESSIBILITY = {
    "colorblind_mode": {"enabled": False, "type": "none"},
    "high_contrast_ui": {"enabled": False, "text_scale": 1.0},
    "screen_shake": {"enabled": True, "intensity": 1.0},
    "flash_effects": {"enabled": True, "intensity": 1.0},
    "audio_cues": {"enabled": True, "volume": 1.0}
}

def load_accessibility_settings():
    try:
        with open('config/accessibility.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_ACCESSIBILITY.copy()

# Example: Conditional screen shake
settings = load_accessibility_settings()
if settings['screen_shake']['enabled']:
    intensity = base_intensity * settings['screen_shake']['intensity']
    apply_screen_shake(intensity)
```

## Adding New Features

### Adding a New Control Action

1. Add the action to `config/controls.json`:
   ```json
   "keyboard": {
       "new_action": ["K_x"]
   }
   ```

2. Add to `DEFAULT_CONTROLS` in `core/controls.py`

3. Use the new action in game code:
   ```python
   manager.get_keyboard_keys('new_action')
   ```

### Adding a New Accessibility Option

1. Add the option to `config/accessibility.json`:
   ```json
   "new_option": {
       "enabled": true,
       "value": 1.0
   }
   ```

2. Load and check the setting in relevant game code

3. Document the new option in this file and `CONTRIBUTING.md`

## Testing

### Manual Testing Checklist

- [ ] Controls load correctly from config file
- [ ] Default controls work when config is missing
- [ ] Invalid config falls back to defaults
- [ ] Gamepad deadzone is respected
- [ ] Accessibility settings load correctly
- [ ] Screen shake respects intensity setting
- [ ] High contrast mode is visually distinct

### Testing Controls

```python
from core.controls import ControlsManager

# Test loading
manager = ControlsManager()
manager.load()
assert manager.is_loaded

# Test keyboard keys
keys = manager.get_keyboard_keys('fire')
assert 'K_SPACE' in keys

# Test gamepad binding
binding = manager.get_gamepad_binding('fire')
assert binding['type'] == 'button'
```
