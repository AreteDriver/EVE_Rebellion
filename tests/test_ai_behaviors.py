"""Tests for AI behavior system"""

import os
import sys
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pygame before importing
pygame_mock = MagicMock()
sys.modules["pygame"] = pygame_mock

from ai_behaviors import (  # noqa: E402
    AI_BASIC,
    AI_BEHAVIORS,
    AI_KAMIKAZE,
    AI_SNIPER,
    AI_SPAWNER,
    AI_TANK,
    AI_WEAVER,
    AIState,
    BasicAI,
    KamikazeAI,
    SniperAI,
    SpawnerAI,
    TankAI,
    WeaverAI,
    get_ai_for_enemy,
)


def _make_enemy(speed=2.0, x=400, y=100, enemy_type="rifter"):
    """Create a mock enemy for testing."""
    enemy = MagicMock()
    enemy.speed = speed
    enemy.rect = MagicMock()
    enemy.rect.centerx = x
    enemy.rect.centery = y
    enemy.enemy_type = enemy_type
    return enemy


class TestAIState:
    def test_default_state(self):
        state = AIState()
        assert state.timer == 0.0
        assert state.phase == "idle"
        assert state.target_x == 0.0


class TestAIBehaviorRegistry:
    def test_all_behaviors_registered(self):
        assert AI_BASIC in AI_BEHAVIORS
        assert AI_KAMIKAZE in AI_BEHAVIORS
        assert AI_WEAVER in AI_BEHAVIORS
        assert AI_SNIPER in AI_BEHAVIORS
        assert AI_SPAWNER in AI_BEHAVIORS
        assert AI_TANK in AI_BEHAVIORS

    def test_registry_maps_to_classes(self):
        assert AI_BEHAVIORS[AI_BASIC] is BasicAI
        assert AI_BEHAVIORS[AI_KAMIKAZE] is KamikazeAI
        assert AI_BEHAVIORS[AI_TANK] is TankAI


class TestGetAIForEnemy:
    def test_known_enemy_types(self):
        assert get_ai_for_enemy("executioner") == AI_BASIC
        assert get_ai_for_enemy("punisher") == AI_TANK
        assert get_ai_for_enemy("drone") == AI_KAMIKAZE
        assert get_ai_for_enemy("tormentor") == AI_SNIPER
        assert get_ai_for_enemy("crucifier") == AI_WEAVER
        assert get_ai_for_enemy("harbinger") == AI_SPAWNER

    def test_unknown_enemy_defaults_to_basic(self):
        assert get_ai_for_enemy("nonexistent_ship") == AI_BASIC

    def test_gallente_drone_boats_are_spawners(self):
        assert get_ai_for_enemy("tristan") == AI_SPAWNER
        assert get_ai_for_enemy("vexor") == AI_SPAWNER
        assert get_ai_for_enemy("dominix") == AI_SPAWNER

    def test_caldari_missile_ships_are_snipers(self):
        assert get_ai_for_enemy("kestrel") == AI_SNIPER
        assert get_ai_for_enemy("caracal") == AI_SNIPER
        assert get_ai_for_enemy("raven") == AI_SNIPER


class TestBasicAI:
    def test_returns_three_values(self):
        enemy = _make_enemy()
        ai = BasicAI(enemy)
        result = ai.update((400, 500))
        assert len(result) == 3

    def test_moves_downward(self):
        enemy = _make_enemy(speed=2.0)
        ai = BasicAI(enemy)
        vx, vy, _ = ai.update((400, 500))
        assert vy > 0

    def test_shoots_when_player_below_and_aligned(self):
        enemy = _make_enemy(x=400, y=100)
        ai = BasicAI(enemy)
        _, _, should_shoot = ai.update((400, 500))
        assert should_shoot is True

    def test_no_shoot_when_player_above(self):
        enemy = _make_enemy(x=400, y=500)
        ai = BasicAI(enemy)
        _, _, should_shoot = ai.update((400, 100))
        assert should_shoot is False

    def test_fire_rate_modifier_default(self):
        enemy = _make_enemy()
        ai = BasicAI(enemy)
        assert ai.get_fire_rate_modifier() == 1.0


class TestKamikazeAI:
    def test_initial_phase_is_approach(self):
        enemy = _make_enemy()
        ai = KamikazeAI(enemy)
        assert ai.state.phase == "approach"

    def test_never_shoots(self):
        enemy = _make_enemy(x=400, y=200)
        ai = KamikazeAI(enemy)
        # Advance past approach phase
        ai.state.phase = "dive"
        ai.dive_speed = enemy.speed
        _, _, should_shoot = ai.update((400, 500))
        assert should_shoot is False

    def test_fire_rate_is_zero(self):
        enemy = _make_enemy()
        ai = KamikazeAI(enemy)
        assert ai.get_fire_rate_modifier() == 0.0

    def test_approach_phase_moves_down(self):
        enemy = _make_enemy(x=400, y=50, speed=3.0)
        ai = KamikazeAI(enemy)
        vx, vy, _ = ai.update((400, 500))
        assert vy > 0
        assert vx == 0.0

    def test_dive_accelerates(self):
        enemy = _make_enemy(x=400, y=200, speed=2.0)
        ai = KamikazeAI(enemy)
        ai.state.phase = "dive"
        ai.dive_speed = 2.0
        ai.update((400, 500), dt=1 / 60)
        assert ai.dive_speed > 2.0
        assert ai.dive_speed <= ai.max_dive_speed


class TestSniperAI:
    def test_fire_rate_modifier_slow(self):
        enemy = _make_enemy()
        ai = SniperAI(enemy)
        assert ai.get_fire_rate_modifier() == 0.4

    def test_backs_off_when_too_close(self):
        enemy = _make_enemy(x=400, y=400)
        ai = SniperAI(enemy)
        # Player very close
        _, vy, _ = ai.update((400, 450))
        assert vy < 0  # Should retreat

    def test_approaches_when_too_far(self):
        enemy = _make_enemy(x=400, y=50)
        ai = SniperAI(enemy)
        _, vy, _ = ai.update((400, 600))
        assert vy > 0

    def test_stays_in_bounds_left(self):
        enemy = _make_enemy(x=30, y=200)
        ai = SniperAI(enemy)
        vx, _, _ = ai.update((400, 500))
        assert vx >= 0  # Should move right


class TestSpawnerAI:
    def test_spawn_queue_initially_empty(self):
        enemy = _make_enemy()
        ai = SpawnerAI(enemy)
        assert len(ai.spawn_queue) == 0

    def test_spawns_after_cooldown(self):
        enemy = _make_enemy(x=400, y=100)
        ai = SpawnerAI(enemy)
        # Simulate enough time passing
        ai.state.timer = 10.0
        ai.last_spawn = 0.0
        ai.update((400, 500), dt=1 / 60)
        assert len(ai.spawn_queue) == 1
        assert ai.children_spawned == 1

    def test_get_spawn_queue_clears(self):
        enemy = _make_enemy(x=400, y=100)
        ai = SpawnerAI(enemy)
        ai.spawn_queue.append({"type": "drone", "x": 400, "y": 130})
        queue = ai.get_spawn_queue()
        assert len(queue) == 1
        assert len(ai.spawn_queue) == 0

    def test_respects_max_children(self):
        enemy = _make_enemy(x=400, y=100)
        ai = SpawnerAI(enemy)
        ai.children_spawned = ai.max_children
        ai.state.timer = 100.0
        ai.last_spawn = 0.0
        ai.update((400, 500), dt=1 / 60)
        assert len(ai.spawn_queue) == 0


class TestTankAI:
    def test_fire_rate_modifier_fast(self):
        enemy = _make_enemy()
        ai = TankAI(enemy)
        assert ai.get_fire_rate_modifier() == 1.5

    def test_advances_slowly(self):
        enemy = _make_enemy(speed=3.0)
        ai = TankAI(enemy)
        _, vy, _ = ai.update((400, 500))
        assert vy > 0
        assert vy < enemy.speed  # Slower than full speed

    def test_suppressive_fire_when_in_range(self):
        enemy = _make_enemy(x=400, y=200)
        ai = TankAI(enemy)
        _, _, should_shoot = ai.update((400, 500))
        assert should_shoot is True


class TestWeaverAI:
    def test_weaves_without_bullets(self):
        enemy = _make_enemy(x=400, y=200)
        ai = WeaverAI(enemy)
        vx, vy, _ = ai.update((400, 500), bullets=None)
        assert vy > 0

    def test_dodges_nearby_bullet(self):
        enemy = _make_enemy(x=400, y=200)
        ai = WeaverAI(enemy)
        bullet = MagicMock()
        bullet.rect.centerx = 410
        bullet.rect.centery = 150  # Above enemy, approaching
        vx, vy, should_shoot = ai.update((400, 500), bullets=[bullet])
        # Should dodge and not shoot
        assert abs(vx) > 0
        assert should_shoot is False
