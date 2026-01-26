"""
Enhanced Background System for Minmatar Rebellion
Adds dynamic space backgrounds with asteroids, rings, nebulae, and distant ships
"""

import math
import random

import pygame

# Ship silhouette definitions (side profile shapes)
# Each is a list of (x, y) points normalized to 0-1 range
SHIP_SILHOUETTES = {
    # Minmatar style - angular, aggressive
    'frigate_minmatar': [
        (0.0, 0.5), (0.2, 0.3), (0.4, 0.2), (0.7, 0.15),
        (1.0, 0.5),  # nose
        (0.7, 0.85), (0.4, 0.8), (0.2, 0.7)
    ],
    'cruiser_minmatar': [
        (0.0, 0.4), (0.1, 0.25), (0.3, 0.2), (0.5, 0.15), (0.8, 0.2),
        (1.0, 0.5),  # nose
        (0.8, 0.8), (0.5, 0.85), (0.3, 0.8), (0.1, 0.75), (0.0, 0.6)
    ],
    'battleship_minmatar': [
        (0.0, 0.35), (0.05, 0.2), (0.2, 0.15), (0.4, 0.1), (0.6, 0.15), (0.85, 0.25),
        (1.0, 0.5),  # nose
        (0.85, 0.75), (0.6, 0.85), (0.4, 0.9), (0.2, 0.85), (0.05, 0.8), (0.0, 0.65)
    ],
    # Amarr style - sleek, golden curves
    'frigate_amarr': [
        (0.0, 0.5), (0.15, 0.35), (0.4, 0.25), (0.7, 0.3),
        (1.0, 0.5),  # nose
        (0.7, 0.7), (0.4, 0.75), (0.15, 0.65)
    ],
    'cruiser_amarr': [
        (0.0, 0.5), (0.1, 0.3), (0.25, 0.2), (0.5, 0.18), (0.75, 0.25),
        (1.0, 0.5),  # nose
        (0.75, 0.75), (0.5, 0.82), (0.25, 0.8), (0.1, 0.7)
    ],
    'battleship_amarr': [
        (0.0, 0.5), (0.08, 0.3), (0.2, 0.18), (0.4, 0.12), (0.6, 0.15), (0.8, 0.3),
        (1.0, 0.5),  # nose
        (0.8, 0.7), (0.6, 0.85), (0.4, 0.88), (0.2, 0.82), (0.08, 0.7)
    ],
}

# Faction colors
MINMATAR_COLORS = [
    (180, 100, 60),   # Rust orange
    (150, 80, 50),    # Dark rust
    (200, 120, 70),   # Light rust
]
AMARR_COLORS = [
    (200, 170, 80),   # Gold
    (180, 150, 60),   # Dark gold
    (220, 190, 100),  # Bright gold
]


class BackgroundShip:
    """A distant ship silhouette flying in the background"""

    def __init__(self, width, height, sprite_cache=None):
        self.width = width
        self.height = height

        # Pick faction - determines direction and color
        self.faction = random.choice(['minmatar', 'amarr'])

        # Pick ship class (affects size)
        self.ship_class = random.choices(
            ['frigate', 'cruiser', 'battleship'],
            weights=[0.5, 0.35, 0.15]  # More frigates than battleships
        )[0]

        # Size based on class and distance
        base_sizes = {'frigate': 25, 'cruiser': 45, 'battleship': 70}
        self.base_size = base_sizes[self.ship_class]

        # Distance factor (0.3 = far, 1.0 = close)
        self.distance = random.uniform(0.3, 0.8)
        self.size = int(self.base_size * self.distance)
        self.alpha = int(60 + self.distance * 120)  # Closer = more visible

        # Color based on faction
        if self.faction == 'minmatar':
            self.color = random.choice(MINMATAR_COLORS)
            # Minmatar fly left to right (retreating/flanking)
            self.x = -self.size
            self.y = random.randint(50, height - 50)
            self.vx = random.uniform(0.8, 1.5) * self.distance
            self.vy = random.uniform(-0.15, 0.15)
            self.facing_right = True
        else:
            self.color = random.choice(AMARR_COLORS)
            # Amarr fly right to left (attacking)
            self.x = width + self.size
            self.y = random.randint(50, height - 50)
            self.vx = random.uniform(-1.5, -0.8) * self.distance
            self.vy = random.uniform(-0.15, 0.15)
            self.facing_right = False

        # Engine glow
        self.engine_flicker = random.uniform(0, math.pi * 2)

        # Create the ship silhouette
        self.image = self._create_silhouette()

    def _create_silhouette(self):
        """Create a ship silhouette sprite"""
        silhouette_key = f'{self.ship_class}_{self.faction}'
        points_normalized = SHIP_SILHOUETTES.get(silhouette_key)

        if not points_normalized:
            # Fallback simple shape
            points_normalized = [(0, 0.5), (0.3, 0.2), (1, 0.5), (0.3, 0.8)]

        # Scale points to actual size
        ship_width = self.size
        ship_height = int(self.size * 0.5)

        points = []
        for px, py in points_normalized:
            x = int(px * ship_width)
            y = int(py * ship_height)
            points.append((x, y))

        # Flip if facing left
        if not self.facing_right:
            points = [(ship_width - x, y) for x, y in points]

        # Create surface
        surf = pygame.Surface((ship_width + 10, ship_height + 10), pygame.SRCALPHA)

        # Offset points for padding
        offset_points = [(x + 5, y + 5) for x, y in points]

        # Draw glow/outline
        glow_color = (*self.color, self.alpha // 3)
        pygame.draw.polygon(surf, glow_color, offset_points)

        # Draw main hull
        hull_color = (*self.color, self.alpha)
        pygame.draw.polygon(surf, hull_color, offset_points)

        # Draw darker outline
        outline_color = (self.color[0] // 2, self.color[1] // 2, self.color[2] // 2, self.alpha)
        pygame.draw.polygon(surf, outline_color, offset_points, 1)

        return surf

    def update(self, speed_mult=1.0):
        """Move the ship"""
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult
        self.engine_flicker += 0.2

    def is_offscreen(self):
        """Check if ship has left the screen"""
        margin = self.size + 50
        return (self.x < -margin or self.x > self.width + margin or
                self.y < -margin or self.y > self.height + margin)

    def draw(self, surface):
        """Draw the ship with engine glow"""
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect)

            # Draw engine glow
            engine_intensity = 0.5 + 0.5 * math.sin(self.engine_flicker)
            glow_alpha = int(self.alpha * 0.6 * engine_intensity)

            # Engine position (rear of ship)
            if self.facing_right:
                engine_x = int(self.x - self.size // 2)
            else:
                engine_x = int(self.x + self.size // 2)
            engine_y = int(self.y)

            # Draw engine glow
            glow_size = int(4 + self.distance * 6)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)

            if self.faction == 'minmatar':
                glow_color = (255, 150, 50, glow_alpha)  # Orange exhaust
            else:
                glow_color = (255, 220, 100, glow_alpha)  # Yellow exhaust

            pygame.draw.circle(glow_surf, glow_color, (glow_size, glow_size), glow_size)
            surface.blit(glow_surf, (engine_x - glow_size, engine_y - glow_size))


class SpaceBackground:
    """Scrolling space background with parallax layers"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Create layered background
        self.nebula_layer = self.create_nebula(width, height)
        self.star_field = self.create_star_field(100)
        self.asteroids = self.create_asteroid_field(30)

        # Background ships
        self.sprite_cache = {}  # Cache loaded ship sprites
        self.background_ships = []
        self.ship_spawn_timer = 0
        self.ship_spawn_interval = 120  # Frames between potential spawns
        self.max_background_ships = 8

        self.scroll_y = 0

    def create_nebula(self, width, height):
        """Create a darker nebula background for contrast"""
        surface = pygame.Surface((width, height * 2))

        # Dark purple/blue gradient
        for y in range(height * 2):
            progress = y / (height * 2)
            r = int(15 + math.sin(progress * math.pi) * 10)
            g = int(10 + math.sin(progress * math.pi * 1.5) * 8)
            b = int(35 + math.sin(progress * math.pi * 0.8) * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

        # Add nebula clouds
        for _ in range(20):
            x = random.randint(0, width)
            y = random.randint(0, height * 2)
            size = random.randint(100, 300)

            # Semi-transparent purple/orange clouds
            cloud_color = random.choice([
                (80, 40, 120, 30),   # Purple
                (100, 50, 80, 25),   # Magenta
                (60, 30, 90, 20)     # Deep purple
            ])

            cloud_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(cloud_surf, cloud_color, (size//2, size//2), size//2)
            surface.blit(cloud_surf, (x - size//2, y - size//2))

        return surface

    def create_star_field(self, count):
        """Create distant stars"""
        stars = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height * 2)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            stars.append({
                'x': x, 'y': y, 'size': size,
                'color': (brightness, brightness, brightness),
                'speed': 0.2
            })
        return stars

    def create_asteroid_field(self, count):
        """Create scrolling asteroids for depth"""
        asteroids = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height * 2)
            size = random.randint(15, 45)
            speed = random.uniform(1.0, 3.0)
            rotation = random.uniform(0, math.pi * 2)

            asteroids.append({
                'x': x, 'y': y, 'size': size,
                'speed': speed, 'rotation': rotation,
                'color': (100, 90, 80)
            })
        return asteroids

    def update(self, speed=1.0):
        """Scroll background"""
        self.scroll_y += speed

        # Wrap around
        if self.scroll_y >= self.height:
            self.scroll_y = 0

        # Update stars
        for star in self.star_field:
            star['y'] += star['speed'] * speed
            if star['y'] > self.height * 2:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)

        # Update asteroids
        for asteroid in self.asteroids:
            asteroid['y'] += asteroid['speed'] * speed
            asteroid['rotation'] += 0.02

            if asteroid['y'] > self.height * 2:
                asteroid['y'] = -asteroid['size']
                asteroid['x'] = random.randint(0, self.width)

        # Update background ships
        for ship in self.background_ships[:]:
            ship.update(speed)
            if ship.is_offscreen():
                self.background_ships.remove(ship)

        # Spawn new background ships occasionally
        self.ship_spawn_timer += 1
        if (self.ship_spawn_timer >= self.ship_spawn_interval and
                len(self.background_ships) < self.max_background_ships):
            if random.random() < 0.5:  # 50% chance each interval
                self.background_ships.append(
                    BackgroundShip(self.width, self.height, self.sprite_cache)
                )
            self.ship_spawn_timer = 0

    def draw(self, surface):
        """Draw all background layers"""
        # Draw nebula
        y_offset = -self.height + int(self.scroll_y)
        surface.blit(self.nebula_layer, (0, y_offset))

        # Draw stars
        for star in self.star_field:
            y = int(star['y'] - self.scroll_y)
            if 0 <= y <= self.height:
                pygame.draw.circle(surface, star['color'],
                                   (int(star['x']), y), star['size'])

        # Draw background ships (behind asteroids, in front of stars)
        for ship in self.background_ships:
            ship.draw(surface)

        # Draw asteroids
        for asteroid in self.asteroids:
            y = int(asteroid['y'] - self.scroll_y)
            if -asteroid['size'] <= y <= self.height + asteroid['size']:
                self.draw_asteroid(surface, asteroid['x'], y,
                                   asteroid['size'], asteroid['rotation'])

    def draw_asteroid(self, surface, x, y, size, rotation):
        """Draw a rocky asteroid"""
        points = []
        segments = 8

        for i in range(segments):
            angle = (i / segments) * math.pi * 2 + rotation
            distance = size * random.uniform(0.7, 1.0)
            px = x + math.cos(angle) * distance
            py = y + math.sin(angle) * distance
            points.append((int(px), int(py)))

        # Draw filled polygon
        pygame.draw.polygon(surface, (80, 75, 70), points)
        # Dark outline
        pygame.draw.polygon(surface, (40, 35, 30), points, 2)
