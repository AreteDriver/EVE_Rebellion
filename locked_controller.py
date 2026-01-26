"""
HARD-LOCKED CONTROLLER LAYOUT
EVE Rebellion - No Compromises, No Rebinding

This module enforces the optimal controller layout.
No customization of bindings - only sensitivity/deadzone adjustments allowed.

Philosophy: One tested layout > infinite broken configurations
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

import pygame


class GameAction(IntEnum):
    """
    All possible game actions.
    These are ABSTRACT - mapped to physical buttons in ControllerLayout.
    """
    # Movement (analog)
    MOVE_SHIP = 0
    AIM_TURRET = 1

    # Weapons
    PRIMARY_FIRE = 10
    ALTERNATE_FIRE = 11

    # Ammo management
    CYCLE_AMMO_NEXT = 20
    CYCLE_AMMO_PREV = 21

    # Tactical
    EMERGENCY_BURN = 30
    DEPLOY_FLEET = 31
    SWITCH_FORMATION = 32
    CONTEXT_ACTION = 33

    # System
    PAUSE = 40
    QUICK_STATS = 41


@dataclass(frozen=True)  # Immutable - can't be changed at runtime
class ControllerLayout:
    """
    HARD-LOCKED controller layout.
    This class is frozen - bindings cannot be modified.

    If you want different bindings, you're using the wrong controller.
    This layout is tested and optimal for vertical scrollers.
    """

    # === XBOX LAYOUT (Primary) ===
    # Sticks (axes)
    MOVE_X_AXIS: int = 0          # Left stick horizontal
    MOVE_Y_AXIS: int = 1          # Left stick vertical
    AIM_X_AXIS: int = 2           # Right stick horizontal
    AIM_Y_AXIS: int = 3           # Right stick vertical

    # Triggers (axes on most controllers)
    PRIMARY_FIRE_AXIS: int = 5    # RT (Right Trigger)
    ALTERNATE_FIRE_AXIS: int = 4  # LT (Left Trigger) - may be axis 2 on some

    # Buttons
    BTN_CONTEXT_ACTION: int = 0   # A / Cross
    BTN_EMERGENCY_BURN: int = 1   # B / Circle
    BTN_DEPLOY_FLEET: int = 2     # X / Square
    BTN_FORMATION_SWITCH: int = 3 # Y / Triangle
    BTN_CYCLE_AMMO_PREV: int = 4  # LB / L1
    BTN_CYCLE_AMMO_NEXT: int = 5  # RB / R1
    BTN_QUICK_STATS: int = 6      # Back/Select / Share
    BTN_PAUSE: int = 7            # Start / Options
    BTN_L_STICK_PRESS: int = 8    # L3 (unused, reserved)
    BTN_R_STICK_PRESS: int = 9    # R3 (unused, reserved)

    # D-Pad (treated as buttons)
    DPAD_UP: int = 11
    DPAD_DOWN: int = 12
    DPAD_LEFT: int = 13
    DPAD_RIGHT: int = 14

    def __post_init__(self):
        """Validate layout on creation"""
        # Ensure no duplicate bindings
        buttons = [
            self.BTN_CONTEXT_ACTION, self.BTN_EMERGENCY_BURN,
            self.BTN_DEPLOY_FLEET, self.BTN_FORMATION_SWITCH,
            self.BTN_CYCLE_AMMO_PREV, self.BTN_CYCLE_AMMO_NEXT,
            self.BTN_QUICK_STATS, self.BTN_PAUSE
        ]
        if len(buttons) != len(set(buttons)):
            raise ValueError("Duplicate button bindings detected")


# Global singleton - THE ONLY LAYOUT
LAYOUT = ControllerLayout()


class InputValidator:
    """
    Validates controller configuration to prevent bad habits.

    BLOCKS:
    - Mouse-dependent features during controller mode
    - Keyboard input when controller is active
    - Simultaneous controller + keyboard (pick one)
    """

    def __init__(self):
        self.controller_active = False
        self.keyboard_active = False
        self.mixed_input_frames = 0
        self.warn_threshold = 30  # Warn after 30 frames of mixed input

    def validate_input_source(self, controller_used: bool, keyboard_used: bool):
        """
        Enforce single input method.

        Returns: (allowed_controller, allowed_keyboard, warning_message)
        """
        if controller_used and keyboard_used:
            self.mixed_input_frames += 1

            if self.mixed_input_frames > self.warn_threshold:
                # After 30 frames, force decision
                if self.controller_active:
                    return (True, False, "CONTROLLER MODE - Keyboard disabled")
                else:
                    return (False, True, "KEYBOARD MODE - Controller disabled")

            # Grace period for transition
            return (True, True, None)

        # Clear input detected
        self.mixed_input_frames = 0

        if controller_used:
            self.controller_active = True
            self.keyboard_active = False
            return (True, False, None)

        if keyboard_used:
            self.keyboard_active = False
            self.controller_active = True  # Wait for actual input
            return (False, True, None)

        # No input
        return (self.controller_active, self.keyboard_active, None)

    def reset(self):
        """Reset validator (e.g., on game restart)"""
        self.controller_active = False
        self.keyboard_active = False
        self.mixed_input_frames = 0


class LockedControllerInput:
    """
    Controller input with HARD-LOCKED layout.

    CUSTOMIZABLE:
    - Deadzone sizes
    - Sensitivity multipliers
    - Haptic intensity
    - Invert Y axis

    NOT CUSTOMIZABLE:
    - Button bindings (use LAYOUT constant)
    - Stick assignments (left = move, right = aim)
    - Trigger functions (RT = fire, LT = rockets)
    """

    def __init__(self):
        self.layout = LAYOUT
        self.validator = InputValidator()

        # Controller state
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.connected = False

        # User-adjustable settings (NOT bindings)
        self.deadzone_move = 0.15
        self.deadzone_aim = 0.20
        self.deadzone_trigger = 0.10
        self.sensitivity_move = 1.0
        self.sensitivity_aim = 0.8
        self.invert_y = False
        self.haptic_enabled = True
        self.haptic_intensity = 1.0

        # Input state
        self.move_x = 0.0
        self.move_y = 0.0
        self.aim_x = 0.0
        self.aim_y = 0.0
        self.primary_fire = False
        self.alternate_fire = False
        self.trigger_pressure = 0.0

        # Button state
        self.buttons_pressed = set()
        self.buttons_just_pressed = set()

        # Input lock
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
            print(f"✓ Controller: {self.joystick.get_name()}")
            print("✓ Layout: HARD-LOCKED (no rebinding)")
            print(f"✓ Axes: {self.joystick.get_numaxes()}")
            print(f"✓ Buttons: {self.joystick.get_numbuttons()}")
        else:
            print("✗ No controller detected")

    def update(self, dt: float):
        """Update controller state"""
        if not self.connected or self.joystick is None:
            return

        self.buttons_just_pressed.clear()

        # Handle input lock
        if self.locked:
            self.lock_timer -= dt
            if self.lock_timer <= 0:
                self.locked = False
            else:
                # Zero all inputs while locked
                self.move_x = 0.0
                self.move_y = 0.0
                self.primary_fire = False
                self.alternate_fire = False
                return

        # Read movement stick (HARD-LOCKED to left stick)
        raw_x = self._get_axis_safe(self.layout.MOVE_X_AXIS)
        raw_y = self._get_axis_safe(self.layout.MOVE_Y_AXIS)

        self.move_x = self._apply_deadzone(raw_x, self.deadzone_move)
        self.move_y = self._apply_deadzone(raw_y, self.deadzone_move)

        if self.invert_y:
            self.move_y = -self.move_y

        # Apply momentum curve
        self.move_x = self._momentum_curve(self.move_x) * self.sensitivity_move
        self.move_y = self._momentum_curve(self.move_y) * self.sensitivity_move

        # Read aim stick (HARD-LOCKED to right stick)
        raw_aim_x = self._get_axis_safe(self.layout.AIM_X_AXIS)
        raw_aim_y = self._get_axis_safe(self.layout.AIM_Y_AXIS)

        self.aim_x = self._apply_deadzone(raw_aim_x, self.deadzone_aim)
        self.aim_y = self._apply_deadzone(raw_aim_y, self.deadzone_aim)

        if self.invert_y:
            self.aim_y = -self.aim_y

        self.aim_x *= self.sensitivity_aim
        self.aim_y *= self.sensitivity_aim

        # Read triggers (HARD-LOCKED to RT/LT)
        rt = self._get_axis_safe(self.layout.PRIMARY_FIRE_AXIS)
        lt = self._get_axis_safe(self.layout.ALTERNATE_FIRE_AXIS)

        # Normalize triggers (some controllers use -1 to 1, others 0 to 1)
        rt = (rt + 1.0) / 2.0 if rt < 0 else rt
        lt = (lt + 1.0) / 2.0 if lt < 0 else lt

        rt = self._apply_deadzone(rt, self.deadzone_trigger)
        lt = self._apply_deadzone(lt, self.deadzone_trigger)

        self.primary_fire = rt > 0.05
        self.alternate_fire = lt > 0.05
        self.trigger_pressure = rt

    def handle_event(self, event):
        """Handle button events"""
        if not self.connected or self.locked:
            return

        if event.type == pygame.JOYBUTTONDOWN:
            btn = event.button
            self.buttons_pressed.add(btn)
            self.buttons_just_pressed.add(btn)

            # Haptic feedback on button press
            if self.haptic_enabled:
                self._rumble(0.3 * self.haptic_intensity, 50)

        elif event.type == pygame.JOYBUTTONUP:
            btn = event.button
            self.buttons_pressed.discard(btn)

    def _get_axis_safe(self, axis_id: int) -> float:
        """Safely read axis value"""
        try:
            return self.joystick.get_axis(axis_id)
        except Exception:
            return 0.0

    def _apply_deadzone(self, value: float, deadzone: float) -> float:
        """Apply circular deadzone"""
        if abs(value) < deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - deadzone) / (1.0 - deadzone)
        return sign * scaled

    def _momentum_curve(self, value: float) -> float:
        """Apply exponential curve for weighty movement"""
        if value == 0.0:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        return sign * pow(abs(value), 1.8)

    def _rumble(self, intensity: float, duration_ms: int):
        """Trigger haptic feedback"""
        if not self.haptic_enabled or not hasattr(self.joystick, 'rumble'):
            return
        try:
            self.joystick.rumble(intensity, intensity, duration_ms)
        except Exception:
            pass

    # === PUBLIC API ===

    def get_movement(self) -> tuple[float, float]:
        """Get movement vector (-1.0 to 1.0)"""
        return (self.move_x, self.move_y)

    def get_aim_offset(self) -> tuple[float, float]:
        """Get aim offset for precision targeting"""
        return (self.aim_x * 30, self.aim_y * 30)  # pixels

    def is_action_pressed(self, action: GameAction) -> bool:
        """Check if action button is currently pressed"""
        button_map = {
            GameAction.CONTEXT_ACTION: self.layout.BTN_CONTEXT_ACTION,
            GameAction.EMERGENCY_BURN: self.layout.BTN_EMERGENCY_BURN,
            GameAction.DEPLOY_FLEET: self.layout.BTN_DEPLOY_FLEET,
            GameAction.SWITCH_FORMATION: self.layout.BTN_FORMATION_SWITCH,
            GameAction.CYCLE_AMMO_PREV: self.layout.BTN_CYCLE_AMMO_PREV,
            GameAction.CYCLE_AMMO_NEXT: self.layout.BTN_CYCLE_AMMO_NEXT,
            GameAction.PAUSE: self.layout.BTN_PAUSE,
            GameAction.QUICK_STATS: self.layout.BTN_QUICK_STATS,
        }

        btn = button_map.get(action)
        return btn in self.buttons_pressed if btn is not None else False

    def is_action_just_pressed(self, action: GameAction) -> bool:
        """Check if action was pressed THIS frame (edge detection)"""
        button_map = {
            GameAction.CONTEXT_ACTION: self.layout.BTN_CONTEXT_ACTION,
            GameAction.EMERGENCY_BURN: self.layout.BTN_EMERGENCY_BURN,
            GameAction.DEPLOY_FLEET: self.layout.BTN_DEPLOY_FLEET,
            GameAction.SWITCH_FORMATION: self.layout.BTN_FORMATION_SWITCH,
            GameAction.CYCLE_AMMO_PREV: self.layout.BTN_CYCLE_AMMO_PREV,
            GameAction.CYCLE_AMMO_NEXT: self.layout.BTN_CYCLE_AMMO_NEXT,
            GameAction.PAUSE: self.layout.BTN_PAUSE,
            GameAction.QUICK_STATS: self.layout.BTN_QUICK_STATS,
        }

        btn = button_map.get(action)
        return btn in self.buttons_just_pressed if btn is not None else False

    def lock_inputs(self, duration: float = 1.0):
        """Lock all inputs for duration (death sequence)"""
        self.locked = True
        self.lock_timer = duration
        self._rumble(1.0 * self.haptic_intensity, 500)

    def set_haptic_intensity(self, intensity: float):
        """Set haptic feedback strength (0.0 to 1.0)"""
        self.haptic_intensity = max(0.0, min(1.0, intensity))

    def configure(self, **kwargs):
        """
        Configure ALLOWED settings (NOT bindings).

        Allowed kwargs:
        - deadzone_move: float (0.05 to 0.30)
        - deadzone_aim: float (0.10 to 0.40)
        - sensitivity_move: float (0.5 to 2.0)
        - sensitivity_aim: float (0.3 to 1.5)
        - invert_y: bool
        - haptic_enabled: bool
        - haptic_intensity: float (0.0 to 1.0)

        NOT allowed:
        - Rebinding buttons (layout is LOCKED)
        """
        if 'deadzone_move' in kwargs:
            self.deadzone_move = max(0.05, min(0.30, kwargs['deadzone_move']))
        if 'deadzone_aim' in kwargs:
            self.deadzone_aim = max(0.10, min(0.40, kwargs['deadzone_aim']))
        if 'sensitivity_move' in kwargs:
            self.sensitivity_move = max(0.5, min(2.0, kwargs['sensitivity_move']))
        if 'sensitivity_aim' in kwargs:
            self.sensitivity_aim = max(0.3, min(1.5, kwargs['sensitivity_aim']))
        if 'invert_y' in kwargs:
            self.invert_y = bool(kwargs['invert_y'])
        if 'haptic_enabled' in kwargs:
            self.haptic_enabled = bool(kwargs['haptic_enabled'])
        if 'haptic_intensity' in kwargs:
            self.haptic_intensity = max(0.0, min(1.0, kwargs['haptic_intensity']))


# === INTEGRATION EXAMPLE ===

def example_game_loop():
    """Example showing how to use hard-locked controller in game loop"""
    pygame.init()
    controller = LockedControllerInput()

    # Optional: Configure sensitivity (NOT bindings)
    controller.configure(
        deadzone_move=0.12,
        sensitivity_move=1.2,
        invert_y=False,
        haptic_intensity=0.8
    )

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            controller.handle_event(event)

        # Update controller
        controller.update(dt)

        # Get inputs (NO if/else for different bindings - LOCKED)
        move_x, move_y = controller.get_movement()

        if controller.primary_fire:
            # Fire weapons
            pass

        if controller.is_action_just_pressed(GameAction.EMERGENCY_BURN):
            # Activate burn
            controller._rumble(0.6, 200)  # Haptic confirmation

        if controller.is_action_just_pressed(GameAction.CYCLE_AMMO_NEXT):
            # Next ammo type
            pass

        # ... rest of game logic ...

    pygame.quit()


if __name__ == "__main__":
    print("=== HARD-LOCKED CONTROLLER LAYOUT ===")
    print(f"Move: Left Stick (Axis {LAYOUT.MOVE_X_AXIS}, {LAYOUT.MOVE_Y_AXIS})")
    print(f"Aim: Right Stick (Axis {LAYOUT.AIM_X_AXIS}, {LAYOUT.AIM_Y_AXIS})")
    print(f"Fire: RT (Axis {LAYOUT.PRIMARY_FIRE_AXIS})")
    print(f"Rockets: LT (Axis {LAYOUT.ALTERNATE_FIRE_AXIS})")
    print(f"Cycle Ammo: LB/RB (Buttons {LAYOUT.BTN_CYCLE_AMMO_PREV}/{LAYOUT.BTN_CYCLE_AMMO_NEXT})")
    print(f"Emergency Burn: B (Button {LAYOUT.BTN_EMERGENCY_BURN})")
    print(f"Deploy Fleet: X (Button {LAYOUT.BTN_DEPLOY_FLEET})")
    print(f"Formation: Y (Button {LAYOUT.BTN_FORMATION_SWITCH})")
    print(f"Pause: Start (Button {LAYOUT.BTN_PAUSE})")
    print("\n✓ LAYOUT IS LOCKED - No rebinding allowed")
    print("✓ Customizable: Deadzone, Sensitivity, Haptics")
    print("✓ NOT Customizable: Button bindings")
