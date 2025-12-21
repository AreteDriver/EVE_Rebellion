"""
Enhanced Background System for Minmatar Rebellion
Adds dynamic space backgrounds with asteroids, rings, and nebulae
"""

import pygame
import random
import math

class SpaceBackground:
    """Scrolling space background with parallax layers"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        # Create layered background
        self.nebula_layer = self.create_nebula(width, height)
        self.star_field = self.create_star_field(100)
        self.asteroids = self.create_asteroid_field(30)
        
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
