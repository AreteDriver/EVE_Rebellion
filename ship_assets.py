"""
Ship Asset Manager for EVE Rebellion
Downloads, caches, and processes ship renders from EVE Online's image server.
"""

import os
import math
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Tuple, Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Ship manifest
PLAYER_SHIPS = {587: "Rifter", 11379: "Wolf", 11377: "Jaguar"}
ENEMY_SHIPS = {589: "Executioner", 597: "Punisher", 2006: "Omen", 624: "Maller"}
INDUSTRIAL = {1944: "Bestower", 2863: "Sigil"}
BOSSES = {642: "Apocalypse", 24690: "Abaddon"}

# Combined manifest for easy access
ALL_SHIPS = {**PLAYER_SHIPS, **ENEMY_SHIPS, **INDUSTRIAL, **BOSSES}

# EVE image server base URL
EVE_IMAGE_URL = "https://images.evetech.net/types/{type_id}/render?size={size}"

# Default cache directory
CACHE_DIR = Path("assets/ships")

# Rotation angles for converting isometric to top-down
# EVE renders are typically at ~35 degrees, we rotate to face "up" for the game
ROTATION_ANGLE = -45  # Degrees to rotate for top-down view


class ShipAssetManager:
    """Manages downloading, caching, and processing of ship assets."""

    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.cache_dir / "raw").mkdir(exist_ok=True)
        (self.cache_dir / "processed").mkdir(exist_ok=True)
        (self.cache_dir / "sprites").mkdir(exist_ok=True)
        (self.cache_dir / "effects").mkdir(exist_ok=True)

        self.loaded_ships: Dict[int, pygame.Surface] = {} if PYGAME_AVAILABLE else {}
        self.sprite_sheets: Dict[int, pygame.Surface] = {} if PYGAME_AVAILABLE else {}
        self.thrust_effects: Dict[int, List[pygame.Surface]] = {} if PYGAME_AVAILABLE else {}

    def get_cache_path(self, type_id: int, subdir: str = "raw", suffix: str = ".png") -> Path:
        """Get the cache file path for a ship."""
        ship_name = ALL_SHIPS.get(type_id, f"ship_{type_id}")
        return self.cache_dir / subdir / f"{ship_name.lower()}_{type_id}{suffix}"

    def download_ship(self, type_id: int, size: int = 256, force: bool = False) -> Optional[Path]:
        """
        Download a ship render from EVE's image server.

        Args:
            type_id: EVE Online type ID for the ship
            size: Image size (64, 128, 256, 512, 1024)
            force: Force re-download even if cached

        Returns:
            Path to downloaded file, or None if failed
        """
        cache_path = self.get_cache_path(type_id, "raw")

        if cache_path.exists() and not force:
            print(f"[Cache] {ALL_SHIPS.get(type_id, type_id)} already cached")
            return cache_path

        url = EVE_IMAGE_URL.format(type_id=type_id, size=size)
        ship_name = ALL_SHIPS.get(type_id, f"Unknown ({type_id})")

        try:
            print(f"[Download] Fetching {ship_name} from {url}")

            # Create request with user agent
            request = urllib.request.Request(
                url,
                headers={'User-Agent': 'EVE-Rebellion-Game/1.0'}
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()

            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(data)

            print(f"[Download] Saved {ship_name} to {cache_path}")
            return cache_path

        except urllib.error.HTTPError as e:
            print(f"[Error] HTTP {e.code} downloading {ship_name}: {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"[Error] URL error downloading {ship_name}: {e.reason}")
            return None
        except Exception as e:
            print(f"[Error] Failed to download {ship_name}: {e}")
            return None

    def download_all_ships(self, size: int = 256, force: bool = False) -> Dict[int, Path]:
        """Download all ships in the manifest."""
        results = {}
        for type_id in ALL_SHIPS:
            path = self.download_ship(type_id, size, force)
            if path:
                results[type_id] = path
        return results

    def load_and_rotate(self, type_id: int, rotation: float = ROTATION_ANGLE) -> Optional['pygame.Surface']:
        """
        Load a ship image and rotate it for top-down view.

        Args:
            type_id: EVE Online type ID
            rotation: Degrees to rotate (negative = clockwise)

        Returns:
            Rotated pygame Surface, or None if failed
        """
        if not PYGAME_AVAILABLE:
            print("[Error] Pygame not available")
            return None

        raw_path = self.get_cache_path(type_id, "raw")

        if not raw_path.exists():
            # Try to download
            if not self.download_ship(type_id):
                return None

        try:
            # Load the raw image
            surface = pygame.image.load(str(raw_path)).convert_alpha()

            # Rotate for top-down view
            rotated = pygame.transform.rotate(surface, rotation)

            # Cache the processed version
            processed_path = self.get_cache_path(type_id, "processed")
            pygame.image.save(rotated, str(processed_path))

            self.loaded_ships[type_id] = rotated
            return rotated

        except Exception as e:
            print(f"[Error] Failed to load/rotate ship {type_id}: {e}")
            return None

    def create_sprite_sheet(self, type_id: int, frames: int = 8,
                           effect_type: str = "pulse") -> Optional['pygame.Surface']:
        """
        Create a sprite sheet with animation frames for a ship.

        Args:
            type_id: EVE Online type ID
            frames: Number of animation frames
            effect_type: Type of animation ("pulse", "glow", "shield")

        Returns:
            Sprite sheet surface, or None if failed
        """
        if not PYGAME_AVAILABLE:
            return None

        # Ensure ship is loaded
        if type_id not in self.loaded_ships:
            if not self.load_and_rotate(type_id):
                return None

        base_surface = self.loaded_ships[type_id]
        width, height = base_surface.get_size()

        # Create sprite sheet (horizontal strip)
        sheet_width = width * frames
        sheet = pygame.Surface((sheet_width, height), pygame.SRCALPHA)

        for i in range(frames):
            frame = base_surface.copy()

            if effect_type == "pulse":
                # Subtle brightness pulse
                pulse = 0.9 + 0.2 * math.sin(2 * math.pi * i / frames)
                frame = self._adjust_brightness(frame, pulse)

            elif effect_type == "glow":
                # Add glow effect that pulses
                glow_intensity = int(50 + 30 * math.sin(2 * math.pi * i / frames))
                frame = self._add_glow(frame, glow_intensity)

            elif effect_type == "shield":
                # Shield shimmer effect
                alpha = int(100 + 50 * math.sin(2 * math.pi * i / frames))
                frame = self._add_shield_effect(frame, alpha)

            sheet.blit(frame, (i * width, 0))

        # Save sprite sheet
        sprite_path = self.get_cache_path(type_id, "sprites", f"_{effect_type}.png")
        pygame.image.save(sheet, str(sprite_path))

        self.sprite_sheets[type_id] = sheet
        return sheet

    def generate_thrust_effects(self, type_id: int, frames: int = 6) -> List['pygame.Surface']:
        """
        Generate thrust/engine glow effects for a ship.

        Args:
            type_id: EVE Online type ID
            frames: Number of thrust animation frames

        Returns:
            List of thrust effect surfaces
        """
        if not PYGAME_AVAILABLE:
            return []

        # Ensure ship is loaded
        if type_id not in self.loaded_ships:
            if not self.load_and_rotate(type_id):
                return []

        base_surface = self.loaded_ships[type_id]
        width, height = base_surface.get_size()

        # Determine ship category for thrust color
        if type_id in PLAYER_SHIPS:
            # Minmatar: Orange/red thrust (rusty, industrial)
            thrust_colors = [(255, 150, 50), (255, 100, 30), (255, 200, 100)]
        elif type_id in BOSSES:
            # Amarr capitals: Golden/yellow thrust
            thrust_colors = [(255, 215, 0), (255, 180, 50), (255, 240, 150)]
        else:
            # Amarr standard: Yellow/white thrust
            thrust_colors = [(255, 220, 100), (255, 200, 80), (255, 255, 200)]

        thrust_frames = []

        for i in range(frames):
            # Create thrust effect surface
            thrust = pygame.Surface((width, height + 40), pygame.SRCALPHA)

            # Copy ship
            thrust.blit(base_surface, (0, 0))

            # Calculate thrust intensity (oscillating)
            intensity = 0.7 + 0.3 * math.sin(2 * math.pi * i / frames)

            # Draw thrust plume at bottom center of ship
            cx = width // 2
            base_y = height - 10

            # Multiple thrust cones for layered effect
            for j, color in enumerate(thrust_colors):
                # Outer to inner layers
                plume_height = int((25 - j * 5) * intensity)
                plume_width = int((15 - j * 3) * intensity)

                # Flicker effect
                flicker = 1.0 + 0.1 * math.sin(4 * math.pi * i / frames + j)
                plume_height = int(plume_height * flicker)

                alpha = int((200 - j * 50) * intensity)

                # Draw elongated thrust cone
                self._draw_thrust_plume(thrust, cx, base_y, plume_width,
                                       plume_height, color, alpha)

            # Add glow around thrust
            glow_radius = int(20 * intensity)
            glow_color = thrust_colors[0]
            glow_alpha = int(80 * intensity)
            self._draw_glow_circle(thrust, cx, base_y + 5, glow_radius,
                                  glow_color, glow_alpha)

            thrust_frames.append(thrust)

        # Save thrust frames
        for i, frame in enumerate(thrust_frames):
            effect_path = self.cache_dir / "effects" / f"{ALL_SHIPS.get(type_id, type_id).lower()}_thrust_{i}.png"
            pygame.image.save(frame, str(effect_path))

        self.thrust_effects[type_id] = thrust_frames
        return thrust_frames

    def _adjust_brightness(self, surface: 'pygame.Surface', factor: float) -> 'pygame.Surface':
        """Adjust the brightness of a surface."""
        result = surface.copy()
        arr = pygame.surfarray.pixels3d(result)
        arr[:] = (arr * factor).clip(0, 255).astype('uint8')
        del arr
        return result

    def _add_glow(self, surface: 'pygame.Surface', intensity: int) -> 'pygame.Surface':
        """Add an outer glow effect to a surface."""
        width, height = surface.get_size()
        result = pygame.Surface((width + 20, height + 20), pygame.SRCALPHA)

        # Draw glow layers (blurred copies offset and tinted)
        for offset in range(3, 0, -1):
            glow = surface.copy()
            glow.fill((255, 200, 100, intensity // offset), special_flags=pygame.BLEND_RGBA_MULT)

            # Draw at multiple offsets for blur effect
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    result.blit(glow, (10 + dx, 10 + dy), special_flags=pygame.BLEND_RGBA_ADD)

        # Draw original on top
        result.blit(surface, (10, 10))

        return result

    def _add_shield_effect(self, surface: 'pygame.Surface', alpha: int) -> 'pygame.Surface':
        """Add a shield shimmer effect."""
        result = surface.copy()
        width, height = result.get_size()

        # Create shield overlay
        shield = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw shield bubble
        cx, cy = width // 2, height // 2
        radius = max(width, height) // 2

        pygame.draw.circle(shield, (100, 150, 255, alpha), (cx, cy), radius, 3)
        pygame.draw.circle(shield, (150, 200, 255, alpha // 2), (cx, cy), radius - 5, 2)

        result.blit(shield, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return result

    def _draw_thrust_plume(self, surface: 'pygame.Surface', x: int, y: int,
                          width: int, height: int, color: Tuple[int, int, int],
                          alpha: int):
        """Draw a thrust plume effect."""
        plume = pygame.Surface((width * 2, height), pygame.SRCALPHA)

        # Draw gradient cone
        for i in range(height):
            progress = i / height
            current_width = int(width * (1 - progress * 0.5))
            current_alpha = int(alpha * (1 - progress))

            if current_width > 0 and current_alpha > 0:
                pygame.draw.line(
                    plume,
                    (*color, current_alpha),
                    (width - current_width, i),
                    (width + current_width, i)
                )

        surface.blit(plume, (x - width, y))

    def _draw_glow_circle(self, surface: 'pygame.Surface', x: int, y: int,
                         radius: int, color: Tuple[int, int, int], alpha: int):
        """Draw a glowing circle effect."""
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

        # Draw concentric circles with decreasing alpha
        for r in range(radius, 0, -2):
            circle_alpha = int(alpha * (r / radius))
            pygame.draw.circle(glow, (*color, circle_alpha), (radius, radius), r)

        surface.blit(glow, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_ADD)

    def get_ship(self, type_id: int, with_thrust: bool = False) -> Optional['pygame.Surface']:
        """
        Get a ship surface, loading/downloading if necessary.

        Args:
            type_id: EVE Online type ID
            with_thrust: Include thrust effect (returns first frame)

        Returns:
            Ship surface or None
        """
        if with_thrust:
            if type_id not in self.thrust_effects:
                self.generate_thrust_effects(type_id)
            if type_id in self.thrust_effects and self.thrust_effects[type_id]:
                return self.thrust_effects[type_id][0]

        if type_id not in self.loaded_ships:
            self.load_and_rotate(type_id)

        return self.loaded_ships.get(type_id)

    def get_thrust_frame(self, type_id: int, frame: int) -> Optional['pygame.Surface']:
        """Get a specific thrust animation frame."""
        if type_id not in self.thrust_effects:
            self.generate_thrust_effects(type_id)

        frames = self.thrust_effects.get(type_id, [])
        if frames:
            return frames[frame % len(frames)]
        return None

    def process_all_ships(self, generate_effects: bool = True) -> Dict[int, bool]:
        """
        Download and process all ships in the manifest.

        Args:
            generate_effects: Also generate thrust effects

        Returns:
            Dict mapping type_id to success status
        """
        results = {}

        print("\n=== Processing Ship Assets ===\n")

        for type_id, name in ALL_SHIPS.items():
            print(f"\n--- {name} (ID: {type_id}) ---")

            # Download
            if self.download_ship(type_id):
                # Load and rotate
                if self.load_and_rotate(type_id):
                    results[type_id] = True

                    if generate_effects:
                        # Create sprite sheet
                        self.create_sprite_sheet(type_id)
                        # Generate thrust effects
                        self.generate_thrust_effects(type_id)

                    print(f"[Success] {name} processed")
                else:
                    results[type_id] = False
                    print(f"[Failed] {name} - rotation failed")
            else:
                results[type_id] = False
                print(f"[Failed] {name} - download failed")

        # Summary
        success = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"\n=== Complete: {success}/{total} ships processed ===\n")

        return results


def get_asset_manager() -> ShipAssetManager:
    """Get or create the global ship asset manager."""
    global _asset_manager
    if '_asset_manager' not in globals():
        _asset_manager = ShipAssetManager()
    return _asset_manager


# Convenience functions
def download_all() -> Dict[int, Path]:
    """Download all ship assets."""
    return get_asset_manager().download_all_ships()


def process_all() -> Dict[int, bool]:
    """Process all ship assets (download, rotate, generate effects)."""
    return get_asset_manager().process_all_ships()


def get_ship(type_id: int, with_thrust: bool = False) -> Optional['pygame.Surface']:
    """Get a ship surface by type ID."""
    return get_asset_manager().get_ship(type_id, with_thrust)


def init_headless():
    """Initialize pygame for headless/offscreen processing."""
    if not PYGAME_AVAILABLE:
        return False

    # Use dummy video driver for headless operation
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()

    # Create a small dummy display for image operations
    pygame.display.set_mode((1, 1))
    return True


# CLI interface
if __name__ == "__main__":
    import sys

    print("EVE Rebellion Ship Asset Manager")
    print("================================\n")

    if not PYGAME_AVAILABLE:
        print("[Warning] Pygame not available - only downloading is supported")
        print("Run: pip install pygame\n")

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "download":
            print("Downloading all ships...\n")
            manager = ShipAssetManager()
            manager.download_all_ships()

        elif command == "process":
            if not PYGAME_AVAILABLE:
                print("Error: Pygame required for processing")
                sys.exit(1)
            print("Processing all ships...\n")
            init_headless()
            manager = ShipAssetManager()
            manager.process_all_ships()

        elif command == "list":
            print("Ship Manifest:")
            print("\nPlayer Ships:")
            for tid, name in PLAYER_SHIPS.items():
                print(f"  {tid}: {name}")
            print("\nEnemy Ships:")
            for tid, name in ENEMY_SHIPS.items():
                print(f"  {tid}: {name}")
            print("\nIndustrial:")
            for tid, name in INDUSTRIAL.items():
                print(f"  {tid}: {name}")
            print("\nBosses:")
            for tid, name in BOSSES.items():
                print(f"  {tid}: {name}")

        else:
            print(f"Unknown command: {command}")
            print("Usage: python ship_assets.py [download|process|list]")
    else:
        # Default: process all
        if PYGAME_AVAILABLE:
            init_headless()
            manager = ShipAssetManager()
            manager.process_all_ships()
        else:
            print("Usage: python ship_assets.py [download|process|list]")
            print("\nCommands:")
            print("  download - Download all ship renders")
            print("  process  - Download, rotate, and generate effects")
            print("  list     - Show ship manifest")
