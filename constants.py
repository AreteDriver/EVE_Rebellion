"""Game constants and configuration for Minmatar Rebellion"""
import pygame

# Display
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Screen shake
SHAKE_SMALL = 3
SHAKE_MEDIUM = 6
SHAKE_LARGE = 12
SHAKE_DECAY = 0.85

# Difficulty settings
DIFFICULTY_SETTINGS = {
    'easy': {
        'name': 'Easy',
        'enemy_health_mult': 0.7,
        'enemy_damage_mult': 0.7,
        'enemy_fire_rate_mult': 1.3,  # Higher = slower
        'player_damage_mult': 1.2,
        'refugee_mult': 1.5,
        'powerup_chance': 0.2
    },
    'normal': {
        'name': 'Normal',
        'enemy_health_mult': 1.0,
        'enemy_damage_mult': 1.0,
        'enemy_fire_rate_mult': 1.0,
        'player_damage_mult': 1.0,
        'refugee_mult': 1.0,
        'powerup_chance': 0.15
    },
    'hard': {
        'name': 'Hard',
        'enemy_health_mult': 1.3,
        'enemy_damage_mult': 1.3,
        'enemy_fire_rate_mult': 0.8,  # Lower = faster
        'player_damage_mult': 0.9,
        'refugee_mult': 0.8,
        'powerup_chance': 0.1
    },
    'nightmare': {
        'name': 'Nightmare',
        'enemy_health_mult': 1.6,
        'enemy_damage_mult': 1.5,
        'enemy_fire_rate_mult': 0.6,
        'player_damage_mult': 0.8,
        'refugee_mult': 0.6,
        'powerup_chance': 0.08
    }
}

# Colors - Minmatar (rust/brown/orange industrial)
COLOR_MINMATAR_HULL = (139, 90, 43)
COLOR_MINMATAR_ACCENT = (180, 100, 50)
COLOR_MINMATAR_DARK = (80, 50, 30)

# Colors - Amarr (gold/white/ornate)
COLOR_AMARR_HULL = (218, 165, 32)
COLOR_AMARR_ACCENT = (255, 215, 0)
COLOR_AMARR_DARK = (139, 117, 0)

# UI Colors
COLOR_SHIELD = (100, 150, 255)
COLOR_ARMOR = (200, 150, 100)
COLOR_HULL = (150, 150, 150)
COLOR_HUD_BG = (20, 20, 30, 200)
COLOR_TEXT = (220, 220, 220)

# Ammo types: (name, color, shield_mult, armor_mult, fire_rate_mult, description)
AMMO_TYPES = {
    'sabot': {
        'name': 'Titanium Sabot',
        'color': (180, 180, 180),
        'tracer': (200, 200, 200),
        'shield_mult': 1.0,
        'armor_mult': 1.0,
        'fire_rate': 1.0,
        'key': pygame.K_1
    },
    'emp': {
        'name': 'EMP',
        'color': (50, 150, 255),
        'tracer': (100, 180, 255),
        'shield_mult': 1.5,
        'armor_mult': 0.7,
        'fire_rate': 1.0,
        'key': pygame.K_2
    },
    'plasma': {
        'name': 'Phased Plasma',
        'color': (255, 120, 0),
        'tracer': (255, 150, 50),
        'shield_mult': 0.7,
        'armor_mult': 1.5,
        'fire_rate': 1.0,
        'key': pygame.K_3
    },
    'fusion': {
        'name': 'Fusion',
        'color': (255, 50, 50),
        'tracer': (255, 100, 100),
        'shield_mult': 1.3,
        'armor_mult': 1.3,
        'fire_rate': 0.7,
        'key': pygame.K_4
    },
    'barrage': {
        'name': 'Barrage',
        'color': (220, 200, 50),
        'tracer': (240, 220, 100),
        'shield_mult': 0.9,
        'armor_mult': 0.9,
        'fire_rate': 1.4,
        'key': pygame.K_5
    }
}

# Player stats
PLAYER_SPEED = 5
PLAYER_BASE_FIRE_RATE = 150  # ms between shots
PLAYER_ROCKET_COOLDOWN = 500  # ms between rockets
PLAYER_MAX_ROCKETS = 10
PLAYER_START_SHIELDS = 100
PLAYER_START_ARMOR = 100
PLAYER_START_HULL = 50

# Wolf upgrade bonuses
WOLF_SPEED_BONUS = 1.2
WOLF_ARMOR_BONUS = 50
WOLF_HULL_BONUS = 25

# Bullet stats
BULLET_SPEED = 12
BULLET_DAMAGE = 10
ROCKET_SPEED = 8
ROCKET_DAMAGE = 50

# Enemy stats
ENEMY_STATS = {
    'executioner': {
        'name': 'Executioner',
        'shields': 60,
        'armor': 20,
        'hull': 20,
        'speed': 2.5,
        'fire_rate': 1500,
        'score': 100,
        'size': (60, 78)  # Frigates
    },
    'punisher': {
        'name': 'Punisher',
        'shields': 30,
        'armor': 80,
        'hull': 30,
        'speed': 1.5,
        'fire_rate': 2000,
        'score': 150,
        'size': (66, 86)  # Frigates
    },
    'omen': {
        'name': 'Omen',
        'shields': 100,
        'armor': 150,
        'hull': 80,
        'speed': 1.2,
        'fire_rate': 1200,
        'score': 500,
        'size': (100, 130)  # Cruisers
    },
    'maller': {
        'name': 'Maller',
        'shields': 50,
        'armor': 250,
        'hull': 100,
        'speed': 0.8,
        'fire_rate': 1800,
        'score': 600,
        'size': (105, 135)  # Cruisers
    },
    'bestower': {
        'name': 'Bestower',
        'shields': 40,
        'armor': 100,
        'hull': 60,
        'speed': 1.0,
        'fire_rate': 0,  # Non-combat - Amarr industrial
        'score': 200,
        'refugees': 5,
        'size': (88, 150)  # Industrial
    },
    'apocalypse': {
        'name': 'Apocalypse',
        'shields': 300,
        'armor': 400,
        'hull': 200,
        'speed': 0.5,
        'fire_rate': 800,
        'score': 2000,
        'size': (130, 195),  # Battleship
        'boss': True
    },
    'abaddon': {
        'name': 'Abaddon',
        'shields': 500,
        'armor': 600,
        'hull': 300,
        'speed': 0.3,
        'fire_rate': 600,
        'score': 5000,
        'size': (160, 240),  # Battleship boss
        'boss': True
    },
    'amarr_capital': {
        'name': 'Golden Supercarrier',
        'shields': 500,
        'armor': 1500,
        'hull': 1000,
        'speed': 0.3,
        'fire_rate': 1500,
        'score': 5000,
        'size': (320, 480),  # Capital ship
        'boss': True
    },
    'machariel': {
        'name': 'Machariel',
        'shields': 200,
        'armor': 400,
        'hull': 300,
        'speed': 1.0,
        'fire_rate': 800,
        'score': 2000,
        'size': (130, 195),  # Pirate battleship
        'boss': True
    },
    'stratios': {
        'name': 'Stratios',
        'shields': 150,
        'armor': 150,
        'hull': 100,
        'speed': 1.2,
        'fire_rate': 1000,
        'score': 1500,
        'size': (98, 130),  # Cruiser-size
        'boss': True
    },
    # New enemy types
    'drone': {
        'name': 'Combat Drone',
        'shields': 15,
        'armor': 10,
        'hull': 5,
        'speed': 4.0,
        'fire_rate': 2500,
        'score': 25,
        'size': (32, 32),  # Drones
        'behavior': 'swarm'
    },
    'bomber': {
        'name': 'Purifier Bomber',
        'shields': 40,
        'armor': 60,
        'hull': 40,
        'speed': 0.8,
        'fire_rate': 3000,
        'score': 300,
        'size': (75, 105),  # Bombers
        'behavior': 'bomber'
    },
    'interceptor': {
        'name': 'Crusader Interceptor',
        'shields': 80,
        'armor': 15,
        'hull': 15,
        'speed': 5.0,
        'fire_rate': 1000,
        'score': 200,
        'size': (48, 66),  # Interceptors
        'behavior': 'aggressive'
    },
    'coercer': {
        'name': 'Coercer',
        'shields': 45,
        'armor': 45,
        'hull': 25,
        'speed': 2.0,
        'fire_rate': 1200,
        'score': 125,
        'size': (64, 84),  # Destroyers
        'behavior': 'strafe'
    },
    'harbinger': {
        'name': 'Harbinger',
        'shields': 200,
        'armor': 300,
        'hull': 150,
        'speed': 0.6,
        'fire_rate': 1000,
        'score': 800,
        'size': (120, 165),  # Battlecruisers
        'behavior': 'artillery'
    },
    'dragoon': {
        'name': 'Dragoon',
        'shields': 100,
        'armor': 80,
        'hull': 50,
        'speed': 1.5,
        'fire_rate': 1800,
        'score': 350,
        'size': (84, 112),  # Drone carriers
        'behavior': 'drone_carrier',
        'drones': 4  # Spawns more drones
    }
}

# Upgrade costs (refugees)
UPGRADE_COSTS = {
    'gyrostabilizer': 10,
    'armor_plate': 15,
    'tracking_enhancer': 20,
    'emp_ammo': 25,
    'plasma_ammo': 35,
    'fusion_ammo': 45,
    'barrage_ammo': 55,
    'wolf_upgrade': 50,
    'jaguar_upgrade': 50
}

# Jaguar upgrade bonuses
JAGUAR_SPEED_BONUS = 1.4
JAGUAR_SHIELD_BONUS = 30

# Powerup types
POWERUP_TYPES = {
    'nanite': {'name': 'Nanite Paste', 'color': (100, 255, 100), 'heal': 50},
    'capacitor': {'name': 'Capacitor Booster', 'color': (100, 100, 255), 'rockets': 5},
    'overdrive': {'name': 'Overdrive', 'color': (255, 255, 100), 'duration': 5000},
    'shield_boost': {'name': 'Shield Booster', 'color': (150, 200, 255), 'duration': 3000},
    'double_damage': {'name': 'Damage Amplifier', 'color': (255, 100, 100), 'duration': 6000},
    'rapid_fire': {'name': 'Rapid Fire', 'color': (255, 150, 50), 'duration': 5000},
    'bomb_charge': {'name': 'Bomb Charge', 'color': (255, 50, 255), 'bombs': 1},
    'magnet': {'name': 'Tractor Beam', 'color': (200, 200, 255), 'duration': 8000},
    'invulnerability': {'name': 'Hardener', 'color': (255, 215, 0), 'duration': 3000}
}

# Stage definitions
STAGES = [
    {
        'name': 'Asteroid Belt Escape',
        'waves': 5,
        'enemies': ['executioner', 'punisher', 'drone'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Amarr Patrol Interdiction',
        'waves': 7,
        'enemies': ['executioner', 'punisher', 'coercer', 'drone'],
        'industrial_chance': 0.15,
        'boss': 'omen'
    },
    {
        'name': 'Slave Colony Liberation',
        'waves': 8,
        'enemies': ['executioner', 'punisher', 'coercer', 'omen', 'interceptor'],
        'industrial_chance': 0.25,
        'boss': None
    },
    {
        'name': 'Gate Assault',
        'waves': 10,
        'enemies': ['punisher', 'coercer', 'omen', 'maller', 'interceptor', 'bomber'],
        'industrial_chance': 0.15,
        'boss': 'apocalypse'
    },
    {
        'name': 'Final Push - Amarr Station',
        'waves': 12,
        'enemies': ['coercer', 'omen', 'maller', 'harbinger', 'interceptor', 'bomber', 'dragoon'],
        'industrial_chance': 0.2,
        'boss': 'abaddon'
    }
]


def _convert_json_stage_to_stage_format(stage_data):
    """
    Convert a JSON stage definition to the format used by STAGES.
    
    This function handles both simple stage formats (like example_stage.json)
    and complex wave-based formats (like capital_ship_assault.json).
    
    Args:
        stage_data: Dictionary loaded from a JSON stage file
        
    Returns:
        Dictionary in STAGES format, or None if conversion fails
    """
    # Simple format: has 'waves' as integer, 'enemies' as list
    if isinstance(stage_data.get('waves'), int):
        return {
            'name': stage_data.get('name', 'Unknown Stage'),
            'waves': stage_data['waves'],
            'enemies': stage_data.get('enemies', []),
            'industrial_chance': stage_data.get('industrial_chance', 0.1),
            'boss': stage_data.get('boss')
        }
    
    # Complex format: has 'waves' as list of wave definitions
    elif isinstance(stage_data.get('waves'), list):
        # For complex wave formats, we simplify by counting waves
        # and extracting boss from last wave if present
        waves_list = stage_data['waves']
        num_waves = len(waves_list)
        
        # Collect all enemy types from all waves (using set for O(1) lookups)
        all_enemies_set = set()
        boss_type = None
        
        for wave in waves_list:
            if 'boss' in wave:
                boss_type = wave['boss']
            elif 'enemies' in wave:
                for enemy_def in wave['enemies']:
                    if isinstance(enemy_def, dict) and 'type' in enemy_def:
                        all_enemies_set.add(enemy_def['type'])
        
        # Check if stage has a boss definition at top level
        if not boss_type and 'boss' in stage_data:
            boss_info = stage_data['boss']
            if isinstance(boss_info, dict):
                boss_type = boss_info.get('type')
            else:
                boss_type = boss_info
        
        return {
            'name': stage_data.get('name', 'Unknown Stage'),
            'waves': num_waves,
            'enemies': list(all_enemies_set) if all_enemies_set else ['executioner', 'punisher'],
            'industrial_chance': 0.1,  # Default value
            'boss': boss_type
        }
    
    return None


def load_expansion_stages():
    """
    Load expansion stages from data/stages/ directory and add them to STAGES.
    
    This function is called at module initialization to integrate expansion
    content. It skips example_stage.json and any stages already in the base
    STAGES list.
    """
    try:
        from core.loader import load_stages
        
        # Load all stage JSON files
        json_stages = load_stages()
        
        # List of stage files to skip (examples or already integrated)
        skip_stages = {'example_stage'}
        
        # Stage names already in base STAGES to avoid duplicates
        existing_names = {stage['name'] for stage in STAGES}
        
        for stage_id, stage_data in json_stages.items():
            # Skip example stages
            if stage_id in skip_stages:
                continue
            
            # Skip if already in STAGES by name
            if stage_data.get('name') in existing_names:
                continue
            
            # Convert JSON format to STAGES format
            converted_stage = _convert_json_stage_to_stage_format(stage_data)
            
            if converted_stage:
                STAGES.append(converted_stage)
    
    except ImportError:
        # If loader is not available, silently skip
        pass
    except Exception as e:
        # Log error but don't crash
        print(f"Warning: Could not load expansion stages: {e}")


# Load expansion stages on module import
load_expansion_stages()
