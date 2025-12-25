"""
Minmatar Rebellion - Enhanced Particle Effects
Adds visual polish with trails, sparks, and enhanced explosions
"""

import pygame
import random
import math


class Particle(pygame.sprite.Sprite):
    """A single particle for visual effects"""

    def __init__(self, x, y, color, velocity, size=3, lifetime=30, gravity=0, fade=True):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vx, self.vy = velocity
        self.color = color
        self.size = size
        self.initial_size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.gravity = gravity
        self.fade = fade
        self._update_image()

    def _update_image(self):
        progress = 1 - (self.lifetime / self.max_lifetime)
        if self.fade:
            alpha = int(255 * (1 - progress))
            current_size = max(1, int(self.size * (1 - progress * 0.5)))
        else:
            alpha = 255
            current_size = self.size

        self.image = pygame.Surface((current_size * 2, current_size * 2), pygame.SRCALPHA)
        color_with_alpha = (*self.color[:3], alpha)
        pygame.draw.circle(self.image, color_with_alpha, (current_size, current_size), current_size)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self._update_image()


class TrailParticle(pygame.sprite.Sprite):
    """Fast, simple trail particle"""

    def __init__(self, x, y, color, lifetime=10):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self._update_image()

    def _update_image(self):
        progress = 1 - (self.lifetime / self.max_lifetime)
        alpha = int(150 * (1 - progress))
        size = max(1, int(3 * (1 - progress * 0.7)))

        self.image = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (*self.color[:3], alpha), (size, size), size)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
        else:
            self._update_image()


class ParticleEmitter:
    """Manages particle creation and effects"""

    def __init__(self, particle_group):
        self.particle_group = particle_group

    def emit_explosion(self, x, y, color, count=15, speed=4, size=4):
        """Create an explosion burst of particles"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.5, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lifetime = random.randint(15, 30)
            particle_size = random.randint(2, size)

            # Vary the color slightly
            r = min(255, max(0, color[0] + random.randint(-30, 30)))
            g = min(255, max(0, color[1] + random.randint(-30, 30)))
            b = min(255, max(0, color[2] + random.randint(-30, 30)))

            particle = Particle(x, y, (r, g, b), (vx, vy), particle_size, lifetime)
            self.particle_group.add(particle)

    def emit_sparks(self, x, y, color, count=8, direction=None):
        """Create spark particles, optionally in a specific direction"""
        for _ in range(count):
            if direction:
                # Emit in a cone around the direction
                angle = direction + random.uniform(-0.5, 0.5)
            else:
                angle = random.uniform(0, 2 * math.pi)

            spd = random.uniform(2, 6)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd

            # Bright spark color
            r = min(255, color[0] + random.randint(50, 100))
            g = min(255, color[1] + random.randint(20, 50))
            b = color[2]

            particle = Particle(x, y, (r, g, b), (vx, vy), 2, random.randint(8, 15))
            self.particle_group.add(particle)

    def emit_trail(self, x, y, color):
        """Create a single trail particle"""
        particle = TrailParticle(x, y, color, random.randint(8, 15))
        self.particle_group.add(particle)

    def emit_engine_exhaust(self, x, y, color, direction='down'):
        """Create engine exhaust particles"""
        # Direction offsets
        if direction == 'down':
            angle_base = math.pi / 2  # Pointing down
        elif direction == 'up':
            angle_base = -math.pi / 2
        else:
            angle_base = 0

        for _ in range(2):
            angle = angle_base + random.uniform(-0.3, 0.3)
            spd = random.uniform(1, 3)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd

            # Orange/yellow exhaust
            r = random.randint(200, 255)
            g = random.randint(100, 180)
            b = random.randint(20, 80)

            particle = Particle(x, y, (r, g, b), (vx, vy), 2, random.randint(5, 12))
            self.particle_group.add(particle)

    def emit_shield_hit(self, x, y):
        """Create shield impact effect"""
        color = (100, 150, 255)
        for _ in range(6):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1, 3)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd

            particle = Particle(x, y, color, (vx, vy), 3, random.randint(10, 20))
            self.particle_group.add(particle)

    def emit_armor_hit(self, x, y):
        """Create armor impact effect with debris"""
        color = (200, 150, 100)
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(1, 4)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd

            # Add some gravity for debris feel
            particle = Particle(x, y, color, (vx, vy), random.randint(2, 4),
                                random.randint(15, 25), gravity=0.1)
            self.particle_group.add(particle)

    def emit_hull_hit(self, x, y):
        """Create hull breach effect with sparks and debris"""
        # Debris
        for _ in range(5):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(2, 5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd

            color = (150, 150, 150)
            particle = Particle(x, y, color, (vx, vy), random.randint(2, 5),
                                random.randint(20, 35), gravity=0.15)
            self.particle_group.add(particle)

        # Sparks
        self.emit_sparks(x, y, (255, 200, 100), 6)

    def emit_death_explosion(self, x, y, color, size='medium'):
        """Create a dramatic death explosion"""
        if size == 'small':
            count = 20
            speed = 5
        elif size == 'large':
            count = 50
            speed = 8
        elif size == 'boss':
            count = 100
            speed = 10
        else:  # medium
            count = 35
            speed = 6

        # Main explosion
        self.emit_explosion(x, y, color, count, speed, 5)

        # Secondary ring
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            dist = speed * 2
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist
            self.emit_sparks(px, py, color, 3, angle)

    def emit_berserk_aura(self, x, y, intensity='normal'):
        """Create berserk visual feedback"""
        if intensity == 'extreme':
            color = (255, 50, 50)
            count = 4
        elif intensity == 'close':
            color = (255, 150, 50)
            count = 2
        else:
            return

        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(10, 30)
            px = x + math.cos(angle) * dist
            py = y + math.sin(angle) * dist

            particle = Particle(px, py, color, (0, -0.5), 2, 15)
            self.particle_group.add(particle)


class ScreenEffects:
    """Manages screen-wide visual effects"""

    def __init__(self):
        self.flash_alpha = 0
        self.flash_color = (255, 255, 255)
        self.flash_decay = 10

        self.vignette_intensity = 0
        self.vignette_target = 0

    def flash(self, color=(255, 255, 255), intensity=100):
        """Trigger a screen flash"""
        self.flash_color = color
        self.flash_alpha = intensity

    def set_vignette(self, intensity):
        """Set vignette intensity (0-1)"""
        self.vignette_target = intensity

    def update(self):
        """Update screen effects"""
        # Decay flash
        if self.flash_alpha > 0:
            self.flash_alpha -= self.flash_decay
            self.flash_alpha = max(0, self.flash_alpha)

        # Smooth vignette transition
        diff = self.vignette_target - self.vignette_intensity
        self.vignette_intensity += diff * 0.1

    def draw_flash(self, surface):
        """Draw flash overlay"""
        if self.flash_alpha > 0:
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((*self.flash_color, int(self.flash_alpha)))
            surface.blit(overlay, (0, 0))

    def draw_vignette(self, surface):
        """Draw vignette effect"""
        if self.vignette_intensity < 0.05:
            return

        width, height = surface.get_size()
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw radial gradient vignette
        alpha = int(180 * self.vignette_intensity)
        for i in range(5):
            rect_size = (width - i * 40, height - i * 40)
            rect = pygame.Rect(0, 0, *rect_size)
            rect.center = (width // 2, height // 2)
            alpha_step = alpha // 5 * (5 - i)
            pygame.draw.rect(overlay, (0, 0, 0, alpha_step), rect, 20)

        surface.blit(overlay, (0, 0))
