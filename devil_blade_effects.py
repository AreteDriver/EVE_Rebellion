"""
Devil Blade Reboot Visual Effects
Pixel-perfect retro effects matching the game's aesthetic
"""

import pygame
import random
import math
from typing import Tuple, List, Optional

class PixelExplosion:
    """
    Retro-style pixel particle explosion
    Used for enemy deaths, impacts, etc.
    """
    
    def __init__(self, pos: Tuple[int, int], color: Tuple[int, int, int],
                 particle_count: int = 20, spread: float = 5.0):
        self.particles = []
        
        for _ in range(particle_count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, spread)
            
            particle = {
                'x': float(pos[0]),
                'y': float(pos[1]),
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': random.randint(20, 60),
                'max_lifetime': 60,
                'size': random.randint(2, 4),
                'color': color,
                'gravity': random.uniform(0.1, 0.3)
            }
            self.particles.append(particle)
    
    def update(self):
        """Update particle positions and lifetime"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += particle['gravity']  # Gravity
            particle['lifetime'] -= 1
            
            # Air resistance
            particle['vx'] *= 0.95
            particle['vy'] *= 0.95
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw(self, surface: pygame.Surface):
        """Draw particles"""
        for particle in self.particles:
            # Fade out based on lifetime
            alpha = int((particle['lifetime'] / particle['max_lifetime']) * 255)
            color = particle['color']
            
            # Create small surface for particle with alpha
            size = particle['size']
            particle_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            particle_surf.fill((*color, alpha))
            
            surface.blit(particle_surf, (int(particle['x']), int(particle['y'])))
    
    def is_finished(self) -> bool:
        """Check if explosion is complete"""
        return len(self.particles) == 0


class ScreenFlash:
    """
    Full-screen flash effect for dramatic moments
    Devil Blade uses these for boss deaths, extreme close kills, etc.
    """
    
    def __init__(self, color: Tuple[int, int, int] = (255, 255, 255),
                 duration: int = 10, peak_alpha: int = 180):
        self.color = color
        self.duration = duration
        self.max_duration = duration
        self.peak_alpha = peak_alpha
        self.active = True
    
    def update(self):
        """Update flash state"""
        if self.duration > 0:
            self.duration -= 1
        else:
            self.active = False
    
    def draw(self, surface: pygame.Surface):
        """Draw flash overlay"""
        if not self.active:
            return
        
        # Calculate alpha (fade in then out)
        progress = self.duration / self.max_duration
        if progress > 0.5:
            # Fading in
            alpha = int(((1.0 - progress) * 2) * self.peak_alpha)
        else:
            # Fading out
            alpha = int((progress * 2) * self.peak_alpha)
        
        # Create overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((*self.color, alpha))
        surface.blit(overlay, (0, 0))


class ScreenShake:
    """
    Screen shake effect for impacts and explosions
    Pixel-perfect displacement
    """
    
    def __init__(self, intensity: int = 5, duration: int = 10):
        self.intensity = intensity
        self.duration = duration
        self.max_duration = duration
        self.offset_x = 0
        self.offset_y = 0
    
    def update(self):
        """Update shake and calculate offset"""
        if self.duration > 0:
            self.duration -= 1
            
            # Decay intensity
            current_intensity = int(self.intensity * (self.duration / self.max_duration))
            
            # Random offset
            self.offset_x = random.randint(-current_intensity, current_intensity)
            self.offset_y = random.randint(-current_intensity, current_intensity)
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def get_offset(self) -> Tuple[int, int]:
        """Get current screen offset"""
        return (self.offset_x, self.offset_y)
    
    def is_active(self) -> bool:
        """Check if shake is still active"""
        return self.duration > 0


class ScanLine:
    """
    CRT-style scanline effect (optional retro filter)
    Can be toggled in settings for authentic retro feel
    """
    
    def __init__(self, screen_height: int, line_spacing: int = 2,
                 opacity: int = 30):
        self.screen_height = screen_height
        self.line_spacing = line_spacing
        self.opacity = opacity
    
    def draw(self, surface: pygame.Surface):
        """Draw scanlines overlay"""
        width = surface.get_width()
        
        # Create scanline surface
        scanline_surf = pygame.Surface((width, self.screen_height), pygame.SRCALPHA)
        
        # Draw horizontal lines
        for y in range(0, self.screen_height, self.line_spacing):
            pygame.draw.line(scanline_surf, (0, 0, 0, self.opacity),
                           (0, y), (width, y))
        
        surface.blit(scanline_surf, (0, 0))


class BulletTrail:
    """
    Pixel-perfect bullet trails for enhanced visual feedback
    """
    
    def __init__(self, start_pos: Tuple[float, float],
                 end_pos: Tuple[float, float],
                 color: Tuple[int, int, int],
                 lifetime: int = 5):
        self.start = start_pos
        self.end = end_pos
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
    
    def update(self):
        """Update trail lifetime"""
        self.lifetime -= 1
    
    def draw(self, surface: pygame.Surface):
        """Draw fading trail line"""
        if self.lifetime > 0:
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            
            # Create surface for line with alpha
            x1, y1 = self.start
            x2, y2 = self.end
            
            # Calculate bounding box
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            w = max(1, int(max_x - min_x))
            h = max(1, int(max_y - min_y))
            
            trail_surf = pygame.Surface((w + 4, h + 4), pygame.SRCALPHA)
            
            # Draw line on surface
            local_x1 = x1 - min_x + 2
            local_y1 = y1 - min_y + 2
            local_x2 = x2 - min_x + 2
            local_y2 = y2 - min_y + 2
            
            pygame.draw.line(trail_surf, (*self.color, alpha),
                           (local_x1, local_y1), (local_x2, local_y2), 2)
            
            surface.blit(trail_surf, (min_x - 2, min_y - 2))
    
    def is_finished(self) -> bool:
        """Check if trail has faded"""
        return self.lifetime <= 0


class ImpactRing:
    """
    Expanding ring effect for bullet impacts
    Classic shmup visual
    """
    
    def __init__(self, pos: Tuple[int, int], color: Tuple[int, int, int],
                 max_radius: int = 30, duration: int = 15):
        self.pos = pos
        self.color = color
        self.radius = 5
        self.max_radius = max_radius
        self.duration = duration
        self.max_duration = duration
    
    def update(self):
        """Update ring expansion"""
        if self.duration > 0:
            self.duration -= 1
            # Expand radius
            self.radius += (self.max_radius - self.radius) * 0.3
    
    def draw(self, surface: pygame.Surface):
        """Draw expanding ring"""
        if self.duration > 0:
            alpha = int((self.duration / self.max_duration) * 255)
            
            # Create surface for ring
            size = int(self.radius * 2 + 10)
            ring_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw ring
            center = (size // 2, size // 2)
            pygame.draw.circle(ring_surf, (*self.color, alpha),
                             center, int(self.radius), 2)
            
            # Blit centered on position
            surface.blit(ring_surf, (self.pos[0] - size // 2, self.pos[1] - size // 2))
    
    def is_finished(self) -> bool:
        """Check if ring is complete"""
        return self.duration <= 0


class EffectManager:
    """
    Central manager for all visual effects
    Handles creation, update, and rendering of effects
    """
    
    def __init__(self):
        self.explosions: List[PixelExplosion] = []
        self.flashes: List[ScreenFlash] = []
        self.shakes: List[ScreenShake] = []
        self.trails: List[BulletTrail] = []
        self.rings: List[ImpactRing] = []
        
        # Settings
        self.scanlines_enabled = False
        self.scanline_effect: Optional[ScanLine] = None
        
        # Current shake offset (combined from all active shakes)
        self.total_shake_x = 0
        self.total_shake_y = 0
    
    def add_explosion(self, pos: Tuple[int, int], color: Tuple[int, int, int],
                     particle_count: int = 20, spread: float = 5.0):
        """Add pixel explosion effect"""
        explosion = PixelExplosion(pos, color, particle_count, spread)
        self.explosions.append(explosion)
    
    def add_flash(self, color: Tuple[int, int, int] = (255, 255, 255),
                  duration: int = 10, alpha: int = 180):
        """Add screen flash"""
        flash = ScreenFlash(color, duration, alpha)
        self.flashes.append(flash)
    
    def add_shake(self, intensity: int = 5, duration: int = 10):
        """Add screen shake"""
        shake = ScreenShake(intensity, duration)
        self.shakes.append(shake)
    
    def add_trail(self, start: Tuple[float, float], end: Tuple[float, float],
                  color: Tuple[int, int, int], lifetime: int = 5):
        """Add bullet trail"""
        trail = BulletTrail(start, end, color, lifetime)
        self.trails.append(trail)
    
    def add_impact_ring(self, pos: Tuple[int, int], color: Tuple[int, int, int],
                       max_radius: int = 30):
        """Add impact ring"""
        ring = ImpactRing(pos, color, max_radius)
        self.rings.append(ring)
    
    def enable_scanlines(self, screen_height: int, spacing: int = 2, opacity: int = 30):
        """Enable CRT scanline effect"""
        self.scanlines_enabled = True
        self.scanline_effect = ScanLine(screen_height, spacing, opacity)
    
    def disable_scanlines(self):
        """Disable scanline effect"""
        self.scanlines_enabled = False
    
    def update(self):
        """Update all active effects"""
        # Update and clean up explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished():
                self.explosions.remove(explosion)
        
        # Update flashes
        for flash in self.flashes[:]:
            flash.update()
            if not flash.active:
                self.flashes.remove(flash)
        
        # Update shakes and calculate total offset
        self.total_shake_x = 0
        self.total_shake_y = 0
        for shake in self.shakes[:]:
            shake.update()
            if not shake.is_active():
                self.shakes.remove(shake)
            else:
                offset_x, offset_y = shake.get_offset()
                self.total_shake_x += offset_x
                self.total_shake_y += offset_y
        
        # Update trails
        for trail in self.trails[:]:
            trail.update()
            if trail.is_finished():
                self.trails.remove(trail)
        
        # Update rings
        for ring in self.rings[:]:
            ring.update()
            if ring.is_finished():
                self.rings.remove(ring)
    
    def draw_background_effects(self, surface: pygame.Surface):
        """Draw effects that go behind gameplay elements"""
        # Trails and rings go behind
        for trail in self.trails:
            trail.draw(surface)
        
        for ring in self.rings:
            ring.draw(surface)
    
    def draw_foreground_effects(self, surface: pygame.Surface):
        """Draw effects that go in front of gameplay elements"""
        # Explosions in front
        for explosion in self.explosions:
            explosion.draw(surface)
        
        # Flashes on top of everything
        for flash in self.flashes:
            flash.draw(surface)
        
        # Scanlines last (optional)
        if self.scanlines_enabled and self.scanline_effect:
            self.scanline_effect.draw(surface)
    
    def get_shake_offset(self) -> Tuple[int, int]:
        """Get total screen shake offset"""
        return (self.total_shake_x, self.total_shake_y)
    
    def clear_all(self):
        """Clear all active effects"""
        self.explosions.clear()
        self.flashes.clear()
        self.shakes.clear()
        self.trails.clear()
        self.rings.clear()
