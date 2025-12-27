"""
Berserk System for Minmatar Rebellion

Core mechanics:
- Berserk multiplier increases the closer enemies are when destroyed
- Distance-based scoring with dramatic visual feedback
- Danger zones that boost score but increase risk
- Retro-inspired pixel-perfect presentation
- Minimal UI clutter, maximum gameplay focus

Integration with EVE theme:
- Distance measured in actual space units (matching EVE's tactical ranges)
- Works with existing enemy types and scoring
- Compatible with refugee rescue currency system
"""

import pygame
import math
from typing import Optional, Tuple

class BerserkSystem:
    """
    Arcade-style Berserk scoring system

    Distance Ranges (from player):
    - EXTREME CLOSE: 0-80 pixels → 5.0x multiplier (INSANE!)
    - CLOSE: 80-150 pixels → 3.0x multiplier (DANGEROUS!)
    - MEDIUM: 150-250 pixels → 1.5x multiplier (RISKY)
    - FAR: 250-400 pixels → 1.0x multiplier (SAFE)
    - VERY FAR: 400+ pixels → 0.5x multiplier (COWARD)
    """
    
    # Distance thresholds (in pixels)
    EXTREME_CLOSE = 80
    CLOSE = 150
    MEDIUM = 250
    FAR = 400
    
    # Multipliers for each range
    MULTIPLIERS = {
        'EXTREME': 5.0,
        'CLOSE': 3.0,
        'MEDIUM': 1.5,
        'FAR': 1.0,
        'VERY_FAR': 0.5
    }
    
    # Colors for range indicators
    RANGE_COLORS = {
        'EXTREME': (255, 50, 50),      # Bright red - DANGER
        'CLOSE': (255, 150, 50),       # Orange - WARNING
        'MEDIUM': (255, 255, 50),      # Yellow - RISKY
        'FAR': (100, 200, 100),        # Green - SAFE
        'VERY_FAR': (100, 100, 200)    # Blue - TOO FAR
    }
    
    def __init__(self):
        self.total_score = 0
        self.session_score = 0
        self.current_multiplier = 1.0
        self.current_range = 'FAR'

        # Combo system
        self.combo_count = 0
        self.combo_timer = 0
        self.combo_timeout = 120  # 2 seconds at 60fps to chain kills
        self.max_combo = 0
        self.combo_bonus_thresholds = {
            5: 1.2,    # 5 kills = 20% bonus
            10: 1.5,   # 10 kills = 50% bonus
            20: 2.0,   # 20 kills = 100% bonus
            50: 3.0    # 50 kills = 200% bonus
        }

        # Visual feedback
        self.score_popups = []  # [{pos, value, lifetime, multiplier, range_name}]
        self.combo_popup = None  # Special popup for combo milestones
        self.danger_pulse = 0
        self.extreme_close_time = 0  # Frames spent in extreme danger

        # Heat bonus tracking
        self.current_heat_state = 'COOL'

        # Statistics
        self.kills_by_range = {
            'EXTREME': 0,
            'CLOSE': 0,
            'MEDIUM': 0,
            'FAR': 0,
            'VERY_FAR': 0
        }
        self.total_kills = 0
        
    def calculate_multiplier(self, player_pos: Tuple[float, float], 
                           enemy_pos: Tuple[float, float]) -> Tuple[float, str]:
        """
        Calculate score multiplier based on distance at moment of kill
        
        Returns: (multiplier, range_name)
        """
        # Calculate distance
        dx = enemy_pos[0] - player_pos[0]
        dy = enemy_pos[1] - player_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Determine range and multiplier
        if distance < self.EXTREME_CLOSE:
            return (self.MULTIPLIERS['EXTREME'], 'EXTREME')
        elif distance < self.CLOSE:
            return (self.MULTIPLIERS['CLOSE'], 'CLOSE')
        elif distance < self.MEDIUM:
            return (self.MULTIPLIERS['MEDIUM'], 'MEDIUM')
        elif distance < self.FAR:
            return (self.MULTIPLIERS['FAR'], 'FAR')
        else:
            return (self.MULTIPLIERS['VERY_FAR'], 'VERY_FAR')
    
    def get_combo_bonus(self) -> float:
        """Get current combo bonus multiplier"""
        bonus = 1.0
        for threshold, mult in sorted(self.combo_bonus_thresholds.items()):
            if self.combo_count >= threshold:
                bonus = mult
        return bonus

    def get_heat_bonus(self, heat_percent: float) -> Tuple[float, str]:
        """
        Get heat-based score bonus multiplier.
        Higher heat = higher risk but higher reward.

        Heat thresholds:
        - 0-50%: 1.0x (COOL)
        - 50-75%: 1.25x (WARM)
        - 75-99%: 1.5x (HOT)
        - 100%: 2.0x (OVERHEATED - maximum risk/reward)

        Returns: (multiplier, heat_state_name)
        """
        if heat_percent >= 1.0:  # Overheated
            return (2.0, 'OVERHEATED')
        elif heat_percent >= 0.75:
            return (1.5, 'HOT')
        elif heat_percent >= 0.5:
            return (1.25, 'WARM')
        else:
            return (1.0, 'COOL')

    def register_kill(self, base_score: int, player_pos: Tuple[float, float],
                     enemy_pos: Tuple[float, float], enemy_type: str = "default",
                     heat_percent: float = 0.0) -> int:
        """
        Register an enemy kill and calculate berserked score

        Args:
            base_score: Base score value of the enemy
            player_pos: Player position at time of kill
            enemy_pos: Enemy position at time of kill
            enemy_type: Type of enemy (for potential future bonuses)
            heat_percent: Player's current heat level (0.0-1.0)

        Returns: Final score value with all multipliers applied
        """
        multiplier, range_name = self.calculate_multiplier(player_pos, enemy_pos)

        # Update combo
        self.combo_count += 1
        self.combo_timer = self.combo_timeout
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count

        # Get combo bonus
        combo_bonus = self.get_combo_bonus()

        # Get heat bonus
        heat_bonus, heat_state = self.get_heat_bonus(heat_percent)
        self.current_heat_state = heat_state

        # Apply multipliers (berserk * combo * heat)
        total_multiplier = multiplier * combo_bonus * heat_bonus
        final_score = int(base_score * total_multiplier)

        # Update stats
        self.total_score += final_score
        self.session_score += final_score
        self.kills_by_range[range_name] += 1
        self.total_kills += 1
        self.current_multiplier = multiplier
        self.current_range = range_name

        # Create score popup
        self.create_score_popup(enemy_pos, final_score, multiplier, range_name)

        # Check for combo milestone
        if self.combo_count in self.combo_bonus_thresholds:
            self.combo_popup = {
                'text': f"{self.combo_count}x COMBO!",
                'lifetime': 90,
                'bonus': self.combo_bonus_thresholds[self.combo_count]
            }

        # Visual feedback for extreme close kills
        if range_name == 'EXTREME':
            self.danger_pulse = 30  # Flash screen

        return final_score
    
    def create_score_popup(self, pos: Tuple[float, float], score: int, 
                          multiplier: float, range_name: str):
        """Create floating score indicator"""
        popup = {
            'pos': list(pos),
            'score': score,
            'multiplier': multiplier,
            'range': range_name,
            'lifetime': 90,  # 1.5 seconds at 60fps
            'velocity': [0, -2],  # Float upward
            'alpha': 255
        }
        self.score_popups.append(popup)
    
    def update(self, delta_time: float = 1.0):
        """Update berserk system state"""
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0:
                self.combo_count = 0  # Reset combo

        # Update combo popup
        if self.combo_popup:
            self.combo_popup['lifetime'] -= 1
            if self.combo_popup['lifetime'] <= 0:
                self.combo_popup = None

        # Update score popups
        for popup in self.score_popups[:]:
            popup['lifetime'] -= 1
            popup['pos'][0] += popup['velocity'][0]
            popup['pos'][1] += popup['velocity'][1]

            # Fade out in last 30 frames
            if popup['lifetime'] < 30:
                popup['alpha'] = int((popup['lifetime'] / 30) * 255)

            if popup['lifetime'] <= 0:
                self.score_popups.remove(popup)

        # Update danger pulse
        if self.danger_pulse > 0:
            self.danger_pulse -= 1
    
    def draw_popups(self, surface: pygame.Surface, font_small: pygame.font.Font,
                   font_large: pygame.font.Font):
        """Draw score popups on screen"""
        for popup in self.score_popups:
            x, y = popup['pos']
            score = popup['score']
            multiplier = popup['multiplier']
            range_name = popup['range']
            alpha = popup['alpha']
            
            # Choose font based on multiplier
            font = font_large if multiplier >= 3.0 else font_small
            
            # Score text
            score_text = f"+{score}"
            color = self.RANGE_COLORS[range_name]
            
            score_surf = font.render(score_text, True, color)
            score_surf.set_alpha(alpha)
            score_rect = score_surf.get_rect(center=(int(x), int(y)))
            surface.blit(score_surf, score_rect)
            
            # Multiplier indicator for high-risk kills
            if multiplier > 1.0:
                mult_text = f"x{multiplier:.1f}"
                mult_surf = font_small.render(mult_text, True, (255, 255, 255))
                mult_surf.set_alpha(alpha)
                mult_rect = mult_surf.get_rect(center=(int(x), int(y + 20)))
                surface.blit(mult_surf, mult_rect)
                
                # Range name for extreme kills
                if range_name == 'EXTREME':
                    danger_text = "BERSERK!"
                    danger_surf = font_small.render(danger_text, True, (255, 100, 100))
                    danger_surf.set_alpha(alpha)
                    danger_rect = danger_surf.get_rect(center=(int(x), int(y + 35)))
                    surface.blit(danger_surf, danger_rect)

        # Draw combo milestone popup (center screen)
        if self.combo_popup:
            popup = self.combo_popup
            alpha = min(255, popup['lifetime'] * 3)

            # Large combo text
            combo_surf = font_large.render(popup['text'], True, (255, 255, 100))
            combo_surf.set_alpha(alpha)
            screen_w = surface.get_width()
            combo_rect = combo_surf.get_rect(center=(screen_w // 2, 200))
            surface.blit(combo_surf, combo_rect)

            # Bonus text
            bonus_text = f"+{int((popup['bonus'] - 1) * 100)}% BONUS!"
            bonus_surf = font_small.render(bonus_text, True, (255, 200, 100))
            bonus_surf.set_alpha(alpha)
            bonus_rect = bonus_surf.get_rect(center=(screen_w // 2, 235))
            surface.blit(bonus_surf, bonus_rect)

    def draw_hud(self, surface: pygame.Surface, x: int, y: int,
                font_small: pygame.font.Font, font_large: pygame.font.Font):
        """
        Draw Berserk HUD element (minimal arcade style)
        Shows current multiplier and risk level
        """
        # Current multiplier indicator (only if > 1.0)
        if self.current_multiplier > 1.0:
            mult_text = f"x{self.current_multiplier:.1f}"
            color = self.RANGE_COLORS[self.current_range]
            
            # Pulsing effect for extreme danger
            if self.current_range == 'EXTREME' and self.danger_pulse > 0:
                pulse_scale = 1.0 + (self.danger_pulse / 30.0) * 0.3
                # Scale the font rendering
                temp_surf = font_large.render(mult_text, True, color)
                w, h = temp_surf.get_size()
                scaled_surf = pygame.transform.scale(
                    temp_surf,
                    (int(w * pulse_scale), int(h * pulse_scale))
                )
                rect = scaled_surf.get_rect(topright=(x, y))
                surface.blit(scaled_surf, rect)
            else:
                mult_surf = font_large.render(mult_text, True, color)
                rect = mult_surf.get_rect(topright=(x, y))
                surface.blit(mult_surf, rect)
            
            # Small "BERSERK" label
            label_surf = font_small.render("BERSERK", True, (200, 200, 200))
            label_rect = label_surf.get_rect(topright=(x, y + 30))
            surface.blit(label_surf, label_rect)

        # === PROMINENT COMBO DISPLAY ===
        # Show combo counter even at low counts for feedback
        if self.combo_count >= 2:
            combo_y = y + 55
            combo_bonus = self.get_combo_bonus()

            # Combo count with color and title based on level
            if self.combo_count >= 100:
                combo_color = (255, 50, 255)  # Purple
                combo_title = "GODLIKE!"
                font_scale = 1.5
            elif self.combo_count >= 50:
                combo_color = (255, 50, 200)  # Magenta
                combo_title = "UNSTOPPABLE!"
                font_scale = 1.4
            elif self.combo_count >= 30:
                combo_color = (255, 80, 80)  # Red
                combo_title = "RAMPAGE!"
                font_scale = 1.3
            elif self.combo_count >= 20:
                combo_color = (255, 120, 50)  # Orange-red
                combo_title = "DOMINATING!"
                font_scale = 1.2
            elif self.combo_count >= 10:
                combo_color = (255, 200, 50)  # Orange
                combo_title = "KILLING SPREE!"
                font_scale = 1.1
            elif self.combo_count >= 5:
                combo_color = (200, 255, 100)  # Yellow-green
                combo_title = "COMBO!"
                font_scale = 1.0
            else:
                combo_color = (100, 255, 100)  # Green
                combo_title = ""
                font_scale = 1.0

            # Draw combo title (milestone names)
            if combo_title:
                title_font = pygame.font.Font(None, int(28 * font_scale))
                title_surf = title_font.render(combo_title, True, combo_color)
                title_rect = title_surf.get_rect(topright=(x, combo_y - 5))

                # Glow effect for high combos
                if self.combo_count >= 10:
                    glow_surf = pygame.Surface((title_surf.get_width() + 10, title_surf.get_height() + 10), pygame.SRCALPHA)
                    glow_color = (*combo_color[:3], 60)
                    pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=5)
                    surface.blit(glow_surf, (title_rect.x - 5, title_rect.y - 5))

                surface.blit(title_surf, title_rect)
                combo_y += 22

            # Large combo count number
            count_font = pygame.font.Font(None, int(36 * font_scale))
            combo_text = f"{self.combo_count}x"

            # Pulsing effect for high combos
            if self.combo_count >= 10:
                pulse = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * 0.01)
                temp_surf = count_font.render(combo_text, True, combo_color)
                w, h = temp_surf.get_size()
                scaled = pygame.transform.scale(temp_surf, (int(w * pulse), int(h * pulse)))
                combo_rect = scaled.get_rect(topright=(x, combo_y))
                surface.blit(scaled, combo_rect)
            else:
                combo_surf = count_font.render(combo_text, True, combo_color)
                combo_rect = combo_surf.get_rect(topright=(x, combo_y))
                surface.blit(combo_surf, combo_rect)

            # Show bonus percentage
            if combo_bonus > 1.0:
                bonus_text = f"+{int((combo_bonus - 1) * 100)}% SCORE"
                bonus_surf = font_small.render(bonus_text, True, combo_color)
                bonus_rect = bonus_surf.get_rect(topright=(x, combo_y + 30))
                surface.blit(bonus_surf, bonus_rect)

            # Combo timer bar (shows time remaining to keep combo)
            timer_pct = self.combo_timer / self.combo_timeout
            bar_width = 80
            bar_height = 6
            bar_x = x - bar_width
            bar_y = combo_y + 50

            # Background
            pygame.draw.rect(surface, (30, 30, 40), (bar_x - 1, bar_y - 1, bar_width + 2, bar_height + 2), border_radius=3)
            pygame.draw.rect(surface, (50, 50, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=2)

            # Fill with urgency coloring
            if timer_pct < 0.3:
                fill_color = (255, 80, 80)  # Red when low
            elif timer_pct < 0.6:
                fill_color = (255, 200, 80)  # Orange when medium
            else:
                fill_color = combo_color

            fill_width = int(bar_width * timer_pct)
            if fill_width > 0:
                pygame.draw.rect(surface, fill_color, (bar_x, bar_y, fill_width, bar_height), border_radius=2)

    def draw_danger_zones(self, surface: pygame.Surface, player_pos: Tuple[int, int],
                         alpha: int = 60):
        """
        Draw danger zone rings around player (optional visual aid)
        Can be toggled on/off in settings
        """
        px, py = player_pos
        
        # Draw range circles (from outermost to innermost)
        ranges = [
            (self.FAR, self.RANGE_COLORS['FAR']),
            (self.MEDIUM, self.RANGE_COLORS['MEDIUM']),
            (self.CLOSE, self.RANGE_COLORS['CLOSE']),
            (self.EXTREME_CLOSE, self.RANGE_COLORS['EXTREME'])
        ]
        
        for radius, color in ranges:
            # Create surface for circle with transparency
            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (*color, alpha), (radius, radius), radius, 2)
            
            # Blit centered on player
            surface.blit(circle_surf, (px - radius, py - radius))
    
    def get_stats(self) -> dict:
        """Get statistics for end-of-stage display"""
        avg_multiplier = 0.0
        if self.total_kills > 0:
            weighted_sum = sum(
                count * self.MULTIPLIERS[range_name]
                for range_name, count in self.kills_by_range.items()
            )
            avg_multiplier = weighted_sum / self.total_kills
        
        return {
            'total_score': self.total_score,
            'session_score': self.session_score,
            'total_kills': self.total_kills,
            'kills_by_range': self.kills_by_range.copy(),
            'avg_multiplier': avg_multiplier,
            'extreme_kills': self.kills_by_range['EXTREME'],
            'safe_kills': self.kills_by_range['FAR'] + self.kills_by_range['VERY_FAR'],
            'max_combo': self.max_combo
        }
    
    def reset_session(self):
        """Reset session stats (new stage)"""
        self.session_score = 0
        self.kills_by_range = {k: 0 for k in self.kills_by_range}
        self.total_kills = 0
        self.score_popups.clear()
        self.danger_pulse = 0
        self.current_multiplier = 1.0
        self.current_range = 'FAR'


class DangerIndicator:
    """
    Visual indicator showing current danger level
    Minimal, pixel-art arcade style
    """
    
    def __init__(self, width: int = 200, height: int = 10):
        self.width = width
        self.height = height
        self.current_danger = 0.0  # 0.0 to 1.0
        
    def update_danger(self, player_pos: Tuple[float, float],
                     enemies: list, berserk_system: BerserkSystem):
        """
        Calculate current danger level based on nearby enemies
        """
        if not enemies:
            self.current_danger = max(0, self.current_danger - 0.05)
            return
        
        # Find closest enemy
        min_dist = float('inf')
        for enemy in enemies:
            dx = enemy.rect.centerx - player_pos[0]
            dy = enemy.rect.centery - player_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            min_dist = min(min_dist, dist)
        
        # Convert distance to danger (inverse relationship)
        if min_dist < berserk_system.EXTREME_CLOSE:
            danger = 1.0
        elif min_dist < berserk_system.CLOSE:
            danger = 0.7
        elif min_dist < berserk_system.MEDIUM:
            danger = 0.4
        elif min_dist < berserk_system.FAR:
            danger = 0.2
        else:
            danger = 0.0
        
        # Smooth transition
        self.current_danger += (danger - self.current_danger) * 0.1
    
    def draw(self, surface: pygame.Surface, x: int, y: int):
        """Draw danger indicator bar"""
        # Background
        bg_rect = pygame.Rect(x, y, self.width, self.height)
        pygame.draw.rect(surface, (50, 50, 50), bg_rect)
        pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)
        
        # Danger bar (color changes with danger level)
        if self.current_danger > 0:
            bar_width = int(self.width * self.current_danger)
            
            # Color gradient: green → yellow → red
            if self.current_danger < 0.33:
                color = (100, 200, 100)
            elif self.current_danger < 0.66:
                color = (255, 255, 50)
            else:
                color = (255, 50, 50)
            
            danger_rect = pygame.Rect(x, y, bar_width, self.height)
            pygame.draw.rect(surface, color, danger_rect)
        
        # Label
        # (Optional - can be drawn externally)


# Utility function for easy integration
def create_berserk_game_systems():
    """
    Convenience function to create all Berserk scoring systems
    Returns: (berserk_system, danger_indicator)
    """
    berserk = BerserkSystem()
    danger = DangerIndicator()
    return berserk, danger
