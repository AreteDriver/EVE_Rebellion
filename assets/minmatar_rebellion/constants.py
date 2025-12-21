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

# T2 Ship Variants
# Wolf upgrade bonuses - Offense focus
WOLF_SPEED_BONUS = 1.2
WOLF_ARMOR_BONUS = 50
WOLF_HULL_BONUS = 25
WOLF_DAMAGE_BONUS = 1.25

# Jaguar upgrade bonuses - Defense/Speed focus
JAGUAR_SPEED_BONUS = 1.3
JAGUAR_SHIELD_BONUS = 50
JAGUAR_HULL_BONUS = 15
JAGUAR_DAMAGE_BONUS = 1.1

# Skill Point System
SP_PER_FRIGATE = 5
SP_PER_CRUISER = 20
SP_PER_DESTROYER = 10
SP_PER_BATTLECRUISER = 50
SP_PER_BATTLESHIP = 100
SP_PER_INDUSTRIAL = 10
SP_UNLOCK_THRESHOLD = 500  # SP needed to unlock each T2 variant

# SP multipliers by difficulty
SP_DIFFICULTY_MULT = {
    'easy': 0.8,
    'normal': 1.0,
    'hard': 1.3,
    'nightmare': 1.5
}

# Bullet stats
BULLET_SPEED = 12
BULLET_DAMAGE = 10
ROCKET_SPEED = 8
ROCKET_DAMAGE = 50

# Enemy stats
ENEMY_STATS = {
    # Frigates (Tier 0)
    'executioner': {
        'name': 'Executioner',
        'shields': 60,
        'armor': 20,
        'hull': 20,
        'speed': 2.5,
        'fire_rate': 1500,
        'score': 100,
        'size': (30, 40),
        'tier': 'frigate',
        'sp_value': 5
    },
    'punisher': {
        'name': 'Punisher',
        'shields': 30,
        'armor': 80,
        'hull': 30,
        'speed': 1.5,
        'fire_rate': 2000,
        'score': 150,
        'size': (35, 45),
        'tier': 'frigate',
        'sp_value': 6
    },
    # Destroyers (Tier 1)
    'coercer': {
        'name': 'Coercer',
        'shields': 80,
        'armor': 100,
        'hull': 50,
        'speed': 1.8,
        'fire_rate': 1000,
        'score': 300,
        'size': (40, 55),
        'tier': 'destroyer',
        'sp_value': 12,
        'boss': True,
        'special_ability': 'rapid_fire',
        'ability_desc': 'Burst fire mode - rapid laser volleys'
    },
    'dragoon': {
        'name': 'Dragoon',
        'shields': 100,
        'armor': 80,
        'hull': 60,
        'speed': 1.6,
        'fire_rate': 1200,
        'score': 320,
        'size': (42, 58),
        'tier': 'destroyer',
        'sp_value': 13,
        'boss': True,
        'special_ability': 'drone_swarm',
        'ability_desc': 'Deploys combat drones'
    },
    'heretic': {
        'name': 'Heretic',
        'shields': 120,
        'armor': 60,
        'hull': 50,
        'speed': 2.0,
        'fire_rate': 1100,
        'score': 310,
        'size': (38, 54),
        'tier': 'destroyer',
        'sp_value': 12,
        'boss': True,
        'special_ability': 'interdiction',
        'ability_desc': 'Slows player movement'
    },
    # Cruisers (Tier 2)
    'omen': {
        'name': 'Omen',
        'shields': 100,
        'armor': 150,
        'hull': 80,
        'speed': 1.2,
        'fire_rate': 1200,
        'score': 500,
        'size': (50, 65),
        'tier': 'cruiser',
        'sp_value': 22,
        'boss': True,
        'special_ability': 'beam_sweep',
        'ability_desc': 'Wide laser sweep attack'
    },
    'maller': {
        'name': 'Maller',
        'shields': 50,
        'armor': 250,
        'hull': 100,
        'speed': 0.8,
        'fire_rate': 1800,
        'score': 600,
        'size': (55, 70),
        'tier': 'cruiser',
        'sp_value': 25,
        'boss': True,
        'special_ability': 'armor_repair',
        'ability_desc': 'Regenerates armor over time'
    },
    'arbitrator': {
        'name': 'Arbitrator',
        'shields': 120,
        'armor': 120,
        'hull': 70,
        'speed': 1.0,
        'fire_rate': 1400,
        'score': 550,
        'size': (52, 68),
        'tier': 'cruiser',
        'sp_value': 23,
        'boss': True,
        'special_ability': 'neut_pulse',
        'ability_desc': 'Drains rocket capacity'
    },
    'augoror': {
        'name': 'Augoror',
        'shields': 100,
        'armor': 140,
        'hull': 80,
        'speed': 1.1,
        'fire_rate': 1500,
        'score': 520,
        'size': (50, 66),
        'tier': 'cruiser',
        'sp_value': 21,
        'boss': True,
        'special_ability': 'energy_transfer',
        'ability_desc': 'Charges shields quickly'
    },
    # Battlecruisers (Tier 3)
    'harbinger': {
        'name': 'Harbinger',
        'shields': 200,
        'armor': 300,
        'hull': 150,
        'speed': 0.7,
        'fire_rate': 900,
        'score': 1200,
        'size': (65, 85),
        'tier': 'battlecruiser',
        'sp_value': 55,
        'boss': True,
        'special_ability': 'focused_beam',
        'ability_desc': 'Charges powerful focused laser'
    },
    'prophecy': {
        'name': 'Prophecy',
        'shields': 150,
        'armor': 350,
        'hull': 160,
        'speed': 0.6,
        'fire_rate': 1000,
        'score': 1300,
        'size': (68, 88),
        'tier': 'battlecruiser',
        'sp_value': 58,
        'boss': True,
        'special_ability': 'combat_drones',
        'ability_desc': 'Launches swarm of heavy drones'
    },
    'oracle': {
        'name': 'Oracle',
        'shields': 180,
        'armor': 250,
        'hull': 140,
        'speed': 0.8,
        'fire_rate': 800,
        'score': 1250,
        'size': (64, 84),
        'tier': 'battlecruiser',
        'sp_value': 56,
        'boss': True,
        'special_ability': 'alpha_strike',
        'ability_desc': 'Devastating single shot'
    },
    # Battleships (Tier 4)
    'apocalypse': {
        'name': 'Apocalypse',
        'shields': 300,
        'armor': 400,
        'hull': 200,
        'speed': 0.5,
        'fire_rate': 800,
        'score': 2000,
        'size': (80, 120),
        'tier': 'battleship',
        'sp_value': 120,
        'boss': True,
        'special_ability': 'mega_pulse',
        'ability_desc': 'Multi-directional energy pulse'
    },
    'abaddon': {
        'name': 'Abaddon',
        'shields': 500,
        'armor': 600,
        'hull': 300,
        'speed': 0.3,
        'fire_rate': 600,
        'score': 5000,
        'size': (100, 150),
        'tier': 'battleship',
        'sp_value': 200,
        'boss': True,
        'special_ability': 'omega_strike',
        'ability_desc': 'Ultimate weapon - massive AoE'
    },
    'armageddon': {
        'name': 'Armageddon',
        'shields': 400,
        'armor': 500,
        'hull': 250,
        'speed': 0.4,
        'fire_rate': 700,
        'score': 3500,
        'size': (90, 135),
        'tier': 'battleship',
        'sp_value': 150,
        'boss': True,
        'special_ability': 'neut_wave',
        'ability_desc': 'Energy drain wave attack'
    },
    # Industrials
    'bestower': {
        'name': 'Bestower',
        'shields': 40,
        'armor': 100,
        'hull': 60,
        'speed': 1.0,
        'fire_rate': 0,  # Non-combat
        'score': 200,
        'refugees': 5,
        'size': (45, 80),
        'tier': 'industrial',
        'sp_value': 10
    },
}

# Boss pools by tier
BOSS_POOLS = {
    1: ['coercer', 'dragoon', 'heretic'],  # Destroyers
    2: ['omen', 'maller', 'arbitrator', 'augoror'],  # Cruisers
    3: ['harbinger', 'prophecy', 'oracle'],  # Battlecruisers
    4: ['apocalypse', 'abaddon', 'armageddon']  # Battleships
}

# Wave configuration
WAVE_CONFIG = {
    'base_enemies': 3,
    'per_wave': 1,
    'per_stage': 2,
    'spawn_interval': 45,  # frames between spawns
    'difficulty_scaling': {
        'wave_mult': 0.1,  # +10% per wave
        'stage_mult': 0.15  # +15% per stage
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
    'wolf_upgrade': 50
}

# Powerup types
POWERUP_TYPES = {
    'nanite': {'name': 'Nanite Paste', 'color': (100, 255, 100), 'heal': 50},
    'capacitor': {'name': 'Capacitor Booster', 'color': (100, 100, 255), 'rockets': 5},
    'overdrive': {'name': 'Overdrive', 'color': (255, 255, 100), 'duration': 5000},
    'shield_boost': {'name': 'Shield Booster', 'color': (150, 200, 255), 'duration': 3000}
}

# Stage definitions
STAGES = [
    {
        'name': 'Asteroid Belt Escape',
        'waves': 5,
        'enemies': ['executioner', 'punisher'],
        'industrial_chance': 0.1,
        'boss_tier': 1,  # Destroyer
        'wave_scaling': 1.0,
        'description': 'Escape from the belt while Amarr destroyers hunt you'
    },
    {
        'name': 'Amarr Patrol Interdiction',
        'waves': 7,
        'enemies': ['executioner', 'punisher'],
        'industrial_chance': 0.15,
        'boss_tier': 1,  # Destroyer
        'wave_scaling': 1.2,
        'description': 'Intercept the patrol and destroy their destroyer'
    },
    {
        'name': 'Slave Colony Liberation',
        'waves': 8,
        'enemies': ['executioner', 'punisher'],
        'industrial_chance': 0.25,
        'boss_tier': 2,  # Cruiser
        'wave_scaling': 1.4,
        'description': 'Free the slaves, face cruiser-class opposition'
    },
    {
        'name': 'Gate Assault',
        'waves': 10,
        'enemies': ['executioner', 'punisher'],
        'industrial_chance': 0.15,
        'boss_tier': 3,  # Battlecruiser
        'wave_scaling': 1.6,
        'description': 'Assault the gate defended by a battlecruiser'
    },
    {
        'name': 'Final Push - Amarr Station',
        'waves': 12,
        'enemies': ['executioner', 'punisher'],
        'industrial_chance': 0.2,
        'boss_tier': 4,  # Battleship
        'wave_scaling': 2.0,
        'description': 'The final confrontation with an Amarr battleship'
    }
]
