"""
VERTICAL SHMUP CONTROLLER
EVE Rebellion - Arcade Style

Features:
- Point-blank proximity scoring
- Berserk mode (Heat system)
- Boost mechanic (5x gain with drain)
- Formation switching (Spread ↔ Focused)
"""

import pygame
from enum import IntEnum
from typing import Optional, Tuple


class XboxButton(IntEnum):
    """Xbox controller button indices"""
    A = 0          # Primary action
    B = 1          # Emergency/Cancel
    X = 2          # Secondary action
    Y = 3          # Tertiary action
    LB = 4         # Left bumper
    RB = 5         # Right bumper
    BACK = 6       # Back/Select
    START = 7      # Start/Menu
    L_STICK = 8    # Left stick press
    R_STICK = 9    # Right stick press
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14


class PlayStationButton(IntEnum):
    """PlayStation controller button indices"""
    CROSS = 0      # × (Cross)
    CIRCLE = 1     # ○ (Circle)
    SQUARE = 2     # □ (Square)
    TRIANGLE = 3   # △ (Triangle)
    L1 = 4         # Left bumper
    R1 = 5         # Right bumper
    SHARE = 6      # Share/Back
    OPTIONS = 7    # Options/Start
    L3 = 8         # Left stick press
    R3 = 9         # Right stick press
    DPAD_UP = 11
    DPAD_DOWN = 12
    DPAD_LEFT = 13
    DPAD_RIGHT = 14


class VerticalShmupController:
    """
    Controller input for vertical shoot-em-ups.
    Arcade-style control philosophy.

    Key Mechanics:
    - Slower, precise movement (vertical shmup standard)
    - Formation switch: Spread (fast) ↔ Focused (slow + narrow)
    - Boost system: Hold LT/L2 for 5x Heat gain (drains Heat)
    - Continuous fire on RT/R2 (no button mashing)
    - Subtle haptic feedback (tension, not chaos)
    """
    
    def __init__(self):
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.connected = False
        
        # Movement settings
        self.deadzone_move = 0.15
        self.sensitivity_move = 1.0
        self.invert_y = False
        
        # Formation state (Wide ↔ Narrow)
        self.formation = "spread"  # "spread" or "focused"
        self.focused_speed_mult = 0.5  # 50% speed in focused mode
        
        # Input state
        self.move_x = 0.0
        self.move_y = 0.0
        self.firing = False
        self.boost_active = False
        
        # Button state tracking
        self.buttons_pressed = set()
        self.buttons_just_pressed = set()
        self.buttons_just_released = set()
        
        # Haptic feedback
        self.haptic_enabled = True
        self.haptic_intensity = 1.0
        self.current_rumble = 0.0
        self.target_rumble = 0.0
        
        # Input lock (death sequence)
        self.locked = False
        self.lock_timer = 0.0
        
        pygame.joystick.init()
        self._connect()
    
    def _connect(self):
        """Connect to first available controller"""
        count = pygame.joystick.get_count()
        if count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
            print("Control scheme: Vertical Shmup (Arcade style)")
        else:
            print("No controller detected")
    
    def update(self, dt: float):
        """Update controller state each frame"""
        if not self.connected or self.joystick is None:
            return
        
        self.buttons_just_pressed.clear()
        self.buttons_just_released.clear()
        
        # Handle input lock
        if self.locked:
            self.lock_timer -= dt
            if self.lock_timer <= 0:
                self.locked = False
            else:
                # Zero all inputs while locked
                self.move_x = 0.0
                self.move_y = 0.0
                self.firing = False
                self.boost_active = False
                return
        
        # Read left stick (movement)
        raw_x = self._get_axis_safe(0)
        raw_y = self._get_axis_safe(1)
        
        # Apply deadzone
        self.move_x = self._apply_deadzone(raw_x, self.deadzone_move)
        self.move_y = self._apply_deadzone(raw_y, self.deadzone_move)
        
        if self.invert_y:
            self.move_y = -self.move_y
        
        # Apply vertical shmup movement curve
        self.move_x = self._shmup_curve(self.move_x) * self.sensitivity_move
        self.move_y = self._shmup_curve(self.move_y) * self.sensitivity_move
        
        # Apply formation speed modifier
        if self.formation == "focused":
            self.move_x *= self.focused_speed_mult
            self.move_y *= self.focused_speed_mult
        
        # Read triggers
        rt = self._get_axis_safe(5)  # Right trigger (fire)
        lt = self._get_axis_safe(4)  # Left trigger (boost)
        
        # Normalize triggers (-1 to 1 → 0 to 1)
        rt = (rt + 1.0) / 2.0 if rt < 0 else rt
        lt = (lt + 1.0) / 2.0 if lt < 0 else lt
        
        # RT = continuous fire
        self.firing = rt > 0.05
        
        # LT = boost mode
        self.boost_active = lt > 0.05
        
        # Smooth haptic transitions
        self._update_haptics(dt)
    
    def handle_event(self, event):
        """Handle button press/release events"""
        if not self.connected or self.locked:
            return
        
        if event.type == pygame.JOYBUTTONDOWN:
            btn = event.button
            self.buttons_pressed.add(btn)
            self.buttons_just_pressed.add(btn)
            
            # Formation toggle (Y/Triangle)
            if btn == XboxButton.Y:
                self.toggle_formation()
            
            # Haptic click on button press
            if self.haptic_enabled:
                self._pulse_haptic(0.3, 50)
        
        elif event.type == pygame.JOYBUTTONUP:
            btn = event.button
            self.buttons_pressed.discard(btn)
            self.buttons_just_released.add(btn)
    
    def _get_axis_safe(self, axis_id: int) -> float:
        """Safely read axis value"""
        try:
            if self.joystick.get_numaxes() > axis_id:
                return self.joystick.get_axis(axis_id)
        except:
            pass
        return 0.0
    
    def _apply_deadzone(self, value: float, deadzone: float) -> float:
        """Apply circular deadzone with range scaling"""
        if abs(value) < deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - deadzone) / (1.0 - deadzone)
        return sign * scaled
    
    def _shmup_curve(self, value: float) -> float:
        """
        Vertical shmup movement curve.
        Gentler than horizontal arcade shooters (1.5 vs 1.8).
        Allows precise micro-dodges for bullet hell patterns.
        """
        if value == 0.0:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        return sign * pow(abs(value), 1.5)
    
    def _update_haptics(self, dt: float):
        """Smooth haptic feedback transitions"""
        if not self.haptic_enabled:
            return
        
        # Interpolate toward target
        self.current_rumble += (self.target_rumble - self.current_rumble) * 0.1
        
        if self.current_rumble > 0.01:
            self._set_rumble(self.current_rumble)
    
    def _set_rumble(self, intensity: float):
        """Set controller rumble motors"""
        if not hasattr(self.joystick, 'rumble'):
            return
        try:
            # Dual motor: low frequency (left), high frequency (right)
            low_freq = intensity * 0.7
            high_freq = intensity * 0.3
            self.joystick.rumble(low_freq, high_freq, 1000)
        except:
            pass
    
    def _pulse_haptic(self, intensity: float, duration_ms: int):
        """Quick haptic pulse (button press, event)"""
        if not self.haptic_enabled:
            return
        try:
            if hasattr(self.joystick, 'rumble'):
                self.joystick.rumble(
                    intensity * self.haptic_intensity,
                    intensity * self.haptic_intensity,
                    duration_ms
                )
        except:
            pass
    
    # === PUBLIC API ===
    
    def get_movement_vector(self) -> Tuple[float, float]:
        """
        Get movement vector (-1.0 to 1.0).
        Already accounts for formation speed modifier.
        """
        return (self.move_x, self.move_y)
    
    def is_firing(self) -> bool:
        """Check if RT/R2 trigger is held (continuous fire)"""
        return self.firing
    
    def is_boost_active(self) -> bool:
        """
        Check if LT/L2 is held (Boost mode).
        Boost = 5x Heat gain but drains Heat over time.
        """
        return self.boost_active
    
    def toggle_formation(self):
        """
        Switch between Spread and Focused formations.
        
        Spread: Full speed, wide shot pattern
        Focused: 50% speed, narrow beam (precise dodging)
        """
        if self.formation == "spread":
            self.formation = "focused"
            self._pulse_haptic(0.4, 100)
            return "focused"
        else:
            self.formation = "spread"
            self._pulse_haptic(0.4, 100)
            return "spread"
    
    def get_formation(self) -> str:
        """Get current formation: 'spread' or 'focused'"""
        return self.formation
    
    def is_focused(self) -> bool:
        """Check if in focused mode (narrow shot, slow movement)"""
        return self.formation == "focused"
    
    def is_button_pressed(self, button: int) -> bool:
        """Check if button is currently held"""
        return button in self.buttons_pressed
    
    def is_button_just_pressed(self, button: int) -> bool:
        """Check if button was pressed THIS frame"""
        return button in self.buttons_just_pressed
    
    def is_button_just_released(self, button: int) -> bool:
        """Check if button was released THIS frame"""
        return button in self.buttons_just_released
    
    def set_heat_rumble(self, heat_percent: float):
        """
        Set sustained rumble based on Heat level.
        
        Vertical shmup haptics = tension building, not chaos.
        Low rumble that increases as Heat rises.
        
        Args:
            heat_percent: Heat level (0.0 to 1.0)
        """
        if heat_percent < 0.5:
            # Low Heat = no rumble
            self.target_rumble = 0.0
        elif heat_percent < 0.7:
            # Building tension
            self.target_rumble = 0.2 * self.haptic_intensity
        elif heat_percent < 1.0:
            # High tension (approaching Berserk)
            self.target_rumble = 0.4 * self.haptic_intensity
        else:
            # Berserk mode = sustained high rumble
            self.target_rumble = 0.6 * self.haptic_intensity
    
    def proximity_pulse(self, distance: float):
        """
        Haptic pulse on point-blank kill.

        Closer enemy death = higher multiplier.
        Haptic confirms max multiplier achieved.
        
        Args:
            distance: Distance to enemy when killed (pixels)
        """
        if distance < 50:
            # Point-blank! (x4 multiplier)
            self._pulse_haptic(0.5, 80)
        elif distance < 100:
            # Close (x3 multiplier)
            self._pulse_haptic(0.3, 60)
    
    def boss_warning_rumble(self):
        """Heavy rumble when boss appears"""
        self._pulse_haptic(0.7, 500)
    
    def berserk_activated_rumble(self):
        """Strong pulse when Berserk mode activates"""
        self._pulse_haptic(0.8, 300)
    
    def lock_inputs(self, duration: float = 1.0):
        """
        Lock all inputs (death sequence).
        Triggers maximum haptic feedback.
        """
        self.locked = True
        self.lock_timer = duration
        self._pulse_haptic(1.0 * self.haptic_intensity, 500)
    
    def configure(self, **kwargs):
        """
        Configure controller settings.
        
        Allowed kwargs:
        - deadzone_move: float (0.05 to 0.30)
        - sensitivity_move: float (0.5 to 2.0)
        - invert_y: bool
        - haptic_enabled: bool
        - haptic_intensity: float (0.0 to 1.0)
        - focused_speed_mult: float (0.3 to 0.8)
        """
        if 'deadzone_move' in kwargs:
            self.deadzone_move = max(0.05, min(0.30, kwargs['deadzone_move']))
        if 'sensitivity_move' in kwargs:
            self.sensitivity_move = max(0.5, min(2.0, kwargs['sensitivity_move']))
        if 'invert_y' in kwargs:
            self.invert_y = bool(kwargs['invert_y'])
        if 'haptic_enabled' in kwargs:
            self.haptic_enabled = bool(kwargs['haptic_enabled'])
        if 'haptic_intensity' in kwargs:
            self.haptic_intensity = max(0.0, min(1.0, kwargs['haptic_intensity']))
        if 'focused_speed_mult' in kwargs:
            self.focused_speed_mult = max(0.3, min(0.8, kwargs['focused_speed_mult']))


# === INTEGRATION EXAMPLE ===

def apply_vertical_shmup_movement(controller: VerticalShmupController, 
                                   player, dt: float):
    """
    Example integration with Player sprite.
    
    Args:
        controller: VerticalShmupController instance
        player: Player sprite object
        dt: Delta time (seconds)
    """
    # Get movement vector (already accounts for focused mode)
    move_x, move_y = controller.get_movement_vector()
    
    # Apply to player position
    base_speed = 150  # Vertical shmup standard (slower than arcade)
    player.x += move_x * base_speed * dt
    player.y += move_y * base_speed * dt
    
    # Formation affects weapon pattern
    if controller.is_focused():
        player.weapon_pattern = "narrow_beam"
    else:
        player.weapon_pattern = "wide_spread"
    
    # Firing
    if controller.is_firing():
        player.fire_weapon()
    
    # Boost mode
    if controller.is_boost_active():
        player.activate_boost()


if __name__ == "__main__":
    print("=== VERTICAL SHMUP CONTROLLER ===")
    print("EVE Rebellion - Arcade Style Controls")
    print()
    print("Controls:")
    print("  Left Stick: Ship movement")
    print("  RT/R2: Continuous fire")
    print("  LT/L2: Boost mode (5x Heat gain)")
    print("  Y/Triangle: Formation switch (Spread ↔ Focused)")
    print("  RB/R1: Cycle ammo next")
    print("  LB/L1: Cycle ammo prev")
    print("  B/Circle: Emergency burn")
    print("  X/Square: Deploy fleet")
    print("  A/Cross: Context action")
    print()
    print("Formation Modes:")
    print("  Spread: Full speed, wide shot")
    print("  Focused: 50% speed, narrow beam (precise dodging)")
    print()
    print("Haptic Feedback:")
    print("  Sustained rumble = Heat level")
    print("  Sharp pulse = Point-blank kill")
    print("  Heavy pulse = Boss warning")
