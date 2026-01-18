#!/usr/bin/env python3
"""Generate game icon for Minmatar Rebellion using actual Rifter sprite"""
import pygame
import math
import os

def create_icon(size=256):
    """Create an icon using the actual Rifter ship sprite"""
    pygame.init()

    # Create surface with alpha
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    cx, cy = size // 2, size // 2
    scale = size / 256  # Scale factor for different sizes

    # Try to load the actual Rifter sprite
    base_dir = os.path.dirname(__file__)
    sprite_paths = [
        os.path.join(base_dir, 'assets', 'ship_sprites', 'rifter.png'),
        os.path.join(base_dir, 'assets', 'eve_renders', 'rifter.png'),
    ]

    rifter_sprite = None
    for path in sprite_paths:
        if os.path.exists(path):
            try:
                rifter_sprite = pygame.image.load(path).convert_alpha()
                break
            except pygame.error:
                continue

    if rifter_sprite:
        # === BACKGROUND: Circular space gradient ===
        for r in range(int(size * 0.48), 0, -2):
            t = r / (size * 0.48)
            alpha = int(200 * t)
            color = (15 + int(10 * t), 15 + int(5 * t), 30 + int(15 * t), alpha)
            pygame.draw.circle(surface, color, (cx, cy), r)

        # === ENGINE GLOW (behind ship) ===
        glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        engine_color = (255, 120, 40)
        engine_y = int(cy + size * 0.15)
        for r in range(int(40 * scale), 0, -2):
            alpha = int(80 * (r / (40 * scale)))
            pygame.draw.circle(glow_surf, (*engine_color, alpha), (cx, engine_y), r)
        surface.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # === SCALE AND CENTER RIFTER ===
        orig_w, orig_h = rifter_sprite.get_size()
        # Scale to fit nicely in icon (about 70% of icon size)
        target_size = int(size * 0.7)
        aspect = orig_w / orig_h
        if aspect > 1:
            new_w = target_size
            new_h = int(target_size / aspect)
        else:
            new_h = target_size
            new_w = int(target_size * aspect)

        rifter_scaled = pygame.transform.smoothscale(rifter_sprite, (new_w, new_h))

        # === RIM LIGHTING EFFECT ===
        rim_surf = pygame.Surface((new_w + 8, new_h + 8), pygame.SRCALPHA)
        rim_color = (255, 180, 120, 80)
        for offset in [(2, 0), (-2, 0), (0, 2), (0, -2), (1, 1), (-1, -1)]:
            rim_surf.blit(rifter_scaled, (4 + offset[0], 4 + offset[1]))
        rim_tint = pygame.Surface(rim_surf.get_size(), pygame.SRCALPHA)
        rim_tint.fill(rim_color)
        rim_surf.blit(rim_tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Position ship
        ship_x = (size - new_w) // 2
        ship_y = (size - new_h) // 2 - int(5 * scale)  # Slightly up to show engines

        # Draw rim then ship
        surface.blit(rim_surf, (ship_x - 4, ship_y - 4))
        surface.blit(rifter_scaled, (ship_x, ship_y))

        # === ENGINE EXHAUST TRAILS ===
        trail_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        engine_positions = [
            (cx - int(12 * scale), engine_y + int(10 * scale)),
            (cx, engine_y + int(8 * scale)),
            (cx + int(12 * scale), engine_y + int(10 * scale)),
        ]
        for ex, ey in engine_positions:
            # Trail
            for i in range(int(25 * scale), 0, -2):
                t = i / (25 * scale)
                alpha = int(200 * t * t)
                width = int(6 * t * scale + 2)
                if t > 0.6:
                    color = (255, 255, 220, alpha)
                else:
                    color = (255, 150, 60, alpha)
                trail_y = ey + int((25 * scale - i) * 0.6)
                pygame.draw.circle(trail_surf, color, (ex, trail_y), width)
            # Core
            pygame.draw.circle(trail_surf, (255, 255, 255), (ex, ey), int(3 * scale))

        surface.blit(trail_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

        # === OUTER RING (subtle) ===
        ring_color = (180, 100, 50, 100)
        pygame.draw.circle(surface, ring_color, (cx, cy), int(size * 0.46), max(1, int(2 * scale)))
        pygame.draw.circle(surface, (100, 60, 40, 60), (cx, cy), int(size * 0.44), max(1, int(1 * scale)))

    else:
        # Fallback to procedural icon if sprite not found
        surface = _create_procedural_icon(size)

    return surface


def _create_procedural_icon(size=256):
    """Fallback procedural Minmatar-style ship icon"""
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # Colors - Minmatar rust/industrial theme
    rust_dark = (120, 65, 35)
    rust_light = (220, 140, 80)
    engine_glow = (255, 150, 50)
    engine_core = (255, 220, 150)

    cx, cy = size // 2, size // 2
    scale = size / 256

    # Background
    for y in range(size):
        alpha = int(180 + 40 * (y / size))
        for x in range(size):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if dist < size * 0.48:
                bg_alpha = int(alpha * (1 - dist / (size * 0.6)))
                surface.set_at((x, y), (15, 15, 25, max(0, bg_alpha)))

    # Simplified ship shape
    hull_points = [
        (cx, cy - 90 * scale),
        (cx + 25 * scale, cy - 60 * scale),
        (cx + 35 * scale, cy - 20 * scale),
        (cx + 45 * scale, cy + 30 * scale),
        (cx + 30 * scale, cy + 60 * scale),
        (cx + 15 * scale, cy + 80 * scale),
        (cx - 15 * scale, cy + 80 * scale),
        (cx - 30 * scale, cy + 60 * scale),
        (cx - 45 * scale, cy + 30 * scale),
        (cx - 35 * scale, cy - 20 * scale),
        (cx - 25 * scale, cy - 60 * scale),
    ]
    pygame.draw.polygon(surface, rust_dark, hull_points)
    pygame.draw.polygon(surface, rust_light, hull_points, max(1, int(3 * scale)))

    # Engine glows
    for x_off in [-20, 20]:
        for r in range(int(18 * scale), 0, -2):
            alpha = int(150 * (r / (18 * scale)))
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*engine_glow[:3], alpha), (r, r), r)
            surface.blit(glow_surf, (cx + x_off * scale - r, cy + 85 * scale - r))
        pygame.draw.circle(surface, engine_core,
                          (int(cx + x_off * scale), int(cy + 85 * scale)),
                          int(6 * scale))

    return surface


def main():
    """Generate icons in multiple sizes"""
    sizes = [256, 128, 64, 48, 32, 16]

    # Create icons directory if needed
    os.makedirs("icons", exist_ok=True)

    for size in sizes:
        icon = create_icon(size)
        filename = f"icons/icon_{size}.png"
        pygame.image.save(icon, filename)
        print(f"Created {filename}")

    # Save main icon
    main_icon = create_icon(256)
    pygame.image.save(main_icon, "icons/minmatar_rebellion.png")
    print("Created icons/minmatar_rebellion.png")

    # Also save to root for easy access
    pygame.image.save(main_icon, "icon.png")
    print("Created icon.png")

    pygame.quit()
    print("\nIcon generation complete!")
    print("Use icon.png for the game window icon")
    print("Use icons/ folder for desktop launcher")


if __name__ == "__main__":
    main()
