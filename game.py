"""Main game logic for EVE Rebellion"""
import pygame
import random
import math
import json
import os
import sys
from constants import (
    AMMO_TYPES, COLOR_AMARR_ACCENT, COLOR_AMARR_DARK, COLOR_ARMOR,
    COLOR_HULL, COLOR_MINMATAR_ACCENT, COLOR_SHIELD, COLOR_TEXT,
    DIFFICULTY_SETTINGS, ENEMY_STATS, FACTIONS, FPS,
    JAGUAR_SHIELD_BONUS, JAGUAR_SPEED_BONUS, ROCKET_DAMAGE,
    SCREEN_HEIGHT, SCREEN_WIDTH, SHAKE_DECAY, SHAKE_LARGE,
    SHAKE_MEDIUM, SHAKE_SMALL, STAGES_AMARR, STAGES_CALDARI,
    STAGES_GALLENTE, STAGES_MINMATAR, UPGRADE_COSTS,
    WOLF_ARMOR_BONUS, WOLF_HULL_BONUS, WOLF_SPEED_BONUS
)
from sprites import (Player, Enemy, Wingman,
                     RefugeePod, Powerup, PowerupPickupEffect, Explosion, Star, ParallaxBackground)
from sounds import get_sound_manager, get_music_manager
from controller_input import ControllerInput, XboxButton
from space_background import SpaceBackground, AmarrArchon
from parallax_background import ParallaxBackground as StageParallaxBackground
from visual_effects import (ShipDamageEffects, EnhancedExplosion,
                            get_ship_damage_effects, clear_ship_damage_effects,
                            get_shield_impact_manager, get_screen_shake, get_muzzle_flash_manager,
                            clear_all_effects)
from expansion.capital_ship_enemy import CapitalShipEnemy
from berserk_system import BerserkSystem
from cinematic_system import CinematicManager, TribeType
from tutorial import TutorialManager
from high_scores import HighScoreManager, AchievementManager
from particle_effects import (ParticleEmitter, ScreenEffects, DamageNumberManager,
                              WarpTransition, HitMarker, ComboEffects)
from environmental_hazards import HazardManager
from ship_roster import get_ship_roster
from wave_patterns import get_wave_pattern_manager
from abyssal_mode import get_abyssal_mode


class SplashScreen:
    """Polished splash screen with detailed Rifter hull"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.timer = 0
        self.done = False
        self.skip_requested = False

        # Create the detailed Rifter surface once
        self.rifter_surface = self._create_detailed_rifter()

        # Stars for background (more stars, varied)
        self.stars = []
        for _ in range(150):
            self.stars.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'speed': random.uniform(0.2, 1.5),
                'size': random.randint(1, 2),
                'brightness': random.randint(60, 200),
                'twinkle': random.uniform(0, math.pi * 2)
            })

        # Ship fade-in animation
        self.ship_alpha = 0
        self.ship_glow = 0

        # Title animation
        self.title_alpha = 0
        self.subtitle_alpha = 0
        self.prompt_alpha = 0
        self.prompt_blink = 0

        # Ambient particles (dust/debris)
        self.particles = []
        for _ in range(30):
            self.particles.append({
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'vx': random.uniform(-0.3, 0.3),
                'vy': random.uniform(0.2, 0.8),
                'size': random.randint(1, 3),
                'alpha': random.randint(30, 80)
            })

    def _create_detailed_rifter(self):
        """Load and display the Rifter sprite for title screen - clean and sharp"""
        import os

        # Try to load the actual Rifter sprite
        sprite_path = os.path.join(os.path.dirname(__file__), 'assets', 'ship_sprites', 'rifter.png')

        try:
            # Load the Rifter sprite
            rifter_sprite = pygame.image.load(sprite_path).convert_alpha()

            # Scale up for title screen - keep it sharp
            orig_w, orig_h = rifter_sprite.get_size()
            scale = 4.5
            new_w = int(orig_w * scale)
            new_h = int(orig_h * scale)
            rifter_sprite = pygame.transform.smoothscale(rifter_sprite, (new_w, new_h))

            # Simple canvas with minimal padding
            padding = 60
            size = max(new_w, new_h) + padding * 2
            final_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            cx, _cy = size // 2, size // 2

            # Center the sprite - that's it, let the actual art speak
            sprite_x = (size - new_w) // 2
            sprite_y = (size - new_h) // 2
            final_surf.blit(rifter_sprite, (sprite_x, sprite_y))

            # Simple engine glow at the rear (subtle)
            glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            engine_y = sprite_y + new_h - 15
            for r in range(25, 0, -3):
                alpha = int(100 * (r / 25))
                pygame.draw.circle(glow_surf, (255, 150, 50, alpha), (cx, engine_y), r)
            final_surf.blit(glow_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

            return final_surf

        except (pygame.error, FileNotFoundError):
            # Fallback to procedural generation if sprite not found
            return self._create_procedural_rifter()

    def _create_procedural_rifter(self):
        """Fallback procedural Rifter if sprite not available"""
        size = 400
        surf = pygame.Surface((size, size), pygame.SRCALPHA)

        # Minmatar color palette
        rust_dark = (80, 45, 25)
        rust_mid = (140, 80, 45)
        metal_mid = (90, 85, 75)
        cockpit_glass = (80, 120, 160)
        engine_glow = (255, 200, 100)

        cx, cy = size // 2, size // 2

        # Main hull body
        hull_main = [
            (cx + 110, cy - 5),
            (cx + 75, cy - 42),
            (cx - 15, cy - 60),
            (cx - 90, cy - 35),
            (cx - 110, cy),
            (cx - 90, cy + 42),
            (cx - 25, cy + 70),
            (cx + 55, cy + 52),
            (cx + 95, cy + 18),
        ]
        pygame.draw.polygon(surf, rust_mid, hull_main)
        pygame.draw.polygon(surf, rust_dark, hull_main, 2)

        # Upper asymmetric wing
        wing_upper = [
            (cx - 20, cy - 60),
            (cx - 80, cy - 120),
            (cx - 100, cy - 110),
            (cx - 120, cy - 80),
            (cx - 100, cy - 40),
        ]
        pygame.draw.polygon(surf, metal_mid, wing_upper)

        # Lower asymmetric wing
        wing_lower = [
            (cx - 30, cy + 70),
            (cx - 60, cy + 130),
            (cx - 90, cy + 120),
            (cx - 110, cy + 80),
            (cx - 90, cy + 45),
        ]
        pygame.draw.polygon(surf, metal_mid, wing_lower)

        # Cockpit
        pygame.draw.ellipse(surf, cockpit_glass, (cx + 45, cy - 14, 25, 18))

        # Engines
        for ey in [cy - 20, cy, cy + 25]:
            pygame.draw.circle(surf, engine_glow, (cx - 105, ey), 8)

        # Add glow
        glow_surf = pygame.Surface((size + 40, size + 40), pygame.SRCALPHA)
        for r in range(40, 0, -5):
            alpha = int(15 * r / 40)
            pygame.draw.circle(glow_surf, (255, 150, 80, alpha), (size // 2 + 20, size // 2 + 20), size // 3 + r)
        final_surf = pygame.Surface((size + 40, size + 40), pygame.SRCALPHA)
        final_surf.blit(glow_surf, (0, 0))
        final_surf.blit(surf, (20, 20))

        return final_surf

    def update(self):
        """Update splash screen animations"""
        self.timer += 1

        # Update stars with twinkle
        for star in self.stars:
            star['y'] += star['speed']
            star['twinkle'] += 0.05
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)

        # Ship fades in
        if self.timer > 20:
            self.ship_alpha = min(180, self.ship_alpha + 2)
            self.ship_glow = min(100, self.ship_glow + 1)

        # Fade in title
        if self.timer > 60:
            self.title_alpha = min(255, self.title_alpha + 4)

        if self.timer > 100:
            self.subtitle_alpha = min(255, self.subtitle_alpha + 4)

        if self.timer > 140:
            self.prompt_blink += 1
            self.prompt_alpha = int(128 + 127 * math.sin(self.prompt_blink * 0.08))

        # Update ambient particles
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            if p['y'] > self.height:
                p['y'] = 0
                p['x'] = random.randint(0, self.width)
            if p['x'] < 0:
                p['x'] = self.width
            elif p['x'] > self.width:
                p['x'] = 0

        # Auto-advance after delay or on input
        if self.timer > 400 or self.skip_requested:
            self.done = True

    def handle_event(self, event):
        """Handle input to skip splash"""
        if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            if self.timer > 40:  # Minimum display time
                self.skip_requested = True
        if event.type == pygame.JOYBUTTONDOWN:
            if self.timer > 40:
                self.skip_requested = True

    def draw(self, surface):
        """Draw splash screen"""
        # Deep space gradient background
        for y in range(self.height):
            progress = y / self.height
            r = int(5 + 10 * progress)
            g = int(5 + 8 * progress)
            b = int(20 + 15 * progress)
            pygame.draw.line(surface, (r, g, b), (0, y), (self.width, y))

        # Draw stars with twinkle effect
        for star in self.stars:
            twinkle = 0.7 + 0.3 * math.sin(star['twinkle'])
            brightness = int(star['brightness'] * twinkle)
            color = (brightness, brightness, int(brightness * 1.1))
            pygame.draw.circle(surface, color,
                             (int(star['x']), int(star['y'])), star['size'])

        # Draw ambient dust particles
        for p in self.particles:
            color = (180, 140, 100, p['alpha'])
            dust_surf = pygame.Surface((p['size'] * 2, p['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(dust_surf, color, (p['size'], p['size']), p['size'])
            surface.blit(dust_surf, (int(p['x']) - p['size'], int(p['y']) - p['size']))

        # Draw the detailed Rifter (diagonal, in background)
        if self.ship_alpha > 0:
            # Rotate the rifter for diagonal orientation
            rotated = pygame.transform.rotate(self.rifter_surface, 25)
            rotated.set_alpha(self.ship_alpha)
            # Position in right side of screen
            rx = self.width // 2 - rotated.get_width() // 2 + 80
            ry = self.height // 2 - rotated.get_height() // 2 + 50
            surface.blit(rotated, (rx, ry))

        # Draw title with glow
        if self.title_alpha > 0:
            self._draw_title(surface)

        # Draw subtitle
        if self.subtitle_alpha > 0:
            font = pygame.font.Font(None, 26)
            text = font.render("An EVE-Inspired Arcade Shooter", True,
                             (160, 110, 70))
            text.set_alpha(self.subtitle_alpha)
            rect = text.get_rect(center=(self.width // 2, self.height * 0.46))
            surface.blit(text, rect)

        # Draw prompt
        if self.prompt_alpha > 50:
            font = pygame.font.Font(None, 22)
            prompt_text = "Press any button to start"
            text = font.render(prompt_text, True, (200, 200, 200))
            text.set_alpha(self.prompt_alpha)
            rect = text.get_rect(center=(self.width // 2, self.height * 0.88))
            surface.blit(text, rect)

    def _draw_title(self, surface):
        """Draw animated title with glow effect"""
        font_large = pygame.font.Font(None, 80)
        font_sub = pygame.font.Font(None, 44)

        # Outer glow
        glow_color = (180, 100, 50)
        for offset in range(12, 0, -2):
            alpha = int(self.title_alpha * 0.2 * (12 - offset) / 12)
            glow_surf = pygame.Surface((self.width, 100), pygame.SRCALPHA)
            glow_text = font_large.render("MINMATAR", True, (*glow_color, alpha))
            glow_rect = glow_text.get_rect(center=(self.width // 2, 50))
            glow_surf.blit(glow_text, glow_rect)
            surface.blit(glow_surf, (0, int(self.height * 0.28) + offset))

        # Main title
        title_color = (255, 210, 160)
        title = font_large.render("MINMATAR", True, title_color)
        title.set_alpha(self.title_alpha)
        rect = title.get_rect(center=(self.width // 2, self.height * 0.30))
        surface.blit(title, rect)

        # Subtitle with subtle glow
        sub_color = (230, 130, 70)
        subtitle = font_sub.render("REBELLION", True, sub_color)
        subtitle.set_alpha(self.title_alpha)
        rect = subtitle.get_rect(center=(self.width // 2, self.height * 0.39))
        surface.blit(subtitle, rect)

        # Decorative line under subtitle
        if self.title_alpha > 100:
            line_alpha = min(150, self.title_alpha - 100)
            line_surf = pygame.Surface((200, 3), pygame.SRCALPHA)
            pygame.draw.line(line_surf, (180, 100, 50, line_alpha), (0, 1), (200, 1), 2)
            surface.blit(line_surf, (self.width // 2 - 100, int(self.height * 0.42)))


class ScreenShake:
    """Manages screen shake effects"""

    def __init__(self):
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def add(self, intensity):
        """Add shake intensity"""
        self.intensity = max(self.intensity, intensity)
    
    def update(self):
        """Update shake and get current offset"""
        if self.intensity > 0.5:
            self.offset_x = random.uniform(-self.intensity, self.intensity)
            self.offset_y = random.uniform(-self.intensity, self.intensity)
            self.intensity *= SHAKE_DECAY
        else:
            self.intensity = 0
            self.offset_x = 0
            self.offset_y = 0
        return self.offset_x, self.offset_y


class Game:
    """Main game class"""
    
    def __init__(self):
        pygame.init()

        # Windowed mode - use configured screen size
        display_info = pygame.display.Info()
        self.fullscreen = False  # Windowed mode for desktop use
        if self.fullscreen:
            self.actual_width = display_info.current_w
            self.actual_height = display_info.current_h
            self.screen = pygame.display.set_mode((self.actual_width, self.actual_height), pygame.FULLSCREEN)
        else:
            self.actual_width = SCREEN_WIDTH
            self.actual_height = SCREEN_HEIGHT
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Render at game resolution, scale to screen
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.space_background = SpaceBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.archon_carrier = AmarrArchon(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Stage-based parallax background system
        self.stage_background = StageParallaxBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player_dx = 0  # Track player horizontal movement for parallax
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

        pygame.display.set_caption("EVE Rebellion")

        # Load window icon
        try:
            import os
            icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
            if os.path.exists(icon_path):
                icon = pygame.image.load(icon_path)
                pygame.display.set_icon(icon)
        except Exception:
            pass  # Icon is optional

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 22)
        

        # Controller (optional)
        self.controller = ControllerInput()
        # Initialize sound
        self.sound_manager = get_sound_manager()
        self.music_manager = get_music_manager()
        self.sound_enabled = True
        self.music_enabled = True
        
        # Screen shake
        self.shake = ScreenShake()
        self.shake_enabled = True

        # Berserk scoring system
        self.berserk = BerserkSystem()

        # Environmental hazards
        self.hazards = HazardManager()

        # Wave pattern system
        self.wave_patterns = get_wave_pattern_manager()
        self.current_wave_pattern = None
        self.pattern_spawn_queue = []  # Queue of SpawnPoints to spawn

        # Abyssal Depths mode
        self.abyssal = get_abyssal_mode()
        self.selected_filament = 0  # Index into abyssal_filaments
        self.selected_tier = 0  # Index into abyssal_tiers

        # Visual effects
        self.screen_flash_alpha = 0
        self.screen_flash_color = (255, 50, 50)
        self.show_danger_zones = False  # Toggle with D key or R3
        self.hud_mode = 0  # 0=full, 1=minimal, 2=off - Toggle with L3

        # Low health warning
        self.low_health_timer = 0
        self.low_health_interval = 90  # Frames between warning beeps

        # Cinematic system
        self.cinematic = CinematicManager(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.selected_tribe = TribeType.SEBIESTOR
        self.show_cinematics = True  # Can be toggled in options

        # Tutorial system
        self.tutorial = TutorialManager()
        self.tutorial_shown = False  # Track if player has seen tutorial

        # High scores and achievements
        self.high_scores = HighScoreManager()
        self.achievements = AchievementManager()
        self.last_rank = 0  # Rank achieved in last game
        self.new_high_score = False  # Flag for new high score
        self.achievement_display = []  # Queue of achievements to display
        self.achievement_timer = 0

        # Particle effects system
        self.particles = pygame.sprite.Group()
        self.particle_emitter = ParticleEmitter(self.particles)
        self.screen_effects = ScreenEffects()
        self.damage_numbers = DamageNumberManager()

        # Visual effects
        self.warp_transition = WarpTransition(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.hit_markers = HitMarker()
        self.combo_effects = ComboEffects(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Splash screen
        self.splash_screen = SplashScreen(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Faction background images for menus
        self.faction_backgrounds = {}
        bg_path = os.path.join(os.path.dirname(__file__), 'assets', 'backgrounds')
        for faction in ['minmatar', 'amarr', 'caldari', 'gallente']:
            bg_file = os.path.join(bg_path, f'{faction}_bg.jpg')
            if os.path.exists(bg_file):
                try:
                    bg_img = pygame.image.load(bg_file).convert()
                    # Scale to screen size
                    self.faction_backgrounds[faction] = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                except pygame.error:
                    self.faction_backgrounds[faction] = None
            else:
                self.faction_backgrounds[faction] = None

        # Game state
        self.state = 'splash'  # splash, chapter_select, menu, difficulty, tribe_select, empire_select, faction_select, filament_select, ship_select, mode_select, playing, shop, paused, gameover, victory, settings, credits
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']

        # Game mode
        self.game_mode = 'campaign'  # campaign, endless, or boss_rush
        self.endless_wave = 0
        self.endless_time = 0
        self.endless_high_wave = 0
        self.endless_high_score = 0

        # Boss rush mode
        self.boss_rush_bosses = ['omen', 'apocalypse', 'abaddon', 'machariel', 'stratios', 'amarr_capital']
        self.boss_rush_index = 0
        self.boss_rush_high_score = 0
        self.boss_rush_best_time = 0

        # Settings menu
        self.settings = {
            'master_volume': 100,
            'sfx_volume': 100,
            'music_volume': 100,
            'screen_shake': True,
            'show_damage_numbers': True,
            'show_danger_zones': False,
            'controller_vibration': True,
        }
        self.settings_options = [
            ('master_volume', 'Master Volume', 'slider'),
            ('sfx_volume', 'SFX Volume', 'slider'),
            ('music_volume', 'Music Volume', 'slider'),
            ('screen_shake', 'Screen Shake', 'toggle'),
            ('show_damage_numbers', 'Damage Numbers', 'toggle'),
            ('show_danger_zones', 'Danger Zones', 'toggle'),
            ('controller_vibration', 'Controller Vibration', 'toggle'),
        ]
        self.settings_index = 0
        self._load_settings()  # Load saved settings

        # Pause menu
        self.pause_menu_index = 0
        self.pause_menu_options = ['Resume', 'Settings', 'Restart', 'Quit to Menu']

        # Ship roster from JSON config
        self.ship_roster = get_ship_roster()

        # Ship selection
        self.selected_ship = 'rifter'  # Default ship
        self.ship_options = self.ship_roster.get_ship_options('minmatar', 'minmatar_rebellion')
        if not self.ship_options:
            self.ship_options = ['rifter', 'breacher', 'wolf', 'jaguar']  # Fallback
        self.ship_select_index = 0
        self.t2_ships_unlocked = True  # TESTING: Wolf and Jaguar unlocked

        # Difficulty selection
        self.difficulty_options = ['easy', 'normal', 'hard', 'nightmare']
        self.difficulty_index = 1  # Default to normal

        # Mode selection
        self.mode_options = ['campaign', 'endless', 'boss_rush', 'abyssal']
        self.mode_index = 0

        # Abyssal Depths mode data
        self.abyssal_filaments = [
            {
                'id': 'exotic',
                'name': 'EXOTIC',
                'color': (255, 255, 255),
                'description': 'Stable void. No modifiers.',
                'player_buff': None,
                'player_debuff': None
            },
            {
                'id': 'firestorm',
                'name': 'FIRESTORM',
                'color': (255, 69, 0),
                'description': '+50% Armor, -50% Shield',
                'player_buff': {'armor': 1.5},
                'player_debuff': {'shield': 0.5}
            },
            {
                'id': 'electrical',
                'name': 'ELECTRICAL',
                'color': (0, 191, 255),
                'description': '+50% Shield, -50% Armor',
                'player_buff': {'shield': 1.5},
                'player_debuff': {'armor': 0.5}
            },
            {
                'id': 'dark_matter',
                'name': 'DARK MATTER',
                'color': (148, 0, 211),
                'description': '-30% Signature, -50% Range',
                'player_buff': {'signature': 0.7},
                'player_debuff': {'range': 0.5}
            },
            {
                'id': 'gamma',
                'name': 'GAMMA',
                'color': (50, 205, 50),
                'description': '+50% Shield Boost, -30% Explosive Resist',
                'player_buff': {'shield_boost': 1.5},
                'player_debuff': {'explosive_resist': 0.7}
            }
        ]
        self.abyssal_tiers = [
            {'name': 'Calm', 'mult': 1.0, 'color': (144, 238, 144)},
            {'name': 'Agitated', 'mult': 1.3, 'color': (255, 255, 0)},
            {'name': 'Fierce', 'mult': 1.6, 'color': (255, 165, 0)},
            {'name': 'Raging', 'mult': 2.0, 'color': (255, 69, 0)},
            {'name': 'Chaotic', 'mult': 2.5, 'color': (220, 20, 60)},
            {'name': 'Cataclysmic', 'mult': 3.0, 'color': (139, 0, 0)}
        ]
        self.abyssal_filament_index = 0
        self.abyssal_tier_index = 0
        self.abyssal_room = 1  # Current room (1-3)
        self.abyssal_timer = 0  # Time remaining in abyss

        # Faction selection
        self.faction_options = ['minmatar', 'amarr']
        self.faction_index = 0
        self.selected_faction = 'minmatar'  # Default faction
        self.active_stages = STAGES_MINMATAR  # Campaign stages for selected faction

        # Faction selection - choose your faction (enemy is the opposing faction)
        self.empire_options = [
            {
                'id': 'minmatar',
                'name': 'MINMATAR REPUBLIC',
                'player_faction': 'minmatar',
                'enemy_faction': 'amarr',
                'description': 'Break the chains. Free our people.',
                'narrative': 'The Amarr Empire has enslaved our people for centuries.',
                'color_primary': (180, 100, 50),  # Minmatar rust
                'color_secondary': (139, 90, 43),  # Darker rust
            },
            {
                'id': 'amarr',
                'name': 'AMARR EMPIRE',
                'player_faction': 'amarr',
                'enemy_faction': 'minmatar',
                'description': 'Reclaim the heretics. Restore order.',
                'narrative': 'The Minmatar rebels threaten the Empire.',
                'color_primary': (139, 69, 19),  # Saddle brown/gold
                'color_secondary': (218, 165, 32),  # Golden rod
            },
            {
                'id': 'caldari',
                'name': 'CALDARI STATE',
                'player_faction': 'caldari',
                'enemy_faction': 'gallente',
                'description': 'Corporate warfare. Profit in blood.',
                'narrative': 'The Federation encroaches on State interests.',
                'color_primary': (30, 58, 95),  # Dark blue
                'color_secondary': (70, 130, 180),  # Steel blue
            },
            {
                'id': 'gallente',
                'name': 'GALLENTE FEDERATION',
                'player_faction': 'gallente',
                'enemy_faction': 'caldari',
                'description': 'Liberty and justice. Freedom for all.',
                'narrative': 'The Caldari State must be stopped.',
                'color_primary': (46, 93, 46),  # Dark green
                'color_secondary': (107, 142, 35),  # Olive
            }
        ]
        self.empire_index = 0
        self.selected_empire = self.empire_options[0]  # Default to Amarr front

        # Chapter selection - EVE Rebellion is a platform with multiple campaigns
        self.chapter_options = [
            {
                'id': 'minmatar_rebellion',
                'name': 'MINMATAR REBELLION',
                'subtitle': 'Break the Chains',
                'description': 'Fight for freedom against the Amarr Empire.',
                'color': (180, 100, 50),  # Minmatar rust
                'icon': 'rifter',
                'unlocked': True,
                'flow': ['difficulty', 'ship_select']  # Simplified: Difficulty → Ship
            },
            {
                'id': 'the_last_stand',
                'name': 'THE LAST STAND',
                'subtitle': 'Caldari-Gallente War',
                'description': 'Control a titan. Hold the line or stop the fall.',
                'color': (100, 150, 200),  # Caldari blue
                'icon': 'leviathan',
                'unlocked': False,  # Unlock after completing Minmatar
                'flow': ['faction_select', 'difficulty', 'ship_select']
            },
            {
                'id': 'abyssal_depths',
                'name': 'ABYSSAL DEPTHS',
                'subtitle': 'Triglavian Roguelike',
                'description': 'Enter the Abyss. Survive. Escape with loot.',
                'color': (200, 50, 80),  # Triglavian red
                'icon': 'vedmak',
                'unlocked': False,
                'flow': ['filament_select', 'ship_select']
            },
            {
                'id': 'sansha_incursion',
                'name': 'SANSHA INCURSION',
                'subtitle': 'Nation Rising',
                'description': 'Defend against the Sansha horde.',
                'color': (100, 200, 150),  # Sansha teal
                'icon': 'nightmare',
                'unlocked': False,
                'flow': ['difficulty', 'ship_select']
            },
            {
                'id': 'elder_fleet',
                'name': 'ELDER FLEET',
                'subtitle': 'The Great Escape',
                'description': 'Jove technology. Unlimited power.',
                'color': (180, 150, 220),  # Jove purple
                'icon': 'gnosis',
                'unlocked': False,
                'flow': ['difficulty', 'ship_select']
            }
        ]
        self.chapter_index = 0
        self.selected_chapter = self.chapter_options[0]

        # Menu navigation
        self.menu_options = ['start', 'how_to_play', 'settings', 'leaderboard', 'credits', 'quit']
        self.menu_index = 0

        # Menu transitions and animations
        self.menu_transition_alpha = 0
        self.menu_transition_target = 0
        self.menu_transition_speed = 15
        self.menu_slide_offset = 0
        self.menu_slide_target = 0
        self.menu_pulse_timer = 0  # For button pulse effects
        self.selection_bounce = 0  # Bounce effect on selection

        # Background stars
        self.stars = [Star() for _ in range(100)]

        # Parallax background layers
        self.parallax = ParallaxBackground()

        self.reset_game()
    
    def play_sound(self, sound_name, volume=1.0):
        """Play sound if enabled"""
        if self.sound_enabled:
            self.sound_manager.play(sound_name, volume)
    
    def reset_game(self):
        """Reset all game state"""
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.wingmen = pygame.sprite.Group()  # Allied wingmen for boss fights
        self.kill_counter = 0  # Track kills for wingman spawns
        self.kills_per_wingman = 15  # Spawn wingman every 15 kills
        self.pods = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.particles.empty()  # Clear particle effects
        self.damage_numbers.clear()  # Clear damage numbers

        # Boss tracking
        self.current_boss = None  # Track current boss for drone spawning/enrage

        # Player
        self.player = Player()
        self.all_sprites.add(self.player)

        # Player damage visual effects
        self.player_damage_effects = ShipDamageEffects()

        # Enhanced explosions list (for big ships with secondary explosions)
        self.enhanced_explosions = []

        # Shield impact effects
        self.shield_impacts = get_shield_impact_manager()
        self.shield_impacts.clear()

        # Screen shake
        self.screen_shake = get_screen_shake()
        self.screen_shake.clear()

        # Muzzle flash effects
        self.muzzle_flashes = get_muzzle_flash_manager()
        self.muzzle_flashes.clear()

        # Clear any lingering ship damage effects
        clear_all_effects()

        # Apply selected ship bonuses
        self.apply_ship_selection()

        # Stage/Wave tracking
        self.current_stage = 0
        self.current_wave = 0
        self.wave_enemies = 0
        self.wave_spawned = 0
        self.spawn_timer = 0
        self.wave_delay = 0
        self.stage_complete = False

        # Reset wave progression trackers
        self._bc_spawned_this_stage = False
        self._cruiser_count = 0
        self._destroyer_wing_timer = 0

        # Reset berserk system for new game
        self.berserk.reset_session()

        # Initialize environmental hazards for first stage
        self.hazards.clear()
        self.hazards.set_stage_hazards(self.current_stage)

        # Set background environment for current stage (1-indexed for display)
        if hasattr(self, 'stage_background'):
            self.stage_background.set_stage(self.current_stage + 1)

        # Messages
        self.message = ""
        self.message_timer = 0
        self.message_subtitle = None

    def apply_ship_selection(self):
        """Apply bonuses based on selected ship"""
        # === MINMATAR SHIPS ===
        if self.selected_ship == 'wolf':
            # Wolf: T2 Assault Frigate - armor and weapon focused
            self.player.is_wolf = True
            self.player.speed *= WOLF_SPEED_BONUS
            self.player.max_armor += WOLF_ARMOR_BONUS
            self.player.armor = self.player.max_armor
            self.player.max_hull += WOLF_HULL_BONUS
            self.player.hull = self.player.max_hull
            self.player.spread_bonus += 1
            self.player.ship_class = 'Wolf'
            self.player.image = self.player._create_ship_image()
        elif self.selected_ship == 'jaguar':
            # Jaguar: T2 Assault Frigate - speed and evasion focused
            self.player.is_jaguar = True
            self.player.speed *= JAGUAR_SPEED_BONUS
            self.player.max_shields += JAGUAR_SHIELD_BONUS
            self.player.shields = self.player.max_shields
            self.player.ship_class = 'Jaguar'
            self.player.image = self.player._create_ship_image()
        elif self.selected_ship == 'rifter':
            # Rifter: T1 Frigate - default Minmatar
            self.player.ship_class = 'Rifter'
            self.player.image = self.player._create_ship_image()
        # === AMARR SHIPS ===
        elif self.selected_ship == 'executioner':
            # Executioner: T1 Frigate - fast Amarr frigate
            self.player.ship_class = 'Executioner'
            self.player.image = self.player._create_ship_image()
        elif self.selected_ship == 'crusader':
            # Crusader: T2 Interceptor - speed focused
            self.player.is_crusader = True
            self.player.speed *= 1.35  # Fast interceptor
            self.player.max_shields += 25
            self.player.shields = self.player.max_shields
            self.player.ship_class = 'Crusader'
            self.player.image = self.player._create_ship_image()
        elif self.selected_ship == 'malediction':
            # Malediction: T2 Interceptor - tackle/evasion focused
            self.player.is_malediction = True
            self.player.speed *= 1.5  # Fastest interceptor
            self.player.max_armor += 30
            self.player.armor = self.player.max_armor
            self.player.ship_class = 'Malediction'
            self.player.image = self.player._create_ship_image()
    
    def show_message(self, text, duration=120, subtitle=None):
        """Show a temporary message with optional subtitle"""
        self.message = text
        self.message_timer = duration
        self.message_subtitle = subtitle
    
    def spawn_wave(self):
        """Spawn enemies for current wave with progressive scaling"""
        # Endless mode has its own spawning logic
        if self.game_mode == 'endless':
            self._spawn_endless_wave()
            return

        stage = self.active_stages[self.current_stage]

        # Progressive wave scaling formula - LOTS of enemies to plow through
        # Base enemies + wave bonus + stage bonus + difficulty modifier
        base_enemies = 12
        wave_bonus = self.current_wave * 3  # +3 enemies per wave
        stage_bonus = self.current_stage * 5  # +5 enemies per stage

        # Difficulty modifiers - more enemies on harder difficulties
        diff_mult = {
            'easy': 0.8,
            'normal': 1.2,
            'hard': 1.6,
            'nightmare': 2.0
        }.get(self.difficulty, 1.0)

        num_enemies = int((base_enemies + wave_bonus + stage_bonus) * diff_mult)
        num_enemies = min(num_enemies, 60)  # Cap per wave but there are many waves

        # Check for boss wave
        if (stage['boss'] and self.current_wave == stage['waves'] - 1):
            # Boss wave
            boss_type = stage['boss']

            # Use specialized CapitalShipEnemy class for amarr_capital
            if boss_type == 'amarr_capital':
                boss = CapitalShipEnemy(SCREEN_WIDTH // 2, self.difficulty_settings)
            else:
                boss = Enemy(boss_type, SCREEN_WIDTH // 2, -100, self.difficulty_settings)

            self.enemies.add(boss)
            self.all_sprites.add(boss)
            self.current_boss = boss  # Track boss for drone spawning/enrage
            self.wave_enemies = 1
            self.wave_spawned = 1

            # 33% chance to spawn 2 wingmen to assist
            if random.random() < 0.33:
                self._spawn_wingmen()
                self.show_message(f"REINFORCEMENTS! {boss.stats['name'].upper()} APPROACHING!", 180)
            else:
                self.show_message(f"WARNING: {boss.stats['name'].upper()} APPROACHING!", 180)

            self.play_sound('boss_entrance', 0.7)
            self.play_sound('warning')
            return

        # Regular wave
        self.wave_enemies = num_enemies
        self.wave_spawned = 0

        # Maybe spawn industrial
        if random.random() < stage['industrial_chance']:
            self.wave_enemies += 1

        # Use wave patterns for varied enemy spawn formations
        # Higher chance in later waves/stages for more tactical variety
        pattern_chance = 0.5 + (self.current_wave * 0.05) + (self.current_stage * 0.1)
        pattern_chance = min(pattern_chance, 0.85)  # Cap at 85%

        if random.random() < pattern_chance:
            pattern_name = self.wave_patterns.get_pattern_for_wave(
                self.current_wave, self.current_stage
            )
            enemy_types = [e for e in stage['enemies'] if e not in ['bestower', 'drone']]
            if not enemy_types:
                enemy_types = ['executioner']

            spawn_points = self.wave_patterns.generate_wave(
                pattern_name, min(num_enemies, 15), enemy_types
            )
            self.pattern_spawn_queue = spawn_points
            self.current_wave_pattern = pattern_name

    def _spawn_endless_wave(self):
        """Spawn enemies for endless mode with escalating difficulty"""
        self.endless_wave += 1
        wave = self.endless_wave

        # Difficulty multiplier
        diff_mult = {
            'easy': 0.7,
            'normal': 1.0,
            'hard': 1.3,
            'nightmare': 1.6
        }.get(self.difficulty, 1.0)

        # Escalating enemy count: starts at 3, grows with diminishing returns
        base_enemies = 3 + int(wave * 0.5) + int(wave ** 0.7)
        num_enemies = int(base_enemies * diff_mult)
        num_enemies = min(num_enemies, 25)  # Cap at 25 enemies per wave

        # Boss every 10 waves
        if wave % 10 == 0:
            # Spawn a mini-boss
            boss_types = ['apocalypse', 'harbinger', 'zealot']
            boss_type = boss_types[min(wave // 10 - 1, len(boss_types) - 1)]
            boss = Enemy(boss_type, SCREEN_WIDTH // 2, -100, self.difficulty_settings)
            self.enemies.add(boss)
            self.all_sprites.add(boss)
            self.wave_enemies = 1 + num_enemies // 2  # Half normal + boss
            self.wave_spawned = 1
            self.show_message(f"WAVE {wave} - BOSS INCOMING!", 180)
            self.play_sound('boss_entrance', 0.7)
            self.play_sound('warning')
        else:
            self.wave_enemies = num_enemies
            self.wave_spawned = 0
            self.show_message(f"WAVE {wave}", 90)
            self.play_sound('wave_start')

        # Industrial chance increases with waves (caps at 40%)
        industrial_chance = min(0.1 + wave * 0.015, 0.4)
        if random.random() < industrial_chance:
            self.wave_enemies += 1
    
    def _get_spawn_position(self, allow_flanking: bool = True):
        """Get a spawn position from full 360-degree arc for tactical spawning

        Args:
            allow_flanking: If True, allows bottom/side spawns for flanking attacks
        """
        # Spawn direction weights - now includes flanking positions
        if allow_flanking and self.current_wave > 1:
            # After first wave, enable tactical flanking spawns
            spawn_type = random.choices(
                ['top', 'carrier', 'left', 'right', 'top_left', 'top_right',
                 'bottom_left', 'bottom_right', 'bottom'],
                weights=[25, 20, 10, 10, 8, 8, 6, 6, 7]
            )[0]
        else:
            # Early waves - mostly frontal assault
            spawn_type = random.choices(
                ['top', 'carrier', 'left', 'right', 'top_left', 'top_right'],
                weights=[30, 30, 12, 12, 8, 8]
            )[0]

        if spawn_type == 'carrier' and hasattr(self, 'archon_carrier'):
            # Spawn from Archon carrier hangar
            carrier_x, carrier_y = self.archon_carrier.get_spawn_position()
            x = carrier_x + random.randint(-150, 150)
            x = max(50, min(SCREEN_WIDTH - 50, x))
            y = carrier_y
            self.archon_carrier.trigger_launch()
            return x, y, 0, 'top'

        elif spawn_type == 'top':
            # Standard top spawn
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = -50
            return x, y, 0, 'top'

        elif spawn_type == 'left':
            # Left side spawn - enemies fly in from left
            x = -50
            y = random.randint(100, SCREEN_HEIGHT // 2)
            return x, y, math.radians(45), 'left'

        elif spawn_type == 'right':
            # Right side spawn - enemies fly in from right
            x = SCREEN_WIDTH + 50
            y = random.randint(100, SCREEN_HEIGHT // 2)
            return x, y, math.radians(-45), 'right'

        elif spawn_type == 'top_left':
            # Top-left diagonal
            x = random.randint(-50, SCREEN_WIDTH // 4)
            y = -50
            return x, y, math.radians(20), 'top'

        elif spawn_type == 'top_right':
            # Top-right diagonal
            x = random.randint(SCREEN_WIDTH * 3 // 4, SCREEN_WIDTH + 50)
            y = -50
            return x, y, math.radians(-20), 'top'

        elif spawn_type == 'bottom_left':
            # Bottom-left flanking attack
            x = -50
            y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
            return x, y, math.radians(30), 'bottom_left'

        elif spawn_type == 'bottom_right':
            # Bottom-right flanking attack
            x = SCREEN_WIDTH + 50
            y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 100)
            return x, y, math.radians(-30), 'bottom_right'

        else:  # bottom
            # Bottom spawn - behind the player!
            x = random.randint(200, SCREEN_WIDTH - 200)
            y = SCREEN_HEIGHT + 50
            return x, y, math.radians(180), 'bottom'

    def spawn_enemy(self):
        """Spawn a single enemy from 260-degree frontal arc with progressive composition"""
        if self.wave_spawned >= self.wave_enemies:
            return

        if self.game_mode == 'endless':
            self._spawn_endless_enemy()
            return

        # Check pattern spawn queue first
        if self.pattern_spawn_queue:
            self._spawn_from_pattern()
            return

        stage = self.active_stages[self.current_stage]

        # Chance for industrial - guarantee at least one per wave in later stages
        if (self.wave_spawned == self.wave_enemies - 1 and
            random.random() < stage['industrial_chance'] * 2):
            enemy_type = 'bestower'
        else:
            # Progressive enemy composition based on wave progress and kills
            enemy_type = self._get_progressive_enemy_type(stage)

        # Get spawn position from multi-directional system
        x, y, entry_angle, spawn_direction = self._get_spawn_position()

        # Drones spawn in swarms of 3-5 with formation
        if enemy_type == 'drone':
            self._spawn_drone_swarm(x, y)
        else:
            enemy = Enemy(enemy_type, x, y, self.difficulty_settings)
            # Set entry angle and spawn direction for tactical spawning
            enemy.spawn_direction = spawn_direction
            if entry_angle != 0:
                enemy.entry_angle = entry_angle
                enemy.entering_from_side = True
            # Configure movement for flanking spawns
            if spawn_direction in ['bottom', 'bottom_left', 'bottom_right']:
                enemy.is_flanking = True
                enemy.target_y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT - 150)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.wave_spawned += 1

    def _spawn_from_pattern(self):
        """Spawn enemies from the pattern queue."""
        if not self.pattern_spawn_queue:
            return

        # Process spawn points that are ready (delay == 0)
        spawned_this_frame = 0
        remaining = []

        for spawn_point in self.pattern_spawn_queue:
            if spawn_point.delay <= 0:
                # Spawn this enemy
                enemy_type = spawn_point.enemy_type or 'executioner'
                enemy = Enemy(enemy_type, spawn_point.x, spawn_point.y, self.difficulty_settings)

                # Apply custom velocity from pattern and use wave spawn movement
                enemy.vx = spawn_point.vx
                enemy.vy = spawn_point.vy
                enemy.from_wave_pattern = True
                enemy.pattern_vx = spawn_point.vx
                enemy.pattern_vy = spawn_point.vy
                enemy.pattern = Enemy.PATTERN_WAVE_SPAWN  # Use wave pattern movement

                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                self.wave_spawned += 1
                spawned_this_frame += 1

                # Limit spawns per frame to prevent lag
                if spawned_this_frame >= 3:
                    remaining.extend([p for p in self.pattern_spawn_queue if p.delay > 0])
                    break
            else:
                spawn_point.delay -= 1
                remaining.append(spawn_point)

        self.pattern_spawn_queue = remaining

    def _get_progressive_enemy_type(self, stage):
        """
        Select enemy type based on wave progress for structured escalation:
        - Early wave: Mostly frigates
        - Mid wave: Destroyers join from diagonals
        - Late wave: Cruisers appear
        - Every 3-4 waves: Battlecruiser mini-boss chance

        Creates feeling of escalating battle intensity.
        """
        wave_progress = self.wave_spawned / max(1, self.wave_enemies)
        current_wave = self.current_wave

        # Track destroyer wing spawns (trigger diagonal attacks)
        if not hasattr(self, '_destroyer_wing_timer'):
            self._destroyer_wing_timer = 0
            self._cruiser_count = 0
            self._bc_spawned_this_stage = False

        available = stage['enemies']

        # Categorize available enemies
        frigates = [e for e in available if e in ['executioner', 'punisher', 'tormentor', 'crucifier', 'drone']]
        destroyers = [e for e in available if e in ['coercer']]
        cruisers = [e for e in available if e in ['omen', 'maller']]
        battlecruisers = [e for e in available if e in ['harbinger']]

        # Default to frigates if categories are empty
        if not frigates:
            frigates = [available[0]] if available else ['executioner']

        # === WAVE STRUCTURE ===

        # Early wave (0-30%): Frigates only, but trigger destroyer wing attack occasionally
        if wave_progress < 0.3:
            # Every 15 spawns, chance for destroyer diagonal wing
            self._destroyer_wing_timer += 1
            if self._destroyer_wing_timer >= 15 and destroyers and current_wave >= 1:
                if random.random() < 0.4:  # 40% chance
                    self._spawn_destroyer_wing()
                    self._destroyer_wing_timer = 0
            return random.choice(frigates)

        # Mid wave (30-60%): Mix frigates and destroyers
        elif wave_progress < 0.6:
            if destroyers and random.random() < 0.35:
                return random.choice(destroyers)
            return random.choice(frigates)

        # Late wave (60-85%): Cruisers enter the battle
        elif wave_progress < 0.85:
            if cruisers and random.random() < 0.25:
                self._cruiser_count += 1
                return random.choice(cruisers)
            elif destroyers and random.random() < 0.3:
                return random.choice(destroyers)
            return random.choice(frigates)

        # End wave (85-100%): Battlecruiser mini-boss after enough cruisers
        else:
            # Spawn BC mini-boss after 3+ cruisers killed and every 3rd wave
            if (battlecruisers and
                self._cruiser_count >= 3 and
                current_wave >= 2 and
                current_wave % 3 == 0 and
                not self._bc_spawned_this_stage):
                self._bc_spawned_this_stage = True
                self._cruiser_count = 0
                self.show_message("BATTLECRUISER APPROACHING!", 90)
                self.play_sound('warning')
                return random.choice(battlecruisers)

            # Otherwise continue with cruiser/destroyer mix
            if cruisers and random.random() < 0.3:
                return random.choice(cruisers)
            elif destroyers and random.random() < 0.35:
                return random.choice(destroyers)
            return random.choice(frigates)

    def _spawn_destroyer_wing(self):
        """
        Spawn a wing of destroyers that attack from diagonal corners.
        They cross the screen diagonally and respawn from top if not destroyed.
        """
        # Alternate spawn sides
        from_left = random.choice([True, False])

        # Wing of 3-5 destroyers
        wing_size = random.randint(3, 5)

        for i in range(wing_size):
            if from_left:
                # Spawn from top-left, move to bottom-right
                x = -40 - i * 30
                y = -60 - i * 40
                vx = 3.0 + random.uniform(-0.3, 0.3)
            else:
                # Spawn from top-right, move to bottom-left
                x = SCREEN_WIDTH + 40 + i * 30
                y = -60 - i * 40
                vx = -3.0 + random.uniform(-0.3, 0.3)

            vy = 2.5 + random.uniform(-0.2, 0.4)

            enemy = Enemy('coercer', x, y, self.difficulty_settings)
            enemy.pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx
            enemy.patrol_vy = vy
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        direction = "LEFT FLANK" if from_left else "RIGHT FLANK"
        self.show_message(f"DESTROYER WING - {direction}!", 60)

    def _spawn_drone_swarm(self, center_x, center_y):
        """Spawn a swarm of 3-5 drones in formation"""
        swarm_size = random.randint(3, 5)

        # Formation patterns
        formations = [
            # V formation
            [(0, 0), (-30, 25), (30, 25), (-60, 50), (60, 50)],
            # Diamond formation
            [(0, 0), (-35, 30), (35, 30), (0, 60), (0, -30)],
            # Line formation
            [(-60, 0), (-30, 0), (0, 0), (30, 0), (60, 0)],
            # Cluster formation
            [(0, 0), (-20, 20), (20, 20), (-25, -15), (25, -15)],
        ]

        formation = random.choice(formations)

        for i in range(swarm_size):
            if i < len(formation):
                offset_x, offset_y = formation[i]
            else:
                # Random offset for extra drones
                offset_x = random.randint(-40, 40)
                offset_y = random.randint(-20, 40)

            drone_x = center_x + offset_x
            drone_y = center_y + offset_y

            # Keep on screen
            drone_x = max(30, min(SCREEN_WIDTH - 30, drone_x))

            drone = Enemy('drone', drone_x, drone_y, self.difficulty_settings)
            # Give drones in same swarm similar orbit parameters for cohesion
            if hasattr(drone, 'swarm_angle'):
                drone.swarm_angle = random.uniform(0, math.pi * 2)
                drone.swarm_radius = random.randint(50, 80)  # Tighter swarm
            self.enemies.add(drone)
            self.all_sprites.add(drone)

        self.wave_spawned += 1  # Count as one "spawn" even though multiple drones

    def _spawn_wingmen(self):
        """Spawn 2 allied wingmen to assist during boss fight"""
        # Clear any existing wingmen
        self.wingmen.empty()

        # Spawn 2 wingmen flanking the player
        offsets = [-60, 60]
        for offset in offsets:
            wingman = Wingman(self.player, offset)
            wingman.rect.centerx = self.player.rect.centerx + offset
            wingman.rect.centery = self.player.rect.centery + 40
            self.wingmen.add(wingman)
            self.all_sprites.add(wingman)

        self.show_message("Wingmen deployed!", 60)

    def _spawn_wingman(self):
        """Spawn a single Rifter wingman to join the player (33% wave reward)"""
        # Find an open position (avoid stacking)
        existing_offsets = [w.offset_x for w in self.wingmen]
        possible_offsets = [-80, -50, 50, 80, -110, 110]

        for offset in possible_offsets:
            if offset not in existing_offsets:
                wingman = Wingman(self.player, offset)
                wingman.rect.centerx = self.player.rect.centerx + offset
                wingman.rect.centery = self.player.rect.centery + 40
                self.wingmen.add(wingman)
                self.all_sprites.add(wingman)
                self.show_message("Rifter pilot joins your wing!", 90)
                self.play_sound('pickup_major', 0.6)
                return

        # Max wingmen reached
        self.show_message("Wing at full capacity", 60)

    def _spawn_endless_enemy(self):
        """Spawn enemy for endless mode from 260-degree frontal arc"""
        wave = self.endless_wave

        # Enemy pool expands as waves progress
        if wave <= 5:
            pool = ['executioner', 'punisher', 'tormentor']
        elif wave <= 15:
            pool = ['executioner', 'punisher', 'tormentor', 'coercer', 'crucifier']
        elif wave <= 30:
            pool = ['punisher', 'coercer', 'omen', 'maller', 'dragoon']
        else:
            pool = ['coercer', 'omen', 'maller', 'harbinger', 'dragoon', 'zealot']

        # Chance for industrial (increases with waves)
        if random.random() < 0.08 + wave * 0.005:
            enemy_type = 'bestower'
        else:
            enemy_type = random.choice(pool)

        # Get spawn position from multi-directional system
        x, y, entry_angle, spawn_direction = self._get_spawn_position()

        enemy = Enemy(enemy_type, x, y, self.difficulty_settings)
        # Set entry angle and spawn direction for tactical spawning
        if entry_angle != 0:
            enemy.entry_angle = entry_angle
            enemy.entering_from_side = True
        enemy.spawn_direction = spawn_direction
        # Mark as flanking if spawning from bottom/sides
        if spawn_direction in ['bottom', 'bottom_left', 'bottom_right']:
            enemy.is_flanking = True
            enemy.pattern = enemy.PATTERN_FLANKING
            enemy._init_flanking_behavior()
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        self.wave_spawned += 1
    
    def spawn_powerup(self, x, y):
        """Maybe spawn a powerup at location - contextual based on player state"""
        chance = self.difficulty_settings.get('powerup_chance', 0.15)
        if random.random() < chance:
            powerup_type = self._choose_powerup_type()
            powerup = Powerup(x, y, powerup_type)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)

    def _choose_powerup_type(self):
        """Choose powerup type based on player state - health drops are contextual"""
        # 30% chance for contextual health powerup if player is damaged
        if random.random() < 0.3:
            health_type = self._get_contextual_health_powerup()
            if health_type:
                return health_type

        # Otherwise pick from random powerups
        from constants import RANDOM_POWERUPS
        return random.choice(RANDOM_POWERUPS)

    def _get_contextual_health_powerup(self):
        """Return appropriate health powerup based on what's damaged, or None"""
        # Only drop health for the layer that's currently taking damage
        shield_pct = self.player.shields / max(self.player.max_shields, 1)
        armor_pct = self.player.armor / max(self.player.max_armor, 1)
        hull_pct = self.player.hull / max(self.player.max_hull, 1)

        # Hull is damaged (player is in hull) - drop hull repairer
        if hull_pct < 1.0 and self.player.armor <= 0:
            return 'hull_repairer'
        # Armor is damaged (player is in armor) - drop armor repairer
        elif armor_pct < 1.0 and self.player.shields <= 0:
            return 'armor_repairer'
        # Shields are damaged - drop shield recharger
        elif shield_pct < 0.8:
            return 'shield_recharger'

        return None  # Player is healthy, no health powerup needed

    def spawn_formation(self, formation_type, enemy_types=None):
        """Spawn a group of enemies in formation"""
        if enemy_types is None:
            if self.game_mode == 'endless':
                wave = self.endless_wave
                if wave <= 10:
                    enemy_types = ['executioner', 'punisher']
                elif wave <= 25:
                    enemy_types = ['punisher', 'coercer']
                else:
                    enemy_types = ['coercer', 'omen']
            else:
                stage = self.active_stages[self.current_stage]
                enemy_types = [e for e in stage['enemies'] if e not in ['bestower', 'drone']]
                if not enemy_types:
                    enemy_types = ['executioner']

        if formation_type == 'v_shape':
            self._spawn_v_formation(enemy_types)
        elif formation_type == 'escort':
            self._spawn_escort_formation(enemy_types)
        elif formation_type == 'pincer':
            self._spawn_pincer_formation(enemy_types)
        elif formation_type == 'line':
            self._spawn_line_formation(enemy_types)
        elif formation_type == 'diamond':
            self._spawn_diamond_formation(enemy_types)
        elif formation_type == 'surround':
            self._spawn_surround_formation(enemy_types)
        elif formation_type == 'roaming_fleet':
            self._spawn_roaming_fleet(enemy_types)

    def _spawn_v_formation(self, enemy_types):
        """Spawn V-formation from any direction - 360 degree spawning"""
        # Choose spawn direction with weights
        directions = ['top', 'left', 'right', 'bottom', 'top_left', 'top_right', 'bottom_left', 'bottom_right']
        weights = [15, 15, 15, 10, 12, 12, 10, 10]  # Slightly favor sides
        direction = random.choices(directions, weights=weights)[0]

        self._spawn_directional_v_formation(enemy_types, direction)

    def _spawn_directional_v_formation(self, enemy_types, direction, size=5):
        """Spawn V-formation from specified direction pointing toward screen center"""
        spacing = 45

        # Calculate spawn position and velocity based on direction
        if direction == 'top':
            cx, cy = random.randint(150, SCREEN_WIDTH - 150), -50
            vx, vy = 0, 2.5
            # V points down (direction of travel)
            wing_dx, wing_dy = spacing, -spacing
        elif direction == 'bottom':
            cx, cy = random.randint(150, SCREEN_WIDTH - 150), SCREEN_HEIGHT + 50
            vx, vy = 0, -2.5
            # V points up
            wing_dx, wing_dy = spacing, spacing
        elif direction == 'left':
            cx, cy = -50, random.randint(150, SCREEN_HEIGHT - 200)
            vx, vy = 3.0, 0.5
            # V points right
            wing_dx, wing_dy = -spacing, spacing
        elif direction == 'right':
            cx, cy = SCREEN_WIDTH + 50, random.randint(150, SCREEN_HEIGHT - 200)
            vx, vy = -3.0, 0.5
            # V points left
            wing_dx, wing_dy = spacing, spacing
        elif direction == 'top_left':
            cx, cy = -50, -50
            vx, vy = 2.5, 2.0
            # V points bottom-right (diagonal)
            wing_dx, wing_dy = -spacing * 0.7, -spacing * 0.7
        elif direction == 'top_right':
            cx, cy = SCREEN_WIDTH + 50, -50
            vx, vy = -2.5, 2.0
            # V points bottom-left
            wing_dx, wing_dy = spacing * 0.7, -spacing * 0.7
        elif direction == 'bottom_left':
            cx, cy = -50, SCREEN_HEIGHT + 50
            vx, vy = 2.5, -2.0
            # V points top-right
            wing_dx, wing_dy = -spacing * 0.7, spacing * 0.7
        else:  # bottom_right
            cx, cy = SCREEN_WIDTH + 50, SCREEN_HEIGHT + 50
            vx, vy = -2.5, -2.0
            # V points top-left
            wing_dx, wing_dy = spacing * 0.7, spacing * 0.7

        # Build V-formation positions: leader at tip, wings spread back
        positions_and_offsets = [(0, 0)]  # Leader at tip
        for row in range(1, (size + 1) // 2):
            positions_and_offsets.append((wing_dx * row, wing_dy * row))      # Left wing
            positions_and_offsets.append((-wing_dx * row, wing_dy * row))     # Right wing

        leader_type = random.choice(enemy_types)
        leader = None

        for i, (off_x, off_y) in enumerate(positions_and_offsets):
            if i >= size:
                break
            x = cx + off_x
            y = cy + off_y
            etype = leader_type if i == 0 else random.choice(enemy_types)
            enemy = Enemy(etype, x, y, self.difficulty_settings)

            # Set velocity for the formation direction
            enemy.vx = vx
            enemy.vy = vy
            enemy.pattern = enemy.PATTERN_DIAGONAL

            if i == 0:
                leader = enemy
                enemy.formation_role = 'leader'
            else:
                enemy.pattern = enemy.PATTERN_FORMATION
                enemy.formation_leader = leader
                enemy.formation_offset = (off_x, off_y)
                enemy.formation_role = 'follower'

            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        self.wave_spawned += min(size, len(positions_and_offsets))

        # Direction-specific messages
        dir_names = {
            'top': 'ABOVE', 'bottom': 'BELOW', 'left': 'PORT', 'right': 'STARBOARD',
            'top_left': 'PORT BOW', 'top_right': 'STARBOARD BOW',
            'bottom_left': 'PORT STERN', 'bottom_right': 'STARBOARD STERN'
        }
        self.show_message(f"V-FORMATION FROM {dir_names.get(direction, 'UNKNOWN')}!", 60)

    def _spawn_escort_formation(self, enemy_types):
        """Spawn escorts protecting a Bestower with formation following"""
        center_x = random.randint(100, SCREEN_WIDTH - 100)
        base_y = -80

        # Center: Bestower (VIP) is the leader
        bestower = Enemy('bestower', center_x, base_y, self.difficulty_settings)
        bestower.formation_role = 'leader'
        self.enemies.add(bestower)
        self.all_sprites.add(bestower)

        # Escorts around the Bestower with offsets for formation following
        escort_offsets = [
            (-60, -30),   # Front left
            (60, -30),    # Front right
            (-50, 50),    # Rear left
            (50, 50),     # Rear right
        ]

        for offset_x, offset_y in escort_offsets:
            x = center_x + offset_x
            y = base_y + offset_y
            enemy = Enemy(random.choice(enemy_types), x, y, self.difficulty_settings)
            # Set up formation following
            enemy.pattern = enemy.PATTERN_FORMATION
            enemy.formation_leader = bestower
            enemy.formation_offset = (offset_x, offset_y)
            enemy.formation_role = 'escort'
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        self.wave_spawned += 5
        self.show_message("ESCORT FORMATION - PROTECT THE SLAVES!", 90)

    def _spawn_pincer_formation(self, enemy_types):
        """Spawn enemies from opposite sides - 360 degree pincer attack"""
        count_per_side = 3

        # Choose pincer axis: horizontal (left/right), vertical (top/bottom), or diagonal
        axis = random.choice(['horizontal', 'vertical', 'diagonal_1', 'diagonal_2'])

        if axis == 'horizontal':
            # Classic left-right pincer
            center_y = random.randint(200, SCREEN_HEIGHT - 200)
            for i in range(count_per_side):
                # Left side
                enemy = Enemy(random.choice(enemy_types), -30, center_y + (i - 1) * 50, self.difficulty_settings)
                enemy.vx, enemy.vy = 2.5, 0.3
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                # Right side
                enemy = Enemy(random.choice(enemy_types), SCREEN_WIDTH + 30, center_y + (i - 1) * 50, self.difficulty_settings)
                enemy.vx, enemy.vy = -2.5, 0.3
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "PINCER - PORT AND STARBOARD!"

        elif axis == 'vertical':
            # Top-bottom pincer (requires 360 aiming!)
            center_x = random.randint(150, SCREEN_WIDTH - 150)
            for i in range(count_per_side):
                # Top
                enemy = Enemy(random.choice(enemy_types), center_x + (i - 1) * 50, -30, self.difficulty_settings)
                enemy.vx, enemy.vy = 0, 2.5
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                # Bottom
                enemy = Enemy(random.choice(enemy_types), center_x + (i - 1) * 50, SCREEN_HEIGHT + 30, self.difficulty_settings)
                enemy.vx, enemy.vy = 0, -2.5
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "PINCER - ABOVE AND BELOW!"

        elif axis == 'diagonal_1':
            # Top-left to bottom-right diagonal
            for i in range(count_per_side):
                offset = (i - 1) * 40
                # Top-left
                enemy = Enemy(random.choice(enemy_types), -30 + offset, -30 - offset, self.difficulty_settings)
                enemy.vx, enemy.vy = 2.2, 2.2
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                # Bottom-right
                enemy = Enemy(random.choice(enemy_types), SCREEN_WIDTH + 30 - offset, SCREEN_HEIGHT + 30 + offset, self.difficulty_settings)
                enemy.vx, enemy.vy = -2.2, -2.2
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "DIAGONAL PINCER!"

        else:  # diagonal_2
            # Top-right to bottom-left diagonal
            for i in range(count_per_side):
                offset = (i - 1) * 40
                # Top-right
                enemy = Enemy(random.choice(enemy_types), SCREEN_WIDTH + 30 - offset, -30 - offset, self.difficulty_settings)
                enemy.vx, enemy.vy = -2.2, 2.2
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
                # Bottom-left
                enemy = Enemy(random.choice(enemy_types), -30 + offset, SCREEN_HEIGHT + 30 + offset, self.difficulty_settings)
                enemy.vx, enemy.vy = 2.2, -2.2
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "DIAGONAL PINCER!"

        self.wave_spawned += count_per_side * 2
        self.show_message(msg, 60)

    def _spawn_line_formation(self, enemy_types):
        """Spawn enemies in line formation from any edge"""
        count = 5
        direction = random.choice(['top', 'bottom', 'left', 'right'])

        if direction == 'top':
            spacing = (SCREEN_WIDTH - 100) // (count + 1)
            for i in range(count):
                x = 50 + spacing * (i + 1)
                enemy = Enemy(random.choice(enemy_types), x, -50, self.difficulty_settings)
                enemy.vy = 2.0
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "LINE FROM ABOVE!"

        elif direction == 'bottom':
            spacing = (SCREEN_WIDTH - 100) // (count + 1)
            for i in range(count):
                x = 50 + spacing * (i + 1)
                enemy = Enemy(random.choice(enemy_types), x, SCREEN_HEIGHT + 50, self.difficulty_settings)
                enemy.vy = -2.5
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "LINE FROM BELOW!"

        elif direction == 'left':
            spacing = (SCREEN_HEIGHT - 200) // (count + 1)
            for i in range(count):
                y = 100 + spacing * (i + 1)
                enemy = Enemy(random.choice(enemy_types), -50, y, self.difficulty_settings)
                enemy.vx = 2.5
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "LINE FROM PORT!"

        else:  # right
            spacing = (SCREEN_HEIGHT - 200) // (count + 1)
            for i in range(count):
                y = 100 + spacing * (i + 1)
                enemy = Enemy(random.choice(enemy_types), SCREEN_WIDTH + 50, y, self.difficulty_settings)
                enemy.vx = -2.5
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)
            msg = "LINE FROM STARBOARD!"

        self.wave_spawned += count
        self.show_message(msg, 60)

    def _spawn_diamond_formation(self, enemy_types):
        """Spawn diamond formation from any direction"""
        direction = random.choice(['top', 'bottom', 'left', 'right'])
        spacing = 50

        if direction == 'top':
            cx, cy = random.randint(150, SCREEN_WIDTH - 150), -50
            vx, vy = 0, 2.5
            offsets = [(0, 0), (-spacing, -spacing), (spacing, -spacing), (0, -spacing * 2)]
        elif direction == 'bottom':
            cx, cy = random.randint(150, SCREEN_WIDTH - 150), SCREEN_HEIGHT + 50
            vx, vy = 0, -2.5
            offsets = [(0, 0), (-spacing, spacing), (spacing, spacing), (0, spacing * 2)]
        elif direction == 'left':
            cx, cy = -50, random.randint(200, SCREEN_HEIGHT - 200)
            vx, vy = 2.5, 0.3
            offsets = [(0, 0), (-spacing, -spacing), (-spacing, spacing), (-spacing * 2, 0)]
        else:  # right
            cx, cy = SCREEN_WIDTH + 50, random.randint(200, SCREEN_HEIGHT - 200)
            vx, vy = -2.5, 0.3
            offsets = [(0, 0), (spacing, -spacing), (spacing, spacing), (spacing * 2, 0)]

        leader = None
        for i, (off_x, off_y) in enumerate(offsets):
            x, y = cx + off_x, cy + off_y
            enemy = Enemy(random.choice(enemy_types), x, y, self.difficulty_settings)
            enemy.vx, enemy.vy = vx, vy
            enemy.pattern = enemy.PATTERN_DIAGONAL

            if i == 0:
                leader = enemy
                enemy.formation_role = 'leader'
            else:
                enemy.pattern = enemy.PATTERN_FORMATION
                enemy.formation_leader = leader
                enemy.formation_offset = (off_x, off_y)
                enemy.formation_role = 'wingman'

            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        dir_names = {'top': 'ABOVE', 'bottom': 'BELOW', 'left': 'PORT', 'right': 'STARBOARD'}
        self.wave_spawned += 4
        self.show_message(f"DIAMOND FROM {dir_names[direction]}!", 60)

    def _spawn_surround_formation(self, enemy_types):
        """Spawn enemies from all 4 cardinal directions simultaneously - true 360 combat!"""
        count_per_direction = 2

        # Get player position for targeting (or screen center if no player)
        if hasattr(self, 'player') and self.player.alive():
            target_x = self.player.rect.centerx
            target_y = self.player.rect.centery
        else:
            target_x = SCREEN_WIDTH // 2
            target_y = SCREEN_HEIGHT // 2

        spawn_points = [
            # (start_x, start_y, velocity toward center)
            (target_x, -50, 0, 2.5),                          # Top
            (target_x, SCREEN_HEIGHT + 50, 0, -2.5),          # Bottom
            (-50, target_y, 2.5, 0),                          # Left
            (SCREEN_WIDTH + 50, target_y, -2.5, 0),           # Right
        ]

        for base_x, base_y, vx, vy in spawn_points:
            for i in range(count_per_direction):
                # Offset perpendicular to velocity
                if vx == 0:  # Vertical movement, offset horizontally
                    offset = (i - (count_per_direction - 1) / 2) * 60
                    x = base_x + offset
                    y = base_y
                else:  # Horizontal movement, offset vertically
                    offset = (i - (count_per_direction - 1) / 2) * 60
                    x = base_x
                    y = base_y + offset

                enemy = Enemy(random.choice(enemy_types), x, y, self.difficulty_settings)
                enemy.vx = vx
                enemy.vy = vy
                enemy.pattern = enemy.PATTERN_DIAGONAL
                self.enemies.add(enemy)
                self.all_sprites.add(enemy)

        self.wave_spawned += count_per_direction * 4
        self.show_message("SURROUNDED! ALL DIRECTIONS!", 90)

    def _spawn_roaming_fleet(self, enemy_types):
        """
        Spawn a realistic EVE-style roaming fleet that crosses the screen diagonally.
        Fleets don't vibrate in place - they cross through hunting for targets.
        Composition: 10-20 frigs, 5-10 dessies, 1-5 cruisers, 2-3 BCs
        """
        # Determine fleet composition
        num_frigates = random.randint(8, 15)
        num_destroyers = random.randint(4, 8)
        num_cruisers = random.randint(1, 3)
        num_battlecruisers = random.randint(1, 2)

        num_frigates + num_destroyers + num_cruisers + num_battlecruisers

        # Entry point: left or right side
        from_left = random.choice([True, False])
        start_x = -100 if from_left else SCREEN_WIDTH + 100
        SCREEN_WIDTH + 200 if from_left else -200

        # Entry y range (upper portion of screen)
        start_y = random.randint(-150, 100)

        # Diagonal velocity (crossing the screen)
        vx = 1.5 if from_left else -1.5
        vy = random.uniform(0.3, 0.8)  # Slight downward angle

        # Fleet arrangement - staggered rows
        spacing_x = 35
        spacing_y = 30
        row_width = 8  # Ships per row

        ships_spawned = 0

        # Spawn battlecruisers first (center/lead position)
        for i in range(num_battlecruisers):
            row = i // row_width
            col = i % row_width
            x = start_x + (col - row_width // 2) * spacing_x * 2
            y = start_y + row * spacing_y * 2
            enemy = Enemy('harbinger', x, y, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx * 0.8  # Slower, heavier
            enemy.patrol_vy = vy
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            ships_spawned += 1

        # Cruisers behind BCs
        for i in range(num_cruisers):
            offset = ships_spawned + i
            row = 1 + offset // row_width
            col = offset % row_width
            x = start_x + (col - row_width // 2) * spacing_x * 1.5
            y = start_y + row * spacing_y + 60
            etype = random.choice(['omen', 'maller'])
            enemy = Enemy(etype, x, y, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx * 0.9
            enemy.patrol_vy = vy
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            ships_spawned += 1

        # Destroyers flanking
        for i in range(num_destroyers):
            side = i % 2  # Alternate sides
            row = 2 + i // 4
            x = start_x + ((-1 if side == 0 else 1) * (spacing_x * 4 + i * 15))
            y = start_y + row * spacing_y + 120
            enemy = Enemy('coercer', x, y, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx * 1.1  # Faster
            enemy.patrol_vy = vy
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            ships_spawned += 1

        # Frigates swarming around
        for i in range(num_frigates):
            scatter_x = random.randint(-80, 80)
            scatter_y = random.randint(150, 300)
            x = start_x + scatter_x
            y = start_y + scatter_y + i * 20
            etype = random.choice(['executioner', 'punisher', 'tormentor'])
            enemy = Enemy(etype, x, y, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx * (1.0 + random.uniform(-0.2, 0.3))  # Varied speeds
            enemy.patrol_vy = vy + random.uniform(-0.1, 0.2)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            ships_spawned += 1

        self.wave_spawned += ships_spawned
        fleet_name = "HOSTILE FLEET" if from_left else "ENEMY ROAM"
        self.show_message(f"{fleet_name} CROSSING - {ships_spawned} CONTACTS!", 90)

    def maybe_spawn_formation(self):
        """Chance to spawn a formation instead of single enemies"""
        # Formation chance increases with progression
        if self.game_mode == 'endless':
            # More formations as endless waves progress
            formation_chance = min(0.35, 0.08 + self.endless_wave * 0.015)
        else:
            # Formations start appearing in stage 2+
            formation_chance = 0.15 + self.current_stage * 0.06

        if random.random() < formation_chance:
            # Base formations - all support 360 degree spawning
            formations = ['v_shape', 'v_shape', 'line', 'pincer', 'diamond']

            # Surround attack - requires 360 aiming, appears after wave 3
            if self.game_mode == 'endless' and self.endless_wave >= 3:
                formations.append('surround')
            elif self.game_mode != 'endless' and self.current_stage >= 2:
                formations.append('surround')

            # Escort only if bestower makes sense
            if self.game_mode == 'endless' and self.endless_wave >= 5:
                formations.append('escort')
            elif self.game_mode != 'endless' and self.current_stage >= 1:
                formations.append('escort')

            # Roaming fleets appear more often (they feel more realistic)
            if self.game_mode == 'endless' and self.endless_wave >= 3:
                formations.extend(['roaming_fleet', 'roaming_fleet'])  # Double weight
            elif self.game_mode != 'endless' and self.current_stage >= 2:
                formations.append('roaming_fleet')

            self.spawn_formation(random.choice(formations))
            return True
        return False

    def _boss_summon_minions(self, boss):
        """Boss summons minion enemies"""
        self.play_sound('boss_summon', 0.6)
        self.shake.add(SHAKE_SMALL)

        # Spawn 2-3 small enemies near the boss
        minion_types = ['executioner', 'punisher']
        count = 2 + (boss.boss_phase)  # More minions in later phases

        for i in range(count):
            offset_x = (i - count // 2) * 60
            spawn_x = boss.rect.centerx + offset_x
            spawn_x = max(50, min(SCREEN_WIDTH - 50, spawn_x))

            enemy = Enemy(
                spawn_x, boss.rect.bottom + 30,
                random.choice(minion_types),
                self.difficulty_settings
            )
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

            # Spawn particles
            self.particle_emitter.emit_explosion(
                spawn_x, boss.rect.bottom + 30,
                (255, 200, 100), 8, 3, 3)

    def _use_bomb(self):
        """Use screen-clearing bomb"""
        if not self.player.use_bomb():
            self.play_sound('error')
            return

        self.play_sound('bomb')
        self.shake.add(SHAKE_LARGE)

        # Big screen flash
        self.screen_flash_alpha = 200
        self.screen_flash_color = (255, 255, 255)

        # Clear all enemy bullets
        for bullet in self.enemy_bullets:
            self.particle_emitter.emit_explosion(
                bullet.rect.centerx, bullet.rect.centery,
                (255, 200, 100), 4, 2, 2)
            bullet.kill()

        # Damage all enemies on screen (except bosses which take partial)
        for enemy in list(self.enemies):
            # Create explosion at enemy position
            self.particle_emitter.emit_death_explosion(
                enemy.rect.centerx, enemy.rect.centery,
                COLOR_AMARR_ACCENT, 'medium')

            if enemy.is_boss:
                # Bosses take 25% of max health as damage
                total_hp = enemy.max_shields + enemy.max_armor + enemy.max_hull
                damage = int(total_hp * 0.25)
                # Apply damage to shields first, then armor, then hull
                if enemy.shields > 0:
                    absorbed = min(enemy.shields, damage)
                    enemy.shields -= absorbed
                    damage -= absorbed
                if damage > 0 and enemy.armor > 0:
                    absorbed = min(enemy.armor, damage)
                    enemy.armor -= absorbed
                    damage -= absorbed
                if damage > 0:
                    enemy.hull -= damage
                if enemy.hull <= 0:
                    enemy.kill()
                    self.player.score += enemy.score
                    self.play_sound('boss_death', 0.8)
            else:
                # Non-bosses are destroyed
                # Calculate heat percent for berserk bonus
                heat_percent = self.player.heat / self.player.max_heat if self.player.max_heat > 0 else 0
                berserk_score = self.berserk.register_kill(
                    enemy.score,
                    (self.player.rect.centerx, self.player.rect.centery),
                    (enemy.rect.centerx, enemy.rect.centery),
                    enemy.enemy_type,
                    heat_percent
                )
                self.player.score += berserk_score

                # Drop refugees from industrials
                if enemy.refugees > 0:
                    refugee_count = int(enemy.refugees * self.difficulty_settings['refugee_mult'])
                    for _ in range(max(1, refugee_count)):
                        pod = RefugeePod(
                            enemy.rect.centerx + random.randint(-20, 20),
                            enemy.rect.centery + random.randint(-20, 20)
                        )
                        self.refugee_pods.add(pod)
                        self.all_sprites.add(pod)

                enemy.kill()

        self.show_message("BOMB!", 90)

    def _toggle_fire_pattern(self):
        """Toggle between focused and spread fire patterns"""
        # Cooldown to prevent accidental double-toggle
        fire_pattern_cooldown = getattr(self, '_fire_pattern_cooldown', 0)
        if fire_pattern_cooldown > 0:
            return  # Still on cooldown

        if not hasattr(self.player, 'fire_pattern'):
            self.player.fire_pattern = 'focused'

        if self.player.fire_pattern == 'focused':
            self.player.fire_pattern = 'spread'
            self.show_message("SPREAD FIRE", 45)
        else:
            self.player.fire_pattern = 'focused'
            self.show_message("FOCUSED FIRE", 45)

        self._fire_pattern_cooldown = 20  # ~0.33 second cooldown at 60fps
        self.play_sound('ammo_switch')

    def _thrust_jet(self, direction=1):
        """Execute thrust jet maneuver - quick burst in movement direction

        Pure mobility skill - no invincibility. Jaguar has unlimited uses.

        Args:
            direction: -1 for left, 0 for forward, 1 for right
        """
        # Check thrust cooldown (Jaguar has 0 cooldown = unlimited)
        if self.player.thrust_cooldown > 0:
            self.play_sound('error')
            return False

        self.player.thrust_active = True
        self.player.thrust_timer = self.player.thrust_duration
        self.player.thrust_cooldown = self.player.thrust_cooldown_time
        self.player.thrust_direction = direction
        self.player.thrust_velocity = 25  # Initial burst speed (pixels/frame)

        # No invincibility - thrust is pure mobility

        self.play_sound('powerup')
        if self.controller and self.controller.connected:
            self.controller.trigger_decision_haptic()

        # Engine flare effect
        self.screen_flash_alpha = 20
        if direction == 0:
            self.screen_flash_color = (255, 200, 100)  # Forward boost
        elif direction > 0:
            self.screen_flash_color = (255, 150, 50)  # Right
        else:
            self.screen_flash_color = (50, 150, 255)  # Left
        return True

    def _thrust_with_movement(self):
        """Execute thrust in current movement direction (from left stick)

        Pure mobility skill - no invincibility. Uses left stick direction.
        LB or RB triggers thrust in whatever direction player is moving.
        """
        # Check thrust cooldown (Jaguar has 0 cooldown = unlimited)
        if self.player.thrust_cooldown > 0:
            self.play_sound('error')
            return False

        # Get movement direction from controller
        move_x, move_y = 0.0, 0.0
        if self.controller and self.controller.connected:
            move_x, move_y = self.controller.get_movement_vector()

        # Determine thrust direction from movement
        # If no movement, default to forward
        if abs(move_x) < 0.2 and abs(move_y) < 0.2:
            direction = 0  # Forward
        elif abs(move_x) > abs(move_y):
            direction = 1 if move_x > 0 else -1  # Horizontal
        else:
            direction = 0  # Forward (up) or back, treat as forward

        self.player.thrust_active = True
        self.player.thrust_timer = self.player.thrust_duration
        self.player.thrust_cooldown = self.player.thrust_cooldown_time
        self.player.thrust_direction = direction
        self.player.thrust_velocity = 25 if direction != 0 else 30  # Forward is faster

        # No invincibility - thrust is pure mobility

        self.play_sound('powerup')
        if self.controller and self.controller.connected:
            self.controller.trigger_decision_haptic()

        # Engine flare effect based on direction
        self.screen_flash_alpha = 20
        if direction == 0:
            self.screen_flash_color = (255, 200, 100)  # Forward
        elif direction > 0:
            self.screen_flash_color = (255, 150, 50)  # Right
        else:
            self.screen_flash_color = (50, 150, 255)  # Left
        return True

    def _emergency_brake(self):
        """Execute emergency brake - escape maneuver with invincibility

        Drops to bottom of screen with invincibility that lasts until landing.
        This is an escape mechanic, not mobility - use it to survive.
        Weapons are disabled during brake animation.
        """
        if self.player.emergency_brake_cooldown > 0:
            self.play_sound('error')
            return False

        self.player.emergency_brake_active = True
        self.player.emergency_brake_timer = self.player.emergency_brake_duration
        self.player.emergency_brake_cooldown = self.player.emergency_brake_cooldown_time
        self.player.brake_start_y = self.player.rect.centery

        # Invincibility lasts until landing - set far future, cleared when brake ends
        self.player.brake_invulnerable = True
        self.player.invulnerable_until = pygame.time.get_ticks() + 60000  # 60s failsafe

        self.play_sound('powerup')
        self.show_message("EMERGENCY ESCAPE!", 50)
        if self.controller and self.controller.connected:
            self.controller.trigger_decision_haptic()

        # Golden flash effect (like ADC activation)
        self.screen_flash_alpha = 40
        self.screen_flash_color = (255, 215, 0)
        return True

    def _update_maneuvers(self):
        """Update active combat maneuvers"""
        # Thrust jet update
        if self.player.thrust_active:
            self.player.thrust_timer -= 1

            # Calculate progress (0 to 1)
            duration = self.player.thrust_duration + (6 if self.player.thrust_direction == 0 else 0)
            progress = 1 - (self.player.thrust_timer / duration)

            # Velocity starts high and decelerates (ease-out)
            velocity_mult = 1 - (progress * progress)
            current_velocity = self.player.thrust_velocity * velocity_mult

            if self.player.thrust_direction == 0:
                # Forward boost - move UP (toward enemies)
                self.player.rect.y -= current_velocity
            else:
                # Horizontal thrust
                self.player.rect.x += self.player.thrust_direction * current_velocity

            # Keep on screen
            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

            # Emit thrust trail
            if self.player.thrust_timer % 2 == 0:
                if self.player.thrust_direction == 0:
                    # Forward boost - trail behind (below) the ship
                    px = self.player.rect.centerx + random.randint(-10, 10)
                    py = self.player.rect.bottom + 5
                    color = random.choice([
                        (255, 220, 100), (255, 180, 50), (255, 140, 0)
                    ])
                    trail_angle = math.pi / 2  # Down
                else:
                    # Horizontal - trail from opposite side
                    trail_side = -self.player.thrust_direction
                    px = self.player.rect.centerx + trail_side * 20
                    py = self.player.rect.centery + random.randint(-5, 5)

                    if self.player.thrust_direction > 0:
                        color = random.choice([
                            (255, 200, 100), (255, 150, 50), (255, 100, 0)
                        ])
                    else:
                        color = random.choice([
                            (100, 200, 255), (50, 150, 255), (0, 100, 255)
                        ])
                    trail_angle = math.pi if self.player.thrust_direction > 0 else 0

                self.particle_emitter.emit_sparks(px, py, color, count=3, direction=trail_angle)

            if self.player.thrust_timer <= 0:
                self.player.thrust_active = False
                self.player.thrust_velocity = 0

        if self.player.thrust_cooldown > 0:
            self.player.thrust_cooldown -= 1

        # Emergency brake update
        if self.player.emergency_brake_active:
            self.player.emergency_brake_timer -= 1
            progress = 1 - (self.player.emergency_brake_timer / self.player.emergency_brake_duration)

            # Ease-out curve for smooth deceleration
            eased = 1 - (1 - progress) ** 2
            target_y = SCREEN_HEIGHT - 60  # Near bottom
            self.player.rect.centery = int(self.player.brake_start_y + (target_y - self.player.brake_start_y) * eased)

            # Emit trail particles
            if self.player.emergency_brake_timer % 2 == 0:
                self.particle_emitter.emit_explosion(
                    self.player.rect.centerx, self.player.rect.top,
                    (255, 200, 100), 5, 3, 3)

            if self.player.emergency_brake_timer <= 0:
                self.player.emergency_brake_active = False
                # Clear brake invincibility on landing
                if getattr(self.player, 'brake_invulnerable', False):
                    self.player.brake_invulnerable = False
                    self.player.invulnerable_until = 0

        if self.player.emergency_brake_cooldown > 0:
            self.player.emergency_brake_cooldown -= 1

    def _apply_hazard_effects(self):
        """Apply environmental hazard effects to player"""
        if self.state != 'playing':
            return

        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery
        total_damage = 0

        # Asteroid collision damage
        asteroid_damage = self.hazards.get_asteroid_collisions(self.player.rect)
        if asteroid_damage > 0:
            total_damage += asteroid_damage
            self.shake.add(10)
            self.play_sound('hull_hit', 0.7)
            self.particle_emitter.emit_explosion(player_x, player_y, (150, 100, 50), 20, 8, 5)

        # Solar flare damage
        flare_damage = self.hazards.get_flare_damage()
        if flare_damage > 0:
            # Flare hits shields first
            total_damage += flare_damage
            self.screen_flash_alpha = 80
            self.screen_flash_color = (255, 220, 100)

        # Mine explosion damage
        mine_damage = self.hazards.get_mine_damage(player_x, player_y)
        if mine_damage > 0:
            total_damage += mine_damage
            self.shake.add(15)
            self.play_sound('explosion', 0.8)

        # Apply accumulated damage
        if total_damage > 0:
            self.player.take_damage(total_damage)
            self.damage_numbers.spawn(player_x, player_y, total_damage, (255, 100, 100))

        # Warp bubble pull effect
        pull_x, pull_y = self.hazards.get_bubble_pull(player_x, player_y)
        if pull_x != 0 or pull_y != 0:
            self.player.rect.x += int(pull_x)
            self.player.rect.y += int(pull_y)
            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Nebula slow effect - stored for player movement modifier
        self._nebula_slow = self.hazards.get_nebula_slow(player_x, player_y)

    def _handle_dpad_input(self):
        """Handle D-Pad input for quick actions"""
        if not self.controller.joystick:
            return

        try:
            # Get D-Pad (hat) input
            hat = self.controller.joystick.get_hat(0)
            hat_x, hat_y = hat

            # Track D-Pad state for edge detection
            if not hasattr(self, '_last_dpad'):
                self._last_dpad = (0, 0)

            # D-Pad Left/Right: Cycle ammo
            if hat_x == -1 and self._last_dpad[0] != -1:
                self.player.cycle_ammo(reverse=True)
                self.play_sound('ammo_switch')
            elif hat_x == 1 and self._last_dpad[0] != 1:
                self.player.cycle_ammo()
                self.play_sound('ammo_switch')

            # D-Pad Up: Toggle HUD
            if hat_y == 1 and self._last_dpad[1] != 1:
                self.hud_mode = (self.hud_mode + 1) % 3
                hud_names = ['FULL', 'MINIMAL', 'OFF']
                self.show_message(f"HUD: {hud_names[self.hud_mode]}", 60)
                self.play_sound('menu_select')

            # D-Pad Down: Toggle danger zones
            if hat_y == -1 and self._last_dpad[1] != -1:
                self.show_danger_zones = not self.show_danger_zones
                status = "ON" if self.show_danger_zones else "OFF"
                self.show_message(f"DANGER ZONES: {status}", 60)
                self.play_sound('menu_select')

            self._last_dpad = hat
        except (pygame.error, AttributeError):
            pass

    def handle_events(self):
        """Process input events"""
        # Controller: start frame (clears edge states)
        if self.controller:
            if hasattr(self.controller, "start_frame"):
                self.controller.start_frame()

        for event in pygame.event.get():
            # Feed controller events first
            if self.controller:
                self.controller.handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False

            # Auto-pause when window loses focus
            if event.type == pygame.WINDOWFOCUSLOST:
                if self.state == 'playing':
                    self.state = 'paused'
                    self.pause_menu_index = 0

            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYHATMOTION:
                pass  # Events handled by controller.handle_event()

            if self.controller and self.controller.connected:
                # Tutorial controller support
                if self.tutorial.active:
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.tutorial.skip_timer = 1
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.tutorial.tutorial_complete = True
                        self.tutorial.active = False

                if self.state == 'chapter_select':
                    # Left/Right navigation for chapter selection
                    move_x, move_y = self.controller.get_movement_vector()
                    if not getattr(self, '_chapter_controller_moved', False):
                        if move_x < -0.5 and self.chapter_index > 0:
                            self.chapter_index -= 1
                            self.play_sound('menu_select')
                            self._chapter_controller_moved = True
                        elif move_x > 0.5 and self.chapter_index < len(self.chapter_options) - 1:
                            self.chapter_index += 1
                            self.play_sound('menu_select')
                            self._chapter_controller_moved = True
                    if abs(move_x) < 0.3:
                        self._chapter_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        chapter = self.chapter_options[self.chapter_index]
                        if chapter.get('unlocked', False):
                            self.selected_chapter = chapter
                            self.start_chapter_flow()
                            self.play_sound('menu_select')
                        else:
                            self.play_sound('menu_error')  # Locked chapter
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'menu'  # Back to main menu
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.BACK):
                        self.state = 'settings'
                        self.play_sound('menu_select')

                elif self.state == 'menu':
                    # Navigation in main menu
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_menu_controller_moved', False):
                        self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                        self.play_sound('menu_select')
                        self._menu_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_menu_controller_moved', False):
                        self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                        self.play_sound('menu_select')
                        self._menu_controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._menu_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        option = self.menu_options[self.menu_index]
                        if option == 'start':
                            self.state = 'difficulty'  # Difficulty first, then ship
                        elif option == 'how_to_play':
                            self.state = 'how_to_play'
                            self.how_to_play_scroll = 0
                        elif option == 'settings':
                            self.state = 'settings'
                        elif option == 'leaderboard':
                            self.state = 'leaderboard'
                        elif option == 'credits':
                            self.state = 'credits'
                        elif option == 'quit':
                            pygame.quit()
                            sys.exit()
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.BACK):
                        # Quick access to settings
                        self.state = 'settings'
                        self.play_sound('menu_select')
                elif self.state == 'ship_select':
                    # Left stick for navigation
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_controller_moved', False):
                        self.ship_select_index = (self.ship_select_index - 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                        self._controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_controller_moved', False):
                        self.ship_select_index = (self.ship_select_index + 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                        self._controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._controller_moved = False
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        selected_key = self.ship_options[self.ship_select_index]
                        is_locked = selected_key in ['wolf', 'jaguar', 'crusader', 'malediction'] and not self.t2_ships_unlocked
                        if is_locked:
                            self.play_sound('menu_error')  # Can't select locked ship
                        else:
                            self.selected_ship = selected_key
                            self.start_game()  # Start game directly after ship select
                            self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'difficulty'  # Back to difficulty selection
                        self.play_sound('menu_select')
                elif self.state == 'empire_select':
                    # 2x2 grid navigation for faction selection (4 options)
                    move_x, move_y = self.controller.get_movement_vector()
                    if not getattr(self, '_empire_controller_moved', False):
                        row = self.empire_index // 2
                        col = self.empire_index % 2
                        moved = False
                        if move_x < -0.5 and col > 0:
                            self.empire_index -= 1
                            moved = True
                        elif move_x > 0.5 and col < 1:
                            self.empire_index += 1
                            moved = True
                        elif move_y < -0.5 and row > 0:
                            self.empire_index -= 2
                            moved = True
                        elif move_y > 0.5 and row < 1:
                            self.empire_index += 2
                            moved = True
                        if moved:
                            self.play_sound('menu_select')
                            self._empire_controller_moved = True
                    if abs(move_x) < 0.3 and abs(move_y) < 0.3:
                        self._empire_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.set_empire(self.empire_index)
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'difficulty'  # Back to difficulty
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.LB):
                        if self.empire_index > 0:
                            self.empire_index -= 1
                            self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.RB):
                        if self.empire_index < len(self.empire_options) - 1:
                            self.empire_index += 1
                            self.play_sound('menu_select')

                elif self.state == 'faction_select':
                    # Left/Right navigation for faction selection
                    move_x, move_y = self.controller.get_movement_vector()
                    if not getattr(self, '_faction_controller_moved', False):
                        if move_x < -0.5:
                            self.faction_index = 0
                            self.play_sound('menu_select')
                            self._faction_controller_moved = True
                        elif move_x > 0.5:
                            self.faction_index = 1
                            self.play_sound('menu_select')
                            self._faction_controller_moved = True
                    if abs(move_x) < 0.3:
                        self._faction_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.set_faction(self.faction_options[self.faction_index])
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'empire_select'  # Back to empire selection
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.LB):
                        self.faction_index = 0
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.RB):
                        self.faction_index = 1
                        self.play_sound('menu_select')
                elif self.state == 'difficulty':
                    # 2x2 grid navigation for difficulty
                    move_x, move_y = self.controller.get_movement_vector()
                    moved = False

                    if not getattr(self, '_diff_controller_moved', False):
                        # Up/Down for rows (index 0,1 = top row, 2,3 = bottom row)
                        if move_y < -0.5 and self.difficulty_index >= 2:
                            self.difficulty_index -= 2
                            self.play_sound('menu_select')
                            moved = True
                        elif move_y > 0.5 and self.difficulty_index < 2:
                            self.difficulty_index += 2
                            self.play_sound('menu_select')
                            moved = True
                        # Left/Right for columns (index 0,2 = left col, 1,3 = right col)
                        elif move_x < -0.5 and self.difficulty_index % 2 == 1:
                            self.difficulty_index -= 1
                            self.play_sound('menu_select')
                            moved = True
                        elif move_x > 0.5 and self.difficulty_index % 2 == 0:
                            self.difficulty_index += 1
                            self.play_sound('menu_select')
                            moved = True

                        if moved or abs(move_x) > 0.5 or abs(move_y) > 0.5:
                            self._diff_controller_moved = True

                    if abs(move_x) < 0.3 and abs(move_y) < 0.3:
                        self._diff_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.set_difficulty(self.difficulty_options[self.difficulty_index])
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'chapter_select'  # Back to chapter selection
                        self.play_sound('menu_select')
                elif self.state == 'mode_select':
                    # Navigation for mode selection
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_mode_controller_moved', False):
                        self.mode_index = (self.mode_index - 1) % len(self.mode_options)
                        self.play_sound('menu_select')
                        self._mode_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_mode_controller_moved', False):
                        self.mode_index = (self.mode_index + 1) % len(self.mode_options)
                        self.play_sound('menu_select')
                        self._mode_controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._mode_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        selected_mode = self.mode_options[self.mode_index]
                        if selected_mode == 'abyssal':
                            # Abyssal requires filament/tier selection first
                            self.state = 'filament_select'
                            self.play_sound('menu_select')
                        else:
                            self.start_game(selected_mode)
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'ship_select'  # Back to ship selection
                        self.play_sound('menu_select')
                elif self.state == 'filament_select':
                    # Navigation for filament and tier selection
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_x < -0.5 and not getattr(self, '_filament_controller_moved', False):
                        self.selected_filament = (self.selected_filament - 1) % len(self.abyssal_filaments)
                        self.play_sound('menu_select')
                        self._filament_controller_moved = True
                    elif move_x > 0.5 and not getattr(self, '_filament_controller_moved', False):
                        self.selected_filament = (self.selected_filament + 1) % len(self.abyssal_filaments)
                        self.play_sound('menu_select')
                        self._filament_controller_moved = True
                    elif move_y < -0.5 and not getattr(self, '_filament_controller_moved', False):
                        self.selected_tier = max(0, self.selected_tier - 1)
                        self.play_sound('menu_select')
                        self._filament_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_filament_controller_moved', False):
                        self.selected_tier = min(len(self.abyssal_tiers) - 1, self.selected_tier + 1)
                        self.play_sound('menu_select')
                        self._filament_controller_moved = True
                    elif abs(move_x) < 0.3 and abs(move_y) < 0.3:
                        self._filament_controller_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self._start_abyssal_run()
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'mode_select'  # Back to mode selection
                        self.play_sound('menu_select')
                elif self.state == 'playing':
                    if self.controller.is_button_just_pressed(XboxButton.START):
                        self.state = 'paused'
                        self.pause_menu_index = 0
                        self.play_sound('menu_select')
                    # A/B/X/Y are RESERVED - no gameplay bindings
                    # All gameplay controls handled via InputState:
                    # - LT = Brake (InputState.brake_pressed)
                    # - LB/RB = Thrust (InputState.thrust_held)
                    # - RT = Fire (InputState.fire_held)
                    # - R3 = Toggle fire mode (InputState.toggle_fire_mode_pressed)
                    # - Right Stick = Aim (InputState.aim_x/y)

                    # L3 for HUD toggle (utility, not gameplay)
                    if self.controller.is_button_just_pressed(XboxButton.L_STICK):
                        # Toggle HUD mode (full -> minimal -> off -> full)
                        self.hud_mode = (self.hud_mode + 1) % 3
                        hud_names = ['FULL', 'MINIMAL', 'OFF']
                        self.show_message(f"HUD: {hud_names[self.hud_mode]}", 60)
                        self.play_sound('menu_select')
                    # D-Pad for ammo cycling and HUD toggles
                    self._handle_dpad_input()
                elif self.state == 'paused':
                    if self.controller.is_button_just_pressed(XboxButton.START):
                        self.state = 'playing'
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.A):
                        self._select_pause_option()
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'playing'
                        self.play_sound('menu_select')
                    else:
                        # Left stick for pause menu navigation
                        move_x, move_y = self.controller.get_movement_vector()
                        if move_y < -0.5 and not getattr(self, '_pause_controller_moved', False):
                            self.pause_menu_index = (self.pause_menu_index - 1) % len(self.pause_menu_options)
                            self.play_sound('menu_select')
                            self._pause_controller_moved = True
                        elif move_y > 0.5 and not getattr(self, '_pause_controller_moved', False):
                            self.pause_menu_index = (self.pause_menu_index + 1) % len(self.pause_menu_options)
                            self.play_sound('menu_select')
                            self._pause_controller_moved = True
                        elif abs(move_y) < 0.3:
                            self._pause_controller_moved = False
                elif self.state in ['gameover', 'victory']:
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.reset_game()
                        self.state = 'menu'
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.X):
                        # Quick restart with same mode
                        self.reset_game()
                        self.start_game(self.game_mode)
                        self.play_sound('menu_select')
                elif self.state == 'settings':
                    # Settings navigation with controller
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_settings_controller_moved', False):
                        self.settings_index = (self.settings_index - 1) % len(self.settings_options)
                        self.play_sound('menu_select')
                        self._settings_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_settings_controller_moved', False):
                        self.settings_index = (self.settings_index + 1) % len(self.settings_options)
                        self.play_sound('menu_select')
                        self._settings_controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._settings_controller_moved = False

                    option_key, _, option_type = self.settings_options[self.settings_index]
                    if option_type == 'toggle':
                        if self.controller.is_button_just_pressed(XboxButton.A):
                            self.settings[option_key] = not self.settings[option_key]
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                    elif option_type == 'slider':
                        if move_x < -0.5 and not getattr(self, '_settings_x_moved', False):
                            self.settings[option_key] = max(0, self.settings[option_key] - 10)
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                            self._settings_x_moved = True
                        elif move_x > 0.5 and not getattr(self, '_settings_x_moved', False):
                            self.settings[option_key] = min(100, self.settings[option_key] + 10)
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                            self._settings_x_moved = True
                        elif abs(move_x) < 0.3:
                            self._settings_x_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'menu'
                        self.play_sound('menu_select')
                elif self.state == 'pause_settings':
                    # Settings navigation with controller (from pause menu)
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_settings_controller_moved', False):
                        self.settings_index = (self.settings_index - 1) % len(self.settings_options)
                        self.play_sound('menu_select')
                        self._settings_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_settings_controller_moved', False):
                        self.settings_index = (self.settings_index + 1) % len(self.settings_options)
                        self.play_sound('menu_select')
                        self._settings_controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._settings_controller_moved = False

                    option_key, _, option_type = self.settings_options[self.settings_index]
                    if option_type == 'toggle':
                        if self.controller.is_button_just_pressed(XboxButton.A):
                            self.settings[option_key] = not self.settings[option_key]
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                    elif option_type == 'slider':
                        if move_x < -0.5 and not getattr(self, '_settings_x_moved', False):
                            self.settings[option_key] = max(0, self.settings[option_key] - 10)
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                            self._settings_x_moved = True
                        elif move_x > 0.5 and not getattr(self, '_settings_x_moved', False):
                            self.settings[option_key] = min(100, self.settings[option_key] + 10)
                            self.play_sound('ammo_switch')
                            self._apply_settings()
                            self._settings_x_moved = True
                        elif abs(move_x) < 0.3:
                            self._settings_x_moved = False

                    if self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'paused'
                        self.play_sound('menu_select')
                elif self.state in ['leaderboard', 'credits', 'how_to_play']:
                    if self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'menu'
                        self.play_sound('menu_select')
            elif event.type == pygame.KEYDOWN:
                # Pass events to tutorial if active
                if self.tutorial.active:
                    self.tutorial.handle_input(event)

                # Handle splash screen input
                if self.state == 'splash':
                    self.splash_screen.handle_event(event)

                elif self.state == 'chapter_select':
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.chapter_index > 0:
                            self.chapter_index -= 1
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.chapter_index < len(self.chapter_options) - 1:
                            self.chapter_index += 1
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        chapter = self.chapter_options[self.chapter_index]
                        if chapter.get('unlocked', False):
                            self.selected_chapter = chapter
                            self.start_chapter_flow()
                            self.play_sound('menu_select')
                        else:
                            self.play_sound('menu_error')
                    elif event.key == pygame.K_1:
                        self.chapter_index = 0
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_2:
                        self.chapter_index = min(1, len(self.chapter_options) - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_3:
                        self.chapter_index = min(2, len(self.chapter_options) - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_4:
                        self.chapter_index = min(3, len(self.chapter_options) - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_5:
                        self.chapter_index = min(4, len(self.chapter_options) - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_o:
                        self.state = 'settings'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'  # Back to main menu
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                elif self.state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'difficulty'  # Difficulty first
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_t:
                        # Start tutorial
                        self.tutorial.start_tutorial()
                        self.state = 'difficulty'
                    elif event.key == pygame.K_o:
                        # Open settings
                        self.state = 'settings'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_l:
                        # Open leaderboard
                        self.state = 'leaderboard'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_c:
                        # Open credits
                        self.state = 'credits'
                        self.credits_scroll = 0
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                        # Quit game
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.music_manager.start_music(stage=self.current_stage)
                        else:
                            self.music_manager.stop_music()
                    elif event.key == pygame.K_s:
                        self.sound_enabled = not self.sound_enabled

                elif self.state == 'ship_select':
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.ship_select_index = (self.ship_select_index - 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.ship_select_index = (self.ship_select_index + 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        selected_key = self.ship_options[self.ship_select_index]
                        is_locked = selected_key in ['wolf', 'jaguar', 'crusader', 'malediction'] and not self.t2_ships_unlocked
                        if is_locked:
                            self.play_sound('menu_error')  # Can't select locked ship
                        else:
                            self.selected_ship = selected_key
                            self.start_game()  # Start game directly
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'difficulty'  # Back to difficulty selection
                        self.play_sound('menu_select')

                elif self.state == 'difficulty':
                    if event.key == pygame.K_1:
                        self.set_difficulty('easy')
                    elif event.key == pygame.K_2:
                        self.set_difficulty('normal')
                    elif event.key == pygame.K_3:
                        self.set_difficulty('hard')
                    elif event.key == pygame.K_4:
                        self.set_difficulty('nightmare')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'chapter_select'  # Back to chapter selection
                        self.play_sound('menu_select')

                elif self.state == 'empire_select':
                    # 2x2 grid: 1=Minmatar, 2=Amarr, 3=Caldari, 4=Gallente
                    if event.key == pygame.K_1:
                        self.empire_index = 0
                        self.set_empire(0)
                    elif event.key == pygame.K_2:
                        self.empire_index = 1
                        self.set_empire(1)
                    elif event.key == pygame.K_3:
                        self.empire_index = 2
                        self.set_empire(2)
                    elif event.key == pygame.K_4:
                        self.empire_index = 3
                        self.set_empire(3)
                    elif event.key == pygame.K_LEFT:
                        col = self.empire_index % 2
                        if col > 0:
                            self.empire_index -= 1
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_RIGHT:
                        col = self.empire_index % 2
                        if col < 1:
                            self.empire_index += 1
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_UP:
                        row = self.empire_index // 2
                        if row > 0:
                            self.empire_index -= 2
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_DOWN:
                        row = self.empire_index // 2
                        if row < 1:
                            self.empire_index += 2
                            self.play_sound('menu_select')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.set_empire(self.empire_index)
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'difficulty'  # Back to difficulty
                        self.play_sound('menu_select')

                elif self.state == 'faction_select':
                    if event.key == pygame.K_1:
                        self.set_faction('minmatar')
                    elif event.key == pygame.K_2:
                        self.set_faction('amarr')
                    elif event.key == pygame.K_LEFT:
                        self.faction_index = 0
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_RIGHT:
                        self.faction_index = 1
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.set_faction(self.faction_options[self.faction_index])
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'difficulty'  # Back to difficulty
                        self.play_sound('menu_select')

                elif self.state == 'filament_select':
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.selected_filament = (self.selected_filament - 1) % len(self.abyssal_filaments)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.selected_filament = (self.selected_filament + 1) % len(self.abyssal_filaments)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.selected_tier = max(0, self.selected_tier - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.selected_tier = min(len(self.abyssal_tiers) - 1, self.selected_tier + 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self._start_abyssal_run()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'mode_select'  # Back to mode selection
                        self.play_sound('menu_select')

                elif self.state == 'mode_select':
                    if event.key == pygame.K_1:
                        self.start_game('campaign')
                    elif event.key == pygame.K_2:
                        self.start_game('endless')
                    elif event.key == pygame.K_3:
                        self.start_game('boss_rush')
                    elif event.key == pygame.K_4:
                        # Abyssal mode goes to filament selection
                        self.state = 'filament_select'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'ship_select'  # Back to ship selection
                        self.play_sound('menu_select')

                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                        self.pause_menu_index = 0
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_f:
                        # Ship special ability
                        success, ability_name = self.player.use_ability()
                        if success:
                            self.play_sound('powerup')
                            self.show_message(ability_name, 60)
                            # Visual feedback
                            self.screen_flash_alpha = 40
                            self.screen_flash_color = (100, 200, 255)
                        else:
                            self.play_sound('error')
                    elif event.key == pygame.K_g:
                        # Screen-clearing bomb
                        self._use_bomb()
                    elif event.key == pygame.K_d:
                        # Toggle danger zone display
                        self.show_danger_zones = not self.show_danger_zones
                    elif event.key == pygame.K_q or event.key == pygame.K_TAB:
                        self.player.cycle_ammo()
                        self.play_sound('ammo_switch')
                        if self.tutorial.active:
                            self.tutorial.track_ammo_switch()
                    else:
                        # Check ammo hotkeys
                        for ammo_type, data in AMMO_TYPES.items():
                            if event.key == data['key']:
                                if self.player.switch_ammo(ammo_type):
                                    self.show_message(f"Ammo: {data['name']}", 60)
                                    if self.tutorial.active:
                                        self.tutorial.track_ammo_switch()
                                    self.play_sound('ammo_switch')
                                break
                
                elif self.state == 'paused':
                    self._handle_pause_input(event.key)
                
                elif self.state == 'shop':
                    self.handle_shop_input(event.key)
                
                elif self.state in ['gameover', 'victory']:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = 'menu'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_r:
                        # Quick restart with same mode
                        self.reset_game()
                        self.start_game(self.game_mode)
                        self.play_sound('menu_select')

                elif self.state == 'settings':
                    self._handle_settings_input(event.key)

                elif self.state == 'pause_settings':
                    self._handle_pause_settings_input(event.key)

                elif self.state == 'leaderboard':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        self.play_sound('menu_select')

                elif self.state == 'credits':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'

                elif self.state == 'how_to_play':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
                        self.play_sound('menu_select')

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle splash screen mouse click
                if self.state == 'splash':
                    self.splash_screen.handle_event(event)

        # Controller menu navigation (runs once per frame after all events processed)
        if self.controller and self.controller.connected:
            # Tutorial controller support
            if self.tutorial.active:
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.tutorial.skip_timer = 1
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.tutorial.tutorial_complete = True
                    self.tutorial.active = False

            # Splash screen - any button to continue
            if self.state == 'splash':
                if self.controller.is_button_just_pressed(XboxButton.A) or \
                   self.controller.is_button_just_pressed(XboxButton.B) or \
                   self.controller.is_button_just_pressed(XboxButton.START):
                    if self.splash_screen.timer > 40:
                        self.splash_screen.skip_requested = True

            if self.state == 'menu':
                move_x, move_y = self.controller.get_movement_vector()
                if move_y < -0.5 and not getattr(self, '_menu_controller_moved', False):
                    self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    self.play_sound('menu_select')
                    self._menu_controller_moved = True
                elif move_y > 0.5 and not getattr(self, '_menu_controller_moved', False):
                    self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    self.play_sound('menu_select')
                    self._menu_controller_moved = True
                elif abs(move_y) < 0.3:
                    self._menu_controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    option = self.menu_options[self.menu_index]
                    if option == 'start':
                        self.state = 'difficulty'
                    elif option == 'how_to_play':
                        self.state = 'how_to_play'
                        self.how_to_play_scroll = 0
                    elif option == 'settings':
                        self.state = 'settings'
                    elif option == 'leaderboard':
                        self.state = 'leaderboard'
                    elif option == 'credits':
                        self.state = 'credits'
                    elif option == 'quit':
                        pygame.quit()
                        sys.exit()
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.BACK):
                    self.state = 'settings'
                    self.play_sound('menu_select')

            elif self.state == 'ship_select':
                move_x, move_y = self.controller.get_movement_vector()
                if move_y < -0.5 and not getattr(self, '_controller_moved', False):
                    self.ship_select_index = (self.ship_select_index - 1) % len(self.ship_options)
                    self.play_sound('menu_select')
                    self._controller_moved = True
                elif move_y > 0.5 and not getattr(self, '_controller_moved', False):
                    self.ship_select_index = (self.ship_select_index + 1) % len(self.ship_options)
                    self.play_sound('menu_select')
                    self._controller_moved = True
                elif abs(move_y) < 0.3:
                    self._controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    selected_key = self.ship_options[self.ship_select_index]
                    is_locked = selected_key in ['wolf', 'jaguar', 'crusader', 'malediction'] and not self.t2_ships_unlocked
                    if is_locked:
                        self.play_sound('menu_error')
                    else:
                        self.selected_ship = selected_key
                        self.state = 'mode_select'
                        self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'faction_select'
                    self.play_sound('menu_select')

            elif self.state == 'empire_select':
                move_x, move_y = self.controller.get_movement_vector()
                if not getattr(self, '_empire_controller_moved', False):
                    # 2x2 grid navigation: left/right moves within row, up/down moves between rows
                    row = self.empire_index // 2
                    col = self.empire_index % 2
                    moved = False
                    if move_x < -0.5 and col > 0:
                        self.empire_index -= 1
                        moved = True
                    elif move_x > 0.5 and col < 1:
                        self.empire_index += 1
                        moved = True
                    elif move_y < -0.5 and row > 0:
                        self.empire_index -= 2
                        moved = True
                    elif move_y > 0.5 and row < 1:
                        self.empire_index += 2
                        moved = True
                    if moved:
                        self.play_sound('menu_select')
                        self._empire_controller_moved = True
                if abs(move_x) < 0.3 and abs(move_y) < 0.3:
                    self._empire_controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.set_empire(self.empire_index)
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'difficulty'
                    self.play_sound('menu_select')

            elif self.state == 'faction_select':
                move_x, move_y = self.controller.get_movement_vector()
                if not getattr(self, '_faction_controller_moved', False):
                    if move_x < -0.5:
                        self.faction_index = 0
                        self.play_sound('menu_select')
                        self._faction_controller_moved = True
                    elif move_x > 0.5:
                        self.faction_index = 1
                        self.play_sound('menu_select')
                        self._faction_controller_moved = True
                if abs(move_x) < 0.3:
                    self._faction_controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.set_faction(self.faction_options[self.faction_index])
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'empire_select'
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.LB):
                    self.faction_index = 0
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.RB):
                    self.faction_index = 1
                    self.play_sound('menu_select')

            elif self.state == 'difficulty':
                move_x, move_y = self.controller.get_movement_vector()
                moved = False
                if not getattr(self, '_diff_controller_moved', False):
                    if move_y < -0.5 and self.difficulty_index >= 2:
                        self.difficulty_index -= 2
                        self.play_sound('menu_select')
                        moved = True
                    elif move_y > 0.5 and self.difficulty_index < 2:
                        self.difficulty_index += 2
                        self.play_sound('menu_select')
                        moved = True
                    elif move_x < -0.5 and self.difficulty_index % 2 == 1:
                        self.difficulty_index -= 1
                        self.play_sound('menu_select')
                        moved = True
                    elif move_x > 0.5 and self.difficulty_index % 2 == 0:
                        self.difficulty_index += 1
                        self.play_sound('menu_select')
                        moved = True
                    if moved or abs(move_x) > 0.5 or abs(move_y) > 0.5:
                        self._diff_controller_moved = True
                if abs(move_x) < 0.3 and abs(move_y) < 0.3:
                    self._diff_controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.set_difficulty(self.difficulty_options[self.difficulty_index])
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'menu'
                    self.play_sound('menu_select')

            elif self.state == 'mode_select':
                move_x, move_y = self.controller.get_movement_vector()
                if move_y < -0.5 and not getattr(self, '_mode_controller_moved', False):
                    self.mode_index = (self.mode_index - 1) % len(self.mode_options)
                    self.play_sound('menu_select')
                    self._mode_controller_moved = True
                elif move_y > 0.5 and not getattr(self, '_mode_controller_moved', False):
                    self.mode_index = (self.mode_index + 1) % len(self.mode_options)
                    self.play_sound('menu_select')
                    self._mode_controller_moved = True
                elif abs(move_y) < 0.3:
                    self._mode_controller_moved = False
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.start_game(self.mode_options[self.mode_index])
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'ship_select'
                    self.play_sound('menu_select')

            elif self.state == 'playing':
                if self.controller.is_button_just_pressed(XboxButton.START):
                    self.state = 'paused'
                    self.pause_menu_index = 0
                    self.play_sound('menu_select')
                if self.controller.is_button_just_pressed(XboxButton.L_STICK):
                    self.hud_mode = (self.hud_mode + 1) % 3
                    hud_names = ['FULL', 'MINIMAL', 'OFF']
                    self.show_message(f"HUD: {hud_names[self.hud_mode]}", 60)
                    self.play_sound('menu_select')
                self._handle_dpad_input()

            elif self.state == 'paused':
                if self.controller.is_button_just_pressed(XboxButton.START):
                    self.state = 'playing'
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.A):
                    self._select_pause_option()
                elif self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'playing'
                    self.play_sound('menu_select')
                else:
                    move_x, move_y = self.controller.get_movement_vector()
                    if move_y < -0.5 and not getattr(self, '_pause_controller_moved', False):
                        self.pause_menu_index = (self.pause_menu_index - 1) % len(self.pause_menu_options)
                        self.play_sound('menu_select')
                        self._pause_controller_moved = True
                    elif move_y > 0.5 and not getattr(self, '_pause_controller_moved', False):
                        self.pause_menu_index = (self.pause_menu_index + 1) % len(self.pause_menu_options)
                        self.play_sound('menu_select')
                        self._pause_controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._pause_controller_moved = False

            elif self.state in ['gameover', 'victory']:
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.reset_game()
                    self.state = 'menu'
                    self.play_sound('menu_select')
                elif self.controller.is_button_just_pressed(XboxButton.X):
                    self.reset_game()
                    self.start_game(self.game_mode)
                    self.play_sound('menu_select')

            elif self.state == 'settings':
                move_x, move_y = self.controller.get_movement_vector()
                if move_y < -0.5 and not getattr(self, '_settings_controller_moved', False):
                    self.settings_index = (self.settings_index - 1) % len(self.settings_options)
                    self.play_sound('menu_select')
                    self._settings_controller_moved = True
                elif move_y > 0.5 and not getattr(self, '_settings_controller_moved', False):
                    self.settings_index = (self.settings_index + 1) % len(self.settings_options)
                    self.play_sound('menu_select')
                    self._settings_controller_moved = True
                elif abs(move_y) < 0.3:
                    self._settings_controller_moved = False
                option_key, _, option_type = self.settings_options[self.settings_index]
                if option_type == 'toggle':
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.settings[option_key] = not self.settings[option_key]
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                elif option_type == 'slider':
                    if move_x < -0.5 and not getattr(self, '_settings_x_moved', False):
                        self.settings[option_key] = max(0, self.settings[option_key] - 10)
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                        self._settings_x_moved = True
                    elif move_x > 0.5 and not getattr(self, '_settings_x_moved', False):
                        self.settings[option_key] = min(100, self.settings[option_key] + 10)
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                        self._settings_x_moved = True
                    elif abs(move_x) < 0.3:
                        self._settings_x_moved = False
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'menu'
                    self.play_sound('menu_select')

            elif self.state == 'pause_settings':
                move_x, move_y = self.controller.get_movement_vector()
                if move_y < -0.5 and not getattr(self, '_settings_controller_moved', False):
                    self.settings_index = (self.settings_index - 1) % len(self.settings_options)
                    self.play_sound('menu_select')
                    self._settings_controller_moved = True
                elif move_y > 0.5 and not getattr(self, '_settings_controller_moved', False):
                    self.settings_index = (self.settings_index + 1) % len(self.settings_options)
                    self.play_sound('menu_select')
                    self._settings_controller_moved = True
                elif abs(move_y) < 0.3:
                    self._settings_controller_moved = False
                option_key, _, option_type = self.settings_options[self.settings_index]
                if option_type == 'toggle':
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.settings[option_key] = not self.settings[option_key]
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                elif option_type == 'slider':
                    if move_x < -0.5 and not getattr(self, '_settings_x_moved', False):
                        self.settings[option_key] = max(0, self.settings[option_key] - 10)
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                        self._settings_x_moved = True
                    elif move_x > 0.5 and not getattr(self, '_settings_x_moved', False):
                        self.settings[option_key] = min(100, self.settings[option_key] + 10)
                        self.play_sound('ammo_switch')
                        self._apply_settings()
                        self._settings_x_moved = True
                    elif abs(move_x) < 0.3:
                        self._settings_x_moved = False
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'paused'
                    self.play_sound('menu_select')

            elif self.state in ['leaderboard', 'credits', 'how_to_play']:
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'menu'
                    self.play_sound('menu_select')

    def _handle_pause_input(self, key):
        """Handle pause menu navigation"""
        if key == pygame.K_ESCAPE:
            self.state = 'playing'
            self.play_sound('menu_select')
            return

        if key == pygame.K_UP or key == pygame.K_w:
            self.pause_menu_index = (self.pause_menu_index - 1) % len(self.pause_menu_options)
            self.play_sound('menu_select')
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.pause_menu_index = (self.pause_menu_index + 1) % len(self.pause_menu_options)
            self.play_sound('menu_select')
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self._select_pause_option()

    def _select_pause_option(self):
        """Execute the selected pause menu option"""
        option = self.pause_menu_options[self.pause_menu_index]
        self.play_sound('menu_select')

        if option == 'Resume':
            self.state = 'playing'
        elif option == 'Settings':
            self.state = 'pause_settings'
        elif option == 'Restart':
            self.reset_game()
            self.start_game(self.game_mode)
        elif option == 'Quit to Menu':
            self.state = 'menu'
            if self.music_enabled:
                self.music_manager.stop_music()

    def _handle_pause_settings_input(self, key):
        """Handle settings menu when accessed from pause"""
        if key == pygame.K_ESCAPE:
            self.state = 'paused'
            self.play_sound('menu_select')
            return

        if key == pygame.K_UP or key == pygame.K_w:
            self.settings_index = (self.settings_index - 1) % len(self.settings_options)
            self.play_sound('menu_select')
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.settings_index = (self.settings_index + 1) % len(self.settings_options)
            self.play_sound('menu_select')

        option_key, _, option_type = self.settings_options[self.settings_index]

        if option_type == 'toggle':
            # Screen shake has special preview on ENTER
            if option_key == 'screen_shake' and key == pygame.K_RETURN:
                self.shake.add(SHAKE_MEDIUM)
                self.play_sound('explosion')
                return
            if key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT,
                       pygame.K_a, pygame.K_d]:
                self.settings[option_key] = not self.settings[option_key]
                self.play_sound('ammo_switch')
                self._apply_settings()
        elif option_type == 'slider':
            if key in [pygame.K_LEFT, pygame.K_a]:
                self.settings[option_key] = max(0, self.settings[option_key] - 10)
                self.play_sound('ammo_switch')
                self._apply_settings()
            elif key in [pygame.K_RIGHT, pygame.K_d]:
                self.settings[option_key] = min(100, self.settings[option_key] + 10)
                self.play_sound('ammo_switch')
                self._apply_settings()

    def _handle_settings_input(self, key):
        """Handle settings menu navigation and changes"""
        if key == pygame.K_ESCAPE:
            # Return to pause menu if we came from there, otherwise main menu
            if hasattr(self, '_from_pause') and self._from_pause:
                self.state = 'paused'
                self._from_pause = False
            else:
                self.state = 'menu'
            self.play_sound('menu_select')
            return

        if key == pygame.K_UP or key == pygame.K_w:
            self.settings_index = (self.settings_index - 1) % len(self.settings_options)
            self.play_sound('menu_select')
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.settings_index = (self.settings_index + 1) % len(self.settings_options)
            self.play_sound('menu_select')

        option_key, _, option_type = self.settings_options[self.settings_index]

        if option_type == 'toggle':
            # Screen shake has special preview on ENTER
            if option_key == 'screen_shake' and key == pygame.K_RETURN:
                self.shake.add(SHAKE_MEDIUM)
                self.play_sound('explosion')
                return
            if key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_LEFT, pygame.K_RIGHT,
                       pygame.K_a, pygame.K_d]:
                self.settings[option_key] = not self.settings[option_key]
                self.play_sound('ammo_switch')
                self._apply_settings()
        elif option_type == 'slider':
            if key in [pygame.K_LEFT, pygame.K_a]:
                self.settings[option_key] = max(0, self.settings[option_key] - 10)
                self.play_sound('ammo_switch')
                self._apply_settings()
            elif key in [pygame.K_RIGHT, pygame.K_d]:
                self.settings[option_key] = min(100, self.settings[option_key] + 10)
                self.play_sound('ammo_switch')
                self._apply_settings()

    def _apply_settings(self):
        """Apply current settings"""
        # Apply volume settings
        master = self.settings['master_volume'] / 100
        sfx = self.settings['sfx_volume'] / 100
        self.sound_manager.set_volume(master * sfx)

        # Apply screen shake setting
        self.shake_enabled = self.settings['screen_shake']

        # Apply danger zones setting
        self.show_danger_zones = self.settings['show_danger_zones']

        # Save settings to file
        self._save_settings()

    def _load_settings(self):
        """Load settings from file"""
        settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    saved = json.load(f)
                    # Update settings with saved values
                    for key in self.settings:
                        if key in saved:
                            self.settings[key] = saved[key]
                    # Load endless high scores
                    self.endless_high_wave = saved.get('endless_high_wave', 0)
                    self.endless_high_score = saved.get('endless_high_score', 0)
                    # Load boss rush high scores
                    self.boss_rush_high_score = saved.get('boss_rush_high_score', 0)
                    self.boss_rush_best_time = saved.get('boss_rush_best_time', 0)
                    # Load T2 ship unlock status
                    self.t2_ships_unlocked = saved.get('t2_ships_unlocked', False)
                # Apply loaded settings
                self._apply_settings_no_save()
        except (json.JSONDecodeError, IOError):
            pass  # Use defaults if file is corrupted

    def _apply_settings_no_save(self):
        """Apply settings without saving (used during load)"""
        master = self.settings['master_volume'] / 100
        sfx = self.settings['sfx_volume'] / 100
        self.sound_manager.set_volume(master * sfx)
        self.shake_enabled = self.settings['screen_shake']
        self.show_danger_zones = self.settings['show_danger_zones']

    def _save_settings(self):
        """Save settings to file"""
        settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        try:
            save_data = dict(self.settings)
            save_data['endless_high_wave'] = self.endless_high_wave
            save_data['endless_high_score'] = self.endless_high_score
            save_data['boss_rush_high_score'] = self.boss_rush_high_score
            save_data['boss_rush_best_time'] = self.boss_rush_best_time
            save_data['t2_ships_unlocked'] = self.t2_ships_unlocked
            with open(settings_file, 'w') as f:
                json.dump(save_data, f, indent=2)
        except IOError:
            pass  # Silently fail if can't save

    def start_chapter_flow(self):
        """Start the appropriate flow for the selected chapter"""
        chapter = self.selected_chapter
        chapter_id = chapter['id']

        # Each chapter has its own flow
        if chapter_id == 'minmatar_rebellion':
            # Minmatar Rebellion: Difficulty → Empire Select → Faction → Ship → Mode → Play
            self.faction_options = ['minmatar', 'amarr']  # Reset to default
            self.state = 'difficulty'
        elif chapter_id == 'the_last_stand':
            # The Last Stand: Faction Select (Caldari vs Gallente) → Difficulty → Ship → Play
            # Set up faction options for this chapter
            self.faction_options = ['caldari', 'gallente']
            self.faction_index = 0
            self.state = 'faction_select'
        elif chapter_id == 'abyssal_depths':
            # Abyssal Depths: Filament Select → Ship → Play
            self.game_mode = 'abyssal'
            self.state = 'filament_select'
        elif chapter_id == 'sansha_incursion':
            # Sansha Incursion: Difficulty → Ship → Play
            self.enemy_faction = 'sansha'
            self.state = 'difficulty'
        elif chapter_id == 'elder_fleet':
            # Elder Fleet: Difficulty → Ship → Play
            self.enemy_faction = 'jove'
            self.state = 'difficulty'
        else:
            # Default: go to difficulty
            self.state = 'difficulty'

    def set_difficulty(self, difficulty):
        """Set game difficulty and continue chapter flow"""
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]

        # Determine next state based on current chapter
        chapter_id = self.selected_chapter.get('id', 'minmatar_rebellion')
        if chapter_id == 'minmatar_rebellion':
            self.state = 'empire_select'  # Empire selection for Minmatar
        elif chapter_id == 'the_last_stand':
            self.state = 'ship_select'  # Ship selection for Last Stand
        else:
            self.state = 'ship_select'  # Default to ship selection
        self.play_sound('menu_select')

    def set_empire(self, empire_index):
        """Set player faction and configure campaign based on selection"""
        self.selected_empire = self.empire_options[empire_index]
        self.empire_index = empire_index

        # Get player and enemy faction from selection
        player_faction = self.selected_empire.get('player_faction', 'minmatar')
        enemy_faction = self.selected_empire.get('enemy_faction', 'amarr')

        # Set player faction
        self.selected_faction = player_faction
        self.enemy_faction = enemy_faction

        # Load appropriate campaign stages
        if player_faction == 'minmatar':
            self.active_stages = STAGES_MINMATAR
        elif player_faction == 'amarr':
            self.active_stages = STAGES_AMARR
        elif player_faction == 'caldari':
            self.active_stages = STAGES_CALDARI
        elif player_faction == 'gallente':
            self.active_stages = STAGES_GALLENTE
        else:
            self.active_stages = STAGES_MINMATAR

        # Load ships for selected faction
        chapter_id = self.selected_chapter.get('id', 'minmatar_rebellion')
        self.ship_options = self.ship_roster.get_ship_options(player_faction, chapter_id)
        if not self.ship_options:
            # Fallback to hardcoded options
            if player_faction == 'minmatar':
                self.ship_options = ['rifter', 'breacher', 'wolf', 'jaguar']
            elif player_faction == 'amarr':
                self.ship_options = ['executioner', 'crusader', 'malediction']
            elif player_faction == 'caldari':
                self.ship_options = ['kestrel', 'hawk', 'harpy']
            elif player_faction == 'gallente':
                self.ship_options = ['tristan', 'enyo', 'ishkur']
            else:
                self.ship_options = ['rifter']

        self.selected_ship = self.ship_options[0]
        self.ship_select_index = 0

        # Set enemy faction for background carrier images
        if hasattr(self, 'stage_background'):
            self.stage_background.set_enemy_faction(enemy_faction)

        # Skip faction_select, go directly to ship_select
        self.state = 'ship_select'
        self.play_sound('menu_select')

    def set_faction(self, faction):
        """Set player faction and load appropriate campaign stages"""
        self.selected_faction = faction
        FACTIONS.get(faction, {})

        # Get chapter for ship filtering
        chapter_id = self.selected_chapter.get('id', 'minmatar_rebellion')

        # Load faction-specific campaign stages and ships from roster
        if faction == 'minmatar':
            self.active_stages = STAGES_MINMATAR
            # Use selected empire's enemy faction
            enemy_faction = self.selected_empire.get('enemy_faction', 'amarr')
        elif faction == 'caldari':
            self.active_stages = STAGES_CALDARI
            enemy_faction = 'gallente'
        elif faction == 'gallente':
            self.active_stages = STAGES_GALLENTE
            enemy_faction = 'caldari'
        else:
            self.active_stages = STAGES_AMARR
            enemy_faction = 'minmatar'

        # Load ships from roster based on faction and chapter
        self.ship_options = self.ship_roster.get_ship_options(faction, chapter_id)
        if not self.ship_options:
            # Fallback to hardcoded options
            if faction == 'minmatar':
                self.ship_options = ['rifter', 'breacher', 'wolf', 'jaguar']
            elif faction == 'amarr':
                self.ship_options = ['executioner', 'crusader', 'malediction']
            elif faction == 'caldari':
                self.ship_options = ['kestrel', 'hawk', 'harpy']
            elif faction == 'gallente':
                self.ship_options = ['tristan', 'enyo', 'ishkur']
            else:
                self.ship_options = ['rifter']

        # Store enemy faction for use in gameplay
        self.enemy_faction = enemy_faction

        # Set enemy faction for background carrier images
        if hasattr(self, 'stage_background'):
            self.stage_background.set_enemy_faction(enemy_faction)

        # Set default ship for this faction
        self.selected_ship = self.ship_options[0]
        self.ship_select_index = 0

        self.state = 'ship_select'
        self.play_sound('menu_select')

    def start_game(self, mode='campaign'):
        """Start the game with selected mode"""
        self.game_mode = mode
        self.reset_game()

        if mode == 'endless':
            self.endless_wave = 0
            self.endless_time = 0
            self.show_message("ENDLESS MODE - Survive!", 180)
        elif mode == 'boss_rush':
            self.boss_rush_index = 0
            self.boss_rush_time = 0
            self.show_message("BOSS RUSH - Defeat all bosses!", 180)
            # Spawn first boss immediately
            self._spawn_boss_rush_boss()
        elif mode == 'abyssal':
            self.abyssal_room = 1
            self.abyssal_timer = 60 * 60 * 20  # 20 minutes in frames
            filament = self.abyssal_filaments[self.abyssal_filament_index]
            tier = self.abyssal_tiers[self.abyssal_tier_index]
            self.show_message(f"ABYSSAL DEPTHS - {filament['name']} {tier['name']}", 180,
                            subtitle="Clear 3 rooms to extract")
            # Apply filament modifiers to player would go here
        else:
            stage = self.active_stages[0]
            self.show_message(stage['name'], 180, subtitle=stage.get('story'))

        self.state = 'playing'
        self.play_sound('wave_start')
        if self.music_enabled:
            self.music_manager.start_music(stage=self.current_stage)

    def _spawn_boss_rush_boss(self):
        """Spawn the next boss in boss rush mode"""
        if self.boss_rush_index >= len(self.boss_rush_bosses):
            return

        boss_type = self.boss_rush_bosses[self.boss_rush_index]
        boss_name = ENEMY_STATS.get(boss_type, {}).get('name', boss_type.title())

        # Spawn boss at top center
        x = SCREEN_WIDTH // 2
        y = -100

        boss = Enemy(boss_type, x, y, self.difficulty_settings)
        self.enemies.add(boss)
        self.all_sprites.add(boss)

        self.show_message(f"BOSS {self.boss_rush_index + 1}/{len(self.boss_rush_bosses)}: {boss_name}", 120)
        self.play_sound('boss_intro', 0.8)
        self.shake.add(SHAKE_MEDIUM)

    def _update_boss_rush(self):
        """Handle boss rush mode progression"""
        # Track time
        self.boss_rush_time += 1

        # Check if current boss is defeated
        if len(self.enemies) == 0:
            self.boss_rush_index += 1

            # Check if all bosses defeated
            if self.boss_rush_index >= len(self.boss_rush_bosses):
                # Victory!
                self._boss_rush_victory()
                return

            # Small delay then spawn next boss
            self.wave_delay = 120
            self.show_message("BOSS DEFEATED! Next boss incoming...", 90)

        # Spawn next boss after delay
        if self.wave_delay > 0:
            self.wave_delay -= 1
            if self.wave_delay == 0 and len(self.enemies) == 0 and self.boss_rush_index < len(self.boss_rush_bosses):
                self._spawn_boss_rush_boss()

    def _boss_rush_victory(self):
        """Handle boss rush mode completion"""
        final_score = self.player.score
        final_time = self.boss_rush_time // 60  # Convert to seconds

        # Update best scores
        if final_score > self.boss_rush_high_score:
            self.boss_rush_high_score = final_score
        if self.boss_rush_best_time == 0 or final_time < self.boss_rush_best_time:
            self.boss_rush_best_time = final_time

        self.state = 'victory'
        self.show_message(f"BOSS RUSH COMPLETE! Time: {final_time}s", 180)
        self.play_sound('victory')
        self._save_settings()

    def _start_abyssal_run(self):
        """Start an Abyssal Depths run with selected filament and tier."""
        filament = self.abyssal_filaments[self.selected_filament]
        tier = self.abyssal_tiers[self.selected_tier]

        # Initialize the Abyssal mode with selected settings
        self.abyssal.start_run(filament['id'], tier['tier'])

        # Apply filament modifiers to player
        if 'player_bonus' in filament:
            bonus = filament['player_bonus']
            if 'damage_mult' in bonus:
                self.player.damage_mult = bonus['damage_mult']
            if 'speed_mult' in bonus:
                self.player.speed_mult = bonus.get('speed_mult', 1.0)

        # Apply filament penalties
        if 'player_penalty' in filament:
            penalty = filament['player_penalty']
            if 'resist_mult' in penalty:
                self.player.resist_mult = penalty.get('resist_mult', 1.0)

        # Set up game state for abyssal mode
        self.abyssal_room = 1
        self.abyssal_timer = tier.get('timer_frames', 60 * 60 * 20)  # Default 20 min at 60fps

        # Clear existing enemies and bullets
        self.enemies.empty()
        self.bullets.empty()
        self.enemy_bullets.empty()
        self.collectibles.empty()

        self.show_message("ENTERING THE ABYSS", 180,
                         subtitle=f"{filament['name']} - Tier {tier['tier']}")

        self.state = 'playing'
        self.play_sound('wave_start')
        if self.music_enabled:
            self.music_manager.start_music(stage='abyssal')

    def _update_abyssal(self):
        """Update Abyssal Depths mode each frame."""
        if not self.abyssal.state:
            return

        dt = 1.0 / 60.0  # Delta time in seconds
        player_x = self.player.rect.centerx
        player_y = self.player.rect.centery

        # Handle extraction channeling (A button or E key when in range of gate)
        if self.abyssal.extraction_gate and self.abyssal.extraction_gate.active:
            in_range = self.abyssal.extraction_gate.is_in_range(player_x, player_y)
            if in_range:
                # Check for channel input (keyboard E or controller A held)
                keys = pygame.key.get_pressed()
                controller_channel = False
                if self.controller and self.controller.is_connected():
                    controller_channel = self.controller.is_button_pressed(XboxButton.A)

                if keys[pygame.K_e] or controller_channel:
                    self.abyssal.start_extraction_channel()
                else:
                    self.abyssal.stop_extraction_channel()
            else:
                self.abyssal.stop_extraction_channel()

        # Update abyssal state and get events
        events = self.abyssal.update(dt, player_x, player_y)

        # Handle events
        if events.get('spawn_enemy'):
            trig_enemy = self.abyssal.spawn_enemy()
            if trig_enemy:
                # Create a game Enemy from Triglavian config
                enemy = Enemy(
                    'damavik',  # Use damavik as base sprite
                    int(trig_enemy.x),
                    int(trig_enemy.y),
                    self.difficulty_settings
                )
                # Override stats with Triglavian stats
                enemy.hp = trig_enemy.hp
                enemy.max_hp = trig_enemy.max_hp
                enemy.speed = trig_enemy.speed / 60.0  # Convert to pixels per frame
                enemy.trig_enemy = trig_enemy  # Store reference for damage ramping
                self.enemies.add(enemy)

        if events.get('hazard_damage'):
            damage = events['hazard_damage']
            self.player.take_damage(damage)
            self.play_sound('hit')

        if events.get('time_out'):
            # Player ran out of time - death in the abyss
            self.player.hp = 0
            self.show_message("TIME EXPIRED", 180, subtitle="Lost in the Abyss...")
            self.state = 'game_over'
            self.play_sound('explosion')
            self._save_settings()

        if events.get('extracted'):
            # Successful extraction!
            self.show_message("EXTRACTION COMPLETE!", 180,
                            subtitle=f"Loot: {self.abyssal.state.total_loot}")
            self.state = 'victory'
            self.play_sound('victory')
            self._save_settings()

        if events.get('room_transition'):
            room = events['room_transition']
            room_names = ['POCKETS', 'ESCALATION', 'EXTRACTION']
            self.show_message(f"ROOM {room}", 120, subtitle=room_names[room - 1])
            self.play_sound('wave_start')
            # Clear bullets for new room
            self.bullets.empty()
            self.enemy_bullets.empty()

    def handle_shop_input(self, key):
        """Handle shop menu input"""
        costs = UPGRADE_COSTS
        player = self.player
        
        purchased = None
        
        if key == pygame.K_1 and not player.has_gyro:
            if player.refugees >= costs['gyrostabilizer']:
                player.refugees -= costs['gyrostabilizer']
                player.has_gyro = True
                player.fire_rate_mult *= 1.3
                purchased = "Gyrostabilizer"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_2:
            if player.refugees >= costs['armor_plate']:
                player.refugees -= costs['armor_plate']
                player.max_armor += 30
                player.armor = min(player.armor + 30, player.max_armor)
                purchased = "Armor Plate"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_3 and not player.has_tracking:
            if player.refugees >= costs['tracking_enhancer']:
                player.refugees -= costs['tracking_enhancer']
                player.has_tracking = True
                player.spread_bonus += 1
                purchased = "Tracking Enhancer"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_4 and 'emp' not in player.unlocked_ammo:
            if player.refugees >= costs['emp_ammo']:
                player.refugees -= costs['emp_ammo']
                player.unlock_ammo('emp')
                purchased = "EMP Ammo"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_5 and 'plasma' not in player.unlocked_ammo:
            if player.refugees >= costs['plasma_ammo']:
                player.refugees -= costs['plasma_ammo']
                player.unlock_ammo('plasma')
                purchased = "Phased Plasma Ammo"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_6 and 'fusion' not in player.unlocked_ammo:
            if player.refugees >= costs['fusion_ammo']:
                player.refugees -= costs['fusion_ammo']
                player.unlock_ammo('fusion')
                purchased = "Fusion Ammo"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_7 and 'barrage' not in player.unlocked_ammo:
            if player.refugees >= costs['barrage_ammo']:
                player.refugees -= costs['barrage_ammo']
                player.unlock_ammo('barrage')
                purchased = "Barrage Ammo"
            else:
                self.play_sound('error')
        
        elif key == pygame.K_8 and not player.is_wolf:
            if player.refugees >= costs['wolf_upgrade']:
                player.refugees -= costs['wolf_upgrade']
                player.upgrade_to_wolf()
                purchased = "WOLF UPGRADE!"
                self.play_sound('upgrade')
            else:
                self.play_sound('error')

        elif key == pygame.K_9 and not player.is_wolf:
            if player.refugees >= costs['jaguar_upgrade']:
                player.refugees -= costs['jaguar_upgrade']
                player.upgrade_to_jaguar()
                purchased = "JAGUAR UPGRADE!"
                self.play_sound('upgrade')
            else:
                self.play_sound('error')

        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Continue to next stage
            self.current_stage += 1
            if self.current_stage >= len(self.active_stages):
                self.state = 'victory'
                self.play_sound('victory', 0.8)
                self._record_game_end(victory=True)
                # Unlock T2 ships on first campaign completion!
                if not self.t2_ships_unlocked:
                    self.t2_ships_unlocked = True
                    self._save_settings()
                    self.show_message("T2 ASSAULT FRIGATES UNLOCKED!", 300)
            else:
                self.current_wave = 0
                self.wave_delay = 60
                self.stage_complete = False
                # Set up hazards for new stage
                self.hazards.clear()
                self.hazards.set_stage_hazards(self.current_stage)
                # Transition background to new stage environment
                if hasattr(self, 'stage_background'):
                    self.stage_background.transition_to_stage(self.current_stage + 1)
                self.state = 'playing'
                # Reset wave progression trackers for new stage
                self._bc_spawned_this_stage = False
                self._cruiser_count = 0
                self._destroyer_wing_timer = 0
                stage = self.active_stages[self.current_stage]
                self.show_message(stage['name'], 180, subtitle=stage.get('story'))
                self.play_sound('wave_start')
                # Change music theme for new stage
                if self.music_enabled:
                    self.music_manager.change_stage(self.current_stage)
        
        if purchased:
            self.show_message(f"Purchased: {purchased}", 90)
            if purchased != "WOLF UPGRADE!":  # Wolf has its own sound
                self.play_sound('purchase')
    
    def update(self):
        # Update scrolling background
        if hasattr(self, "space_background"):
            self.space_background.update(2.0)
        if hasattr(self, "archon_carrier"):
            self.archon_carrier.update()

        # Update stage-based parallax background with player movement
        if hasattr(self, 'stage_background'):
            player_dx = getattr(self, 'player_dx', 0)
            self.stage_background.update(scroll_speed=1.5, player_dx=player_dx)
            self.player_dx = 0  # Reset for next frame

        """Update game state"""
        # Handle splash screen
        if self.state == 'splash':
            self.splash_screen.update()
            if self.splash_screen.done:
                self.state = 'chapter_select'
            return

        # Always update parallax and stars for visual movement
        for star in self.stars:
            star.update()
        self.parallax.update()

        # Controller update - MUST happen before early return so menus work!
        dt = self.clock.get_time() / 1000.0
        if self.controller:
            self.controller.update(dt)

        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()

        # Track overheat state for powerup expiration feedback
        was_overheated = getattr(self, '_was_overheated', False)

        # Track player position for parallax effect
        player_x_before = self.player.rect.x

        # Update player
        self.player.update(keys)
        self.player.update_ability_cooldown()

        # Calculate horizontal movement for background parallax
        self.player_dx = self.player.rect.x - player_x_before

        # Update Jaguar shield deflector timers
        if hasattr(self.player, 'update_frontal_shield'):
            self.player.update_frontal_shield()

        # Update Wolf armor regen
        if hasattr(self.player, 'update_armor_regen'):
            self.player.update_armor_regen()

        # Check if player just overheated - show powerup loss message
        if self.player.is_overheated and not was_overheated:
            self.show_message("OVERHEATED! Powerups Lost!", 90)
            self.play_sound('error')
            self.screen_flash_alpha = 60
            self.screen_flash_color = (255, 100, 50)
        self._was_overheated = self.player.is_overheated

        # Update combat maneuvers (barrel roll, emergency brake)
        self._update_maneuvers()

        # Engine exhaust particles when moving
        is_moving = (keys[pygame.K_w] or keys[pygame.K_UP] or keys[pygame.K_s] or keys[pygame.K_DOWN] or
                     keys[pygame.K_a] or keys[pygame.K_LEFT] or keys[pygame.K_d] or keys[pygame.K_RIGHT])
        if is_moving and random.random() < 0.3:
            exhaust_x = self.player.rect.centerx + random.randint(-5, 5)
            exhaust_y = self.player.rect.bottom - 5
            self.particle_emitter.emit_engine_exhaust(exhaust_x, exhaust_y, COLOR_MINMATAR_ACCENT)

        # Update player ship damage visual effects (smoke, sparks, fire)
        if hasattr(self, 'player_damage_effects'):
            shield_pct = self.player.shields / max(self.player.max_shields, 1)
            armor_pct = self.player.armor / max(self.player.max_armor, 1)
            hull_pct = self.player.hull / max(self.player.max_hull, 1)
            self.player_damage_effects.update(
                self.player.rect.centerx, self.player.rect.centery,
                self.player.rect.width, self.player.rect.height,
                shield_pct, armor_pct, hull_pct
            )

        # Track movement for tutorial
        if self.tutorial.active:
            if keys[pygame.K_w] or keys[pygame.K_a] or keys[pygame.K_s] or keys[pygame.K_d] or \
               keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.tutorial.track_move()

        # Add controller movement on top of keyboard (analog)
        if self.controller and self.controller.connected:
            move_x, move_y = self.controller.get_movement_vector()
            self.player.rect.x += move_x * self.player.speed
            self.player.rect.y += move_y * self.player.speed
            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            if self.tutorial.active and (abs(move_x) > 0.1 or abs(move_y) > 0.1):
                self.tutorial.track_move()
        # Player input via unified InputState
        input_state = None

        if self.controller and self.controller.connected:
            input_state = self.controller.get_input_state()

            # R3 = Toggle fire mode (Spread/Focus)
            if input_state.toggle_fire_mode_pressed:
                new_mode = self.player.toggle_fire_mode()
                self.play_sound('ammo_switch')
                self.show_message(f"FIRE: {new_mode.upper()}", 45)

            # LT = Brake (emergency escape with invincibility)
            if input_state.brake_pressed:
                self._emergency_brake()

            # LB/RB = Thrust (uses movement direction)
            if input_state.thrust_held and not self.player.thrust_active:
                self._thrust_with_movement()

        # Disable weapons during brake animation
        brake_active = getattr(self.player, 'emergency_brake_active', False)

        # Determine fire state from InputState or keyboard/mouse
        if input_state:
            controller_fire = input_state.fire_held
            aim_x, aim_y = input_state.aim_x, input_state.aim_y
        else:
            controller_fire = False
            aim_x, aim_y = 0.0, -1.0  # Default forward

        # Store aim direction for wingmen to use
        self._player_aim_direction = (aim_x, aim_y)

        # Keyboard/mouse fire (always Standard behavior)
        kb_mouse_fire = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]

        if (kb_mouse_fire or controller_fire) and not brake_active:
            ship_class = getattr(self.player, 'ship_class', 'Rifter')

            # Jaguar: Seeking rocket streams as main weapon
            if ship_class == 'Jaguar':
                # Update rocket stream cooldown
                if hasattr(self.player, 'rocket_stream_cooldown') and self.player.rocket_stream_cooldown > 0:
                    self.player.rocket_stream_cooldown -= 1

                # Always pass aim direction (right stick with persistence)
                projectiles = self.player.shoot(aim_direction=(aim_x, aim_y))
                if projectiles:
                    self.play_sound('rocket', 0.15)  # Quieter for streams
                    if self.tutorial.active:
                        self.tutorial.track_shot()
                    for rocket in projectiles:
                        # Set targets for seeking
                        if hasattr(rocket, 'set_targets'):
                            rocket.set_targets(self.enemies)
                        # Smaller muzzle flash for stream rockets
                        self.particle_emitter.emit_sparks(
                            rocket.rect.centerx, rocket.rect.top + 5,
                            (100, 180, 255), 2)
                        self.player_bullets.add(rocket)
                        self.all_sprites.add(rocket)
            else:
                # Other ships: Normal autocannon fire with 360° aim
                bullets = self.player.shoot(aim_direction=(aim_x, aim_y))
                if bullets:
                    self.play_sound('autocannon', 0.3)
                    if self.tutorial.active:
                        self.tutorial.track_shot()
                    ammo = AMMO_TYPES.get(self.player.current_ammo, {})
                    flash_color = ammo.get('tracer', (255, 200, 100))
                    for bullet in bullets:
                        self.particle_emitter.emit_sparks(
                            bullet.rect.centerx, bullet.rect.top + 5,
                            flash_color, 2)
                for bullet in bullets:
                    self.player_bullets.add(bullet)
                    self.all_sprites.add(bullet)

        # Store current input state for HUD reticle drawing
        self._current_input_state = input_state
        self._manual_aim_active = input_state is not None

        # Special Abilities (keyboard/mouse only - LT is brake on controller)
        kb_special = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2]
        if kb_special:
            ship_class = getattr(self.player, 'ship_class', 'Rifter')

            # Jaguar: LT activates SHIELD BUBBLE (7s immunity, 20s cooldown)
            if ship_class == 'Jaguar':
                if self.player.can_frontal_shield():
                    if self.player.activate_frontal_shield():
                        self.play_sound('shield_boost', 0.8)
                        self.show_message("SHIELD BUBBLE ACTIVE!", 60)
                        # Visual burst effect
                        self.particle_emitter.emit_explosion(
                            self.player.rect.centerx, self.player.rect.centery,
                            (80, 180, 255), 40, 12, 8)

            # Wolf: LT fires UNLIMITED DUAL SEEKING ROCKETS
            elif ship_class == 'Wolf':
                # Wolf has unlimited seeking rockets on LT - no ammo cost
                wolf_rocket_cooldown = getattr(self.player, 'wolf_rocket_cooldown', 0)
                if wolf_rocket_cooldown <= 0:
                    # Fire dual seeking rockets
                    from sprites import Rocket
                    for offset in [-12, 12]:
                        rocket = Rocket(
                            self.player.rect.centerx + offset,
                            self.player.rect.top,
                            seeking=True
                        )
                        rocket.damage = int(ROCKET_DAMAGE * 0.6 * self.player.get_damage_bonus())
                        rocket.turn_rate = 0.25
                        rocket.set_targets(self.enemies)
                        self.particle_emitter.emit_explosion(
                            rocket.rect.centerx, rocket.rect.top + 5,
                            (255, 150, 50), 6, 3, 3)
                        self.player_bullets.add(rocket)
                        self.all_sprites.add(rocket)
                    self.play_sound('rocket', 0.4)
                    self.player.wolf_rocket_cooldown = 12  # Fast fire rate

            else:
                # Rifter: Fire rockets normally (uses ammo)
                result = self.player.shoot_rocket()
                if result:
                    self.play_sound('rocket', 0.5)
                    rockets = result if isinstance(result, list) else [result]
                    for rocket in rockets:
                        if hasattr(rocket, 'seeking') and rocket.seeking:
                            rocket.set_targets(self.enemies)
                        self.particle_emitter.emit_explosion(
                            rocket.rect.centerx, rocket.rect.top + 5,
                            (255, 150, 50), 6, 3, 3)
                        self.player_bullets.add(rocket)
                        self.all_sprites.add(rocket)
                    if self.tutorial.active:
                        self.tutorial.track_rocket()

        # Decrement Wolf rocket cooldown
        if hasattr(self.player, 'wolf_rocket_cooldown') and self.player.wolf_rocket_cooldown > 0:
            self.player.wolf_rocket_cooldown -= 1

        # Decrement fire pattern toggle cooldown
        if hasattr(self, '_fire_pattern_cooldown') and self._fire_pattern_cooldown > 0:
            self._fire_pattern_cooldown -= 1

        # Update sprites
        self.player_bullets.update()
        self.enemy_bullets.update()
        
        # Update enemies with player position for AI
        for enemy in self.enemies:
            enemy.update(self.player.rect)

            # Update enemy damage visual effects
            enemy_id = id(enemy)
            enemy_effects = get_ship_damage_effects(enemy_id)
            shield_pct = getattr(enemy, 'shields', 0) / max(getattr(enemy, 'max_shields', 1), 1)
            armor_pct = getattr(enemy, 'armor', 0) / max(getattr(enemy, 'max_armor', 1), 1)
            hull_pct = getattr(enemy, 'hull', 100) / max(getattr(enemy, 'max_hull', 100), 1)
            enemy_effects.update(
                enemy.rect.centerx, enemy.rect.centery,
                enemy.rect.width, enemy.rect.height,
                shield_pct, armor_pct, hull_pct
            )

        # Update wingmen and have them shoot
        # Pass player's aim direction so wingmen track with player's fire
        player_aim = getattr(self, '_player_aim_direction', (0, -1))
        for wingman in self.wingmen:
            wingman.update()
            bullet = wingman.shoot(aim_direction=player_aim)
            if bullet:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)

        self.pods.update()
        self.powerups.update()

        # Magnet powerup - attract pods and powerups toward player
        if self.player.has_magnet():
            magnet_strength = 5  # Pixels per frame
            for pod in self.pods:
                dx = self.player.rect.centerx - pod.rect.centerx
                dy = self.player.rect.centery - pod.rect.centery
                dist = max(1, (dx**2 + dy**2)**0.5)
                pod.rect.x += int(dx / dist * magnet_strength)
                pod.rect.y += int(dy / dist * magnet_strength)
            for powerup in self.powerups:
                dx = self.player.rect.centerx - powerup.rect.centerx
                dy = self.player.rect.centery - powerup.rect.centery
                dist = max(1, (dx**2 + dy**2)**0.5)
                powerup.rect.x += int(dx / dist * magnet_strength)
                powerup.rect.y += int(dy / dist * magnet_strength)

        self.effects.update()
        self.particles.update()
        self.damage_numbers.update()
        self.screen_effects.update()

        # Update enhanced explosions
        if hasattr(self, 'enhanced_explosions'):
            self.enhanced_explosions = [e for e in self.enhanced_explosions if e.update()]

        # Update shield impact effects
        if hasattr(self, 'shield_impacts'):
            self.shield_impacts.update()

        # Update muzzle flash effects
        if hasattr(self, 'muzzle_flashes'):
            self.muzzle_flashes.update()

        # Update screen shake
        if hasattr(self, 'screen_shake'):
            self.screen_shake.update()

        # Update visual effects
        self.warp_transition.update()
        self.hit_markers.update()
        self.combo_effects.update()

        # Update screen shake
        self.shake.update()

        # Update berserk system (for popups)
        self.berserk.update()

        # Update environmental hazards
        self.hazards.update(self.player.rect)

        # Apply hazard effects to player
        self._apply_hazard_effects()

        # Decay screen flash
        if self.screen_flash_alpha > 0:
            self.screen_flash_alpha = max(0, self.screen_flash_alpha - 8)

        # Update tutorial
        if self.tutorial.active:
            self.tutorial.update()

        # Low health warning
        total_health = self.player.shields + self.player.armor + self.player.hull
        max_health = self.player.max_shields + self.player.max_armor + self.player.max_hull
        health_pct = total_health / max_health if max_health > 0 else 0

        if health_pct < 0.25:
            self.low_health_timer += 1
            if self.low_health_timer >= self.low_health_interval:
                self.play_sound('low_health', 0.5)
                self.low_health_timer = 0
        else:
            self.low_health_timer = 0

        # Shield down warning (plays once when shields deplete)
        if self.player.shields <= 0 and hasattr(self, '_shields_were_up') and self._shields_were_up:
            self.play_sound('shield_down', 0.6)
        self._shields_were_up = self.player.shields > 0

        # Enemy shooting
        for enemy in self.enemies:
            bullets = enemy.shoot(self.player.rect)
            if bullets:
                self.play_sound('laser', 0.2)
            for bullet in bullets:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)

            # Boss special attacks
            if enemy.is_boss:
                special_bullets, attack_type = enemy.get_boss_special_attack(self.player.rect)
                if special_bullets:
                    self.play_sound('boss_attack', 0.7)
                    self.shake.add(SHAKE_MEDIUM)
                    self.screen_flash_alpha = 60
                    self.screen_flash_color = (255, 200, 100)
                    for bullet in special_bullets:
                        self.enemy_bullets.add(bullet)
                        self.all_sprites.add(bullet)
                elif attack_type == 'summon':
                    # Spawn minions
                    self._boss_summon_minions(enemy)
                    enemy.summon_count += 1
                    enemy.boss_special_cooldown = 180
                elif attack_type == 'drone_stream':
                    # Drone stream announced
                    self.show_message("DRONE SWARM INCOMING!", 60)
                    self.play_sound('warning', 0.6)
                    self.shake.add(SHAKE_SMALL)

                # Spawn queued drones from boss (staggered over frames)
                drone_pos = enemy.get_drone_spawn()
                if drone_pos:
                    drone = Enemy('drone', drone_pos[0], drone_pos[1], self.difficulty_settings)
                    self.enemies.add(drone)
                    self.all_sprites.add(drone)

                # Check for enrage trigger (20% health)
                if hasattr(enemy, 'is_enraged') and enemy.is_enraged:
                    # Show enrage message only once
                    if not hasattr(enemy, '_enrage_announced'):
                        enemy._enrage_announced = True
                        self.show_message("BOSS ENRAGED! 20% HEALTH!", 120)
                        self.play_sound('warning', 0.8)
                        self.shake.add(SHAKE_LARGE)
                        self.screen_flash_alpha = 150
                        self.screen_flash_color = (255, 0, 0)

                # Visual indicator for enraged boss
                if hasattr(enemy, 'is_enraged') and enemy.is_enraged:
                    # Red glow effect on enraged boss
                    if random.random() < 0.1:
                        self.particle_emitter.emit_sparks(
                            enemy.rect.centerx + random.randint(-30, 30),
                            enemy.rect.centery + random.randint(-20, 20),
                            (255, 50, 50), 3)
        
        # Check collisions - player bullets vs enemies
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                # Emit hit sparks at bullet impact point
                self.particle_emitter.emit_sparks(
                    bullet.rect.centerx, bullet.rect.centery,
                    bullet.color if hasattr(bullet, 'color') else (255, 200, 100), 4)

                # Hit marker
                self.hit_markers.add(bullet.rect.centerx, bullet.rect.centery)

                # Spawn damage number if enabled
                if self.settings.get('show_damage_numbers', True):
                    dmg = getattr(bullet, 'damage', 10)
                    dmg_color = bullet.color if hasattr(bullet, 'color') else (255, 255, 255)
                    self.damage_numbers.spawn(
                        enemy.rect.centerx, enemy.rect.top - 5,
                        dmg, dmg_color)

                bullet.kill()
                if enemy.take_damage(bullet):
                    # Enemy destroyed - use berserk scoring with heat bonus
                    heat_percent = self.player.heat / self.player.max_heat if self.player.max_heat > 0 else 0
                    berserk_score = self.berserk.register_kill(
                        enemy.score,
                        (self.player.rect.centerx, self.player.rect.centery),
                        (enemy.rect.centerx, enemy.rect.centery),
                        enemy.enemy_type,
                        heat_percent
                    )
                    self.player.score += berserk_score

                    # Screen flash and sound for berserk kills
                    if self.berserk.current_range == 'EXTREME':
                        self.screen_flash_alpha = 100
                        self.screen_flash_color = (255, 50, 50)
                        self.play_sound('berserk_extreme', 0.6)
                        self.particle_emitter.emit_berserk_aura(
                            self.player.rect.centerx, self.player.rect.centery, 'extreme')
                    elif self.berserk.current_range == 'CLOSE':
                        self.screen_flash_alpha = 50
                        self.screen_flash_color = (255, 150, 50)
                        self.play_sound('berserk_close', 0.4)
                        self.particle_emitter.emit_berserk_aura(
                            self.player.rect.centerx, self.player.rect.centery, 'close')

                    # Trigger combo visual effects
                    self.combo_effects.trigger(self.berserk.combo_count)

                    # Play combo sound on milestone
                    if self.berserk.combo_count in self.berserk.combo_bonus_thresholds:
                        self.play_sound('combo', 0.7)
                        self.screen_flash_alpha = 80
                        self.screen_flash_color = (255, 255, 100)

                    # Track kill for tutorial
                    if self.tutorial.active:
                        self.tutorial.track_kill(self.berserk.current_range)
                    
                    # Screen shake and sounds based on enemy size
                    if enemy.is_boss:
                        self.shake.add(SHAKE_LARGE)
                        self.play_sound('boss_death', 0.8)
                        self.play_sound('explosion_large')
                        # Clear wingmen when boss dies
                        for wingman in self.wingmen:
                            wingman.kill()
                        self.wingmen.empty()
                        self.current_boss = None
                    elif enemy.enemy_type in ['omen', 'maller']:
                        self.shake.add(SHAKE_MEDIUM)
                        self.play_sound('explosion_medium')
                    else:
                        self.shake.add(SHAKE_SMALL)
                        self.play_sound('explosion_small', 0.6)
                    
                    # Create explosion - enhanced for bosses and large ships
                    exp_size = 30 if not enemy.is_boss else 80
                    is_large_ship = enemy.is_boss or enemy.enemy_type in ['omen', 'maller', 'harbinger', 'apocalypse', 'abaddon']

                    if is_large_ship and hasattr(self, 'enhanced_explosions'):
                        # Use enhanced explosion with secondary explosions for big ships
                        enhanced_exp = EnhancedExplosion(
                            enemy.rect.centerx, enemy.rect.centery,
                            exp_size, COLOR_AMARR_ACCENT,
                            has_secondaries=enemy.is_boss
                        )
                        self.enhanced_explosions.append(enhanced_exp)
                        # Screen shake for large explosions
                        if hasattr(self, 'screen_shake'):
                            shake_intensity = 15 if enemy.is_boss else 8
                            shake_duration = 25 if enemy.is_boss else 15
                            self.screen_shake.add_shake(shake_intensity, shake_duration, 'exponential')
                    else:
                        # Explosion with enhanced effects for bosses/cruisers
                        explosion = Explosion(enemy.rect.centerx, enemy.rect.centery,
                                            exp_size, COLOR_AMARR_ACCENT,
                                            is_boss=is_large_ship)
                        self.effects.add(explosion)
                        self.all_sprites.add(explosion)

                    # Clear enemy damage effects
                    clear_ship_damage_effects(id(enemy))

                    # Emit particle death explosion
                    if enemy.is_boss:
                        self.particle_emitter.emit_death_explosion(
                            enemy.rect.centerx, enemy.rect.centery,
                            COLOR_AMARR_ACCENT, 'boss')
                    elif enemy.enemy_type in ['omen', 'maller', 'harbinger']:
                        self.particle_emitter.emit_death_explosion(
                            enemy.rect.centerx, enemy.rect.centery,
                            COLOR_AMARR_ACCENT, 'large')
                    else:
                        self.particle_emitter.emit_death_explosion(
                            enemy.rect.centerx, enemy.rect.centery,
                            COLOR_AMARR_ACCENT, 'small')
                    
                    # Drop refugees from industrials
                    if enemy.refugees > 0:
                        refugee_count = int(enemy.refugees * self.difficulty_settings['refugee_mult'])
                        for _ in range(max(1, refugee_count)):
                            pod = RefugeePod(
                                enemy.rect.centerx + random.randint(-20, 20),
                                enemy.rect.centery + random.randint(-20, 20)
                            )
                            self.pods.add(pod)
                            self.all_sprites.add(pod)
                    
                    # Maybe drop powerup
                    self.spawn_powerup(enemy.rect.centerx, enemy.rect.centery)

                    enemy.kill()

                    # Kill counter for wingman spawns (Rifter only)
                    if not self.player.is_wolf and not self.player.is_jaguar:
                        self.kill_counter += 1
                        if self.kill_counter >= self.kills_per_wingman:
                            self.kill_counter = 0
                            self._spawn_wingman()
                            self.show_message("WINGMAN REINFORCEMENT!", 60)
                break

        # Enemy bullets vs player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in hits:
            # Jaguar shield bubble - blocks ALL damage from any direction
            if self.player.is_frontal_shield_active():
                if getattr(self.player, 'shield_bubble_mode', False):
                    # Full 360 bubble - blocks everything
                    self.particle_emitter.emit_sparks(
                        bullet.rect.centerx, bullet.rect.centery,
                        (80, 180, 255), 8)
                    continue  # Skip damage
                else:
                    # Frontal only - check if hit came from front (above player center)
                    if self.player.is_hit_from_front(bullet.rect.centery):
                        # Blocked by frontal shield - just sparks, no damage
                        self.particle_emitter.emit_sparks(
                            bullet.rect.centerx, bullet.rect.centery,
                            (80, 180, 255), 6)
                        continue  # Skip damage

            damage = int(bullet.damage * self.difficulty_settings['enemy_damage_mult'])

            # Determine which layer took the hit for sound and effects
            if self.player.shields > 0:
                self.play_sound('shield_hit', 0.5)
                # Shield impact ripple effect
                if hasattr(self, 'shield_impacts'):
                    self.shield_impacts.add_impact(
                        bullet.rect.centerx, bullet.rect.centery,
                        self.player.rect.centerx, self.player.rect.centery,
                        self.player.rect.width, self.player.rect.height,
                        damage, 50)
            elif self.player.armor > 0:
                self.play_sound('armor_hit', 0.5)
                # Armor hit - small screen shake
                if hasattr(self, 'screen_shake'):
                    self.screen_shake.add_shake(3, 8, 'exponential')
            else:
                self.play_sound('hull_hit', 0.6)
                # Hull hit - bigger screen shake
                if hasattr(self, 'screen_shake'):
                    self.screen_shake.add_shake(6, 12, 'exponential')

            self.shake.add(SHAKE_SMALL)

            # Apply damage resistance from abilities
            actual_damage = int(damage * self.player.get_damage_resistance())
            if self.player.take_damage(actual_damage):
                # Player dead
                explosion = Explosion(self.player.rect.centerx, self.player.rect.centery,
                                    50, COLOR_MINMATAR_ACCENT)
                self.effects.add(explosion)
                self.all_sprites.add(explosion)
                self.shake.add(SHAKE_LARGE)
                # Big screen shake for player death
                if hasattr(self, 'screen_shake'):
                    self.screen_shake.add_shake(20, 30, 'exponential')
                self.play_sound('explosion_large')
                self.play_sound('defeat', 0.7)
                self.state = 'gameover'
                self._record_game_end(victory=False)
                self.music_manager.stop_music()
                return

        # Enemy bullets vs wingmen
        for wingman in list(self.wingmen):
            hits = pygame.sprite.spritecollide(wingman, self.enemy_bullets, True)
            for bullet in hits:
                if wingman.take_damage(bullet.damage):
                    # Wingman destroyed
                    explosion = Explosion(wingman.rect.centerx, wingman.rect.centery,
                                        25, COLOR_MINMATAR_ACCENT)
                    self.effects.add(explosion)
                    self.all_sprites.add(explosion)
                    self.play_sound('explosion_small', 0.5)
                    wingman.kill()

        # Player collision with enemies
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            self.shake.add(SHAKE_MEDIUM)
            self.play_sound('hull_hit', 0.8)
            collision_damage = int(30 * self.player.get_damage_resistance())
            if self.player.take_damage(collision_damage):
                self.play_sound('explosion_large')
                self.play_sound('defeat', 0.7)
                self.shake.add(SHAKE_LARGE)
                self.state = 'gameover'
                self._record_game_end(victory=False)
                self.music_manager.stop_music()
                return
        
        # Collect refugee pods
        hits = pygame.sprite.spritecollide(self.player, self.pods, True)
        for pod in hits:
            self.player.collect_refugee(pod.count)
            self.play_sound('pickup_refugee', 0.5)
        
        # Collect powerups
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            # Spawn pickup effect at powerup location
            effect = PowerupPickupEffect(
                powerup.rect.centerx,
                powerup.rect.centery,
                powerup.color,
                powerup.powerup_type
            )
            self.effects.add(effect)
            self.all_sprites.add(effect)
            self.apply_powerup(powerup)
        
        # Wave/Stage logic
        self.update_waves()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def apply_powerup(self, powerup):
        """Apply powerup effect to player

        Timed powerups now last until the player overheats or dies.
        """
        data = powerup.data
        now = pygame.time.get_ticks()
        timed_duration = data.get('duration', 5000)
        ptype = powerup.powerup_type

        # === HEAT MANAGEMENT ===
        if ptype == 'nanite':
            heat_reduce = data.get('heat_reduce', 100)
            self.player.cool_heat(heat_reduce)
            self.show_message("Heat Cooled!", 60)
            self.play_sound('powerup_nanite', 0.7)

        # === HEALTH POWERUPS (contextual) ===
        elif ptype == 'shield_recharger':
            heal = data.get('shield_heal', 40)
            self.player.shields = min(self.player.shields + heal, self.player.max_shields)
            self.show_message(f"Shields +{heal}!", 60)
            self.play_sound('powerup_shield', 0.7)
        elif ptype == 'armor_repairer':
            heal = data.get('armor_heal', 35)
            self.player.armor = min(self.player.armor + heal, self.player.max_armor)
            self.show_message(f"Armor +{heal}!", 60)
            self.play_sound('powerup_armor', 0.7)
        elif ptype == 'hull_repairer':
            heal = data.get('hull_heal', 30)
            self.player.hull = min(self.player.hull + heal, self.player.max_hull)
            self.show_message(f"Hull +{heal}!", 60)
            self.play_sound('powerup_nanite', 0.7)

        # === AMMO/CHARGES ===
        elif ptype == 'capacitor':
            self.player.add_rockets(data['rockets'])
            self.show_message("Rockets Loaded!", 60)
            self.play_sound('powerup_capacitor', 0.7)
        elif ptype == 'bomb_charge':
            self.player.bombs = min(self.player.bombs + data['bombs'], self.player.max_bombs)
            self.show_message("Bomb Charged!", 60)
            self.play_sound('powerup_bomb', 0.7)

        # === WEAPON UPGRADES (stack until overheat) ===
        elif ptype == 'weapon_upgrade':
            if self.player.upgrade_weapon():
                lvl = self.player.weapon_level
                msg = f"WEAPON LVL {lvl}!"
                if lvl >= 2:
                    msg += f" (+{self.player.extra_streams} streams)"
                self.show_message(msg, 60)
            else:
                self.show_message("WEAPONS MAXED!", 60)
            self.play_sound('powerup_damage', 0.7)
        elif ptype == 'rapid_fire':
            self.player.add_rapid_fire()
            self.show_message("RAPID FIRE! (5s)", 60)
            self.play_sound('powerup_rapid', 0.7)

        # === TIMED BUFFS ===
        elif ptype == 'overdrive':
            self.player.overdrive_until = now + timed_duration
            self.show_message(f"OVERDRIVE! ({timed_duration//1000}s)", 60)
            self.play_sound('powerup_overdrive', 0.7)
        elif ptype == 'magnet':
            self.player.magnet_until = now + timed_duration
            self.show_message(f"Tractor Beam! ({timed_duration//1000}s)", 60)
            self.play_sound('powerup_magnet', 0.7)
        elif ptype == 'invulnerability':
            self.player.invulnerable_until = now + timed_duration
            self.show_message(f"INVULNERABLE! ({timed_duration//1000}s)", 60)
            self.play_sound('powerup_invuln', 0.7)

        # === LEGACY SUPPORT (in case old saves have these) ===
        elif ptype == 'shield_boost':
            self.player.shield_boost_until = now + timed_duration
            self.player.shields = min(self.player.shields + 30, self.player.max_shields)
            self.show_message("Shields Boosted!", 60)
            self.play_sound('powerup_shield', 0.7)
        elif ptype == 'double_damage':
            self.player.upgrade_weapon()
            self.show_message("Damage Boost!", 60)
            self.play_sound('powerup_damage', 0.7)
    
    def update_waves(self):
        """Handle wave progression"""
        # Endless mode has different wave logic
        if self.game_mode == 'endless':
            self._update_endless_waves()
            return

        # Nightmare mode = endless onslaught with boss every 5th wave
        if self.difficulty == 'nightmare':
            self._update_nightmare_waves()
            return

        # Boss rush mode
        if self.game_mode == 'boss_rush':
            self._update_boss_rush()
            return

        # Abyssal Depths mode
        if self.game_mode == 'abyssal':
            self._update_abyssal()
            return

        stage = self.active_stages[self.current_stage]

        # Wave delay
        if self.wave_delay > 0:
            self.wave_delay -= 1
            return

        # Need to spawn wave?
        if self.wave_enemies == 0 and not self.stage_complete:
            if self.current_wave < stage['waves']:
                self.spawn_wave()
                if not (stage['boss'] and self.current_wave == stage['waves'] - 1):
                    self.show_message(f"Wave {self.current_wave + 1}/{stage['waves']}", 90)
                    self.play_sound('wave_start', 0.4)

        # Spawn enemies RAPIDLY - plow through endless hordes
        spawn_rate_mult = self.difficulty_settings.get('spawn_rate_mult', 1.0)
        spawn_delay = int(15 * spawn_rate_mult)  # Much faster base spawns
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_delay and self.wave_spawned < self.wave_enemies:
            self.spawn_timer = 0
            # High chance for formation spawn - groups of enemies
            if self.wave_spawned < self.wave_enemies - 5:
                if random.random() < 0.5:  # 50% formation chance
                    if not self.maybe_spawn_formation():
                        self.spawn_enemy()
                else:
                    self.spawn_enemy()
            else:
                self.spawn_enemy()

        # Diagonal fleet crossings in ALL modes (not just nightmare)
        if not hasattr(self, '_campaign_fleet_timer'):
            self._campaign_fleet_timer = 0
            self._campaign_fleet_left = True
        self._campaign_fleet_timer += 1
        fleet_interval = 180 if self.difficulty == 'easy' else 120 if self.difficulty == 'normal' else 90
        if self._campaign_fleet_timer >= fleet_interval:
            self._campaign_fleet_timer = 0
            self._spawn_diagonal_fleet(from_left=self._campaign_fleet_left)
            self._campaign_fleet_left = not self._campaign_fleet_left

        # Wave complete?
        if len(self.enemies) == 0 and self.wave_spawned >= self.wave_enemies and self.wave_enemies > 0:
            self.current_wave += 1
            self.wave_enemies = 0
            self.wave_spawned = 0
            self.wave_delay = 90

            # Wingmen now spawn via kill counter gauge (every 15 kills for Rifter)

            # Stage complete?
            if self.current_wave >= stage['waves']:
                self.stage_complete = True
                self.wave_delay = 120
                self.shop_transition_timer = 120  # 2 seconds at 60fps
                self.show_message("STAGE COMPLETE!", 120)
                self.play_sound('stage_complete')
                # Start warp transition effect
                self.warp_transition.start(90)

        # Fallback: ensure stage completes if all waves done and no enemies remain
        # This handles edge cases where wave_enemies might be 0 prematurely
        if (not self.stage_complete and
            len(self.enemies) == 0 and
            self.current_wave >= stage['waves'] and
            not hasattr(self, 'shop_transition_timer')):
            self.stage_complete = True
            self.wave_delay = 120
            self.shop_transition_timer = 120
            self.show_message("STAGE COMPLETE!", 120)
            self.play_sound('stage_complete')
            if hasattr(self, 'warp_transition'):
                self.warp_transition.start(90)

        # Check for shop transition using timer
        if self.stage_complete and hasattr(self, 'shop_transition_timer'):
            self.shop_transition_timer -= 1
            if self.shop_transition_timer <= 0:
                self.state = 'shop'
                del self.shop_transition_timer

    def _update_endless_waves(self):
        """Handle endless mode wave progression"""
        # Track time
        self.endless_time += 1

        # Wave delay
        if self.wave_delay > 0:
            self.wave_delay -= 1
            return

        # Need to spawn new wave?
        if self.wave_enemies == 0:
            self.spawn_wave()

        # Spawn enemies gradually - speed increases with waves
        spawn_delay = max(20, 45 - self.endless_wave)  # Faster spawns over time
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_delay and self.wave_spawned < self.wave_enemies:
            self.spawn_timer = 0
            # Chance for formation spawn (only if enough enemies remain)
            if self.wave_spawned < self.wave_enemies - 3:
                if not self.maybe_spawn_formation():
                    self.spawn_enemy()
            else:
                self.spawn_enemy()

        # Wave complete?
        if len(self.enemies) == 0 and self.wave_spawned >= self.wave_enemies and self.wave_enemies > 0:
            self.wave_enemies = 0
            self.wave_spawned = 0
            # Shorter delays as waves progress
            self.wave_delay = max(30, 90 - self.endless_wave * 2)

    def _update_nightmare_waves(self):
        """Nightmare mode = endless onslaught. Boss every 5th wave. 100 Amarr to 1 Minmatar - survive as long as you can."""
        # Track time (use endless_time for nightmare too)
        if not hasattr(self, 'nightmare_wave'):
            self.nightmare_wave = 0
            self.nightmare_time = 0
            self.nightmare_fleet_timer = 0

        self.nightmare_time += 1
        self.nightmare_fleet_timer += 1

        # Wave delay
        if self.wave_delay > 0:
            self.wave_delay -= 1
            return

        # Need to spawn new wave?
        if self.wave_enemies == 0:
            self._spawn_nightmare_wave()

        # Spawn enemies RAPIDLY - Amarr have endless resources
        spawn_delay = max(8, 20 - self.nightmare_wave)  # Very fast spawns
        self.spawn_timer += 1
        if self.spawn_timer >= spawn_delay and self.wave_spawned < self.wave_enemies:
            self.spawn_timer = 0
            # Higher chance for fleet formations in nightmare
            if self.wave_spawned < self.wave_enemies - 5:
                if random.random() < 0.4:  # 40% fleet formation chance
                    self._spawn_nightmare_fleet()
                elif not self.maybe_spawn_formation():
                    self.spawn_enemy()
            else:
                self.spawn_enemy()

        # Spawn diagonal crossing fleets frequently - alternating sides
        if self.nightmare_fleet_timer >= 120:  # Every 2 seconds
            self.nightmare_fleet_timer = 0
            # Alternate sides each spawn
            if not hasattr(self, '_fleet_from_left'):
                self._fleet_from_left = True
            self._spawn_diagonal_fleet(from_left=self._fleet_from_left)
            self._fleet_from_left = not self._fleet_from_left

        # Carrier drone waves
        if hasattr(self, 'archon_carrier') and random.random() < 0.01:  # 1% per frame = frequent
            self._spawn_carrier_drones()

        # Wave complete?
        if len(self.enemies) == 0 and self.wave_spawned >= self.wave_enemies and self.wave_enemies > 0:
            self.nightmare_wave += 1
            self.wave_enemies = 0
            self.wave_spawned = 0
            # Minimal delay between waves - relentless
            self.wave_delay = max(15, 45 - self.nightmare_wave * 2)
            # Wingmen spawn via kill counter (every 15 kills for Rifter)

    def _spawn_nightmare_wave(self):
        """Spawn nightmare wave - massive enemy counts with boss every 5th wave"""
        self.nightmare_wave += 1
        wave = self.nightmare_wave

        # Massive enemy counts - 100 Amarr to 1 Minmatar ratio
        base_enemies = 25 + wave * 5
        base_enemies = min(base_enemies, 80)  # Cap at 80 per wave

        # Boss every 5th wave
        if wave % 5 == 0:
            # Boss wave - spawn appropriate boss based on wave progress
            if wave >= 20:
                boss_type = 'amarr_capital'
                boss = CapitalShipEnemy(SCREEN_WIDTH // 2, self.difficulty_settings)
            elif wave >= 15:
                boss_type = 'abaddon'
                boss = Enemy(boss_type, SCREEN_WIDTH // 2, -100, self.difficulty_settings)
            elif wave >= 10:
                boss_type = 'apocalypse'
                boss = Enemy(boss_type, SCREEN_WIDTH // 2, -100, self.difficulty_settings)
            else:
                boss_types = ['harbinger', 'prophecy', 'zealot']
                boss_type = random.choice(boss_types)
                boss = Enemy(boss_type, SCREEN_WIDTH // 2, -100, self.difficulty_settings)

            self.enemies.add(boss)
            self.all_sprites.add(boss)
            self.current_boss = boss
            # Boss + massive escort
            self.wave_enemies = 1 + base_enemies
            self.wave_spawned = 1
            self.show_message(f"WAVE {wave} - BOSS APPROACHING!", 120)
            self.play_sound('boss_entrance', 0.7)
            self.play_sound('warning')
        else:
            self.wave_enemies = base_enemies
            self.wave_spawned = 0
            self.show_message(f"WAVE {wave} - INCOMING!", 60)
            self.play_sound('wave_start')

    def _spawn_nightmare_fleet(self):
        """Spawn a formation of same-type ships in nightmare"""
        ship_types = ['executioner', 'punisher', 'tormentor', 'coercer']
        ship_type = random.choice(ship_types)

        # Spawn 5-10 of same ship type in formation
        count = random.randint(5, 10)
        x_center = random.randint(100, SCREEN_WIDTH - 100)

        # Pick a diagonal direction for the whole formation
        from_left = x_center < SCREEN_WIDTH // 2
        vx = random.uniform(1.5, 3.0) if from_left else random.uniform(-3.0, -1.5)

        for i in range(count):
            x_offset = (i - count // 2) * 40
            x = max(40, min(SCREEN_WIDTH - 40, x_center + x_offset))
            enemy = Enemy(ship_type, x, -50 - i * 20, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx + random.uniform(-0.3, 0.3)
            enemy.patrol_vy = random.uniform(2.0, 3.0)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)
            self.wave_spawned += 1

    def _spawn_diagonal_fleet(self, from_left=None):
        """Spawn fleet of SAME hull type that crosses screen diagonally"""
        if from_left is None:
            from_left = random.choice([True, False])

        # Always same hull type for fleet cohesion
        ship_types = ['executioner', 'punisher', 'tormentor', 'coercer']
        ship_type = random.choice(ship_types)

        # Large fleets - 12-20 ships of same type
        count = random.randint(12, 20)

        for i in range(count):
            if from_left:
                x = -50 - i * 25
                y = random.randint(-50, 50) + i * 12
                vx = random.uniform(3, 5)
            else:
                x = SCREEN_WIDTH + 50 + i * 25
                y = random.randint(-50, 50) + i * 12
                vx = random.uniform(-5, -3)

            enemy = Enemy(ship_type, x, y, self.difficulty_settings)
            enemy.movement_pattern = Enemy.PATTERN_DIAGONAL
            enemy.patrol_vx = vx
            enemy.patrol_vy = random.uniform(2, 3.5)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def _spawn_carrier_drones(self):
        """Spawn wave of drones from carrier in nightmare mode"""
        if not hasattr(self, 'archon_carrier'):
            return

        carrier_x, carrier_y = self.archon_carrier.get_spawn_position()
        num_drones = random.randint(4, 8)

        for i in range(num_drones):
            x = carrier_x + random.randint(-100, 100)
            x = max(40, min(SCREEN_WIDTH - 40, x))
            y = carrier_y + random.randint(0, 30)

            drone_type = random.choice(['drone', 'drone', 'interceptor', 'bomber'])
            enemy = Enemy(drone_type, x, y, self.difficulty_settings)
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

        self.archon_carrier.trigger_launch()

    def draw(self):
        """Render everything"""
        # Draw to render surface first (for screen shake)
        self.render_surface.fill((10, 10, 20))

        # Parallax back layers (nebulae - furthest)
        self.parallax.draw_back_layers(self.render_surface)

        # Stars
        for star in self.stars:
            star.draw(self.render_surface)

        # Parallax mid layers (stations, far asteroids)
        self.parallax.draw_mid_layers(self.render_surface)

        # Parallax front layers (medium asteroids, debris - closest background)
        self.parallax.draw_front_layers(self.render_surface)

        if self.state == 'splash':
            self.splash_screen.draw(self.render_surface)
        elif self.state == 'chapter_select':
            self.draw_chapter_select()
        elif self.state == 'menu':
            self.draw_menu()
        elif self.state == 'ship_select':
            self.draw_ship_select()
        elif self.state == 'difficulty':
            self.draw_difficulty()
        elif self.state == 'empire_select':
            self.draw_empire_select()
        elif self.state == 'faction_select':
            self.draw_faction_select()
        elif self.state == 'filament_select':
            self.draw_filament_select()
        elif self.state == 'mode_select':
            self.draw_mode_select()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'paused':
            self.draw_game()
            self.draw_pause()
        elif self.state == 'shop':
            self.draw_shop()
        elif self.state == 'gameover':
            self.draw_game()
            self.draw_gameover()
        elif self.state == 'victory':
            self.draw_victory()
        elif self.state == 'settings':
            self.draw_settings()
        elif self.state == 'pause_settings':
            self.draw_game()
            self.draw_settings(from_pause=True)
        elif self.state == 'leaderboard':
            self.draw_leaderboard()
        elif self.state == 'credits':
            self.draw_credits()
        elif self.state == 'how_to_play':
            self.draw_how_to_play()

        # Draw warp transition effect
        self.warp_transition.draw(self.render_surface)

        # Apply screen shake (if enabled)
        if self.shake_enabled:
            shake_x, shake_y = self.shake.offset_x, self.shake.offset_y
            # Add new screen shake system offset
            if hasattr(self, 'screen_shake'):
                new_shake_x, new_shake_y = self.screen_shake.get_offset()
                shake_x += new_shake_x
                shake_y += new_shake_y
        else:
            shake_x, shake_y = 0, 0

        # Scale render surface to actual screen (fullscreen support)
        if self.fullscreen and (self.actual_width != SCREEN_WIDTH or self.actual_height != SCREEN_HEIGHT):
            scaled = pygame.transform.scale(self.render_surface, (self.actual_width, self.actual_height))
            self.screen.blit(scaled, (shake_x, shake_y))
        else:
            self.screen.blit(self.render_surface, (shake_x, shake_y))

        # Apply screen flash overlay (for berserk kills)
        if self.screen_flash_alpha > 0:
            flash_overlay = pygame.Surface((self.actual_width, self.actual_height), pygame.SRCALPHA)
            flash_overlay.fill((*self.screen_flash_color, int(self.screen_flash_alpha)))
            self.screen.blit(flash_overlay, (0, 0))

        # Draw achievement notifications
        self._draw_achievement_notifications()

        pygame.display.flip()
    
    def draw_difficulty(self):
        """Draw clean difficulty selection screen"""
        cx = SCREEN_WIDTH // 2

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SELECT DIFFICULTY", True, (255, 180, 100))
        rect = title.get_rect(center=(cx, 80))
        self.render_surface.blit(title, rect)
        pygame.draw.line(self.render_surface, (100, 60, 40), (cx - 180, 105), (cx + 180, 105), 2)

        difficulties = [
            ('1', 'easy', 'CAREBEAR', (100, 200, 100), 1.0),
            ('2', 'normal', 'NEWBRO', (200, 180, 100), 2.0),
            ('3', 'hard', 'BITTER VET', (255, 150, 80), 3.0),
            ('4', 'nightmare', 'TRIGLAVIAN', (255, 80, 80), 4.0)
        ]

        # Draw difficulty cards in a 2x2 grid
        card_w, card_h = 220, 70
        start_y = 150
        for i, (key, diff_id, name, color, intensity) in enumerate(difficulties):
            row, col = i // 2, i % 2
            card_x = cx - card_w - 10 + col * (card_w + 20)
            card_y = start_y + row * (card_h + 20)

            is_selected = (i == self.difficulty_index)

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((40, 35, 45, 220))
                glow_rect = pygame.Rect(card_x - 4, card_y - 4, card_w + 8, card_h + 8)
                pygame.draw.rect(self.render_surface, (*color, 100), glow_rect, 4, border_radius=8)
            else:
                card_surf.fill((25, 25, 35, 180))
            border_width = 3 if is_selected else 2
            pygame.draw.rect(card_surf, color, (0, 0, card_w, card_h), border_width, border_radius=6)
            self.render_surface.blit(card_surf, (card_x, card_y))

            # Selection arrow
            if is_selected:
                arrow_x = card_x - 18
                arrow_y = card_y + card_h // 2
                pygame.draw.polygon(self.render_surface, color,
                    [(arrow_x, arrow_y), (arrow_x + 10, arrow_y - 6), (arrow_x + 10, arrow_y + 6)])

            # Name centered
            name_font = pygame.font.Font(None, 36)
            name_color = (255, 255, 255) if is_selected else color
            name_text = name_font.render(name, True, name_color)
            name_rect = name_text.get_rect(center=(card_x + card_w // 2, card_y + 28))
            self.render_surface.blit(name_text, name_rect)

            # Difficulty bar
            bar_y = card_y + card_h - 18
            bar_width = card_w - 40
            pygame.draw.rect(self.render_surface, (40, 40, 50),
                           (card_x + 20, bar_y, bar_width, 6), border_radius=2)
            fill_width = int(bar_width * intensity / 4)
            pygame.draw.rect(self.render_surface, color,
                           (card_x + 20, bar_y, fill_width, 6), border_radius=2)

        # Controller/Back hints
        hint_y = SCREEN_HEIGHT - 60
        if self.controller.connected:
            hint_text = self.font_small.render("[A] Select    [B] Back", True, (100, 100, 100))
        else:
            hint_text = self.font_small.render("[1-4] Select    [ESC] Back", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(cx, hint_y))
        self.render_surface.blit(hint_text, hint_rect)

    def draw_empire_select(self):
        """Draw empire selection screen - Choose your faction"""
        cx = SCREEN_WIDTH // 2

        # Draw faction background based on current selection
        selected_faction = self.empire_options[self.empire_index].get('player_faction', 'minmatar')
        bg = self.faction_backgrounds.get(selected_faction)
        if bg:
            # Draw background with darkening overlay
            self.render_surface.blit(bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))  # Semi-transparent dark overlay
            self.render_surface.blit(overlay, (0, 0))

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("CHOOSE YOUR FACTION", True, (255, 150, 100))
        rect = title.get_rect(center=(cx, 50))
        self.render_surface.blit(title, rect)

        subtitle_font = pygame.font.Font(None, 32)
        subtitle = subtitle_font.render("Fight for your empire", True, (180, 180, 180))
        sub_rect = subtitle.get_rect(center=(cx, 85))
        self.render_surface.blit(subtitle, sub_rect)

        # Difficulty badge
        diff_name = self.difficulty_settings['name'].upper()
        diff_colors = {'CAREBEAR': (100, 200, 100), 'NEWBRO': (200, 180, 100),
                      'BITTER VET': (255, 150, 80), 'TRIGLAVIAN': (255, 80, 80)}
        diff_color = diff_colors.get(diff_name, (150, 150, 150))
        badge_font = pygame.font.Font(None, 22)
        badge_text = badge_font.render(diff_name, True, diff_color)
        badge_rect = badge_text.get_rect(center=(cx, 110))
        self.render_surface.blit(badge_text, badge_rect)

        # Faction cards - 4 side by side (2x2 grid for better fit)
        card_w, card_h = 180, 280
        spacing_x = 20
        spacing_y = 20
        # 2x2 grid layout
        grid_w = 2 * card_w + spacing_x
        2 * card_h + spacing_y
        start_x = cx - grid_w // 2
        start_y = 130

        for i, empire in enumerate(self.empire_options):
            # 2x2 grid: row = i // 2, col = i % 2
            row = i // 2
            col = i % 2
            card_x = start_x + col * (card_w + spacing_x)
            card_y = start_y + row * (card_h + spacing_y)

            is_selected = (i == self.empire_index)
            color = empire['color_primary']
            color_sec = empire['color_secondary']

            # Card background with glow if selected
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((40, 35, 45, 230))
                # Glow effect
                glow_rect = pygame.Rect(card_x - 4, card_y - 4, card_w + 8, card_h + 8)
                pygame.draw.rect(self.render_surface, (*color[:3], 100), glow_rect, 4, border_radius=10)
            else:
                card_surf.fill((25, 25, 35, 180))

            border_width = 3 if is_selected else 2
            pygame.draw.rect(card_surf, color, (0, 0, card_w, card_h), border_width, border_radius=8)
            self.render_surface.blit(card_surf, (card_x, card_y))

            # Selection indicator (arrow pointing to card)
            if is_selected:
                indicator_y = card_y - 12
                pygame.draw.polygon(self.render_surface, color,
                    [(card_x + card_w // 2, indicator_y + 10),
                     (card_x + card_w // 2 - 8, indicator_y),
                     (card_x + card_w // 2 + 8, indicator_y)])

            # Faction name
            name_font = pygame.font.Font(None, 28)
            name_color = (255, 255, 255) if is_selected else color
            name_text = name_font.render(empire['name'], True, name_color)
            name_rect = name_text.get_rect(center=(card_x + card_w // 2, card_y + 25))
            self.render_surface.blit(name_text, name_rect)

            # Description (smaller)
            desc_font = pygame.font.Font(None, 20)
            desc_text = desc_font.render(empire['description'], True, color_sec)
            desc_rect = desc_text.get_rect(center=(card_x + card_w // 2, card_y + 50))
            self.render_surface.blit(desc_text, desc_rect)

            # Divider line
            pygame.draw.line(self.render_surface, (*color[:3], 100),
                           (card_x + 10, card_y + 65), (card_x + card_w - 10, card_y + 65), 1)

            # Narrative text (wrapped, smaller)
            narr_font = pygame.font.Font(None, 18)
            narrative = empire['narrative']
            words = narrative.split()
            lines = []
            current_line = ""
            max_width = card_w - 20

            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surf = narr_font.render(test_line, True, (180, 180, 180))
                if test_surf.get_width() < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw narrative lines
            narr_y = card_y + 80
            for line in lines[:4]:  # Max 4 lines
                line_text = narr_font.render(line, True, (140, 140, 140))
                line_rect = line_text.get_rect(center=(card_x + card_w // 2, narr_y))
                self.render_surface.blit(line_text, line_rect)
                narr_y += 16

            # VS indicator box at bottom
            vs_y = card_y + card_h - 55
            vs_font = pygame.font.Font(None, 20)

            # Player faction
            player_faction = empire.get('player_faction', 'minmatar').upper()
            player_text = vs_font.render(f"Play: {player_faction}", True, (100, 200, 100))
            player_rect = player_text.get_rect(center=(card_x + card_w // 2, vs_y))
            self.render_surface.blit(player_text, player_rect)

            # Enemy faction
            enemy_faction = empire.get('enemy_faction', 'amarr').upper()
            enemy_text = vs_font.render(f"vs {enemy_faction}", True, (255, 100, 100))
            enemy_rect = enemy_text.get_rect(center=(card_x + card_w // 2, vs_y + 20))
            self.render_surface.blit(enemy_text, enemy_rect)

        # Controls hint
        hint_y = SCREEN_HEIGHT - 40
        if self.controller and self.controller.connected:
            hint_text = self.font_small.render("[A] Select    [B] Back    [D-pad] Navigate", True, (100, 100, 100))
        else:
            hint_text = self.font_small.render("[1-4] Select    [ESC] Back    [Arrow Keys] Navigate", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(cx, hint_y))
        self.render_surface.blit(hint_text, hint_rect)

    def draw_faction_select(self):
        """Draw faction selection screen - Minmatar vs Amarr"""
        cx = SCREEN_WIDTH // 2

        # Title
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("CHOOSE YOUR SIDE", True, (255, 200, 150))
        rect = title.get_rect(center=(cx, 60))
        self.render_surface.blit(title, rect)
        pygame.draw.line(self.render_surface, (100, 60, 40), (cx - 200, 90), (cx + 200, 90), 2)

        # Difficulty badge
        diff_name = self.difficulty_settings['name'].upper()
        diff_colors = {'CAREBEAR': (100, 200, 100), 'NEWBRO': (200, 180, 100),
                      'BITTER VET': (255, 150, 80), 'TRIGLAVIAN': (255, 80, 80)}
        diff_color = diff_colors.get(diff_name, (150, 150, 150))
        badge_font = pygame.font.Font(None, 22)
        badge_text = badge_font.render(diff_name, True, diff_color)
        badge_rect = badge_text.get_rect(center=(cx, 110))
        self.render_surface.blit(badge_text, badge_rect)

        # Faction cards - side by side
        card_w, card_h = 320, 380
        spacing = 60
        start_x = cx - card_w - spacing // 2

        factions = [
            ('minmatar', FACTIONS['minmatar']),
            ('amarr', FACTIONS['amarr'])
        ]

        for i, (faction_id, faction_data) in enumerate(factions):
            card_x = start_x + i * (card_w + spacing)
            card_y = 140

            is_selected = (i == self.faction_index)
            color = faction_data['color_primary']

            # Card background with glow if selected
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((40, 35, 45, 230))
                # Glow effect
                glow_rect = pygame.Rect(card_x - 6, card_y - 6, card_w + 12, card_h + 12)
                pygame.draw.rect(self.render_surface, (*color[:3], 80), glow_rect, 6, border_radius=12)
            else:
                card_surf.fill((25, 25, 35, 180))

            border_width = 4 if is_selected else 2
            pygame.draw.rect(card_surf, color, (0, 0, card_w, card_h), border_width, border_radius=10)
            self.render_surface.blit(card_surf, (card_x, card_y))

            # Selection indicator
            if is_selected:
                indicator_y = card_y - 20
                pygame.draw.polygon(self.render_surface, color,
                    [(card_x + card_w // 2, indicator_y),
                     (card_x + card_w // 2 - 12, indicator_y - 15),
                     (card_x + card_w // 2 + 12, indicator_y - 15)])

            # Faction name
            name_font = pygame.font.Font(None, 44)
            name_color = (255, 255, 255) if is_selected else color
            name_text = name_font.render(faction_data['name'], True, name_color)
            name_rect = name_text.get_rect(center=(card_x + card_w // 2, card_y + 35))
            self.render_surface.blit(name_text, name_rect)

            # Tagline
            tagline_font = pygame.font.Font(None, 28)
            tagline_text = tagline_font.render(f'"{faction_data["tagline"]}"', True, color)
            tagline_rect = tagline_text.get_rect(center=(card_x + card_w // 2, card_y + 65))
            self.render_surface.blit(tagline_text, tagline_rect)

            # Divider line
            pygame.draw.line(self.render_surface, (*color[:3], 100),
                           (card_x + 20, card_y + 90), (card_x + card_w - 20, card_y + 90), 1)

            # Story intro (wrapped text)
            story_font = pygame.font.Font(None, 22)
            story_text = faction_data['story_intro']
            words = story_text.split()
            lines = []
            current_line = ""
            max_width = card_w - 40

            for word in words:
                test_line = current_line + " " + word if current_line else word
                test_surf = story_font.render(test_line, True, (180, 180, 180))
                if test_surf.get_width() < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            # Draw story lines
            story_y = card_y + 105
            for line in lines[:6]:  # Max 6 lines
                line_text = story_font.render(line, True, (160, 160, 160))
                line_rect = line_text.get_rect(center=(card_x + card_w // 2, story_y))
                self.render_surface.blit(line_text, line_rect)
                story_y += 22

            # Weapon type indicator
            weapon_y = card_y + card_h - 100
            weapon_font = pygame.font.Font(None, 26)
            weapon_type = "AUTOCANNONS" if faction_id == 'minmatar' else "LASERS"
            weapon_color = (255, 150, 50) if faction_id == 'minmatar' else (100, 150, 255)
            weapon_text = weapon_font.render(f"Weapon: {weapon_type}", True, weapon_color)
            weapon_rect = weapon_text.get_rect(center=(card_x + card_w // 2, weapon_y))
            self.render_surface.blit(weapon_text, weapon_rect)

            # Engine color indicator
            engine_y = weapon_y + 28
            engine_color = faction_data['engine_color']
            engine_text = weapon_font.render("Engines:", True, (120, 120, 120))
            engine_rect = engine_text.get_rect(midright=(card_x + card_w // 2 - 5, engine_y))
            self.render_surface.blit(engine_text, engine_rect)
            # Draw engine color swatch
            pygame.draw.circle(self.render_surface, engine_color,
                             (card_x + card_w // 2 + 20, engine_y), 8)
            pygame.draw.circle(self.render_surface, (255, 255, 255),
                             (card_x + card_w // 2 + 20, engine_y), 8, 1)

            # Ship preview sprites
            ships_y = engine_y + 30
            ship_preview_size = 45
            ship_spacing = 55
            ships = faction_data['player_ships']
            total_width = len(ships) * ship_spacing - 10
            start_ship_x = card_x + (card_w - total_width) // 2

            for j, ship_name in enumerate(ships):
                ship_x = start_ship_x + j * ship_spacing
                # Try to load and display ship sprite
                try:
                    from sprites import load_ship_sprite
                    ship_sprite = load_ship_sprite(ship_name, (ship_preview_size, ship_preview_size))
                    if ship_sprite:
                        sprite_rect = ship_sprite.get_rect(center=(ship_x + ship_preview_size // 2, ships_y))
                        self.render_surface.blit(ship_sprite, sprite_rect)
                        # Ship name below
                        name_font = pygame.font.Font(None, 16)
                        name_text = name_font.render(ship_name.title(), True, (120, 120, 120))
                        name_rect = name_text.get_rect(center=(ship_x + ship_preview_size // 2, ships_y + 32))
                        self.render_surface.blit(name_text, name_rect)
                except Exception:
                    pass

        # Controller/keyboard hints
        hint_y = SCREEN_HEIGHT - 60
        if self.controller.connected:
            hint_text = self.font_small.render("[A] Select    [B] Back    [LB/RB] Switch", True, (100, 100, 100))
        else:
            hint_text = self.font_small.render("[1/2] or [LEFT/RIGHT] Select    [ESC] Back", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(cx, hint_y))
        self.render_surface.blit(hint_text, hint_rect)

    def draw_filament_select(self):
        """Draw Abyssal filament and tier selection screen."""
        cx = SCREEN_WIDTH // 2
        SCREEN_HEIGHT // 2

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("ENTER THE ABYSS", True, (200, 50, 80))
        rect = title.get_rect(center=(cx, 50))
        self.render_surface.blit(title, rect)

        sub_font = pygame.font.Font(None, 24)
        subtitle = sub_font.render("Select Filament Type and Tier", True, (150, 150, 150))
        sub_rect = subtitle.get_rect(center=(cx, 80))
        self.render_surface.blit(subtitle, sub_rect)

        # Filament selection (horizontal)
        filament_y = 150
        filament_width = 120
        filament_spacing = 15
        total_width = len(self.abyssal_filaments) * (filament_width + filament_spacing) - filament_spacing
        start_x = cx - total_width // 2

        for i, filament in enumerate(self.abyssal_filaments):
            x = start_x + i * (filament_width + filament_spacing)
            is_selected = (i == self.selected_filament)

            # Card background
            card_surf = pygame.Surface((filament_width, 80), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((40, 20, 30, 220))
            else:
                card_surf.fill((25, 20, 25, 180))

            # Border
            color = filament['color']
            pygame.draw.rect(card_surf, color if is_selected else (80, 80, 90),
                           (0, 0, filament_width, 80), 2 if is_selected else 1, border_radius=6)

            self.render_surface.blit(card_surf, (x, filament_y))

            # Filament name
            name_color = color if is_selected else (120, 120, 130)
            name_text = self.font_small.render(filament['name'], True, name_color)
            name_rect = name_text.get_rect(center=(x + filament_width // 2, filament_y + 25))
            self.render_surface.blit(name_text, name_rect)

            # Effect hint
            effect = filament.get('description', '')[:20] + '...' if len(filament.get('description', '')) > 20 else filament.get('description', 'Stable')
            effect_text = self.font_small.render(effect[:15], True, (100, 100, 110))
            effect_rect = effect_text.get_rect(center=(x + filament_width // 2, filament_y + 55))
            self.render_surface.blit(effect_text, effect_rect)

        # Tier selection (vertical)
        tier_y = 260
        tier_height = 50
        tier_spacing = 10

        tier_label = pygame.font.Font(None, 28).render("TIER", True, (150, 100, 100))
        self.render_surface.blit(tier_label, tier_label.get_rect(center=(cx, tier_y - 20)))

        for i, tier in enumerate(self.abyssal_tiers[:5]):  # Show first 5 tiers
            y = tier_y + i * (tier_height + tier_spacing)
            is_selected = (i == self.selected_tier)

            # Tier bar
            bar_width = 400
            bar_x = cx - bar_width // 2

            bar_surf = pygame.Surface((bar_width, tier_height), pygame.SRCALPHA)
            if is_selected:
                bar_surf.fill((40, 30, 35, 220))
            else:
                bar_surf.fill((25, 25, 30, 160))

            color = tier['color']
            pygame.draw.rect(bar_surf, color if is_selected else (60, 60, 70),
                           (0, 0, bar_width, tier_height), 2 if is_selected else 1, border_radius=4)

            self.render_surface.blit(bar_surf, (bar_x, y))

            # Tier number and name
            tier_num = self.font_small.render(f"T{i+1}", True, color)
            self.render_surface.blit(tier_num, (bar_x + 15, y + 15))

            tier_name = pygame.font.Font(None, 28).render(tier['name'], True,
                                                         (255, 255, 255) if is_selected else (150, 150, 150))
            self.render_surface.blit(tier_name, (bar_x + 60, y + 13))

            # Timer hint
            timer_mins = 20 - i * 2  # Approximate timer per tier
            timer_text = self.font_small.render(f"{timer_mins}min", True, (100, 100, 110))
            self.render_surface.blit(timer_text, (bar_x + bar_width - 60, y + 15))

        # Navigation hints
        hint_y = SCREEN_HEIGHT - 60
        if self.controller and self.controller.connected:
            hint = "[D-Pad] Navigate    [A] Enter Abyss    [B] Back"
        else:
            hint = "[Arrow Keys] Navigate    [Enter] Enter Abyss    [ESC] Back"
        hint_text = self.font_small.render(hint, True, (100, 100, 100))
        self.render_surface.blit(hint_text, hint_text.get_rect(center=(cx, hint_y)))

        # Warning
        warning = "Warning: Death in the Abyss means losing your ship!"
        warning_text = self.font_small.render(warning, True, (200, 100, 100))
        self.render_surface.blit(warning_text, warning_text.get_rect(center=(cx, SCREEN_HEIGHT - 30)))

    def draw_mode_select(self):
        """Draw polished game mode selection screen"""
        cx = SCREEN_WIDTH // 2

        # Title
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SELECT MODE", True, (255, 180, 100))
        rect = title.get_rect(center=(cx, 60))
        self.render_surface.blit(title, rect)
        pygame.draw.line(self.render_surface, (100, 60, 40), (cx - 150, 85), (cx + 150, 85), 2)

        # Difficulty badge
        diff_name = self.difficulty_settings['name'].upper()
        diff_colors = {'EASY': (100, 200, 100), 'NORMAL': (200, 180, 100),
                      'HARD': (255, 150, 80), 'NIGHTMARE': (255, 80, 80)}
        diff_color = diff_colors.get(diff_name, (150, 150, 150))
        badge_surf = pygame.Surface((120, 24), pygame.SRCALPHA)
        badge_surf.fill((30, 30, 40, 200))
        pygame.draw.rect(badge_surf, diff_color, (0, 0, 120, 24), 1, border_radius=4)
        self.render_surface.blit(badge_surf, (cx - 60, 95))
        diff_text = self.font_small.render(diff_name, True, diff_color)
        diff_rect = diff_text.get_rect(center=(cx, 107))
        self.render_surface.blit(diff_text, diff_rect)

        # Mode cards
        modes = [
            ('1', 'CAMPAIGN', 'Fight through 5 stages', '5 stages • Boss battles • Upgrades',
             COLOR_MINMATAR_ACCENT, (180, 100, 50)),
            ('2', 'ENDLESS', 'Survive infinite waves', 'No end • Escalating • Leaderboard',
             (255, 150, 100), (200, 100, 50)),
            ('3', 'BOSS RUSH', 'All bosses back-to-back', f'{len(self.boss_rush_bosses)} bosses • No breaks',
             (180, 130, 220), (140, 90, 180)),
            ('4', 'ABYSSAL', 'Roguelike Triglavian abyss', '3 rooms • Timer • Filaments',
             (148, 0, 211), (100, 0, 150))
        ]

        card_w, card_h = SCREEN_WIDTH - 100, 85
        start_y = 145

        for i, (key, name, desc, features, color, bg_tint) in enumerate(modes):
            card_y = start_y + i * (card_h + 15)
            is_selected = (i == self.mode_index)

            # Card background - highlighted if selected
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            if is_selected:
                card_surf.fill((bg_tint[0]//4, bg_tint[1]//4, bg_tint[2]//4, 220))
                # Selection glow
                glow_rect = pygame.Rect(46, card_y - 4, card_w + 8, card_h + 8)
                pygame.draw.rect(self.render_surface, (*color, 80), glow_rect, 4, border_radius=12)
            else:
                card_surf.fill((bg_tint[0]//6, bg_tint[1]//6, bg_tint[2]//6, 180))
            border_width = 3 if is_selected else 2
            pygame.draw.rect(card_surf, color, (0, 0, card_w, card_h), border_width, border_radius=8)
            self.render_surface.blit(card_surf, (50, card_y))

            # Selection arrow
            if is_selected:
                arrow_x = 30
                arrow_y = card_y + card_h // 2
                pygame.draw.polygon(self.render_surface, color,
                    [(arrow_x, arrow_y), (arrow_x + 14, arrow_y - 10), (arrow_x + 14, arrow_y + 10)])

            # Key badge
            key_rect = pygame.Rect(65, card_y + 15, 40, 40)
            bg_color = (50, 45, 55) if is_selected else (30, 30, 40)
            pygame.draw.rect(self.render_surface, bg_color, key_rect, border_radius=6)
            pygame.draw.rect(self.render_surface, color, key_rect, 3 if is_selected else 2, border_radius=6)
            key_text = self.font_large.render(key, True, color)
            key_text_rect = key_text.get_rect(center=key_rect.center)
            self.render_surface.blit(key_text, key_text_rect)

            # Mode name
            name_color = (255, 255, 255) if is_selected else color
            name_text = self.font_large.render(name, True, name_color)
            self.render_surface.blit(name_text, (120, card_y + 12))

            # Description
            desc_color = (230, 230, 230) if is_selected else (200, 200, 200)
            desc_text = self.font.render(desc, True, desc_color)
            self.render_surface.blit(desc_text, (120, card_y + 40))

            # Features
            feat_color = (160, 160, 160) if is_selected else (120, 120, 120)
            feat_text = self.font_small.render(features, True, feat_color)
            self.render_surface.blit(feat_text, (120, card_y + 62))

        # High scores panel at bottom
        stats_y = SCREEN_HEIGHT - 110
        stats_panel = pygame.Surface((SCREEN_WIDTH - 80, 45), pygame.SRCALPHA)
        stats_panel.fill((20, 20, 30, 160))
        pygame.draw.rect(stats_panel, (60, 50, 45), (0, 0, SCREEN_WIDTH - 80, 45), 1, border_radius=4)
        self.render_surface.blit(stats_panel, (40, stats_y))

        # Endless best
        if self.endless_high_wave > 0:
            label = self.font_small.render("ENDLESS BEST", True, (100, 100, 100))
            self.render_surface.blit(label, (60, stats_y + 5))
            value = self.font.render(f"Wave {self.endless_high_wave}", True, (255, 180, 100))
            self.render_surface.blit(value, (60, stats_y + 20))

        # Boss rush best
        if self.boss_rush_best_time > 0:
            label = self.font_small.render("BOSS RUSH BEST", True, (100, 100, 100))
            self.render_surface.blit(label, (SCREEN_WIDTH - 200, stats_y + 5))
            value = self.font.render(f"{self.boss_rush_best_time}s", True, (180, 130, 220))
            self.render_surface.blit(value, (SCREEN_WIDTH - 200, stats_y + 20))

        # Controller/Back hints
        hint_y = SCREEN_HEIGHT - 50
        if self.controller.connected:
            hint_text = self.font_small.render("[A] Select    [B] Back", True, (100, 100, 100))
        else:
            hint_text = self.font_small.render("[1-3] Select    [ESC] Back", True, (100, 100, 100))
        hint_rect = hint_text.get_rect(center=(cx, hint_y))
        self.render_surface.blit(hint_text, hint_rect)

    def draw_game(self):
        # Draw stage-based parallax background (nebulae, stars, stage environment, traffic)
        if hasattr(self, 'stage_background'):
            self.stage_background.draw(self.render_surface, pygame.time.get_ticks())
        else:
            # Fallback to old background
            if hasattr(self, "space_background"):
                self.space_background.draw(self.render_surface)

        # Draw Archon carrier in background (only during gameplay)
        if hasattr(self, "archon_carrier") and self.state == 'playing':
            self.archon_carrier.draw(self.render_surface)

        # Draw environmental hazards (behind most sprites)
        if self.state == 'playing':
            self.hazards.draw(self.render_surface)

            # Draw abyssal-specific elements (hazards, gates)
            if self.game_mode == 'abyssal':
                self._draw_abyssal_elements()

        """Draw gameplay elements"""
        # Draw rocket trails BEFORE sprites (so trails appear behind rockets)
        for sprite in self.player_bullets:
            if hasattr(sprite, 'draw_trail'):
                sprite.draw_trail(self.render_surface)

        # Draw enemy bullet trails
        for bullet in self.enemy_bullets:
            if hasattr(bullet, 'draw_trail'):
                bullet.draw_trail(self.render_surface)

        # Draw sprites
        for sprite in self.all_sprites:
            if sprite != self.player:
                self.render_surface.blit(sprite.image, sprite.rect)

        # Draw enemy damage effects (smoke, sparks, fire)
        for enemy in self.enemies:
            enemy_id = id(enemy)
            from visual_effects import _ship_damage_effects
            if enemy_id in _ship_damage_effects:
                _ship_damage_effects[enemy_id].draw(self.render_surface)

        # Draw enhanced explosions
        if hasattr(self, 'enhanced_explosions'):
            for exp in self.enhanced_explosions:
                exp.draw(self.render_surface)

        # Draw player powerup glow effects
        self._draw_player_powerup_glow()

        # Draw player last (on top) - apply thrust jet effect if active
        if self.player.thrust_active:
            duration = self.player.thrust_duration + (6 if self.player.thrust_direction == 0 else 0)
            progress = 1 - (self.player.thrust_timer / duration)
            direction = self.player.thrust_direction
            cx, cy = self.player.rect.center

            # Draw motion blur trail (ghost images trailing behind movement)
            for i in range(4):
                ghost_alpha = int(80 - i * 20)
                if ghost_alpha > 0:
                    if direction == 0:
                        # Forward boost - trail below
                        ghost_x = cx
                        ghost_y = cy + (i + 1) * 15 * (1 - progress)
                        tint_color = (255, 180, 50, 30)
                    else:
                        # Horizontal - trail opposite to movement
                        ghost_x = cx + direction * -20 * (i + 1) * (1 - progress)
                        ghost_y = cy
                        tint_color = (255, 150, 50, 30) if direction > 0 else (50, 150, 255, 30)

                    ghost_surf = self.player.image.copy()
                    ghost_surf.set_alpha(ghost_alpha)
                    tint = pygame.Surface(ghost_surf.get_size(), pygame.SRCALPHA)
                    tint.fill(tint_color)
                    ghost_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                    ghost_rect = ghost_surf.get_rect(center=(ghost_x, ghost_y))
                    self.render_surface.blit(ghost_surf, ghost_rect)

            # Draw engine flare
            flare_intensity = 1 - progress
            flare_size = int(15 + 10 * flare_intensity)

            if direction == 0:
                # Forward - flare below ship
                flare_x = cx
                flare_y = cy + 30
                flare_color = (255, 200, 100)
            else:
                # Horizontal - flare opposite to movement
                flare_x = cx - direction * 25
                flare_y = cy
                flare_color = (255, 200, 100) if direction > 0 else (100, 200, 255)

            # Engine flare glow
            flare_surf = pygame.Surface((flare_size * 4, flare_size * 4), pygame.SRCALPHA)
            flare_alpha = int(150 * flare_intensity)
            pygame.draw.circle(flare_surf, (*flare_color, flare_alpha // 2),
                             (flare_size * 2, flare_size * 2), flare_size * 2)
            pygame.draw.circle(flare_surf, (*flare_color, flare_alpha),
                             (flare_size * 2, flare_size * 2), flare_size)
            pygame.draw.circle(flare_surf, (255, 255, 255, min(255, flare_alpha + 50)),
                             (flare_size * 2, flare_size * 2), flare_size // 2)
            flare_rect = flare_surf.get_rect(center=(flare_x, flare_y))
            self.render_surface.blit(flare_surf, flare_rect)

            # Draw speed streaks
            for i in range(5):
                if direction == 0:
                    # Forward - vertical streaks
                    streak_x = cx + random.randint(-25, 25)
                    streak_y = cy + random.randint(15, 50)
                    streak_len = random.randint(20, 40)
                    int(100 * flare_intensity)
                    streak_color = (255, 220, 150)
                    pygame.draw.line(self.render_surface, streak_color,
                                   (streak_x, streak_y), (streak_x, streak_y + streak_len), 2)
                else:
                    # Horizontal streaks
                    streak_y = cy + random.randint(-20, 20)
                    streak_x = cx - direction * random.randint(10, 40)
                    streak_len = random.randint(15, 30)
                    int(100 * flare_intensity)
                    streak_color = (255, 220, 150) if direction > 0 else (150, 220, 255)
                    end_x = streak_x - direction * streak_len
                    pygame.draw.line(self.render_surface, streak_color,
                                   (streak_x, streak_y), (end_x, streak_y), 2)

            # Draw main player
            self.render_surface.blit(self.player.image, self.player.rect)
        else:
            self.render_surface.blit(self.player.image, self.player.rect)

        # Draw player damage effects (smoke, sparks, fire when damaged)
        if hasattr(self, 'player_damage_effects'):
            self.player_damage_effects.draw(self.render_surface)

        # Draw shield impact ripple effects
        if hasattr(self, 'shield_impacts'):
            self.shield_impacts.draw(self.render_surface)

        # Draw muzzle flash effects
        if hasattr(self, 'muzzle_flashes'):
            self.muzzle_flashes.draw(self.render_surface)

        # Draw particle effects
        self.particles.draw(self.render_surface)

        # Draw hit markers
        self.hit_markers.draw(self.render_surface)

        # Draw damage numbers
        if self.settings.get('show_damage_numbers', True):
            self.damage_numbers.draw(self.render_surface)

        # Draw combo pulse effect
        self.combo_effects.draw_pulse(self.render_surface)

        # Draw berserk score popups
        self.berserk.draw_popups(self.render_surface, self.font_small, self.font_large)

        # Draw danger zone circles (optional visual aid for berserk system)
        if hasattr(self, 'show_danger_zones') and self.show_danger_zones:
            self.berserk.draw_danger_zones(self.render_surface,
                (self.player.rect.centerx, self.player.rect.centery), alpha=30)

        # Draw boss health bar if fighting a boss
        self.draw_boss_health_bar()

        # Draw HUD
        self.draw_hud()

        # Draw tutorial overlay
        if self.tutorial.active:
            self.tutorial.draw(self.render_surface, self.font, self.font_small, self.font_large)

        # Draw message
        if self.message_timer > 0:
            msg_y = SCREEN_HEIGHT // 3
            cx = SCREEN_WIDTH // 2

            # Get faction color for accent
            faction_color = FACTIONS[self.selected_faction]['color_primary']

            # Calculate fade alpha based on timer
            fade_alpha = min(255, self.message_timer * 4)

            # Draw subtitle box if present (story text)
            if self.message_subtitle:
                # Wrap text first to calculate box size
                words = self.message_subtitle.split()
                lines = []
                current_line = ""
                max_width = SCREEN_WIDTH - 300

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    test_surf = self.font_small.render(test_line, True, (200, 200, 200))
                    if test_surf.get_width() < max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            lines.append(current_line)
                        current_line = word
                if current_line:
                    lines.append(current_line)

                # Draw semi-transparent background box
                box_width = max_width + 60
                box_height = 50 + len(lines[:3]) * 24
                box_x = cx - box_width // 2
                box_y = msg_y - 20

                box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
                box_surf.fill((15, 15, 25, int(180 * fade_alpha / 255)))
                pygame.draw.rect(box_surf, (*faction_color[:3], int(120 * fade_alpha / 255)),
                               (0, 0, box_width, box_height), 2, border_radius=8)
                self.render_surface.blit(box_surf, (box_x, box_y))

                # Faction accent line at top
                line_y = box_y + 2
                pygame.draw.line(self.render_surface, (*faction_color[:3], int(200 * fade_alpha / 255)),
                               (box_x + 20, line_y), (box_x + box_width - 20, line_y), 2)

            # Stage name (main message)
            text = self.font_large.render(self.message, True, (255, 255, 255))
            rect = text.get_rect(center=(cx, msg_y))
            self.render_surface.blit(text, rect)

            # Draw subtitle lines
            if self.message_subtitle:
                subtitle_y = msg_y + 40
                for line in lines[:3]:  # Max 3 lines
                    subtitle_text = self.font_small.render(line, True, (180, 180, 180))
                    subtitle_rect = subtitle_text.get_rect(center=(cx, subtitle_y))
                    self.render_surface.blit(subtitle_text, subtitle_rect)
                    subtitle_y += 24

    def _draw_player_powerup_glow(self):
        """Draw glow effects around player for active powerups"""
        now = pygame.time.get_ticks()
        active_effects = []

        # Check each timed powerup and assign colors
        if now < self.player.invulnerable_until:
            active_effects.append((255, 215, 0))    # Gold
        if now < self.player.double_damage_until:
            active_effects.append((255, 80, 80))    # Red
        if now < self.player.rapid_fire_until:
            active_effects.append((255, 150, 50))   # Orange
        if now < self.player.overdrive_until:
            active_effects.append((255, 255, 100))  # Yellow
        if now < self.player.shield_boost_until:
            active_effects.append((100, 180, 255))  # Blue
        if now < self.player.magnet_until:
            active_effects.append((180, 100, 255))  # Purple

        if not active_effects:
            return

        # Pulsing effect
        pulse = 0.6 + 0.4 * math.sin(now * 0.008)

        cx, cy = self.player.rect.center

        # Draw layered glows for each active effect
        for i, color in enumerate(active_effects):
            # Outer glow radius varies by effect index
            base_radius = 35 + i * 8
            radius = int(base_radius * pulse)
            alpha = int(60 * pulse)

            # Create glow surface
            glow_size = radius * 2 + 20
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)

            # Draw multiple circles for gradient glow effect
            for r in range(radius, 5, -5):
                circle_alpha = int(alpha * (r / radius))
                glow_color = (*color, circle_alpha)
                pygame.draw.circle(glow_surf, glow_color,
                                 (glow_size // 2, glow_size // 2), r)

            # Blit glow centered on player
            glow_rect = glow_surf.get_rect(center=(cx, cy))
            self.render_surface.blit(glow_surf, glow_rect)

        # Invulnerability already shown by gold glow - no additional outline needed

        # === JAGUAR FRONTAL SHIELD VISUAL ===
        if hasattr(self.player, 'is_frontal_shield_active') and self.player.is_frontal_shield_active():
            now = pygame.time.get_ticks()
            pulse = 0.7 + 0.3 * math.sin(now * 0.015)
            fast_pulse = 0.8 + 0.2 * math.sin(now * 0.04)
            shield_pct = self.player.get_frontal_shield_percent()
            is_bubble = getattr(self.player, 'shield_bubble_mode', False)

            px, py = self.player.rect.center

            if is_bubble:
                # === FULL 360° SHIELD BUBBLE ===
                bubble_radius = 55
                surf_size = bubble_radius * 2 + 40
                shield_surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                cx, cy = surf_size // 2, surf_size // 2

                # Outer glow layers
                for i in range(10, 0, -1):
                    alpha = int(20 * pulse * i / 10 * shield_pct)
                    r = bubble_radius + i * 3
                    pygame.draw.circle(shield_surf, (60, 140, 255, alpha), (cx, cy), r, 3)

                # Main bubble (semi-transparent fill)
                bubble_fill = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                pygame.draw.circle(bubble_fill, (80, 160, 255, int(40 * shield_pct)), (cx, cy), bubble_radius)
                shield_surf.blit(bubble_fill, (0, 0))

                # Inner rings
                for i in range(5, 0, -1):
                    alpha = int(60 * pulse * i / 5 * shield_pct)
                    r = bubble_radius - i * 3
                    if r > 10:
                        pygame.draw.circle(shield_surf, (100 + i * 20, 180 + i * 10, 255, alpha), (cx, cy), r, 2)

                # Bright edge
                pygame.draw.circle(shield_surf, (120, 210, 255, int(200 * fast_pulse * shield_pct)),
                                 (cx, cy), bubble_radius, 3)

                # Energy ripples (expanding circles)
                ripple_phase = (now * 0.15) % 30
                for r_offset in range(0, 60, 30):
                    r = int((ripple_phase + r_offset) % 60)
                    if r < bubble_radius:
                        ripple_alpha = int(80 * (1 - r / bubble_radius) * shield_pct)
                        pygame.draw.circle(shield_surf, (150, 220, 255, ripple_alpha), (cx, cy), bubble_radius - r, 1)

                # Hexagonal energy pattern
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    line_pulse = 0.6 + 0.4 * math.sin(now * 0.02 + angle * 0.05)
                    x1 = cx + int((bubble_radius - 10) * math.cos(rad))
                    y1 = cy + int((bubble_radius - 10) * math.sin(rad))
                    x2 = cx + int((bubble_radius + 5) * math.cos(rad))
                    y2 = cy + int((bubble_radius + 5) * math.sin(rad))
                    pygame.draw.line(shield_surf, (180, 230, 255, int(100 * line_pulse * shield_pct)),
                                   (x1, y1), (x2, y2), 2)

                # Edge sparkles
                if random.random() < 0.4 * shield_pct:
                    spark_angle = random.uniform(0, math.pi * 2)
                    sx = cx + int(bubble_radius * math.cos(spark_angle))
                    sy = cy + int(bubble_radius * math.sin(spark_angle))
                    pygame.draw.circle(shield_surf, (255, 255, 255, 220), (sx, sy), random.randint(2, 4))

                # Center energy core
                core_alpha = int(100 * pulse * shield_pct)
                pygame.draw.circle(shield_surf, (120, 200, 255, core_alpha), (cx, cy), 15)
                pygame.draw.circle(shield_surf, (200, 240, 255, int(core_alpha * 0.7)), (cx, cy), 8)

                # Blit centered on player
                shield_rect = shield_surf.get_rect(center=(px, py))
                self.render_surface.blit(shield_surf, shield_rect)

            else:
                # === FRONTAL ARC SHIELD ===
                arc_width = 130
                arc_height = 90
                py_arc = self.player.rect.top - 15

                shield_surf = pygame.Surface((arc_width + 60, arc_height + 40), pygame.SRCALPHA)
                cx, cy = (arc_width + 60) // 2, arc_height + 10
                arc_rect = pygame.Rect(cx - arc_width // 2, cy - arc_height, arc_width, arc_height * 2)

                # Outer glow
                for i in range(8, 0, -1):
                    alpha = int(25 * pulse * i / 8 * shield_pct)
                    expand = i * 3
                    glow_rect = pygame.Rect(arc_rect.x - expand, arc_rect.y - expand,
                                           arc_rect.width + expand * 2, arc_rect.height + expand * 2)
                    pygame.draw.arc(shield_surf, (60, 120, 255, alpha), glow_rect,
                                  math.radians(180), math.radians(360), 4)

                # Inner arcs
                for i in range(5, 0, -1):
                    alpha = int(50 * pulse * i / 5 * shield_pct)
                    pygame.draw.arc(shield_surf, (80 + i * 20, 160 + i * 15, 255, alpha), arc_rect,
                                  math.radians(180), math.radians(360), 2 + i)

                # Bright edge
                pygame.draw.arc(shield_surf, (120, 210, 255, int(220 * fast_pulse * shield_pct)),
                              arc_rect, math.radians(180), math.radians(360), 3)

                # Energy lines
                for angle in range(185, 356, 20):
                    rad = math.radians(angle)
                    line_pulse = 0.6 + 0.4 * math.sin(now * 0.02 + angle * 0.1)
                    x1 = cx + int((arc_width // 2 - 15) * math.cos(rad))
                    y1 = cy + int((arc_height - 15) * math.sin(rad))
                    x2 = cx + int((arc_width // 2 + 8) * math.cos(rad))
                    y2 = cy + int((arc_height + 8) * math.sin(rad))
                    pygame.draw.line(shield_surf, (180, 230, 255, int(100 * line_pulse * shield_pct)),
                                   (x1, y1), (x2, y2), 2)

                shield_rect = shield_surf.get_rect(center=(px, py_arc))
                self.render_surface.blit(shield_surf, shield_rect)

    def draw_hud(self):
        """Draw EVE-style heads-up display with circular capacitor and status arcs"""
        # HUD mode: 0=full, 1=minimal (health only), 2=off
        if self.hud_mode == 2:
            return  # HUD off

        # EVE-style status panel - CENTER BOTTOM for easy reference
        cx = SCREEN_WIDTH // 2  # Center of screen
        cy = SCREEN_HEIGHT - 75  # Near bottom

        # Draw EVE-style status panel
        self._draw_eve_status_panel(cx, cy)

        # Heat warning symbol (熱) above HUD when at 75%+ heat
        heat_pct = self.player.heat / self.player.max_heat
        if heat_pct >= 0.75:
            self._draw_heat_warning_symbol(cx, cy - 55, heat_pct)

        # Minimal HUD mode: only show status panel and score
        if self.hud_mode == 1:
            # Just draw score on right side
            score_text = self.font.render(f"Score: {self.player.score:,}", True, COLOR_TEXT)
            self.render_surface.blit(score_text, (SCREEN_WIDTH - 160, 10))
            return

        # Faction indicator - top left corner
        self._draw_faction_indicator()

        # Vertical thrust cooldown bar (left side of status panel)
        self._draw_thrust_gauge(cx - 75, cy)

        # Ammo and rockets - positioned bottom left
        ammo_x = 10
        ammo_y = SCREEN_HEIGHT - 100

        # Ammo indicator
        ammo = AMMO_TYPES[self.player.current_ammo]
        pygame.draw.rect(self.render_surface, ammo['color'], (ammo_x, ammo_y, 14, 14))
        pygame.draw.rect(self.render_surface, (200, 200, 200), (ammo_x, ammo_y, 14, 14), 1)
        ammo_text = self.font_small.render(ammo['name'][:6], True, ammo['color'])
        self.render_surface.blit(ammo_text, (ammo_x + 18, ammo_y))

        # Rockets - visual dots
        ammo_y += 18
        rocket_count = min(self.player.rockets, 16)  # Cap display
        for i in range(rocket_count):
            color = (100, 180, 255) if getattr(self.player, 'ship_class', 'Rifter') == 'Jaguar' else (255, 120, 60)
            pygame.draw.circle(self.render_surface, color, (ammo_x + 5 + (i % 8) * 10, ammo_y + 5 + (i // 8) * 10), 3)

        # Bomb indicator
        ammo_y += 25
        for i in range(self.player.bombs):
            pygame.draw.circle(self.render_surface, (255, 80, 180), (ammo_x + 5 + i * 12, ammo_y), 4)
            pygame.draw.circle(self.render_surface, (255, 150, 200), (ammo_x + 5 + i * 12, ammo_y), 2)

        # Wingman gauge (Rifter only) - polished EVE-style progress bar
        if not self.player.is_wolf and not self.player.is_jaguar:
            ammo_y += 22
            gauge_width = 90
            gauge_height = 12
            progress = self.kill_counter / self.kills_per_wingman

            # Outer glow when near full
            if progress > 0.7:
                glow_surf = pygame.Surface((gauge_width + 10, gauge_height + 10), pygame.SRCALPHA)
                glow_alpha = int(60 + 40 * math.sin(pygame.time.get_ticks() * 0.008))
                pygame.draw.rect(glow_surf, (220, 180, 80, glow_alpha), (0, 0, gauge_width + 10, gauge_height + 10), border_radius=4)
                self.render_surface.blit(glow_surf, (ammo_x - 5, ammo_y - 5))

            # Background with gradient look
            pygame.draw.rect(self.render_surface, (25, 25, 35), (ammo_x, ammo_y, gauge_width, gauge_height), border_radius=3)
            pygame.draw.rect(self.render_surface, (35, 35, 45), (ammo_x + 1, ammo_y + 1, gauge_width - 2, gauge_height - 2), border_radius=2)

            # Segmented fill (15 segments for 15 kills)
            segment_width = (gauge_width - 4) / self.kills_per_wingman
            for i in range(self.kill_counter):
                seg_x = ammo_x + 2 + i * segment_width
                # Gradient color from copper to gold
                t = i / self.kills_per_wingman
                r = int(160 + 60 * t)
                g = int(100 + 80 * t)
                b = int(40 + 40 * t)
                pygame.draw.rect(self.render_surface, (r, g, b),
                               (seg_x, ammo_y + 2, segment_width - 1, gauge_height - 4), border_radius=1)

            # Border
            pygame.draw.rect(self.render_surface, (120, 100, 60), (ammo_x, ammo_y, gauge_width, gauge_height), 1, border_radius=3)

            # Label with icon
            label_color = (220, 180, 100) if progress > 0.5 else (150, 130, 90)
            wingman_label = self.font_small.render("WINGMAN", True, label_color)
            self.render_surface.blit(wingman_label, (ammo_x, ammo_y - 14))
            # Kill count on right
            count_label = self.font_small.render(f"{self.kill_counter}/{self.kills_per_wingman}", True, label_color)
            self.render_surface.blit(count_label, (ammo_x + gauge_width - 25, ammo_y - 14))

            # Active wingman count (ship icons)
            if len(self.wingmen) > 0:
                icon_x = ammo_x + gauge_width + 8
                icon_y = ammo_y + 2
                for i in range(len(self.wingmen)):
                    # Mini ship icon
                    pygame.draw.polygon(self.render_surface, (200, 150, 80),
                                       [(icon_x + i*12, icon_y), (icon_x + 4 + i*12, icon_y + 8), (icon_x - 4 + i*12, icon_y + 8)])
                    pygame.draw.polygon(self.render_surface, (255, 200, 100),
                                       [(icon_x + i*12, icon_y + 1), (icon_x + 2 + i*12, icon_y + 6), (icon_x - 2 + i*12, icon_y + 6)])

        # Active powerup indicators - above center HUD
        now = pygame.time.get_ticks()
        active_powerups = []

        if now < self.player.invulnerable_until:
            remaining = (self.player.invulnerable_until - now) / 1000
            active_powerups.append(('INVULN', (255, 215, 0), remaining))
        if now < self.player.double_damage_until:
            remaining = (self.player.double_damage_until - now) / 1000
            active_powerups.append(('DMG x2', (255, 100, 100), remaining))
        if now < self.player.rapid_fire_until:
            remaining = (self.player.rapid_fire_until - now) / 1000
            active_powerups.append(('RAPID', (255, 150, 50), remaining))
        if now < self.player.overdrive_until:
            remaining = (self.player.overdrive_until - now) / 1000
            active_powerups.append(('SPEED', (255, 255, 100), remaining))
        if now < self.player.shield_boost_until:
            remaining = (self.player.shield_boost_until - now) / 1000
            active_powerups.append(('SHIELD', (150, 200, 255), remaining))
        if now < self.player.magnet_until:
            remaining = (self.player.magnet_until - now) / 1000
            active_powerups.append(('MAGNET', (200, 200, 255), remaining))

        # Draw powerups as EVE-style module icons above HUD
        if active_powerups:
            powerup_y = SCREEN_HEIGHT - 175  # Above the capacitor gauge
            icon_size = 24
            spacing = 28
            total_width = len(active_powerups) * spacing
            powerup_x = (SCREEN_WIDTH - total_width) // 2 + spacing // 2
            for name, color, remaining in active_powerups:
                # EVE-style square module icon
                icon_rect = pygame.Rect(powerup_x - icon_size//2, powerup_y - icon_size//2, icon_size, icon_size)

                # Pulsing glow
                pulse = 0.5 + 0.5 * math.sin(now * 0.008)
                glow_surf = pygame.Surface((icon_size + 8, icon_size + 8), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*color, int(50 * pulse)), (0, 0, icon_size + 8, icon_size + 8), border_radius=4)
                self.render_surface.blit(glow_surf, (icon_rect.x - 4, icon_rect.y - 4))

                # Icon background
                pygame.draw.rect(self.render_surface, (20, 25, 35), icon_rect, border_radius=3)
                pygame.draw.rect(self.render_surface, color, icon_rect, 2, border_radius=3)

                # Inner fill based on remaining time (like EVE module cycle)
                fill_height = int(icon_size * min(remaining / 5, 1.0))  # 5 seconds max display
                if fill_height > 0:
                    fill_rect = pygame.Rect(icon_rect.x + 2, icon_rect.y + icon_size - fill_height - 2,
                                           icon_size - 4, fill_height)
                    pygame.draw.rect(self.render_surface, (*color, 180), fill_rect, border_radius=2)

                # Small icon symbol in center
                symbol = name[0]  # First letter
                sym_text = self.font_small.render(symbol, True, color)
                sym_rect = sym_text.get_rect(center=(powerup_x, powerup_y))
                self.render_surface.blit(sym_text, sym_rect)

                powerup_x += spacing

        # Right side - score and wave info
        x = SCREEN_WIDTH - 130
        y = 10

        # Score
        text = self.font.render(f"{self.player.score:,}", True, COLOR_TEXT)
        self.render_surface.blit(text, (x, y))

        # Refugees
        y += 22
        text = self.font_small.render(f"{self.player.refugees} rescued", True, (100, 255, 100))
        self.render_surface.blit(text, (x, y))

        # Wave/Stage
        y += 20
        if self.game_mode == 'endless':
            wave_color = (255, 150, 100) if self.endless_wave % 10 == 0 else (200, 180, 150)
            text = self.font_small.render(f"Wave {self.endless_wave}", True, wave_color)
            self.render_surface.blit(text, (x, y))
        elif self.game_mode == 'abyssal':
            # Abyssal-specific HUD
            self._draw_abyssal_hud()
        elif self.current_stage < len(self.active_stages):
            text = self.font_small.render(f"Wave {self.current_wave}/{self.active_stages[self.current_stage]['waves']}", True, (180, 180, 180))
            self.render_surface.blit(text, (x, y))

        # Berserk multiplier HUD (top right area)
        self.berserk.draw_hud(self.render_surface, SCREEN_WIDTH - 10, 80,
                              self.font_small, self.font_large)

    def _draw_eve_status_panel(self, cx, cy):
        """Draw exact EVE Online capacitor wheel replica

        EVE Layout:
        - CENTER: Capacitor "star" - yellow dashes that turn grey when depleted
        - Surrounding: Health rings - Shield (outer), Armor (middle), Hull (inner)
        - Health rings turn red as damage accumulates
        """
        now = pygame.time.get_ticks()

        # EVE-accurate dimensions
        outer_radius = 58        # Total wheel size
        cap_radius = 28          # Central capacitor star
        shield_radius = 54       # Shield ring (outermost)
        armor_radius = 46        # Armor ring
        hull_radius = 38         # Hull ring
        ring_thickness = 6       # Health ring thickness

        # Panel surface
        panel_size = outer_radius * 2 + 30
        panel_surf = pygame.Surface((panel_size, panel_size), pygame.SRCALPHA)
        panel_cx, panel_cy = panel_size // 2, panel_size // 2

        # Calculate percentages
        shield_pct = self.player.shields / max(self.player.max_shields, 1)
        armor_pct = self.player.armor / max(self.player.max_armor, 1)
        hull_pct = self.player.hull / max(self.player.max_hull, 1)
        heat_pct = self.player.heat / self.player.max_heat
        cap_pct = 1.0 - heat_pct  # Capacitor = inverse of heat

        # === BACKGROUND (dark circle) ===
        pygame.draw.circle(panel_surf, (12, 14, 18), (panel_cx, panel_cy), outer_radius)
        pygame.draw.circle(panel_surf, (30, 35, 45), (panel_cx, panel_cy), outer_radius, 2)

        # === HEALTH RINGS (outer to inner: Shield -> Armor -> Hull) ===
        # EVE shows damage as RED filling the empty portion
        self._draw_eve_health_arc(panel_surf, panel_cx, panel_cy, shield_radius,
                                  ring_thickness, shield_pct, (64, 156, 255), now)
        self._draw_eve_health_arc(panel_surf, panel_cx, panel_cy, armor_radius,
                                  ring_thickness, armor_pct, (255, 176, 48), now)
        self._draw_eve_health_arc(panel_surf, panel_cx, panel_cy, hull_radius,
                                  ring_thickness, hull_pct, (160, 165, 175), now,
                                  critical=(hull_pct < 0.25))

        # === CENTRAL CAPACITOR STAR (EVE's iconic yellow dashes) ===
        self._draw_eve_capacitor_star(panel_surf, panel_cx, panel_cy, cap_radius,
                                      cap_pct, now)

        # === CENTER HEAT DISPLAY ===
        self._draw_eve_center_heat(panel_surf, panel_cx, panel_cy, 14, heat_pct, now)

        # === THRUST COOLDOWN (thin arc at bottom) ===
        thrust_cd = getattr(self.player, 'thrust_cooldown', 0)
        thrust_max = getattr(self.player, 'thrust_cooldown_time', 90)
        if thrust_cd > 0:
            thrust_pct = 1.0 - (thrust_cd / thrust_max)
            self._draw_eve_thrust_arc(panel_surf, panel_cx, panel_cy,
                                      outer_radius + 4, thrust_pct)

        # Blit to main surface
        self.render_surface.blit(panel_surf, (cx - panel_cx, cy - panel_cy))

    def _draw_health_ring(self, surface, cx, cy, radius, thickness, fill_pct, fill_color, bg_color, label, now):
        """Draw a polished health ring with smooth anti-aliased segments"""
        num_segments = 32  # More segments for smoother look
        segment_gap = 2.5  # degrees - smaller gap for cleaner look
        segment_arc = (360 / num_segments) - segment_gap

        # Draw background segments (empty state)
        for i in range(num_segments):
            angle_start = -90 + i * (360 / num_segments)
            self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                     angle_start, segment_arc, bg_color, 0.6)

        # Draw filled segments
        filled_segments = int(fill_pct * num_segments)
        partial_fill = (fill_pct * num_segments) - filled_segments

        for i in range(filled_segments):
            angle_start = -90 + i * (360 / num_segments)
            # Brighter inner edge for EVE-style gradient
            self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                     angle_start, segment_arc, fill_color, 1.0, glow=True)

        # Partial segment (dimmer)
        if partial_fill > 0.1 and filled_segments < num_segments:
            angle_start = -90 + filled_segments * (360 / num_segments)
            partial_arc = segment_arc * partial_fill
            dim_color = (int(fill_color[0] * 0.5), int(fill_color[1] * 0.5), int(fill_color[2] * 0.5))
            self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                     angle_start, partial_arc, dim_color, 0.8)

        # Critical hull warning flash
        if label == "H" and fill_pct < 0.25 and fill_pct > 0:
            pulse = 0.5 + 0.5 * math.sin(now * 0.012)
            if pulse > 0.7:
                flash_color = (255, 80, 80)
                for i in range(min(filled_segments + 1, num_segments)):
                    angle_start = -90 + i * (360 / num_segments)
                    self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                             angle_start, segment_arc, flash_color, pulse)

    def _draw_smooth_segment(self, surface, cx, cy, radius, thickness, angle_start, arc_span, color, alpha=1.0, glow=False):
        """Draw a smooth anti-aliased ring segment using polygon"""
        if arc_span <= 0:
            return

        # Build polygon points for the segment
        outer_r = radius
        inner_r = radius - thickness
        steps = max(3, int(arc_span / 3))  # More steps for smoother curve

        points = []

        # Outer arc (clockwise)
        for i in range(steps + 1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            x = cx + outer_r * math.cos(angle)
            y = cy + outer_r * math.sin(angle)
            points.append((x, y))

        # Inner arc (counter-clockwise)
        for i in range(steps, -1, -1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            x = cx + inner_r * math.cos(angle)
            y = cy + inner_r * math.sin(angle)
            points.append((x, y))

        if len(points) >= 3:
            # Draw the segment with alpha
            seg_color = (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha))
            pygame.draw.polygon(surface, seg_color, points)

            # Add bright edge highlight for EVE-style depth
            if glow and alpha > 0.8:
                highlight = (min(color[0] + 60, 255), min(color[1] + 60, 255), min(color[2] + 60, 255))
                # Inner edge highlight
                for i in range(steps):
                    angle1 = math.radians(angle_start + (arc_span * i / steps))
                    angle2 = math.radians(angle_start + (arc_span * (i + 1) / steps))
                    x1 = cx + inner_r * math.cos(angle1)
                    y1 = cy + inner_r * math.sin(angle1)
                    x2 = cx + inner_r * math.cos(angle2)
                    y2 = cy + inner_r * math.sin(angle2)
                    pygame.draw.line(surface, highlight, (x1, y1), (x2, y2), 1)

    def _draw_wheel_glow(self, surface, cx, cy, radius, shield_pct, armor_pct, hull_pct):
        """Draw subtle ambient glow around the capacitor wheel"""
        # Determine dominant status color for glow
        if hull_pct < 0.25:
            glow_color = (180, 40, 40)  # Red danger glow
            intensity = 0.4
        elif armor_pct < 0.5 and shield_pct <= 0:
            glow_color = (180, 120, 30)  # Orange warning
            intensity = 0.25
        elif shield_pct > 0.5:
            glow_color = (40, 100, 180)  # Blue healthy
            intensity = 0.15
        else:
            glow_color = (60, 80, 100)  # Neutral
            intensity = 0.1

        # Draw soft radial glow (scaled to wheel size)
        glow_depth = max(8, int(radius * 0.25))
        for r in range(int(radius), int(radius - glow_depth), -2):
            alpha = int(intensity * 255 * (radius - r) / glow_depth)
            glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, alpha), (r, r), r)
            surface.blit(glow_surf, (cx - r, cy - r))

    def _draw_wheel_labels(self, surface, cx, cy, radius, shield_pct, armor_pct, hull_pct):
        """Draw percentage labels around the wheel"""
        # Position labels at cardinal points outside the wheel (scaled to wheel size)
        label_r = radius + 14

        # Shield percentage (top)
        shield_text = f"{int(shield_pct * 100)}%"
        shield_color = (64, 156, 255) if shield_pct > 0.25 else (100, 100, 120)
        text = self.font_small.render(shield_text, True, shield_color)
        text_rect = text.get_rect(center=(cx, cy - label_r))
        surface.blit(text, text_rect)

        # Armor percentage (right)
        armor_text = f"{int(armor_pct * 100)}%"
        armor_color = (255, 176, 48) if armor_pct > 0.25 else (100, 100, 120)
        text = self.font_small.render(armor_text, True, armor_color)
        text_rect = text.get_rect(center=(cx + label_r, cy))
        surface.blit(text, text_rect)

        # Hull percentage (left)
        hull_text = f"{int(hull_pct * 100)}%"
        if hull_pct < 0.25:
            hull_color = (255, 80, 80)
        elif hull_pct > 0.5:
            hull_color = (160, 165, 175)
        else:
            hull_color = (180, 120, 80)
        text = self.font_small.render(hull_text, True, hull_color)
        text_rect = text.get_rect(center=(cx - label_r, cy))
        surface.blit(text, text_rect)

    def _draw_heat_center(self, surface, cx, cy, radius, heat_pct, now):
        """Draw the polished central heat/capacitor gauge"""
        heat_warning = getattr(self.player, 'heat_warning', False)
        is_overheated = getattr(self.player, 'is_overheated', False)

        # Outer ring (border)
        border_color = (50, 60, 80)
        if is_overheated:
            pulse = 0.5 + 0.5 * math.sin(now * 0.02)
            border_color = (int(200 * pulse), int(50 * pulse), int(50 * pulse))
        elif heat_warning:
            pulse = 0.5 + 0.5 * math.sin(now * 0.015)
            border_color = (int(180 * pulse), int(100 * pulse), 30)

        pygame.draw.circle(surface, border_color, (cx, cy), radius, 2)

        # Background circle with subtle gradient
        for r in range(radius - 2, 0, -1):
            t = r / (radius - 2)
            if is_overheated:
                pulse = 0.5 + 0.5 * math.sin(now * 0.02)
                bg = (int(40 * pulse + 15), 10, 10)
            else:
                bg = (int(12 + 8 * t), int(15 + 10 * t), int(22 + 12 * t))
            pygame.draw.circle(surface, bg, (cx, cy), r)

        # Heat fill (rises from bottom like capacitor)
        if heat_pct > 0.01:
            fill_height = int((radius - 3) * 2 * heat_pct)

            # Create clipping surface
            heat_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)

            # Color gradient based on heat level (EVE style)
            if heat_pct < 0.4:
                heat_color = (80, 180, 120)   # Green - safe
            elif heat_pct < 0.65:
                heat_color = (200, 200, 60)   # Yellow - caution
            elif heat_pct < 0.85:
                heat_color = (255, 140, 40)   # Orange - warning
            else:
                heat_color = (255, 60, 40)    # Red - critical

            # Draw gradient heat fill
            for y in range(fill_height):
                progress = y / max(fill_height, 1)
                row_y = radius * 2 - fill_height + y
                # Gradient from darker at bottom to brighter at top
                row_color = (int(heat_color[0] * (0.6 + 0.4 * progress)),
                            int(heat_color[1] * (0.6 + 0.4 * progress)),
                            int(heat_color[2] * (0.6 + 0.4 * progress)),
                            200)
                pygame.draw.line(heat_surf, row_color, (0, row_y), (radius * 2, row_y))

            # Mask to circle
            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (radius, radius), radius - 3)
            heat_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(heat_surf, (cx - radius, cy - radius))

            # Heat level line indicator
            line_y = cy + (radius - 3) - fill_height
            line_color = (min(heat_color[0] + 50, 255), min(heat_color[1] + 50, 255), min(heat_color[2] + 50, 255))
            half_width = int(math.sqrt(max(0, (radius - 3)**2 - (fill_height - (radius - 3))**2)))
            if half_width > 2:
                pygame.draw.line(surface, line_color, (cx - half_width, line_y), (cx + half_width, line_y), 2)

        # Center text
        if is_overheated:
            pulse = 0.7 + 0.3 * math.sin(now * 0.02)
            text_color = (255, int(80 * pulse), int(80 * pulse))
            label = "HOT"
        elif heat_warning:
            pulse = 0.8 + 0.2 * math.sin(now * 0.015)
            text_color = (int(255 * pulse), int(180 * pulse), 50)
            label = f"{int(heat_pct * 100)}"
        else:
            text_color = (180, 190, 210)
            label = f"{int(heat_pct * 100)}"

        text = self.font_small.render(label, True, text_color)
        text_rect = text.get_rect(center=(cx, cy))
        surface.blit(text, text_rect)

    def _draw_thrust_indicator(self, surface, cx, cy, radius, fill_pct, now):
        """Draw polished thrust cooldown arc at bottom of wheel"""
        arc_span = 50  # degrees
        thickness = 3
        start_angle = 90 - arc_span / 2
        90 + arc_span / 2

        # Background arc
        bg_color = (25, 30, 40)
        self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                 start_angle, arc_span, bg_color, 0.8)

        # Fill arc based on cooldown
        if fill_pct > 0.05:
            filled_span = arc_span * fill_pct
            # Cyan/blue color for thrust - pulses when nearly ready
            if fill_pct > 0.9:
                pulse = 0.8 + 0.2 * math.sin(now * 0.02)
                thrust_color = (int(100 * pulse), int(220 * pulse), 255)
            else:
                thrust_color = (60, 180, 240)

            self._draw_smooth_segment(surface, cx, cy, radius, thickness,
                                     start_angle, filled_span, thrust_color, 1.0, glow=True)

        # "THRUST" label below (only when recharging)
        if fill_pct < 0.99:
            label_color = (50, 120, 180) if fill_pct < 0.5 else (80, 180, 240)
            text = self.font_small.render("THRUST", True, label_color)
            text_rect = text.get_rect(center=(cx, cy + radius + 14))
            surface.blit(text, text_rect)

    # =========================================================================
    # NEW EVE-AUTHENTIC CAPACITOR WHEEL METHODS
    # =========================================================================

    def _draw_capacitor_ring(self, surface, cx, cy, radius, thickness, cap_pct, now):
        """Draw EVE-authentic capacitor ring with glowing gold cells

        In EVE, capacitor shows as bright gold/yellow cells that dim to grey
        as capacitor depletes. Cells are arranged around the ring.
        """
        num_cells = 24  # EVE typically has ~24 cells
        cell_gap = 4    # degrees between cells
        cell_arc = (360 / num_cells) - cell_gap

        # Calculate how many cells are "charged"
        charged_cells = int(cap_pct * num_cells)
        partial_charge = (cap_pct * num_cells) - charged_cells

        for i in range(num_cells):
            # Cells start from top (-90 degrees) and go clockwise
            angle_start = -90 + i * (360 / num_cells)

            # Determine cell state
            if i < charged_cells:
                # Fully charged cell - bright gold with glow
                cell_brightness = 1.0
                is_charged = True
            elif i == charged_cells and partial_charge > 0.1:
                # Partially charged cell
                cell_brightness = partial_charge
                is_charged = True
            else:
                # Depleted cell - dark grey
                cell_brightness = 0.0
                is_charged = False

            self._draw_cap_cell(surface, cx, cy, radius, thickness,
                               angle_start, cell_arc, cell_brightness, is_charged)

        # Low capacitor warning pulse
        if cap_pct < 0.25:
            pulse = 0.3 + 0.7 * abs(math.sin(now * 0.008))
            # Draw warning glow on remaining cells
            for i in range(charged_cells + 1):
                angle_start = -90 + i * (360 / num_cells)
                self._draw_cap_warning(surface, cx, cy, radius, thickness,
                                       angle_start, cell_arc, pulse)

    def _draw_cap_cell(self, surface, cx, cy, radius, thickness,
                       angle_start, arc_span, brightness, is_charged):
        """Draw a single capacitor cell with EVE-style appearance"""
        outer_r = radius
        inner_r = radius - thickness
        steps = max(4, int(arc_span / 4))

        # Build cell polygon
        points = []
        for i in range(steps + 1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + outer_r * math.cos(angle),
                          cy + outer_r * math.sin(angle)))
        for i in range(steps, -1, -1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + inner_r * math.cos(angle),
                          cy + inner_r * math.sin(angle)))

        if len(points) < 3:
            return

        if is_charged and brightness > 0:
            # Charged cell: Gold gradient from bright center to darker edge
            # Base gold color with brightness adjustment
            gold_r = int(200 + 55 * brightness)
            gold_g = int(160 + 60 * brightness)
            gold_b = int(40 + 30 * brightness)
            cell_color = (min(255, gold_r), min(255, gold_g), gold_b)

            # Draw cell body
            pygame.draw.polygon(surface, cell_color, points)

            # Inner glow (brighter toward center)
            glow_color = (min(255, gold_r + 40), min(255, gold_g + 30), min(255, gold_b + 20))
            mid_r = (outer_r + inner_r) / 2
            glow_points = []
            for i in range(steps + 1):
                angle = math.radians(angle_start + (arc_span * i / steps))
                glow_points.append((cx + mid_r * math.cos(angle),
                                   cy + mid_r * math.sin(angle)))
            if len(glow_points) >= 2:
                pygame.draw.lines(surface, glow_color, False, glow_points, 2)

            # Outer edge highlight
            edge_color = (255, 240, 180)
            for i in range(steps):
                angle1 = math.radians(angle_start + (arc_span * i / steps))
                angle2 = math.radians(angle_start + (arc_span * (i + 1) / steps))
                pygame.draw.line(surface, edge_color,
                               (cx + outer_r * math.cos(angle1), cy + outer_r * math.sin(angle1)),
                               (cx + outer_r * math.cos(angle2), cy + outer_r * math.sin(angle2)), 1)
        else:
            # Depleted cell: Dark grey
            cell_color = (35, 38, 45)
            pygame.draw.polygon(surface, cell_color, points)
            # Subtle edge
            edge_color = (50, 55, 65)
            pygame.draw.polygon(surface, edge_color, points, 1)

    def _draw_cap_warning(self, surface, cx, cy, radius, thickness,
                          angle_start, arc_span, pulse):
        """Draw warning pulse overlay on low capacitor"""
        outer_r = radius + 2
        inner_r = radius - thickness - 2
        steps = max(4, int(arc_span / 4))

        points = []
        for i in range(steps + 1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + outer_r * math.cos(angle),
                          cy + outer_r * math.sin(angle)))
        for i in range(steps, -1, -1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + inner_r * math.cos(angle),
                          cy + inner_r * math.sin(angle)))

        if len(points) >= 3:
            warning_color = (int(200 * pulse), int(60 * pulse), int(30 * pulse))
            pygame.draw.polygon(surface, warning_color, points, 2)

    def _draw_eve_health_ring(self, surface, cx, cy, radius, thickness, fill_pct,
                               healthy_color, damage_color, bg_color, now, critical=False):
        """Draw EVE-style health ring

        In EVE, health rings show full in their color, and damage appears as
        red coloring from the "empty" portion. The ring doesn't deplete from
        one end - instead, damage overlays the missing health portion.
        """
        num_segments = 36
        segment_gap = 2.0
        segment_arc = (360 / num_segments) - segment_gap

        for i in range(num_segments):
            angle_start = -90 + i * (360 / num_segments)

            # Calculate if this segment is "healthy" or "damaged"
            segment_pos = (i + 0.5) / num_segments
            is_healthy = segment_pos <= fill_pct

            if is_healthy:
                # Healthy segment - ring color with subtle glow
                self._draw_health_segment(surface, cx, cy, radius, thickness,
                                         angle_start, segment_arc, healthy_color, True)
            else:
                # Damaged segment - red/damage color (dimmer)
                dim_damage = (damage_color[0] // 2, damage_color[1] // 2, damage_color[2] // 2)
                self._draw_health_segment(surface, cx, cy, radius, thickness,
                                         angle_start, segment_arc, dim_damage, False)

        # Critical hull pulsing
        if critical:
            pulse = 0.4 + 0.6 * abs(math.sin(now * 0.01))
            # Pulse the damaged segments
            for i in range(num_segments):
                angle_start = -90 + i * (360 / num_segments)
                segment_pos = (i + 0.5) / num_segments
                if segment_pos > fill_pct:
                    pulse_color = (int(220 * pulse), int(40 * pulse), int(40 * pulse))
                    self._draw_health_segment(surface, cx, cy, radius, thickness,
                                             angle_start, segment_arc, pulse_color, False)

    def _draw_health_segment(self, surface, cx, cy, radius, thickness,
                             angle_start, arc_span, color, is_healthy):
        """Draw a single health ring segment"""
        outer_r = radius
        inner_r = radius - thickness
        steps = max(3, int(arc_span / 5))

        points = []
        for i in range(steps + 1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + outer_r * math.cos(angle),
                          cy + outer_r * math.sin(angle)))
        for i in range(steps, -1, -1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + inner_r * math.cos(angle),
                          cy + inner_r * math.sin(angle)))

        if len(points) < 3:
            return

        pygame.draw.polygon(surface, color, points)

        # Add inner edge highlight for healthy segments
        if is_healthy:
            highlight = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            for i in range(steps):
                angle1 = math.radians(angle_start + (arc_span * i / steps))
                angle2 = math.radians(angle_start + (arc_span * (i + 1) / steps))
                pygame.draw.line(surface, highlight,
                               (cx + inner_r * math.cos(angle1), cy + inner_r * math.sin(angle1)),
                               (cx + inner_r * math.cos(angle2), cy + inner_r * math.sin(angle2)), 1)

    def _draw_eve_center_gauge(self, surface, cx, cy, radius, heat_pct, cap_pct, now):
        """Draw EVE-style center gauge with heat as primary indicator

        The center shows:
        - Heat level as the main display (like EVE capacitor center)
        - Color changes based on heat level
        - Fills from bottom like a thermometer
        """
        is_overheated = getattr(self.player, 'is_overheated', False)
        heat_warning = getattr(self.player, 'heat_warning', False)

        # === BACKGROUND CIRCLE ===
        # Dark metallic background
        pygame.draw.circle(surface, (15, 18, 25), (cx, cy), radius)

        # === BORDER RING ===
        if is_overheated:
            pulse = 0.5 + 0.5 * math.sin(now * 0.02)
            border_color = (int(220 * pulse), int(50 * pulse), 20)
        elif heat_warning:
            pulse = 0.7 + 0.3 * math.sin(now * 0.015)
            border_color = (int(200 * pulse), int(130 * pulse), 40)
        else:
            border_color = (50, 60, 75)
        pygame.draw.circle(surface, border_color, (cx, cy), radius, 2)

        # === HEAT FILL (thermometer style, fills from bottom) ===
        if heat_pct > 0.02:
            inner_r = radius - 3
            fill_height = int(inner_r * 2 * heat_pct)

            # Heat color gradient based on level
            if heat_pct < 0.35:
                heat_color = (50, 160, 100)    # Green - cool
            elif heat_pct < 0.55:
                heat_color = (180, 180, 50)    # Yellow - warm
            elif heat_pct < 0.75:
                heat_color = (220, 130, 40)    # Orange - hot
            else:
                heat_color = (220, 50, 40)     # Red - critical

            # Create heat fill surface
            heat_surf = pygame.Surface((inner_r * 2, inner_r * 2), pygame.SRCALPHA)

            # Draw gradient fill from bottom
            for y in range(fill_height):
                row_y = inner_r * 2 - fill_height + y
                progress = y / max(fill_height, 1)
                # Gradient from darker at bottom to brighter at top
                mult = 0.6 + 0.4 * progress
                row_color = (int(heat_color[0] * mult),
                            int(heat_color[1] * mult),
                            int(heat_color[2] * mult), 220)
                pygame.draw.line(heat_surf, row_color, (0, row_y), (inner_r * 2, row_y))

            # Mask to circle
            mask = pygame.Surface((inner_r * 2, inner_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(mask, (255, 255, 255, 255), (inner_r, inner_r), inner_r)
            heat_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(heat_surf, (cx - inner_r, cy - inner_r))

            # Heat level line at top of fill
            fill_y = cy + inner_r - fill_height
            # Calculate line width at this y position
            dy = abs(fill_y - cy)
            if dy < inner_r:
                half_width = int(math.sqrt(inner_r**2 - dy**2))
                if half_width > 2:
                    line_color = (min(255, heat_color[0] + 60),
                                 min(255, heat_color[1] + 60),
                                 min(255, heat_color[2] + 60))
                    pygame.draw.line(surface, line_color,
                                   (cx - half_width, fill_y), (cx + half_width, fill_y), 2)

        # === CENTER TEXT (Heat %) ===
        if is_overheated:
            pulse = 0.7 + 0.3 * math.sin(now * 0.02)
            text_color = (255, int(60 * pulse), int(60 * pulse))
            label = "HOT"
        elif heat_pct > 0.75:
            pulse = 0.8 + 0.2 * math.sin(now * 0.015)
            text_color = (int(255 * pulse), int(120 * pulse), 40)
            label = f"{int(heat_pct * 100)}"
        elif heat_pct > 0.5:
            text_color = (200, 180, 60)
            label = f"{int(heat_pct * 100)}"
        else:
            text_color = (140, 160, 180)
            label = f"{int(heat_pct * 100)}"

        text_surf = self.font_small.render(label, True, text_color)
        text_rect = text_surf.get_rect(center=(cx, cy))
        surface.blit(text_surf, text_rect)

    def _draw_eve_glow(self, surface, cx, cy, radius, shield_pct, armor_pct, hull_pct, cap_pct):
        """Draw subtle ambient glow based on ship status"""
        # Determine glow color based on most critical status
        if hull_pct < 0.25:
            glow_color = (180, 40, 40)   # Critical - red
            intensity = 0.35
        elif cap_pct < 0.2:
            glow_color = (180, 140, 40)  # Low cap - orange
            intensity = 0.25
        elif armor_pct < 0.5 and shield_pct <= 0:
            glow_color = (180, 100, 40)  # Armor damage - orange
            intensity = 0.2
        elif shield_pct > 0.7:
            glow_color = (40, 100, 180)  # Healthy - blue
            intensity = 0.12
        else:
            glow_color = (50, 60, 80)    # Neutral
            intensity = 0.08

        # Draw soft radial glow
        glow_steps = max(6, int(radius * 0.2))
        for i in range(glow_steps):
            r = radius - i * 2
            if r <= 0:
                break
            alpha = int(intensity * 255 * (1 - i / glow_steps))
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, alpha), (r + 2, r + 2), r + 2)
            surface.blit(glow_surf, (cx - r - 2, cy - r - 2))

    def _draw_eve_thrust_arc(self, surface, cx, cy, radius, fill_pct):
        """Draw thrust cooldown indicator as thin outer arc"""
        arc_span = 60  # degrees
        start_angle = 90 - arc_span / 2  # Bottom of wheel
        thickness = 3

        # Background arc
        self._draw_arc_segment(surface, cx, cy, radius, thickness,
                              start_angle, arc_span, (25, 30, 40))

        # Fill arc
        if fill_pct > 0.02:
            fill_span = arc_span * fill_pct
            fill_color = (60, 180, 255) if fill_pct < 1.0 else (100, 220, 255)
            self._draw_arc_segment(surface, cx, cy, radius, thickness,
                                  start_angle, fill_span, fill_color)

    def _draw_arc_segment(self, surface, cx, cy, radius, thickness,
                          angle_start, arc_span, color):
        """Helper to draw a simple arc segment"""
        outer_r = radius
        inner_r = radius - thickness
        steps = max(4, int(arc_span / 5))

        points = []
        for i in range(steps + 1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + outer_r * math.cos(angle),
                          cy + outer_r * math.sin(angle)))
        for i in range(steps, -1, -1):
            angle = math.radians(angle_start + (arc_span * i / steps))
            points.append((cx + inner_r * math.cos(angle),
                          cy + inner_r * math.sin(angle)))

        if len(points) >= 3:
            pygame.draw.polygon(surface, color, points)

    # =========================================================================
    # EVE-ACCURATE CAPACITOR WHEEL METHODS
    # =========================================================================

    def _draw_eve_health_arc(self, surface, cx, cy, radius, thickness, fill_pct,
                             color, now, critical=False):
        """Draw EVE-style health ring - full ring that turns RED as health drops

        In EVE, health rings show as their color when healthy, and the
        DAMAGE portion fills with red from the empty end.
        """
        num_segments = 40
        segment_gap = 1.5
        segment_arc = (360 / num_segments) - segment_gap

        for i in range(num_segments):
            # Start from top (-90 degrees), go clockwise
            angle_start = -90 + i * (360 / num_segments)
            segment_pos = i / num_segments

            if segment_pos < fill_pct:
                # Healthy - show ring color
                seg_color = color
                # Add slight highlight
                highlight = 1.0 + 0.1 * math.sin(now * 0.003 + i * 0.2)
                seg_color = (min(255, int(color[0] * highlight)),
                           min(255, int(color[1] * highlight)),
                           min(255, int(color[2] * highlight)))
            else:
                # Damaged - show red
                if critical:
                    # Pulsing red for critical
                    pulse = 0.5 + 0.5 * math.sin(now * 0.01)
                    seg_color = (int(180 * pulse), int(30 * pulse), int(30 * pulse))
                else:
                    seg_color = (120, 25, 25)

            self._draw_arc_segment(surface, cx, cy, radius, thickness,
                                  angle_start, segment_arc, seg_color)

        # Draw ring border
        pygame.draw.circle(surface, (50, 55, 65), (cx, cy), radius, 1)
        pygame.draw.circle(surface, (40, 45, 55), (cx, cy), radius - thickness, 1)

    def _draw_eve_capacitor_star(self, surface, cx, cy, radius, cap_pct, now):
        """Draw EVE's central capacitor - yellow dashes that turn grey when depleted

        The capacitor is a 'star' of bright yellow dashes arranged in a circle.
        As capacitor drains, dashes dim from yellow to grey.
        """
        num_dashes = 16  # EVE typically has ~16-24 dashes
        dash_length = radius * 0.65
        dash_width = 4
        inner_radius = radius * 0.35

        # Background circle
        pygame.draw.circle(surface, (15, 18, 22), (cx, cy), int(radius * 0.9))

        charged_dashes = int(cap_pct * num_dashes)
        partial = (cap_pct * num_dashes) - charged_dashes

        for i in range(num_dashes):
            angle = -90 + i * (360 / num_dashes)
            angle_rad = math.radians(angle)

            # Calculate dash endpoints
            inner_x = cx + inner_radius * math.cos(angle_rad)
            inner_y = cy + inner_radius * math.sin(angle_rad)
            outer_x = cx + (inner_radius + dash_length) * math.cos(angle_rad)
            outer_y = cy + (inner_radius + dash_length) * math.sin(angle_rad)

            if i < charged_dashes:
                # Fully charged - bright yellow/gold
                brightness = 0.9 + 0.1 * math.sin(now * 0.005 + i * 0.4)
                dash_color = (int(255 * brightness), int(220 * brightness), int(80 * brightness))
                glow_color = (255, 200, 50)
            elif i == charged_dashes and partial > 0.1:
                # Partially charged
                brightness = 0.5 + 0.4 * partial
                dash_color = (int(255 * brightness), int(200 * brightness), int(60 * brightness))
                glow_color = (200, 160, 40)
            else:
                # Depleted - grey
                dash_color = (45, 50, 55)
                glow_color = None

            # Draw glow for charged dashes
            if glow_color:
                pygame.draw.line(surface, glow_color,
                               (inner_x, inner_y), (outer_x, outer_y), dash_width + 2)

            # Draw main dash
            pygame.draw.line(surface, dash_color,
                           (inner_x, inner_y), (outer_x, outer_y), dash_width)

            # Bright tip for charged dashes
            if i < charged_dashes:
                pygame.draw.circle(surface, (255, 255, 200),
                                 (int(outer_x), int(outer_y)), 2)

        # Low capacitor warning
        if cap_pct < 0.25:
            pulse = 0.5 + 0.5 * math.sin(now * 0.008)
            warning_color = (int(200 * pulse), int(100 * pulse), 20)
            pygame.draw.circle(surface, warning_color, (cx, cy), int(radius * 0.9), 2)

    def _draw_eve_center_heat(self, surface, cx, cy, radius, heat_pct, now):
        """Draw minimal heat indicator in the very center"""
        is_overheated = getattr(self.player, 'is_overheated', False)
        heat_warning = getattr(self.player, 'heat_warning', False)

        # Small circle background
        pygame.draw.circle(surface, (18, 22, 28), (cx, cy), radius)

        # Heat color based on level
        if heat_pct < 0.4:
            text_color = (100, 160, 120)  # Green
        elif heat_pct < 0.7:
            text_color = (200, 180, 80)   # Yellow
        elif is_overheated:
            pulse = 0.7 + 0.3 * math.sin(now * 0.02)
            text_color = (255, int(60 * pulse), int(40 * pulse))
        else:
            text_color = (220, 100, 60)   # Orange/Red

        # Heat percentage text
        heat_text = f"{int(heat_pct * 100)}"
        text_surf = self.font_small.render(heat_text, True, text_color)
        text_rect = text_surf.get_rect(center=(cx, cy))
        surface.blit(text_surf, text_rect)

        # Warning border
        if heat_warning or is_overheated:
            pulse = 0.5 + 0.5 * math.sin(now * 0.015)
            border_color = (int(200 * pulse), int(80 * pulse), 30)
            pygame.draw.circle(surface, border_color, (cx, cy), radius, 2)

    def _draw_status_bar(self, surface, x, y, width, height, fill_pct, fill_color, bg_color, label):
        """Draw a single EVE-style status bar"""
        # Background
        pygame.draw.rect(surface, bg_color, (x, y, width, height), border_radius=2)
        pygame.draw.rect(surface, (60, 70, 90), (x, y, width, height), 1, border_radius=2)

        # Fill
        if fill_pct > 0:
            fill_width = int(width * fill_pct)
            if fill_width > 0:
                pygame.draw.rect(surface, fill_color, (x + 1, y + 1, fill_width - 2, height - 2), border_radius=1)
                # Highlight on top edge
                highlight = (min(fill_color[0] + 40, 255), min(fill_color[1] + 40, 255), min(fill_color[2] + 40, 255))
                pygame.draw.line(surface, highlight, (x + 2, y + 1), (x + fill_width - 3, y + 1))

        # Label on left
        label_text = self.font_small.render(label, True, (140, 150, 170))
        surface.blit(label_text, (x - 14, y - 2))

        # Percentage on right
        pct_text = self.font_small.render(f"{int(fill_pct * 100)}", True, fill_color if fill_pct > 0.3 else (180, 180, 180))
        surface.blit(pct_text, (x + width + 4, y - 2))

    def _draw_abyssal_hud(self):
        """Draw Abyssal Depths-specific HUD elements: timer, room, extraction."""
        if not self.abyssal.state:
            return

        hud_data = self.abyssal.get_hud_data()
        if not hud_data:
            return

        # Top center - ABYSSAL TIMER (big, critical when low)
        timer = hud_data.get('timer', '00:00')
        timer_critical = hud_data.get('timer_critical', False)

        # Timer background panel
        timer_panel_width = 140
        timer_panel_height = 50
        timer_x = SCREEN_WIDTH // 2 - timer_panel_width // 2
        timer_y = 10

        # Dark Triglavian-styled panel
        pygame.draw.rect(self.render_surface, (25, 15, 30),
                        (timer_x, timer_y, timer_panel_width, timer_panel_height), border_radius=5)
        pygame.draw.rect(self.render_surface, (120, 50, 80),
                        (timer_x, timer_y, timer_panel_width, timer_panel_height), 2, border_radius=5)

        # Timer text (large, centered)
        if timer_critical:
            # Pulsing red when critical
            pulse = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.01))
            timer_color = (255, pulse, pulse)
        else:
            timer_color = (220, 200, 180)

        timer_text = self.font_large.render(timer, True, timer_color)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, timer_y + 25))
        self.render_surface.blit(timer_text, timer_rect)

        # "ABYSSAL" label above timer
        label_text = self.font_small.render("ABYSSAL", True, (150, 100, 130))
        label_rect = label_text.get_rect(center=(SCREEN_WIDTH // 2, timer_y + timer_panel_height + 10))
        self.render_surface.blit(label_text, label_rect)

        # Room indicator (left side)
        room = hud_data.get('room', 1)
        room_name = hud_data.get('room_name', 'POCKETS')
        room_progress = hud_data.get('room_progress', 0.0)

        room_x = 10
        room_y = 10

        # Room number and name
        room_color = (180, 100, 140)
        room_text = self.font.render(f"ROOM {room}/3", True, room_color)
        self.render_surface.blit(room_text, (room_x, room_y))

        room_name_text = self.font_small.render(room_name, True, (140, 80, 100))
        self.render_surface.blit(room_name_text, (room_x, room_y + 20))

        # Room progress bar
        progress_width = 100
        progress_height = 8
        progress_y = room_y + 38

        pygame.draw.rect(self.render_surface, (30, 20, 25),
                        (room_x, progress_y, progress_width, progress_height), border_radius=2)
        if room_progress > 0:
            fill_width = int(progress_width * room_progress)
            pygame.draw.rect(self.render_surface, (200, 80, 120),
                            (room_x, progress_y, fill_width, progress_height), border_radius=2)
        pygame.draw.rect(self.render_surface, (100, 60, 80),
                        (room_x, progress_y, progress_width, progress_height), 1, border_radius=2)

        # Gate indicator (when gate is active)
        gate_active = hud_data.get('gate_active', False)
        extraction_progress = hud_data.get('extraction_progress', 0.0)

        if gate_active or extraction_progress > 0:
            gate_y = room_y + 55
            gate_text = self.font_small.render("GATE ACTIVE", True, (100, 255, 180))
            self.render_surface.blit(gate_text, (room_x, gate_y))

            # Extraction progress bar (if room 3)
            if room == 3 and extraction_progress > 0:
                ext_y = gate_y + 15
                ext_width = 100
                ext_height = 10

                pygame.draw.rect(self.render_surface, (20, 40, 30),
                                (room_x, ext_y, ext_width, ext_height), border_radius=3)
                fill_w = int(ext_width * extraction_progress)
                pygame.draw.rect(self.render_surface, (80, 255, 160),
                                (room_x, ext_y, fill_w, ext_height), border_radius=3)
                pygame.draw.rect(self.render_surface, (60, 180, 120),
                                (room_x, ext_y, ext_width, ext_height), 1, border_radius=3)

                ext_label = self.font_small.render("EXTRACTING...", True, (80, 255, 160))
                self.render_surface.blit(ext_label, (room_x, ext_y + 12))

        # Filament and tier indicator (top right)
        filament = hud_data.get('filament', 'EXOTIC')
        tier = hud_data.get('tier', 1)

        info_x = SCREEN_WIDTH - 120
        info_y = 10

        filament_text = self.font_small.render(f"{filament} T{tier}", True, (160, 120, 140))
        self.render_surface.blit(filament_text, (info_x, info_y))

        # Room intro overlay
        if hud_data.get('showing_intro', False):
            self._draw_room_intro_overlay(room, room_name)

    def _draw_room_intro_overlay(self, room_num, room_name):
        """Draw dramatic room introduction overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((15, 10, 20, 150))
        self.render_surface.blit(overlay, (0, 0))

        # Room number (large)
        room_text = self.font_large.render(f"ROOM {room_num}", True, (255, 120, 160))
        room_rect = room_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.render_surface.blit(room_text, room_rect)

        # Room name (subtitle)
        name_text = self.font.render(room_name, True, (200, 140, 170))
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.render_surface.blit(name_text, name_rect)

        # Flavor text
        flavor_texts = {
            'POCKETS': "Clear the perimeter...",
            'ESCALATION': "Hostiles inbound!",
            'EXTRACTION': "Reach the gate to escape!"
        }
        flavor = flavor_texts.get(room_name, "")
        if flavor:
            flavor_text = self.font_small.render(flavor, True, (150, 100, 130))
            flavor_rect = flavor_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            self.render_surface.blit(flavor_text, flavor_rect)

    def _draw_abyssal_elements(self):
        """Draw Abyssal hazards and extraction gate."""
        if not self.abyssal:
            return

        now = pygame.time.get_ticks()

        # Draw hazards
        for hazard in self.abyssal.hazards:
            if not hazard.active:
                continue

            x, y = int(hazard.x), int(hazard.y)
            radius = int(hazard.radius)

            # Hazard colors by type
            hazard_colors = {
                'deviant_automata': (255, 80, 80),      # Red - damage pulses
                'tachyon_cloud': (100, 180, 255),       # Blue - slow
                'ephialtes_cloud': (200, 150, 255),     # Purple - tracking disruption
            }
            color = hazard_colors.get(hazard.hazard_type, (180, 100, 140))

            # Outer glow (semi-transparent)
            glow_surf = pygame.Surface((radius * 3, radius * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, 40), (radius * 1.5, radius * 1.5), radius * 1.5)
            self.render_surface.blit(glow_surf, (x - radius * 1.5, y - radius * 1.5))

            # Inner circle with rotation effect
            math.sin(now * 0.002 + hazard.rotation * 0.1) * 10

            # Hazard ring
            pygame.draw.circle(self.render_surface, color, (x, y), radius, 3)

            # Pulsing inner circle when about to damage
            if hazard.pulse_flash > 0:
                flash_radius = int(radius * (0.5 + hazard.pulse_flash * 0.5))
                flash_alpha = int(200 * hazard.pulse_flash)
                flash_surf = pygame.Surface((flash_radius * 2, flash_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(flash_surf, (*color, flash_alpha),
                                  (flash_radius, flash_radius), flash_radius)
                self.render_surface.blit(flash_surf, (x - flash_radius, y - flash_radius))

            # Hazard symbol in center
            symbol = {'deviant_automata': '!', 'tachyon_cloud': '~', 'ephialtes_cloud': '?'}
            sym = symbol.get(hazard.hazard_type, '*')
            sym_text = self.font.render(sym, True, color)
            sym_rect = sym_text.get_rect(center=(x, y))
            self.render_surface.blit(sym_text, sym_rect)

        # Draw room transition gate (rooms 1-2)
        if self.abyssal.room_state and self.abyssal.room_state.gate_active:
            if self.abyssal.room_state.room_number < 3:
                gate_x = SCREEN_WIDTH // 2
                gate_y = 50
                gate_radius = 40

                # Pulsing gate effect
                pulse = 0.8 + 0.2 * math.sin(now * 0.005)
                gate_color = (100, 255, 180)

                # Gate glow
                glow_surf = pygame.Surface((gate_radius * 4, gate_radius * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*gate_color, 60),
                                  (gate_radius * 2, gate_radius * 2), int(gate_radius * 2 * pulse))
                self.render_surface.blit(glow_surf, (gate_x - gate_radius * 2, gate_y - gate_radius * 2))

                # Gate ring
                pygame.draw.circle(self.render_surface, gate_color, (gate_x, gate_y),
                                  int(gate_radius * pulse), 3)

                # Inner portal effect
                inner_radius = int(gate_radius * 0.6 * pulse)
                pygame.draw.circle(self.render_surface, (50, 200, 140), (gate_x, gate_y), inner_radius)

                # "ENTER" text
                enter_text = self.font_small.render("ENTER", True, gate_color)
                enter_rect = enter_text.get_rect(center=(gate_x, gate_y + gate_radius + 15))
                self.render_surface.blit(enter_text, enter_rect)

        # Draw extraction gate (room 3)
        if self.abyssal.extraction_gate:
            gate = self.abyssal.extraction_gate
            gate_x, gate_y = int(gate.x), int(gate.y)
            gate_radius = int(gate.radius)

            if gate.active:
                # Active extraction gate - bright and pulsing
                pulse = 0.8 + 0.2 * math.sin(now * 0.008)
                gate_color = (80, 255, 160)

                # Large glow when active
                glow_surf = pygame.Surface((gate_radius * 5, gate_radius * 5), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*gate_color, 80),
                                  (gate_radius * 2.5, gate_radius * 2.5), int(gate_radius * 2.5 * pulse))
                self.render_surface.blit(glow_surf,
                                        (gate_x - gate_radius * 2.5, gate_y - gate_radius * 2.5))

                # Gate rings
                for i in range(3):
                    r = int((gate_radius - i * 8) * pulse)
                    255 - i * 60
                    ring_color = (80, 255, 160) if not gate.channeling else (160, 255, 200)
                    pygame.draw.circle(self.render_surface, ring_color, (gate_x, gate_y), r, 2)

                # Channeling effect
                if gate.channeling:
                    # Channel progress spiral
                    progress = gate.channel_progress
                    angle = progress * math.pi * 4  # 2 full rotations
                    spiral_x = gate_x + math.cos(angle) * gate_radius * 0.7
                    spiral_y = gate_y + math.sin(angle) * gate_radius * 0.7
                    pygame.draw.circle(self.render_surface, (255, 255, 255),
                                      (int(spiral_x), int(spiral_y)), 5)

                    # Progress bar below gate
                    bar_width = 80
                    bar_height = 8
                    bar_x = gate_x - bar_width // 2
                    bar_y = gate_y + gate_radius + 10

                    pygame.draw.rect(self.render_surface, (20, 60, 40),
                                    (bar_x, bar_y, bar_width, bar_height), border_radius=3)
                    pygame.draw.rect(self.render_surface, (100, 255, 180),
                                    (bar_x, bar_y, int(bar_width * progress), bar_height), border_radius=3)

                    # "EXTRACTING" text
                    ext_text = self.font_small.render("EXTRACTING...", True, (150, 255, 200))
                    ext_rect = ext_text.get_rect(center=(gate_x, bar_y + 20))
                    self.render_surface.blit(ext_text, ext_rect)
                else:
                    # "HOLD [E] / [A]" prompt
                    prompt_text = self.font_small.render("HOLD [E] TO EXTRACT", True, gate_color)
                    prompt_rect = prompt_text.get_rect(center=(gate_x, gate_y + gate_radius + 15))
                    self.render_surface.blit(prompt_text, prompt_rect)
            else:
                # Inactive gate - dimmed
                pygame.draw.circle(self.render_surface, (60, 80, 70), (gate_x, gate_y), gate_radius, 2)
                inactive_text = self.font_small.render("CLEAR ROOM", True, (80, 100, 90))
                inactive_rect = inactive_text.get_rect(center=(gate_x, gate_y + gate_radius + 15))
                self.render_surface.blit(inactive_text, inactive_rect)

    def _draw_heat_warning_symbol(self, cx, cy, heat_pct):
        """Draw heat warning flame symbol above HUD when overheating"""
        now = pygame.time.get_ticks()

        # Calculate color: orange at 75%, red at 100%
        warning_intensity = (heat_pct - 0.75) / 0.25  # 0 to 1
        warning_intensity = min(1.0, warning_intensity)

        # Interpolate orange -> red
        r = 255
        g = int(180 * (1 - warning_intensity))
        b = int(50 * (1 - warning_intensity))
        symbol_color = (r, g, b)

        # Pulsing effect - faster as heat increases
        pulse_speed = 0.008 + 0.012 * warning_intensity
        pulse = 0.7 + 0.3 * abs(math.sin(now * pulse_speed))

        # Create the symbol surface
        surf_w, surf_h = 60, 70
        symbol_surf = pygame.Surface((surf_w, surf_h), pygame.SRCALPHA)
        scx, scy = surf_w // 2, surf_h // 2 + 5

        # Outer glow
        glow_alpha = int(50 * pulse * warning_intensity)
        for r_off in range(22, 8, -2):
            alpha = int(glow_alpha * (22 - r_off) / 14)
            pygame.draw.circle(symbol_surf, (*symbol_color, alpha), (scx, scy - 8), r_off)

        # Draw flame shape
        flame_h = int(28 * pulse)
        flame_w = int(18 * pulse)

        # Outer flame
        points = [
            (scx, scy - flame_h),
            (scx + flame_w // 2, scy + 2),
            (scx + flame_w // 3, scy + 8),
            (scx, scy + 3),
            (scx - flame_w // 3, scy + 8),
            (scx - flame_w // 2, scy + 2),
        ]
        pygame.draw.polygon(symbol_surf, symbol_color, points)

        # Inner flame (brighter)
        inner_color = (255, min(255, g + 60), min(255, b + 40))
        inner_h = int(18 * pulse)
        inner_w = int(10 * pulse)
        inner_pts = [
            (scx, scy - inner_h),
            (scx + inner_w // 2, scy - 2),
            (scx, scy + 4),
            (scx - inner_w // 2, scy - 2),
        ]
        pygame.draw.polygon(symbol_surf, inner_color, inner_pts)

        # Core
        pygame.draw.ellipse(symbol_surf, (255, 255, min(255, b + 120)),
                           (scx - 3, scy - 6, 6, 10))

        # Rising particles
        for i in range(3):
            py = scy - 12 - ((now // 35 + i * 12) % 20)
            px = scx + int(4 * math.sin(now * 0.008 + i * 2))
            pa = int(140 * (1 - ((scy - 12 - py) / 20)))
            if pa > 0:
                pygame.draw.circle(symbol_surf, (*symbol_color, pa), (px, py), 2)

        # Blit flame
        self.render_surface.blit(symbol_surf, (cx - scx, cy - scy))

        # Warning text below
        if self.player.is_overheated:
            if int(now / 150) % 2 == 0:
                txt = self.font.render("OVERHEAT", True, (255, 50, 50))
                self.render_surface.blit(txt, txt.get_rect(center=(cx, cy + 35)))
        else:
            txt = self.font_small.render("HEAT", True, symbol_color)
            self.render_surface.blit(txt, txt.get_rect(center=(cx, cy + 30)))

    def _draw_faction_indicator(self):
        """Draw faction emblem and name in top-left corner"""
        if not hasattr(self, 'selected_faction') or not self.selected_faction:
            return

        faction_data = FACTIONS.get(self.selected_faction)
        if not faction_data:
            return

        x, y = 10, 10
        faction_color = faction_data['color_primary']
        faction_name = faction_data['name'].upper()

        # Background panel
        panel_width = 140
        panel_height = 28
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((15, 15, 25, 180))

        # Faction color accent bar on left
        pygame.draw.rect(panel_surf, faction_color, (0, 0, 4, panel_height))

        # Border
        pygame.draw.rect(panel_surf, (*faction_color[:3], 120), (0, 0, panel_width, panel_height), 1)

        self.render_surface.blit(panel_surf, (x, y))

        # Faction emblem (small geometric shape)
        emblem_x = x + 14
        emblem_y = y + panel_height // 2
        if self.selected_faction == 'minmatar':
            # Minmatar tribal symbol - angular/tribal
            points = [
                (emblem_x, emblem_y - 8),
                (emblem_x + 6, emblem_y),
                (emblem_x, emblem_y + 8),
                (emblem_x - 6, emblem_y),
            ]
            pygame.draw.polygon(self.render_surface, faction_color, points)
            pygame.draw.polygon(self.render_surface, (255, 200, 150), points, 1)
        else:
            # Amarr symbol - golden circle with cross
            pygame.draw.circle(self.render_surface, faction_color, (emblem_x, emblem_y), 7)
            pygame.draw.circle(self.render_surface, (255, 230, 180), (emblem_x, emblem_y), 7, 1)
            pygame.draw.line(self.render_surface, (60, 50, 30), (emblem_x - 4, emblem_y), (emblem_x + 4, emblem_y), 2)
            pygame.draw.line(self.render_surface, (60, 50, 30), (emblem_x, emblem_y - 4), (emblem_x, emblem_y + 4), 2)

        # Faction name text
        text = self.font_small.render(faction_name, True, faction_color)
        self.render_surface.blit(text, (x + 26, y + 7))

    def _draw_thrust_gauge(self, x, cy):
        """Draw EVE-style vertical thrust/afterburner gauge"""
        now = pygame.time.get_ticks()
        bar_height = 70
        bar_width = 12
        y = cy - bar_height // 2 - 10

        # Calculate fill based on thrust cooldown
        if hasattr(self.player, 'thrust_cooldown'):
            max_cooldown = self.player.thrust_cooldown_time
            cooldown_remaining = max(0, self.player.thrust_cooldown)
            fill_pct = 1.0 - (cooldown_remaining / max_cooldown) if max_cooldown > 0 else 1.0
        else:
            fill_pct = 1.0

        # Outer glow when ready
        if fill_pct >= 1.0:
            pulse = 0.5 + 0.5 * math.sin(now * 0.006)
            glow_surf = pygame.Surface((bar_width + 12, bar_height + 12), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 180, 80, int(40 * pulse)), (0, 0, bar_width + 12, bar_height + 12), border_radius=6)
            self.render_surface.blit(glow_surf, (x - 6, y - 6))

        # Background with border
        pygame.draw.rect(self.render_surface, (20, 25, 35), (x, y, bar_width, bar_height), border_radius=4)
        pygame.draw.rect(self.render_surface, (50, 60, 80), (x, y, bar_width, bar_height), 1, border_radius=4)

        # Segmented fill (8 segments)
        num_segments = 8
        segment_height = (bar_height - 4) / num_segments
        filled_segments = int(fill_pct * num_segments)

        for i in range(num_segments):
            seg_y = y + bar_height - 2 - (i + 1) * segment_height
            if i < filled_segments:
                # Gradient from blue (bottom) to orange (top)
                t = i / num_segments
                if fill_pct >= 1.0:
                    # Ready - orange/gold
                    r = int(200 + 55 * t)
                    g = int(140 + 40 * t)
                    b = 60
                else:
                    # Charging - blue
                    r = int(60 + 40 * t)
                    g = int(120 + 60 * t)
                    b = int(200 + 55 * t)
                pygame.draw.rect(self.render_surface, (r, g, b),
                               (x + 2, seg_y, bar_width - 4, segment_height - 2), border_radius=2)
            else:
                # Empty segment
                pygame.draw.rect(self.render_surface, (30, 35, 45),
                               (x + 2, seg_y, bar_width - 4, segment_height - 2), border_radius=2)

        # Label
        label_color = (255, 200, 100) if fill_pct >= 1.0 else (100, 120, 160)
        label = self.font_small.render("AB", True, label_color)
        label_rect = label.get_rect(center=(x + bar_width // 2, y + bar_height + 12))
        self.render_surface.blit(label, label_rect)

    def draw_boss_health_bar(self):
        """Draw enhanced boss health bar at top of screen when fighting a boss"""
        # Find boss in enemies
        boss = None
        for enemy in self.enemies:
            if enemy.is_boss:
                boss = enemy
                break

        if not boss:
            self._boss_bar_visible = False
            return

        # Track boss for damage flash effect
        if not hasattr(self, '_boss_last_health'):
            self._boss_last_health = boss.shields + boss.armor + boss.hull
            self._boss_damage_flash = 0
            self._boss_bar_visible = False
            self._boss_bar_slide = 0

        # Slide-in animation
        if not self._boss_bar_visible:
            self._boss_bar_visible = True
            self._boss_bar_slide = 0
        if self._boss_bar_slide < 1.0:
            self._boss_bar_slide = min(1.0, self._boss_bar_slide + 0.05)

        # Check for damage flash
        current_health = boss.shields + boss.armor + boss.hull
        if current_health < self._boss_last_health:
            self._boss_damage_flash = 15
        self._boss_last_health = current_health
        if self._boss_damage_flash > 0:
            self._boss_damage_flash -= 1

        # Boss health bar dimensions
        bar_width = SCREEN_WIDTH - 100
        bar_height = 24
        x = 50
        base_y = 35
        y = int(base_y - (1 - self._boss_bar_slide) * 60)  # Slide down from top

        # Decorative frame
        frame_rect = pygame.Rect(x - 8, y - 18, bar_width + 16, bar_height + 28)
        pygame.draw.rect(self.render_surface, (20, 20, 30), frame_rect)
        pygame.draw.rect(self.render_surface, COLOR_AMARR_DARK, frame_rect, 2)

        # Corner decorations
        corner_size = 8
        for cx, cy in [(frame_rect.left, frame_rect.top), (frame_rect.right - corner_size, frame_rect.top),
                       (frame_rect.left, frame_rect.bottom - corner_size), (frame_rect.right - corner_size, frame_rect.bottom - corner_size)]:
            pygame.draw.rect(self.render_surface, COLOR_AMARR_ACCENT, (cx, cy, corner_size, corner_size))

        # Background bar
        pygame.draw.rect(self.render_surface, (15, 15, 20), (x, y, bar_width, bar_height))

        # Calculate segment widths based on max values
        total_max = boss.max_shields + boss.max_armor + boss.max_hull
        shield_max_width = int(bar_width * (boss.max_shields / total_max)) if total_max > 0 else 0
        armor_max_width = int(bar_width * (boss.max_armor / total_max)) if total_max > 0 else 0
        hull_max_width = bar_width - shield_max_width - armor_max_width

        # Calculate current fill widths
        shield_pct = boss.shields / boss.max_shields if boss.max_shields > 0 else 0
        armor_pct = boss.armor / boss.max_armor if boss.max_armor > 0 else 0
        hull_pct = boss.hull / boss.max_hull if boss.max_hull > 0 else 0

        shield_width = int(shield_max_width * max(0, shield_pct))
        armor_width = int(armor_max_width * max(0, armor_pct))
        hull_width = int(hull_max_width * max(0, hull_pct))

        # Draw segment backgrounds (darker versions)
        seg_x = x
        if shield_max_width > 0:
            pygame.draw.rect(self.render_surface, (30, 45, 75), (seg_x, y, shield_max_width, bar_height))
            seg_x += shield_max_width
        if armor_max_width > 0:
            pygame.draw.rect(self.render_surface, (60, 45, 30), (seg_x, y, armor_max_width, bar_height))
            seg_x += armor_max_width
        if hull_max_width > 0:
            pygame.draw.rect(self.render_surface, (45, 45, 45), (seg_x, y, hull_max_width, bar_height))

        # Draw filled segments
        seg_x = x
        if shield_width > 0:
            pygame.draw.rect(self.render_surface, COLOR_SHIELD, (seg_x, y, shield_width, bar_height))
            pygame.draw.rect(self.render_surface, (150, 200, 255), (seg_x, y, shield_width, 4))  # Highlight
        seg_x = x + shield_max_width
        if armor_width > 0:
            pygame.draw.rect(self.render_surface, COLOR_ARMOR, (seg_x, y, armor_width, bar_height))
            pygame.draw.rect(self.render_surface, (230, 180, 130), (seg_x, y, armor_width, 4))  # Highlight
        seg_x = x + shield_max_width + armor_max_width
        if hull_width > 0:
            pygame.draw.rect(self.render_surface, COLOR_HULL, (seg_x, y, hull_width, bar_height))
            pygame.draw.rect(self.render_surface, (180, 180, 180), (seg_x, y, hull_width, 4))  # Highlight

        # Segment dividers
        if shield_max_width > 0 and armor_max_width > 0:
            pygame.draw.line(self.render_surface, (80, 80, 100),
                           (x + shield_max_width, y), (x + shield_max_width, y + bar_height), 2)
        if armor_max_width > 0 and hull_max_width > 0:
            pygame.draw.line(self.render_surface, (80, 80, 100),
                           (x + shield_max_width + armor_max_width, y),
                           (x + shield_max_width + armor_max_width, y + bar_height), 2)

        # Damage flash overlay
        if self._boss_damage_flash > 0:
            flash_alpha = int(150 * (self._boss_damage_flash / 15))
            flash_surface = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
            flash_surface.fill((255, 50, 50, flash_alpha))
            self.render_surface.blit(flash_surface, (x, y))

        # Border
        border_color = (255, 100, 100) if self._boss_damage_flash > 0 else (100, 100, 120)
        pygame.draw.rect(self.render_surface, border_color, (x, y, bar_width, bar_height), 2)

        # Boss name with shadow
        name_text = self.font.render(boss.stats['name'].upper(), True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2 + 1, y - 9))
        self.render_surface.blit(name_text, name_rect)
        name_text = self.font.render(boss.stats['name'].upper(), True, COLOR_AMARR_ACCENT)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y - 10))
        self.render_surface.blit(name_text, name_rect)

        # Health numbers on right side
        health_pct = (current_health / total_max * 100) if total_max > 0 else 0
        pct_text = self.font_small.render(f"{int(health_pct)}%", True, COLOR_TEXT)
        pct_rect = pct_text.get_rect(right=x + bar_width - 5, centery=y + bar_height // 2)
        self.render_surface.blit(pct_text, pct_rect)

        # Shield/Armor/Hull labels on left
        labels_text = self.font_small.render("S/A/H", True, (120, 120, 140))
        labels_rect = labels_text.get_rect(left=x + 5, centery=y + bar_height // 2)
        self.render_surface.blit(labels_text, labels_rect)

        # Phase indicator for multi-phase bosses
        if hasattr(boss, 'boss_phase') and boss.boss_phase > 0:
            phase_text = self.font_small.render(f"PHASE {boss.boss_phase + 1}", True, (255, 100, 100))
            phase_rect = phase_text.get_rect(right=x + bar_width, centery=y - 10)
            self.render_surface.blit(phase_text, phase_rect)

        # Warning indicator when boss is about to use special attack
        if hasattr(boss, 'boss_special_cooldown') and boss.boss_special_cooldown < 60:
            warning_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.02))
            warning_text = self.font_small.render("! SPECIAL ATTACK !", True, (255, warning_alpha, 0))
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, y + bar_height + 12))
            self.render_surface.blit(warning_text, warning_rect)

    def _draw_achievement_notifications(self):
        """Draw achievement unlock notifications"""
        if not self.achievement_display:
            return

        # Display first achievement in queue
        achievement = self.achievement_display[0]
        self.achievement_timer += 1

        # Notification lasts 180 frames (3 seconds)
        if self.achievement_timer > 180:
            self.achievement_display.pop(0)
            self.achievement_timer = 0
            return

        # Animation: slide in, hold, slide out
        if self.achievement_timer < 20:
            # Slide in from right
            offset_x = int((20 - self.achievement_timer) * 15)
            alpha = int(self.achievement_timer * 12.75)
        elif self.achievement_timer > 160:
            # Slide out to right
            offset_x = int((self.achievement_timer - 160) * 15)
            alpha = int((180 - self.achievement_timer) * 12.75)
        else:
            offset_x = 0
            alpha = 255

        # Draw notification box
        box_width = 280
        box_height = 60
        box_x = SCREEN_WIDTH - box_width - 10 + offset_x
        box_y = 80

        # Background
        notification_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        notification_surface.fill((40, 40, 50, min(alpha, 230)))
        pygame.draw.rect(notification_surface, (255, 215, 0, alpha), (0, 0, box_width, box_height), 2)

        # Trophy icon (simple rectangle for now)
        pygame.draw.rect(notification_surface, (255, 215, 0, alpha), (10, 15, 30, 30))

        # Achievement text
        title_text = self.font_small.render("ACHIEVEMENT UNLOCKED", True, (255, 215, 0))
        notification_surface.blit(title_text, (50, 8))

        name_text = self.font.render(achievement['name'], True, (255, 255, 255))
        notification_surface.blit(name_text, (50, 28))

        self.screen.blit(notification_surface, (box_x, box_y))

    def _record_game_end(self, victory=False):
        """Record score and check achievements at end of game"""
        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        berserk_stats = self.berserk.get_stats()

        # Endless mode high score tracking
        if self.game_mode == 'endless':
            updated = False
            if self.endless_wave > self.endless_high_wave:
                self.endless_high_wave = self.endless_wave
                updated = True
            if self.player.score > self.endless_high_score:
                self.endless_high_score = self.player.score
                updated = True
            if updated:
                self._save_settings()  # Persist new records

        # Record high score
        self.last_rank, self.new_high_score = self.high_scores.add_score(
            score=self.player.score,
            refugees=self.player.total_refugees,
            stage=self.current_stage if self.game_mode == 'campaign' else 0,
            wave=self.current_wave if self.game_mode == 'campaign' else self.endless_wave,
            ship=ship_class,
            difficulty=self.difficulty,
            berserk_stats=berserk_stats
        )

        # Check achievements
        game_stats = {
            'total_kills': berserk_stats.get('total_kills', 0),
            'refugees': self.player.total_refugees,
            'score': self.player.score,
            'stage': self.current_stage,
            'victory': victory,
            'ship': ship_class,
            'difficulty': self.difficulty,
            'berserk': berserk_stats,
            'game_mode': self.game_mode,
            'endless_wave': self.endless_wave if self.game_mode == 'endless' else 0,
            'endless_time': self.endless_time // 60 if self.game_mode == 'endless' else 0  # Convert frames to seconds
        }
        newly_unlocked = self.achievements.check_achievements(game_stats)

        # Queue achievement notifications
        for achievement_id in newly_unlocked:
            info = self.achievements.get_achievement_info(achievement_id)
            if info:
                self.achievement_display.append(info)

    def draw_chapter_select(self):
        """Draw chapter selection screen - horizontal scroll layout"""
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        # Animate timer for effects
        if not hasattr(self, 'chapter_timer'):
            self.chapter_timer = 0
        self.chapter_timer += 1

        # === TITLE ===
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("SELECT CHAPTER", True, (200, 200, 200))
        rect = title.get_rect(center=(cx, 50))
        self.render_surface.blit(title, rect)

        # Subtitle with animated glow
        sub_font = pygame.font.Font(None, 28)
        pulse = int(20 * math.sin(self.chapter_timer * 0.03))
        subtitle = sub_font.render("EVE REBELLION", True, (150 + pulse, 100, 80))
        rect = subtitle.get_rect(center=(cx, 80))
        self.render_surface.blit(subtitle, rect)

        # Decorative line
        pygame.draw.line(self.render_surface, (100, 80, 70), (cx - 200, 100), (cx + 200, 100), 2)

        # === CHAPTER CARDS ===
        card_width = 180
        card_height = 280
        card_spacing = 20
        total_width = len(self.chapter_options) * (card_width + card_spacing) - card_spacing
        start_x = cx - total_width // 2

        for i, chapter in enumerate(self.chapter_options):
            card_x = start_x + i * (card_width + card_spacing)
            card_y = cy - card_height // 2 + 20

            is_selected = (i == self.chapter_index)
            is_unlocked = chapter.get('unlocked', False)

            # Selection bounce effect
            if is_selected:
                bounce = int(5 * math.sin(self.chapter_timer * 0.1))
                card_y -= bounce

            # Card background
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)

            if is_unlocked:
                if is_selected:
                    card_surf.fill((40, 35, 45, 230))
                else:
                    card_surf.fill((25, 25, 35, 200))
            else:
                card_surf.fill((20, 20, 25, 180))  # Darker for locked

            # Border
            color = chapter['color']
            if is_selected and is_unlocked:
                # Glowing border for selected
                glow_rect = pygame.Rect(card_x - 4, card_y - 4, card_width + 8, card_height + 8)
                pygame.draw.rect(self.render_surface, (*color, 100), glow_rect, 4, border_radius=10)
                pygame.draw.rect(card_surf, color, (0, 0, card_width, card_height), 3, border_radius=8)
            elif is_unlocked:
                pygame.draw.rect(card_surf, (*color[:3],), (0, 0, card_width, card_height), 2, border_radius=8)
            else:
                pygame.draw.rect(card_surf, (60, 60, 70), (0, 0, card_width, card_height), 2, border_radius=8)

            self.render_surface.blit(card_surf, (card_x, card_y))

            # Chapter number
            num_font = pygame.font.Font(None, 24)
            num_color = color if is_unlocked else (80, 80, 90)
            num_text = num_font.render(f"CHAPTER {i + 1}", True, num_color)
            num_rect = num_text.get_rect(center=(card_x + card_width // 2, card_y + 25))
            self.render_surface.blit(num_text, num_rect)

            # Chapter name (split into lines if needed)
            name_font = pygame.font.Font(None, 28)
            name_color = (255, 255, 255) if is_unlocked else (100, 100, 110)
            name_words = chapter['name'].split()
            if len(name_words) > 1:
                line1 = name_font.render(name_words[0], True, name_color)
                line2 = name_font.render(' '.join(name_words[1:]), True, name_color)
                self.render_surface.blit(line1, line1.get_rect(center=(card_x + card_width // 2, card_y + 55)))
                self.render_surface.blit(line2, line2.get_rect(center=(card_x + card_width // 2, card_y + 78)))
            else:
                name_text = name_font.render(chapter['name'], True, name_color)
                name_rect = name_text.get_rect(center=(card_x + card_width // 2, card_y + 65))
                self.render_surface.blit(name_text, name_rect)

            # Subtitle
            sub_color = color if is_unlocked else (70, 70, 80)
            sub_text = self.font_small.render(chapter['subtitle'], True, sub_color)
            sub_rect = sub_text.get_rect(center=(card_x + card_width // 2, card_y + 105))
            self.render_surface.blit(sub_text, sub_rect)

            # Divider line
            div_y = card_y + 125
            pygame.draw.line(self.render_surface, (*color[:3], 100) if is_unlocked else (50, 50, 60),
                           (card_x + 20, div_y), (card_x + card_width - 20, div_y), 1)

            # Icon placeholder (faction symbol area)
            icon_y = card_y + 155
            icon_size = 60
            icon_color = color if is_unlocked else (50, 50, 60)
            pygame.draw.circle(self.render_surface, (*icon_color[:3], 60),
                             (card_x + card_width // 2, icon_y), icon_size // 2)
            pygame.draw.circle(self.render_surface, icon_color,
                             (card_x + card_width // 2, icon_y), icon_size // 2, 2)

            # Lock icon if not unlocked
            if not is_unlocked:
                lock_font = pygame.font.Font(None, 32)
                lock_text = lock_font.render("🔒", True, (80, 80, 90))
                lock_rect = lock_text.get_rect(center=(card_x + card_width // 2, icon_y))
                self.render_surface.blit(lock_text, lock_rect)

            # Description (at bottom)
            if is_selected:
                desc_y = card_y + card_height - 35
                desc_lines = self._wrap_text(chapter['description'], self.font_small, card_width - 20)
                for j, line in enumerate(desc_lines[:2]):  # Max 2 lines
                    desc_color = (180, 180, 180) if is_unlocked else (100, 100, 110)
                    desc_text = self.font_small.render(line, True, desc_color)
                    desc_rect = desc_text.get_rect(center=(card_x + card_width // 2, desc_y + j * 16))
                    self.render_surface.blit(desc_text, desc_rect)

        # === NAVIGATION HINTS ===
        hint_y = SCREEN_HEIGHT - 80

        # Controller or keyboard hints
        if self.controller and self.controller.connected:
            hint_font = self.font_small
            hints = [
                ("←", "D-Pad", (100, 100, 100)),
                ("→", "", (100, 100, 100)),
                ("A", "Select", (100, 200, 100)),
                ("B", "Back", (200, 100, 100)),
            ]
            hint_x = cx - 120
            for btn, label, color in hints:
                self._draw_controller_button(hint_x, hint_y, btn, 24)
                if label:
                    lbl_text = hint_font.render(label, True, (120, 120, 120))
                    self.render_surface.blit(lbl_text, (hint_x + 28, hint_y + 4))
                hint_x += 80
        else:
            hint_font = self.font_small
            hint_text = hint_font.render("← → Navigate   ENTER Select   ESC Back", True, (120, 120, 120))
            hint_rect = hint_text.get_rect(center=(cx, hint_y))
            self.render_surface.blit(hint_text, hint_rect)

        # Settings shortcut hint
        settings_hint = self.font_small.render("[O] Settings   [Q] Quit", True, (80, 80, 80))
        settings_rect = settings_hint.get_rect(center=(cx, SCREEN_HEIGHT - 40))
        self.render_surface.blit(settings_hint, settings_rect)

    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw_menu(self):
        """Draw sleek main menu"""
        cx = SCREEN_WIDTH // 2

        # Animate timer for effects
        if not hasattr(self, 'menu_timer'):
            self.menu_timer = 0
        self.menu_timer += 1

        # === TITLE SECTION ===
        # Title glow effect
        glow_alpha = int(40 + 20 * math.sin(self.menu_timer * 0.05))
        for offset in range(12, 0, -3):
            glow_surf = pygame.font.Font(None, 56).render("EVE REBELLION", True, (180, 100, 50))
            glow_surf.set_alpha(glow_alpha // (offset // 3 + 1))
            rect = glow_surf.get_rect(center=(cx, 140 + offset // 2))
            self.render_surface.blit(glow_surf, rect)

        # Main title
        title_font = pygame.font.Font(None, 56)
        title = title_font.render("EVE REBELLION", True, (255, 180, 100))
        rect = title.get_rect(center=(cx, 140))
        self.render_surface.blit(title, rect)

        # Decorative line under title
        line_width = 250
        pygame.draw.line(self.render_surface, (100, 60, 40),
                        (cx - line_width, 170), (cx + line_width, 170), 2)
        pygame.draw.line(self.render_surface, (180, 100, 50),
                        (cx - line_width + 50, 173), (cx + line_width - 50, 173), 1)

        # === MAIN MENU PANEL ===
        panel_y = 200
        panel_height = 370
        panel_width = 340

        # Panel background with border
        panel_rect = pygame.Rect(cx - panel_width//2, panel_y, panel_width, panel_height)
        panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surf.fill((20, 20, 30, 180))
        pygame.draw.rect(panel_surf, (80, 60, 50), (0, 0, panel_width, panel_height), 2, border_radius=8)
        pygame.draw.rect(panel_surf, (60, 40, 35), (2, 2, panel_width-4, panel_height-4), 1, border_radius=6)
        self.render_surface.blit(panel_surf, panel_rect)

        # Menu items - matching self.menu_options for controller support
        menu_items = [
            ("PLAY GAME", "ENTER", 'start'),
            ("HOW TO PLAY", "H", 'how_to_play'),
            ("SETTINGS", "O", 'settings'),
            ("LEADERBOARD", "L", 'leaderboard'),
            ("CREDITS", "C", 'credits'),
            ("QUIT GAME", "Q", 'quit'),
        ]

        item_y = panel_y + 35
        for i, (text, key_hint, option_key) in enumerate(menu_items):
            is_selected = (self.menu_index == i)

            # Selected item has glow and highlight
            if is_selected:
                pulse = int(10 * math.sin(self.menu_timer * 0.08))
                btn_color = (180 + pulse, 100 + pulse//2, 50)
                text_color = (255, 220, 180)
                # Draw button background
                btn_rect = pygame.Rect(cx - 120, item_y - 5, 240, 36)
                pygame.draw.rect(self.render_surface, (60, 40, 30), btn_rect, border_radius=4)
                pygame.draw.rect(self.render_surface, btn_color, btn_rect, 2, border_radius=4)
                # Selection indicator
                pygame.draw.polygon(self.render_surface, btn_color,
                    [(cx - 135, item_y + 10), (cx - 125, item_y + 5), (cx - 125, item_y + 15)])
            else:
                text_color = (150, 150, 150)

            # Key hint (shows controller button icon if connected)
            if self.controller.connected:
                if is_selected:
                    self._draw_controller_button(cx - 140, item_y - 2, 'A', 24)
            else:
                hint_text = f"[{key_hint}]"
                hint = self.font_small.render(hint_text, True, (100, 100, 100))
                self.render_surface.blit(hint, (cx - 130, item_y + 2))

            # Menu text
            item_text = self.font.render(text, True, text_color)
            item_rect = item_text.get_rect(center=(cx + 20, item_y + 12))
            self.render_surface.blit(item_text, item_rect)

            item_y += 50

        # === AUDIO TOGGLES ===
        toggle_y = panel_y + panel_height + 20

        # Sound toggle
        sound_on = self.sound_enabled
        self._draw_toggle(cx - 90, toggle_y, "SOUND", sound_on, "S")

        # Music toggle
        music_on = self.music_enabled
        self._draw_toggle(cx + 30, toggle_y, "MUSIC", music_on, "M")

        # === STATS BAR ===
        stats_y = SCREEN_HEIGHT - 60

        # Stats background
        stats_rect = pygame.Rect(20, stats_y - 5, SCREEN_WIDTH - 40, 50)
        stats_surf = pygame.Surface((stats_rect.width, stats_rect.height), pygame.SRCALPHA)
        stats_surf.fill((15, 15, 25, 160))
        pygame.draw.rect(stats_surf, (60, 50, 45), (0, 0, stats_rect.width, stats_rect.height), 1, border_radius=4)
        self.render_surface.blit(stats_surf, stats_rect)

        # High score
        high_score = self.high_scores.get_high_score()
        hs_label = self.font_small.render("HIGH SCORE", True, (120, 120, 120))
        self.render_surface.blit(hs_label, (50, stats_y))
        hs_value = self.font.render(f"{high_score:,}" if high_score > 0 else "---", True, (255, 200, 100))
        self.render_surface.blit(hs_value, (50, stats_y + 16))

        # Achievements
        unlocked, total = self.achievements.get_progress()
        ach_label = self.font_small.render("ACHIEVEMENTS", True, (120, 120, 120))
        self.render_surface.blit(ach_label, (cx - 40, stats_y))
        ach_value = self.font.render(f"{unlocked}/{total}", True, (180, 180, 180))
        self.render_surface.blit(ach_value, (cx - 40, stats_y + 16))

        # Version/hint
        version = self.font_small.render("v1.0", True, (80, 80, 80))
        self.render_surface.blit(version, (SCREEN_WIDTH - 60, stats_y + 16))

    def _draw_maneuver_gauges(self, x, y):
        """Draw minimal circular cooldown gauges for Roll and Brake maneuvers"""
        gauge_size = 24
        spacing = 32

        now = pygame.time.get_ticks()

        # Thrust gauge - Orange theme (glowing when active)
        thrust_x = x
        thrust_active = self.player.thrust_active
        thrust_cd = self.player.thrust_cooldown
        thrust_max_cd = self.player.thrust_cooldown_time

        if thrust_active:
            fill_pct = 1.0
            color = (255, 180, 80)
            inner_color = (255, 220, 150)
            glow = True
        elif thrust_cd > 0:
            fill_pct = 1.0 - (thrust_cd / thrust_max_cd)
            color = (80, 60, 40)
            inner_color = (100, 80, 50)
            glow = False
        else:
            fill_pct = 1.0
            color = (255, 150, 50)
            inner_color = (255, 200, 100)
            glow = True

        self._draw_circular_gauge(thrust_x, y, gauge_size, fill_pct, color, inner_color, glow, now, thrust_active)

        # Brake gauge - Orange theme
        brake_x = x + spacing
        brake_active = self.player.emergency_brake_active
        brake_cd = self.player.emergency_brake_cooldown
        brake_max_cd = self.player.emergency_brake_cooldown_time

        if brake_active:
            fill_pct = 1.0
            color = (255, 180, 80)
            inner_color = (255, 220, 150)
            glow = True
        elif brake_cd > 0:
            fill_pct = 1.0 - (brake_cd / brake_max_cd)
            color = (80, 60, 40)
            inner_color = (100, 80, 50)
            glow = False
        else:
            fill_pct = 1.0
            color = (220, 140, 50)
            inner_color = (255, 180, 100)
            glow = True

        self._draw_circular_gauge(brake_x, y, gauge_size, fill_pct, color, inner_color, glow, now, brake_active, is_brake=True)

    def _draw_circular_gauge(self, x, y, size, fill_pct, color, inner_color, glow=False, now=0, active=False, is_brake=False):
        """Draw a minimal circular cooldown gauge"""
        cx, cy = x + size // 2, y + size // 2
        radius = size // 2

        # Subtle outer glow when ready
        if glow:
            pulse = 0.5 + 0.5 * math.sin(now * 0.008)
            glow_alpha = int(25 + 15 * pulse)
            glow_surf = pygame.Surface((size + 12, size + 12), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*color, glow_alpha), (size // 2 + 6, size // 2 + 6), radius + 4)
            self.render_surface.blit(glow_surf, (x - 6, y - 6))

        # Dark background
        pygame.draw.circle(self.render_surface, (18, 20, 25), (cx, cy), radius)

        # Fill arc (clockwise from top)
        if fill_pct > 0:
            points_outer = []
            points_inner = []
            start_angle = -90
            end_angle = start_angle + (360 * fill_pct)
            step = 4
            for angle in range(int(start_angle), int(end_angle) + 1, step):
                rad = math.radians(angle)
                px_o = cx + (radius - 2) * math.cos(rad)
                py_o = cy + (radius - 2) * math.sin(rad)
                points_outer.append((px_o, py_o))
                px_i = cx + (radius - 5) * math.cos(rad)
                py_i = cy + (radius - 5) * math.sin(rad)
                points_inner.append((px_i, py_i))

            if len(points_outer) > 1:
                arc_points = points_outer + points_inner[::-1]
                if len(arc_points) > 2:
                    pygame.draw.polygon(self.render_surface, color, arc_points)

        # Center with icon
        pygame.draw.circle(self.render_surface, (25, 28, 32), (cx, cy), radius - 6)

        # Draw simple icon in center
        icon_color = inner_color if glow else (80, 85, 95)
        if is_brake:
            # Brake icon - horizontal lines
            pygame.draw.line(self.render_surface, icon_color, (cx - 4, cy - 2), (cx + 4, cy - 2), 2)
            pygame.draw.line(self.render_surface, icon_color, (cx - 4, cy + 2), (cx + 4, cy + 2), 2)
        else:
            # Thrust icon - horizontal arrows
            if active:
                # Pulsing effect when thrusting
                pulse = math.sin(now * 0.02) * 2
                pygame.draw.polygon(self.render_surface, icon_color,
                                  [(cx - 4 - pulse, cy), (cx + 2, cy - 3), (cx + 2, cy + 3)])
                pygame.draw.polygon(self.render_surface, icon_color,
                                  [(cx + 4 + pulse, cy), (cx - 2, cy - 3), (cx - 2, cy + 3)])
            else:
                # Static double arrow hint
                pygame.draw.polygon(self.render_surface, icon_color,
                                  [(cx - 4, cy), (cx, cy - 3), (cx, cy + 3)])
                pygame.draw.polygon(self.render_surface, icon_color,
                                  [(cx + 4, cy), (cx, cy - 3), (cx, cy + 3)])

        # Thin outer ring
        ring_color = inner_color if glow else (45, 48, 55)
        pygame.draw.circle(self.render_surface, ring_color, (cx, cy), radius, 1)

    def _draw_controller_button(self, x, y, button, size=20):
        """Draw a stylized controller button icon"""
        colors = {
            'A': ((50, 180, 80), (30, 120, 50)),      # Green
            'B': ((200, 60, 60), (140, 40, 40)),      # Red
            'X': ((60, 120, 200), (40, 80, 140)),     # Blue
            'Y': ((200, 180, 50), (140, 120, 30)),    # Yellow
            'LB': ((100, 100, 120), (70, 70, 90)),    # Gray
            'RB': ((100, 100, 120), (70, 70, 90)),    # Gray
            'LT': ((80, 80, 100), (50, 50, 70)),      # Dark gray
            'RT': ((80, 80, 100), (50, 50, 70)),      # Dark gray
            'START': ((100, 100, 100), (70, 70, 70)), # Gray
            'BACK': ((100, 100, 100), (70, 70, 70)),  # Gray
        }
        fg, bg = colors.get(button, ((100, 100, 100), (70, 70, 70)))

        # Draw button circle/shape
        if button in ['LB', 'RB', 'LT', 'RT']:
            # Bumpers/triggers are rounded rectangles
            rect = pygame.Rect(x, y, size + 10, size - 4)
            pygame.draw.rect(self.render_surface, bg, rect, border_radius=4)
            pygame.draw.rect(self.render_surface, fg, rect, 2, border_radius=4)
            text_x = x + (size + 10) // 2
            text_y = y + (size - 4) // 2
        else:
            # Face buttons are circles
            pygame.draw.circle(self.render_surface, bg, (x + size//2, y + size//2), size//2)
            pygame.draw.circle(self.render_surface, fg, (x + size//2, y + size//2), size//2, 2)
            text_x = x + size // 2
            text_y = y + size // 2

        # Button letter
        font = pygame.font.Font(None, size - 4)
        text = font.render(button, True, (255, 255, 255))
        text_rect = text.get_rect(center=(text_x, text_y))
        self.render_surface.blit(text, text_rect)

    def _draw_control_hints(self, y):
        """Draw controller control hints at bottom of screen"""
        if not self.controller.connected:
            return

        hints = [
            ('A', 'Select'),
            ('B', 'Back'),
        ]

        x = 30
        for button, action in hints:
            self._draw_controller_button(x, y, button, 22)
            text = self.font_small.render(action, True, (150, 150, 150))
            self.render_surface.blit(text, (x + 28, y + 3))
            x += 90

    def _draw_toggle(self, x, y, label, is_on, key):
        """Draw a sleek toggle switch"""
        # Label
        label_text = self.font_small.render(f"[{key}] {label}", True, (140, 140, 140))
        self.render_surface.blit(label_text, (x, y))

        # Toggle track
        track_rect = pygame.Rect(x, y + 18, 50, 20)
        track_color = (40, 80, 40) if is_on else (60, 40, 40)
        pygame.draw.rect(self.render_surface, track_color, track_rect, border_radius=10)
        pygame.draw.rect(self.render_surface, (80, 80, 80), track_rect, 1, border_radius=10)

        # Toggle knob
        knob_x = x + 32 if is_on else x + 8
        knob_color = (100, 200, 100) if is_on else (150, 80, 80)
        pygame.draw.circle(self.render_surface, knob_color, (knob_x, y + 28), 8)
        pygame.draw.circle(self.render_surface, (200, 200, 200), (knob_x, y + 28), 8, 1)

    def draw_ship_select(self):
        """Draw polished ship selection screen"""
        cx = SCREEN_WIDTH // 2

        # Draw faction background
        bg = self.faction_backgrounds.get(self.selected_faction)
        if bg:
            self.render_surface.blit(bg, (0, 0))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))  # Semi-transparent dark overlay
            self.render_surface.blit(overlay, (0, 0))

        # Get faction info
        faction_data = FACTIONS[self.selected_faction]
        faction_color = faction_data['color_primary']

        # Title with glow
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("SELECT YOUR SHIP", True, faction_color)
        rect = title.get_rect(center=(cx, 50))
        self.render_surface.blit(title, rect)

        # Faction badge
        badge_font = pygame.font.Font(None, 24)
        faction_name = faction_data['name'].upper()
        badge_text = badge_font.render(faction_name, True, faction_color)
        badge_rect = badge_text.get_rect(center=(cx, 78))
        self.render_surface.blit(badge_text, badge_rect)

        # Decorative line
        pygame.draw.line(self.render_surface, (*faction_color[:3], 150), (cx - 180, 95), (cx + 180, 95), 2)

        # Helper to get ship display data from roster
        def get_ship_info(ship_key):
            """Get ship info from roster, with fallback display values."""
            data = self.ship_roster.get_ship_display_data(ship_key)
            stats = data.get('stats', {})
            tier = data.get('tier', 't1')

            # Map tier to display class
            tier_class_map = {
                't1': 'T1 Frigate',
                't2': 'T2 Assault Frigate',
                't3': 'T3 Tactical',
                'capital': 'Capital Ship',
                'titan': 'Titan'
            }

            # Normalize stats to 0-150 scale for display bars
            hull = stats.get('hull', 100)
            shield = stats.get('shield', 80)
            speed = stats.get('speed', 350)
            damage = stats.get('damage', 1.0)

            # Scale to visual bar range (0-150)
            speed_bar = min(150, int(speed / 4))  # 350 speed -> ~87
            armor_bar = min(150, hull + int(shield * 0.5))  # Combined tankiness
            power_bar = min(150, int(damage * 100))  # 1.0 -> 100, 1.5 -> 150

            return {
                'name': data.get('name', ship_key.upper()).upper(),
                'type_id': data.get('type_id'),
                'class': tier_class_map.get(tier, 'T1 Frigate'),
                'tier': tier,
                'catchphrase': data.get('catchphrase', ''),
                'desc': data.get('catchphrase', '') or f"A reliable {tier.upper()} ship.",
                'desc_locked': f"Unlock: {data.get('unlock', 'Complete campaign')}",
                'speed': speed_bar,
                'armor': armor_bar,
                'firepower': power_bar,
                'color': faction_color,
                'icon_color': faction_color,
                'locked': data.get('locked', False)
            }

        # ========================================
        # LARGE SHIP PREVIEW (Selected Ship)
        # ========================================
        selected_key = self.ship_options[self.ship_select_index]
        selected_info = get_ship_info(selected_key)
        is_selected_locked = selected_info['locked'] and not self.t2_ships_unlocked

        # Preview area - centered above card row
        preview_y = 110
        preview_size = 180

        # Try to load high-res render for preview
        from sprites import load_ship_sprite
        preview_sprite = None
        for sprite_name in [f"{selected_key}_render_256", f"{selected_key}_render_512", selected_key]:
            preview_sprite = load_ship_sprite(sprite_name, (preview_size, preview_size))
            if preview_sprite:
                break

        if preview_sprite:
            # Glow effect behind selected ship
            if not is_selected_locked:
                glow_surf = pygame.Surface((preview_size + 60, preview_size + 60), pygame.SRCALPHA)
                pulse = int(20 + 10 * math.sin(pygame.time.get_ticks() * 0.003))
                for r in range(30, 0, -3):
                    alpha = pulse * r // 30
                    pygame.draw.circle(glow_surf, (*faction_color[:3], alpha),
                                      (preview_size // 2 + 30, preview_size // 2 + 30), preview_size // 2 + r)
                self.render_surface.blit(glow_surf, (cx - preview_size // 2 - 30, preview_y - 10))

            # Ship sprite
            if is_selected_locked:
                dark_surf = preview_sprite.copy()
                dark_surf.fill((60, 60, 80, 200), special_flags=pygame.BLEND_RGBA_MULT)
                sprite_rect = dark_surf.get_rect(center=(cx, preview_y + preview_size // 2))
                self.render_surface.blit(dark_surf, sprite_rect)
            else:
                sprite_rect = preview_sprite.get_rect(center=(cx, preview_y + preview_size // 2))
                self.render_surface.blit(preview_sprite, sprite_rect)

        # Ship name (large)
        name_y = preview_y + preview_size + 10
        name_font = pygame.font.Font(None, 42)
        name_color = (80, 80, 90) if is_selected_locked else faction_color
        name_text = name_font.render(selected_info['name'], True, name_color)
        name_rect = name_text.get_rect(center=(cx, name_y))
        self.render_surface.blit(name_text, name_rect)

        # Catchphrase
        if selected_info['catchphrase'] and not is_selected_locked:
            catch_font = pygame.font.Font(None, 22)
            catch_text = catch_font.render(f'"{selected_info["catchphrase"]}"', True, (180, 160, 140))
            catch_rect = catch_text.get_rect(center=(cx, name_y + 25))
            self.render_surface.blit(catch_text, catch_rect)

        # Ship class badge
        class_y = name_y + 48
        class_color = (100, 80, 60) if is_selected_locked else (140, 140, 140)
        class_text = self.font_small.render(selected_info['class'], True, class_color)
        class_rect = class_text.get_rect(center=(cx, class_y))
        self.render_surface.blit(class_text, class_rect)

        # ========================================
        # SHIP THUMBNAIL CARDS (Row below preview)
        # ========================================
        card_y_start = 365

        # Draw ship cards (compact thumbnails - details shown in preview above)
        card_width = 100
        card_height = 120
        spacing = 20
        total_width = len(self.ship_options) * card_width + (len(self.ship_options) - 1) * spacing
        start_x = cx - total_width // 2

        for i, ship_key in enumerate(self.ship_options):
            ship = get_ship_info(ship_key)
            is_selected = i == self.ship_select_index
            is_locked = ship['locked'] and not self.t2_ships_unlocked
            card_x = start_x + i * (card_width + spacing)
            card_y = card_y_start

            # Card background
            card_rect = pygame.Rect(card_x, card_y, card_width, card_height)
            card_surf = pygame.Surface((card_width, card_height), pygame.SRCALPHA)

            if is_locked:
                # Locked card - dark, grayed out
                card_surf.fill((15, 15, 20, 200))
                pygame.draw.rect(card_surf, (50, 50, 60), (0, 0, card_width, card_height), 2, border_radius=8)
            elif is_selected:
                # Selected card - bright border, lifted effect
                card_surf.fill((30, 30, 45, 230))
                pygame.draw.rect(card_surf, ship['color'], (0, 0, card_width, card_height), 3, border_radius=8)
                # Glow effect
                glow_rect = pygame.Rect(card_x - 4, card_y - 4, card_width + 8, card_height + 8)
                pygame.draw.rect(self.render_surface, (*ship['color'][:3], 60), glow_rect, border_radius=10)
            else:
                card_surf.fill((20, 20, 30, 180))
                pygame.draw.rect(card_surf, (60, 60, 70), (0, 0, card_width, card_height), 2, border_radius=8)

            self.render_surface.blit(card_surf, card_rect)

            # Ship sprite thumbnail (compact card)
            icon_cx = card_x + card_width // 2
            icon_cy = card_y + 45
            sprite_size = 50

            try:
                ship_sprite = load_ship_sprite(ship_key, (sprite_size, sprite_size))
                if ship_sprite:
                    if is_locked:
                        dark_surf = ship_sprite.copy()
                        dark_surf.fill((30, 30, 40, 180), special_flags=pygame.BLEND_RGBA_MULT)
                        sprite_rect = dark_surf.get_rect(center=(icon_cx, icon_cy))
                        self.render_surface.blit(dark_surf, sprite_rect)
                    else:
                        sprite_rect = ship_sprite.get_rect(center=(icon_cx, icon_cy))
                        self.render_surface.blit(ship_sprite, sprite_rect)
                else:
                    raise Exception("No sprite")
            except Exception:
                # Fallback to geometric ship
                icon_color = (40, 40, 50) if is_locked else ((80, 80, 90) if not is_selected else ship['icon_color'])
                ship_points = [
                    (icon_cx, icon_cy - 20),
                    (icon_cx + 15, icon_cy + 15),
                    (icon_cx, icon_cy + 8),
                    (icon_cx - 15, icon_cy + 15)
                ]
                pygame.draw.polygon(self.render_surface, icon_color, ship_points)

            # Lock icon for locked ships
            if is_locked:
                lock_y = icon_cy
                pygame.draw.rect(self.render_surface, (80, 60, 40), (icon_cx - 6, lock_y, 12, 10), border_radius=2)
                pygame.draw.arc(self.render_surface, (80, 60, 40), (icon_cx - 5, lock_y - 6, 10, 10), 0, 3.14, 2)

            # Ship name (compact)
            name_color = (80, 80, 90) if is_locked else ((255, 220, 180) if is_selected else (150, 150, 150))
            name_font = pygame.font.Font(None, 20)
            name_text = name_font.render(ship['name'], True, name_color)
            name_rect = name_text.get_rect(center=(card_x + card_width // 2, card_y + 90))
            self.render_surface.blit(name_text, name_rect)

            # Tier badge
            tier_text = "LOCKED" if is_locked else ship['tier'].upper()
            tier_color = (120, 80, 60) if is_locked else ((200, 180, 100) if ship['tier'] == 't2' else (120, 120, 120))
            tier_label = self.font_small.render(tier_text, True, tier_color)
            tier_rect = tier_label.get_rect(center=(card_x + card_width // 2, card_y + 108))
            self.render_surface.blit(tier_label, tier_rect)

        # Selected ship stats panel (below cards)
        desc_y = card_y_start + card_height + 20
        stats_panel = pygame.Surface((SCREEN_WIDTH - 80, 70), pygame.SRCALPHA)
        stats_panel.fill((20, 20, 30, 160))
        pygame.draw.rect(stats_panel, (60, 50, 45), (0, 0, SCREEN_WIDTH - 80, 70), 1, border_radius=4)
        self.render_surface.blit(stats_panel, (40, desc_y))

        # Show stats or unlock info
        if is_selected_locked:
            desc_text = self.font.render(selected_info['desc_locked'], True, (150, 100, 80))
            desc_rect = desc_text.get_rect(center=(cx, desc_y + 35))
            self.render_surface.blit(desc_text, desc_rect)
        else:
            # Stat bars in panel
            stat_y = desc_y + 15
            stat_bar_width = 120
            stat_spacing = 180
            start_stat_x = cx - stat_spacing
            stats_display = [
                ('HULL', selected_info['armor'], (100, 150, 255)),
                ('SPEED', selected_info['speed'], (100, 200, 100)),
                ('POWER', selected_info['firepower'], (255, 150, 100))
            ]
            for j, (stat_name, stat_val, stat_color) in enumerate(stats_display):
                sx = start_stat_x + j * stat_spacing
                # Label
                label = self.font_small.render(stat_name, True, (120, 120, 120))
                self.render_surface.blit(label, (sx - stat_bar_width // 2, stat_y))
                # Bar background
                bar_rect = pygame.Rect(sx - stat_bar_width // 2, stat_y + 18, stat_bar_width, 10)
                pygame.draw.rect(self.render_surface, (40, 40, 50), bar_rect, border_radius=3)
                # Bar fill
                fill_width = int(stat_bar_width * stat_val / 150)
                if fill_width > 0:
                    pygame.draw.rect(self.render_surface, stat_color,
                                   (sx - stat_bar_width // 2, stat_y + 18, fill_width, 10), border_radius=3)

        # Controls hint
        hint_y = SCREEN_HEIGHT - 50
        controls = [
            ("[W/S]", "Select"),
            ("[ENTER]", "Confirm"),
            ("[ESC]", "Back")
        ]
        hint_x = cx - 150
        for key, action in controls:
            key_text = self.font_small.render(key, True, (100, 100, 100))
            self.render_surface.blit(key_text, (hint_x, hint_y))
            action_text = self.font_small.render(action, True, (160, 160, 160))
            self.render_surface.blit(action_text, (hint_x + 50, hint_y))
            hint_x += 110

    def draw_pause(self):
        """Draw pause menu with options"""
        cx = SCREEN_WIDTH // 2

        # Animated timer for effects
        if not hasattr(self, 'pause_timer'):
            self.pause_timer = 0
        self.pause_timer += 1

        # Dark overlay with slight vignette
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.render_surface.blit(overlay, (0, 0))

        # Title with glow effect
        glow_alpha = int(30 + 15 * math.sin(self.pause_timer * 0.06))
        for offset in range(8, 0, -2):
            glow_surf = self.font_large.render("PAUSED", True, (180, 100, 50))
            glow_surf.set_alpha(glow_alpha // (offset // 2 + 1))
            rect = glow_surf.get_rect(center=(cx, 80 + offset // 2))
            self.render_surface.blit(glow_surf, rect)

        text = self.font_large.render("PAUSED", True, COLOR_MINMATAR_ACCENT)
        rect = text.get_rect(center=(cx, 80))
        self.render_surface.blit(text, rect)

        # Menu panel with rounded corners
        box_rect = pygame.Rect(cx - 160, 120, 320, 220)
        panel_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        panel_surf.fill((15, 15, 25, 220))
        pygame.draw.rect(panel_surf, (80, 60, 50), (0, 0, box_rect.width, box_rect.height), 2, border_radius=8)
        self.render_surface.blit(panel_surf, box_rect)

        # Draw menu options with improved styling
        y = 150
        for i, option in enumerate(self.pause_menu_options):
            is_selected = i == self.pause_menu_index

            if is_selected:
                # Animated pulse
                pulse = int(8 * math.sin(self.pause_timer * 0.1))

                # Highlight background
                highlight_rect = pygame.Rect(cx - 145, y - 5, 290, 38)
                pygame.draw.rect(self.render_surface, (50, 40, 35), highlight_rect, border_radius=4)
                pygame.draw.rect(self.render_surface, (180 + pulse, 100 + pulse//2, 50), highlight_rect, 2, border_radius=4)

                # Selection arrow
                pygame.draw.polygon(self.render_surface, (200, 120, 60),
                    [(cx - 155, y + 12), (cx - 145, y + 6), (cx - 145, y + 18)])

                # Controller button icon
                if self.controller.connected:
                    self._draw_controller_button(cx + 100, y, 'A', 22)

                color = (255, 230, 180)
            else:
                color = (140, 140, 140)

            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(cx, y + 12))
            self.render_surface.blit(text, rect)
            y += 45

        # Current game status panel
        status_y = 365
        status_rect = pygame.Rect(cx - 150, status_y - 5, 300, 50)
        pygame.draw.rect(self.render_surface, (20, 20, 30, 180), status_rect, border_radius=4)
        pygame.draw.rect(self.render_surface, (60, 50, 45), status_rect, 1, border_radius=4)

        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        ship_label = self.font_small.render(f"Ship: {ship_class}", True, (150, 120, 100))
        self.render_surface.blit(ship_label, (cx - 140, status_y))
        score_label = self.font_small.render(f"Score: {self.player.score:,}", True, (180, 180, 100))
        self.render_surface.blit(score_label, (cx - 140, status_y + 18))

        if self.game_mode == 'endless':
            wave_label = self.font_small.render(f"Wave: {self.endless_wave}", True, (100, 150, 200))
        else:
            wave_label = self.font_small.render(f"Stage: {self.current_stage + 1}", True, (100, 150, 200))
        self.render_surface.blit(wave_label, (cx + 50, status_y + 9))

        # Controls hint bar at bottom
        hint_y = SCREEN_HEIGHT - 60
        hint_rect = pygame.Rect(30, hint_y - 5, SCREEN_WIDTH - 60, 45)
        pygame.draw.rect(self.render_surface, (15, 15, 25, 180), hint_rect, border_radius=4)

        if self.controller.connected:
            # Controller hints with button icons
            x = 50
            hints = [('A', 'Select'), ('B', 'Resume'), ('START', 'Resume')]
            for btn, action in hints:
                self._draw_controller_button(x, hint_y + 5, btn, 20)
                text = self.font_small.render(action, True, (120, 120, 120))
                w = 30 if btn in ['START'] else 26
                self.render_surface.blit(text, (x + w, hint_y + 8))
                x += 100
        else:
            # Keyboard hints
            hints_text = "ESC: Resume    ENTER: Select    UP/DOWN: Navigate"
            text = self.font_small.render(hints_text, True, (100, 100, 100))
            rect = text.get_rect(center=(cx, hint_y + 15))
            self.render_surface.blit(text, rect)
    
    def draw_shop(self):
        """Draw upgrade shop"""
        # Title
        title = self.font_large.render("REBEL STATION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.render_surface.blit(title, rect)
        
        # Refugees
        text = self.font.render(f"Refugees Available: {self.player.refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(text, rect)
        
        # Upgrade options
        y = 160
        costs = UPGRADE_COSTS
        player = self.player
        
        upgrades = [
            ("1", "Gyrostabilizer", costs['gyrostabilizer'], player.has_gyro, "+30% Fire Rate"),
            ("2", "Armor Plate", costs['armor_plate'], False, "+30 Max Armor"),
            ("3", "Tracking Enhancer", costs['tracking_enhancer'], player.has_tracking, "+1 Gun Spread"),
            ("4", "EMP Ammo", costs['emp_ammo'], 'emp' in player.unlocked_ammo, "Strong vs Shields"),
            ("5", "Phased Plasma", costs['plasma_ammo'], 'plasma' in player.unlocked_ammo, "Strong vs Armor"),
            ("6", "Fusion Ammo", costs['fusion_ammo'], 'fusion' in player.unlocked_ammo, "High Damage"),
            ("7", "Barrage Ammo", costs['barrage_ammo'], 'barrage' in player.unlocked_ammo, "Fast Fire"),
            ("8", "WOLF UPGRADE", costs['wolf_upgrade'], player.is_wolf, "T2 Armor/Dmg"),
            ("9", "JAGUAR UPGRADE", costs['jaguar_upgrade'], player.is_wolf, "T2 Speed/Shield")
        ]
        
        for key, name, cost, owned, desc in upgrades:
            if owned:
                color = (80, 80, 80)
                status = "[OWNED]"
            elif player.refugees >= cost:
                color = (100, 255, 100)
                status = f"[{cost} refugees]"
            else:
                color = (255, 100, 100)
                status = f"[{cost} refugees]"
            
            text = self.font.render(f"[{key}] {name} - {desc} {status}", True, color)
            self.render_surface.blit(text, (50, y))
            y += 35
        
        # Continue prompt
        y += 30
        text = self.font.render("Press ENTER to continue to next stage", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_gameover(self):
        """Draw game over screen with berserk stats"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((80, 0, 0, 180))
        self.render_surface.blit(overlay, (0, 0))

        # Title
        text = self.font_large.render("SHIP DESTROYED", True, (255, 100, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.render_surface.blit(text, rect)

        # Main stats
        y = 180
        score_color = (255, 215, 0) if self.new_high_score else (255, 200, 100)
        text = self.font_large.render(f"Final Score: {self.player.score}", True, score_color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # High score / rank info
        if self.new_high_score:
            hs_text = self.font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            self.render_surface.blit(hs_text, hs_rect)
            y += 15
        elif self.last_rank > 0:
            rank_text = self.font_small.render(f"Rank #{self.last_rank} on leaderboard", True, (200, 200, 100))
            rank_rect = rank_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            self.render_surface.blit(rank_text, rank_rect)
            y += 10

        # Faction-specific rescued text
        if self.selected_faction == 'minmatar':
            rescue_text = f"Souls Liberated: {self.player.total_refugees}"
        else:
            rescue_text = f"Civilians Secured: {self.player.total_refugees}"
        text = self.font.render(rescue_text, True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.render_surface.blit(text, rect)

        # Stage/Wave reached
        if self.game_mode == 'endless':
            # Endless mode stats
            minutes = self.endless_time // 3600
            seconds = (self.endless_time // 60) % 60
            text = self.font.render(f"Survived: Wave {self.endless_wave}", True, (255, 150, 100))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 65))
            self.render_surface.blit(text, rect)

            time_text = self.font_small.render(f"Time: {minutes:02d}:{seconds:02d}", True, COLOR_TEXT)
            time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, y + 90))
            self.render_surface.blit(time_text, time_rect)

            # Best wave indicator
            if self.endless_wave >= self.endless_high_wave:
                best_text = self.font_small.render("NEW BEST WAVE!", True, (255, 215, 0))
                best_rect = best_text.get_rect(center=(SCREEN_WIDTH // 2, y + 115))
                self.render_surface.blit(best_text, best_rect)
                y += 25
        else:
            stage_name = self.active_stages[self.current_stage]['name'] if self.current_stage < len(self.active_stages) else "Final Stage"
            text = self.font_small.render(f"Reached: {stage_name} - Wave {self.current_wave + 1}", True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 70))
            self.render_surface.blit(text, rect)

        # Berserk stats box
        y += 110
        box_rect = pygame.Rect(80, y, SCREEN_WIDTH - 160, 120)
        pygame.draw.rect(self.render_surface, (40, 20, 20), box_rect)
        pygame.draw.rect(self.render_surface, (150, 80, 80), box_rect, 2)

        berserk_stats = self.berserk.get_stats()
        kills = berserk_stats['kills_by_range']
        total_kills = berserk_stats.get('total_kills', 0)
        avg_mult = berserk_stats.get('avg_multiplier', 1.0)

        text = self.font.render("COMBAT ANALYSIS", True, (255, 150, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 15))
        self.render_surface.blit(text, rect)

        y += 40
        text = self.font_small.render(f"Total Kills: {total_kills}  |  Avg Multiplier: x{avg_mult:.2f}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        extreme = kills.get('EXTREME', 0)
        close = kills.get('CLOSE', 0)
        text = self.font_small.render(f"Extreme Kills: {extreme}  |  Close Range: {close}", True, (255, 150, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 25))
        self.render_surface.blit(text, rect)

        # Ship info
        y += 70
        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        text = self.font_small.render(f"Ship: {ship_class}  |  Difficulty: {self.difficulty_settings['name']}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # Continue prompt
        text = self.font.render("Press ENTER to return to menu", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 45))
        self.render_surface.blit(text, rect)

        # Quick restart hint
        restart_text = self.font_small.render("[R] or (X) Quick Restart", True, (150, 150, 150))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, y + 70))
        self.render_surface.blit(restart_text, restart_rect)

    def draw_victory(self):
        """Draw victory screen with berserk stats"""
        # Faction-specific colors and text
        faction_data = FACTIONS[self.selected_faction]
        faction_color = faction_data['color_primary']

        title = self.font_large.render("VICTORY!", True, faction_color)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.render_surface.blit(title, rect)

        # Faction tagline
        tagline = self.font.render(faction_data['tagline'], True, faction_color)
        rect = tagline.get_rect(center=(SCREEN_WIDTH // 2, 120))
        self.render_surface.blit(tagline, rect)

        # Victory text (wrapped)
        victory_text = faction_data['victory_text']
        words = victory_text.split()
        lines = []
        current_line = ""
        max_width = SCREEN_WIDTH - 200

        for word in words:
            test_line = current_line + " " + word if current_line else word
            test_surf = self.font_small.render(test_line, True, COLOR_TEXT)
            if test_surf.get_width() < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        y_offset = 150
        for line in lines[:2]:  # Max 2 lines
            text = self.font_small.render(line, True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.render_surface.blit(text, rect)
            y_offset += 22

        # Main stats
        y = 210
        text = self.font_large.render(f"Final Score: {self.player.score}", True, (255, 215, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # High score / rank info
        if self.new_high_score:
            hs_text = self.font.render("NEW HIGH SCORE!", True, (255, 255, 100))
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            self.render_surface.blit(hs_text, hs_rect)
            y += 10
        elif self.last_rank > 0 and self.last_rank <= 3:
            rank_text = self.font.render(f"#{self.last_rank} on Leaderboard!", True, (255, 200, 100))
            rank_rect = rank_text.get_rect(center=(SCREEN_WIDTH // 2, y + 30))
            self.render_surface.blit(rank_text, rank_rect)
            y += 10

        # Faction-specific rescued text
        if self.selected_faction == 'minmatar':
            rescue_text = f"Souls Liberated: {self.player.total_refugees}"
        else:
            rescue_text = f"Civilians Secured: {self.player.total_refugees}"
        text = self.font.render(rescue_text, True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.render_surface.blit(text, rect)

        # Berserk stats
        berserk_stats = self.berserk.get_stats()
        y += 90

        # Draw berserk stats box
        box_rect = pygame.Rect(80, y - 10, SCREEN_WIDTH - 160, 160)
        pygame.draw.rect(self.render_surface, (30, 30, 40), box_rect)
        pygame.draw.rect(self.render_surface, (100, 80, 60), box_rect, 2)

        text = self.font.render("BERSERK PERFORMANCE", True, (255, 150, 50))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 5))
        self.render_surface.blit(text, rect)

        y += 35
        # Kill breakdown by range
        kills = berserk_stats['kills_by_range']
        extreme_kills = kills.get('EXTREME', 0)
        close_kills = kills.get('CLOSE', 0)
        safe_kills = kills.get('FAR', 0) + kills.get('VERY_FAR', 0)

        text = self.font_small.render(f"Extreme Close Kills (5x): {extreme_kills}", True, (255, 50, 50))
        self.render_surface.blit(text, (100, y))

        text = self.font_small.render(f"Close Range Kills (3x): {close_kills}", True, (255, 150, 50))
        self.render_surface.blit(text, (100, y + 22))

        text = self.font_small.render(f"Safe Distance Kills: {safe_kills}", True, (100, 200, 100))
        self.render_surface.blit(text, (100, y + 44))

        # Average multiplier
        avg_mult = berserk_stats.get('avg_multiplier', 1.0)
        mult_color = (255, 50, 50) if avg_mult >= 3.0 else ((255, 200, 50) if avg_mult >= 1.5 else (150, 150, 150))
        text = self.font.render(f"Avg Multiplier: x{avg_mult:.2f}", True, mult_color)
        rect = text.get_rect(right=SCREEN_WIDTH - 100, top=y)
        self.render_surface.blit(text, rect)

        # Risk rating
        total_kills = berserk_stats.get('total_kills', 1)
        risk_pct = ((extreme_kills + close_kills) / total_kills * 100) if total_kills > 0 else 0
        if risk_pct >= 50:
            rating = "BERSERKER"
            rating_color = (255, 50, 50)
        elif risk_pct >= 30:
            rating = "AGGRESSIVE"
            rating_color = (255, 150, 50)
        elif risk_pct >= 15:
            rating = "BALANCED"
            rating_color = (255, 255, 100)
        else:
            rating = "CAUTIOUS"
            rating_color = (100, 200, 100)

        text = self.font.render(f"Combat Style: {rating}", True, rating_color)
        rect = text.get_rect(right=SCREEN_WIDTH - 100, top=y + 30)
        self.render_surface.blit(text, rect)

        # Ship and difficulty
        y += 100
        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        ship_type = f"{ship_class} {'Assault Frigate' if self.player.is_wolf else 'Frigate'}"
        text = self.font_small.render(f"Ship: {ship_type}  |  Difficulty: {self.difficulty_settings['name']}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        text = self.font.render("Press ENTER to play again", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 45))
        self.render_surface.blit(text, rect)

        # Quick restart hint
        restart_text = self.font_small.render("[R] or (X) Quick Restart", True, (150, 150, 150))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, y + 70))
        self.render_surface.blit(restart_text, restart_rect)

    def draw_settings(self, from_pause=False):
        """Draw settings menu"""
        if from_pause:
            # Darken the game in the background
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.render_surface.blit(overlay, (0, 0))
        else:
            # Background with stars
            self.render_surface.fill((10, 10, 20))
            for star in self.stars:
                star.draw(self.render_surface)

        # Title
        title = self.font_large.render("SETTINGS", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.render_surface.blit(title, rect)

        # Settings box
        box_rect = pygame.Rect(60, 100, SCREEN_WIDTH - 120, 400)
        pygame.draw.rect(self.render_surface, (20, 20, 30), box_rect)
        pygame.draw.rect(self.render_surface, COLOR_MINMATAR_ACCENT, box_rect, 2)

        y = 130
        for i, (key, label, option_type) in enumerate(self.settings_options):
            is_selected = i == self.settings_index
            color = (255, 255, 100) if is_selected else COLOR_TEXT
            value = self.settings[key]

            # Draw selector arrow
            if is_selected:
                arrow = self.font.render(">", True, COLOR_MINMATAR_ACCENT)
                self.render_surface.blit(arrow, (80, y))

            # Draw label
            label_text = self.font.render(label, True, color)
            self.render_surface.blit(label_text, (110, y))

            # Draw value/control
            if option_type == 'toggle':
                value_text = "ON" if value else "OFF"
                value_color = (100, 255, 100) if value else (255, 100, 100)
                val_surface = self.font.render(value_text, True, value_color)
                val_rect = val_surface.get_rect(right=SCREEN_WIDTH - 100, top=y)
                self.render_surface.blit(val_surface, val_rect)

                if is_selected:
                    # Special hint for screen shake with preview option
                    if key == 'screen_shake':
                        hint = self.font_small.render("SPACE toggle | ENTER preview", True, (150, 150, 150))
                    else:
                        hint = self.font_small.render("< SPACE/ENTER to toggle >", True, (150, 150, 150))
                    hint_rect = hint.get_rect(right=SCREEN_WIDTH - 100, top=y + 24)
                    self.render_surface.blit(hint, hint_rect)

            elif option_type == 'slider':
                # Draw slider bar
                bar_x = SCREEN_WIDTH - 250
                bar_width = 140
                bar_height = 16
                bar_y = y + 4

                # Background
                pygame.draw.rect(self.render_surface, (50, 50, 60),
                               (bar_x, bar_y, bar_width, bar_height))
                # Fill
                fill_width = int(bar_width * value / 100)
                pygame.draw.rect(self.render_surface, COLOR_MINMATAR_ACCENT,
                               (bar_x, bar_y, fill_width, bar_height))
                # Border
                pygame.draw.rect(self.render_surface, color,
                               (bar_x, bar_y, bar_width, bar_height), 1)

                # Value text
                val_surface = self.font_small.render(f"{value}%", True, color)
                val_rect = val_surface.get_rect(left=bar_x + bar_width + 10, centery=bar_y + bar_height // 2)
                self.render_surface.blit(val_surface, val_rect)

                if is_selected:
                    hint = self.font_small.render("< LEFT/RIGHT to adjust >", True, (150, 150, 150))
                    hint_rect = hint.get_rect(right=SCREEN_WIDTH - 100, top=y + 24)
                    self.render_surface.blit(hint, hint_rect)

            y += 50

        # Controls reference
        y += 30
        pygame.draw.line(self.render_surface, (60, 60, 80), (80, y), (SCREEN_WIDTH - 80, y), 1)
        y += 20

        controls_title = self.font.render("CONTROLS REFERENCE", True, COLOR_MINMATAR_ACCENT)
        ctrl_rect = controls_title.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(controls_title, ctrl_rect)
        y += 30

        controls = [
            ("WASD/Arrows", "Move"),
            ("Space/LMB/RT", "Fire Autocannons"),
            ("Shift/RMB/LT", "Fire Rockets"),
            ("1-5/Q/RB", "Switch Ammo"),
            ("F/Y", "Ship Ability"),
            ("G/X", "Bomb (clears screen)"),
        ]

        for key, action in controls:
            text = self.font_small.render(f"{key}: {action}", True, (150, 150, 150))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.render_surface.blit(text, rect)
            y += 20

        # Exit hint
        y = SCREEN_HEIGHT - 50
        hint_text = "Press ESC to return" if from_pause else "Press ESC to return to menu"
        hint = self.font.render(hint_text, True, COLOR_TEXT)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(hint, hint_rect)

    def draw_leaderboard(self):
        """Draw leaderboard/high scores screen"""
        # Background with stars
        self.render_surface.fill((10, 10, 20))
        for star in self.stars:
            star.draw(self.render_surface)

        # Title
        title = self.font_large.render("LEADERBOARD", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.render_surface.blit(title, rect)

        # Get top 10 scores
        scores = self.high_scores.get_top_scores(10)

        if not scores:
            # No scores yet
            text = self.font.render("No scores yet!", True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300))
            self.render_surface.blit(text, rect)

            text = self.font_small.render("Play a game to set your first high score", True, (150, 150, 150))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, 340))
            self.render_surface.blit(text, rect)
        else:
            # Header
            y = 100
            header_color = (150, 150, 150)
            headers = [("RANK", 60), ("SCORE", 180), ("WAVE", 320), ("SHIP", 420), ("DIFF", 520)]
            for header, x in headers:
                text = self.font_small.render(header, True, header_color)
                self.render_surface.blit(text, (x, y))

            pygame.draw.line(self.render_surface, (60, 60, 80), (50, y + 22), (SCREEN_WIDTH - 50, y + 22), 1)

            # Scores
            y = 130
            for i, entry in enumerate(scores):
                rank = i + 1

                # Highlight colors for top 3
                if rank == 1:
                    color = (255, 215, 0)  # Gold
                elif rank == 2:
                    color = (192, 192, 192)  # Silver
                elif rank == 3:
                    color = (205, 127, 50)  # Bronze
                else:
                    color = COLOR_TEXT

                # Rank
                rank_text = self.font.render(f"#{rank}", True, color)
                self.render_surface.blit(rank_text, (60, y))

                # Score
                score_text = self.font.render(f"{entry['score']:,}", True, color)
                self.render_surface.blit(score_text, (130, y))

                # Wave/Stage
                stage = entry.get('stage', 0)
                wave = entry.get('wave', 0)
                if stage == 0:
                    # Endless mode
                    wave_text = self.font_small.render(f"Wave {wave}", True, (255, 150, 100))
                else:
                    wave_text = self.font_small.render(f"S{stage+1} W{wave+1}", True, color)
                self.render_surface.blit(wave_text, (300, y + 3))

                # Ship
                ship = entry.get('ship', 'Rifter')
                ship_text = self.font_small.render(ship, True, color)
                self.render_surface.blit(ship_text, (400, y + 3))

                # Difficulty - EVE themed names
                diff = entry.get('difficulty', 'normal')
                diff_colors = {
                    'easy': (100, 255, 100),
                    'normal': COLOR_TEXT,
                    'hard': (255, 200, 100),
                    'nightmare': (255, 100, 100)
                }
                diff_names = {
                    'easy': 'Carebear',
                    'normal': 'Newbro',
                    'hard': 'Bitter Vet',
                    'nightmare': 'Triglavian'
                }
                diff_text = self.font_small.render(diff_names.get(diff, diff.capitalize()), True, diff_colors.get(diff, COLOR_TEXT))
                self.render_surface.blit(diff_text, (500, y + 3))

                # Date (smaller, right side)
                date = entry.get('date', '')
                if date:
                    date_text = self.font_small.render(date, True, (100, 100, 100))
                    date_rect = date_text.get_rect(right=SCREEN_WIDTH - 60, top=y + 3)
                    self.render_surface.blit(date_text, date_rect)

                y += 40

        # Endless mode best
        y = SCREEN_HEIGHT - 120
        pygame.draw.line(self.render_surface, (60, 60, 80), (50, y), (SCREEN_WIDTH - 50, y), 1)
        y += 15

        endless_title = self.font.render("ENDLESS MODE BEST", True, (255, 150, 100))
        endless_rect = endless_title.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(endless_title, endless_rect)
        y += 30

        if self.endless_high_wave > 0:
            endless_text = self.font.render(f"Wave {self.endless_high_wave}  |  Score: {self.endless_high_score:,}", True, (255, 200, 100))
        else:
            endless_text = self.font_small.render("No endless runs yet", True, (150, 150, 150))
        endless_rect = endless_text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(endless_text, endless_rect)

        # Exit hint
        y = SCREEN_HEIGHT - 40
        hint = self.font.render("Press ESC to return to menu", True, COLOR_TEXT)
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(hint, hint_rect)

    def draw_credits(self):
        """Draw credits screen with scrolling text"""
        # Background
        self.render_surface.fill((5, 5, 15))

        # Draw some stars
        for star in self.stars:
            star.draw(self.render_surface)

        # Credits content
        credits_lines = [
            ("EVE REBELLION", "title"),
            ("", ""),
            ("An EVE-Inspired Arcade Shooter", "subtitle"),
            ("", ""),
            ("", ""),
            ("DEVELOPMENT", "header"),
            ("", ""),
            ("Game Design & Programming", "label"),
            ("Created with Python & Pygame", "text"),
            ("", ""),
            ("Procedural Audio", "label"),
            ("Vaporwave Music Generator", "text"),
            ("", ""),
            ("Visual Effects", "label"),
            ("Particle Systems & Shaders", "text"),
            ("", ""),
            ("", ""),
            ("INSPIRED BY", "header"),
            ("", ""),
            ("EVE Online", "text"),
            ("CCP Games", "small"),
            ("", ""),
            ("Classic Arcade Shooters", "text"),
            ("", ""),
            ("", ""),
            ("SPECIAL THANKS", "header"),
            ("", ""),
            ("The Pygame Community", "text"),
            ("Open Source Contributors", "text"),
            ("Coffee & Late Nights", "text"),
            ("", ""),
            ("", ""),
            ("TECHNOLOGIES", "header"),
            ("", ""),
            ("Python 3", "text"),
            ("Pygame 2", "text"),
            ("NumPy", "text"),
            ("", ""),
            ("", ""),
            ("", ""),
            ("Thank you for playing!", "subtitle"),
            ("", ""),
            ("Press ESC to return", "small"),
        ]

        # Update scroll
        if not hasattr(self, 'credits_scroll'):
            self.credits_scroll = 0
        self.credits_scroll += 0.5

        # Reset scroll if past end
        total_height = len(credits_lines) * 35 + SCREEN_HEIGHT
        if self.credits_scroll > total_height:
            self.credits_scroll = 0

        # Draw credits
        y_base = SCREEN_HEIGHT - self.credits_scroll

        for line_text, style in credits_lines:
            y = y_base

            # Skip if off screen
            if y < -50 or y > SCREEN_HEIGHT + 50:
                y_base += 35
                continue

            # Style-based rendering
            if style == "title":
                font = pygame.font.Font(None, 64)
                color = COLOR_MINMATAR_ACCENT
                y_base += 50
            elif style == "subtitle":
                font = pygame.font.Font(None, 36)
                color = (200, 150, 100)
                y_base += 40
            elif style == "header":
                font = pygame.font.Font(None, 42)
                color = (255, 200, 100)
                y_base += 45
            elif style == "label":
                font = pygame.font.Font(None, 28)
                color = (150, 200, 150)
                y_base += 30
            elif style == "text":
                font = pygame.font.Font(None, 32)
                color = COLOR_TEXT
                y_base += 35
            elif style == "small":
                font = pygame.font.Font(None, 22)
                color = (120, 120, 120)
                y_base += 25
            else:
                y_base += 20
                continue

            if line_text:
                text = font.render(line_text, True, color)
                rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.render_surface.blit(text, rect)

        # Draw gradient fade at top and bottom
        for i in range(60):
            int(255 * (60 - i) / 60)
            pygame.draw.line(self.render_surface, (5, 5, 15),
                           (0, i), (SCREEN_WIDTH, i), 1)
            pygame.draw.line(self.render_surface, (5, 5, 15),
                           (0, SCREEN_HEIGHT - i), (SCREEN_WIDTH, SCREEN_HEIGHT - i), 1)

    def draw_how_to_play(self):
        """Draw how to play / game guide screen explaining progression and refugee rescue"""
        # Dark background
        self.render_surface.fill((8, 8, 18))

        # Title
        title_font = pygame.font.Font(None, 52)
        title = title_font.render("HOW TO PLAY", True, (255, 180, 100))
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.render_surface.blit(title, rect)

        # Decorative line
        cx = SCREEN_WIDTH // 2
        pygame.draw.line(self.render_surface, (100, 60, 40),
                        (cx - 200, 80), (cx + 200, 80), 2)

        # Content sections - using columns for better layout
        left_x = 80
        right_x = SCREEN_WIDTH // 2 + 40
        section_font = pygame.font.Font(None, 36)
        header_font = pygame.font.Font(None, 32)
        text_font = pygame.font.Font(None, 26)
        small_font = pygame.font.Font(None, 22)

        y = 120

        # === LEFT COLUMN: CAMPAIGN PROGRESSION ===
        # Section header
        header = section_font.render("CAMPAIGN PROGRESSION", True, (255, 150, 80))
        self.render_surface.blit(header, (left_x, y))
        y += 40

        stages_info = [
            ("Stage 1: Asteroid Belt Escape", "5 waves", (180, 180, 180)),
            ("Stage 2: Amarr Patrol Interdiction", "7 waves + Boss", (180, 180, 180)),
            ("Stage 3: Slave Colony Liberation", "8 waves", (180, 180, 180)),
            ("Stage 4: Gate Assault", "10 waves + Boss", (180, 180, 180)),
            ("Stage 5: Final Push", "12 waves + Boss", (255, 200, 100)),
        ]

        for name, waves, color in stages_info:
            text = text_font.render(name, True, color)
            self.render_surface.blit(text, (left_x + 15, y))
            waves_text = small_font.render(waves, True, (120, 150, 120))
            self.render_surface.blit(waves_text, (left_x + 380, y + 2))
            y += 28

        y += 20

        # Wave system explanation
        header = header_font.render("WAVE SYSTEM", True, (150, 200, 150))
        self.render_surface.blit(header, (left_x, y))
        y += 30

        wave_info = [
            "Enemies spawn in waves - clear all to advance",
            "Enemy count increases each wave & stage",
            "Formations appear: V-shape, pincer, escort",
            "Boss appears on final wave of boss stages",
        ]

        for line in wave_info:
            text = small_font.render(line, True, (160, 160, 160))
            self.render_surface.blit(text, (left_x + 15, y))
            y += 22

        y += 20

        # Combat maneuvers
        header = header_font.render("COMBAT MANEUVERS", True, (150, 200, 150))
        self.render_surface.blit(header, (left_x, y))
        y += 28

        maneuver_info = [
            ("EMERGENCY ESCAPE (LB+RB / Q):", (255, 180, 100)),
            ("  Drop to bottom + 5s invincibility", (160, 160, 160)),
            ("  10s cooldown - escape, not mobility", (140, 140, 140)),
            ("", (0, 0, 0)),
            ("THRUST (LB or RB):", (255, 180, 100)),
            ("  Quick horizontal dodge burst", (160, 160, 160)),
            ("  Jaguar: UNLIMITED thrust - pure mobility", (255, 215, 0)),
        ]

        for line, color in maneuver_info:
            if line:
                text = small_font.render(line, True, color)
                self.render_surface.blit(text, (left_x + 10, y))
            y += 18

        y += 15

        # === REFUGEE RESCUE SECTION ===
        header = section_font.render("LIBERATING SOULS", True, (100, 255, 100))
        self.render_surface.blit(header, (left_x, y))
        y += 35

        rescue_info = [
            ("BESTOWER TRANSPORTS", (255, 180, 100)),
            ("Golden industrial ships carrying enslaved Minmatar", (160, 160, 160)),
            ("Destroy Bestowers to release refugee escape pods", (160, 160, 160)),
            ("", (0, 0, 0)),
            ("COLLECTING REFUGEES", (255, 180, 100)),
            ("Fly over escape pods to rescue survivors", (160, 160, 160)),
            ("Refugees become currency at Rebel Station", (160, 160, 160)),
            ("", (0, 0, 0)),
            ("SPAWN RATES BY STAGE:", (200, 200, 150)),
            ("  Stage 1: 10% chance per spawn", (140, 140, 140)),
            ("  Stage 2: 15% chance per spawn", (140, 140, 140)),
            ("  Stage 3: 25% chance (Liberation!)", (140, 200, 140)),
            ("  Stage 4: 15% chance per spawn", (140, 140, 140)),
            ("  Stage 5: 20% chance per spawn", (140, 140, 140)),
        ]

        for line, color in rescue_info:
            if line:
                text = small_font.render(line, True, color)
                self.render_surface.blit(text, (left_x + 15, y))
            y += 20

        # === RIGHT COLUMN: UPGRADES & COMBAT ===
        y = 120

        # Upgrades section
        header = section_font.render("REBEL STATION UPGRADES", True, (255, 150, 80))
        self.render_surface.blit(header, (right_x, y))
        y += 40

        upgrades = [
            ("Gyrostabilizer", "10", "+30% Fire Rate"),
            ("Armor Plate", "15", "+30 Max Armor"),
            ("Tracking Enhancer", "20", "+1 Gun Spread"),
            ("EMP Ammo", "25", "Strong vs Shields"),
            ("Phased Plasma", "35", "Strong vs Armor"),
            ("Fusion Ammo", "45", "High Damage"),
            ("Barrage Ammo", "55", "Fast Fire Rate"),
            ("Wolf Upgrade", "50", "T2 Ship Variant"),
            ("Jaguar Upgrade", "50", "T2 Ship Variant"),
        ]

        for name, cost, desc in upgrades:
            name_text = text_font.render(name, True, (180, 180, 180))
            self.render_surface.blit(name_text, (right_x + 15, y))
            cost_text = small_font.render(f"[{cost}]", True, (100, 255, 100))
            self.render_surface.blit(cost_text, (right_x + 200, y + 2))
            desc_text = small_font.render(desc, True, (140, 140, 140))
            self.render_surface.blit(desc_text, (right_x + 250, y + 2))
            y += 24

        y += 25

        # Powerups section with EVE icons
        header = header_font.render("POWERUP DROPS", True, (150, 200, 150))
        self.render_surface.blit(header, (right_x, y))
        y += 28

        # Powerup descriptions with icons
        powerups_display = [
            ("UTILITY:", None, (180, 180, 180)),
            ("Nanite Paste", "nanite_paste.png", "Cools weapons, clears heat"),
            ("", None, (0, 0, 0)),
            ("COMBAT BOOSTERS:", None, (180, 180, 180)),
            ("Weapon Upgrade", "combat_booster.png", "+Damage (lost on overheat)"),
            ("Rapid Fire", "combat_booster.png", "+Fire rate (lost on overheat)"),
            ("Overdrive", "speed_booster.png", "5s speed boost"),
            ("", None, (0, 0, 0)),
            ("DEFENSIVE:", None, (180, 180, 180)),
            ("Assault DC", "assault_damage_control.png", "5s invulnerability"),
            ("Shield Hardener", "shield_hardener.png", "Repairs shields"),
            ("Armor Hardener", "armor_hardener.png", "Repairs armor"),
            ("Bulkheads", "reinforced_bulkheads.png", "Repairs hull"),
        ]

        eve_icon_path = "assets/eve_icons/powerups/"
        for item in powerups_display:
            if len(item) == 3:
                name, icon_file, desc = item
                if name == "":
                    y += 8
                    continue
                if icon_file is None:
                    # Header line
                    text = small_font.render(name, True, desc)
                    self.render_surface.blit(text, (right_x + 10, y))
                    y += 20
                else:
                    # Try to load and display EVE icon
                    try:
                        icon_path = eve_icon_path + icon_file
                        icon = pygame.image.load(icon_path).convert_alpha()
                        icon = pygame.transform.scale(icon, (18, 18))
                        self.render_surface.blit(icon, (right_x + 12, y))
                    except Exception:
                        pygame.draw.circle(self.render_surface, (200, 150, 50),
                                         (right_x + 21, y + 9), 8)
                    # Name and description
                    name_surf = small_font.render(name, True, (200, 200, 200))
                    self.render_surface.blit(name_surf, (right_x + 36, y))
                    desc_surf = small_font.render(desc, True, (140, 140, 140))
                    self.render_surface.blit(desc_surf, (right_x + 140, y))
                    y += 20

        y += 15

        # Difficulty tips
        header = header_font.render("DIFFICULTY TIERS", True, (150, 200, 150))
        self.render_surface.blit(header, (right_x, y))
        y += 30

        diff_info = [
            ("Carebear: 0.5x enemy HP, forgiving", (100, 200, 100)),
            ("Newbro: Balanced, teaches mechanics", (180, 180, 180)),
            ("Bitter Vet: 1.4x HP, no mercy", (200, 150, 100)),
            ("Triglavian: 2.2x HP, hostile reality", (255, 100, 100)),
        ]

        for line, color in diff_info:
            text = small_font.render(line, True, color)
            self.render_surface.blit(text, (right_x + 15, y))
            y += 22

        # Footer
        footer_y = SCREEN_HEIGHT - 50
        if self.controller.connected:
            footer = self.font_small.render("Press B to return", True, (100, 100, 100))
        else:
            footer = self.font_small.render("Press ESC to return", True, (100, 100, 100))
        rect = footer.get_rect(center=(SCREEN_WIDTH // 2, footer_y))
        self.render_surface.blit(footer, rect)

        # Decorative border
        pygame.draw.rect(self.render_surface, (60, 40, 30),
                        (20, 20, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), 2, border_radius=8)

    def run(self):
        """Main game loop"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
