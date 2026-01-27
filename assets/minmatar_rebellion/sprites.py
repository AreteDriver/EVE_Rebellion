"""Game sprites for Minmatar Rebellion"""

import math
import random

import pygame
from ship_loader import load_ship_image

from constants import *


class Player(pygame.sprite.Sprite):
    """Player ship - Rifter/Wolf/Jaguar"""

    def __init__(self, ship_type="rifter"):
        super().__init__()
        self.ship_type = ship_type  # 'rifter', 'wolf', or 'jaguar'
        self.is_wolf = ship_type == "wolf"
        self.is_jaguar = ship_type == "jaguar"
        self.width = 40
        self.height = 50
        self.image = self._create_ship_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50

        # Stats - apply T2 bonuses
        base_shields = PLAYER_START_SHIELDS
        base_armor = PLAYER_START_ARMOR
        base_hull = PLAYER_START_HULL

        if self.is_jaguar:
            # Jaguar bonuses: shields, speed, minor damage
            self.max_shields = base_shields + JAGUAR_SHIELD_BONUS
            self.max_armor = base_armor
            self.max_hull = base_hull + JAGUAR_HULL_BONUS
            self.damage_mult = JAGUAR_DAMAGE_BONUS
            self.speed_mult = JAGUAR_SPEED_BONUS
        elif self.is_wolf:
            # Wolf bonuses: armor, damage, minor speed
            self.max_shields = base_shields
            self.max_armor = base_armor + WOLF_ARMOR_BONUS
            self.max_hull = base_hull + WOLF_HULL_BONUS
            self.damage_mult = WOLF_DAMAGE_BONUS
            self.speed_mult = WOLF_SPEED_BONUS
        else:
            # Base Rifter
            self.max_shields = base_shields
            self.max_armor = base_armor
            self.max_hull = base_hull
            self.damage_mult = 1.0
            self.speed_mult = 1.0

        self.shields = self.max_shields
        self.armor = self.max_armor
        self.hull = self.max_hull

        # Weapons
        self.current_ammo = "sabot"
        self.unlocked_ammo = ["sabot"]
        self.rockets = PLAYER_MAX_ROCKETS
        self.max_rockets = PLAYER_MAX_ROCKETS

        # Timing
        self.last_shot = 0
        self.last_rocket = 0
        self.fire_rate_mult = 1.0
        self.spread_bonus = 1 if self.is_wolf else 0  # Wolf gets +1 spread

        # Movement
        self.speed = PLAYER_SPEED * self.speed_mult

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
        self.sp = 0  # Skill Points

    def _create_ship_image(self):
        """Create Rifter/Wolf/Jaguar sprite - loads SVG if available, else procedural"""
        # Determine ship name and color
        if self.is_jaguar:
            ship_name = "jaguar"
            color = (50, 150, 255)  # Blue accent for Jaguar
        elif self.is_wolf:
            ship_name = "Wolf"
            color = COLOR_MINMATAR_ACCENT  # Orange for Wolf
        else:
            ship_name = "rifter"
            color = COLOR_MINMATAR_HULL  # Brown for Rifter

        # Try to load actual ship image
        svg_surface = load_ship_image(ship_name, self.width, self.height, color)

        if svg_surface:
            # Successfully loaded SVG!
            # Rotate 180 degrees (SVGs point down, we need up)
            return pygame.transform.rotate(svg_surface, 180)

        # Fallback to procedural graphics
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.is_jaguar:
            # Jaguar - angular, fast, shield-focused
            pygame.draw.polygon(
                surf,
                color,
                [
                    (self.width // 2, 0),
                    (self.width - 6, self.height - 12),
                    (self.width // 2, self.height - 6),
                    (6, self.height - 12),
                ],
            )
            # Shield generator pods
            pygame.draw.polygon(
                surf,
                (100, 180, 255),
                [(2, self.height - 18), (8, self.height // 2), (8, self.height - 8)],
            )
            pygame.draw.polygon(
                surf,
                (100, 180, 255),
                [
                    (self.width - 2, self.height - 18),
                    (self.width - 8, self.height // 2),
                    (self.width - 8, self.height - 8),
                ],
            )
            # Blue engine glow
            pygame.draw.circle(surf, (100, 200, 255), (self.width // 2, self.height - 6), 5)

        elif self.is_wolf:
            # Wolf - sleeker, more refined
            pygame.draw.polygon(
                surf,
                color,
                [
                    (self.width // 2, 0),
                    (self.width - 5, self.height - 10),
                    (self.width // 2, self.height - 5),
                    (5, self.height - 10),
                ],
            )
            pygame.draw.polygon(
                surf,
                COLOR_MINMATAR_HULL,
                [(0, self.height - 15), (10, self.height // 2), (10, self.height - 5)],
            )
            pygame.draw.polygon(
                surf,
                COLOR_MINMATAR_HULL,
                [
                    (self.width, self.height - 15),
                    (self.width - 10, self.height // 2),
                    (self.width - 10, self.height - 5),
                ],
            )
            # Orange engine glow
            pygame.draw.circle(surf, (255, 150, 50), (self.width // 2, self.height - 8), 5)
        else:
            # Rifter - asymmetric, aggressive
            pygame.draw.polygon(
                surf,
                color,
                [
                    (self.width // 2 - 3, 0),
                    (self.width - 8, self.height - 15),
                    (self.width // 2, self.height),
                    (8, self.height - 15),
                ],
            )
            pygame.draw.polygon(
                surf,
                COLOR_MINMATAR_DARK,
                [(0, self.height - 10), (5, self.height // 3), (12, self.height - 5)],
            )
            pygame.draw.polygon(
                surf,
                COLOR_MINMATAR_DARK,
                [
                    (self.width - 3, self.height - 20),
                    (self.width - 8, self.height // 2),
                    (self.width - 12, self.height - 8),
                ],
            )
            # Red engine glow
            pygame.draw.circle(surf, (255, 100, 0), (self.width // 2, self.height - 5), 4)

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
        if ammo_type not in self.unlocked_ammo:
            self.unlocked_ammo.append(ammo_type)

    def switch_ammo(self, ammo_type):
        if ammo_type in self.unlocked_ammo:
            self.current_ammo = ammo_type
            return True
        return False

    def cycle_ammo(self):
        idx = self.unlocked_ammo.index(self.current_ammo)
        idx = (idx + 1) % len(self.unlocked_ammo)
        self.current_ammo = self.unlocked_ammo[idx]

    def update(self, keys):
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

        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def can_shoot(self):
        now = pygame.time.get_ticks()
        ammo = AMMO_TYPES[self.current_ammo]
        cooldown = PLAYER_BASE_FIRE_RATE / (ammo["fire_rate"] * self.fire_rate_mult)
        return now - self.last_shot > cooldown

    def shoot(self):
        if not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()
        bullets = []
        ammo = AMMO_TYPES[self.current_ammo]

        num_shots = 2 + self.spread_bonus
        spread = 15 + (self.spread_bonus * 5)

        for i in range(num_shots):
            offset = (i - (num_shots - 1) / 2) * spread
            bullet = Bullet(
                self.rect.centerx + offset,
                self.rect.top,
                0,
                -BULLET_SPEED,
                ammo["tracer"],
                BULLET_DAMAGE,
                ammo["shield_mult"],
                ammo["armor_mult"],
            )
            bullets.append(bullet)

        return bullets

    def can_rocket(self):
        now = pygame.time.get_ticks()
        return self.rockets > 0 and now - self.last_rocket > PLAYER_ROCKET_COOLDOWN

    def shoot_rocket(self):
        if not self.can_rocket():
            return None

        self.last_rocket = pygame.time.get_ticks()
        self.rockets -= 1
        return Rocket(self.rect.centerx, self.rect.top)

    def take_damage(self, amount):
        if pygame.time.get_ticks() < self.shield_boost_until:
            amount *= 0.3

        if self.shields > 0:
            absorbed = min(self.shields, amount)
            self.shields -= absorbed
            amount -= absorbed

        if amount > 0 and self.armor > 0:
            absorbed = min(self.armor, amount)
            self.armor -= absorbed
            amount -= absorbed

        if amount > 0:
            self.hull -= amount

        return self.hull <= 0

    def heal(self, amount):
        self.hull = min(self.hull + amount, self.max_hull)
        remaining = amount - (self.max_hull - self.hull)
        if remaining > 0:
            self.armor = min(self.armor + remaining, self.max_armor)

    def add_rockets(self, amount):
        self.rockets = min(self.rockets + amount, self.max_rockets)

    def collect_refugee(self, count=1):
        self.refugees += count
        self.total_refugees += count
        self.score += count * 10


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, color, damage, shield_mult=1.0, armor_mult=1.0):
        super().__init__()
        self.image = pygame.Surface((4, 12), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 4, 12))
        pygame.draw.rect(self.image, (255, 255, 255), (1, 0, 2, 4))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.shield_mult = shield_mult
        self.armor_mult = armor_mult

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (
            self.rect.bottom < 0
            or self.rect.top > SCREEN_HEIGHT
            or self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
        ):
            self.kill()


class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (150, 150, 150), (2, 5, 4, 15))
        pygame.draw.polygon(self.image, (200, 50, 50), [(4, 0), (0, 8), (8, 8)])
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
    def __init__(self, x, y, dx, dy, damage=10):
        super().__init__()
        self.image = pygame.Surface((4, 16), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (255, 220, 100), (0, 0, 4, 16))
        pygame.draw.rect(self.image, (255, 255, 200), (1, 0, 2, 16))
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.damage = damage

    def update(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if (
            self.rect.bottom < 0
            or self.rect.top > SCREEN_HEIGHT
            or self.rect.right < 0
            or self.rect.left > SCREEN_WIDTH
        ):
            self.kill()


class Enemy(pygame.sprite.Sprite):
    PATTERN_DRIFT = 0
    PATTERN_SINE = 1
    PATTERN_ZIGZAG = 2
    PATTERN_CIRCLE = 3
    PATTERN_SWOOP = 4
    PATTERN_FLANK = 5
    PATTERN_STRAFE = 6  # Boss pattern - side to side while shooting
    PATTERN_AGGRESSIVE = 7  # Boss pattern - moves toward player

    def __init__(self, enemy_type, x, y, difficulty=None, wave_scaling=1.0):
        super().__init__()
        self.enemy_type = enemy_type
        self.stats = ENEMY_STATS[enemy_type]
        self.difficulty = difficulty or {}
        self.wave_scaling = wave_scaling

        self.width, self.height = self.stats["size"]
        self.image = self._create_image()
        self.rect = self.image.get_rect(center=(x, y))

        health_mult = self.difficulty.get("enemy_health_mult", 1.0) * wave_scaling

        self.shields = int(self.stats["shields"] * health_mult)
        self.armor = int(self.stats["armor"] * health_mult)
        self.hull = int(self.stats["hull"] * health_mult)
        self.max_shields = self.shields
        self.max_armor = self.armor
        self.max_hull = self.hull

        self.speed = self.stats["speed"]
        fire_rate_mult = self.difficulty.get("enemy_fire_rate_mult", 1.0)
        self.fire_rate = int(self.stats["fire_rate"] * fire_rate_mult)
        self.last_shot = pygame.time.get_ticks() + random.randint(0, 1000)
        self.score = int(self.stats["score"] * wave_scaling)
        self.refugees = self.stats.get("refugees", 0)
        self.is_boss = self.stats.get("boss", False)
        self.sp_value = int(self.stats.get("sp_value", 5) * wave_scaling)

        # Boss-specific attributes
        if self.is_boss:
            self.boss_phase = 0
            self.boss_phase_timer = 0
            self.special_ability = self.stats.get("special_ability", None)
            self.ability_cooldown = 0
            self.ability_active = False
            self.enraged = False  # Enrage at 25% health
            self.shield_regen_rate = 0  # For armor_repair ability
            self.strafe_direction = 1  # For STRAFE pattern

        self._select_movement_pattern()

        self.pattern_timer = random.uniform(0, math.pi * 2)
        self.target_y = self._get_target_y()
        self.entered = False
        self.swoop_state = "enter"
        self.flank_side = random.choice([-1, 1])
        self.circle_center_x = x
        self.circle_radius = random.randint(50, 100)

    def _select_movement_pattern(self):
        if self.is_boss:
            self.pattern = self.PATTERN_DRIFT
        elif self.enemy_type == "executioner":
            self.pattern = random.choice(
                [self.PATTERN_SINE, self.PATTERN_ZIGZAG, self.PATTERN_SWOOP, self.PATTERN_FLANK]
            )
        elif self.enemy_type == "punisher":
            self.pattern = random.choice(
                [self.PATTERN_DRIFT, self.PATTERN_SINE, self.PATTERN_CIRCLE]
            )
        elif self.enemy_type in ["omen", "maller"]:
            self.pattern = random.choice(
                [self.PATTERN_CIRCLE, self.PATTERN_FLANK, self.PATTERN_DRIFT]
            )
        elif self.enemy_type == "bestower":
            self.pattern = self.PATTERN_DRIFT
            self.speed *= 0.8
        else:
            self.pattern = self.PATTERN_DRIFT

    def _get_target_y(self):
        if self.is_boss:
            return 120
        elif self.enemy_type == "bestower":
            return random.randint(80, 180)
        else:
            return random.randint(80, 300)

    def _create_image(self):
        """Create Amarr ship sprite - loads SVG if available, else procedural"""
        # Try to load actual ship image
        svg_surface = load_ship_image(self.enemy_type, self.width, self.height, COLOR_AMARR_HULL)

        if svg_surface:
            # Successfully loaded SVG! No rotation needed (enemies point down)
            return svg_surface

        # Fallback to procedural graphics
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.enemy_type == "executioner":
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_HULL,
                [(self.width // 2, self.height), (0, 10), (self.width // 2, 0), (self.width, 10)],
            )
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_ACCENT,
                [(self.width // 2, self.height - 5), (10, 15), (self.width - 10, 15)],
            )

        elif self.enemy_type == "punisher":
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_HULL,
                [
                    (self.width // 2, self.height),
                    (5, self.height // 3),
                    (5, 5),
                    (self.width - 5, 5),
                    (self.width - 5, self.height // 3),
                ],
            )
            pygame.draw.rect(
                surf, COLOR_AMARR_ACCENT, (self.width // 4, 10, self.width // 2, self.height // 2)
            )

        elif self.enemy_type == "omen":
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_HULL,
                [
                    (self.width // 2, self.height),
                    (0, self.height // 2),
                    (5, 5),
                    (self.width - 5, 5),
                    (self.width, self.height // 2),
                ],
            )
            pygame.draw.ellipse(
                surf, COLOR_AMARR_ACCENT, (10, 10, self.width - 20, self.height // 2)
            )

        elif self.enemy_type == "maller":
            pygame.draw.rect(surf, COLOR_AMARR_HULL, (5, 5, self.width - 10, self.height - 10))
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_ACCENT,
                [
                    (self.width // 2, self.height - 5),
                    (10, self.height // 2),
                    (self.width - 10, self.height // 2),
                ],
            )

        elif self.enemy_type == "bestower":
            pygame.draw.rect(surf, COLOR_AMARR_DARK, (10, 5, self.width - 20, self.height - 10))
            pygame.draw.rect(
                surf, COLOR_AMARR_HULL, (5, self.height // 3, self.width - 10, self.height // 3)
            )

        elif self.enemy_type in ["apocalypse", "abaddon"]:
            pygame.draw.polygon(
                surf,
                COLOR_AMARR_HULL,
                [
                    (self.width // 2, self.height),
                    (0, self.height * 2 // 3),
                    (0, self.height // 3),
                    (self.width // 4, 0),
                    (self.width * 3 // 4, 0),
                    (self.width, self.height // 3),
                    (self.width, self.height * 2 // 3),
                ],
            )
            pygame.draw.ellipse(
                surf,
                COLOR_AMARR_ACCENT,
                (self.width // 4, self.height // 4, self.width // 2, self.height // 2),
            )
            if self.enemy_type == "abaddon":
                pygame.draw.rect(surf, (255, 215, 0), (self.width // 3, 10, self.width // 3, 20))

        return surf

    def update(self, player_rect=None):
        self.pattern_timer += 0.05

        if not self.entered:
            if self.rect.centery < self.target_y:
                self.rect.y += self.speed * 1.5
            else:
                self.entered = True
            return

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

        if self.is_boss:
            self._update_boss_behavior()

        if self.rect.left < 10:
            self.rect.left = 10
        elif self.rect.right > SCREEN_WIDTH - 10:
            self.rect.right = SCREEN_WIDTH - 10

    def _move_drift(self):
        self.rect.x += math.sin(self.pattern_timer) * self.speed
        if self.rect.centery < self.target_y:
            self.rect.y += self.speed * 0.3

    def _move_sine(self):
        amplitude = 80 + 40 * math.sin(self.pattern_timer * 0.3)
        self.rect.centerx = SCREEN_WIDTH // 2 + math.sin(self.pattern_timer * 1.5) * amplitude
        self.rect.centery = self.target_y + math.sin(self.pattern_timer * 0.8) * 30

    def _move_zigzag(self):
        direction = 1 if int(self.pattern_timer * 2) % 2 == 0 else -1
        self.rect.x += direction * self.speed * 2
        if abs(math.sin(self.pattern_timer * 2)) < 0.1:
            self.rect.y += self.speed

    def _move_circle(self):
        self.rect.centerx = self.circle_center_x + math.cos(self.pattern_timer) * self.circle_radius
        self.rect.centery = self.target_y + math.sin(self.pattern_timer) * (
            self.circle_radius * 0.5
        )
        self.circle_center_x += math.sin(self.pattern_timer * 0.2) * 0.5
        self.circle_center_x = max(100, min(SCREEN_WIDTH - 100, self.circle_center_x))

    def _move_swoop(self, player_rect):
        if self.swoop_state == "enter":
            if self.rect.centery >= self.target_y:
                self.swoop_state = "aim"
        elif self.swoop_state == "aim":
            if self.pattern_timer % (math.pi * 2) < 0.1:
                self.swoop_state = "dive"
                if player_rect:
                    self.swoop_target_x = player_rect.centerx
                else:
                    self.swoop_target_x = SCREEN_WIDTH // 2
        elif self.swoop_state == "dive":
            self.rect.y += self.speed * 3
            dx = self.swoop_target_x - self.rect.centerx
            self.rect.x += max(-self.speed * 2, min(self.speed * 2, dx * 0.1))
            if self.rect.centery > SCREEN_HEIGHT * 0.6:
                self.swoop_state = "retreat"
        elif self.swoop_state == "retreat":
            self.rect.y -= self.speed * 2
            if self.rect.centery < self.target_y:
                self.swoop_state = "aim"

        if self.swoop_state == "aim":
            self.rect.x += math.sin(self.pattern_timer * 2) * self.speed

    def _move_flank(self, player_rect):
        target_x = 80 if self.flank_side < 0 else SCREEN_WIDTH - 80
        dx = target_x - self.rect.centerx
        if abs(dx) > 5:
            self.rect.x += max(-self.speed, min(self.speed, dx * 0.05))

        if player_rect:
            target_y = min(player_rect.centery - 200, 250)
            target_y = max(80, target_y)
            dy = target_y - self.rect.centery
            self.rect.y += max(-self.speed * 0.5, min(self.speed * 0.5, dy * 0.02))

        if random.random() < 0.002:
            self.flank_side *= -1

    def _update_boss_behavior(self):
        self.boss_phase_timer += 1
        health_pct = (self.shields + self.armor + self.hull) / (
            self.max_shields + self.max_armor + self.max_hull
        )

        if health_pct < 0.3 and self.boss_phase < 2:
            self.boss_phase = 2
            self.speed *= 1.3
        elif health_pct < 0.6 and self.boss_phase < 1:
            self.boss_phase = 1
            self.fire_rate = int(self.fire_rate * 0.8)

    def can_shoot(self):
        if self.fire_rate == 0:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_shot > self.fire_rate

    def shoot(self, player_rect):
        if not self.can_shoot():
            return []

        self.last_shot = pygame.time.get_ticks()
        bullets = []

        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dx = dx / dist * 5
            dy = dy / dist * 5
        else:
            dy = 5

        if self.is_boss:
            for angle in [-20, -10, 0, 10, 20]:
                rad = math.radians(angle)
                bdx = dx * math.cos(rad) - dy * math.sin(rad)
                bdy = dx * math.sin(rad) + dy * math.cos(rad)
                bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, bdx, bdy, 15))
        else:
            bullets.append(EnemyBullet(self.rect.centerx, self.rect.bottom, dx * 0.3, dy, 10))

        return bullets

    def take_damage(self, bullet):
        damage = bullet.damage

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
    def __init__(self, x, y, count=1):
        super().__init__()
        self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (200, 200, 200), (8, 8), 7)
        pygame.draw.circle(self.image, (100, 200, 100), (8, 8), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.count = count
        self.lifetime = 300
        self.drift_x = random.uniform(-0.5, 0.5)
        self.drift_y = random.uniform(0.5, 1.5)

    def update(self):
        self.rect.x += self.drift_x
        self.rect.y += self.drift_y
        self.lifetime -= 1

        if self.lifetime < 60 and self.lifetime % 10 < 5:
            self.image.set_alpha(128)
        else:
            self.image.set_alpha(255)

        if self.lifetime <= 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.data = POWERUP_TYPES[powerup_type]

        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.data["color"], (2, 2, 16, 16))
        pygame.draw.rect(self.image, (255, 255, 255), (2, 2, 16, 16), 2)

        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
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
        pygame.draw.circle(self.image, color_with_alpha, (current_size, current_size), current_size)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.frame += 1
        if self.frame >= self.max_frames:
            self.kill()
        else:
            self._update_image()


class Star:
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
