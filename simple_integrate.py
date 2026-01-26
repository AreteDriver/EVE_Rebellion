#!/usr/bin/env python3
"""
Simple Berserk System Integration Guide
This script shows you exactly what to add to your game files
"""

print("=" * 70)
print("DEVIL BLADE BERSERK SYSTEM - SIMPLE INTEGRATION GUIDE")
print("=" * 70)

print("""
STEP 1: Add imports to game.py
================================
At the top of game.py, add:

    from berserk_system import BerserkSystem, DangerIndicator
    from devil_blade_effects import EffectManager


STEP 2: Initialize in Game.__init__()
======================================
In your Game class __init__ method, add:

    # Devil Blade Berserk System
    self.berserk_system = BerserkSystem()
    self.danger_indicator = DangerIndicator()
    self.effect_manager = EffectManager()


STEP 3: Modify enemy kill handling
===================================
Find where you handle enemy deaths. Replace the score calculation:

BEFORE:
    def handle_enemy_death(self, enemy):
        self.score += enemy.score_value

AFTER:
    def handle_enemy_death(self, enemy):
        # Calculate berserked score
        player_pos = (self.player.rect.centerx, self.player.rect.centery)
        enemy_pos = (enemy.rect.centerx, enemy.rect.centery)

        final_score = self.berserk_system.register_kill(
            enemy.score_value,
            player_pos,
            enemy_pos
        )
        self.score += final_score

        # Add explosion effect
        self.effect_manager.add_explosion(
            enemy_pos,
            (255, 150, 50),
            particle_count=20,
            spread=5.0
        )


STEP 4: Add to update loop
===========================
In your Game.update() method:

    self.berserk_system.update()
    self.effect_manager.update()


STEP 5: Add to render/draw
===========================
In your Game.draw() method:

    # Get shake offset
    shake_x, shake_y = self.effect_manager.get_shake_offset()

    # Draw background (with shake)
    self.screen.blit(self.background, (shake_x, shake_y))

    # Draw background effects
    self.effect_manager.draw_background_effects(self.screen)

    # ... draw gameplay ...

    # Draw foreground effects
    self.effect_manager.draw_foreground_effects(self.screen)

    # Draw HUD
    self.draw_hud()


STEP 6: Add Berserk HUD
========================
In your draw_hud() method:

    # Berserk multiplier (top-right)
    self.berserk_system.draw_hud(
        self.screen,
        self.screen.get_width() - 20,
        20,
        self.font_small,
        self.font_large
    )

    # Score popups
    self.berserk_system.draw_popups(
        self.screen,
        self.font_small,
        self.font_large
    )


OPTIONAL: Screen shake on close kills
======================================
In handle_enemy_death(), after register_kill():

    multiplier, range_name = self.berserk_system.calculate_multiplier(
        player_pos, enemy_pos
    )
    if range_name == 'EXTREME':
        self.effect_manager.add_shake(intensity=8, duration=12)
        self.effect_manager.add_flash((255, 100, 100), duration=8)
    elif range_name == 'CLOSE':
        self.effect_manager.add_shake(intensity=5, duration=8)


THAT'S IT!

Test: Run 'python3 test_berserk.py' to verify the system works
Guide: See DEVIL_BLADE_INTEGRATION.md for detailed examples
""")

print("=" * 70)
