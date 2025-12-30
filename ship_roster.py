"""
Ship Roster Manager for EVE Rebellion
Loads ships from JSON config, filters by faction/chapter, and manages unlocks.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any


class ShipRoster:
    """Manages the complete ship roster from JSON configuration."""

    def __init__(self, config_path: str = "config/ship_roster_complete.json"):
        self.config_path = Path(config_path)
        self.factions: Dict[str, Any] = {}
        self.ships: Dict[str, List[Dict]] = {}  # faction -> list of ships
        self.ships_by_id: Dict[str, Dict] = {}  # ship_id -> ship data
        self.unlocked_ships: set = set()
        self.metadata: Dict = {}

        self._load_config()
        self._index_ships()

        # Default unlocks
        self.unlocked_ships.add('rifter')
        self.unlocked_ships.add('executioner')
        self.unlocked_ships.add('kestrel')
        self.unlocked_ships.add('tristan')

    def _load_config(self):
        """Load the ship roster configuration from JSON."""
        if not self.config_path.exists():
            print(f"[ShipRoster] Config not found: {self.config_path}")
            self._create_default_config()
            return

        try:
            with open(self.config_path, 'r') as f:
                data = json.load(f)

            self.metadata = data.get('metadata', {})
            self.factions = data.get('factions', {})

            # Parse ships by faction
            ships_data = data.get('ships', {})
            for faction_id, categories in ships_data.items():
                self.ships[faction_id] = []
                for category, ship_list in categories.items():
                    if isinstance(ship_list, list):
                        for ship in ship_list:
                            ship['category'] = category
                            ship['faction'] = faction_id
                            self.ships[faction_id].append(ship)

            print(f"[ShipRoster] Loaded {sum(len(s) for s in self.ships.values())} ships from config")

        except json.JSONDecodeError as e:
            print(f"[ShipRoster] Error parsing config: {e}")
            self._create_default_config()
        except Exception as e:
            print(f"[ShipRoster] Error loading config: {e}")
            self._create_default_config()

    def _index_ships(self):
        """Create an index of ships by ID for quick lookup."""
        for faction_id, ship_list in self.ships.items():
            for ship in ship_list:
                ship_id = ship.get('id')
                if ship_id:
                    self.ships_by_id[ship_id] = ship

    def _create_default_config(self):
        """Create a minimal default config if none exists."""
        self.factions = {
            'minmatar': {'name': 'Minmatar Republic', 'color_primary': '#8B4513'},
            'amarr': {'name': 'Amarr Empire', 'color_primary': '#DAA520'},
        }
        self.ships = {
            'minmatar': [
                {'id': 'rifter', 'name': 'Rifter', 'type_id': 587, 'class': 'frigate',
                 'tier': 't1', 'stats': {'hull': 100, 'shield': 80, 'speed': 350, 'damage': 1.0},
                 'available_chapters': ['minmatar_rebellion'], 'unlock': 'default'},
                {'id': 'wolf', 'name': 'Wolf', 'type_id': 11400, 'class': 'assault_frigate',
                 'tier': 't2', 'stats': {'hull': 180, 'shield': 150, 'speed': 320, 'damage': 1.4},
                 'available_chapters': ['minmatar_rebellion'], 'unlock': 'rebellion_boss_7'},
                {'id': 'jaguar', 'name': 'Jaguar', 'type_id': 11196, 'class': 'assault_frigate',
                 'tier': 't2', 'stats': {'hull': 160, 'shield': 200, 'speed': 380, 'damage': 1.3},
                 'available_chapters': ['minmatar_rebellion'], 'unlock': 'rebellion_boss_13'},
            ],
            'amarr': [
                {'id': 'executioner', 'name': 'Executioner', 'type_id': 589, 'class': 'frigate',
                 'tier': 't1', 'stats': {'hull': 80, 'shield': 60, 'speed': 380, 'damage': 1.0},
                 'available_chapters': ['minmatar_rebellion'], 'unlock': 'default'},
            ]
        }

    def get_faction_ships(self, faction: str, chapter: Optional[str] = None) -> List[Dict]:
        """
        Get all ships for a faction, optionally filtered by chapter.

        Args:
            faction: Faction ID (e.g., 'minmatar', 'amarr')
            chapter: Optional chapter ID to filter by availability

        Returns:
            List of ship dictionaries
        """
        ships = self.ships.get(faction, [])

        if chapter:
            ships = [s for s in ships if chapter in s.get('available_chapters', [])]

        return ships

    def get_playable_ships(self, faction: str, chapter: str, unlocked_only: bool = True) -> List[Dict]:
        """
        Get ships that can be selected for play.

        Args:
            faction: Faction ID
            chapter: Chapter ID
            unlocked_only: Only return unlocked ships

        Returns:
            List of playable ship dictionaries
        """
        ships = self.get_faction_ships(faction, chapter)

        if unlocked_only:
            ships = [s for s in ships if self.is_ship_unlocked(s.get('id'))]

        # Sort by tier (t1 first, then t2)
        tier_order = {'t1': 0, 't2': 1, 't3': 2}
        ships.sort(key=lambda s: tier_order.get(s.get('tier', 't1'), 0))

        return ships

    def get_ship(self, ship_id: str) -> Optional[Dict]:
        """Get a ship by its ID."""
        return self.ships_by_id.get(ship_id)

    def get_ship_by_type_id(self, type_id: int) -> Optional[Dict]:
        """Get a ship by its EVE type ID."""
        for ship in self.ships_by_id.values():
            if ship.get('type_id') == type_id:
                return ship
        return None

    def is_ship_unlocked(self, ship_id: str) -> bool:
        """Check if a ship is unlocked."""
        ship = self.get_ship(ship_id)
        if not ship:
            return False

        # Default ships are always unlocked
        if ship.get('unlock') == 'default':
            return True

        return ship_id in self.unlocked_ships

    def unlock_ship(self, ship_id: str):
        """Unlock a ship."""
        self.unlocked_ships.add(ship_id)

    def get_faction_info(self, faction: str) -> Dict:
        """Get faction metadata."""
        return self.factions.get(faction, {})

    def get_ship_stats(self, ship_id: str) -> Dict:
        """Get the stats for a ship."""
        ship = self.get_ship(ship_id)
        if ship:
            return ship.get('stats', {})
        return {'hull': 100, 'shield': 80, 'speed': 350, 'damage': 1.0}

    def get_type_id(self, ship_id: str) -> Optional[int]:
        """Get the EVE type ID for a ship."""
        ship = self.get_ship(ship_id)
        if ship:
            return ship.get('type_id')
        return None

    def get_all_type_ids(self) -> List[int]:
        """Get all EVE type IDs for downloading assets."""
        type_ids = []
        for ship in self.ships_by_id.values():
            type_id = ship.get('type_id')
            if type_id:
                type_ids.append(type_id)
        return list(set(type_ids))

    def get_ship_options(self, faction: str, chapter: str = 'minmatar_rebellion') -> List[str]:
        """
        Get a list of ship IDs that can be displayed in ship selection.
        This is what the game uses for ship_options.
        """
        ships = self.get_playable_ships(faction, chapter, unlocked_only=False)
        return [s.get('id') for s in ships if s.get('id')]

    def get_ship_display_data(self, ship_id: str) -> Dict:
        """
        Get display data for ship selection screen.

        Returns dict with name, catchphrase, stats, tier, locked status
        """
        ship = self.get_ship(ship_id)
        if not ship:
            return {
                'name': ship_id.title(),
                'catchphrase': '',
                'stats': {'hull': 100, 'shield': 80, 'speed': 350, 'damage': 1.0},
                'tier': 't1',
                'locked': False,
                'type_id': None
            }

        return {
            'name': ship.get('name', ship_id.title()),
            'catchphrase': ship.get('catchphrase', ''),
            'stats': ship.get('stats', {}),
            'tier': ship.get('tier', 't1'),
            'locked': not self.is_ship_unlocked(ship_id),
            'type_id': ship.get('type_id'),
            'unlock': ship.get('unlock', 'default')
        }


# Singleton instance
_ship_roster: Optional[ShipRoster] = None

def get_ship_roster() -> ShipRoster:
    """Get the global ship roster instance."""
    global _ship_roster
    if _ship_roster is None:
        _ship_roster = ShipRoster()
    return _ship_roster
