"""Controller/Gamepad support for Minmatar Rebellion"""

import pygame


class Controller:
    """Handle gamepad/controller input"""

    def __init__(self):
        self.joystick = None
        self.enabled = False
        self.dead_zone = 0.15  # Ignore small stick movements

        # Try to initialize controller
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.enabled = True
            print(f"Controller detected: {self.joystick.get_name()}")
            print(f"  Buttons: {self.joystick.get_numbuttons()}")
            print(f"  Axes: {self.joystick.get_numaxes()}")
        else:
            print("No controller detected - using keyboard")

    def get_movement(self):
        """Get movement from left analog stick"""
        if not self.enabled:
            return 0, 0

        # Left stick - axes 0 (horizontal) and 1 (vertical)
        x = self.joystick.get_axis(0)
        y = self.joystick.get_axis(1)

        # Apply dead zone
        if abs(x) < self.dead_zone:
            x = 0
        if abs(y) < self.dead_zone:
            y = 0

        return x, y

    def get_aim(self):
        """Get aim from right analog stick (for twin-stick shooter mode)"""
        if not self.enabled or self.joystick.get_numaxes() < 4:
            return 0, 0

        # Right stick - axes 2 (horizontal) and 3 (vertical)
        x = self.joystick.get_axis(2)
        y = self.joystick.get_axis(3)

        # Apply dead zone
        if abs(x) < self.dead_zone:
            x = 0
        if abs(y) < self.dead_zone:
            y = 0

        return x, y

    def is_button_pressed(self, button_id):
        """Check if a button is pressed"""
        if not self.enabled:
            return False

        if button_id < self.joystick.get_numbuttons():
            return self.joystick.get_button(button_id)
        return False

    def get_trigger(self, trigger_id):
        """Get trigger value (0.0 to 1.0)"""
        if not self.enabled:
            return 0.0

        # On most controllers, triggers are axes 4 and 5
        if trigger_id == "left" and self.joystick.get_numaxes() > 4:
            value = self.joystick.get_axis(4)
            return (value + 1) / 2  # Convert from -1..1 to 0..1
        elif trigger_id == "right" and self.joystick.get_numaxes() > 5:
            value = self.joystick.get_axis(5)
            return (value + 1) / 2

        return 0.0

    # Button mapping for common controllers
    # Xbox: A=0, B=1, X=2, Y=3, LB=4, RB=5, Back=6, Start=7
    BUTTON_A = 0
    BUTTON_B = 1
    BUTTON_X = 2
    BUTTON_Y = 3
    BUTTON_LB = 4
    BUTTON_RB = 5
    BUTTON_BACK = 6
    BUTTON_START = 7

    def fire_pressed(self):
        """Check if fire button is pressed (A or Right Trigger)"""
        return self.is_button_pressed(self.BUTTON_A) or self.get_trigger("right") > 0.3

    def rocket_pressed(self):
        """Check if rocket button is pressed (B or Left Trigger)"""
        return self.is_button_pressed(self.BUTTON_B) or self.get_trigger("left") > 0.3

    def cycle_ammo_pressed(self):
        """Check if cycle ammo button is pressed (X or LB)"""
        return self.is_button_pressed(self.BUTTON_X) or self.is_button_pressed(self.BUTTON_LB)

    def pause_pressed(self):
        """Check if pause button is pressed (Start)"""
        return self.is_button_pressed(self.BUTTON_START)

    def select_pressed(self):
        """Check if select button is pressed (A)"""
        return self.is_button_pressed(self.BUTTON_A)
