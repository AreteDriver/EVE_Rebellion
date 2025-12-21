"""
Data loader module for loading JSON game data.

This module provides utilities for loading enemy, stage, and power-up
definitions from JSON files in the data/ directory structure.
"""

import json
import os
from typing import Any


def get_data_path() -> str:
    """Get the path to the data directory."""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def load_json_file(filepath: str) -> dict[str, Any]:
    """
    Load a single JSON file and return its contents.

    Args:
        filepath: Full path to the JSON file.

    Returns:
        Dictionary containing the JSON data.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_all_from_directory(directory: str) -> dict[str, dict[str, Any]]:
    """
    Load all JSON files from a directory.

    Args:
        directory: Path to the directory containing JSON files.

    Returns:
        Dictionary mapping filenames (without extension) to their parsed contents.
    """
    data = {}
    if not os.path.exists(directory):
        return data

    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            filepath = os.path.join(directory, filename)
            name = os.path.splitext(filename)[0]
            data[name] = load_json_file(filepath)

    return data


def load_enemies() -> dict[str, dict[str, Any]]:
    """
    Load all enemy definitions from data/enemies/.

    Returns:
        Dictionary mapping enemy IDs to their stats and properties.
    """
    enemies_dir = os.path.join(get_data_path(), 'enemies')
    return load_all_from_directory(enemies_dir)


def load_stages() -> dict[str, dict[str, Any]]:
    """
    Load all stage definitions from data/stages/.

    Returns:
        Dictionary mapping stage IDs to their configuration.
    """
    stages_dir = os.path.join(get_data_path(), 'stages')
    return load_all_from_directory(stages_dir)


def load_powerups() -> dict[str, dict[str, Any]]:
    """
    Load all power-up definitions from data/powerups/.

    Returns:
        Dictionary mapping power-up IDs to their effects and properties.
    """
    powerups_dir = os.path.join(get_data_path(), 'powerups')
    return load_all_from_directory(powerups_dir)


def load_all_game_data() -> dict[str, dict[str, dict[str, Any]]]:
    """
    Load all game data (enemies, stages, power-ups) at once.

    Returns:
        Dictionary with 'enemies', 'stages', and 'powerups' keys,
        each containing the respective loaded data.
    """
    return {
        'enemies': load_enemies(),
        'stages': load_stages(),
        'powerups': load_powerups()
    }


if __name__ == "__main__":
    # Sample usage demonstrating the loader functionality
    print("Loading game data...")
    print("=" * 50)

    # Load all data at once
    all_data = load_all_game_data()

    # Display loaded enemies
    print("\n--- Enemies ---")
    enemies = all_data['enemies']
    if enemies:
        for enemy_id, enemy_data in enemies.items():
            name = enemy_data.get('name', enemy_id)
            health = enemy_data.get('health', 'N/A')
            print(f"  {enemy_id}: {name} (Health: {health})")
    else:
        print("  No enemy data found.")

    # Display loaded stages
    print("\n--- Stages ---")
    stages = all_data['stages']
    if stages:
        for stage_id, stage_data in stages.items():
            name = stage_data.get('name', stage_id)
            waves = stage_data.get('waves', 'N/A')
            print(f"  {stage_id}: {name} (Waves: {waves})")
    else:
        print("  No stage data found.")

    # Display loaded power-ups
    print("\n--- Power-ups ---")
    powerups = all_data['powerups']
    if powerups:
        for powerup_id, powerup_data in powerups.items():
            name = powerup_data.get('name', powerup_id)
            effect = powerup_data.get('effect', 'N/A')
            print(f"  {powerup_id}: {name} (Effect: {effect})")
    else:
        print("  No power-up data found.")

    print("\n" + "=" * 50)
    print("Data loading complete.")
