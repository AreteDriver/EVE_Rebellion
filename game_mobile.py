"""Mobile game logic for Minmatar Rebellion - Touch Controls Edition"""
import pygame
import random
import math
import asyncio
from constants import *
from mobile_constants import *
from sprites import (Player, Enemy, Bullet, EnemyBullet, Rocket, 
                     RefugeePod, Powerup, Explosion, Star)
from sounds import get_sound_manager, get_music_manager, play_sound
from touch_controls import TouchControls


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


class MobileGame:
    """Mobile game class with touch controls"""
    
    def __init__(self):
        pygame.init()
        
        # Try to initialize mixer, but continue if it fails (web might not have audio)
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_available = True
        except pygame.error:
            self.audio_available = False
            print("Audio not available - continuing without sound")
        
        # Use flexible screen size that works on mobile
        self.screen_width = MOBILE_SCREEN_WIDTH
        self.screen_height = MOBILE_SCREEN_HEIGHT
        
        # Override constants for mobile
        global SCREEN_WIDTH, SCREEN_HEIGHT
        SCREEN_WIDTH = self.screen_width
        SCREEN_HEIGHT = self.screen_height
        
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.render_surface = pygame.Surface((self.screen_width, self.screen_height))
        pygame.display.set_caption("Minmatar Rebellion - Mobile")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 18)
        
        # Initialize touch controls
        self.touch_controls = TouchControls(self.screen_width, self.screen_height)
        self.touch_controls.set_font(self.font_small)
        
        # Initialize sound (if available)
        if self.audio_available:
            self.sound_manager = get_sound_manager()
            self.music_manager = get_music_manager()
        else:
            self.sound_manager = None
            self.music_manager = None
        self.sound_enabled = self.audio_available
        self.music_enabled = False  # Disable by default on mobile for performance
        
        # Screen shake
        self.shake = ScreenShake()
        
        # Game state
        self.state = 'menu'  # menu, difficulty, playing, shop, paused, gameover, victory
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']
        
        # Track pause toggle to prevent rapid toggling
        self.pause_cooldown = 0
        
        # Background stars
        self.stars = [Star() for _ in range(100)]
        
        self.reset_game()
    
    def play_sound(self, sound_name, volume=1.0):
        """Play sound if enabled"""
        if self.sound_enabled and self.sound_manager:
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
        # Apply mobile speed bonus
        self.player.speed *= MOBILE_PLAYER_SPEED_MULT
        self.player.fire_rate_mult *= MOBILE_FIRE_RATE_MULT
        self.all_sprites.add(self.player)
        
        # Update touch controls with player's unlocked ammo
        self.touch_controls.update_unlocked_ammo(self.player.unlocked_ammo)
        
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
    
    def show_message(self, text, duration=120):
        """Show a temporary message"""
        self.message = text
        self.message_timer = duration
    
    def spawn_wave(self):
        """Spawn enemies for current wave"""
        stage = STAGES[self.current_stage]
        
        # Determine wave composition
        num_enemies = 3 + self.current_wave + self.current_stage
        
        # Check for boss wave
        if (stage['boss'] and self.current_wave == stage['waves'] - 1):
            # Boss wave
            boss = Enemy(stage['boss'], self.screen_width // 2, -100, self.difficulty_settings)
            self.enemies.add(boss)
            self.all_sprites.add(boss)
            self.wave_enemies = 1
            self.wave_spawned = 1
            self.show_message(f"WARNING: {boss.stats['name'].upper()}", 180)
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
        
        x = random.randint(50, self.screen_width - 50)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle touch controls events
            self.touch_controls.handle_event(event)
            
            if event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'difficulty'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_s:
                        self.sound_enabled = not self.sound_enabled
                    elif event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled and self.music_manager:
                            self.music_manager.start_music()
                        elif self.music_manager:
                            self.music_manager.stop_music()
                
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
            
            # Handle touch-based menu navigation
            if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                self._handle_touch_menu(event)
    
    def _handle_touch_menu(self, event):
        """Handle touch-based menu interactions"""
        if event.type == pygame.FINGERDOWN:
            x = event.x * self.screen_width
            y = event.y * self.screen_height
        else:
            x, y = event.pos
        
        if self.state == 'menu':
            # Tap anywhere to start
            if y > self.screen_height * 0.5:
                self.state = 'difficulty'
                self.play_sound('menu_select')
        
        elif self.state == 'difficulty':
            # Touch difficulty selection
            if 0.25 < y / self.screen_height < 0.35:
                self.set_difficulty('easy')
            elif 0.35 < y / self.screen_height < 0.45:
                self.set_difficulty('normal')
            elif 0.45 < y / self.screen_height < 0.55:
                self.set_difficulty('hard')
            elif 0.55 < y / self.screen_height < 0.65:
                self.set_difficulty('nightmare')
            elif y > self.screen_height * 0.8:
                self.state = 'menu'
                self.play_sound('menu_select')
        
        elif self.state == 'paused':
            # Tap to resume
            self.state = 'playing'
            self.play_sound('menu_select')
        
        elif self.state == 'shop':
            self._handle_shop_touch(x, y)
        
        elif self.state in ['gameover', 'victory']:
            # Tap to restart
            self.reset_game()
            self.state = 'menu'
            self.play_sound('menu_select')
    
    def _handle_shop_touch(self, x, y):
        """Handle shop touch interactions"""
        # Calculate which upgrade was tapped based on y position
        base_y = self.screen_height * 0.2
        item_height = self.screen_height * 0.08
        
        relative_y = y - base_y
        if relative_y > 0:
            item_index = int(relative_y / item_height)
            if 0 <= item_index <= 7:
                # Simulate key press for that upgrade
                key_map = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, 
                          pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]
                self.handle_shop_input(key_map[item_index])
        
        # Continue button at bottom
        if y > self.screen_height * 0.9:
            self.handle_shop_input(pygame.K_RETURN)
    
    def set_difficulty(self, difficulty):
        """Set game difficulty and start"""
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.reset_game()
        self.state = 'playing'
        self.show_message(STAGES[0]['name'], 180)
        self.play_sound('wave_start')
        if self.music_enabled and self.music_manager:
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
                self.touch_controls.update_unlocked_ammo(player.unlocked_ammo)
            else:
                self.play_sound('error')
        
        elif key == pygame.K_5 and 'plasma' not in player.unlocked_ammo:
            if player.refugees >= costs['plasma_ammo']:
                player.refugees -= costs['plasma_ammo']
                player.unlock_ammo('plasma')
                purchased = "Phased Plasma"
                self.touch_controls.update_unlocked_ammo(player.unlocked_ammo)
            else:
                self.play_sound('error')
        
        elif key == pygame.K_6 and 'fusion' not in player.unlocked_ammo:
            if player.refugees >= costs['fusion_ammo']:
                player.refugees -= costs['fusion_ammo']
                player.unlock_ammo('fusion')
                purchased = "Fusion Ammo"
                self.touch_controls.update_unlocked_ammo(player.unlocked_ammo)
            else:
                self.play_sound('error')
        
        elif key == pygame.K_7 and 'barrage' not in player.unlocked_ammo:
            if player.refugees >= costs['barrage_ammo']:
                player.refugees -= costs['barrage_ammo']
                player.unlock_ammo('barrage')
                purchased = "Barrage Ammo"
                self.touch_controls.update_unlocked_ammo(player.unlocked_ammo)
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
                self.show_message(STAGES[self.current_stage]['name'], 180)
                self.play_sound('wave_start')
        
        if purchased:
            self.show_message(f"Purchased: {purchased}", 90)
            if purchased != "WOLF UPGRADE!":
                self.play_sound('purchase')
    
    def update(self):
        """Update game state"""
        if self.state != 'playing':
            return
        
        # Handle pause from touch controls
        if self.pause_cooldown > 0:
            self.pause_cooldown -= 1
        
        if self.touch_controls.is_pause_pressed() and self.pause_cooldown == 0:
            self.state = 'paused'
            self.play_sound('menu_select')
            self.pause_cooldown = 30  # Cooldown frames
            return
        
        # Get movement from touch controls (or keyboard)
        keys = pygame.key.get_pressed()
        touch_dx, touch_dy = self.touch_controls.get_movement()
        
        # Handle ammo switching from touch
        tapped_ammo = self.touch_controls.get_ammo_tap()
        if tapped_ammo and tapped_ammo in self.player.unlocked_ammo:
            self.player.switch_ammo(tapped_ammo)
            self.play_sound('ammo_switch')
        
        # Update player with combined input
        self._update_player(keys, touch_dx, touch_dy)
        
        # Player shooting (touch or keyboard)
        if self.touch_controls.is_firing() or keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            bullets = self.player.shoot()
            if bullets:
                self.play_sound('autocannon', 0.3)
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        # Rockets
        if self.touch_controls.is_rocket() or keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
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
        
        # Check collisions
        self._check_collisions()
        
        # Wave/Stage logic
        self.update_waves()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def _update_player(self, keys, touch_dx, touch_dy):
        """Update player with combined keyboard and touch input"""
        current_speed = self.player.speed
        if pygame.time.get_ticks() < self.player.overdrive_until:
            current_speed *= 1.5
        
        # Keyboard input
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += 1
        
        # Combine with touch input
        if abs(touch_dx) > 0.1 or abs(touch_dy) > 0.1:
            dx = touch_dx
            dy = touch_dy
        
        # Apply movement
        self.player.rect.x += int(dx * current_speed)
        self.player.rect.y += int(dy * current_speed)
        
        # Keep on screen
        self.player.rect.clamp_ip(pygame.Rect(0, 0, self.screen_width, self.screen_height))
    
    def _check_collisions(self):
        """Handle all collision detection"""
        # Player bullets vs enemies
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
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
            
            if self.player.shields > 0:
                self.play_sound('shield_hit', 0.5)
            elif self.player.armor > 0:
                self.play_sound('armor_hit', 0.5)
            else:
                self.play_sound('hull_hit', 0.6)
            
            self.shake.add(SHAKE_SMALL)
            
            if self.player.take_damage(damage):
                explosion = Explosion(self.player.rect.centerx, self.player.rect.centery,
                                    50, COLOR_MINMATAR_ACCENT)
                self.effects.add(explosion)
                self.all_sprites.add(explosion)
                self.shake.add(SHAKE_LARGE)
                self.play_sound('explosion_large')
                self.state = 'gameover'
                if self.music_manager:
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
                if self.music_manager:
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
    
    def draw_menu(self):
        """Draw main menu"""
        # Title
        title = self.font_large.render("MINMATAR REBELLION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.render_surface.blit(title, rect)
        
        # Subtitle
        sub = self.font.render("Mobile Edition", True, COLOR_TEXT)
        rect = sub.get_rect(center=(self.screen_width // 2, 190))
        self.render_surface.blit(sub, rect)
        
        # Instructions
        y = 300
        instructions = [
            "Touch Controls:",
            "Left Joystick - Move",
            "FIRE Button - Shoot",
            "RKT Button - Rockets",
            "Ammo Buttons - Switch Ammo",
            "",
            "TAP TO START"
        ]
        for line in instructions:
            text = self.font.render(line, True, COLOR_TEXT)
            rect = text.get_rect(center=(self.screen_width // 2, y))
            self.render_surface.blit(text, rect)
            y += 30
        
        # Sound options
        y += 20
        sound_status = "ON" if self.sound_enabled else "OFF"
        text = self.font_small.render(f"Sound: {sound_status}", True, (150, 150, 150))
        rect = text.get_rect(center=(self.screen_width // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_difficulty(self):
        """Draw difficulty selection screen"""
        title = self.font_large.render("SELECT DIFFICULTY", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(self.screen_width // 2, 100))
        self.render_surface.blit(title, rect)
        
        y = 200
        difficulties = [
            ('Easy', 'Less enemies, more powerups', (100, 255, 100)),
            ('Normal', 'Standard experience', COLOR_TEXT),
            ('Hard', 'Tougher enemies', (255, 200, 100)),
            ('Nightmare', 'For veterans only', (255, 100, 100))
        ]
        
        for name, desc, color in difficulties:
            # Draw touch area
            pygame.draw.rect(self.render_surface, (30, 30, 40), 
                           (40, y - 10, self.screen_width - 80, 60))
            pygame.draw.rect(self.render_surface, color, 
                           (40, y - 10, self.screen_width - 80, 60), 2)
            
            text = self.font.render(name, True, color)
            self.render_surface.blit(text, (60, y))
            
            desc_text = self.font_small.render(desc, True, (150, 150, 150))
            self.render_surface.blit(desc_text, (60, y + 25))
            
            y += 80
        
        # Back option
        text = self.font.render("TAP HERE TO GO BACK", True, (150, 150, 150))
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        self.render_surface.blit(text, rect)
    
    def draw_game(self):
        """Draw gameplay elements"""
        # Draw sprites
        for sprite in self.all_sprites:
            if sprite != self.player:
                self.render_surface.blit(sprite.image, sprite.rect)
        
        # Draw player last (on top)
        self.render_surface.blit(self.player.image, self.player.rect)
        
        # Draw HUD
        self.draw_hud()
        
        # Draw touch controls
        self.touch_controls.draw(self.render_surface, self.player.current_ammo)
        
        # Draw message
        if self.message_timer > 0:
            text = self.font_large.render(self.message, True, (255, 255, 255))
            rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))
            self.render_surface.blit(text, rect)
    
    def draw_hud(self):
        """Draw heads-up display (compact for mobile)"""
        # Health bars (top center, smaller for mobile)
        bar_width = 100
        bar_height = 8
        x = (self.screen_width - bar_width) // 2
        y = 8
        
        # Shields
        pygame.draw.rect(self.render_surface, (50, 50, 80), (x, y, bar_width, bar_height))
        shield_pct = self.player.shields / self.player.max_shields
        pygame.draw.rect(self.render_surface, COLOR_SHIELD, (x, y, int(bar_width * shield_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 100, 150), (x, y, bar_width, bar_height), 1)
        
        # Armor
        y += bar_height + 2
        pygame.draw.rect(self.render_surface, (50, 40, 30), (x, y, bar_width, bar_height))
        armor_pct = self.player.armor / self.player.max_armor
        pygame.draw.rect(self.render_surface, COLOR_ARMOR, (x, y, int(bar_width * armor_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 80, 60), (x, y, bar_width, bar_height), 1)
        
        # Hull
        y += bar_height + 2
        pygame.draw.rect(self.render_surface, (40, 40, 40), (x, y, bar_width, bar_height))
        hull_pct = self.player.hull / self.player.max_hull
        pygame.draw.rect(self.render_surface, COLOR_HULL, (x, y, int(bar_width * hull_pct), bar_height))
        pygame.draw.rect(self.render_surface, (80, 80, 80), (x, y, bar_width, bar_height), 1)
        
        # Score and refugees (compact, top right)
        score_text = self.font_small.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.render_surface.blit(score_text, (self.screen_width - 120, 8))
        
        ref_text = self.font_small.render(f"Refugees: {self.player.refugees}", True, (100, 255, 100))
        self.render_surface.blit(ref_text, (self.screen_width - 120, 24))
        
        # Rockets count near rocket button
        rockets_text = self.font_small.render(f"x{self.player.rockets}", True, COLOR_TEXT)
        rocket_btn = self.touch_controls.rocket_button
        self.render_surface.blit(rockets_text, (rocket_btn.x - 40, rocket_btn.y - 5))
    
    def draw_pause(self):
        """Draw pause overlay"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.render_surface.blit(overlay, (0, 0))
        
        text = self.font_large.render("PAUSED", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Tap to Resume", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 50))
        self.render_surface.blit(text, rect)
    
    def draw_shop(self):
        """Draw upgrade shop"""
        title = self.font_large.render("REBEL STATION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(self.screen_width // 2, 40))
        self.render_surface.blit(title, rect)
        
        # Refugees
        text = self.font.render(f"Refugees: {self.player.refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(self.screen_width // 2, 80))
        self.render_surface.blit(text, rect)
        
        # Upgrades
        y = 120
        costs = UPGRADE_COSTS
        player = self.player
        
        upgrades = [
            ("Gyro (+30% Fire)", costs['gyrostabilizer'], player.has_gyro),
            ("Armor (+30)", costs['armor_plate'], False),
            ("Tracking (+1 Gun)", costs['tracking_enhancer'], player.has_tracking),
            ("EMP Ammo", costs['emp_ammo'], 'emp' in player.unlocked_ammo),
            ("Plasma Ammo", costs['plasma_ammo'], 'plasma' in player.unlocked_ammo),
            ("Fusion Ammo", costs['fusion_ammo'], 'fusion' in player.unlocked_ammo),
            ("Barrage Ammo", costs['barrage_ammo'], 'barrage' in player.unlocked_ammo),
            ("WOLF (T2 Ship!)", costs['wolf_upgrade'], player.is_wolf)
        ]
        
        for name, cost, owned in upgrades:
            if owned:
                color = (80, 80, 80)
                status = "[OWNED]"
            elif player.refugees >= cost:
                color = (100, 255, 100)
                status = f"[{cost}]"
            else:
                color = (255, 100, 100)
                status = f"[{cost}]"
            
            # Draw touch area
            pygame.draw.rect(self.render_surface, (25, 25, 35), 
                           (20, y - 5, self.screen_width - 40, 40))
            
            text = self.font_small.render(f"{name} {status}", True, color)
            self.render_surface.blit(text, (30, y + 5))
            y += 45
        
        # Continue
        y += 20
        pygame.draw.rect(self.render_surface, (50, 100, 50), 
                       (60, y, self.screen_width - 120, 50))
        text = self.font.render("CONTINUE", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen_width // 2, y + 25))
        self.render_surface.blit(text, rect)
    
    def draw_gameover(self):
        """Draw game over screen"""
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 150))
        self.render_surface.blit(overlay, (0, 0))
        
        text = self.font_large.render("SHIP DESTROYED", True, (255, 100, 100))
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 30))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Tap to return to menu", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 100))
        self.render_surface.blit(text, rect)
    
    def draw_victory(self):
        """Draw victory screen"""
        title = self.font_large.render("VICTORY!", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(self.screen_width // 2, 150))
        self.render_surface.blit(title, rect)
        
        text = self.font.render("The Amarr have fallen!", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, 220))
        self.render_surface.blit(text, rect)
        
        y = 300
        text = self.font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, y))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(self.screen_width // 2, y + 40))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Tap to play again", True, COLOR_TEXT)
        rect = text.get_rect(center=(self.screen_width // 2, y + 120))
        self.render_surface.blit(text, rect)
    
    async def run_async(self):
        """Async main game loop for web/mobile (Pygbag compatible)"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            await asyncio.sleep(0)  # Required for Pygbag
        
        pygame.quit()
    
    def run(self):
        """Standard main game loop for desktop testing"""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    game = MobileGame()
    game.run()
