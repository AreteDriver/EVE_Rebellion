"""Tests for wave pattern system"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wave_patterns import (  # noqa: E402
    WAVE_PATTERNS,
    AmbushPattern,
    LinearPattern,
    PincerPattern,
    ScreenClearPattern,
    SinePattern,
    SpawnPoint,
    SpiralPattern,
    WavePatternManager,
)

ENEMY_TYPES = ["executioner", "punisher", "rifter"]


class TestSpawnPoint:
    def test_defaults(self):
        sp = SpawnPoint(x=100, y=200)
        assert sp.vx == 0.0
        assert sp.vy == 2.0
        assert sp.delay == 0
        assert sp.enemy_type is None


class TestWavePatternRegistry:
    def test_all_patterns_registered(self):
        expected = {"linear", "sine", "spiral", "ambush", "pincer", "screen_clear"}
        assert set(WAVE_PATTERNS.keys()) == expected


class TestLinearPattern:
    def test_generates_correct_count(self):
        pattern = LinearPattern()
        points = pattern.generate(5, ENEMY_TYPES)
        assert len(points) == 5

    def test_all_points_have_enemy_type(self):
        pattern = LinearPattern()
        points = pattern.generate(4, ENEMY_TYPES)
        for p in points:
            assert p.enemy_type in ENEMY_TYPES


class TestSinePattern:
    def test_generates_correct_count(self):
        pattern = SinePattern()
        points = pattern.generate(8, ENEMY_TYPES)
        assert len(points) == 8

    def test_staggered_delays(self):
        pattern = SinePattern()
        points = pattern.generate(5, ENEMY_TYPES)
        delays = [p.delay for p in points]
        assert delays == sorted(delays)


class TestSpiralPattern:
    def test_generates_correct_count(self):
        pattern = SpiralPattern()
        points = pattern.generate(6, ENEMY_TYPES)
        assert len(points) == 6


class TestAmbushPattern:
    def test_generates_correct_count(self):
        pattern = AmbushPattern()
        points = pattern.generate(12, ENEMY_TYPES)
        assert len(points) == 12

    def test_small_count(self):
        pattern = AmbushPattern()
        points = pattern.generate(3, ENEMY_TYPES)
        assert len(points) == 3


class TestPincerPattern:
    def test_generates_correct_count(self):
        pattern = PincerPattern()
        points = pattern.generate(8, ENEMY_TYPES)
        assert len(points) == 8

    def test_two_groups_from_opposite_sides(self):
        pattern = PincerPattern(screen_width=800)
        points = pattern.generate(6, ENEMY_TYPES)
        left = [p for p in points if p.x < 0]
        right = [p for p in points if p.x > 800]
        assert len(left) == 3
        assert len(right) == 3


class TestScreenClearPattern:
    def test_generates_correct_count(self):
        pattern = ScreenClearPattern()
        points = pattern.generate(10, ENEMY_TYPES)
        assert len(points) == 10

    def test_slow_velocity(self):
        pattern = ScreenClearPattern()
        points = pattern.generate(5, ENEMY_TYPES)
        for p in points:
            assert p.vy <= 2.0


class TestWavePatternManager:
    def setup_method(self):
        self.mgr = WavePatternManager(screen_width=800, screen_height=700)

    def test_get_pattern_by_name(self):
        p = self.mgr.get_pattern("linear")
        assert isinstance(p, LinearPattern)

    def test_get_pattern_invalid(self):
        assert self.mgr.get_pattern("nonexistent") is None

    def test_generate_wave(self):
        points = self.mgr.generate_wave("sine", 5, ENEMY_TYPES)
        assert len(points) == 5
        assert self.mgr.last_pattern == "sine"

    def test_generate_wave_invalid_pattern(self):
        points = self.mgr.generate_wave("nonexistent", 5, ENEMY_TYPES)
        assert points == []

    def test_random_pattern_excludes(self):
        # Run multiple times to check exclusion
        for _ in range(20):
            name, _ = self.mgr.random_pattern(exclude="linear")
            assert name != "linear"

    def test_generate_random_wave(self):
        name, points = self.mgr.generate_random_wave(6, ENEMY_TYPES)
        assert name in WAVE_PATTERNS
        assert len(points) == 6

    def test_pattern_for_early_waves(self):
        pattern = self.mgr.get_pattern_for_wave(1, 1)
        assert pattern == "linear"

    def test_pattern_for_mid_waves(self):
        pattern = self.mgr.get_pattern_for_wave(3, 1)
        assert pattern in ["linear", "sine"]

    def test_pattern_for_late_waves(self):
        pattern = self.mgr.get_pattern_for_wave(9, 1)
        assert pattern in ["sine", "spiral", "ambush", "pincer"]
