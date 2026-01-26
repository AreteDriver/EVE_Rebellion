"""
Enhanced Background System for Minmatar Rebellion
Adds dynamic space backgrounds with asteroids, rings, nebulae, and distant ships
"""

import pygame
import random
import math
import os

# Background ship sprites (scaled down and dimmed for distance effect)
BACKGROUND_SHIP_TYPES = [
    'apocalypse', 'abaddon', 'harbinger', 'prophecy',  # Amarr
    'rifter', 'wolf', 'jaguar',  # Minmatar
    'bestower', 'omen', 'maller',  # Various
]


class BackgroundShip:
    """A distant ship flying in the background"""

    def __init__(self, width, height, sprite_cache):
        self.width = width
        self.height = height
        self.sprite_cache = sprite_cache

        # Pick a random ship type
        self.ship_type = random.choice(BACKGROUND_SHIP_TYPES)

        # Scale and appearance (smaller = more distant)
        self.scale = random.uniform(0.08, 0.2)
        self.alpha = int(40 + self.scale * 150)  # More distant = more transparent

        # Position - spawn from top or sides
        spawn_side = random.choice(['top', 'left', 'right'])
        if spawn_side == 'top':
            self.x = random.randint(0, width)
            self.y = -50
            self.vx = random.uniform(-0.3, 0.3)
            self.vy = random.uniform(0.3, 1.0) * (1 + self.scale * 2)
        elif spawn_side == 'left':
            self.x = -50
            self.y = random.randint(0, height)
            self.vx = random.uniform(0.5, 1.2) * (1 + self.scale * 2)
            self.vy = random.uniform(-0.2, 0.5)
        else:  # right
            self.x = width + 50
            self.y = random.randint(0, height)
            self.vx = random.uniform(-1.2, -0.5) * (1 + self.scale * 2)
            self.vy = random.uniform(-0.2, 0.5)

        # Load and prepare sprite
        self.image = self._load_ship_sprite()

    def _load_ship_sprite(self):
        """Load ship sprite, scaled and dimmed for background"""
        # Try to load from eve_renders first
        paths_to_try = [
            f'assets/eve_renders/{self.ship_type}.png',
            f'assets/ship_sprites/{self.ship_type}_render_256.png',
        ]

        original = None
        for path in paths_to_try:
            if os.path.exists(path):
                try:
                    original = pygame.image.load(path).convert_alpha()
                    break
                except pygame.error:
                    continue

        if original is None:
            # Fallback: create a simple ship shape
            size = int(30 * self.scale)
            surf = pygame.Surface((size, size), pygame.SRCALPHA)
            color = (100, 100, 120, self.alpha)
            points = [(size//2, 0), (size, size), (size//2, size*3//4), (0, size)]
            pygame.draw.polygon(surf, color, points)
            return surf

        # Scale down
        orig_w, orig_h = original.get_size()
        new_w = int(orig_w * self.scale)
        new_h = int(orig_h * self.scale)
        if new_w < 5 or new_h < 5:
            new_w, new_h = max(5, new_w), max(5, new_h)

        scaled = pygame.transform.smoothscale(original, (new_w, new_h))

        # Apply transparency/dimming
        scaled.set_alpha(self.alpha)

        return scaled

    def update(self, speed_mult=1.0):
        """Move the ship"""
        self.x += self.vx * speed_mult
        self.y += self.vy * speed_mult

    def is_offscreen(self):
        """Check if ship has left the screen"""
        margin = 100
        return (self.x < -margin or self.x > self.width + margin or
                self.y < -margin or self.y > self.height + margin)

    def draw(self, surface):
        """Draw the ship"""
        if self.image:
            rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(self.image, rect)


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
