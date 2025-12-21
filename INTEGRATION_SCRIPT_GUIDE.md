# Integration Script Usage Guide

Automated integration of save/load, pause menu, and tutorial systems for Minmatar Rebellion.

## Quick Start (Recommended)

```bash
# 1. Copy script to your game directory
cp integrate_systems.py /path/to/minmatar-rebellion/

# 2. Navigate to game directory
cd /path/to/minmatar-rebellion/

# 3. Run the integration (creates automatic backup)
python integrate_systems.py
```

That's it! The script will:
- ✓ Automatically back up your `game.py`
- ✓ Add all imports
- ✓ Initialize all three systems
- ✓ Add save/load methods
- ✓ Hook up auto-save
- ✓ Add menu options
- ✓ Integrate tutorial system
- ✓ Show you exactly what it did

## Usage Options

### Dry Run (See What Will Happen)
```bash
# See what changes would be made WITHOUT modifying files
python integrate_systems.py --dry-run
```

### Skip Backup
```bash
# Skip creating backup (not recommended)
python integrate_systems.py --no-backup
```

### Custom Game Path
```bash
# If your game.py is elsewhere
python integrate_systems.py --game-path /custom/path/game.py
```

### Get Help
```bash
python integrate_systems.py --help
```

## What It Does

The script makes 9 targeted modifications to `game.py`:

1. **Adds imports** - Imports SaveManager, PauseMenu, Tutorial
2. **Initializes managers** - Creates instances in `Game.__init__`
3. **Adds save_game() method** - Handles saving player + game state
4. **Adds load_game() method** - Loads and applies saved state
5. **Auto-save trigger** - Saves when stage completes
6. **Load menu option** - Adds "Press L to Load Game" to menu
7. **Load event handler** - Handles L key press in menu
8. **Tutorial start** - Starts tutorial on new game
9. **Tutorial rendering** - Draws overlay in game

## Example Output

```
============================================================
Minmatar Rebellion - System Integration
============================================================

✓ All core modules found

✓ Backup created: game.py.backup_20241220_153045

Applying integrations...

✓ Added imports
✓ Added manager initialization
✓ Added save/load methods
✓ Added auto-save trigger
✓ Added load menu option
✓ Added load event handler
✓ Added tutorial start
✓ Added tutorial update
✓ Added tutorial overlay

============================================================
✓ Integration complete! Made 9 modifications:
  1. Added system imports
  2. Added manager initialization
  3. Added save_game() and load_game() methods
  4. Added auto-save trigger
  5. Added load game menu instruction
  6. Added load game key handler
  7. Added tutorial start trigger
  8. Added tutorial update call
  9. Added tutorial overlay rendering
============================================================

📋 Next Steps:
  1. Test the game: python game.py
  2. Try saving and loading
  3. Check the tutorial on first launch

💾 Backup saved to: game.py.backup_20241220_153045
   (Restore with: mv game.py.backup_20241220_153045 game.py)
```

## Safety Features

### Automatic Backup
Every run creates a timestamped backup:
```
game.py.backup_20241220_153045
```

To restore:
```bash
mv game.py.backup_20241220_153045 game.py
```

### Idempotent Design
The script can be run multiple times safely:
- Checks if changes already exist
- Skips duplicate modifications
- Won't break if run twice

### Dry Run Mode
Always test first:
```bash
python integrate_systems.py --dry-run
```

## Prerequisites

The script requires these files to exist:
```
core/
├── save_manager.py
├── pause_menu.py
└── tutorial.py
```

If any are missing, the script will tell you and exit safely.

## Testing Your Integration

After running the script, test each feature:

### 1. Test Save/Load
```bash
python game.py
# Play for a bit, complete a stage
# ESC to menu
# Press 'L' to load
# Verify you're back where you left off
```

### 2. Test Tutorial
```bash
python game.py
# Start new game
# Tutorial messages should appear at bottom
# Messages auto-advance
```

### 3. Test Pause Menu
```bash
python game.py
# During gameplay, press ESC
# Should see pause menu (not just "PAUSED" text)
```

## Troubleshooting

### "game.py not found"
Make sure you're in the game directory:
```bash
cd /path/to/minmatar-rebellion/
python integrate_systems.py
```

### "Missing required modules"
The core modules need to exist first. Make sure you have:
- `core/save_manager.py`
- `core/pause_menu.py`
- `core/tutorial.py`

### "Could not find..."
If the script can't find specific code patterns:
1. Run with `--dry-run` to see what's detected
2. Check your `game.py` structure matches expected patterns
3. You may need manual integration (see `QUICK_INTEGRATION.md`)

### Nothing changed
If the script says "already present, skipping" for everything:
- The integration was already done!
- Check if a previous run completed successfully

## Manual Rollback

If you need to undo everything:

```bash
# Option 1: Restore from backup
mv game.py.backup_TIMESTAMP game.py

# Option 2: Git reset (if using version control)
git checkout game.py

# Option 3: Remove specific changes
# Edit game.py and remove sections marked with comments like:
# "# Integrated systems"
# "# Auto-save on stage completion"
```

## Advanced: Customizing the Script

The `GameIntegrator` class has methods for each modification:
- `add_imports()` - Add system imports
- `add_manager_init()` - Initialize in __init__
- `add_save_load_methods()` - Add save/load methods
- `add_autosave_trigger()` - Hook auto-save
- `add_load_menu_option()` - Menu text
- `add_load_event_handler()` - Key handler
- `add_tutorial_start()` - Tutorial trigger
- `add_tutorial_update()` - Update loop
- `add_tutorial_overlay()` - Rendering

You can comment out specific methods in `integrate_all()` if you only want certain features.

## Support

If the automated script doesn't work for your setup:
1. Use `--dry-run` to see what it would do
2. Check the backup file to see what changed
3. Fall back to `QUICK_INTEGRATION.md` for manual steps
4. Review `CODE_SNIPPETS.md` for exact code to add

## Complete Workflow

```bash
# 1. Dry run to preview
python integrate_systems.py --dry-run

# 2. Run for real
python integrate_systems.py

# 3. Test the game
python game.py

# 4. If issues, restore backup
mv game.py.backup_TIMESTAMP game.py

# 5. If working, commit changes
git add game.py
git commit -m "Integrate save/load, pause menu, and tutorial systems"
```

## What's Next?

Once integration is complete:
- ✅ Test all three systems
- ✅ Customize tutorial messages in `data/tutorial.json`
- ✅ Adjust auto-save frequency if needed
- ✅ Add more pause menu options
- ✅ Build and test executables

See `INTEGRATION_GUIDE.md` for detailed documentation on customizing each system!
