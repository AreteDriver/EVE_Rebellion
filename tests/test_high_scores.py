"""Tests for high score and achievement systems"""

import json
import os
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from high_scores import AchievementManager, HighScoreManager  # noqa: E402


class TestHighScoreManager:
    def setup_method(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.mgr = HighScoreManager()
        self.mgr.SAVE_FILE = self.tmpfile.name
        self.mgr.scores = []

    def teardown_method(self):
        os.unlink(self.tmpfile.name)

    def _add(self, score, **kwargs):
        defaults = dict(refugees=0, stage=1, wave=1, ship="Rifter", difficulty="normal")
        defaults.update(kwargs)
        return self.mgr.add_score(score, **defaults)

    def test_empty_high_score_is_zero(self):
        assert self.mgr.get_high_score() == 0

    def test_add_first_score(self):
        rank, is_new = self._add(1000)
        assert rank == 1
        assert is_new is True
        assert self.mgr.get_high_score() == 1000

    def test_scores_sorted_descending(self):
        self._add(500)
        self._add(1000)
        self._add(750)
        assert self.mgr.scores[0]["score"] == 1000
        assert self.mgr.scores[1]["score"] == 750
        assert self.mgr.scores[2]["score"] == 500

    def test_max_scores_enforced(self):
        for i in range(15):
            self._add(i * 100)
        assert len(self.mgr.scores) == self.mgr.MAX_SCORES

    def test_is_high_score_when_list_not_full(self):
        assert self.mgr.is_high_score(1) is True

    def test_is_high_score_when_list_full(self):
        for i in range(10):
            self._add((i + 1) * 1000)
        assert self.mgr.is_high_score(500) is False
        assert self.mgr.is_high_score(50000) is True

    def test_get_top_scores(self):
        for i in range(8):
            self._add((i + 1) * 100)
        top3 = self.mgr.get_top_scores(3)
        assert len(top3) == 3
        assert top3[0]["score"] == 800

    def test_clear(self):
        self._add(1000)
        self.mgr.clear()
        assert len(self.mgr.scores) == 0
        assert self.mgr.get_high_score() == 0

    def test_persistence(self):
        self._add(5000)
        # Create new manager pointing at same file
        mgr2 = HighScoreManager()
        mgr2.SAVE_FILE = self.tmpfile.name
        mgr2.load()
        assert mgr2.get_high_score() == 5000

    def test_corrupted_file_handled(self):
        with open(self.tmpfile.name, "w") as f:
            f.write("not json")
        self.mgr.load()
        assert self.mgr.scores == []


class TestAchievementManager:
    def setup_method(self):
        self.tmpfile = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmpfile.close()
        self.mgr = AchievementManager()
        self.mgr.SAVE_FILE = self.tmpfile.name
        self.mgr.unlocked = set()
        self.mgr.stats = {"total_kills": 0, "total_refugees": 0, "games_played": 0, "victories": 0}

    def teardown_method(self):
        os.unlink(self.tmpfile.name)

    def test_unlock_new_achievement(self):
        assert self.mgr.unlock("first_blood") is True
        assert self.mgr.is_unlocked("first_blood") is True

    def test_unlock_already_unlocked(self):
        self.mgr.unlock("first_blood")
        assert self.mgr.unlock("first_blood") is False

    def test_unlock_invalid_achievement(self):
        assert self.mgr.unlock("nonexistent") is False

    def test_pending_unlocks(self):
        self.mgr.unlock("first_blood")
        self.mgr.unlock("centurion")
        pending = self.mgr.get_pending_unlocks()
        assert "first_blood" in pending
        assert "centurion" in pending
        # Should be cleared
        assert len(self.mgr.get_pending_unlocks()) == 0

    def test_check_achievements_kills(self):
        stats = {"total_kills": 100, "refugees": 0, "score": 0, "stage": 0}
        unlocked = self.mgr.check_achievements(stats)
        assert "first_blood" in unlocked
        assert "centurion" in unlocked

    def test_check_achievements_refugees(self):
        stats = {"total_kills": 0, "refugees": 200, "score": 0, "stage": 0}
        unlocked = self.mgr.check_achievements(stats)
        assert "liberator" in unlocked
        assert "freedom_fighter" in unlocked

    def test_check_achievements_score(self):
        stats = {"total_kills": 0, "refugees": 0, "score": 100000, "stage": 0}
        unlocked = self.mgr.check_achievements(stats)
        assert "high_roller" in unlocked
        assert "score_master" in unlocked

    def test_check_achievements_victory(self):
        stats = {
            "total_kills": 0,
            "refugees": 0,
            "score": 0,
            "stage": 5,
            "victory": True,
            "difficulty": "normal",
            "ship": "Wolf",
        }
        unlocked = self.mgr.check_achievements(stats)
        assert "rebel_hero" in unlocked
        assert "wolf_pack" in unlocked

    def test_check_achievements_endless(self):
        stats = {
            "total_kills": 0,
            "refugees": 0,
            "score": 60000,
            "stage": 0,
            "game_mode": "endless",
            "endless_wave": 25,
            "endless_time": 700,
        }
        unlocked = self.mgr.check_achievements(stats)
        assert "endless_initiate" in unlocked
        assert "endless_warrior" in unlocked
        assert "endless_champion" in unlocked
        assert "endless_endurance" in unlocked
        assert "endless_score_50k" in unlocked

    def test_stats_accumulate(self):
        stats = {"total_kills": 50, "refugees": 10, "score": 0, "stage": 0}
        self.mgr.check_achievements(stats)
        assert self.mgr.stats["total_kills"] == 50
        assert self.mgr.stats["games_played"] == 1

    def test_get_progress(self):
        unlocked, total = self.mgr.get_progress()
        assert unlocked == 0
        assert total > 0

    def test_hidden_achievements_excluded_from_list(self):
        visible = self.mgr.get_all_achievements(include_hidden=False)
        hidden_ids = [a["id"] for a in visible if a.get("hidden")]
        assert len(hidden_ids) == 0

    def test_hidden_achievements_included_when_requested(self):
        all_achs = self.mgr.get_all_achievements(include_hidden=True)
        assert len(all_achs) == len(self.mgr.ACHIEVEMENTS)
