# DEVIL BLADE REBOOT CONTROLLER DESIGN
## EVE Rebellion - Vertical Shmup Control Philosophy

**Source**: Devil Blade Reboot by SHIGATAKE GAMES (May 2024)  
**Genre**: Vertical scrolling shoot-em-up with point-blank scoring  
**Core Mechanic**: Proximity multipliers + Berserk mode

---

## 🎮 DEVIL BLADE REBOOT CONTROLS

### Original Control Scheme
```
Button 1: Shot (continuous fire)
Button 2: Bomb/Boost (hold to activate Boost)
Button 3: Change shot type (Wide ↔ Narrow)
```

### Key Mechanics
1. **Point-Blank Scoring**: Closer to enemy = higher multiplier (x1 → x4)
2. **Berserk Mode**: Doubles all multipliers (x5 → x20) when gauge fills
3. **Boost System**: Hold Bomb button to spend bomb + increase Berserk gain 5x
4. **Shot Switching**: Wide (fast movement) ↔ Narrow (slow + focused)
5. **Auto-Bomb**: Easy/Normal difficulties auto-bomb on hit

---

## 🎯 CONTROLLER LAYOUT FOR EVE REBELLION

### Analog Movement (Left Stick)
**CRITICAL DIFFERENCE FROM PREVIOUS DESIGN**:
- Vertical shmups use **slower, more deliberate movement**
- NOT twitchy arcade-shooter like horizontal shmups
- Narrow shot mode = even slower (50% speed reduction)

```python
# Vertical shmup movement curve
def vertical_shmup_curve(value: float, focused: bool) -> float:
    """
    Slower, more measured movement for vertical shmup.
    Focused mode (narrow shot) = 50% speed.
    """
    if value == 0.0:
        return 0.0
    
    sign = 1.0 if value > 0 else -1.0
    
    # Gentler curve than horizontal shmup
    base = sign * pow(abs(value), 1.5)  # 1.5 vs 1.8 = less momentum
    
    if focused:
        return base * 0.5  # Narrow shot = half speed
    return base
```

---

## 🔥 BERSERK SYSTEM (Heat in EVE Rebellion)

Devil Blade Reboot's **Berserk Mode** = EVE Rebellion's **Heat System**

### Berserk Mechanics (from Devil Blade)
- **Gain**: Point-blank kills fill Berserk gauge
- **Loss**: Timer expires if not maintained
- **Boost**: Hold Bomb button = 5x Berserk gain (costs 1 bomb)
- **Effect**: Doubles all multipliers (x1→x5, x2→x10, x4→x20)
- **Rank**: Berserk increases enemy difficulty + health

### Translated to EVE Rebellion Heat
```
Heat Gain:
- Close kills: +10% Heat
- Medium kills: +5% Heat
- Far kills: +2% Heat
- Refugee rescue: +15% Heat

Heat Loss:
- Passive decay: -5% per second (like Berserk timer)
- Death: -50% Heat (penalty for dying)

Heat Effects:
- 0-24%: Normal multipliers (x1 → x4)
- 25-49%: Increased multipliers (x2 → x8)
- 50-74%: High multipliers (x3 → x12)
- 75-100%: BERSERK (x5 → x20)

Heat Consequences:
- 75%+ Heat: Fleet AI more aggressive, enemies spawn faster
- 100% Heat: Max damage output, max danger
```

---

## 🎮 CORRECTED BUTTON LAYOUT

### Face Buttons (Based on Devil Blade 3-button setup)

| Button | Devil Blade | EVE Rebellion | Why |
|--------|-------------|---------------|-----|
| **A / Cross** | Shot | Auto-fire (toggle) | Held for continuous fire is standard |
| **B / Circle** | Bomb/Boost | Emergency Burn | Panic button (same position) |
| **X / Square** | (unused) | Deploy Fleet | High-risk action |
| **Y / Triangle** | Change Shot Type | Formation Switch | Tactical swap |

### Triggers (Shmup Standard)

| Trigger | Function | Devil Blade Equivalent |
|---------|----------|------------------------|
| **RT / R2** | Primary Fire | Button 1 (Shot) |
| **LT / L2** | Boost Mode | Button 2 (Bomb/Boost held) |

**Why Triggers for Shooting?**
- Vertical shmups = constant firing
- Pressure-sensitive triggers allow future "charge shot" mechanics
- Frees face buttons for tactical decisions

### Bumpers (Quick Access)

| Bumper | Function | Devil Blade Equivalent |
|--------|----------|------------------------|
| **LB / L1** | Cycle Ammo Prev | (not in Devil Blade) |
| **RB / R1** | Cycle Ammo Next | (not in Devil Blade) |

### Shot Type Toggle (Critical Mechanic)

**Devil Blade**: Button 3 switches Wide ↔ Narrow  
**EVE Rebellion**: Y/Triangle switches formations

```python
# Shot type affects movement speed
class Player:
    def __init__(self):
        self.shot_type = "wide"  # "wide" or "narrow"
        self.base_speed = 200
    
    def get_movement_speed(self):
        if self.shot_type == "narrow":
            return self.base_speed * 0.5  # Slow + focused
        return self.base_speed  # Fast + spread
    
    def toggle_shot_type(self):
        if self.shot_type == "wide":
            self.shot_type = "narrow"
            play_sound("focus_on")
        else:
            self.shot_type = "wide"
            play_sound("focus_off")
```

---

## 📊 BOOST SYSTEM (Devil Blade's Best Mechanic)

### Original Devil Blade Boost
```
Hold Bomb button = Boost mode
- Costs 1 bomb
- Increases Berserk gain by 5x
- Acts as shield (Easy/Normal)
- Used strategically during boss fights to max Berserk
```

### EVE Rebellion Adaptation
```python
class BoostSystem:
    """
    LT/L2 held = Boost mode
    Drains Heat rapidly but increases gain multiplier
    """
    
    def __init__(self):
        self.boost_active = False
        self.boost_cost = 25  # Heat cost to activate
        self.heat_multiplier = 5.0  # 5x Heat gain
        self.drain_rate = 10  # -10 Heat/sec while boosting
    
    def update(self, dt, controller, heat):
        # LT/L2 held = Boost
        if controller.alternate_fire and heat >= self.boost_cost:
            if not self.boost_active:
                # Activate Boost
                self.boost_active = True
                heat -= self.boost_cost
                controller._rumble(0.6, 100)
                play_sound("boost_start")
            
            # Apply effects while active
            heat -= self.drain_rate * dt  # Constant drain
            
            # Visual feedback
            self.render_boost_aura()
        
        else:
            if self.boost_active:
                self.boost_active = False
                play_sound("boost_end")
        
        return heat
    
    def get_heat_multiplier(self):
        return self.heat_multiplier if self.boost_active else 1.0
```

**Strategic Use**:
- Boss appears → Hold LT to activate Boost
- Rush into point-blank range
- Kill boss with max multiplier
- Berserk gauge fills 5x faster
- High risk = high reward

---

## 🎯 POINT-BLANK PROXIMITY SYSTEM

### Devil Blade Distance Multipliers
```
Distance from enemy on death:
- 0-50px: x4 multiplier
- 51-100px: x3 multiplier
- 101-150px: x2 multiplier
- 151+px: x1 multiplier

Berserk doubles these: x4 → x8, x3 → x6, etc.
Max Berserk: x4 → x20
```

### EVE Rebellion Implementation
```python
def calculate_kill_score(enemy, player_pos):
    """
    Score based on proximity when enemy dies.
    Matches Devil Blade's point-blank reward.
    """
    dx = enemy.x - player_pos[0]
    dy = enemy.y - player_pos[1]
    dist = math.sqrt(dx*dx + dy*dy)
    
    # Distance brackets (pixels)
    if dist < 50:
        proximity_mult = 4
    elif dist < 100:
        proximity_mult = 3
    elif dist < 150:
        proximity_mult = 2
    else:
        proximity_mult = 1
    
    # Heat multiplier
    heat_mult = get_heat_multiplier(current_heat)
    
    # Base score
    base = enemy.base_value
    
    # Final calculation
    score = base * proximity_mult * heat_mult
    
    # Visual feedback
    if proximity_mult >= 3:
        show_proximity_indicator("CLOSE!", color=YELLOW)
    if proximity_mult == 4:
        show_proximity_indicator("POINT BLANK!!", color=RED)
        controller._rumble(0.4, 50)
    
    return score
```

---

## 🔊 HAPTIC FEEDBACK (Shmup-Specific)

### Devil Blade Feel
Vertical shmups are about **tension building**, not constant chaos.

```python
class ShmupHaptics:
    """
    Haptic feedback tuned for vertical shmup pacing.
    More subtle than horizontal arcade shooters.
    """
    
    def __init__(self, controller):
        self.controller = controller
        self.danger_zone_rumble = 0.0
    
    def update(self, player, enemies, heat):
        # Proximity warning (enemies too close)
        closest_enemy = self.get_closest_enemy(player, enemies)
        if closest_enemy and closest_enemy.dist < 80:
            # Gentle pulse = danger nearby
            intensity = 0.3 * (1.0 - closest_enemy.dist / 80)
            self.controller._rumble(intensity, 100)
        
        # Heat pulse (climbing toward Berserk)
        if 70 <= heat < 100:
            # Heartbeat rumble as Heat approaches max
            pulse = 0.2 + (heat - 70) / 30 * 0.3  # 0.2 → 0.5
            self.controller._rumble(pulse, 150)
        
        # Berserk activation (BIG pulse)
        if heat >= 100:
            self.controller._rumble(0.8, 300)
            play_sound("berserk_activate")
    
    def point_blank_kill(self):
        """Sharp pulse on max multiplier kill"""
        self.controller._rumble(0.5, 80)
    
    def boss_warning(self):
        """Boss incoming = heavy rumble"""
        self.controller._rumble(0.7, 500)
```

**Key Difference**: Vertical shmups use **sustained low rumble** for tension, not constant spikes.

---

## 📐 NARROW SHOT MODE (Speed Reduction)

### Devil Blade Narrow Shot
```
Wide Shot:
- Spread pattern
- Full movement speed
- General use

Narrow Shot:
- Focused beam
- 50% movement speed
- Precise dodging
```

### EVE Rebellion Implementation
```python
class ShipMovement:
    """
    Movement speed tied to formation/shot type.
    Hold Y/Triangle to switch.
    """
    
    def __init__(self):
        self.formation = "spread"  # "spread" or "focused"
        self.base_speed = 250
    
    def apply_movement(self, controller, dt):
        move_x, move_y = controller.get_movement()
        
        # Speed modifier based on formation
        speed_mult = 0.6 if self.formation == "focused" else 1.0
        
        # Apply
        self.x += move_x * self.base_speed * speed_mult * dt
        self.y += move_y * self.base_speed * speed_mult * dt
        
        # Visual feedback
        if self.formation == "focused":
            self.render_focus_aura()
```

**When to Use Narrow/Focused**:
- Boss bullet patterns (precise dodging)
- Navigating tight gaps
- Maximizing damage on single target

**When to Use Wide/Spread**:
- Clearing crowds
- Fast repositioning
- General movement

---

## 🎮 FINAL CONTROLLER LAYOUT

```
LEFT STICK: Ship Movement (analog, slower for vertical shmup)
RIGHT STICK: (unused - no aim offset in vertical shmups)

RT / R2: Primary Fire (held = continuous)
LT / L2: Boost Mode (hold = 5x Heat gain, drains Heat)

RB / R1: Cycle Ammo Next
LB / L1: Cycle Ammo Prev

Y / Triangle: Formation Switch (Spread ↔ Focused)
X / Square: Deploy Fleet
B / Circle: Emergency Burn (panic button)
A / Cross: Context Action (rescue refugees)

START: Pause
BACK: Quick Stats
```

---

## 🚫 WHAT TO REMOVE FROM PREVIOUS DESIGN

### Removed (Not Shmup-Standard)
1. **Right stick aim offset** - Vertical shmups have fixed scrolling
2. **Twitchy movement** - Too fast for bullet hell dodging
3. **Heavy momentum curve** - Vertical shmups need precision, not weight
4. **Constant rumble** - Shmups use subtle haptics for tension

### Added (Shmup-Specific)
1. **Formation toggle** - Spread vs Focused (speed trade-off)
2. **Boost system** - High-risk Heat multiplier
3. **Proximity scoring** - Point-blank encouraged
4. **Sustained tension rumble** - Low-intensity danger pulse

---

## 📊 COMPARISON: DEVIL BLADE vs EVE REBELLION

| Devil Blade Reboot | EVE Rebellion Equivalent |
|--------------------|-------------------------|
| Berserk gauge | Heat system |
| Point-blank kills | Close-range kills |
| Boost (hold Bomb) | Boost (hold LT/L2) |
| Wide/Narrow shot | Spread/Focused formation |
| Auto-bomb (Easy) | Emergency Burn (B button) |
| Blue crystals | Refugees |
| Bomb capsules | Fleet power-ups |
| Boss rush mode | Boss gauntlet unlock |

---

## ✅ DESIGN PRINCIPLES (Corrected)

### Vertical Shmup Rules
1. **Slower, Deliberate Movement** - NOT twitchy arcade
2. **Proximity = Risk = Reward** - Point-blank scoring
3. **Tension Through Pacing** - Calm → chaos → calm
4. **Strategic Resource Use** - Boost at right moment
5. **Formation Switching** - Speed vs power trade-off

### Controller Feel
- **Gentle stick input** = precise micro-dodges
- **Trigger hold** = continuous fire (no button mashing)
- **Face buttons** = tactical decisions (not panic spam)
- **Haptics** = tension building (not constant noise)

---

## 🎯 NEXT STEPS

1. **Adjust movement speed** - Reduce from 250px/s to ~150px/s base
2. **Implement formation toggle** - Y/Triangle = Spread ↔ Focused
3. **Add Boost system** - LT/L2 = 5x Heat gain with drain
4. **Tune proximity scoring** - 50px brackets like Devil Blade
5. **Refine haptics** - Sustained low rumble vs sharp spikes
6. **Test narrow shot** - 50% speed reduction feels right?

---

**Key Insight**: Devil Blade Reboot is a **methodical, tactical shmup**, not a twitch arcade shooter. Controller design must reflect slower pacing, strategic resource use, and proximity-based risk/reward.
