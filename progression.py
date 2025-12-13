"""
Progression and save system for Minmatar Rebellion.

Tracks player progression across play sessions including:
- Skill points earned
- Unlocked ships
- Purchased upgrades
- Game statistics
"""

import json
import os
from typing import Dict, List, Any

# Save file location
SAVE_FILE = os.path.expanduser('~/.minmatar_rebellion_save.json')


def load_progress() -> Dict[str, Any]:
    """
    Load player progression data from save file.
    
    Returns:
        Dictionary containing progression data with default values if file doesn't exist.
    """
    default_data = {
        'total_sp': 0,
        'purchased_upgrades': [],
        'unlocked_ships': [],
        'wolf_unlocked': False,
        'jaguar_unlocked': False,
        'total_kills': 0,
        'highest_stage': 0
    }
    
    if not os.path.exists(SAVE_FILE):
        return default_data
    
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Merge with defaults to ensure all keys exist
        for key, value in default_data.items():
            if key not in data:
                data[key] = value
        return data
    except (json.JSONDecodeError, IOError):
        return default_data


def save_progress(sp: int = 0, unlocked_ships: List[str] = None,
                 wolf_unlocked: bool = False, jaguar_unlocked: bool = False,
                 total_kills: int = 0, highest_stage: int = 0) -> None:
    """
    Save player progression data to save file.
    
    Args:
        sp: Total skill points earned
        unlocked_ships: List of unlocked ship IDs
        wolf_unlocked: Whether Wolf assault frigate is unlocked
        jaguar_unlocked: Whether Jaguar assault frigate is unlocked
        total_kills: Total enemy kills across all sessions
        highest_stage: Highest stage reached
    """
    if unlocked_ships is None:
        unlocked_ships = []
    
    # Load existing data to preserve purchased_upgrades
    existing_data = load_progress()
    
    save_data = {
        'total_sp': sp,
        'unlocked_ships': unlocked_ships,
        'wolf_unlocked': wolf_unlocked,
        'jaguar_unlocked': jaguar_unlocked,
        'total_kills': total_kills,
        'highest_stage': highest_stage,
        'purchased_upgrades': existing_data.get('purchased_upgrades', [])
    }
    
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2)
    except IOError as e:
        print(f"Warning: Could not save progress: {e}")


def reset_progress() -> None:
    """Reset all progression data by removing the save file."""
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except IOError as e:
            print(f"Warning: Could not reset progress: {e}")
