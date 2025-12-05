"""Mobile-specific constants for Minmatar Rebellion"""
import pygame

# Mobile display - optimized for portrait mobile screens
# Will be overridden at runtime based on actual device
MOBILE_SCREEN_WIDTH = 480
MOBILE_SCREEN_HEIGHT = 800

# Touch control zones (percentages of screen)
# Virtual joystick area (bottom-left quadrant)
JOYSTICK_AREA_X = 0.05  # 5% from left
JOYSTICK_AREA_Y = 0.70  # 70% from top (bottom area)
JOYSTICK_RADIUS = 60  # pixels
JOYSTICK_KNOB_RADIUS = 25  # inner knob

# Fire button (bottom-right area)
FIRE_BUTTON_X = 0.85  # 85% from left
FIRE_BUTTON_Y = 0.80  # 80% from top
FIRE_BUTTON_RADIUS = 40

# Rocket button (above fire button)
ROCKET_BUTTON_X = 0.85
ROCKET_BUTTON_Y = 0.65
ROCKET_BUTTON_RADIUS = 30

# Ammo buttons (top-right area, smaller)
AMMO_BUTTON_SIZE = 35
AMMO_BUTTON_SPACING = 40
AMMO_BUTTONS_X = 0.85
AMMO_BUTTONS_Y = 0.12

# Pause button (top-left)
PAUSE_BUTTON_X = 0.08
PAUSE_BUTTON_Y = 0.05
PAUSE_BUTTON_SIZE = 35

# Touch control colors
TOUCH_CONTROL_COLOR = (100, 100, 100, 100)  # Semi-transparent gray
TOUCH_CONTROL_ACTIVE = (150, 150, 150, 150)  # Brighter when touched
FIRE_BUTTON_COLOR = (255, 100, 100, 150)  # Reddish
ROCKET_BUTTON_COLOR = (100, 100, 255, 150)  # Bluish

# Mobile-specific settings
MOBILE_PLAYER_SPEED_MULT = 1.2  # Slightly faster for touch controls
MOBILE_FIRE_RATE_MULT = 1.1  # Slightly faster fire rate for mobile

# Touch sensitivity
TOUCH_DEAD_ZONE = 10  # pixels - ignore tiny movements
