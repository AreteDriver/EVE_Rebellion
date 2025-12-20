# Devil Blade Reboot Integration Guide
## Minmatar Rebellion - Berserk System Implementation

This guide shows how to integrate Devil Blade Reboot's signature **Berserk System** into your EVE-themed space shooter while maintaining the existing refugee rescue currency and progression systems.

---

## Overview

**What is the Berserk System?**
Devil Blade Reboot's core mechanic rewards **dangerous play** - the closer enemies are when destroyed, the higher the score multiplier:

- **EXTREME CLOSE** (0-80px): **5.0x** multiplier - INSANE!
- **CLOSE** (80-150px): **3.0x** multiplier - DANGEROUS!
- **MEDIUM** (150-250px): **1.5x** multiplier - RISKY
- **FAR** (250-400px): **1.0x** multiplier - SAFE
- **VERY FAR** (400+px): **0.5x** multiplier - COWARD

This creates the classic risk/reward dynamic: play safe for survival, or push close for massive scores.

---

## Integration Steps

### 1. Add the Modules

Copy these files into your game directory:
- `berserk_system.py` - Core Berserk System and danger tracking
- `devil_blade_effects.py` - Visual effects (explosions, screen shake, flashes)

```bash
# Place in your game root alongside game.py
cp berserk_system.py /path/to/minmatar-rebellion/
cp devil_blade_effects.py /path/to/minmatar-rebellion/
```

### 2. Import in game.py

Add to the top of `game.py`:

```python
from berserk_system import BerserkSystem, DangerIndicator, create_berserk_game_systems
from devil_blade_effects import EffectManager
```

### 3. Initialize Systems in Game.__init__()

```python
class Game:
    def __init__(self):
        # ... existing initialization ...
        
        # Devil Blade Reboot systems
        self.berserk_system, self.danger_indicator = create_berserk_game_systems()
        self.effect_manager = EffectManager()
        
        # Optional: Enable retro CRT scanlines
        # self.effect_manager.enable_scanlines(SCREEN_HEIGHT, spacing=2, opacity=30)
```

### 4. Modify Enemy Kill Handling

Find where you handle enemy deaths (likely in `game.py` or `sprites.py`). Replace the score calculation:

**BEFORE:**
```python
def handle_enemy_death(enemy):
    base_score = enemy.score_value
    self.score += base_score
    # ... handle refugees, etc ...
```

**AFTER:**
```python
def handle_enemy_death(enemy):
    # Calculate berserked score based on distance
    player_pos = (self.player.rect.centerx, self.player.rect.centery)
    enemy_pos = (enemy.rect.centerx, enemy.rect.centery)
    
    base_score = enemy.score_value
    final_score = self.berserk_system.register_kill(
        base_score, 
        player_pos, 
        enemy_pos,
        enemy.type
    )
    
    self.score += final_score
    
    # Visual effects
    self.effect_manager.add_explosion(
        enemy_pos, 
        (255, 150, 50),  # Orange explosion
        particle_count=30,
        spread=8.0
    )
    
    # Screen shake for close kills
    multiplier, range_name = self.berserk_system.calculate_multiplier(player_pos, enemy_pos)
    if range_name == 'EXTREME':
        self.effect_manager.add_shake(intensity=8, duration=12)
        self.effect_manager.add_flash((255, 100, 100), duration=8, alpha=120)
    elif range_name == 'CLOSE':
        self.effect_manager.add_shake(intensity=5, duration=8)
    
    # ... handle refugees, etc ...
```

### 5. Update Game Loop

Add to your main `update()` method:

```python
def update(self):
    # ... existing update logic ...
    
    # Update Berserk system
    self.berserk_system.update()
    self.danger_indicator.update_danger(
        (self.player.rect.centerx, self.player.rect.centery),
        self.enemies,  # Your enemy sprite group
        self.berserk_system
    )
    
    # Update visual effects
    self.effect_manager.update()
```

### 6. Add to Rendering

Modify your `draw()` / `render()` method:

```python
def draw(self):
    # Apply screen shake offset
    shake_x, shake_y = self.effect_manager.get_shake_offset()
    
    # Draw background (with shake)
    self.screen.blit(self.background, (shake_x, shake_y))
    
    # Draw background effects (trails, rings)
    self.effect_manager.draw_background_effects(self.screen)
    
    # Draw gameplay elements (with shake)
    # ... draw enemies, player, bullets, etc ...
    # Add shake_x, shake_y to all positions during shake
    
    # Draw foreground effects (explosions, flashes)
    self.effect_manager.draw_foreground_effects(self.screen)
    
    # Draw HUD (no shake on UI)
    self.draw_hud()
```

### 7. Add Berserk HUD Elements

In your HUD drawing code:

```python
def draw_hud(self):
    # ... existing HUD elements (score, health, ammo, etc.) ...
    
    # Berserk multiplier indicator (top-right)
    self.berserk_system.draw_hud(
        self.screen, 
        SCREEN_WIDTH - 20,  # Right side
        20,                  # Top
        self.font_small, 
        self.font_large
    )
    
    # Optional: Score popups (floating damage numbers)
    self.berserk_system.draw_popups(
        self.screen,
        self.font_small,
        self.font_large
    )
    
    # Optional: Danger zone visualization (bottom-center)
    # self.danger_indicator.draw(self.screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 30)
    
    # Optional: Visual danger zones around player (for learning/practice mode)
    # self.berserk_system.draw_danger_zones(
    #     self.screen,
    #     (self.player.rect.centerx, self.player.rect.centery),
    #     alpha=40  # Subtle
    # )
```

### 8. Add to End-of-Stage Stats

```python
def show_stage_results(self):
    stats = self.berserk_system.get_stats()
    
    # Display stats
    print(f"Total Score: {stats['total_score']}")
    print(f"Average Multiplier: {stats['avg_multiplier']:.2f}x")
    print(f"Extreme Close Kills: {stats['extreme_kills']}")
    print(f"Kills by Range:")
    for range_name, count in stats['kills_by_range'].items():
        print(f"  {range_name}: {count}")
    
    # Reset for next stage
    self.berserk_system.reset_session()
```

---

## Advanced Features

### Bullet Impact Effects

Add visual feedback when bullets hit enemies:

```python
def on_bullet_hit(bullet, enemy):
    impact_pos = (bullet.rect.centerx, bullet.rect.centery)
    
    # Impact ring
    self.effect_manager.add_impact_ring(
        impact_pos,
        (255, 200, 100),  # Yellow-orange
        max_radius=25
    )
    
    # Small particle burst
    self.effect_manager.add_explosion(
        impact_pos,
        (255, 255, 100),
        particle_count=8,
        spread=3.0
    )
```

### Bullet Trails

For enhanced visual feedback on projectiles:

```python
def update_bullets(self):
    for bullet in self.bullets:
        old_pos = (bullet.rect.centerx, bullet.rect.centery)
        bullet.update()
        new_pos = (bullet.rect.centerx, bullet.rect.centery)
        
        # Add trail
        self.effect_manager.add_trail(
            old_pos,
            new_pos,
            (100, 200, 255),  # Minmatar blue
            lifetime=3
        )
```

### Boss Kill Effects

Extra dramatic effects for boss defeats:

```python
def on_boss_defeated(boss):
    boss_pos = (boss.rect.centerx, boss.rect.centery)
    
    # Massive explosion
    self.effect_manager.add_explosion(
        boss_pos,
        (255, 100, 100),
        particle_count=100,
        spread=15.0
    )
    
    # Screen flash
    self.effect_manager.add_flash(
        (255, 255, 255),
        duration=20,
        alpha=200
    )
    
    # Heavy shake
    self.effect_manager.add_shake(intensity=15, duration=30)
```

---

## Balancing Tips

### Score Values

The Berserk System multiplies your **base score values**. For good balance:

```python
# Enemy base scores (before Berserk multiplier)
ENEMY_SCORES = {
    'frigate': 100,      # x5.0 extreme = 500
    'destroyer': 250,    # x5.0 extreme = 1250
    'cruiser': 500,      # x5.0 extreme = 2500
    'battleship': 1000,  # x5.0 extreme = 5000
}
```

### Distance Tuning

You can adjust the distance thresholds in `berserk_system.py`:

```python
class BerserkSystem:
    # Make it harder (smaller danger zones)
    EXTREME_CLOSE = 60   # Was 80
    CLOSE = 120          # Was 150
    
    # Or easier (larger danger zones)
    EXTREME_CLOSE = 100  # Was 80
    CLOSE = 180          # Was 150
```

### Visual Intensity

Tone down effects if they're too distracting:

```python
# Fewer particles
self.effect_manager.add_explosion(pos, color, particle_count=15)  # Was 30

# Less screen shake
self.effect_manager.add_shake(intensity=3, duration=8)  # Was 8, 12

# Subtler flashes
self.effect_manager.add_flash(color, duration=6, alpha=80)  # Was 10, 180
```

---

## Testing Checklist

- [ ] Score increases correctly with distance (check console/HUD)
- [ ] Visual popups show multiplier values
- [ ] Screen shake triggers on close kills
- [ ] Particle explosions appear on enemy deaths
- [ ] Danger indicator updates based on enemy proximity
- [ ] Stats display correctly at end of stage
- [ ] System resets properly between stages
- [ ] Performance is acceptable (60 FPS target)
- [ ] Works with existing refugee rescue system
- [ ] Multiplier HUD displays in top-right

---

## Compatibility Notes

### Refugee Rescue System
The Berserk System is **fully compatible** with your refugee currency:
- Berserk affects **score** (for leaderboards, bragging rights)
- Refugees are still collected normally
- Use refugees for ship upgrades (existing system)
- Use score for ranking/achievements

### Skill Points System
The Berserk System can integrate with skill unlocks:
- Award skill points based on **average multiplier** per stage
- Unlock skills that increase Berserk multipliers
- Add skills that extend danger zones for easier extreme kills

### Multiple Ships
Each ship can have different Berserk characteristics:
```python
# In ship stats
'rifter': {
    'berserk_bonus': 1.0,      # Standard
    'danger_threshold_mod': 1.0
},
'jaguar': {
    'berserk_bonus': 1.2,      # +20% all multipliers
    'danger_threshold_mod': 1.1  # Slightly larger danger zones
}
```

---

## Performance Optimization

If you experience slowdowns:

1. **Limit particle count**: Cap explosions at 20-30 particles
2. **Reduce trail lifetime**: Set trails to 2-3 frames instead of 5
3. **Disable scanlines**: Comment out CRT effect if not needed
4. **Pool effects**: Reuse effect objects instead of creating new ones
5. **Cull off-screen effects**: Don't update/draw effects outside viewport

Example pooling:
```python
class EffectManager:
    def __init__(self):
        # ... existing ...
        self.explosion_pool = []  # Reuse explosion objects
    
    def add_explosion(self, pos, color, count, spread):
        if self.explosion_pool:
            # Reuse existing
            explosion = self.explosion_pool.pop()
            explosion.reset(pos, color, count, spread)
        else:
            # Create new
            explosion = PixelExplosion(pos, color, count, spread)
        self.explosions.append(explosion)
```

---

## Troubleshooting

### Multipliers not showing
- Check that `berserk_system.draw_hud()` is called in your HUD render
- Verify fonts are loaded: `self.font_small`, `self.font_large`

### Screen shake too intense
- Reduce intensity parameter: `add_shake(intensity=3)` instead of `8`
- Reduce duration: `duration=6` instead of `12`

### Score popups not appearing
- Ensure `draw_popups()` is called AFTER gameplay rendering but BEFORE final flip
- Check that popup lifetime (90 frames) isn't too short for your frame rate

### Effects causing slowdown
- Limit concurrent explosions: `if len(self.explosions) < 10:`
- Reduce particle counts
- Disable scanlines
- Profile with: `python -m cProfile game.py`

---

## Future Enhancements

Ideas for extending the Berserk System:

1. **Combo System**: Chain kills quickly for multiplier stacking
2. **Risk Levels**: Dynamic difficulty that increases with high multipliers
3. **Berserk Gauge**: Fill a meter to trigger temporary 10x multiplier mode
4. **Achievements**: "100 Extreme Kills", "Perfect Berserk Stage" (all kills at 3x+)
5. **Leaderboards**: Separate scores for Safe vs Berserk playstyles
6. **Visual Themes**: Unlock different particle effects/screen shakes
7. **Sound Integration**: Procedural audio intensity based on danger level

---

## Credits

Devil Blade Reboot mechanics by **Mikito Ichikawa**  
Integration for Minmatar Rebellion by **ARETE**  
Based on EVE Online by **CCP Games**

---

## License Note

This integration is for your personal project pitch to CCP Games. The Berserk System mechanic is inspired by but legally distinct from Devil Blade Reboot. You're implementing similar risk/reward mechanics in your own codebase, which is standard game design practice. Ensure your final pitch clearly distinguishes your implementation as "Devil Blade-inspired" rather than a direct copy.
