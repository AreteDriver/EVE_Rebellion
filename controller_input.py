"""
Controller-First Input System for EVE Rebellion
Arcade-style vertical scroller controls

Design Philosophy:
- Movement feels weighty, not twitchy
- No menu diving during combat
- Physical tension through haptics
- Mistakes are final (no undo)
"""

import pygame
import math
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ControllerConfig:
    """Controller configuration with dead zones and sensitivity"""
    left_stick_deadzone: float = 0.15
    right_stick_deadzone: float = 0.20
    trigger_deadzone: float = 0.10
    movement_sensitivity: float = 1.0
    aim_sensitivity: float = 0.8
    # Manual Aim deadzone - slightly higher to prevent accidental fire
    aim_fire_deadzone: float = 0.25

    # Haptic intensities (0.0 to 1.0)
    haptic_heat_base: float = 0.3
    haptic_heat_max: float = 0.8
    haptic_lock: float = 0.6
    haptic_decision: float = 0.9
    haptic_death: float = 1.0


@dataclass
class InputState:
    """
    Abstracted input state for unified controller input.

    Single control schema - no modes or settings toggles:
    - Left Stick: Movement
    - LB/RB: Thrust (uses movement direction)
    - LT: Brake/Drop-down (invincible until landing)
    - Right Stick: 360° aiming with persistence
    - RT: Fire primary weapons
    - R3: Toggle Spread/Focus
    """
    # Movement (left stick)
    move_x: float = 0.0
    move_y: float = 0.0

    # Aim direction (unit vector from right stick, with persistence)
    aim_x: float = 0.0
    aim_y: float = -1.0  # Default aim up
    aim_magnitude: float = 0.0  # Current stick deflection (0.0-1.0)

    # Fire state (Right Stick - twin-stick style)
    fire_held: bool = False
    fire_pressure: float = 0.0

    # Special ability (RT - rockets, shield boost, etc.)
    special_ability: bool = False
    special_pressure: float = 0.0

    # Actions
    thrust_held: bool = False  # LB or RB
    brake_pressed: bool = False  # LT pressed (edge detected)
    toggle_fire_mode_pressed: bool = False  # R3 pressed


class ControllerInput:
    """
    Controller-first input handler for EVE Rebellion.

    UNIFIED LAYOUT (Xbox/PlayStation):
    - Left Stick: Ship movement (analog 360°, momentum-aware)
    - Right Stick: 360° aiming with persistence (last direction remembered)
    - RT/R2: Primary fire
    - LT/L2: Brake/Drop-down (invincible until landing)
    - LB/RB (L1/R1): Thrust (uses movement direction)
    - R3: Toggle Spread/Focus fire mode
    - A/B/X/Y: Reserved (no gameplay bindings)
    - Start: Pause

    This is the ONLY control scheme - no modes or settings toggles.

    WHY CONTROLLER > KEYBOARD:
    1. Analog movement creates natural evasion patterns
    2. Right stick allows 360° aim while moving independently
    3. Haptic feedback communicates danger without UI
    4. Muscle memory for high-pressure decisions
    """
    
    def __init__(self, config: Optional[ControllerConfig] = None):
        self.config = config or ControllerConfig()
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.connected = False
        
        # Initialize pygame joystick system
        pygame.joystick.init()
        self._connect_controller()
        
        # Input state
        self.movement_x = 0.0
        self.movement_y = 0.0
        self.aim_offset_x = 0.0
        self.aim_offset_y = 0.0
        self.primary_fire = False
        self.alternate_fire = False
        self.primary_pressure = 0.0  # 0.0 to 1.0 for triggers

        # Trigger edge detection
        self.prev_primary_fire = False
        self.rt_just_pressed = False
        self.prev_brake_trigger = False
        self.lt_just_pressed = False

        # Raw aim vector (right stick)
        self.raw_aim_x = 0.0
        self.raw_aim_y = 0.0
        self.aim_magnitude = 0.0  # 0.0-1.0, magnitude before deadzone

        # Aim persistence - remembers last aim direction when stick is neutral
        self.persistent_aim_x = 0.0
        self.persistent_aim_y = -1.0  # Default aim up

        # Button state (edge detection)
        self.buttons_pressed = set()
        self.buttons_just_pressed = set()
        self.buttons_just_released = set()

        # D-pad state (from HAT)
        self.dpad_x = 0
        self.dpad_y = 0
        self.prev_dpad_x = 0
        self.prev_dpad_y = 0

        # Haptic state
        self.current_rumble = 0.0
        self.heat_level = 0.0  # 0.0 to 1.0

        # Input lock (for death sequence)
        self.input_locked = False
        self.lock_timer = 0
    
    def _connect_controller(self):
        """Auto-detect and connect first available controller"""
        joystick_count = pygame.joystick.get_count()
        if joystick_count > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"Controller connected: {self.joystick.get_name()}")
            
            # Enable haptics if supported
            if hasattr(self.joystick, 'rumble'):
                print("Haptic feedback enabled")
                # Stop any startup vibration (some controllers rumble on init)
                try:
                    self.joystick.rumble(0, 0, 0)
                except Exception:
                    pass
        else:
            print("No controller detected - keyboard/mouse active")
    
    def update(self, dt: float):
        """Update controller state - call once per frame"""
        if not self.connected or self.joystick is None:
            return
        
        # Clear just-pressed state from last frame
        self.buttons_just_pressed.clear()
        self.buttons_just_released.clear()
        
        # Update input lock timer
        if self.input_locked:
            self.lock_timer -= dt
            if self.lock_timer <= 0:
                self.input_locked = False
            return  # Skip input processing while locked
        
        # Read analog sticks with deadzone
        # Xbox Series X mapping: Axis 0=LX, 1=LY, 2=LT, 3=RX, 4=RY, 5=RT
        left_x = self._apply_deadzone(
            self.joystick.get_axis(0),
            self.config.left_stick_deadzone
        )
        left_y = self._apply_deadzone(
            self.joystick.get_axis(1),
            self.config.left_stick_deadzone
        )

        # Get raw right stick values BEFORE deadzone for Manual Aim magnitude
        raw_right_x = self.joystick.get_axis(3)
        raw_right_y = self.joystick.get_axis(4)
        self.aim_magnitude = math.sqrt(raw_right_x**2 + raw_right_y**2)
        self.aim_magnitude = min(1.0, self.aim_magnitude)  # Clamp to 1.0

        # Store normalized aim direction (unit vector when magnitude > 0)
        if self.aim_magnitude > 0.01:
            self.raw_aim_x = raw_right_x / self.aim_magnitude
            self.raw_aim_y = raw_right_y / self.aim_magnitude
        else:
            self.raw_aim_x = 0.0
            self.raw_aim_y = 0.0

        right_x = self._apply_deadzone(raw_right_x, self.config.right_stick_deadzone)
        right_y = self._apply_deadzone(raw_right_y, self.config.right_stick_deadzone)

        # Apply movement with momentum curve (not linear)
        # Use exponential curve for finer control at low speeds
        self.movement_x = self._momentum_curve(left_x) * self.config.movement_sensitivity
        self.movement_y = self._momentum_curve(left_y) * self.config.movement_sensitivity

        # Right stick for precision aim offset (subtle) - Standard mode
        self.aim_offset_x = right_x * self.config.aim_sensitivity * 30  # pixels
        self.aim_offset_y = right_y * self.config.aim_sensitivity * 30
        
        # Read triggers - Xbox Series X: Axis 2=LT, Axis 5=RT
        # Triggers report -1.0 when released, 1.0 when fully pressed
        try:
            rt_raw = self.joystick.get_axis(5)  # Right trigger
            lt_raw = self.joystick.get_axis(2)  # Left trigger
        except Exception:
            rt_raw = -1.0
            lt_raw = -1.0

        # Normalize triggers from [-1, 1] to [0, 1]
        rt = (rt_raw + 1.0) / 2.0
        lt = (lt_raw + 1.0) / 2.0

        # Apply deadzone after normalization
        rt = rt if rt > self.config.trigger_deadzone else 0.0
        lt = lt if lt > self.config.trigger_deadzone else 0.0

        # Track RT edge detection
        new_primary_fire = rt > 0.1
        self.rt_just_pressed = new_primary_fire and not self.prev_primary_fire
        self.prev_primary_fire = new_primary_fire

        # Track LT edge detection for brake
        new_brake_trigger = lt > 0.1
        self.lt_just_pressed = new_brake_trigger and not self.prev_brake_trigger
        self.prev_brake_trigger = new_brake_trigger

        self.primary_fire = new_primary_fire
        self.alternate_fire = new_brake_trigger  # LT is now brake, not alternate fire
        self.primary_pressure = rt

        # Update aim persistence - only when stick is significantly deflected
        if self.aim_magnitude > self.config.right_stick_deadzone:
            self.persistent_aim_x = self.raw_aim_x
            self.persistent_aim_y = self.raw_aim_y

        # Read D-pad (HAT 0)
        self.prev_dpad_x = self.dpad_x
        self.prev_dpad_y = self.dpad_y
        try:
            if self.joystick.get_numhats() > 0:
                self.dpad_x, self.dpad_y = self.joystick.get_hat(0)
        except Exception:
            self.dpad_x, self.dpad_y = 0, 0

        # Generate virtual D-pad button events
        # Up: hat_y == 1, Down: hat_y == -1, Left: hat_x == -1, Right: hat_x == 1
        if self.dpad_y == 1 and self.prev_dpad_y != 1:
            self.buttons_just_pressed.add(100)  # DPAD_UP
        elif self.dpad_y != 1 and self.prev_dpad_y == 1:
            self.buttons_just_released.add(100)

        if self.dpad_y == -1 and self.prev_dpad_y != -1:
            self.buttons_just_pressed.add(101)  # DPAD_DOWN
        elif self.dpad_y != -1 and self.prev_dpad_y == -1:
            self.buttons_just_released.add(101)

        if self.dpad_x == -1 and self.prev_dpad_x != -1:
            self.buttons_just_pressed.add(102)  # DPAD_LEFT
        elif self.dpad_x != -1 and self.prev_dpad_x == -1:
            self.buttons_just_released.add(102)

        if self.dpad_x == 1 and self.prev_dpad_x != 1:
            self.buttons_just_pressed.add(103)  # DPAD_RIGHT
        elif self.dpad_x != 1 and self.prev_dpad_x == 1:
            self.buttons_just_released.add(103)

        # Update haptic feedback based on heat
        self._update_haptics()
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame joystick events for button presses"""
        if not self.connected or self.input_locked:
            return
        
        if event.type == pygame.JOYBUTTONDOWN:
            button = event.button
            self.buttons_pressed.add(button)
            self.buttons_just_pressed.add(button)
            
            # Haptic spike on important buttons
            if button in [0, 1, 2, 3]:  # Face buttons
                self._haptic_spike(self.config.haptic_decision)
        
        elif event.type == pygame.JOYBUTTONUP:
            button = event.button
            if button in self.buttons_pressed:
                self.buttons_pressed.remove(button)
            self.buttons_just_released.add(button)
    
    def _apply_deadzone(self, value: float, deadzone: float) -> float:
        """Apply circular deadzone to analog input"""
        if abs(value) < deadzone:
            return 0.0
        # Scale to full range after deadzone
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - deadzone) / (1.0 - deadzone)
        return sign * scaled
    
    def _momentum_curve(self, input_value: float) -> float:
        """
        Apply momentum curve for weighty, not twitchy movement.
        Uses exponential curve: fine control at center, full speed at edges.
        """
        if input_value == 0.0:
            return 0.0
        
        sign = 1.0 if input_value > 0 else -1.0
        magnitude = abs(input_value)
        
        # Exponential curve: x^1.8 gives good "weight" feel
        curved = pow(magnitude, 1.8)
        return sign * curved
    
    def get_movement_vector(self) -> Tuple[float, float]:
        """Get movement vector with magnitude 0.0 to 1.0"""
        return (self.movement_x, self.movement_y)
    
    def get_aim_offset(self) -> Tuple[float, float]:
        """Get precision aim offset in pixels"""
        return (self.aim_offset_x, self.aim_offset_y)
    
    def is_firing(self) -> bool:
        """Check if primary fire is active (twin-stick: right stick deflection)"""
        # Twin-stick shooter style: fire when aiming with right stick
        # Fire threshold is slightly above deadzone for intentional firing
        return self.aim_magnitude > 0.3
    
    def is_alternate_fire(self) -> bool:
        """Check if alternate fire (rockets) is active"""
        return self.alternate_fire
    
    def get_fire_pressure(self) -> float:
        """Get trigger pressure (0.0 to 1.0) for future fire rate scaling"""
        return self.primary_pressure

    def get_aim_vector(self) -> Tuple[float, float, float]:
        """
        Get raw aim direction vector and magnitude.

        Returns:
            (aim_x, aim_y, magnitude): Unit direction vector and stick magnitude (0-1)
        """
        return (self.raw_aim_x, self.raw_aim_y, self.aim_magnitude)

    def get_input_state(self) -> InputState:
        """
        Get unified input state using the single controller schema.

        Mapping (twin-stick shooter):
            - Left Stick: Movement
            - Right Stick: Aim direction + Fire (twin-stick style)
            - RT: Special ability (rockets/shield boost) - RESERVED
            - LT: Brake/Drop-down (invincible until landing)
            - LB or RB: Thrust (uses movement direction)
            - R3: Toggle Spread/Focus

        Returns:
            InputState with all input values
        """
        state = InputState()

        # Movement from left stick
        state.move_x = self.movement_x
        state.move_y = self.movement_y

        # Aim from right stick with persistence
        # Use persistent aim when stick is neutral, live aim when deflected
        if self.aim_magnitude > self.config.right_stick_deadzone:
            state.aim_x = self.raw_aim_x
            state.aim_y = self.raw_aim_y
        else:
            state.aim_x = self.persistent_aim_x
            state.aim_y = self.persistent_aim_y
        state.aim_magnitude = self.aim_magnitude

        # Twin-stick: fire when right stick is deflected (handled in is_firing())
        # RT is now reserved for special ability
        state.fire_held = self.is_firing()
        state.fire_pressure = self.aim_magnitude  # Use stick deflection as "pressure"

        # RT = Special ability (rockets, shield boost, etc.) - available for future use
        state.special_ability = self.primary_fire  # RT now triggers special
        state.special_pressure = self.primary_pressure

        # LB or RB = Thrust (either bumper works)
        state.thrust_held = (
            self.is_button_held(XboxButton.LB) or
            self.is_button_held(XboxButton.RB)
        )

        # LT = Brake (edge detected - triggers on press, not hold)
        state.brake_pressed = self.lt_just_pressed

        # R3 = Toggle Spread/Focus (edge detected)
        state.toggle_fire_mode_pressed = self.is_button_just_pressed(XboxButton.R_STICK)

        return state

    def is_button_just_pressed(self, button: int) -> bool:
        """Check if button was pressed this frame (edge detection)"""
        return button in self.buttons_just_pressed
    
    def is_button_held(self, button: int) -> bool:
        """Check if button is currently held"""
        return button in self.buttons_pressed
    
    def set_heat_level(self, heat: float):
        """
        Set heat level (0.0 to 1.0) for dynamic haptic feedback.
        Higher heat = stronger continuous rumble.
        """
        self.heat_level = max(0.0, min(1.0, heat))
    
    def _update_haptics(self):
        """Update continuous haptic feedback based on heat"""
        if not self.connected or not hasattr(self.joystick, 'rumble'):
            return

        # Only rumble if heat level is actively set (during gameplay)
        if self.heat_level <= 0:
            # Stop rumble when not in gameplay
            if self.current_rumble > 0:
                self.current_rumble = 0
                try:
                    self.joystick.rumble(0, 0, 0)
                except Exception:
                    pass
            return

        # Rumble intensity scales with heat (no base rumble)
        target_rumble = self.heat_level * self.config.haptic_heat_max

        # Smooth rumble changes
        self.current_rumble += (target_rumble - self.current_rumble) * 0.1

        try:
            # Dual motor rumble (low frequency, high frequency)
            self.joystick.rumble(
                self.current_rumble * 0.7,  # Low frequency motor
                self.current_rumble * 0.3,  # High frequency motor
                100  # Duration in ms
            )
        except Exception:
            pass
    
    def _haptic_spike(self, intensity: float):
        """Trigger sharp haptic spike (lock-on, decision, death)"""
        if not self.connected or not hasattr(self.joystick, 'rumble'):
            return
        
        try:
            self.joystick.rumble(intensity, intensity, 200)
        except Exception:
            pass
    
    def trigger_lock_haptic(self):
        """Sharp spike when enemy locks onto player"""
        self._haptic_spike(self.config.haptic_lock)
    
    def trigger_decision_haptic(self):
        """Sharp spike for irreversible decisions"""
        self._haptic_spike(self.config.haptic_decision)
    
    def trigger_death_sequence(self):
        """
        Lock inputs and trigger death haptic.
        Player cannot restart immediately - must feel the loss.
        """
        self.input_locked = True
        self.lock_timer = 1.0  # 1 second lock
        self._haptic_spike(self.config.haptic_death)
    
    def reconnect(self):
        """Attempt to reconnect controller - reinitializes joystick subsystem"""
        # Quit and reinit to detect newly connected controllers
        pygame.joystick.quit()
        pygame.joystick.init()
        self.connected = False
        self.joystick = None
        self._connect_controller()


# Button mapping constants for clarity
class XboxButton:
    """Xbox controller button mapping"""
    A = 0
    B = 1
    X = 2
    Y = 3
    LB = 4
    RB = 5
    BACK = 6
    START = 7
    L_STICK = 8
    R_STICK = 9
    XBOX = 10  # Xbox/Guide button
    SHARE = 11  # Share button (Series X)
    # D-pad virtual buttons (handled via HAT)
    DPAD_UP = 100
    DPAD_DOWN = 101
    DPAD_LEFT = 102
    DPAD_RIGHT = 103


class PlayStationButton:
    """PlayStation controller button mapping"""
    CROSS = 0
    CIRCLE = 1
    SQUARE = 2
    TRIANGLE = 3
    L1 = 4
    R1 = 5
    SHARE = 6
    OPTIONS = 7
    L3 = 8
    R3 = 9


# Example integration with EVE Rebellion's Player class
def apply_controller_movement(player, controller: ControllerInput, dt: float):
    """
    Apply controller input to player movement with analog precision.
    
    This demonstrates WHY analog is superior:
    - Player can dodge with precise 23° angle, not just 8 directions
    - Speed varies naturally with stick pressure
    - Creates organic evasion patterns keyboard can't match
    """
    if not controller.connected:
        return  # Fall back to keyboard
    
    # Get analog movement vector
    move_x, move_y = controller.get_movement_vector()
    
    # Get aim offset for precision targeting
    aim_x, aim_y = controller.get_aim_offset()
    
    # Apply movement with momentum
    player.rect.x += move_x * player.speed * dt
    player.rect.y += move_y * player.speed * dt
    
    # Optional: Apply aim offset to bullets when firing
    # This creates a "turret offset" effect for precision
    if controller.is_firing():
        # Bullets spawn with slight offset based on right stick
        pass  # Implement in shooting logic
    
    # Example: Trigger pressure affects fire rate (future feature)
    fire_pressure = controller.get_fire_pressure()
    if fire_pressure > 0.5:
        # Rapid fire mode
        pass


if __name__ == "__main__":
    # Test controller detection
    pygame.init()
    controller = ControllerInput()

    if controller.connected:
        print("\n=== EVE Rebellion Controller Layout ===")
        print("Left Stick:  Movement (analog 360°)")
        print("Right Stick: 360° aiming (with persistence)")
        print("RT/R2:       Fire primary weapons")
        print("LT/L2:       Brake/Drop-down (invincible until landing)")
        print("LB/RB:       Thrust (uses movement direction)")
        print("R3:          Toggle Spread/Focus")
        print("A/B/X/Y:     Reserved (no bindings)")
        print("Start:       Pause")
        print("\n=== Why Controller Feels Better ===")
        print("1. Analog evasion > 8-way keyboard")
        print("2. Right stick 360° aim while moving independently")
        print("3. Haptics communicate danger without UI clutter")
        print("4. Muscle memory for high-pressure decisions")
    else:
        print("No controller detected")

    pygame.quit()
