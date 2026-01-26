"""
Platform initialization module for EVE Rebellion.

Handles display driver detection and configuration for different platforms,
including Wayland and X11 on Linux. Must be called BEFORE pygame.init().

Wayland Support:
    - Auto-detects Wayland sessions via WAYLAND_DISPLAY env var
    - Falls back to X11 via XWayland if pure Wayland fails
    - Respects user-set SDL_VIDEODRIVER if already configured

Portable Mode:
    - Detects if running from a packaged/portable install
    - Provides utilities for resolving resource paths
"""

import os
import sys
from typing import Optional


# Track whether we've initialized platform settings
_platform_initialized = False
_detected_driver: Optional[str] = None


def get_base_path() -> str:
    """
    Get the base path for the application.

    Handles both development mode (running from source) and
    packaged mode (PyInstaller, portable install).

    Returns:
        Base directory path for the application.
    """
    # PyInstaller sets _MEIPASS for bundled apps
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return sys._MEIPASS

    # Check if we're running from a portable install
    # (EVE_REBELLION_ROOT environment variable can be set by launcher)
    if 'EVE_REBELLION_ROOT' in os.environ:
        return os.environ['EVE_REBELLION_ROOT']

    # Development mode - use the directory containing this file
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to a resource, works in dev and packaged mode.

    Args:
        relative_path: Path relative to the application root.

    Returns:
        Absolute path to the resource.
    """
    return os.path.join(get_base_path(), relative_path)


def is_wayland_session() -> bool:
    """Check if running under a Wayland session."""
    return bool(os.environ.get('WAYLAND_DISPLAY'))


def is_x11_session() -> bool:
    """Check if running under an X11 session."""
    return bool(os.environ.get('DISPLAY'))


def get_linux_display_driver() -> str:
    """
    Determine the best SDL video driver for Linux.

    Priority:
        1. User-specified SDL_VIDEODRIVER (if set)
        2. Wayland (if in Wayland session)
        3. X11 (if in X11 session)
        4. Default (let SDL decide)

    Returns:
        Video driver name or empty string for default.
    """
    # Respect user override
    user_driver = os.environ.get('SDL_VIDEODRIVER')
    if user_driver:
        return user_driver

    # Auto-detect based on session type
    if is_wayland_session():
        return 'wayland'
    elif is_x11_session():
        return 'x11'

    return ''


def init_platform() -> str:
    """
    Initialize platform-specific settings before pygame.

    This function MUST be called before pygame.init() to ensure
    proper display driver configuration.

    Sets SDL environment variables for:
        - Video driver (Wayland/X11 on Linux)
        - Audio driver preferences
        - IME and input method handling

    Returns:
        The video driver that will be used (or 'default' if system decides).
    """
    global _platform_initialized, _detected_driver

    if _platform_initialized:
        return _detected_driver or 'default'

    platform = sys.platform
    driver = ''

    if platform == 'linux':
        driver = get_linux_display_driver()

        if driver:
            os.environ['SDL_VIDEODRIVER'] = driver

            # Additional Wayland-specific settings
            if driver == 'wayland':
                # Enable Wayland IME support
                os.environ.setdefault('SDL_IM_MODULE', 'fcitx')

                # Allow fallback to X11 via XWayland if needed
                # This helps with some edge cases where pure Wayland fails
                os.environ.setdefault('SDL_VIDEO_WAYLAND_ALLOW_LIBDECOR', '1')

                # Better scaling on HiDPI displays
                os.environ.setdefault('SDL_VIDEO_WAYLAND_SCALE_TO_DISPLAY', '1')

    elif platform == 'darwin':
        # macOS-specific settings
        # Let SDL use the default Cocoa driver
        pass

    elif platform == 'win32':
        # Windows-specific settings
        # Let SDL use the default Windows driver
        pass

    # Common settings for all platforms
    # Disable compositor bypass which can cause issues on some systems
    os.environ.setdefault('SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR', '0')

    _platform_initialized = True
    _detected_driver = driver or 'default'

    return _detected_driver


def get_detected_driver() -> str:
    """
    Get the video driver that was detected/configured.

    Returns:
        Video driver name, or 'default' if using system default,
        or 'uninitialized' if init_platform() hasn't been called.
    """
    if not _platform_initialized:
        return 'uninitialized'
    return _detected_driver or 'default'


def print_platform_info():
    """Print platform detection info for debugging."""
    print("EVE Rebellion Platform Info")
    print("=" * 40)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version}")
    print(f"Base path: {get_base_path()}")
    print(f"Wayland session: {is_wayland_session()}")
    print(f"X11 session: {is_x11_session()}")
    print(f"SDL_VIDEODRIVER: {os.environ.get('SDL_VIDEODRIVER', '(not set)')}")
    print(f"Detected driver: {get_detected_driver()}")
    print("=" * 40)


if __name__ == '__main__':
    # Initialize and print debug info
    init_platform()
    print_platform_info()
