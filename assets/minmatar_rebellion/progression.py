"""Skill Point persistence system for Minmatar Rebellion"""
import json
import os

SAVE_FILE = os.path.join(os.path.expanduser('~'), '.minmatar_rebellion_save.json')


def load_progress():
    """Load player progress including SP and unlocks"""
    default_data = {
        'total_sp': 0,
        'unlocked_ships': ['rifter'],  # Rifter always unlocked
        'wolf_unlocked': False,
        'jaguar_unlocked': False,
        'total_kills': 0,
        'highest_stage': 0
    }

    if not os.path.exists(SAVE_FILE):
        return default_data

    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            # Merge with defaults in case of missing keys
            for key in default_data:
                if key not in data:
                    data[key] = default_data[key]
            return data
    except Exception as e:
        print(f"Error loading save: {e}")
        return default_data


def save_progress(sp, unlocked_ships, wolf_unlocked, jaguar_unlocked, total_kills, highest_stage):
    """Save player progress"""
    data = {
        'total_sp': sp,
        'unlocked_ships': unlocked_ships,
        'wolf_unlocked': wolf_unlocked,
        'jaguar_unlocked': jaguar_unlocked,
        'total_kills': total_kills,
        'highest_stage': highest_stage
    }

    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving progress: {e}")
        return False


def add_sp(amount):
    """Add SP to the player's total"""
    data = load_progress()
    data['total_sp'] += amount
    save_progress(
        data['total_sp'],
        data['unlocked_ships'],
        data['wolf_unlocked'],
        data['jaguar_unlocked'],
        data['total_kills'],
        data['highest_stage']
    )
    return data['total_sp']


def unlock_ship(ship_name):
    """Unlock a T2 ship"""
    data = load_progress()

    if ship_name == 'wolf':
        data['wolf_unlocked'] = True
        if 'wolf' not in data['unlocked_ships']:
            data['unlocked_ships'].append('wolf')
    elif ship_name == 'jaguar':
        data['jaguar_unlocked'] = True
        if 'jaguar' not in data['unlocked_ships']:
            data['unlocked_ships'].append('jaguar')

    save_progress(
        data['total_sp'],
        data['unlocked_ships'],
        data['wolf_unlocked'],
        data['jaguar_unlocked'],
        data['total_kills'],
        data['highest_stage']
    )
    return True


def can_unlock_ship(ship_name, sp):
    """Check if player has enough SP to unlock a ship"""
    from constants import SP_UNLOCK_THRESHOLD

    data = load_progress()

    if ship_name == 'wolf':
        return sp >= SP_UNLOCK_THRESHOLD and not data['wolf_unlocked']
    elif ship_name == 'jaguar':
        return sp >= SP_UNLOCK_THRESHOLD and not data['jaguar_unlocked']

    return False


def get_sp_progress():
    """Get current SP and progress toward next unlock"""
    from constants import SP_UNLOCK_THRESHOLD

    data = load_progress()
    sp = data['total_sp']

    # Find next unlock
    if not data['wolf_unlocked']:
        return sp, SP_UNLOCK_THRESHOLD, 'Wolf'
    elif not data['jaguar_unlocked']:
        return sp, SP_UNLOCK_THRESHOLD, 'Jaguar'
    else:
        return sp, 0, 'All ships unlocked!'


if __name__ == "__main__":
    # Test the system
    print("Testing SP persistence...")

    # Load
    data = load_progress()
    print(f"Current SP: {data['total_sp']}")
    print(f"Unlocked ships: {data['unlocked_ships']}")

    # Add some SP
    new_sp = add_sp(50)
    print(f"Added 50 SP, now have: {new_sp}")

    # Check unlock status
    print(f"Can unlock Wolf: {can_unlock_ship('wolf', new_sp)}")
    print(f"Can unlock Jaguar: {can_unlock_ship('jaguar', new_sp)}")

    print(f"Save file location: {SAVE_FILE}")
