"""Tests for ship roster system"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ship_roster import ShipRoster  # noqa: E402


class TestShipRosterDefaults:
    """Test ShipRoster with default config (no JSON file)."""

    def setup_method(self):
        self.roster = ShipRoster(config_path="/tmp/nonexistent_ship_roster.json")

    def test_default_unlocks(self):
        assert self.roster.is_ship_unlocked("rifter")
        assert self.roster.is_ship_unlocked("executioner")

    def test_locked_ship(self):
        assert not self.roster.is_ship_unlocked("wolf")

    def test_get_ship_by_id(self):
        ship = self.roster.get_ship("rifter")
        assert ship is not None
        assert ship["name"] == "Rifter"

    def test_get_nonexistent_ship(self):
        assert self.roster.get_ship("nonexistent") is None

    def test_get_faction_ships(self):
        minmatar = self.roster.get_faction_ships("minmatar")
        assert len(minmatar) >= 2  # At least rifter and wolf

    def test_get_faction_ships_unknown_faction(self):
        ships = self.roster.get_faction_ships("jove")
        assert ships == []

    def test_unlock_ship(self):
        self.roster.unlock_ship("wolf")
        assert self.roster.is_ship_unlocked("wolf")

    def test_get_ship_stats(self):
        stats = self.roster.get_ship_stats("rifter")
        assert "hull" in stats
        assert "speed" in stats
        assert stats["hull"] > 0

    def test_get_ship_stats_unknown(self):
        stats = self.roster.get_ship_stats("nonexistent")
        assert stats["hull"] == 100  # Defaults

    def test_get_type_id(self):
        type_id = self.roster.get_type_id("rifter")
        assert type_id == 587

    def test_get_all_type_ids(self):
        ids = self.roster.get_all_type_ids()
        assert len(ids) > 0
        assert 587 in ids

    def test_get_playable_ships_unlocked_only(self):
        ships = self.roster.get_playable_ships("minmatar", "minmatar_rebellion", unlocked_only=True)
        ship_ids = [s["id"] for s in ships]
        assert "rifter" in ship_ids
        assert "wolf" not in ship_ids  # locked

    def test_get_playable_ships_all(self):
        ships = self.roster.get_playable_ships(
            "minmatar", "minmatar_rebellion", unlocked_only=False
        )
        ship_ids = [s["id"] for s in ships]
        assert "rifter" in ship_ids
        assert "wolf" in ship_ids

    def test_ship_display_data(self):
        data = self.roster.get_ship_display_data("rifter")
        assert data["name"] == "Rifter"
        assert data["locked"] is False

    def test_ship_display_data_locked(self):
        data = self.roster.get_ship_display_data("wolf")
        assert data["locked"] is True

    def test_ship_display_data_unknown(self):
        data = self.roster.get_ship_display_data("nonexistent")
        assert data["name"] == "Nonexistent"
        assert data["locked"] is False

    def test_get_faction_info(self):
        info = self.roster.get_faction_info("minmatar")
        assert "name" in info
        assert "Minmatar" in info["name"]

    def test_get_ship_by_type_id(self):
        ship = self.roster.get_ship_by_type_id(587)
        assert ship is not None
        assert ship["id"] == "rifter"

    def test_get_ship_by_type_id_unknown(self):
        assert self.roster.get_ship_by_type_id(99999) is None

    def test_default_ships_always_unlocked(self):
        """Ships with unlock='default' should always return True."""
        ship = self.roster.get_ship("rifter")
        assert ship.get("unlock") == "default"
        assert self.roster.is_ship_unlocked("rifter")
