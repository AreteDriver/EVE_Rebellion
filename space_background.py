"""
Enhanced Background System for Minmatar Rebellion
Adds dynamic space backgrounds with asteroids, rings, and nebulae
Supports directional scrolling for varied level orientations
"""

import pygame
import random
import math

class SpaceBackground:
    """Scrolling space background with parallax layers and directional support"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Current scroll direction (dx, dy) - default is vertical scrolling down
        self.scroll_direction = (0, 1)

        # Create layered background (2x size for seamless wrapping in both directions)
        self.nebula_layer = self.create_nebula(width * 2, height * 2)
        self.star_field = self.create_star_field(150)
        self.asteroids = self.create_asteroid_field(40)

        self.scroll_x = 0
        self.scroll_y = 0

    def set_direction(self, direction_tuple):
        """Set the scroll direction (dx, dy) - background moves opposite to flight"""
        self.scroll_direction = direction_tuple
        
    def create_nebula(self, width, height):
        """Create a darker nebula background for contrast (supports 2x size for scrolling)"""
        surface = pygame.Surface((width, height))

        # Dark purple/blue gradient (diagonal for both directions)
        for y in range(height):
            for x in range(0, width, 4):  # Skip pixels for performance
                progress = (x + y) / (width + height)
                r = int(15 + math.sin(progress * math.pi) * 10)
                g = int(10 + math.sin(progress * math.pi * 1.5) * 8)
                b = int(35 + math.sin(progress * math.pi * 0.8) * 15)
                pygame.draw.line(surface, (r, g, b), (x, y), (x + 4, y))

        # Add nebula clouds
        for _ in range(30):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(100, 300)

            # Semi-transparent purple/orange clouds
            cloud_color = random.choice([
                (80, 40, 120, 30),   # Purple
                (100, 50, 80, 25),   # Magenta
                (60, 30, 90, 20)     # Deep purple
            ])

            cloud_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(cloud_surf, cloud_color, (size // 2, size // 2), size // 2)
            surface.blit(cloud_surf, (x - size // 2, y - size // 2))

        return surface
    
    def create_star_field(self, count):
        """Create distant stars that work with any scroll direction"""
        stars = []
        for _ in range(count):
            x = random.randint(-self.width, self.width * 2)
            y = random.randint(-self.height, self.height * 2)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            stars.append({
                'x': x, 'y': y, 'size': size,
                'color': (brightness, brightness, brightness),
                'speed': random.uniform(0.15, 0.3)
            })
        return stars

    def create_asteroid_field(self, count):
        """Create scrolling asteroids for depth (works with any direction)"""
        asteroids = []
        for _ in range(count):
            x = random.randint(-self.width, self.width * 2)
            y = random.randint(-self.height, self.height * 2)
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
        """Scroll background based on current direction"""
        dx, dy = self.scroll_direction

        self.scroll_x += dx * speed
        self.scroll_y += dy * speed

        # Wrap scroll positions
        if self.scroll_x >= self.width:
            self.scroll_x -= self.width
        elif self.scroll_x <= -self.width:
            self.scroll_x += self.width

        if self.scroll_y >= self.height:
            self.scroll_y -= self.height
        elif self.scroll_y <= -self.height:
            self.scroll_y += self.height

        # Update stars based on scroll direction
        for star in self.star_field:
            star['x'] += dx * star['speed'] * speed
            star['y'] += dy * star['speed'] * speed

            # Wrap stars around screen edges
            if star['x'] > self.width * 1.5:
                star['x'] = -self.width * 0.5
                star['y'] = random.randint(0, self.height)
            elif star['x'] < -self.width * 0.5:
                star['x'] = self.width * 1.5
                star['y'] = random.randint(0, self.height)

            if star['y'] > self.height * 1.5:
                star['y'] = -self.height * 0.5
                star['x'] = random.randint(0, self.width)
            elif star['y'] < -self.height * 0.5:
                star['y'] = self.height * 1.5
                star['x'] = random.randint(0, self.width)

        # Update asteroids based on scroll direction
        for asteroid in self.asteroids:
            asteroid['x'] += dx * asteroid['speed'] * speed
            asteroid['y'] += dy * asteroid['speed'] * speed
            asteroid['rotation'] += 0.02

            # Wrap asteroids around screen edges
            if asteroid['x'] > self.width + asteroid['size']:
                asteroid['x'] = -asteroid['size']
                asteroid['y'] = random.randint(0, self.height)
            elif asteroid['x'] < -asteroid['size']:
                asteroid['x'] = self.width + asteroid['size']
                asteroid['y'] = random.randint(0, self.height)

            if asteroid['y'] > self.height + asteroid['size']:
                asteroid['y'] = -asteroid['size']
                asteroid['x'] = random.randint(0, self.width)
            elif asteroid['y'] < -asteroid['size']:
                asteroid['y'] = self.height + asteroid['size']
                asteroid['x'] = random.randint(0, self.width)

    def draw(self, surface):
        """Draw all background layers"""
        # Draw nebula with tiled wrapping for any scroll direction
        nebula_w = self.nebula_layer.get_width()
        nebula_h = self.nebula_layer.get_height()

        # Calculate base offsets for tiling
        base_x = int(-self.scroll_x * 0.3) % nebula_w - nebula_w
        base_y = int(-self.scroll_y * 0.3) % nebula_h - nebula_h

        # Tile the nebula to cover the screen
        for tile_x in range(base_x, self.width + nebula_w, nebula_w):
            for tile_y in range(base_y, self.height + nebula_h, nebula_h):
                surface.blit(self.nebula_layer, (tile_x, tile_y))

        # Draw stars
        for star in self.star_field:
            sx = int(star['x'])
            sy = int(star['y'])
            if -5 <= sx <= self.width + 5 and -5 <= sy <= self.height + 5:
                pygame.draw.circle(surface, star['color'], (sx, sy), star['size'])

        # Draw asteroids
        for asteroid in self.asteroids:
            ax = int(asteroid['x'])
            ay = int(asteroid['y'])
            if (-asteroid['size'] <= ax <= self.width + asteroid['size'] and
                    -asteroid['size'] <= ay <= self.height + asteroid['size']):
                self.draw_asteroid(surface, ax, ay,
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
