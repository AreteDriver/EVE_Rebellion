"""
Parallax Background System for EVE Rebellion
Multi-layer starfields, nebulae, ambient traffic, and stage-specific environments.
"""

import math
import os
import random
from typing import List, Optional, Tuple

import pygame

# Cache for loaded ship images
_carrier_image_cache = {}

# Carrier definitions: Amarr and Minmatar only
CARRIER_TYPES = {
    'amarr': {
        'name': 'archon',
        'engine_color': (100, 150, 255),  # Amarr blue engines
    },
    'minmatar': {
        'name': 'nidhoggur',
        'engine_color': (255, 150, 50),  # Minmatar orange engines
    }
}

def _load_carrier_image(size: int, faction: str = None) -> Tuple[Optional[pygame.Surface], str]:
    """Load and cache a carrier image at the specified size.

    Args:
        size: Base size for scaling
        faction: 'amarr' or 'minmatar' - if None, randomly selects

    Returns:
        Tuple of (surface, faction_name) or (None, faction_name)
    """
    # Select faction if not specified
    if faction is None:
        faction = random.choice(['amarr', 'minmatar'])

    carrier_info = CARRIER_TYPES.get(faction, CARRIER_TYPES['amarr'])
    ship_name = carrier_info['name']

    cache_key = f"{faction}_{size}"
    if cache_key in _carrier_image_cache:
        return _carrier_image_cache[cache_key], faction

    # Try to load carrier image
    base_dir = os.path.dirname(__file__)
    image_paths = [
        os.path.join(base_dir, 'assets', 'ship_sprites', f'{ship_name}.png'),
        os.path.join(base_dir, 'assets', 'eve_renders', f'{ship_name}.png'),
    ]

    for path in image_paths:
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                # Scale to appropriate size (carriers are large)
                target_width = size * 5
                target_height = size * 3
                img = pygame.transform.smoothscale(img, (target_width, target_height))
                _carrier_image_cache[cache_key] = img
                return img, faction
            except pygame.error:
                pass

    return None, faction


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
    """Non-interactive background ship for atmosphere - EVE-style silhouettes"""

    SHIP_TYPES = ['frigate', 'cruiser', 'industrial', 'shuttle', 'battleship', 'mining']
    # Carriers are rare - not in normal rotation, spawned specially

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT,
                 force_type: str = None, enemy_faction: str = None):
        self.width = width
        self.height = height
        # Store enemy faction for carrier image selection
        self.enemy_faction = enemy_faction or 'amarr'

        # Spawn position (off-screen)
        self.direction = random.choice(['left', 'right', 'up', 'down'])
        self._init_position()

        # Ship properties - carrier can be forced, otherwise rare chance
        if force_type:
            self.ship_type = force_type
        elif random.random() < 0.02:  # 2% chance of carrier
            self.ship_type = 'carrier'
        else:
            self.ship_type = random.choice(self.SHIP_TYPES)

        # Carriers are always very far back (distant, imposing silhouettes)
        if self.ship_type == 'carrier':
            self.depth = random.uniform(0.12, 0.22)  # Very far back
            self.speed = 0.15 + self.depth * 0.3  # Slow, majestic movement
            self.size = int(80 + self.depth * 60)  # Large even at distance
        else:
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

    def _apply_atmospheric_perspective(self, color: Tuple[int, int, int],
                                        alpha: int) -> Tuple[int, int, int, int]:
        """Apply atmospheric perspective - distant objects get blue-ish tint"""
        # Farther = more blue tint, less saturation
        distance_factor = 1.0 - self.depth  # 0.2-0.7 range
        blue_shift = int(distance_factor * 40)
        desat = distance_factor * 0.3

        r = int(color[0] * (1 - desat) + blue_shift)
        g = int(color[1] * (1 - desat * 0.5) + blue_shift * 0.5)
        b = int(color[2] + blue_shift)

        return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), alpha)

    def _draw_engine_glow(self, surf: pygame.Surface, x: int, y: int,
                          size: int, color: Tuple[int, int, int]):
        """Draw multi-layer engine glow effect"""
        # Outer glow (large, faint)
        glow_surf = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
        for r in range(size * 2, 0, -2):
            alpha = int(60 * (r / (size * 2)))
            pygame.draw.circle(glow_surf, (*color, alpha),
                             (size * 2, size * 2), r)
        surf.blit(glow_surf, (x - size * 2, y - size * 2),
                 special_flags=pygame.BLEND_RGBA_ADD)

        # Core glow (bright center)
        pygame.draw.circle(surf, (255, 255, 255, 200), (x, y), max(1, size // 3))
        pygame.draw.circle(surf, (*color, 255), (x, y), max(1, size // 2))

    def _draw_hull_details(self, surf: pygame.Surface, points: list,
                           color: Tuple[int, int, int, int], size: int):
        """Add hull panel lines and lighting details"""
        # Subtle edge highlight (top-left lighting)
        highlight = (min(255, color[0] + 40), min(255, color[1] + 40),
                    min(255, color[2] + 35), min(255, color[3]))
        (max(0, color[0] - 30), max(0, color[1] - 30),
                 max(0, color[2] - 25), color[3])

        # Draw highlight on upper edges
        pygame.draw.polygon(surf, highlight, points, 1)

        # Add window lights for larger ships
        if size > 12 and random.random() > 0.3:
            cx = sum(p[0] for p in points) / len(points)
            cy = sum(p[1] for p in points) / len(points)
            num_windows = max(1, size // 8)
            for _ in range(num_windows):
                wx = int(cx + random.uniform(-size * 0.4, size * 0.4))
                wy = int(cy + random.uniform(-size * 0.2, size * 0.2))
                window_color = random.choice([
                    (255, 255, 200, 180),  # Warm interior
                    (200, 220, 255, 180),  # Cool interior
                    (255, 200, 150, 180),  # Orange light
                ])
                pygame.draw.circle(surf, window_color, (wx, wy), max(1, size // 12))

    def _create_sprite(self) -> pygame.Surface:
        """Create detailed EVE-style ship sprite"""
        size = self.size
        surf = pygame.Surface((size * 4, size * 3), pygame.SRCALPHA)
        cx, cy = size * 2, size * 1.5

        # Base brightness with depth falloff
        brightness = int(80 + self.depth * 120)
        # Alpha based on depth (distant = more transparent)
        alpha = int(120 + self.depth * 135)

        if self.ship_type == 'frigate':
            # Sleek angular frigate - Minmatar style
            base_color = (brightness + 10, brightness - 10, brightness - 30)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            # Main hull (angular, aggressive)
            hull_points = [
                (cx, cy - size * 0.7),           # Nose
                (cx + size * 0.3, cy - size * 0.3),  # Right front
                (cx + size * 0.6, cy + size * 0.3),  # Right wing
                (cx + size * 0.2, cy + size * 0.5),  # Right back
                (cx, cy + size * 0.3),            # Tail center
                (cx - size * 0.2, cy + size * 0.5),  # Left back
                (cx - size * 0.6, cy + size * 0.3),  # Left wing
                (cx - size * 0.3, cy - size * 0.3),  # Left front
            ]
            pygame.draw.polygon(surf, color, hull_points)
            self._draw_hull_details(surf, hull_points, color, size)

            # Engine nacelles
            self._draw_engine_glow(surf, int(cx - size * 0.3), int(cy + size * 0.45),
                                  max(2, size // 5), (255, 150, 50))
            self._draw_engine_glow(surf, int(cx + size * 0.3), int(cy + size * 0.45),
                                  max(2, size // 5), (255, 150, 50))

        elif self.ship_type == 'cruiser':
            # Elongated cruiser - Amarr style (golden, ornate)
            base_color = (brightness + 20, brightness, brightness - 40)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            # Main hull body
            hull_points = [
                (cx + size * 1.2, cy),            # Bow
                (cx + size * 0.8, cy - size * 0.25),
                (cx - size * 0.3, cy - size * 0.35),
                (cx - size * 0.8, cy - size * 0.25),
                (cx - size * 1.0, cy),            # Stern
                (cx - size * 0.8, cy + size * 0.25),
                (cx - size * 0.3, cy + size * 0.35),
                (cx + size * 0.8, cy + size * 0.25),
            ]
            pygame.draw.polygon(surf, color, hull_points)

            # Command section (raised)
            cmd_color = (min(255, color[0] + 20), min(255, color[1] + 15),
                        color[2], color[3])
            pygame.draw.ellipse(surf, cmd_color,
                              (cx - size * 0.2, cy - size * 0.2, size * 0.6, size * 0.4))

            self._draw_hull_details(surf, hull_points, color, size)

            # Twin engines
            self._draw_engine_glow(surf, int(cx - size * 0.9), int(cy - size * 0.15),
                                  max(2, size // 4), (100, 180, 255))
            self._draw_engine_glow(surf, int(cx - size * 0.9), int(cy + size * 0.15),
                                  max(2, size // 4), (100, 180, 255))

        elif self.ship_type == 'industrial':
            # Bulky cargo hauler - blocky utilitarian design
            base_color = (brightness - 20, brightness - 10, brightness - 25)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            # Cargo section (large box)
            cargo_rect = (cx - size * 0.7, cy - size * 0.45, size * 1.4, size * 0.9)
            pygame.draw.rect(surf, color, cargo_rect, border_radius=3)

            # Bridge section (front)
            bridge_color = (min(255, color[0] + 15), min(255, color[1] + 10),
                           color[2], color[3])
            bridge_points = [
                (cx + size * 0.7, cy - size * 0.3),
                (cx + size * 1.1, cy),
                (cx + size * 0.7, cy + size * 0.3),
            ]
            pygame.draw.polygon(surf, bridge_color, bridge_points)

            # Cargo bay lines
            line_color = (max(0, color[0] - 20), max(0, color[1] - 20),
                         max(0, color[2] - 15), color[3])
            for i in range(3):
                lx = int(cx - size * 0.5 + i * size * 0.35)
                pygame.draw.line(surf, line_color,
                               (lx, int(cy - size * 0.4)),
                               (lx, int(cy + size * 0.4)), 1)

            # Running lights
            pygame.draw.circle(surf, (255, 80, 80, 200),
                             (int(cx - size * 0.65), int(cy - size * 0.35)), 2)
            pygame.draw.circle(surf, (80, 255, 80, 200),
                             (int(cx - size * 0.65), int(cy + size * 0.35)), 2)

            # Engine cluster
            self._draw_engine_glow(surf, int(cx - size * 0.85), int(cy),
                                  max(2, size // 4), (255, 180, 100))

        elif self.ship_type == 'shuttle':
            # Small fast shuttle
            base_color = (brightness + 5, brightness + 5, brightness - 10)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            hull_points = [
                (cx + size * 0.7, cy),            # Nose
                (cx + size * 0.3, cy - size * 0.25),
                (cx - size * 0.4, cy - size * 0.2),
                (cx - size * 0.5, cy),
                (cx - size * 0.4, cy + size * 0.2),
                (cx + size * 0.3, cy + size * 0.25),
            ]
            pygame.draw.polygon(surf, color, hull_points)

            # Cockpit window
            pygame.draw.ellipse(surf, (150, 200, 255, 150),
                              (cx + size * 0.1, cy - size * 0.1, size * 0.3, size * 0.2))

            self._draw_engine_glow(surf, int(cx - size * 0.45), int(cy),
                                  max(2, size // 5), (180, 255, 180))

        elif self.ship_type == 'battleship':
            # Massive battleship silhouette
            base_color = (brightness - 10, brightness - 15, brightness + 10)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            # Massive hull
            hull_points = [
                (cx + size * 1.5, cy),            # Bow
                (cx + size * 1.2, cy - size * 0.3),
                (cx + size * 0.5, cy - size * 0.45),
                (cx - size * 0.5, cy - size * 0.5),
                (cx - size * 1.2, cy - size * 0.35),
                (cx - size * 1.4, cy),            # Stern
                (cx - size * 1.2, cy + size * 0.35),
                (cx - size * 0.5, cy + size * 0.5),
                (cx + size * 0.5, cy + size * 0.45),
                (cx + size * 1.2, cy + size * 0.3),
            ]
            pygame.draw.polygon(surf, color, hull_points)

            # Superstructure
            super_color = (min(255, color[0] + 15), min(255, color[1] + 10),
                          color[2], color[3])
            pygame.draw.ellipse(surf, super_color,
                              (cx - size * 0.4, cy - size * 0.3, size * 0.9, size * 0.6))

            self._draw_hull_details(surf, hull_points, color, size)

            # Multiple engine banks
            for offset in [-0.25, 0, 0.25]:
                self._draw_engine_glow(surf, int(cx - size * 1.3),
                                      int(cy + size * offset),
                                      max(2, size // 4), (100, 150, 255))

        elif self.ship_type == 'mining':
            # Mining barge with ore hold
            base_color = (brightness - 15, brightness + 5, brightness - 20)
            color = self._apply_atmospheric_perspective(base_color, alpha)

            # Main body
            pygame.draw.ellipse(surf, color,
                              (cx - size * 0.8, cy - size * 0.35, size * 1.6, size * 0.7))

            # Mining laser arm
            arm_color = (max(0, color[0] - 15), max(0, color[1] - 10),
                        max(0, color[2] - 10), color[3])
            pygame.draw.line(surf, arm_color,
                           (int(cx + size * 0.6), int(cy)),
                           (int(cx + size * 1.2), int(cy - size * 0.3)), 2)
            # Laser tip glow
            pygame.draw.circle(surf, (100, 255, 150, 180),
                             (int(cx + size * 1.2), int(cy - size * 0.3)), 3)

            # Ore hold bulge
            pygame.draw.ellipse(surf, color,
                              (cx - size * 0.5, cy + size * 0.1, size * 0.8, size * 0.4))

            self._draw_engine_glow(surf, int(cx - size * 0.75), int(cy),
                                  max(2, size // 4), (255, 200, 100))

        else:  # carrier
            # Try to use actual carrier image (Amarr Archon or Minmatar Nidhoggur)
            # Use enemy faction if set, otherwise random
            carrier_img, faction = _load_carrier_image(size, self.enemy_faction)

            # Get faction-specific engine color
            engine_color = CARRIER_TYPES.get(faction, CARRIER_TYPES['amarr'])['engine_color']

            if carrier_img:
                # Use actual carrier image with atmospheric effects
                surf = carrier_img.copy()

                # Apply atmospheric perspective (fade distant objects)
                if alpha < 255:
                    fade_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
                    fade_surf.fill((0, 0, 0, 255 - alpha))
                    surf.blit(fade_surf, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)

                # Add engine glow effects
                w, h = surf.get_size()
                cx, cy = w // 2, h // 2

                # Engine banks on the stern - faction-appropriate color
                engine_positions = [-0.2, 0, 0.2]
                for offset in engine_positions:
                    engine_y = int(cy + h * offset * 0.3)
                    engine_x = int(w * 0.1)  # Left side (stern)
                    self._draw_engine_glow(surf, engine_x, engine_y,
                                          max(6, size // 5), engine_color)

                # Running lights
                pygame.draw.circle(surf, (255, 80, 80, 180),
                                 (int(w * 0.9), int(cy - h * 0.15)), 3)
                pygame.draw.circle(surf, (80, 255, 80, 180),
                                 (int(w * 0.9), int(cy + h * 0.15)), 3)
            else:
                # Fallback: Simple silhouette if image not available
                # Use faction-appropriate colors
                if faction == 'minmatar':
                    base_color = (brightness - 10, brightness - 15, brightness - 20)  # Rusty Minmatar
                else:
                    base_color = (brightness + 15, brightness + 5, brightness - 35)  # Golden Amarr
                color = self._apply_atmospheric_perspective(base_color, alpha)
                surf = pygame.Surface((size * 5, size * 3), pygame.SRCALPHA)
                cx, cy = size * 2.5, size * 1.5

                # Simple carrier hull shape
                hull_points = [
                    (cx + size * 2.0, cy),
                    (cx + size * 1.5, cy - size * 0.4),
                    (cx - size * 1.5, cy - size * 0.4),
                    (cx - size * 1.8, cy),
                    (cx - size * 1.5, cy + size * 0.4),
                    (cx + size * 1.5, cy + size * 0.4),
                ]
                pygame.draw.polygon(surf, color, hull_points)
                pygame.draw.polygon(surf, (200, 170, 100, min(255, alpha)), hull_points, 2)

                # Engine glow - faction-appropriate color
                self._draw_engine_glow(surf, int(cx - size * 1.7), int(cy),
                                      max(6, size // 4), engine_color)

        # Scale based on depth for distant ships
        if self.depth < 0.5:
            scale = 0.5 + self.depth
            new_size = (int(surf.get_width() * scale), int(surf.get_height() * scale))
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
                 max_ships: int = 5, spawn_rate: float = 0.005, enemy_faction: str = None):
        self.width = width
        self.height = height
        self.max_ships = max_ships
        self.spawn_rate = spawn_rate
        self.ships: List[AmbientShip] = []
        self.enemy_faction = enemy_faction or 'amarr'

    def set_enemy_faction(self, faction: str):
        """Set the enemy faction for carrier images"""
        self.enemy_faction = faction

    def update(self):
        """Update all ambient ships"""
        # Spawn new ships
        if len(self.ships) < self.max_ships and random.random() < self.spawn_rate:
            self.ships.append(AmbientShip(self.width, self.height, enemy_faction=self.enemy_faction))

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
    """Drifting asteroid for Stage 1 - realistic rocky/metallic appearance"""

    # Asteroid composition types
    ROCK = 'rock'
    METALLIC = 'metallic'
    ICE = 'ice'

    def __init__(self, x: float, y: float, size: int, depth: float):
        self.x = x
        self.y = y
        self.size = size
        self.depth = depth
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-0.5, 0.5)
        self.drift_x = random.uniform(-0.3, 0.3)
        self.drift_y = random.uniform(0.2, 0.8)
        # Random composition
        self.composition = random.choice([self.ROCK, self.ROCK, self.METALLIC, self.ICE])
        self.sprite = self._create_sprite()

    def _create_sprite(self) -> pygame.Surface:
        """Create realistic asteroid sprite with baked-in transparency"""
        size = self.size
        surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        cx, cy = size + 2, size + 2

        # Generate irregular polygon with more natural variation
        num_points = random.randint(8, 14)
        points = []
        base_angles = []
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2 + random.uniform(-0.15, 0.15)
            base_angles.append(angle)
            # More irregular radius variation
            r = size * random.uniform(0.55, 1.0)
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            points.append((px, py))

        # Bake alpha based on depth (50-150 range)
        alpha = int(50 + self.depth * 100)

        # Color based on composition
        if self.composition == self.METALLIC:
            # Metallic gray with slight golden tint
            base_val = int(70 + self.depth * 50)
            color = (base_val + random.randint(0, 20),
                    base_val + random.randint(-5, 15),
                    base_val + random.randint(-15, 5),
                    alpha)
        elif self.composition == self.ICE:
            # Bluish-white ice
            base_val = int(80 + self.depth * 60)
            color = (base_val + random.randint(-10, 5),
                    base_val + random.randint(0, 15),
                    base_val + random.randint(10, 30),
                    alpha)
        else:  # ROCK
            # Brown-gray rock
            base_val = int(55 + self.depth * 45)
            color = (base_val + random.randint(-10, 20),
                    base_val + random.randint(-15, 10),
                    base_val + random.randint(-20, 5),
                    alpha)

        # Draw base shape
        pygame.draw.polygon(surf, color, points)

        # === LIGHTING GRADIENT ===
        # Create top-left lighting effect
        light_angle = -math.pi / 4  # Upper-left light source
        for i, (px, py) in enumerate(points):
            # Calculate point's angle from center
            point_angle = math.atan2(py - cy, px - cx)
            # Angle difference from light source
            angle_diff = abs(point_angle - light_angle)
            if angle_diff > math.pi:
                angle_diff = 2 * math.pi - angle_diff

            # Points facing light are brighter
            if angle_diff < math.pi / 2:
                1.0 - (angle_diff / (math.pi / 2)) * 0.4
            else:
                pass

        # === SURFACE TEXTURE ===
        # Add rocky texture bumps
        for _ in range(random.randint(3, 8)):
            bump_angle = random.uniform(0, math.pi * 2)
            bump_dist = random.uniform(size * 0.2, size * 0.7)
            bump_x = int(cx + bump_dist * math.cos(bump_angle))
            bump_y = int(cy + bump_dist * math.sin(bump_angle))
            bump_r = random.randint(max(2, size // 10), max(3, size // 5))

            # Bumps can be lighter or darker
            if random.random() > 0.5:
                bump_color = (max(0, color[0] - 15), max(0, color[1] - 15),
                             max(0, color[2] - 12), alpha)
            else:
                bump_color = (min(255, color[0] + 12), min(255, color[1] + 10),
                             min(255, color[2] + 8), alpha)
            pygame.draw.circle(surf, bump_color, (bump_x, bump_y), bump_r)

        # === CRATERS ===
        for _ in range(random.randint(1, 4)):
            crater_angle = random.uniform(0, math.pi * 2)
            crater_dist = random.uniform(0, size * 0.5)
            crater_x = int(cx + crater_dist * math.cos(crater_angle))
            crater_y = int(cy + crater_dist * math.sin(crater_angle))
            crater_r = random.randint(max(2, size // 8), max(4, size // 4))

            # Dark crater interior
            crater_color = (max(0, color[0] - 30), max(0, color[1] - 28),
                          max(0, color[2] - 25), alpha)
            pygame.draw.circle(surf, crater_color, (crater_x, crater_y), crater_r)

            # Light rim on upper-left (facing light)
            rim_color = (min(255, color[0] + 20), min(255, color[1] + 18),
                        min(255, color[2] + 15), min(255, alpha + 10))
            pygame.draw.arc(surf, rim_color,
                          (crater_x - crater_r, crater_y - crater_r,
                           crater_r * 2, crater_r * 2),
                          math.pi * 0.75, math.pi * 1.75, 1)

        # === METALLIC ORE VEINS ===
        if self.composition == self.METALLIC and size > 20:
            num_veins = random.randint(1, 3)
            for _ in range(num_veins):
                vein_start_angle = random.uniform(0, math.pi * 2)
                vein_end_angle = vein_start_angle + random.uniform(0.5, 1.5)
                vein_dist = random.uniform(size * 0.3, size * 0.7)

                vein_color = random.choice([
                    (180, 150, 80, min(255, alpha + 30)),   # Gold
                    (120, 180, 200, min(255, alpha + 30)),  # Platinum
                    (160, 100, 60, min(255, alpha + 30)),   # Copper
                ])

                vein_points = []
                for t in range(6):
                    a = vein_start_angle + (vein_end_angle - vein_start_angle) * t / 5
                    d = vein_dist + random.uniform(-size * 0.1, size * 0.1)
                    vein_points.append((
                        int(cx + d * math.cos(a)),
                        int(cy + d * math.sin(a))
                    ))

                if len(vein_points) >= 2:
                    pygame.draw.lines(surf, vein_color, False, vein_points, 2)

        # === ICE CRYSTALS ===
        if self.composition == self.ICE and size > 15:
            for _ in range(random.randint(2, 5)):
                crystal_angle = random.uniform(0, math.pi * 2)
                crystal_dist = random.uniform(size * 0.2, size * 0.6)
                crystal_x = int(cx + crystal_dist * math.cos(crystal_angle))
                crystal_y = int(cy + crystal_dist * math.sin(crystal_angle))
                crystal_r = random.randint(2, max(3, size // 6))

                # Bright icy sparkle
                ice_color = (200, 230, 255, min(255, alpha + 40))
                pygame.draw.circle(surf, ice_color, (crystal_x, crystal_y), crystal_r)

        # === EDGE HIGHLIGHT ===
        # Draw lit edge (upper-left quadrant)
        highlight = (min(255, color[0] + 35), min(255, color[1] + 32),
                    min(255, color[2] + 28), min(255, alpha + 25))
        shadow = (max(0, color[0] - 20), max(0, color[1] - 18),
                 max(0, color[2] - 15), alpha)

        # Draw partial outline for 3D effect
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            # Get midpoint angle
            mid_angle = math.atan2((p1[1] + p2[1]) / 2 - cy,
                                   (p1[0] + p2[0]) / 2 - cx)
            # Upper-left edges get highlight
            if -math.pi < mid_angle < 0:
                pygame.draw.line(surf, highlight, p1, p2, 1)
            else:
                pygame.draw.line(surf, shadow, p1, p2, 1)

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
            int(200 * p['life'] / p['max_life'])
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
        """Create detailed debris piece with scorching and panel details"""
        surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
        cx, cy = size + 2, size + 2

        # Bake alpha based on depth (50-150 range)
        alpha = int(50 + depth * 100)

        # Debris type variation
        debris_type = random.choice(['hull_plate', 'structural', 'armor', 'tech'])

        # Random angular shape with jagged broken edges
        num_points = random.randint(5, 9)
        points = []
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2 + random.uniform(-0.25, 0.25)
            # More irregular edges for broken look
            r = size * random.uniform(0.4, 1.0)
            points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

        # Color based on debris type
        if debris_type == 'hull_plate':
            # Amarr golden-brown hull
            base_r, base_g, base_b = 85, 70, 50
            accent = (180, 150, 100, min(255, alpha + 20))
        elif debris_type == 'structural':
            # Dark gray framework
            base_r, base_g, base_b = 60, 55, 50
            accent = (100, 95, 85, min(255, alpha + 15))
        elif debris_type == 'armor':
            # Darker armor plating
            base_r, base_g, base_b = 50, 45, 40
            accent = (90, 85, 75, min(255, alpha + 20))
        else:  # tech
            # Blueish tech debris
            base_r, base_g, base_b = 50, 55, 65
            accent = (80, 120, 150, min(255, alpha + 25))

        # Apply atmospheric perspective (distant = more blue)
        distance_factor = 1.0 - depth
        blue_shift = int(distance_factor * 20)
        color = (max(0, min(255, base_r - int(distance_factor * 15) + random.randint(-10, 10))),
                max(0, min(255, base_g - int(distance_factor * 10) + random.randint(-8, 8))),
                max(0, min(255, base_b + blue_shift + random.randint(-5, 10))),
                alpha)

        # Draw base shape
        pygame.draw.polygon(surf, color, points)

        # === HULL PANEL LINES ===
        if size > 10:
            line_color = (max(0, color[0] - 15), max(0, color[1] - 12),
                         max(0, color[2] - 10), alpha)
            # Random panel lines
            for _ in range(random.randint(1, 3)):
                # Draw across the debris
                angle = random.uniform(0, math.pi)
                start = (int(cx + size * 0.6 * math.cos(angle)),
                        int(cy + size * 0.6 * math.sin(angle)))
                end = (int(cx - size * 0.6 * math.cos(angle)),
                      int(cy - size * 0.6 * math.sin(angle)))
                pygame.draw.line(surf, line_color, start, end, 1)

        # === SCORCHING / BURN MARKS ===
        for _ in range(random.randint(1, 4)):
            scorch_x = int(cx + random.uniform(-size * 0.5, size * 0.5))
            scorch_y = int(cy + random.uniform(-size * 0.5, size * 0.5))
            scorch_r = random.randint(max(2, size // 6), max(3, size // 3))

            # Dark scorch center
            scorch_color = (25, 20, 18, alpha)
            pygame.draw.circle(surf, scorch_color, (scorch_x, scorch_y), scorch_r)

            # Orange/red heat ring around fresh scorch
            if random.random() < 0.4:
                heat_color = (160, 60, 20, min(200, alpha + 40))
                pygame.draw.circle(surf, heat_color, (scorch_x, scorch_y),
                                 scorch_r + 2, 1)

        # === GLOWING HOT EDGES ===
        if random.random() < 0.3 and size > 8:
            # Some debris has glowing molten edges from recent damage
            glow_idx = random.randint(0, len(points) - 2)
            glow_start = points[glow_idx]
            glow_end = points[(glow_idx + 1) % len(points)]

            # Hot edge glow
            glow_color = (255, 120, 40, min(255, alpha + 60))
            pygame.draw.line(surf, glow_color, glow_start, glow_end, 2)

            # Brighter core
            core_color = (255, 200, 100, min(255, alpha + 80))
            mid_x = int((glow_start[0] + glow_end[0]) / 2)
            mid_y = int((glow_start[1] + glow_end[1]) / 2)
            pygame.draw.circle(surf, core_color, (mid_x, mid_y), 2)

        # === EDGE LIGHTING ===
        # Upper-left highlight, bottom-right shadow
        highlight = (min(255, color[0] + 30), min(255, color[1] + 25),
                    min(255, color[2] + 20), min(255, alpha + 20))
        shadow = (max(0, color[0] - 20), max(0, color[1] - 18),
                 max(0, color[2] - 15), alpha)

        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            mid_angle = math.atan2((p1[1] + p2[1]) / 2 - cy,
                                   (p1[0] + p2[0]) / 2 - cx)
            if -math.pi < mid_angle < 0:
                pygame.draw.line(surf, highlight, p1, p2, 1)
            else:
                pygame.draw.line(surf, shadow, p1, p2, 1)

        # === ACCENT DETAILS ===
        pygame.draw.polygon(surf, accent, points, 1)

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
        """Create detailed large wreckage sprite with authentic damage"""
        base_size = int(200 * scale)
        surf = pygame.Surface((base_size * 2 + 20, base_size + 20), pygame.SRCALPHA)
        cx, cy = base_size + 10, base_size // 2 + 10

        # Baked alpha for background clarity
        alpha = 130

        # Hull colors with baked alpha (Amarr gold/brown damaged)
        hull_dark = (55, 45, 35, alpha)
        hull_mid = (85, 70, 50, alpha)
        hull_light = (115, 95, 65, alpha)
        hull_accent = (140, 115, 80, min(255, alpha + 20))
        damage = (25, 20, 18, alpha)
        fire_glow = (200, 100, 40, min(200, alpha + 70))
        ember = (255, 150, 50, min(255, alpha + 80))

        if wreck_type == 'hull_section':
            # Large curved hull plate with detailed damage
            points = [
                (cx - base_size * 0.8, cy - base_size * 0.15),
                (cx - base_size * 0.65, cy - base_size * 0.4),
                (cx - base_size * 0.2, cy - base_size * 0.42),
                (cx + base_size * 0.4, cy - base_size * 0.35),
                (cx + base_size * 0.7, cy - base_size * 0.1),
                (cx + base_size * 0.65, cy + base_size * 0.2),
                (cx + base_size * 0.3, cy + base_size * 0.35),
                (cx - base_size * 0.5, cy + base_size * 0.3),
                (cx - base_size * 0.75, cy + base_size * 0.1),
            ]
            pygame.draw.polygon(surf, hull_mid, points)

            # Hull panel lines
            for i in range(4):
                line_y = int(cy - base_size * 0.25 + i * base_size * 0.15)
                pygame.draw.line(surf, hull_dark,
                               (int(cx - base_size * 0.6), line_y),
                               (int(cx + base_size * 0.5), line_y), 1)

            # Vertical ribbing
            for i in range(5):
                line_x = int(cx - base_size * 0.5 + i * base_size * 0.25)
                pygame.draw.line(surf, hull_dark,
                               (line_x, int(cy - base_size * 0.3)),
                               (line_x, int(cy + base_size * 0.25)), 2)

            # Damage holes with molten edges
            for _ in range(6):
                hx = int(cx + random.uniform(-base_size * 0.5, base_size * 0.4))
                hy = int(cy + random.uniform(-base_size * 0.25, base_size * 0.2))
                hr = random.randint(base_size // 12, base_size // 6)

                # Hole
                pygame.draw.circle(surf, damage, (hx, hy), hr)

                # Molten edge ring
                pygame.draw.circle(surf, fire_glow, (hx, hy), hr + 3, 2)

                # Ember core in some holes
                if random.random() < 0.4:
                    pygame.draw.circle(surf, ember, (hx, hy), max(2, hr // 2))

            # Edge highlight
            pygame.draw.polygon(surf, hull_light, points, 2)

        elif wreck_type == 'engine_block':
            # Cylindrical engine section with detailed nacelles
            # Main engine housing
            pygame.draw.ellipse(surf, hull_dark,
                              (cx - base_size * 0.65, cy - base_size * 0.35,
                               base_size * 1.3, base_size * 0.7))
            pygame.draw.ellipse(surf, hull_mid,
                              (cx - base_size * 0.55, cy - base_size * 0.28,
                               base_size * 1.1, base_size * 0.56))

            # Engine bell/nozzle
            nozzle_x = int(cx + base_size * 0.5)
            pygame.draw.circle(surf, (35, 30, 28, alpha), (nozzle_x, cy), int(base_size * 0.28))
            pygame.draw.circle(surf, (20, 18, 15, alpha), (nozzle_x, cy), int(base_size * 0.22))

            # Residual engine glow (dying)
            for r in range(int(base_size * 0.18), 0, -3):
                glow_alpha = int(80 * (r / (base_size * 0.18)))
                pygame.draw.circle(surf, (255, 120, 50, glow_alpha),
                                 (nozzle_x, cy), r)

            # Damage streaks
            for _ in range(4):
                streak_y = int(cy + random.uniform(-base_size * 0.2, base_size * 0.2))
                pygame.draw.line(surf, damage,
                               (int(cx - base_size * 0.4), streak_y),
                               (int(cx + base_size * 0.3), streak_y + random.randint(-10, 10)), 3)

            # Panel details
            pygame.draw.ellipse(surf, hull_light,
                              (cx - base_size * 0.55, cy - base_size * 0.28,
                               base_size * 1.1, base_size * 0.56), 2)

        elif wreck_type == 'bridge':
            # Command bridge section with windows and antenna
            bridge_points = [
                (cx - base_size * 0.4, cy + base_size * 0.25),
                (cx - base_size * 0.35, cy - base_size * 0.2),
                (cx - base_size * 0.15, cy - base_size * 0.35),
                (cx + base_size * 0.2, cy - base_size * 0.38),
                (cx + base_size * 0.45, cy - base_size * 0.15),
                (cx + base_size * 0.5, cy + base_size * 0.2),
            ]
            pygame.draw.polygon(surf, hull_mid, bridge_points)

            # Viewport windows (some broken, some dark)
            for i in range(5):
                wx = int(cx - base_size * 0.25 + i * base_size * 0.12)
                wy = int(cy - base_size * 0.18)
                w_width = int(base_size * 0.08)
                w_height = int(base_size * 0.06)

                if random.random() < 0.3:
                    # Broken window - dark with cracks
                    pygame.draw.rect(surf, (15, 12, 10, alpha), (wx, wy, w_width, w_height))
                    # Crack lines
                    pygame.draw.line(surf, (80, 70, 60, alpha),
                                   (wx, wy), (wx + w_width, wy + w_height), 1)
                else:
                    # Intact dark window
                    pygame.draw.rect(surf, (20, 35, 50, alpha), (wx, wy, w_width, w_height))
                    # Window frame
                    pygame.draw.rect(surf, hull_accent, (wx, wy, w_width, w_height), 1)

            # Antenna/sensor array (bent)
            pygame.draw.line(surf, hull_dark,
                           (int(cx + base_size * 0.1), int(cy - base_size * 0.35)),
                           (int(cx + base_size * 0.25), int(cy - base_size * 0.5)), 2)

            pygame.draw.polygon(surf, hull_light, bridge_points, 2)

        else:  # hangar
            # Open hangar bay with interior detail
            # Outer frame
            pygame.draw.rect(surf, hull_mid,
                           (int(cx - base_size * 0.55), int(cy - base_size * 0.3),
                            int(base_size * 1.1), int(base_size * 0.6)), border_radius=5)

            # Dark interior
            pygame.draw.rect(surf, (12, 10, 8, alpha),
                           (int(cx - base_size * 0.45), int(cy - base_size * 0.2),
                            int(base_size * 0.9), int(base_size * 0.4)))

            # Hangar floor lines
            for i in range(6):
                line_x = int(cx - base_size * 0.4 + i * base_size * 0.15)
                pygame.draw.line(surf, (40, 35, 30, alpha),
                               (line_x, int(cy - base_size * 0.15)),
                               (line_x, int(cy + base_size * 0.15)), 1)

            # Interior emergency lighting (faint red)
            pygame.draw.rect(surf, (80, 30, 20, min(100, alpha)),
                           (int(cx - base_size * 0.4), int(cy - base_size * 0.15),
                            int(base_size * 0.8), int(base_size * 0.3)))

            # Scattered debris inside
            for _ in range(3):
                dx = int(cx + random.uniform(-base_size * 0.3, base_size * 0.3))
                dy = int(cy + random.uniform(-base_size * 0.1, base_size * 0.1))
                pygame.draw.circle(surf, hull_dark, (dx, dy), random.randint(3, 8))

            # Frame highlight
            pygame.draw.rect(surf, hull_light,
                           (int(cx - base_size * 0.55), int(cy - base_size * 0.3),
                            int(base_size * 1.1), int(base_size * 0.6)), 2, border_radius=5)

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

    def set_enemy_faction(self, faction: str):
        """Set the enemy faction for background carrier images"""
        self.traffic.set_enemy_faction(faction)

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
