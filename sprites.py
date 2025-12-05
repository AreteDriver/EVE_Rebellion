"""Game sprites for Minmatar Rebellion"""
import pygame
import math
import random
from constants import *


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
        
        # Score/Progress
        self.refugees = 0
        self.total_refugees = 0
        self.score = 0
    
    def _create_ship_image(self):
        """Create Rifter/Wolf sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        if self.is_wolf:
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
        self.speed *= WOLF_SPEED_BONUS
        self.max_armor += WOLF_ARMOR_BONUS
        self.max_hull += WOLF_HULL_BONUS
        self.armor = min(self.armor + WOLF_ARMOR_BONUS, self.max_armor)
        self.hull = min(self.hull + WOLF_HULL_BONUS, self.max_hull)
        self.spread_bonus += 1
        self.image = self._create_ship_image()
    
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
        return self.rockets > 0 and now - self.last_rocket > PLAYER_ROCKET_COOLDOWN
    
    def shoot_rocket(self):
        """Fire rocket, returns rocket or None"""
        if not self.can_rocket():
            return None
        
        self.last_rocket = pygame.time.get_ticks()
        self.rockets -= 1
        return Rocket(self.rect.centerx, self.rect.top)
    
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
    """Base enemy class with support for boss tiers and special abilities"""
    
    # Movement pattern types
    PATTERN_DRIFT = 0      # Basic side-to-side drift
    PATTERN_SINE = 1       # Sine wave movement
    PATTERN_ZIGZAG = 2     # Sharp zigzag
    PATTERN_CIRCLE = 3     # Circular strafing
    PATTERN_SWOOP = 4      # Dive toward player then retreat
    PATTERN_FLANK = 5      # Move to screen edge then track player
    PATTERN_STRAFE = 6     # Boss strafing pattern
    PATTERN_AGGRESSIVE = 7 # Aggressive pursuit pattern
    
    def __init__(self, enemy_type, x, y, difficulty=None, wave_scaling=1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.stats = ENEMY_STATS[enemy_type]
        self.difficulty = difficulty or {}
        self.wave_scaling = wave_scaling
        
        self.width, self.height = self.stats['size']
        
        # Boss tier and special ability
        self.boss_tier = self.stats.get('boss_tier', 0)
        self.special_ability = self.stats.get('special_ability', None)
        self.ability_cooldown = 0
        self.ability_active = False
        self.ability_timer = 0
        
        # Apply difficulty and wave scaling
        health_mult = self.difficulty.get('enemy_health_mult', 1.0) * wave_scaling
        
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
        self.score = int(self.stats['score'] * wave_scaling)
        self.refugees = self.stats.get('refugees', 0)
        self.is_boss = self.stats.get('boss', False)
        self.ship_class = self.stats.get('ship_class', 'frigate')
        
        # Create image after boss_tier is set
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
            self.enrage_mode = False
            # Scale boss stats based on tier
            tier_mult = 1.0 + (self.boss_tier - 1) * 0.15
            self.shields = int(self.shields * tier_mult)
            self.armor = int(self.armor * tier_mult)
            self.hull = int(self.hull * tier_mult)
            self.max_shields = self.shields
            self.max_armor = self.armor
            self.max_hull = self.hull
        
        # Drone tracking for drone-based abilities
        self.active_drones = []
    
    def _select_movement_pattern(self):
        """Select movement pattern based on enemy type and ship class"""
        if self.is_boss:
            # Bosses use tier-appropriate patterns
            if self.boss_tier <= 1:
                self.pattern = random.choice([self.PATTERN_DRIFT, self.PATTERN_STRAFE])
            elif self.boss_tier == 2:
                self.pattern = random.choice([self.PATTERN_STRAFE, self.PATTERN_CIRCLE])
            elif self.boss_tier >= 3:
                self.pattern = random.choice([self.PATTERN_STRAFE, self.PATTERN_AGGRESSIVE])
        elif self.ship_class == 'frigate':
            if self.enemy_type == 'executioner':
                self.pattern = random.choice([
                    self.PATTERN_SINE, self.PATTERN_ZIGZAG, 
                    self.PATTERN_SWOOP, self.PATTERN_FLANK
                ])
            elif self.enemy_type == 'punisher':
                self.pattern = random.choice([
                    self.PATTERN_DRIFT, self.PATTERN_SINE, self.PATTERN_CIRCLE
                ])
            elif self.enemy_type in ['tormentor', 'crucifier']:
                self.pattern = random.choice([
                    self.PATTERN_SINE, self.PATTERN_FLANK, self.PATTERN_ZIGZAG
                ])
            else:
                self.pattern = self.PATTERN_DRIFT
        elif self.ship_class == 'industrial':
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.8
        else:
            self.pattern = self.PATTERN_DRIFT
    
    def _get_target_y(self):
        """Get target Y position based on enemy type and ship class"""
        if self.is_boss:
            # Bigger bosses stay higher
            return 100 + (4 - self.boss_tier) * 20
        elif self.ship_class == 'industrial':
            return random.randint(80, 180)
        else:
            return random.randint(80, 300)
    
    def _create_image(self):
        """Create Amarr ship sprite with visual distinctions per class"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        ship_class = self.stats.get('ship_class', 'frigate')
        
        # Frigates
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
        
        elif self.enemy_type == 'tormentor':
            # Laser-focused frigate with wing design
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (5, self.height//2),
                (0, 10),
                (self.width//2, 0),
                (self.width, 10),
                (self.width-5, self.height//2)
            ])
            pygame.draw.polygon(surf, COLOR_AMARR_ACCENT, [
                (self.width//2, self.height-8),
                (self.width//4, self.height//3),
                (self.width*3//4, self.height//3)
            ])
        
        elif self.enemy_type == 'crucifier':
            # Electronic warfare frigate - sleek, angular
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (3, self.height//2),
                (self.width//2, 0),
                (self.width-3, self.height//2)
            ])
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT,
                              (self.width//4, self.height//4, self.width//2, self.height//4))
        
        # Destroyers
        elif self.enemy_type == 'coercer':
            # Laser destroyer - elongated with turrets
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (5, self.height*2//3),
                (5, 5),
                (self.width-5, 5),
                (self.width-5, self.height*2//3)
            ])
            # Turret mounts
            pygame.draw.rect(surf, COLOR_AMARR_ACCENT, (8, 8, 8, 15))
            pygame.draw.rect(surf, COLOR_AMARR_ACCENT, (self.width-16, 8, 8, 15))
            pygame.draw.rect(surf, (255, 200, 50), (self.width//2-3, 5, 6, 10))
        
        elif self.enemy_type == 'dragoon':
            # Drone destroyer - wider with drone bays
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (0, self.height//2),
                (0, 10),
                (self.width, 10),
                (self.width, self.height//2)
            ])
            # Drone bay indicators
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT, (5, 15, 12, 12))
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT, (self.width-17, 15, 12, 12))
            pygame.draw.ellipse(surf, (100, 200, 255), (self.width//2-6, 20, 12, 12))
        
        elif self.enemy_type == 'heretic':
            # Interdictor - aggressive angular design
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (3, self.height//2),
                (8, 5),
                (self.width-8, 5),
                (self.width-3, self.height//2)
            ])
            pygame.draw.polygon(surf, COLOR_AMARR_ACCENT, [
                (self.width//2, self.height-10),
                (15, 20),
                (self.width-15, 20)
            ])
            # Missile ports
            pygame.draw.circle(surf, (255, 100, 50), (self.width//3, self.height//3), 4)
            pygame.draw.circle(surf, (255, 100, 50), (self.width*2//3, self.height//3), 4)
        
        # Cruisers
        elif self.enemy_type == 'omen':
            # Attack cruiser
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
        
        elif self.enemy_type == 'arbitrator':
            # Disruption cruiser - ornate design
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (5, self.height*2//3),
                (0, self.height//3),
                (10, 5),
                (self.width-10, 5),
                (self.width, self.height//3),
                (self.width-5, self.height*2//3)
            ])
            pygame.draw.ellipse(surf, (150, 100, 200),  # Purple for disruption
                              (self.width//4, self.height//4, self.width//2, self.height//3))
        
        elif self.enemy_type == 'augoror':
            # Logistics cruiser - support design
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (8, self.height*2//3),
                (3, self.height//4),
                (self.width//2, 0),
                (self.width-3, self.height//4),
                (self.width-8, self.height*2//3)
            ])
            # Energy transfer arrays (glowing)
            pygame.draw.ellipse(surf, (100, 200, 255), 
                              (self.width//3, self.height//3, self.width//3, self.height//4))
        
        # Battlecruisers
        elif self.enemy_type == 'harbinger':
            # Attack battlecruiser - aggressive
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (5, self.height*2//3),
                (0, self.height//3),
                (5, 5),
                (self.width-5, 5),
                (self.width, self.height//3),
                (self.width-5, self.height*2//3)
            ])
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT,
                              (15, 15, self.width-30, self.height//2))
            # Heavy laser arrays
            pygame.draw.rect(surf, (255, 200, 50), (10, 10, 8, 20))
            pygame.draw.rect(surf, (255, 200, 50), (self.width-18, 10, 8, 20))
        
        elif self.enemy_type == 'prophecy':
            # Drone battlecruiser - wide with drone hangars
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (0, self.height*2//3),
                (0, self.height//4),
                (self.width//4, 0),
                (self.width*3//4, 0),
                (self.width, self.height//4),
                (self.width, self.height*2//3)
            ])
            # Drone bays
            pygame.draw.rect(surf, COLOR_AMARR_ACCENT, (5, self.height//3, 15, 25))
            pygame.draw.rect(surf, COLOR_AMARR_ACCENT, (self.width-20, self.height//3, 15, 25))
            pygame.draw.ellipse(surf, (100, 200, 255), 
                              (self.width//3, self.height//4, self.width//3, self.height//4))
        
        elif self.enemy_type == 'oracle':
            # Attack battlecruiser - long range sniper
            pygame.draw.polygon(surf, COLOR_AMARR_HULL, [
                (self.width//2, self.height),
                (10, self.height*3//4),
                (5, self.height//2),
                (5, 5),
                (self.width-5, 5),
                (self.width-5, self.height//2),
                (self.width-10, self.height*3//4)
            ])
            # Long barrel laser
            pygame.draw.rect(surf, (255, 220, 100), (self.width//2-4, 0, 8, 25))
            pygame.draw.ellipse(surf, COLOR_AMARR_ACCENT,
                              (self.width//4, self.height//4, self.width//2, self.height//3))
        
        # Battleships
        elif self.enemy_type == 'apocalypse':
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
        
        elif self.enemy_type == 'abaddon':
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
            pygame.draw.rect(surf, (255, 215, 0),
                           (self.width//3, 10, self.width//3, 20))
        
        elif self.enemy_type == 'armageddon':
            # Neuting battleship - darker, more menacing
            pygame.draw.polygon(surf, COLOR_AMARR_DARK, [
                (self.width//2, self.height),
                (5, self.height*2//3),
                (0, self.height//3),
                (self.width//4, 0),
                (self.width*3//4, 0),
                (self.width, self.height//3),
                (self.width-5, self.height*2//3)
            ])
            pygame.draw.ellipse(surf, COLOR_AMARR_HULL,
                              (self.width//4, self.height//4, 
                               self.width//2, self.height//2))
            # Neut arrays (purple glow)
            pygame.draw.ellipse(surf, (150, 50, 200),
                              (self.width//3, self.height//6, self.width//3, self.height//5))
        
        # Industrial
        elif self.enemy_type == 'bestower':
            pygame.draw.rect(surf, COLOR_AMARR_DARK,
                           (10, 5, self.width-20, self.height-10))
            pygame.draw.rect(surf, COLOR_AMARR_HULL,
                           (5, self.height//3, self.width-10, self.height//3))
        
        # Add boss tier indicator for boss ships
        if self.is_boss and self.boss_tier > 0:
            # Draw a subtle glow effect for bosses based on tier
            glow_colors = {
                1: (100, 150, 255, 100),   # Blue glow for destroyers
                2: (200, 150, 50, 100),    # Gold glow for cruisers
                3: (255, 100, 50, 100),    # Orange glow for battlecruisers
                4: (255, 50, 50, 100)      # Red glow for battleships
            }
            glow_color = glow_colors.get(self.boss_tier, (255, 255, 255, 100))
            glow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, glow_color, (0, 0, self.width, self.height))
            surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_ADD)
        
        return surf
    
    def update(self, player_rect=None):
        """Update enemy position and behavior with advanced patterns"""
        self.pattern_timer += 0.05
        
        # Update ability cooldown
        if self.ability_cooldown > 0:
            self.ability_cooldown -= 1
        
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
        elif self.pattern == self.PATTERN_STRAFE:
            self._move_strafe(player_rect)
        elif self.pattern == self.PATTERN_AGGRESSIVE:
            self._move_aggressive(player_rect)
        
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
    
    def _move_strafe(self, player_rect):
        """Boss strafing pattern - sweeps across screen while tracking player"""
        # Wide sweeping motion
        amplitude = SCREEN_WIDTH * 0.35
        self.rect.centerx = SCREEN_WIDTH // 2 + math.sin(self.pattern_timer * 0.5) * amplitude
        
        # Subtle vertical movement
        base_y = self.target_y
        if player_rect:
            # Slightly track player position
            target_y = min(player_rect.centery - 150, base_y + 50)
            target_y = max(base_y - 30, target_y)
            dy = target_y - self.rect.centery
            self.rect.y += max(-self.speed * 0.3, min(self.speed * 0.3, dy * 0.02))
        else:
            self.rect.centery = base_y + math.sin(self.pattern_timer * 0.3) * 20
    
    def _move_aggressive(self, player_rect):
        """Aggressive pursuit pattern - actively moves toward player"""
        if player_rect:
            # Track player X position more aggressively
            dx = player_rect.centerx - self.rect.centerx
            move_speed = self.speed * 1.5
            self.rect.x += max(-move_speed, min(move_speed, dx * 0.03))
            
            # Oscillate vertically while tracking
            base_y = self.target_y + 30
            self.rect.centery = base_y + math.sin(self.pattern_timer * 0.8) * 40
            
            # Occasionally push forward
            if self.boss_phase >= 1 and random.random() < 0.005:
                self.target_y = min(self.target_y + 20, 200)
        else:
            self._move_drift()
    
    def _update_boss_behavior(self):
        """Update boss-specific behavior with tier-based enhancements"""
        self.boss_phase_timer += 1
        
        # Phase changes based on health
        health_pct = (self.shields + self.armor + self.hull) / (self.max_shields + self.max_armor + self.max_hull)
        
        if health_pct < 0.25 and not self.enrage_mode:
            # Enrage mode - final phase
            self.enrage_mode = True
            self.speed *= 1.2
            self.fire_rate = int(self.fire_rate * 0.6)
        elif health_pct < 0.5 and self.boss_phase < 2:
            self.boss_phase = 2
            self.speed *= 1.15
            self.fire_rate = int(self.fire_rate * 0.85)
        elif health_pct < 0.75 and self.boss_phase < 1:
            self.boss_phase = 1
            self.fire_rate = int(self.fire_rate * 0.9)
    
    def can_use_ability(self):
        """Check if boss can use special ability"""
        return self.is_boss and self.special_ability and self.ability_cooldown <= 0
    
    def use_ability(self, player_rect):
        """Use boss special ability, returns list of projectiles/effects"""
        if not self.can_use_ability():
            return []
        
        projectiles = []
        ability = self.special_ability
        
        if ability == 'rapid_fire':
            # Coercer - rapid burst of lasers
            self.ability_cooldown = 180
            for i in range(5):
                angle = -15 + i * 7.5
                rad = math.radians(angle)
                dx = math.sin(rad) * 5
                dy = math.cos(rad) * 5
                projectiles.append(EnemyBullet(
                    self.rect.centerx + (i - 2) * 8,
                    self.rect.bottom,
                    dx, dy, 12
                ))
        
        elif ability == 'drone_swarm':
            # Dragoon - fires tracking drone projectiles
            self.ability_cooldown = 240
            for i in range(3):
                offset = (i - 1) * 20
                projectiles.append(EnemyBullet(
                    self.rect.centerx + offset,
                    self.rect.bottom,
                    0, 3, 8
                ))
        
        elif ability == 'missile_barrage':
            # Heretic - fires spread of missiles
            self.ability_cooldown = 200
            for angle in [-30, -15, 0, 15, 30]:
                rad = math.radians(angle)
                dx = math.sin(rad) * 4
                dy = math.cos(rad) * 4
                projectiles.append(EnemyBullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    dx, dy, 15
                ))
        
        elif ability == 'beam_sweep':
            # Omen - wide angle sweep
            self.ability_cooldown = 150
            for angle in range(-40, 45, 10):
                rad = math.radians(angle)
                dx = math.sin(rad) * 6
                dy = math.cos(rad) * 6
                projectiles.append(EnemyBullet(
                    self.rect.centerx,
                    self.rect.bottom,
                    dx, dy, 10
                ))
        
        elif ability == 'armor_repair':
            # Maller - repairs armor over time (no projectiles)
            self.ability_cooldown = 300
            repair_amount = int(self.max_armor * 0.1)
            self.armor = min(self.armor + repair_amount, self.max_armor)
        
        elif ability == 'tracking_disrupt':
            # Arbitrator - fires disruptive projectiles
            self.ability_cooldown = 200
            if player_rect:
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dx = dx / dist * 4
                    dy = dy / dist * 4
                    projectiles.append(EnemyBullet(
                        self.rect.centerx, self.rect.bottom,
                        dx, dy, 12
                    ))
        
        elif ability == 'energy_transfer':
            # Augoror - drains shields (fires special projectiles)
            self.ability_cooldown = 180
            for angle in [-20, 0, 20]:
                rad = math.radians(angle)
                dx = math.sin(rad) * 5
                dy = math.cos(rad) * 5
                projectiles.append(EnemyBullet(
                    self.rect.centerx, self.rect.bottom,
                    dx, dy, 10
                ))
        
        elif ability == 'focused_beam':
            # Harbinger - high damage focused shot
            self.ability_cooldown = 120
            if player_rect:
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dx = dx / dist * 7
                    dy = dy / dist * 7
                    projectiles.append(EnemyBullet(
                        self.rect.centerx, self.rect.bottom,
                        dx, dy, 25
                    ))
        
        elif ability == 'heavy_drones':
            # Prophecy - deploys heavy damage drones
            self.ability_cooldown = 250
            for i in range(4):
                offset = (i - 1.5) * 25
                projectiles.append(EnemyBullet(
                    self.rect.centerx + offset,
                    self.rect.bottom,
                    random.uniform(-1, 1), 3, 12
                ))
        
        elif ability == 'sniper_beam':
            # Oracle - long range precision shot
            self.ability_cooldown = 100
            if player_rect:
                dx = player_rect.centerx - self.rect.centerx
                dy = player_rect.centery - self.rect.centery
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dx = dx / dist * 10
                    dy = dy / dist * 10
                    projectiles.append(EnemyBullet(
                        self.rect.centerx, self.rect.bottom,
                        dx, dy, 20
                    ))
        
        elif ability == 'pulse_barrage':
            # Apocalypse - multi-directional pulse
            self.ability_cooldown = 150
            for angle in range(0, 360, 30):
                rad = math.radians(angle)
                dx = math.sin(rad) * 4
                dy = math.cos(rad) * 4
                projectiles.append(EnemyBullet(
                    self.rect.centerx, self.rect.centery,
                    dx, dy, 12
                ))
        
        elif ability == 'omega_strike':
            # Abaddon - devastating area attack
            self.ability_cooldown = 200
            for angle in range(0, 360, 20):
                rad = math.radians(angle)
                dx = math.sin(rad) * 5
                dy = math.cos(rad) * 5
                projectiles.append(EnemyBullet(
                    self.rect.centerx, self.rect.centery,
                    dx, dy, 18
                ))
        
        elif ability == 'neut_pulse':
            # Armageddon - energy neutralizing pulse
            self.ability_cooldown = 180
            for angle in range(-60, 65, 15):
                rad = math.radians(angle)
                dx = math.sin(rad) * 4
                dy = math.cos(rad) * 4
                projectiles.append(EnemyBullet(
                    self.rect.centerx, self.rect.bottom,
                    dx, dy, 14
                ))
        
        return projectiles
    
    def can_shoot(self):
        """Check if enemy can fire"""
        if self.fire_rate == 0:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate
    
    def shoot(self, player_rect):
        """Fire at player with tier-appropriate attack patterns"""
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
            # Boss attack patterns based on tier
            if self.boss_tier == 1:
                # Destroyer - focused fire
                for angle in [-10, 0, 10]:
                    rad = math.radians(angle)
                    bdx = dx * math.cos(rad) - dy * math.sin(rad)
                    bdy = dx * math.sin(rad) + dy * math.cos(rad)
                    bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 12))
            elif self.boss_tier == 2:
                # Cruiser - medium spread
                for angle in [-15, -7, 0, 7, 15]:
                    rad = math.radians(angle)
                    bdx = dx * math.cos(rad) - dy * math.sin(rad)
                    bdy = dx * math.sin(rad) + dy * math.cos(rad)
                    bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 13))
            elif self.boss_tier == 3:
                # Battlecruiser - wide spread with higher damage
                for angle in [-25, -12, 0, 12, 25]:
                    rad = math.radians(angle)
                    bdx = dx * math.cos(rad) - dy * math.sin(rad)
                    bdy = dx * math.sin(rad) + dy * math.cos(rad)
                    bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 15))
            else:
                # Battleship - full spread
                for angle in [-25, -15, -5, 5, 15, 25]:
                    rad = math.radians(angle)
                    bdx = dx * math.cos(rad) - dy * math.sin(rad)
                    bdy = dx * math.sin(rad) + dy * math.cos(rad)
                    bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 18))
            
            # Enraged bosses fire additional projectiles
            if hasattr(self, 'enrage_mode') and self.enrage_mode:
                for angle in [-30, 30]:
                    rad = math.radians(angle)
                    bdx = dx * math.cos(rad) - dy * math.sin(rad)
                    bdy = dx * math.sin(rad) + dy * math.cos(rad)
                    bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 12))
        else:
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.3, dy, 10))
        
        return bullets
        
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
