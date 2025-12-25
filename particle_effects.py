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


class DamageNumber(pygame.sprite.Sprite):
    """Floating damage number that rises and fades"""

    def __init__(self, x, y, damage, color=(255, 255, 255), is_crit=False):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.damage = damage
        self.color = color
        self.is_crit = is_crit
        self.lifetime = 45  # frames
        self.max_lifetime = 45
        self.vy = -2.5  # Rise speed
        self.vx = random.uniform(-0.5, 0.5)  # Slight horizontal drift

        # Create font (cached at class level for performance)
        if not hasattr(DamageNumber, '_font'):
            DamageNumber._font = pygame.font.Font(None, 24)
        if not hasattr(DamageNumber, '_font_crit'):
            DamageNumber._font_crit = pygame.font.Font(None, 32)

        self._update_image()

    def _update_image(self):
        progress = 1 - (self.lifetime / self.max_lifetime)
        alpha = int(255 * (1 - progress))

        # Format damage text
        text = str(self.damage)
        if self.is_crit:
            text = f"{self.damage}!"
            font = DamageNumber._font_crit
        else:
            font = DamageNumber._font

        # Render text
        text_surface = font.render(text, True, self.color)

        # Create surface with alpha
        self.image = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        self.image.blit(text_surface, (0, 0))
        self.image.set_alpha(alpha)

        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        # Float upward with slight deceleration
        self.x += self.vx
        self.y += self.vy
        self.vy *= 0.97  # Slow down rise

        self._update_image()


class DamageNumberManager:
    """Manages floating damage numbers"""

    def __init__(self):
        self.numbers = pygame.sprite.Group()

    def spawn(self, x, y, damage, color=(255, 255, 255), is_crit=False):
        """Spawn a new damage number"""
        # Slight random offset to prevent stacking
        x += random.randint(-10, 10)
        y += random.randint(-5, 5)
        num = DamageNumber(x, y, damage, color, is_crit)
        self.numbers.add(num)

    def update(self):
        self.numbers.update()

    def draw(self, surface):
        self.numbers.draw(surface)

    def clear(self):
        self.numbers.empty()


class WarpTransition:
    """Hyperspace warp effect for stage transitions"""

    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.active = False
        self.phase = 'idle'  # idle, warp_in, hold, warp_out
        self.timer = 0
        self.max_timer = 0
        self.stars = []
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2

    def start(self, duration=90):
        """Start warp transition"""
        self.active = True
        self.phase = 'warp_in'
        self.timer = 0
        self.max_timer = duration // 3  # Each phase gets 1/3 of duration
        self._generate_warp_stars()

    def _generate_warp_stars(self):
        """Generate star streaks for warp effect"""
        self.stars = []
        for _ in range(80):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, max(self.width, self.height))
            speed = random.uniform(5, 15)
            length = random.uniform(20, 100)
            brightness = random.randint(150, 255)
            self.stars.append({
                'angle': angle,
                'distance': distance,
                'speed': speed,
                'length': length,
                'brightness': brightness
            })

    def update(self):
        """Update warp effect"""
        if not self.active:
            return False

        self.timer += 1

        if self.phase == 'warp_in':
            # Stars accelerate toward center
            for star in self.stars:
                star['distance'] -= star['speed'] * (self.timer / self.max_timer)
                star['length'] += 2

            if self.timer >= self.max_timer:
                self.phase = 'hold'
                self.timer = 0

        elif self.phase == 'hold':
            # Bright flash at center
            if self.timer >= self.max_timer // 2:
                self.phase = 'warp_out'
                self.timer = 0
                self._generate_warp_stars()

        elif self.phase == 'warp_out':
            # Stars streak outward
            for star in self.stars:
                star['distance'] += star['speed'] * 2
                star['length'] = max(10, star['length'] - 1)

            if self.timer >= self.max_timer:
                self.active = False
                self.phase = 'idle'
                return True  # Transition complete

        return False

    def draw(self, surface):
        """Draw warp effect"""
        if not self.active:
            return

        # Create overlay surface
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.phase == 'warp_in':
            # Draw streaking stars toward center
            progress = self.timer / self.max_timer
            for star in self.stars:
                if star['distance'] > 0:
                    # Calculate start and end points
                    x1 = self.center_x + math.cos(star['angle']) * star['distance']
                    y1 = self.center_y + math.sin(star['angle']) * star['distance']
                    x2 = self.center_x + math.cos(star['angle']) * (star['distance'] + star['length'])
                    y2 = self.center_y + math.sin(star['angle']) * (star['distance'] + star['length'])

                    alpha = int(star['brightness'] * progress)
                    color = (star['brightness'], star['brightness'], 255, alpha)
                    pygame.draw.line(overlay, color, (int(x1), int(y1)), (int(x2), int(y2)), 2)

            # Vignette darkening
            dark_alpha = int(100 * progress)
            pygame.draw.rect(overlay, (0, 0, 0, dark_alpha), (0, 0, self.width, self.height))

        elif self.phase == 'hold':
            # Bright flash
            progress = 1 - abs(self.timer / (self.max_timer // 2) - 1)
            flash_alpha = int(255 * progress)
            overlay.fill((255, 255, 255, flash_alpha))

        elif self.phase == 'warp_out':
            # Stars streak outward
            progress = self.timer / self.max_timer
            fade = 1 - progress

            for star in self.stars:
                x1 = self.center_x + math.cos(star['angle']) * star['distance']
                y1 = self.center_y + math.sin(star['angle']) * star['distance']
                x2 = self.center_x + math.cos(star['angle']) * (star['distance'] - star['length'])
                y2 = self.center_y + math.sin(star['angle']) * (star['distance'] - star['length'])

                alpha = int(star['brightness'] * fade)
                color = (star['brightness'], star['brightness'], 255, alpha)
                pygame.draw.line(overlay, color, (int(x1), int(y1)), (int(x2), int(y2)), 2)

        surface.blit(overlay, (0, 0))

    @property
    def is_active(self):
        return self.active


class HitMarker:
    """Brief crosshair flash when bullets connect"""

    def __init__(self):
        self.markers = []

    def add(self, x, y, is_crit=False):
        """Add a hit marker at position"""
        self.markers.append({
            'x': x,
            'y': y,
            'timer': 8 if not is_crit else 12,
            'size': 6 if not is_crit else 10,
            'is_crit': is_crit
        })

    def update(self):
        """Update all markers"""
        self.markers = [m for m in self.markers if m['timer'] > 0]
        for marker in self.markers:
            marker['timer'] -= 1

    def draw(self, surface):
        """Draw all active markers"""
        for marker in self.markers:
            alpha = int(255 * (marker['timer'] / (12 if marker['is_crit'] else 8)))
            size = marker['size']
            x, y = int(marker['x']), int(marker['y'])

            if marker['is_crit']:
                color = (255, 255, 100, alpha)
            else:
                color = (255, 255, 255, alpha)

            # Draw X shape
            overlay = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
            cx, cy = size * 2, size * 2

            # Diagonal lines
            pygame.draw.line(overlay, color, (cx - size, cy - size), (cx + size, cy + size), 2)
            pygame.draw.line(overlay, color, (cx + size, cy - size), (cx - size, cy + size), 2)

            surface.blit(overlay, (x - size * 2, y - size * 2))

    def clear(self):
        self.markers = []


class ComboEffects:
    """Visual effects for combo system"""

    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.pulse_intensity = 0
        self.combo_scale = 1.0
        self.target_scale = 1.0
        self.last_combo = 0
        self.shake_offset = (0, 0)

    def trigger(self, combo_count):
        """Trigger effects based on combo count"""
        if combo_count > self.last_combo:
            # Combo increased - trigger effects
            if combo_count >= 10:
                self.pulse_intensity = min(0.3, combo_count * 0.02)
                self.target_scale = min(2.0, 1.0 + combo_count * 0.05)

                # Screen shake for big combos
                if combo_count >= 20:
                    shake = min(8, combo_count // 5)
                    self.shake_offset = (
                        random.randint(-shake, shake),
                        random.randint(-shake, shake)
                    )

        self.last_combo = combo_count

    def update(self):
        """Update combo effects"""
        # Decay pulse
        self.pulse_intensity *= 0.95
        if self.pulse_intensity < 0.01:
            self.pulse_intensity = 0

        # Smooth scale transition
        self.combo_scale += (self.target_scale - self.combo_scale) * 0.1
        self.target_scale += (1.0 - self.target_scale) * 0.05

        # Decay shake
        self.shake_offset = (
            int(self.shake_offset[0] * 0.8),
            int(self.shake_offset[1] * 0.8)
        )

    def draw_pulse(self, surface):
        """Draw screen pulse effect"""
        if self.pulse_intensity > 0.01:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            # Red/orange pulse from edges
            alpha = int(self.pulse_intensity * 100)
            for i in range(3):
                border = 30 + i * 20
                rect = pygame.Rect(border, border, self.width - border * 2, self.height - border * 2)
                pygame.draw.rect(overlay, (255, 100, 50, alpha // (i + 1)), rect, 10 - i * 3)
            surface.blit(overlay, (0, 0))

    def get_combo_scale(self):
        """Get current scale for combo text"""
        return self.combo_scale

    def get_shake_offset(self):
        """Get current shake offset"""
        return self.shake_offset
