#!/usr/bin/env python3
"""
Generate thrust effects for top-down orthographic ship sprites.
"""

import math
import os

import pygame

# Ship categories for thrust colors
MINMATAR_SHIPS = [
    "rifter",
    "wolf",
    "jaguar",
    "slasher",
    "breacher",
    "thrasher",
    "rupture",
    "stabber",
    "hurricane",
    "cyclone",
    "tempest",
    "typhoon",
    "maelstrom",
    "tornado",
    "naglfar",
    "hel",
    "ragnarok",
]

AMARR_SHIPS = [
    "executioner",
    "punisher",
    "tormentor",
    "crucifier",
    "magnate",
    "coercer",
    "omen",
    "maller",
    "arbitrator",
    "augoror",
    "harbinger",
    "prophecy",
    "oracle",
    "apocalypse",
    "abaddon",
    "armageddon",
    "paladin",
    "redeemer",
    "revelation",
    "avatar",
    "bestower",
    "sigil",
]

CALDARI_SHIPS = [
    "condor",
    "merlin",
    "kestrel",
    "heron",
    "bantam",
    "cormorant",
    "caracal",
    "moa",
    "osprey",
    "blackbird",
    "drake",
    "ferox",
    "naga",
    "raven",
    "rokh",
    "scorpion",
    "phoenix",
    "leviathan",
    "badger",
    "tayra",
]

GALLENTE_SHIPS = [
    "atron",
    "tristan",
    "incursus",
    "maulus",
    "navitas",
    "catalyst",
    "vexor",
    "thorax",
    "celestis",
    "exequror",
    "brutix",
    "myrmidon",
    "talos",
    "dominix",
    "megathron",
    "hyperion",
    "kronos",
    "moros",
    "erebus",
    "iteron",
]

SPRITE_DIR = os.path.join(os.path.dirname(__file__), "assets", "ship_sprites")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "ships", "effects")


def get_thrust_colors(ship_name):
    """Get thrust colors based on faction."""
    name = ship_name.lower()

    if any(s in name for s in MINMATAR_SHIPS):
        # Minmatar: Orange/red (rusty, industrial)
        return [(255, 150, 50), (255, 100, 30), (255, 200, 100)]
    elif any(s in name for s in AMARR_SHIPS):
        # Amarr: Golden/yellow
        return [(255, 215, 0), (255, 180, 50), (255, 240, 150)]
    elif any(s in name for s in CALDARI_SHIPS):
        # Caldari: Blue/white
        return [(100, 180, 255), (150, 200, 255), (200, 230, 255)]
    elif any(s in name for s in GALLENTE_SHIPS):
        # Gallente: Green/teal
        return [(50, 255, 150), (100, 255, 180), (150, 255, 200)]
    else:
        # Default: White/blue
        return [(200, 220, 255), (180, 200, 255), (220, 240, 255)]


def draw_thrust_plume(surface, x, y, width, height, color, alpha):
    """Draw a thrust plume effect."""
    plume = pygame.Surface((width * 2, height), pygame.SRCALPHA)

    for i in range(height):
        progress = i / height
        current_width = int(width * (1 - progress * 0.6))
        current_alpha = int(alpha * (1 - progress * 0.8))

        if current_width > 0 and current_alpha > 0:
            pygame.draw.line(
                plume,
                (*color, current_alpha),
                (width - current_width, i),
                (width + current_width, i),
            )

    surface.blit(plume, (x - width, y))


def draw_glow_circle(surface, x, y, radius, color, alpha):
    """Draw a glowing circle effect."""
    glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

    for r in range(radius, 0, -2):
        circle_alpha = int(alpha * (r / radius))
        pygame.draw.circle(glow, (*color, circle_alpha), (radius, radius), r)

    surface.blit(glow, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_ADD)


def generate_thrust_frames(ship_name, frames=6):
    """Generate thrust effect frames for a ship sprite."""
    sprite_path = os.path.join(SPRITE_DIR, f"{ship_name}.png")

    if not os.path.exists(sprite_path):
        print(f"  [SKIP] {ship_name} - sprite not found")
        return []

    # Load the sprite
    base_surface = pygame.image.load(sprite_path).convert_alpha()
    width, height = base_surface.get_size()

    thrust_colors = get_thrust_colors(ship_name)
    thrust_frames = []

    for i in range(frames):
        # Create surface with extra space for thrust
        thrust = pygame.Surface((width, height + 50), pygame.SRCALPHA)

        # Copy ship (thrust extends below)
        thrust.blit(base_surface, (0, 0))

        # Calculate thrust intensity (oscillating)
        intensity = 0.7 + 0.3 * math.sin(2 * math.pi * i / frames)

        # Draw thrust at bottom center
        cx = width // 2
        base_y = height - 5

        # Multiple thrust cones for layered effect
        for j, color in enumerate(thrust_colors):
            plume_height = int((30 - j * 8) * intensity)
            plume_width = int((18 - j * 4) * intensity)

            # Flicker effect
            flicker = 1.0 + 0.15 * math.sin(4 * math.pi * i / frames + j)
            plume_height = int(plume_height * flicker)

            alpha = int((220 - j * 50) * intensity)

            draw_thrust_plume(thrust, cx, base_y, plume_width, plume_height, color, alpha)

        # Add glow around thrust
        glow_radius = int(25 * intensity)
        glow_color = thrust_colors[0]
        glow_alpha = int(100 * intensity)
        draw_glow_circle(thrust, cx, base_y + 5, glow_radius, glow_color, glow_alpha)

        thrust_frames.append(thrust)

    return thrust_frames


def save_thrust_frames(ship_name, frames):
    """Save thrust frames to disk."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, frame in enumerate(frames):
        output_path = os.path.join(OUTPUT_DIR, f"{ship_name}_topdown_thrust_{i}.png")
        pygame.image.save(frame, output_path)


def main():
    # Initialize pygame
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    pygame.init()
    pygame.display.set_mode((1, 1))

    # Ships to generate effects for
    ships = [
        # Player ships (Minmatar)
        "rifter",
        "wolf",
        "jaguar",
        # Enemy ships (Amarr)
        "executioner",
        "punisher",
        "omen",
        "maller",
        # Industrial
        "bestower",
        "sigil",
        # Bosses
        "apocalypse",
        "abaddon",
        # Extra ships
        "condor",
        "tristan",
        "hurricane",
        "tempest",
        "dominix",
        "megathron",
        "raven",
        "rokh",
    ]

    print("Generating top-down thrust effects...\n")

    success = 0
    for ship in ships:
        print(f"Processing {ship}...")
        frames = generate_thrust_frames(ship)
        if frames:
            save_thrust_frames(ship, frames)
            print(f"  ✓ Generated {len(frames)} frames")
            success += 1

    print(f"\nDone! Generated effects for {success} ships")
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
