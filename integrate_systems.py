#!/usr/bin/env python3
"""
Automated Integration Script for Minmatar Rebellion
Integrates save/load, pause menu, and tutorial systems into game.py

Usage: python integrate_systems.py [--dry-run] [--backup]
"""

import os
import re
import shutil
import sys
from datetime import datetime


class GameIntegrator:
    def __init__(self, game_path='game.py'):
        self.game_path = game_path
        self.backup_path = None
        self.changes = []

    def backup_file(self):
        """Create backup of game.py"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_path = f'game.py.backup_{timestamp}'
        shutil.copy(self.game_path, self.backup_path)
        print(f"✓ Backup created: {self.backup_path}")

    def read_file(self):
        """Read game.py content"""
        with open(self.game_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, content):
        """Write modified content to game.py"""
        with open(self.game_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def add_imports(self, content):
        """Add system imports after existing imports"""
        # Find the last import statement
        import_pattern = r'((?:from|import)\s+\S+.*\n)'
        imports = list(re.finditer(import_pattern, content))

        if not imports:
            print("⚠ Warning: Could not find import section")
            return content

        last_import = imports[-1]
        insert_pos = last_import.end()

        new_imports = """
# Integrated systems
from core.save_manager import SaveManager
from core.pause_menu import PauseMenu
from core.tutorial import Tutorial
"""

        # Check if already added
        if 'from core.save_manager import SaveManager' in content:
            print("⚠ Imports already present, skipping")
            return content

        content = content[:insert_pos] + new_imports + content[insert_pos:]
        self.changes.append("Added system imports")
        print("✓ Added imports")
        return content

    def add_manager_init(self, content):
        """Add manager initialization in Game.__init__"""
        # Find Game.__init__ method
        init_pattern = r'(class Game.*?def __init__\(self.*?\):.*?)(\n        [^\n])'

        match = re.search(init_pattern, content, re.DOTALL)
        if not match:
            print("⚠ Warning: Could not find Game.__init__ method")
            return content

        # Check if already added
        if 'self.save_manager = SaveManager()' in content:
            print("⚠ Manager initialization already present, skipping")
            return content

        # Find a good insertion point (after pygame.init() or similar setup)
        init_section = match.group(0)

        manager_init = """
        # Initialize integrated systems
        self.save_manager = SaveManager()
        self.pause_menu = PauseMenu()
        self.tutorial = Tutorial()
"""

        # Insert before the first non-comment, non-blank line after __init__ signature
        lines = init_section.split('\n')
        insert_line = 2  # After def __init__ line

        lines.insert(insert_line, manager_init.rstrip())
        new_init = '\n'.join(lines)

        content = content.replace(init_section, new_init)
        self.changes.append("Added manager initialization")
        print("✓ Added manager initialization")
        return content

    def add_save_load_methods(self, content):
        """Add save_game() and load_game() methods to Game class"""

        # Check if already added
        if 'def save_game(self):' in content:
            print("⚠ Save/load methods already present, skipping")
            return content

        # Find end of Game class (look for a good insertion point)
        # We'll add it after reset_game or similar method

        save_load_methods = '''
    def save_game(self):
        """Save current game state"""
        player_state = self.save_manager.extract_player_state(self.player)
        game_state = {
            'current_stage': self.current_stage,
            'current_wave': self.current_wave,
            'difficulty': self.difficulty
        }
        return self.save_manager.save(player_state, game_state)

    def load_game(self):
        """Load saved game state"""
        player_state, game_state = self.save_manager.load()
        if player_state and game_state:
            # Apply loaded state
            self.save_manager.apply_player_state(self.player, player_state)
            self.current_stage = game_state.get('current_stage', 0)
            self.current_wave = game_state.get('current_wave', 0)
            self.difficulty = game_state.get('difficulty', 'normal')
            return True
        return False
'''

        # Find a method definition to insert after
        method_pattern = r'(    def \w+\(self.*?\n(?:        .*\n)*)'
        methods = list(re.finditer(method_pattern, content))

        if methods:
            # Insert after last method found
            last_method = methods[-1]
            insert_pos = last_method.end()
            content = content[:insert_pos] + '\n' + save_load_methods + content[insert_pos:]
            self.changes.append("Added save_game() and load_game() methods")
            print("✓ Added save/load methods")
        else:
            print("⚠ Warning: Could not find insertion point for save/load methods")

        return content

    def add_autosave_trigger(self, content):
        """Add auto-save when stage completes"""

        # Look for stage completion logic (self.stage_complete = True or similar)
        stage_complete_pattern = r'(self\.stage_complete\s*=\s*True)'

        if not re.search(stage_complete_pattern, content):
            print("⚠ Warning: Could not find stage completion trigger")
            return content

        # Check if already added
        if 'self.save_game()  # Auto-save on stage completion' in content:
            print("⚠ Auto-save already present, skipping")
            return content

        # Add save_game() call after stage_complete = True
        replacement = r'\1\n                self.save_game()  # Auto-save on stage completion'
        content = re.sub(stage_complete_pattern, replacement, content)

        self.changes.append("Added auto-save trigger")
        print("✓ Added auto-save trigger")
        return content

    def add_load_menu_option(self, content):
        """Add 'Press L to Load Game' menu option"""

        # Find menu instructions
        menu_pattern = r'("Press ENTER to Start")'

        if not re.search(menu_pattern, content):
            print("⚠ Warning: Could not find menu instructions")
            return content

        # Check if already added
        if '"Press L to Load Game"' in content:
            print("⚠ Load menu option already present, skipping")
            return content

        replacement = r'\1,\n            "Press L to Load Game"'
        content = re.sub(menu_pattern, replacement, content)

        self.changes.append("Added load game menu instruction")
        print("✓ Added load menu option")
        return content

    def add_load_event_handler(self, content):
        """Add L key handler in menu state"""

        # Find menu event handling
        menu_event_pattern = r"(elif self\.state == 'menu':.*?if event\.key == pygame\.K_RETURN.*?\n.*?\n)"

        if not re.search(menu_event_pattern, content, re.DOTALL):
            print("⚠ Warning: Could not find menu event handler")
            return content

        # Check if already added
        if 'pygame.K_l' in content and 'load_game()' in content:
            print("⚠ Load event handler already present, skipping")
            return content

        load_handler = """                elif event.key == pygame.K_l:
                    if self.load_game():
                        self.state = 'playing'
                        self.show_message("Game Loaded!", 120)
                        self.play_sound('menu_select')
                    else:
                        self.play_sound('error')
"""

        # Insert after the RETURN key handler
        replacement = r'\1' + load_handler
        content = re.sub(menu_event_pattern, replacement, content, flags=re.DOTALL)

        self.changes.append("Added load game key handler")
        print("✓ Added load event handler")
        return content

    def add_tutorial_start(self, content):
        """Add tutorial.start() when starting new game"""

        # Find where new game starts (likely in set_difficulty or reset_game)
        new_game_pattern = r"(self\.state = 'playing')"

        if not re.search(new_game_pattern, content):
            print("⚠ Warning: Could not find new game start point")
            return content

        # Check if already added
        if 'self.tutorial.start()' in content:
            print("⚠ Tutorial start already present, skipping")
            return content

        # Add tutorial start before state change
        replacement = r'self.tutorial.start()  # Start tutorial for new game\n        \1'
        content = re.sub(new_game_pattern, replacement, content, count=1)

        self.changes.append("Added tutorial start trigger")
        print("✓ Added tutorial start")
        return content

    def add_tutorial_update(self, content):
        """Add tutorial update in main game loop"""

        # Find update method
        update_pattern = r"(    def update\(self\):.*?if self\.state != 'playing':.*?return)"

        match = re.search(update_pattern, content, re.DOTALL)
        if not match:
            print("⚠ Warning: Could not find update() method")
            return content

        # Check if already added
        if 'self.tutorial.update' in content:
            print("⚠ Tutorial update already present, skipping")
            return content

        tutorial_update = """

        # Update tutorial
        if self.tutorial.is_active:
            self.tutorial.update(1/60)  # Assuming 60 FPS
"""

        insert_pos = match.end()
        content = content[:insert_pos] + tutorial_update + content[insert_pos:]

        self.changes.append("Added tutorial update call")
        print("✓ Added tutorial update")
        return content

    def add_tutorial_overlay(self, content):
        """Add tutorial overlay rendering in draw_game"""

        # Find draw_game method
        draw_pattern = r'(    def draw_game\(self\):.*?)(\n    def \w+\(self)'

        match = re.search(draw_pattern, content, re.DOTALL)
        if not match:
            print("⚠ Warning: Could not find draw_game() method")
            return content

        # Check if already added
        if 'tutorial_data = self.tutorial.get_display_data()' in content:
            print("⚠ Tutorial overlay already present, skipping")
            return content

        tutorial_overlay = '''

        # Draw tutorial overlay if active
        if self.tutorial.is_active:
            tutorial_data = self.tutorial.get_display_data()
            if tutorial_data['message']:
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, 200), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.render_surface.blit(overlay, (0, SCREEN_HEIGHT - 200))

                # Message
                msg = self.font.render(tutorial_data['message'], True, (255, 255, 255))
                msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
                self.render_surface.blit(msg, msg_rect)

                # Progress indicator
                progress = f"Step {tutorial_data['progress']['current']}/{tutorial_data['progress']['total']}"
                progress_text = self.font_small.render(progress, True, (200, 200, 200))
                self.render_surface.blit(progress_text, (SCREEN_WIDTH - 120, SCREEN_HEIGHT - 30))
'''

        # Insert before the next method definition
        draw_section = match.group(1)
        next_method = match.group(2)

        new_draw = draw_section + tutorial_overlay + next_method
        content = content.replace(match.group(0), new_draw)

        self.changes.append("Added tutorial overlay rendering")
        print("✓ Added tutorial overlay")
        return content

    def integrate_all(self, dry_run=False, backup=True):
        """Run all integration steps"""
        print("\n" + "="*60)
        print("Minmatar Rebellion - System Integration")
        print("="*60 + "\n")

        if not os.path.exists(self.game_path):
            print(f"❌ Error: {self.game_path} not found!")
            print("Please run this script from your game directory.")
            return False

        # Verify core modules exist
        required_modules = [
            'core/save_manager.py',
            'core/pause_menu.py',
            'core/tutorial.py'
        ]

        missing = [m for m in required_modules if not os.path.exists(m)]
        if missing:
            print("❌ Error: Missing required modules:")
            for m in missing:
                print(f"   - {m}")
            print("\nPlease ensure all core modules are in place.")
            return False

        print("✓ All core modules found\n")

        # Create backup
        if backup and not dry_run:
            self.backup_file()

        # Read original content
        content = self.read_file()
        _original_content = content  # Kept for potential rollback

        print("Applying integrations...\n")

        # Apply all modifications
        content = self.add_imports(content)
        content = self.add_manager_init(content)
        content = self.add_save_load_methods(content)
        content = self.add_autosave_trigger(content)
        content = self.add_load_menu_option(content)
        content = self.add_load_event_handler(content)
        content = self.add_tutorial_start(content)
        content = self.add_tutorial_update(content)
        content = self.add_tutorial_overlay(content)

        # Show summary
        print("\n" + "="*60)
        if dry_run:
            print("DRY RUN - No changes written")
            print(f"Would have made {len(self.changes)} modifications:")
        else:
            self.write_file(content)
            print(f"✓ Integration complete! Made {len(self.changes)} modifications:")

        for i, change in enumerate(self.changes, 1):
            print(f"  {i}. {change}")

        print("="*60)

        if not dry_run and self.changes:
            print("\n📋 Next Steps:")
            print("  1. Test the game: python game.py")
            print("  2. Try saving and loading")
            print("  3. Check the tutorial on first launch")
            print(f"\n💾 Backup saved to: {self.backup_path}")
            print("   (Restore with: mv {} {})\n".format(
                self.backup_path, self.game_path
            ))

        return True

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Integrate save/load, pause, and tutorial systems into game.py'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup file'
    )
    parser.add_argument(
        '--game-path',
        default='game.py',
        help='Path to game.py file (default: game.py)'
    )

    args = parser.parse_args()

    integrator = GameIntegrator(args.game_path)
    success = integrator.integrate_all(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
