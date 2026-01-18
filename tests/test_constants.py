"""Tests for game constants"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pygame before importing constants
pygame_mock = type(sys)('pygame')
pygame_mock.K_1 = 49
pygame_mock.K_2 = 50
pygame_mock.K_3 = 51
pygame_mock.K_4 = 52
pygame_mock.K_5 = 53
sys.modules['pygame'] = pygame_mock

from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS,
    DIFFICULTY_SETTINGS, AMMO_TYPES, ENEMY_STATS,
    STAGES_MINMATAR, STAGES_AMARR, UPGRADE_COSTS
)


class TestDisplayConstants:
    """Test display-related constants"""

    def test_screen_dimensions(self):
        """Test screen dimensions are reasonable"""
        assert SCREEN_WIDTH > 0
        assert SCREEN_HEIGHT > 0
        assert SCREEN_WIDTH >= 600
        assert SCREEN_HEIGHT >= 600

    def test_fps(self):
        """Test FPS is reasonable"""
        assert FPS > 0
        assert FPS <= 144


class TestDifficultySettings:
    """Test difficulty configuration"""

    def test_all_difficulties_exist(self):
        """Test all difficulty levels are defined"""
        assert 'easy' in DIFFICULTY_SETTINGS
        assert 'normal' in DIFFICULTY_SETTINGS
        assert 'hard' in DIFFICULTY_SETTINGS
        assert 'nightmare' in DIFFICULTY_SETTINGS

    def test_difficulty_has_required_keys(self):
        """Test each difficulty has required settings"""
        required_keys = ['enemy_health_mult', 'enemy_damage_mult', 'powerup_chance']
        for difficulty in DIFFICULTY_SETTINGS.values():
            for key in required_keys:
                assert key in difficulty

    def test_difficulty_scaling(self):
        """Test difficulty scales correctly (easy < normal < hard < nightmare)"""
        assert DIFFICULTY_SETTINGS['easy']['enemy_health_mult'] < DIFFICULTY_SETTINGS['normal']['enemy_health_mult']
        assert DIFFICULTY_SETTINGS['normal']['enemy_health_mult'] < DIFFICULTY_SETTINGS['hard']['enemy_health_mult']
        assert DIFFICULTY_SETTINGS['hard']['enemy_health_mult'] < DIFFICULTY_SETTINGS['nightmare']['enemy_health_mult']


class TestAmmoTypes:
    """Test ammo configuration"""

    def test_all_ammo_types_exist(self):
        """Test all ammo types are defined"""
        assert 'sabot' in AMMO_TYPES
        assert 'emp' in AMMO_TYPES
        assert 'plasma' in AMMO_TYPES
        assert 'fusion' in AMMO_TYPES
        assert 'barrage' in AMMO_TYPES

    def test_ammo_has_required_keys(self):
        """Test each ammo type has required settings"""
        required_keys = ['name', 'color', 'shield_mult', 'armor_mult']
        for ammo in AMMO_TYPES.values():
            for key in required_keys:
                assert key in ammo

    def test_emp_is_anti_shield(self):
        """Test EMP is effective against shields"""
        assert AMMO_TYPES['emp']['shield_mult'] > AMMO_TYPES['emp']['armor_mult']

    def test_plasma_is_anti_armor(self):
        """Test Plasma is effective against armor"""
        assert AMMO_TYPES['plasma']['armor_mult'] > AMMO_TYPES['plasma']['shield_mult']


class TestEnemyStats:
    """Test enemy configuration"""

    def test_basic_enemies_exist(self):
        """Test basic enemy types are defined"""
        assert 'executioner' in ENEMY_STATS
        assert 'punisher' in ENEMY_STATS

    def test_enemy_has_required_stats(self):
        """Test enemies have required stats"""
        required_keys = ['shields', 'armor', 'hull', 'speed', 'score']
        for enemy_name, enemy in ENEMY_STATS.items():
            for key in required_keys:
                assert key in enemy, f"{enemy_name} missing {key}"

    def test_enemy_health_positive(self):
        """Test all enemies have positive health values"""
        for enemy_name, enemy in ENEMY_STATS.items():
            total_health = enemy['shields'] + enemy['armor'] + enemy['hull']
            assert total_health > 0, f"{enemy_name} has no health"


class TestStages:
    """Test stage configuration"""

    def test_minmatar_campaign_has_stages(self):
        """Test Minmatar campaign has stages"""
        assert len(STAGES_MINMATAR) >= 5

    def test_amarr_campaign_has_stages(self):
        """Test Amarr campaign has stages"""
        assert len(STAGES_AMARR) >= 5

    def test_stages_have_required_keys(self):
        """Test stages have required configuration"""
        required_keys = ['name', 'waves', 'enemies']
        for stage in STAGES_MINMATAR:
            for key in required_keys:
                assert key in stage


class TestUpgrades:
    """Test upgrade configuration"""

    def test_upgrades_have_costs(self):
        """Test all upgrades have positive costs"""
        for upgrade, cost in UPGRADE_COSTS.items():
            assert cost > 0, f"{upgrade} has invalid cost"

    def test_wolf_upgrade_exists(self):
        """Test Wolf ship upgrade exists"""
        assert 'wolf_upgrade' in UPGRADE_COSTS
