"""
AI Behavior System for EVE Rebellion
Implements the 6 core AI behaviors from the design doc.
"""

import math
import random
from typing import Optional, Tuple, Any
from dataclasses import dataclass


# Behavior type constants
AI_BASIC = 'basic'
AI_KAMIKAZE = 'kamikaze'
AI_WEAVER = 'weaver'
AI_SNIPER = 'sniper'
AI_SPAWNER = 'spawner'
AI_TANK = 'tank'


@dataclass
class AIState:
    """State for AI behavior."""
    timer: float = 0.0
    phase: str = 'idle'
    target_x: float = 0.0
    target_y: float = 0.0
    last_dodge_time: float = 0.0
    spawn_cooldown: float = 0.0
    aggro_timer: float = 0.0
    path_angle: float = 0.0


class AIBehavior:
    """Base class for AI behaviors."""

    def __init__(self, enemy: Any, screen_width: int = 800, screen_height: int = 700):
        self.enemy = enemy
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = AIState()

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        """
        Update AI and return velocity and shoot flag.

        Returns:
            (vx, vy, should_shoot)
        """
        raise NotImplementedError

    def get_fire_rate_modifier(self) -> float:
        """Return fire rate modifier for this AI type."""
        return 1.0


class BasicAI(AIBehavior):
    """
    BASIC: Standard enemy behavior.
    Moves toward player's general area, shoots periodically.
    """

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt

        # Simple drift toward player's x position
        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        # Drift toward player's x with some variance
        target_x = px + random.uniform(-100, 100)
        dx = target_x - ex

        vx = 0.0
        if abs(dx) > 20:
            vx = math.copysign(min(abs(dx) * 0.02, 1.5), dx)

        # Move down the screen
        vy = self.enemy.speed * 0.6

        # Shoot if player is below
        should_shoot = py > ey and abs(px - ex) < 150

        return vx, vy, should_shoot


class KamikazeAI(AIBehavior):
    """
    KAMIKAZE: Suicide dive at player.
    Fast, aggressive, aims directly at player position.
    Explodes on contact for area damage.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state.phase = 'approach'
        self.dive_speed = 0.0
        self.max_dive_speed = 8.0
        self.locked = False

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt
        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        if self.state.phase == 'approach':
            # Move down until in range
            if ey < 150:
                return 0.0, self.enemy.speed * 0.8, False
            else:
                self.state.phase = 'lock_on'
                self.state.target_x = px
                self.state.target_y = py

        elif self.state.phase == 'lock_on':
            # Lock onto player and start dive
            self.state.phase = 'dive'
            self.dive_speed = self.enemy.speed

        elif self.state.phase == 'dive':
            # Accelerate toward locked position (slightly leading player)
            self.dive_speed = min(self.dive_speed + 0.2, self.max_dive_speed)

            # Aim at player with slight lead
            dx = px - ex
            dy = py - ey
            dist = max(1, math.sqrt(dx*dx + dy*dy))

            # Normalize and apply speed
            vx = (dx / dist) * self.dive_speed
            vy = (dy / dist) * self.dive_speed

            # Never shoot - all energy into the dive
            return vx, vy, False

        return 0.0, self.enemy.speed, False

    def get_fire_rate_modifier(self) -> float:
        return 0.0  # Kamikaze don't shoot


class WeaverAI(AIBehavior):
    """
    WEAVER: Dodges through bullet patterns.
    Evasive, hard to hit, unpredictable movement.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dodge_direction = random.choice([-1, 1])
        self.dodge_timer = 0.0
        self.weave_amplitude = 80
        self.weave_frequency = 2.0

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt
        self.dodge_timer += dt

        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        # Check for nearby bullets and dodge
        should_dodge = False
        dodge_dir = 0.0

        if bullets:
            for bullet in bullets:
                bx, by = bullet.rect.centerx, bullet.rect.centery
                dx = bx - ex
                dy = by - ey
                dist = math.sqrt(dx*dx + dy*dy)

                # If bullet is close and approaching
                if dist < 100 and by < ey:
                    should_dodge = True
                    # Dodge away from bullet
                    dodge_dir = -1 if dx > 0 else 1
                    break

        if should_dodge:
            # Sharp evasive maneuver
            vx = dodge_dir * 5.0
            vy = self.enemy.speed * 0.3
            self.dodge_direction = dodge_dir
        else:
            # Normal weaving movement
            weave_offset = math.sin(self.state.timer * self.weave_frequency) * self.weave_amplitude
            target_x = (self.screen_width / 2) + weave_offset

            dx = target_x - ex
            vx = min(abs(dx) * 0.1, 3.0) * math.copysign(1, dx)
            vy = self.enemy.speed * 0.7

        # Shoot only when not dodging
        should_shoot = not should_dodge and abs(px - ex) < 100

        return vx, vy, should_shoot


class SniperAI(AIBehavior):
    """
    SNIPER: Stays at range, precise shooting.
    Slow movement, high accuracy, deadly at distance.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.optimal_range = 350  # Preferred distance from player
        self.aim_timer = 0.0
        self.aiming = False

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt

        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        # Calculate distance to player
        dx = px - ex
        dy = py - ey
        dist = math.sqrt(dx*dx + dy*dy)

        # Movement: maintain optimal range
        if dist < self.optimal_range - 50:
            # Too close, back off
            vy = -0.5 * self.enemy.speed
            vx = 0.0
        elif dist > self.optimal_range + 50:
            # Too far, approach
            vy = 0.7 * self.enemy.speed
            vx = (dx / max(1, abs(dx))) * 0.5
        else:
            # Good range, slow strafe
            vx = math.sin(self.state.timer * 0.5) * 1.5
            vy = 0.1  # Very slow descent

        # Stay in bounds
        if ex < 50:
            vx = abs(vx)
        elif ex > self.screen_width - 50:
            vx = -abs(vx)

        # Aiming and shooting - slow, accurate
        if abs(px - ex) < 50 and not self.aiming:
            self.aiming = True
            self.aim_timer = 0.0

        if self.aiming:
            self.aim_timer += dt
            # Shoot after brief aim time
            if self.aim_timer > 0.5:  # 0.5 second aim time
                self.aiming = False
                return vx, vy, True

        return vx, vy, False

    def get_fire_rate_modifier(self) -> float:
        return 0.4  # Slower fire rate but more accurate


class SpawnerAI(AIBehavior):
    """
    SPAWNER: Summons smaller enemies.
    Hangs back, periodically spawns drones/fighters.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spawn_cooldown = 3.0  # Seconds between spawns
        self.last_spawn = 0.0
        self.max_children = 6
        self.children_spawned = 0
        self.spawn_queue = []  # Queue of enemies to spawn

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt

        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        # Stay at back of screen
        target_y = 100
        if ey < target_y:
            vy = 0.5
        elif ey > target_y + 50:
            vy = -0.3
        else:
            vy = 0.0

        # Slow lateral movement
        vx = math.sin(self.state.timer * 0.3) * 1.0

        # Keep in bounds
        if ex < 100:
            vx = abs(vx)
        elif ex > self.screen_width - 100:
            vx = -abs(vx)

        # Spawn check
        if (self.state.timer - self.last_spawn > self.spawn_cooldown and
            self.children_spawned < self.max_children):
            self.last_spawn = self.state.timer
            self.children_spawned += 1
            # Signal to spawn a drone (handled by game.py)
            self.spawn_queue.append({
                'type': 'drone',
                'x': ex + random.randint(-30, 30),
                'y': ey + 30
            })

        # Occasional shooting
        should_shoot = random.random() < 0.02

        return vx, vy, should_shoot

    def get_spawn_queue(self):
        """Get and clear the spawn queue."""
        queue = self.spawn_queue
        self.spawn_queue = []
        return queue


class TankAI(AIBehavior):
    """
    TANK: Slow, tough, absorbs damage.
    Advances steadily, soaks bullets, suppressive fire.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.advance_speed = 0.3
        self.suppression_mode = False

    def update(self, player_pos: Tuple[float, float], bullets: Any = None, dt: float = 1/60) -> Tuple[float, float, bool]:
        self.state.timer += dt

        ex, ey = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py = player_pos

        # Slow, inexorable advance
        vy = self.enemy.speed * self.advance_speed

        # Slight tracking of player
        dx = px - ex
        if abs(dx) > 50:
            vx = math.copysign(0.3, dx)
        else:
            vx = 0.0

        # Stay in bounds
        if ex < 80:
            vx = 0.3
        elif ex > self.screen_width - 80:
            vx = -0.3

        # Suppressive fire - always shooting when in range
        should_shoot = ey > 50 and ey < py

        return vx, vy, should_shoot

    def get_fire_rate_modifier(self) -> float:
        return 1.5  # Faster fire rate for suppression


# AI behavior registry
AI_BEHAVIORS = {
    AI_BASIC: BasicAI,
    AI_KAMIKAZE: KamikazeAI,
    AI_WEAVER: WeaverAI,
    AI_SNIPER: SniperAI,
    AI_SPAWNER: SpawnerAI,
    AI_TANK: TankAI,
}


def get_ai_for_enemy(enemy_type: str) -> str:
    """Get the appropriate AI behavior type for an enemy type."""
    # Map enemy types to AI behaviors
    ai_mapping = {
        # === AMARR ===
        'executioner': AI_BASIC,
        'punisher': AI_TANK,
        'tormentor': AI_SNIPER,
        'crucifier': AI_WEAVER,
        'coercer': AI_TANK,
        'omen': AI_SNIPER,
        'maller': AI_TANK,
        'harbinger': AI_SPAWNER,
        'prophecy': AI_TANK,
        'apocalypse': AI_TANK,
        'abaddon': AI_SNIPER,

        # === MINMATAR ===
        'rifter': AI_BASIC,
        'slasher': AI_WEAVER,
        'breacher': AI_BASIC,
        'burst': AI_BASIC,
        'thrasher': AI_BASIC,
        'stabber': AI_WEAVER,
        'rupture': AI_TANK,
        'bellicose': AI_SNIPER,
        'hurricane': AI_TANK,
        'cyclone': AI_SPAWNER,
        'tempest': AI_SNIPER,
        'typhoon': AI_SPAWNER,
        'maelstrom': AI_TANK,

        # === GALLENTE ===
        'tristan': AI_SPAWNER,  # Drone boat
        'atron': AI_WEAVER,
        'incursus': AI_TANK,
        'catalyst': AI_BASIC,
        'thorax': AI_TANK,
        'vexor': AI_SPAWNER,  # Drone boat
        'brutix': AI_TANK,
        'myrmidon': AI_SPAWNER,  # Drone boat
        'dominix': AI_SPAWNER,  # Drone boat
        'megathron': AI_SNIPER,

        # === CALDARI ===
        'kestrel': AI_SNIPER,  # Missiles
        'merlin': AI_TANK,
        'condor': AI_WEAVER,
        'cormorant': AI_SNIPER,
        'caracal': AI_SNIPER,  # Missiles
        'moa': AI_TANK,
        'drake': AI_TANK,  # Famous shield tank
        'ferox': AI_SNIPER,
        'raven': AI_SNIPER,  # Missiles
        'rokh': AI_SNIPER,

        # === SPECIAL ===
        'drone': AI_KAMIKAZE,
        'interceptor': AI_KAMIKAZE,
        'bomber': AI_SNIPER,

        # === TRIGLAVIAN ===
        'vedmak': AI_WEAVER,
        'leshak': AI_SNIPER,
    }

    return ai_mapping.get(enemy_type, AI_BASIC)


def create_ai_behavior(enemy: Any, behavior_type: str = None) -> AIBehavior:
    """Create an AI behavior instance for an enemy."""
    if behavior_type is None:
        behavior_type = get_ai_for_enemy(enemy.enemy_type)

    ai_class = AI_BEHAVIORS.get(behavior_type, BasicAI)
    return ai_class(enemy)
