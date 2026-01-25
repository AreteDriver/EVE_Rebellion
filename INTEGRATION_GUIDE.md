# Integration Guide: Cinematic & Devil Blade Combat Systems

## Overview
This guide explains how to integrate the new cinematic and combat systems into your existing Minmatar Rebellion codebase.

---

## File Structure

```
minmatar_rebellion/
├── cinematic_system.py          # NEW: Cinematic manager
├── devil_blade_combat.py        # NEW: Combat scoring & AI
├── game_main.py                 # MODIFIED: Add new flow
├── player.py                    # MODIFIED: Add tribal bonuses
├── enemy.py                     # MODIFIED: Use new AI system
├── ui.py                        # MODIFIED: Add score displays
├── data/
│   ├── profiles/                # NEW: Player profiles
│   │   └── {callsign}.json
│   ├── tribes/                  # NEW: Tribal data
│   │   └── tribe_data.json
│   └── waves/                   # NEW: Wave definitions
│       └── missions.json
└── assets/
    └── cinematics/              # NEW: Cinematic assets
        ├── titan_base.png
        ├── explosion_frames/
        └── tribal_portraits/
```

---

## Step 1: Integrate Cinematic System

### 1.1 Modify game_main.py

```python
from cinematic_system import CinematicManager, TribeType, CinematicType
from devil_blade_combat import ComboSystem, ScoringSystem, WaveSpawner

class GameState(Enum):
    OPENING_CINEMATIC = "opening"
    TRIBAL_SELECTION = "tribal_selection"
    PROFILE_CREATION = "profile_creation"
    FIRST_SHIP_ACQUISITION = "first_ship"
    MAIN_MENU = "main_menu"
    IN_GAME = "in_game"
    UPGRADE_CINEMATIC = "upgrade"
    MISSION_DEBRIEF = "debrief"

class MinmatarRebellion:
    def __init__(self):
        # ... existing init ...
        
        # NEW: Add cinematic and combat systems
        self.cinematic_mgr = CinematicManager(self.width, self.height)
        self.combo_system = ComboSystem()
        self.scoring_system = ScoringSystem(self.combo_system)
        self.wave_spawner = WaveSpawner(self.width, self.height)
        
        # NEW: Game state management
        self.game_state = GameState.OPENING_CINEMATIC
        self.player_profile = None
        self.selected_tribe = TribeType.SEBIESTOR
        
        # Start with opening cinematic
        self.cinematic_mgr.start_opening_cinematic()
        
    def run(self):
        while self.running:
            delta_time = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_event(event)
                
            # Update based on state
            self.update(delta_time)
            
            # Render based on state
            self.render()
            
            pygame.display.flip()
            
    def handle_event(self, event):
        """Route events based on game state"""
        if self.game_state == GameState.OPENING_CINEMATIC:
            self.cinematic_mgr.handle_input(event)
            
        elif self.game_state == GameState.TRIBAL_SELECTION:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self._cycle_tribe(-1)
                elif event.key == pygame.K_DOWN:
                    self._cycle_tribe(1)
                elif event.key == pygame.K_RETURN:
                    self._confirm_tribe_selection()
                    
        elif self.game_state == GameState.IN_GAME:
            # Existing game input handling
            pass
            
    def update(self, delta_time):
        """Update based on game state"""
        if self.game_state == GameState.OPENING_CINEMATIC:
            # Cinematic updates handled in render
            pass
        
        elif self.game_state == GameState.FIRST_SHIP_ACQUISITION:
            # Cinematic updates handled in render
            pass
            
        elif self.game_state == GameState.IN_GAME:
            # Update combo timer
            self.combo_system.update(delta_time)
            self.scoring_system.update(delta_time)
            
            # Existing game updates
            self.update_game_logic(delta_time)
            
    def render(self):
        """Render based on game state"""
        if self.game_state == GameState.OPENING_CINEMATIC:
            complete = self.cinematic_mgr.render_opening_cinematic(
                self.screen, 
                self.clock.get_time() / 1000.0
            )
            if complete:
                self.game_state = GameState.TRIBAL_SELECTION
                
        elif self.game_state == GameState.TRIBAL_SELECTION:
            self.cinematic_mgr.render_tribal_selection(
                self.screen, 
                self.selected_tribe
            )
        
        elif self.game_state == GameState.FIRST_SHIP_ACQUISITION:
            complete = self.cinematic_mgr.render_first_ship_cinematic(
                self.screen,
                self.clock.get_time() / 1000.0,
                self.player_profile["tribe"]
            )
            if complete:
                self.game_state = GameState.MAIN_MENU
            
        elif self.game_state == GameState.IN_GAME:
            self.render_game()
            # Add score overlays
            self.render_combat_ui()
            
    def render_combat_ui(self):
        """Render Devil Blade style UI elements"""
        # Combo counter (top right)
        if self.combo_system.multiplier > 1.0:
            font_combo = pygame.font.Font(None, 48)
            combo_text = f"{self.combo_system.multiplier:.1f}x COMBO"
            combo_surface = font_combo.render(combo_text, True, (255, 255, 100))
            self.screen.blit(combo_surface, (self.width - 250, 50))
            
            # Combo status text
            status_text = self.combo_system.get_combo_text()
            if status_text:
                status_surface = font_combo.render(status_text, True, (255, 200, 100))
                rect = status_surface.get_rect(center=(self.width // 2, 150))
                self.screen.blit(status_surface, rect)
                
        # Score (top left)
        font_score = pygame.font.Font(None, 36)
        score_text = f"SCORE: {self.scoring_system.total_score:,}"
        score_surface = font_score.render(score_text, True, (255, 255, 255))
        self.screen.blit(score_surface, (20, 20))
        
        # Render floating score events
        self.scoring_system.render_score_events(self.screen)
        
    def _cycle_tribe(self, direction):
        """Cycle through tribe selection"""
        tribes = list(TribeType)
        idx = tribes.index(self.selected_tribe)
        self.selected_tribe = tribes[(idx + direction) % len(tribes)]
        
    def _confirm_tribe_selection(self):
        """Create player profile with selected tribe"""
        callsign = self._prompt_callsign()  # Implementation needed
        self.player_profile = {
            "callsign": callsign,
            "tribe": self.selected_tribe,
            "ship_tier": 0,
            "total_score": 0,
            "missions_completed": 0,
            "total_refugees": 0,
            "skill_points": 0,
            "cinematics_seen": ["opening"]
        }
        self._save_profile()
        # Show first ship acquisition scene
        self.cinematic_mgr.cinematic_timer = 0
        self.cinematic_mgr.skip_requested = False
        self.game_state = GameState.FIRST_SHIP_ACQUISITION
```

### 1.2 Add Player Tribal Bonuses

```python
# In player.py

class Player:
    def __init__(self, x, y, tribe: TribeType = None):
        # ... existing init ...
        
        self.tribe = tribe
        self.apply_tribal_bonus()
        
    def apply_tribal_bonus(self):
        """Apply tribal stat bonuses"""
        if not self.tribe:
            return
            
        bonuses = {
            TribeType.SEBIESTOR: {"repair_rate": 1.05},
            TribeType.BRUTOR: {"weapon_damage": 1.05},
            TribeType.VHEROKIOR: {"speed": 1.05, "evasion": 1.05},
            TribeType.KRUSUAL: {"refugee_bonus": 1.10}
        }
        
        tribe_bonus = bonuses.get(self.tribe, {})
        
        if "repair_rate" in tribe_bonus:
            self.repair_effectiveness *= tribe_bonus["repair_rate"]
        if "weapon_damage" in tribe_bonus:
            self.weapon_damage *= tribe_bonus["weapon_damage"]
        if "speed" in tribe_bonus:
            self.max_speed *= tribe_bonus["speed"]
        if "refugee_bonus" in tribe_bonus:
            self.refugee_score_multiplier = tribe_bonus["refugee_bonus"]
```

---

## Step 2: Integrate Devil Blade Combat

### 2.1 Update Enemy System

```python
# In enemy.py

from devil_blade_combat import EnemyAI, EnemyBehavior

class Enemy:
    def __init__(self, x, y, behavior: EnemyBehavior, movement_params: Dict):
        # ... existing init ...
        
        self.ai = EnemyAI(behavior, (x, y), movement_params)
        self.behavior = behavior
        
    def update(self, delta_time, player_pos, screen_bounds):
        """Use AI system for movement and behavior"""
        shot_data = self.ai.update(delta_time, player_pos, screen_bounds)
        
        # Update sprite position from AI
        self.x, self.y = self.ai.position
        
        # If AI wants to fire, create projectile
        if shot_data:
            return self.create_projectile(shot_data)
            
        return None
        
    def take_damage(self, damage):
        """Apply damage and check for death"""
        was_killed = self.ai.take_damage(damage)
        if was_killed:
            self.alive = False
        return was_killed
```

### 2.2 Add Wave-Based Spawning

```python
# In game_main.py (continued)

class MinmatarRebellion:
    def spawn_wave(self, mission_number: int):
        """Spawn enemies based on mission and wave patterns"""
        # Determine patterns based on mission
        patterns = self._get_mission_patterns(mission_number)
        difficulty = 1.0 + (mission_number * 0.1)
        
        for pattern in patterns:
            wave_data = self.wave_spawner.spawn_wave(pattern, difficulty)
            
            for enemy_data in wave_data:
                # Schedule enemy spawn
                self.spawn_queue.append({
                    "spawn_time": self.mission_time + enemy_data["spawn_time"],
                    "type": enemy_data["type"],
                    "position": enemy_data["position"],
                    "params": enemy_data["movement_params"]
                })
                
    def _get_mission_patterns(self, mission_num: int):
        """Get wave patterns for mission"""
        from devil_blade_combat import EnemyPattern
        
        # Early missions: Simple patterns
        if mission_num <= 3:
            return [EnemyPattern.LINEAR_RUSH, EnemyPattern.SINE_WAVE]
            
        # Mid missions: Mixed patterns
        elif mission_num <= 6:
            return [
                EnemyPattern.LINEAR_RUSH,
                EnemyPattern.SINE_WAVE,
                EnemyPattern.AMBUSH
            ]
            
        # Late missions: Complex patterns
        else:
            return [
                EnemyPattern.SINE_WAVE,
                EnemyPattern.SPIRAL,
                EnemyPattern.PINCER,
                EnemyPattern.SCREEN_CLEAR
            ]
```

### 2.3 Update Combat Scoring

```python
# When player kills enemy

def on_enemy_killed(self, enemy, player_took_damage=False):
    """Handle enemy death and scoring"""
    # Register kill with combo system
    self.combo_system.register_kill(took_damage=player_took_damage)
    
    # Calculate distance from player
    dx = self.player.x - enemy.x
    dy = self.player.y - enemy.y
    distance = math.sqrt(dx*dx + dy*dy)
    
    # Check for special conditions
    special_conditions = []
    if self.player.is_dashing:
        special_conditions.append("during_dash")
    if self.refugees_nearby > 0 and self.enemies_nearby > 3:
        special_conditions.append("rescue_under_fire")
        
    # Calculate and award score
    score = self.scoring_system.calculate_kill_score(
        enemy_type=enemy.behavior.value,
        distance=distance,
        player_pos=(self.player.x, self.player.y),
        enemy_pos=(enemy.x, enemy.y),
        special_conditions=special_conditions
    )
    
    # Visual/audio feedback
    self.play_explosion_effect(enemy.x, enemy.y)
    if self.combo_system.multiplier >= 3.0:
        self.play_combo_sound()
```

---

## Step 3: Add Mission Debrief

```python
# In game_main.py (continued)

class MinmatarRebellion:
    def end_mission(self):
        """Transition to mission debrief"""
        # Calculate performance rating
        performance = self._calculate_performance()
        
        # Get tribal message
        debrief_msg = self.cinematic_mgr.get_mission_debrief_message(
            self.player_profile["tribe"],
            performance
        )
        
        # Store mission results
        self.mission_results = {
            "score": self.scoring_system.total_score,
            "refugees": self.refugees_rescued,
            "accuracy": self.shots_hit / max(1, self.shots_fired),
            "deaths": self.player_deaths,
            "performance": performance,
            "tribal_message": debrief_msg
        }
        
        self.game_state = GameState.MISSION_DEBRIEF
        
    def _calculate_performance(self) -> str:
        """Determine mission performance rating"""
        score = self.scoring_system.total_score
        deaths = self.player_deaths
        
        if deaths == 0 and score > 50000:
            return "excellent"
        elif deaths <= 1 and score > 30000:
            return "good"
        elif deaths <= 3:
            return "survival"
        else:
            return "difficult"
            
    def render_mission_debrief(self):
        """Show mission results with tribal feedback"""
        self.screen.fill((10, 10, 15))
        
        # Mission stats
        font_title = pygame.font.Font(None, 56)
        font_stat = pygame.font.Font(None, 36)
        
        title = font_title.render("MISSION COMPLETE", True, (200, 150, 100))
        title_rect = title.get_rect(center=(self.width // 2, 80))
        self.screen.blit(title, title_rect)
        
        # Display stats
        stats = [
            f"SCORE: {self.mission_results['score']:,}",
            f"REFUGEES RESCUED: {self.mission_results['refugees']}",
            f"ACCURACY: {self.mission_results['accuracy']:.1%}",
            f"DEATHS: {self.mission_results['deaths']}"
        ]
        
        y = 200
        for stat in stats:
            stat_surf = font_stat.render(stat, True, (255, 255, 255))
            stat_rect = stat_surf.get_rect(center=(self.width // 2, y))
            self.screen.blit(stat_surf, stat_rect)
            y += 50
            
        # Tribal representative box
        tribe_color = self.cinematic_mgr.tribes[self.player_profile["tribe"]]["color"]
        msg_box = pygame.Rect(200, 450, self.width - 400, 150)
        pygame.draw.rect(self.screen, (30, 30, 40), msg_box)
        pygame.draw.rect(self.screen, tribe_color, msg_box, 3)
        
        # Tribal message
        font_msg = pygame.font.Font(None, 32)
        msg_lines = self._wrap_text(
            self.mission_results['tribal_message'], 
            font_msg, 
            msg_box.width - 40
        )
        
        msg_y = msg_box.top + 30
        for line in msg_lines:
            line_surf = font_msg.render(line, True, (220, 220, 220))
            line_rect = line_surf.get_rect(center=(self.width // 2, msg_y))
            self.screen.blit(line_surf, line_rect)
            msg_y += 40
```

---

## Step 4: Add Upgrade Cinematics

```python
def check_for_upgrade(self):
    """Check if player has unlocked new ship tier"""
    current_tier = self.player_profile["ship_tier"]
    sp = self.player_profile["skill_points"]
    
    # Wolf unlock
    if current_tier == 0 and sp >= WOLF_UNLOCK_COST:
        if "upgrade_wolf" not in self.player_profile["cinematics_seen"]:
            self.trigger_upgrade_cinematic("wolf")
            self.player_profile["ship_tier"] = 1
            self.player_profile["cinematics_seen"].append("upgrade_wolf")
            return True
            
    # Jaguar unlock
    elif current_tier == 1 and sp >= JAGUAR_UNLOCK_COST:
        if "upgrade_jaguar" not in self.player_profile["cinematics_seen"]:
            self.trigger_upgrade_cinematic("jaguar")
            self.player_profile["ship_tier"] = 2
            self.player_profile["cinematics_seen"].append("upgrade_jaguar")
            return True
            
    return False
    
def trigger_upgrade_cinematic(self, ship_name: str):
    """Show ship upgrade cinematic"""
    self.game_state = GameState.UPGRADE_CINEMATIC
    self.upgrade_ship = ship_name
    # Implementation would show ship with upgrade effects
```

---

## Step 5: Testing Checklist

### Phase 1: Cinematic Testing
- [ ] Opening cinematic plays on first launch
- [ ] Can skip cinematic with SPACE
- [ ] Tribal selection screen appears
- [ ] All four tribes selectable
- [ ] Profile creation stores data
- [ ] **First ship cinematic plays after tribe selection**
- [ ] **Ace's "pile of rust" dialogue displays correctly**
- [ ] **Elder response matches selected tribe**
- [ ] **Beat-up Rifter visual shows damage/duct tape**
- [ ] Tribal bonuses apply correctly

### Phase 2: Combat Testing
- [ ] Combo builds without damage
- [ ] Combo resets on hit
- [ ] Score popups appear
- [ ] Distance bonuses calculate
- [ ] Special condition bonuses work
- [ ] Combo text displays correctly

### Phase 3: Wave Testing
- [ ] Each pattern spawns correctly
- [ ] Enemy AI behaviors work
- [ ] Difficulty scales with mission
- [ ] Wave timing feels good
- [ ] Screen never feels empty or too full

### Phase 4: Integration Testing
- [ ] Full gameplay loop works
- [ ] Mission debrief shows stats
- [ ] Tribal messages appear
- [ ] Upgrade cinematics trigger
- [ ] Profile saves and loads

---

## Performance Considerations

### Optimization Tips

1. **Particle System**
   - Pool particles, don't create/destroy
   - Limit active particles to 500
   
2. **Score Events**
   - Cap floating text to 20 active
   - Use sprite batching for numbers
   
3. **Enemy AI**
   - Update only on-screen enemies
   - Cull off-screen enemies after 2 seconds
   
4. **Combo System**
   - Very lightweight, no optimization needed
   
5. **Cinematic Rendering**
   - Cache rendered frames for replay
   - Use sprite sheets for explosions

---

## Assets Needed

### Cinematic Assets
- `titan_base.png` - Amarr Avatar titan silhouette
- `planet_temperate.png` - Planet background
- `explosion_01.png` through `explosion_10.png` - Explosion frames
- `tribal_borders/` - Decorative borders for each tribe

### Tribal Assets
- `portrait_sebiestor.png` - Sebiestor representative
- `portrait_brutor.png` - Brutor representative
- `portrait_vherokior.png` - Vherokior representative
- `portrait_krusual.png` - Krusual representative

### Combat Assets
- Already have most assets (existing game)
- May need: hit markers, combo graphics

---

## Next Steps

1. **Week 1**: Implement opening cinematic and tribal selection
2. **Week 2**: Add combo/scoring system to existing combat
3. **Week 3**: Replace enemy spawning with wave system
4. **Week 4**: Add mission debrief and upgrade cinematics
5. **Week 5**: Polish, balance, test

Would you like me to:
1. Create example mission definition JSON files?
2. Write the profile save/load system?
3. Design the boss ability system?
4. Create audio cue specifications?
