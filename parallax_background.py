"""
Parallax Background System for EVE Rebellion
Multi-layer starfields, nebulae, ambient traffic, and stage-specific environments.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional


# Constants
SCREEN_WIDTH = 1800
SCREEN_HEIGHT = 1000


class Star:
    """Individual star with parallax depth"""
    __slots__ = ['x', 'y', 'base_speed', 'size', 'brightness', 'twinkle_phase',
                 'twinkle_speed', 'color_tint']

    def __init__(self, x: float, y: float, depth: int):
        self.x = x
        self.y = y
        # Depth 0 = far (slow), higher = closer (faster)
        self.base_speed = 0.3 + depth * 0.6
        self.size = 1 + depth
        self.brightness = random.randint(80, 180) + depth * 25
        self.twinkle_phase = random.uniform(0, math.pi * 2)
        self.twinkle_speed = random.uniform(0.02, 0.08)
        # Slight color variation
        tint = random.choice(['white', 'blue', 'yellow', 'red'])
        if tint == 'blue':
            self.color_tint = (0.9, 0.95, 1.0)
        elif tint == 'yellow':
            self.color_tint = (1.0, 1.0, 0.85)
        elif tint == 'red':
            self.color_tint = (1.0, 0.9, 0.85)
        else:
            self.color_tint = (1.0, 1.0, 1.0)


class ParallaxStarfield:
    """Multi-layer starfield with depth-based parallax scrolling"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT,
                 num_layers: int = 4):
        self.width = width
        self.height = height
        self.num_layers = num_layers

        # Create star layers (layer 0 = furthest, layer n = closest)
        self.layers: List[List[Star]] = []
        stars_per_layer = [200, 120, 60, 30]  # More stars in distant layers

        for layer in range(num_layers):
            layer_stars = []
            count = stars_per_layer[layer] if layer < len(stars_per_layer) else 20
            for _ in range(count):
                x = random.uniform(0, width)
                y = random.uniform(0, height)
                layer_stars.append(Star(x, y, layer))
            self.layers.append(layer_stars)

        # Pre-render star surfaces for performance
        self._star_cache = {}

    def update(self, scroll_speed: float = 1.0, dx: float = 0, dy: float = 0):
        """Update star positions with parallax effect"""
        for layer_idx, layer in enumerate(self.layers):
            layer_mult = 0.3 + layer_idx * 0.25
            for star in layer:
                # Vertical scroll (main game movement)
                star.y += star.base_speed * scroll_speed
                # Horizontal parallax from player movement
                star.x -= dx * layer_mult * 0.3

                # Wrap around
                if star.y > self.height:
                    star.y = -2
                    star.x = random.uniform(0, self.width)
                elif star.y < -5:
                    star.y = self.height + 2

                if star.x < -10:
                    star.x = self.width + 10
                elif star.x > self.width + 10:
                    star.x = -10

                # Update twinkle
                star.twinkle_phase += star.twinkle_speed

    def draw(self, surface: pygame.Surface, time_ms: int = 0):
        """Draw all star layers"""
        for layer_idx, layer in enumerate(self.layers):
            for star in layer:
                # Calculate twinkle brightness
                twinkle = 0.7 + 0.3 * math.sin(star.twinkle_phase)
                brightness = int(star.brightness * twinkle)
                brightness = max(40, min(255, brightness))

                # Apply color tint
                r = int(brightness * star.color_tint[0])
                g = int(brightness * star.color_tint[1])
                b = int(brightness * star.color_tint[2])
                color = (min(255, r), min(255, g), min(255, b))

                # Draw star
                x, y = int(star.x), int(star.y)
                if star.size == 1:
                    surface.set_at((x, y), color)
                elif star.size == 2:
                    pygame.draw.circle(surface, color, (x, y), 1)
                else:
                    # Larger stars get a slight glow
                    pygame.draw.circle(surface, color, (x, y), star.size // 2)
                    glow_color = (color[0] // 3, color[1] // 3, color[2] // 3)
                    pygame.draw.circle(surface, glow_color, (x, y), star.size)


class ProceduralNebula:
    """Procedurally generated nebula backdrop"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT,
                 color_scheme: str = 'blue'):
        self.width = width
        self.height = height
        self.color_scheme = color_scheme
        self.surface = None
        self.scroll_offset = 0
        self.regenerate()

    def _get_color_palette(self) -> List[Tuple[int, int, int]]:
        """Get color palette based on scheme"""
        palettes = {
            'blue': [(20, 40, 80), (40, 80, 140), (60, 100, 180), (80, 140, 220)],
            'purple': [(50, 20, 70), (80, 40, 120), (120, 60, 160), (160, 80, 200)],
            'red': [(60, 20, 20), (100, 30, 30), (140, 40, 50), (180, 60, 70)],
            'green': [(20, 50, 30), (30, 80, 50), (40, 120, 70), (60, 160, 90)],
            'gold': [(50, 40, 20), (90, 70, 30), (130, 100, 40), (170, 140, 60)],
            'cyan': [(20, 50, 60), (30, 80, 100), (50, 120, 150), (70, 160, 200)],
        }
        return palettes.get(self.color_scheme, palettes['blue'])

    def regenerate(self, color_scheme: str = None):
        """Generate new nebula texture"""
        if color_scheme:
            self.color_scheme = color_scheme

        # Create surface (double height for scrolling)
        self.surface = pygame.Surface((self.width, self.height * 2), pygame.SRCALPHA)
        palette = self._get_color_palette()

        # Generate multiple cloud layers
        for layer in range(4):
            self._add_cloud_layer(palette, layer)

        # Add subtle dust lanes
        self._add_dust_lanes(palette)

    def _add_cloud_layer(self, palette: List[Tuple], layer: int):
        """Add a layer of nebula clouds using noise-like patterns"""
        num_blobs = 8 - layer * 2
        base_size = 200 + layer * 100
        alpha_base = 15 + layer * 8

        color_idx = min(layer, len(palette) - 1)
        base_color = palette[color_idx]

        for _ in range(num_blobs):
            cx = random.randint(0, self.width)
            cy = random.randint(0, self.height * 2)
            size = random.randint(base_size, base_size * 2)

            # Create gradient blob
            for r in range(size, 0, -10):
                alpha = int(alpha_base * (r / size) ** 0.5)
                color = (*base_color, alpha)

                # Draw elliptical blob
                offset_x = random.randint(-20, 20)
                offset_y = random.randint(-20, 20)
                rect = pygame.Rect(cx - r + offset_x, cy - r // 2 + offset_y,
                                  r * 2, r)
                pygame.draw.ellipse(self.surface, color, rect)

    def _add_dust_lanes(self, palette: List[Tuple]):
        """Add dark dust lane streaks"""
        for _ in range(3):
            points = []
            x = random.randint(0, self.width)
            y = random.randint(0, self.height * 2)

            for i in range(20):
                points.append((x + random.randint(-30, 30),
                              y + i * 50 + random.randint(-20, 20)))
                x += random.randint(-60, 60)

            if len(points) >= 2:
                for i in range(len(points) - 1):
                    pygame.draw.line(self.surface, (5, 5, 10, 30),
                                   points[i], points[i + 1],
                                   random.randint(20, 60))

    def update(self, scroll_speed: float = 0.1):
        """Update nebula scroll position"""
        self.scroll_offset += scroll_speed
        if self.scroll_offset >= self.height:
            self.scroll_offset -= self.height

    def draw(self, surface: pygame.Surface):
        """Draw nebula with seamless scrolling"""
        if self.surface:
            # Draw with offset for seamless scroll
            y_offset = int(self.scroll_offset)
            surface.blit(self.surface, (0, -y_offset))
            if y_offset > 0:
                surface.blit(self.surface, (0, self.height * 2 - y_offset - self.height))


class AmbientShip:
    """Non-interactive background ship for atmosphere"""

    SHIP_TYPES = ['frigate', 'cruiser', 'industrial', 'shuttle']

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Spawn position (off-screen)
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self._init_position()

        # Ship properties
        self.ship_type = random.choice(self.SHIP_TYPES)
        self.depth = random.uniform(0.3, 0.8)  # 0 = far, 1 = close
        self.speed = (0.5 + self.depth) * random.uniform(0.8, 1.5)
        self.size = int(8 + self.depth * 20)

        # Visual
        self.sprite = self._create_sprite()
        self.engine_phase = random.uniform(0, math.pi * 2)
        self.alive = True

    def _init_position(self):
        """Initialize position based on travel direction"""
        margin = 100
        if self.direction == 'left':
            self.x = self.width + margin
            self.y = random.randint(0, self.height)
            self.vx = -1
            self.vy = random.uniform(-0.2, 0.2)
        elif self.direction == 'right':
            self.x = -margin
            self.y = random.randint(0, self.height)
            self.vx = 1
            self.vy = random.uniform(-0.2, 0.2)
        elif self.direction == 'up':
            self.x = random.randint(0, self.width)
            self.y = self.height + margin
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = -1
        else:  # down
            self.x = random.randint(0, self.width)
            self.y = -margin
            self.vx = random.uniform(-0.2, 0.2)
            self.vy = 1

    def _create_sprite(self) -> pygame.Surface:
        """Create ship sprite based on type"""
        size = self.size
        surf = pygame.Surface((size * 3, size * 2), pygame.SRCALPHA)
        cx, cy = size * 1.5, size

        # Color based on depth (farther = dimmer)
        brightness = int(100 + self.depth * 100)

        if self.ship_type == 'frigate':
            # Small angular ship
            color = (brightness, brightness - 20, brightness - 40)
            points = [
                (cx, cy - size * 0.6),
                (cx + size * 0.5, cy + size * 0.4),
                (cx, cy + size * 0.2),
                (cx - size * 0.5, cy + size * 0.4),
            ]
            pygame.draw.polygon(surf, color, points)
            # Engine glow
            pygame.draw.circle(surf, (255, 150, 50),
                             (int(cx), int(cy + size * 0.3)), size // 4)

        elif self.ship_type == 'cruiser':
            # Medium elongated ship
            color = (brightness - 20, brightness - 20, brightness)
            pygame.draw.ellipse(surf, color,
                              (cx - size, cy - size * 0.3, size * 2, size * 0.6))
            pygame.draw.polygon(surf, color, [
                (cx + size, cy),
                (cx + size * 1.3, cy - size * 0.2),
                (cx + size * 1.3, cy + size * 0.2),
            ])
            # Engines
            pygame.draw.circle(surf, (100, 200, 255),
                             (int(cx - size * 0.8), int(cy)), size // 5)

        elif self.ship_type == 'industrial':
            # Bulky cargo ship
            color = (brightness - 30, brightness - 10, brightness - 30)
            pygame.draw.rect(surf, color,
                           (cx - size * 0.8, cy - size * 0.4, size * 1.6, size * 0.8))
            pygame.draw.polygon(surf, color, [
                (cx + size * 0.8, cy - size * 0.2),
                (cx + size * 1.2, cy),
                (cx + size * 0.8, cy + size * 0.2),
            ])
            # Running lights
            pygame.draw.circle(surf, (255, 100, 100),
                             (int(cx - size * 0.7), int(cy - size * 0.3)), 2)
            pygame.draw.circle(surf, (100, 255, 100),
                             (int(cx - size * 0.7), int(cy + size * 0.3)), 2)

        else:  # shuttle
            # Tiny fast ship
            color = (brightness, brightness, brightness - 20)
            pygame.draw.polygon(surf, color, [
                (cx + size * 0.6, cy),
                (cx - size * 0.4, cy - size * 0.3),
                (cx - size * 0.4, cy + size * 0.3),
            ])
            pygame.draw.circle(surf, (200, 255, 200),
                             (int(cx - size * 0.3), int(cy)), size // 6)

        # Scale based on depth
        if self.depth < 0.5:
            new_size = (int(surf.get_width() * 0.6), int(surf.get_height() * 0.6))
            surf = pygame.transform.smoothscale(surf, new_size)

        return surf

    def update(self):
        """Update ship position"""
        self.x += self.vx * self.speed
        self.y += self.vy * self.speed
        self.engine_phase += 0.1

        # Check if off-screen
        margin = 150
        if (self.x < -margin or self.x > self.width + margin or
            self.y < -margin or self.y > self.height + margin):
            self.alive = False

    def draw(self, surface: pygame.Surface):
        """Draw ship with engine effects"""
        if self.sprite:
            # Rotate sprite based on velocity
            angle = math.degrees(math.atan2(-self.vy, -self.vx)) - 90
            rotated = pygame.transform.rotate(self.sprite, angle)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))

            # Apply depth-based alpha
            alpha = int(100 + self.depth * 155)
            rotated.set_alpha(alpha)

            surface.blit(rotated, rect)


class AmbientTraffic:
    """Manages background ship traffic"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT,
                 max_ships: int = 5, spawn_rate: float = 0.005):
        self.width = width
        self.height = height
        self.max_ships = max_ships
        self.spawn_rate = spawn_rate
        self.ships: List[AmbientShip] = []

    def update(self):
        """Update all ambient ships"""
        # Spawn new ships
        if len(self.ships) < self.max_ships and random.random() < self.spawn_rate:
            self.ships.append(AmbientShip(self.width, self.height))

        # Update existing ships
        for ship in self.ships:
            ship.update()

        # Remove dead ships
        self.ships = [s for s in self.ships if s.alive]

    def draw(self, surface: pygame.Surface):
        """Draw all ambient ships (sorted by depth)"""
        # Draw far ships first
        for ship in sorted(self.ships, key=lambda s: s.depth):
            ship.draw(surface)


# ============================================================================
# STAGE-SPECIFIC ENVIRONMENTS
# ============================================================================

class Asteroid:
    """Drifting asteroid for Stage 1"""

    def __init__(self, x: float, y: float, size: int, depth: float):
        self.x = x
        self.y = y
        self.size = size
        self.depth = depth
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.5, 0.5)
        self.drift_x = random.uniform(-0.3, 0.3)
        self.drift_y = random.uniform(0.2, 0.8)
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """Create rocky asteroid sprite with baked-in transparency"""
        size = self.size
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx, cy = size, size

        # Generate irregular polygon
        num_points = random.randint(7, 12)
        points = []
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            r = size * random.uniform(0.6, 1.0)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append((px, py))

        # Bake alpha based on depth (40-140 range, clearly background)
        alpha = int(40 + self.depth * 100)

        # Base color varies
        base_gray = int(60 + self.depth * 40)
        color = (base_gray + random.randint(-15, 15),
                base_gray + random.randint(-15, 10),
                base_gray + random.randint(-20, 5),
                alpha)

        pygame.draw.polygon(surf, color, points)

        # Add craters
        for _ in range(random.randint(2, 5)):
            crater_x = cx + random.randint(-size // 2, size // 2)
            crater_y = cy + random.randint(-size // 2, size // 2)
            crater_r = random.randint(size // 8, size // 4)
            crater_color = (max(0, color[0] - 25),
                          max(0, color[1] - 25),
                          max(0, color[2] - 20),
                          alpha)
            pygame.draw.circle(surf, crater_color, (crater_x, crater_y), crater_r)

        # Highlight edge
        highlight = (min(255, color[0] + 30),
                    min(255, color[1] + 30),
                    min(255, color[2] + 25),
                    min(255, alpha + 20))
        pygame.draw.polygon(surf, highlight, points, 2)

        return surf

    def update(self, scroll_speed: float = 1.0):
        self.x += self.drift_x * self.depth
        self.y += (self.drift_y + scroll_speed * 0.3) * self.depth
        self.rotation += self.rot_speed

    def draw(self, surface: pygame.Surface):
        rotated = pygame.transform.rotate(self.sprite, self.rotation)
        # Alpha is baked into sprite - no set_alpha needed
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated, rect)


class AsteroidBeltEnvironment:
    """Stage 1: Asteroid Belt"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.asteroids: List[Asteroid] = []
        self.max_asteroids = 25
        self._spawn_initial()

    def _spawn_initial(self):
        """Spawn initial asteroids"""
        for _ in range(self.max_asteroids):
            self._spawn_asteroid(random.randint(0, self.height))

    def _spawn_asteroid(self, y: float = -100):
        """Spawn a new asteroid"""
        x = random.randint(-50, self.width + 50)
        size = random.randint(15, 60)
        depth = random.uniform(0.3, 1.0)
        self.asteroids.append(Asteroid(x, y, size, depth))

    def update(self, scroll_speed: float = 1.0):
        for asteroid in self.asteroids:
            asteroid.update(scroll_speed)

        # Remove off-screen and respawn
        self.asteroids = [a for a in self.asteroids
                         if a.y < self.height + 100 and a.x > -100 and a.x < self.width + 100]

        while len(self.asteroids) < self.max_asteroids:
            self._spawn_asteroid()

    def draw(self, surface: pygame.Surface):
        # Draw sorted by depth (far first)
        for asteroid in sorted(self.asteroids, key=lambda a: a.depth):
            asteroid.draw(surface)


class DeepSpaceEnvironment:
    """Stage 2: Deep Space Patrol - minimal, vast emptiness"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Pre-render wisp surfaces
        self.wisps = []
        for _ in range(5):
            w = random.randint(100, 300)
            h = random.randint(20, 60)
            alpha = random.randint(15, 35)
            color = random.choice([(40, 60, 100), (60, 40, 80), (40, 80, 60)])

            # Pre-render the wisp
            wisp_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.ellipse(wisp_surf, (*color, alpha), (0, 0, w, h))

            self.wisps.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'surface': wisp_surf
            })

        # Pre-render galaxy sprites
        self.galaxies = []
        for _ in range(3):
            size = random.randint(40, 100)
            color_name = random.choice(['blue', 'purple', 'gold'])
            colors = {
                'blue': (60, 100, 180),
                'purple': (120, 60, 140),
                'gold': (160, 140, 80)
            }
            color = colors.get(color_name, (100, 100, 140))

            # Pre-render galaxy
            galaxy_surf = self._create_galaxy_sprite(size, color)

            self.galaxies.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'surface': galaxy_surf,
                'size': size
            })

        self.scroll_offset = 0

    def _create_galaxy_sprite(self, size: int, color: tuple) -> pygame.Surface:
        """Pre-render a galaxy sprite"""
        surf_size = size * 2
        surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
        cx, cy = surf_size // 2, surf_size // 2

        # Core glow
        for r in range(size // 3, 0, -3):
            alpha = int(50 * r / (size // 3))
            pygame.draw.circle(surf, (*color, alpha), (cx, cy), r)

        # Simple spiral suggestion (static)
        for arm in range(2):
            arm_offset = arm * math.pi
            for i in range(15):
                t = i / 15
                r = size * 0.8 * t
                angle = t * 2.5 + arm_offset
                x = cx + r * math.cos(angle)
                y = cy + r * math.sin(angle) * 0.5

                alpha = int(30 * (1 - t))
                point_size = max(1, int(2 + (1 - t) * 3))
                pygame.draw.circle(surf, (*color, alpha), (int(x), int(y)), point_size)

        return surf

    def update(self, scroll_speed: float = 1.0):
        self.scroll_offset += scroll_speed * 0.05

        for galaxy in self.galaxies:
            galaxy['y'] += scroll_speed * 0.1
            if galaxy['y'] > self.height + 100:
                galaxy['y'] = -100
                galaxy['x'] = random.randint(0, self.width)

    def draw(self, surface: pygame.Surface):
        # Draw distant wisps (pre-rendered)
        for wisp in self.wisps:
            y = (wisp['y'] + self.scroll_offset * 0.5) % (self.height + 100)
            surface.blit(wisp['surface'], (wisp['x'], int(y)))

        # Draw galaxies (pre-rendered)
        for galaxy in self.galaxies:
            x = galaxy['x'] - galaxy['size']
            y = int(galaxy['y']) - galaxy['size']
            surface.blit(galaxy['surface'], (x, y))


class PlanetEnvironment:
    """Stage 3: Planet Atmosphere Glow"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Planet parameters
        self.planet_radius = 600
        self.planet_y = height + self.planet_radius - 150  # Partially visible at bottom
        self.planet_x = width // 2

        # Atmosphere colors (like a gas giant or terrestrial)
        self.atmosphere_type = random.choice(['terran', 'gas_giant', 'volcanic', 'ice'])
        self._setup_atmosphere()

        # Atmospheric particles
        self.particles = []
        for _ in range(50):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.5, 2.0),
                'alpha': random.randint(20, 80)
            })

        # Pre-render planet
        self.planet_surface = self._render_planet()

    def _setup_atmosphere(self):
        """Setup atmosphere colors based on type"""
        atmospheres = {
            'terran': {
                'glow': (80, 140, 255),
                'surface': (40, 80, 40),
                'clouds': (200, 200, 220),
                'particle': (100, 160, 255)
            },
            'gas_giant': {
                'glow': (200, 150, 100),
                'surface': (180, 140, 100),
                'clouds': (220, 180, 140),
                'particle': (255, 200, 150)
            },
            'volcanic': {
                'glow': (255, 100, 50),
                'surface': (60, 30, 20),
                'clouds': (100, 60, 40),
                'particle': (255, 150, 100)
            },
            'ice': {
                'glow': (150, 200, 255),
                'surface': (180, 200, 220),
                'clouds': (220, 230, 255),
                'particle': (200, 220, 255)
            }
        }
        self.colors = atmospheres.get(self.atmosphere_type, atmospheres['terran'])

    def _render_planet(self) -> pygame.Surface:
        """Pre-render the planet with atmosphere"""
        size = self.planet_radius * 2 + 200
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Atmospheric glow layers
        glow = self.colors['glow']
        for r in range(self.planet_radius + 80, self.planet_radius, -5):
            alpha = int(30 * (r - self.planet_radius) / 80)
            pygame.draw.circle(surf, (*glow, alpha), (cx, cy), r)

        # Planet surface
        pygame.draw.circle(surf, self.colors['surface'], (cx, cy), self.planet_radius)

        # Cloud bands for gas giants
        if self.atmosphere_type == 'gas_giant':
            for i in range(8):
                band_y = cy - self.planet_radius + i * (self.planet_radius * 2 // 8)
                band_h = self.planet_radius // 6
                band_alpha = 40 + random.randint(-10, 10)
                band_color = (*self.colors['clouds'], band_alpha)

                band_surf = pygame.Surface((self.planet_radius * 2, band_h), pygame.SRCALPHA)
                pygame.draw.ellipse(band_surf, band_color,
                                   (0, 0, self.planet_radius * 2, band_h))
                surf.blit(band_surf, (cx - self.planet_radius, band_y))

        # Add cloud wisps
        for _ in range(15):
            cloud_x = cx + random.randint(-self.planet_radius + 50, self.planet_radius - 50)
            cloud_y = cy + random.randint(-self.planet_radius + 50, self.planet_radius - 50)
            # Check if inside planet
            if (cloud_x - cx)**2 + (cloud_y - cy)**2 < (self.planet_radius - 30)**2:
                cloud_size = random.randint(30, 80)
                cloud_alpha = random.randint(20, 50)
                cloud_surf = pygame.Surface((cloud_size, cloud_size // 2), pygame.SRCALPHA)
                pygame.draw.ellipse(cloud_surf, (*self.colors['clouds'], cloud_alpha),
                                   (0, 0, cloud_size, cloud_size // 2))
                surf.blit(cloud_surf, (cloud_x - cloud_size // 2, cloud_y - cloud_size // 4))

        # Terminator (day/night line) shading
        shadow = pygame.Surface((size, size), pygame.SRCALPHA)
        for x in range(size):
            for y in range(size):
                dx = x - cx
                dy = y - cy
                if dx*dx + dy*dy < self.planet_radius * self.planet_radius:
                    # Gradient from left (lit) to right (shadow)
                    shade = max(0, min(1, (dx + self.planet_radius) / (self.planet_radius * 2)))
                    alpha = int(150 * (1 - shade))
                    shadow.set_at((x, y), (0, 0, 20, alpha))
        surf.blit(shadow, (0, 0))

        return surf

    def update(self, scroll_speed: float = 1.0):
        # Update atmospheric particles
        for p in self.particles:
            p['y'] += p['speed'] + scroll_speed * 0.5
            p['x'] += random.uniform(-0.5, 0.5)
            if p['y'] > self.height:
                p['y'] = -10
                p['x'] = random.randint(0, self.width)

    def draw(self, surface: pygame.Surface):
        # Draw planet (positioned at bottom)
        planet_draw_y = self.planet_y - self.planet_radius - 100
        surface.blit(self.planet_surface,
                    (self.planet_x - self.planet_surface.get_width() // 2,
                     planet_draw_y))

        # Draw atmospheric particles (simple circles, no surface creation)
        particle_color = self.colors['particle']
        for p in self.particles:
            # Draw directly without creating surfaces
            pygame.draw.circle(surface, (*particle_color, p['alpha']),
                             (int(p['x']), int(p['y'])), p['size'])


class StargateEnvironment:
    """Stage 4: Stargate Structure"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Stargate properties
        self.gate_x = width // 2
        self.gate_y = height // 2 - 100
        self.gate_radius = 180
        self.ring_thickness = 25

        # Animation
        self.rotation = 0
        self.energy_phase = 0
        self.active = True

        # Energy particles
        self.particles = []

        # Pre-render gate structure
        self.gate_surface = self._render_gate_structure()

    def _render_gate_structure(self) -> pygame.Surface:
        """Pre-render the stargate ring structure"""
        size = self.gate_radius * 2 + 100
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        cx, cy = size // 2, size // 2

        # Outer ring (structural)
        outer_r = self.gate_radius
        inner_r = self.gate_radius - self.ring_thickness

        # Main ring - metallic gray with golden accents (Amarr style)
        for r in range(outer_r, inner_r, -1):
            t = (outer_r - r) / self.ring_thickness
            gray = int(80 + 40 * math.sin(t * math.pi))
            color = (gray, gray - 10, gray - 20)
            pygame.draw.circle(surf, color, (cx, cy), r, 2)

        # Golden accent rings
        pygame.draw.circle(surf, (180, 150, 80), (cx, cy), outer_r, 3)
        pygame.draw.circle(surf, (180, 150, 80), (cx, cy), inner_r, 2)
        pygame.draw.circle(surf, (200, 170, 100), (cx, cy), outer_r - self.ring_thickness // 2, 2)

        # Structural pylons (8 around the ring)
        for i in range(8):
            angle = i * math.pi / 4
            px = cx + (self.gate_radius - self.ring_thickness // 2) * math.cos(angle)
            py = cy + (self.gate_radius - self.ring_thickness // 2) * math.sin(angle)

            # Pylon shape
            pylon_surf = pygame.Surface((30, 50), pygame.SRCALPHA)
            pygame.draw.polygon(pylon_surf, (100, 90, 80),
                              [(15, 0), (25, 50), (5, 50)])
            pygame.draw.polygon(pylon_surf, (140, 130, 110),
                              [(15, 0), (25, 50), (5, 50)], 2)

            rotated = pygame.transform.rotate(pylon_surf, -math.degrees(angle) - 90)
            surf.blit(rotated, (px - rotated.get_width() // 2,
                               py - rotated.get_height() // 2))

        return surf

    def update(self, scroll_speed: float = 1.0):
        self.rotation += 0.3
        self.energy_phase += 0.08

        # Spawn energy particles
        if random.random() < 0.3 and self.active:
            angle = random.uniform(0, math.pi * 2)
            r = self.gate_radius - self.ring_thickness - 10
            self.particles.append({
                'x': self.gate_x + r * math.cos(angle),
                'y': self.gate_y + r * math.sin(angle),
                'vx': -2 * math.cos(angle),
                'vy': -2 * math.sin(angle),
                'life': 30,
                'max_life': 30,
                'size': random.randint(2, 5)
            })

        # Update particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            # Spiral toward center
            dx = self.gate_x - p['x']
            dy = self.gate_y - p['y']
            dist = max(1, math.sqrt(dx*dx + dy*dy))
            p['vx'] += dx / dist * 0.3
            p['vy'] += dy / dist * 0.3

        self.particles = [p for p in self.particles if p['life'] > 0]

    def draw(self, surface: pygame.Surface):
        # Draw simple vortex glow (no per-frame surface creation)
        if self.active:
            self._draw_vortex_simple(surface)

        # Draw gate structure (pre-rendered, just rotate)
        rotated = pygame.transform.rotate(self.gate_surface, self.rotation)
        rect = rotated.get_rect(center=(self.gate_x, self.gate_y))
        surface.blit(rotated, rect)

        # Draw energy particles (simple circles)
        for p in self.particles:
            alpha = int(200 * p['life'] / p['max_life'])
            size = max(1, int(p['size'] * p['life'] / p['max_life']))
            color = (100, 200, 255)
            pygame.draw.circle(surface, color, (int(p['x']), int(p['y'])), size)

    def _draw_vortex_simple(self, surface: pygame.Surface):
        """Draw simplified swirling energy vortex"""
        inner_r = self.gate_radius - self.ring_thickness - 5

        # Draw fewer, simpler spiral points
        for arm in range(4):
            arm_offset = arm * math.pi / 2 + self.energy_phase
            for i in range(0, 20, 2):  # Fewer points
                t = i / 20
                r = inner_r * (1 - t * 0.85)
                angle = arm_offset + t * 3.5

                x = int(self.gate_x + r * math.cos(angle))
                y = int(self.gate_y + r * math.sin(angle))
                size = max(2, int(4 + 6 * (1 - t)))
                color = (80, 180, 255)

                pygame.draw.circle(surface, color, (x, y), size)

        # Central glow - simple gradient
        for r in range(35, 5, -8):
            brightness = 150 + int(105 * (35 - r) / 30)
            color = (brightness, min(255, brightness + 50), 255)
            pygame.draw.circle(surface, color, (self.gate_x, self.gate_y), r)


class WreckageField:
    """Stage 5: Capital Ship Wreckage Field"""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Generate wreckage pieces
        self.debris: List[dict] = []
        self.large_wrecks: List[dict] = []

        self._generate_debris()
        self._generate_large_wrecks()

        # Ambient fires and sparks
        self.fires = []
        self.sparks = []

    def _generate_debris(self):
        """Generate small debris pieces"""
        for _ in range(40):
            self.debris.append({
                'x': random.randint(0, self.width),
                'y': random.randint(-self.height, self.height),
                'size': random.randint(5, 25),
                'rotation': random.uniform(0, 360),
                'rot_speed': random.uniform(-2, 2),
                'drift_x': random.uniform(-0.5, 0.5),
                'drift_y': random.uniform(0.3, 1.0),
                'depth': random.uniform(0.3, 1.0),
                'sprite': None
            })

        # Pre-render debris sprites with baked-in alpha
        for d in self.debris:
            d['sprite'] = self._create_debris_sprite(d['size'], d['depth'])

    def _create_debris_sprite(self, size: int, depth: float) -> pygame.Surface:
        """Create debris piece sprite with baked-in transparency"""
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx, cy = size, size

        # Bake alpha based on depth (40-140 range)
        alpha = int(40 + depth * 100)

        # Random angular shape
        num_points = random.randint(4, 7)
        points = []
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2 + random.uniform(-0.3, 0.3)
            r = size * random.uniform(0.5, 1.0)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        # Hull plating colors with baked alpha
        gray = random.randint(50, 90)
        color = (gray, gray - 10, gray - 15, alpha)
        pygame.draw.polygon(surf, color, points)
        pygame.draw.polygon(surf, (gray + 30, gray + 20, gray + 15, alpha), points, 1)

        # Damage marks
        for _ in range(random.randint(1, 3)):
            dx = random.randint(-size // 2, size // 2)
            dy = random.randint(-size // 2, size // 2)
            damage_r = max(2, size // 4)
            pygame.draw.circle(surf, (30, 25, 20, alpha), (cx + dx, cy + dy),
                             random.randint(2, damage_r))

        return surf

    def _generate_large_wrecks(self):
        """Generate large capital ship hull sections"""
        wreck_types = ['hull_section', 'engine_block', 'bridge', 'hangar']

        for _ in range(3):
            wreck = {
                'type': random.choice(wreck_types),
                'x': random.randint(100, self.width - 100),
                'y': random.randint(-500, 0),
                'rotation': random.uniform(-15, 15),
                'scale': random.uniform(0.8, 1.5),
                'drift_y': random.uniform(0.1, 0.3),
                'sprite': None
            }
            wreck['sprite'] = self._create_wreck_sprite(wreck['type'], wreck['scale'])
            self.large_wrecks.append(wreck)

    def _create_wreck_sprite(self, wreck_type: str, scale: float) -> pygame.Surface:
        """Create large wreckage sprite with baked-in transparency"""
        base_size = int(200 * scale)
        surf = pygame.Surface((base_size * 2, base_size), pygame.SRCALPHA)
        cx, cy = base_size, base_size // 2

        # Baked alpha for background clarity
        alpha = 120

        # Hull colors with baked alpha (Amarr gold/brown damaged)
        hull_dark = (50, 40, 30, alpha)
        hull_mid = (80, 65, 45, alpha)
        hull_light = (110, 90, 60, alpha)
        damage = (30, 25, 20, alpha)
        fire_glow = (180, 80, 30, min(180, alpha + 60))

        if wreck_type == 'hull_section':
            # Large curved hull plate
            points = [
                (cx - base_size * 0.8, cy - base_size * 0.2),
                (cx - base_size * 0.6, cy - base_size * 0.4),
                (cx + base_size * 0.5, cy - base_size * 0.35),
                (cx + base_size * 0.7, cy),
                (cx + base_size * 0.4, cy + base_size * 0.3),
                (cx - base_size * 0.7, cy + base_size * 0.25),
            ]
            pygame.draw.polygon(surf, hull_mid, points)
            pygame.draw.polygon(surf, hull_light, points, 3)

            # Damage holes
            for _ in range(5):
                hx = cx + random.randint(-base_size // 2, base_size // 2)
                hy = cy + random.randint(-base_size // 4, base_size // 4)
                hr = random.randint(base_size // 10, base_size // 5)
                pygame.draw.circle(surf, damage, (hx, hy), hr)
                # Fire glow in some holes
                if random.random() < 0.3:
                    pygame.draw.circle(surf, fire_glow, (hx, hy), hr - 5)

        elif wreck_type == 'engine_block':
            # Cylindrical engine section
            pygame.draw.ellipse(surf, hull_dark,
                              (cx - base_size * 0.6, cy - base_size * 0.3,
                               base_size * 1.2, base_size * 0.6))
            pygame.draw.ellipse(surf, hull_mid,
                              (cx - base_size * 0.5, cy - base_size * 0.25,
                               base_size, base_size * 0.5))
            # Engine nozzle
            pygame.draw.circle(surf, (40, 35, 30, alpha),
                             (cx + base_size // 2, cy), base_size // 4)
            pygame.draw.circle(surf, fire_glow,
                             (cx + base_size // 2, cy), base_size // 6)

        elif wreck_type == 'bridge':
            # Command bridge section
            pygame.draw.polygon(surf, hull_mid, [
                (cx - base_size * 0.4, cy + base_size * 0.2),
                (cx - base_size * 0.3, cy - base_size * 0.3),
                (cx + base_size * 0.3, cy - base_size * 0.35),
                (cx + base_size * 0.5, cy + base_size * 0.15),
            ])
            # Windows (broken)
            for i in range(4):
                wx = cx - base_size * 0.2 + i * base_size * 0.15
                wy = cy - base_size * 0.15
                pygame.draw.rect(surf, (20, 30, 40, alpha), (wx, wy, 10, 6))
                if random.random() < 0.5:
                    pygame.draw.rect(surf, (200, 180, 100, alpha), (wx, wy, 10, 6), 1)

        else:  # hangar
            # Open hangar bay
            pygame.draw.rect(surf, hull_dark,
                           (cx - base_size * 0.5, cy - base_size * 0.25,
                            base_size, base_size * 0.5))
            pygame.draw.rect(surf, (15, 12, 10, alpha),
                           (cx - base_size * 0.4, cy - base_size * 0.15,
                            base_size * 0.8, base_size * 0.3))
            # Interior glow
            pygame.draw.rect(surf, (50, 30, 20, alpha),
                           (cx - base_size * 0.35, cy - base_size * 0.1,
                            base_size * 0.7, base_size * 0.2))

        return surf

    def update(self, scroll_speed: float = 1.0):
        # Update debris
        for d in self.debris:
            d['y'] += d['drift_y'] * d['depth'] + scroll_speed * 0.5
            d['x'] += d['drift_x'] * d['depth']
            d['rotation'] += d['rot_speed']

            # Respawn if off screen
            if d['y'] > self.height + 50:
                d['y'] = random.randint(-100, -20)
                d['x'] = random.randint(0, self.width)

        # Update large wrecks
        for w in self.large_wrecks:
            w['y'] += w['drift_y'] + scroll_speed * 0.2

            if w['y'] > self.height + 200:
                w['y'] = random.randint(-600, -300)
                w['x'] = random.randint(100, self.width - 100)

        # Spawn fires on wrecks
        if random.random() < 0.1:
            for w in self.large_wrecks:
                if random.random() < 0.3:
                    self.fires.append({
                        'x': w['x'] + random.randint(-80, 80),
                        'y': w['y'] + random.randint(-30, 30),
                        'life': random.randint(30, 60),
                        'size': random.randint(5, 15)
                    })

        # Update fires
        for f in self.fires:
            f['life'] -= 1
            f['y'] -= 0.5
            f['size'] = max(1, f['size'] - 0.2)

        self.fires = [f for f in self.fires if f['life'] > 0]

    def draw(self, surface: pygame.Surface):
        # Draw large wrecks first (background) - alpha baked into sprites
        for w in self.large_wrecks:
            if w['sprite']:
                rotated = pygame.transform.rotate(w['sprite'], w['rotation'])
                rect = rotated.get_rect(center=(int(w['x']), int(w['y'])))
                surface.blit(rotated, rect)

        # Draw fires (simple circles, no per-frame surface creation)
        for f in self.fires:
            size = max(1, int(f['size']))
            x, y = int(f['x']), int(f['y'])
            # Outer glow
            pygame.draw.circle(surface, (255, 150, 50), (x, y), size)
            # Inner bright core
            if size > 2:
                pygame.draw.circle(surface, (255, 200, 100), (x, y), size // 2)

        # Draw debris (sorted by depth) - alpha baked into sprites
        for d in sorted(self.debris, key=lambda x: x['depth']):
            if d['sprite']:
                rotated = pygame.transform.rotate(d['sprite'], d['rotation'])
                rect = rotated.get_rect(center=(int(d['x']), int(d['y'])))
                surface.blit(rotated, rect)


# ============================================================================
# MAIN PARALLAX BACKGROUND MANAGER
# ============================================================================

class ParallaxBackground:
    """Main manager for parallax backgrounds with stage-specific environments"""

    STAGE_ENVIRONMENTS = {
        1: 'asteroid_belt',
        2: 'deep_space',
        3: 'planet',
        4: 'stargate',
        5: 'wreckage'
    }

    STAGE_NEBULA_COLORS = {
        1: 'gold',      # Asteroid belt - dusty gold
        2: 'purple',    # Deep space - mysterious purple
        3: 'blue',      # Planet - atmospheric blue
        4: 'cyan',      # Stargate - energy cyan
        5: 'red',       # Wreckage - ominous red
    }

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height

        # Core layers (always present)
        self.starfield = ParallaxStarfield(width, height, num_layers=4)
        self.nebula = ProceduralNebula(width, height, 'blue')
        self.traffic = AmbientTraffic(width, height, max_ships=4, spawn_rate=0.003)

        # Stage-specific environment
        self.current_stage = 1
        self.environment = None
        self.set_stage(1)

        # Transition effects
        self.transitioning = False
        self.transition_alpha = 0

    def set_stage(self, stage: int):
        """Set up environment for a specific stage"""
        self.current_stage = stage

        # Update nebula color
        nebula_color = self.STAGE_NEBULA_COLORS.get(stage, 'blue')
        self.nebula.regenerate(nebula_color)

        # Create stage environment
        env_type = self.STAGE_ENVIRONMENTS.get(stage, 'deep_space')

        if env_type == 'asteroid_belt':
            self.environment = AsteroidBeltEnvironment(self.width, self.height)
        elif env_type == 'deep_space':
            self.environment = DeepSpaceEnvironment(self.width, self.height)
        elif env_type == 'planet':
            self.environment = PlanetEnvironment(self.width, self.height)
        elif env_type == 'stargate':
            self.environment = StargateEnvironment(self.width, self.height)
        elif env_type == 'wreckage':
            self.environment = WreckageField(self.width, self.height)
        else:
            self.environment = DeepSpaceEnvironment(self.width, self.height)

        # Adjust traffic based on stage
        if stage == 2:  # Deep space - more traffic
            self.traffic.max_ships = 6
            self.traffic.spawn_rate = 0.008
        elif stage == 4:  # Stargate - lots of traffic
            self.traffic.max_ships = 8
            self.traffic.spawn_rate = 0.01
        elif stage == 5:  # Wreckage - minimal traffic
            self.traffic.max_ships = 2
            self.traffic.spawn_rate = 0.002
        else:
            self.traffic.max_ships = 4
            self.traffic.spawn_rate = 0.005

    def transition_to_stage(self, stage: int):
        """Start transition to a new stage"""
        self.transitioning = True
        self.transition_alpha = 0
        self.next_stage = stage

    def update(self, scroll_speed: float = 1.0, player_dx: float = 0):
        """Update all background layers"""
        # Update core layers
        self.starfield.update(scroll_speed, player_dx)
        self.nebula.update(scroll_speed * 0.2)
        self.traffic.update()

        # Update stage environment
        if self.environment:
            self.environment.update(scroll_speed)

        # Handle stage transitions
        if self.transitioning:
            self.transition_alpha += 5
            if self.transition_alpha >= 255:
                self.set_stage(self.next_stage)
                self.transitioning = False
            elif self.transition_alpha >= 128:
                # Switch stage at midpoint
                if hasattr(self, 'next_stage') and self.current_stage != self.next_stage:
                    self.set_stage(self.next_stage)

    def draw(self, surface: pygame.Surface, time_ms: int = 0):
        """Draw all background layers in order"""
        # Clear with deep space black
        surface.fill((5, 5, 12))

        # Layer 1: Nebula (furthest back)
        self.nebula.draw(surface)

        # Layer 2: Stars
        self.starfield.draw(surface, time_ms)

        # Layer 3: Stage-specific environment
        if self.environment:
            self.environment.draw(surface)

        # Layer 4: Ambient traffic (closest background layer)
        self.traffic.draw(surface)

        # Transition overlay
        if self.transitioning:
            fade = pygame.Surface((self.width, self.height))
            fade.fill((0, 0, 0))
            # Fade out then in
            if self.transition_alpha < 128:
                fade.set_alpha(self.transition_alpha * 2)
            else:
                fade.set_alpha((255 - self.transition_alpha) * 2)
            surface.blit(fade, (0, 0))


# For backwards compatibility / direct usage
def create_background(stage: int = 1) -> ParallaxBackground:
    """Factory function to create a parallax background for a given stage"""
    bg = ParallaxBackground()
    bg.set_stage(stage)
    return bg
