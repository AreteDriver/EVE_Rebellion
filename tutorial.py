"""
Minmatar Rebellion - Tutorial System
Teaches new players the game mechanics step by step
"""

import pygame

from constants import COLOR_MINMATAR_ACCENT, COLOR_TEXT, SCREEN_WIDTH


class TutorialStep:
    """A single step in the tutorial"""
    def __init__(self, title, instruction, condition_text, check_func=None):
        self.title = title
        self.instruction = instruction
        self.condition_text = condition_text
        self.check_func = check_func
        self.completed = False
        self.progress = 0
        self.target = 1


class TutorialManager:
    """Manages the tutorial experience"""

    def __init__(self):
        self.active = False
        self.current_step = 0
        self.steps = []
        self.tutorial_complete = False
        self.skip_timer = 0

        # Tracking variables
        self.moves_made = 0
        self.shots_fired = 0
        self.rockets_fired = 0
        self.ammo_switches = 0
        self.close_kills = 0
        self.enemies_killed = 0

        self._create_steps()

    def _create_steps(self):
        """Create all tutorial steps"""
        self.steps = [
            TutorialStep(
                "WELCOME, PILOT",
                "You are the last hope of the Minmatar Rebellion.\nMaster your ship to liberate your people.",
                "Press SPACE or (A) to continue",
                lambda: self.skip_timer > 0
            ),
            TutorialStep(
                "MOVEMENT",
                "Use WASD/Arrows or Left Stick to move.\nStay mobile to avoid enemy fire!",
                "Move around the screen",
                lambda: self.moves_made >= 50
            ),
            TutorialStep(
                "AUTOCANNONS",
                "Press SPACE/Left Click or RT to fire autocannons.\nThey are your primary weapon.",
                "Fire your weapons (0/10)",
                lambda: self.shots_fired >= 10
            ),
            TutorialStep(
                "ROCKETS",
                "Press SHIFT/Right Click or LT to fire rockets.\nRockets deal heavy damage but are limited.",
                "Fire 2 rockets",
                lambda: self.rockets_fired >= 2
            ),
            TutorialStep(
                "AMMO TYPES",
                "Press 1-5 or RB to cycle ammo types:\n1=Sabot  2=EMP(shields)  3=Plasma(armor)\n4=Fusion(damage)  5=Barrage(speed)",
                "Switch ammo types 3 times",
                lambda: self.ammo_switches >= 3
            ),
            TutorialStep(
                "BERSERK SCORING",
                "Get CLOSE to enemies when you kill them!\nCloser kills = Higher score multiplier.\nExtreme close (5x) > Close (3x) > Far (0.5x)",
                "Kill an enemy at close range",
                lambda: self.close_kills >= 1
            ),
            TutorialStep(
                "REFUGEES",
                "Destroy industrial ships to rescue refugees.\nRefugees are your currency for upgrades.",
                "You're ready! Press SPACE or (A) to start",
                lambda: self.skip_timer > 0
            ),
        ]

        # Set targets for progress tracking
        self.steps[1].target = 50  # moves
        self.steps[2].target = 10  # shots
        self.steps[3].target = 2   # rockets
        self.steps[4].target = 3   # ammo switches

    def start_tutorial(self):
        """Begin the tutorial"""
        self.active = True
        self.current_step = 0
        self.tutorial_complete = False
        self.reset_tracking()

    def reset_tracking(self):
        """Reset all tracking variables"""
        self.moves_made = 0
        self.shots_fired = 0
        self.rockets_fired = 0
        self.ammo_switches = 0
        self.close_kills = 0
        self.enemies_killed = 0
        self.skip_timer = 0

    def track_move(self):
        """Track player movement"""
        self.moves_made += 1

    def track_shot(self):
        """Track autocannon fire"""
        self.shots_fired += 1

    def track_rocket(self):
        """Track rocket fire"""
        self.rockets_fired += 1

    def track_ammo_switch(self):
        """Track ammo type change"""
        self.ammo_switches += 1

    def track_kill(self, distance_range):
        """Track enemy kill with berserk range"""
        self.enemies_killed += 1
        if distance_range in ['EXTREME', 'CLOSE']:
            self.close_kills += 1

    def handle_input(self, event):
        """Handle tutorial-specific input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.skip_timer = 1

            # Allow skipping entire tutorial with ESC
            if event.key == pygame.K_ESCAPE:
                self.tutorial_complete = True
                self.active = False

    def update(self):
        """Update tutorial state"""
        if not self.active:
            return

        step = self.steps[self.current_step]

        # Update progress for current step
        if self.current_step == 1:
            step.progress = min(self.moves_made, step.target)
        elif self.current_step == 2:
            step.progress = min(self.shots_fired, step.target)
        elif self.current_step == 3:
            step.progress = min(self.rockets_fired, step.target)
        elif self.current_step == 4:
            step.progress = min(self.ammo_switches, step.target)

        # Check if current step is complete
        if step.check_func and step.check_func():
            step.completed = True
            self.skip_timer = 0

            # Move to next step
            self.current_step += 1
            if self.current_step >= len(self.steps):
                self.tutorial_complete = True
                self.active = False

    def draw(self, surface, font, font_small, font_large):
        """Draw tutorial overlay"""
        if not self.active:
            return

        step = self.steps[self.current_step]

        # Semi-transparent overlay at top
        overlay = pygame.Surface((SCREEN_WIDTH, 160), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        # Border
        pygame.draw.line(surface, COLOR_MINMATAR_ACCENT, (0, 158), (SCREEN_WIDTH, 158), 2)

        # Tutorial indicator
        step_text = font_small.render(f"TUTORIAL {self.current_step + 1}/{len(self.steps)}", True, (150, 150, 150))
        surface.blit(step_text, (10, 10))

        # Title
        title_text = font_large.render(step.title, True, COLOR_MINMATAR_ACCENT)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(title_text, title_rect)

        # Instructions (multi-line)
        y = 70
        for line in step.instruction.split('\n'):
            inst_text = font.render(line, True, COLOR_TEXT)
            inst_rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            surface.blit(inst_text, inst_rect)
            y += 25

        # Progress/condition
        if step.target > 1 and not step.completed:
            cond_text = step.condition_text.replace("0", str(step.progress))
            cond_text = cond_text.replace("/10", f"/{step.target}")
        else:
            cond_text = step.condition_text

        # Pulsing effect for condition
        pulse = abs((pygame.time.get_ticks() % 1000) - 500) / 500
        cond_color = (
            int(100 + 155 * pulse),
            int(200 + 55 * pulse),
            int(100 + 55 * pulse)
        )
        cond_surface = font.render(cond_text, True, cond_color)
        cond_rect = cond_surface.get_rect(center=(SCREEN_WIDTH // 2, 140))
        surface.blit(cond_surface, cond_rect)

        # Skip hint (with controller support)
        skip_hint = "Press ESC or (B) to skip tutorial"
        skip_text = font_small.render(skip_hint, True, (100, 100, 100))
        skip_rect = skip_text.get_rect(bottomright=(SCREEN_WIDTH - 10, 155))
        surface.blit(skip_text, skip_rect)
