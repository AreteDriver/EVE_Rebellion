"""
Minmatar Rebellion - Cinematic System
Handles story sequences, tribal identity, and narrative moments
"""

import pygame
import time
from typing import Dict, List, Tuple, Optional
from enum import Enum

class TribeType(Enum):
    SEBIESTOR = "sebiestor"
    BRUTOR = "brutor"
    VHEROKIOR = "vherokior"
    KRUSUAL = "krusual"

class CinematicType(Enum):
    OPENING = "opening"
    FIRST_SHIP = "first_ship"
    UPGRADE_WOLF = "upgrade_wolf"
    UPGRADE_JAGUAR = "upgrade_jaguar"
    MISSION_DEBRIEF = "mission_debrief"

class CinematicManager:
    """Manages all cinematic sequences and tribal narrative"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        self.active_cinematic = None
        self.cinematic_timer = 0
        self.skip_requested = False
        
        # Tribal data
        self.tribes = {
            TribeType.SEBIESTOR: {
                "name": "Sebiestor",
                "tagline": "Engineers & Innovators",
                "motto": "Through knowledge, we find freedom",
                "bonus": {"repair_rate": 1.05},
                "color": (100, 150, 255),  # Blue
                "voice_style": "analytical",
                "thanks_messages": [
                    "Your technical precision honors our clan, Ace.",
                    "The efficiency of your strike pleases the engineers, Ace.",
                    "Data shows exceptional performance. The tribe is grateful, Ace."
                ]
            },
            TribeType.BRUTOR: {
                "name": "Brutor",
                "tagline": "Warriors & Defenders",
                "motto": "Strength through unity and steel",
                "bonus": {"weapon_damage": 1.05},
                "color": (255, 100, 80),  # Red
                "voice_style": "fierce",
                "thanks_messages": [
                    "You fight with the strength of ancestors, Ace!",
                    "The enemy falls before your fury! Well done, Ace!",
                    "Blood and honor! Your courage inspires us all, Ace!"
                ]
            },
            TribeType.VHEROKIOR: {
                "name": "Vherokior",
                "tagline": "Mystics & Nomads",
                "motto": "The path reveals itself to the worthy",
                "bonus": {"speed": 1.05, "evasion": 1.05},
                "color": (180, 100, 255),  # Purple
                "voice_style": "mysterious",
                "thanks_messages": [
                    "The spirits guide your path, Ace. We are grateful.",
                    "Your dance between the stars is blessed, Ace.",
                    "The ancestors smile upon your journey, Ace."
                ]
            },
            TribeType.KRUSUAL: {
                "name": "Krusual",
                "tagline": "Tacticians & Survivors",
                "motto": "Adapt. Survive. Triumph.",
                "bonus": {"refugee_bonus": 1.10},
                "color": (100, 255, 150),  # Green
                "voice_style": "stoic",
                "thanks_messages": [
                    "Efficiency and honor. The Krusual way. Well done, Ace.",
                    "Tactical superiority confirmed. The tribe approves, Ace.",
                    "You rescued many. Pragmatic and effective, Ace."
                ]
            }
        }
        
    def start_opening_cinematic(self):
        """Begin the opening rebellion cinematic"""
        self.active_cinematic = CinematicType.OPENING
        self.cinematic_timer = 0
        self.skip_requested = False
        
    def render_opening_cinematic(self, screen: pygame.Surface, delta_time: float) -> bool:
        """
        Render the opening cinematic sequence
        Returns True when cinematic is complete
        """
        self.cinematic_timer += delta_time
        
        # Cinematic phases (timing in seconds)
        PHASE_TITAN = 2.0
        PHASE_EXPLOSION_START = 2.0
        PHASE_EXPLOSION_PEAK = 3.5
        PHASE_MESSAGE = 6.0
        PHASE_TOTAL = 10.0
        
        # Allow skip after 1 second
        if self.cinematic_timer > 1.0 and self.skip_requested:
            return True
            
        # Black background
        screen.fill((0, 0, 0))
        
        # Phase 1: Show titan
        if self.cinematic_timer < PHASE_TITAN:
            self._render_titan_scene(screen, self.cinematic_timer / PHASE_TITAN)
            
        # Phase 2: Begin explosions
        elif self.cinematic_timer < PHASE_EXPLOSION_START:
            progress = (self.cinematic_timer - PHASE_TITAN) / (PHASE_EXPLOSION_START - PHASE_TITAN)
            self._render_titan_scene(screen, 1.0)
            self._render_explosion_effects(screen, progress, intensity=0.3)
            
        # Phase 3: Main explosion
        elif self.cinematic_timer < PHASE_EXPLOSION_PEAK:
            progress = (self.cinematic_timer - PHASE_EXPLOSION_START) / (PHASE_EXPLOSION_PEAK - PHASE_EXPLOSION_START)
            self._render_explosion_effects(screen, progress, intensity=1.0)
            
        # Phase 4: Show message
        elif self.cinematic_timer < PHASE_MESSAGE:
            progress = (self.cinematic_timer - PHASE_EXPLOSION_PEAK) / (PHASE_MESSAGE - PHASE_EXPLOSION_PEAK)
            self._render_rebellion_message(screen, progress)
            
        # Phase 5: Fade out
        else:
            progress = (self.cinematic_timer - PHASE_MESSAGE) / (PHASE_TOTAL - PHASE_MESSAGE)
            self._render_rebellion_message(screen, 1.0 - progress)
            
        # Skip prompt
        if self.cinematic_timer > 1.0:
            self._render_skip_prompt(screen)
            
        return self.cinematic_timer >= PHASE_TOTAL
        
    def _render_titan_scene(self, screen: pygame.Surface, alpha: float):
        """Render the Amarr titan near planet"""
        # Fade in effect
        fade_alpha = int(alpha * 255)
        
        # Draw background stars (simple white dots)
        for i in range(100):
            x = (i * 137) % self.width  # Pseudo-random positioning
            y = (i * 219) % self.height
            brightness = int((i % 3 + 1) * fade_alpha / 3)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
            
        # Draw planet (lower right)
        planet_pos = (int(self.width * 0.75), int(self.height * 0.7))
        planet_radius = 150
        pygame.draw.circle(screen, (80, 60, 100), planet_pos, planet_radius)
        # Planet highlight
        pygame.draw.circle(screen, (120, 90, 140), 
                         (planet_pos[0] - 40, planet_pos[1] - 40), planet_radius // 3)
        
        # Draw titan silhouette (upper left)
        titan_rect = pygame.Rect(100, 100, 400, 150)
        
        # Main hull (simplified rectangular shape)
        pygame.draw.rect(screen, (100, 100, 120), titan_rect)
        pygame.draw.rect(screen, (150, 150, 170), titan_rect, 2)
        
        # Titan "wings" (Amarr aesthetic)
        points_left = [
            (titan_rect.left, titan_rect.centery),
            (titan_rect.left - 80, titan_rect.top + 20),
            (titan_rect.left - 60, titan_rect.centery)
        ]
        points_right = [
            (titan_rect.right, titan_rect.centery),
            (titan_rect.right + 80, titan_rect.top + 20),
            (titan_rect.right + 60, titan_rect.centery)
        ]
        pygame.draw.polygon(screen, (120, 120, 140), points_left)
        pygame.draw.polygon(screen, (120, 120, 140), points_right)
        
        # Titan lights (golden - Amarr colors)
        for i in range(6):
            light_x = titan_rect.left + 50 + i * 60
            light_y = titan_rect.centery
            pygame.draw.circle(screen, (255, 200, 100), (light_x, light_y), 3)
            
    def _render_explosion_effects(self, screen: pygame.Surface, progress: float, intensity: float):
        """Render explosion particle effects"""
        # White flash at explosion center
        titan_center = (250, 175)
        
        # Flash intensity
        flash_size = int(100 + progress * 400 * intensity)
        flash_alpha = int((1.0 - progress) * 200 * intensity)
        
        # Draw expanding explosion circles
        for i in range(5):
            radius = int(flash_size + i * 50)
            color_val = max(0, flash_alpha - i * 40)
            pygame.draw.circle(screen, (255, color_val, 0), titan_center, radius, 3)
            
        # Screen shake simulation (render offset)
        if intensity > 0.5:
            shake_amount = int((1.0 - progress) * 10)
            # This would be applied to camera in full implementation
            
        # Debris particles (simple version)
        import random
        random.seed(42)  # Consistent debris pattern
        for i in range(50):
            angle = (i / 50.0) * 6.28  # Full circle
            distance = progress * 300
            debris_x = int(titan_center[0] + distance * pygame.math.Vector2(1, 0).rotate_rad(angle).x)
            debris_y = int(titan_center[1] + distance * pygame.math.Vector2(1, 0).rotate_rad(angle).y)
            if 0 <= debris_x < self.width and 0 <= debris_y < self.height:
                debris_size = random.randint(2, 5)
                pygame.draw.circle(screen, (200, 100, 0), (debris_x, debris_y), debris_size)
                
    def _render_rebellion_message(self, screen: pygame.Surface, alpha: float):
        """Render the rebellion call-to-arms message"""
        if alpha <= 0:
            return
            
        # Message box
        box_width = 600
        box_height = 300
        box_x = (self.width - box_width) // 2
        box_y = (self.height - box_height) // 2
        
        # Background with border
        pygame.draw.rect(screen, (20, 20, 30), (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, (150, 100, 50), (box_x, box_y, box_width, box_height), 3)
        
        # Tribal pattern decoration (simple lines)
        for i in range(5):
            y = box_y + 10 + i * 60
            pygame.draw.line(screen, (100, 70, 40), (box_x + 20, y), (box_x + box_width - 20, y), 1)
            
        # Message text (would use actual font rendering)
        messages = [
            "ENCRYPTED TRANSMISSION - ALL TRIBES",
            "",
            "THE TIME HAS COME",
            "OUR CAPTORS ARE WEAK",
            "NOW IS THE TIME FOR REBELLION",
            "",
            "- Elder Council"
        ]
        
        # Simple text rendering (placeholder - would use proper fonts)
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        
        y_offset = box_y + 40
        for i, message in enumerate(messages):
            if i == 0 or i == len(messages) - 1:
                text = font_medium.render(message, True, (150, 120, 80))
            else:
                text = font_large.render(message, True, (255, 200, 150))
            text_rect = text.get_rect(center=(self.width // 2, y_offset))
            screen.blit(text, text_rect)
            y_offset += 35
            
    def _render_skip_prompt(self, screen: pygame.Surface):
        """Show skip instruction"""
        font = pygame.font.Font(None, 24)
        text = font.render("Press SPACE to skip", True, (150, 150, 150))
        text_rect = text.get_rect(bottomright=(self.width - 20, self.height - 20))
        screen.blit(text, text_rect)
        
    def render_tribal_selection(self, screen: pygame.Surface, selected_tribe: Optional[TribeType] = None) -> None:
        """Render tribal selection screen"""
        screen.fill((10, 10, 15))
        
        # Title
        font_title = pygame.font.Font(None, 48)
        title_text = font_title.render("MINMATAR ACE PILOT REGISTRY", True, (200, 150, 100))
        title_rect = title_text.get_rect(center=(self.width // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        font_subtitle = pygame.font.Font(None, 32)
        subtitle_text = font_subtitle.render("SELECT YOUR TRIBE", True, (180, 180, 180))
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 140))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Tribal options (vertical layout)
        start_y = 200
        spacing = 120
        font_name = pygame.font.Font(None, 36)
        font_detail = pygame.font.Font(None, 24)
        
        for i, (tribe_type, tribe_data) in enumerate(self.tribes.items()):
            y_pos = start_y + i * spacing
            
            # Selection box
            box_rect = pygame.Rect(150, y_pos, self.width - 300, 100)
            
            # Highlight selected
            if selected_tribe == tribe_type:
                pygame.draw.rect(screen, tribe_data["color"], box_rect)
                pygame.draw.rect(screen, (255, 255, 255), box_rect, 3)
            else:
                pygame.draw.rect(screen, (30, 30, 40), box_rect)
                pygame.draw.rect(screen, tribe_data["color"], box_rect, 2)
                
            # Tribe name
            name_text = font_name.render(
                f"{tribe_data['name'].upper()} - {tribe_data['tagline']}", 
                True, 
                (255, 255, 255) if selected_tribe == tribe_type else (200, 200, 200)
            )
            name_rect = name_text.get_rect(midleft=(box_rect.left + 20, box_rect.centery - 15))
            screen.blit(name_text, name_rect)
            
            # Tribe motto
            motto_text = font_detail.render(
                f'"{tribe_data["motto"]}"', 
                True, 
                (220, 220, 220) if selected_tribe == tribe_type else (150, 150, 150)
            )
            motto_rect = motto_text.get_rect(midleft=(box_rect.left + 20, box_rect.centery + 15))
            screen.blit(motto_text, motto_rect)
            
        # Instructions
        inst_text = font_detail.render("Use UP/DOWN arrows to select, ENTER to confirm", True, (150, 150, 150))
        inst_rect = inst_text.get_rect(center=(self.width // 2, self.height - 50))
        screen.blit(inst_text, inst_rect)
        
    def get_mission_debrief_message(self, tribe: TribeType, performance: str) -> str:
        """
        Get contextual debrief message based on tribe and performance
        
        Args:
            tribe: Player's tribe
            performance: "excellent", "good", "survival", or "difficult"
        """
        import random
        
        messages = self.tribes[tribe]["thanks_messages"]
        
        if performance == "excellent":
            return messages[0]
        elif performance == "good":
            return messages[1] if len(messages) > 1 else messages[0]
        elif performance == "survival":
            return "You survived. That matters most, Ace."
        else:  # difficult
            return "The ship can be rebuilt. You cannot. Fly safer, Ace."
    
    def get_ace_victory_shout(self, performance: str, ship_tier: int) -> str:
        """
        Get Ace's victory shout based on performance and ship
        
        Args:
            performance: Mission performance rating
            ship_tier: 0=Rifter, 1=Wolf, 2=Jaguar
        """
        # Rifter-specific victory shouts (the rust bucket)
        if ship_tier == 0:
            rifter_shouts = [
                "In Rust We Trust!",
                "Duct tape holds! In Rust We Trust!",
                "Still flying! In Rust We Trust!",
                "Rust bucket for the win!"
            ]
            
            if performance == "excellent":
                return "In Rust We Trust!"  # The classic
            elif performance == "good":
                return rifter_shouts[1]  # Duct tape variant
            else:
                return rifter_shouts[2]  # Still flying variant
                
        # Wolf victory shouts (earned upgrade)
        elif ship_tier == 1:
            wolf_shouts = [
                "The Wolf hunts well!",
                "Upgraded and deadly!",
                "This is more like it!",
                "No more rust - just steel!"
            ]
            return wolf_shouts[0] if performance == "excellent" else wolf_shouts[1]
            
        # Jaguar victory shouts (ultimate ship)
        else:
            jaguar_shouts = [
                "Lightning strike! Mission complete!",
                "Jaguar precision!",
                "This is what power feels like!",
                "From rust to legend!"
            ]
            return jaguar_shouts[0] if performance == "excellent" else jaguar_shouts[1]
            
    def render_upgrade_cinematic(self, screen: pygame.Surface, ship_tier: int, delta_time: float) -> bool:
        """
        Render ship upgrade cinematic
        Returns True when complete

        Future enhancement: Show ship in hangar with engineer dialogue
        and visual upgrade effects (armor plates, weapon mounts, etc.)
        """
        # Placeholder: Skip directly to gameplay for now
        # Full cinematic implementation deferred to future release
        return True
    
    def render_first_ship_cinematic(self, screen: pygame.Surface, delta_time: float, tribe: TribeType) -> bool:
        """
        Render the first ship acquisition scene - beat up Rifter
        Returns True when complete
        """
        self.cinematic_timer += delta_time
        
        PHASE_SHIP_REVEAL = 3.0
        PHASE_ACE_REACTION = 6.0
        PHASE_ELDER_RESPONSE = 9.0
        PHASE_TOTAL = 12.0
        
        if self.cinematic_timer > 1.0 and self.skip_requested:
            return True
            
        screen.fill((15, 15, 20))
        
        # Phase 1: Show beat-up Rifter in hangar
        if self.cinematic_timer < PHASE_SHIP_REVEAL:
            self._render_hangar_scene(screen, self.cinematic_timer / PHASE_SHIP_REVEAL)
            
        # Phase 2: Ace's reaction
        elif self.cinematic_timer < PHASE_ACE_REACTION:
            self._render_hangar_scene(screen, 1.0)
            progress = (self.cinematic_timer - PHASE_SHIP_REVEAL) / (PHASE_ACE_REACTION - PHASE_SHIP_REVEAL)
            self._render_ace_dialogue(screen, progress, 
                "A Rifter? THIS is what you're giving me?\nIt looks like a pile of rust duct-taped together!")
                
        # Phase 3: Elder's response
        elif self.cinematic_timer < PHASE_ELDER_RESPONSE:
            self._render_hangar_scene(screen, 1.0)
            progress = (self.cinematic_timer - PHASE_ACE_REACTION) / (PHASE_ELDER_RESPONSE - PHASE_ACE_REACTION)
            self._render_elder_dialogue(screen, progress, tribe,
                "It's what we have, Ace. Prove yourself worthy,\nand better ships will come. Now fly.")
                
        # Phase 4: Fade out
        else:
            progress = (self.cinematic_timer - PHASE_ELDER_RESPONSE) / (PHASE_TOTAL - PHASE_ELDER_RESPONSE)
            fade_alpha = int((1.0 - progress) * 255)
            # Simple fade to black
            
        if self.cinematic_timer > 1.0:
            self._render_skip_prompt(screen)
            
        return self.cinematic_timer >= PHASE_TOTAL
    
    def _render_hangar_scene(self, screen: pygame.Surface, alpha: float):
        """Render hangar bay with beat-up Rifter"""
        # Hangar background (dark, industrial)
        screen.fill((20, 20, 25))
        
        # Draw hangar floor
        floor_y = int(self.height * 0.7)
        pygame.draw.rect(screen, (40, 40, 45), (0, floor_y, self.width, self.height - floor_y))
        
        # Grid lines on floor
        for i in range(0, self.width, 100):
            pygame.draw.line(screen, (60, 60, 65), (i, floor_y), (i, self.height), 1)
        for i in range(floor_y, self.height, 50):
            pygame.draw.line(screen, (60, 60, 65), (0, i), (self.width, i), 1)
            
        # Rifter in center (simplified, beat-up looking)
        ship_center = (self.width // 2, int(self.height * 0.5))
        ship_width = 250
        ship_height = 120
        
        # Main hull (angular, Minmatar style - rusty brown/grey)
        hull_color = (100, 85, 70)  # Rusty brown
        hull_points = [
            (ship_center[0] - ship_width//2, ship_center[1]),  # Left point
            (ship_center[0] - ship_width//4, ship_center[1] - ship_height//2),  # Top left
            (ship_center[0] + ship_width//4, ship_center[1] - ship_height//2),  # Top right
            (ship_center[0] + ship_width//2, ship_center[1]),  # Right point
            (ship_center[0] + ship_width//4, ship_center[1] + ship_height//2),  # Bottom right
            (ship_center[0] - ship_width//4, ship_center[1] + ship_height//2),  # Bottom left
        ]
        pygame.draw.polygon(screen, hull_color, hull_points)
        
        # Damage marks (scorch marks, dents)
        for i in range(15):
            mark_x = ship_center[0] + random.randint(-ship_width//2, ship_width//2)
            mark_y = ship_center[1] + random.randint(-ship_height//2, ship_height//2)
            mark_size = random.randint(3, 10)
            pygame.draw.circle(screen, (60, 50, 40), (mark_x, mark_y), mark_size)
            
        # Duct tape strips (silver/grey patches)
        tape_positions = [
            (ship_center[0] - 60, ship_center[1] - 30, 80, 8),
            (ship_center[0] + 20, ship_center[1] + 10, 60, 8),
            (ship_center[0] - 90, ship_center[1] + 25, 70, 8),
        ]
        for x, y, w, h in tape_positions:
            pygame.draw.rect(screen, (160, 160, 160), (x, y, w, h))
            pygame.draw.rect(screen, (180, 180, 180), (x, y, w, h), 1)
            
        # Engine exhausts (dim, not very bright - barely working)
        left_engine = (ship_center[0] - ship_width//4, ship_center[1] + ship_height//2)
        right_engine = (ship_center[0] + ship_width//4, ship_center[1] + ship_height//2)
        
        # Faint glow (engines barely work)
        glow_color = (100, 120, 150)  # Dim blue
        pygame.draw.circle(screen, glow_color, left_engine, 8)
        pygame.draw.circle(screen, glow_color, right_engine, 8)
        
        # Hangar lights (overhead, casting shadows)
        for i in range(3):
            light_x = (self.width // 4) * (i + 1)
            light_y = 50
            pygame.draw.circle(screen, (255, 200, 150), (light_x, light_y), 15)
            # Light beam down
            beam_points = [
                (light_x - 100, light_y),
                (light_x + 100, light_y),
                (light_x + 150, floor_y),
                (light_x - 150, floor_y)
            ]
            beam_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.polygon(beam_surface, (255, 200, 150, 20), beam_points)
            screen.blit(beam_surface, (0, 0))
            
    def _render_ace_dialogue(self, screen: pygame.Surface, alpha: float, text: str):
        """Render Ace pilot dialogue box"""
        if alpha <= 0:
            return
            
        # Dialogue box (bottom of screen)
        box_height = 150
        box_y = self.height - box_height - 20
        box_rect = pygame.Rect(50, box_y, self.width - 100, box_height)
        
        # Background with portrait area
        pygame.draw.rect(screen, (25, 25, 30), box_rect)
        pygame.draw.rect(screen, (150, 120, 80), box_rect, 3)
        
        # Portrait placeholder (left side) - Ace pilot
        portrait_rect = pygame.Rect(box_rect.left + 10, box_rect.top + 10, 120, 130)
        pygame.draw.rect(screen, (40, 40, 50), portrait_rect)
        pygame.draw.rect(screen, (100, 100, 120), portrait_rect, 2)
        
        # ACE label above portrait
        font_small = pygame.font.Font(None, 24)
        ace_label = font_small.render("ACE PILOT", True, (200, 180, 150))
        screen.blit(ace_label, (portrait_rect.centerx - ace_label.get_width()//2, portrait_rect.top - 25))
        
        # Dialogue text (right side)
        font_dialogue = pygame.font.Font(None, 28)
        text_area_x = portrait_rect.right + 20
        text_area_width = box_rect.right - text_area_x - 20
        
        # Word wrap
        lines = text.split('\n')
        y_offset = box_rect.top + 30
        for line in lines:
            words = line.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                test_surface = font_dialogue.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() > text_area_width:
                    if current_line:
                        line_surf = font_dialogue.render(current_line, True, (255, 255, 255))
                        screen.blit(line_surf, (text_area_x, y_offset))
                        y_offset += 35
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                line_surf = font_dialogue.render(current_line, True, (255, 255, 255))
                screen.blit(line_surf, (text_area_x, y_offset))
                y_offset += 35
                
    def _render_elder_dialogue(self, screen: pygame.Surface, alpha: float, tribe: TribeType, text: str):
        """Render tribal elder dialogue box"""
        if alpha <= 0:
            return
            
        # Dialogue box (bottom of screen)
        box_height = 150
        box_y = self.height - box_height - 20
        box_rect = pygame.Rect(50, box_y, self.width - 100, box_height)
        
        # Get tribe color
        tribe_color = self.tribes[tribe]["color"]
        
        # Background with portrait area
        pygame.draw.rect(screen, (25, 25, 30), box_rect)
        pygame.draw.rect(screen, tribe_color, box_rect, 3)
        
        # Portrait placeholder (left side) - Elder
        portrait_rect = pygame.Rect(box_rect.left + 10, box_rect.top + 10, 120, 130)
        pygame.draw.rect(screen, (40, 40, 50), portrait_rect)
        pygame.draw.rect(screen, tribe_color, portrait_rect, 2)
        
        # Tribal elder label
        font_small = pygame.font.Font(None, 24)
        tribe_name = self.tribes[tribe]["name"].upper()
        elder_label = font_small.render(f"{tribe_name} ELDER", True, tribe_color)
        screen.blit(elder_label, (portrait_rect.centerx - elder_label.get_width()//2, portrait_rect.top - 25))
        
        # Dialogue text
        font_dialogue = pygame.font.Font(None, 28)
        text_area_x = portrait_rect.right + 20
        text_area_width = box_rect.right - text_area_x - 20
        
        lines = text.split('\n')
        y_offset = box_rect.top + 30
        for line in lines:
            words = line.split(' ')
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                test_surface = font_dialogue.render(test_line, True, (255, 255, 255))
                if test_surface.get_width() > text_area_width:
                    if current_line:
                        line_surf = font_dialogue.render(current_line, True, (255, 255, 255))
                        screen.blit(line_surf, (text_area_x, y_offset))
                        y_offset += 35
                    current_line = word + " "
                else:
                    current_line = test_line
            if current_line:
                line_surf = font_dialogue.render(current_line, True, (255, 255, 255))
                screen.blit(line_surf, (text_area_x, y_offset))
                y_offset += 35
        
    def handle_input(self, event: pygame.event.Event) -> bool:
        """
        Handle input during cinematics
        Returns True if cinematic should advance/skip
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.skip_requested = True
                return True
        return False


# Example usage demonstration
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    
    cinematic_mgr = CinematicManager(1280, 720)
    cinematic_mgr.start_opening_cinematic()
    
    running = True
    game_phase = "opening"  # opening -> tribal_selection -> first_ship -> ready
    selected_tribe = TribeType.SEBIESTOR
    
    while running:
        delta_time = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            cinematic_mgr.handle_input(event)
            
            if game_phase == "tribal_selection" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    tribes = list(TribeType)
                    idx = tribes.index(selected_tribe)
                    selected_tribe = tribes[(idx - 1) % len(tribes)]
                elif event.key == pygame.K_DOWN:
                    tribes = list(TribeType)
                    idx = tribes.index(selected_tribe)
                    selected_tribe = tribes[(idx + 1) % len(tribes)]
                elif event.key == pygame.K_RETURN:
                    print(f"Selected tribe: {selected_tribe.value}")
                    game_phase = "first_ship"
                    cinematic_mgr.cinematic_timer = 0
                    cinematic_mgr.skip_requested = False
        
        if game_phase == "opening":
            complete = cinematic_mgr.render_opening_cinematic(screen, delta_time)
            if complete:
                game_phase = "tribal_selection"
                
        elif game_phase == "tribal_selection":
            cinematic_mgr.render_tribal_selection(screen, selected_tribe)
            
        elif game_phase == "first_ship":
            complete = cinematic_mgr.render_first_ship_cinematic(screen, delta_time, selected_tribe)
            if complete:
                print("Ready to start first mission!")
                game_phase = "ready"
                
        elif game_phase == "ready":
            # Would transition to actual gameplay
            screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 72)
            text = font.render("READY FOR MISSION 1", True, (255, 200, 100))
            rect = text.get_rect(center=(640, 360))
            screen.blit(text, rect)
            
        pygame.display.flip()
        
    pygame.quit()
