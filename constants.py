"""Game constants and configuration for EVE Rebellion"""
import pygame

# Display - Wide arcade window
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 800
FPS = 60

# Screen shake
SHAKE_SMALL = 3
SHAKE_MEDIUM = 6
SHAKE_LARGE = 12
SHAKE_DECAY = 0.85

# Difficulty settings - EVE Online themed labels
# Carebear = Easy, Newbro = Normal, Bitter Vet = Hard, Triglavian = Nightmare
DIFFICULTY_SETTINGS = {
    'easy': {
        'name': 'Carebear',
        'desc': 'Forgiving. Learn systems. Minimal punishment.',
        'enemy_health_mult': 0.5,      # Easy to kill
        'enemy_damage_mult': 0.4,      # Low damage
        'enemy_fire_rate_mult': 1.8,   # Slow shooting
        'player_damage_mult': 1.5,     # Player hits hard
        'refugee_mult': 1.5,
        'powerup_chance': 0.30,        # Lots of powerups
        'enemy_speed_mult': 0.7,       # Slow enemies
        'spawn_rate_mult': 1.4         # Slower spawns
    },
    'normal': {
        'name': 'Newbro',
        'desc': 'Real mechanics. Teaches heat, positioning, failure.',
        'enemy_health_mult': 0.8,      # Slightly easier than before
        'enemy_damage_mult': 0.8,      # Manageable damage
        'enemy_fire_rate_mult': 1.2,   # Slightly slower fire
        'player_damage_mult': 1.1,     # Slight damage boost
        'refugee_mult': 1.0,
        'powerup_chance': 0.18,
        'enemy_speed_mult': 0.9,
        'spawn_rate_mult': 1.1
    },
    'hard': {
        'name': 'Bitter Vet',
        'desc': 'No mercy. Assumes mastery and discipline.',
        'enemy_health_mult': 1.4,      # Tougher but not brutal
        'enemy_damage_mult': 1.3,      # Noticeable damage
        'enemy_fire_rate_mult': 0.75,  # Faster but manageable
        'player_damage_mult': 0.9,     # Slight reduction
        'refugee_mult': 0.7,
        'powerup_chance': 0.10,
        'enemy_speed_mult': 1.1,       # Slightly faster
        'spawn_rate_mult': 0.85
    },
    'nightmare': {
        'name': 'Triglavian',
        'desc': 'Hostile reality. Systems turn against you.',
        'enemy_health_mult': 2.2,      # Tanky but killable
        'enemy_damage_mult': 1.8,      # Hurts a lot
        'enemy_fire_rate_mult': 0.5,   # Fast shooting
        'player_damage_mult': 0.7,     # Reduced damage
        'refugee_mult': 0.4,
        'powerup_chance': 0.06,
        'enemy_speed_mult': 1.25,      # Fast enemies
        'spawn_rate_mult': 0.75
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

# Colors - Caldari (steel blue/corporate)
COLOR_CALDARI_HULL = (30, 58, 95)
COLOR_CALDARI_ACCENT = (70, 130, 180)
COLOR_CALDARI_DARK = (20, 40, 70)

# Colors - Gallente (olive green/organic)
COLOR_GALLENTE_HULL = (46, 93, 46)
COLOR_GALLENTE_ACCENT = (107, 142, 35)
COLOR_GALLENTE_DARK = (30, 60, 30)

# === FACTION DEFINITIONS ===
FACTIONS = {
    'minmatar': {
        'name': 'Minmatar Republic',
        'tagline': 'In Rust We Trust',
        'color_primary': COLOR_MINMATAR_ACCENT,
        'color_secondary': COLOR_MINMATAR_HULL,
        'engine_color': (255, 150, 50),  # Orange engines
        'weapon_type': 'projectile',  # Autocannons
        'player_ships': ['rifter', 'wolf', 'jaguar'],
        'enemy_faction': 'amarr',
        'story_intro': "Your ancestors were enslaved by the Amarr Empire. Generations suffered under their golden heel. But the Minmatar spirit cannot be broken. Today, you strike back.",
        'victory_text': "The Amarr fleet lies in ruins. Slaves are free. The Republic stands defiant. You are legend.",
    },
    'amarr': {
        'name': 'Amarr Empire',
        'tagline': 'Amarr Victor',
        'color_primary': COLOR_AMARR_ACCENT,
        'color_secondary': COLOR_AMARR_HULL,
        'engine_color': (100, 150, 255),  # Blue engines
        'weapon_type': 'laser',  # Pulse lasers
        'player_ships': ['executioner', 'crusader', 'malediction'],
        'enemy_faction': 'minmatar',
        'story_intro': "The Minmatar rebels threaten the divine order of the Empire. As a loyal servant of the Empress, you will crush this insurrection and restore peace through strength.",
        'victory_text': "The rebellion is crushed. Order is restored. The Empire endures eternal. Glory to Amarr.",
    },
    'caldari': {
        'name': 'Caldari State',
        'tagline': 'The State Provides',
        'color_primary': (70, 130, 180),  # Steel blue
        'color_secondary': (30, 58, 95),  # Dark blue
        'engine_color': (100, 200, 255),  # Cyan engines
        'weapon_type': 'missile',  # Missiles
        'player_ships': ['kestrel', 'hawk', 'harpy'],
        'enemy_faction': 'gallente',
        'story_intro': "The Gallente Federation encroaches on State interests. Corporate profits demand action. You are the blade of the megacorporations.",
        'victory_text': "Gallente forces are scattered. The trade lanes are secure. The State prospers.",
    },
    'gallente': {
        'name': 'Gallente Federation',
        'tagline': 'Liberty or Death',
        'color_primary': (107, 142, 35),  # Olive green
        'color_secondary': (46, 93, 46),  # Dark green
        'engine_color': (150, 255, 150),  # Green engines
        'weapon_type': 'hybrid',  # Hybrid turrets
        'player_ships': ['tristan', 'enyo', 'ishkur'],
        'enemy_faction': 'caldari',
        'story_intro': "The Caldari State oppresses its workers and threatens Federation sovereignty. Fight for liberty against corporate tyranny.",
        'victory_text': "The Caldari fleet retreats. Freedom rings across the stars. Vive la Federation!",
    }
}

# Ship mappings for faction swapping
MINMATAR_SHIPS = ['rifter', 'wolf', 'jaguar', 'slasher', 'hurricane', 'nidhoggur']
AMARR_SHIPS = ['executioner', 'punisher', 'coercer', 'omen', 'maller', 'harbinger',
               'apocalypse', 'abaddon', 'archon', 'avatar']

# Equivalent ship classes between factions (for enemy substitution)
SHIP_EQUIVALENTS = {
    # Minmatar -> Amarr equivalent
    'rifter': 'executioner',
    'slasher': 'punisher',
    'wolf': 'crusader',
    'jaguar': 'malediction',
    'hurricane': 'harbinger',
    # Amarr -> Minmatar equivalent
    'executioner': 'rifter',
    'punisher': 'slasher',
    'coercer': 'thrasher',
    'omen': 'stabber',
    'maller': 'rupture',
    'harbinger': 'hurricane',
    'apocalypse': 'typhoon',
    'abaddon': 'maelstrom',
}

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
PLAYER_BASE_FIRE_RATE = 50  # ms between shots (3x faster - mow them down)
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
        'size': (79, 103)  # Frigates
    },
    'punisher': {
        'name': 'Punisher',
        'shields': 30,
        'armor': 80,
        'hull': 30,
        'speed': 1.5,
        'fire_rate': 2000,
        'score': 150,
        'size': (87, 113)  # Frigates
    },
    'tormentor': {
        'name': 'Tormentor',
        'shields': 50,
        'armor': 40,
        'hull': 25,
        'speed': 2.2,
        'fire_rate': 1400,
        'score': 120,
        'size': (74, 97)  # Frigates - laser boat
    },
    'crucifier': {
        'name': 'Crucifier',
        'shields': 45,
        'armor': 35,
        'hull': 20,
        'speed': 2.8,
        'fire_rate': 1600,
        'score': 110,
        'size': (69, 92)  # Frigates - fast EWAR
    },
    'omen': {
        'name': 'Omen',
        'shields': 150,
        'armor': 200,
        'hull': 100,
        'speed': 0.9,
        'fire_rate': 1200,
        'score': 800,
        'size': (368, 482),  # MASSIVE cruiser - dwarfs player ships
    },
    'maller': {
        'name': 'Maller',
        'shields': 80,
        'armor': 350,
        'hull': 150,
        'speed': 0.6,
        'fire_rate': 1800,
        'score': 1000,
        'size': (402, 529),  # MASSIVE armor cruiser - tank
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
        'size': (206, 356)  # Industrial - tall hauler
    },
    'apocalypse': {
        'name': 'Apocalypse',
        'shields': 600,
        'armor': 900,
        'hull': 500,
        'speed': 0.5,
        'fire_rate': 800,
        'score': 2000,
        'size': (322, 482),  # Battleship - 5x frigate (~1200m)
        'boss': True
    },
    'abaddon': {
        'name': 'Abaddon',
        'shields': 1000,
        'armor': 1500,
        'hull': 800,
        'speed': 0.3,
        'fire_rate': 600,
        'score': 5000,
        'size': (390, 586),  # Battleship boss - massive armored beast
        'boss': True
    },
    'amarr_capital': {
        'name': 'Golden Supercarrier',
        'shields': 2000,
        'armor': 4000,
        'hull': 2500,
        'speed': 0.3,
        'fire_rate': 1500,
        'score': 10000,
        'size': (575, 862),  # Capital ship - truly massive
        'boss': True
    },
    'machariel': {
        'name': 'Machariel',
        'shields': 400,
        'armor': 800,
        'hull': 600,
        'speed': 1.0,
        'fire_rate': 800,
        'score': 3000,
        'size': (322, 482),  # Pirate battleship
        'boss': True
    },
    'stratios': {
        'name': 'Stratios',
        'shields': 300,
        'armor': 350,
        'hull': 200,
        'speed': 1.2,
        'fire_rate': 1000,
        'score': 2000,
        'size': (229, 322),  # Cruiser-size cloaky hunter
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
        'size': (42, 42),  # Drones
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
        'size': (98, 139),  # Bombers
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
        'size': (63, 87),  # Interceptors
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
        'size': (85, 111),  # Destroyers
        'behavior': 'strafe'
    },
    'harbinger': {
        'name': 'Harbinger',
        'shields': 500,
        'armor': 800,
        'hull': 400,
        'speed': 0.45,
        'fire_rate': 1000,
        'score': 2500,
        'size': (517, 690),  # MASSIVE battlecruiser - mini-boss sized
        'behavior': 'artillery',
    },
    'dragoon': {
        'name': 'Dragoon',
        'shields': 100,
        'armor': 80,
        'hull': 50,
        'speed': 1.5,
        'fire_rate': 1800,
        'score': 350,
        'size': (111, 148),  # Drone carriers
        'behavior': 'drone_carrier',
        'drones': 4  # Spawns more drones
    },
    # === MINMATAR SHIPS (for Amarr campaign enemies) ===
    'rifter': {
        'name': 'Rifter',
        'shields': 40,
        'armor': 50,
        'hull': 25,
        'speed': 3.0,
        'fire_rate': 1300,
        'score': 100,
        'size': (79, 103),  # Frigate - fast attack
        'faction': 'minmatar'
    },
    'slasher': {
        'name': 'Slasher',
        'shields': 50,
        'armor': 30,
        'hull': 20,
        'speed': 3.5,
        'fire_rate': 1100,
        'score': 90,
        'size': (74, 97),  # Frigate - very fast
        'faction': 'minmatar'
    },
    'thrasher': {
        'name': 'Thrasher',
        'shields': 60,
        'armor': 70,
        'hull': 40,
        'speed': 2.2,
        'fire_rate': 1000,
        'score': 180,
        'size': (109, 143),  # Destroyer - heavy firepower
        'faction': 'minmatar'
    },
    'stabber': {
        'name': 'Stabber',
        'shields': 120,
        'armor': 180,
        'hull': 90,
        'speed': 1.1,
        'fire_rate': 1100,
        'score': 700,
        'size': (345, 459),  # Cruiser - fast for its class
        'faction': 'minmatar'
    },
    'rupture': {
        'name': 'Rupture',
        'shields': 100,
        'armor': 250,
        'hull': 120,
        'speed': 0.8,
        'fire_rate': 1400,
        'score': 850,
        'size': (368, 482),  # Cruiser - armor tank
        'faction': 'minmatar'
    },
    'hurricane': {
        'name': 'Hurricane',
        'shields': 400,
        'armor': 700,
        'hull': 350,
        'speed': 0.5,
        'fire_rate': 900,
        'score': 2200,
        'size': (494, 655),  # Battlecruiser
        'faction': 'minmatar',
        'behavior': 'artillery'
    },
    'typhoon': {
        'name': 'Typhoon',
        'shields': 600,
        'armor': 900,
        'hull': 500,
        'speed': 0.35,
        'fire_rate': 1500,
        'score': 4000,
        'size': (552, 736),  # Battleship
        'faction': 'minmatar',
        'boss': True
    },
    'maelstrom': {
        'name': 'Maelstrom',
        'shields': 800,
        'armor': 1000,
        'hull': 600,
        'speed': 0.3,
        'fire_rate': 1200,
        'score': 5000,
        'size': (598, 804),  # Battleship - final boss
        'faction': 'minmatar',
        'boss': True
    },
    # === GALLENTE SHIPS ===
    'tristan': {
        'name': 'Tristan',
        'shields': 50,
        'armor': 30,
        'hull': 20,
        'speed': 2.3,
        'fire_rate': 1400,
        'score': 100,
        'size': (74, 97),
        'faction': 'gallente'
    },
    'atron': {
        'name': 'Atron',
        'shields': 40,
        'armor': 20,
        'hull': 15,
        'speed': 3.0,
        'fire_rate': 1200,
        'score': 90,
        'size': (63, 80),
        'faction': 'gallente'
    },
    'incursus': {
        'name': 'Incursus',
        'shields': 45,
        'armor': 50,
        'hull': 25,
        'speed': 2.0,
        'fire_rate': 1600,
        'score': 120,
        'size': (69, 89),
        'faction': 'gallente'
    },
    'catalyst': {
        'name': 'Catalyst',
        'shields': 80,
        'armor': 60,
        'hull': 40,
        'speed': 1.8,
        'fire_rate': 800,
        'score': 200,
        'size': (103, 138),
        'faction': 'gallente'
    },
    'thorax': {
        'name': 'Thorax',
        'shields': 150,
        'armor': 180,
        'hull': 100,
        'speed': 1.0,
        'fire_rate': 1300,
        'score': 700,
        'size': (322, 413),
        'faction': 'gallente',
        'boss': True
    },
    'vexor': {
        'name': 'Vexor',
        'shields': 120,
        'armor': 160,
        'hull': 80,
        'speed': 1.2,
        'fire_rate': 1500,
        'score': 600,
        'size': (299, 390),
        'faction': 'gallente'
    },
    'brutix': {
        'name': 'Brutix',
        'shields': 300,
        'armor': 400,
        'hull': 200,
        'speed': 0.7,
        'fire_rate': 1100,
        'score': 1200,
        'size': (436, 575),
        'faction': 'gallente'
    },
    'myrmidon': {
        'name': 'Myrmidon',
        'shields': 350,
        'armor': 450,
        'hull': 250,
        'speed': 0.6,
        'fire_rate': 1400,
        'score': 1500,
        'size': (459, 598),
        'faction': 'gallente',
        'boss': True
    },
    'dominix': {
        'name': 'Dominix',
        'shields': 500,
        'armor': 700,
        'hull': 400,
        'speed': 0.4,
        'fire_rate': 1600,
        'score': 3000,
        'size': (517, 690),
        'faction': 'gallente'
    },
    'megathron': {
        'name': 'Megathron',
        'shields': 600,
        'armor': 900,
        'hull': 500,
        'speed': 0.35,
        'fire_rate': 1000,
        'score': 5000,
        'size': (575, 781),
        'faction': 'gallente',
        'boss': True
    },
    # === CALDARI SHIPS ===
    'kestrel': {
        'name': 'Kestrel',
        'shields': 60,
        'armor': 20,
        'hull': 20,
        'speed': 2.5,
        'fire_rate': 1200,
        'score': 100,
        'size': (69, 92),
        'faction': 'caldari'
    },
    'merlin': {
        'name': 'Merlin',
        'shields': 70,
        'armor': 25,
        'hull': 20,
        'speed': 2.2,
        'fire_rate': 1400,
        'score': 110,
        'size': (63, 86),
        'faction': 'caldari'
    },
    'condor': {
        'name': 'Condor',
        'shields': 45,
        'armor': 15,
        'hull': 15,
        'speed': 3.2,
        'fire_rate': 1000,
        'score': 80,
        'size': (57, 74),
        'faction': 'caldari'
    },
    'cormorant': {
        'name': 'Cormorant',
        'shields': 100,
        'armor': 40,
        'hull': 35,
        'speed': 1.9,
        'fire_rate': 700,
        'score': 200,
        'size': (97, 132),
        'faction': 'caldari'
    },
    'caracal': {
        'name': 'Caracal',
        'shields': 180,
        'armor': 60,
        'hull': 50,
        'speed': 1.3,
        'fire_rate': 1100,
        'score': 500,
        'size': (276, 368),
        'faction': 'caldari'
    },
    'moa': {
        'name': 'Moa',
        'shields': 200,
        'armor': 80,
        'hull': 60,
        'speed': 1.1,
        'fire_rate': 1300,
        'score': 550,
        'size': (287, 379),
        'faction': 'caldari'
    },
    'drake': {
        'name': 'Drake',
        'shields': 400,
        'armor': 150,
        'hull': 120,
        'speed': 0.7,
        'fire_rate': 900,
        'score': 1200,
        'size': (436, 575),
        'faction': 'caldari'
    },
    'ferox': {
        'name': 'Ferox',
        'shields': 350,
        'armor': 180,
        'hull': 140,
        'speed': 0.75,
        'fire_rate': 800,
        'score': 1100,
        'size': (413, 552),
        'faction': 'caldari'
    },
    'raven': {
        'name': 'Raven',
        'shields': 600,
        'armor': 200,
        'hull': 180,
        'speed': 0.4,
        'fire_rate': 1500,
        'score': 4000,
        'size': (552, 747),
        'faction': 'caldari',
        'boss': True
    },
    'rokh': {
        'name': 'Rokh',
        'shields': 700,
        'armor': 250,
        'hull': 200,
        'speed': 0.35,
        'fire_rate': 800,
        'score': 5000,
        'size': (575, 781),
        'faction': 'caldari',
        'boss': True
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
    # Heat management - Nanite Paste cools weapons (EVE lore accurate)
    'nanite': {'name': 'Nanite Paste', 'color': (100, 255, 100), 'heat_reduce': 100, 'category': 'utility'},

    # Health powerups - spawn based on what's damaged
    'shield_recharger': {'name': 'Shield Recharger', 'color': (100, 180, 255), 'shield_heal': 40, 'category': 'health'},
    'armor_repairer': {'name': 'Armor Repairer', 'color': (255, 180, 80), 'armor_heal': 35, 'category': 'health'},
    'hull_repairer': {'name': 'Hull Repairer', 'color': (180, 180, 180), 'hull_heal': 30, 'category': 'health'},

    # Weapon upgrades - STACK for increased power
    'weapon_upgrade': {'name': 'Weapon Upgrade', 'color': (255, 100, 100), 'category': 'weapon'},
    'rapid_fire': {'name': 'Rapid Fire', 'color': (255, 150, 50), 'category': 'weapon'},

    # Timed buffs
    'overdrive': {'name': 'Overdrive', 'color': (255, 255, 100), 'duration': 5000, 'category': 'buff'},
    'magnet': {'name': 'Tractor Beam', 'color': (200, 200, 255), 'duration': 8000, 'category': 'buff'},
    'invulnerability': {'name': 'Assault Damage Control', 'color': (255, 215, 0), 'duration': 5000, 'category': 'buff'},
}

# Powerups that can spawn randomly (excludes contextual health powerups)
# Removed: capacitor (unlimited ammo), bomb_charge (no bombs)
RANDOM_POWERUPS = ['nanite', 'weapon_upgrade', 'rapid_fire',
                   'overdrive', 'magnet', 'invulnerability']

# Health powerups spawn based on player damage state
HEALTH_POWERUPS = ['shield_recharger', 'armor_repairer', 'hull_repairer']

# Stage definitions
# === CAMPAIGN STAGES BY FACTION ===

# Minmatar Campaign - Fighting Amarr oppressors
STAGES_MINMATAR = [
    {
        'name': 'Asteroid Belt Escape',
        'story': "Amarr slavers patrol the belt. Break through their picket and escape to Republic space.",
        'waves': 5,
        'enemies': ['executioner', 'punisher', 'drone'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Amarr Patrol Interdiction',
        'story': "An Amarr patrol blocks the only gate. Engage and destroy their cruiser commander.",
        'waves': 7,
        'enemies': ['executioner', 'punisher', 'coercer', 'drone'],
        'industrial_chance': 0.15,
        'boss': 'omen'
    },
    {
        'name': 'Slave Colony Liberation',
        'story': "A hidden colony holds thousands of Minmatar slaves. Free them at any cost.",
        'waves': 8,
        'enemies': ['executioner', 'punisher', 'coercer', 'omen', 'interceptor'],
        'industrial_chance': 0.25,
        'boss': None
    },
    {
        'name': 'Gate Assault',
        'story': "The Amarr have fortified the gate with a battleship. Punch through to open the escape route.",
        'waves': 10,
        'enemies': ['punisher', 'coercer', 'omen', 'maller', 'interceptor', 'bomber'],
        'industrial_chance': 0.15,
        'boss': 'apocalypse'
    },
    {
        'name': 'Final Push - Amarr Station',
        'story': "The Amarr flagship Damnation guards the station. Destroy it and the rebellion succeeds.",
        'waves': 12,
        'enemies': ['coercer', 'omen', 'maller', 'harbinger', 'interceptor', 'bomber', 'dragoon'],
        'industrial_chance': 0.2,
        'boss': 'abaddon'
    }
]

# Amarr Campaign - Crushing Minmatar rebellion
STAGES_AMARR = [
    {
        'name': 'Border Patrol',
        'story': "Minmatar raiders have breached the border. Hunt them down in the asteroid field.",
        'waves': 5,
        'enemies': ['rifter', 'slasher', 'drone'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Rebel Convoy Ambush',
        'story': "Intelligence reports a rebel supply convoy. Intercept and destroy their escort.",
        'waves': 7,
        'enemies': ['rifter', 'slasher', 'thrasher', 'drone'],
        'industrial_chance': 0.15,
        'boss': 'stabber'
    },
    {
        'name': 'Terrorist Cell Raid',
        'story': "A Minmatar terrorist cell operates from this station. Eliminate all hostiles.",
        'waves': 8,
        'enemies': ['rifter', 'slasher', 'thrasher', 'stabber', 'interceptor'],
        'industrial_chance': 0.25,
        'boss': None
    },
    {
        'name': 'Gate Defense',
        'story': "Rebels are attempting to seize the gate. Hold the line against their battlecruiser.",
        'waves': 10,
        'enemies': ['slasher', 'thrasher', 'stabber', 'rupture', 'interceptor', 'bomber'],
        'industrial_chance': 0.15,
        'boss': 'hurricane'
    },
    {
        'name': 'Crushing the Rebellion',
        'story': "The rebel flagship Defiance leads their final assault. Destroy it and end this war.",
        'waves': 12,
        'enemies': ['thrasher', 'stabber', 'rupture', 'hurricane', 'interceptor', 'bomber'],
        'industrial_chance': 0.2,
        'boss': 'maelstrom'
    }
]

# Caldari Campaign - Fighting Gallente Federation
STAGES_CALDARI = [
    {
        'name': 'Gallente Border Incursion',
        'story': "Gallente raiders have crossed into State territory. Defend the homeland.",
        'waves': 5,
        'enemies': ['tristan', 'atron', 'drone'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Trade Lane Defense',
        'story': "Protect the corporate convoy from Gallente pirates threatening vital supply lines.",
        'waves': 7,
        'enemies': ['tristan', 'atron', 'incursus', 'catalyst'],
        'industrial_chance': 0.15,
        'boss': 'thorax'
    },
    {
        'name': 'Rogue Drone Infestation',
        'story': "A rogue drone hive threatens the State outpost. Purge the infestation.",
        'waves': 8,
        'enemies': ['drone', 'interceptor', 'vexor'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Outer Ring Assault',
        'story': "Push into Gallente-held space. Break through their battlecruiser screen.",
        'waves': 10,
        'enemies': ['vexor', 'thorax', 'brutix', 'bomber'],
        'industrial_chance': 0.2,
        'boss': 'myrmidon'
    },
    {
        'name': 'Federation Dreadnought',
        'story': "The Gallente command ship blocks our advance. Destroy the Megathron and claim victory.",
        'waves': 12,
        'enemies': ['brutix', 'myrmidon', 'dominix', 'bomber'],
        'industrial_chance': 0.25,
        'boss': 'megathron'
    }
]

# Gallente Campaign - Fighting Caldari State
STAGES_GALLENTE = [
    {
        'name': 'Caldari Patrol Interdiction',
        'story': "Caldari patrols threaten Federation shipping lanes. Clear the sector.",
        'waves': 5,
        'enemies': ['kestrel', 'condor', 'drone'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Corporate Outpost Raid',
        'story': "Strike at a Caldari megacorp outpost. Expect heavy missile fire.",
        'waves': 7,
        'enemies': ['kestrel', 'merlin', 'condor', 'cormorant'],
        'industrial_chance': 0.15,
        'boss': 'caracal'
    },
    {
        'name': 'Missile Barrage',
        'story': "Caldari cruiser wing incoming. Their missiles will blot out the stars.",
        'waves': 8,
        'enemies': ['caracal', 'moa', 'cormorant', 'interceptor'],
        'industrial_chance': 0.1,
        'boss': None
    },
    {
        'name': 'Drake Wall Assault',
        'story': "Break through the infamous Caldari Drake wall formation.",
        'waves': 10,
        'enemies': ['caracal', 'moa', 'drake', 'ferox', 'bomber'],
        'industrial_chance': 0.2,
        'boss': 'drake'
    },
    {
        'name': 'State Flagship',
        'story': "The Caldari Raven-class battleship commands their fleet. End this war.",
        'waves': 12,
        'enemies': ['drake', 'ferox', 'raven', 'bomber'],
        'industrial_chance': 0.25,
        'boss': 'rokh'
    }
]

# Default stages (Minmatar campaign for backwards compatibility)
STAGES = STAGES_MINMATAR

# === CHAPTERS - Rebellion Stories Collection ===
# Each chapter represents a major conflict/rebellion in EVE lore
CHAPTERS = [
    {
        'id': 'minmatar_rebellion',
        'title': 'The Minmatar Rebellion',
        'subtitle': 'Rise Against the Golden Fleet',
        'description': 'Break free from Amarr slavery. Lead the uprising that shook the Empire.',
        'faction': 'minmatar',
        'stages': STAGES_MINMATAR,
        'color': COLOR_MINMATAR_ACCENT,
        'year': 'BYC 20',  # Before Yoiul Conference
    },
    {
        'id': 'caldari_secession',
        'title': 'The Caldari Secession',
        'subtitle': 'Morning of Reasoning',
        'description': 'Defend Caldari Prime from Gallente occupation. Fight for State independence.',
        'faction': 'caldari',
        'stages': STAGES_CALDARI,
        'color': COLOR_CALDARI_ACCENT,
        'year': 'BYC 187',
    },
    {
        'id': 'amarr_reclaiming',
        'title': 'The Amarr Reclaiming',
        'subtitle': 'Righteous Fury of God',
        'description': 'Crush the Minmatar uprising. Restore divine order to the Empire.',
        'faction': 'amarr',
        'stages': STAGES_AMARR,
        'color': COLOR_AMARR_ACCENT,
        'year': 'BYC 20',
    },
    {
        'id': 'gallente_liberation',
        'title': 'The Gallente Liberation',
        'subtitle': 'For Freedom and Democracy',
        'description': 'Liberate oppressed systems from Caldari corporate tyranny.',
        'faction': 'gallente',
        'stages': STAGES_GALLENTE,
        'color': COLOR_GALLENTE_ACCENT,
        'year': 'YC 110',
    },
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
