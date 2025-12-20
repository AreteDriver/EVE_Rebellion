# EVE SHIP IMAGES INTEGRATION

## What's New?

Your game now displays **actual EVE Online ship silhouettes** instead of procedural graphics!

## Ships Integrated:

### Player Ships (Minmatar):
- **Rifter** - Your starting frigate (rust/brown colored)
- **Wolf** - T2 Assault Frigate upgrade (orange/metallic)

### Enemy Ships (Amarr):
- **Executioner** - Fast attack frigate
- **Punisher** - Armor-tanked frigate
- **Omen** - Cruiser
- **Maller** - Heavy cruiser
- **Bestower** - Industrial (drops refugees)
- **Apocalypse** - Battleship boss
- **Abaddon** - Dreadnought final boss

## How It Works:

1. **SVG Files**: 267 ship silhouettes in `svg/top/` folder
2. **Ship Loader**: Automatically loads the right ship for each enemy
3. **Fallback System**: If SVGs don't load, uses procedural graphics
4. **Color Tinting**: Ships are tinted to match faction colors

## Technical Details:

### Required Library:
- **cairosvg** - Converts SVG to PNG for pygame

### Installation:
```bash
pip install cairosvg
```

Or just run `INSTALL.bat` on Windows!

### Files Modified:
- `ship_loader.py` - New SVG loading module
- `sprites.py` - Updated to use ship images
- `requirements.txt` - Added cairosvg

## Testing:

Run the ship loader test:
```bash
python ship_loader.py
```

You should see:
```
✓ Loaded rifter: 64x64
✓ Loaded wolf: 64x64
✓ Loaded apocalypse: 64x64
✓ Loaded abaddon: 64x64
```

## Troubleshooting:

### "SVG directory not found"
- Make sure `svg/top/` folder exists
- Extract the full game package

### "SVG libraries not available"
```bash
pip install cairosvg
```

### Ships still showing as procedural graphics:
- Check that cairosvg installed correctly
- Run `python ship_loader.py` to test
- Game will automatically fall back to procedural if SVGs fail

### On Linux, cairosvg installation fails:
```bash
# Install system dependencies first
sudo apt-get install libcairo2-dev pkg-config
pip install cairosvg
```

## Future Enhancements:

Want to add more ships? You have 267 available!

Edit `constants.py` ENEMY_STATS and add new enemy types:
```python
'drake': {  # Caldari missile boat
    'name': 'Drake',
    'shields': 200,
    'armor': 100,
    'hull': 100,
    # ... more stats
}
```

The ship loader will automatically find `drake.svg`!

## Performance:

- **First Load**: SVGs converted to PNG (cached)
- **Subsequent**: Uses cached images
- **Memory**: ~2MB for all ships
- **FPS Impact**: None (loaded at spawn, not per frame)

## Credits:

Ship silhouettes from EVE Online.
All rights belong to CCP Games.

---

*Now go see those beautiful ship silhouettes in action!* 🚀
