"""Game sprites for Minmatar Rebellion"""
import pygame
import math
import random
import os
from constants import *
from visual_enhancements import add_ship_glow, add_colored_tint, add_outline, add_strong_outline

# Ship sprite cache
_ship_sprite_cache = {}
_SPRITE_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'ship_sprites')

def load_ship_sprite(ship_name, target_size=None):
    """Load a rendered ship sprite from the ship_sprites directory.

    Args:
        ship_name: Name of the ship (e.g., 'rifter', 'executioner')
        target_size: Optional (width, height) tuple to scale the sprite to

    Returns:
        pygame.Surface with the ship sprite, or None if not found
    """
    cache_key = (ship_name, target_size)
    if cache_key in _ship_sprite_cache:
        return _ship_sprite_cache[cache_key].copy()

    sprite_path = os.path.join(_SPRITE_DIR, f"{ship_name}.png")
    if not os.path.exists(sprite_path):
        return None

    try:
        sprite = pygame.image.load(sprite_path).convert_alpha()

        if target_size:
            sprite = pygame.transform.smoothscale(sprite, target_size)

        _ship_sprite_cache[cache_key] = sprite
        return sprite.copy()
    except pygame.error:
        return None

# Map enemy types to sprite names
ENEMY_SPRITE_MAP = {
    'executioner': 'executioner',
    'punisher': 'punisher',
    'tormentor': 'tormentor',
    'crucifier': 'crucifier',
    'coercer': 'coercer',
    'dragoon': 'coercer',  # Use coercer as fallback
    'omen': 'omen',
    'maller': 'maller',
    'arbitrator': 'maller',  # Use maller as fallback
    'augoror': 'maller',
    'harbinger': 'harbinger',
    'prophecy': 'prophecy',
    'apocalypse': 'apocalypse',
    'abaddon': 'abaddon',
    'armageddon': 'abaddon',
    'archon': 'archon',
    'aeon': 'archon',
    'revelation': 'apocalypse',
    'avatar': 'avatar',
    'bestower': None,  # Use procedural industrial ship
    'drone': None,  # Keep procedural for small drones
    'heavy_drone': None,
    'interceptor': 'executioner',
    'bomber': 'punisher',
    'zealot': 'omen',
    'sacrilege': 'maller',
}


class Player(pygame.sprite.Sprite):
    """Player ship - Rifter/Wolf"""
    
    def __init__(self):
        super().__init__()
        self.is_wolf = False
        self.width = 40
        self.height = 50
        self.image = self._create_ship_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        
        # Stats
        self.max_shields = PLAYER_START_SHIELDS
        self.max_armor = PLAYER_START_ARMOR
        self.max_hull = PLAYER_START_HULL
        self.shields = self.max_shields
        self.armor = self.max_armor
        self.hull = self.max_hull
        
        # Weapons
        self.current_ammo = 'sabot'
        self.unlocked_ammo = ['sabot']
        self.rockets = PLAYER_MAX_ROCKETS
        self.max_rockets = PLAYER_MAX_ROCKETS
        
        # Timing
        self.last_shot = 0
        self.last_rocket = 0
        self.fire_rate_mult = 1.0
        self.spread_bonus = 0
        
        # Movement
        self.speed = PLAYER_SPEED
        
        # Upgrades
        self.has_gyro = False
        self.has_tracking = False
        
        # Powerup effects
        self.overdrive_until = 0
        self.shield_boost_until = 0
        self.double_damage_until = 0
        self.rapid_fire_until = 0
        self.magnet_until = 0
        self.invulnerable_until = 0

        # Ship ability system
        self.ability_cooldown = 0
        self.ability_active_until = 0
        self.ability_base_cooldown = 600  # 10 seconds at 60fps
        self.ability_duration = 180  # 3 seconds

        # Bomb ability (screen clear)
        self.bombs = 3
        self.max_bombs = 3
        self.bomb_cooldown = 0
        self.bomb_base_cooldown = 120  # 2 seconds

        # Combat maneuvers (L3/R3 buttons)
        self.barrel_roll_active = False
        self.barrel_roll_timer = 0
        self.barrel_roll_cooldown = 0
        self.barrel_roll_duration = 20  # frames (~0.33 sec)
        self.barrel_roll_cooldown_time = 180  # 3 seconds
        self.barrel_roll_angle = 0  # Visual rotation

        self.emergency_brake_active = False
        self.emergency_brake_timer = 0
        self.emergency_brake_cooldown = 0
        self.emergency_brake_duration = 15  # frames
        self.emergency_brake_cooldown_time = 240  # 4 seconds
        self.brake_start_y = 0

        # Weapon heat system
        self.heat = 0
        self.max_heat = 100
        self.heat_per_shot = 6  # Balanced heat per shot
        self.heat_dissipation = 0.5  # Per frame
        self.overheat_cooldown = 0
        self.overheat_duration = 90  # 1.5 seconds at 60fps
        self.is_overheated = False

        # Score/Progress
        self.refugees = 0
        self.total_refugees = 0
        self.score = 0
    
    def _create_ship_image(self):
        """Create EVE-accurate Minmatar ship sprite with proper loadouts"""
        ship_class = getattr(self, 'ship_class', 'Rifter')

        # All Minmatar assault frigates use the Rifter hull as base
        # Visual differentiation through color tints, weapon loadouts, and tank effects:
        # - Rifter: T1 frigate, 3 turrets + 1 launcher, rust brown
        # - Wolf: Assault frigate, 4 autocannon turrets, armor tank (darker, more plating)
        # - Jaguar: Assault frigate, 3 turrets + 2 rocket launchers, shield tank (blue glow)
        base_hull = 'rifter'

        # Try to load the Rifter hull sprite
        sprite = load_ship_sprite(base_hull, (self.width, self.height))
        if sprite:
            # Add ship-specific weapons, color tints, and effects
            return self._add_ship_loadout(sprite, ship_class)

        # Fall back to procedural generation
        return self._create_polished_minmatar_ship()

    def _add_ship_loadout(self, sprite, ship_class):
        """Add EVE-accurate weapon loadouts and effects to ship sprite"""
        w, h = sprite.get_size()
        cx = w // 2

        # Minmatar engine colors
        engine_color = (255, 120, 40)
        engine_glow = (255, 180, 100)

        # Autocannon turret colors (Minmatar projectile weapons)
        turret_base = (60, 50, 45)
        turret_barrel = (90, 80, 70)
        turret_highlight = (120, 100, 80)

        # Rocket launcher colors
        launcher_base = (70, 60, 55)
        launcher_tube = (50, 45, 40)
        launcher_tip = (180, 60, 40)

        if ship_class == 'Wolf':
            # === WOLF: 4 AUTOCANNON TURRETS, ARMOR PLATING ===
            # Wolf is an armor-tanked assault frigate with all guns

            # Add armor plating overlay (darker patches)
            armor_color = (50, 35, 25, 120)
            armor_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            # Side armor plates
            pygame.draw.polygon(armor_surf, armor_color, [(5, h//3), (12, h//4), (12, h*2//3), (5, h*3//4)])
            pygame.draw.polygon(armor_surf, armor_color, [(w-5, h//3), (w-12, h//4), (w-12, h*2//3), (w-5, h*3//4)])
            sprite.blit(armor_surf, (0, 0))

            # 4 Autocannon turrets (2 on each side, staggered)
            turret_positions = [
                (cx - 12, h//4 + 5),      # Left front
                (cx + 12, h//4 + 5),      # Right front
                (cx - 10, h//2),          # Left mid
                (cx + 10, h//2),          # Right mid
            ]
            for tx, ty in turret_positions:
                # Turret base
                pygame.draw.circle(sprite, turret_base, (tx, ty), 4)
                # Barrel pointing forward (up)
                pygame.draw.line(sprite, turret_barrel, (tx, ty), (tx, ty - 6), 2)
                pygame.draw.circle(sprite, turret_highlight, (tx, ty - 6), 1)

            # Armor repair effect (subtle orange glow on hull)
            repair_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(repair_surf, (200, 100, 50, 30), (cx - 10, h//3, 20, 25))
            sprite.blit(repair_surf, (0, 0))

        elif ship_class == 'Jaguar':
            # === JAGUAR: 2 AUTOCANNONS + 4 ROCKET LAUNCHERS, SHIELD TANK ===
            # Jaguar is a fast shield-tanked assault frigate - rocket specialist
            # Uses Rifter hull with blue shield glow tint

            # Apply subtle blue tint to hull (shield tank coloring)
            tint_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            tint_surf.fill((60, 100, 180, 40))
            sprite.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            # Shield glow effect (subtle blue aura overlay)
            shield_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for r in range(12, 0, -3):
                alpha = int(25 * r / 12)
                pygame.draw.ellipse(shield_surf, (80, 150, 255, alpha),
                                   (cx - w//3 - r, h//4 - r//2, w*2//3 + r*2, h//2 + r))
            sprite.blit(shield_surf, (0, 0))

            # 2 Autocannon turrets (flanking)
            turret_positions = [
                (cx - 8, h//4 + 3),    # Left
                (cx + 8, h//4 + 3),    # Right
            ]
            for tx, ty in turret_positions:
                pygame.draw.circle(sprite, turret_base, (tx, ty), 3)
                pygame.draw.line(sprite, turret_barrel, (tx, ty), (tx, ty - 5), 2)

            # 4 Rocket launchers (2 on each wing, stacked)
            launcher_positions = [
                (cx - 14, h//4 + 8),   # Left wing upper
                (cx - 12, h//3 + 6),   # Left wing lower
                (cx + 14, h//4 + 8),   # Right wing upper
                (cx + 12, h//3 + 6),   # Right wing lower
            ]
            for lx, ly in launcher_positions:
                # Launcher housing
                pygame.draw.rect(sprite, launcher_base, (lx - 2, ly - 2, 4, 6))
                # Rocket tube
                pygame.draw.circle(sprite, launcher_tube, (lx, ly), 2)
                # Rocket tip (red)
                pygame.draw.circle(sprite, launcher_tip, (lx, ly - 2), 1)

            # Shield capacitor indicators (blue dots near engines)
            for i in range(2):
                sx = cx + (i * 2 - 1) * 6
                pygame.draw.circle(sprite, (100, 180, 255), (sx, h - 8), 2)

        else:
            # === RIFTER: 3 TURRETS + 1 LAUNCHER (standard T1 loadout) ===
            # 3 Autocannon turrets
            turret_positions = [
                (cx - 8, h//4 + 5),    # Left
                (cx, h//4),            # Center (forward)
                (cx + 8, h//4 + 5),    # Right
            ]
            for tx, ty in turret_positions:
                pygame.draw.circle(sprite, turret_base, (tx, ty), 3)
                pygame.draw.line(sprite, turret_barrel, (tx, ty), (tx, ty - 4), 2)

            # 1 Rocket launcher (center rear)
            lx, ly = cx, h//2 + 5
            pygame.draw.rect(sprite, launcher_base, (lx - 2, ly - 2, 4, 6))
            pygame.draw.circle(sprite, launcher_tube, (lx, ly), 2)
            pygame.draw.circle(sprite, launcher_tip, (lx, ly - 2), 1)

        # Add engine glow (all ships)
        for offset in [-6, 0, 6]:
            ex = cx + offset
            ey = h - 5 if ship_class != 'Jaguar' else h - 8
            pygame.draw.circle(sprite, engine_glow, (ex, ey), 3)
            pygame.draw.circle(sprite, engine_color, (ex, ey), 2)
            pygame.draw.circle(sprite, (255, 220, 150), (ex, ey), 1)

        return sprite

    def _create_polished_minmatar_ship(self):
        """Create a highly detailed top-down Minmatar ship with proper shading"""
        # Use larger canvas for detail
        w, h = 50, 60
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        ship_type = getattr(self, 'ship_class', 'Rifter')

        # Color palettes and ship-specific designs
        if ship_type == 'Wolf':
            # Wolf - darker, heavily armored assault frigate
            base = (60, 35, 25)
            mid = (100, 60, 45)
            light = (140, 90, 65)
            highlight = (180, 130, 95)
            accent = (160, 120, 60)
            armor_plate = (70, 50, 35)
            engine_color = (255, 100, 30)
            engine_glow = (255, 160, 80)

            # === WOLF HULL - Thicker, more armored ===
            # Shadow layer - wider, more aggressive
            hull_shadow = [(cx, 3), (cx+20, 22), (cx+18, 52), (cx, 58), (cx-18, 52), (cx-20, 22)]
            pygame.draw.polygon(surf, base, hull_shadow)

            # Main hull - armored plating visible
            hull_main = [(cx, 6), (cx+17, 22), (cx+15, 50), (cx, 55), (cx-15, 50), (cx-17, 22)]
            pygame.draw.polygon(surf, mid, hull_main)

            # Armor plate overlays
            pygame.draw.polygon(surf, armor_plate, [(cx-12, 20), (cx-8, 18), (cx-6, 45), (cx-10, 48)])
            pygame.draw.polygon(surf, armor_plate, [(cx+12, 20), (cx+8, 18), (cx+6, 45), (cx+10, 48)])

            # Hull highlight
            pygame.draw.polygon(surf, light, [(cx, 8), (cx+14, 22), (cx+10, 35), (cx+3, 38)])

            # Reinforced nose
            pygame.draw.polygon(surf, light, [(cx, 2), (cx+10, 16), (cx, 20), (cx-10, 16)])
            pygame.draw.polygon(surf, highlight, [(cx, 4), (cx+6, 14), (cx, 17)])

            # Heavy wing struts
            pygame.draw.polygon(surf, base, [(cx-14, 26), (3, 35), (2, 46), (10, 50), (cx-12, 44)])
            pygame.draw.polygon(surf, mid, [(cx-13, 28), (6, 36), (5, 44), (cx-11, 42)])
            pygame.draw.polygon(surf, base, [(cx+14, 26), (w-3, 35), (w-2, 46), (w-10, 50), (cx+12, 44)])
            pygame.draw.polygon(surf, light, [(cx+13, 28), (w-6, 36), (w-5, 44), (cx+11, 42)])

            # Weapon hardpoints on wings
            pygame.draw.circle(surf, (80, 60, 40), (5, 42), 4)
            pygame.draw.circle(surf, (120, 90, 60), (5, 42), 2)
            pygame.draw.circle(surf, (80, 60, 40), (w-5, 42), 4)
            pygame.draw.circle(surf, (120, 90, 60), (w-5, 42), 2)

            # Armored cockpit
            pygame.draw.ellipse(surf, (30, 45, 60), (cx-5, 12, 10, 14))
            pygame.draw.ellipse(surf, (50, 80, 110), (cx-3, 14, 6, 10))

            # Heavy engine section
            pygame.draw.polygon(surf, base, [(cx-12, 46), (cx+12, 46), (cx+10, 58), (cx-10, 58)])
            pygame.draw.ellipse(surf, engine_color, (cx-8, 53, 16, 7))
            pygame.draw.ellipse(surf, engine_glow, (cx-5, 54, 10, 5))
            pygame.draw.ellipse(surf, (255, 220, 150), (cx-3, 55, 6, 3))

            # Armor rivets
            for rx, ry in [(-8, 28), (8, 28), (-6, 38), (6, 38), (0, 32)]:
                pygame.draw.circle(surf, accent, (cx + rx, ry), 2)

        elif ship_type == 'Jaguar':
            # Jaguar - sleek, shield-focused assault frigate
            base = (40, 50, 65)
            mid = (70, 85, 105)
            light = (110, 125, 145)
            highlight = (150, 165, 185)
            accent = (60, 150, 200)
            shield_tint = (80, 180, 255)
            engine_color = (80, 180, 255)
            engine_glow = (150, 220, 255)

            # === JAGUAR HULL - Sleeker, more angular ===
            # Shadow layer - sharper angles
            hull_shadow = [(cx, 2), (cx+16, 20), (cx+14, 52), (cx, 56), (cx-14, 52), (cx-16, 20)]
            pygame.draw.polygon(surf, base, hull_shadow)

            # Main hull - streamlined
            hull_main = [(cx, 5), (cx+13, 20), (cx+11, 50), (cx, 53), (cx-11, 50), (cx-13, 20)]
            pygame.draw.polygon(surf, mid, hull_main)

            # Hull highlight - elongated
            pygame.draw.polygon(surf, light, [(cx, 7), (cx+10, 20), (cx+8, 42), (cx+2, 48)])

            # Sharp pointed nose
            pygame.draw.polygon(surf, light, [(cx, 1), (cx+8, 14), (cx, 18), (cx-8, 14)])
            pygame.draw.polygon(surf, highlight, [(cx, 3), (cx+4, 12), (cx, 15)])

            # Angular wing struts
            pygame.draw.polygon(surf, base, [(cx-10, 24), (4, 32), (2, 42), (6, 46), (cx-8, 40)])
            pygame.draw.polygon(surf, mid, [(cx-9, 26), (6, 33), (5, 40), (cx-7, 38)])
            pygame.draw.polygon(surf, base, [(cx+10, 24), (w-4, 32), (w-2, 42), (w-6, 46), (cx+8, 40)])
            pygame.draw.polygon(surf, light, [(cx+9, 26), (w-6, 33), (w-5, 40), (cx+7, 38)])

            # Shield emitters on wings (glowing)
            pygame.draw.circle(surf, shield_tint, (4, 40), 4)
            pygame.draw.circle(surf, (180, 220, 255), (4, 40), 2)
            pygame.draw.circle(surf, shield_tint, (w-4, 40), 4)
            pygame.draw.circle(surf, (180, 220, 255), (w-4, 40), 2)

            # Sleek cockpit with shield tint
            pygame.draw.ellipse(surf, (40, 70, 100), (cx-4, 12, 8, 12))
            pygame.draw.ellipse(surf, (80, 130, 180), (cx-3, 14, 6, 8))
            pygame.draw.ellipse(surf, (140, 190, 230), (cx-2, 15, 4, 5))

            # Streamlined engine section
            pygame.draw.polygon(surf, base, [(cx-8, 46), (cx+8, 46), (cx+6, 56), (cx-6, 56)])
            pygame.draw.ellipse(surf, engine_color, (cx-5, 52, 10, 6))
            pygame.draw.ellipse(surf, engine_glow, (cx-3, 53, 6, 4))
            pygame.draw.ellipse(surf, (200, 240, 255), (cx-2, 54, 4, 2))

            # Side thrusters (smaller, sleeker)
            pygame.draw.ellipse(surf, engine_color, (cx-10, 50, 4, 3))
            pygame.draw.ellipse(surf, engine_color, (cx+6, 50, 4, 3))

            # Shield effect lines
            pygame.draw.line(surf, shield_tint, (cx-6, 25), (cx-4, 42), 1)
            pygame.draw.line(surf, shield_tint, (cx+6, 25), (cx+4, 42), 1)

        else:
            # Rifter - classic rust-red industrial
            base = (70, 40, 30)
            mid = (110, 60, 40)
            light = (150, 85, 55)
            highlight = (190, 120, 80)
            accent = (200, 160, 80)
            engine_color = (255, 120, 40)
            engine_glow = (255, 180, 100)

            # === RIFTER HULL (base design) ===
            # Shadow layer (3D depth)
            hull_shadow = [(cx, 5), (cx+18, 25), (cx+15, 50), (cx, 55), (cx-15, 50), (cx-18, 25)]
            pygame.draw.polygon(surf, base, hull_shadow)

            # Main hull body
            hull_main = [(cx, 8), (cx+15, 25), (cx+12, 48), (cx, 52), (cx-12, 48), (cx-15, 25)]
            pygame.draw.polygon(surf, mid, hull_main)

            # Hull highlight (top-right lighting)
            hull_highlight = [(cx, 10), (cx+12, 25), (cx+10, 40), (cx+2, 45)]
            pygame.draw.polygon(surf, light, hull_highlight)

            # Nose section (pointed)
            pygame.draw.polygon(surf, light, [(cx, 3), (cx+8, 18), (cx, 22), (cx-8, 18)])
            pygame.draw.polygon(surf, highlight, [(cx, 5), (cx+5, 16), (cx, 18)])

            # === WING STRUTS (Minmatar asymmetric style) ===
            pygame.draw.polygon(surf, base, [(cx-12, 28), (5, 38), (3, 45), (8, 48), (cx-10, 42)])
            pygame.draw.polygon(surf, mid, [(cx-11, 30), (7, 39), (6, 44), (cx-9, 40)])
            pygame.draw.polygon(surf, base, [(cx+12, 28), (w-5, 38), (w-3, 45), (w-8, 48), (cx+10, 42)])
            pygame.draw.polygon(surf, light, [(cx+11, 30), (w-7, 39), (w-6, 44), (cx+9, 40)])

            # Wing tips
            pygame.draw.circle(surf, accent, (4, 44), 3)
            pygame.draw.circle(surf, accent, (w-4, 44), 3)

            # === COCKPIT ===
            pygame.draw.ellipse(surf, (40, 60, 80), (cx-4, 14, 8, 12))
            pygame.draw.ellipse(surf, (70, 100, 140), (cx-3, 15, 6, 8))
            pygame.draw.ellipse(surf, (120, 160, 200), (cx-2, 16, 3, 4))

            # === ENGINE SECTION ===
            pygame.draw.polygon(surf, base, [(cx-10, 45), (cx+10, 45), (cx+8, 56), (cx-8, 56)])
            pygame.draw.ellipse(surf, engine_color, (cx-6, 52, 12, 6))
            pygame.draw.ellipse(surf, engine_glow, (cx-4, 53, 8, 4))
            pygame.draw.ellipse(surf, (255, 255, 200), (cx-2, 54, 4, 2))

            # Side thrusters
            pygame.draw.ellipse(surf, engine_color, (cx-12, 50, 5, 4))
            pygame.draw.ellipse(surf, engine_color, (cx+7, 50, 5, 4))

            # Panel lines
            pygame.draw.line(surf, base, (cx, 22), (cx, 45), 1)
            pygame.draw.line(surf, accent, (cx-5, 30), (cx-5, 44), 1)
            pygame.draw.line(surf, accent, (cx+5, 30), (cx+5, 44), 1)

            # Antennae
            pygame.draw.line(surf, accent, (cx-3, 6), (cx-8, 2), 2)
            pygame.draw.circle(surf, highlight, (cx-8, 2), 2)
            pygame.draw.line(surf, accent, (cx+3, 6), (cx+6, 3), 1)

        # === EDGE GLOW (for visibility) ===
        # Create glow by drawing slightly larger behind
        glow_surf = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        for i in range(4, 0, -1):
            alpha = 30 // i
            glow_color = (*engine_color[:3], alpha)
            offset = i
            # Draw hull outline as glow
            glow_hull = [(cx+4, 8+offset), (cx+4+15, 25), (cx+4+12, 48), (cx+4, 52-offset),
                        (cx+4-12, 48), (cx+4-15, 25)]
            pygame.draw.polygon(glow_surf, glow_color, glow_hull, 2)

        # Combine glow with ship
        final_surf = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        final_surf.blit(glow_surf, (0, 0))
        final_surf.blit(surf, (4, 4))

        self.width = w + 8
        self.height = h + 8

        return final_surf

    def _create_fallback_ship_image(self):
        """Fallback ship sprite - Minmatar rust-red industrial style with 3D shading"""
        w, h = self.width, self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Minmatar color palette - rust, copper, industrial
        if self.ship_class == 'Wolf':
            # Wolf - darker, more armored look
            hull_dark = (100, 50, 40)
            hull_mid = (140, 70, 50)
            hull_light = (180, 100, 70)
            accent = (200, 150, 80)  # Copper accent
            engine = (255, 150, 50)
        elif self.ship_class == 'Jaguar':
            # Jaguar - sleeker, more blue-ish tint
            hull_dark = (70, 60, 80)
            hull_mid = (100, 90, 110)
            hull_light = (140, 130, 150)
            accent = (100, 180, 200)  # Cyan accent
            engine = (100, 200, 255)
        else:
            # Rifter - classic rust red
            hull_dark = (90, 45, 35)
            hull_mid = (130, 65, 45)
            hull_light = (170, 95, 65)
            accent = (220, 180, 100)  # Brass
            engine = (255, 120, 50)

        # Main hull body - angular Minmatar design
        # Back section (widest)
        pygame.draw.polygon(surf, hull_dark, [
            (cx-12, h-8), (cx+12, h-8), (cx+8, h-20), (cx-8, h-20)
        ])

        # Mid section with 3D bevel
        pygame.draw.polygon(surf, hull_mid, [
            (cx-10, h-18), (cx+10, h-18), (cx+6, h//2), (cx-6, h//2)
        ])
        # Left bevel (shadow)
        pygame.draw.polygon(surf, hull_dark, [
            (cx-10, h-18), (cx-6, h//2), (cx-8, h//2+5), (cx-12, h-15)
        ])
        # Right bevel (highlight)
        pygame.draw.polygon(surf, hull_light, [
            (cx+10, h-18), (cx+6, h//2), (cx+4, h//2-3), (cx+8, h-20)
        ])

        # Nose cone
        pygame.draw.polygon(surf, hull_mid, [
            (cx, 4), (cx-5, h//2-5), (cx+5, h//2-5)
        ])
        # Nose highlight
        pygame.draw.polygon(surf, hull_light, [
            (cx, 6), (cx+4, h//2-8), (cx+2, h//2-5)
        ])

        # Wing struts - asymmetric Minmatar style
        # Left wing
        pygame.draw.polygon(surf, hull_dark, [
            (cx-8, h//2+5), (2, h//2+15), (4, h//2+5), (cx-6, h//2)
        ])
        pygame.draw.polygon(surf, hull_mid, [
            (cx-6, h//2), (4, h//2+5), (6, h//2-2), (cx-4, h//2-5)
        ])

        # Right wing
        pygame.draw.polygon(surf, hull_dark, [
            (cx+8, h//2+5), (w-2, h//2+15), (w-4, h//2+5), (cx+6, h//2)
        ])
        pygame.draw.polygon(surf, hull_mid, [
            (cx+6, h//2), (w-4, h//2+5), (w-6, h//2-2), (cx+4, h//2-5)
        ])

        # Cockpit window
        pygame.draw.ellipse(surf, (60, 80, 100), (cx-3, h//3, 6, 8))
        pygame.draw.ellipse(surf, (100, 140, 180), (cx-2, h//3+1, 4, 5))

        # Engine glow
        pygame.draw.ellipse(surf, engine, (cx-6, h-6, 12, 5))
        pygame.draw.ellipse(surf, (255, 220, 150), (cx-3, h-5, 6, 3))

        # Panel lines (detail)
        pygame.draw.line(surf, hull_dark, (cx, h//3+10), (cx, h-15), 1)
        pygame.draw.line(surf, accent, (cx-4, h//2+10), (cx-4, h-12), 1)
        pygame.draw.line(surf, accent, (cx+4, h//2+10), (cx+4, h-12), 1)

        # Antenna/sensor (Minmatar flair)
        pygame.draw.line(surf, accent, (cx-2, 8), (cx-6, 2), 1)
        pygame.draw.circle(surf, accent, (cx-6, 2), 2)

        return surf
    def upgrade_to_wolf(self):
        """Upgrade to Wolf assault frigate"""
        self.is_wolf = True
        self.ship_class = 'Wolf'
        self.speed *= WOLF_SPEED_BONUS
        self.max_armor += WOLF_ARMOR_BONUS
        self.max_hull += WOLF_HULL_BONUS
        self.armor = min(self.armor + WOLF_ARMOR_BONUS, self.max_armor)
        self.hull = min(self.hull + WOLF_HULL_BONUS, self.max_hull)
        self.spread_bonus += 1
        self.image = self._create_ship_image()

    def upgrade_to_jaguar(self):
        """Upgrade to Jaguar assault frigate - fast, agile, rocket specialist"""
        from constants import JAGUAR_SPEED_BONUS, JAGUAR_SHIELD_BONUS
        self.is_wolf = True  # T2 flag
        self.ship_class = 'Jaguar'
        # Jaguar is the fastest assault frigate
        self.speed *= JAGUAR_SPEED_BONUS * 1.15  # Extra 15% on top of base bonus
        self.max_shields += JAGUAR_SHIELD_BONUS
        self.shields = min(self.shields + JAGUAR_SHIELD_BONUS, self.max_shields)
        # Faster barrel roll cooldown (agile ship)
        self.barrel_roll_cooldown_time = 120  # 2 seconds instead of 3
        # Rocket specialist: increased rocket capacity (4 launchers)
        self.max_rockets = 16  # More rockets
        self.rockets = min(self.rockets + 6, self.max_rockets)  # Bonus rockets on upgrade
        self.image = self._create_ship_image()

    def can_use_ability(self):
        """Check if ship ability is ready"""
        return self.ability_cooldown <= 0

    def is_ability_active(self):
        """Check if ability effect is currently active"""
        return pygame.time.get_ticks() < self.ability_active_until

    def use_ability(self):
        """
        Activate ship special ability.
        Returns (success, ability_name) tuple.

        Abilities:
        - Rifter: "Minmatar Grit" - 50% damage resistance for 3s
        - Wolf: "Overdrive" - 50% speed + 25% damage for 3s
        - Jaguar: "Shield Overload" - Restore 50 shields instantly
        """
        if self.ability_cooldown > 0:
            return False, None

        ship_class = getattr(self, 'ship_class', 'Rifter')
        current_time = pygame.time.get_ticks()

        if ship_class == 'Rifter':
            # Minmatar Grit - damage resistance
            self.ability_active_until = current_time + 3000
            self.ability_cooldown = self.ability_base_cooldown
            return True, 'Minmatar Grit'

        elif ship_class == 'Wolf':
            # Overdrive - speed and damage boost
            self.ability_active_until = current_time + 3000
            self.overdrive_until = current_time + 3000  # Uses existing overdrive
            self.ability_cooldown = self.ability_base_cooldown
            return True, 'Overdrive'

        elif ship_class == 'Jaguar':
            # Shield Overload - instant shield restore
            shield_restore = 50
            self.shields = min(self.shields + shield_restore, self.max_shields)
            self.ability_cooldown = self.ability_base_cooldown
            return True, 'Shield Overload'

        return False, None

    def get_ability_info(self):
        """Get info about ship's ability for HUD display"""
        ship_class = getattr(self, 'ship_class', 'Rifter')

        abilities = {
            'Rifter': {
                'name': 'Minmatar Grit',
                'desc': '50% damage resistance',
                'key': 'F'
            },
            'Wolf': {
                'name': 'Overdrive',
                'desc': 'Speed + damage boost',
                'key': 'F'
            },
            'Jaguar': {
                'name': 'Shield Overload',
                'desc': 'Restore 50 shields',
                'key': 'F'
            }
        }
        return abilities.get(ship_class, abilities['Rifter'])

    def get_damage_resistance(self):
        """Get current damage resistance multiplier (1.0 = no resistance)"""
        ship_class = getattr(self, 'ship_class', 'Rifter')
        if ship_class == 'Rifter' and self.is_ability_active():
            return 0.5  # 50% damage reduction
        return 1.0

    def get_damage_bonus(self):
        """Get current damage bonus multiplier"""
        bonus = 1.0
        ship_class = getattr(self, 'ship_class', 'Rifter')
        if ship_class == 'Wolf' and self.is_ability_active():
            bonus *= 1.25  # 25% damage boost from ability
        # Double damage powerup
        if pygame.time.get_ticks() < self.double_damage_until:
            bonus *= 2.0
        return bonus

    def get_fire_rate_bonus(self):
        """Get current fire rate multiplier from powerups and ship bonuses"""
        bonus = 1.0

        # Wolf: 25% faster fire rate (rapid fire autocannons)
        ship_class = getattr(self, 'ship_class', 'Rifter')
        if ship_class == 'Wolf':
            bonus = 1.25

        # Rapid fire powerup stacks
        if pygame.time.get_ticks() < self.rapid_fire_until:
            bonus *= 2.0  # Double fire rate

        return bonus

    def is_invulnerable(self):
        """Check if player is invulnerable"""
        return pygame.time.get_ticks() < self.invulnerable_until

    def has_magnet(self):
        """Check if magnet powerup is active"""
        return pygame.time.get_ticks() < self.magnet_until

    def update_ability_cooldown(self):
        """Update ability cooldown timer (call each frame)"""
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1

    def can_use_bomb(self):
        """Check if bomb is ready"""
        return self.bombs > 0 and self.bomb_cooldown <= 0

    def use_bomb(self):
        """Use a screen-clearing bomb. Returns True if successful."""
        if not self.can_use_bomb():
            return False
        self.bombs -= 1
        self.bomb_cooldown = self.bomb_base_cooldown
        return True

    def add_bomb(self, count=1):
        """Add bombs (from powerups)"""
        self.bombs = min(self.bombs + count, self.max_bombs)

    def unlock_ammo(self, ammo_type):
        """Unlock new ammo type"""
        if ammo_type not in self.unlocked_ammo:
            self.unlocked_ammo.append(ammo_type)
    
    def switch_ammo(self, ammo_type):
        """Switch to specified ammo type if unlocked"""
        if ammo_type in self.unlocked_ammo:
            self.current_ammo = ammo_type
            return True
        return False
    
    def cycle_ammo(self, reverse=False):
        """Cycle to next/previous unlocked ammo type"""
        idx = self.unlocked_ammo.index(self.current_ammo)
        if reverse:
            idx = (idx - 1) % len(self.unlocked_ammo)
        else:
            idx = (idx + 1) % len(self.unlocked_ammo)
        self.current_ammo = self.unlocked_ammo[idx]
    
    def update(self, keys):
        """Update player position based on input"""
        current_speed = self.speed
        if pygame.time.get_ticks() < self.overdrive_until:
            current_speed *= 1.5

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += current_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= current_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += current_speed

        # Keep on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Weapon heat management
        if self.is_overheated:
            self.overheat_cooldown -= 1
            if self.overheat_cooldown <= 0:
                self.is_overheated = False
                self.heat = 0
        else:
            # Dissipate heat over time
            self.heat = max(0, self.heat - self.heat_dissipation)

        # Assault frigate passive regen (every 60 frames = 1 second)
        ship_class = getattr(self, 'ship_class', 'Rifter')
        if ship_class == 'Wolf':
            # Wolf: Armor tank - passive armor regen (0.5 armor/sec)
            if not hasattr(self, '_regen_counter'):
                self._regen_counter = 0
            self._regen_counter += 1
            if self._regen_counter >= 120:  # Every 2 seconds
                self._regen_counter = 0
                if self.armor < self.max_armor:
                    self.armor = min(self.armor + 1, self.max_armor)
        elif ship_class == 'Jaguar':
            # Jaguar: Shield tank - passive shield regen (1 shield/sec)
            if not hasattr(self, '_regen_counter'):
                self._regen_counter = 0
            self._regen_counter += 1
            if self._regen_counter >= 60:  # Every second
                self._regen_counter = 0
                if self.shields < self.max_shields:
                    self.shields = min(self.shields + 1, self.max_shields)

    def can_shoot(self):
        """Check if enough time has passed to fire"""
        # Can't shoot if overheated
        if self.is_overheated:
            return False

        now = pygame.time.get_ticks()
        ammo = AMMO_TYPES[self.current_ammo]
        fire_rate = ammo['fire_rate'] * self.fire_rate_mult * self.get_fire_rate_bonus()
        cooldown = PLAYER_BASE_FIRE_RATE / fire_rate
        return now - self.last_shot > cooldown
    
    def shoot(self):
        """Fire autocannons, returns list of bullets"""
        if not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()
        bullets = []
        ammo = AMMO_TYPES[self.current_ammo]
        ship_class = getattr(self, 'ship_class', 'Rifter')

        # Apply damage bonus from abilities
        damage_bonus = self.get_damage_bonus()
        bullet_damage = int(BULLET_DAMAGE * damage_bonus)

        # Wolf: 4 autocannons with wide spread pattern
        if ship_class == 'Wolf':
            num_shots = 4
            spread = 22  # Wider spread for 4 guns
            # Slight angular spread for more coverage
            angles = [-8, -3, 3, 8]  # degrees from vertical
            for i, angle in enumerate(angles):
                offset = (i - 1.5) * spread
                # Convert angle to velocity components
                rad = math.radians(angle)
                vx = math.sin(rad) * BULLET_SPEED * 0.3
                vy = -BULLET_SPEED
                bullet = Bullet(
                    self.rect.centerx + offset,
                    self.rect.top,
                    vx, vy,
                    ammo['tracer'],
                    bullet_damage,
                    ammo['shield_mult'],
                    ammo['armor_mult']
                )
                bullet.color = ammo['tracer']
                bullets.append(bullet)
        elif ship_class == 'Jaguar':
            # Jaguar: 2 autocannons only (rocket specialist)
            num_shots = 2
            spread = 16
            for i in range(num_shots):
                offset = (i - 0.5) * spread
                bullet = Bullet(
                    self.rect.centerx + offset,
                    self.rect.top,
                    0, -BULLET_SPEED,
                    ammo['tracer'],
                    bullet_damage,
                    ammo['shield_mult'],
                    ammo['armor_mult']
                )
                bullet.color = ammo['tracer']
                bullets.append(bullet)
        else:
            # Standard Rifter: base shots
            num_shots = 2 + self.spread_bonus
            spread = 15 + (self.spread_bonus * 5)

            for i in range(num_shots):
                offset = (i - (num_shots - 1) / 2) * spread
                bullet = Bullet(
                    self.rect.centerx + offset,
                    self.rect.top,
                    0, -BULLET_SPEED,
                    ammo['tracer'],
                    bullet_damage,
                    ammo['shield_mult'],
                    ammo['armor_mult']
                )
                bullet.color = ammo['tracer']
                bullets.append(bullet)

        # Add heat when firing
        now = pygame.time.get_ticks()
        heat_to_add = self.heat_per_shot

        # Wolf: 4 guns = 40% more heat buildup (trade-off for firepower)
        if ship_class == 'Wolf':
            heat_to_add = int(self.heat_per_shot * 1.4)

        # Add 50% extra heat if any offensive powerup is active
        if (now < self.double_damage_until or now < self.rapid_fire_until or
            now < self.overdrive_until):
            heat_to_add = int(heat_to_add * 1.5)
        self.heat += heat_to_add
        if self.heat >= self.max_heat:
            self.is_overheated = True
            self.overheat_cooldown = self.overheat_duration
            # Expire all powerups when overheated
            self.expire_all_powerups()

        return bullets

    def expire_all_powerups(self):
        """Expire all active powerups (called when overheating)"""
        now = pygame.time.get_ticks()
        # Reset all timed powerup effects
        self.overdrive_until = 0
        self.shield_boost_until = 0
        self.double_damage_until = 0
        self.rapid_fire_until = 0
        self.magnet_until = 0
        # Note: invulnerability from maneuvers should not be affected
        # Only expire invulnerability if it's a powerup (long duration)
        if self.invulnerable_until > now + 1000:  # More than 1 second remaining = powerup
            self.invulnerable_until = 0
    
    def can_rocket(self):
        """Check if can fire rocket"""
        now = pygame.time.get_ticks()
        # Jaguar: 4 rocket launchers = 40% faster rocket cooldown
        ship_class = getattr(self, 'ship_class', 'Rifter')
        cooldown = PLAYER_ROCKET_COOLDOWN
        if ship_class == 'Jaguar':
            cooldown = int(PLAYER_ROCKET_COOLDOWN * 0.6)
        return self.rockets > 0 and now - self.last_rocket > cooldown

    def shoot_rocket(self):
        """Fire rocket, returns rocket(s) or None/empty list"""
        if not self.can_rocket():
            return None

        self.last_rocket = pygame.time.get_ticks()
        ship_class = getattr(self, 'ship_class', 'Rifter')

        # Jaguar: Fire 2 rockets at once (from 4 launchers, alternating pairs)
        if ship_class == 'Jaguar':
            rockets = []
            for offset in [-12, 12]:
                self.rockets -= 1
                if self.rockets < 0:
                    self.rockets = 0
                    break
                rocket = Rocket(self.rect.centerx + offset, self.rect.top)
                rocket.damage = int(ROCKET_DAMAGE * self.get_damage_bonus())
                rockets.append(rocket)
            return rockets if rockets else None
        else:
            self.rockets -= 1
            rocket = Rocket(self.rect.centerx, self.rect.top)
            # Apply damage bonus from abilities
            rocket.damage = int(ROCKET_DAMAGE * self.get_damage_bonus())
            return rocket
    
    def take_damage(self, amount):
        """Apply damage through shields -> armor -> hull"""
        # Check invulnerability
        if self.is_invulnerable():
            return False  # No damage taken

        if pygame.time.get_ticks() < self.shield_boost_until:
            amount *= 0.3  # 70% damage reduction

        # Shields first
        if self.shields > 0:
            absorbed = min(self.shields, amount)
            self.shields -= absorbed
            amount -= absorbed
        
        # Then armor
        if amount > 0 and self.armor > 0:
            absorbed = min(self.armor, amount)
            self.armor -= absorbed
            amount -= absorbed
        
        # Finally hull
        if amount > 0:
            self.hull -= amount
        
        return self.hull <= 0  # Return True if dead
    
    def heal(self, amount):
        """Repair hull and armor"""
        self.hull = min(self.hull + amount, self.max_hull)
        remaining = amount - (self.max_hull - self.hull)
        if remaining > 0:
            self.armor = min(self.armor + remaining, self.max_armor)
    
    def add_rockets(self, amount):
        """Add rockets up to max"""
        self.rockets = min(self.rockets + amount, self.max_rockets)
    
    def collect_refugee(self, count=1):
        """Collect refugees"""
        self.refugees += count
        self.total_refugees += count
        self.score += count * 10


class Wingman(pygame.sprite.Sprite):
    """Allied Minmatar frigate that assists the player during boss fights"""

    def __init__(self, player, offset_x):
        super().__init__()
        self.player = player
        self.offset_x = offset_x  # Position relative to player
        self.width = 30
        self.height = 38

        # Create Minmatar frigate sprite
        self.image = self._create_wingman_sprite()
        self.rect = self.image.get_rect()

        # Stats
        self.health = 50
        self.max_health = 50
        self.speed = 6

        # Shooting
        self.fire_rate = 400  # ms between shots
        self.last_shot = 0
        self.damage = 8

    def _create_wingman_sprite(self):
        """Create a small Minmatar frigate sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        w, h = self.width, self.height
        cx = w // 2

        # Minmatar colors
        hull = (139, 90, 43)
        hull_dark = (100, 65, 30)
        accent = (180, 100, 50)
        engine = (255, 120, 40)

        # Main hull (angular)
        points = [
            (cx, 2),           # Nose
            (w - 4, h // 3),   # Right front
            (w - 2, h - 8),    # Right rear
            (cx, h - 4),       # Tail
            (2, h - 8),        # Left rear
            (4, h // 3),       # Left front
        ]
        pygame.draw.polygon(surf, hull, points)
        pygame.draw.polygon(surf, hull_dark, points, 1)

        # Wing struts
        pygame.draw.line(surf, accent, (cx, h // 3), (2, h - 10), 2)
        pygame.draw.line(surf, accent, (cx, h // 3), (w - 2, h - 10), 2)

        # Engine glow
        pygame.draw.circle(surf, engine, (cx - 4, h - 5), 3)
        pygame.draw.circle(surf, engine, (cx + 4, h - 5), 3)
        pygame.draw.circle(surf, (255, 200, 100), (cx - 4, h - 5), 1)
        pygame.draw.circle(surf, (255, 200, 100), (cx + 4, h - 5), 1)

        # Cockpit
        pygame.draw.ellipse(surf, (60, 80, 100), (cx - 3, 6, 6, 8))

        return surf

    def update(self):
        """Follow player with offset"""
        if self.player:
            target_x = self.player.rect.centerx + self.offset_x
            target_y = self.player.rect.centery + 40  # Slightly behind

            # Smooth movement towards target position
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery

            if abs(dx) > 2:
                self.rect.x += self.speed if dx > 0 else -self.speed
            if abs(dy) > 2:
                self.rect.y += self.speed if dy > 0 else -self.speed

            # Keep on screen
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def can_shoot(self):
        """Check if wingman can fire"""
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate

    def shoot(self):
        """Fire autocannon, returns bullet or None"""
        if not self.can_shoot():
            return None

        self.last_shot = pygame.time.get_ticks()
        bullet = Bullet(
            self.rect.centerx,
            self.rect.top,
            0, -BULLET_SPEED,
            (200, 150, 100),  # Minmatar tracer color
            self.damage,
            1.0, 1.0
        )
        return bullet

    def take_damage(self, amount):
        """Take damage, returns True if destroyed"""
        self.health -= amount
        return self.health <= 0


class Bullet(pygame.sprite.Sprite):
    """Projectile sprite with tracer glow effect"""

    def __init__(self, x, y, dx, dy, color, damage, shield_mult=1.0, armor_mult=1.0):
        super().__init__()
        # Larger surface for glow effect
        self.image = pygame.Surface((16, 24), pygame.SRCALPHA)

        # Outer glow
        glow_color = (*color[:3], 60)
        pygame.draw.ellipse(self.image, glow_color, (2, 4, 12, 18))

        # Middle glow
        mid_color = (*color[:3], 120)
        pygame.draw.ellipse(self.image, mid_color, (4, 6, 8, 14))

        # Core tracer
        pygame.draw.rect(self.image, color, (6, 6, 4, 14))

        # Bright tip
        pygame.draw.ellipse(self.image, (255, 255, 255), (5, 4, 6, 6))

        # Trail fade
        trail_color = (*color[:3], 40)
        pygame.draw.rect(self.image, trail_color, (6, 16, 4, 6))

        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.shield_mult = shield_mult
        self.armor_mult = armor_mult
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()


class Rocket(pygame.sprite.Sprite):
    """Rocket projectile"""
    
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        # Rocket body
        pygame.draw.rect(self.image, (150, 150, 150), (2, 5, 4, 15))
        # Nose cone
        pygame.draw.polygon(self.image, (200, 50, 50), [(4, 0), (0, 8), (8, 8)])
        # Exhaust
        pygame.draw.polygon(self.image, (255, 200, 50), [(2, 18), (4, 22), (6, 18)])
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = ROCKET_DAMAGE
        self.shield_mult = 1.2
        self.armor_mult = 1.2
    
    def update(self):
        self.rect.y -= ROCKET_SPEED
        if self.rect.bottom < 0:
            self.kill()


class EnemyBullet(pygame.sprite.Sprite):
    """Enemy laser projectile"""
    
    def __init__(self, x, y, dx, dy, damage=10):
        super().__init__()
        self.image = pygame.Surface((4, 16), pygame.SRCALPHA)
        # Yellow/gold Amarr laser
        pygame.draw.rect(self.image, (255, 220, 100), (0, 0, 4, 16))
        pygame.draw.rect(self.image, (255, 255, 200), (1, 0, 2, 16))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.damage = damage
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """Base enemy class"""

    # Movement pattern types
    PATTERN_DRIFT = 0      # Basic side-to-side drift
    PATTERN_SINE = 1       # Sine wave movement
    PATTERN_ZIGZAG = 2     # Sharp zigzag
    PATTERN_CIRCLE = 3     # Circular strafing
    PATTERN_SWOOP = 4      # Dive toward player then retreat
    PATTERN_FLANK = 5      # Move to screen edge then track player
    PATTERN_SWARM = 6      # Drone swarm behavior - surround and track player
    
    def __init__(self, enemy_type, x, y, difficulty=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.stats = ENEMY_STATS[enemy_type]
        self.difficulty = difficulty or {}
        
        self.width, self.height = self.stats['size']
        
        # Apply difficulty scaling
        health_mult = self.difficulty.get('enemy_health_mult', 1.0)
        
        # Combat stats
        self.shields = int(self.stats['shields'] * health_mult)
        self.armor = int(self.stats['armor'] * health_mult)
        self.hull = int(self.stats['hull'] * health_mult)
        self.max_shields = self.shields
        self.max_armor = self.armor
        self.max_hull = self.hull
        
        # Behavior
        self.speed = self.stats['speed']
        fire_rate_mult = self.difficulty.get('enemy_fire_rate_mult', 1.0)
        self.fire_rate = int(self.stats['fire_rate'] * fire_rate_mult)
        self.last_shot = pygame.time.get_ticks() + random.randint(0, 1000)
        self.score = self.stats['score']
        self.refugees = self.stats.get('refugees', 0)
        self.is_boss = self.stats.get('boss', False)
        
        # Create image after all attributes are set
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))
        
        # Movement pattern selection based on enemy type
        self._select_movement_pattern()
        
        # Pattern state variables
        self.pattern_timer = random.uniform(0, math.pi * 2)
        self.target_y = self._get_target_y()
        self.entered = False  # Has reached initial position
        self.swoop_state = 'enter'  # For swoop pattern
        self.flank_side = random.choice([-1, 1])  # For flank pattern
        self.circle_center_x = x
        self.circle_radius = random.randint(50, 100)
        
        # Boss-specific behavior
        if self.is_boss:
            self.boss_phase = 0
            self.boss_phase_timer = 0
            self.boss_attack_timer = 0
            self.boss_special_cooldown = 0
            self.boss_charging = False
            self.boss_charge_timer = 0
            self.boss_attack_type = None
            self.summon_count = 0
            self.max_summons = 3
            # Enrage at 20% health
            self.is_enraged = False
            self.enrage_threshold = 0.2
            # Drone stream attack
            self.drone_stream_cooldown = 0
            self.drones_to_spawn = []  # Queue of drones to spawn
    
    def _select_movement_pattern(self):
        """Select movement pattern based on enemy type"""
        behavior = self.stats.get('behavior', None)

        if self.is_boss:
            self.pattern = self.PATTERN_DRIFT  # Bosses use simple patterns
        elif behavior == 'swarm':
            # Drones - aggressive swarming behavior
            self.pattern = self.PATTERN_SWARM
            # Swarm behavior state
            self.swarm_angle = random.uniform(0, math.pi * 2)  # Orbit angle
            self.swarm_radius = random.randint(60, 120)  # Distance from swarm center
            self.swarm_speed = random.uniform(0.03, 0.06)  # Orbit speed
            self.swarm_approach_timer = 0  # Timer for attack runs
            self.swarm_state = 'orbit'  # orbit, attack, retreat
        elif behavior == 'bomber':
            # Bombers - slow steady approach
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.7
        elif behavior == 'aggressive':
            # Interceptors - dive at player
            self.pattern = self.PATTERN_SWOOP
        elif behavior == 'strafe':
            # Coercer - circle strafe
            self.pattern = self.PATTERN_CIRCLE
        elif behavior == 'artillery':
            # Harbinger - stay at range
            self.pattern = self.PATTERN_FLANK
        elif behavior == 'drone_carrier':
            # Dragoon - steady with drone spawns
            self.pattern = self.PATTERN_DRIFT
            self.drone_timer = 0
            self.drones_spawned = 0
            self.max_drones = self.stats.get('drones', 2)
        elif self.enemy_type == 'executioner':
            self.pattern = random.choice([
                self.PATTERN_SINE, self.PATTERN_ZIGZAG,
                self.PATTERN_SWOOP, self.PATTERN_FLANK
            ])
        elif self.enemy_type == 'punisher':
            self.pattern = random.choice([
                self.PATTERN_DRIFT, self.PATTERN_SINE, self.PATTERN_CIRCLE
            ])
        elif self.enemy_type in ['omen', 'maller']:
            self.pattern = random.choice([
                self.PATTERN_CIRCLE, self.PATTERN_FLANK, self.PATTERN_DRIFT
            ])
        elif self.enemy_type == 'bestower':
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.8
        else:
            self.pattern = self.PATTERN_DRIFT
    
    def _get_target_y(self):
        """Get target Y position based on enemy type"""
        if self.is_boss:
            return 120
        elif self.enemy_type == 'bestower':
            return random.randint(80, 180)
        else:
            return random.randint(80, 300)
    
    def _create_image(self):
        """Create polished top-down Amarr ship sprite"""
        # Try to load rendered sprite from the sprite map
        sprite_name = ENEMY_SPRITE_MAP.get(self.enemy_type)
        if sprite_name:
            sprite = load_ship_sprite(sprite_name, (self.width, self.height))
            if sprite:
                # Add engine glow and flip so nose points down (enemy faces player)
                sprite = pygame.transform.flip(sprite, False, True)
                return self._add_enemy_engine_effects(sprite)

        # Fall back to procedural generation
        return self._create_polished_amarr_ship()

    def _add_enemy_engine_effects(self, sprite):
        """Add engine glow effects to enemy sprites"""
        w, h = sprite.get_size()
        engine_color = (255, 120, 50)
        engine_glow = (255, 180, 100)

        # Engines at top (since sprite is flipped)
        for offset in [-6, 0, 6]:
            cx = w // 2 + offset
            pygame.draw.circle(sprite, engine_glow, (cx, 4), 2)
            pygame.draw.circle(sprite, engine_color, (cx, 4), 1)

        return sprite

    def _create_polished_amarr_ship(self):
        """Create a highly detailed top-down Amarr ship with golden aesthetic"""
        w, h = self.width, self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Amarr golden color palette
        gold_dark = (100, 75, 30)
        gold_mid = (160, 130, 50)
        gold_light = (210, 180, 90)
        gold_highlight = (255, 230, 150)
        hull_shadow = (60, 45, 20)
        accent_red = (150, 50, 40)
        engine_color = (255, 120, 50)
        engine_glow = (255, 180, 100)
        cockpit_color = (60, 80, 120)

        # === BESTOWER INDUSTRIAL SHIP ===
        if self.enemy_type == 'bestower':
            # Bestower is a long hauler with cargo bays - distinctive industrial shape
            # Main elongated hull
            hull_outer = [
                (cx, 5), (cx + 20, 15), (cx + 25, h//4),
                (cx + 30, h//2), (cx + 25, h*3//4), (cx + 15, h - 20), (cx, h - 5),
                (cx - 15, h - 20), (cx - 25, h*3//4), (cx - 30, h//2),
                (cx - 25, h//4), (cx - 20, 15)
            ]
            pygame.draw.polygon(surf, hull_shadow, hull_outer)

            # Main hull body
            hull_main = [
                (cx, 10), (cx + 17, 18), (cx + 22, h//4),
                (cx + 26, h//2), (cx + 22, h*3//4), (cx + 12, h - 22), (cx, h - 10),
                (cx - 12, h - 22), (cx - 22, h*3//4), (cx - 26, h//2),
                (cx - 22, h//4), (cx - 17, 18)
            ]
            pygame.draw.polygon(surf, gold_mid, hull_main)

            # Highlight on hull
            pygame.draw.polygon(surf, gold_light, [
                (cx, 12), (cx + 15, 20), (cx + 18, h//3), (cx + 5, h//3 + 10)
            ])

            # Cargo bay sections (3 large rectangular sections)
            cargo_color = (80, 60, 30)
            cargo_highlight = (120, 90, 50)
            for i, y_pos in enumerate([h//4, h//2, h*3//4 - 10]):
                bay_w = 35 if i == 1 else 28
                pygame.draw.rect(surf, cargo_color, (cx - bay_w//2, y_pos - 8, bay_w, 18), border_radius=3)
                pygame.draw.rect(surf, cargo_highlight, (cx - bay_w//2 + 2, y_pos - 6, bay_w - 4, 14), border_radius=2)
                # Cargo lines
                for j in range(3):
                    lx = cx - bay_w//2 + 6 + j * (bay_w // 3 - 2)
                    pygame.draw.line(surf, gold_dark, (lx, y_pos - 4), (lx, y_pos + 8), 1)

            # Bridge section at front
            pygame.draw.ellipse(surf, cockpit_color, (cx - 8, 12, 16, 20))
            pygame.draw.ellipse(surf, (80, 110, 150), (cx - 5, 15, 10, 14))
            pygame.draw.ellipse(surf, (120, 150, 190), (cx - 3, 17, 6, 8))

            # Side cargo pods
            pod_color = (90, 70, 40)
            pod_light = (130, 100, 60)
            for side in [-1, 1]:
                pod_x = cx + side * 32
                pygame.draw.ellipse(surf, pod_color, (pod_x - 8, h//3, 16, 40))
                pygame.draw.ellipse(surf, pod_light, (pod_x - 5, h//3 + 4, 10, 32))

            # Engine section
            pygame.draw.rect(surf, hull_shadow, (cx - 18, h - 18, 36, 14), border_radius=3)
            # Multiple small engines (industrial)
            for offset in [-10, 0, 10]:
                pygame.draw.ellipse(surf, accent_red, (cx + offset - 4, h - 12, 8, 8))
                pygame.draw.ellipse(surf, engine_color, (cx + offset - 2, h - 10, 4, 5))
                pygame.draw.ellipse(surf, engine_glow, (cx + offset - 1, h - 9, 2, 3))

            # Antenna arrays
            pygame.draw.line(surf, gold_light, (cx - 10, 8), (cx - 18, 3), 2)
            pygame.draw.circle(surf, (180, 200, 220), (cx - 18, 3), 3)
            pygame.draw.line(surf, gold_light, (cx + 10, 8), (cx + 18, 3), 2)
            pygame.draw.circle(surf, (180, 200, 220), (cx + 18, 3), 3)

            return surf

        if self.is_boss or h > 80:
            # === LARGE SHIP (Battleship/Boss) - Enhanced detail ===
            # Main hull - elongated diamond shape (Amarr aesthetic)
            hull_outer = [(cx, 5), (w-8, h//3), (w-5, h*2//3), (cx, h-5), (5, h*2//3), (8, h//3)]
            pygame.draw.polygon(surf, hull_shadow, hull_outer)

            hull_main = [(cx, 10), (w-12, h//3), (w-10, h*2//3-5), (cx, h-10), (10, h*2//3-5), (12, h//3)]
            pygame.draw.polygon(surf, gold_mid, hull_main)

            # 3D highlights with more definition
            pygame.draw.polygon(surf, gold_light, [(cx, 12), (w-14, h//3), (w-16, h//3+10), (cx+5, 20)])
            pygame.draw.polygon(surf, gold_dark, [(cx, 12), (14, h//3), (16, h//3+10), (cx-5, 20)])

            # Hull panel lines for detail
            for i in range(3):
                y_pos = h//4 + i * (h//6)
                pygame.draw.line(surf, gold_dark, (cx-w//4, y_pos), (cx+w//4, y_pos), 1)
            # Vertical panel lines
            pygame.draw.line(surf, gold_dark, (cx-w//6, h//5), (cx-w//6, h*2//3), 1)
            pygame.draw.line(surf, gold_dark, (cx+w//6, h//5), (cx+w//6, h*2//3), 1)

            # Central dome (Amarr religious architecture) - more layered
            pygame.draw.ellipse(surf, gold_dark, (cx-15, h//3-5, 30, 25))
            pygame.draw.ellipse(surf, gold_mid, (cx-12, h//3-2, 24, 20))
            pygame.draw.ellipse(surf, gold_light, (cx-8, h//3+2, 16, 12))
            pygame.draw.ellipse(surf, gold_highlight, (cx-4, h//3+5, 8, 6))
            # Dome highlight sparkle
            pygame.draw.circle(surf, (255, 255, 220), (cx-2, h//3+4), 2)

            # Wing panels with more detail
            pygame.draw.polygon(surf, gold_dark, [(8, h//2-5), (2, h//2+15), (10, h*2//3)])
            pygame.draw.polygon(surf, gold_mid, [(10, h//2-3), (5, h//2+12), (12, h*2//3-5)])
            pygame.draw.polygon(surf, gold_dark, [(w-8, h//2-5), (w-2, h//2+15), (w-10, h*2//3)])
            pygame.draw.polygon(surf, gold_light, [(w-10, h//2-3), (w-5, h//2+12), (w-12, h*2//3-5)])

            # Weapon turret hardpoints (dorsal)
            turret_color = (80, 60, 30)
            turret_highlight = (140, 110, 60)
            for tx, ty in [(cx-w//5, h//4+5), (cx+w//5, h//4+5), (cx, h//2+10)]:
                pygame.draw.circle(surf, turret_color, (tx, ty), 5)
                pygame.draw.circle(surf, turret_highlight, (tx, ty), 3)
                pygame.draw.circle(surf, gold_highlight, (tx-1, ty-1), 1)

            # Window lights (small glowing dots along hull)
            window_color = (200, 220, 255)
            window_glow = (150, 180, 220)
            for i in range(4):
                wx = cx - w//5 + i * (w//8)
                wy = h//3 + 20
                pygame.draw.circle(surf, window_glow, (wx, wy), 2)
                pygame.draw.circle(surf, window_color, (wx, wy), 1)

            # Engine array - more engines for large ships
            engine_offsets = [-18, -9, 0, 9, 18] if w > 100 else [-12, 0, 12]
            for offset in engine_offsets:
                pygame.draw.ellipse(surf, accent_red, (cx+offset-5, h-15, 10, 10))
                pygame.draw.ellipse(surf, engine_color, (cx+offset-3, h-13, 6, 7))
                pygame.draw.ellipse(surf, engine_glow, (cx+offset-2, h-11, 4, 4))

            # Decorative spines and ornate details
            pygame.draw.line(surf, gold_highlight, (cx, 15), (cx, h//3-5), 2)
            pygame.draw.line(surf, gold_light, (cx-8, h//2), (cx-8, h-20), 1)
            pygame.draw.line(surf, gold_light, (cx+8, h//2), (cx+8, h-20), 1)

            # Ornate bow detail (Amarr religious iconography)
            pygame.draw.polygon(surf, gold_highlight, [(cx, 8), (cx-4, 16), (cx+4, 16)])
            pygame.draw.circle(surf, gold_highlight, (cx, 22), 3)
            pygame.draw.circle(surf, gold_light, (cx, 22), 2)

        elif h > 45:
            # === MEDIUM SHIP (Cruiser) - Enhanced detail ===
            hull_outer = [(cx, 3), (w-5, h//3), (w-6, h-8), (cx, h-3), (6, h-8), (5, h//3)]
            pygame.draw.polygon(surf, hull_shadow, hull_outer)

            hull_main = [(cx, 7), (w-9, h//3+3), (w-10, h-12), (cx, h-7), (10, h-12), (9, h//3+3)]
            pygame.draw.polygon(surf, gold_mid, hull_main)

            # Highlights
            pygame.draw.polygon(surf, gold_light, [(cx, 9), (w-11, h//3+5), (w-13, h//3+12), (cx+3, 15)])

            # Hull panel lines
            pygame.draw.line(surf, gold_dark, (cx-w//5, h//3+8), (cx+w//5, h//3+8), 1)
            pygame.draw.line(surf, gold_dark, (cx-w//5, h//2+5), (cx+w//5, h//2+5), 1)

            # Cockpit area with more detail
            pygame.draw.ellipse(surf, cockpit_color, (cx-5, h//4, 10, 14))
            pygame.draw.ellipse(surf, (90, 120, 160), (cx-3, h//4+2, 6, 10))
            pygame.draw.ellipse(surf, (120, 150, 190), (cx-2, h//4+3, 4, 6))  # Cockpit glass highlight

            # Nacelles with weapon mounts
            pygame.draw.polygon(surf, gold_dark, [(5, h//2-3), (2, h-10), (10, h-12), (8, h//2)])
            pygame.draw.polygon(surf, gold_dark, [(w-5, h//2-3), (w-2, h-10), (w-10, h-12), (w-8, h//2)])
            # Weapon turrets on nacelles
            pygame.draw.circle(surf, (80, 60, 30), (6, h//2+5), 3)
            pygame.draw.circle(surf, (140, 110, 60), (6, h//2+5), 2)
            pygame.draw.circle(surf, (80, 60, 30), (w-6, h//2+5), 3)
            pygame.draw.circle(surf, (140, 110, 60), (w-6, h//2+5), 2)

            # Window lights
            for i in range(3):
                wx = cx - 8 + i * 8
                pygame.draw.circle(surf, (180, 200, 240), (wx, h//2), 1)

            # Engines - dual engines for cruisers
            for offset in [-6, 6]:
                pygame.draw.ellipse(surf, accent_red, (cx+offset-4, h-10, 8, 7))
                pygame.draw.ellipse(surf, engine_color, (cx+offset-2, h-9, 4, 5))
                pygame.draw.ellipse(surf, engine_glow, (cx+offset-1, h-8, 2, 3))

        else:
            # === SMALL SHIP (Frigate/Fighter) ===
            hull_outer = [(cx, 2), (w-4, h//2-3), (w-5, h-4), (cx, h-2), (5, h-4), (4, h//2-3)]
            pygame.draw.polygon(surf, hull_shadow, hull_outer)

            hull_main = [(cx, 5), (w-7, h//2), (w-8, h-7), (cx, h-5), (8, h-7), (7, h//2)]
            pygame.draw.polygon(surf, gold_mid, hull_main)

            # Highlight
            pygame.draw.polygon(surf, gold_light, [(cx, 6), (w-9, h//2), (cx+2, 10)])

            # Small cockpit
            pygame.draw.ellipse(surf, cockpit_color, (cx-3, h//4, 6, 8))
            pygame.draw.ellipse(surf, (100, 130, 170), (cx-2, h//4+1, 4, 5))

            # Small fins
            pygame.draw.polygon(surf, gold_dark, [(5, h//2+2), (2, h-5), (8, h-7)])
            pygame.draw.polygon(surf, gold_dark, [(w-5, h//2+2), (w-2, h-5), (w-8, h-7)])

            # Engine
            pygame.draw.ellipse(surf, accent_red, (cx-4, h-6, 8, 5))
            pygame.draw.ellipse(surf, engine_color, (cx-2, h-5, 4, 3))

        # Add outer glow for visibility
        glow_surf = pygame.Surface((w+6, h+6), pygame.SRCALPHA)
        for i in range(3, 0, -1):
            alpha = 25 // i
            pygame.draw.polygon(glow_surf, (*gold_mid, alpha),
                [(cx+3, 3+i), (w-5+3+i, h//3+3), (w-5+3+i, h*2//3+3), (cx+3, h-3-i),
                 (5+3-i, h*2//3+3), (5+3-i, h//3+3)], 2)

        final_surf = pygame.Surface((w+6, h+6), pygame.SRCALPHA)
        final_surf.blit(glow_surf, (0, 0))
        final_surf.blit(surf, (3, 3))

        return final_surf

    def _create_fallback_image(self):
        """Fallback enemy sprite - Amarr golden ship design with 3D shading"""
        w, h = self.width, self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Amarr Empire color palette - ornate gold/bronze
        gold_dark = (120, 90, 40)
        gold_mid = (180, 150, 70)
        gold_light = (240, 210, 130)
        gold_highlight = (255, 245, 200)
        hull_shadow = (80, 60, 30)
        accent_red = (160, 50, 50)
        engine_orange = (255, 140, 50)
        cockpit_blue = (80, 120, 180)

        if h > 60:  # Large ship (battleship/boss)
            # Main hull - curved Amarr aesthetic
            # Shadow layer
            pygame.draw.polygon(surf, hull_shadow, [
                (cx, h-3), (w-5, h*2//3), (w-3, h//3), (cx, 5), (3, h//3), (5, h*2//3)
            ])
            # Main hull
            pygame.draw.polygon(surf, gold_mid, [
                (cx, h-8), (w-10, h*2//3), (w-8, h//3), (cx, 10), (8, h//3), (10, h*2//3)
            ])
            # 3D highlight (right side)
            pygame.draw.polygon(surf, gold_light, [
                (cx, 12), (w-10, h//3+5), (w-12, h//3), (cx+2, 14)
            ])
            # 3D shadow (left side)
            pygame.draw.polygon(surf, gold_dark, [
                (cx, 12), (10, h//3+5), (8, h//3), (cx-2, 14)
            ])

            # Central dome (Amarr style)
            pygame.draw.ellipse(surf, gold_dark, (cx-12, h//3, 24, 20))
            pygame.draw.ellipse(surf, gold_mid, (cx-10, h//3+2, 20, 16))
            pygame.draw.ellipse(surf, gold_light, (cx-6, h//3+4, 8, 8))

            # Wing panels
            pygame.draw.polygon(surf, gold_dark, [(5, h//2), (0, h//2+20), (8, h*2//3)])
            pygame.draw.polygon(surf, gold_mid, [(6, h//2+2), (2, h//2+18), (9, h*2//3-3)])
            pygame.draw.polygon(surf, gold_dark, [(w-5, h//2), (w, h//2+20), (w-8, h*2//3)])
            pygame.draw.polygon(surf, gold_mid, [(w-6, h//2+2), (w-2, h//2+18), (w-9, h*2//3-3)])

            # Engine array
            for offset in [-10, 0, 10]:
                pygame.draw.ellipse(surf, accent_red, (cx+offset-4, h-10, 8, 8))
                pygame.draw.ellipse(surf, engine_orange, (cx+offset-2, h-8, 4, 5))

            # Decorative lines
            pygame.draw.line(surf, gold_highlight, (cx, 15), (cx, h//3), 2)

        elif h > 35:  # Medium ship (cruiser)
            # Main body
            pygame.draw.polygon(surf, hull_shadow, [
                (cx, 3), (w-3, h//3), (w-5, h-5), (5, h-5), (3, h//3)
            ])
            pygame.draw.polygon(surf, gold_mid, [
                (cx, 8), (w-8, h//3+5), (w-10, h-10), (10, h-10), (8, h//3+5)
            ])
            # 3D bevel right
            pygame.draw.polygon(surf, gold_light, [
                (cx, 10), (w-10, h//3+5), (w-12, h//3+8), (cx+3, 12)
            ])
            # 3D bevel left
            pygame.draw.polygon(surf, gold_dark, [
                (cx, 10), (10, h//3+5), (12, h//3+8), (cx-3, 12)
            ])

            # Nacelles/wings
            pygame.draw.polygon(surf, gold_dark, [(3, h//2-5), (0, h-8), (8, h-12), (6, h//2)])
            pygame.draw.polygon(surf, gold_mid, [(4, h//2-3), (2, h-10), (7, h-13)])
            pygame.draw.polygon(surf, gold_dark, [(w-3, h//2-5), (w, h-8), (w-8, h-12), (w-6, h//2)])
            pygame.draw.polygon(surf, gold_mid, [(w-4, h//2-3), (w-2, h-10), (w-7, h-13)])

            # Cockpit
            pygame.draw.ellipse(surf, cockpit_blue, (cx-4, h//4, 8, 12))
            pygame.draw.ellipse(surf, (120, 160, 220), (cx-2, h//4+2, 4, 6))

            # Engine
            pygame.draw.ellipse(surf, accent_red, (cx-8, h-8, 16, 6))
            pygame.draw.ellipse(surf, engine_orange, (cx-5, h-7, 10, 4))

        else:  # Small ship (frigate/fighter)
            # Compact pointed design
            pygame.draw.polygon(surf, hull_shadow, [
                (cx, 2), (w-3, h//2), (w-4, h-3), (4, h-3), (3, h//2)
            ])
            pygame.draw.polygon(surf, gold_mid, [
                (cx, 5), (w-6, h//2), (w-7, h-6), (7, h-6), (6, h//2)
            ])
            # Highlight
            pygame.draw.polygon(surf, gold_light, [
                (cx, 6), (w-8, h//2-2), (cx+2, 8)
            ])
            # Shadow
            pygame.draw.polygon(surf, gold_dark, [
                (cx, 6), (8, h//2-2), (cx-2, 8)
            ])

            # Small fins
            pygame.draw.polygon(surf, gold_dark, [(4, h//2+3), (1, h-4), (6, h-6)])
            pygame.draw.polygon(surf, gold_dark, [(w-4, h//2+3), (w-1, h-4), (w-6, h-6)])

            # Cockpit
            pygame.draw.ellipse(surf, cockpit_blue, (cx-2, h//4, 4, 6))

            # Engine
            pygame.draw.circle(surf, accent_red, (cx, h-4), 3)
            pygame.draw.circle(surf, engine_orange, (cx, h-4), 2)

        return surf
    def update(self, player_rect=None):
        """Update enemy position and behavior with advanced patterns"""
        self.pattern_timer += 0.05
        
        # Enter phase - move to target Y first
        if not self.entered:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed * 1.5
            else:
                self.entered = True
            return
        
        # Execute movement pattern
        if self.pattern == self.PATTERN_DRIFT:
            self._move_drift()
        elif self.pattern == self.PATTERN_SINE:
            self._move_sine()
        elif self.pattern == self.PATTERN_ZIGZAG:
            self._move_zigzag()
        elif self.pattern == self.PATTERN_CIRCLE:
            self._move_circle()
        elif self.pattern == self.PATTERN_SWOOP:
            self._move_swoop(player_rect)
        elif self.pattern == self.PATTERN_FLANK:
            self._move_flank(player_rect)
        elif self.pattern == self.PATTERN_SWARM:
            self._move_swarm(player_rect)
        
        # Boss phase changes
        if self.is_boss:
            self._update_boss_behavior()
        
        # Keep on screen horizontally
        if self.rect.left < 10:
            self.rect.left = 10
        elif self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10
    
    def _move_drift(self):
        """Basic side-to-side drift"""
        self.rect.x += math.sin(self.pattern_timer) * self.speed
        # Slow vertical drift
        if self.rect.centery < self.target_y:
            self.rect.y += self.speed * 0.3
    
    def _move_sine(self):
        """Smooth sine wave movement"""
        amplitude = 80 + 40 * math.sin(self.pattern_timer * 0.3)
        self.rect.centerx = SCREEN_WIDTH // 2 + math.sin(self.pattern_timer * 1.5) * amplitude
        # Gentle vertical oscillation
        self.rect.centery = self.target_y + math.sin(self.pattern_timer * 0.8) * 30
    
    def _move_zigzag(self):
        """Sharp zigzag pattern"""
        # Change direction every ~60 frames
        direction = 1 if int(self.pattern_timer * 2) % 2 == 0 else -1
        self.rect.x += direction * self.speed * 2
        # Slight downward movement on direction change
        if abs(math.sin(self.pattern_timer * 2)) < 0.1:
            self.rect.y += self.speed
    
    def _move_circle(self):
        """Circular strafing pattern"""
        self.rect.centerx = self.circle_center_x + math.cos(self.pattern_timer) * self.circle_radius
        self.rect.centery = self.target_y + math.sin(self.pattern_timer) * (self.circle_radius * 0.5)
        # Slowly drift the center
        self.circle_center_x += math.sin(self.pattern_timer * 0.2) * 0.5
        self.circle_center_x = max(100, min(SCREEN_WIDTH - 100, self.circle_center_x))
    
    def _move_swoop(self, player_rect):
        """Dive toward player then retreat"""
        if self.swoop_state == 'enter':
            if self.rect.centery >= self.target_y:
                self.swoop_state = 'aim'
        elif self.swoop_state == 'aim':
            # Wait and aim at player
            if self.pattern_timer % (math.pi * 2) < 0.1:
                self.swoop_state = 'dive'
                if player_rect:
                    self.swoop_target_x = player_rect.centerx
                else:
                    self.swoop_target_x = SCREEN_WIDTH // 2
        elif self.swoop_state == 'dive':
            # Dive toward player position
            self.rect.y += self.speed * 3
            dx = self.swoop_target_x - self.rect.centerx
            self.rect.x += max(-self.speed * 2, min(self.speed * 2, dx * 0.1))
            if self.rect.centery > SCREEN_HEIGHT * 0.6:
                self.swoop_state = 'retreat'
        elif self.swoop_state == 'retreat':
            # Retreat back up
            self.rect.y -= self.speed * 2
            if self.rect.centery < self.target_y:
                self.swoop_state = 'aim'
        
        # Horizontal drift while aiming
        if self.swoop_state == 'aim':
            self.rect.x += math.sin(self.pattern_timer * 2) * self.speed
    
    def _move_flank(self, player_rect):
        """Move to screen edge then track player"""
        target_x = 80 if self.flank_side < 0 else SCREEN_WIDTH - 80
        
        # Move to flanking position
        dx = target_x - self.rect.centerx
        if abs(dx) > 5:
            self.rect.x += max(-self.speed, min(self.speed, dx * 0.05))
        
        # Track player Y position loosely
        if player_rect:
            target_y = min(player_rect.centery - 200, 250)
            target_y = max(80, target_y)
            dy = target_y - self.rect.centery
            self.rect.y += max(-self.speed * 0.5, min(self.speed * 0.5, dy * 0.02))
        
        # Occasionally switch sides
        if random.random() < 0.002:
            self.flank_side *= -1

    def _move_swarm(self, player_rect):
        """Drone swarm behavior - orbit around player position then attack"""
        if not player_rect:
            # No player, just drift down
            self.rect.y += self.speed * 0.5
            return

        # Update swarm approach timer
        self.swarm_approach_timer += 1

        # Calculate swarm center (ahead of player)
        swarm_center_x = player_rect.centerx
        swarm_center_y = player_rect.centery - 150  # Orbit above player

        if self.swarm_state == 'orbit':
            # Orbit around the swarm center
            self.swarm_angle += self.swarm_speed
            target_x = swarm_center_x + math.cos(self.swarm_angle) * self.swarm_radius
            target_y = swarm_center_y + math.sin(self.swarm_angle) * (self.swarm_radius * 0.6)

            # Smooth movement toward orbit position
            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            self.rect.x += dx * 0.08
            self.rect.y += dy * 0.08

            # Randomly decide to attack
            if self.swarm_approach_timer > 120 and random.random() < 0.01:
                self.swarm_state = 'attack'
                self.swarm_approach_timer = 0

        elif self.swarm_state == 'attack':
            # Dive toward player
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.rect.x += (dx / dist) * self.speed * 2.5
                self.rect.y += (dy / dist) * self.speed * 2.5

            # Close enough or timer expired, retreat
            if dist < 50 or self.swarm_approach_timer > 60:
                self.swarm_state = 'retreat'
                self.swarm_approach_timer = 0

        elif self.swarm_state == 'retreat':
            # Retreat back to orbit
            target_x = swarm_center_x + math.cos(self.swarm_angle) * self.swarm_radius
            target_y = swarm_center_y + math.sin(self.swarm_angle) * (self.swarm_radius * 0.6)

            dx = target_x - self.rect.centerx
            dy = target_y - self.rect.centery
            self.rect.x += dx * 0.05
            self.rect.y += dy * 0.05

            # Back in orbit
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 30 or self.swarm_approach_timer > 90:
                self.swarm_state = 'orbit'
                self.swarm_approach_timer = 0

        # Jitter for organic feel
        self.rect.x += random.uniform(-0.5, 0.5)
        self.rect.y += random.uniform(-0.5, 0.5)

    def _update_boss_behavior(self):
        """Update boss-specific behavior with phases and special attacks"""
        self.boss_phase_timer += 1
        self.boss_attack_timer += 1

        # Cooldown tracking
        if self.boss_special_cooldown > 0:
            self.boss_special_cooldown -= 1
        if self.drone_stream_cooldown > 0:
            self.drone_stream_cooldown -= 1

        # Phase changes based on health
        health_pct = (self.shields + self.armor + self.hull) / (self.max_shields + self.max_armor + self.max_hull)

        # ENRAGE at 20% health - boss becomes much more aggressive
        if health_pct <= self.enrage_threshold and not self.is_enraged:
            self.is_enraged = True
            self.speed *= 1.5  # Much faster
            self.fire_rate = int(self.fire_rate * 0.5)  # Double fire rate
            self.boss_special_cooldown = 0  # Immediate special attack
            # Trigger drone stream as enrage attack
            self.drones_to_spawn = list(range(6))  # Queue 6 drones

        if health_pct < 0.3 and self.boss_phase < 2:
            self.boss_phase = 2
            if not self.is_enraged:  # Don't stack speed bonuses
                self.speed *= 1.3
            self.boss_special_cooldown = 0  # Immediate special attack on phase change
        elif health_pct < 0.6 and self.boss_phase < 1:
            self.boss_phase = 1
            self.fire_rate = int(self.fire_rate * 0.8)
            self.boss_special_cooldown = 0

        # Handle charging state
        if self.boss_charging:
            self.boss_charge_timer += 1
            if self.boss_charge_timer >= 60:  # 1 second charge
                self.boss_charging = False
                self.boss_charge_timer = 0

    def get_boss_special_attack(self, player_rect):
        """
        Get special attack bullets if ready.
        Returns: (bullets list, attack_type string or None)
        """
        if not self.is_boss:
            return [], None

        if self.boss_special_cooldown > 0 or self.boss_charging:
            return [], None

        # Check if it's time for a special attack
        attack_interval = 300 - (self.boss_phase * 60)  # Faster in later phases
        if self.boss_attack_timer < attack_interval:
            return [], None

        self.boss_attack_timer = 0

        # Choose attack based on phase and randomness
        # Enraged bosses get drone_stream as priority attack
        if self.is_enraged:
            attacks = ['spiral', 'barrage', 'ring', 'drone_stream', 'drone_stream']
        elif self.boss_phase == 0:
            attacks = ['spread', 'spiral']
        elif self.boss_phase == 1:
            attacks = ['spread', 'spiral', 'barrage', 'summon', 'drone_stream']
        else:
            attacks = ['spiral', 'barrage', 'ring', 'summon', 'drone_stream']

        attack = random.choice(attacks)
        bullets = []

        if attack == 'spread':
            bullets = self._attack_spread(player_rect)
        elif attack == 'spiral':
            bullets = self._attack_spiral()
        elif attack == 'barrage':
            bullets = self._attack_barrage(player_rect)
        elif attack == 'ring':
            bullets = self._attack_ring()
        elif attack == 'summon':
            # Summon returns None for bullets, handled separately
            return [], 'summon' if self.summon_count < self.max_summons else None
        elif attack == 'drone_stream':
            # Queue drones to spawn - game will spawn them
            if self.drone_stream_cooldown <= 0:
                num_drones = 4 if self.is_enraged else 3
                self.drones_to_spawn = list(range(num_drones))
                self.drone_stream_cooldown = 300  # 5 second cooldown
                return [], 'drone_stream'
            else:
                # Fallback to spread if drone stream on cooldown
                bullets = self._attack_spread(player_rect)

        self.boss_special_cooldown = 120  # 2 second cooldown
        self.boss_attack_type = attack

        return bullets, attack

    def _attack_spread(self, player_rect):
        """Wide spread shot pattern"""
        bullets = []
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx, dy = dx/dist * 6, dy/dist * 6
        else:
            dx, dy = 0, 6

        for angle in range(-60, 61, 15):
            rad = math.radians(angle)
            bdx = dx * math.cos(rad) - dy * math.sin(rad)
            bdy = dx * math.sin(rad) + dy * math.cos(rad)
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 12))
        return bullets

    def _attack_spiral(self):
        """Spiral bullet pattern"""
        bullets = []
        base_angle = self.boss_phase_timer * 0.15
        for i in range(8):
            angle = base_angle + (i * math.pi / 4)
            speed = 4
            bdx = math.cos(angle) * speed
            bdy = math.sin(angle) * speed
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, bdx, bdy, 10))
        return bullets

    def _attack_barrage(self, player_rect):
        """Rapid fire barrage toward player"""
        bullets = []
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx, dy = dx/dist * 7, dy/dist * 7
        else:
            dx, dy = 0, 7

        # Slightly randomized aim
        for i in range(5):
            offset = (i - 2) * 0.1
            bdx = dx + offset * 3
            bullets.append(EnemyBullet(
                self.rect.centerx + (i - 2) * 15,
                self.rect.bottom, bdx, dy, 15))
        return bullets

    def _attack_ring(self):
        """360 degree ring of bullets"""
        bullets = []
        count = 16 + (self.boss_phase * 4)
        for i in range(count):
            angle = (i / count) * math.pi * 2
            speed = 3.5
            bdx = math.cos(angle) * speed
            bdy = math.sin(angle) * speed
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, bdx, bdy, 8))
        return bullets

    def get_drone_spawn(self):
        """Get drone spawn position if boss has drones queued to spawn.
        Returns (x, y) position or None if no drones to spawn."""
        if not self.is_boss or not hasattr(self, 'drones_to_spawn'):
            return None
        if not self.drones_to_spawn:
            return None

        # Pop one drone from the queue
        self.drones_to_spawn.pop()

        # Spawn position: left or right side of boss, alternating
        side = 1 if len(self.drones_to_spawn) % 2 == 0 else -1
        spawn_x = self.rect.centerx + (side * self.rect.width // 2)
        spawn_y = self.rect.bottom + 20

        return (spawn_x, spawn_y)

    def can_shoot(self):
        """Check if enemy can fire"""
        if self.fire_rate == 0:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate
    
    def shoot(self, player_rect):
        """Fire at player with behavior-specific shooting"""
        # Drones in attack mode shoot faster
        if self.pattern == self.PATTERN_SWARM and hasattr(self, 'swarm_state'):
            if self.swarm_state == 'attack':
                # Attacking drones have reduced cooldown
                now = pygame.time.get_ticks()
                if now - self.last_shot < self.fire_rate * 0.4:
                    return []
            elif not self.can_shoot():
                return []
        elif not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()
        bullets = []

        # Calculate direction to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx = dx / dist * 5
            dy = dy / dist * 5
        else:
            dy = 5

        if self.is_boss:
            # Boss fires spread
            for angle in [-20, -10, 0, 10, 20]:
                rad = math.radians(angle)
                bdx = dx * math.cos(rad) - dy * math.sin(rad)
                bdy = dx * math.sin(rad) + dy * math.cos(rad)
                bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 15))
        elif self.pattern == self.PATTERN_SWARM and hasattr(self, 'swarm_state') and self.swarm_state == 'attack':
            # Attacking drones fire faster, more accurate shots
            speed = 7  # Faster bullets
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.8, dy * 1.4, 8))
        else:
            # Add slight inaccuracy for regular enemies
            spread = random.uniform(-0.3, 0.3)
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.3 + spread, dy, 10))

        return bullets
    
    def take_damage(self, bullet):
        """Take damage from bullet, return True if destroyed"""
        damage = bullet.damage
        
        # Apply multipliers
        if self.shields > 0:
            damage *= bullet.shield_mult
            absorbed = min(self.shields, damage)
            self.shields -= absorbed
            damage = (damage - absorbed) / bullet.shield_mult
        
        if damage > 0 and self.armor > 0:
            damage *= bullet.armor_mult
            absorbed = min(self.armor, damage)
            self.armor -= absorbed
            damage = (damage - absorbed) / bullet.armor_mult
        
        if damage > 0:
            self.hull -= damage
        
        return self.hull <= 0


class RefugeePod(pygame.sprite.Sprite):
    """EVE-style escape pod with refugees"""

    def __init__(self, x, y, count=1):
        super().__init__()
        self.count = count
        self.lifetime = 300  # frames until disappear
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(0.5, 1.5)
        self.pulse_timer = random.uniform(0, math.pi * 2)
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-1, 1)

        self.base_image = self._create_pod_image()
        self.image = self.base_image
        self.rect = self.image.get_rect(center=(x, y))

    def _create_pod_image(self):
        """Create an EVE-style escape pod"""
        w, h = 24, 32
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx = w // 2

        # Pod colors - sleek metallic with emergency lighting
        hull_dark = (60, 65, 70)
        hull_mid = (100, 105, 115)
        hull_light = (140, 145, 155)
        hull_highlight = (180, 185, 195)
        emergency_green = (50, 200, 80)
        emergency_glow = (100, 255, 120)
        window_color = (40, 60, 80)
        window_light = (80, 120, 160)

        # Main pod body - elongated capsule shape
        # Shadow/base layer
        pygame.draw.ellipse(surf, hull_dark, (2, 3, w-4, h-6))

        # Main hull
        pygame.draw.ellipse(surf, hull_mid, (4, 5, w-8, h-10))

        # Highlight (top portion)
        pygame.draw.ellipse(surf, hull_light, (6, 6, w-12, h//2-4))

        # Cockpit window (top)
        pygame.draw.ellipse(surf, window_color, (cx-5, 8, 10, 12))
        pygame.draw.ellipse(surf, window_light, (cx-3, 10, 6, 7))
        pygame.draw.ellipse(surf, (120, 160, 200), (cx-2, 11, 3, 4))

        # Emergency beacon light (pulsing green)
        pygame.draw.circle(surf, emergency_green, (cx, h-8), 4)
        pygame.draw.circle(surf, emergency_glow, (cx, h-8), 2)

        # Side panel lines
        pygame.draw.line(surf, hull_dark, (5, h//2), (5, h-10), 1)
        pygame.draw.line(surf, hull_dark, (w-5, h//2), (w-5, h-10), 1)

        # Small thrusters at bottom
        pygame.draw.ellipse(surf, (80, 80, 90), (cx-6, h-5, 5, 3))
        pygame.draw.ellipse(surf, (80, 80, 90), (cx+1, h-5, 5, 3))

        # Panel details
        pygame.draw.rect(surf, hull_dark, (cx-4, h//2+2, 8, 6), 1, border_radius=2)

        # Create glow effect
        glow_surf = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        # Green emergency glow
        for i in range(4, 0, -1):
            alpha = 20 // i
            pygame.draw.circle(glow_surf, (*emergency_green, alpha), (cx+4, h-8+4), 6+i)

        final_surf = pygame.Surface((w+8, h+8), pygame.SRCALPHA)
        final_surf.blit(glow_surf, (0, 0))
        final_surf.blit(surf, (4, 4))

        return final_surf

    def update(self):
        self.rect.x += self.drift_x
        self.rect.y += self.drift_y
        self.lifetime -= 1
        self.pulse_timer += 0.15
        self.rotation += self.rot_speed

        # Animate the beacon pulse
        if self.lifetime > 60:
            # Create pulsing effect on the image
            pulse = 0.7 + 0.3 * math.sin(self.pulse_timer * 3)
            if int(self.pulse_timer * 10) % 20 < 10:
                # Beacon flash
                self.image = self.base_image.copy()
            else:
                self.image = self.base_image

        # Blink when about to expire
        if self.lifetime < 60 and self.lifetime % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

        if self.lifetime <= 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    """Powerup pickup with glowing animated visuals"""

    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.data = POWERUP_TYPES[powerup_type]
        self.color = self.data['color']
        self.size = 28
        self.pulse_timer = random.uniform(0, math.pi * 2)  # Random start phase
        self.rotation = 0
        self.bob_offset = 0

        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        self.speed = 1.5
        self._create_base_image()
        # Initialize image (will be animated in update)
        self.image = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
        self.image.blit(self.base_surface, (2, 2))

    def _create_base_image(self):
        """Create the base powerup image with icon"""
        size = self.size + 16  # Extra space for glow
        self.base_surface = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Draw icon based on type
        if self.powerup_type == 'nanite':
            # Green cross (health)
            self._draw_cross(cx, cy, (100, 255, 100))
        elif self.powerup_type == 'capacitor':
            # Blue lightning bolt (rockets)
            self._draw_lightning(cx, cy, (100, 150, 255))
        elif self.powerup_type == 'overdrive':
            # Yellow speed arrows
            self._draw_speed_arrows(cx, cy, (255, 255, 100))
        elif self.powerup_type == 'shield_boost':
            # Cyan shield
            self._draw_shield(cx, cy, (150, 220, 255))
        elif self.powerup_type == 'double_damage':
            # Red damage star
            self._draw_damage_star(cx, cy, (255, 100, 100))
        elif self.powerup_type == 'rapid_fire':
            # Orange bullets
            self._draw_rapid_fire(cx, cy, (255, 180, 50))
        elif self.powerup_type == 'bomb_charge':
            # Magenta bomb
            self._draw_bomb(cx, cy, (255, 100, 255))
        elif self.powerup_type == 'magnet':
            # Light blue magnet
            self._draw_magnet(cx, cy, (180, 200, 255))
        elif self.powerup_type == 'invulnerability':
            # Gold star
            self._draw_invuln_star(cx, cy, (255, 215, 50))
        else:
            # Default: colored diamond
            self._draw_diamond(cx, cy, self.color)

    def _draw_cross(self, cx, cy, color):
        """Health cross"""
        s = self.size // 2
        # Outer glow
        pygame.draw.rect(self.base_surface, (*color, 60), (cx-s-2, cy-s//3-2, s*2+4, s*2//3+4), border_radius=3)
        pygame.draw.rect(self.base_surface, (*color, 60), (cx-s//3-2, cy-s-2, s*2//3+4, s*2+4), border_radius=3)
        # Cross
        pygame.draw.rect(self.base_surface, color, (cx-s, cy-s//3, s*2, s*2//3), border_radius=2)
        pygame.draw.rect(self.base_surface, color, (cx-s//3, cy-s, s*2//3, s*2), border_radius=2)
        # Highlight
        pygame.draw.rect(self.base_surface, (255, 255, 255), (cx-s+2, cy-s//3+2, s//2, s//3), border_radius=1)

    def _draw_lightning(self, cx, cy, color):
        """Lightning bolt for rockets"""
        points = [(cx-4, cy-10), (cx+2, cy-3), (cx-2, cy-3), (cx+6, cy+10), (cx, cy+2), (cx+4, cy+2)]
        # Glow
        for i in range(3, 0, -1):
            glow_points = [(p[0], p[1]) for p in points]
            pygame.draw.polygon(self.base_surface, (*color, 40), glow_points)
        pygame.draw.polygon(self.base_surface, color, points)
        pygame.draw.polygon(self.base_surface, (255, 255, 255), points, 1)

    def _draw_speed_arrows(self, cx, cy, color):
        """Speed boost arrows"""
        for offset in [-6, 0, 6]:
            points = [(cx+offset-5, cy+6), (cx+offset, cy-8), (cx+offset+5, cy+6)]
            pygame.draw.polygon(self.base_surface, color, points)
            pygame.draw.polygon(self.base_surface, (255, 255, 255), points, 1)

    def _draw_shield(self, cx, cy, color):
        """Shield icon"""
        # Shield shape
        points = [(cx, cy-10), (cx+10, cy-5), (cx+8, cy+5), (cx, cy+12), (cx-8, cy+5), (cx-10, cy-5)]
        pygame.draw.polygon(self.base_surface, (*color, 150), points)
        pygame.draw.polygon(self.base_surface, color, points, 2)
        # Inner highlight
        pygame.draw.arc(self.base_surface, (255, 255, 255), (cx-6, cy-6, 12, 12), 0.5, 2.5, 2)

    def _draw_damage_star(self, cx, cy, color):
        """Damage multiplier star"""
        # 6-pointed star
        for i in range(6):
            angle = i * math.pi / 3 - math.pi / 2
            x1, y1 = cx + math.cos(angle) * 10, cy + math.sin(angle) * 10
            angle2 = angle + math.pi / 6
            x2, y2 = cx + math.cos(angle2) * 5, cy + math.sin(angle2) * 5
            pygame.draw.polygon(self.base_surface, color, [(cx, cy), (x1, y1), (x2, y2)])
        pygame.draw.circle(self.base_surface, (255, 200, 200), (cx, cy), 4)

    def _draw_rapid_fire(self, cx, cy, color):
        """Rapid fire bullets"""
        for offset in [-5, 0, 5]:
            pygame.draw.ellipse(self.base_surface, color, (cx+offset-2, cy-8, 4, 16))
            pygame.draw.ellipse(self.base_surface, (255, 255, 200), (cx+offset-1, cy-6, 2, 4))

    def _draw_bomb(self, cx, cy, color):
        """Bomb icon"""
        # Bomb body
        pygame.draw.circle(self.base_surface, color, (cx, cy+2), 9)
        pygame.draw.circle(self.base_surface, (255, 200, 255), (cx-3, cy-1), 3)
        # Fuse
        pygame.draw.line(self.base_surface, (200, 150, 100), (cx, cy-7), (cx+4, cy-11), 2)
        # Spark
        pygame.draw.circle(self.base_surface, (255, 255, 100), (cx+4, cy-11), 3)
        pygame.draw.circle(self.base_surface, (255, 255, 255), (cx+4, cy-11), 2)

    def _draw_magnet(self, cx, cy, color):
        """Magnet/tractor beam"""
        # U-shape magnet
        pygame.draw.arc(self.base_surface, color, (cx-8, cy-4, 16, 16), 0, math.pi, 4)
        pygame.draw.rect(self.base_surface, (255, 100, 100), (cx-10, cy-8, 6, 12))
        pygame.draw.rect(self.base_surface, (100, 100, 255), (cx+4, cy-8, 6, 12))

    def _draw_invuln_star(self, cx, cy, color):
        """Invulnerability golden star"""
        # 5-pointed star
        points = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = 10 if i % 2 == 0 else 5
            points.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
        pygame.draw.polygon(self.base_surface, color, points)
        pygame.draw.polygon(self.base_surface, (255, 255, 200), points, 1)
        pygame.draw.circle(self.base_surface, (255, 255, 200), (cx, cy), 3)

    def _draw_diamond(self, cx, cy, color):
        """Default diamond shape"""
        points = [(cx, cy-10), (cx+8, cy), (cx, cy+10), (cx-8, cy)]
        pygame.draw.polygon(self.base_surface, color, points)
        pygame.draw.polygon(self.base_surface, (255, 255, 255), points, 2)

    def update(self):
        self.rect.y += self.speed
        self.pulse_timer += 0.15
        self.rotation += 2
        self.bob_offset = math.sin(self.pulse_timer * 2) * 3

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

        # Create animated image with glow
        pulse = 0.7 + 0.3 * math.sin(self.pulse_timer)
        glow_size = int(8 + 4 * math.sin(self.pulse_timer))

        size = self.size + 20
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Outer glow pulse
        glow_color = (*self.color, int(60 * pulse))
        pygame.draw.circle(self.image, glow_color, (cx, cy), self.size//2 + glow_size)

        # Middle glow
        glow_color2 = (*self.color, int(100 * pulse))
        pygame.draw.circle(self.image, glow_color2, (cx, cy), self.size//2 + 4)

        # Core background
        pygame.draw.circle(self.image, (30, 30, 40), (cx, cy), self.size//2)
        pygame.draw.circle(self.image, self.color, (cx, cy), self.size//2, 2)

        # Blit the icon
        icon_rect = self.base_surface.get_rect(center=(cx, cy))
        self.image.blit(self.base_surface, icon_rect)

        # Sparkle effect
        if random.random() < 0.1:
            sx = cx + random.randint(-10, 10)
            sy = cy + random.randint(-10, 10)
            pygame.draw.circle(self.image, (255, 255, 255), (sx, sy), 2)

        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery + self.bob_offset))


class Explosion(pygame.sprite.Sprite):
    """Visual explosion effect"""
    
    def __init__(self, x, y, size=30, color=COLOR_AMARR_ACCENT):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size
        self.color = color
        self.frame = 0
        self.max_frames = 20
        self._update_image()
    
    def _update_image(self):
        progress = self.frame / self.max_frames
        current_size = int(self.size * (1 + progress))
        alpha = int(255 * (1 - progress))
        
        self.image = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(self.image, color_with_alpha, 
                          (current_size, current_size), current_size)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
        else:
            self._update_image()


class Star:
    """Background star for parallax"""
    
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.speed = random.uniform(0.5, 3)
        self.size = 1 if self.speed < 1.5 else 2
        self.brightness = int(100 + self.speed * 50)
    
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)


class ParallaxObject:
    """Base class for parallax background objects"""

    def __init__(self, speed_mult=1.0, start_random_y=True):
        self.x = random.randint(0, SCREEN_WIDTH)
        if start_random_y:
            self.y = random.randint(-50, SCREEN_HEIGHT)
        else:
            self.y = random.randint(-200, -50)
        self.speed_mult = speed_mult
        self.base_speed = 0.5
        self.alpha = 255

    def update(self):
        self.y += self.base_speed * self.speed_mult
        if self.y > SCREEN_HEIGHT + 100:
            self.respawn()

    def respawn(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-200, -50)

    def draw(self, surface):
        pass


class DistantNebula(ParallaxObject):
    """Very distant, slow-moving nebula clouds"""

    def __init__(self):
        super().__init__(speed_mult=0.1)
        self.size = random.randint(150, 350)  # Larger nebulae
        self.color = random.choice([
            (100, 50, 150),   # Brighter purple
            (50, 100, 150),   # Brighter blue
            (150, 80, 50),    # Brighter rust (Minmatar)
            (80, 130, 100),   # Brighter teal
            (130, 70, 100),   # Brighter magenta
        ])
        self.alpha = random.randint(80, 140)  # More visible
        self._create_surface()

    def _create_surface(self):
        self.surface = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        # Draw fuzzy circle with multiple layers
        for i in range(7):
            radius = self.size - i * (self.size // 8)
            alpha = self.alpha - i * (self.alpha // 8)
            color = (*self.color, max(10, alpha))
            pygame.draw.circle(self.surface, color, (self.size, self.size), radius)

    def respawn(self):
        super().respawn()
        self.size = random.randint(150, 350)
        self.color = random.choice([
            (100, 50, 150), (50, 100, 150), (150, 80, 50), (80, 130, 100), (130, 70, 100)
        ])
        self.alpha = random.randint(80, 140)
        self._create_surface()

    def draw(self, surface):
        surface.blit(self.surface, (int(self.x - self.size), int(self.y - self.size)))


class DistantAsteroid(ParallaxObject):
    """Far away, small asteroids"""

    def __init__(self, start_random_y=True):
        super().__init__(speed_mult=0.3, start_random_y=start_random_y)
        self.size = random.randint(8, 18)  # Larger
        self.color = random.choice([
            (140, 110, 80),   # Brighter brown
            (120, 120, 130),  # Brighter gray
            (150, 120, 90),   # Brighter tan
            (130, 100, 80),   # Brighter rust
        ])
        self.points = self._generate_shape()

    def _generate_shape(self):
        points = []
        num_points = random.randint(5, 8)
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            dist = self.size * random.uniform(0.6, 1.0)
            px = math.cos(angle) * dist
            py = math.sin(angle) * dist
            points.append((px, py))
        return points

    def respawn(self):
        super().respawn()
        self.size = random.randint(8, 18)
        self.points = self._generate_shape()

    def draw(self, surface):
        translated = [(int(self.x + px), int(self.y + py)) for px, py in self.points]
        if len(translated) >= 3:
            pygame.draw.polygon(surface, self.color, translated)


class MediumAsteroid(ParallaxObject):
    """Medium distance asteroids with more detail"""

    def __init__(self, start_random_y=True):
        super().__init__(speed_mult=0.6, start_random_y=start_random_y)
        self.size = random.randint(20, 45)  # Larger
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rot_speed = random.uniform(-0.02, 0.02)
        base_color = random.randint(90, 130)  # Brighter
        self.color = (base_color + 30, base_color + 15, base_color)
        self.highlight = (base_color + 60, base_color + 45, base_color + 30)
        self.points = self._generate_shape()

    def _generate_shape(self):
        points = []
        num_points = random.randint(6, 10)
        for i in range(num_points):
            angle = (i / num_points) * 2 * math.pi
            dist = self.size * random.uniform(0.5, 1.0)
            px = math.cos(angle) * dist
            py = math.sin(angle) * dist
            points.append((px, py))
        return points

    def update(self):
        super().update()
        self.rotation += self.rot_speed

    def respawn(self):
        super().respawn()
        self.size = random.randint(10, 25)
        self.points = self._generate_shape()

    def draw(self, surface):
        # Rotate and translate points
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)
        translated = []
        for px, py in self.points:
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            translated.append((int(self.x + rx), int(self.y + ry)))

        if len(translated) >= 3:
            pygame.draw.polygon(surface, self.color, translated)
            pygame.draw.polygon(surface, self.highlight, translated, 1)


class SpaceDebris(ParallaxObject):
    """Close, fast-moving debris and wreckage"""

    def __init__(self, start_random_y=True):
        super().__init__(speed_mult=1.2, start_random_y=start_random_y)
        self.debris_type = random.choice(['panel', 'shard', 'chunk'])
        self.size = random.randint(4, 12)
        self.rotation = random.uniform(0, 2 * math.pi)
        self.rot_speed = random.uniform(-0.05, 0.05)
        self.color = random.choice([
            (100, 90, 80),   # Rusty metal
            (80, 80, 90),    # Dark metal
            (90, 70, 50),    # Copper
        ])

    def update(self):
        super().update()
        self.rotation += self.rot_speed

    def respawn(self):
        super().respawn()
        self.debris_type = random.choice(['panel', 'shard', 'chunk'])
        self.size = random.randint(4, 12)

    def draw(self, surface):
        cos_r = math.cos(self.rotation)
        sin_r = math.sin(self.rotation)

        if self.debris_type == 'panel':
            # Rectangular panel
            w, h = self.size, self.size // 2
            points = [(-w, -h), (w, -h), (w, h), (-w, h)]
        elif self.debris_type == 'shard':
            # Triangular shard
            points = [(0, -self.size), (self.size//2, self.size//2), (-self.size//2, self.size//2)]
        else:
            # Irregular chunk
            points = [(0, -self.size), (self.size, 0), (self.size//2, self.size), (-self.size//2, self.size//2)]

        translated = []
        for px, py in points:
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            translated.append((int(self.x + rx), int(self.y + ry)))

        pygame.draw.polygon(surface, self.color, translated)
        # Edge highlight
        lighter = tuple(min(255, c + 30) for c in self.color)
        pygame.draw.polygon(surface, lighter, translated, 1)


class DistantStation(ParallaxObject):
    """Very distant space stations, rare"""

    def __init__(self, start_random_y=True):
        super().__init__(speed_mult=0.15, start_random_y=start_random_y)
        self.station_type = random.choice(['outpost', 'platform', 'antenna'])
        self.size = random.randint(40, 80)  # Larger
        self.alpha = random.randint(100, 180)  # More visible
        self._create_surface()

    def _create_surface(self):
        self.surface = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        cx, cy = self.size * 1.5, self.size * 1.5
        color = (100, 100, 130, self.alpha)  # Brighter
        highlight = (180, 180, 220, self.alpha)  # Brighter highlights

        if self.station_type == 'outpost':
            # Central hub with arms
            pygame.draw.circle(self.surface, color, (int(cx), int(cy)), self.size // 2)
            for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
                x2 = cx + math.cos(angle) * self.size
                y2 = cy + math.sin(angle) * self.size
                pygame.draw.line(self.surface, color, (cx, cy), (x2, y2), 3)
                pygame.draw.circle(self.surface, highlight, (int(x2), int(y2)), 4)

        elif self.station_type == 'platform':
            # Large flat platform
            rect = pygame.Rect(cx - self.size, cy - self.size//4, self.size * 2, self.size // 2)
            pygame.draw.rect(self.surface, color, rect)
            pygame.draw.rect(self.surface, highlight, rect, 1)
            # Support struts
            pygame.draw.line(self.surface, color, (cx - self.size//2, cy), (cx - self.size//2, cy + self.size), 2)
            pygame.draw.line(self.surface, color, (cx + self.size//2, cy), (cx + self.size//2, cy + self.size), 2)

        else:  # antenna
            # Tall antenna array
            pygame.draw.line(self.surface, color, (cx, cy - self.size), (cx, cy + self.size), 2)
            pygame.draw.line(self.surface, highlight, (cx - self.size//2, cy - self.size//2),
                           (cx + self.size//2, cy - self.size//2), 2)
            pygame.draw.circle(self.surface, highlight, (int(cx), int(cy - self.size)), 3)

    def respawn(self):
        super().respawn()
        self.station_type = random.choice(['outpost', 'platform', 'antenna'])
        self.size = random.randint(40, 80)
        self.alpha = random.randint(100, 180)
        self._create_surface()

    def draw(self, surface):
        surface.blit(self.surface, (int(self.x - self.size * 1.5), int(self.y - self.size * 1.5)))


class ParallaxBackground:
    """Manages all parallax background layers"""

    def __init__(self):
        # Layer 0: Distant nebulae (furthest back) - more and larger
        self.nebulae = [DistantNebula() for _ in range(5)]

        # Layer 1: Distant stations - more visible
        self.stations = [DistantStation() for _ in range(3)]

        # Layer 2: Far asteroids - more
        self.far_asteroids = [DistantAsteroid() for _ in range(12)]

        # Layer 3: Medium asteroids - more
        self.med_asteroids = [MediumAsteroid() for _ in range(8)]

        # Layer 4: Close debris (closest)
        self.debris = [SpaceDebris() for _ in range(8)]

    def update(self):
        for obj in self.nebulae:
            obj.update()
        for obj in self.stations:
            obj.update()
        for obj in self.far_asteroids:
            obj.update()
        for obj in self.med_asteroids:
            obj.update()
        for obj in self.debris:
            obj.update()

    def draw_back_layers(self, surface):
        """Draw the furthest layers (behind stars)"""
        for obj in self.nebulae:
            obj.draw(surface)

    def draw_mid_layers(self, surface):
        """Draw middle layers (with stars)"""
        for obj in self.stations:
            obj.draw(surface)
        for obj in self.far_asteroids:
            obj.draw(surface)

    def draw_front_layers(self, surface):
        """Draw closest layers (in front of stars, behind gameplay)"""
        for obj in self.med_asteroids:
            obj.draw(surface)
        for obj in self.debris:
            obj.draw(surface)
