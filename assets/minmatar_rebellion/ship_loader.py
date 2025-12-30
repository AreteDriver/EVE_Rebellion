"""SVG ship loader for Minmatar Rebellion"""
import pygame
import os
from io import BytesIO


class ShipImageCache:
    """Cache for loaded ship images"""
    
    def __init__(self):
        self.cache = {}
        self.svg_path = os.path.join(os.path.dirname(__file__), 'svg', 'top')
        self.available = os.path.exists(self.svg_path)
        
        if not self.available:
            print("SVG ships not found. Using procedural graphics.")
    
    def load_ship(self, ship_name, width, height, color=None):
        """
        Load a ship SVG and convert to pygame surface.
        
        Args:
            ship_name: Name of the ship (e.g., 'rifter')
            width: Target width in pixels
            height: Target height in pixels
            color: Optional RGB tuple to tint the ship
        
        Returns:
            pygame.Surface with the ship image, or None if loading fails
        """
        # Normalize ship name
        ship_name = ship_name.lower()
        
        # Check cache
        cache_key = (ship_name, width, height, color)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try to load SVG
        if not self.available:
            return None
        
        svg_file = os.path.join(self.svg_path, f'{ship_name}.svg')
        if not os.path.exists(svg_file):
            # Try with capital first letter (some files use this)
            svg_file = os.path.join(self.svg_path, f'{ship_name.capitalize()}.svg')
            if not os.path.exists(svg_file):
                return None
        
        try:
            # Load and parse SVG
            surface = self._load_svg_simple(svg_file, width, height, color)
            
            if surface:
                self.cache[cache_key] = surface
                return surface
            
        except Exception as e:
            print(f"Failed to load {ship_name}: {e}")
            return None
        
        return None
    
    def _load_svg_simple(self, svg_file, width, height, color=None):
        """
        Simple SVG loader using pygame and basic parsing.
        Converts SVG paths to a pygame surface.
        """
        try:
            # Try using cairosvg if available
            import cairosvg
            
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(
                url=svg_file,
                output_width=width,
                output_height=height
            )
            
            # Load PNG data into pygame surface
            png_io = BytesIO(png_data)
            surface = pygame.image.load(png_io, 'PNG')
            
            # Apply color tint if specified
            if color:
                surface = self._tint_surface(surface, color)
            
            return surface
            
        except ImportError:
            # cairosvg not available, try alternative method
            return self._load_svg_fallback(svg_file, width, height, color)
    
    def _load_svg_fallback(self, svg_file, width, height, color=None):
        """
        Fallback SVG loader using PIL/Pillow if available.
        """
        try:
            from PIL import Image
            import cairosvg
            
            # Convert to PNG
            png_data = cairosvg.svg2png(url=svg_file, output_width=width, output_height=height)
            
            # Load with PIL
            image = Image.open(BytesIO(png_data))
            
            # Convert to pygame surface
            mode = image.mode
            size = image.size
            data = image.tobytes()
            
            surface = pygame.image.fromstring(data, size, mode)
            
            if color:
                surface = self._tint_surface(surface, color)
            
            return surface
            
        except (ImportError, Exception):
            # No SVG support available
            return None
    
    def _tint_surface(self, surface, color):
        """Apply color tint to a surface"""
        # Create a copy with per-pixel alpha
        tinted = surface.copy()
        
        # Create color overlay
        color_surface = pygame.Surface(tinted.get_size(), pygame.SRCALPHA)
        color_surface.fill((*color, 128))
        
        # Blend with multiply
        tinted.blit(color_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return tinted
    
    def is_available(self):
        """Check if SVG loading is available"""
        return self.available


# Global ship cache instance
_ship_cache = None


def get_ship_cache():
    """Get or create the global ship cache"""
    global _ship_cache
    if _ship_cache is None:
        _ship_cache = ShipImageCache()
    return _ship_cache


def load_ship_image(ship_name, width, height, color=None):
    """
    Convenience function to load a ship image.
    
    Args:
        ship_name: Name of the ship (e.g., 'rifter')
        width: Target width in pixels
        height: Target height in pixels  
        color: Optional RGB tuple to tint the ship
    
    Returns:
        pygame.Surface or None
    """
    cache = get_ship_cache()
    return cache.load_ship(ship_name, width, height, color)


def check_svg_support():
    """Check if SVG loading libraries are available"""
    try:
        import cairosvg
        return True
    except ImportError:
        try:
            from PIL import Image
            import cairosvg
            return True
        except ImportError:
            return False


if __name__ == "__main__":
    # Test the loader
    print("Testing SVG Ship Loader")
    print("=" * 50)
    
    pygame.init()
    
    cache = get_ship_cache()
    
    if not cache.is_available():
        print("SVG directory not found!")
    else:
        print(f"SVG directory found: {cache.svg_path}")
        
        # Check for SVG library support
        if check_svg_support():
            print("✓ SVG libraries available (cairosvg)")
        else:
            print("✗ SVG libraries not available")
            print("  Install with: pip install cairosvg")
        
        print()
        
        # Test loading some ships
        test_ships = ['rifter', 'wolf', 'apocalypse', 'abaddon']
        
        for ship in test_ships:
            surface = cache.load_ship(ship, 64, 64)
            if surface:
                print(f"✓ Loaded {ship}: {surface.get_width()}x{surface.get_height()}")
            else:
                print(f"✗ Failed to load {ship}")
    
    print("=" * 50)
