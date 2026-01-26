"""Tests for the Berserk scoring system"""
import os
import sys
from unittest.mock import MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock pygame before importing berserk_system
pygame_mock = MagicMock()
pygame_mock.Surface = MagicMock
pygame_mock.font = MagicMock()
pygame_mock.font.Font = MagicMock
sys.modules['pygame'] = pygame_mock

from berserk_system import BerserkSystem  # noqa: E402


class TestBerserkSystem:
    """Test the BerserkSystem class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.berserk = BerserkSystem()

    def test_initial_state(self):
        """Test initial state of BerserkSystem"""
        assert self.berserk.total_score == 0
        assert self.berserk.session_score == 0
        assert self.berserk.current_multiplier == 1.0
        assert self.berserk.total_kills == 0

    def test_calculate_multiplier_extreme(self):
        """Test extreme close range multiplier (0-80 pixels)"""
        player_pos = (100, 100)
        enemy_pos = (150, 100)  # 50 pixels away
        multiplier, range_name = self.berserk.calculate_multiplier(player_pos, enemy_pos)
        assert multiplier == 5.0
        assert range_name == 'EXTREME'

    def test_calculate_multiplier_close(self):
        """Test close range multiplier (80-150 pixels)"""
        player_pos = (100, 100)
        enemy_pos = (200, 100)  # 100 pixels away
        multiplier, range_name = self.berserk.calculate_multiplier(player_pos, enemy_pos)
        assert multiplier == 3.0
        assert range_name == 'CLOSE'

    def test_calculate_multiplier_medium(self):
        """Test medium range multiplier (150-250 pixels)"""
        player_pos = (100, 100)
        enemy_pos = (300, 100)  # 200 pixels away
        multiplier, range_name = self.berserk.calculate_multiplier(player_pos, enemy_pos)
        assert multiplier == 1.5
        assert range_name == 'MEDIUM'

    def test_calculate_multiplier_far(self):
        """Test far range multiplier (250-400 pixels)"""
        player_pos = (100, 100)
        enemy_pos = (400, 100)  # 300 pixels away
        multiplier, range_name = self.berserk.calculate_multiplier(player_pos, enemy_pos)
        assert multiplier == 1.0
        assert range_name == 'FAR'

    def test_calculate_multiplier_very_far(self):
        """Test very far range multiplier (400+ pixels)"""
        player_pos = (100, 100)
        enemy_pos = (600, 100)  # 500 pixels away
        multiplier, range_name = self.berserk.calculate_multiplier(player_pos, enemy_pos)
        assert multiplier == 0.5
        assert range_name == 'VERY_FAR'

    def test_distance_thresholds(self):
        """Test that distance thresholds are correctly defined"""
        assert BerserkSystem.EXTREME_CLOSE == 80
        assert BerserkSystem.CLOSE == 150
        assert BerserkSystem.MEDIUM == 250
        assert BerserkSystem.FAR == 400
