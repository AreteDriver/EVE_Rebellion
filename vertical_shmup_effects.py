"""
VERTICAL SHMUP WEAPON EFFECTS
EVE Rebellion - Devil Blade Reboot Visual Style

Visual effects for:
- Projectile trails (autocannon, missiles, lasers)
- Muzzle flashes
- Impact particles
- Heat visualization
- Berserk aura
- Point-blank kill feedback
- Boss attack patterns
"""

import pygame
import math
import random
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class Particle:
    """Individual particle for effects"""
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    color: Tuple[int, int, int]
    size: float
    fade: bool = True


class WeaponEffects:
    """
    Visual effects system for vertical shmup weapons.
    All effects use lightweight particle systems.
    """
    
    def __init__(self):
        self.particles: List[Particle] = []
        self.muzzle_flashes: List[dict] = []
        
        # Effect colors (EVE-themed)
        self.COLOR_AUTOCANNON = (255, 200, 100)  # Orange tracer
        self.COLOR_MISSILE = (255, 100, 50)       # Red flame
        self.COLOR_LASER = (100, 200, 255)        # Blue beam
        self.COLOR_ROCKET = (255, 150, 0)         # Orange exhaust
        self.COLOR_EXPLOSION = (255, 100, 0)      # Red-orange
        self.COLOR_IMPACT = (255, 255, 200)       # Yellow spark
        self.COLOR_BERSERK = (255, 50, 50)        # Red aura
        self.COLOR_HEAT_LOW = (255, 255, 100)     # Yellow
        self.COLOR_HEAT_MED = (255, 150, 50)      # Orange
        self.COLOR_HEAT_HIGH = (255, 50, 50)      # Red
    
    def update(self, dt: float):
        """Update all active effects"""
        # Update particles
        for particle in self.particles[:]:
            particle.life -= dt
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            
            # Gravity (optional)
            particle.vy += 50 * dt
            
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update muzzle flashes
        for flash in self.muzzle_flashes[:]:
            flash['life'] -= dt
            if flash['life'] <= 0:
                self.muzzle_flashes.remove(flash)
    
    def render(self, surface: pygame.Surface):
        """Render all active effects"""
        # Render particles
        for particle in self.particles:
            alpha = int(255 * (particle.life / particle.max_life)) if particle.fade else 255
            alpha = max(0, min(255, alpha))
            
            # Create color with alpha (unused - pygame.draw doesn't support alpha)
            _color = (*particle.color, alpha)
            
            # Draw particle
            if particle.size > 2:
                # Circle for larger particles
                pygame.draw.circle(
                    surface,
                    particle.color,  # pygame.draw doesn't support alpha
                    (int(particle.x), int(particle.y)),
                    int(particle.size)
                )
            else:
                # Pixel for small particles
                if 0 <= particle.x < surface.get_width() and 0 <= particle.y < surface.get_height():
                    surface.set_at((int(particle.x), int(particle.y)), particle.color)
        
        # Render muzzle flashes
        for flash in self.muzzle_flashes:
            alpha = int(255 * (flash['life'] / flash['max_life']))
            size = flash['size'] * (flash['life'] / flash['max_life'])
            
            pygame.draw.circle(
                surface,
                flash['color'],
                (int(flash['x']), int(flash['y'])),
                int(size)
            )
    
    # === WEAPON EFFECTS ===
    
    def autocannon_muzzle_flash(self, x: float, y: float, angle: float = 0):
        """
        Small muzzle flash for autocannon.
        
        Args:
            x, y: Position
            angle: Direction (radians, 0 = up)
        """
        self.muzzle_flashes.append({
            'x': x,
            'y': y,
            'size': 8,
            'color': self.COLOR_AUTOCANNON,
            'life': 0.05,
            'max_life': 0.05
        })
    
    def autocannon_tracer(self, x: float, y: float, angle: float = 0):
        """
        Autocannon projectile trail.
        
        Args:
            x, y: Current projectile position
            angle: Direction (radians)
        """
        # Small trail particle
        self.particles.append(Particle(
            x=x,
            y=y,
            vx=0,
            vy=0,
            life=0.1,
            max_life=0.1,
            color=self.COLOR_AUTOCANNON,
            size=2,
            fade=True
        ))
    
    def missile_trail(self, x: float, y: float, angle: float):
        """
        Missile smoke trail.
        
        Args:
            x, y: Current missile position
            angle: Direction (radians)
        """
        # Spawn multiple smoke particles
        for _ in range(2):
            spread = random.uniform(-0.3, 0.3)
            vx = math.cos(angle + math.pi + spread) * 30
            vy = math.sin(angle + math.pi + spread) * 30
            
            self.particles.append(Particle(
                x=x + random.uniform(-2, 2),
                y=y + random.uniform(-2, 2),
                vx=vx,
                vy=vy,
                life=0.5,
                max_life=0.5,
                color=(200, 200, 200),  # Gray smoke
                size=4,
                fade=True
            ))
    
    def laser_beam(self, x1: float, y1: float, x2: float, y2: float):
        """
        Draw laser beam from source to target.
        
        Args:
            x1, y1: Beam start
            x2, y2: Beam end
        """
        # Beam is drawn separately (not particle-based)
        # But we add glow particles along the beam
        
        length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        steps = int(length / 10)
        
        for i in range(steps):
            t = i / max(steps, 1)
            x = x1 + (x2 - x1) * t
            y = y1 + (y2 - y1) * t
            
            self.particles.append(Particle(
                x=x + random.uniform(-2, 2),
                y=y + random.uniform(-2, 2),
                vx=0,
                vy=0,
                life=0.15,
                max_life=0.15,
                color=self.COLOR_LASER,
                size=3,
                fade=True
            ))
    
    def rocket_exhaust(self, x: float, y: float, angle: float):
        """
        Heavy rocket exhaust flame.
        
        Args:
            x, y: Rocket position
            angle: Direction (radians)
        """
        for _ in range(3):
            spread = random.uniform(-0.5, 0.5)
            speed = random.uniform(50, 100)
            vx = math.cos(angle + math.pi + spread) * speed
            vy = math.sin(angle + math.pi + spread) * speed
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=vx,
                vy=vy,
                life=0.3,
                max_life=0.3,
                color=self.COLOR_ROCKET,
                size=6,
                fade=True
            ))
    
    # === IMPACT EFFECTS ===
    
    def impact_sparks(self, x: float, y: float, count: int = 8):
        """
        Sparks on projectile impact.
        
        Args:
            x, y: Impact position
            count: Number of sparks
        """
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=0.2,
                max_life=0.2,
                color=self.COLOR_IMPACT,
                size=2,
                fade=True
            ))
    
    def explosion_small(self, x: float, y: float):
        """
        Small explosion (enemy death).
        
        Args:
            x, y: Explosion center
        """
        # Flash
        self.muzzle_flashes.append({
            'x': x,
            'y': y,
            'size': 30,
            'color': (255, 255, 255),
            'life': 0.1,
            'max_life': 0.1
        })
        
        # Debris particles
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 200)
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=0.5,
                max_life=0.5,
                color=self.COLOR_EXPLOSION,
                size=random.randint(2, 5),
                fade=True
            ))
    
    def explosion_large(self, x: float, y: float):
        """
        Large explosion (boss death).
        
        Args:
            x, y: Explosion center
        """
        # Multiple flash rings
        for i in range(3):
            self.muzzle_flashes.append({
                'x': x,
                'y': y,
                'size': 50 + i * 20,
                'color': (255, 200, 100) if i % 2 else (255, 100, 50),
                'life': 0.3 + i * 0.1,
                'max_life': 0.3 + i * 0.1
            })
        
        # Heavy debris
        for _ in range(50):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 300)
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=1.0,
                color=random.choice([
                    self.COLOR_EXPLOSION,
                    (255, 150, 50),
                    (200, 100, 50)
                ]),
                size=random.randint(4, 10),
                fade=True
            ))
    
    def pointblank_burst(self, x: float, y: float):
        """
        Special effect for point-blank kill (x4 multiplier).
        Visual confirmation of max score.
        
        Args:
            x, y: Kill position
        """
        # Bright flash
        self.muzzle_flashes.append({
            'x': x,
            'y': y,
            'size': 40,
            'color': (255, 255, 0),  # Bright yellow
            'life': 0.15,
            'max_life': 0.15
        })
        
        # Ring of particles
        for i in range(12):
            angle = (i / 12) * 2 * math.pi
            speed = 200
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=0.3,
                max_life=0.3,
                color=(255, 255, 100),
                size=4,
                fade=True
            ))
    
    # === HEAT/BERSERK EFFECTS ===
    
    def heat_aura(self, x: float, y: float, heat_percent: float):
        """
        Aura around player based on Heat level.
        
        Args:
            x, y: Player position
            heat_percent: Heat level (0.0 to 1.0)
        """
        if heat_percent < 0.25:
            return  # No aura below 25%
        
        # Color shifts with Heat
        if heat_percent < 0.5:
            color = self.COLOR_HEAT_LOW
        elif heat_percent < 0.75:
            color = self.COLOR_HEAT_MED
        else:
            color = self.COLOR_HEAT_HIGH
        
        # Spawn aura particles
        if random.random() < heat_percent:  # More particles = higher Heat
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(10, 20)
            
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            
            self.particles.append(Particle(
                x=px,
                y=py,
                vx=math.cos(angle) * 30,
                vy=math.sin(angle) * 30,
                life=0.5,
                max_life=0.5,
                color=color,
                size=3,
                fade=True
            ))
    
    def berserk_pulse(self, x: float, y: float):
        """
        Pulse effect when Berserk activates.
        
        Args:
            x, y: Player position
        """
        # Expanding ring
        for i in range(3):
            self.muzzle_flashes.append({
                'x': x,
                'y': y,
                'size': 50 + i * 30,
                'color': self.COLOR_BERSERK,
                'life': 0.5 + i * 0.2,
                'max_life': 0.5 + i * 0.2
            })
        
        # Particle burst
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 250)
            
            self.particles.append(Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=0.8,
                max_life=0.8,
                color=self.COLOR_BERSERK,
                size=5,
                fade=True
            ))
    
    def berserk_aura(self, x: float, y: float):
        """
        Continuous aura while Berserk active.
        
        Args:
            x, y: Player position
        """
        # Aggressive red aura
        for _ in range(3):
            angle = random.uniform(0, 2 * math.pi)
            radius = random.uniform(15, 30)
            
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            
            self.particles.append(Particle(
                x=px,
                y=py,
                vx=math.cos(angle) * 50,
                vy=math.sin(angle) * 50,
                life=0.4,
                max_life=0.4,
                color=self.COLOR_BERSERK,
                size=4,
                fade=True
            ))
    
    # === BOSS EFFECTS ===
    
    def boss_spawn_portal(self, x: float, y: float):
        """
        Boss warp-in effect.
        
        Args:
            x, y: Spawn position
        """
        # Spiral particles
        for i in range(50):
            angle = (i / 50) * 4 * math.pi  # Two full rotations
            radius = 100 - (i / 50) * 100   # Shrink to center
            
            px = x + math.cos(angle) * radius
            py = y + math.sin(angle) * radius
            
            # Velocity toward center
            vx = -math.cos(angle) * 200
            vy = -math.sin(angle) * 200
            
            self.particles.append(Particle(
                x=px,
                y=py,
                vx=vx,
                vy=vy,
                life=0.5,
                max_life=0.5,
                color=(150, 100, 255),  # Purple
                size=4,
                fade=True
            ))
    
    def boss_charge_warning(self, x: float, y: float):
        """
        Visual warning for boss attack charging.
        
        Args:
            x, y: Boss position
        """
        # Pulsing glow
        self.muzzle_flashes.append({
            'x': x,
            'y': y,
            'size': 60,
            'color': (255, 50, 50),
            'life': 0.3,
            'max_life': 0.3
        })


# === INTEGRATION EXAMPLE ===

class ExamplePlayer:
    """Example player sprite with weapon effects"""
    
    def __init__(self, effects: WeaponEffects):
        self.x = 400
        self.y = 500
        self.effects = effects
        self.heat = 0.0
        self.berserk = False
    
    def fire_autocannon(self):
        """Fire autocannon with muzzle flash"""
        self.effects.autocannon_muzzle_flash(self.x, self.y - 10)
    
    def update(self, dt: float):
        """Update player effects each frame"""
        # Heat aura
        self.effects.heat_aura(self.x, self.y, self.heat)
        
        # Berserk aura
        if self.berserk:
            self.effects.berserk_aura(self.x, self.y)


class ExampleProjectile:
    """Example projectile with trail"""
    
    def __init__(self, x: float, y: float, effects: WeaponEffects):
        self.x = x
        self.y = y
        self.vy = -300  # Moving up
        self.effects = effects
        self.type = "autocannon"
    
    def update(self, dt: float):
        """Update projectile and spawn trail"""
        self.y += self.vy * dt
        
        # Spawn trail particle
        if self.type == "autocannon":
            self.effects.autocannon_tracer(self.x, self.y)
        elif self.type == "missile":
            self.effects.missile_trail(self.x, self.y, -math.pi/2)
    
    def on_hit(self, enemy_x: float, enemy_y: float):
        """Called when projectile hits enemy"""
        self.effects.impact_sparks(enemy_x, enemy_y, count=8)


if __name__ == "__main__":
    print("=== VERTICAL SHMUP WEAPON EFFECTS ===")
    print()
    print("Weapon Effects:")
    print("  - Autocannon: Muzzle flash + orange tracer")
    print("  - Missile: Smoke trail + red flame")
    print("  - Laser: Blue beam glow")
    print("  - Rocket: Heavy orange exhaust")
    print()
    print("Impact Effects:")
    print("  - Sparks (8 particles)")
    print("  - Small explosion (20 particles)")
    print("  - Large explosion (50 particles)")
    print("  - Point-blank burst (12-particle ring + flash)")
    print()
    print("Heat/Berserk:")
    print("  - Heat aura (color shifts: yellow → orange → red)")
    print("  - Berserk pulse (expanding rings + 30 particles)")
    print("  - Berserk aura (continuous aggressive red)")
    print()
    print("Boss Effects:")
    print("  - Spawn portal (spiral particles)")
    print("  - Charge warning (pulsing red glow)")
