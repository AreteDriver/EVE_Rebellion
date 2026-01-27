"""
Minmatar Rebellion - Arcade Combat System
Implements satisfying arcade scoring, combo mechanics, and enemy AI patterns
"""

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

import pygame


class EnemyPattern(Enum):
    LINEAR_RUSH = "linear_rush"
    SINE_WAVE = "sine_wave"
    SPIRAL = "spiral"
    AMBUSH = "ambush"
    PINCER = "pincer"
    SCREEN_CLEAR = "screen_clear"


class EnemyBehavior(Enum):
    KAMIKAZE = "kamikaze"
    WEAVER = "weaver"
    SNIPER = "sniper"
    SPAWNER = "spawner"
    TANK = "tank"
    BASIC = "basic"


@dataclass
class ScoreEvent:
    """Individual scoring event for visual feedback"""

    points: int
    x: float
    y: float
    text: str
    lifetime: float = 0.0
    max_lifetime: float = 1.5


class ComboSystem:
    """Manages combo multiplier and timing"""

    def __init__(self):
        self.multiplier = 1.0
        self.max_multiplier = 5.0
        self.combo_timer = 0.0
        self.combo_timeout = 3.0  # Seconds between kills
        self.hits_in_combo = 0
        self.no_damage_streak = True

    def register_kill(self, took_damage: bool = False):
        """Register enemy kill for combo"""
        if took_damage:
            self.reset_combo()
        else:
            self.hits_in_combo += 1
            self.multiplier = min(1.0 + (self.hits_in_combo * 0.5), self.max_multiplier)
            self.combo_timer = self.combo_timeout

    def take_damage(self):
        """Player took damage - reset combo"""
        self.reset_combo()

    def reset_combo(self):
        """Reset combo to base state"""
        self.multiplier = 1.0
        self.hits_in_combo = 0
        self.no_damage_streak = False

    def update(self, delta_time: float):
        """Update combo timer"""
        if self.combo_timer > 0:
            self.combo_timer -= delta_time
            if self.combo_timer <= 0:
                self.reset_combo()

    def get_combo_text(self) -> str:
        """Get display text for current combo"""
        if self.multiplier >= 5.0:
            return "LEGENDARY!"
        elif self.multiplier >= 4.0:
            return "AMAZING!"
        elif self.multiplier >= 3.0:
            return "EXCELLENT!"
        elif self.multiplier >= 2.0:
            return "GREAT!"
        else:
            return ""


class ScoringSystem:
    """Handles all scoring calculations and visual feedback"""

    def __init__(self, combo_system: ComboSystem):
        self.combo = combo_system
        self.total_score = 0
        self.score_events: List[ScoreEvent] = []

        # Base values
        self.enemy_values = {
            "basic": 10,
            "weaver": 25,
            "sniper": 30,
            "tank": 40,
            "spawner": 35,
            "kamikaze": 15,
            "boss_tier1": 500,
            "boss_tier2": 1000,
            "boss_tier3": 2500,
            "boss_tier4": 5000,
        }

    def calculate_kill_score(
        self,
        enemy_type: str,
        distance: float,
        player_pos: Tuple[float, float],
        enemy_pos: Tuple[float, float],
        special_conditions: List[str] = None,
    ) -> int:
        """
        Calculate score for killing enemy

        Args:
            enemy_type: Type of enemy killed
            distance: Distance from player to enemy
            player_pos: Player position
            enemy_pos: Enemy position
            special_conditions: List of special condition strings
                ["close_range", "sniper", "during_dash", "under_fire", etc.]
        """
        base_score = self.enemy_values.get(enemy_type, 10)

        # Apply combo multiplier
        score = int(base_score * self.combo.multiplier)

        # Distance modifiers
        if distance < 200:
            score = int(score * 1.25)
            self._add_score_event(score, enemy_pos[0], enemy_pos[1], "DANGER CLOSE!")
        elif distance > 600:
            score = int(score * 1.15)
            self._add_score_event(score, enemy_pos[0], enemy_pos[1], "SNIPER!")

        # Special condition bonuses
        if special_conditions:
            if "rescue_under_fire" in special_conditions:
                score += 100
                self._add_score_event(100, enemy_pos[0], enemy_pos[1], "BRAVE!")
            if "boss_no_hit" in special_conditions:
                score += 1000
                self._add_score_event(1000, enemy_pos[0], enemy_pos[1], "FLAWLESS!")
            if "during_dash" in special_conditions:
                score += 50
                self._add_score_event(50, enemy_pos[0], enemy_pos[1], "QUICK STRIKE!")
        else:
            self._add_score_event(score, enemy_pos[0], enemy_pos[1], f"+{score}")

        self.total_score += score
        return score

    def _add_score_event(self, points: int, x: float, y: float, text: str):
        """Add visual score popup"""
        self.score_events.append(ScoreEvent(points, x, y, text))

    def update(self, delta_time: float):
        """Update score events for visual feedback"""
        for event in self.score_events[:]:
            event.lifetime += delta_time
            if event.lifetime >= event.max_lifetime:
                self.score_events.remove(event)

    def render_score_events(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """Render floating score popups"""
        font = pygame.font.Font(None, 32)

        for event in self.score_events:
            # Fade out and float up
            alpha = int(255 * (1.0 - event.lifetime / event.max_lifetime))
            y_offset = -event.lifetime * 50  # Float upward

            color = (255, 255, 100) if event.points > 100 else (255, 255, 255)
            text_surface = font.render(event.text, True, color)
            text_surface.set_alpha(alpha)

            pos = (int(event.x - camera_offset[0]), int(event.y + y_offset - camera_offset[1]))

            screen.blit(text_surface, pos)


class WaveSpawner:
    """Generates enemy waves with arcade-style patterns"""

    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.active_patterns: List[Dict] = []

    def spawn_wave(self, pattern: EnemyPattern, difficulty: float = 1.0) -> List[Dict]:
        """
        Generate enemy spawn data for a wave pattern

        Returns list of enemy spawn dictionaries:
        {
            "type": EnemyBehavior,
            "spawn_time": float,  # Seconds after wave start
            "position": (x, y),
            "movement_params": dict
        }
        """
        enemies = []

        if pattern == EnemyPattern.LINEAR_RUSH:
            # Enemies fly straight down in formation
            count = int(5 + difficulty * 3)
            for i in range(count):
                enemies.append(
                    {
                        "type": EnemyBehavior.BASIC,
                        "spawn_time": i * 0.5,
                        "position": (100 + i * 100, -50),
                        "movement_params": {"velocity": (0, 100 * difficulty)},
                    }
                )

        elif pattern == EnemyPattern.SINE_WAVE:
            # Enemies weave side to side
            count = int(8 + difficulty * 4)
            for i in range(count):
                enemies.append(
                    {
                        "type": EnemyBehavior.WEAVER,
                        "spawn_time": i * 0.4,
                        "position": (self.width // 2, -50),
                        "movement_params": {
                            "base_velocity": (0, 80 * difficulty),
                            "wave_amplitude": 100,
                            "wave_frequency": 2.0,
                        },
                    }
                )

        elif pattern == EnemyPattern.SPIRAL:
            # Enemies rotate inward
            count = int(12 + difficulty * 6)
            center = (self.width // 2, self.height // 4)
            for i in range(count):
                angle = (i / count) * 2 * math.pi
                radius = 300
                enemies.append(
                    {
                        "type": EnemyBehavior.BASIC,
                        "spawn_time": i * 0.2,
                        "position": (
                            center[0] + math.cos(angle) * radius,
                            center[1] + math.sin(angle) * radius,
                        ),
                        "movement_params": {
                            "spiral_center": center,
                            "spiral_speed": 50 * difficulty,
                        },
                    }
                )

        elif pattern == EnemyPattern.AMBUSH:
            # Enemies enter from sides and behind
            count = int(6 + difficulty * 3)
            for i in range(count):
                side = i % 4
                if side == 0:  # Left
                    pos = (-50, random.randint(100, self.height - 100))
                    vel = (150 * difficulty, 0)
                elif side == 1:  # Right
                    pos = (self.width + 50, random.randint(100, self.height - 100))
                    vel = (-150 * difficulty, 0)
                elif side == 2:  # Top
                    pos = (random.randint(100, self.width - 100), -50)
                    vel = (0, 150 * difficulty)
                else:  # Bottom
                    pos = (random.randint(100, self.width - 100), self.height + 50)
                    vel = (0, -150 * difficulty)

                enemies.append(
                    {
                        "type": EnemyBehavior.KAMIKAZE,
                        "spawn_time": i * 0.6,
                        "position": pos,
                        "movement_params": {"velocity": vel},
                    }
                )

        elif pattern == EnemyPattern.PINCER:
            # Two groups converge from edges
            count = int(10 + difficulty * 5)
            for i in range(count):
                side = i % 2
                y_pos = 100 + (i // 2) * 80
                if side == 0:
                    pos = (-50, y_pos)
                    target = (self.width // 2, self.height // 2)
                else:
                    pos = (self.width + 50, y_pos)
                    target = (self.width // 2, self.height // 2)

                enemies.append(
                    {
                        "type": EnemyBehavior.BASIC,
                        "spawn_time": (i // 2) * 0.5,
                        "position": pos,
                        "movement_params": {"target": target, "speed": 100 * difficulty},
                    }
                )

        elif pattern == EnemyPattern.SCREEN_CLEAR:
            # Fills screen gradually
            count = int(20 + difficulty * 10)
            for i in range(count):
                enemies.append(
                    {
                        "type": random.choice([EnemyBehavior.BASIC, EnemyBehavior.WEAVER]),
                        "spawn_time": i * 0.3,
                        "position": (
                            random.randint(50, self.width - 50),
                            random.randint(-200, -50),
                        ),
                        "movement_params": {
                            "velocity": (
                                random.uniform(-30, 30),
                                random.uniform(60, 120) * difficulty,
                            )
                        },
                    }
                )

        return enemies


class EnemyAI:
    """Individual enemy AI controller"""

    def __init__(
        self, behavior: EnemyBehavior, position: Tuple[float, float], movement_params: Dict
    ):
        self.behavior = behavior
        self.position = list(position)
        self.params = movement_params
        self.alive = True
        self.time_alive = 0.0
        self.velocity = [0.0, 0.0]

        # AI state
        self.target_acquired = False
        self.firing_cooldown = 0.0

    def update(
        self, delta_time: float, player_pos: Tuple[float, float], screen_bounds: Tuple[int, int]
    ) -> Optional[Dict]:
        """
        Update enemy AI and return shot data if firing

        Returns:
            Dict with shot data or None
            {"position": (x, y), "velocity": (vx, vy), "damage": int}
        """
        self.time_alive += delta_time
        shot_data = None

        if self.behavior == EnemyBehavior.BASIC:
            # Simple movement toward target or constant velocity
            if "velocity" in self.params:
                self.velocity = self.params["velocity"]
            elif "target" in self.params:
                target = self.params["target"]
                speed = self.params.get("speed", 100)
                dx = target[0] - self.position[0]
                dy = target[1] - self.position[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    self.velocity = [dx / dist * speed, dy / dist * speed]

        elif self.behavior == EnemyBehavior.WEAVER:
            # Sine wave movement
            base_vel = self.params.get("base_velocity", (0, 80))
            amplitude = self.params.get("wave_amplitude", 100)
            frequency = self.params.get("wave_frequency", 2.0)

            wave_offset = math.sin(self.time_alive * frequency) * amplitude
            self.velocity = [wave_offset * 0.5, base_vel[1]]

        elif self.behavior == EnemyBehavior.KAMIKAZE:
            # Accelerate toward player
            if not self.target_acquired:
                self.target_acquired = True
                dx = player_pos[0] - self.position[0]
                dy = player_pos[1] - self.position[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    speed = 200
                    self.velocity = [dx / dist * speed, dy / dist * speed]

        elif self.behavior == EnemyBehavior.SNIPER:
            # Stay at top, track and shoot player
            self.velocity = [0, 0]
            self.firing_cooldown -= delta_time

            if self.firing_cooldown <= 0:
                # Fire tracking shot at player
                dx = player_pos[0] - self.position[0]
                dy = player_pos[1] - self.position[1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    shot_speed = 300
                    shot_data = {
                        "position": tuple(self.position),
                        "velocity": (dx / dist * shot_speed, dy / dist * shot_speed),
                        "damage": 15,
                    }
                    self.firing_cooldown = 2.0  # Fire every 2 seconds

        elif self.behavior == EnemyBehavior.TANK:
            # Slow, shoots area denial patterns
            self.velocity = [0, 30]
            self.firing_cooldown -= delta_time

            if self.firing_cooldown <= 0:
                # Fire spread pattern
                shot_data = {
                    "position": tuple(self.position),
                    "velocity": (0, 200),
                    "damage": 20,
                    "pattern": "spread",  # Would spawn multiple shots
                }
                self.firing_cooldown = 3.0

        # Update position
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time

        # Check if off screen
        if (
            self.position[0] < -100
            or self.position[0] > screen_bounds[0] + 100
            or self.position[1] < -100
            or self.position[1] > screen_bounds[1] + 100
        ):
            self.alive = False

        return shot_data

    def take_damage(self, damage: int) -> bool:
        """
        Take damage, return True if killed
        """
        # Simple version - enemies die in one hit
        # Full version would have HP system
        self.alive = False
        return True


# Example usage
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    combo = ComboSystem()
    scoring = ScoringSystem(combo)
    spawner = WaveSpawner(1280, 720)

    # Spawn test wave
    wave_data = spawner.spawn_wave(EnemyPattern.SINE_WAVE, difficulty=1.0)
    print(f"Spawned wave with {len(wave_data)} enemies")

    # Test scoring
    player_pos = (640, 600)
    enemy_pos = (640, 100)
    distance = math.sqrt((player_pos[0] - enemy_pos[0]) ** 2 + (player_pos[1] - enemy_pos[1]) ** 2)

    for i in range(5):
        combo.register_kill(took_damage=False)
        score = scoring.calculate_kill_score("basic", distance, player_pos, enemy_pos)
        print(
            f"Kill {i + 1}: {score} points, Combo: {combo.multiplier}x, Text: {combo.get_combo_text()}"
        )

    print(f"Total score: {scoring.total_score}")

    pygame.quit()
