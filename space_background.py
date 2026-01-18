"""
Enhanced Background System for Minmatar Rebellion
Realistic space backgrounds with mechanical carrier intensity
"""

import pygame
import random
import math


class LaunchedFighter:
    """
    A fighter/drone visibly launched from the Archon carrier.
    Uses proper Amarr ship renders matching the game's aesthetic.
    """

    # Ship types: 'fighter' (small agile), 'drone' (tiny swarm), 'bomber' (larger)
    SHIP_TYPES = ['fighter', 'fighter', 'fighter', 'drone', 'drone', 'bomber']

    def __init__(self, x, y, target_x, target_y, formation_delay=0):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.target_x = target_x
        self.target_y = target_y

        # Ship type determines visuals
        self.ship_type = random.choice(self.SHIP_TYPES)

        # Calculate trajectory
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)

        # Speed varies by type - smaller ships for massive carrier scale
        if self.ship_type == 'drone':
            self.speed = random.uniform(5.0, 7.0)
            self.size = random.randint(6, 9)  # Tiny drones
        elif self.ship_type == 'bomber':
            self.speed = random.uniform(3.0, 4.5)
            self.size = random.randint(12, 16)  # Medium bombers
        else:  # fighter
            self.speed = random.uniform(4.5, 6.0)
            self.size = random.randint(8, 12)  # Small fighters

        self.vx = (dx / dist) * self.speed if dist > 0 else 0
        self.vy = (dy / dist) * self.speed if dist > 0 else self.speed

        # Launch delay for formation effect
        self.delay = formation_delay
        self.active = formation_delay == 0

        # Visual state
        self.engine_flicker = 0
        self.trail = []
        self.lifetime = 350
        self.alpha = 255

        # Pre-render the ship sprite
        self.sprite = self._create_ship_sprite()

    def _create_ship_sprite(self):
        """Create Amarr-style ship sprite based on type"""
        size = self.size
        w, h = size * 2, size * 2
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        cx, cy = size, size

        # Amarr color palette
        gold_dark = (90, 70, 35)
        gold_mid = (130, 105, 50)
        gold_light = (170, 145, 80)
        gold_highlight = (210, 190, 120)
        hull_shadow = (55, 42, 22)
        engine_core = (255, 180, 100)
        engine_glow = (255, 140, 60)

        if self.ship_type == 'drone':
            # Small Amarr combat drone - compact angular design
            # Main body - hexagonal
            body_points = [
                (cx, cy - size * 0.6),      # Top
                (cx + size * 0.5, cy - size * 0.25),
                (cx + size * 0.5, cy + size * 0.25),
                (cx, cy + size * 0.5),      # Bottom
                (cx - size * 0.5, cy + size * 0.25),
                (cx - size * 0.5, cy - size * 0.25),
            ]
            pygame.draw.polygon(surf, gold_mid, body_points)
            pygame.draw.polygon(surf, hull_shadow, body_points, 1)

            # Central eye/sensor
            pygame.draw.circle(surf, (60, 80, 100), (cx, cy - size * 0.1), size * 0.2)
            pygame.draw.circle(surf, (100, 130, 160), (cx, cy - size * 0.1), size * 0.12)

            # Wing stubs
            pygame.draw.polygon(surf, gold_dark, [
                (cx - size * 0.5, cy), (cx - size * 0.7, cy + size * 0.1),
                (cx - size * 0.5, cy + size * 0.25)
            ])
            pygame.draw.polygon(surf, gold_dark, [
                (cx + size * 0.5, cy), (cx + size * 0.7, cy + size * 0.1),
                (cx + size * 0.5, cy + size * 0.25)
            ])

            # Engine (small)
            pygame.draw.circle(surf, engine_glow, (cx, int(cy + size * 0.4)), 2)

        elif self.ship_type == 'bomber':
            # Larger Amarr bomber - elongated heavy design
            # Main hull
            hull_points = [
                (cx, cy - size * 0.8),      # Nose
                (cx + size * 0.35, cy - size * 0.5),
                (cx + size * 0.4, cy + size * 0.3),
                (cx + size * 0.25, cy + size * 0.7),
                (cx, cy + size * 0.8),      # Tail
                (cx - size * 0.25, cy + size * 0.7),
                (cx - size * 0.4, cy + size * 0.3),
                (cx - size * 0.35, cy - size * 0.5),
            ]
            pygame.draw.polygon(surf, gold_mid, hull_points)
            pygame.draw.polygon(surf, hull_shadow, hull_points, 2)

            # Upper hull highlight
            pygame.draw.polygon(surf, gold_light, [
                (cx, cy - size * 0.75),
                (cx + size * 0.3, cy - size * 0.4),
                (cx + size * 0.15, cy),
                (cx, cy - size * 0.2),
            ])

            # Central dome
            pygame.draw.ellipse(surf, gold_light,
                               (cx - size * 0.15, cy - size * 0.3, size * 0.3, size * 0.25))
            pygame.draw.ellipse(surf, gold_highlight,
                               (cx - size * 0.08, cy - size * 0.25, size * 0.16, size * 0.15))

            # Wing pylons
            for side in [-1, 1]:
                pylon_x = cx + side * size * 0.45
                pygame.draw.polygon(surf, gold_dark, [
                    (pylon_x, cy - size * 0.2),
                    (pylon_x + side * size * 0.25, cy + size * 0.1),
                    (pylon_x + side * size * 0.2, cy + size * 0.4),
                    (pylon_x, cy + size * 0.3),
                ])

            # Dual engines
            for offset in [-size * 0.15, size * 0.15]:
                ex = cx + offset
                pygame.draw.ellipse(surf, (80, 50, 30),
                                   (ex - 4, cy + size * 0.65, 8, 10))
                pygame.draw.ellipse(surf, engine_glow, (ex - 2, cy + size * 0.7, 4, 6))
                pygame.draw.ellipse(surf, engine_core, (ex - 1, cy + size * 0.72, 2, 4))

        else:  # fighter
            # Amarr fighter - sleek angular design
            # Main hull - diamond shape
            hull_points = [
                (cx, cy - size * 0.75),     # Nose
                (cx + size * 0.4, cy - size * 0.2),
                (cx + size * 0.35, cy + size * 0.5),
                (cx, cy + size * 0.7),      # Tail
                (cx - size * 0.35, cy + size * 0.5),
                (cx - size * 0.4, cy - size * 0.2),
            ]
            pygame.draw.polygon(surf, gold_mid, hull_points)
            pygame.draw.polygon(surf, hull_shadow, hull_points, 1)

            # Upper hull shading
            pygame.draw.polygon(surf, gold_light, [
                (cx, cy - size * 0.7),
                (cx + size * 0.35, cy - size * 0.15),
                (cx + size * 0.1, cy + size * 0.1),
                (cx, cy - size * 0.1),
            ])

            # Cockpit
            pygame.draw.ellipse(surf, (50, 65, 85),
                               (cx - size * 0.12, cy - size * 0.35, size * 0.24, size * 0.3))
            pygame.draw.ellipse(surf, (80, 100, 130),
                               (cx - size * 0.08, cy - size * 0.3, size * 0.16, size * 0.2))

            # Nacelles/wings
            pygame.draw.polygon(surf, gold_dark, [
                (cx - size * 0.4, cy - size * 0.15),
                (cx - size * 0.6, cy + size * 0.15),
                (cx - size * 0.5, cy + size * 0.45),
                (cx - size * 0.35, cy + size * 0.4),
            ])
            pygame.draw.polygon(surf, gold_dark, [
                (cx + size * 0.4, cy - size * 0.15),
                (cx + size * 0.6, cy + size * 0.15),
                (cx + size * 0.5, cy + size * 0.45),
                (cx + size * 0.35, cy + size * 0.4),
            ])

            # Engine
            pygame.draw.ellipse(surf, (80, 50, 30),
                               (cx - 4, cy + size * 0.55, 8, 10))
            pygame.draw.ellipse(surf, engine_glow, (cx - 2, cy + size * 0.6, 4, 6))
            pygame.draw.ellipse(surf, engine_core, (cx - 1, cy + size * 0.62, 2, 4))

        return surf

    def update(self):
        if self.delay > 0:
            self.delay -= 1
            if self.delay == 0:
                self.active = True
            return True

        if not self.active:
            return True

        # Store trail position
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)

        # Move toward target
        self.x += self.vx
        self.y += self.vy

        # Engine flicker
        self.engine_flicker = random.uniform(0.7, 1.0)

        self.lifetime -= 1
        if self.lifetime < 40:
            self.alpha = int(255 * (self.lifetime / 40))

        # Remove when off screen or expired
        return self.lifetime > 0 and self.y < 1500

    def draw(self, surface):
        if not self.active or self.alpha <= 0:
            return

        # Draw engine trail
        trail_len = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            progress = (i + 1) / trail_len
            trail_alpha = int(50 * progress * (self.alpha / 255))
            trail_size = int(2 + progress * 3)
            if trail_alpha > 0:
                trail_surf = pygame.Surface((trail_size * 2, trail_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (255, 160, 60, trail_alpha),
                                 (trail_size, trail_size), trail_size)
                surface.blit(trail_surf, (int(tx) - trail_size, int(ty) - trail_size))

        # Draw the ship sprite with alpha
        if self.alpha < 255:
            sprite_copy = self.sprite.copy()
            sprite_copy.set_alpha(self.alpha)
            surface.blit(sprite_copy, (int(self.x) - self.size, int(self.y) - self.size))
        else:
            surface.blit(self.sprite, (int(self.x) - self.size, int(self.y) - self.size))


class AmarrArchon:
    """
    The Amarr Archon carrier - massive capital ship with mechanical intensity.
    Acts as a "level" - approaches over 5 waves, boss fight, then departs.
    Creates a 3D feel with distance-based scaling.
    """

    # Carrier states
    STATE_APPROACHING = 'approaching'  # Warping in from distance
    STATE_ENGAGING = 'engaging'        # Actively launching waves
    STATE_BOSS = 'boss'                # Boss fight phase
    STATE_DEPARTING = 'departing'      # Warping out after defeat
    STATE_GONE = 'gone'                # Ready for next carrier

    # Carrier variations for visual variety
    CARRIER_VARIANTS = [
        {'name': 'Archon', 'hull_tint': (90, 75, 55), 'approach_angle': 0},
        {'name': 'Thanatos', 'hull_tint': (60, 70, 85), 'approach_angle': -15},  # Bluish
        {'name': 'Aeon', 'hull_tint': (100, 85, 45), 'approach_angle': 10},      # More gold
        {'name': 'Avatar', 'hull_tint': (75, 65, 55), 'approach_angle': -8},     # Darker
    ]

    def __init__(self, screen_width, screen_height, carrier_number=1):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.carrier_number = carrier_number

        # Pick variant based on carrier number
        self.variant = self.CARRIER_VARIANTS[(carrier_number - 1) % len(self.CARRIER_VARIANTS)]

        # State machine
        self.state = self.STATE_APPROACHING
        self.waves_completed = 0
        self.waves_per_carrier = 5  # 5 waves then boss

        # Position - starts FAR in background
        self.x = screen_width // 2
        self.approach_offset_x = random.randint(-100, 100)  # Slight horizontal variance

        # Distance system (0.0 = far, 1.0 = close)
        # 3x FARTHER - carrier should feel massive and distant like EVE
        self.distance = 0.0  # Start far away
        self.target_distance = 0.0
        self.approach_speed = 0.001  # Slower approach for scale

        # Approach angle for 3D feel
        self.approach_angle = math.radians(self.variant['approach_angle'])

        # Size scales with distance (smaller when far)
        # Archon is ~2920m - should feel MASSIVE even at distance
        self.min_scale = 0.05  # 5% size when far (distant carrier)
        self.max_scale = 0.30  # 30% size when "close" (still distant - it's huge)
        self.current_scale = self.min_scale

        # Calculate y position based on distance - stays higher on screen
        self.far_y = 60   # Y position when far (very near top)
        self.close_y = 160  # Y position when close (still upper third)
        self.y = self.far_y
        self.base_y = self.y

        # Warp effects
        self.warp_intensity = 1.0
        self.warp_in_timer = 0
        self.warp_in_duration = 180  # 3 seconds to warp in
        self.warp_out_timer = 0
        self.warp_out_duration = 120  # 2 seconds to warp out

        # Backward compatibility entrance vars
        self.entrance_timer = 0
        self.entrance_duration = 240  # 4 seconds
        self.target_y = self.close_y

        # Visual state
        self.hover_offset = 0
        self.hover_timer = 0
        self.engine_pulse = 0
        self.hangar_glow = 0
        self.launch_flash = 0

        # Mechanical rumble
        self.rumble_offset_x = 0
        self.rumble_offset_y = 0

        # Launched fighters
        self.launched_fighters = []

        # Generate initial sprites at smallest scale
        self._regenerate_sprites()

    def _regenerate_sprites(self):
        """Regenerate carrier sprites at current scale"""
        # Calculate size based on distance
        self.current_scale = self.min_scale + (self.max_scale - self.min_scale) * self.distance
        self.size = int(self.screen_width * self.current_scale)

        # Regenerate sprite surfaces
        self.surface = self._create_archon_sprite()
        self.glow_surface = self._create_engine_glow()

    def _create_archon_sprite(self):
        """Create detailed Archon carrier - industrial/military aesthetic"""
        size = self.size
        surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        cx, cy = size, size // 2

        # Muted Amarr military palette - less gold, more gunmetal
        hull_main = (90, 75, 55)
        hull_dark = (50, 42, 32)
        hull_plate = (110, 95, 70)
        metal_accent = (130, 115, 85)
        window_dim = (180, 160, 120)

        # Main hull - angular military design
        hull_points = [
            (cx - size * 0.9, cy),
            (cx - size * 0.7, cy - size * 0.32),
            (cx - size * 0.3, cy - size * 0.38),
            (cx + size * 0.2, cy - size * 0.35),
            (cx + size * 0.6, cy - size * 0.22),
            (cx + size * 0.88, cy),
            (cx + size * 0.6, cy + size * 0.22),
            (cx + size * 0.2, cy + size * 0.35),
            (cx - size * 0.3, cy + size * 0.38),
            (cx - size * 0.7, cy + size * 0.32),
        ]
        pygame.draw.polygon(surf, hull_main, hull_points)
        pygame.draw.polygon(surf, hull_dark, hull_points, 2)

        # Armored plating segments
        for i in range(4):
            plate_x = cx - size * 0.5 + i * size * 0.25
            plate_points = [
                (plate_x, cy - size * 0.25),
                (plate_x + size * 0.2, cy - size * 0.28),
                (plate_x + size * 0.22, cy - size * 0.15),
                (plate_x + size * 0.02, cy - size * 0.12),
            ]
            pygame.draw.polygon(surf, hull_plate, plate_points)
            pygame.draw.polygon(surf, hull_dark, plate_points, 1)

        # Command bridge - armored dome
        pygame.draw.ellipse(surf, hull_plate,
                           (cx - size * 0.12, cy - size * 0.22, size * 0.24, size * 0.18))
        pygame.draw.ellipse(surf, hull_dark,
                           (cx - size * 0.12, cy - size * 0.22, size * 0.24, size * 0.18), 1)

        # Bridge viewports (dim, not glowing)
        for i in range(4):
            wx = cx - size * 0.06 + i * (size * 0.04)
            pygame.draw.rect(surf, window_dim, (wx, cy - size * 0.16, size * 0.02, size * 0.04))

        # MAIN HANGAR BAY - large and prominent
        hangar_x = cx - size * 0.18
        hangar_y = cy + size * 0.18
        hangar_w = size * 0.36
        hangar_h = size * 0.14

        # Hangar interior (dark void)
        pygame.draw.rect(surf, (15, 12, 8), (hangar_x, hangar_y, hangar_w, hangar_h))
        # Hangar frame (heavy industrial)
        pygame.draw.rect(surf, metal_accent, (hangar_x, hangar_y, hangar_w, hangar_h), 3)
        # Inner frame
        pygame.draw.rect(surf, hull_dark,
                        (hangar_x + 4, hangar_y + 4, hangar_w - 8, hangar_h - 8), 1)

        # Secondary hangars
        for offset in [-size * 0.4, size * 0.4]:
            hx = cx + offset - size * 0.07
            pygame.draw.rect(surf, (20, 16, 12),
                            (hx, cy + size * 0.12, size * 0.14, size * 0.1))
            pygame.draw.rect(surf, hull_dark,
                            (hx, cy + size * 0.12, size * 0.14, size * 0.1), 2)

        # Engine nacelles - large and industrial
        for offset in [-0.28, -0.1, 0.1, 0.28]:
            ex = cx - size * 0.82
            ey = cy + size * offset
            # Engine housing
            pygame.draw.ellipse(surf, hull_dark,
                               (ex - size * 0.1, ey - size * 0.055, size * 0.18, size * 0.11))
            pygame.draw.ellipse(surf, (30, 25, 20),
                               (ex - size * 0.06, ey - size * 0.03, size * 0.1, size * 0.06))

        # Hull detail lines
        pygame.draw.line(surf, hull_dark,
                        (cx - size * 0.6, cy - size * 0.1),
                        (cx + size * 0.5, cy - size * 0.1), 1)
        pygame.draw.line(surf, hull_dark,
                        (cx - size * 0.6, cy + size * 0.1),
                        (cx + size * 0.5, cy + size * 0.1), 1)

        return surf

    def _create_engine_glow(self):
        """Create engine glow - amber/orange industrial look"""
        size = self.size
        surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        cx, cy = size, size // 2

        for offset in [-0.28, -0.1, 0.1, 0.28]:
            ex = cx - size * 0.82
            ey = cy + size * offset

            # Outer glow
            for r in range(18, 0, -3):
                alpha = max(5, 40 - r * 2)
                pygame.draw.circle(surf, (255, 140, 50, alpha), (int(ex), int(ey)), r)

            # Core
            pygame.draw.circle(surf, (255, 180, 100, 150), (int(ex), int(ey)), 6)
            pygame.draw.circle(surf, (255, 220, 180, 200), (int(ex), int(ey)), 3)

        return surf

    def trigger_launch(self):
        """Trigger launch effect and spawn visible fighters"""
        self.launch_flash = 40
        self.hangar_glow = 255

        # Spawn a formation of fighters
        self._launch_fighter_formation()

    def _launch_fighter_formation(self):
        """Launch a formation of fighters from the massive carrier's hangars"""
        hangar_x = self.x
        hangar_y = self.y + self.size * 0.35

        # Wider formations for massive carrier - launch from multiple hangars
        formations = [
            # Wide V-formation
            [(0, 0), (-60, -20), (60, -20), (-120, -40), (120, -40), (-180, -60), (180, -60)],
            # Triple line (3 hangars)
            [(-150, 0), (-100, 0), (-50, 0), (0, 0), (50, 0), (100, 0), (150, 0)],
            # Diamond formation
            [(0, 0), (-80, -30), (80, -30), (-160, -60), (160, -60), (0, -60)],
            # Swarm pattern
            [(0, 0), (-40, -15), (40, -15), (-80, -30), (80, -30),
             (-20, -45), (20, -45), (-60, -60), (60, -60)],
        ]

        formation = random.choice(formations)
        num_fighters = random.randint(4, len(formation))

        for i in range(num_fighters):
            offset_x, offset_y = formation[i]
            fighter = LaunchedFighter(
                hangar_x + offset_x * 0.3,  # Start more clustered at hangar
                hangar_y,
                hangar_x + offset_x + random.randint(-30, 30),  # Spread to formation
                1600,  # Target off bottom of screen
                formation_delay=i * 4  # Faster staggered launch
            )
            self.launched_fighters.append(fighter)

    def get_spawn_position(self):
        """Get spawn position (below hangar)"""
        return (self.x, int(self.y + self.size * 0.45))

    @property
    def entering(self):
        """Backward compatibility - True when in approaching state"""
        return self.state == self.STATE_APPROACHING

    def update(self):
        """Update carrier state machine"""
        # Handle state transitions
        if self.state == self.STATE_APPROACHING:
            self.entrance_timer += 1
            progress = self.entrance_timer / self.entrance_duration

            # Ease-out movement
            ease = 1 - (1 - progress) ** 3
            self.y = -300 + (self.target_y + 300) * ease

            # Warp distortion decreases
            self.warp_intensity = 1 - progress

            # Mechanical rumble during entry
            if progress < 0.7:
                self.rumble_offset_x = random.uniform(-3, 3) * (1 - progress)
                self.rumble_offset_y = random.uniform(-2, 2) * (1 - progress)
            else:
                self.rumble_offset_x *= 0.9
                self.rumble_offset_y *= 0.9

            if self.entrance_timer >= self.entrance_duration:
                self.state = self.STATE_ENGAGING  # Transition to engaging
                self.y = self.target_y
                self.base_y = self.y
        else:
            # Gentle hover
            self.hover_timer += 0.015
            self.hover_offset = math.sin(self.hover_timer) * 4
            self.y = self.base_y + self.hover_offset

            # Minimal rumble
            self.rumble_offset_x *= 0.95
            self.rumble_offset_y *= 0.95

        # Engine pulse
        self.engine_pulse = 0.75 + 0.25 * math.sin(self.hover_timer * 2.5)

        # Decay effects
        if self.launch_flash > 0:
            self.launch_flash -= 1
        if self.hangar_glow > 0:
            self.hangar_glow = max(0, self.hangar_glow - 6)

        # Update launched fighters
        self.launched_fighters = [f for f in self.launched_fighters if f.update()]

    def draw(self, surface):
        """Draw the carrier with all effects"""
        draw_x = self.x - self.size + self.rumble_offset_x
        draw_y = int(self.y - self.size // 2 + self.rumble_offset_y)

        # Warp effect during entrance
        if self.entering and self.warp_intensity > 0.1:
            self._draw_warp_effect(surface, draw_x, draw_y)

        # Engine glow
        glow_alpha = int(180 * self.engine_pulse)
        glow_copy = self.glow_surface.copy()
        glow_copy.set_alpha(glow_alpha)
        surface.blit(glow_copy, (draw_x, draw_y))

        # Main carrier
        surface.blit(self.surface, (draw_x, draw_y))

        # Hangar glow effect
        if self.launch_flash > 0 or self.hangar_glow > 0:
            self._draw_hangar_glow(surface)

        # Draw launched fighters
        for fighter in self.launched_fighters:
            fighter.draw(surface)

    def _draw_warp_effect(self, surface, draw_x, draw_y):
        """Draw warp/jump entrance effect"""
        intensity = self.warp_intensity

        # Stretched light lines
        for i in range(int(20 * intensity)):
            lx = self.x + random.randint(-self.size, self.size)
            ly = self.y + random.randint(-self.size // 2, self.size // 2)
            length = int(50 + 100 * intensity)
            alpha = int(100 * intensity)

            line_surf = pygame.Surface((8, length), pygame.SRCALPHA)
            # Gradient line
            for j in range(length):
                a = int(alpha * (1 - j / length))
                pygame.draw.line(line_surf, (200, 180, 140, a), (4, j), (4, j))

            surface.blit(line_surf, (lx - 4, ly - length))

    def _draw_hangar_glow(self, surface):
        """Draw hangar launch glow"""
        hx = int(self.x + self.rumble_offset_x)
        hy = int(self.y + self.size * 0.25 + self.rumble_offset_y)

        intensity = max(self.launch_flash * 6, self.hangar_glow)

        # Rectangular glow matching hangar shape
        glow_w, glow_h = int(self.size * 0.4), int(self.size * 0.2)
        glow_surf = pygame.Surface((glow_w, glow_h), pygame.SRCALPHA)

        alpha = min(200, intensity)
        pygame.draw.rect(glow_surf, (255, 200, 120, alpha), (0, 0, glow_w, glow_h))

        # Bright center
        if self.launch_flash > 20:
            core_alpha = min(255, (self.launch_flash - 20) * 12)
            pygame.draw.rect(glow_surf, (255, 240, 200, core_alpha),
                           (glow_w // 4, glow_h // 4, glow_w // 2, glow_h // 2))

        surface.blit(glow_surf, (hx - glow_w // 2, hy - glow_h // 2))


class SpaceBackground:
    """Dynamic space background - intense arcade action with EVE atmosphere"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Create layered background
        self.nebula_layer = self.create_nebula(width, height)

        # Scale object counts to screen size - MORE objects for intensity
        star_count = int(width * height / 6000)  # More stars
        asteroid_count = int(width / 35)  # More asteroids (~51)
        debris_count = int(width / 60)  # More debris (~30)

        self.star_field = self.create_star_field(star_count)
        self.asteroids = self.create_asteroid_field(asteroid_count)
        self.debris = self.create_debris_field(debris_count)
        self.distant_structures = self.create_distant_structures(8)
        self.wrecks = self.create_ship_wrecks(5)

        # Dynamic effects - intense arcade atmosphere
        self.flashes = []  # Explosions
        self.flash_timer = 0
        self.laser_beams = []  # Sweeping laser beams
        self.energy_pulses = []  # Energy wave effects
        self.tracer_fire = []  # Background firefights

        # Environmental hazard timers
        self.beam_spawn_timer = 0
        self.pulse_timer = 0
        self.firefight_timer = 0

        self.scroll_y = 0

        # Directional flow for sense of movement/turning
        self.flow_angle = 0  # Current flow direction offset
        self.target_flow_angle = 0  # Target angle to transition to
        self.flow_change_timer = 0
        self.flow_intensity = 0  # How strong the directional effect is

        # Far background Aeon supercarrier - atmospheric element
        self.aeon = self._create_far_aeon(width, height)
        self.aeon_x = width * 0.7  # Right side of screen
        self.aeon_y = 80  # Near top
        self.aeon_drift = 0  # Slow drift animation

        # === REBELLION STORY ELEMENTS ===
        # These create a living battlefield that tells the Minmatar uprising story

        # Slave transports (Bestowers) - Amarr ships carrying enslaved Minmatar
        self.slave_ships = []
        self.slave_ship_timer = 0
        self.slave_ship_sprite = self._create_slave_transport()

        # Escape pods - freed Minmatar fleeing to safety
        self.escape_pods = []
        self.escape_pod_timer = 0

        # Burning Amarr stations in the distance
        self.burning_stations = self._create_burning_stations(3)

        # Distant capital ship battles (rebellion in progress)
        self.distant_battles = []
        self.battle_timer = 0

        # Rebel fleet movements (friendly Minmatar ships)
        self.rebel_ships = []
        self.rebel_timer = 0

        # Story event messages
        self.story_event = None
        self.story_event_timer = 0

        # === PLANETARY BODIES ===
        # Creates the feeling of flying between planets/moons and carrier battles
        # Following the Minmatar Rebellion chronicles - fighting near homeworlds
        self.planet = self._create_planet(width, height)
        self.planet_x = width * 0.15  # Left side of screen
        self.planet_y = height * 0.3
        self.planet_drift = 0
        self.planet_visible = True

        # Moons - smaller bodies that pass by more frequently
        self.moons = []
        self.moon_timer = 0
        self._init_moons()

        # Current environment phase (changes per stage)
        # 'planet_orbit' - near Pator/Matar (Minmatar homeworld)
        # 'asteroid_belt' - mining operations, slave camps
        # 'carrier_approach' - closing on Amarr carrier groups
        self.environment_phase = 'planet_orbit'
        self.phase_transition_timer = 0

    def _create_planet(self, width, height):
        """Create a large distant planet - Matar (Minmatar homeworld) aesthetic

        Polished to match rendered ship quality with:
        - Multi-layer atmospheric effects
        - Realistic surface shading with specular highlights
        - Volumetric cloud formations
        - Animated-ready city light clusters
        - Proper limb darkening
        """
        # Large planet in far background - about 40% of screen height for impact
        size = int(height * 0.40)
        surf = pygame.Surface((size * 2 + 60, size * 2 + 60), pygame.SRCALPHA)
        cx, cy = size + 30, size + 30  # Extra margin for atmosphere

        # === ATMOSPHERIC OUTER GLOW (furthest layer) ===
        # Multiple rings of atmospheric scattering - like real planet limbs
        atmo_colors = [
            (200, 120, 70, 8),   # Outermost - faint orange scatter
            (180, 100, 60, 15),  # Mid scatter
            (160, 90, 55, 25),   # Inner scatter
            (140, 80, 50, 35),   # Atmospheric edge
        ]
        for i, (r, g, b, a) in enumerate(atmo_colors):
            atmo_r = size + 25 - i * 6
            pygame.draw.circle(surf, (r, g, b, a), (cx, cy), atmo_r)

        # === BASE PLANET SPHERE with proper limb darkening ===
        # Use multiple passes for smooth gradient
        for r in range(size, 0, -1):
            progress = r / size  # 1.0 at edge, 0.0 at center

            # Limb darkening - edges are darker (realistic)
            limb_factor = math.sqrt(1 - (1 - progress) ** 2) if progress < 1 else 0
            darken = 0.4 + 0.6 * (1 - limb_factor)

            # Base colors - Matar's harsh industrial rust
            base_r = int((55 + 40 * (1 - progress)) * darken)
            base_g = int((38 + 25 * (1 - progress)) * darken)
            base_b = int((30 + 18 * (1 - progress)) * darken)

            # Slight color variation based on position for realism
            base_r = min(255, base_r + int(8 * math.sin(progress * 4)))

            pygame.draw.circle(surf, (base_r, base_g, base_b), (cx, cy), r)

        # === CONTINENTAL MASSES with elevation shading ===
        # Main continent - mountains and plains
        continent_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cont_cx, cont_cy = size, size

        # Multiple elevation layers for depth
        for elev in range(4):
            elev_alpha = 80 + elev * 25
            elev_color = (30 + elev * 8, 22 + elev * 5, 18 + elev * 4, elev_alpha)
            scale = 1.0 - elev * 0.15

            # Large continent
            pygame.draw.ellipse(continent_surf, elev_color,
                (cont_cx - size * 0.45 * scale, cont_cy - size * 0.55 * scale,
                 size * 0.65 * scale, size * 0.45 * scale))

            # Secondary continent
            pygame.draw.ellipse(continent_surf, elev_color,
                (cont_cx + size * 0.05, cont_cy + size * 0.08,
                 size * 0.55 * scale, size * 0.38 * scale))

        # Mountain ranges (bright highlights on continents)
        mount_color = (65, 50, 40, 100)
        pygame.draw.arc(continent_surf, mount_color,
            (cont_cx - size * 0.35, cont_cy - size * 0.45, size * 0.5, size * 0.3),
            0.5, 2.5, 2)
        pygame.draw.arc(continent_surf, mount_color,
            (cont_cx + size * 0.1, cont_cy + size * 0.15, size * 0.4, size * 0.25),
            -0.5, 1.5, 2)

        # Island archipelago with varying sizes
        for i in range(7):
            angle = 0.8 + i * 0.25
            dist = size * (0.35 + i * 0.03)
            ix = cont_cx + int(math.cos(angle) * dist * 0.8)
            iy = cont_cy + int(math.sin(angle) * dist)
            island_size = int(size * 0.04 * (1.5 - i * 0.12))
            if island_size > 2:
                pygame.draw.circle(continent_surf, (35, 26, 22, 110), (ix, iy), island_size)

        surf.blit(continent_surf, (30, 30))

        # === VOLUMETRIC CLOUD BANDS ===
        cloud_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Multiple cloud layers with proper blending
        cloud_bands = [
            (-0.2, 0.85, 0.14),   # y_offset, width, height (as fraction of size)
            (0.1, 0.75, 0.10),
            (0.32, 0.65, 0.08),
            (-0.45, 0.55, 0.06),
        ]

        for y_off, w, h in cloud_bands:
            # Outer wispy clouds
            cloud_outer = (95, 70, 55, 35)
            pygame.draw.ellipse(cloud_surf, cloud_outer,
                (cont_cx - size * w * 0.55, cont_cy + size * y_off - size * h * 0.6,
                 size * w * 1.1, size * h * 1.2))

            # Inner dense clouds
            cloud_inner = (110, 80, 60, 50)
            pygame.draw.ellipse(cloud_surf, cloud_inner,
                (cont_cx - size * w * 0.45, cont_cy + size * y_off - size * h * 0.4,
                 size * w * 0.9, size * h * 0.8))

            # Highlights on cloud tops
            cloud_bright = (130, 100, 75, 40)
            pygame.draw.ellipse(cloud_surf, cloud_bright,
                (cont_cx - size * w * 0.35, cont_cy + size * y_off - size * h * 0.5,
                 size * w * 0.6, size * h * 0.4))

        # Storm vortex (great storm like Jupiter's)
        storm_x = cont_cx + int(size * 0.25)
        storm_y = cont_cy - int(size * 0.1)
        for r in range(int(size * 0.12), 0, -2):
            storm_alpha = int(60 * (r / (size * 0.12)))
            pygame.draw.circle(cloud_surf, (140, 95, 70, storm_alpha),
                             (storm_x, storm_y), r)
        pygame.draw.circle(cloud_surf, (90, 60, 45, 80), (storm_x, storm_y), int(size * 0.04))

        surf.blit(cloud_surf, (30, 30))

        # === CITY LIGHT CLUSTERS (dark side) ===
        light_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # Major city clusters with glow
        city_clusters = [
            (cont_cx - size * 0.3, cont_cy - size * 0.2, 8),   # Capital region
            (cont_cx - size * 0.4, cont_cy + size * 0.1, 5),   # Secondary city
            (cont_cx - size * 0.15, cont_cy - size * 0.35, 4), # Northern settlement
            (cont_cx - size * 0.25, cont_cy + size * 0.25, 3), # Southern outpost
        ]

        for cluster_x, cluster_y, num_lights in city_clusters:
            # Check if in planet radius and on dark side
            dist = math.sqrt((cluster_x - cont_cx) ** 2 + (cluster_y - cont_cy) ** 2)
            if dist < size * 0.85:
                # Cluster glow
                glow_size = num_lights * 4
                pygame.draw.circle(light_surf, (220, 170, 100, 25),
                                 (int(cluster_x), int(cluster_y)), glow_size)

                # Individual lights
                for _ in range(num_lights):
                    lx = int(cluster_x + random.randint(-glow_size, glow_size) // 2)
                    ly = int(cluster_y + random.randint(-glow_size, glow_size) // 2)
                    brightness = random.randint(150, 220)
                    pygame.draw.circle(light_surf, (brightness + 35, brightness, brightness - 50, 180),
                                     (lx, ly), random.randint(1, 2))

        surf.blit(light_surf, (30, 30))

        # === SPECULAR HIGHLIGHT (sun reflection) ===
        # Creates the "3D sphere" look
        highlight_x = cx + int(size * 0.25)
        highlight_y = cy - int(size * 0.3)
        for r in range(int(size * 0.3), 0, -2):
            h_alpha = int(30 * (1 - r / (size * 0.3)))
            pygame.draw.circle(surf, (255, 220, 180, h_alpha), (highlight_x, highlight_y), r)

        # Small bright core
        pygame.draw.circle(surf, (255, 240, 210, 45), (highlight_x, highlight_y), int(size * 0.08))

        # === TERMINATOR LINE (day/night boundary) ===
        # Smooth gradient for realistic transition
        term_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        term_x = size + int(size * 0.12)
        for x_off in range(-30, 40):
            alpha = max(0, 35 - abs(x_off))
            for y in range(0, size * 2, 2):
                dist_from_center = abs(y - size)
                if dist_from_center < size * 0.95:
                    pygame.draw.line(term_surf, (0, 0, 0, alpha),
                                   (term_x + x_off, y), (term_x + x_off, y))
        surf.blit(term_surf, (30, 30))

        surf.set_alpha(155)  # Slightly more visible
        return surf

    def _create_moon(self):
        """Create a smaller moon body"""
        size = random.randint(20, 50)
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx, cy = size, size

        # Gray/brown rocky moon
        base = random.randint(50, 80)
        for r in range(size, 0, -2):
            progress = r / size
            c = int(base + 20 * (1 - progress))
            alpha = int(150 * progress + 30)
            pygame.draw.circle(surf, (c, c - 5, c - 10, alpha), (cx, cy), r)

        # Craters
        for _ in range(random.randint(2, 5)):
            crater_x = cx + random.randint(-int(size * 0.5), int(size * 0.5))
            crater_y = cy + random.randint(-int(size * 0.5), int(size * 0.5))
            crater_r = random.randint(3, int(size * 0.2))
            # Check if within moon
            if math.sqrt((crater_x - cx) ** 2 + (crater_y - cy) ** 2) + crater_r < size * 0.9:
                pygame.draw.circle(surf, (base - 20, base - 25, base - 25, 100),
                                 (crater_x, crater_y), crater_r)
                pygame.draw.circle(surf, (base + 10, base + 5, base, 80),
                                 (crater_x - 1, crater_y - 1), crater_r - 1)

        surf.set_alpha(120)
        return {
            'surf': surf,
            'size': size,
            'x': random.choice([-size * 2, self.width + size * 2]),  # Start off-screen
            'y': random.randint(50, self.height // 2),
            'vx': random.uniform(0.3, 0.8) * (1 if random.random() > 0.5 else -1),
            'vy': random.uniform(0.1, 0.3),
            'rotation': 0,
        }

    def _init_moons(self):
        """Initialize starting moons"""
        # Start with 1-2 moons visible
        for _ in range(random.randint(1, 2)):
            moon = self._create_moon()
            moon['x'] = random.randint(100, self.width - 100)
            self.moons.append(moon)

    def set_environment_phase(self, phase):
        """Change environment phase for stage progression"""
        self.environment_phase = phase
        self.phase_transition_timer = 120  # 2 second transition

    def _create_far_aeon(self, width, height):
        """Create a distant Aeon supercarrier for far background atmosphere"""
        # Very small due to distance - about 10% of screen width
        size = int(width * 0.12)
        surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        cx, cy = size, size // 2

        # Faded colors due to distance/atmosphere
        hull_main = (50, 45, 38, 180)  # Semi-transparent dark hull
        hull_dark = (35, 32, 28, 180)
        hull_light = (65, 58, 48, 180)
        engine_glow = (180, 120, 60, 100)  # Dim engine glow

        # Simplified hull shape - Aeon has distinctive angular design
        hull_points = [
            (cx - size * 0.85, cy),
            (cx - size * 0.6, cy - size * 0.35),
            (cx - size * 0.2, cy - size * 0.4),
            (cx + size * 0.3, cy - size * 0.35),
            (cx + size * 0.7, cy - size * 0.2),
            (cx + size * 0.85, cy),
            (cx + size * 0.7, cy + size * 0.2),
            (cx + size * 0.3, cy + size * 0.35),
            (cx - size * 0.2, cy + size * 0.4),
            (cx - size * 0.6, cy + size * 0.35),
        ]
        pygame.draw.polygon(surf, hull_main[:3], hull_points)
        pygame.draw.polygon(surf, hull_dark[:3], hull_points, 1)

        # Central command structure
        pygame.draw.ellipse(surf, hull_light[:3],
                           (cx - size * 0.15, cy - size * 0.18, size * 0.3, size * 0.2))

        # Wing pylons (Aeon has massive wings)
        for side in [-1, 1]:
            pylon_y = cy + side * size * 0.25
            pygame.draw.polygon(surf, hull_dark[:3], [
                (cx - size * 0.3, pylon_y),
                (cx - size * 0.5, pylon_y + side * size * 0.15),
                (cx - size * 0.65, pylon_y + side * size * 0.1),
                (cx - size * 0.5, pylon_y),
            ])

        # Distant engine glows (very dim)
        for offset in [-0.2, 0, 0.2]:
            ex = cx - size * 0.82
            ey = cy + size * offset
            pygame.draw.circle(surf, engine_glow[:3], (int(ex), int(ey)), 4)
            pygame.draw.circle(surf, (200, 150, 80), (int(ex), int(ey)), 2)

        # Apply overall transparency for distance effect
        surf.set_alpha(120)

        return surf

    def _create_slave_transport(self):
        """Create Amarr Bestower slave transport ship"""
        size = 40
        surf = pygame.Surface((size * 2, size), pygame.SRCALPHA)
        cx, cy = size, size // 2

        # Amarr gold/brown colors
        hull = (100, 80, 50)
        hull_dark = (60, 48, 30)
        cargo = (80, 65, 40)

        # Bestower hull - elongated cargo hauler
        hull_points = [
            (cx - size * 0.8, cy),
            (cx - size * 0.6, cy - size * 0.25),
            (cx + size * 0.4, cy - size * 0.2),
            (cx + size * 0.7, cy),
            (cx + size * 0.4, cy + size * 0.2),
            (cx - size * 0.6, cy + size * 0.25),
        ]
        pygame.draw.polygon(surf, hull, hull_points)
        pygame.draw.polygon(surf, hull_dark, hull_points, 1)

        # Cargo pods (where the slaves are held)
        for i in range(3):
            px = cx - size * 0.3 + i * size * 0.25
            pygame.draw.ellipse(surf, cargo, (px - 8, cy - 6, 16, 12))
            pygame.draw.ellipse(surf, hull_dark, (px - 8, cy - 6, 16, 12), 1)

        # Engine glow
        pygame.draw.circle(surf, (200, 150, 80), (int(cx - size * 0.75), cy), 4)

        return surf

    def _create_burning_stations(self, count):
        """Create distant burning Amarr stations"""
        stations = []
        for i in range(count):
            station = {
                'x': random.randint(100, self.width - 100),
                'y': random.randint(50, 200),
                'size': random.randint(30, 60),
                'fire_offset': random.random() * math.pi * 2,
                'smoke_timer': 0,
            }
            stations.append(station)
        return stations

    def _create_escape_pod(self):
        """Create a fleeing escape pod"""
        return {
            'x': random.randint(100, self.width - 100),
            'y': -20,
            'vx': random.uniform(-0.5, 0.5),
            'vy': random.uniform(2, 4),
            'size': random.randint(4, 8),
            'blink': 0,
        }

    def _create_rebel_ship(self):
        """Create a friendly Minmatar rebel ship passing through"""
        side = random.choice([-1, 1])
        return {
            'x': -50 if side > 0 else self.width + 50,
            'y': random.randint(100, self.height - 200),
            'vx': random.uniform(3, 6) * side,
            'vy': random.uniform(-0.5, 0.5),
            'size': random.randint(15, 25),
            'type': random.choice(['rifter', 'slasher', 'breacher']),
        }

    def _create_distant_battle(self):
        """Create a distant capital ship battle effect"""
        return {
            'x': random.randint(50, self.width - 50),
            'y': random.randint(30, 150),
            'duration': random.randint(120, 300),
            'timer': 0,
            'intensity': random.uniform(0.5, 1.0),
            'flash_timer': 0,
        }

    def create_nebula(self, width, height):
        """Create EVE Frontier-style dark, oppressive space backdrop

        Aesthetic: Dark forest survival horror in space
        - Near-black void with subtle threatening undertones
        - Distant gravitational distortions
        - Ancient, hostile atmosphere
        - Suffocating darkness with hints of danger
        """
        surface = pygame.Surface((width, height * 2))

        # Almost pure black - the void is hostile and empty
        for y in range(height * 2):
            progress = y / (height * 2)
            # Deep blacks with subtle blood-red and sickly green undertones
            # Like something wrong lurks in the darkness
            r = int(5 + math.sin(progress * math.pi * 0.3) * 3)
            g = int(4 + math.sin(progress * math.pi * 0.5) * 2)
            b = int(6 + math.sin(progress * math.pi * 0.2) * 4)
            pygame.draw.line(surface, (r, g, b), (0, y), (width, y))

        # Ominous dust clouds - like something lurks within
        for _ in range(6):
            x = random.randint(0, width)
            y = random.randint(0, height * 2)
            size = random.randint(200, 500)

            # Threatening colors - deep reds, sickly greens, void blacks
            cloud_color = random.choice([
                (20, 8, 8, 15),     # Blood-tinted void
                (8, 15, 10, 12),    # Sickly green haze
                (12, 10, 18, 10),   # Deep purple corruption
                (5, 5, 5, 20),      # Pure darkness patch
            ])

            cloud_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            for r in range(size // 2, 0, -size // 8):
                alpha = cloud_color[3] * (r / (size // 2))
                pygame.draw.circle(cloud_surf, (*cloud_color[:3], int(alpha)),
                                 (size // 2, size // 2), r)
            surface.blit(cloud_surf, (x - size // 2, y - size // 2))

        # Gravitational distortion zones - black hole influence
        for _ in range(3):
            gx = random.randint(100, width - 100)
            gy = random.randint(100, height * 2 - 100)
            gsize = random.randint(80, 200)

            # Dark vortex center
            grav_surf = pygame.Surface((gsize * 2, gsize * 2), pygame.SRCALPHA)
            for r in range(gsize, 0, -5):
                # Gets darker toward center
                darkness = int(8 * (1 - r / gsize))
                alpha = int(30 * (1 - r / gsize))
                pygame.draw.circle(grav_surf, (darkness, darkness, darkness + 2, alpha),
                                 (gsize, gsize), r)
            # Accretion disk hint (faint ring)
            pygame.draw.circle(grav_surf, (40, 20, 15, 20), (gsize, gsize), gsize - 10, 2)
            surface.blit(grav_surf, (gx - gsize, gy - gsize))

        # Ancient megastructure silhouettes in the far distance
        for _ in range(2):
            mx = random.randint(50, width - 50)
            my = random.randint(50, height)
            msize = random.randint(100, 250)

            # Ruined gate/structure shapes - barely visible
            struct_color = (15, 12, 10)
            # Vertical pylons
            pygame.draw.rect(surface, struct_color,
                           (mx - msize // 2, my - msize, 8, msize * 2))
            pygame.draw.rect(surface, struct_color,
                           (mx + msize // 2 - 8, my - msize, 8, msize * 2))
            # Horizontal beam (broken)
            pygame.draw.rect(surface, struct_color,
                           (mx - msize // 2, my - msize // 3, msize // 2 - 20, 6))
            pygame.draw.rect(surface, struct_color,
                           (mx + 20, my - msize // 3, msize // 2 - 20, 6))

        return surface

    def create_star_field(self, count):
        """Create EVE Frontier star field - sparse, dim, hostile void

        Most of space is empty darkness. Stars are distant, cold, uncaring.
        A few red giants hint at dying systems. The frontier is desolate.
        """
        stars = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height * 2)

            # 90% of stars are barely visible - the void dominates
            if random.random() < 0.90:
                brightness = random.randint(30, 80)  # Much dimmer
                size = 1
            elif random.random() < 0.7:
                brightness = random.randint(80, 140)
                size = 1
            else:
                # Rare bright stars - often dying red giants
                brightness = random.randint(140, 200)
                size = random.choice([1, 2])

            # Color: cold blues, dying reds, sickly yellows
            star_type = random.random()
            if star_type < 0.5:
                # Cold blue-white (distant, uncaring)
                r = brightness - 20
                g = brightness
                b = min(255, brightness + 20)
            elif star_type < 0.8:
                # Dying red (ancient, fading)
                r = min(255, brightness + 40)
                g = brightness - 30
                b = brightness - 40
            else:
                # Sickly yellow (corrupted?)
                r = min(255, brightness + 20)
                g = brightness
                b = brightness - 30

            r = max(0, min(255, r))
            g = max(0, min(255, g))
            b = max(0, min(255, b))

            stars.append({
                'x': x, 'y': y, 'size': size,
                'color': (r, g, b),
                'speed': 0.15,
                'twinkle': random.uniform(0, math.pi * 2)
            })
        return stars

    def create_asteroid_field(self, count):
        """Create sparse asteroid field"""
        asteroids = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height * 2)
            size = random.randint(8, 25)
            speed = random.uniform(0.5, 1.5)
            rotation = random.uniform(0, math.pi * 2)

            # Dark gray-brown colors
            base = random.randint(40, 70)
            asteroids.append({
                'x': x, 'y': y, 'size': size,
                'speed': speed, 'rotation': rotation,
                'rot_speed': random.uniform(-0.01, 0.01),
                'color': (base + 10, base + 5, base),
                'points': self._generate_asteroid_shape(size)
            })
        return asteroids

    def _generate_asteroid_shape(self, size):
        """Generate irregular asteroid polygon"""
        points = []
        num_points = random.randint(6, 9)
        for i in range(num_points):
            angle = (i / num_points) * math.pi * 2
            dist = size * random.uniform(0.6, 1.0)
            points.append((math.cos(angle) * dist, math.sin(angle) * dist))
        return points

    def create_debris_field(self, count):
        """Create floating debris - ship parts, containers, etc."""
        debris = []
        for _ in range(count):
            debris.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height * 2),
                'size': random.randint(4, 12),
                'speed': random.uniform(0.8, 2.0),
                'rotation': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.03, 0.03),
                'type': random.choice(['plate', 'beam', 'container', 'panel']),
                'color': random.choice([
                    (70, 60, 50),  # Rusty metal
                    (50, 55, 60),  # Gray metal
                    (80, 65, 40),  # Bronze
                ])
            })
        return debris

    def create_distant_structures(self, count):
        """Create distant stations/structures visible in background"""
        structures = []
        for _ in range(count):
            structures.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height * 2),
                'size': random.randint(30, 80),
                'speed': random.uniform(0.1, 0.3),  # Very slow - far away
                'alpha': random.randint(30, 60),  # Faint
                'type': random.choice(['station', 'gate', 'platform']),
            })
        return structures

    def create_ship_wrecks(self, count):
        """Create distant destroyed ship wrecks"""
        wrecks = []
        for _ in range(count):
            wrecks.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height * 2),
                'size': random.randint(40, 100),
                'speed': random.uniform(0.2, 0.5),
                'rotation': random.uniform(0, math.pi * 2),
                'rot_speed': random.uniform(-0.005, 0.005),
                'alpha': random.randint(40, 80),
                'fire_timer': random.uniform(0, math.pi * 2),
            })
        return wrecks

    def update(self, speed=1.0):
        """Update background - constant forward motion with directional changes"""
        # Update directional flow (creates illusion of turning/maneuvering)
        self.flow_change_timer -= 1
        if self.flow_change_timer <= 0:
            # Randomly change direction
            self.target_flow_angle = random.uniform(-0.4, 0.4)  # Radians
            self.flow_intensity = random.uniform(0.5, 1.5)
            self.flow_change_timer = random.randint(120, 300)  # 2-5 seconds

        # Smooth transition to target angle
        self.flow_angle += (self.target_flow_angle - self.flow_angle) * 0.02

        # Calculate flow vectors
        flow_x = math.sin(self.flow_angle) * self.flow_intensity
        flow_y = math.cos(self.flow_angle)  # Always moving forward

        # Faster scroll for forward motion sensation
        self.scroll_y += speed * 1.5 * flow_y

        if self.scroll_y >= self.height:
            self.scroll_y = 0

        # === PLANETARY BODIES UPDATE ===
        # Planet slowly drifts for parallax effect (very far, minimal movement)
        self.planet_drift += 0.005
        # Very subtle movement - planet is massive and distant

        # Moons update - closer so they move more
        self.moon_timer -= 1
        if self.moon_timer <= 0 and len(self.moons) < 4 and random.random() < 0.02:
            self.moons.append(self._create_moon())
            self.moon_timer = random.randint(300, 600)

        new_moons = []
        for moon in self.moons:
            # Moons drift across the sky
            moon['x'] += moon['vx'] * speed * 0.5
            moon['y'] += moon['vy'] * speed * 0.3

            # Keep if still visible
            if -moon['size'] * 3 < moon['x'] < self.width + moon['size'] * 3:
                new_moons.append(moon)
        self.moons = new_moons

        # Phase transition timer
        if self.phase_transition_timer > 0:
            self.phase_transition_timer -= 1

        # Stars move at different speeds for depth (parallax layers)
        for star in self.star_field:
            parallax = 0.3 + (star['size'] * 0.4)
            move_speed = star['speed'] * speed * parallax * 3
            star['x'] += flow_x * move_speed * 0.5  # Horizontal drift
            star['y'] += flow_y * move_speed
            star['twinkle'] += 0.05
            # Wrap around
            if star['y'] > self.height * 2:
                star['y'] = -10
                star['x'] = random.randint(0, self.width)
            if star['x'] < -20:
                star['x'] = self.width + 10
            elif star['x'] > self.width + 20:
                star['x'] = -10

        # Asteroids stream past with directional flow
        for asteroid in self.asteroids:
            move_speed = asteroid['speed'] * speed * 2.5
            asteroid['x'] += flow_x * move_speed * 0.8
            asteroid['y'] += flow_y * move_speed
            asteroid['rotation'] += asteroid['rot_speed']
            if asteroid['y'] > self.height + asteroid['size']:
                asteroid['y'] = -asteroid['size'] * 2
                asteroid['x'] = random.randint(0, self.width)
            if asteroid['x'] < -50:
                asteroid['x'] = self.width + 30
            elif asteroid['x'] > self.width + 50:
                asteroid['x'] = -30

        # Debris moves fastest with strong directional effect
        for debris in self.debris:
            move_speed = debris['speed'] * speed * 3.5
            debris['x'] += flow_x * move_speed * 1.2  # Most affected
            debris['y'] += flow_y * move_speed
            debris['rotation'] += debris['rot_speed'] * 2
            if debris['y'] > self.height + debris['size']:
                debris['y'] = -debris['size'] * 2
                debris['x'] = random.randint(0, self.width)
            if debris['x'] < -30:
                debris['x'] = self.width + 20
            elif debris['x'] > self.width + 30:
                debris['x'] = -20

        # Distant structures - minimal directional effect (far away)
        for struct in self.distant_structures:
            move_speed = struct['speed'] * speed * 1.2
            struct['x'] += flow_x * move_speed * 0.2
            struct['y'] += flow_y * move_speed
            if struct['y'] > self.height + struct['size']:
                struct['y'] = -struct['size'] * 2
                struct['x'] = random.randint(0, self.width)

        # Wrecks drift with medium directional effect
        for wreck in self.wrecks:
            move_speed = wreck['speed'] * speed * 1.8
            wreck['x'] += flow_x * move_speed * 0.5
            wreck['y'] += flow_y * move_speed
            wreck['rotation'] += wreck['rot_speed']
            wreck['fire_timer'] += 0.1
            if wreck['y'] > self.height + wreck['size']:
                wreck['y'] = -wreck['size'] * 2
                wreck['x'] = random.randint(0, self.width)

        # === INTENSE BATTLE EFFECTS ===

        # Frequent battle flashes
        self.flash_timer -= 1
        if self.flash_timer <= 0 and random.random() < 0.08:  # More frequent
            self.flashes.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(15, 50),  # Bigger explosions
                'life': 20,
                'max_life': 20,
                'color': random.choice([(255, 200, 100), (255, 150, 50), (255, 100, 50)])
            })
            self.flash_timer = 15  # Faster respawn

        # Update flashes
        self.flashes = [f for f in self.flashes if f['life'] > 0]
        for flash in self.flashes:
            flash['life'] -= 1

        # Laser beam sweeps (distant capital ship fire)
        self.beam_spawn_timer -= 1
        if self.beam_spawn_timer <= 0 and random.random() < 0.03:
            side = random.choice(['left', 'right', 'top'])
            if side == 'left':
                self.laser_beams.append({
                    'x1': 0, 'y1': random.randint(0, self.height // 2),
                    'x2': self.width, 'y2': random.randint(self.height // 3, self.height),
                    'life': 25, 'max_life': 25,
                    'color': (255, 200, 50), 'width': random.randint(2, 4)
                })
            elif side == 'right':
                self.laser_beams.append({
                    'x1': self.width, 'y1': random.randint(0, self.height // 2),
                    'x2': 0, 'y2': random.randint(self.height // 3, self.height),
                    'life': 25, 'max_life': 25,
                    'color': (255, 180, 50), 'width': random.randint(2, 4)
                })
            else:  # top
                self.laser_beams.append({
                    'x1': random.randint(0, self.width), 'y1': 0,
                    'x2': random.randint(0, self.width), 'y2': self.height,
                    'life': 30, 'max_life': 30,
                    'color': (255, 220, 100), 'width': random.randint(3, 5)
                })
            self.beam_spawn_timer = random.randint(60, 120)

        # Update beams
        self.laser_beams = [b for b in self.laser_beams if b['life'] > 0]
        for beam in self.laser_beams:
            beam['life'] -= 1

        # Tracer fire streaks (distant dogfights)
        self.firefight_timer -= 1
        if self.firefight_timer <= 0 and random.random() < 0.1:
            # Spawn a burst of tracers
            base_x = random.randint(100, self.width - 100)
            base_y = random.randint(50, self.height - 200)
            for _ in range(random.randint(3, 8)):
                angle = random.uniform(-0.5, 0.5)
                speed = random.uniform(8, 15)
                self.tracer_fire.append({
                    'x': base_x + random.randint(-30, 30),
                    'y': base_y + random.randint(-20, 20),
                    'vx': math.sin(angle) * speed,
                    'vy': math.cos(angle) * speed,
                    'life': random.randint(15, 30),
                    'color': random.choice([(255, 200, 50), (255, 100, 50), (200, 255, 100)])
                })
            self.firefight_timer = random.randint(20, 50)

        # Update tracers
        self.tracer_fire = [t for t in self.tracer_fire if t['life'] > 0]
        for tracer in self.tracer_fire:
            tracer['x'] += tracer['vx']
            tracer['y'] += tracer['vy']
            tracer['life'] -= 1

        # Energy pulses (shockwaves from distant explosions)
        self.pulse_timer -= 1
        if self.pulse_timer <= 0 and random.random() < 0.02:
            self.energy_pulses.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height // 2),
                'radius': 0,
                'max_radius': random.randint(100, 250),
                'speed': random.uniform(3, 6),
                'alpha': 80
            })
            self.pulse_timer = random.randint(90, 180)

        # Update pulses
        new_pulses = []
        for pulse in self.energy_pulses:
            pulse['radius'] += pulse['speed']
            pulse['alpha'] = int(80 * (1 - pulse['radius'] / pulse['max_radius']))
            if pulse['radius'] < pulse['max_radius']:
                new_pulses.append(pulse)
        self.energy_pulses = new_pulses

        # === REBELLION STORY ELEMENTS UPDATE ===

        # Spawn slave transports occasionally (Amarr hauling slaves)
        self.slave_ship_timer -= 1
        if self.slave_ship_timer <= 0 and random.random() < 0.01 and len(self.slave_ships) < 2:
            self.slave_ships.append({
                'x': random.randint(100, self.width - 100),
                'y': -50,
                'vy': random.uniform(0.8, 1.5),
                'vx': random.uniform(-0.3, 0.3),
            })
            self.slave_ship_timer = random.randint(300, 600)

        # Update slave ships
        new_slaves = []
        for ship in self.slave_ships:
            ship['x'] += ship['vx']
            ship['y'] += ship['vy']
            if ship['y'] < self.height + 50:
                new_slaves.append(ship)
        self.slave_ships = new_slaves

        # Spawn escape pods (freed Minmatar)
        self.escape_pod_timer -= 1
        if self.escape_pod_timer <= 0 and random.random() < 0.03 and len(self.escape_pods) < 8:
            self.escape_pods.append(self._create_escape_pod())
            self.escape_pod_timer = random.randint(60, 180)

        # Update escape pods
        new_pods = []
        for pod in self.escape_pods:
            pod['x'] += pod['vx']
            pod['y'] += pod['vy']
            pod['blink'] += 0.15
            if pod['y'] < self.height + 20:
                new_pods.append(pod)
        self.escape_pods = new_pods

        # Spawn rebel ships passing through
        self.rebel_timer -= 1
        if self.rebel_timer <= 0 and random.random() < 0.02 and len(self.rebel_ships) < 3:
            self.rebel_ships.append(self._create_rebel_ship())
            self.rebel_timer = random.randint(180, 400)

        # Update rebel ships
        new_rebels = []
        for ship in self.rebel_ships:
            ship['x'] += ship['vx']
            ship['y'] += ship['vy']
            if -100 < ship['x'] < self.width + 100:
                new_rebels.append(ship)
        self.rebel_ships = new_rebels

        # Update burning stations (fire flickers)
        for station in self.burning_stations:
            station['smoke_timer'] += 1

        # Spawn distant battles
        self.battle_timer -= 1
        if self.battle_timer <= 0 and random.random() < 0.01 and len(self.distant_battles) < 2:
            self.distant_battles.append(self._create_distant_battle())
            self.battle_timer = random.randint(300, 600)

        # Update distant battles
        new_battles = []
        for battle in self.distant_battles:
            battle['timer'] += 1
            battle['flash_timer'] += 1
            if battle['timer'] < battle['duration']:
                new_battles.append(battle)
        self.distant_battles = new_battles

        # Story event timer
        if self.story_event_timer > 0:
            self.story_event_timer -= 1
            if self.story_event_timer <= 0:
                self.story_event = None

    def draw(self, surface):
        """Draw background layers with intense battle atmosphere"""
        # Nebula
        y_offset = -self.height + int(self.scroll_y)
        surface.blit(self.nebula_layer, (0, y_offset))

        # === PLANETARY BODIES (furthest layer) ===
        # Draw the planet (Matar - Minmatar homeworld)
        if self.planet_visible:
            # Subtle drift animation for depth
            planet_draw_x = self.planet_x + math.sin(self.planet_drift) * 8
            planet_draw_y = self.planet_y + math.cos(self.planet_drift * 0.6) * 5
            # Get planet size from surface
            planet_size = self.planet.get_height() // 2
            surface.blit(self.planet,
                        (int(planet_draw_x) - planet_size,
                         int(planet_draw_y) - planet_size))

        # Draw moons (closer than planet, further than carriers)
        for moon in self.moons:
            surface.blit(moon['surf'],
                        (int(moon['x']) - moon['size'],
                         int(moon['y']) - moon['size']))

        # Far background Aeon supercarrier (very distant, atmospheric)
        self.aeon_drift += 0.002  # Very slow drift
        aeon_draw_x = self.aeon_x + math.sin(self.aeon_drift) * 15
        aeon_draw_y = self.aeon_y + math.cos(self.aeon_drift * 0.7) * 8
        surface.blit(self.aeon, (int(aeon_draw_x), int(aeon_draw_y)))

        # === REBELLION STORY ELEMENTS DRAWING ===

        # Burning Amarr stations (distant, atmospheric)
        for station in self.burning_stations:
            sx, sy = station['x'], station['y']
            size = station['size']

            # Station silhouette (dark, damaged)
            pygame.draw.rect(surface, (30, 25, 20),
                           (sx - size // 2, sy - size // 3, size, size // 2))
            pygame.draw.polygon(surface, (25, 22, 18), [
                (sx, sy - size // 2), (sx - size // 3, sy - size // 4),
                (sx + size // 3, sy - size // 4)
            ])

            # Fire glow effect
            fire_flicker = math.sin(station['smoke_timer'] * 0.1 + station['fire_offset']) * 0.3 + 0.7
            fire_size = int(size * 0.4 * fire_flicker)
            fire_alpha = int(80 * fire_flicker)
            fire_surf = pygame.Surface((fire_size * 2, fire_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(fire_surf, (255, 100, 30, fire_alpha),
                             (fire_size, fire_size), fire_size)
            pygame.draw.circle(fire_surf, (255, 180, 50, fire_alpha + 30),
                             (fire_size, fire_size), fire_size // 2)
            surface.blit(fire_surf, (sx - fire_size, sy - fire_size))

        # Distant capital ship battles
        for battle in self.distant_battles:
            bx, by = battle['x'], battle['y']
            intensity = battle['intensity']

            # Periodic flashes
            if battle['flash_timer'] % 8 < 4:
                flash_size = int(20 * intensity)
                flash_alpha = int(100 * intensity)
                flash_surf = pygame.Surface((flash_size * 2, flash_size * 2), pygame.SRCALPHA)
                color = random.choice([(255, 200, 100), (255, 150, 50), (100, 200, 255)])
                pygame.draw.circle(flash_surf, (*color, flash_alpha),
                                 (flash_size, flash_size), flash_size)
                surface.blit(flash_surf, (bx - flash_size, by - flash_size))

            # Beam exchanges
            if battle['flash_timer'] % 15 == 0:
                beam_len = random.randint(40, 80)
                beam_angle = random.uniform(0, math.pi * 2)
                bx2 = bx + math.cos(beam_angle) * beam_len
                by2 = by + math.sin(beam_angle) * beam_len
                pygame.draw.line(surface, (255, 200, 100),
                               (bx, by), (int(bx2), int(by2)), 1)

        # Slave transport ships (Amarr Bestowers)
        for ship in self.slave_ships:
            # Draw the slave ship sprite
            surface.blit(self.slave_ship_sprite,
                        (int(ship['x']) - 40, int(ship['y']) - 20))

        # Escape pods (freed Minmatar)
        for pod in self.escape_pods:
            # Blinking distress beacon
            blink_on = math.sin(pod['blink']) > 0
            pod_color = (200, 50, 50) if blink_on else (100, 30, 30)

            # Small pod shape
            pygame.draw.ellipse(surface, (80, 80, 90),
                              (int(pod['x']) - pod['size'],
                               int(pod['y']) - pod['size'] // 2,
                               pod['size'] * 2, pod['size']))
            # Beacon
            if blink_on:
                pygame.draw.circle(surface, pod_color,
                                 (int(pod['x']), int(pod['y']) - pod['size'] // 2), 2)

        # Rebel Minmatar ships passing through
        for ship in self.rebel_ships:
            rx, ry = int(ship['x']), int(ship['y'])
            size = ship['size']

            # Minmatar ship colors (rusty, industrial)
            hull = (120, 85, 60)
            hull_dark = (80, 55, 35)
            engine = (200, 150, 80)

            # Simple Rifter-like shape
            if ship['type'] == 'rifter':
                # Angular aggressive shape
                pygame.draw.polygon(surface, hull, [
                    (rx, ry - size), (rx + size * 0.6, ry + size * 0.3),
                    (rx + size * 0.3, ry + size * 0.8),
                    (rx - size * 0.3, ry + size * 0.8),
                    (rx - size * 0.6, ry + size * 0.3)
                ])
                # Wing struts
                pygame.draw.line(surface, hull_dark,
                               (rx, ry), (rx + size * 0.8, ry + size * 0.5), 2)
                pygame.draw.line(surface, hull_dark,
                               (rx, ry), (rx - size * 0.8, ry + size * 0.5), 2)
            else:
                # Generic small ship
                pygame.draw.polygon(surface, hull, [
                    (rx, ry - size * 0.8), (rx + size * 0.4, ry + size * 0.6),
                    (rx - size * 0.4, ry + size * 0.6)
                ])

            # Engine glow
            pygame.draw.circle(surface, engine,
                             (rx, int(ry + size * 0.7)), 3)

        # Energy pulses (shockwaves - behind everything)
        for pulse in self.energy_pulses:
            if pulse['alpha'] > 5:
                pulse_surf = pygame.Surface((pulse['max_radius'] * 2, pulse['max_radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(pulse_surf, (255, 200, 100, pulse['alpha']),
                                 (pulse['max_radius'], pulse['max_radius']), int(pulse['radius']), 2)
                surface.blit(pulse_surf,
                           (pulse['x'] - pulse['max_radius'], pulse['y'] - pulse['max_radius']))

        # Laser beams (distant capital ship fire)
        for beam in self.laser_beams:
            alpha = int(200 * (beam['life'] / beam['max_life']))
            # Glow effect
            for w in range(beam['width'] + 4, 0, -2):
                glow_alpha = alpha // (w // 2 + 1)
                color = (*beam['color'][:3], glow_alpha)
                # Draw on temp surface for alpha
                beam_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(beam_surf, color, (beam['x1'], beam['y1']), (beam['x2'], beam['y2']), w)
                surface.blit(beam_surf, (0, 0))

        # Tracer fire
        for tracer in self.tracer_fire:
            alpha = int(255 * (tracer['life'] / 30))
            # Trail
            trail_len = 8
            for i in range(trail_len):
                t_alpha = int(alpha * (1 - i / trail_len))
                tx = tracer['x'] - tracer['vx'] * i * 0.3
                ty = tracer['y'] - tracer['vy'] * i * 0.3
                pygame.draw.circle(surface, (*tracer['color'][:3], t_alpha), (int(tx), int(ty)), 2)
            # Head
            pygame.draw.circle(surface, tracer['color'], (int(tracer['x']), int(tracer['y'])), 3)

        # Distant flashes (explosions)
        for flash in self.flashes:
            alpha = int(180 * (flash['life'] / flash['max_life']))
            size = int(flash['size'] * (1 + (1 - flash['life'] / flash['max_life']) * 0.8))
            flash_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            # Outer glow
            pygame.draw.circle(flash_surf, (*flash.get('color', (255, 200, 100))[:3], alpha // 2), (size, size), size)
            # Inner bright
            pygame.draw.circle(flash_surf, (255, 255, 200, min(255, alpha)), (size, size), size // 2)
            # Core
            pygame.draw.circle(flash_surf, (255, 255, 255, min(255, alpha + 50)), (size, size), size // 4)
            surface.blit(flash_surf, (flash['x'] - size, flash['y'] - size))

        # Distant structures (very far back)
        for struct in self.distant_structures:
            y = int(struct['y'] - self.scroll_y * 0.3)  # Slower parallax
            if -struct['size'] <= y <= self.height + struct['size']:
                self._draw_structure(surface, struct, y)

        # Ship wrecks
        for wreck in self.wrecks:
            y = int(wreck['y'] - self.scroll_y * 0.5)
            if -wreck['size'] <= y <= self.height + wreck['size']:
                self._draw_wreck(surface, wreck, y)

        # Stars with subtle twinkle
        for star in self.star_field:
            y = int(star['y'] - self.scroll_y)
            if 0 <= y <= self.height:
                twinkle = 0.85 + 0.15 * math.sin(star['twinkle'])
                color = tuple(int(c * twinkle) for c in star['color'])
                pygame.draw.circle(surface, color, (int(star['x']), y), star['size'])

        # Asteroids
        for asteroid in self.asteroids:
            y = int(asteroid['y'] - self.scroll_y)
            if -asteroid['size'] <= y <= self.height + asteroid['size']:
                self._draw_asteroid(surface, asteroid, y)

        # Debris (closest)
        for debris in self.debris:
            y = int(debris['y'] - self.scroll_y)
            if -debris['size'] <= y <= self.height + debris['size']:
                self._draw_debris(surface, debris, y)

    def _draw_structure(self, surface, struct, y):
        """Draw a distant space structure"""
        x = int(struct['x'])
        size = struct['size']
        alpha = struct['alpha']

        struct_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx, cy = size, size

        if struct['type'] == 'station':
            # Space station silhouette
            pygame.draw.rect(struct_surf, (40, 38, 35, alpha),
                           (cx - size * 0.4, cy - size * 0.6, size * 0.8, size * 1.2))
            pygame.draw.rect(struct_surf, (50, 48, 42, alpha),
                           (cx - size * 0.6, cy - size * 0.15, size * 1.2, size * 0.3))
            # Lights
            for i in range(3):
                pygame.draw.circle(struct_surf, (100, 80, 60, alpha + 30),
                                 (cx - size * 0.2 + i * size * 0.2, cy), 2)
        elif struct['type'] == 'gate':
            # Stargate ring
            pygame.draw.circle(struct_surf, (45, 42, 38, alpha), (cx, cy), int(size * 0.7), 4)
            pygame.draw.circle(struct_surf, (55, 50, 45, alpha), (cx, cy), int(size * 0.5), 2)
        else:  # platform
            pygame.draw.polygon(struct_surf, (42, 40, 36, alpha), [
                (cx, cy - size * 0.5), (cx + size * 0.6, cy),
                (cx, cy + size * 0.5), (cx - size * 0.6, cy)
            ])

        surface.blit(struct_surf, (x - size, y - size))

    def _draw_wreck(self, surface, wreck, y):
        """Draw a destroyed ship wreck"""
        x = int(wreck['x'])
        size = wreck['size']
        alpha = wreck['alpha']
        rot = wreck['rotation']

        wreck_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        cx, cy = size, size

        # Broken hull pieces
        cos_r, sin_r = math.cos(rot), math.sin(rot)

        # Main hull fragment
        hull_points = [
            (0, -size * 0.4), (size * 0.3, -size * 0.2),
            (size * 0.25, size * 0.3), (-size * 0.2, size * 0.35),
            (-size * 0.35, 0)
        ]
        rotated = [(cx + px * cos_r - py * sin_r, cy + px * sin_r + py * cos_r)
                   for px, py in hull_points]
        pygame.draw.polygon(wreck_surf, (50, 45, 38, alpha), rotated)
        pygame.draw.polygon(wreck_surf, (35, 32, 28, alpha), rotated, 1)

        # Secondary fragment
        frag_points = [
            (size * 0.4, -size * 0.1), (size * 0.5, size * 0.15),
            (size * 0.3, size * 0.25)
        ]
        rotated2 = [(cx + px * cos_r - py * sin_r, cy + px * sin_r + py * cos_r)
                    for px, py in frag_points]
        pygame.draw.polygon(wreck_surf, (45, 42, 35, alpha), rotated2)

        # Flickering fire/sparks
        if math.sin(wreck['fire_timer']) > 0.3:
            fire_alpha = int(40 + 30 * math.sin(wreck['fire_timer'] * 2))
            pygame.draw.circle(wreck_surf, (255, 120, 50, fire_alpha),
                             (cx + int(size * 0.1), cy), 4)

        surface.blit(wreck_surf, (x - size, y - size))

    def _draw_debris(self, surface, debris, y):
        """Draw floating debris"""
        x = int(debris['x'])
        size = debris['size']
        rot = debris['rotation']
        color = debris['color']

        cos_r, sin_r = math.cos(rot), math.sin(rot)

        if debris['type'] == 'plate':
            points = [(-size, -size * 0.3), (size, -size * 0.4),
                     (size * 0.8, size * 0.3), (-size * 0.7, size * 0.4)]
        elif debris['type'] == 'beam':
            points = [(-size, -size * 0.15), (size, -size * 0.1),
                     (size, size * 0.1), (-size, size * 0.15)]
        elif debris['type'] == 'container':
            points = [(-size * 0.5, -size * 0.5), (size * 0.5, -size * 0.5),
                     (size * 0.5, size * 0.5), (-size * 0.5, size * 0.5)]
        else:  # panel
            points = [(-size * 0.7, -size * 0.5), (size * 0.6, -size * 0.3),
                     (size * 0.5, size * 0.4), (-size * 0.8, size * 0.3)]

        rotated = [(int(x + px * cos_r - py * sin_r), int(y + px * sin_r + py * cos_r))
                   for px, py in points]

        if len(rotated) >= 3:
            pygame.draw.polygon(surface, color, rotated)
            darker = tuple(max(0, c - 15) for c in color)
            pygame.draw.polygon(surface, darker, rotated, 1)

    def _draw_asteroid(self, surface, asteroid, y):
        """Draw a single asteroid"""
        x = asteroid['x']
        rot = asteroid['rotation']

        # Rotate and translate points
        cos_r, sin_r = math.cos(rot), math.sin(rot)
        points = []
        for px, py in asteroid['points']:
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            points.append((int(x + rx), int(y + ry)))

        if len(points) >= 3:
            pygame.draw.polygon(surface, asteroid['color'], points)
            # Darker edge
            darker = tuple(max(0, c - 20) for c in asteroid['color'])
            pygame.draw.polygon(surface, darker, points, 1)
