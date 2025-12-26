"""Game sprites for Minmatar Rebellion"""
import pygame
import math
import random
import os
from constants import *
from visual_enhancements import add_ship_glow, add_colored_tint, add_outline, add_strong_outline

# Import ship assets module for EVE renders
try:
    from ship_assets import (
        ShipAssetManager, PLAYER_SHIPS, ENEMY_SHIPS, INDUSTRIAL, BOSSES, ALL_SHIPS
    )
    _ship_asset_manager = None
    SHIP_ASSETS_AVAILABLE = True
except ImportError:
    SHIP_ASSETS_AVAILABLE = False
    _ship_asset_manager = None

# Ship sprite cache
_ship_sprite_cache = {}
_SPRITE_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'ship_sprites')
_EVE_SPRITE_DIR = os.path.join(os.path.dirname(__file__), 'assets', 'ships', 'processed')

# EVE Type ID mapping for ships
EVE_TYPE_IDS = {
    # Player ships (Minmatar)
    'rifter': 587,
    'wolf': 11379,
    'jaguar': 11377,
    # Enemy ships (Amarr frigates)
    'executioner': 589,
    'punisher': 597,
    'tormentor': 589,  # Use executioner model
    'crucifier': 589,
    'coercer': 597,    # Use punisher model
    # Cruisers
    'omen': 2006,
    'maller': 624,
    'arbitrator': 624,
    'augoror': 624,
    # Battlecruisers
    'harbinger': 2006,  # Use omen for now
    'prophecy': 624,    # Use maller for now
    # Battleships
    'apocalypse': 642,
    'abaddon': 24690,
    'armageddon': 24690,
    # Capitals
    'archon': 642,      # Use apocalypse
    'aeon': 24690,      # Use abaddon
    'avatar': 24690,
    # Industrial
    'bestower': 1944,
    'sigil': 2863,
    # Fallbacks
    'interceptor': 589,
    'bomber': 597,
    'zealot': 2006,
    'sacrilege': 624,
}

# Ship class scale ratios (base size is 48px for frigates)
SHIP_SCALE_RATIOS = {
    'frigate': 1.0,
    'destroyer': 1.2,
    'cruiser': 1.5,
    'battlecruiser': 1.8,
    'battleship': 2.5,
    'industrial': 1.2,
    'capital': 3.0,
    'titan': 4.0,
}

# Map ship names to their class
SHIP_CLASSES = {
    'rifter': 'frigate', 'wolf': 'frigate', 'jaguar': 'frigate',
    'executioner': 'frigate', 'punisher': 'frigate', 'tormentor': 'frigate',
    'crucifier': 'frigate', 'coercer': 'destroyer',
    'omen': 'cruiser', 'maller': 'cruiser', 'arbitrator': 'cruiser', 'augoror': 'cruiser',
    'harbinger': 'battlecruiser', 'prophecy': 'battlecruiser',
    'apocalypse': 'battleship', 'abaddon': 'battleship', 'armageddon': 'battleship',
    'archon': 'capital', 'aeon': 'capital', 'revelation': 'capital',
    'avatar': 'titan',
    'bestower': 'industrial', 'sigil': 'industrial',
    'interceptor': 'frigate', 'bomber': 'frigate',
    'zealot': 'cruiser', 'sacrilege': 'cruiser',
    'drone': 'frigate', 'heavy_drone': 'frigate',
}

def get_ship_asset_manager():
    """Get or create the ship asset manager singleton."""
    global _ship_asset_manager
    if _ship_asset_manager is None and SHIP_ASSETS_AVAILABLE:
        _ship_asset_manager = ShipAssetManager()
    return _ship_asset_manager

def load_ship_sprite(ship_name, target_size=None, use_eve_assets=False):
    """Load a rendered ship sprite from the ship_sprites directory.

    Args:
        ship_name: Name of the ship (e.g., 'rifter', 'executioner')
        target_size: Optional (width, height) tuple to scale the sprite to
        use_eve_assets: If True, try EVE API assets (disabled by default - icons look boxy)

    Returns:
        pygame.Surface with the ship sprite, or None if not found
    """
    cache_key = (ship_name, target_size, use_eve_assets)
    if cache_key in _ship_sprite_cache:
        return _ship_sprite_cache[cache_key].copy()

    sprite = None
    ship_name_lower = ship_name.lower()

    # Use game-designed ship sprites (not EVE API icons which look boxy)
    sprite_path = os.path.join(_SPRITE_DIR, f"{ship_name}.png")
    if os.path.exists(sprite_path):
        try:
            sprite = pygame.image.load(sprite_path).convert_alpha()
        except pygame.error:
            pass

    # Only try EVE assets if explicitly requested and sprite not found
    if sprite is None and use_eve_assets and ship_name_lower in EVE_TYPE_IDS:
        type_id = EVE_TYPE_IDS[ship_name_lower]
        eve_sprite_path = os.path.join(
            _EVE_SPRITE_DIR,
            f"{ship_name_lower}_{type_id}.png"
        )
        if os.path.exists(eve_sprite_path):
            try:
                sprite = pygame.image.load(eve_sprite_path).convert_alpha()
            except pygame.error:
                pass

    if sprite is None:
        return None

    if target_size:
        sprite = pygame.transform.smoothscale(sprite, target_size)

    _ship_sprite_cache[cache_key] = sprite
    return sprite.copy()


def get_ship_scale(ship_name):
    """Get the scale ratio for a ship based on its class."""
    ship_class = SHIP_CLASSES.get(ship_name.lower(), 'frigate')
    return SHIP_SCALE_RATIOS.get(ship_class, 1.0)


class ShipRenderer:
    """Handles ship rendering with effects, damage states, and animations."""

    # Faction-specific colors
    MINMATAR_ENGINE = (255, 120, 40)   # Orange/red rusty thrust
    AMARR_ENGINE = (255, 220, 100)     # Golden/yellow thrust
    SHIELD_COLOR = (100, 180, 255)     # Blue shield shimmer
    ARMOR_COLOR = (180, 140, 80)       # Bronze armor

    def __init__(self, ship_name, is_player=False):
        self.ship_name = ship_name.lower()
        self.is_player = is_player
        self.type_id = EVE_TYPE_IDS.get(self.ship_name)
        self.ship_class = SHIP_CLASSES.get(self.ship_name, 'frigate')

        # Load base sprite
        self.base_sprite = load_ship_sprite(ship_name)
        if self.base_sprite:
            self.width, self.height = self.base_sprite.get_size()
        else:
            self.width, self.height = 48, 48

        # Animation state
        self.engine_frame = 0
        self.engine_timer = 0
        self.thrust_intensity = 0.5

        # Damage state
        self.damage_level = 0  # 0=none, 1=light, 2=moderate, 3=critical
        self.fire_particles = []
        self.smoke_particles = []
        self.spark_timer = 0

        # Shield effect
        self.shield_shimmer = 0
        self.shield_hit_timer = 0

        # Determine faction for engine color
        if self.ship_name in ['rifter', 'wolf', 'jaguar']:
            self.engine_color = self.MINMATAR_ENGINE
            self.faction = 'minmatar'
        else:
            self.engine_color = self.AMARR_ENGINE
            self.faction = 'amarr'

    def update(self, health_percent=1.0, is_moving=False, shield_active=False):
        """Update animation states."""
        # Update engine animation
        self.engine_timer += 1
        if self.engine_timer >= 3:
            self.engine_timer = 0
            self.engine_frame = (self.engine_frame + 1) % 6

        # Update thrust intensity based on movement
        target_thrust = 0.8 if is_moving else 0.4
        self.thrust_intensity += (target_thrust - self.thrust_intensity) * 0.1

        # Update damage level based on health
        if health_percent > 0.75:
            self.damage_level = 0
        elif health_percent > 0.50:
            self.damage_level = 1
        elif health_percent > 0.25:
            self.damage_level = 2
        else:
            self.damage_level = 3

        # Update damage particles
        self._update_damage_particles()

        # Update shield shimmer
        self.shield_shimmer = (self.shield_shimmer + 0.1) % (math.pi * 2)
        if self.shield_hit_timer > 0:
            self.shield_hit_timer -= 1

    def _update_damage_particles(self):
        """Update fire and smoke particles for damage visualization."""
        # Spawn new particles based on damage level
        if self.damage_level >= 2 and random.random() < 0.3:
            # Smoke particles
            self.smoke_particles.append({
                'x': random.randint(-self.width // 4, self.width // 4),
                'y': random.randint(-self.height // 4, self.height // 4),
                'alpha': 200,
                'size': random.randint(3, 8),
                'drift_x': random.uniform(-0.5, 0.5),
                'drift_y': random.uniform(-1.5, -0.5),
            })

        if self.damage_level >= 3 and random.random() < 0.4:
            # Fire particles
            self.fire_particles.append({
                'x': random.randint(-self.width // 4, self.width // 4),
                'y': random.randint(-self.height // 4, self.height // 4),
                'alpha': 255,
                'size': random.randint(2, 6),
                'life': random.randint(10, 20),
            })

        # Update existing particles
        for p in self.smoke_particles[:]:
            p['x'] += p['drift_x']
            p['y'] += p['drift_y']
            p['alpha'] -= 5
            if p['alpha'] <= 0:
                self.smoke_particles.remove(p)

        for p in self.fire_particles[:]:
            p['life'] -= 1
            p['alpha'] = int(255 * (p['life'] / 20))
            if p['life'] <= 0:
                self.fire_particles.remove(p)

        # Limit particle counts
        self.smoke_particles = self.smoke_particles[-20:]
        self.fire_particles = self.fire_particles[-15:]

    def render(self, surface, x, y, angle=0):
        """Render the ship with all effects at the given position."""
        if self.base_sprite is None:
            return

        # Start with base sprite
        ship_img = self.base_sprite.copy()

        # Apply damage tint
        if self.damage_level > 0:
            ship_img = self._apply_damage_tint(ship_img)

        # Rotate if needed
        if angle != 0:
            ship_img = pygame.transform.rotate(ship_img, angle)

        # Get blit position (centered)
        rect = ship_img.get_rect(center=(x, y))

        # Draw smoke particles (behind ship)
        for p in self.smoke_particles:
            smoke_alpha = min(p['alpha'], 150)
            smoke_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(smoke_surf, (80, 80, 80, smoke_alpha),
                             (p['size'], p['size']), p['size'])
            surface.blit(smoke_surf, (x + p['x'] - p['size'], y + p['y'] - p['size']))

        # Draw ship
        surface.blit(ship_img, rect)

        # Draw fire particles (in front of ship)
        for p in self.fire_particles:
            fire_color = (255, 150 + random.randint(0, 50), 50, p['alpha'])
            fire_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(fire_surf, fire_color, (p['size'], p['size']), p['size'])
            surface.blit(fire_surf, (x + p['x'] - p['size'], y + p['y'] - p['size']),
                        special_flags=pygame.BLEND_RGBA_ADD)

        # Draw engine glow
        self._draw_engine_glow(surface, x, y, angle)

        # Draw shield effect if active
        if self.shield_hit_timer > 0:
            self._draw_shield_hit(surface, x, y)

    def _apply_damage_tint(self, surface):
        """Apply damage coloring to the ship surface."""
        result = surface.copy()

        if self.damage_level == 1:
            # Light damage - slight darkening
            dark = pygame.Surface(result.get_size(), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 30))
            result.blit(dark, (0, 0))
        elif self.damage_level == 2:
            # Moderate damage - orange tint
            tint = pygame.Surface(result.get_size(), pygame.SRCALPHA)
            tint.fill((100, 50, 0, 50))
            result.blit(tint, (0, 0))
        elif self.damage_level == 3:
            # Critical damage - red flicker
            if random.random() < 0.3:
                tint = pygame.Surface(result.get_size(), pygame.SRCALPHA)
                tint.fill((150, 0, 0, 80))
                result.blit(tint, (0, 0))

        return result

    def _draw_engine_glow(self, surface, x, y, angle):
        """Draw engine thrust glow effect."""
        # Calculate engine position (bottom of ship)
        rad = math.radians(angle)
        engine_offset_y = self.height // 2 + 5
        engine_x = x - math.sin(rad) * engine_offset_y
        engine_y = y + math.cos(rad) * engine_offset_y

        # Glow intensity with flicker
        intensity = self.thrust_intensity * (0.8 + 0.2 * math.sin(self.engine_frame * 0.5))

        # Draw glow layers
        for i in range(3):
            radius = int((10 - i * 2) * intensity)
            if radius > 0:
                alpha = int((150 - i * 40) * intensity)
                glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                color = (*self.engine_color[:3], alpha)
                pygame.draw.circle(glow_surf, color, (radius, radius), radius)
                surface.blit(glow_surf,
                           (engine_x - radius, engine_y - radius),
                           special_flags=pygame.BLEND_RGBA_ADD)

    def _draw_shield_hit(self, surface, x, y):
        """Draw shield impact effect."""
        radius = max(self.width, self.height) // 2 + 10
        alpha = int(150 * (self.shield_hit_timer / 15))

        shield_surf = pygame.Surface((radius * 2 + 20, radius * 2 + 20), pygame.SRCALPHA)
        shimmer = int(20 * math.sin(self.shield_shimmer * 3))

        # Outer ring
        pygame.draw.circle(shield_surf, (*self.SHIELD_COLOR[:3], alpha),
                          (radius + 10, radius + 10), radius, 3)
        # Inner shimmer
        pygame.draw.circle(shield_surf, (*self.SHIELD_COLOR[:3], alpha // 2 + shimmer),
                          (radius + 10, radius + 10), radius - 5, 2)

        surface.blit(shield_surf, (x - radius - 10, y - radius - 10),
                    special_flags=pygame.BLEND_RGBA_ADD)

    def trigger_shield_hit(self):
        """Trigger shield hit visual effect."""
        self.shield_hit_timer = 15

    def get_thrust_frames(self):
        """Get thrust animation frames from ship_assets if available."""
        if not SHIP_ASSETS_AVAILABLE or self.type_id is None:
            return None

        manager = get_ship_asset_manager()
        if manager and self.type_id in manager.thrust_effects:
            return manager.thrust_effects[self.type_id]
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
        self.is_jaguar = False
        self.width = 46
        self.height = 58

        # Ship renderer for advanced effects (initialized after ship selection)
        self.ship_renderer = None
        self._current_ship_name = 'rifter'

        self.base_image = self._create_ship_image()  # Store base for animation
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect()

        # Engine animation state
        self.engine_timer = 0
        self.engine_flicker = 1.0
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

        # Combat maneuvers (LB/RB bumpers for thrust)
        self.thrust_active = False
        self.thrust_timer = 0
        self.thrust_cooldown = 0
        self.thrust_duration = 12  # frames (~0.2 sec) - quick burst
        self.thrust_cooldown_time = 90  # 1.5 seconds - faster recovery
        self.thrust_direction = 0  # -1 left, 1 right
        self.thrust_velocity = 0  # Current thrust speed

        self.emergency_brake_active = False
        self.emergency_brake_timer = 0
        self.emergency_brake_cooldown = 0
        self.emergency_brake_duration = 8  # frames - fast snap to bottom
        self.emergency_brake_cooldown_time = 180  # 3 seconds
        self.brake_start_y = 0

        # Frontal shield system (Jaguar only - defaults inactive)
        # Provides 180-degree frontal immunity when active
        self.frontal_shield_active = False
        self.frontal_shield_timer = 0
        self.frontal_shield_duration = 0  # 0 = disabled for non-Jaguar
        self.frontal_shield_cooldown = 0
        self.frontal_shield_cooldown_time = 999999  # Effectively disabled

        # Rocket stream mode (Jaguar only)
        self.rocket_stream_mode = False
        self.rocket_stream_cooldown = 0
        self.rocket_stream_rate = 4

        # Armor regen (Wolf only - defaults inactive)
        self.armor_regen_active = False
        self.armor_regen_rate = 0
        self.armor_regen_delay = 120
        self.armor_regen_timer = 0

        # Weapon heat system - balanced for continuous fire
        self.heat = 0
        self.max_heat = 100
        self.heat_per_shot = 2.0  # Base heat per shot - balanced for sustained fire
        self.heat_dissipation = 1.2  # Cooling rate per frame
        self.is_overheated = False
        self.heat_warning = False  # True when heat >= 75%

        # Score/Progress
        self.refugees = 0
        self.total_refugees = 0
        self.score = 0
    
    def _create_ship_image(self):
        """Create EVE-accurate Minmatar ship sprite with proper loadouts"""
        ship_class = getattr(self, 'ship_class', 'Rifter')

        # Determine which ship to load based on ship class
        if self.is_wolf:
            ship_name = 'wolf'
        elif self.is_jaguar:
            ship_name = 'jaguar'
        else:
            ship_name = 'rifter'

        self._current_ship_name = ship_name

        # Initialize ship renderer for effects
        self.ship_renderer = ShipRenderer(ship_name, is_player=True)

        # Try to load from EVE assets first
        sprite = load_ship_sprite(ship_name, (self.width, self.height))
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
        """Upgrade to Wolf assault frigate - autocannon barrage specialist with armor tank"""
        self.is_wolf = True
        self.ship_class = 'Wolf'
        # Wolf is slightly slower but tankier
        self.speed *= 0.95  # Slightly slower than Rifter
        self.max_armor += WOLF_ARMOR_BONUS * 1.5  # Extra armor
        self.max_hull += WOLF_HULL_BONUS
        self.armor = min(self.armor + WOLF_ARMOR_BONUS * 1.5, self.max_armor)
        self.hull = min(self.hull + WOLF_HULL_BONUS, self.max_hull)
        self.spread_bonus += 2  # More autocannons = wider spread

        # === WOLF AUTOCANNON BARRAGE ===
        # Faster fire rate for endless barrage
        self.fire_rate_mult *= 1.5  # 50% faster autocannon fire
        self.damage_bonus *= 1.2  # 20% more damage per shot

        # === WOLF ARMOR REGEN SYSTEM ===
        # Fast passive armor repair nanites
        self.armor_regen_active = True
        self.armor_regen_rate = 0.3  # Armor points per frame (~18/sec at 60fps) - FAST
        self.armor_regen_delay = 90  # 1.5 sec without damage before regen starts
        self.armor_regen_timer = 0

        # === WOLF SEEKER MISSILES (Secondary - LT) ===
        self.wolf_seeking_rockets = True
        self.max_rockets = 16
        self.rockets = 16

        # Heavier ship = slower thrust recovery
        self.thrust_cooldown_time = 75  # 1.25 seconds

        self.base_image = self._create_ship_image()
        self.image = self.base_image.copy()

    def upgrade_to_jaguar(self):
        """Upgrade to Jaguar assault frigate - fast, agile, seeking rocket specialist"""
        from constants import JAGUAR_SPEED_BONUS, JAGUAR_SHIELD_BONUS
        self.is_jaguar = True  # T2 Jaguar flag
        self.ship_class = 'Jaguar'
        # Jaguar is the fastest assault frigate
        self.speed *= JAGUAR_SPEED_BONUS * 1.15  # Extra 15% on top of base bonus
        self.max_shields += JAGUAR_SHIELD_BONUS
        self.shields = min(self.shields + JAGUAR_SHIELD_BONUS, self.max_shields)

        # === JAGUAR THRUST UPGRADES ===
        # Double thrust duration (24 frames ~0.4 sec burst)
        self.thrust_duration = 24
        # Twice the thrust regen (half cooldown - 30 frames = 0.5 sec)
        self.thrust_cooldown_time = 30

        # === JAGUAR SHIELD BUBBLE (LT) ===
        # 360-degree immunity shield bubble - blocks ALL damage
        self.frontal_shield_active = False
        self.frontal_shield_timer = 0
        self.frontal_shield_duration = 420   # 7 seconds at 60fps (middle of 5-10 range)
        self.frontal_shield_cooldown = 0
        self.frontal_shield_cooldown_time = 1200  # 20 seconds cooldown
        self.shield_bubble_mode = True  # True = 360 bubble, False = frontal only

        # === JAGUAR ROCKET STREAMS (Main Weapon) ===
        # Seeking rockets as main weapon - no autocannons
        self.rocket_stream_mode = True  # Use rockets instead of bullets
        self.rocket_stream_cooldown = 0
        self.rocket_stream_rate = 4  # Frames between rockets (FAST)
        self.max_rockets = 999  # Effectively unlimited - seeking rockets ARE the weapon
        self.rockets = 999

        self.base_image = self._create_ship_image()
        self.image = self.base_image.copy()

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

    # === JAGUAR FRONTAL SHIELD SYSTEM ===
    def can_frontal_shield(self):
        """Check if Jaguar can activate frontal shield"""
        if getattr(self, 'ship_class', 'Rifter') != 'Jaguar':
            return False
        cooldown = getattr(self, 'frontal_shield_cooldown', 0)
        return cooldown <= 0

    def activate_frontal_shield(self):
        """Activate Jaguar's frontal shield (LT) - 10 sec immunity, 15 sec regen"""
        if not self.can_frontal_shield():
            return False
        self.frontal_shield_active = True
        self.frontal_shield_timer = self.frontal_shield_duration
        self.frontal_shield_cooldown = self.frontal_shield_cooldown_time
        return True

    def is_frontal_shield_active(self):
        """Check if frontal shield is currently active"""
        return getattr(self, 'frontal_shield_active', False)

    def update_frontal_shield(self):
        """Update frontal shield timers (call each frame)"""
        if getattr(self, 'frontal_shield_cooldown', 0) > 0:
            self.frontal_shield_cooldown -= 1

        if getattr(self, 'frontal_shield_active', False):
            self.frontal_shield_timer -= 1
            if self.frontal_shield_timer <= 0:
                self.frontal_shield_active = False

    def is_hit_from_front(self, bullet_y):
        """Check if a hit came from the front (above the player)"""
        # Front 180 degrees = anything hitting from above player center
        return bullet_y < self.rect.centery

    def get_frontal_shield_percent(self):
        """Get remaining shield time as percentage for HUD"""
        if not self.is_frontal_shield_active() or self.frontal_shield_duration <= 0:
            return 0
        return self.frontal_shield_timer / self.frontal_shield_duration

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

        # Track if moving for engine intensity
        is_moving = False

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= current_speed
            is_moving = True
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += current_speed
            is_moving = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= current_speed
            is_moving = True
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += current_speed
            is_moving = True

        # Keep on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Animate engine glow
        self._update_engine_animation(is_moving)

        # Weapon heat management - heat always dissipates
        # When overheated: 50% slower dissipation, ends when heat drops below 50%
        if self.is_overheated:
            # Slower cooling when overheated
            self.heat = max(0, self.heat - self.heat_dissipation * 0.5)
            # Exit overheat when cooled to 50%
            if self.heat <= self.max_heat * 0.5:
                self.is_overheated = False
        else:
            # Normal heat dissipation
            self.heat = max(0, self.heat - self.heat_dissipation)

        # Track heat warning state for HUD (75% threshold)
        self.heat_warning = self.heat >= self.max_heat * 0.75

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

    def _update_engine_animation(self, is_moving):
        """Update engine glow animation"""
        self.engine_timer += 1

        # Engine flicker - more intense when moving
        base_flicker = 0.7 + 0.3 * math.sin(self.engine_timer * 0.15)
        if is_moving:
            self.engine_flicker = 0.9 + 0.1 * math.sin(self.engine_timer * 0.25)
        else:
            self.engine_flicker = base_flicker * 0.8

        # Recreate image with animated engine
        self.image = self.base_image.copy()
        w, h = self.image.get_size()
        cx = w // 2

        # Determine engine color based on ship class
        ship_class = getattr(self, 'ship_class', 'Rifter')
        if ship_class == 'Jaguar':
            engine_base = (80, 180, 255)
            engine_bright = (150, 220, 255)
        else:
            engine_base = (255, 120, 40)
            engine_bright = (255, 200, 100)

        # Calculate animated engine intensity
        intensity = self.engine_flicker
        glow_alpha = int(180 * intensity)

        # Draw animated engine exhaust plume
        exhaust_surf = pygame.Surface((w, 20), pygame.SRCALPHA)

        # Outer glow
        for i in range(3):
            glow_size = 8 + i * 4
            glow_y = 5 + i * 3
            alpha = int(glow_alpha * (0.5 - i * 0.15))
            if alpha > 0:
                pygame.draw.ellipse(exhaust_surf, (*engine_base, alpha),
                                  (cx - glow_size, glow_y, glow_size * 2, 8))

        # Core bright exhaust
        core_size = int(6 * intensity)
        pygame.draw.ellipse(exhaust_surf, (*engine_bright, int(200 * intensity)),
                          (cx - core_size, 3, core_size * 2, 6))

        # Hot white center
        if intensity > 0.8:
            pygame.draw.ellipse(exhaust_surf, (255, 255, 255, int(150 * intensity)),
                              (cx - 3, 4, 6, 4))

        # Add exhaust particles when moving
        if is_moving and random.random() < 0.4:
            px = cx + random.randint(-5, 5)
            py = random.randint(8, 15)
            pygame.draw.circle(exhaust_surf, (*engine_bright, 150), (px, py), 2)

        # Blit exhaust below ship (at bottom of image)
        self.image.blit(exhaust_surf, (0, h - 12))

    def can_shoot(self):
        """Check if enough time has passed to fire"""
        # Heat system: overheating no longer blocks shooting, just penalizes
        # Weapons can ALWAYS fire - heat only affects powerups
        now = pygame.time.get_ticks()
        ammo = AMMO_TYPES[self.current_ammo]
        fire_rate = ammo['fire_rate'] * self.fire_rate_mult * self.get_fire_rate_bonus()

        # When overheated: 30% slower fire rate as a penalty
        if self.is_overheated:
            fire_rate *= 0.7

        cooldown = PLAYER_BASE_FIRE_RATE / fire_rate
        return now - self.last_shot > cooldown
    
    def shoot(self):
        """Fire autocannons, returns list of bullets

        Fire patterns:
        - 'focused': All bullets fire straight forward (or converging)
        - 'spread': Bullets fan out for wider coverage
        """
        if not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()
        bullets = []
        ship_class = getattr(self, 'ship_class', 'Rifter')
        fire_pattern = getattr(self, 'fire_pattern', 'focused')

        # Default bullet color (Minmatar orange/rust)
        bullet_color = (255, 180, 100)

        # Apply damage bonus from abilities
        damage_bonus = self.get_damage_bonus()
        bullet_damage = int(BULLET_DAMAGE * damage_bonus)

        # Wolf: Autocannon barrage specialist
        if ship_class == 'Wolf':
            if fire_pattern == 'spread':
                # 240-degree arc spread: bullets every 20 degrees
                # From -120 to +120 degrees = 13 bullets covering 240 degrees
                angles = list(range(-120, 121, 20))  # [-120, -100, -80, ..., 100, 120]
                for angle in angles:
                    rad = math.radians(angle)
                    vx = math.sin(rad) * BULLET_SPEED
                    vy = -math.cos(rad) * BULLET_SPEED
                    # Spawn from edge of ship based on angle
                    spawn_offset_x = int(math.sin(rad) * 15)
                    spawn_offset_y = int(-math.cos(rad) * 10)
                    bullet = Bullet(
                        self.rect.centerx + spawn_offset_x,
                        self.rect.centery + spawn_offset_y,
                        vx, vy,
                        bullet_color,
                        int(bullet_damage * 0.7)  # Slightly less damage per bullet due to volume
                    )
                    bullets.append(bullet)
            else:
                # Focused: 4 weapons forward in tight formation
                num_shots = 4
                offsets = [-18, -6, 6, 18]
                for offset in offsets:
                    bullet = Bullet(
                        self.rect.centerx + offset,
                        self.rect.top,
                        0, -BULLET_SPEED,
                        bullet_color,
                        bullet_damage
                    )
                    bullets.append(bullet)

        elif ship_class == 'Jaguar':
            # Jaguar: SEEKING ROCKET STREAMS - no autocannons!
            # Check rocket stream cooldown (fast fire rate)
            rocket_stream_cooldown = getattr(self, 'rocket_stream_cooldown', 0)
            if rocket_stream_cooldown > 0:
                return []  # Still on cooldown

            rockets = []

            if fire_pattern == 'spread':
                # 180-degree arc spread: seeking rockets every 20 degrees
                # From -90 to +90 degrees = 10 rockets covering front hemisphere
                angles = list(range(-90, 91, 20))  # [-90, -70, -50, ..., 70, 90]
                for angle in angles:
                    rad = math.radians(angle)
                    # Spawn from edge of ship based on angle
                    spawn_offset_x = int(math.sin(rad) * 12)
                    spawn_offset_y = int(-math.cos(rad) * 8)
                    rocket = Rocket(
                        self.rect.centerx + spawn_offset_x,
                        self.rect.centery + spawn_offset_y,
                        seeking=True,
                        initial_angle=angle  # Launch in this direction
                    )
                    rocket.damage = int(ROCKET_DAMAGE * 0.25 * self.get_damage_bonus())
                    rocket.turn_rate = 0.22  # Agile seeking
                    rockets.append(rocket)
                # Longer cooldown for spread volley
                self.rocket_stream_cooldown = 8
            else:
                # Focused: 4 seeking rockets forward (quad launchers)
                offsets = [-12, -4, 4, 12]
                for offset in offsets:
                    rocket = Rocket(
                        self.rect.centerx + offset,
                        self.rect.top,
                        seeking=True
                    )
                    rocket.damage = int(ROCKET_DAMAGE * 0.3 * self.get_damage_bonus())
                    rocket.turn_rate = 0.28  # Very agile seeking
                    rockets.append(rocket)
                # Fast cooldown for focused fire
                self.rocket_stream_cooldown = getattr(self, 'rocket_stream_rate', 4)

            # Minimal heat for rocket streams
            self.heat += 2
            if self.heat >= self.max_heat:
                self.is_overheated = True
                self.overheat_cooldown = self.overheat_duration

            return rockets  # Return rockets instead of bullets

        else:
            # Rifter: 2-4 autocannons based on upgrades
            num_shots = 2 + self.spread_bonus

            if fire_pattern == 'spread':
                # 45-degree arc: front-focused fan
                if num_shots == 2:
                    angles = [-22, 22]
                elif num_shots == 3:
                    angles = [-22, 0, 22]
                else:  # 4+
                    angles = [-22, -8, 8, 22]
            else:
                # Focused: all weapons forward only
                angles = [0] * num_shots

            spread_offset = 12 + (self.spread_bonus * 4)
            for i in range(num_shots):
                offset = (i - (num_shots - 1) / 2) * spread_offset
                angle = angles[i] if i < len(angles) else 0
                rad = math.radians(angle)
                vx = math.sin(rad) * BULLET_SPEED
                vy = -math.cos(rad) * BULLET_SPEED
                bullet = Bullet(
                    self.rect.centerx + offset,
                    self.rect.top,
                    vx, vy,
                    bullet_color,
                    bullet_damage
                )
                bullets.append(bullet)

        # Add heat when firing - balanced by ship class and ammo type
        now = pygame.time.get_ticks()
        ammo = AMMO_TYPES[self.current_ammo]

        # Base heat from ammo type (higher damage = more heat)
        ammo_heat_mult = {
            0: 1.0,   # Standard - balanced
            1: 1.3,   # EMP - electronic stress
            2: 0.8,   # Phased Plasma - efficient
            3: 1.5,   # Fusion - explosive heat
            4: 1.2,   # Depleted Uranium - heavy rounds
            5: 0.7,   # Titanium Sabot - cool ammo
        }.get(self.current_ammo, 1.0)

        heat_to_add = self.heat_per_shot * ammo_heat_mult

        # Wolf: 4 guns = more heat per volley
        if ship_class == 'Wolf':
            heat_to_add *= 1.4

        # Jaguar: Assault ship efficiency = less heat
        if ship_class == 'Jaguar':
            heat_to_add *= 0.85

        # More heat when damage powerups active (pushing the guns harder)
        if now < self.double_damage_until:
            heat_to_add *= 1.2
        if now < self.rapid_fire_until:
            heat_to_add *= 1.15

        self.heat += heat_to_add

        # Check for overheat threshold
        if self.heat >= self.max_heat and not self.is_overheated:
            self.is_overheated = True
            self.expire_all_powerups()  # Penalty for overheating

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

        # Jaguar: Fire 4 seeking rockets at once (from 4 launchers)
        if ship_class == 'Jaguar':
            rockets = []
            for offset in [-18, -6, 6, 18]:  # 4 rocket launchers spread wide
                self.rockets -= 1
                if self.rockets < 0:
                    self.rockets = 0
                    break
                # Jaguar rockets are seeking missiles
                rocket = Rocket(self.rect.centerx + offset, self.rect.top, seeking=True)
                rocket.damage = int(ROCKET_DAMAGE * self.get_damage_bonus() * 0.7)  # Slightly less per rocket
                rockets.append(rocket)
            return rockets if rockets else None

        # Wolf: Fire 2 seeking rockets (assault frigate with rocket bonus)
        elif ship_class == 'Wolf':
            rockets = []
            for offset in [-10, 10]:  # Dual launchers
                self.rockets -= 1
                if self.rockets < 0:
                    self.rockets = 0
                    break
                # Wolf rockets are also seeking
                rocket = Rocket(self.rect.centerx + offset, self.rect.top, seeking=True)
                rocket.damage = int(ROCKET_DAMAGE * self.get_damage_bonus() * 1.1)  # Slightly more damage
                rockets.append(rocket)
            return rockets if rockets else None

        else:
            # Rifter: Standard single rocket
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

        # Reset Wolf armor regen timer when taking damage
        if hasattr(self, 'armor_regen_timer'):
            self.armor_regen_timer = 0

        return self.hull <= 0  # Return True if dead

    def update_armor_regen(self):
        """Update Wolf's passive armor regeneration"""
        if not getattr(self, 'armor_regen_active', False):
            return

        # Increment timer (counts frames without damage)
        self.armor_regen_timer += 1

        # Only regen after delay period
        if self.armor_regen_timer >= self.armor_regen_delay:
            # Regenerate armor up to max
            if self.armor < self.max_armor:
                self.armor = min(self.armor + self.armor_regen_rate, self.max_armor)
    
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
        self.width = 35
        self.height = 44

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
        """Create exact scaled copy of player Rifter sprite (76% scale)"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        w, h = self.width, self.height
        cx = w // 2

        # Scale factor from player (46x58) to wingman (35x44)
        s = 0.76

        # Exact same Rifter colors as player
        base = (70, 40, 30)
        mid = (110, 60, 40)
        light = (150, 85, 55)
        highlight = (190, 120, 80)
        accent = (200, 160, 80)
        engine_color = (255, 120, 40)
        engine_glow = (255, 180, 100)

        # === RIFTER HULL (exact copy, scaled) ===
        # Shadow layer (3D depth)
        hull_shadow = [(cx, int(5*s)), (cx+int(18*s), int(25*s)), (cx+int(15*s), int(50*s)),
                       (cx, int(55*s)), (cx-int(15*s), int(50*s)), (cx-int(18*s), int(25*s))]
        pygame.draw.polygon(surf, base, hull_shadow)

        # Main hull body
        hull_main = [(cx, int(8*s)), (cx+int(15*s), int(25*s)), (cx+int(12*s), int(48*s)),
                     (cx, int(52*s)), (cx-int(12*s), int(48*s)), (cx-int(15*s), int(25*s))]
        pygame.draw.polygon(surf, mid, hull_main)

        # Hull highlight (top-right lighting)
        hull_highlight = [(cx, int(10*s)), (cx+int(12*s), int(25*s)), (cx+int(10*s), int(40*s)), (cx+int(2*s), int(45*s))]
        pygame.draw.polygon(surf, light, hull_highlight)

        # Nose section (pointed)
        pygame.draw.polygon(surf, light, [(cx, int(3*s)), (cx+int(8*s), int(18*s)), (cx, int(22*s)), (cx-int(8*s), int(18*s))])
        pygame.draw.polygon(surf, highlight, [(cx, int(5*s)), (cx+int(5*s), int(16*s)), (cx, int(18*s))])

        # === WING STRUTS (Minmatar asymmetric style) ===
        pygame.draw.polygon(surf, base, [(cx-int(12*s), int(28*s)), (int(5*s), int(38*s)), (int(3*s), int(45*s)), (int(8*s), int(48*s)), (cx-int(10*s), int(42*s))])
        pygame.draw.polygon(surf, mid, [(cx-int(11*s), int(30*s)), (int(7*s), int(39*s)), (int(6*s), int(44*s)), (cx-int(9*s), int(40*s))])
        pygame.draw.polygon(surf, base, [(cx+int(12*s), int(28*s)), (w-int(5*s), int(38*s)), (w-int(3*s), int(45*s)), (w-int(8*s), int(48*s)), (cx+int(10*s), int(42*s))])
        pygame.draw.polygon(surf, light, [(cx+int(11*s), int(30*s)), (w-int(7*s), int(39*s)), (w-int(6*s), int(44*s)), (cx+int(9*s), int(40*s))])

        # Wing tips
        pygame.draw.circle(surf, accent, (int(4*s), int(44*s)), max(2, int(3*s)))
        pygame.draw.circle(surf, accent, (w-int(4*s), int(44*s)), max(2, int(3*s)))

        # === COCKPIT ===
        pygame.draw.ellipse(surf, (40, 60, 80), (cx-int(4*s), int(14*s), int(8*s), int(12*s)))
        pygame.draw.ellipse(surf, (70, 100, 140), (cx-int(3*s), int(15*s), int(6*s), int(8*s)))
        pygame.draw.ellipse(surf, (120, 160, 200), (cx-int(2*s), int(16*s), max(2, int(3*s)), max(3, int(4*s))))

        # === ENGINE SECTION ===
        pygame.draw.polygon(surf, base, [(cx-int(10*s), int(45*s)), (cx+int(10*s), int(45*s)), (cx+int(8*s), int(56*s)), (cx-int(8*s), int(56*s))])
        pygame.draw.ellipse(surf, engine_color, (cx-int(6*s), int(52*s), int(12*s), int(6*s)))
        pygame.draw.ellipse(surf, engine_glow, (cx-int(4*s), int(53*s), int(8*s), int(4*s)))
        pygame.draw.ellipse(surf, (255, 255, 200), (cx-int(2*s), int(54*s), max(3, int(4*s)), max(2, int(2*s))))

        # Side thrusters
        pygame.draw.ellipse(surf, engine_color, (cx-int(12*s), int(50*s), int(5*s), int(4*s)))
        pygame.draw.ellipse(surf, engine_color, (cx+int(7*s), int(50*s), int(5*s), int(4*s)))

        # Panel lines
        pygame.draw.line(surf, base, (cx, int(22*s)), (cx, int(45*s)), 1)
        pygame.draw.line(surf, accent, (cx-int(5*s), int(30*s)), (cx-int(5*s), int(44*s)), 1)
        pygame.draw.line(surf, accent, (cx+int(5*s), int(30*s)), (cx+int(5*s), int(44*s)), 1)

        # Antennae
        pygame.draw.line(surf, accent, (cx-int(3*s), int(6*s)), (cx-int(8*s), int(2*s)), 2)
        pygame.draw.circle(surf, highlight, (cx-int(8*s), int(2*s)), max(1, int(2*s)))
        pygame.draw.line(surf, accent, (cx+int(3*s), int(6*s)), (cx+int(6*s), int(3*s)), 1)

        return surf

    def update(self):
        """Follow player with offset and animate engine"""
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

        # Animate engine glow
        self._update_engine_animation()

    def _update_engine_animation(self):
        """Redraw sprite with animated engine flicker and visual polish"""
        # Recreate base sprite
        self.image = self._create_wingman_sprite()

        # Add engine flicker effect
        w, h = self.width, self.height
        cx = w // 2
        s = 0.76
        now = pygame.time.get_ticks()

        # Flickering engine glow - more dynamic
        flicker = 0.7 + 0.3 * math.sin(now * 0.025)
        fast_flicker = 0.8 + 0.2 * math.sin(now * 0.08)
        glow_alpha = int(140 * flicker)

        # Engine exhaust plume (layered glow)
        glow_surf = pygame.Surface((w, h + 15), pygame.SRCALPHA)

        # Outer glow haze
        pygame.draw.ellipse(glow_surf, (255, 100, 30, int(50 * flicker)),
                          (cx - int(12*s), int(52*s), int(24*s), int(18*s)))

        # Main engine exhaust
        pygame.draw.ellipse(glow_surf, (255, 150, 50, glow_alpha),
                          (cx - int(8*s), int(54*s), int(16*s), int(12*s)))

        # Inner bright core
        pygame.draw.ellipse(glow_surf, (255, 200, 100, int(180 * fast_flicker)),
                          (cx - int(5*s), int(55*s), int(10*s), int(8*s)))

        # Hot white center
        pygame.draw.ellipse(glow_surf, (255, 255, 220, int(200 * fast_flicker)),
                          (cx - int(3*s), int(56*s), int(6*s), int(4*s)))

        # Exhaust particles (random sparkles)
        if random.random() < 0.5:
            px = cx + random.randint(-6, 6)
            py = int(58*s) + random.randint(0, 8)
            pygame.draw.circle(glow_surf, (255, 180, 80, 150), (px, py), random.randint(1, 3))

        self.image.blit(glow_surf, (0, 0))

        # Add damage visualization if damaged
        health_pct = self.health / self.max_health
        if health_pct < 0.7:
            # Smoke effect when damaged
            smoke_alpha = int(80 * (1 - health_pct))
            smoke_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            for _ in range(int((1 - health_pct) * 5)):
                sx = random.randint(5, w - 5)
                sy = random.randint(5, h - 10)
                pygame.draw.circle(smoke_surf, (60, 60, 60, smoke_alpha), (sx, sy), random.randint(2, 5))
            self.image.blit(smoke_surf, (0, 0))

        # Edge highlight glow for visibility
        edge_surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
        pygame.draw.rect(edge_surf, (255, 180, 100, 30), (0, 0, w + 4, h + 4), 2, border_radius=3)
        # self.image.blit(edge_surf, (-2, -2))  # Subtle edge - commented for cleaner look

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
    """Autocannon projectile - chunky Minmatar tracer rounds with motion blur"""

    def __init__(self, x, y, dx, dy, color, damage, shield_mult=1.0, armor_mult=1.0):
        super().__init__()
        # Larger surface for glow and trail
        self.image = pygame.Surface((20, 32), pygame.SRCALPHA)
        cx, cy = 10, 12

        # Motion blur trail (long fade behind projectile)
        for i in range(8):
            trail_alpha = int(50 - i * 6)
            trail_y = cy + 4 + i * 2
            trail_width = max(2, 6 - i)
            pygame.draw.ellipse(self.image, (*color[:3], trail_alpha),
                              (cx - trail_width//2, trail_y, trail_width, 4))

        # Outer glow halo
        for r in range(8, 2, -2):
            glow_alpha = int(40 * (8 - r) / 6)
            pygame.draw.circle(self.image, (*color[:3], glow_alpha), (cx, cy), r)

        # Hot core (white center fading to color)
        pygame.draw.ellipse(self.image, color, (cx - 3, cy - 5, 6, 12))
        pygame.draw.ellipse(self.image, (255, 230, 180), (cx - 2, cy - 4, 4, 8))
        pygame.draw.ellipse(self.image, (255, 255, 255), (cx - 1, cy - 3, 2, 5))

        # Bright tip (impact point)
        pygame.draw.circle(self.image, (255, 255, 255), (cx, cy - 4), 3)
        pygame.draw.circle(self.image, (255, 255, 220), (cx, cy - 5), 2)

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
    """Rocket projectile - can be seeking (homing) for Jaguar. Polished visuals with trails."""

    def __init__(self, x, y, seeking=False, initial_angle=0):
        super().__init__()
        self.seeking = seeking
        self.target = None
        # Initial velocity based on launch angle (0 = up, positive = right)
        rad = math.radians(initial_angle)
        self.vx = math.sin(rad) * ROCKET_SPEED
        self.vy = -math.cos(rad) * ROCKET_SPEED
        self.turn_rate = 0.15 if seeking else 0  # How fast it can turn
        self.angle = initial_angle  # Track current angle for rotation

        # Trail system for polished visuals
        self.trail_positions = []
        self.trail_max_length = 12 if seeking else 8
        self.trail_timer = 0

        # Create polished base image
        self.base_image = pygame.Surface((12, 24), pygame.SRCALPHA)
        w, h = 12, 24
        cx = w // 2

        if seeking:
            # Seeking rockets - sleek blue missiles with glow
            # Body gradient
            pygame.draw.polygon(self.base_image, (70, 120, 180), [(cx, 2), (cx-3, 8), (cx-3, 18), (cx+3, 18), (cx+3, 8)])
            pygame.draw.polygon(self.base_image, (100, 160, 220), [(cx, 3), (cx-2, 8), (cx-2, 16), (cx+2, 16), (cx+2, 8)])
            # Nose cone
            pygame.draw.polygon(self.base_image, (150, 200, 255), [(cx, 0), (cx-3, 7), (cx+3, 7)])
            pygame.draw.polygon(self.base_image, (200, 230, 255), [(cx, 1), (cx-1, 5), (cx+1, 5)])
            # Fins
            pygame.draw.polygon(self.base_image, (60, 100, 160), [(cx-3, 16), (cx-5, 20), (cx-3, 20)])
            pygame.draw.polygon(self.base_image, (60, 100, 160), [(cx+3, 16), (cx+5, 20), (cx+3, 20)])
            # Engine glow
            pygame.draw.ellipse(self.base_image, (100, 200, 255), (cx-2, 18, 4, 4))
            pygame.draw.ellipse(self.base_image, (200, 240, 255), (cx-1, 19, 2, 2))
            self.trail_color = (80, 160, 255)
            self.glow_color = (100, 180, 255)
        else:
            # Standard rockets - orange/red with fire trail
            pygame.draw.polygon(self.base_image, (120, 100, 90), [(cx, 2), (cx-3, 8), (cx-3, 18), (cx+3, 18), (cx+3, 8)])
            pygame.draw.polygon(self.base_image, (160, 130, 100), [(cx, 3), (cx-2, 8), (cx-2, 16), (cx+2, 16), (cx+2, 8)])
            # Warhead
            pygame.draw.polygon(self.base_image, (200, 60, 40), [(cx, 0), (cx-3, 7), (cx+3, 7)])
            pygame.draw.polygon(self.base_image, (255, 100, 60), [(cx, 1), (cx-1, 5), (cx+1, 5)])
            # Fins
            pygame.draw.polygon(self.base_image, (100, 80, 70), [(cx-3, 16), (cx-5, 20), (cx-3, 20)])
            pygame.draw.polygon(self.base_image, (100, 80, 70), [(cx+3, 16), (cx+5, 20), (cx+3, 20)])
            # Engine fire
            pygame.draw.polygon(self.base_image, (255, 200, 50), [(cx-2, 18), (cx, 23), (cx+2, 18)])
            pygame.draw.polygon(self.base_image, (255, 255, 150), [(cx-1, 19), (cx, 22), (cx+1, 19)])
            self.trail_color = (255, 150, 50)
            self.glow_color = (255, 200, 100)

        # Apply initial rotation if launching at an angle
        if initial_angle != 0:
            self.image = pygame.transform.rotate(self.base_image, -initial_angle)
        else:
            self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.damage = ROCKET_DAMAGE
        self.shield_mult = 1.2
        self.armor_mult = 1.2

    def set_targets(self, targets_group):
        """Set the sprite group to seek targets from"""
        self.targets_group = targets_group

    def update(self):
        # Update trail - store position every other frame
        self.trail_timer += 1
        if self.trail_timer >= 2:
            self.trail_timer = 0
            self.trail_positions.append((self.rect.centerx, self.rect.centery))
            if len(self.trail_positions) > self.trail_max_length:
                self.trail_positions.pop(0)

        if self.seeking and hasattr(self, 'targets_group') and self.targets_group:
            # Find closest target
            closest_dist = float('inf')
            closest_target = None
            for target in self.targets_group:
                dx = target.rect.centerx - self.rect.centerx
                dy = target.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_target = target

            # Turn toward target
            if closest_target and closest_dist < 400:  # Only seek within range
                dx = closest_target.rect.centerx - self.rect.centerx
                dy = closest_target.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    # Calculate desired velocity
                    target_vx = (dx / dist) * ROCKET_SPEED
                    target_vy = (dy / dist) * ROCKET_SPEED
                    # Smoothly turn toward target
                    self.vx += (target_vx - self.vx) * self.turn_rate
                    self.vy += (target_vy - self.vy) * self.turn_rate

            # Normalize velocity to maintain speed
            speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
            if speed > 0:
                self.vx = (self.vx / speed) * ROCKET_SPEED
                self.vy = (self.vy / speed) * ROCKET_SPEED

        # Rotate sprite to match velocity direction
        angle = math.degrees(math.atan2(-self.vx, -self.vy))
        self.image = pygame.transform.rotate(self.base_image, angle)
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

        # Move
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Kill if off screen
        if (self.rect.bottom < -50 or self.rect.top > SCREEN_HEIGHT + 50 or
            self.rect.right < -50 or self.rect.left > SCREEN_WIDTH + 50):
            self.kill()

    def draw_trail(self, surface):
        """Draw rocket exhaust trail"""
        if len(self.trail_positions) < 2:
            return

        # Draw fading trail segments
        for i, (x, y) in enumerate(self.trail_positions):
            # Fade based on position in trail
            alpha = int(180 * (i + 1) / len(self.trail_positions))
            size = max(1, int(4 * (i + 1) / len(self.trail_positions)))

            # Create trail particle
            r, g, b = self.trail_color
            trail_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(trail_surf, (r, g, b, alpha), (size, size), size)
            surface.blit(trail_surf, (x - size, y - size))


class EnemyBullet(pygame.sprite.Sprite):
    """Enemy laser projectile with visual variants for different ship classes"""

    # Bullet style types
    STYLE_NORMAL = 0       # Standard frigate laser
    STYLE_CRUISER = 1      # Heavy cruiser beam - thick, intense
    STYLE_BATTLECRUISER = 2  # Massive BC laser - huge, glowing
    STYLE_BEAM = 3         # Continuous beam effect
    STYLE_PLASMA = 4       # Plasma ball for bombers

    def __init__(self, x, y, dx, dy, damage=10, style=0):
        super().__init__()
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.style = style
        self.age = 0  # For animated effects

        # Create visual based on style
        if style == self.STYLE_CRUISER:
            # Heavy cruiser beam - thick golden laser with corona
            self.image = pygame.Surface((8, 28), pygame.SRCALPHA)
            # Outer glow
            pygame.draw.rect(self.image, (255, 180, 50, 80), (0, 0, 8, 28), border_radius=2)
            # Core beam
            pygame.draw.rect(self.image, (255, 220, 100), (1, 0, 6, 28), border_radius=1)
            pygame.draw.rect(self.image, (255, 255, 200), (2, 0, 4, 28))
            # Bright center
            pygame.draw.rect(self.image, (255, 255, 255), (3, 0, 2, 28))

        elif style == self.STYLE_BATTLECRUISER:
            # Massive battlecruiser laser - huge, intimidating
            self.image = pygame.Surface((14, 40), pygame.SRCALPHA)
            # Outer intense glow
            pygame.draw.ellipse(self.image, (255, 150, 50, 60), (0, 0, 14, 40))
            # Secondary glow layer
            pygame.draw.ellipse(self.image, (255, 200, 100, 100), (2, 2, 10, 36))
            # Core beam
            pygame.draw.ellipse(self.image, (255, 240, 150), (4, 4, 6, 32))
            # White hot center
            pygame.draw.ellipse(self.image, (255, 255, 255), (5, 6, 4, 28))
            # Pulsing effect particles
            for _ in range(3):
                px = random.randint(3, 10)
                py = random.randint(5, 35)
                pygame.draw.circle(self.image, (255, 255, 200, 150), (px, py), 2)

        elif style == self.STYLE_BEAM:
            # Continuous beam segment - for sweeping attacks
            self.image = pygame.Surface((6, 50), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 200, 100, 120), (0, 0, 6, 50))
            pygame.draw.rect(self.image, (255, 255, 200), (1, 0, 4, 50))
            pygame.draw.rect(self.image, (255, 255, 255), (2, 0, 2, 50))

        elif style == self.STYLE_PLASMA:
            # Plasma ball for bombers
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 100, 50, 80), (8, 8), 8)
            pygame.draw.circle(self.image, (255, 180, 80), (8, 8), 6)
            pygame.draw.circle(self.image, (255, 255, 150), (8, 8), 3)

        else:
            # Standard frigate laser
            self.image = pygame.Surface((4, 16), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (255, 220, 100), (0, 0, 4, 16))
            pygame.draw.rect(self.image, (255, 255, 200), (1, 0, 2, 16))

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        self.age += 1

        # Pulsing effect for heavy projectiles
        if self.style in [self.STYLE_CRUISER, self.STYLE_BATTLECRUISER]:
            if self.age % 3 == 0:
                # Recreate with slight variation for shimmer effect
                pulse = 0.9 + 0.2 * math.sin(self.age * 0.5)
                self.image = self.base_image.copy()
                if pulse > 1.0:
                    # Brighten
                    bright_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                    bright_surf.fill((255, 255, 255, int(30 * (pulse - 1.0) * 5)))
                    self.image.blit(bright_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
            self.kill()


class Hardpoint(pygame.sprite.Sprite):
    """
    Destructible weapon hardpoint for cruisers and battlecruisers.

    Hardpoints must be destroyed before the main hull takes full damage.
    Each hardpoint can fire independently and has its own health pool.
    """

    def __init__(self, parent, offset_x, offset_y, hardpoint_type='laser', health=50):
        super().__init__()
        self.parent = parent  # The cruiser/BC this is attached to
        self.offset_x = offset_x  # Position relative to parent center
        self.offset_y = offset_y
        self.hardpoint_type = hardpoint_type
        self.health = health
        self.max_health = health
        self.destroyed = False
        self.fire_rate = 1200  # ms between shots
        self.last_shot = pygame.time.get_ticks() + random.randint(0, 800)
        self.damage_flash = 0

        # Create hardpoint visual based on type
        if hardpoint_type == 'heavy_laser':
            # Battlecruiser main turret - large
            self.image = pygame.Surface((24, 32), pygame.SRCALPHA)
            # Turret base
            pygame.draw.ellipse(self.image, (120, 90, 40), (2, 16, 20, 12))
            pygame.draw.ellipse(self.image, (160, 130, 60), (4, 18, 16, 8))
            # Gun barrels
            pygame.draw.rect(self.image, (100, 80, 35), (4, 0, 6, 20))
            pygame.draw.rect(self.image, (100, 80, 35), (14, 0, 6, 20))
            pygame.draw.rect(self.image, (150, 120, 60), (5, 0, 4, 18))
            pygame.draw.rect(self.image, (150, 120, 60), (15, 0, 4, 18))
            # Muzzle glow
            pygame.draw.circle(self.image, (255, 200, 100), (7, 2), 3)
            pygame.draw.circle(self.image, (255, 200, 100), (17, 2), 3)
            self.fire_rate = 1500
            self.damage_per_shot = 18

        elif hardpoint_type == 'dual_laser':
            # Cruiser dual turret
            self.image = pygame.Surface((18, 24), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (120, 90, 40), (1, 12, 16, 10))
            pygame.draw.ellipse(self.image, (160, 130, 60), (3, 14, 12, 6))
            pygame.draw.rect(self.image, (100, 80, 35), (3, 0, 4, 14))
            pygame.draw.rect(self.image, (100, 80, 35), (11, 0, 4, 14))
            pygame.draw.rect(self.image, (150, 120, 60), (4, 0, 2, 12))
            pygame.draw.rect(self.image, (150, 120, 60), (12, 0, 2, 12))
            pygame.draw.circle(self.image, (255, 200, 100), (5, 2), 2)
            pygame.draw.circle(self.image, (255, 200, 100), (13, 2), 2)
            self.fire_rate = 1000
            self.damage_per_shot = 14

        else:  # 'laser' - single turret
            self.image = pygame.Surface((12, 18), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (120, 90, 40), (1, 10, 10, 6))
            pygame.draw.rect(self.image, (100, 80, 35), (4, 0, 4, 12))
            pygame.draw.rect(self.image, (150, 120, 60), (5, 0, 2, 10))
            pygame.draw.circle(self.image, (255, 200, 100), (6, 2), 2)
            self.fire_rate = 800
            self.damage_per_shot = 10

        self.base_image = self.image.copy()
        self.rect = self.image.get_rect()
        self._update_position()

    def _update_position(self):
        """Update position based on parent"""
        if self.parent and hasattr(self.parent, 'rect'):
            self.rect.centerx = self.parent.rect.centerx + self.offset_x
            self.rect.centery = self.parent.rect.centery + self.offset_y

    def update(self):
        """Update hardpoint state"""
        if self.destroyed:
            return

        self._update_position()

        # Damage flash effect
        if self.damage_flash > 0:
            self.damage_flash -= 1
            flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, 100))
            self.image = self.base_image.copy()
            self.image.blit(flash_surf, (0, 0))
        else:
            self.image = self.base_image.copy()

        # Show damage state
        if self.health < self.max_health * 0.5:
            # Smoking
            smoke_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            for _ in range(2):
                sx = random.randint(2, self.image.get_width() - 2)
                sy = random.randint(0, self.image.get_height() // 2)
                pygame.draw.circle(smoke_surf, (80, 80, 80, 60), (sx, sy), random.randint(2, 4))
            self.image.blit(smoke_surf, (0, 0))

        if self.health < self.max_health * 0.25:
            # On fire
            fire_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            for _ in range(2):
                fx = random.randint(2, self.image.get_width() - 2)
                fy = random.randint(0, self.image.get_height() // 2)
                pygame.draw.circle(fire_surf, (255, 100, 30, 100), (fx, fy), random.randint(2, 3))
            self.image.blit(fire_surf, (0, 0))

    def can_shoot(self):
        """Check if hardpoint can fire"""
        if self.destroyed:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_shot >= self.fire_rate

    def shoot(self, player_rect):
        """Fire at player, returns list of bullets"""
        if not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()

        # Calculate direction to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            dx = dx / dist * 5
            dy = dy / dist * 5
        else:
            dy = 5

        bullets = []

        if self.hardpoint_type == 'heavy_laser':
            # Dual heavy beams
            for offset in [-5, 5]:
                bullets.append(EnemyBullet(
                    self.rect.centerx + offset, self.rect.top,
                    dx + random.uniform(-0.2, 0.2), dy,
                    self.damage_per_shot, style=EnemyBullet.STYLE_BATTLECRUISER
                ))
        elif self.hardpoint_type == 'dual_laser':
            # Dual medium beams
            for offset in [-4, 4]:
                bullets.append(EnemyBullet(
                    self.rect.centerx + offset, self.rect.top,
                    dx + random.uniform(-0.15, 0.15), dy,
                    self.damage_per_shot, style=EnemyBullet.STYLE_CRUISER
                ))
        else:
            # Single laser
            bullets.append(EnemyBullet(
                self.rect.centerx, self.rect.top,
                dx + random.uniform(-0.1, 0.1), dy,
                self.damage_per_shot, style=EnemyBullet.STYLE_CRUISER
            ))

        return bullets

    def take_damage(self, damage):
        """Take damage, return True if destroyed"""
        if self.destroyed:
            return False

        self.health -= damage
        self.damage_flash = 6

        if self.health <= 0:
            self.destroyed = True
            self.health = 0
            # Create destroyed visual
            self.image = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)
            # Wreckage
            w, h = self.image.get_size()
            pygame.draw.ellipse(self.image, (40, 30, 20), (0, h//3, w, h//2))
            # Smoke
            for _ in range(3):
                sx = random.randint(0, w)
                sy = random.randint(0, h)
                pygame.draw.circle(self.image, (60, 60, 60, 80), (sx, sy), random.randint(2, 5))
            return True

        return False


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
    PATTERN_FLYBY = 7      # Fly across screen, exit, return from other side
    PATTERN_ATTACK_RUN = 8 # Dive at player, pull up, exit top of screen
    PATTERN_DIAGONAL = 9   # Cross screen diagonally, respawn from top
    
    def __init__(self, enemy_type, x, y, difficulty=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.stats = ENEMY_STATS[enemy_type]
        self.difficulty = difficulty or {}

        self.width, self.height = self.stats['size']

        # Ship renderer for advanced effects
        self.ship_renderer = None

        # Apply difficulty scaling
        health_mult = self.difficulty.get('enemy_health_mult', 1.0)

        # Combat stats
        self.shields = int(self.stats['shields'] * health_mult)
        self.armor = int(self.stats['armor'] * health_mult)
        self.hull = int(self.stats['hull'] * health_mult)
        self.max_shields = self.shields
        self.max_armor = self.armor
        self.max_hull = self.hull

        # Behavior - apply speed multiplier for nightmare difficulty
        speed_mult = self.difficulty.get('enemy_speed_mult', 1.0)
        self.speed = self.stats['speed'] * speed_mult
        fire_rate_mult = self.difficulty.get('enemy_fire_rate_mult', 1.0)
        self.fire_rate = int(self.stats['fire_rate'] * fire_rate_mult)
        self.last_shot = pygame.time.get_ticks() + random.randint(0, 1000)
        self.score = self.stats['score']
        self.refugees = self.stats.get('refugees', 0)
        self.is_boss = self.stats.get('boss', False)

        # Create image after all attributes are set
        self.base_image = self._create_image()  # Store pristine image
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))

        # Damage visualization state
        self.damage_flash_timer = 0
        self.smoke_particles = []  # List of (x_offset, y_offset, alpha, drift_x)
        self.spark_timer = 0
        self.last_damage_pct = 1.0  # Track damage for visual updates
        
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

        # Flyby pattern state
        self.flyby_direction = random.choice([-1, 1])  # -1 = left, 1 = right
        self.flyby_state = 'approach'  # approach, flyby, exited, returning
        self.flyby_target_y = random.randint(100, 300)
        self.flyby_start_x = x  # Remember spawn position for return

        # Attack run pattern state
        self.attack_run_state = 'approach'  # approach, dive, pull_up, exit, returning
        self.attack_run_target = None  # Player position when attack starts
        self.attack_run_timer = 0

        # Drift pattern improvements
        self.drift_velocity_x = random.uniform(-0.5, 0.5)
        self.drift_velocity_y = 0
        self.drift_target_x = random.randint(80, SCREEN_WIDTH - 80)
        self.drift_direction_timer = random.randint(60, 180)

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

        # === HARDPOINT SYSTEM for Cruisers/Battlecruisers ===
        # These massive ships have destructible weapon turrets
        self.has_hardpoints = self.stats.get('has_hardpoints', False)
        self.hardpoints = []  # List of Hardpoint sprites

        if self.has_hardpoints:
            hardpoint_defs = self.stats.get('hardpoints', [])
            for hp_def in hardpoint_defs:
                offset_x, offset_y, hp_type, hp_health = hp_def
                # Scale health with difficulty
                hp_health = int(hp_health * health_mult)
                hardpoint = Hardpoint(self, offset_x, offset_y, hp_type, hp_health)
                self.hardpoints.append(hardpoint)

            # Track all-hardpoints-destroyed state
            self.all_hardpoints_destroyed = False

    def get_hardpoints(self):
        """Return list of hardpoint sprites for rendering/collision"""
        return self.hardpoints

    def get_active_hardpoints(self):
        """Return only non-destroyed hardpoints"""
        return [hp for hp in self.hardpoints if not hp.destroyed]

    def check_hardpoints_destroyed(self):
        """Check if all hardpoints are destroyed"""
        if not self.has_hardpoints:
            return True
        active = self.get_active_hardpoints()
        self.all_hardpoints_destroyed = len(active) == 0
        return self.all_hardpoints_destroyed

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
            # Executioners are fast and aggressive - flyby and attack runs
            self.pattern = random.choice([
                self.PATTERN_SINE, self.PATTERN_ZIGZAG,
                self.PATTERN_SWOOP, self.PATTERN_FLYBY,
                self.PATTERN_ATTACK_RUN
            ])
        elif self.enemy_type == 'punisher':
            # Punishers are tanky - prefer staying on screen
            self.pattern = random.choice([
                self.PATTERN_DRIFT, self.PATTERN_SINE, self.PATTERN_CIRCLE,
                self.PATTERN_FLANK
            ])
        elif self.enemy_type in ['omen', 'maller']:
            # Cruisers - wide strafing patterns
            self.pattern = random.choice([
                self.PATTERN_CIRCLE, self.PATTERN_FLANK, self.PATTERN_DRIFT,
                self.PATTERN_FLYBY
            ])
        elif self.enemy_type == 'interceptor':
            # Fast interceptors - attack runs
            self.pattern = random.choice([
                self.PATTERN_ATTACK_RUN, self.PATTERN_FLYBY,
                self.PATTERN_SWOOP
            ])
        elif self.enemy_type == 'coercer':
            # Destroyers - flyby strafing
            self.pattern = random.choice([
                self.PATTERN_FLYBY, self.PATTERN_CIRCLE,
                self.PATTERN_ZIGZAG
            ])
        elif self.enemy_type == 'bestower':
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.8
        else:
            self.pattern = random.choice([
                self.PATTERN_DRIFT, self.PATTERN_SINE,
                self.PATTERN_FLYBY
            ])
    
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
        # Determine sprite name for this enemy type
        sprite_name = ENEMY_SPRITE_MAP.get(self.enemy_type, self.enemy_type)

        # Initialize ship renderer for effects
        if sprite_name and sprite_name in EVE_TYPE_IDS:
            self.ship_renderer = ShipRenderer(sprite_name, is_player=False)

        # Try to load rendered sprite (EVE assets first, then old sprites)
        if sprite_name:
            sprite = load_ship_sprite(sprite_name, (self.width, self.height))
            if sprite:
                # Flip so nose points down (enemy faces player)
                sprite = pygame.transform.flip(sprite, False, True)
                return self._add_enemy_engine_effects(sprite)

        # Fall back to procedural generation
        proc_sprite = self._create_polished_amarr_ship()
        # Flip procedural sprites so they face player (nose down, engines at top)
        proc_sprite = pygame.transform.flip(proc_sprite, False, True)
        return self._add_enemy_engine_effects(proc_sprite)

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

        # Update damage flash
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            # Flash white overlay
            if self.damage_flash_timer % 2 == 0:
                flash_surf = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
                flash_surf.fill((255, 255, 255, 100))
                self.image.blit(flash_surf, (0, 0))

        # Update smoke particles
        for particle in self.smoke_particles[:]:
            particle['alpha'] -= 3
            particle['y'] -= 0.5  # Smoke rises
            particle['x'] += particle['drift_x']
            if particle['alpha'] <= 0:
                self.smoke_particles.remove(particle)

        # Draw smoke on image
        if self.smoke_particles:
            w, h = self.image.get_size()
            for p in self.smoke_particles:
                sx = w // 2 + int(p['x'])
                sy = h // 2 + int(p['y'])
                if 0 <= sx < w and 0 <= sy < h:
                    smoke_color = (60, 60, 60, int(p['alpha']))
                    pygame.draw.circle(self.image, smoke_color, (sx, sy), p['size'])

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
        elif self.pattern == self.PATTERN_FLYBY:
            self._move_flyby(player_rect)
        elif self.pattern == self.PATTERN_ATTACK_RUN:
            self._move_attack_run(player_rect)
        elif self.pattern == self.PATTERN_DIAGONAL:
            self._move_diagonal()

        # Boss phase changes
        if self.is_boss:
            self._update_boss_behavior()

        # === RESPAWN FROM TOP WHEN LEAVING SCREEN ===
        # Non-boss enemies cycle back from top (except diagonal/flyby which handle their own)
        if not self.is_boss and self.pattern not in [self.PATTERN_DIAGONAL, self.PATTERN_FLYBY, self.PATTERN_ATTACK_RUN]:
            respawn = False

            # Exited bottom of screen
            if self.rect.top > SCREEN_HEIGHT + 50:
                respawn = True
            # Exited left side
            elif self.rect.right < -80:
                respawn = True
            # Exited right side
            elif self.rect.left > SCREEN_WIDTH + 80:
                respawn = True

            if respawn:
                # Respawn from top at random x position
                self.rect.bottom = -random.randint(30, 100)
                self.rect.centerx = random.randint(60, SCREEN_WIDTH - 60)
                # Reset movement state for clean re-entry
                self.drift_target_x = random.randint(80, SCREEN_WIDTH - 80)
                self.target_y = random.randint(80, 350)

        # Gentle horizontal bounds for non-diagonal patterns (push back, don't clamp hard)
        if self.pattern not in [self.PATTERN_FLYBY, self.PATTERN_ATTACK_RUN, self.PATTERN_DIAGONAL]:
            if self.rect.left < -50:
                self.rect.x += self.speed * 2  # Push back toward center
            elif self.rect.right > SCREEN_WIDTH + 50:
                self.rect.x -= self.speed * 2
    
    def _move_drift(self):
        """Dynamic drift - smooth acceleration toward target points with constant downward flow"""
        # Decrement direction timer
        self.drift_direction_timer -= 1

        # Pick new target when timer expires or near target
        if self.drift_direction_timer <= 0 or abs(self.rect.centerx - self.drift_target_x) < 20:
            self.drift_target_x = random.randint(100, SCREEN_WIDTH - 100)  # Avoid corners
            self.drift_direction_timer = random.randint(60, 150)

        # Smoothly accelerate toward target (not instant direction change)
        dx = self.drift_target_x - self.rect.centerx
        target_vel = max(-self.speed * 1.5, min(self.speed * 1.5, dx * 0.03))
        self.drift_velocity_x += (target_vel - self.drift_velocity_x) * 0.08
        self.rect.x += self.drift_velocity_x

        # CONSTANT DOWNWARD FLOW - enemies always drift down through screen
        self.rect.y += self.speed * 0.6  # Always moving down
    
    def _move_sine(self):
        """Smooth sine wave movement with constant downward flow"""
        amplitude = 80 + 40 * math.sin(self.pattern_timer * 0.3)
        self.rect.centerx = SCREEN_WIDTH // 2 + math.sin(self.pattern_timer * 1.5) * amplitude
        # CONSTANT DOWNWARD FLOW
        self.rect.y += self.speed * 0.5

    def _move_zigzag(self):
        """Sharp zigzag pattern with constant downward flow"""
        # Change direction every ~60 frames
        direction = 1 if int(self.pattern_timer * 2) % 2 == 0 else -1
        self.rect.x += direction * self.speed * 2
        # CONSTANT DOWNWARD FLOW
        self.rect.y += self.speed * 0.7

    def _move_circle(self):
        """Circular strafing pattern with downward drift"""
        self.rect.centerx = self.circle_center_x + math.cos(self.pattern_timer) * self.circle_radius
        # Circle while drifting down
        self.rect.y += self.speed * 0.4
        # Slowly drift the center down and sideways
        self.circle_center_x += math.sin(self.pattern_timer * 0.2) * 0.5
        self.circle_center_x = max(100, min(SCREEN_WIDTH - 100, self.circle_center_x))
    
    def _move_swoop(self, player_rect):
        """Dive toward player then continue through - no retreat, constant flow"""
        # Always moving down, just faster during dive
        if self.swoop_state == 'enter':
            self.rect.y += self.speed * 0.8
            if self.rect.centery >= 150:
                self.swoop_state = 'dive'
                if player_rect:
                    self.swoop_target_x = player_rect.centerx
                else:
                    self.swoop_target_x = SCREEN_WIDTH // 2
        elif self.swoop_state == 'dive':
            # Dive toward player position - fast descent
            self.rect.y += self.speed * 2.5
            dx = self.swoop_target_x - self.rect.centerx
            self.rect.x += max(-self.speed * 2, min(self.speed * 2, dx * 0.1))

        # Horizontal weave
        self.rect.x += math.sin(self.pattern_timer * 2) * self.speed * 0.5

    def _move_flank(self, player_rect):
        """Flanking run - sweep across screen diagonally, not hover at edges"""
        # Move diagonally across screen
        self.rect.x += self.flank_side * self.speed * 1.2
        # CONSTANT DOWNWARD FLOW
        self.rect.y += self.speed * 0.6

        # Slight tracking toward player x
        if player_rect:
            dx = player_rect.centerx - self.rect.centerx
            self.rect.x += max(-self.speed * 0.3, min(self.speed * 0.3, dx * 0.01))

    def _move_swarm(self, player_rect):
        """Drone swarm behavior - swirl down while attacking, no hovering"""
        if not player_rect:
            # No player, just drift down
            self.rect.y += self.speed * 0.8
            return

        # Update swarm approach timer
        self.swarm_approach_timer += 1

        # ALWAYS drift down - drones flow through screen
        self.rect.y += self.speed * 0.3

        # Swirling movement while descending
        self.swarm_angle += self.swarm_speed
        swirl_x = math.cos(self.swarm_angle) * 40
        self.rect.x += swirl_x * 0.1

        if self.swarm_state == 'orbit':
            # Track toward player x while descending
            dx = player_rect.centerx - self.rect.centerx
            self.rect.x += max(-self.speed, min(self.speed, dx * 0.03))

            # Switch to attack occasionally
            if self.swarm_approach_timer > 60 and random.random() < 0.02:
                self.swarm_state = 'attack'
                self.swarm_approach_timer = 0

        elif self.swarm_state == 'attack':
            # Dive toward player - faster descent
            dx = player_rect.centerx - self.rect.centerx
            dy = player_rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                self.rect.x += (dx / dist) * self.speed * 2
                self.rect.y += (dy / dist) * self.speed * 1.5

            # After diving, go back to orbiting descent
            if self.swarm_approach_timer > 40:
                self.swarm_state = 'orbit'
                self.swarm_approach_timer = 0

        elif self.swarm_state == 'retreat':
            # Just continue descending - no upward retreat
            self.swarm_state = 'orbit'
            self.swarm_approach_timer = 0

    def _move_flyby(self, player_rect):
        """
        Fly diagonally across screen with constant downward flow.
        No lingering - always moving through.
        """
        # ALWAYS move down - no hovering or returning upward
        self.rect.y += self.speed * 0.5

        if self.flyby_state == 'approach':
            # Quick approach phase - just get on screen
            self.rect.y += self.speed * 0.5
            if self.rect.centery > 60:
                self.flyby_state = 'flyby'

        elif self.flyby_state == 'flyby':
            # Fly diagonally across screen
            self.rect.x += self.flyby_direction * self.speed * 2.5

            # Check if exited sides - respawn from top
            if self.flyby_direction > 0 and self.rect.left > SCREEN_WIDTH + 50:
                self.rect.bottom = -random.randint(30, 80)
                self.rect.right = -30
                self.flyby_direction = 1
            elif self.flyby_direction < 0 and self.rect.right < -50:
                self.rect.bottom = -random.randint(30, 80)
                self.rect.left = SCREEN_WIDTH + 30
                self.flyby_direction = -1

        elif self.flyby_state in ['exited', 'returning']:
            # Skip these states - just keep flying
            self.flyby_state = 'flyby'

    def _move_attack_run(self, player_rect):
        """
        Dive at player and continue through - no pull up, just flow through screen.
        Respawns from top after exiting bottom.
        """
        self.attack_run_timer += 1

        if self.attack_run_state == 'approach':
            # Quick approach - always moving down
            self.rect.y += self.speed * 1.2

            # Track player horizontally
            if player_rect:
                dx = player_rect.centerx - self.rect.centerx
                self.rect.x += max(-self.speed, min(self.speed, dx * 0.05))

            # Start dive quickly
            if self.rect.centery > 100 or self.attack_run_timer > 40:
                self.attack_run_state = 'dive'
                if player_rect:
                    self.attack_run_target = (player_rect.centerx, player_rect.centery)
                else:
                    self.attack_run_target = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                self.attack_run_timer = 0

        elif self.attack_run_state == 'dive':
            # Dive toward player's position at high speed
            if self.attack_run_target:
                dx = self.attack_run_target[0] - self.rect.centerx
                self.rect.x += max(-self.speed * 2, min(self.speed * 2, dx * 0.08))
            self.rect.y += self.speed * 3.5  # Fast dive through

        # Handle all other states by returning to approach
        elif self.attack_run_state in ['pull_up', 'exit', 'returning']:
            self.attack_run_state = 'approach'
            self.attack_run_timer = 0

    def _move_diagonal(self):
        """
        Move diagonally across screen using patrol_vx/patrol_vy.
        When exiting screen (bottom or sides), respawn from top.
        Creates endless waves crossing the screen.
        """
        # Use patrol velocities set at spawn
        vx = getattr(self, 'patrol_vx', 2.0)
        vy = getattr(self, 'patrol_vy', 2.5)

        self.rect.x += vx
        self.rect.y += vy

        # Check if exited screen - respawn from top
        exited = False

        # Exited bottom
        if self.rect.top > SCREEN_HEIGHT + 50:
            exited = True
        # Exited left side (moving left)
        elif vx < 0 and self.rect.right < -50:
            exited = True
        # Exited right side (moving right)
        elif vx > 0 and self.rect.left > SCREEN_WIDTH + 50:
            exited = True

        if exited:
            # Respawn from top, opposite side
            self.rect.bottom = -30 - random.randint(0, 100)
            if vx > 0:
                # Was moving right, spawn on left
                self.rect.right = -30 - random.randint(0, 50)
            else:
                # Was moving left, spawn on right
                self.rect.left = SCREEN_WIDTH + 30 + random.randint(0, 50)

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
            # Boss fires spread with heavy bullets
            for angle in [-20, -10, 0, 10, 20]:
                rad = math.radians(angle)
                bdx = dx * math.cos(rad) - dy * math.sin(rad)
                bdy = dx * math.sin(rad) + dy * math.cos(rad)
                bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 15,
                                          style=EnemyBullet.STYLE_BATTLECRUISER))

        # === BATTLECRUISER - MASSIVE LASER BARRAGE ===
        elif self.enemy_type == 'harbinger':
            # Harbinger fires overwhelming salvos - 7 heavy beams in sweeping pattern
            base_angle = math.sin(pygame.time.get_ticks() * 0.003) * 15  # Sweep back and forth
            for i, angle in enumerate([-30, -20, -10, 0, 10, 20, 30]):
                rad = math.radians(angle + base_angle)
                bdx = dx * math.cos(rad) - dy * math.sin(rad)
                bdy = dx * math.sin(rad) + dy * math.cos(rad)
                # Stagger spawn positions across the hull
                spawn_x = self.rect.centerx + (i - 3) * 25
                bullets.append(EnemyBullet(spawn_x, self.rect.bottom, bdx * 1.2, bdy * 1.2, 18,
                                          style=EnemyBullet.STYLE_BATTLECRUISER))

        # === CRUISER - OMEN - FAST LASER SALVOS ===
        elif self.enemy_type == 'omen':
            # Omen fires rapid triple beams - alternating sides
            side = 1 if (pygame.time.get_ticks() // 200) % 2 == 0 else -1
            for i in range(3):
                angle = side * (5 + i * 8)
                rad = math.radians(angle)
                bdx = dx * math.cos(rad) - dy * math.sin(rad)
                bdy = dx * math.sin(rad) + dy * math.cos(rad)
                spawn_x = self.rect.centerx + side * (20 + i * 15)
                bullets.append(EnemyBullet(spawn_x, self.rect.bottom - i * 5, bdx, bdy * 1.1, 14,
                                          style=EnemyBullet.STYLE_CRUISER))

        # === CRUISER - MALLER - HEAVY ARMOR-PIERCING SALVOS ===
        elif self.enemy_type == 'maller':
            # Maller fires slower but devastating dual beams with tracking
            for offset in [-35, 35]:
                # Track player more accurately
                track_dx = player_rect.centerx - (self.rect.centerx + offset)
                track_dy = player_rect.centery - self.rect.bottom
                track_dist = math.sqrt(track_dx*track_dx + track_dy*track_dy)
                if track_dist > 0:
                    track_dx = track_dx / track_dist * 4.5
                    track_dy = track_dy / track_dist * 4.5
                bullets.append(EnemyBullet(self.rect.centerx + offset, self.rect.bottom,
                                          track_dx, track_dy, 20,
                                          style=EnemyBullet.STYLE_CRUISER))
            # Occasional center mega-beam
            if random.random() < 0.3:
                bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom,
                                          dx * 0.8, dy * 1.0, 25,
                                          style=EnemyBullet.STYLE_BATTLECRUISER))

        # === BOMBER - PLASMA TORPEDOES ===
        elif self.enemy_type == 'bomber':
            # Slow but powerful plasma ball
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom,
                                      dx * 0.4, dy * 0.6, 30,
                                      style=EnemyBullet.STYLE_PLASMA))

        elif self.pattern == self.PATTERN_SWARM and hasattr(self, 'swarm_state') and self.swarm_state == 'attack':
            # Attacking drones fire faster, more accurate shots
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.8, dy * 1.4, 8))

        else:
            # Add slight inaccuracy for regular enemies
            spread = random.uniform(-0.3, 0.3)
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.3 + spread, dy, 10))

        # === HARDPOINT FIRING ===
        # Cruisers/BCs with hardpoints fire from each active turret
        if self.has_hardpoints:
            for hardpoint in self.get_active_hardpoints():
                hp_bullets = hardpoint.shoot(player_rect)
                bullets.extend(hp_bullets)

        return bullets
    
    def take_damage(self, bullet):
        """Take damage from bullet, return True if destroyed

        For ships with hardpoints (cruisers/BCs):
        - Hardpoints must be destroyed first
        - Main hull takes 90% reduced damage while hardpoints active
        - Once hardpoints gone, full damage to structure
        """
        damage = bullet.damage

        # === HARDPOINT DAMAGE REDUCTION ===
        # If ship has active hardpoints, main hull is heavily protected
        if self.has_hardpoints and not self.check_hardpoints_destroyed():
            # Hull takes only 10% damage while hardpoints active
            # This encourages targeting hardpoints first
            damage = damage * 0.1

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

        # Trigger damage flash
        self.damage_flash_timer = 8

        # Spawn smoke particles when hull is damaged
        total_health = self.max_shields + self.max_armor + self.max_hull
        current_health = max(0, self.shields) + max(0, self.armor) + max(0, self.hull)
        damage_pct = current_health / total_health if total_health > 0 else 0

        # Add smoke/sparks based on damage level
        if damage_pct < 0.7 and len(self.smoke_particles) < 8:
            # Spawn smoke at random position on ship
            w, h = self.image.get_size()
            self.smoke_particles.append({
                'x': random.randint(-w//3, w//3),
                'y': random.randint(-h//3, h//3),
                'alpha': 180,
                'drift_x': random.uniform(-0.3, 0.3),
                'size': random.randint(4, 10)
            })

        # Update damage visuals
        self._update_damage_visuals(damage_pct)

        return self.hull <= 0

    def _update_damage_visuals(self, damage_pct):
        """Update ship image based on damage level"""
        # Start with base image
        self.image = self.base_image.copy()
        w, h = self.image.get_size()

        # Add hull cracks/damage when below 70% health
        if damage_pct < 0.7:
            # Dark damage marks
            num_marks = int((1 - damage_pct) * 8)
            for _ in range(num_marks):
                mx = random.randint(w//4, 3*w//4)
                my = random.randint(h//4, 3*h//4)
                mark_color = (30, 25, 20, 120)
                pygame.draw.circle(self.image, mark_color, (mx, my), random.randint(2, 5))

        # Add fire glow when below 40% health
        if damage_pct < 0.4:
            fire_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            num_fires = int((0.4 - damage_pct) * 10)
            for _ in range(num_fires):
                fx = random.randint(w//4, 3*w//4)
                fy = random.randint(h//4, 3*h//4)
                fire_colors = [(255, 100, 30, 80), (255, 180, 50, 60), (255, 60, 20, 100)]
                pygame.draw.circle(fire_surf, random.choice(fire_colors), (fx, fy), random.randint(3, 8))
            self.image.blit(fire_surf, (0, 0))

        # Critical damage - red tint overlay when below 20%
        if damage_pct < 0.2:
            crit_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            crit_surf.fill((255, 50, 30, 40))
            self.image.blit(crit_surf, (0, 0))


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

        # Orbital particles for enhanced visuals
        self.orbitals = []
        num_orbitals = 4
        for i in range(num_orbitals):
            self.orbitals.append({
                'angle': i * (2 * math.pi / num_orbitals),
                'radius': 16,
                'speed': 0.08 + random.uniform(-0.01, 0.01),
                'size': random.randint(2, 4)
            })

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

        size = self.size + 24  # Extra space for orbitals
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Outer glow pulse with rays
        glow_color = (*self.color, int(60 * pulse))
        pygame.draw.circle(self.image, glow_color, (cx, cy), self.size//2 + glow_size)

        # Draw orbital particles
        for orb in self.orbitals:
            orb['angle'] += orb['speed']
            ox = cx + math.cos(orb['angle']) * orb['radius']
            oy = cy + math.sin(orb['angle']) * orb['radius']
            # Orbital glow
            pygame.draw.circle(self.image, (*self.color, 100), (int(ox), int(oy)), orb['size'] + 2)
            pygame.draw.circle(self.image, (255, 255, 255), (int(ox), int(oy)), orb['size'])

        # Orbital trail ring
        ring_alpha = int(40 + 20 * pulse)
        pygame.draw.circle(self.image, (*self.color, ring_alpha), (cx, cy), 16, 1)

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
        if random.random() < 0.15:
            sx = cx + random.randint(-12, 12)
            sy = cy + random.randint(-12, 12)
            pygame.draw.circle(self.image, (255, 255, 255, 200), (sx, sy), random.randint(1, 3))

        # Light rays emanating from center
        if random.random() < 0.2:
            ray_angle = random.uniform(0, math.pi * 2)
            ray_len = random.randint(12, 20)
            rx = cx + math.cos(ray_angle) * ray_len
            ry = cy + math.sin(ray_angle) * ray_len
            pygame.draw.line(self.image, (*self.color, 80), (cx, cy), (int(rx), int(ry)), 1)

        self.rect = self.image.get_rect(center=(self.rect.centerx, self.rect.centery + self.bob_offset))


class Explosion(pygame.sprite.Sprite):
    """Polished explosion with shockwave, debris, and layered fire"""

    def __init__(self, x, y, size=30, color=COLOR_AMARR_ACCENT):
        super().__init__()
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size
        self.color = color
        self.frame = 0
        self.max_frames = 25

        # Generate random debris particles
        self.debris = []
        num_debris = min(12, size // 4 + 3)
        for _ in range(num_debris):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5) * (size / 30)
            self.debris.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, max(3, size // 8)),
                'life': random.randint(15, 25)
            })

        self._update_image()

    def _update_image(self):
        progress = self.frame / self.max_frames

        # Canvas size expands with explosion
        canvas_size = int(self.size * 3 * (1 + progress * 0.5))
        self.image = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
        cx, cy = canvas_size // 2, canvas_size // 2

        # === SHOCKWAVE RING ===
        if progress < 0.6:
            ring_progress = progress / 0.6
            ring_radius = int(self.size * 0.5 + self.size * 1.5 * ring_progress)
            ring_alpha = int(120 * (1 - ring_progress))
            ring_width = max(2, int(4 * (1 - ring_progress)))
            pygame.draw.circle(self.image, (255, 255, 255, ring_alpha),
                             (cx, cy), ring_radius, ring_width)

        # === OUTER FIRE (orange/red) ===
        if progress < 0.8:
            fire_progress = min(1.0, progress / 0.5)
            outer_size = int(self.size * (0.8 + fire_progress * 0.8))
            outer_alpha = int(180 * (1 - progress / 0.8))

            # Flickering outer fire
            for i in range(3):
                offset_x = random.randint(-3, 3)
                offset_y = random.randint(-3, 3)
                fire_size = outer_size + random.randint(-4, 4)
                pygame.draw.circle(self.image, (255, 100, 30, outer_alpha // 2),
                                 (cx + offset_x, cy + offset_y), fire_size)

            pygame.draw.circle(self.image, (255, 150, 50, outer_alpha),
                             (cx, cy), int(outer_size * 0.85))

        # === INNER CORE (bright yellow/white) ===
        if progress < 0.5:
            core_progress = progress / 0.5
            core_size = int(self.size * 0.6 * (1 - core_progress * 0.5))
            core_alpha = int(255 * (1 - core_progress))

            pygame.draw.circle(self.image, (255, 220, 100, core_alpha),
                             (cx, cy), core_size)
            pygame.draw.circle(self.image, (255, 255, 200, core_alpha),
                             (cx, cy), int(core_size * 0.6))
            pygame.draw.circle(self.image, (255, 255, 255, core_alpha),
                             (cx, cy), int(core_size * 0.3))

        # === DEBRIS PARTICLES ===
        for d in self.debris:
            if d['life'] > 0:
                d['x'] += d['vx']
                d['y'] += d['vy']
                d['vy'] += 0.15  # Gravity
                d['life'] -= 1

                debris_alpha = int(200 * (d['life'] / 25))
                debris_x = int(cx + d['x'])
                debris_y = int(cy + d['y'])

                if 0 <= debris_x < canvas_size and 0 <= debris_y < canvas_size:
                    # Hot debris with glow
                    pygame.draw.circle(self.image, (255, 200, 100, debris_alpha // 2),
                                     (debris_x, debris_y), d['size'] + 2)
                    pygame.draw.circle(self.image, (255, 150, 50, debris_alpha),
                                     (debris_x, debris_y), d['size'])

        # === SMOKE (late stage) ===
        if progress > 0.4:
            smoke_progress = (progress - 0.4) / 0.6
            smoke_alpha = int(60 * (1 - smoke_progress))
            smoke_size = int(self.size * (1 + smoke_progress))

            for i in range(2):
                smoke_x = cx + random.randint(-8, 8)
                smoke_y = cy + random.randint(-8, 8) - int(smoke_progress * 10)
                pygame.draw.circle(self.image, (80, 60, 50, smoke_alpha),
                                 (smoke_x, smoke_y), smoke_size)

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
