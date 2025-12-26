"""
Visual Effects Module for EVE Rebellion
Screen-space effects, particle systems, and post-processing.
"""

import pygame
import math
import random
from typing import List, Tuple, Optional

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# Faction colors
MINMATAR_ENGINE = (255, 120, 40)    # Orange/rust
AMARR_ENGINE = (255, 200, 80)       # Golden
SHIELD_COLOR = (80, 160, 255)       # Blue
ARMOR_COLOR = (255, 140, 40)        # Orange
HULL_COLOR = (200, 80, 40)          # Red/brown


class Particle:
    """Single particle with physics"""
    __slots__ = ['x', 'y', 'vx', 'vy', 'life', 'max_life', 'color', 'size',
                 'gravity', 'drag', 'fade', 'shrink']

    def __init__(self, x, y, vx, vy, life, color, size,
                 gravity=0, drag=0.98, fade=True, shrink=True):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.drag = drag
        self.fade = fade
        self.shrink = shrink

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.life -= 1
        return self.life > 0

    def get_alpha(self):
        if self.fade:
            return int(255 * (self.life / self.max_life))
        return 255

    def get_size(self):
        if self.shrink:
            return max(1, int(self.size * (self.life / self.max_life)))
        return self.size


class ParticleSystem:
    """Manages multiple particle emitters and effects"""

    def __init__(self, max_particles=2000):
        self.particles: List[Particle] = []
        self.max_particles = max_particles

    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surface):
        """Draw all particles"""
        for p in self.particles:
            alpha = p.get_alpha()
            size = p.get_size()
            if size > 0 and alpha > 0:
                color = (*p.color[:3], alpha)
                if size <= 2:
                    # Small particles - just pixels
                    try:
                        surface.set_at((int(p.x), int(p.y)), color[:3])
                    except IndexError:
                        pass
                else:
                    # Larger particles - circles with glow
                    self._draw_glowing_particle(surface, int(p.x), int(p.y), size, color)

    def _draw_glowing_particle(self, surface, x, y, size, color):
        """Draw a particle with glow effect"""
        # Create particle surface
        psize = size * 3
        psurf = pygame.Surface((psize, psize), pygame.SRCALPHA)
        center = psize // 2

        # Outer glow
        for r in range(size + 2, size - 1, -1):
            glow_alpha = int(color[3] * 0.3 * (1 - (r - size) / 3))
            if glow_alpha > 0:
                pygame.draw.circle(psurf, (*color[:3], glow_alpha), (center, center), r)

        # Core
        pygame.draw.circle(psurf, color, (center, center), max(1, size - 1))

        surface.blit(psurf, (x - center, y - center), special_flags=pygame.BLEND_RGBA_ADD)

    def emit_engine_trail(self, x, y, faction='minmatar', intensity=1.0):
        """Emit engine trail particles"""
        if len(self.particles) >= self.max_particles:
            return

        color = MINMATAR_ENGINE if faction == 'minmatar' else AMARR_ENGINE

        for _ in range(int(3 * intensity)):
            # Spread and velocity
            spread = random.uniform(-3, 3)
            speed = random.uniform(1, 3)

            # Color variation
            var = random.randint(-20, 20)
            pcolor = (min(255, max(0, color[0] + var)),
                     min(255, max(0, color[1] + var)),
                     min(255, max(0, color[2] + var)))

            p = Particle(
                x + spread, y,
                spread * 0.3, speed,
                life=random.randint(10, 20),
                color=pcolor,
                size=random.randint(2, 4),
                drag=0.95
            )
            self.particles.append(p)

    def emit_shield_impact(self, x, y, radius=30):
        """Emit shield impact ripple effect"""
        if len(self.particles) >= self.max_particles:
            return

        # Ring of particles expanding outward
        num_particles = 16
        for i in range(num_particles):
            angle = (i / num_particles) * math.pi * 2
            speed = random.uniform(2, 4)

            # Blue with white core
            if random.random() < 0.3:
                color = (200, 230, 255)  # White-ish
            else:
                color = SHIELD_COLOR

            p = Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life=random.randint(15, 25),
                color=color,
                size=random.randint(2, 4),
                drag=0.92
            )
            self.particles.append(p)

    def emit_armor_sparks(self, x, y, count=10):
        """Emit orange sparks for armor hits"""
        if len(self.particles) >= self.max_particles:
            return

        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)

            # Orange/yellow sparks
            color = (255, random.randint(100, 200), random.randint(20, 60))

            p = Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life=random.randint(10, 25),
                color=color,
                size=random.randint(1, 3),
                gravity=0.1,
                drag=0.96
            )
            self.particles.append(p)

    def emit_hull_damage(self, x, y, count=15):
        """Emit debris and fire for hull damage"""
        if len(self.particles) >= self.max_particles:
            return

        # Debris
        for _ in range(count // 2):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)

            # Gray/brown debris
            gray = random.randint(40, 80)
            color = (gray + 20, gray, gray - 10)

            p = Particle(
                x + random.randint(-5, 5),
                y + random.randint(-5, 5),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life=random.randint(20, 40),
                color=color,
                size=random.randint(2, 5),
                gravity=0.15,
                drag=0.97
            )
            self.particles.append(p)

        # Fire
        for _ in range(count // 2):
            # Fire rises
            color = (255, random.randint(60, 150), random.randint(10, 40))

            p = Particle(
                x + random.randint(-8, 8),
                y + random.randint(-8, 8),
                random.uniform(-1, 1),
                random.uniform(-2, -0.5),
                life=random.randint(15, 30),
                color=color,
                size=random.randint(3, 6),
                gravity=-0.05,  # Fire rises
                drag=0.95
            )
            self.particles.append(p)

    def emit_muzzle_flash(self, x, y, angle=0, spread=30):
        """Emit muzzle flash for autocannons"""
        if len(self.particles) >= self.max_particles:
            return

        # Flash particles in firing direction
        for _ in range(5):
            # Cone in firing direction
            flash_angle = angle + math.radians(random.uniform(-spread/2, spread/2))
            speed = random.uniform(4, 8)

            # Yellow/white flash
            color = (255, 255, random.randint(150, 255))

            p = Particle(
                x, y,
                math.cos(flash_angle) * speed,
                math.sin(flash_angle) * speed,
                life=random.randint(3, 6),
                color=color,
                size=random.randint(2, 4),
                fade=True,
                shrink=False
            )
            self.particles.append(p)

    def emit_missile_trail(self, x, y, vx, vy):
        """Emit smoke trail for missiles"""
        if len(self.particles) >= self.max_particles:
            return

        # Smoke particles behind missile
        for _ in range(2):
            # Gray smoke
            gray = random.randint(80, 140)
            color = (gray, gray, gray)

            p = Particle(
                x + random.uniform(-2, 2),
                y + random.uniform(-2, 2),
                -vx * 0.1 + random.uniform(-0.5, 0.5),
                -vy * 0.1 + random.uniform(-0.5, 0.5),
                life=random.randint(15, 30),
                color=color,
                size=random.randint(3, 6),
                drag=0.98,
                gravity=-0.02
            )
            self.particles.append(p)

    def emit_explosion(self, x, y, radius=30, color=None):
        """Emit explosion particles"""
        if len(self.particles) >= self.max_particles:
            return

        count = int(radius * 1.5)

        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, radius / 5)

            if color is None:
                # Fire colors
                c = random.choice([
                    (255, 200, 50),   # Yellow
                    (255, 150, 30),   # Orange
                    (255, 80, 20),    # Red-orange
                    (200, 200, 200),  # Smoke
                ])
            else:
                c = color

            p = Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                life=random.randint(15, 35),
                color=c,
                size=random.randint(2, 6),
                gravity=0.05,
                drag=0.95
            )
            self.particles.append(p)

    def clear(self):
        """Clear all particles"""
        self.particles.clear()


class WarpEffect:
    """Warp-in/warp-out effect for boss entrances"""

    def __init__(self, x, y, warp_in=True, duration=60):
        self.x = x
        self.y = y
        self.warp_in = warp_in
        self.duration = duration
        self.timer = duration
        self.active = True
        self.particles = []

    def update(self):
        if not self.active:
            return False

        self.timer -= 1
        progress = 1.0 - (self.timer / self.duration)

        # Spawn warp particles
        if self.timer > 10:
            num = int(5 * (1 - progress) if self.warp_in else 5 * progress)
            for _ in range(num):
                angle = random.uniform(0, math.pi * 2)
                dist = random.uniform(50, 150) * (1 - progress if self.warp_in else progress)

                px = self.x + math.cos(angle) * dist
                py = self.y + math.sin(angle) * dist

                # Move toward/away from center
                speed = random.uniform(2, 5)
                if self.warp_in:
                    vx = (self.x - px) / dist * speed
                    vy = (self.y - py) / dist * speed
                else:
                    vx = (px - self.x) / dist * speed
                    vy = (py - self.y) / dist * speed

                self.particles.append({
                    'x': px, 'y': py, 'vx': vx, 'vy': vy,
                    'life': random.randint(10, 20),
                    'color': (100, 150, 255) if random.random() < 0.7 else (200, 220, 255)
                })

        # Update particles
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

        if self.timer <= 0:
            self.active = False

        return self.active

    def draw(self, surface):
        if not self.active:
            return

        progress = 1.0 - (self.timer / self.duration)

        # Central flash
        if self.warp_in:
            flash_size = int(100 * progress)
            flash_alpha = int(200 * (1 - progress))
        else:
            flash_size = int(100 * (1 - progress))
            flash_alpha = int(200 * progress)

        if flash_size > 0 and flash_alpha > 0:
            flash = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            for r in range(flash_size, 0, -2):
                alpha = int(flash_alpha * (r / flash_size) * 0.5)
                pygame.draw.circle(flash, (100, 150, 255, alpha),
                                 (flash_size, flash_size), r)
            surface.blit(flash, (self.x - flash_size, self.y - flash_size),
                        special_flags=pygame.BLEND_RGBA_ADD)

        # Draw particles
        for p in self.particles:
            alpha = int(255 * (p['life'] / 20))
            psurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (*p['color'], alpha), (3, 3), 3)
            surface.blit(psurf, (int(p['x']) - 3, int(p['y']) - 3),
                        special_flags=pygame.BLEND_RGBA_ADD)


class ScreenEffects:
    """Screen-space post-processing effects"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.bloom_enabled = NUMPY_AVAILABLE
        self.bloom_threshold = 200
        self.bloom_intensity = 0.3

    def apply_bloom(self, surface):
        """Apply bloom effect to bright areas"""
        if not self.bloom_enabled:
            return surface

        try:
            # Get pixel array
            arr = pygame.surfarray.array3d(surface)

            # Find bright pixels
            brightness = np.max(arr, axis=2)
            bright_mask = brightness > self.bloom_threshold

            if not np.any(bright_mask):
                return surface

            # Create bloom layer
            bloom = np.zeros_like(arr, dtype=np.float32)
            bloom[bright_mask] = arr[bright_mask]

            # Simple box blur (3x3)
            kernel_size = 3
            blurred = np.zeros_like(bloom)
            for i in range(-kernel_size//2, kernel_size//2 + 1):
                for j in range(-kernel_size//2, kernel_size//2 + 1):
                    shifted = np.roll(np.roll(bloom, i, axis=0), j, axis=1)
                    blurred += shifted
            blurred /= (kernel_size * kernel_size)

            # Combine with original
            result = arr.astype(np.float32) + blurred * self.bloom_intensity
            result = np.clip(result, 0, 255).astype(np.uint8)

            # Create new surface
            return pygame.surfarray.make_surface(result)
        except Exception:
            return surface

    def draw_laser_glow(self, surface, x1, y1, x2, y2, color, width=2):
        """Draw laser beam with glow"""
        # Core beam
        pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)

        # Glow layers
        glow_color = (min(color[0] + 50, 255),
                     min(color[1] + 50, 255),
                     min(color[2] + 50, 255))

        for i in range(3):
            glow_width = width + (i + 1) * 2
            alpha = 100 - i * 30

            glow_surf = pygame.Surface((abs(x2-x1) + glow_width * 2,
                                       abs(y2-y1) + glow_width * 2), pygame.SRCALPHA)

            # Offset for surface
            ox = min(x1, x2) - glow_width
            oy = min(y1, y2) - glow_width

            pygame.draw.line(glow_surf, (*glow_color, alpha),
                           (x1 - ox, y1 - oy), (x2 - ox, y2 - oy), glow_width)

            surface.blit(glow_surf, (ox, oy), special_flags=pygame.BLEND_RGBA_ADD)


# Convenience functions for visual enhancements
def add_ship_glow(surface, color, intensity=0.5):
    """Add glow effect around a ship sprite"""
    w, h = surface.get_size()
    result = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)

    # Draw glow
    for offset in range(5, 0, -1):
        alpha = int(60 * intensity * (1 - offset / 5))
        glow = pygame.Surface((w + offset * 2, h + offset * 2), pygame.SRCALPHA)
        glow.blit(surface, (offset, offset))
        glow.fill((*color, alpha), special_flags=pygame.BLEND_RGBA_MULT)
        result.blit(glow, (5 - offset, 5 - offset), special_flags=pygame.BLEND_RGBA_ADD)

    # Draw original on top
    result.blit(surface, (5, 5))
    return result


def add_colored_tint(surface, color, intensity=0.3):
    """Add color tint to a surface"""
    result = surface.copy()
    tint = pygame.Surface(result.get_size(), pygame.SRCALPHA)
    tint.fill((*color, int(255 * intensity)))
    result.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return result


def add_outline(surface, color, thickness=1):
    """Add outline to a sprite"""
    w, h = surface.get_size()
    result = pygame.Surface((w + thickness * 2, h + thickness * 2), pygame.SRCALPHA)

    # Draw offset copies for outline
    mask = pygame.mask.from_surface(surface)
    outline_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))

    for dx in range(-thickness, thickness + 1):
        for dy in range(-thickness, thickness + 1):
            if dx != 0 or dy != 0:
                result.blit(outline_surf, (thickness + dx, thickness + dy))

    # Draw original on top
    result.blit(surface, (thickness, thickness))
    return result


def add_strong_outline(surface, color, thickness=2):
    """Add stronger outline effect"""
    return add_outline(surface, color, thickness)


# ============================================================================
# SHIP DAMAGE VISUAL EFFECTS
# ============================================================================

class ShipDamageEffects:
    """
    Manages visual damage effects for a ship based on shield/armor/hull state.
    - Shield down: Electrical sparks, blue flickering
    - Armor damaged: Orange sparks, small smoke puffs
    - Hull critical: Fire, heavy smoke, trailing flames
    """

    def __init__(self):
        self.particles: List[dict] = []
        self.max_particles = 50
        self.spark_timer = 0
        self.smoke_timer = 0
        self.fire_timer = 0

    def update(self, x: float, y: float, width: int, height: int,
               shield_pct: float, armor_pct: float, hull_pct: float):
        """Update damage effects based on ship state"""
        # Update existing particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += p.get('gravity', 0)
            p['vx'] *= p.get('drag', 0.98)
            p['vy'] *= p.get('drag', 0.98)
            p['life'] -= 1

        # Remove dead particles
        self.particles = [p for p in self.particles if p['life'] > 0]

        # Spawn new effects based on damage state
        self.spark_timer += 1
        self.smoke_timer += 1
        self.fire_timer += 1

        # === SHIELDS DOWN: Electrical sparks ===
        if shield_pct <= 0 and armor_pct > 0:
            if self.spark_timer >= 8 and len(self.particles) < self.max_particles:
                self.spark_timer = 0
                # Random position on ship
                px = x + random.randint(-width // 3, width // 3)
                py = y + random.randint(-height // 3, height // 3)
                self._spawn_electrical_spark(px, py)

        # === ARMOR DAMAGED: Smoke and orange sparks ===
        if armor_pct < 0.5 and armor_pct > 0:
            intensity = 1.0 - (armor_pct / 0.5)
            if self.smoke_timer >= int(12 - intensity * 8) and len(self.particles) < self.max_particles:
                self.smoke_timer = 0
                px = x + random.randint(-width // 4, width // 4)
                py = y + random.randint(-height // 4, height // 4)
                self._spawn_armor_smoke(px, py, intensity)

                if random.random() < 0.4:
                    self._spawn_armor_spark(px, py)

        # === ARMOR GONE: Sparks from exposed hull ===
        if armor_pct <= 0 and hull_pct > 0.25:
            if self.spark_timer >= 6 and len(self.particles) < self.max_particles:
                self.spark_timer = 0
                px = x + random.randint(-width // 3, width // 3)
                py = y + random.randint(-height // 3, height // 3)
                self._spawn_hull_spark(px, py)

        # === HULL CRITICAL: Fire and heavy smoke ===
        if hull_pct <= 0.25 and hull_pct > 0:
            intensity = 1.0 - (hull_pct / 0.25)
            if self.fire_timer >= int(4 - intensity * 2) and len(self.particles) < self.max_particles:
                self.fire_timer = 0
                # Fire from multiple points
                for _ in range(1 + int(intensity * 2)):
                    px = x + random.randint(-width // 3, width // 3)
                    py = y + random.randint(-height // 4, height // 4)
                    self._spawn_fire(px, py, intensity)

                # Heavy smoke trail
                if random.random() < 0.6:
                    px = x + random.randint(-width // 4, width // 4)
                    py = y + height // 4
                    self._spawn_heavy_smoke(px, py)

    def _spawn_electrical_spark(self, x: float, y: float):
        """Blue electrical spark"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        self.particles.append({
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': random.randint(5, 12),
            'max_life': 12,
            'size': random.randint(2, 4),
            'type': 'spark',
            'color': (100, 180, 255),
            'gravity': 0,
            'drag': 0.9
        })

    def _spawn_armor_smoke(self, x: float, y: float, intensity: float):
        """Gray/brown smoke puff"""
        self.particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(-1.5, -0.5),
            'life': random.randint(20, 35),
            'max_life': 35,
            'size': int(4 + intensity * 6),
            'type': 'smoke',
            'color': (80, 70, 60),
            'gravity': -0.02,
            'drag': 0.98
        })

    def _spawn_armor_spark(self, x: float, y: float):
        """Orange armor spark"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 4)
        self.particles.append({
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': random.randint(8, 15),
            'max_life': 15,
            'size': random.randint(2, 3),
            'type': 'spark',
            'color': (255, 150, 50),
            'gravity': 0.1,
            'drag': 0.95
        })

    def _spawn_hull_spark(self, x: float, y: float):
        """Red/orange hull damage spark"""
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1.5, 3.5)
        self.particles.append({
            'x': x, 'y': y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': random.randint(6, 12),
            'max_life': 12,
            'size': random.randint(2, 4),
            'type': 'spark',
            'color': (255, 100, 50),
            'gravity': 0.15,
            'drag': 0.92
        })

    def _spawn_fire(self, x: float, y: float, intensity: float):
        """Fire particle"""
        self.particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-0.8, 0.8),
            'vy': random.uniform(-2.5, -1.0),
            'life': random.randint(12, 25),
            'max_life': 25,
            'size': int(5 + intensity * 8),
            'type': 'fire',
            'color': (255, 100, 30),
            'gravity': -0.05,
            'drag': 0.97
        })

    def _spawn_heavy_smoke(self, x: float, y: float):
        """Heavy black smoke trail"""
        self.particles.append({
            'x': x, 'y': y,
            'vx': random.uniform(-0.3, 0.3),
            'vy': random.uniform(0.5, 1.5),  # Trails behind
            'life': random.randint(30, 50),
            'max_life': 50,
            'size': random.randint(8, 15),
            'type': 'smoke',
            'color': (40, 35, 30),
            'gravity': 0,
            'drag': 0.99
        })

    def draw(self, surface: pygame.Surface):
        """Draw all damage particles"""
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            size = max(1, int(p['size'] * (p['life'] / p['max_life'])))

            if p['type'] == 'spark':
                # Bright spark with glow
                if size > 1:
                    glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    glow_color = (*p['color'], alpha // 3)
                    pygame.draw.circle(glow_surf, glow_color, (size * 2, size * 2), size * 2)
                    surface.blit(glow_surf, (int(p['x']) - size * 2, int(p['y']) - size * 2))

                spark_color = (min(255, p['color'][0] + 50),
                              min(255, p['color'][1] + 50),
                              min(255, p['color'][2] + 50))
                pygame.draw.circle(surface, spark_color, (int(p['x']), int(p['y'])), size)

            elif p['type'] == 'smoke':
                # Soft smoke puff
                smoke_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                smoke_color = (*p['color'], alpha // 2)
                pygame.draw.circle(smoke_surf, smoke_color, (size, size), size)
                surface.blit(smoke_surf, (int(p['x']) - size, int(p['y']) - size))

            elif p['type'] == 'fire':
                # Layered fire effect
                progress = p['life'] / p['max_life']

                # Outer orange
                fire_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
                outer_color = (255, 80 + int(80 * progress), 20, alpha // 2)
                pygame.draw.circle(fire_surf, outer_color, (size * 1.5, size * 1.5), size)

                # Inner yellow
                inner_size = int(size * 0.6)
                inner_color = (255, 180 + int(75 * progress), 50, alpha)
                pygame.draw.circle(fire_surf, inner_color,
                                 (int(size * 1.5), int(size * 1.5)), inner_size)

                # Core white
                core_size = max(1, int(size * 0.3))
                core_color = (255, 255, 200, alpha)
                pygame.draw.circle(fire_surf, core_color,
                                 (int(size * 1.5), int(size * 1.5)), core_size)

                surface.blit(fire_surf, (int(p['x']) - int(size * 1.5),
                                        int(p['y']) - int(size * 1.5)))


class EnhancedExplosion:
    """
    More dramatic explosion with multiple phases:
    - Initial flash
    - Expanding shockwave
    - Fire ball with internal structure
    - Flying debris
    - Secondary explosions (for large ships)
    - Lingering smoke
    """

    def __init__(self, x: float, y: float, size: int = 30,
                 color: Tuple[int, int, int] = (255, 150, 50),
                 has_secondaries: bool = False):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.has_secondaries = has_secondaries

        self.frame = 0
        self.max_frames = 35 + (15 if has_secondaries else 0)
        self.alive = True

        # Debris
        self.debris = []
        num_debris = min(20, size // 3 + 5)
        for _ in range(num_debris):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8) * (size / 30)
            self.debris.append({
                'x': 0, 'y': 0,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.randint(2, max(4, size // 6)),
                'life': random.randint(20, 35),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-10, 10),
                'is_hull': random.random() < 0.3  # Some debris is hull plating
            })

        # Secondary explosions (for big ships)
        self.secondaries = []
        if has_secondaries:
            num_secondary = random.randint(2, 4)
            for _ in range(num_secondary):
                self.secondaries.append({
                    'x': random.randint(-size, size),
                    'y': random.randint(-size, size),
                    'delay': random.randint(10, 25),
                    'size': random.randint(size // 3, size // 2),
                    'triggered': False
                })

    def update(self) -> bool:
        """Update explosion, return False when done"""
        self.frame += 1

        # Update debris
        for d in self.debris:
            if d['life'] > 0:
                d['x'] += d['vx']
                d['y'] += d['vy']
                d['vy'] += 0.2  # Gravity
                d['vx'] *= 0.98
                d['rotation'] += d['rot_speed']
                d['life'] -= 1

        # Trigger secondary explosions
        for s in self.secondaries:
            if not s['triggered'] and self.frame >= s['delay']:
                s['triggered'] = True
                s['frame'] = 0
            elif s['triggered']:
                s['frame'] += 1

        if self.frame >= self.max_frames:
            self.alive = False
            return False
        return True

    def draw(self, surface: pygame.Surface):
        """Draw the explosion"""
        progress = self.frame / self.max_frames

        # === INITIAL FLASH (first few frames) ===
        if self.frame < 4:
            flash_alpha = int(200 * (1 - self.frame / 4))
            flash_size = int(self.size * 2 * (1 + self.frame * 0.3))
            flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(flash_surf, (255, 255, 255, flash_alpha),
                             (flash_size, flash_size), flash_size)
            surface.blit(flash_surf, (int(self.x) - flash_size, int(self.y) - flash_size))

        # === SHOCKWAVE RING ===
        if progress < 0.5:
            ring_progress = progress / 0.5
            ring_radius = int(self.size * (0.5 + ring_progress * 2))
            ring_alpha = int(150 * (1 - ring_progress))
            ring_width = max(2, int(6 * (1 - ring_progress)))

            ring_surf = pygame.Surface((ring_radius * 2 + 10, ring_radius * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (255, 255, 255, ring_alpha),
                             (ring_radius + 5, ring_radius + 5), ring_radius, ring_width)
            surface.blit(ring_surf, (int(self.x) - ring_radius - 5, int(self.y) - ring_radius - 5))

        # === MAIN FIREBALL ===
        if progress < 0.7:
            fire_progress = min(1.0, progress / 0.4)
            fireball_size = int(self.size * (0.5 + fire_progress * 1.2) * (1 - progress * 0.5))

            # Outer fire (red/orange)
            outer_alpha = int(200 * (1 - progress / 0.7))
            for _ in range(3):
                ox = random.randint(-4, 4)
                oy = random.randint(-4, 4)
                outer_size = fireball_size + random.randint(-3, 3)
                fire_surf = pygame.Surface((outer_size * 2 + 10, outer_size * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(fire_surf, (255, 80, 20, outer_alpha // 2),
                                 (outer_size + 5, outer_size + 5), outer_size)
                surface.blit(fire_surf, (int(self.x) + ox - outer_size - 5,
                                        int(self.y) + oy - outer_size - 5))

            # Middle fire (orange)
            mid_size = int(fireball_size * 0.75)
            mid_surf = pygame.Surface((mid_size * 2 + 10, mid_size * 2 + 10), pygame.SRCALPHA)
            pygame.draw.circle(mid_surf, (255, 150, 30, outer_alpha),
                             (mid_size + 5, mid_size + 5), mid_size)
            surface.blit(mid_surf, (int(self.x) - mid_size - 5, int(self.y) - mid_size - 5))

            # Inner core (yellow/white)
            if progress < 0.4:
                core_alpha = int(255 * (1 - progress / 0.4))
                core_size = int(fireball_size * 0.4)
                core_surf = pygame.Surface((core_size * 2 + 10, core_size * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(core_surf, (255, 255, 150, core_alpha),
                                 (core_size + 5, core_size + 5), core_size)
                pygame.draw.circle(core_surf, (255, 255, 255, core_alpha),
                                 (core_size + 5, core_size + 5), core_size // 2)
                surface.blit(core_surf, (int(self.x) - core_size - 5, int(self.y) - core_size - 5))

        # === DEBRIS ===
        for d in self.debris:
            if d['life'] > 0:
                debris_alpha = int(255 * (d['life'] / 35))
                dx = int(self.x + d['x'])
                dy = int(self.y + d['y'])

                if d['is_hull']:
                    # Hull debris - metallic gray chunks
                    debris_size = d['size']
                    debris_surf = pygame.Surface((debris_size * 3, debris_size * 3), pygame.SRCALPHA)
                    points = [
                        (debris_size * 1.5, debris_size * 0.5),
                        (debris_size * 2.5, debris_size * 1.5),
                        (debris_size * 1.5, debris_size * 2.5),
                        (debris_size * 0.5, debris_size * 1.5),
                    ]
                    pygame.draw.polygon(debris_surf, (100, 90, 80, debris_alpha), points)
                    rotated = pygame.transform.rotate(debris_surf, d['rotation'])
                    surface.blit(rotated, (dx - rotated.get_width() // 2,
                                          dy - rotated.get_height() // 2))
                else:
                    # Hot debris with glow
                    glow_surf = pygame.Surface((d['size'] * 4, d['size'] * 4), pygame.SRCALPHA)
                    pygame.draw.circle(glow_surf, (255, 150, 50, debris_alpha // 3),
                                     (d['size'] * 2, d['size'] * 2), d['size'] * 2)
                    pygame.draw.circle(glow_surf, (255, 200, 100, debris_alpha),
                                     (d['size'] * 2, d['size'] * 2), d['size'])
                    surface.blit(glow_surf, (dx - d['size'] * 2, dy - d['size'] * 2))

        # === SMOKE (late phase) ===
        if progress > 0.3:
            smoke_progress = (progress - 0.3) / 0.7
            smoke_alpha = int(80 * (1 - smoke_progress))
            smoke_size = int(self.size * (0.8 + smoke_progress * 0.8))

            for i in range(3):
                sx = int(self.x + random.randint(-10, 10))
                sy = int(self.y + random.randint(-10, 10) - smoke_progress * 20)
                smoke_surf = pygame.Surface((smoke_size * 2, smoke_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surf, (60, 50, 45, smoke_alpha),
                                 (smoke_size, smoke_size), smoke_size)
                surface.blit(smoke_surf, (sx - smoke_size, sy - smoke_size))

        # === SECONDARY EXPLOSIONS ===
        for s in self.secondaries:
            if s['triggered'] and s.get('frame', 0) < 20:
                sec_progress = s['frame'] / 20
                sec_size = int(s['size'] * (1 - sec_progress * 0.5))
                sec_alpha = int(200 * (1 - sec_progress))

                sec_x = int(self.x + s['x'])
                sec_y = int(self.y + s['y'])

                # Secondary fireball
                sec_surf = pygame.Surface((sec_size * 2 + 10, sec_size * 2 + 10), pygame.SRCALPHA)
                pygame.draw.circle(sec_surf, (255, 120, 30, sec_alpha),
                                 (sec_size + 5, sec_size + 5), sec_size)
                pygame.draw.circle(sec_surf, (255, 200, 100, sec_alpha),
                                 (sec_size + 5, sec_size + 5), sec_size // 2)
                surface.blit(sec_surf, (sec_x - sec_size - 5, sec_y - sec_size - 5))


# Global effect instances
_particle_system = None
_screen_effects = None
_ship_damage_effects = {}


def get_particle_system():
    """Get global particle system"""
    global _particle_system
    if _particle_system is None:
        _particle_system = ParticleSystem()
    return _particle_system


def get_screen_effects(width=None, height=None):
    """Get global screen effects processor"""
    global _screen_effects
    if _screen_effects is None and width and height:
        _screen_effects = ScreenEffects(width, height)
    return _screen_effects


def get_ship_damage_effects(ship_id: int) -> ShipDamageEffects:
    """Get or create damage effects for a specific ship"""
    global _ship_damage_effects
    if ship_id not in _ship_damage_effects:
        _ship_damage_effects[ship_id] = ShipDamageEffects()
    return _ship_damage_effects[ship_id]


def clear_ship_damage_effects(ship_id: int = None):
    """Clear damage effects for a ship or all ships"""
    global _ship_damage_effects
    if ship_id is None:
        _ship_damage_effects = {}
    elif ship_id in _ship_damage_effects:
        del _ship_damage_effects[ship_id]
