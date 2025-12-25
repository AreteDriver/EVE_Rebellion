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

        # Background carriers and fighters
        self.carriers = self.create_carriers(2)
        self.bg_fighters = []  # Fighters launched from carriers

        self.scroll_y = 0
        self.carrier_spawn_timer = 0
        
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

    def create_carriers(self, count):
        """Create distant carrier ships in the background"""
        carriers = []
        for i in range(count):
            # Carriers start off-screen and drift across
            carriers.append({
                'x': random.randint(-200, self.width + 200),
                'y': random.randint(-100, self.height // 2),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(0.2, 0.5),
                'size': random.randint(80, 140),
                'alpha': random.randint(40, 70),  # Semi-transparent (distant)
                'launch_timer': random.randint(0, 200),
                'launch_cooldown': random.randint(180, 300),
                'rotation': random.uniform(-0.1, 0.1)
            })
        return carriers

    def spawn_fighter(self, carrier):
        """Spawn a fighter from a carrier"""
        fighter = {
            'x': carrier['x'],
            'y': carrier['y'] + carrier['size'] // 3,
            'vx': random.uniform(-1, 1),
            'vy': random.uniform(1.5, 3.0),
            'size': random.randint(6, 12),
            'alpha': carrier['alpha'] + 20,
            'lifetime': random.randint(150, 250)
        }
        self.bg_fighters.append(fighter)
    
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

        # Update carriers
        for carrier in self.carriers:
            carrier['x'] += carrier['vx']
            carrier['y'] += carrier['vy'] * speed

            # Launch fighters periodically
            carrier['launch_timer'] += 1
            if carrier['launch_timer'] >= carrier['launch_cooldown']:
                carrier['launch_timer'] = 0
                self.spawn_fighter(carrier)

            # Respawn carrier when off screen
            if carrier['y'] > self.height + carrier['size']:
                carrier['y'] = -carrier['size'] * 2
                carrier['x'] = random.randint(50, self.width - 50)
                carrier['vx'] = random.uniform(-0.3, 0.3)

        # Update background fighters
        for fighter in self.bg_fighters[:]:
            fighter['x'] += fighter['vx']
            fighter['y'] += fighter['vy'] * speed
            fighter['lifetime'] -= 1

            # Remove dead or off-screen fighters
            if fighter['lifetime'] <= 0 or fighter['y'] > self.height + 50:
                self.bg_fighters.remove(fighter)
    
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

        # Draw distant carriers (behind asteroids)
        for carrier in self.carriers:
            self.draw_carrier(surface, carrier)

        # Draw background fighters
        for fighter in self.bg_fighters:
            self.draw_bg_fighter(surface, fighter)

        # Draw asteroids
        for asteroid in self.asteroids:
            y = int(asteroid['y'] - self.scroll_y)
            if -asteroid['size'] <= y <= self.height + asteroid['size']:
                self.draw_asteroid(surface, asteroid['x'], y,
                                 asteroid['size'], asteroid['rotation'])

    def draw_carrier(self, surface, carrier):
        """Draw a distant Amarr carrier silhouette"""
        x, y = int(carrier['x']), int(carrier['y'])
        size = carrier['size']
        alpha = carrier['alpha']

        # Create carrier surface with transparency
        carrier_surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)

        # Amarr carrier shape - elongated golden hull
        hull_color = (120, 90, 40, alpha)
        highlight = (160, 130, 70, alpha)
        dark = (60, 45, 20, alpha)

        cx, cy = size, size // 2

        # Main hull - elongated diamond/oval
        hull_points = [
            (cx - size * 0.8, cy),           # Left
            (cx - size * 0.3, cy - size * 0.3),  # Top-left
            (cx + size * 0.5, cy - size * 0.2),  # Top-right
            (cx + size * 0.8, cy),           # Right (front)
            (cx + size * 0.5, cy + size * 0.2),  # Bottom-right
            (cx - size * 0.3, cy + size * 0.3),  # Bottom-left
        ]
        pygame.draw.polygon(carrier_surf, hull_color, hull_points)
        pygame.draw.polygon(carrier_surf, dark, hull_points, 2)

        # Bridge/dome
        pygame.draw.ellipse(carrier_surf, highlight,
                          (cx - size * 0.2, cy - size * 0.15, size * 0.4, size * 0.3))

        # Engine glows at rear
        for offset in [-0.15, 0, 0.15]:
            ey = cy + int(size * offset)
            pygame.draw.circle(carrier_surf, (255, 150, 50, alpha + 30),
                             (int(cx - size * 0.7), ey), 4)
            pygame.draw.circle(carrier_surf, (255, 200, 100, alpha + 50),
                             (int(cx - size * 0.7), ey), 2)

        # Hangar bay (where fighters launch)
        pygame.draw.rect(carrier_surf, (40, 30, 20, alpha),
                        (int(cx - size * 0.1), int(cy + size * 0.2), int(size * 0.3), int(size * 0.15)))

        surface.blit(carrier_surf, (x - size, y - size // 2))

    def draw_bg_fighter(self, surface, fighter):
        """Draw a small background fighter silhouette"""
        x, y = int(fighter['x']), int(fighter['y'])
        size = fighter['size']
        alpha = fighter['alpha']

        # Simple triangle fighter shape
        color = (140, 110, 50, alpha)
        engine_color = (255, 150, 80, min(255, alpha + 40))

        # Fighter triangle pointing down (toward player)
        points = [
            (x, y - size),      # Nose
            (x - size // 2, y + size // 2),  # Left wing
            (x + size // 2, y + size // 2),  # Right wing
        ]

        # Draw on temp surface for alpha
        fighter_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        local_points = [(p[0] - x + size, p[1] - y + size) for p in points]
        pygame.draw.polygon(fighter_surf, color, local_points)

        # Engine glow
        pygame.draw.circle(fighter_surf, engine_color, (size, size - size // 3), 2)

        surface.blit(fighter_surf, (x - size, y - size))
    
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
