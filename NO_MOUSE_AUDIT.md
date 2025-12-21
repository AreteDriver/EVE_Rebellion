# NO-MOUSE DESIGN AUDIT
## EVE Rebellion - Controller-First Architecture

**Goal**: Remove ALL mouse dependencies from gameplay loop  
**Philosophy**: If you need a mouse, your controller design failed

---

## 🎯 CURRENT MOUSE DEPENDENCIES

### CRITICAL - Must Remove Before v2.1

| System | Mouse Usage | Controller Replacement | Priority |
|--------|------------|------------------------|----------|
| **Ship Selection** | Click ships in hangar | D-Pad navigation + A to select | P0 |
| **Ammo Selection** | Click ammo types in HUD | LB/RB cycle (already implemented) | P0 |
| **Menu Navigation** | Click buttons | D-Pad + face buttons | P0 |
| **Pause Menu** | Click resume/quit | D-Pad + A/B | P0 |
| **Skill Tree** | Click nodes to unlock | D-Pad navigation + A to purchase | P1 |
| **Fleet Management** | Click to assign ships | Auto-assign or quick-select via bumpers | P1 |

### MEDIUM - Remove Before v3.0

| System | Mouse Usage | Controller Replacement | Priority |
|--------|------------|------------------------|----------|
| **Targeting** | Click enemy to focus | Auto-target nearest threat OR right stick aim | P2 |
| **Pickup Selection** | Click refugees/loot | Auto-pickup or context-sensitive A button | P2 |
| **Formation Switch** | Click formation icon | Y button (already mapped) | P2 |
| **Stats Screen** | Scroll with wheel | Right stick scroll OR shoulder buttons | P3 |

### LOW - Quality of Life

| System | Mouse Usage | Controller Replacement | Priority |
|--------|------------|------------------------|----------|
| **Tutorial Tooltips** | Click "Next" | Auto-advance or A button | P4 |
| **Credits Screen** | Click to skip | Any button to skip | P4 |

---

## 🔧 IMPLEMENTATION PLAN

### Phase 1: Core Gameplay (v2.1)
**Goal**: Controller-only from launch to death

#### Ship Selection Screen
```python
class ShipHangar:
    def __init__(self):
        self.ships = [rifter, wolf, jaguar]
        self.selected_index = 0
        self.confirmed = False
    
    def handle_controller(self, controller):
        # D-Pad navigation
        if controller.is_action_just_pressed(GameAction.DPAD_LEFT):
            self.selected_index = (self.selected_index - 1) % len(self.ships)
            play_sound("ui_navigate")
        
        if controller.is_action_just_pressed(GameAction.DPAD_RIGHT):
            self.selected_index = (self.selected_index + 1) % len(self.ships)
            play_sound("ui_navigate")
        
        # Confirm selection
        if controller.is_action_just_pressed(GameAction.CONTEXT_ACTION):
            self.confirmed = True
            play_sound("ui_confirm")
            return self.ships[self.selected_index]
        
        # Visual feedback
        self._highlight_ship(self.selected_index)
```

**UI Changes**:
- Add D-Pad icons to ship cards
- Pulsing border on selected ship
- "Press A to Launch" prompt
- No clickable regions

---

#### Menu Navigation
```python
class PauseMenu:
    def __init__(self):
        self.options = ["Resume", "Restart", "Settings", "Quit"]
        self.selected_index = 0
    
    def handle_controller(self, controller):
        # Vertical D-Pad navigation
        if controller.is_action_just_pressed(GameAction.DPAD_UP):
            self.selected_index = max(0, self.selected_index - 1)
            play_sound("ui_tick")
        
        if controller.is_action_just_pressed(GameAction.DPAD_DOWN):
            self.selected_index = min(len(self.options) - 1, 
                                      self.selected_index + 1)
            play_sound("ui_tick")
        
        # Confirm
        if controller.is_action_just_pressed(GameAction.CONTEXT_ACTION):
            return self._execute_option(self.selected_index)
        
        # Cancel (back to game)
        if controller.is_action_just_pressed(GameAction.EMERGENCY_BURN):
            return "resume"
```

**UI Changes**:
- Highlight current selection
- Show controller hints: "D-Pad: Navigate | A: Select | B: Back"
- Remove hover states (mouse-only)

---

### Phase 2: Meta Progression (v2.2)

#### Skill Tree Navigation
```python
class SkillTree:
    def __init__(self):
        self.nodes = self._build_node_graph()
        self.cursor_node = self.nodes[0]  # Start at root
    
    def handle_controller(self, controller):
        # Navigate to connected nodes
        if controller.is_action_just_pressed(GameAction.DPAD_UP):
            if self.cursor_node.parent:
                self.cursor_node = self.cursor_node.parent
        
        if controller.is_action_just_pressed(GameAction.DPAD_DOWN):
            if self.cursor_node.children:
                self.cursor_node = self.cursor_node.children[0]
        
        if controller.is_action_just_pressed(GameAction.DPAD_LEFT):
            sibling = self._get_left_sibling(self.cursor_node)
            if sibling:
                self.cursor_node = sibling
        
        if controller.is_action_just_pressed(GameAction.DPAD_RIGHT):
            sibling = self._get_right_sibling(self.cursor_node)
            if sibling:
                self.cursor_node = sibling
        
        # Purchase skill
        if controller.is_action_just_pressed(GameAction.CONTEXT_ACTION):
            if self.cursor_node.can_afford():
                self.cursor_node.unlock()
                controller._rumble(0.5, 100)  # Haptic confirmation
        
        # Show tooltip
        if controller.is_action_pressed(GameAction.QUICK_STATS):
            self._show_node_details(self.cursor_node)
```

**UI Changes**:
- Thicker connection lines between nodes
- Pulsing cursor on current node
- Lockout visual for unaffordable nodes
- "Hold Back for Details" prompt

---

#### Fleet Management (Simplified)
```python
class FleetManager:
    """
    No clicking individual ships.
    Auto-assign based on composition rules.
    """
    
    def auto_compose_fleet(self, saved_refugees: int) -> List[Ship]:
        # Spend refugees on optimal fleet
        fleet = []
        budget = saved_refugees
        
        # Priority: 1 Tank, 2 DPS, Fill with Support
        if budget >= 100:
            fleet.append(Ship("Rupture", cost=100))  # Tank
            budget -= 100
        
        while budget >= 50:
            fleet.append(Ship("Thrasher", cost=50))  # DPS
            budget -= 50
            if len([s for s in fleet if s.role == "DPS"]) >= 2:
                break
        
        while budget >= 20:
            fleet.append(Ship("Burst", cost=20))  # Support
            budget -= 20
        
        return fleet
    
    def handle_controller(self, controller):
        # Quick presets
        if controller.is_action_just_pressed(GameAction.DPAD_LEFT):
            self.preset = "AGGRESSIVE"  # More DPS
        
        if controller.is_action_just_pressed(GameAction.DPAD_RIGHT):
            self.preset = "DEFENSIVE"  # More tanks
        
        if controller.is_action_just_pressed(GameAction.CONTEXT_ACTION):
            self.fleet = self.auto_compose_fleet(self.refugee_count)
            return self.fleet
```

**Design Change**:
- Remove manual ship placement
- 3 presets: Aggressive, Balanced, Defensive
- Auto-optimize spending
- D-Pad to switch preset, A to confirm

---

### Phase 3: Advanced Features (v3.0)

#### Right-Stick Targeting
```python
class TargetingSystem:
    """
    Replace mouse-click targeting with right stick aim.
    """
    
    def __init__(self):
        self.current_target = None
        self.enemies = []
        self.lock_range = 150  # pixels
    
    def update(self, controller, player_pos):
        aim_x, aim_y = controller.get_aim_offset()
        
        if abs(aim_x) > 5 or abs(aim_y) > 5:
            # Aim stick active - find target in cone
            angle = math.atan2(aim_y, aim_x)
            
            best_target = None
            best_score = -1
            
            for enemy in self.enemies:
                # Calculate angle to enemy
                dx = enemy.x - player_pos[0]
                dy = enemy.y - player_pos[1]
                dist = math.sqrt(dx*dx + dy*dy)
                enemy_angle = math.atan2(dy, dx)
                
                # Cone detection (30° tolerance)
                angle_diff = abs(enemy_angle - angle)
                if angle_diff < 0.52:  # ~30 degrees in radians
                    # Score by proximity to aim vector
                    score = 1.0 / (dist + 1)
                    if score > best_score:
                        best_score = score
                        best_target = enemy
            
            if best_target:
                self.current_target = best_target
                controller._rumble(0.4, 50)  # Lock-on pulse
        
        else:
            # No aim input - auto-target nearest
            self.current_target = self._get_nearest_enemy(player_pos)
```

**No Mouse Required**:
- Right stick points toward target zone
- Haptic pulse confirms lock
- Auto-fallback to nearest enemy

---

## 🚫 BANNED INTERACTIONS

### Never Allow These (Even in Menus)

1. **Click-to-Proceed**  
   ❌ Click "Next" button  
   ✅ Press A / Any button to continue

2. **Hover States**  
   ❌ Tooltip on mouse hover  
   ✅ Hold Back button to show details

3. **Drag-and-Drop**  
   ❌ Drag ship into fleet slot  
   ✅ Auto-assign or D-Pad select + A confirm

4. **Scrolling with Wheel**  
   ❌ Mouse wheel to scroll stats  
   ✅ Right stick or shoulder buttons

5. **Precision Clicking**  
   ❌ Click small skill tree nodes  
   ✅ D-Pad navigation between nodes

6. **Free-Aim Cursor**  
   ❌ Move cursor to UI element  
   ✅ Tab/cycle through elements with bumpers

---

## 🎮 DESIGN PRINCIPLES

### Rule 1: Thumbs Never Leave Sticks
- All frequent actions on triggers/bumpers/face buttons
- D-Pad for slow/menu contexts only
- Never force thumb to D-Pad during combat

### Rule 2: No Hidden Features
- Every action has visible controller hint
- Icons show actual button (Xbox/PlayStation auto-detect)
- Tutorial teaches controller layout, not mouse

### Rule 3: Fallback to Auto
- If player doesn't target: Auto-target nearest
- If player doesn't select ammo: Use best available
- If player doesn't confirm: Timeout to safe default

### Rule 4: Haptic Feedback = Confirmation
- Lock-on → Pulse
- Purchase → Rumble
- Error → Double-tap rumble
- No visual confirmations needed

---

## 📊 TESTING CHECKLIST

### Can You Complete These Without Touching Mouse?

- [ ] Launch game from desktop
- [ ] Navigate main menu
- [ ] Select ship
- [ ] Play entire mission
- [ ] Cycle ammo types
- [ ] Deploy fleet
- [ ] Pause and resume
- [ ] View stats
- [ ] Purchase skill upgrade
- [ ] Change formation
- [ ] Restart mission
- [ ] Quit to desktop

**If ANY require mouse: FAIL**

---

## 🔄 MIGRATION PATH

### Hybrid Phase (v2.1 - v2.2)
- Support BOTH mouse and controller
- Show input method on first use
- Lock to one input type per session
- Warning if switching mid-game

### Controller-Only Phase (v3.0+)
- Remove all mouse click detection
- Hide mouse cursor in-game
- Show cursor only in terminal/settings
- Console-style UX fully

---

## 🎯 SUCCESS CRITERIA

**v2.1 Launch Requirements**:
1. Complete mission start-to-death with controller only
2. Zero mouse clicks in gameplay loop
3. All menus navigable with D-Pad
4. Haptic feedback on all confirmations

**v3.0 Goals**:
1. Remove mouse.get_pos() from codebase
2. Cursor hidden except in options
3. PlayStation/Xbox UI auto-detection
4. Steam Deck verified

---

## 💡 ACCESSIBILITY NOTES

**Don't Remove (Even if Mouse-Free)**:
- Keyboard shortcuts for menu navigation
- Rebindable sensitivity/deadzones
- Colorblind mode for UI elements
- Adjustable text size

**These Are NOT Mouse Dependencies**:
- They're alternative input methods
- Keep for desktop players without controllers
- Keyboard ≠ Mouse (directional vs pointer)

---

## 📝 CODE AUDIT TARGETS

### Files to Search for Mouse Dependencies

```bash
# Find all mouse events
grep -r "pygame.mouse.get_pos()" *.py
grep -r "MOUSEBUTTONDOWN" *.py
grep -r "MOUSEMOTION" *.py
grep -r "mouse.get_pressed()" *.py

# Find click handlers
grep -r "def.*click" *.py
grep -r "if.*collidepoint" *.py
```

### Expected Results After Cleanup

```
game.py:           0 mouse references (controller only)
sprites.py:        0 mouse references (analog movement)
menu.py:           0 mouse references (D-Pad navigation)
hangar.py:         0 mouse references (button selection)
settings.py:       MAY keep mouse for cursor-based options
```

---

## 🎮 CONTROLLER HINT SYSTEM

### Dynamic On-Screen Prompts

```python
class ControllerHints:
    """
    Shows context-sensitive button prompts.
    Auto-detects Xbox vs PlayStation.
    """
    
    def __init__(self, controller_type="xbox"):
        self.type = controller_type
        self.prompts = {
            "confirm": "A" if controller_type == "xbox" else "×",
            "cancel": "B" if controller_type == "xbox" else "○",
            "menu": "Start" if controller_type == "xbox" else "Options",
        }
    
    def show_prompt(self, action: str, text: str):
        """
        Render: [A] Launch Ship
        """
        button_icon = self.prompts.get(action, "?")
        return f"[{button_icon}] {text}"
```

**Always Visible**:
- Bottom of screen: Available actions
- Context-sensitive (changes per screen)
- Fades after 3 seconds of inactivity
- Reappears on button press

---

## 🚀 IMPLEMENTATION PRIORITY

### Week 1: Core Gameplay
- Remove mouse from combat loop
- Controller movement (already done)
- Ammo cycling (already done)
- Pause menu D-Pad navigation

### Week 2: Menus
- Ship selection D-Pad
- Settings navigation
- Remove all click handlers

### Week 3: Meta Systems
- Skill tree D-Pad
- Fleet auto-assign
- Stats screen scrolling

### Week 4: Polish
- Haptic feedback tuning
- Controller hints
- PlayStation button detection
- Steam Deck testing

---

**COMMIT TO THIS**:  
If you can't play it on a console, it's not finished.
