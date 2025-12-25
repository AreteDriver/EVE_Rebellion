#!/usr/bin/env python3
"""Generate game icon for Minmatar Rebellion"""
import pygame
import math
import os

def create_icon(size=256):
    """Create a Minmatar-style ship icon"""
    pygame.init()

    # Create surface with alpha
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    # Colors - Minmatar rust/industrial theme
    rust = (180, 100, 50)
    rust_dark = (120, 65, 35)
    rust_light = (220, 140, 80)
    metal = (100, 90, 80)
    metal_dark = (60, 55, 50)
    engine_glow = (255, 150, 50)
    engine_core = (255, 220, 150)

    cx, cy = size // 2, size // 2
    scale = size / 256  # Scale factor for different sizes

    # Background - subtle space gradient with transparency
    for y in range(size):
        alpha = int(180 + 40 * (y / size))
        for x in range(size):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            if dist < size * 0.48:
                bg_alpha = int(alpha * (1 - dist / (size * 0.6)))
                surface.set_at((x, y), (15, 15, 25, max(0, bg_alpha)))

    # Draw ship body - asymmetric Minmatar style
    # Main hull (angular, industrial)
    hull_points = [
        (cx, cy - 90 * scale),           # Nose
        (cx + 25 * scale, cy - 60 * scale),  # Right front
        (cx + 35 * scale, cy - 20 * scale),  # Right mid upper
        (cx + 45 * scale, cy + 30 * scale),  # Right wing
        (cx + 30 * scale, cy + 60 * scale),  # Right rear
        (cx + 15 * scale, cy + 80 * scale),  # Right engine
        (cx - 15 * scale, cy + 80 * scale),  # Left engine
        (cx - 30 * scale, cy + 60 * scale),  # Left rear
        (cx - 45 * scale, cy + 30 * scale),  # Left wing
        (cx - 35 * scale, cy - 20 * scale),  # Left mid upper
        (cx - 25 * scale, cy - 60 * scale),  # Left front
    ]

    # Main hull fill
    pygame.draw.polygon(surface, rust_dark, hull_points)

    # Hull plating lines (industrial look)
    plate_lines = [
        [(cx, cy - 90 * scale), (cx, cy + 70 * scale)],
        [(cx - 20 * scale, cy - 50 * scale), (cx - 25 * scale, cy + 50 * scale)],
        [(cx + 20 * scale, cy - 50 * scale), (cx + 25 * scale, cy + 50 * scale)],
        [(cx - 40 * scale, cy + 10 * scale), (cx + 40 * scale, cy + 10 * scale)],
        [(cx - 35 * scale, cy - 30 * scale), (cx + 35 * scale, cy - 30 * scale)],
    ]
    for line in plate_lines:
        pygame.draw.line(surface, metal_dark, line[0], line[1], max(1, int(2 * scale)))

    # Cockpit
    cockpit_points = [
        (cx, cy - 70 * scale),
        (cx + 12 * scale, cy - 45 * scale),
        (cx + 8 * scale, cy - 25 * scale),
        (cx - 8 * scale, cy - 25 * scale),
        (cx - 12 * scale, cy - 45 * scale),
    ]
    pygame.draw.polygon(surface, (40, 60, 80), cockpit_points)
    pygame.draw.polygon(surface, (80, 120, 160), cockpit_points, max(1, int(2 * scale)))

    # Wing extensions (asymmetric Minmatar style)
    left_wing = [
        (cx - 35 * scale, cy - 10 * scale),
        (cx - 60 * scale, cy + 20 * scale),
        (cx - 55 * scale, cy + 45 * scale),
        (cx - 40 * scale, cy + 35 * scale),
    ]
    right_wing = [
        (cx + 35 * scale, cy - 10 * scale),
        (cx + 60 * scale, cy + 20 * scale),
        (cx + 55 * scale, cy + 45 * scale),
        (cx + 40 * scale, cy + 35 * scale),
    ]
    pygame.draw.polygon(surface, rust, left_wing)
    pygame.draw.polygon(surface, rust, right_wing)
    pygame.draw.polygon(surface, rust_light, left_wing, max(1, int(2 * scale)))
    pygame.draw.polygon(surface, rust_light, right_wing, max(1, int(2 * scale)))

    # Engine nacelles
    for x_off in [-20, 20]:
        nacelle_rect = pygame.Rect(
            cx + x_off * scale - 8 * scale,
            cy + 50 * scale,
            16 * scale,
            35 * scale
        )
        pygame.draw.rect(surface, metal, nacelle_rect)
        pygame.draw.rect(surface, metal_dark, nacelle_rect, max(1, int(2 * scale)))

    # Engine glows
    for x_off in [-20, 20]:
        # Outer glow
        for r in range(int(18 * scale), 0, -2):
            alpha = int(150 * (r / (18 * scale)))
            glow_color = (*engine_glow[:3], alpha)
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, glow_color, (r, r), r)
            surface.blit(glow_surf, (cx + x_off * scale - r, cy + 85 * scale - r))

        # Core
        pygame.draw.circle(surface, engine_core,
                          (int(cx + x_off * scale), int(cy + 85 * scale)),
                          int(6 * scale))

    # Rust/wear details (spots)
    import random
    random.seed(42)  # Consistent look
    for _ in range(15):
        rx = cx + random.randint(int(-40 * scale), int(40 * scale))
        ry = cy + random.randint(int(-60 * scale), int(50 * scale))
        rr = random.randint(int(3 * scale), int(8 * scale))
        rust_spot = random.choice([rust_light, rust_dark, metal])
        pygame.draw.circle(surface, rust_spot, (int(rx), int(ry)), int(rr))

    # Highlight edge
    pygame.draw.polygon(surface, rust_light, hull_points, max(1, int(3 * scale)))

    # Add subtle title text at bottom
    if size >= 128:
        font_size = max(12, int(18 * scale))
        try:
            font = pygame.font.Font(None, font_size)
            text = font.render("REBELLION", True, (200, 150, 100))
            text_rect = text.get_rect(center=(cx, size - 20 * scale))
            surface.blit(text, text_rect)
        except:
            pass

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
