# Devil Blade Reboot Integration - Quick Reference

## 🎮 Core Concept
**Risk = Reward**: Closer kills = Higher multipliers

## 📏 Distance Ranges

| Distance | Multiplier | Risk Level | Color |
|----------|-----------|------------|--------|
| 0-80px   | **5.0x**  | EXTREME 🔴 | Red |
| 80-150px | **3.0x**  | CLOSE 🟠 | Orange |
| 150-250px| **1.5x**  | MEDIUM 🟡 | Yellow |
| 250-400px| **1.0x**  | FAR 🟢 | Green |
| 400+px   | **0.5x**  | COWARD 🔵 | Blue |

## ⚡ Quick Implementation

### Minimal Integration (5 minutes)
```python
# 1. Import
from berserk_system import BerserkSystem

# 2. Initialize
self.berserk = BerserkSystem()

# 3. On enemy kill
score = self.berserk.register_kill(
    100,  # base score
    player_pos,
    enemy_pos
)

# 4. Update each frame
self.berserk.update()

# 5. Draw HUD
self.berserk.draw_hud(screen, x, y, font_small, font_large)
```

### Full Integration (30 minutes)
Add visual effects, screen shake, danger zones, stats tracking
→ See DEVIL_BLADE_INTEGRATION.md

## 🎨 Visual Effects

```python
from devil_blade_effects import EffectManager

effects = EffectManager()

# Explosion
effects.add_explosion(pos, color, particles=30, spread=8)

# Screen shake
effects.add_shake(intensity=5, duration=10)

# Flash
effects.add_flash((255,255,255), duration=10, alpha=180)

# Trail
effects.add_trail(start, end, color, lifetime=5)

# Impact ring
effects.add_impact_ring(pos, color, radius=30)

# Update & draw
effects.update()
effects.draw_background_effects(screen)  # Trails/rings
# ... draw game ...
effects.draw_foreground_effects(screen)  # Explosions/flashes
```

## 📊 Statistics

```python
stats = self.berserk.get_stats()

stats['total_score']        # Total points earned
stats['avg_multiplier']     # Average risk taken
stats['extreme_kills']      # Kills at 5.0x
stats['kills_by_range']     # Dict of kills per range
```

## 🎯 Balancing Quick Tips

**Too Easy?** → Reduce danger zone sizes
```python
EXTREME_CLOSE = 60  # Was 80
```

**Too Hard?** → Increase danger zones
```python
EXTREME_CLOSE = 100  # Was 80
```

**Effects too intense?** → Lower particle counts
```python
add_explosion(pos, color, particles=15)  # Was 30
```

**Too much screen shake?** → Reduce intensity
```python
add_shake(intensity=3)  # Was 8
```

## 🏆 Achievements Ideas

- "Berserk Master": 100 kills at 5.0x
- "Perfect Danger": Complete stage with 3.0x+ average
- "No Fear": Never kill beyond 150px for entire stage
- "Safe Player": Complete stage with 1.0x average (survival run)

## 🔧 Troubleshooting

**Problem:** Multipliers not showing
**Fix:** Check `draw_hud()` is called with proper fonts

**Problem:** Effects causing lag
**Fix:** Reduce particle counts, limit concurrent effects

**Problem:** Shake too violent
**Fix:** Lower intensity parameter (try 3-5 instead of 8-12)

**Problem:** Colors wrong
**Fix:** Check RGB tuples in RANGE_COLORS dict

## 📱 HUD Layout Suggestion

```
┌──────────────────────────────────┐
│ SCORE: 125,750        x3.0 🟠    │ ← Top bar
│                        BERSERK    │
├──────────────────────────────────┤
│                                   │
│          [GAMEPLAY AREA]          │
│                                   │
│     +500 x5.0                     │ ← Score popup
│     BERSERK!                      │
│                                   │
├──────────────────────────────────┤
│ ████████░░░░░░░░░░  DANGER        │ ← Bottom bar
│ RIFTER   REFUGEES: 45  AMMO: AC   │
└──────────────────────────────────┘
```

## 🎬 When to Trigger Effects

| Event | Effect |
|-------|--------|
| Any kill | Small explosion (20 particles) |
| Close kill (3.0x) | Medium explosion + light shake |
| Extreme kill (5.0x) | Large explosion + heavy shake + flash |
| Boss death | Massive explosion + long shake + bright flash |
| Bullet impact | Impact ring + tiny sparks (8 particles) |

## 💡 Pro Tips

1. **Combine with EVE lore**: "Optimal range" bonuses fit EVE's tactical combat
2. **Balance vs Refugees**: High-risk players get score, safe players save more refugees
3. **Difficulty scaling**: Berserk makes game easier for skilled players (more score) but harder (more danger)
4. **Tutorial**: Show danger zones in first stage, hide them later
5. **Accessibility**: Option to show/hide visual danger rings for learning

## 📦 Files Required

- `berserk_system.py` - Core mechanics (300 lines)
- `devil_blade_effects.py` - Visual effects (400 lines)
- `DEVIL_BLADE_INTEGRATION.md` - Full guide

Total code: ~700 lines  
Integration time: 30-60 minutes  
Compatible with: All existing Minmatar Rebellion systems

---

**Remember:** The Berserk System is about player choice. Let players choose their risk level - don't force aggressive play!
