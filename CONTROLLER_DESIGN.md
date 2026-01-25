# Controller-First Input Design
## EVE Rebellion - Devil Blade Style Vertical Scroller

---

## Controller Layout

### Primary Layout (Xbox/PlayStation)

| Control | Xbox | PlayStation | Function |
|---------|------|-------------|----------|
| **Left Stick** | Left Analog | Left Analog | Ship movement (analog 360°, momentum-aware) |
| **Right Stick** | Right Analog | Right Analog | Precision aim offset (subtle turret control) |
| **Primary Fire** | RT | R2 | Main weapons (pressure-sensitive*) |
| **Alternate Fire** | LT | L2 | Rockets/missiles |
| **Cycle Ammo →** | RB | R1 | Next ammo type |
| **Cycle Ammo ←** | LB | L1 | Previous ammo type |
| **Context Action** | A | Cross | Collect refugees / Activate |
| **Emergency Burn** | B | Circle | Speed boost (limited uses) |
| **Deploy Fleet** | X | Square | Activate fleet ships |
| **Formation Switch** | Y | Triangle | Change formation (Jaguar only) |
| **Pause** | Start | Options | Pause game |
| **Quick Stats** | Back/Select | Share | Show extended HUD |

*Pressure-sensitive fire rate planned for future update

---

## Why Controller > Keyboard for Vertical Scrollers

### 1. **Analog Movement Creates Natural Evasion**
- **Keyboard**: Limited to 8 directions (WASD combinations)
- **Controller**: Full 360° analog movement with variable speed
- **Impact**: Player can execute precise 23° dodges, create spiral patterns, and vary speed mid-maneuver

**Example That Only Works With Analog:**
```
When facing a boss's circular bullet pattern, the player can:
1. Push stick 40% to slowly drift right (fine positioning)
2. Snap stick to 80° for diagonal escape
3. Ease back to 10% for micro-adjustments between bullets

Keyboard cannot achieve this granularity.
```

### 2. **Trigger Pressure = Fire Intensity**
- **Current**: Binary on/off
- **Future**: Trigger pressure scales fire rate (0.0 to 1.0)
- **Design**: Light trigger tap = conserve ammo, full press = maximum DPS
- **Tension**: Player must decide between control and damage output

### 3. **Haptic Feedback Communicates Danger Without UI**
- **Heat rises**: Rumble intensifies (no need to check HUD)
- **Enemy lock-on**: Sharp spike warns of incoming fire
- **Irreversible decision**: Strong pulse confirms commitment
- **Ship destruction**: Final rumble → input lock → forces player to feel the loss

### 4. **Muscle Memory for High-Pressure Decisions**
- Face buttons are distinct shapes (Xbox: ABXY, PS: ○△□×)
- No visual confirmation needed during intense combat
- Bumpers accessible without removing thumbs from sticks
- **Design Rule**: Critical actions never require menu navigation

---

## Controller-Driven Design Requirements

### Movement Feel: Weighty, Not Twitchy

**Implementation:**
- Momentum curve: `output = input^1.8`
- Prevents instant direction changes (feels like piloting a ship with mass)
- Fine control at low stick pressure
- Full speed at edges

```python
def _momentum_curve(input_value: float) -> float:
    """Exponential curve for weighted movement"""
    sign = 1.0 if input_value > 0 else -1.0
    magnitude = abs(input_value)
    curved = pow(magnitude, 1.8)
    return sign * curved
```

**Result**: Evasion feels intentional, not twitchy.

### Input Buffering: Allowed, But Mistakes Are Final

- **Button buffers**: 100ms window (press B → emergency burn executes even if enemy dies)
- **No undo**: Once fleet is deployed, it's committed
- **No input replays**: Death = death, no "press A to retry immediately"

### Precision From Pressure, Not Tiny Hitboxes

- **Hitboxes**: Generous (30-40 pixel ship with 25 pixel hitbox)
- **Challenge**: Comes from bullet density, Heat system, and decision timing
- **Not**: Pixel-perfect dodging of microscopic bullets

---

## Haptic Feedback Design

### Rising Tension (Heat System)

| Heat Level | Rumble Intensity | Feel |
|------------|------------------|------|
| 0% (Safe) | 0.0 | No vibration |
| 25% (Warm) | 0.3 | Gentle pulse |
| 50% (Hot) | 0.5 | Steady rumble |
| 75% (Danger) | 0.7 | Strong vibration |
| 100% (Critical) | 0.8 | Maximum sustained |

### Sharp Spikes (Events)

| Event | Intensity | Duration | Purpose |
|-------|-----------|----------|---------|
| Enemy Lock-On | 0.6 | 200ms | "You're targeted" |
| Missile Acquisition | 0.6 | 200ms | "Incoming" |
| Irreversible Decision | 0.9 | 200ms | "No going back" |
| Ship Destruction | 1.0 | 500ms | "You lost" |

### Silence + Vibration Moments

**Design**: When entering a boss fight:
1. All UI fades briefly
2. Controller vibrates in sync with boss arrival
3. Player feels the encounter before seeing it
4. Creates physical tension

---

## Death Sequence (Critical Design)

```python
def trigger_death_sequence():
    """
    On ship destruction:
    1. Lock inputs immediately (0.0 second response time)
    2. Trigger maximum haptic pulse (1.0 intensity, 500ms)
    3. Keep inputs locked for 1.0 second
    4. Force player to watch explosion, feel the loss
    5. Then offer restart
    
    WHY: Instant restart devalues death. Player must FEEL consequences.
    """
```

**No Restart During Lock:**
- Prevents panic button mashing
- Forces acknowledgment of failure
- Makes next attempt more deliberate

---

## Accessibility Options

### Allowed Customizations:
- Left/right stick deadzone (0.05 to 0.30)
- Movement sensitivity (0.5 to 2.0)
- Aim sensitivity (0.3 to 1.5)
- Haptic intensity (0.0 to 1.0, or disable)
- Trigger deadzone (for worn controllers)

### NOT Allowed:
- Auto-fire
- Auto-dodge
- Aim assist
- Input macros

**Philosophy**: Accessibility means making controls comfortable, not playing for the player.

---

## Integration with EVE Rebellion

### game.py Modifications

```python
from controller_input import ControllerInput, XboxButton

class Game:
    def __init__(self):
        # ... existing init ...
        self.controller = ControllerInput()
    
    def update(self):
        # Update controller state
        self.controller.update(dt)
        
        # Set heat level for haptic feedback
        heat = self.calculate_heat_level()  # Your heat system
        self.controller.set_heat_level(heat)
        
        # Get analog movement
        if self.controller.connected:
            move_x, move_y = self.controller.get_movement_vector()
            self.player.rect.x += move_x * self.player.speed
            self.player.rect.y += move_y * self.player.speed
        else:
            # Fall back to keyboard
            keys = pygame.key.get_pressed()
            # ... existing keyboard code ...
        
        # Primary fire
        if self.controller.is_firing() or keys[pygame.K_SPACE]:
            bullets = self.player.shoot()
            # ...
        
        # Cycle ammo with bumpers
        if self.controller.is_button_just_pressed(XboxButton.RB):
            self.player.cycle_ammo()
            self.play_sound('ammo_switch')
        
        # Emergency burn (B button)
        if self.controller.is_button_just_pressed(XboxButton.B):
            self.player.activate_emergency_burn()
            self.controller.trigger_decision_haptic()  # Haptic confirmation
    
    def handle_player_death(self):
        # Trigger death sequence with input lock + haptics
        self.controller.trigger_death_sequence()
        # ... rest of death logic ...
```

### sprites.py - Player Class

```python
def apply_controller_movement(self, controller, dt):
    """Apply analog movement with momentum"""
    if not controller.connected:
        return
    
    move_x, move_y = controller.get_movement_vector()
    
    # Apply movement
    self.rect.x += move_x * self.speed * dt
    self.rect.y += move_y * self.speed * dt
    
    # Optional: Precision aim offset
    aim_x, aim_y = controller.get_aim_offset()
    self.turret_offset_x = aim_x
    self.turret_offset_y = aim_y
```

---

## Performance Notes

- Controller polling: 60Hz (matches game loop)
- Haptic updates: 100ms intervals (smooth enough, not CPU intensive)
- Input latency: <16ms (1 frame at 60 FPS)
- Memory overhead: <1KB for controller state

---

## Testing Checklist

- [ ] Controller auto-detected on game start
- [ ] Analog movement feels weighted, not twitchy
- [ ] Dead zones eliminate stick drift
- [ ] Triggers respond with <1 frame latency
- [ ] Haptics scale smoothly with Heat
- [ ] Death sequence locks inputs for 1.0s
- [ ] All actions reachable without removing thumbs from sticks
- [ ] Keyboard still works when controller disconnected
- [ ] Hot-plug: Controller can be connected mid-game

---

## Future Enhancements

### Trigger Pressure → Fire Rate
```python
fire_pressure = controller.get_fire_pressure()
if fire_pressure > 0.8:
    fire_rate_mult = 1.5  # Rapid fire
elif fire_pressure > 0.5:
    fire_rate_mult = 1.0  # Normal
else:
    fire_rate_mult = 0.7  # Conserve ammo
```

### Adaptive Difficulty
- Track player's stick precision
- If player uses only digital inputs (full stick), increase enemy speed
- If player uses analog finesse, introduce complex patterns

### DualSense Features (PS5)
- Adaptive triggers: Resistance increases when overheating
- LED color: Matches ship's Heat level
- Speaker: Warning alerts when surveillance locks on

---

## Philosophy Summary

**"Controller-first forces better pacing, clearer risk decisions, and physical tension aligned with Heat mechanics."**

- Movement: Analog > Digital
- Feedback: Haptics > Visual UI
- Mistakes: Final > Undoable
- Death: Felt > Observed

Devil Blade works because it respects hands, not UI.
EVE Rebellion follows the same principle.

---

## Next Steps

Choose one:
1. **Fixed Xbox/PlayStation layout** (hard-lock this exact mapping)
2. **Godot/Unity input maps** (export bindings for other engines)
3. **"No-mouse" design audit** (remove mouse-dependent features)

Which do you want?
