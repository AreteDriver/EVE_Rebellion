"""
Visual Enhancement System for Minmatar Rebellion
Adds glows, outlines, and color tints for better ship visibility
"""

import pygame
import math

def add_ship_glow(surface, color, intensity=0.3):
    """Add a subtle glow effect around a ship"""
    width, height = surface.get_size()
    glow_surf = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)
    
    # Create multiple glow layers for smooth effect
    for i in range(5):
        alpha = int(intensity * 255 * (5 - i) / 5)
        glow_color = (*color[:3], alpha)
        _offset = i * 2  # Reserved for position offset
        
        # Scale up the ship slightly for each glow layer
        scale = 1.0 + (i * 0.05)
        scaled = pygame.transform.scale(surface, 
            (int(width * scale), int(height * scale)))
        
        # Tint it
        tinted = scaled.copy()
        tinted.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
        
        # Blit centered
        x = (glow_surf.get_width() - tinted.get_width()) // 2
        y = (glow_surf.get_height() - tinted.get_height()) // 2
        glow_surf.blit(tinted, (x, y))
    
    # Blit original ship on top
    glow_surf.blit(surface, (10, 10))
    return glow_surf

def add_colored_tint(surface, color, alpha=80):
    """Add a colored tint overlay to a ship"""
    tinted = surface.copy()
    tint_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    tint_surface.fill((*color, alpha))
    tinted.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

def add_outline(surface, color=(255, 255, 255), thickness=2):
    """Add a crisp outline around a ship"""
    mask = pygame.mask.from_surface(surface)
    outline_surf = mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))
    
    # Expand outline
    result = pygame.Surface((surface.get_width() + thickness*2, 
                            surface.get_height() + thickness*2), pygame.SRCALPHA)
    
    for dx in range(-thickness, thickness+1):
        for dy in range(-thickness, thickness+1):
            if dx*dx + dy*dy <= thickness*thickness:
                result.blit(outline_surf, (thickness + dx, thickness + dy))
    
    # Blit original on top
    result.blit(surface, (thickness, thickness))
    return result

def create_nebula_background(width, height):
    """Create a darker nebula background for better ship contrast"""
    background = pygame.Surface((width, height))
    
    # Dark blue-purple gradient
    for y in range(height):
        progress = y / height
        r = int(10 + progress * 20)
        g = int(5 + progress * 15)
        b = int(30 + progress * 40)
        pygame.draw.line(background, (r, g, b), (0, y), (width, y))
    
    return background

def pulse_glow_alpha(time_ms, base_alpha=0.3, pulse_speed=0.002):
    """Calculate pulsing glow intensity"""
    return base_alpha + math.sin(time_ms * pulse_speed) * 0.15


def add_strong_outline(surface, outline_color=(255, 255, 255), glow_color=None, thickness=3):
    """Add a strong visible outline to ships"""
    width, height = surface.get_size()
    
    # Create result surface with padding
    result = pygame.Surface((width + thickness*4, height + thickness*4), pygame.SRCALPHA)
    
    # Create mask from original
    mask = pygame.mask.from_surface(surface)
    
    # Draw multiple outline layers
    for t in range(thickness, 0, -1):
        outline_surf = mask.to_surface(
            setcolor=outline_color if t == thickness else glow_color or outline_color,
            unsetcolor=(0, 0, 0, 0)
        )
        
        # Draw outline at offset positions
        for dx in range(-t, t+1):
            for dy in range(-t, t+1):
                if dx*dx + dy*dy <= t*t:
                    result.blit(outline_surf, (thickness*2 + dx, thickness*2 + dy))
    
    # Blit original on top
    result.blit(surface, (thickness*2, thickness*2))
    
    return result
