# Quick Integration Guide - 15 Minutes

This guide gets save/load, pause menu, and tutorial working in your game in ~15 minutes.

## Step 1: Add Imports (2 min)

Open `game.py` and add these imports at the top after existing imports:

```python
from core.save_manager import SaveManager
from core.pause_menu import PauseMenu
from core.tutorial import Tutorial
```

## Step 2: Initialize Managers in Game.__init__ (3 min)

In the `Game.__init__()` method, add these lines after your existing initialization code (around line 50-60):

```python
# Add these three lines in Game.__init__()
self.save_manager = SaveManager()
self.pause_menu = PauseMenu()
self.tutorial = Tutorial()
```

## Step 3: Add Save/Load Methods (5 min)

Add these two methods to your `Game` class (anywhere in the class body):

```python
def save_game(self):
    """Save current game state"""
    player_state = self.save_manager.extract_player_state(self.player)
    game_state = {
        'current_stage': self.current_stage,
        'current_wave': self.current_wave,
        'difficulty': self.difficulty
    }
    return self.save_manager.save(player_state, game_state)

def load_game(self):
    """Load saved game state"""
    player_state, game_state = self.save_manager.load()
    if player_state and game_state:
        # Apply loaded state
        self.save_manager.apply_player_state(self.player, player_state)
        self.current_stage = game_state.get('current_stage', 0)
        self.current_wave = game_state.get('current_wave', 0)
        self.difficulty = game_state.get('difficulty', 'normal')
        return True
    return False
```

## Step 4: Wire Up Auto-Save (2 min)

In your `update_waves()` method, find where you handle stage completion and add auto-save:

```python
# In update_waves() when stage completes, add:
if self.current_wave >= stage['waves']:
    self.stage_complete = True
    self.save_game()  # <-- Add this line for auto-save
    # ... rest of your code
```

## Step 5: Add Load Game Menu Option (3 min)

In your `draw_menu()` method, add a load game option. Update the menu rendering to show:

```python
# In draw_menu(), add these instructions:
instructions = [
    "WASD or Arrow Keys - Move",
    "Space or Left Click - Fire Autocannons",
    # ... your existing instructions ...
    "",
    "Press ENTER to Start",
    "Press L to Load Game"  # <-- Add this
]
```

Then in `handle_events()` where you handle the menu state:

```python
elif self.state == 'menu':
    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
        self.state = 'difficulty'
        self.play_sound('menu_select')
    elif event.key == pygame.K_l:  # <-- Add this block
        if self.load_game():
            self.state = 'playing'
            self.show_message("Game Loaded!", 120)
            self.play_sound('menu_select')
        else:
            self.play_sound('error')
```

## Step 6: Enhanced Pause Menu (Optional - adds 5 min)

Replace your simple pause handling with the full pause menu system:

In `handle_events()` where you handle ESC key in 'playing' state:

```python
elif self.state == 'playing':
    if event.key == pygame.K_ESCAPE:
        self.pause_menu.show()
        self.state = 'paused'
```

In `handle_events()` where you handle 'paused' state, replace with:

```python
elif self.state == 'paused':
    if event.key == pygame.K_ESCAPE:
        self.pause_menu.hide()
        self.state = 'playing'
    elif event.key == pygame.K_UP:
        self.pause_menu.navigate_up()
    elif event.key == pygame.K_DOWN:
        self.pause_menu.navigate_down()
    elif event.key == pygame.K_LEFT:
        # Decrease selected setting
        result = self.pause_menu.handle_input(True, False, False)
        if result == 'resume':
            self.state = 'playing'
    elif event.key == pygame.K_RIGHT:
        # Increase selected setting
        result = self.pause_menu.handle_input(False, True, False)
        if result == 'resume':
            self.state = 'playing'
    elif event.key == pygame.K_RETURN:
        result = self.pause_menu.handle_input(False, False, True)
        if result == 'resume':
            self.state = 'playing'
```

In `draw_pause()`, replace the simple overlay with:

```python
def draw_pause(self):
    """Draw enhanced pause menu"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    self.render_surface.blit(overlay, (0, 0))
    
    # Get pause menu display data
    menu_data = self.pause_menu.get_display_data()
    
    # Title
    title = self.font_large.render("PAUSED", True, COLOR_TEXT)
    self.render_surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 150))
    
    # Menu options
    y = 250
    options = ['Music Volume', 'SFX Volume', 'Difficulty', 'Resume']
    for i, option in enumerate(options):
        selected = (i == menu_data['selected_option'])
        color = COLOR_MINMATAR_ACCENT if selected else COLOR_TEXT
        
        if option == 'Music Volume':
            text = f"[{'>' if selected else ' '}] Music: {int(menu_data['music_volume']*100)}%"
        elif option == 'SFX Volume':
            text = f"[{'>' if selected else ' '}] SFX: {int(menu_data['sfx_volume']*100)}%"
        elif option == 'Difficulty':
            text = f"[{'>' if selected else ' '}] Difficulty: {menu_data['difficulty'].upper()}"
        else:
            text = f"[{'>' if selected else ' '}] Resume"
        
        rendered = self.font.render(text, True, color)
        self.render_surface.blit(rendered, (SCREEN_WIDTH//2 - rendered.get_width()//2, y))
        y += 40
```

## Step 7: Tutorial System (Optional - adds 3 min)

Add tutorial to the beginning of the game. In your `set_difficulty()` method or wherever you start a new game:

```python
def set_difficulty(self, difficulty):
    """Set game difficulty and start"""
    self.difficulty = difficulty
    self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
    self.reset_game()
    self.tutorial.start()  # <-- Add this line
    self.state = 'playing'
    # ... rest of code
```

In your `update()` method, add tutorial update:

```python
def update(self):
    """Update game state"""
    if self.state != 'playing':
        return
    
    # Update tutorial
    if self.tutorial.is_active:
        self.tutorial.update(1/FPS)  # Pass delta time in seconds
    
    # ... rest of your update code
```

In your `draw_game()` method, add tutorial overlay at the end:

```python
def draw_game(self):
    """Draw gameplay elements"""
    # ... your existing drawing code ...
    
    # Draw tutorial overlay if active
    if self.tutorial.is_active:
        tutorial_data = self.tutorial.get_display_data()
        if tutorial_data['message']:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.render_surface.blit(overlay, (0, SCREEN_HEIGHT - 200))
            
            # Message
            msg = self.font.render(tutorial_data['message'], True, (255, 255, 255))
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
            self.render_surface.blit(msg, msg_rect)
            
            # Progress indicator
            progress = f"Step {tutorial_data['progress']['current']}/{tutorial_data['progress']['total']}"
            progress_text = self.font_small.render(progress, True, (200, 200, 200))
            self.render_surface.blit(progress_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30))
```

## Testing Your Integration

1. **Test Save/Load:**
   - Start a new game
   - Play for a bit and complete a stage (triggers auto-save)
   - Return to menu (ESC multiple times)
   - Press 'L' to load game
   - Verify you're at the same stage with same stats

2. **Test Pause Menu:**
   - During gameplay, press ESC
   - Use arrow keys to navigate options
   - Use LEFT/RIGHT to adjust volume
   - Press ENTER on Resume to continue

3. **Test Tutorial:**
   - Start a new game
   - Tutorial messages should appear at bottom of screen
   - Messages auto-advance after a few seconds

## Troubleshooting

**Import errors?**
- Make sure `core/save_manager.py`, `core/pause_menu.py`, and `core/tutorial.py` exist
- Check that `core/__init__.py` exists

**Save not working?**
- Check that `saves/` directory gets created automatically
- Verify `save_game()` is being called on stage completion

**Pause menu not showing?**
- Make sure you replaced `draw_pause()` with the enhanced version
- Check that pause menu state is properly toggled

**Tutorial not appearing?**
- Verify `tutorial.start()` is called when starting a new game
- Make sure tutorial overlay code is in `draw_game()`

## What You Get

✅ **Checkpoint saves** - Auto-save on stage completion
✅ **Manual load** - Load from main menu with 'L' key  
✅ **Pause menu** - Volume controls and settings
✅ **Tutorial** - Step-by-step guide for new players
✅ **Persistent config** - Settings saved to `config/options.json`

**Total time:** ~15-20 minutes for basic integration, ~25-30 minutes with all optional features.

## Next Steps

Once working, you can:
- Add more tutorial steps in `data/tutorial.json`
- Add checkpoint save button in pause menu
- Add multiple save slots in menu
- Customize tutorial styling
- Add tutorial skip button

See `INTEGRATION_GUIDE.md` for detailed documentation of all features.
