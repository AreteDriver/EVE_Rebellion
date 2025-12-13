"""Save/resume system for game state persistence.

Reads/writes game state files in the saves/ directory.
"""
import json
import os
from datetime import datetime
from pathlib import Path


def get_saves_directory():
    """Get the path to the saves directory."""
    base_dir = Path(__file__).parent.parent
    return base_dir / "saves"


def list_saves():
    """List all available save files.
    
    Returns:
        list: List of tuples (filename, metadata) for each save file.
              metadata includes timestamp and basic game info if available.
    """
    saves_dir = get_saves_directory()
    saves = []
    
    if not saves_dir.exists():
        return saves
    
    for file_path in saves_dir.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            metadata = {
                'filename': file_path.name,
                'timestamp': data.get('timestamp', 'Unknown'),
                'score': data.get('player', {}).get('score', 0),
                'stage': data.get('game', {}).get('current_stage', 0),
                'difficulty': data.get('game', {}).get('difficulty', 'normal')
            }
            saves.append((file_path.name, metadata))
        except (json.JSONDecodeError, IOError):
            # Include file but with minimal metadata if we can't read it
            saves.append((file_path.name, {'filename': file_path.name, 'error': True}))
    
    return saves


def save_game(filename, player_state, game_state):
    """Save game state to a file.
    
    Args:
        filename: Name of the save file (e.g., 'save1.json').
        player_state: Dictionary containing player state data.
        game_state: Dictionary containing game state data.
    
    Returns:
        bool: True if save was successful, False otherwise.
    
    Example player_state:
        {
            'score': 1500,
            'refugees': 25,
            'total_refugees': 45,
            'shields': 80,
            'armor': 100,
            'hull': 50,
            'max_shields': 100,
            'max_armor': 100,
            'max_hull': 50,
            'rockets': 8,
            'current_ammo': 'sabot',
            'unlocked_ammo': ['sabot', 'emp'],
            'has_gyro': True,
            'has_tracking': False,
            'is_wolf': False
        }
    
    Example game_state:
        {
            'current_stage': 1,
            'current_wave': 3,
            'difficulty': 'normal'
        }
    """
    saves_dir = get_saves_directory()
    saves_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    if not safe_filename.endswith('.json'):
        safe_filename += '.json'
    
    save_path = saves_dir / safe_filename
    
    save_data = {
        'player': player_state,
        'game': game_state,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4)
        return True
    except IOError:
        return False


def load_game(filename):
    """Load game state from a file.
    
    Args:
        filename: Name of the save file (e.g., 'save1.json').
    
    Returns:
        tuple: (player_state, game_state) dictionaries, or (None, None) if load fails.
    """
    saves_dir = get_saves_directory()
    
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    save_path = saves_dir / safe_filename
    
    if not save_path.exists():
        return None, None
    
    try:
        with open(save_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        player_state = data.get('player', {})
        game_state = data.get('game', {})
        
        # Validate required fields exist
        if not player_state or not game_state:
            return None, None
        
        return player_state, game_state
    except (json.JSONDecodeError, IOError):
        return None, None


def delete_save(filename):
    """Delete a save file.
    
    Args:
        filename: Name of the save file to delete.
    
    Returns:
        bool: True if deletion was successful, False otherwise.
    """
    saves_dir = get_saves_directory()
    
    # Sanitize filename to prevent path traversal
    safe_filename = os.path.basename(filename)
    save_path = saves_dir / safe_filename
    
    if not save_path.exists():
        return False
    
    try:
        save_path.unlink()
        return True
    except IOError:
        return False


class SaveManager:
    """Manager class for save/load operations.
    
    Provides a convenient interface for game state persistence.
    
    Attributes:
        current_slot (str): Currently selected save slot filename.
    """
    
    def __init__(self):
        """Initialize the save manager."""
        self.current_slot = 'save1.json'
    
    def get_saves(self):
        """Get list of all available saves.
        
        Returns:
            list: List of (filename, metadata) tuples.
        """
        return list_saves()
    
    def select_slot(self, filename):
        """Select a save slot for subsequent operations.
        
        Args:
            filename: Name of the save file to select.
        """
        self.current_slot = os.path.basename(filename)
        if not self.current_slot.endswith('.json'):
            self.current_slot += '.json'
    
    def save(self, player_state, game_state):
        """Save game to the current slot.
        
        Args:
            player_state: Dictionary containing player state.
            game_state: Dictionary containing game state.
        
        Returns:
            bool: True if save was successful.
        """
        return save_game(self.current_slot, player_state, game_state)
    
    def load(self):
        """Load game from the current slot.
        
        Returns:
            tuple: (player_state, game_state) or (None, None) if load fails.
        """
        return load_game(self.current_slot)
    
    def delete(self):
        """Delete the current slot save file.
        
        Returns:
            bool: True if deletion was successful.
        """
        return delete_save(self.current_slot)
    
    def has_save(self, filename=None):
        """Check if a save file exists.
        
        Args:
            filename: Optional filename to check. Uses current_slot if None.
        
        Returns:
            bool: True if save file exists.
        """
        if filename is None:
            filename = self.current_slot
        
        safe_filename = os.path.basename(filename)
        save_path = get_saves_directory() / safe_filename
        return save_path.exists()
    
    def extract_player_state(self, player):
        """Extract state from a Player object for saving.
        
        Args:
            player: Player sprite object from sprites.py.
        
        Returns:
            dict: Player state dictionary suitable for save_game().
        """
        return {
            'score': getattr(player, 'score', 0),
            'refugees': getattr(player, 'refugees', 0),
            'total_refugees': getattr(player, 'total_refugees', 0),
            'shields': getattr(player, 'shields', 100),
            'armor': getattr(player, 'armor', 100),
            'hull': getattr(player, 'hull', 50),
            'max_shields': getattr(player, 'max_shields', 100),
            'max_armor': getattr(player, 'max_armor', 100),
            'max_hull': getattr(player, 'max_hull', 50),
            'rockets': getattr(player, 'rockets', 10),
            'current_ammo': getattr(player, 'current_ammo', 'sabot'),
            'unlocked_ammo': list(getattr(player, 'unlocked_ammo', ['sabot'])),
            'has_gyro': getattr(player, 'has_gyro', False),
            'has_tracking': getattr(player, 'has_tracking', False),
            'is_wolf': getattr(player, 'is_wolf', False)
        }
    
    def apply_player_state(self, player, state):
        """Apply loaded state to a Player object.
        
        Args:
            player: Player sprite object to update.
            state: Player state dictionary from load_game().
        
        Returns:
            bool: True if state was successfully applied.
        """
        if not state:
            return False
        
        try:
            # Only set attributes if they exist on the player object
            for attr, default in [
                ('score', 0),
                ('refugees', 0),
                ('total_refugees', 0),
                ('shields', 100),
                ('armor', 100),
                ('hull', 50),
                ('max_shields', 100),
                ('max_armor', 100),
                ('max_hull', 50),
                ('rockets', 10),
                ('current_ammo', 'sabot'),
                ('unlocked_ammo', ['sabot']),
                ('has_gyro', False),
                ('has_tracking', False),
            ]:
                if hasattr(player, attr):
                    value = state.get(attr, default)
                    # Ensure unlocked_ammo is always a list
                    if attr == 'unlocked_ammo':
                        value = list(value)
                    setattr(player, attr, value)
            # Handle wolf upgrade specially since it affects ship appearance
            if state.get('is_wolf', False) and not getattr(player, 'is_wolf', False):
                if hasattr(player, 'upgrade_to_wolf'):
                    player.upgrade_to_wolf()
                elif hasattr(player, 'is_wolf'):
                    player.is_wolf = True
            return True
        except (AttributeError, TypeError):
            return False
