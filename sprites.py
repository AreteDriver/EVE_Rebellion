"""Game sprites for Minmatar Rebellion"""
import pygame
import math
import random
from constants import *
from visual_enhancements import add_ship_glow, add_colored_tint, add_outline, add_strong_outline


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
        """Load ship image from SVG file"""
        import cairosvg
        from io import BytesIO
        
        # Map ship types to SVG files
        ship_svgs = {
            'Rifter': 'assets/minmatar_rebellion/svg/top/rifter.svg',
            'Wolf': 'assets/minmatar_rebellion/svg/top/Wolf.svg',
            'Jaguar': 'assets/minmatar_rebellion/svg/top/jaguar.svg'
        }
        
        ship_type = getattr(self, 'ship_class', 'Rifter')
        svg_path = ship_svgs.get(ship_type, ship_svgs['Rifter'])
        
        try:
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(url=svg_path, output_width=self.width, output_height=self.height)
            
            # Load PNG into pygame surface
            image = pygame.image.load(BytesIO(png_data))
            
            # Ensure proper alpha
            image = image.convert_alpha()
            
            # Rotate to face upward (EVE ships face right by default)
            image = pygame.transform.rotate(image, 90)
            
            # Add strong white outline for visibility
            image = add_strong_outline(image, outline_color=(255, 255, 255), glow_color=(200, 150, 255), thickness=2)
            # Add Minmatar glow (rust/orange)
            image = add_ship_glow(image, (200, 100, 50), intensity=0.3)
            
            return image
            
        except Exception as e:
            print(f"Warning: Could not load {svg_path}: {e}")
            # Fallback to simple shape
            return self._create_fallback_ship_image()
    
    def _create_fallback_ship_image(self):
        """Fallback ship sprite if SVG loading fails"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        color = (200, 100, 100)
        
        # Simple triangle ship
        pygame.draw.polygon(surf, color, [
            (self.width//2, 0),
            (self.width-5, self.height-10),
            (self.width//2, self.height-5),
            (5, self.height-10)
        ])
        
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
        """Upgrade to Jaguar assault frigate"""
        from constants import JAGUAR_SPEED_BONUS, JAGUAR_SHIELD_BONUS
        self.is_wolf = True  # T2 flag
        self.ship_class = 'Jaguar'
        self.speed *= JAGUAR_SPEED_BONUS
        self.max_shields += JAGUAR_SHIELD_BONUS
        self.shields = min(self.shields + JAGUAR_SHIELD_BONUS, self.max_shields)
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
        """Load enemy ship image from SVG based on type"""
        import cairosvg
        from io import BytesIO
        import random
        
        # Map enemy types to ship classes
        frigate_ships = ['punisher', 'tormentor', 'crucifier', 'executioner', 'inquisitor', 'magnate']
        destroyer_ships = ['coercer', 'dragoon', 'heretic', 'confessor']
        cruiser_ships = ['maller', 'omen', 'arbitrator', 'augoror', 'zealot', 'sacrilege', 'curse', 'pilgrim', 'absolution']
        
        # Determine ship class based on enemy type
        if self.is_boss:
            ship_name = random.choice(cruiser_ships)
        elif self.stats.get('tough', False) or self.max_hull > 150:
            ship_name = random.choice(destroyer_ships)
        else:
            ship_name = random.choice(frigate_ships)
        
        svg_path = f'assets/minmatar_rebellion/svg/top/{ship_name}.svg'
        
        try:
            # Convert SVG to PNG
            png_data = cairosvg.svg2png(url=svg_path, output_width=self.width, output_height=self.height)
            image = pygame.image.load(BytesIO(png_data)).convert_alpha()
            
            # Rotate to face downward (enemies come from top)
            image = pygame.transform.rotate(image, -90)
            
            # Add gold outline for Amarr ships
            image = add_strong_outline(image, outline_color=(255, 215, 0), glow_color=(255, 180, 50), thickness=2)
            # Add Amarr gold tint and glow
            image = add_colored_tint(image, (255, 215, 0), alpha=40)
            image = add_ship_glow(image, (255, 215, 100), intensity=0.25)
            
            return image
            
        except Exception as e:
            print(f"Warning: Could not load enemy ship {svg_path}: {e}")
            return self._create_fallback_image()
    
    def _create_fallback_image(self):
        """Fallback enemy sprite"""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        # Gold Amarr color
        color = (200, 180, 100)
        pygame.draw.polygon(surf, color, [
            (self.width//2, self.height),
            (self.width-5, 10),
            (self.width//2, 5),
            (5, 10)
        ])
        return surf

        # Gold Amarr color
        color = (200, 180, 100)
        pygame.draw.polygon(surf, color, [
            (self.width//2, self.height),
            (self.width-5, 10),
            (self.width//2, 5),
            (5, 10)
        ])
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
