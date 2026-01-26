"""Main game logic for Minmatar Rebellion"""
import pygame
import random
from constants import *
from sprites import (Player, Enemy, RefugeePod, Powerup, Explosion, Star)
from sounds import get_sound_manager, get_music_manager
from controller_input import ControllerInput, XboxButton
from space_background import SpaceBackground
from visual_effects import ParticleSystem


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

        # Particle system for hit effects, muzzle flashes, etc.
        self.particle_system = ParticleSystem()

        # Game state
        self.state = 'menu'  # menu, chapter_select, difficulty, playing, shop, paused, gameover, victory
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']

        # Menu navigation for controller
        self.menu_selection = 0
        self.menu_cooldown = 0  # Prevent rapid scrolling

        # Chapter selection - EVE Rebellion Collection
        self.selected_chapter = 0  # Index into CHAPTERS
        self.current_stages = STAGES_MINMATAR  # Active campaign stages
        
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
        
        # Stage/Wave tracking
        self.current_stage = 0
        self.current_wave = 0
        self.wave_enemies = 0
        self.wave_spawned = 0
        self.spawn_timer = 0
        self.wave_delay = 0
        self.stage_complete = False
        
        # Messages
        self.message = ""
        self.message_timer = 0

        # Clear particle effects on reset
        self.particle_system.clear()
    
    def show_message(self, text, duration=120):
        """Show a temporary message"""
        self.message = text
        self.message_timer = duration
    
    def spawn_wave(self):
        """Spawn enemies for current wave"""
        stage = self.current_stages[self.current_stage]
        
        # Determine wave composition
        num_enemies = 3 + self.current_wave + self.current_stage
        
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
        
        stage = self.current_stages[self.current_stage]
        
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

            if event.type == pygame.KEYDOWN:
                # F5 to rescan for controllers (works in any state)
                if event.key == pygame.K_F5:
                    if self.controller:
                        self.controller.reconnect()
                        if self.controller.connected:
                            print(f"Controller reconnected: {self.controller.joystick.get_name()}")
                        else:
                            print("No controller found")

                if self.state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'chapter_select'
                        self.menu_selection = 0
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.music_manager.start_music()
                        else:
                            self.music_manager.stop_music()
                    elif event.key == pygame.K_s:
                        self.sound_enabled = not self.sound_enabled
                
                elif self.state == 'chapter_select':
                    if event.key == pygame.K_1:
                        self.select_chapter(0)
                    elif event.key == pygame.K_2:
                        self.select_chapter(1)
                    elif event.key == pygame.K_3:
                        self.select_chapter(2)
                    elif event.key == pygame.K_4:
                        self.select_chapter(3)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.select_chapter(self.menu_selection)
                    elif event.key == pygame.K_UP:
                        self.menu_selection = max(0, self.menu_selection - 1)
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_DOWN:
                        self.menu_selection = min(len(CHAPTERS) - 1, self.menu_selection + 1)
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
                        self.state = 'chapter_select'
                        self.menu_selection = self.selected_chapter  # Restore chapter selection
                        self.play_sound('menu_select')

                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_q or event.key == pygame.K_TAB:
                        self.player.cycle_ammo()
                        self.play_sound('ammo_switch')
                    else:
                        # Check ammo hotkeys
                        for ammo_type, data in AMMO_TYPES.items():
                            if event.key == data['key']:
                                if self.player.switch_ammo(ammo_type):
                                    self.show_message(f"Ammo: {data['name']}", 60)
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

        # Controller menu handling (runs once per frame, outside event loop)
        if self.controller and self.controller.connected:
            move_x, move_y = self.controller.get_movement_vector()

            if self.state == 'menu':
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.state = 'chapter_select'
                    self.menu_selection = 0
                    self.play_sound('menu_select')

            elif self.state == 'chapter_select':
                # Navigate with stick
                if self.menu_cooldown <= 0:
                    if move_y < -0.5:  # Up
                        self.menu_selection = max(0, self.menu_selection - 1)
                        self.menu_cooldown = 15
                        self.play_sound('menu_select')
                    elif move_y > 0.5:  # Down
                        self.menu_selection = min(len(CHAPTERS) - 1, self.menu_selection + 1)
                        self.menu_cooldown = 15
                        self.play_sound('menu_select')
                # Select with A
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.select_chapter(self.menu_selection)
                # Back with B
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'menu'
                    self.play_sound('menu_select')

            elif self.state == 'difficulty':
                # Navigate with stick
                if self.menu_cooldown <= 0:
                    if move_y < -0.5:  # Up
                        self.menu_selection = max(0, self.menu_selection - 1)
                        self.menu_cooldown = 15
                        self.play_sound('menu_select')
                    elif move_y > 0.5:  # Down
                        self.menu_selection = min(3, self.menu_selection + 1)
                        self.menu_cooldown = 15
                        self.play_sound('menu_select')
                # Select with A
                if self.controller.is_button_just_pressed(XboxButton.A):
                    difficulties = ['easy', 'normal', 'hard', 'nightmare']
                    self.set_difficulty(difficulties[self.menu_selection])
                # Back with B
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'chapter_select'
                    self.menu_selection = self.selected_chapter  # Restore chapter selection
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
                if self.controller.is_button_just_pressed(XboxButton.B):
                    self.state = 'playing'
                    self.play_sound('menu_select')

            elif self.state == 'shop':
                # Navigate shop with stick
                if self.menu_cooldown <= 0:
                    if move_y < -0.5:  # Up
                        self.menu_selection = max(0, self.menu_selection - 1)
                        self.menu_cooldown = 15
                    elif move_y > 0.5:  # Down
                        self.menu_selection = min(8, self.menu_selection + 1)
                        self.menu_cooldown = 15
                # Select with A
                if self.controller.is_button_just_pressed(XboxButton.A):
                    if self.menu_selection < 8:
                        keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                               pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]
                        self.handle_shop_input(keys[self.menu_selection])
                    else:
                        self.handle_shop_input(pygame.K_RETURN)

            elif self.state in ['gameover', 'victory']:
                if self.controller.is_button_just_pressed(XboxButton.A):
                    self.reset_game()
                    self.state = 'menu'
                    self.play_sound('menu_select')

    def select_chapter(self, chapter_index):
        """Select a chapter/campaign from the collection"""
        if 0 <= chapter_index < len(CHAPTERS):
            self.selected_chapter = chapter_index
            chapter = CHAPTERS[chapter_index]
            self.current_stages = chapter['stages']
            self.state = 'difficulty'
            self.menu_selection = 1  # Default to 'normal'
            self.play_sound('menu_select')

    def set_difficulty(self, difficulty):
        """Set game difficulty and start"""
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.reset_game()
        self.state = 'playing'
        self.show_message(self.current_stages[0]['name'], 180)
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
        
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Continue to next stage
            self.current_stage += 1
            if self.current_stage >= len(STAGES):
                self.state = 'victory'
                self.play_sound('stage_complete')
            else:
                self.current_wave = 0
                self.wave_delay = 60
                self.stage_complete = False
                self.state = 'playing'
                self.show_message(self.current_stages[self.current_stage]['name'], 180)
                self.play_sound('wave_start')
        
        if purchased:
            self.show_message(f"Purchased: {purchased}", 90)
            if purchased != "WOLF UPGRADE!":  # Wolf has its own sound
                self.play_sound('purchase')
    
    def update(self):
        """Update game state"""
        # Controller update - MUST happen before early return so menus work!
        dt = self.clock.get_time() / 1000.0
        if self.controller:
            # Disable haptics entirely on menus (stops Xbox controller vibration)
            self.controller.haptics_enabled = self.state in ('playing', 'paused')
            self.controller.update(dt)

        # Menu navigation cooldown
        if self.menu_cooldown > 0:
            self.menu_cooldown -= 1

        # Update scrolling background
        if hasattr(self, "space_background"):
            self.space_background.update(2.0)

        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()
        # Update player
        self.player.update(keys)
        

        # Add controller movement on top of keyboard (analog)
        if self.controller and self.controller.connected:
            move_x, move_y = self.controller.get_movement_vector()
            self.player.rect.x += move_x * self.player.speed
            self.player.rect.y += move_y * self.player.speed
            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        # Player shooting
        controller_fire = self.controller.is_firing() if (self.controller and self.controller.connected) else False
        # Get fire direction from controller (twin-stick) or default up
        if self.controller and self.controller.connected and self.controller.right_stick_fire:
            fire_dir = self.controller.get_fire_direction()
        else:
            fire_dir = (0, -1)  # Default: fire up
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] or controller_fire:
            bullets, muzzle_positions = self.player.shoot(fire_dir=fire_dir)
            if bullets:
                self.play_sound('autocannon', 0.3)
                # Muzzle flash particles
                for mx, my in muzzle_positions:
                    self.particle_system.emit_muzzle_flash(mx, my, angle=-1.5708, spread=30)
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

        # Update particle system
        self.particle_system.update()
        
        # Update screen shake
        self.shake.update()
        
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
                # Emit hit particles based on which layer was hit
                hit_x, hit_y = bullet.rect.centerx, bullet.rect.centery
                if enemy.shields > 0:
                    self.particle_system.emit_shield_impact(hit_x, hit_y, radius=15)
                elif enemy.armor > 0:
                    self.particle_system.emit_armor_sparks(hit_x, hit_y, count=8)
                else:
                    self.particle_system.emit_hull_damage(hit_x, hit_y, count=6)

                bullet.kill()
                if enemy.take_damage(bullet):
                    # Enemy destroyed
                    self.player.score += enemy.score
                    
                    # Screen shake based on enemy size
                    if enemy.is_boss:
                        self.shake.add(SHAKE_LARGE)
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

            # Emit hit particles based on which layer will take damage
            hit_x, hit_y = bullet.rect.centerx, bullet.rect.centery
            if self.player.shields > 0:
                self.particle_system.emit_shield_impact(hit_x, hit_y, radius=20)
                self.play_sound('shield_hit', 0.5)
            elif self.player.armor > 0:
                self.particle_system.emit_armor_sparks(hit_x, hit_y, count=12)
                self.play_sound('armor_hit', 0.5)
            else:
                self.particle_system.emit_hull_damage(hit_x, hit_y, count=10)
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
        elif powerup.powerup_type == 'weapon_upgrade':
            self.player.spread_bonus = min(3, self.player.spread_bonus + 1)
            self.show_message("Weapons Upgraded!", 60)
        elif powerup.powerup_type == 'rapid_fire':
            self.player.fire_rate_mult *= 1.2
            self.show_message("Rapid Fire!", 60)
    
    def update_waves(self):
        """Handle wave progression"""
        stage = self.current_stages[self.current_stage]
        
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
        elif self.state == 'chapter_select':
            self.draw_chapter_select()
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
        
        pygame.display.flip()
    
    def draw_difficulty(self):
        """Draw difficulty selection screen"""
        # Get current chapter info
        chapter = CHAPTERS[self.selected_chapter]
        chapter_color = chapter['color']

        # Chapter title
        chapter_title = self.font_large.render(chapter['title'].upper(), True, chapter_color)
        rect = chapter_title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(chapter_title, rect)

        # Difficulty title
        title = self.font.render("SELECT DIFFICULTY", True, (180, 180, 180))
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.render_surface.blit(title, rect)

        y = 220
        difficulties = [
            ('1', 'easy', 'Easy', 'Reduced enemy health and damage, more powerups'),
            ('2', 'normal', 'Normal', 'Standard experience'),
            ('3', 'hard', 'Hard', 'Tougher enemies, faster attacks, fewer powerups'),
            ('4', 'nightmare', 'Nightmare', 'For veteran pilots only')
        ]

        for i, (key, diff_id, name, desc) in enumerate(difficulties):
            # Highlight selected option (controller) or default colors
            is_selected = (i == self.menu_selection)
            if is_selected:
                color = (255, 255, 100)  # Bright yellow for selection
                prefix = "> "
            elif diff_id == 'nightmare':
                color = (255, 100, 100)
                prefix = ""
            elif diff_id == 'normal':
                color = chapter_color
                prefix = ""
            else:
                color = COLOR_TEXT
                prefix = ""

            text = self.font.render(f"{prefix}[{key}] {name}", True, color)
            self.render_surface.blit(text, (150, y))

            desc_color = (200, 200, 150) if is_selected else (150, 150, 150)
            desc_text = self.font_small.render(desc, True, desc_color)
            self.render_surface.blit(desc_text, (150, y + 25))

            y += 70

        # Back option
        y += 30
        back_text = "[B] Back" if self.controller and self.controller.connected else "[ESC] Back to Chapters"
        text = self.font.render(back_text, True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

        # Controller hint
        if self.controller and self.controller.connected:
            hint = self.font_small.render("Use stick to navigate, A to select", True, (100, 100, 100))
            rect = hint.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
            self.render_surface.blit(hint, rect)
    
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

        # Draw particle effects (above sprites, below HUD)
        self.particle_system.draw(self.render_surface)

        # Draw HUD
        self.draw_hud()
        
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
        if self.current_stage < len(self.current_stages):
            y += 30
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
    
    def draw_menu(self):
        """Draw main menu"""
        # Main Title - EVE Rebellion Collection
        title = self.font_large.render("EVE REBELLION COLLECTION", True, (200, 180, 100))
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 180))
        self.render_surface.blit(title, rect)

        # Subtitle
        sub = self.font.render("Stories of Conflict and Uprising", True, COLOR_TEXT)
        rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 230))
        self.render_surface.blit(sub, rect)

        # Tagline
        tagline = self.font_small.render("A Top-Down Space Shooter", True, (150, 150, 150))
        rect = tagline.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.render_surface.blit(tagline, rect)

        # Instructions - show controller or keyboard based on what's connected
        y = 340
        if self.controller and self.controller.connected:
            instructions = [
                "Left Stick - Move",
                "RT / A - Fire Autocannons",
                "LT / X - Fire Rockets",
                "RB - Switch Ammo",
                "",
                "Press A to Begin"
            ]
        else:
            instructions = [
                "WASD or Arrow Keys - Move",
                "Space or Left Click - Fire Autocannons",
                "Shift or Right Click - Fire Rockets",
                "1-5 or Q/Tab - Switch Ammo",
                "",
                "Press ENTER to Begin"
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
        _sound_color = (100, 255, 100) if self.sound_enabled else (255, 100, 100)  # Reserved
        _music_color = (100, 255, 100) if self.music_enabled else (255, 100, 100)  # Reserved

        text = self.font_small.render(f"[S] Sound: {sound_status}  [M] Music: {music_status}", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)

    def draw_chapter_select(self):
        """Draw chapter selection screen"""
        # Title
        title = self.font_large.render("SELECT YOUR STORY", True, (200, 180, 100))
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(title, rect)

        # Draw chapters
        y = 180
        for i, chapter in enumerate(CHAPTERS):
            is_selected = (i == self.menu_selection)

            # Selection highlight
            if is_selected:
                # Draw selection box
                box_rect = pygame.Rect(SCREEN_WIDTH // 2 - 350, y - 10, 700, 100)
                pygame.draw.rect(self.render_surface, (40, 40, 60), box_rect)
                pygame.draw.rect(self.render_surface, chapter['color'], box_rect, 2)

            # Chapter number and title
            number_color = chapter['color'] if is_selected else (100, 100, 100)
            title_color = chapter['color'] if is_selected else (150, 150, 150)

            number_text = self.font.render(f"[{i + 1}]", True, number_color)
            self.render_surface.blit(number_text, (SCREEN_WIDTH // 2 - 330, y))

            title_text = self.font_large.render(chapter['title'], True, title_color)
            self.render_surface.blit(title_text, (SCREEN_WIDTH // 2 - 280, y - 5))

            # Subtitle
            subtitle_color = (180, 180, 180) if is_selected else (100, 100, 100)
            subtitle_text = self.font.render(chapter['subtitle'], True, subtitle_color)
            self.render_surface.blit(subtitle_text, (SCREEN_WIDTH // 2 - 280, y + 30))

            # Description (only for selected)
            if is_selected:
                desc_text = self.font_small.render(chapter['description'], True, (200, 200, 200))
                self.render_surface.blit(desc_text, (SCREEN_WIDTH // 2 - 280, y + 55))

            y += 120

        # Instructions
        y = SCREEN_HEIGHT - 80
        if self.controller and self.controller.connected:
            inst = "Up/Down to navigate  |  A to select  |  B to go back"
        else:
            inst = "Up/Down or 1-4 to select  |  ENTER to confirm  |  ESC to go back"
        inst_text = self.font_small.render(inst, True, (150, 150, 150))
        rect = inst_text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(inst_text, rect)
    
    def draw_pause(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.render_surface.blit(overlay, (0, 0))
        
        text = self.font_large.render("PAUSED", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Press ESC to Resume", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.render_surface.blit(text, rect)
    
    def draw_shop(self):
        """Draw upgrade shop"""
        # Get chapter color for theming
        chapter = CHAPTERS[self.selected_chapter]
        chapter_color = chapter['color']

        # Title
        title = self.font_large.render("SUPPLY STATION", True, chapter_color)
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
            ("8", "WOLF UPGRADE", costs['wolf_upgrade'], player.is_wolf, "T2 Assault Ship!")
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
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 150))
        self.render_surface.blit(overlay, (0, 0))
        
        text = self.font_large.render("SHIP DESTROYED", True, (255, 100, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Press ENTER to return to menu", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.render_surface.blit(text, rect)
    
    def draw_victory(self):
        """Draw victory screen"""
        # Get chapter info for dynamic victory text
        chapter = CHAPTERS[self.selected_chapter]
        chapter_color = chapter['color']
        faction_info = FACTIONS.get(chapter['faction'], FACTIONS['minmatar'])

        title = self.font_large.render("VICTORY!", True, chapter_color)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.render_surface.blit(title, rect)

        # Chapter title
        text = self.font.render(chapter['title'], True, chapter_color)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.render_surface.blit(text, rect)

        # Faction victory text
        text = self.font.render(faction_info['victory_text'], True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.render_surface.blit(text, rect)
        
        y = 350
        text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.render_surface.blit(text, rect)
        
        ship_type = "Wolf Assault Frigate" if self.player.is_wolf else "Rifter Frigate"
        text = self.font.render(f"Ship: {ship_type}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 80))
        self.render_surface.blit(text, rect)
        
        diff_text = f"Difficulty: {self.difficulty_settings['name']}"
        text = self.font.render(diff_text, True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 110))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Press ENTER to play again", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 170))
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
