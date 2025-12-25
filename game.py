"""Main game logic for Minmatar Rebellion"""
import pygame
import random
import math
from constants import *
from sprites import (Player, Enemy, Bullet, EnemyBullet, Rocket,
                     RefugeePod, Powerup, Explosion, Star)
from sounds import get_sound_manager, get_music_manager, play_sound
from controller_input import ControllerInput, XboxButton
from space_background import SpaceBackground
from expansion.capital_ship_enemy import CapitalShipEnemy
from berserk_system import BerserkSystem
from cinematic_system import CinematicManager, TribeType
from tutorial import TutorialManager


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
        self.space_background = SpaceBackground(SCREEN_WIDTH, SCREEN_HEIGHT)
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Minmatar Rebellion")
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

        # Berserk scoring system
        self.berserk = BerserkSystem()

        # Visual effects
        self.screen_flash_alpha = 0
        self.screen_flash_color = (255, 50, 50)
        self.show_danger_zones = False  # Toggle with D key

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

        # Game state
        self.state = 'menu'  # menu, ship_select, difficulty, playing, shop, paused, gameover, victory
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']

        # Ship selection
        self.selected_ship = 'rifter'  # rifter, wolf, jaguar
        self.ship_options = ['rifter', 'wolf', 'jaguar']
        self.ship_select_index = 0

        # Background stars
        self.stars = [Star() for _ in range(100)]

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
        self.pods = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()

        # Player
        self.player = Player()
        self.all_sprites.add(self.player)

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

        # Reset berserk system for new game
        self.berserk.reset_session()

        # Messages
        self.message = ""
        self.message_timer = 0

    def apply_ship_selection(self):
        """Apply bonuses based on selected ship"""
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
            self.player.is_wolf = True  # T2 ship flag
            self.player.speed *= 1.4  # 40% speed bonus
            self.player.max_shields += 30  # Better shields
            self.player.shields = self.player.max_shields
            self.player.ship_class = 'Jaguar'
            self.player.image = self.player._create_ship_image()
        # rifter is default, no changes needed
    
    def show_message(self, text, duration=120):
        """Show a temporary message"""
        self.message = text
        self.message_timer = duration
    
    def spawn_wave(self):
        """Spawn enemies for current wave with progressive scaling"""
        stage = STAGES[self.current_stage]

        # Progressive wave scaling formula
        # Base enemies + wave bonus + stage bonus + difficulty modifier
        base_enemies = 3
        wave_bonus = self.current_wave * 0.5  # +0.5 enemies per wave
        stage_bonus = self.current_stage * 1.5  # +1.5 enemies per stage

        # Difficulty modifiers
        diff_mult = {
            'easy': 0.7,
            'normal': 1.0,
            'hard': 1.3,
            'nightmare': 1.6
        }.get(self.difficulty, 1.0)

        num_enemies = int((base_enemies + wave_bonus + stage_bonus) * diff_mult)
        
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
            self.wave_enemies = 1
            self.wave_spawned = 1
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
    
    def spawn_enemy(self):
        """Spawn a single enemy"""
        if self.wave_spawned >= self.wave_enemies:
            return
        
        stage = STAGES[self.current_stage]
        
        # Chance for industrial
        if (self.wave_spawned == self.wave_enemies - 1 and 
            random.random() < stage['industrial_chance'] * 2):
            enemy_type = 'bestower'
        else:
            enemy_type = random.choice(stage['enemies'])
        
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -50
        
        enemy = Enemy(enemy_type, x, y, self.difficulty_settings)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        self.wave_spawned += 1
    
    def spawn_powerup(self, x, y):
        """Maybe spawn a powerup at location"""
        chance = self.difficulty_settings.get('powerup_chance', 0.15)
        if random.random() < chance:
            powerup_type = random.choice(list(POWERUP_TYPES.keys()))
            powerup = Powerup(x, y, powerup_type)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)
    
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
            

            # Controller button shortcuts
            if self.controller and self.controller.connected:
                # Tutorial controller support
                if self.tutorial.active:
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.tutorial.skip_timer = 1
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.tutorial.tutorial_complete = True
                        self.tutorial.active = False

                if self.state == 'menu':
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.state = 'ship_select'
                        self.play_sound('menu_select')
                elif self.state == 'ship_select':
                    # D-pad or left stick for navigation
                    move_x, move_y = self.controller.get_movement_vector()
                    if self.controller.is_button_just_pressed(XboxButton.DPAD_UP) or (move_y < -0.5 and not hasattr(self, '_controller_moved')):
                        self.ship_select_index = (self.ship_select_index - 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                        self._controller_moved = True
                    elif self.controller.is_button_just_pressed(XboxButton.DPAD_DOWN) or (move_y > 0.5 and not hasattr(self, '_controller_moved')):
                        self.ship_select_index = (self.ship_select_index + 1) % len(self.ship_options)
                        self.play_sound('menu_select')
                        self._controller_moved = True
                    elif abs(move_y) < 0.3:
                        self._controller_moved = False
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.selected_ship = self.ship_options[self.ship_select_index]
                        self.state = 'difficulty'
                        self.play_sound('menu_select')
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'menu'
                        self.play_sound('menu_select')
                elif self.state == 'difficulty':
                    if self.controller.is_button_just_pressed(XboxButton.A):
                        self.set_difficulty('normal')
                    elif self.controller.is_button_just_pressed(XboxButton.B):
                        self.state = 'ship_select'
                        self.play_sound('menu_select')
                elif self.state == 'playing':
                    if self.controller.is_button_just_pressed(XboxButton.START):
                        self.state = 'paused'
                        self.play_sound('menu_select')
                    if self.controller.is_button_just_pressed(XboxButton.RB):
                        self.player.cycle_ammo()
                        self.play_sound('ammo_switch')
                elif self.state == 'paused':
                    if self.controller.is_button_just_pressed(XboxButton.START):
                        self.state = 'playing'
                        self.play_sound('menu_select')
            elif event.type == pygame.KEYDOWN:
                # Pass events to tutorial if active
                if self.tutorial.active:
                    self.tutorial.handle_input(event)

                if self.state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'ship_select'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_t:
                        # Start tutorial
                        self.tutorial.start_tutorial()
                        self.state = 'ship_select'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.music_manager.start_music()
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
                        self.selected_ship = self.ship_options[self.ship_select_index]
                        self.state = 'difficulty'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_ESCAPE:
                        self.state = 'menu'
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
                        self.state = 'menu'
                        self.play_sound('menu_select')
                
                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                        self.play_sound('menu_select')
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
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        self.state = 'playing'
                        self.play_sound('menu_select')
                
                elif self.state == 'shop':
                    self.handle_shop_input(event.key)
                
                elif self.state in ['gameover', 'victory']:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.reset_game()
                        self.state = 'menu'
                        self.play_sound('menu_select')
    
    def set_difficulty(self, difficulty):
        """Set game difficulty and start"""
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.reset_game()
        self.state = 'playing'
        self.show_message(STAGES[0]['name'], 180)
        self.play_sound('wave_start')
        if self.music_enabled:
            self.music_manager.start_music()
    
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
            if self.current_stage >= len(STAGES):
                self.state = 'victory'
                self.play_sound('victory', 0.8)
            else:
                self.current_wave = 0
                self.wave_delay = 60
                self.stage_complete = False
                self.state = 'playing'
                self.show_message(STAGES[self.current_stage]['name'], 180)
                self.play_sound('wave_start')
        
        if purchased:
            self.show_message(f"Purchased: {purchased}", 90)
            if purchased != "WOLF UPGRADE!":  # Wolf has its own sound
                self.play_sound('purchase')
    
    def update(self):
        # Update scrolling background
        if hasattr(self, "space_background"):
            self.space_background.update(2.0)

        """Update game state"""
        if self.state != 'playing':
            return
        
        keys = pygame.key.get_pressed()
        

        # Controller update (dt in seconds)
        dt = self.clock.get_time() / 1000.0
        if self.controller:
            self.controller.update(dt)
        # Update player
        self.player.update(keys)

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
        # Player shooting
        controller_fire = self.controller.is_firing() if (self.controller and self.controller.connected) else False
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] or controller_fire:
            bullets = self.player.shoot()
            if bullets:
                self.play_sound('autocannon', 0.3)
                if self.tutorial.active:
                    self.tutorial.track_shot()
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)

        # Rockets
        controller_rocket = self.controller.is_alternate_fire() if (self.controller and self.controller.connected) else False
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2] or controller_rocket:
            rocket = self.player.shoot_rocket()
            if rocket:
                self.play_sound('rocket', 0.5)
                self.player_bullets.add(rocket)
                self.all_sprites.add(rocket)
                if self.tutorial.active:
                    self.tutorial.track_rocket()
        
        # Update stars
        for star in self.stars:
            star.update()
        
        # Update sprites
        self.player_bullets.update()
        self.enemy_bullets.update()
        
        # Update enemies with player position for AI
        for enemy in self.enemies:
            enemy.update(self.player.rect)
        
        self.pods.update()
        self.powerups.update()
        self.effects.update()
        
        # Update screen shake
        self.shake.update()

        # Update berserk system (for popups)
        self.berserk.update()

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
        
        # Check collisions - player bullets vs enemies
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                if enemy.take_damage(bullet):
                    # Enemy destroyed - use berserk scoring
                    berserk_score = self.berserk.register_kill(
                        enemy.score,
                        (self.player.rect.centerx, self.player.rect.centery),
                        (enemy.rect.centerx, enemy.rect.centery),
                        enemy.enemy_type
                    )
                    self.player.score += berserk_score

                    # Screen flash and sound for berserk kills
                    if self.berserk.current_range == 'EXTREME':
                        self.screen_flash_alpha = 100
                        self.screen_flash_color = (255, 50, 50)
                        self.play_sound('berserk_extreme', 0.6)
                    elif self.berserk.current_range == 'CLOSE':
                        self.screen_flash_alpha = 50
                        self.screen_flash_color = (255, 150, 50)
                        self.play_sound('berserk_close', 0.4)

                    # Track kill for tutorial
                    if self.tutorial.active:
                        self.tutorial.track_kill(self.berserk.current_range)
                    
                    # Screen shake and sounds based on enemy size
                    if enemy.is_boss:
                        self.shake.add(SHAKE_LARGE)
                        self.play_sound('boss_death', 0.8)
                        self.play_sound('explosion_large')
                    elif enemy.enemy_type in ['omen', 'maller']:
                        self.shake.add(SHAKE_MEDIUM)
                        self.play_sound('explosion_medium')
                    else:
                        self.shake.add(SHAKE_SMALL)
                        self.play_sound('explosion_small', 0.6)
                    
                    # Create explosion
                    exp_size = 30 if not enemy.is_boss else 80
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 
                                        exp_size, COLOR_AMARR_ACCENT)
                    self.effects.add(explosion)
                    self.all_sprites.add(explosion)
                    
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
                break
        
        # Enemy bullets vs player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in hits:
            damage = int(bullet.damage * self.difficulty_settings['enemy_damage_mult'])
            
            # Determine which layer took the hit for sound
            if self.player.shields > 0:
                self.play_sound('shield_hit', 0.5)
            elif self.player.armor > 0:
                self.play_sound('armor_hit', 0.5)
            else:
                self.play_sound('hull_hit', 0.6)
            
            self.shake.add(SHAKE_SMALL)
            
            if self.player.take_damage(damage):
                # Player dead
                explosion = Explosion(self.player.rect.centerx, self.player.rect.centery,
                                    50, COLOR_MINMATAR_ACCENT)
                self.effects.add(explosion)
                self.all_sprites.add(explosion)
                self.shake.add(SHAKE_LARGE)
                self.play_sound('explosion_large')
                self.play_sound('defeat', 0.7)
                self.state = 'gameover'
                self.music_manager.stop_music()
                return
        
        # Player collision with enemies
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in hits:
            self.shake.add(SHAKE_MEDIUM)
            self.play_sound('hull_hit', 0.8)
            if self.player.take_damage(30):
                self.play_sound('explosion_large')
                self.play_sound('defeat', 0.7)
                self.shake.add(SHAKE_LARGE)
                self.state = 'gameover'
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
            self.apply_powerup(powerup)
            self.play_sound('pickup_powerup', 0.6)
        
        # Wave/Stage logic
        self.update_waves()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def apply_powerup(self, powerup):
        """Apply powerup effect to player"""
        data = powerup.data
        now = pygame.time.get_ticks()
        
        if powerup.powerup_type == 'nanite':
            self.player.heal(data['heal'])
            self.show_message("Hull Repaired!", 60)
        elif powerup.powerup_type == 'capacitor':
            self.player.add_rockets(data['rockets'])
            self.show_message("Rockets Loaded!", 60)
        elif powerup.powerup_type == 'overdrive':
            self.player.overdrive_until = now + data['duration']
            self.show_message("OVERDRIVE!", 60)
        elif powerup.powerup_type == 'shield_boost':
            self.player.shield_boost_until = now + data['duration']
            self.player.shields = min(self.player.shields + 30, self.player.max_shields)
            self.show_message("Shields Boosted!", 60)
    
    def update_waves(self):
        """Handle wave progression"""
        stage = STAGES[self.current_stage]
        
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
        
        # Spawn enemies gradually
        self.spawn_timer += 1
        if self.spawn_timer >= 45 and self.wave_spawned < self.wave_enemies:
            self.spawn_timer = 0
            self.spawn_enemy()
        
        # Wave complete?
        if len(self.enemies) == 0 and self.wave_spawned >= self.wave_enemies and self.wave_enemies > 0:
            self.current_wave += 1
            self.wave_enemies = 0
            self.wave_spawned = 0
            self.wave_delay = 90
            
            # Stage complete?
            if self.current_wave >= stage['waves']:
                self.stage_complete = True
                self.wave_delay = 120
                self.show_message("STAGE COMPLETE!", 120)
                self.play_sound('stage_complete')
                # Go to shop after delay
                pygame.time.set_timer(pygame.USEREVENT + 1, 2000, 1)
        
        # Check for shop transition
        for event in pygame.event.get(pygame.USEREVENT + 1):
            if self.stage_complete:
                self.state = 'shop'
    
    def draw(self):
        """Render everything"""
        # Draw to render surface first (for screen shake)
        self.render_surface.fill((10, 10, 20))
        
        # Stars
        for star in self.stars:
            star.draw(self.render_surface)
        
        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'ship_select':
            self.draw_ship_select()
        elif self.state == 'difficulty':
            self.draw_difficulty()
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
        
        # Apply screen shake
        shake_x, shake_y = self.shake.offset_x, self.shake.offset_y
        self.screen.blit(self.render_surface, (shake_x, shake_y))

        # Apply screen flash overlay (for berserk kills)
        if self.screen_flash_alpha > 0:
            flash_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_overlay.fill((*self.screen_flash_color, int(self.screen_flash_alpha)))
            self.screen.blit(flash_overlay, (0, 0))

        pygame.display.flip()
    
    def draw_difficulty(self):
        """Draw difficulty selection screen"""
        # Title
        title = self.font_large.render("SELECT DIFFICULTY", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.render_surface.blit(title, rect)
        
        y = 250
        difficulties = [
            ('1', 'easy', 'Easy', 'Reduced enemy health and damage, more powerups'),
            ('2', 'normal', 'Normal', 'Standard experience'),
            ('3', 'hard', 'Hard', 'Tougher enemies, faster attacks, fewer powerups'),
            ('4', 'nightmare', 'Nightmare', 'For veteran pilots only')
        ]
        
        for key, diff_id, name, desc in difficulties:
            # Highlight current selection style
            color = COLOR_MINMATAR_ACCENT if diff_id == 'normal' else COLOR_TEXT
            if diff_id == 'nightmare':
                color = (255, 100, 100)
            
            text = self.font.render(f"[{key}] {name}", True, color)
            self.render_surface.blit(text, (150, y))
            
            desc_text = self.font_small.render(desc, True, (150, 150, 150))
            self.render_surface.blit(desc_text, (150, y + 25))
            
            y += 70
        
        # Back option
        y += 30
        text = self.font.render("[ESC] Back to Menu", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_game(self):
        # Draw space background
        if hasattr(self, "space_background"):
            self.space_background.draw(self.render_surface)

        """Draw gameplay elements"""
        # Draw sprites
        for sprite in self.all_sprites:
            if sprite != self.player:
                self.render_surface.blit(sprite.image, sprite.rect)

        # Draw player last (on top)
        self.render_surface.blit(self.player.image, self.player.rect)

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
            text = self.font_large.render(self.message, True, (255, 255, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.render_surface.blit(text, rect)
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Health bars
        bar_width = 150
        bar_height = 12
        x = 10
        y = 10
        
        # Shields
        pygame.draw.rect(self.render_surface, (50, 50, 80), (x, y, bar_width, bar_height))
        shield_pct = self.player.shields / self.player.max_shields
        pygame.draw.rect(self.render_surface, COLOR_SHIELD, (x, y, int(bar_width * shield_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 100, 150), (x, y, bar_width, bar_height), 1)
        
        # Armor
        y += bar_height + 3
        pygame.draw.rect(self.render_surface, (50, 40, 30), (x, y, bar_width, bar_height))
        armor_pct = self.player.armor / self.player.max_armor
        pygame.draw.rect(self.render_surface, COLOR_ARMOR, (x, y, int(bar_width * armor_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 80, 60), (x, y, bar_width, bar_height), 1)
        
        # Hull
        y += bar_height + 3
        pygame.draw.rect(self.render_surface, (40, 40, 40), (x, y, bar_width, bar_height))
        hull_pct = self.player.hull / self.player.max_hull
        pygame.draw.rect(self.render_surface, COLOR_HULL, (x, y, int(bar_width * hull_pct), bar_height))
        pygame.draw.rect(self.render_surface, (80, 80, 80), (x, y, bar_width, bar_height), 1)
        
        # Ammo indicator
        y += bar_height + 10
        ammo = AMMO_TYPES[self.player.current_ammo]
        pygame.draw.rect(self.render_surface, ammo['color'], (x, y, 20, 20))
        text = self.font_small.render(ammo['name'], True, COLOR_TEXT)
        self.render_surface.blit(text, (x + 25, y + 2))
        
        # Rockets
        y += 25
        text = self.font_small.render(f"Rockets: {self.player.rockets}", True, COLOR_TEXT)
        self.render_surface.blit(text, (x, y))

        # Ship indicator
        y += 25
        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        ship_color = (200, 150, 100) if self.player.is_wolf else COLOR_MINMATAR_ACCENT
        text = self.font_small.render(f"[{ship_class}]", True, ship_color)
        self.render_surface.blit(text, (x, y))
        
        # Right side - score and refugees
        x = SCREEN_WIDTH - 160
        y = 10
        
        text = self.font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.render_surface.blit(text, (x, y))
        
        y += 25
        text = self.font.render(f"Refugees: {self.player.refugees}", True, (100, 255, 100))
        self.render_surface.blit(text, (x, y))
        
        y += 25
        text = self.font_small.render(f"Liberated: {self.player.total_refugees}", True, (150, 200, 150))
        self.render_surface.blit(text, (x, y))
        
        # Stage/Wave
        if self.current_stage < len(STAGES):
            y += 30
            stage = STAGES[self.current_stage]
            text = self.font_small.render(f"Stage {self.current_stage + 1}", True, COLOR_TEXT)
            self.render_surface.blit(text, (x, y))
        
        # Difficulty indicator
        y += 20
        diff_color = (100, 255, 100) if self.difficulty == 'easy' else (
            COLOR_TEXT if self.difficulty == 'normal' else (
            (255, 200, 100) if self.difficulty == 'hard' else (255, 100, 100)
        ))
        text = self.font_small.render(f"[{self.difficulty_settings['name']}]", True, diff_color)
        self.render_surface.blit(text, (x, y))

        # Berserk multiplier HUD (top right area)
        self.berserk.draw_hud(self.render_surface, SCREEN_WIDTH - 10, 80,
                              self.font_small, self.font_large)

    def draw_boss_health_bar(self):
        """Draw boss health bar at top of screen when fighting a boss"""
        # Find boss in enemies
        boss = None
        for enemy in self.enemies:
            if enemy.is_boss:
                boss = enemy
                break

        if not boss:
            return

        # Boss health bar dimensions
        bar_width = SCREEN_WIDTH - 100
        bar_height = 20
        x = 50
        y = 30

        # Calculate total health percentage
        total_max = boss.max_shields + boss.max_armor + boss.max_hull
        total_current = max(0, boss.shields) + max(0, boss.armor) + max(0, boss.hull)
        health_pct = total_current / total_max if total_max > 0 else 0

        # Background
        pygame.draw.rect(self.render_surface, (30, 30, 40), (x - 2, y - 2, bar_width + 4, bar_height + 4))

        # Health bar segments (shields, armor, hull)
        segment_width = bar_width * health_pct

        # Determine color based on remaining health type
        if boss.shields > 0:
            bar_color = COLOR_SHIELD
        elif boss.armor > 0:
            bar_color = COLOR_ARMOR
        else:
            bar_color = COLOR_HULL

        # Draw health bar with gradient effect
        if segment_width > 0:
            pygame.draw.rect(self.render_surface, bar_color, (x, y, int(segment_width), bar_height))
            # Highlight on top
            highlight_color = tuple(min(255, c + 50) for c in bar_color)
            pygame.draw.rect(self.render_surface, highlight_color, (x, y, int(segment_width), 4))

        # Border
        pygame.draw.rect(self.render_surface, (100, 100, 120), (x, y, bar_width, bar_height), 2)

        # Boss name
        name_text = self.font.render(boss.stats['name'].upper(), True, COLOR_AMARR_ACCENT)
        name_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, y - 12))
        self.render_surface.blit(name_text, name_rect)

        # Health percentage
        pct_text = self.font_small.render(f"{int(health_pct * 100)}%", True, COLOR_TEXT)
        pct_rect = pct_text.get_rect(center=(SCREEN_WIDTH // 2, y + bar_height // 2))
        self.render_surface.blit(pct_text, pct_rect)

        # Phase indicator for multi-phase bosses
        if hasattr(boss, 'boss_phase') and boss.boss_phase > 0:
            phase_text = self.font_small.render(f"PHASE {boss.boss_phase + 1}", True, (255, 100, 100))
            phase_rect = phase_text.get_rect(right=x + bar_width, centery=y - 12)
            self.render_surface.blit(phase_text, phase_rect)

    def draw_menu(self):
        """Draw main menu"""
        # Title
        title = self.font_large.render("MINMATAR REBELLION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.render_surface.blit(title, rect)
        
        # Subtitle
        sub = self.font.render("A Top-Down Space Shooter", True, COLOR_TEXT)
        rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.render_surface.blit(sub, rect)
        
        # Instructions
        y = 340
        instructions = [
            "WASD or Arrow Keys - Move",
            "Space or Left Click - Fire Autocannons",
            "Shift or Right Click - Fire Rockets",
            "1-5 or Q/Tab - Switch Ammo",
            "",
            "Press ENTER to Start"
        ]
        for line in instructions:
            text = self.font.render(line, True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.render_surface.blit(text, rect)
            y += 32
        
        # Sound options
        y += 30
        sound_status = "ON" if self.sound_enabled else "OFF"
        music_status = "ON" if self.music_enabled else "OFF"
        sound_color = (100, 255, 100) if self.sound_enabled else (255, 100, 100)
        music_color = (100, 255, 100) if self.music_enabled else (255, 100, 100)

        text = self.font_small.render(f"[S] Sound: {sound_status}  [M] Music: {music_status}", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # Tutorial option
        y += 25
        tutorial_text = self.font_small.render("[T] Tutorial - Learn the basics", True, (150, 200, 150))
        tutorial_rect = tutorial_text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(tutorial_text, tutorial_rect)

    def draw_ship_select(self):
        """Draw ship selection screen"""
        # Title
        title = self.font_large.render("SELECT YOUR SHIP", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(title, rect)

        # Ship data
        ship_data = {
            'rifter': {
                'name': 'Rifter',
                'class': 'T1 Frigate',
                'desc': 'The iconic rust bucket. Reliable but basic.',
                'stats': 'Speed: Normal | Armor: Normal | Weapons: 2',
                'color': COLOR_MINMATAR_ACCENT
            },
            'wolf': {
                'name': 'Wolf',
                'class': 'T2 Assault Frigate',
                'desc': 'Upgraded hull with enhanced armor and speed.',
                'stats': 'Speed: +20% | Armor: +50 | Weapons: 3',
                'color': (200, 150, 100)
            },
            'jaguar': {
                'name': 'Jaguar',
                'class': 'T2 Assault Frigate',
                'desc': 'Lightning-fast interceptor variant.',
                'stats': 'Speed: +40% | Armor: Normal | Weapons: 2 | Evasion: +15%',
                'color': (100, 200, 255)
            }
        }

        # Draw ship options
        y = 200
        for i, ship_key in enumerate(self.ship_options):
            ship = ship_data[ship_key]
            is_selected = i == self.ship_select_index

            # Selection box
            box_rect = pygame.Rect(80, y, SCREEN_WIDTH - 160, 120)
            if is_selected:
                pygame.draw.rect(self.render_surface, ship['color'], box_rect, 0)
                pygame.draw.rect(self.render_surface, (255, 255, 255), box_rect, 3)
                text_color = (255, 255, 255)
            else:
                pygame.draw.rect(self.render_surface, (30, 30, 40), box_rect)
                pygame.draw.rect(self.render_surface, ship['color'], box_rect, 2)
                text_color = (180, 180, 180)

            # Ship name and class
            name_text = self.font_large.render(f"{ship['name']} - {ship['class']}", True, text_color)
            self.render_surface.blit(name_text, (box_rect.left + 20, box_rect.top + 15))

            # Description
            desc_text = self.font_small.render(ship['desc'], True, text_color)
            self.render_surface.blit(desc_text, (box_rect.left + 20, box_rect.top + 55))

            # Stats
            stats_text = self.font_small.render(ship['stats'], True, (150, 200, 150) if is_selected else (120, 150, 120))
            self.render_surface.blit(stats_text, (box_rect.left + 20, box_rect.top + 85))

            y += 140

        # Instructions
        y += 30
        inst_text = self.font.render("UP/DOWN to select, ENTER to confirm, ESC to go back", True, (150, 150, 150))
        rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(inst_text, rect)

    def draw_pause(self):
        """Draw pause overlay with controls"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.render_surface.blit(overlay, (0, 0))

        # Title
        text = self.font_large.render("PAUSED", True, COLOR_MINMATAR_ACCENT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(text, rect)

        # Controls box
        box_rect = pygame.Rect(80, 150, SCREEN_WIDTH - 160, 280)
        pygame.draw.rect(self.render_surface, (30, 30, 40), box_rect)
        pygame.draw.rect(self.render_surface, (100, 100, 120), box_rect, 2)

        text = self.font.render("CONTROLS", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 170))
        self.render_surface.blit(text, rect)

        controls = [
            ("WASD / Arrows", "Move ship"),
            ("Space / Left Click", "Fire autocannons"),
            ("Shift / Right Click", "Fire rockets"),
            ("1-5 / Q / Tab", "Switch ammo type"),
            ("D", "Toggle danger zones"),
            ("ESC", "Pause/Resume"),
        ]

        y = 200
        for key, action in controls:
            key_text = self.font_small.render(key, True, COLOR_MINMATAR_ACCENT)
            self.render_surface.blit(key_text, (100, y))
            action_text = self.font_small.render(action, True, COLOR_TEXT)
            self.render_surface.blit(action_text, (280, y))
            y += 25

        # Current status
        y += 20
        ship_class = getattr(self.player, 'ship_class', 'Rifter')
        status_text = f"Ship: {ship_class} | Score: {self.player.score} | Stage: {self.current_stage + 1}"
        text = self.font_small.render(status_text, True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # Berserk tip
        y += 40
        text = self.font_small.render("TIP: Get closer to enemies for higher score multipliers!", True, (255, 200, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # Resume prompt
        text = self.font.render("Press ESC to Resume", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
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
        text = self.font_large.render(f"Final Score: {self.player.score}", True, (255, 200, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.render_surface.blit(text, rect)

        # Stage reached
        stage_name = STAGES[self.current_stage]['name'] if self.current_stage < len(STAGES) else "Final Stage"
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
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 50))
        self.render_surface.blit(text, rect)
    
    def draw_victory(self):
        """Draw victory screen with berserk stats"""
        title = self.font_large.render("VICTORY!", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.render_surface.blit(title, rect)

        text = self.font.render("The Amarr station has fallen.", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 130))
        self.render_surface.blit(text, rect)

        text = self.font.render("The Minmatar Rebellion grows stronger!", True, COLOR_MINMATAR_ACCENT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.render_surface.blit(text, rect)

        # Main stats
        y = 220
        text = self.font_large.render(f"Final Score: {self.player.score}", True, (255, 215, 0))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
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
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 50))
        self.render_surface.blit(text, rect)
    
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
