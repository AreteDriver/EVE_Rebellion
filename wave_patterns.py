"""
Wave Pattern System for EVE Rebellion
Implements the 6 core wave patterns from the design doc.
"""

import math
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class SpawnPoint:
    """A point where an enemy should spawn."""
    x: float
    y: float
    vx: float = 0.0
    vy: float = 2.0
    delay: int = 0  # Frames to wait before spawning
    enemy_type: Optional[str] = None


class WavePattern:
    """Base class for wave patterns."""

    def __init__(self, screen_width: int = 800, screen_height: int = 700):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        """Generate spawn points for this pattern."""
        raise NotImplementedError


class LinearPattern(WavePattern):
    """
    LINEAR: Enemies spawn in a straight line from one edge.
    Simple, predictable, good for warming up.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []
        spacing = 50
        line_width = (num_enemies - 1) * spacing

        # Random edge selection
        edge = random.choice(['top', 'left', 'right'])

        if edge == 'top':
            start_x = (self.screen_width - line_width) // 2
            for i in range(num_enemies):
                x = start_x + i * spacing
                points.append(SpawnPoint(
                    x=x,
                    y=-30 - i * 10,  # Staggered entry
                    vx=0,
                    vy=random.uniform(2.0, 3.0),
                    delay=i * 5,
                    enemy_type=random.choice(enemy_types)
                ))
        elif edge == 'left':
            start_y = 100
            for i in range(num_enemies):
                y = start_y + i * spacing * 0.8
                points.append(SpawnPoint(
                    x=-30,
                    y=y,
                    vx=random.uniform(2.5, 3.5),
                    vy=random.uniform(0.5, 1.0),
                    delay=i * 8,
                    enemy_type=random.choice(enemy_types)
                ))
        else:  # right
            start_y = 100
            for i in range(num_enemies):
                y = start_y + i * spacing * 0.8
                points.append(SpawnPoint(
                    x=self.screen_width + 30,
                    y=y,
                    vx=random.uniform(-3.5, -2.5),
                    vy=random.uniform(0.5, 1.0),
                    delay=i * 8,
                    enemy_type=random.choice(enemy_types)
                ))

        return points


class SinePattern(WavePattern):
    """
    SINE: Enemies spawn in a sine wave pattern, weaving left and right.
    Creates a flowing, rhythmic challenge.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []
        amplitude = self.screen_width // 4
        center_x = self.screen_width // 2
        spacing_y = 40

        for i in range(num_enemies):
            phase = (i / num_enemies) * math.pi * 2
            x = center_x + amplitude * math.sin(phase)
            y = -30 - i * spacing_y

            # Velocity follows the sine curve
            vx = math.cos(phase) * 1.5
            vy = random.uniform(2.0, 2.5)

            points.append(SpawnPoint(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                delay=i * 10,
                enemy_type=random.choice(enemy_types)
            ))

        return points


class SpiralPattern(WavePattern):
    """
    SPIRAL: Enemies spawn in a spiral pattern, converging toward center.
    Creates a vortex effect, high threat from all angles.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []
        center_x = self.screen_width // 2
        center_y = self.screen_height // 3

        for i in range(num_enemies):
            # Spiral outward from center
            angle = (i / num_enemies) * math.pi * 4  # 2 full rotations
            radius = 100 + i * 20

            # Spawn position (off-screen, following spiral)
            spawn_angle = angle + math.pi  # Opposite side
            spawn_radius = max(self.screen_width, self.screen_height)

            x = center_x + spawn_radius * math.cos(spawn_angle)
            y = center_y + spawn_radius * math.sin(spawn_angle)

            # Velocity toward center with spiral motion
            target_x = center_x + radius * math.cos(angle)
            target_y = center_y + radius * math.sin(angle)

            dx = target_x - x
            dy = target_y - y
            dist = max(1, math.sqrt(dx * dx + dy * dy))

            speed = 2.5
            vx = (dx / dist) * speed
            vy = (dy / dist) * speed

            points.append(SpawnPoint(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                delay=i * 15,
                enemy_type=random.choice(enemy_types)
            ))

        return points


class AmbushPattern(WavePattern):
    """
    AMBUSH: Enemies appear suddenly from multiple directions at once.
    No warning, maximum pressure, requires quick reactions.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []

        # Distribute enemies around all edges
        edges = ['top', 'left', 'right', 'bottom', 'top_left', 'top_right']
        enemies_per_edge = max(1, num_enemies // len(edges))

        for edge_idx, edge in enumerate(edges):
            count = enemies_per_edge
            if edge_idx == len(edges) - 1:
                count = num_enemies - len(points)  # Remaining enemies

            for i in range(count):
                if len(points) >= num_enemies:
                    break

                spawn = self._get_edge_spawn(edge, i, count)
                spawn.delay = random.randint(0, 10)  # Near-simultaneous
                spawn.enemy_type = random.choice(enemy_types)
                points.append(spawn)

        return points

    def _get_edge_spawn(self, edge: str, idx: int, count: int) -> SpawnPoint:
        """Get spawn point for a specific edge."""
        if edge == 'top':
            x = random.randint(50, self.screen_width - 50)
            return SpawnPoint(x=x, y=-30, vx=0, vy=random.uniform(3.0, 4.0))
        elif edge == 'bottom':
            x = random.randint(50, self.screen_width - 50)
            return SpawnPoint(x=x, y=self.screen_height + 30, vx=0, vy=random.uniform(-3.0, -2.0))
        elif edge == 'left':
            y = random.randint(50, self.screen_height - 150)
            return SpawnPoint(x=-30, y=y, vx=random.uniform(3.0, 4.0), vy=random.uniform(0.5, 1.5))
        elif edge == 'right':
            y = random.randint(50, self.screen_height - 150)
            return SpawnPoint(x=self.screen_width + 30, y=y, vx=random.uniform(-4.0, -3.0), vy=random.uniform(0.5, 1.5))
        elif edge == 'top_left':
            return SpawnPoint(x=-30, y=-30, vx=random.uniform(2.5, 3.5), vy=random.uniform(2.5, 3.5))
        else:  # top_right
            return SpawnPoint(x=self.screen_width + 30, y=-30, vx=random.uniform(-3.5, -2.5), vy=random.uniform(2.5, 3.5))


class PincerPattern(WavePattern):
    """
    PINCER: Two groups spawn from opposite sides, closing in.
    Forces player to choose which side to deal with first.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []
        half = num_enemies // 2

        # Left group
        for i in range(half):
            y = 100 + i * 60
            points.append(SpawnPoint(
                x=-30,
                y=y,
                vx=random.uniform(2.0, 3.0),
                vy=random.uniform(0.5, 1.0),
                delay=i * 8,
                enemy_type=random.choice(enemy_types)
            ))

        # Right group
        for i in range(num_enemies - half):
            y = 100 + i * 60
            points.append(SpawnPoint(
                x=self.screen_width + 30,
                y=y,
                vx=random.uniform(-3.0, -2.0),
                vy=random.uniform(0.5, 1.0),
                delay=i * 8,
                enemy_type=random.choice(enemy_types)
            ))

        return points


class ScreenClearPattern(WavePattern):
    """
    SCREEN CLEAR: A wall of enemies fills the screen.
    Must clear all to advance. High risk, high reward.
    """

    def generate(self, num_enemies: int, enemy_types: List[str]) -> List[SpawnPoint]:
        points = []

        # Create rows that fill the screen
        cols = min(8, num_enemies)
        rows = (num_enemies + cols - 1) // cols

        col_spacing = (self.screen_width - 100) // max(1, cols - 1) if cols > 1 else 0
        row_spacing = 50
        start_x = 50

        for row in range(rows):
            for col in range(cols):
                if len(points) >= num_enemies:
                    break

                x = start_x + col * col_spacing
                y = -30 - row * row_spacing

                points.append(SpawnPoint(
                    x=x,
                    y=y,
                    vx=0,
                    vy=random.uniform(1.5, 2.0),  # Slow, wall-like advance
                    delay=row * 20,  # Row by row
                    enemy_type=random.choice(enemy_types)
                ))

        return points


# Pattern registry
WAVE_PATTERNS = {
    'linear': LinearPattern,
    'sine': SinePattern,
    'spiral': SpiralPattern,
    'ambush': AmbushPattern,
    'pincer': PincerPattern,
    'screen_clear': ScreenClearPattern,
}


class WavePatternManager:
    """Manages wave pattern selection and generation."""

    def __init__(self, screen_width: int = 800, screen_height: int = 700):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.patterns = {
            name: cls(screen_width, screen_height)
            for name, cls in WAVE_PATTERNS.items()
        }
        self.last_pattern = None

    def get_pattern(self, pattern_name: str) -> Optional[WavePattern]:
        """Get a specific pattern by name."""
        return self.patterns.get(pattern_name)

    def random_pattern(self, exclude: Optional[str] = None) -> Tuple[str, WavePattern]:
        """Get a random pattern, optionally excluding one."""
        available = [n for n in self.patterns.keys() if n != exclude]
        name = random.choice(available)
        return name, self.patterns[name]

    def generate_wave(self, pattern_name: str, num_enemies: int,
                     enemy_types: List[str]) -> List[SpawnPoint]:
        """Generate spawn points for a specific pattern."""
        pattern = self.patterns.get(pattern_name)
        if pattern:
            self.last_pattern = pattern_name
            return pattern.generate(num_enemies, enemy_types)
        return []

    def generate_random_wave(self, num_enemies: int,
                            enemy_types: List[str]) -> Tuple[str, List[SpawnPoint]]:
        """Generate a random wave pattern."""
        name, pattern = self.random_pattern(exclude=self.last_pattern)
        self.last_pattern = name
        return name, pattern.generate(num_enemies, enemy_types)

    def get_pattern_for_wave(self, wave_num: int, stage_num: int) -> str:
        """Get appropriate pattern based on wave/stage progression."""
        # Early waves use simpler patterns
        if wave_num < 3:
            return 'linear'
        elif wave_num < 5:
            return random.choice(['linear', 'sine'])
        elif wave_num < 8:
            return random.choice(['sine', 'pincer', 'spiral'])
        else:
            # Later waves can use any pattern
            patterns = ['sine', 'spiral', 'ambush', 'pincer']
            if wave_num % 5 == 0:  # Every 5th wave
                patterns.append('screen_clear')
            return random.choice(patterns)


# Singleton instance
_pattern_manager: Optional[WavePatternManager] = None


def get_wave_pattern_manager() -> WavePatternManager:
    """Get the global wave pattern manager."""
    global _pattern_manager
    if _pattern_manager is None:
        _pattern_manager = WavePatternManager()
    return _pattern_manager
