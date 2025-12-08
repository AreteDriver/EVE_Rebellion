"""
Player progression and save file management for Minmatar Rebellion.

This module handles saving and loading player progress including:
- Skill points (SP)
- Purchased upgrades
- Unlocked ships
- Total kills
- Highest stage reached
"""

import json
import os
from typing import List

# Default save file location
SAVE_FILE = 'player_progress.json'


def load_progress() -> dict:
    """
    Load player progress from the save file.
    
    Returns:
        Dictionary containing player progress data. Returns default values
        if save file doesn't exist or is invalid.
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
        return default_data.copy()
    
    try:
        with open(SAVE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Ensure all required fields exist
            for key, value in default_data.items():
                if key not in data:
                    data[key] = value
            return data
    except (json.JSONDecodeError, IOError):
        # If file is corrupted or can't be read, return defaults
        return default_data.copy()


def save_progress(sp: int = 0, 
                  unlocked_ships: List[str] = None,
                  wolf_unlocked: bool = False,
                  jaguar_unlocked: bool = False,
                  total_kills: int = 0,
                  highest_stage: int = 0) -> None:
    """
    Save player progress to the save file.
    
    Args:
        sp: Total skill points available
        unlocked_ships: List of unlocked ship names
        wolf_unlocked: Whether Wolf assault frigate is unlocked
        jaguar_unlocked: Whether Jaguar assault frigate is unlocked
        total_kills: Total number of enemies killed
        highest_stage: Highest stage reached
    """
    if unlocked_ships is None:
        unlocked_ships = []
    
    # Load existing data to preserve purchased_upgrades if they exist
    existing_data = load_progress()
    
    data = {
        'total_sp': sp,
        'purchased_upgrades': existing_data.get('purchased_upgrades', []),
        'unlocked_ships': unlocked_ships,
        'wolf_unlocked': wolf_unlocked,
        'jaguar_unlocked': jaguar_unlocked,
        'total_kills': total_kills,
        'highest_stage': highest_stage
    }
    
    try:
        with open(SAVE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except IOError:
        # Silently fail if we can't write (e.g., permissions issue)
        pass


def reset_progress() -> None:
    """
    Reset player progress by removing the save file.
    """
    if os.path.exists(SAVE_FILE):
        try:
            os.remove(SAVE_FILE)
        except OSError:
            pass
