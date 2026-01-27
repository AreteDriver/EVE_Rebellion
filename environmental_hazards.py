"""
Environmental Hazards for EVE Rebellion

Adds variety and danger to stages with EVE-themed hazards:
- Asteroid fields: Physical obstacles, damage on contact
- Solar flares: Screen-wide periodic damage with warning
- Warp disruption bubbles: Pull player toward center
- Nebula clouds: Slow movement, obscure visibility
- Proximity mines: Explode when player gets close
"""

import math
import random

import pygame

from constants import SCREEN_HEIGHT, SCREEN_WIDTH


class Asteroid(pygame.sprite.Sprite):
    """Drifting asteroid that damages on contact"""

    def __init__(self, x, y, size="medium"):
        super().__init__()
        self.size = size

        # Size determines damage and visual
        sizes = {
            "small": (20, 30, 10),  # (min_radius, max_radius, damage)
            "medium": (35, 50, 20),
            "large": (55, 75, 35),
        }
        min_r, max_r, self.damage = sizes.get(size, sizes["medium"])
        self.radius = random.randint(min_r, max_r)

        # Create asteroid visual
        surf_size = self.radius * 2 + 10
        self.image = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        self._draw_asteroid()

        self.rect = self.image.get_rect(center=(x, y))

        # Movement - slow drift downward with slight horizontal movement
        self.vy = random.uniform(0.8, 1.5)
        self.vx = random.uniform(-0.3, 0.3)
        self.rotation = random.uniform(-0.5, 0.5)
        self.angle = random.uniform(0, 360)

        # For smooth position
        self.x = float(x)
        self.y = float(y)

    def _draw_asteroid(self):
        """Draw procedural asteroid"""
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2

        # Base color - gray/brown rock
        base_color = random.choice(
            [
                (80, 70, 60),  # Brown
                (70, 70, 75),  # Gray
                (60, 55, 50),  # Dark brown
            ]
        )

        # Draw irregular polygon for asteroid shape
        num_points = random.randint(7, 12)
        points = []
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            # Vary radius for irregular shape
            r = self.radius * random.uniform(0.7, 1.0)
            px = cx + int(math.cos(angle) * r)
            py = cy + int(math.sin(angle) * r)
            points.append((px, py))

        # Draw filled polygon
        pygame.draw.polygon(self.image, base_color, points)

        # Add highlight on top-left
        highlight_color = tuple(min(255, c + 40) for c in base_color)
        for i in range(3):
            offset = i * 3
            pygame.draw.circle(
                self.image,
                (*highlight_color, 80 - i * 20),
                (cx - self.radius // 3 + offset, cy - self.radius // 3 + offset),
                self.radius // 4 - i * 2,
            )

        # Add craters
        num_craters = random.randint(2, 5)
        for _ in range(num_craters):
            crater_x = cx + random.randint(-self.radius // 2, self.radius // 2)
            crater_y = cy + random.randint(-self.radius // 2, self.radius // 2)
            crater_r = random.randint(3, self.radius // 4)
            crater_color = tuple(max(0, c - 30) for c in base_color)
            pygame.draw.circle(self.image, crater_color, (crater_x, crater_y), crater_r)

        # Outline
        pygame.draw.polygon(self.image, (40, 35, 30), points, 2)

    def update(self):
        """Update asteroid position"""
        self.x += self.vx
        self.y += self.vy
        self.angle += self.rotation

        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()


class SolarFlare(pygame.sprite.Sprite):
    """Screen-wide solar flare event with warning"""

    # States
    STATE_WARNING = 0
    STATE_CHARGING = 1
    STATE_FLARE = 2
    STATE_FADING = 3
    STATE_DONE = 4

    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.state = self.STATE_WARNING
        self.timer = 0
        self.damage = 15  # Damage dealt during flare

        # Timing
        self.warning_duration = 90  # 1.5 seconds warning
        self.charge_duration = 30  # 0.5 seconds charge
        self.flare_duration = 20  # Brief intense flash
        self.fade_duration = 30  # Fade out

        self.intensity = 0
        self.warning_flash = 0

    def update(self):
        """Update flare state"""
        self.timer += 1
        self.image.fill((0, 0, 0, 0))  # Clear

        if self.state == self.STATE_WARNING:
            # Flashing warning
            self.warning_flash = (self.warning_flash + 1) % 20
            if self.warning_flash < 10:
                # Draw warning bars at top and bottom
                bar_height = 20
                warning_color = (255, 200, 50, 150)
                pygame.draw.rect(self.image, warning_color, (0, 0, SCREEN_WIDTH, bar_height))
                pygame.draw.rect(
                    self.image,
                    warning_color,
                    (0, SCREEN_HEIGHT - bar_height, SCREEN_WIDTH, bar_height),
                )

                # Warning text
                font = pygame.font.Font(None, 48)
                text = font.render("SOLAR FLARE INCOMING!", True, (255, 220, 100))
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.image.blit(text, text_rect)

            if self.timer >= self.warning_duration:
                self.state = self.STATE_CHARGING
                self.timer = 0

        elif self.state == self.STATE_CHARGING:
            # Intensity building
            progress = self.timer / self.charge_duration
            self.intensity = int(progress * 100)

            # Yellow glow building from edges
            glow_color = (255, 220, 100, self.intensity)
            pygame.draw.rect(self.image, glow_color, self.image.get_rect())

            if self.timer >= self.charge_duration:
                self.state = self.STATE_FLARE
                self.timer = 0

        elif self.state == self.STATE_FLARE:
            # Intense white flash
            progress = self.timer / self.flare_duration
            alpha = int(200 * (1 - progress * 0.5))
            flash_color = (255, 255, 220, alpha)
            pygame.draw.rect(self.image, flash_color, self.image.get_rect())

            if self.timer >= self.flare_duration:
                self.state = self.STATE_FADING
                self.timer = 0

        elif self.state == self.STATE_FADING:
            # Fade out
            progress = self.timer / self.fade_duration
            alpha = int(100 * (1 - progress))
            fade_color = (255, 200, 100, alpha)
            pygame.draw.rect(self.image, fade_color, self.image.get_rect())

            if self.timer >= self.fade_duration:
                self.state = self.STATE_DONE
                self.kill()

    def is_damaging(self):
        """Check if flare is currently dealing damage"""
        return self.state == self.STATE_FLARE

    def get_damage(self):
        """Get damage to apply"""
        if self.is_damaging():
            return self.damage
        return 0


class WarpBubble(pygame.sprite.Sprite):
    """Warp disruption bubble that pulls player toward center"""

    def __init__(self, x, y, radius=120, duration=300):
        super().__init__()
        self.center_x = x
        self.center_y = y
        self.radius = radius
        self.pull_strength = 2.0  # Pixels per frame toward center
        self.duration = duration
        self.timer = 0

        # Create visual
        size = radius * 2 + 20
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.pulse_timer = 0

    def update(self):
        """Update bubble state"""
        self.timer += 1
        self.pulse_timer += 1

        # Redraw with pulsing effect
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2

        # Pulsing radius
        pulse = 1.0 + 0.1 * math.sin(self.pulse_timer * 0.1)
        draw_radius = int(self.radius * pulse)

        # Outer glow
        for r in range(draw_radius + 20, draw_radius, -2):
            alpha = int(30 * (1 - (r - draw_radius) / 20))
            pygame.draw.circle(self.image, (100, 50, 150, alpha), (cx, cy), r)

        # Main bubble - semi-transparent purple
        pygame.draw.circle(self.image, (80, 40, 120, 60), (cx, cy), draw_radius)

        # Inner swirl effect
        num_swirls = 6
        swirl_angle = self.pulse_timer * 0.05
        for i in range(num_swirls):
            angle = swirl_angle + (i / num_swirls) * math.pi * 2
            for dist in range(20, draw_radius - 10, 15):
                swirl_x = cx + int(math.cos(angle + dist * 0.02) * dist)
                swirl_y = cy + int(math.sin(angle + dist * 0.02) * dist)
                alpha = int(40 * (1 - dist / draw_radius))
                pygame.draw.circle(self.image, (150, 100, 200, alpha), (swirl_x, swirl_y), 3)

        # Edge ring
        pygame.draw.circle(self.image, (150, 100, 200, 100), (cx, cy), draw_radius, 3)

        # Center point
        pygame.draw.circle(self.image, (200, 150, 255, 150), (cx, cy), 8)
        pygame.draw.circle(self.image, (255, 200, 255), (cx, cy), 4)

        # Expire
        if self.timer >= self.duration:
            self.kill()

    def get_pull_force(self, player_x, player_y):
        """Calculate pull force on player if within bubble"""
        dx = self.center_x - player_x
        dy = self.center_y - player_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.radius and dist > 10:
            # Normalize and apply pull strength
            force_x = (dx / dist) * self.pull_strength
            force_y = (dy / dist) * self.pull_strength
            return force_x, force_y

        return 0, 0


class NebulaCloud(pygame.sprite.Sprite):
    """Nebula cloud that slows movement and obscures vision"""

    def __init__(self, x, y, width=200, height=150):
        super().__init__()
        self.slow_factor = 0.5  # Player moves at 50% speed inside

        # Create cloud visual
        self.width = width
        self.height = height
        self.image = pygame.Surface((width + 40, height + 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self._draw_nebula()

        # Slow drift
        self.vy = random.uniform(0.3, 0.6)
        self.y = float(y)

        # Animation
        self.anim_timer = random.randint(0, 100)

    def _draw_nebula(self):
        """Draw nebula cloud with multiple layers"""
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2

        # Base color - bluish or reddish nebula
        base_hue = random.choice(
            [
                (60, 80, 120),  # Blue nebula
                (120, 60, 80),  # Red nebula
                (80, 100, 80),  # Green nebula
            ]
        )

        # Multiple overlapping ellipses for cloud effect
        for _ in range(8):
            offset_x = random.randint(-self.width // 4, self.width // 4)
            offset_y = random.randint(-self.height // 4, self.height // 4)
            size_x = random.randint(self.width // 2, self.width)
            size_y = random.randint(self.height // 2, self.height)

            # Vary color slightly
            color = tuple(max(0, min(255, c + random.randint(-20, 20))) for c in base_hue)
            alpha = random.randint(30, 60)

            ellipse_surf = pygame.Surface((size_x, size_y), pygame.SRCALPHA)
            pygame.draw.ellipse(ellipse_surf, (*color, alpha), (0, 0, size_x, size_y))

            self.image.blit(
                ellipse_surf, (cx + offset_x - size_x // 2, cy + offset_y - size_y // 2)
            )

        # Add some bright spots (stars within nebula)
        for _ in range(5):
            star_x = cx + random.randint(-self.width // 3, self.width // 3)
            star_y = cy + random.randint(-self.height // 3, self.height // 3)
            pygame.draw.circle(self.image, (200, 200, 255, 100), (star_x, star_y), 2)

    def update(self):
        """Update nebula position"""
        self.y += self.vy
        self.rect.centery = int(self.y)
        self.anim_timer += 1

        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()

    def contains_point(self, x, y):
        """Check if point is inside nebula (approximate)"""
        # Use ellipse check
        cx, cy = self.rect.center
        dx = (x - cx) / (self.width / 2)
        dy = (y - cy) / (self.height / 2)
        return (dx * dx + dy * dy) <= 1.0


class ProximityMine(pygame.sprite.Sprite):
    """Mine that explodes when player gets close"""

    STATE_ARMED = 0
    STATE_TRIGGERED = 1
    STATE_EXPLODING = 2

    def __init__(self, x, y):
        super().__init__()
        self.trigger_radius = 60
        self.explosion_radius = 100
        self.damage = 40

        self.state = self.STATE_ARMED
        self.timer = 0
        self.trigger_delay = 30  # Frames before explosion after trigger
        self.explosion_duration = 15

        # Visual
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

        self.blink_timer = 0
        self._draw_mine()

        # Slow drift
        self.vy = random.uniform(0.2, 0.5)
        self.y = float(y)

    def _draw_mine(self):
        """Draw mine visual"""
        self.image.fill((0, 0, 0, 0))
        cx, cy = 15, 15

        # Main body
        pygame.draw.circle(self.image, (60, 60, 70), (cx, cy), 12)
        pygame.draw.circle(self.image, (80, 80, 90), (cx, cy), 10)

        # Spikes
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            sx = cx + int(math.cos(rad) * 14)
            sy = cy + int(math.sin(rad) * 14)
            pygame.draw.circle(self.image, (100, 100, 110), (sx, sy), 3)

        # Center indicator
        if self.state == self.STATE_ARMED:
            # Blinking red light
            if self.blink_timer % 30 < 15:
                pygame.draw.circle(self.image, (255, 50, 50), (cx, cy), 4)
            else:
                pygame.draw.circle(self.image, (100, 20, 20), (cx, cy), 4)
        elif self.state == self.STATE_TRIGGERED:
            # Fast blinking
            if self.blink_timer % 6 < 3:
                pygame.draw.circle(self.image, (255, 100, 100), (cx, cy), 5)

    def update(self):
        """Update mine state"""
        self.blink_timer += 1
        self.y += self.vy
        self.rect.centery = int(self.y)

        if self.state == self.STATE_TRIGGERED:
            self.timer += 1
            self._draw_mine()

            if self.timer >= self.trigger_delay:
                self.state = self.STATE_EXPLODING
                self.timer = 0

        elif self.state == self.STATE_EXPLODING:
            self.timer += 1

            # Draw explosion
            progress = self.timer / self.explosion_duration
            exp_radius = int(self.explosion_radius * progress)

            self.image = pygame.Surface(
                (self.explosion_radius * 2 + 20, self.explosion_radius * 2 + 20), pygame.SRCALPHA
            )
            cx, cy = self.image.get_width() // 2, self.image.get_height() // 2

            # Explosion rings
            alpha = int(200 * (1 - progress))
            pygame.draw.circle(self.image, (255, 200, 100, alpha), (cx, cy), exp_radius)
            pygame.draw.circle(self.image, (255, 150, 50, alpha), (cx, cy), int(exp_radius * 0.7))
            pygame.draw.circle(self.image, (255, 255, 200, alpha), (cx, cy), int(exp_radius * 0.3))

            self.rect = self.image.get_rect(center=self.rect.center)

            if self.timer >= self.explosion_duration:
                self.kill()

        else:
            self._draw_mine()

        # Remove if off screen
        if self.rect.top > SCREEN_HEIGHT + 50:
            self.kill()

    def check_trigger(self, player_x, player_y):
        """Check if player triggered the mine"""
        if self.state != self.STATE_ARMED:
            return False

        dx = self.rect.centerx - player_x
        dy = self.rect.centery - player_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.trigger_radius:
            self.state = self.STATE_TRIGGERED
            return True
        return False

    def is_exploding(self):
        return self.state == self.STATE_EXPLODING

    def get_explosion_damage(self, player_x, player_y):
        """Get damage if player in explosion radius"""
        if not self.is_exploding():
            return 0

        dx = self.rect.centerx - player_x
        dy = self.rect.centery - player_y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < self.explosion_radius:
            # Damage falls off with distance
            damage_mult = 1.0 - (dist / self.explosion_radius)
            return int(self.damage * damage_mult)
        return 0


class HazardManager:
    """Manages environmental hazards during gameplay"""

    def __init__(self):
        self.asteroids = pygame.sprite.Group()
        self.flares = pygame.sprite.Group()
        self.bubbles = pygame.sprite.Group()
        self.nebulae = pygame.sprite.Group()
        self.mines = pygame.sprite.Group()

        # Spawn timers
        self.asteroid_timer = 0
        self.flare_timer = 0
        self.bubble_timer = 0
        self.nebula_timer = 0
        self.mine_timer = 0

        # Spawn rates (frames between spawns) - adjusted by stage
        self.asteroid_rate = 180  # Every 3 seconds
        self.flare_rate = 1800  # Every 30 seconds
        self.bubble_rate = 600  # Every 10 seconds
        self.nebula_rate = 400  # Every ~7 seconds
        self.mine_rate = 300  # Every 5 seconds

        # Which hazards are active (set by stage)
        self.hazards_enabled = {
            "asteroids": False,
            "flares": False,
            "bubbles": False,
            "nebulae": False,
            "mines": False,
        }

    def set_stage_hazards(self, stage_index):
        """Enable hazards based on stage"""
        # Reset all
        for key in self.hazards_enabled:
            self.hazards_enabled[key] = False

        # Stage-specific hazards
        if stage_index == 0:  # Asteroid Belt Escape
            self.hazards_enabled["asteroids"] = True
        elif stage_index == 1:  # Patrol Interdiction
            self.hazards_enabled["asteroids"] = True
            self.hazards_enabled["mines"] = True
        elif stage_index == 2:  # Slave Colony Liberation
            self.hazards_enabled["nebulae"] = True
        elif stage_index == 3:  # Gate Assault
            self.hazards_enabled["bubbles"] = True
            self.hazards_enabled["mines"] = True
        elif stage_index == 4:  # Final Push
            self.hazards_enabled["asteroids"] = True
            self.hazards_enabled["flares"] = True
            self.hazards_enabled["bubbles"] = True

    def update(self, player_rect):
        """Update all hazards and check collisions"""
        # Spawn new hazards
        self._spawn_hazards()

        # Update all groups
        self.asteroids.update()
        self.flares.update()
        self.bubbles.update()
        self.nebulae.update()
        self.mines.update()

        # Check mine triggers
        for mine in self.mines:
            mine.check_trigger(player_rect.centerx, player_rect.centery)

    def _spawn_hazards(self):
        """Spawn hazards based on timers and enabled flags"""
        if self.hazards_enabled["asteroids"]:
            self.asteroid_timer += 1
            if self.asteroid_timer >= self.asteroid_rate:
                self.asteroid_timer = 0
                size = random.choice(["small", "small", "medium", "medium", "large"])
                x = random.randint(50, SCREEN_WIDTH - 50)
                asteroid = Asteroid(x, -50, size)
                self.asteroids.add(asteroid)

        if self.hazards_enabled["flares"]:
            self.flare_timer += 1
            if self.flare_timer >= self.flare_rate:
                self.flare_timer = 0
                flare = SolarFlare()
                self.flares.add(flare)

        if self.hazards_enabled["bubbles"]:
            self.bubble_timer += 1
            if self.bubble_timer >= self.bubble_rate:
                self.bubble_timer = 0
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT // 2)
                bubble = WarpBubble(x, y)
                self.bubbles.add(bubble)

        if self.hazards_enabled["nebulae"]:
            self.nebula_timer += 1
            if self.nebula_timer >= self.nebula_rate:
                self.nebula_timer = 0
                x = random.randint(100, SCREEN_WIDTH - 100)
                nebula = NebulaCloud(x, -100)
                self.nebulae.add(nebula)

        if self.hazards_enabled["mines"]:
            self.mine_timer += 1
            if self.mine_timer >= self.mine_rate:
                self.mine_timer = 0
                x = random.randint(50, SCREEN_WIDTH - 50)
                mine = ProximityMine(x, -30)
                self.mines.add(mine)

    def get_asteroid_collisions(self, player_rect):
        """Check asteroid collisions with player"""
        total_damage = 0
        for asteroid in list(self.asteroids):
            if player_rect.colliderect(asteroid.rect):
                total_damage += asteroid.damage
                asteroid.kill()  # Asteroid destroyed on impact
        return total_damage

    def get_flare_damage(self):
        """Get damage from active solar flares"""
        for flare in self.flares:
            if flare.is_damaging():
                return flare.get_damage()
        return 0

    def get_bubble_pull(self, player_x, player_y):
        """Get total pull force from all bubbles"""
        total_x, total_y = 0, 0
        for bubble in self.bubbles:
            fx, fy = bubble.get_pull_force(player_x, player_y)
            total_x += fx
            total_y += fy
        return total_x, total_y

    def get_nebula_slow(self, player_x, player_y):
        """Get speed multiplier from nebula (1.0 = normal, <1.0 = slowed)"""
        for nebula in self.nebulae:
            if nebula.contains_point(player_x, player_y):
                return nebula.slow_factor
        return 1.0

    def get_mine_damage(self, player_x, player_y):
        """Get damage from exploding mines"""
        total_damage = 0
        for mine in self.mines:
            total_damage += mine.get_explosion_damage(player_x, player_y)
        return total_damage

    def draw(self, surface):
        """Draw all hazards"""
        # Draw in order: nebulae (background), then others
        self.nebulae.draw(surface)
        self.bubbles.draw(surface)
        self.asteroids.draw(surface)
        self.mines.draw(surface)
        self.flares.draw(surface)

    def clear(self):
        """Clear all hazards"""
        self.asteroids.empty()
        self.flares.empty()
        self.bubbles.empty()
        self.nebulae.empty()
        self.mines.empty()
