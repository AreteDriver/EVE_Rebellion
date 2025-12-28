"""
Abyssal Depths Mode for EVE Rebellion
Triglavian roguelike extraction mode with rooms, hazards, and timer.
"""

import json
import math
import random
import pygame
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field


@dataclass
class AbyssalRoomState:
    """State for a single room in the Abyss."""
    room_number: int  # 1, 2, or 3
    enemies_spawned: int = 0
    enemies_killed: int = 0
    total_enemies: int = 0
    hazards_active: List[Any] = field(default_factory=list)
    cache_collected: bool = False
    gate_active: bool = False
    gate_progress: float = 0.0  # 0 to 1 for extraction
    cleared: bool = False


@dataclass
class AbyssalRunState:
    """State for an entire Abyssal run."""
    filament_type: str = 'exotic'
    tier: int = 1
    current_room: int = 1
    timer_remaining: float = 1200.0  # Seconds
    total_loot: int = 0
    rooms: List[AbyssalRoomState] = field(default_factory=list)
    extracted: bool = False
    failed: bool = False
    death_reason: str = ''


class TriglavianEnemy:
    """Triglavian enemy with disintegrator damage ramping."""

    def __init__(self, enemy_type: str, x: float, y: float, config: Dict):
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.config = config

        # Stats from config
        self.max_hp = config.get('hp', 100)
        self.hp = self.max_hp
        self.speed = config.get('speed', 200)
        self.base_damage = config.get('base_damage', 10)
        self.damage_ramp_max = config.get('damage_ramp_max', 2.0)
        self.damage_ramp_time = config.get('damage_ramp_time', 6.0)

        # Disintegrator state
        self.current_target = None
        self.time_on_target = 0.0
        self.current_damage_mult = 1.0

        # Movement
        self.vx = 0.0
        self.vy = 0.0

    def update_damage_ramp(self, dt: float, has_target: bool, same_target: bool):
        """Update disintegrator damage ramping."""
        if has_target and same_target:
            # Ramp up damage over time
            self.time_on_target += dt
            ramp_progress = min(1.0, self.time_on_target / self.damage_ramp_time)
            self.current_damage_mult = 1.0 + (self.damage_ramp_max - 1.0) * ramp_progress
        else:
            # Reset ramp when switching targets or no target
            self.time_on_target = 0.0
            self.current_damage_mult = 1.0

    def get_damage(self) -> float:
        """Get current damage including ramp."""
        return self.base_damage * self.current_damage_mult

    def take_damage(self, amount: float) -> bool:
        """Take damage, return True if dead."""
        self.hp -= amount
        return self.hp <= 0


class AbyssalHazard:
    """Environmental hazard in the Abyss."""

    def __init__(self, hazard_type: str, x: float, y: float, config: Dict):
        self.hazard_type = hazard_type
        self.x = x
        self.y = y
        self.config = config

        self.radius = config.get('radius', 100)
        self.hp = config.get('hp', 0)  # 0 = indestructible
        self.damage = config.get('damage', 0)
        self.pulse_timer = 0.0
        self.pulse_interval = config.get('pulse_interval', 3.0)
        self.active = True

        # Visual state
        self.pulse_flash = 0.0
        self.rotation = random.uniform(0, 360)

    def update(self, dt: float) -> Optional[Dict]:
        """Update hazard, return effect dict if triggered."""
        if not self.active:
            return None

        self.rotation += 30 * dt  # Spin

        if self.hazard_type == 'deviant_automata':
            self.pulse_timer += dt
            if self.pulse_timer >= self.pulse_interval:
                self.pulse_timer = 0.0
                self.pulse_flash = 1.0
                return {
                    'type': 'aoe_damage',
                    'x': self.x,
                    'y': self.y,
                    'radius': self.radius,
                    'damage': self.damage
                }

        self.pulse_flash = max(0, self.pulse_flash - dt * 2)
        return None

    def take_damage(self, amount: float) -> bool:
        """Take damage, return True if destroyed."""
        if self.hp <= 0:
            return False  # Indestructible
        self.hp -= amount
        if self.hp <= 0:
            self.active = False
            return True
        return False

    def is_in_range(self, x: float, y: float) -> bool:
        """Check if point is within hazard radius."""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx*dx + dy*dy) < self.radius


class ExtractionGate:
    """Extraction gate for escaping the Abyss."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 60
        self.active = False
        self.channeling = False
        self.channel_progress = 0.0
        self.channel_time = 2.0  # Seconds to extract
        self.pulse_timer = 0.0

    def activate(self):
        """Activate the gate after room is cleared."""
        self.active = True

    def start_channel(self):
        """Start extraction channel."""
        if self.active:
            self.channeling = True

    def stop_channel(self):
        """Stop extraction channel."""
        self.channeling = False
        self.channel_progress = 0.0  # Reset on interruption

    def update(self, dt: float, player_in_range: bool) -> bool:
        """Update gate, return True if extraction complete."""
        self.pulse_timer += dt

        if not self.active:
            return False

        if player_in_range and self.channeling:
            self.channel_progress += dt / self.channel_time
            if self.channel_progress >= 1.0:
                return True  # Extracted!
        elif not player_in_range:
            self.stop_channel()

        return False

    def is_in_range(self, x: float, y: float) -> bool:
        """Check if point is within gate activation radius."""
        dx = x - self.x
        dy = y - self.y
        return math.sqrt(dx*dx + dy*dy) < self.radius


class AbyssalDepthsMode:
    """
    Manages the Abyssal Depths roguelike mode.

    Flow:
    1. Select filament type and tier
    2. Enter Room 1 (Pockets) - light enemies, orientation
    3. Clear enemies, collect cache, enter gate
    4. Enter Room 2 (Escalation) - harder enemies, hazards
    5. Clear enemies, collect cache, enter gate
    6. Enter Room 3 (Extraction) - boss + swarm, extraction gate
    7. Clear enough enemies, channel extraction gate to escape
    8. Timer runs out = death (ship lost)
    """

    def __init__(self, screen_width: int = 800, screen_height: int = 700):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = self._load_config()
        self.state: Optional[AbyssalRunState] = None
        self.room_state: Optional[AbyssalRoomState] = None

        # Active entities
        self.enemies: List[TriglavianEnemy] = []
        self.hazards: List[AbyssalHazard] = []
        self.extraction_gate: Optional[ExtractionGate] = None

        # UI state
        self.room_transition_timer = 0.0
        self.showing_room_intro = False
        self.intro_timer = 0.0

    def _load_config(self) -> Dict:
        """Load Abyssal Depths configuration."""
        config_path = Path("config/chapters/abyssal_depths_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[Abyssal] Error loading config: {e}")
        return self._default_config()

    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'filaments': {
                'exotic': {'name': 'Exotic', 'color': '#FFFFFF'},
                'firestorm': {'name': 'Firestorm', 'color': '#FF4500'},
            },
            'tiers': {
                '1': {'name': 'Calm', 'timer_seconds': 1200, 'enemy_hp_mult': 1.0},
            },
            'rooms': {
                'room_1': {'enemy_count_by_tier': [8], 'hazard_count': 0},
                'room_2': {'enemy_count_by_tier': [12], 'hazard_count_by_tier': [1]},
                'room_3': {'enemy_count_by_tier': [15], 'has_extraction_gate': True},
            }
        }

    def start_run(self, filament_type: str, tier: int):
        """Start a new Abyssal run."""
        tier_config = self.config.get('tiers', {}).get(str(tier), {})
        timer = tier_config.get('timer_seconds', 1200)

        self.state = AbyssalRunState(
            filament_type=filament_type,
            tier=tier,
            current_room=1,
            timer_remaining=float(timer),
            rooms=[]
        )

        # Initialize first room
        self._setup_room(1)
        self.showing_room_intro = True
        self.intro_timer = 3.0  # 3 second intro

    def _setup_room(self, room_num: int):
        """Setup a room with enemies and hazards."""
        room_key = f'room_{room_num}'
        room_config = self.config.get('rooms', {}).get(room_key, {})
        tier = self.state.tier if self.state else 1

        # Calculate enemy count
        enemy_counts = room_config.get('enemy_count_by_tier', [10])
        tier_idx = min(tier - 1, len(enemy_counts) - 1)
        total_enemies = enemy_counts[tier_idx]

        self.room_state = AbyssalRoomState(
            room_number=room_num,
            total_enemies=total_enemies
        )

        # Clear previous room entities
        self.enemies.clear()
        self.hazards.clear()
        self.extraction_gate = None

        # Setup hazards for room 2+
        if room_num >= 2:
            hazard_counts = room_config.get('hazard_count_by_tier', [0])
            hazard_idx = min(tier - 1, len(hazard_counts) - 1)
            hazard_count = hazard_counts[hazard_idx] if hazard_idx < len(hazard_counts) else 0
            self._spawn_hazards(hazard_count)

        # Setup extraction gate for room 3
        if room_config.get('has_extraction_gate', False):
            self.extraction_gate = ExtractionGate(
                self.screen_width // 2,
                100  # Top of screen
            )

    def _spawn_hazards(self, count: int):
        """Spawn environmental hazards."""
        hazard_types = ['deviant_automata', 'tachyon_cloud', 'ephialtes_cloud']
        hazard_configs = self.config.get('hazards', {})

        for _ in range(count):
            hazard_type = random.choice(hazard_types)
            config = hazard_configs.get(hazard_type, {})

            x = random.randint(100, self.screen_width - 100)
            y = random.randint(150, self.screen_height - 200)

            hazard = AbyssalHazard(hazard_type, x, y, config)
            self.hazards.append(hazard)

    def spawn_enemy(self) -> Optional[TriglavianEnemy]:
        """Spawn a Triglavian enemy, return it for game integration."""
        if not self.room_state or not self.state:
            return None

        if self.room_state.enemies_spawned >= self.room_state.total_enemies:
            return None

        # Get enemy config
        enemy_configs = self.config.get('enemies', {}).get('triglavian', {})
        enemy_type = random.choice(list(enemy_configs.keys())) if enemy_configs else 'damavik'
        config = enemy_configs.get(enemy_type, {
            'hp': 100,
            'speed': 200,
            'base_damage': 10,
            'damage_ramp_max': 2.0,
            'damage_ramp_time': 6.0
        })

        # Apply tier multipliers
        tier_config = self.config.get('tiers', {}).get(str(self.state.tier), {})
        config['hp'] = int(config.get('hp', 100) * tier_config.get('enemy_hp_mult', 1.0))

        # Spawn position
        x = random.randint(50, self.screen_width - 50)
        y = -30  # Off-screen top

        enemy = TriglavianEnemy(enemy_type, x, y, config)
        self.enemies.append(enemy)
        self.room_state.enemies_spawned += 1

        return enemy

    def on_enemy_killed(self, enemy: TriglavianEnemy):
        """Called when an enemy is killed."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)

        if self.room_state:
            self.room_state.enemies_killed += 1

            # Check if room is cleared (80% enemies killed)
            clear_threshold = int(self.room_state.total_enemies * 0.8)
            if self.room_state.enemies_killed >= clear_threshold:
                self._on_room_cleared()

    def _on_room_cleared(self):
        """Called when room is cleared."""
        if not self.room_state:
            return

        self.room_state.cleared = True

        # Activate extraction gate in room 3
        if self.room_state.room_number == 3 and self.extraction_gate:
            self.extraction_gate.activate()
        else:
            # Spawn transition gate
            self.room_state.gate_active = True

    def update(self, dt: float, player_x: float, player_y: float) -> Dict:
        """
        Update Abyssal mode state.

        Returns dict with events:
        - 'spawn_enemy': Should spawn an enemy
        - 'hazard_damage': Player took hazard damage
        - 'extracted': Player escaped
        - 'time_out': Timer expired
        - 'room_transition': Moving to next room
        """
        events = {}

        if not self.state or self.state.failed or self.state.extracted:
            return events

        # Update timer
        self.state.timer_remaining -= dt
        if self.state.timer_remaining <= 0:
            self.state.failed = True
            self.state.death_reason = 'TIME_EXPIRED'
            events['time_out'] = True
            return events

        # Room intro
        if self.showing_room_intro:
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.showing_room_intro = False
            return events

        # Spawn enemies periodically
        if self.room_state and self.room_state.enemies_spawned < self.room_state.total_enemies:
            if random.random() < 0.02:  # ~2% chance per frame at 60fps
                events['spawn_enemy'] = True

        # Update hazards
        for hazard in self.hazards:
            effect = hazard.update(dt)
            if effect and effect['type'] == 'aoe_damage':
                if hazard.is_in_range(player_x, player_y):
                    events['hazard_damage'] = effect['damage']

        # Update extraction gate
        if self.extraction_gate:
            in_range = self.extraction_gate.is_in_range(player_x, player_y)
            if self.extraction_gate.update(dt, in_range):
                self.state.extracted = True
                events['extracted'] = True

        # Check for room transition (non-extraction gate)
        if self.room_state and self.room_state.gate_active:
            # Gate at top center
            gate_x, gate_y = self.screen_width // 2, 50
            dx = player_x - gate_x
            dy = player_y - gate_y
            if math.sqrt(dx*dx + dy*dy) < 50:
                self._advance_room()
                events['room_transition'] = self.state.current_room

        return events

    def _advance_room(self):
        """Move to the next room."""
        if not self.state:
            return

        if self.state.current_room < 3:
            self.state.current_room += 1
            if self.room_state:
                self.state.rooms.append(self.room_state)
            self._setup_room(self.state.current_room)
            self.showing_room_intro = True
            self.intro_timer = 2.0

    def start_extraction_channel(self):
        """Start channeling the extraction gate."""
        if self.extraction_gate and self.extraction_gate.active:
            self.extraction_gate.start_channel()

    def stop_extraction_channel(self):
        """Stop channeling the extraction gate."""
        if self.extraction_gate:
            self.extraction_gate.stop_channel()

    def get_hud_data(self) -> Dict:
        """Get data for HUD display."""
        if not self.state:
            return {}

        minutes = int(self.state.timer_remaining // 60)
        seconds = int(self.state.timer_remaining % 60)

        room_progress = 0.0
        if self.room_state and self.room_state.total_enemies > 0:
            room_progress = self.room_state.enemies_killed / self.room_state.total_enemies

        return {
            'timer': f"{minutes:02d}:{seconds:02d}",
            'timer_critical': self.state.timer_remaining < 60,
            'room': self.state.current_room,
            'room_name': ['POCKETS', 'ESCALATION', 'EXTRACTION'][self.state.current_room - 1],
            'room_progress': room_progress,
            'filament': self.state.filament_type.upper(),
            'tier': self.state.tier,
            'loot': self.state.total_loot,
            'gate_active': self.room_state.gate_active if self.room_state else False,
            'extraction_progress': self.extraction_gate.channel_progress if self.extraction_gate else 0.0,
            'showing_intro': self.showing_room_intro,
        }

    def draw_hazards(self, surface: pygame.Surface):
        """Draw hazards on the game surface."""
        for hazard in self.hazards:
            if not hazard.active:
                continue

            # Color based on hazard type
            if hazard.hazard_type == 'deviant_automata':
                color = (200, 50, 50)
                pulse_color = (255, 100, 100)
            elif hazard.hazard_type == 'tachyon_cloud':
                color = (50, 100, 200)
                pulse_color = (100, 150, 255)
            else:  # ephialtes_cloud
                color = (150, 50, 200)
                pulse_color = (200, 100, 255)

            # Draw hazard area
            alpha = int(80 + hazard.pulse_flash * 100)
            hazard_surf = pygame.Surface((hazard.radius * 2, hazard.radius * 2), pygame.SRCALPHA)

            # Outer glow
            pygame.draw.circle(hazard_surf, (*color, alpha // 2),
                             (hazard.radius, hazard.radius), hazard.radius)
            # Inner core
            pygame.draw.circle(hazard_surf, (*pulse_color, alpha),
                             (hazard.radius, hazard.radius), hazard.radius // 2)
            # Border
            pygame.draw.circle(hazard_surf, color,
                             (hazard.radius, hazard.radius), hazard.radius, 2)

            surface.blit(hazard_surf,
                        (int(hazard.x - hazard.radius), int(hazard.y - hazard.radius)))

    def draw_extraction_gate(self, surface: pygame.Surface):
        """Draw the extraction gate."""
        if not self.extraction_gate:
            return

        gate = self.extraction_gate
        x, y = int(gate.x), int(gate.y)

        # Gate color based on state
        if gate.active:
            base_color = (100, 255, 100)  # Green when active
            pulse = math.sin(gate.pulse_timer * 3) * 0.3 + 0.7
        else:
            base_color = (100, 100, 100)  # Grey when inactive
            pulse = 0.5

        # Draw gate
        radius = gate.radius
        alpha = int(150 * pulse)

        gate_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        # Outer ring
        pygame.draw.circle(gate_surf, (*base_color, alpha),
                         (radius, radius), radius)
        # Inner portal
        inner_color = (200, 255, 200) if gate.active else (150, 150, 150)
        pygame.draw.circle(gate_surf, (*inner_color, alpha + 50),
                         (radius, radius), radius // 2)
        # Border
        pygame.draw.circle(gate_surf, base_color,
                         (radius, radius), radius, 3)

        surface.blit(gate_surf, (x - radius, y - radius))

        # Draw channel progress bar if channeling
        if gate.channeling and gate.channel_progress > 0:
            bar_width = 100
            bar_height = 10
            bar_x = x - bar_width // 2
            bar_y = y + radius + 10

            pygame.draw.rect(surface, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (100, 255, 100),
                           (bar_x, bar_y, int(bar_width * gate.channel_progress), bar_height))
            pygame.draw.rect(surface, (200, 200, 200),
                           (bar_x, bar_y, bar_width, bar_height), 1)

    def draw_room_intro(self, surface: pygame.Surface):
        """Draw room introduction overlay."""
        if not self.showing_room_intro or not self.room_state:
            return

        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Room title
        room_names = ['POCKETS', 'ESCALATION', 'EXTRACTION']
        room_name = room_names[self.room_state.room_number - 1]

        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 36)

        title = font_large.render(f"ROOM {self.room_state.room_number}", True, (200, 50, 80))
        subtitle = font_small.render(room_name, True, (255, 255, 255))

        cx = self.screen_width // 2
        cy = self.screen_height // 2

        title_rect = title.get_rect(center=(cx, cy - 30))
        subtitle_rect = subtitle.get_rect(center=(cx, cy + 30))

        surface.blit(title, title_rect)
        surface.blit(subtitle, subtitle_rect)


# Singleton instance
_abyssal_mode: Optional[AbyssalDepthsMode] = None


def get_abyssal_mode() -> AbyssalDepthsMode:
    """Get the global Abyssal Depths mode instance."""
    global _abyssal_mode
    if _abyssal_mode is None:
        _abyssal_mode = AbyssalDepthsMode()
    return _abyssal_mode
