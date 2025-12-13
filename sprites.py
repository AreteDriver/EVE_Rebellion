"""Game sprites for Minmatar Rebellion"""
import pygame
import math
import random
from constants import *


class Player(pygame.sprite.Sprite):
    """Player ship - Rifter/Wolf/T2 Variants"""
    
    def __init__(self):
        super().__init__()
        self.is_wolf = False
        self.t2_variant = None  # None, 'autocannon', or 'rocket'
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
        self.rocket_cooldown_mult = 1.0  # T2 variant modifier
        self.rocket_salvo = 1  # Number of rockets fired per volley
        
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
        self.has_fleet_upgrade = False
        
        # Powerup effects
        self.overdrive_until = 0
        self.shield_boost_until = 0
        
        # Fleet system
        self.fleet_count = 1  # Number of ships in fleet (1 = just main ship)
        self.fleet_ships = []  # List of FleetShip instances
        self.fleet_upgrade_until = 0  # When the upgrade expires
        self.fleet_volleys_remaining = 0  # Volleys remaining during upgrade
        self.fleet_volley_cooldown = -2000  # Last volley time (init negative to allow immediate fire)
        
        # Score/Progress
        self.refugees = 0
        self.total_refugees = 0
        self.score = 0
        
        # Formation system (for Jaguar upgrade)
        self.current_formation = 'standard'
        self.formation_cooldown_until = 0
        self.escort_ships = []  # List of EscortShip objects
    
    def _create_ship_image(self):
        """Create Rifter/Wolf/T2 variant sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.is_jaguar:
            # Jaguar - compact, tactical with formation command colors
            color = (100, 180, 220)  # Distinct blue-ish color
            # Main body
            pygame.draw.polygon(surf, color, [
                (self.width//2, 0),
                (self.width-6, self.height-12),
                (self.width//2, self.height-3),
                (6, self.height-12)
            ])
            # Wings - angular
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (0, self.height-12),
                (8, self.height//3),
                (12, self.height-5)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (self.width, self.height-12),
                (self.width-8, self.height//3),
                (self.width-12, self.height-5)
            ])
            # Formation indicator stripe (matches current formation color)
            formation_color = FORMATION_TYPES[self.current_formation]['color']
            pygame.draw.rect(surf, formation_color, (self.width//2 - 4, 5, 8, 4))
            # Engine glow
            pygame.draw.circle(surf, (100, 200, 255), (self.width//2, self.height-6), 5)
        elif self.is_wolf:
            # Wolf - sleeker, more refined
            color = COLOR_MINMATAR_ACCENT
            # Main body
            pygame.draw.polygon(surf, color, [
                (self.width//2, 0),
                (self.width-5, self.height-10),
                (self.width//2, self.height-5),
                (5, self.height-10)
            ])
            # Wings
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (0, self.height-15),
                (10, self.height//2),
                (10, self.height-5)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (self.width, self.height-15),
                (self.width-10, self.height//2),
                (self.width-10, self.height-5)
            ])
            # Engine glow
            pygame.draw.circle(surf, (255, 150, 50), (self.width//2, self.height-8), 5)
        elif self.t2_variant == 'autocannon' and 'autocannon' in RIFTER_T2_VARIANTS:
            # Autocannon Rifter - wider wings with visible gun ports
            variant = RIFTER_T2_VARIANTS['autocannon']
            color = variant.get('color_accent', COLOR_MINMATAR_ACCENT)
            # Main body
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (self.width//2, 0),
                (self.width-5, self.height-12),
                (self.width//2, self.height),
                (5, self.height-12)
            ])
            # Left gun wing (extended)
            pygame.draw.polygon(surf, color, [
                (0, self.height-8),
                (3, self.height//4),
                (15, self.height-5)
            ])
            # Right gun wing (extended)
            pygame.draw.polygon(surf, color, [
                (self.width, self.height-8),
                (self.width-3, self.height//4),
                (self.width-15, self.height-5)
            ])
            # Gun barrels (autocannons)
            pygame.draw.rect(surf, (100, 100, 100), (5, 5, 3, 15))
            pygame.draw.rect(surf, (100, 100, 100), (self.width-8, 5, 3, 15))
            # Engine glow
            pygame.draw.circle(surf, color, (self.width//2, self.height-5), 5)
        elif self.t2_variant == 'rocket' and 'rocket' in RIFTER_T2_VARIANTS:
            # Rocket Specialist Rifter - bulkier with rocket pods
            variant = RIFTER_T2_VARIANTS['rocket']
            color = variant.get('color_accent', COLOR_MINMATAR_ACCENT)
            # Main body (bulkier)
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (self.width//2, 0),
                (self.width-3, self.height-15),
                (self.width//2, self.height),
                (3, self.height-15)
            ])
            # Left rocket pod
            pygame.draw.rect(surf, color, (0, self.height//3, 8, 20))
            pygame.draw.polygon(surf, (150, 50, 50), [
                (4, self.height//3 - 5),
                (0, self.height//3),
                (8, self.height//3)
            ])
            # Right rocket pod
            pygame.draw.rect(surf, color, (self.width-8, self.height//3, 8, 20))
            pygame.draw.polygon(surf, (150, 50, 50), [
                (self.width-4, self.height//3 - 5),
                (self.width-8, self.height//3),
                (self.width, self.height//3)
            ])
            # Rocket indicators
            for i in range(3):
                pygame.draw.circle(surf, (255, 100, 100), (3, self.height//3 + 5 + i*5), 2)
                pygame.draw.circle(surf, (255, 100, 100), (self.width-3, self.height//3 + 5 + i*5), 2)
            # Engine glow (twin engines)
            pygame.draw.circle(surf, color, (self.width//2 - 5, self.height-5), 4)
            pygame.draw.circle(surf, color, (self.width//2 + 5, self.height-5), 4)
        else:
            # Rifter - asymmetric, aggressive
            color = COLOR_MINMATAR_HULL
            # Main body (asymmetric)
            pygame.draw.polygon(surf, color, [
                (self.width//2 - 3, 0),
                (self.width-8, self.height-15),
                (self.width//2, self.height),
                (8, self.height-15)
            ])
            # Left wing (larger)
            pygame.draw.polygon(surf, COLOR_MINMATAR_DARK, [
                (0, self.height-10),
                (5, self.height//3),
                (12, self.height-5)
            ])
            # Right wing (smaller, asymmetric)
            pygame.draw.polygon(surf, COLOR_MINMATAR_DARK, [
                (self.width-3, self.height-20),
                (self.width-8, self.height//2),
                (self.width-12, self.height-8)
            ])
            # Engine glow
            pygame.draw.circle(surf, (255, 100, 0), (self.width//2, self.height-5), 4)
        
        return surf
    
    def upgrade_to_wolf(self):
        """Upgrade to Wolf assault frigate"""
        self.is_wolf = True
        self.t2_variant = None  # Wolf replaces T2 variants
        self.speed *= WOLF_SPEED_BONUS
        self.max_armor += WOLF_ARMOR_BONUS
        self.max_hull += WOLF_HULL_BONUS
        self.armor = min(self.armor + WOLF_ARMOR_BONUS, self.max_armor)
        self.hull = min(self.hull + WOLF_HULL_BONUS, self.max_hull)
        self.spread_bonus += 1
        self.image = self._create_ship_image()
    
    def upgrade_to_t2_variant(self, variant_type):
        """Upgrade to T2 Rifter variant (autocannon or rocket)"""
        if variant_type not in RIFTER_T2_VARIANTS:
            return False
        
        # Prevent upgrading if already has a ship upgrade
        if self.is_wolf or self.t2_variant is not None:
            return False
        
        variant = RIFTER_T2_VARIANTS[variant_type]
        self.t2_variant = variant_type
        self.is_wolf = False  # T2 variants are not Wolf
        
        # Apply variant bonuses
        self.speed *= variant['speed_bonus']
        self.max_armor += variant['armor_bonus']
        self.max_hull += variant['hull_bonus']
        self.armor = min(self.armor + variant['armor_bonus'], self.max_armor)
        self.hull = min(self.hull + variant['hull_bonus'], self.max_hull)
        # Set fire rate mult directly to avoid compounding with Gyrostabilizer
        self.fire_rate_mult = variant['fire_rate_mult']
        self.rocket_cooldown_mult = variant['rocket_cooldown_mult']
        self.rocket_salvo = variant['rocket_salvo']
        self.spread_bonus += variant['spread_bonus']
        
        # Rocket variant gets extra max rockets
        if 'max_rockets_bonus' in variant:
            self.max_rockets += variant['max_rockets_bonus']
            self.rockets = min(self.rockets + variant['max_rockets_bonus'], self.max_rockets)
        
        self.image = self._create_ship_image()
        return True
    
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
    
    def cycle_ammo(self):
        """Cycle to next unlocked ammo type"""
        idx = self.unlocked_ammo.index(self.current_ammo)
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
    
    def can_shoot(self):
        """Check if enough time has passed to fire"""
        now = pygame.time.get_ticks()
        ammo = AMMO_TYPES[self.current_ammo]
        cooldown = PLAYER_BASE_FIRE_RATE / (ammo['fire_rate'] * self.fire_rate_mult)
        return now - self.last_shot > cooldown
    
    def shoot(self):
        """Fire autocannons, returns list of bullets"""
        if not self.can_shoot():
            return []
        
        self.last_shot = pygame.time.get_ticks()
        bullets = []
        ammo = AMMO_TYPES[self.current_ammo]
        
        # Base shots
        num_shots = 2 + self.spread_bonus
        spread = 15 + (self.spread_bonus * 5)
        
        for i in range(num_shots):
            offset = (i - (num_shots - 1) / 2) * spread
            bullet = Bullet(
                self.rect.centerx + offset,
                self.rect.top,
                0, -BULLET_SPEED,
                ammo['tracer'],
                BULLET_DAMAGE,
                ammo['shield_mult'],
                ammo['armor_mult']
            )
            bullets.append(bullet)
        
        return bullets
    
    def can_rocket(self):
        """Check if can fire rocket"""
        now = pygame.time.get_ticks()
        cooldown = PLAYER_ROCKET_COOLDOWN * self.rocket_cooldown_mult
        return self.rockets >= self.rocket_salvo and now - self.last_rocket > cooldown
    
    def shoot_rocket(self):
        """Fire rocket(s), returns list of rockets"""
        if not self.can_rocket():
            return []
        
        self.last_rocket = pygame.time.get_ticks()
        rockets = []
        
        # Fire salvo based on variant
        for i in range(self.rocket_salvo):
            self.rockets -= 1
            # Spread rockets for multi-rocket salvos
            if self.rocket_salvo > 1:
                angle = (i - (self.rocket_salvo - 1) // 2) * 15  # 15 degree spread
                rockets.append(Rocket(self.rect.centerx, self.rect.top, angle))
            else:
                rockets.append(Rocket(self.rect.centerx, self.rect.top))
        
        return rockets
    
    def take_damage(self, amount):
        """Apply damage through shields -> armor -> hull"""
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
    
    def activate_fleet_upgrade(self):
        """Activate fleet upgrade - expand to max ships with volleys"""
        now = pygame.time.get_ticks()
        
        # If fleet is already active, only refresh timer and volleys without recreating ships
        if self.is_fleet_active():
            self.fleet_upgrade_until = now + FLEET_UPGRADE_DURATION
            self.fleet_volleys_remaining = FLEET_VOLLEY_COUNT
            return
        
        # First activation - create new fleet
        self.fleet_count = FLEET_MAX_SHIPS
        self.fleet_upgrade_until = now + FLEET_UPGRADE_DURATION
        self.fleet_volleys_remaining = FLEET_VOLLEY_COUNT
        
        # Create fleet ships
        self.fleet_ships = []
        for i in range(FLEET_MAX_SHIPS - 1):  # -1 because main ship is already there
            ship = FleetShip(self, i)
            self.fleet_ships.append(ship)
    
    def update_fleet(self):
        """Update fleet status and timer"""
        now = pygame.time.get_ticks()
        
        # Check if upgrade timer expired
        if self.fleet_upgrade_until > 0 and now >= self.fleet_upgrade_until:
            self.fleet_upgrade_until = 0
            self.fleet_volleys_remaining = 0
            # Downgrade to FLEET_DOWNGRADE_SHIPS
            if self.fleet_count > FLEET_DOWNGRADE_SHIPS:
                self.fleet_count = FLEET_DOWNGRADE_SHIPS
                # Remove excess ships
                while len(self.fleet_ships) > FLEET_DOWNGRADE_SHIPS - 1:
                    self.fleet_ships.pop()
        
        # Update fleet ship positions
        for ship in self.fleet_ships:
            ship.update()
    
    def get_fleet_positions(self):
        """Get positions of all ships in fleet (including main ship)"""
        positions = [(self.rect.centerx, self.rect.top)]
        
        # Add fleet ship positions using each ship's actual rect
        for ship in self.fleet_ships:
            positions.append((ship.rect.centerx, ship.rect.top))
        
        return positions
    
    def shoot_fleet(self):
        """Fire from all ships in fleet, returns list of bullets"""
        if not self.can_shoot():
            return []
        
        self.last_shot = pygame.time.get_ticks()
        bullets = []
        ammo = AMMO_TYPES[self.current_ammo]
        
        # Get all ship positions
        positions = self.get_fleet_positions()
        
        # Base shots per ship
        num_shots = 2 + self.spread_bonus
        spread = 15 + (self.spread_bonus * 5)
        
        for ship_x, ship_y in positions:
            for i in range(num_shots):
                offset = (i - (num_shots - 1) / 2) * spread
                bullet = Bullet(
                    ship_x + offset,
                    ship_y,
                    0, -BULLET_SPEED,
                    ammo['tracer'],
                    BULLET_DAMAGE,
                    ammo['shield_mult'],
                    ammo['armor_mult']
                )
                bullets.append(bullet)
        
        return bullets
    
    def fire_fleet_volley(self):
        """Fire a powerful volley from all ships (limited uses during upgrade)"""
        now = pygame.time.get_ticks()
        
        if self.fleet_volleys_remaining <= 0:
            return []
        
        # Volley cooldown of 1 second
        if now - self.fleet_volley_cooldown < 1000:
            return []
        
        self.fleet_volley_cooldown = now
        self.fleet_volleys_remaining -= 1
        
        bullets = []
        ammo = AMMO_TYPES[self.current_ammo]
        positions = self.get_fleet_positions()
        
        # Fire spread volley from each ship
        for ship_x, ship_y in positions:
            for angle in range(-30, 31, 10):  # -30 to 30 degrees in steps of 10
                rad = math.radians(angle)
                dx = math.sin(rad) * BULLET_SPEED * 0.5
                dy = -BULLET_SPEED
                
                bullet = Bullet(
                    ship_x,
                    ship_y,
                    dx, dy,
                    ammo['tracer'],
                    int(BULLET_DAMAGE * FLEET_VOLLEY_DAMAGE_MULT),
                    ammo['shield_mult'],
                    ammo['armor_mult']
                )
                bullets.append(bullet)
        
        return bullets
    
    def damage_fleet_ship(self, ship_index, amount):
        """Apply damage to a specific fleet ship"""
        if ship_index < 0 or ship_index >= len(self.fleet_ships):
            return False
        
        ship = self.fleet_ships[ship_index]
        destroyed = ship.take_damage(amount)
        
        if destroyed:
            self.fleet_ships.pop(ship_index)
            self.fleet_count = 1 + len(self.fleet_ships)
            return True
        
        return False
    
    def get_fleet_upgrade_time_remaining(self):
        """Get remaining time on fleet upgrade in ms"""
        if self.fleet_upgrade_until <= 0:
            return 0
        now = pygame.time.get_ticks()
        return max(0, self.fleet_upgrade_until - now)
    
    def is_fleet_active(self):
        """Check if fleet has more than just the main ship"""
        return self.fleet_count > 1


class FleetShip:
    """Individual ship in the player's fleet"""
    
    def __init__(self, player, index):
        self.player = player
        self.index = index
        
        # Individual ship health
        self.shields = FLEET_SHIP_SHIELDS
        self.armor = FLEET_SHIP_ARMOR
        self.hull = FLEET_SHIP_HULL
        self.max_shields = FLEET_SHIP_SHIELDS
        self.max_armor = FLEET_SHIP_ARMOR
        self.max_hull = FLEET_SHIP_HULL
        
        # Position offset from main ship
        # Alternating left/right pattern: index 0→center(0), 1→right(+45), 2→left(-45), 3→right(+90), 4→left(-90)
        # Formula: distance * direction, where:
        #   - distance = SPACING * ((index+1)//2) gives 0, 45, 45, 90, 90, ...
        #   - direction = +1 for odd indices (right), -1 for even indices (left)
        self.offset_x = FLEET_SHIP_SPACING * ((index + 1) // 2) * (1 if index % 2 == 1 else -1)
        self.offset_y = 10  # Slightly behind
        
        # Create ship image (smaller version of player ship)
        self.width = 30
        self.height = 38
        self.image = self._create_image()
        self.rect = self.image.get_rect()
    
    def _create_image(self):
        """Create a smaller fleet ship sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.player.is_wolf:
            color = COLOR_MINMATAR_ACCENT
            pygame.draw.polygon(surf, color, [
                (self.width//2, 0),
                (self.width-4, self.height-8),
                (self.width//2, self.height-4),
                (4, self.height-8)
            ])
            pygame.draw.circle(surf, (255, 150, 50), (self.width//2, self.height-6), 4)
        else:
            color = COLOR_MINMATAR_HULL
            pygame.draw.polygon(surf, color, [
                (self.width//2 - 2, 0),
                (self.width-6, self.height-12),
                (self.width//2, self.height),
                (6, self.height-12)
            ])
            pygame.draw.circle(surf, (255, 100, 0), (self.width//2, self.height-4), 3)
        
        return surf
    
    def update(self):
        """Update fleet ship position to follow main ship"""
        self.rect.centerx = self.player.rect.centerx + self.offset_x
        self.rect.top = self.player.rect.top + self.offset_y
        
        # Keep on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def take_damage(self, amount):
        """Apply damage to this fleet ship, return True if destroyed"""
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
        
        return self.hull <= 0
    
    def get_health_percent(self):
        """Get total health as percentage"""
        total_max = self.max_shields + self.max_armor + self.max_hull
        total_current = self.shields + self.armor + self.hull
        return total_current / total_max if total_max > 0 else 0


class EscortShip(pygame.sprite.Sprite):
    """AI-controlled escort ship that follows player in formation"""
    
    def __init__(self, player, slot_index):
        super().__init__()
        self.player = player
        self.slot_index = slot_index
        self.width = 25
        self.height = 30
        self.image = self._create_image()
        self.rect = self.image.get_rect()
        
        # Position at player initially
        self.rect.centerx = player.rect.centerx
        self.rect.centery = player.rect.centery
        
        # Movement smoothing
        self.target_x = self.rect.centerx
        self.target_y = self.rect.centery
        self.orbit_angle = random.uniform(0, math.pi * 2)
        
        # Combat
        self.last_shot = 0
        self.fire_rate = 300  # ms between shots
        self.damage = 6  # Slightly less than player
        
        # Health (escorts are fragile)
        self.hull = 30
        self.max_hull = 30
    
    def _create_image(self):
        """Create small escort ship sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Small triangular ship
        color = (150, 180, 200)
        pygame.draw.polygon(surf, color, [
            (self.width // 2, 0),
            (self.width - 3, self.height - 5),
            (self.width // 2, self.height - 2),
            (3, self.height - 5)
        ])
        # Engine glow
        pygame.draw.circle(surf, (100, 200, 255), (self.width // 2, self.height - 4), 3)
        
        return surf
    
    def get_formation_position(self):
        """Calculate target position based on current formation"""
        formation = self.player.get_formation_info()
        positions = formation['positions']
        
        # Get position for this slot (wrap if more escorts than positions)
        pos_idx = self.slot_index % len(positions)
        offset_x, offset_y = positions[pos_idx]
        
        # Add orbit movement
        orbit_radius = formation['orbit_radius']
        orbit_speed = formation['orbit_speed']
        self.orbit_angle += orbit_speed * 0.02
        
        orbit_x = math.cos(self.orbit_angle) * orbit_radius
        orbit_y = math.sin(self.orbit_angle) * orbit_radius * 0.5  # Elliptical
        
        return (
            self.player.rect.centerx + offset_x + orbit_x,
            self.player.rect.centery + offset_y + orbit_y
        )
    
    def update(self, enemy_bullets=None):
        """Update escort position and behavior"""
        # Get target position from formation
        self.target_x, self.target_y = self.get_formation_position()
        
        # Smooth movement toward target
        dx = self.target_x - self.rect.centerx
        dy = self.target_y - self.rect.centery
        
        # Move faster if far from position
        speed = 0.15
        self.rect.centerx += dx * speed
        self.rect.centery += dy * speed
        
        # Keep on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Defensive formation: intercept projectiles
        formation = self.player.get_formation_info()
        if formation['intercept_range'] > 0 and enemy_bullets:
            self._intercept_projectiles(enemy_bullets, formation['intercept_range'])
    
    def _intercept_projectiles(self, enemy_bullets, intercept_range):
        """Move to intercept nearby enemy projectiles"""
        closest_bullet = None
        closest_dist = intercept_range
        
        for bullet in enemy_bullets:
            # Only intercept bullets heading toward player
            dx = bullet.rect.centerx - self.player.rect.centerx
            dy = bullet.rect.centery - self.player.rect.centery
            dist_to_player = math.sqrt(dx * dx + dy * dy)
            
            if dist_to_player < intercept_range:  # Bullet is close to player
                dx = bullet.rect.centerx - self.rect.centerx
                dy = bullet.rect.centery - self.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                
                if dist < closest_dist:
                    closest_dist = dist
                    closest_bullet = bullet
        
        # Move toward closest bullet to intercept
        if closest_bullet:
            dx = closest_bullet.rect.centerx - self.rect.centerx
            dy = closest_bullet.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 0:
                # Intercept movement (overrides formation temporarily)
                self.rect.centerx += (dx / dist) * 4
                self.rect.centery += (dy / dist) * 4
    
    def can_shoot(self):
        """Check if escort can fire"""
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate
    
    def shoot(self):
        """Fire autocannon bullets"""
        if not self.can_shoot():
            return []
        
        self.last_shot = pygame.time.get_ticks()
        
        formation = self.player.get_formation_info()
        fire_spread = formation['fire_spread']
        
        # Use player's current ammo type
        ammo = AMMO_TYPES[self.player.current_ammo]
        
        # Calculate firing direction (forward with formation-based spread)
        angle_rad = math.radians(fire_spread)
        dx = math.sin(angle_rad) * 2
        dy = -BULLET_SPEED  # Always fire forward (up)
        
        bullet = Bullet(
            self.rect.centerx,
            self.rect.top,
            dx, dy,
            ammo['tracer'],
            self.damage,
            ammo['shield_mult'],
            ammo['armor_mult']
        )
        
        return [bullet]
    
    def take_damage(self, amount):
        """Take damage to hull"""
        self.hull -= amount
        return self.hull <= 0  # Return True if destroyed
    
    def is_alive(self):
        """Check if escort is still alive"""
        return self.hull > 0


class Bullet(pygame.sprite.Sprite):
    """Projectile sprite"""
    
    def __init__(self, x, y, dx, dy, color, damage, shield_mult=1.0, armor_mult=1.0):
        super().__init__()
        self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 4, 12))
        pygame.draw.rect(self.image, (255, 255, 255), (1, 0, 2, 4))  # Bright tip
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
    
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.angle = angle
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        # Rocket body
        pygame.draw.rect(self.image, (150, 150, 150), (2, 5, 4, 15))
        # Nose cone
        pygame.draw.polygon(self.image, (200, 50, 50), [(4, 0), (0, 8), (8, 8)])
        # Exhaust
        pygame.draw.polygon(self.image, (255, 200, 50), [(2, 18), (4, 22), (6, 18)])
        
        # Rotate image if angle is non-zero
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, -angle)
        
        # Always set the rect center to (x, y) after rotation
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.damage = ROCKET_DAMAGE
        self.shield_mult = 1.2
        self.armor_mult = 1.2
        
        # Calculate velocity based on angle
        rad = math.radians(angle)
        self.dx = math.sin(rad) * ROCKET_SPEED
        self.dy = -math.cos(rad) * ROCKET_SPEED
    
    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or
            self.rect.right < 0 or self.rect.left > SCREEN_WIDTH):
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
    
    def __init__(self, enemy_type, x, y, difficulty=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.stats = ENEMY_STATS[enemy_type]
        self.difficulty = difficulty or {}
        
        self.width, self.height = self.stats['size']
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))
        
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
        
        # Evasion state for reacting to player T2 variants
        self.evasion_timer = 0
        self.is_evading = False
    
    def _select_movement_pattern(self):
        """Select movement pattern based on enemy type"""
        if self.is_boss:
            self.pattern = self.PATTERN_DRIFT  # Bosses use simple patterns
        elif self.enemy_type == 'executioner':
            # Fast ships use aggressive patterns
            self.pattern = random.choice([
                self.PATTERN_SINE, self.PATTERN_ZIGZAG, 
                self.PATTERN_SWOOP, self.PATTERN_FLANK
            ])
        elif self.enemy_type == 'punisher':
            # Heavy ships use steady patterns
            self.pattern = random.choice([
                self.PATTERN_DRIFT, self.PATTERN_SINE, self.PATTERN_CIRCLE
            ])
        elif self.enemy_type in ['omen', 'maller']:
            # Cruisers use tactical patterns
            self.pattern = random.choice([
                self.PATTERN_CIRCLE, self.PATTERN_FLANK, self.PATTERN_DRIFT
            ])
        elif self.enemy_type == 'bestower':
            # Industrials try to escape
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.8  # Slightly slower
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
        """Create Amarr ship sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.enemy_type == 'executioner':
            # Fast, sleek frigate
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (0, 10),
                (self.width//2, 0),
                (self.width, 10)
            ])
            pygame.draw.polygon(surf, COLOR_AMARR_ACCENT, [
                (self.width//2, self.height-5),
                (10, 15),
                (self.width-10, 15)
            ])
        
        elif self.enemy_type == 'punisher':
            # Heavy, armored frigate
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (5, self.height//3),
                (5, 5),
                (self.width-5, 5),
                (self.width-5, self.height//3)
            ])
            pygame.draw.rect(surf, COLOR_AMARR_ACCENT, 
                           (self.width//4, 10, self.width//2, self.height//2))
        
        elif self.enemy_type == 'omen':
            # Cruiser
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (0, self.height//2),
                (5, 5),
                (self.width-5, 5),
                (self.width, self.height//2)
            ])
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT,
                              (10, 10, self.width-20, self.height//2))
        
        elif self.enemy_type == 'maller':
            # Heavy cruiser - boxy
            pygame.draw.rect(surf, COLOR_AMARR_HULL,
                           (5, 5, self.width-10, self.height-10))
            pygame.draw.polygon(surf, COLOR_AMARR_ACCENT, [
                (self.width//2, self.height-5),
                (10, self.height//2),
                (self.width-10, self.height//2)
            ])
        
        elif self.enemy_type == 'bestower':
            # Industrial - long, boxy
            pygame.draw.rect(surf, COLOR_AMARR_DARK,
                           (10, 5, self.width-20, self.height-10))
            pygame.draw.rect(surf, COLOR_AMARR_HULL,
                           (5, self.height//3, self.width-10, self.height//3))
        
        elif self.enemy_type in ['apocalypse', 'abaddon']:
            # Battleship boss
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (0, self.height*2//3),
                (0, self.height//3),
                (self.width//4, 0),
                (self.width*3//4, 0),
                (self.width, self.height//3),
                (self.width, self.height*2//3)
            ])
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT,
                              (self.width//4, self.height//4, 
                               self.width//2, self.height//2))
            # Extra detail for Abaddon
            if self.enemy_type == 'abaddon':
                pygame.draw.rect(surf, (255, 215, 0),
                               (self.width//3, 10, self.width//3, 20))
        
        return surf
    
    def update(self, player_rect=None, player_variant=None):
        """Update enemy position and behavior with advanced patterns"""
        self.pattern_timer += 0.05
        
        # Enter phase - move to target Y first
        if not self.entered:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed * 1.5
            else:
                self.entered = True
            return
        
        # React to player T2 variants
        self._react_to_player_variant(player_variant, player_rect)
        
        # Execute movement pattern (with potential evasion modifier)
        if self.is_evading and player_variant == 'rocket':
            # Evasive maneuvers against rocket specialist
            self._move_evasive(player_rect)
        elif self.pattern == self.PATTERN_DRIFT:
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
        
        # Boss phase changes
        if self.is_boss:
            self._update_boss_behavior()
        
        # Keep on screen horizontally
        if self.rect.left < 10:
            self.rect.left = 10
        elif self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10
    
    def _react_to_player_variant(self, player_variant, player_rect):
        """Adjust behavior based on player's T2 variant"""
        if not player_variant:
            return
        
        # Decrement evasion timer
        if self.evasion_timer > 0:
            self.evasion_timer -= 1
        else:
            self.is_evading = False
        
        if player_variant == 'rocket':
            # React to rocket specialist - more evasive, try to stay moving
            # Randomly trigger evasive maneuvers
            if not self.is_evading and random.random() < 0.02:
                self.is_evading = True
                self.evasion_timer = ENEMY_EVASION_DURATION
        
        elif player_variant == 'autocannon':
            # React to autocannon variant - increase aggression (fire faster)
            # This makes them prioritize attacking the high-threat autocannon
            if self.fire_rate > 0 and random.random() < 0.01:
                # Reduce cooldown by 30% (fire 30% faster), but never allow negative cooldown
                now = pygame.time.get_ticks()
                time_since_last_shot = now - self.last_shot
                normal_cooldown = self.fire_rate
                faster_fire_rate = int(self.fire_rate * 0.7)
                # If enough time has not passed, reduce the cooldown
                if time_since_last_shot < normal_cooldown:
                    # Set last_shot so next shot is allowed after faster_fire_rate
                    self.last_shot = now - (normal_cooldown - faster_fire_rate)
    
    def _move_evasive(self, player_rect):
        """Evasive movement pattern when facing rocket specialist"""
        # Fast zigzag movement to avoid rockets
        direction = 1 if int(self.pattern_timer * 4) % 2 == 0 else -1
        evasion_speed = self.speed * 2.5  # Move faster when evading
        self.rect.x += direction * evasion_speed
        
        # Also move vertically to avoid rockets
        if player_rect:
            # Try to move perpendicular to rocket flight path
            if random.random() < 0.1:
                self.rect.y += random.choice([-1, 1]) * self.speed
    
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
    
    def _update_boss_behavior(self):
        """Update boss-specific behavior"""
        self.boss_phase_timer += 1
        
        # Phase changes based on health
        health_pct = (self.shields + self.armor + self.hull) / (self.max_shields + self.max_armor + self.max_hull)
        
        if health_pct < 0.3 and self.boss_phase < 2:
            self.boss_phase = 2
            self.speed *= 1.3
        elif health_pct < 0.6 and self.boss_phase < 1:
            self.boss_phase = 1
            self.fire_rate = int(self.fire_rate * 0.8)
    
    def can_shoot(self):
        """Check if enemy can fire"""
        if self.fire_rate == 0:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate
    
    def shoot(self, player_rect):
        """Fire at player"""
        if not self.can_shoot():
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
        else:
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.3, dy, 10))
        
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
    """Escape pod with refugees"""
    
    def __init__(self, x, y, count=1):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 200, 200), (8, 8), 7)
        pygame.draw.circle(self.image, (100, 200, 100), (8, 8), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.count = count
        self.lifetime = 300  # frames until disappear
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(0.5, 1.5)
    
    def update(self):
        self.rect.x += self.drift_x
        self.rect.y += self.drift_y
        self.lifetime -= 1
        
        # Blink when about to expire
        if self.lifetime < 60 and self.lifetime % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)
        
        if self.lifetime <= 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    """Powerup pickup"""
    
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.data = POWERUP_TYPES[powerup_type]
        
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.data['color'], (2, 2, 16, 16))
        pygame.draw.rect(self.image, (255, 255, 255), (2, 2, 16, 16), 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2
    
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


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
