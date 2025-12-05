"""Touch controls module for mobile version of Minmatar Rebellion"""
import pygame
import math
from mobile_constants import *


class VirtualJoystick:
    """Virtual joystick for touch-based movement"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Calculate position based on screen size
        self.center_x = int(screen_width * JOYSTICK_AREA_X + JOYSTICK_RADIUS)
        self.center_y = int(screen_height * JOYSTICK_AREA_Y + JOYSTICK_RADIUS)
        self.radius = JOYSTICK_RADIUS
        self.knob_radius = JOYSTICK_KNOB_RADIUS
        
        # Current state
        self.active = False
        self.touch_id = None
        self.knob_x = self.center_x
        self.knob_y = self.center_y
        
        # Output values (-1 to 1)
        self.dx = 0
        self.dy = 0
    
    def handle_touch_down(self, touch_id, x, y):
        """Handle touch start"""
        if self.active:
            return False
        
        # Check if touch is within joystick area
        dist = math.sqrt((x - self.center_x) ** 2 + (y - self.center_y) ** 2)
        if dist <= self.radius * 1.5:  # Slightly larger touch area
            self.active = True
            self.touch_id = touch_id
            self._update_knob(x, y)
            return True
        return False
    
    def handle_touch_move(self, touch_id, x, y):
        """Handle touch movement"""
        if not self.active or touch_id != self.touch_id:
            return False
        
        self._update_knob(x, y)
        return True
    
    def handle_touch_up(self, touch_id):
        """Handle touch end"""
        if touch_id != self.touch_id:
            return False
        
        self.active = False
        self.touch_id = None
        self.knob_x = self.center_x
        self.knob_y = self.center_y
        self.dx = 0
        self.dy = 0
        return True
    
    def _update_knob(self, x, y):
        """Update knob position and output values"""
        # Calculate distance from center
        dx = x - self.center_x
        dy = y - self.center_y
        dist = math.sqrt(dx * dx + dy * dy)
        
        # Clamp to radius
        if dist > self.radius:
            scale = self.radius / dist
            dx *= scale
            dy *= scale
        
        # Update knob position
        self.knob_x = self.center_x + dx
        self.knob_y = self.center_y + dy
        
        # Calculate normalized output (-1 to 1)
        if dist > TOUCH_DEAD_ZONE:
            self.dx = dx / self.radius
            self.dy = dy / self.radius
        else:
            self.dx = 0
            self.dy = 0
    
    def draw(self, surface):
        """Draw joystick on screen"""
        # Create semi-transparent surface
        joystick_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        
        # Draw outer circle (base)
        center = (self.radius * 1.5, self.radius * 1.5)
        pygame.draw.circle(joystick_surface, TOUCH_CONTROL_COLOR, 
                          (int(center[0]), int(center[1])), self.radius)
        pygame.draw.circle(joystick_surface, (150, 150, 150, 180), 
                          (int(center[0]), int(center[1])), self.radius, 3)
        
        # Draw inner knob
        knob_offset_x = self.knob_x - self.center_x
        knob_offset_y = self.knob_y - self.center_y
        knob_color = TOUCH_CONTROL_ACTIVE if self.active else TOUCH_CONTROL_COLOR
        pygame.draw.circle(joystick_surface, knob_color,
                          (int(center[0] + knob_offset_x), int(center[1] + knob_offset_y)),
                          self.knob_radius)
        pygame.draw.circle(joystick_surface, (200, 200, 200, 200),
                          (int(center[0] + knob_offset_x), int(center[1] + knob_offset_y)),
                          self.knob_radius, 2)
        
        # Blit to main surface
        pos = (int(self.center_x - self.radius * 1.5), int(self.center_y - self.radius * 1.5))
        surface.blit(joystick_surface, pos)


class TouchButton:
    """Generic touch button"""
    
    def __init__(self, screen_width, screen_height, x_pct, y_pct, radius, color, label=""):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.x = int(screen_width * x_pct)
        self.y = int(screen_height * y_pct)
        self.radius = radius
        self.color = color
        self.label = label
        
        self.active = False
        self.touch_id = None
    
    def handle_touch_down(self, touch_id, x, y):
        """Check if touch is on this button"""
        if self.active:
            return False
        
        dist = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        if dist <= self.radius * 1.3:  # Slightly larger touch area
            self.active = True
            self.touch_id = touch_id
            return True
        return False
    
    def handle_touch_up(self, touch_id):
        """Handle touch end"""
        if touch_id != self.touch_id:
            return False
        
        self.active = False
        self.touch_id = None
        return True
    
    def draw(self, surface, font=None):
        """Draw button on screen"""
        btn_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
        center = (self.radius * 1.5, self.radius * 1.5)
        
        # Draw button circle
        color = tuple(min(c + 50, 255) if i < 3 else c for i, c in enumerate(self.color)) if self.active else self.color
        pygame.draw.circle(btn_surface, color, (int(center[0]), int(center[1])), self.radius)
        pygame.draw.circle(btn_surface, (200, 200, 200, 200), 
                          (int(center[0]), int(center[1])), self.radius, 2)
        
        # Draw label
        if self.label and font:
            text = font.render(self.label, True, (255, 255, 255))
            text_rect = text.get_rect(center=(int(center[0]), int(center[1])))
            btn_surface.blit(text, text_rect)
        
        pos = (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5))
        surface.blit(btn_surface, pos)


class AmmoButton(TouchButton):
    """Button for selecting ammo type"""
    
    def __init__(self, screen_width, screen_height, x_pct, y_pct, ammo_type, ammo_color, index):
        super().__init__(screen_width, screen_height, x_pct, y_pct, 
                        AMMO_BUTTON_SIZE // 2, (*ammo_color, 150), str(index + 1))
        self.ammo_type = ammo_type
        self.ammo_color = ammo_color
        self.locked = True
    
    def set_locked(self, locked):
        """Set whether this ammo type is locked"""
        self.locked = locked
    
    def draw(self, surface, font=None, current=False):
        """Draw ammo button with lock indicator"""
        if self.locked:
            # Draw grayed out
            btn_surface = pygame.Surface((self.radius * 3, self.radius * 3), pygame.SRCALPHA)
            center = (self.radius * 1.5, self.radius * 1.5)
            pygame.draw.circle(btn_surface, (50, 50, 50, 100), 
                              (int(center[0]), int(center[1])), self.radius)
            pygame.draw.circle(btn_surface, (100, 100, 100, 150), 
                              (int(center[0]), int(center[1])), self.radius, 2)
            pos = (int(self.x - self.radius * 1.5), int(self.y - self.radius * 1.5))
            surface.blit(btn_surface, pos)
        else:
            super().draw(surface, font)
            
            # Draw selection indicator if current
            if current:
                pygame.draw.circle(surface, (255, 255, 255), 
                                  (self.x, self.y), self.radius + 5, 3)


class TouchControls:
    """Manager for all touch controls"""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create joystick
        self.joystick = VirtualJoystick(screen_width, screen_height)
        
        # Create buttons
        self.fire_button = TouchButton(
            screen_width, screen_height,
            FIRE_BUTTON_X, FIRE_BUTTON_Y,
            FIRE_BUTTON_RADIUS, FIRE_BUTTON_COLOR, "FIRE"
        )
        
        self.rocket_button = TouchButton(
            screen_width, screen_height,
            ROCKET_BUTTON_X, ROCKET_BUTTON_Y,
            ROCKET_BUTTON_RADIUS, ROCKET_BUTTON_COLOR, "RKT"
        )
        
        self.pause_button = TouchButton(
            screen_width, screen_height,
            PAUSE_BUTTON_X, PAUSE_BUTTON_Y,
            PAUSE_BUTTON_SIZE // 2, TOUCH_CONTROL_COLOR, "II"
        )
        
        # Create ammo buttons
        self.ammo_buttons = []
        ammo_types = [
            ('sabot', (180, 180, 180)),
            ('emp', (50, 150, 255)),
            ('plasma', (255, 120, 0)),
            ('fusion', (255, 50, 50)),
            ('barrage', (220, 200, 50))
        ]
        
        for i, (ammo_type, color) in enumerate(ammo_types):
            y_offset = AMMO_BUTTONS_Y + (i * AMMO_BUTTON_SPACING / screen_height)
            btn = AmmoButton(
                screen_width, screen_height,
                AMMO_BUTTONS_X, y_offset,
                ammo_type, color, i
            )
            self.ammo_buttons.append(btn)
        
        # Track which ammo button was tapped (for single-tap selection)
        self.tapped_ammo = None
        
        self.font = None  # Will be set from game
    
    def set_font(self, font):
        """Set font for button labels"""
        self.font = font
    
    def update_unlocked_ammo(self, unlocked_list):
        """Update which ammo types are unlocked"""
        for btn in self.ammo_buttons:
            btn.set_locked(btn.ammo_type not in unlocked_list)
    
    def handle_event(self, event):
        """Handle pygame touch/mouse events"""
        self.tapped_ammo = None
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            touch_id = 0  # Mouse only has one "touch"
            
            # Check joystick first
            if self.joystick.handle_touch_down(touch_id, x, y):
                return
            
            # Check buttons
            if self.fire_button.handle_touch_down(touch_id, x, y):
                return
            if self.rocket_button.handle_touch_down(touch_id, x, y):
                return
            if self.pause_button.handle_touch_down(touch_id, x, y):
                return
            
            # Check ammo buttons
            for btn in self.ammo_buttons:
                if not btn.locked and btn.handle_touch_down(touch_id, x, y):
                    self.tapped_ammo = btn.ammo_type
                    return
        
        elif event.type == pygame.MOUSEBUTTONUP:
            touch_id = 0
            self.joystick.handle_touch_up(touch_id)
            self.fire_button.handle_touch_up(touch_id)
            self.rocket_button.handle_touch_up(touch_id)
            self.pause_button.handle_touch_up(touch_id)
            for btn in self.ammo_buttons:
                btn.handle_touch_up(touch_id)
        
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # Left button held
                x, y = event.pos
                touch_id = 0
                self.joystick.handle_touch_move(touch_id, x, y)
        
        # Handle touch events (for actual mobile)
        elif event.type == pygame.FINGERDOWN:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            touch_id = event.finger_id
            
            if self.joystick.handle_touch_down(touch_id, x, y):
                return
            if self.fire_button.handle_touch_down(touch_id, x, y):
                return
            if self.rocket_button.handle_touch_down(touch_id, x, y):
                return
            if self.pause_button.handle_touch_down(touch_id, x, y):
                return
            
            for btn in self.ammo_buttons:
                if not btn.locked and btn.handle_touch_down(touch_id, x, y):
                    self.tapped_ammo = btn.ammo_type
                    return
        
        elif event.type == pygame.FINGERUP:
            touch_id = event.finger_id
            self.joystick.handle_touch_up(touch_id)
            self.fire_button.handle_touch_up(touch_id)
            self.rocket_button.handle_touch_up(touch_id)
            self.pause_button.handle_touch_up(touch_id)
            for btn in self.ammo_buttons:
                btn.handle_touch_up(touch_id)
        
        elif event.type == pygame.FINGERMOTION:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
            touch_id = event.finger_id
            self.joystick.handle_touch_move(touch_id, x, y)
    
    def get_movement(self):
        """Get movement vector from joystick"""
        return self.joystick.dx, self.joystick.dy
    
    def is_firing(self):
        """Check if fire button is held"""
        return self.fire_button.active
    
    def is_rocket(self):
        """Check if rocket button is held"""
        return self.rocket_button.active
    
    def is_pause_pressed(self):
        """Check if pause was pressed"""
        return self.pause_button.active
    
    def get_ammo_tap(self):
        """Get ammo type that was tapped (or None)"""
        return self.tapped_ammo
    
    def draw(self, surface, current_ammo=None):
        """Draw all touch controls"""
        self.joystick.draw(surface)
        self.fire_button.draw(surface, self.font)
        self.rocket_button.draw(surface, self.font)
        self.pause_button.draw(surface, self.font)
        
        for btn in self.ammo_buttons:
            is_current = (btn.ammo_type == current_ammo)
            btn.draw(surface, self.font, is_current)
