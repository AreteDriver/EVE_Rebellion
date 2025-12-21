#!/usr/bin/env bash
# install_controller_support.sh
# Usage:
#   cd /path/to/EVE_Rebellion
#   chmod +x install_controller_support.sh
#   ./install_controller_support.sh
#
# What it does:
# - Creates controller_input.py if missing
# - Patches game.py (root) to add controller support
# - Creates backups: game.py.bak.<timestamp>

set -euo pipefail

ROOT="$(pwd)"
GAME_FILE="$ROOT/game.py"
CTRL_FILE="$ROOT/controller_input.py"

if [[ ! -f "$GAME_FILE" ]]; then
  echo "ERROR: game.py not found in: $ROOT"
  echo "Run this from your repo root (the folder containing game.py)."
  exit 1
fi

timestamp="$(date +%Y%m%d_%H%M%S)"
backup="$GAME_FILE.bak.$timestamp"
cp "$GAME_FILE" "$backup"
echo "Backup created: $backup"

# 1) Create controller_input.py if missing
if [[ -f "$CTRL_FILE" ]]; then
  echo "controller_input.py already exists, not overwriting."
else
  cat > "$CTRL_FILE" <<'PY'
"""
Drop-in controller input module for Minmatar Rebellion / EVE_Rebellion.

Integration contract:
- Call controller.start_frame() once per frame BEFORE reading events.
- Call controller.handle_event(event) for each pygame event.
- Call controller.update(dt) once per frame AFTER events are processed.
- Use controller.get_movement_vector() and controller.is_firing()/is_alternate_fire().
"""

from __future__ import annotations

import pygame
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class ControllerConfig:
    left_stick_deadzone: float = 0.15
    right_stick_deadzone: float = 0.20
    trigger_deadzone: float = 0.10
    movement_sensitivity: float = 1.0
    aim_sensitivity: float = 0.8


class ControllerInput:
    """
    Controller input handler for arcade shooters (pygame joystick).

    Defaults:
    - Left stick: movement
    - Triggers: RT primary fire, LT alternate fire (common XInput layout)
    - Buttons: exposed with edge detection (just pressed / held)

    Note: axis indices can vary by platform/controller. If triggers don’t work,
    change TRIGGER_AXES below.
    """

    # Common guess (LT, RT)
    TRIGGER_AXES = (4, 5)

    def __init__(self, config: Optional[ControllerConfig] = None, joystick_index: int = 0):
        self.config = config or ControllerConfig()
        self.joystick_index = joystick_index

        pygame.joystick.init()

        self.joystick: Optional[pygame.joystick.Joystick] = None
        self.connected = False
        self._connect()

        # Per-frame edge state
        self.buttons_pressed = set()
        self.buttons_just_pressed = set()
        self.buttons_just_released = set()

        # Analog state
        self.movement_x = 0.0
        self.movement_y = 0.0
        self.aim_offset_x = 0.0
        self.aim_offset_y = 0.0

        # Fire state
        self.primary_fire = False
        self.alternate_fire = False
        self.primary_pressure = 0.0

    def _connect(self) -> None:
        count = pygame.joystick.get_count()
        if count <= 0:
            self.connected = False
            self.joystick = None
            return

        idx = min(self.joystick_index, count - 1)
        js = pygame.joystick.Joystick(idx)
        js.init()
        self.joystick = js
        self.connected = True
        print(f"[controller] connected: {js.get_name()} ({idx})")

    def reconnect(self) -> None:
        if not self.connected:
            self._connect()

    def start_frame(self) -> None:
        """Call once per frame before handling pygame events."""
        self.buttons_just_pressed.clear()
        self.buttons_just_released.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.JOYDEVICEADDED:
            self._connect()
            return

        if event.type == pygame.JOYDEVICEREMOVED:
            self.connected = False
            self.joystick = None
            return

        if not self.connected:
            return

        if event.type == pygame.JOYBUTTONDOWN:
            b = event.button
            self.buttons_pressed.add(b)
            self.buttons_just_pressed.add(b)

        elif event.type == pygame.JOYBUTTONUP:
            b = event.button
            self.buttons_pressed.discard(b)
            self.buttons_just_released.add(b)

    def update(self, dt: float) -> None:
        """Call once per frame AFTER events are processed."""
        if not self.connected or not self.joystick:
            self.movement_x = 0.0
            self.movement_y = 0.0
            self.aim_offset_x = 0.0
            self.aim_offset_y = 0.0
            self.primary_fire = False
            self.alternate_fire = False
            self.primary_pressure = 0.0
            return

        # Left stick
        lx = self._apply_deadzone(self.joystick.get_axis(0), self.config.left_stick_deadzone)
        ly = self._apply_deadzone(self.joystick.get_axis(1), self.config.left_stick_deadzone)

        # Right stick (optional aim offset)
        rx = 0.0
        ry = 0.0
        if self.joystick.get_numaxes() >= 4:
            rx = self._apply_deadzone(self.joystick.get_axis(2), self.config.right_stick_deadzone)
            ry = self._apply_deadzone(self.joystick.get_axis(3), self.config.right_stick_deadzone)

        self.movement_x = self._momentum_curve(lx) * self.config.movement_sensitivity
        self.movement_y = self._momentum_curve(ly) * self.config.movement_sensitivity

        # Aim offset (pixels) if you later want aim bias
        self.aim_offset_x = rx * self.config.aim_sensitivity * 30.0
        self.aim_offset_y = ry * self.config.aim_sensitivity * 30.0

        # Triggers
        lt, rt = self._read_triggers()
        self.primary_fire = rt > 0.1
        self.alternate_fire = lt > 0.1
        self.primary_pressure = rt

    def _read_triggers(self) -> Tuple[float, float]:
        if not self.joystick:
            return 0.0, 0.0

        lt_axis, rt_axis = self.TRIGGER_AXES

        def safe_axis(i: int) -> float:
            try:
                return self.joystick.get_axis(i)
            except Exception:
                return 0.0

        lt = self._apply_deadzone(safe_axis(lt_axis), self.config.trigger_deadzone)
        rt = self._apply_deadzone(safe_axis(rt_axis), self.config.trigger_deadzone)

        # Normalize -1..1 to 0..1 if needed
        lt = (lt + 1.0) / 2.0 if lt < 0 else lt
        rt = (rt + 1.0) / 2.0 if rt < 0 else rt
        return lt, rt

    @staticmethod
    def _apply_deadzone(value: float, deadzone: float) -> float:
        if abs(value) < deadzone:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - deadzone) / (1.0 - deadzone)
        return sign * scaled

    @staticmethod
    def _momentum_curve(v: float) -> float:
        if v == 0.0:
            return 0.0
        sign = 1.0 if v > 0 else -1.0
        return sign * (abs(v) ** 1.8)

    def get_movement_vector(self) -> Tuple[float, float]:
        return (self.movement_x, self.movement_y)

    def get_aim_offset(self) -> Tuple[float, float]:
        return (self.aim_offset_x, self.aim_offset_y)

    def is_firing(self) -> bool:
        return self.primary_fire

    def is_alternate_fire(self) -> bool:
        return self.alternate_fire

    def get_fire_pressure(self) -> float:
        return self.primary_pressure

    def is_button_just_pressed(self, button: int) -> bool:
        return button in self.buttons_just_pressed

    def is_button_held(self, button: int) -> bool:
        return button in self.buttons_pressed


class XboxButton:
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
PY
  echo "Created: controller_input.py"
fi

# 2) Patch game.py using a small python patcher (idempotent)
python3 - <<'PY'
import re
from pathlib import Path

p = Path("game.py")
s = p.read_text(encoding="utf-8")

def ensure_once(insert: str, after_pattern: str) -> str:
    if insert in s:
        return s
    m = re.search(after_pattern, s, flags=re.M)
    if not m:
        raise SystemExit(f"Could not find insertion point for pattern: {after_pattern}")
    idx = m.end()
    return s[:idx] + insert + s[idx:]

# 2a) import line
if "from controller_input import ControllerInput, XboxButton" not in s:
    # Insert after sounds import line
    m = re.search(r"^from sounds import .*?$", s, flags=re.M)
    if not m:
        raise SystemExit("Could not find sounds import line to insert controller import.")
    insert = "\nfrom controller_input import ControllerInput, XboxButton"
    s = s[:m.end()] + insert + s[m.end():]

# 2b) init in __init__
if "self.controller = ControllerInput()" not in s:
    m = re.search(r"self\.font_small\s*=\s*pygame\.font\.Font\(None,\s*22\)\s*\n", s)
    if not m:
        raise SystemExit("Could not find font_small init to insert controller init after it.")
    insert = "\n        # Controller (optional)\n        self.controller = ControllerInput()\n"
    s = s[:m.end()] + insert + s[m.end():]

# 2c) handle_events: start_frame + handle_event injection
if "self.controller.start_frame()" not in s:
    m = re.search(r"def handle_events\(self\):\n\s+\"\"\"Process input events\"\"\"\n\s+for event in pygame\.event\.get\(\):", s)
    if not m:
        raise SystemExit("Could not find handle_events() event loop.")
    # Replace the "for event in pygame.event.get():" line with prelude + loop
    s = re.sub(
        r"(def handle_events\(self\):\n\s+\"\"\"Process input events\"\"\"\n)(\s+for event in pygame\.event\.get\(\):)",
        r"\1        # Controller: start frame (clears edge states)\n        if self.controller:\n            self.controller.start_frame()\n\n\2",
        s,
        count=1
    )

if "self.controller.handle_event(event)" not in s:
    # Insert just after `for event in pygame.event.get():`
    s = re.sub(
        r"(\s+for event in pygame\.event\.get\(\):\n)",
        r"\1            # Feed controller events first\n            if self.controller:\n                self.controller.handle_event(event)\n\n",
        s,
        count=1
    )

# 2d) update(): controller.update + analog movement overlay
if "self.controller.update(dt)" not in s:
    s = re.sub(
        r"(keys\s*=\s*pygame\.key\.get_pressed\(\)\s*\n)",
        r"\1\n        # Controller update (dt in seconds)\n        dt = self.clock.get_time() / 1000.0\n        if self.controller:\n            self.controller.update(dt)\n",
        s,
        count=1
    )

if "move_x, move_y = self.controller.get_movement_vector()" not in s:
    s = re.sub(
        r"(# Update player\s*\n\s*self\.player\.update\(keys\)\s*\n)",
        r"\1\n        # Add controller movement on top of keyboard (analog)\n        if self.controller and self.controller.connected:\n            move_x, move_y = self.controller.get_movement_vector()\n            self.player.rect.x += move_x * self.player.speed\n            self.player.rect.y += move_y * self.player.speed\n            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))\n",
        s,
        count=1
    )

# 2e) firing / rockets: add controller booleans (non-destructive)
if "controller_fire" not in s:
    s = re.sub(
        r"(\s*# Player shooting\s*\n)(\s*if\s+keys\[pygame\.K_SPACE\]\s+or\s+pygame\.mouse\.get_pressed\(\)\[0\]\s*:)",
        r"\1        controller_fire = self.controller.is_firing() if (self.controller and self.controller.connected) else False\n\2",
        s,
        count=1
    )
    s = s.replace(
        "if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:",
        "if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] or controller_fire:"
    )

if "controller_rocket" not in s:
    s = re.sub(
        r"(\s*# Rockets\s*\n)(\s*if\s+keys\[pygame\.K_LSHIFT\]\s+or\s+keys\[pygame\.K_RSHIFT\]\s+or\s+pygame\.mouse\.get_pressed\(\)\[2\]\s*:)",
        r"\1        controller_rocket = self.controller.is_alternate_fire() if (self.controller and self.controller.connected) else False\n\2",
        s,
        count=1
    )
    s = s.replace(
        "if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2]:",
        "if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2] or controller_rocket:"
    )

# 2f) Pause + ammo cycle via controller (minimal, safe insertion inside handle_events loop)
if "XboxButton.RB" not in s:
    # Insert near other state checks: after KEYDOWN block starts is fragile, so append near end of event loop
    anchor = "elif event.type == pygame.KEYDOWN:"
    if anchor in s:
        # Add a small controller shortcut block just before the end of the for-event loop
        # Find first occurrence of "elif event.type == pygame.KEYDOWN:" and ensure we only inject once
        pass

# Safer: add controller shortcuts near top of event loop (after quit handling, before KEYDOWN)
if "Controller button shortcuts" not in s:
    s = re.sub(
        r"(if event\.type == pygame\.QUIT:\n\s+self\.running = False\s*\n)",
        r"\1\n            # Controller button shortcuts (pause/ammo) while playing\n            if self.controller and self.controller.connected:\n                if self.state == 'playing':\n                    if self.controller.is_button_just_pressed(XboxButton.START):\n                        self.state = 'paused'\n                        self.play_sound('menu_select')\n                    if self.controller.is_button_just_pressed(XboxButton.RB):\n                        self.player.cycle_ammo()\n                        self.play_sound('ammo_switch')\n                elif self.state == 'paused':\n                    if self.controller.is_button_just_pressed(XboxButton.START):\n                        self.state = 'playing'\n                        self.play_sound('menu_select')\n",
        s,
        count=1
    )

p.write_text(s, encoding="utf-8")
print("Patched game.py successfully.")
PY

echo "Done."
echo "Run: python3 main.py  (or python3 game.py if that's what your build uses)"

