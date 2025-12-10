"""Main game logic for Minmatar Rebellion"""
import pygame
import random
import math
from constants import *
from sprites import (Player, Enemy, Bullet, EnemyBullet, Rocket, 
                     RefugeePod, Powerup, Explosion, Star)
from sounds import get_sound_manager, get_music_manager, play_sound


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
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.render_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Minmatar Rebellion")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)
        self.font_large = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 22)
        
        # Initialize sound
        self.sound_manager = get_sound_manager()
        self.music_manager = get_music_manager()
        self.sound_enabled = True
        self.music_enabled = True
        
        # Screen shake
        self.shake = ScreenShake()
        
        # Game state
        self.state = 'menu'  # menu, difficulty, ship_select, playing, shop, paused, gameover, victory
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']
        
        # T2 Ship unlocks (persists across games)
        self.unlocked_ships = ['rifter']  # Start with only Rifter unlocked
        self.total_skill_points = 0  # Accumulated skill points across all games
        self.selected_ship = 'rifter'
        
        # Ship selection UI state
        self.ship_select_index = 0
        self.show_ship_info = False
        
        # Background stars
        self.stars = [Star() for _ in range(100)]
        
        self.reset_game()
    
    def play_sound(self, sound_name, volume=1.0):
        """Play sound if enabled"""
        if self.sound_enabled:
            self.sound_manager.play(sound_name, volume)
    
    def reset_game(self, ship_type=None):
        """Reset all game state"""
        # Sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pods = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        
        # Player - use selected ship type
        if ship_type is None:
            ship_type = self.selected_ship
        self.player = Player(ship_type)
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
            boss = Enemy(stage['boss'], SCREEN_WIDTH // 2, -100, self.difficulty_settings)
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
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == 'menu':
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        self.state = 'difficulty'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_m:
                        self.music_enabled = not self.music_enabled
                        if self.music_enabled:
                            self.music_manager.start_music()
                        else:
                            self.music_manager.stop_music()
                    elif event.key == pygame.K_s:
                        self.sound_enabled = not self.sound_enabled
                
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
                
                elif self.state == 'ship_select':
                    self.handle_ship_select_input(event.key)
                
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
                        # Save skill points before reset
                        self.total_skill_points += self.player.skill_points
                        self.reset_game()
                        self.state = 'menu'
                        self.play_sound('menu_select')
    
    def handle_ship_select_input(self, key):
        """Handle ship selection screen input"""
        ships = ['rifter', 'wolf', 'jaguar']
        
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.ship_select_index = (self.ship_select_index - 1) % len(ships)
            self.play_sound('menu_select')
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.ship_select_index = (self.ship_select_index + 1) % len(ships)
            self.play_sound('menu_select')
        elif key == pygame.K_i:
            # Toggle info display
            self.show_ship_info = not self.show_ship_info
            self.play_sound('menu_select')
        elif key == pygame.K_u:
            # Unlock ship with skill points
            ship = ships[self.ship_select_index]
            if ship not in self.unlocked_ships and ship in T2_SHIP_COSTS:
                cost = T2_SHIP_COSTS[ship]
                if self.total_skill_points >= cost:
                    self.total_skill_points -= cost
                    self.unlocked_ships.append(ship)
                    self.play_sound('upgrade')
                    self.show_message(f"{ship.upper()} UNLOCKED!", 90)
                else:
                    self.play_sound('error')
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Select ship and start game
            ship = ships[self.ship_select_index]
            if ship in self.unlocked_ships:
                self.selected_ship = ship
                self.reset_game(ship)
                self.state = 'playing'
                self.show_message(STAGES[0]['name'], 180)
                self.play_sound('wave_start')
                if self.music_enabled:
                    self.music_manager.start_music()
            else:
                self.play_sound('error')
        elif key == pygame.K_ESCAPE:
            self.state = 'difficulty'
            self.play_sound('menu_select')
    
    def set_difficulty(self, difficulty):
        """Set game difficulty and go to ship selection"""
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.state = 'ship_select'
        self.ship_select_index = 0
        self.play_sound('menu_select')
    
    def handle_shop_input(self, key):
        """Handle shop menu input"""
        costs = UPGRADE_COSTS
        player = self.player
        
        purchased = None
        
        # Check if player already has T2 ship
        has_t2 = player.is_wolf or player.is_jaguar
        
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
        
        elif key == pygame.K_8 and not has_t2:
            if player.refugees >= costs['wolf_upgrade']:
                player.refugees -= costs['wolf_upgrade']
                player.upgrade_to_wolf()
                purchased = "WOLF UPGRADE!"
                self.play_sound('upgrade')
            else:
                self.play_sound('error')
        
        elif key == pygame.K_9 and not has_t2:
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
            if purchased not in ["WOLF UPGRADE!", "JAGUAR UPGRADE!"]:  # T2 upgrades have their own sound
                self.play_sound('purchase')
    
    def update(self):
        """Update game state"""
        if self.state != 'playing':
            return
        
        keys = pygame.key.get_pressed()
        
        # Update player
        self.player.update(keys)
        
        # Player shooting
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            bullets = self.player.shoot()
            if bullets:
                self.play_sound('autocannon', 0.3)
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        # Rockets
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2]:
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
        
        # Check collisions - player bullets vs enemies
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                if enemy.take_damage(bullet):
                    # Enemy destroyed
                    self.player.score += enemy.score
                    
                    # Award skill points for the kill
                    skill_points = SKILL_POINTS_PER_ENEMY.get(enemy.enemy_type, 5)
                    self.player.add_skill_points(skill_points)
                    
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
        elif self.state == 'ship_select':
            self.draw_ship_select()
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
    
    def draw_ship_select(self):
        """Draw ship selection screen"""
        # Title
        title = self.font_large.render("SELECT YOUR SHIP", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.render_surface.blit(title, rect)
        
        # Skill points display
        sp_text = self.font.render(f"Skill Points: {self.total_skill_points}", True, (200, 150, 255))
        rect = sp_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(sp_text, rect)
        
        ships = ['rifter', 'wolf', 'jaguar']
        ship_width = 120
        spacing = 40
        total_width = len(ships) * ship_width + (len(ships) - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, ship in enumerate(ships):
            x = start_x + i * (ship_width + spacing) + ship_width // 2
            y = 220
            
            # Selection highlight
            is_selected = i == self.ship_select_index
            is_unlocked = ship in self.unlocked_ships
            
            # Draw ship box
            box_color = (80, 60, 40) if is_unlocked else (40, 40, 50)
            if is_selected:
                box_color = COLOR_MINMATAR_ACCENT if is_unlocked else (80, 80, 100)
            
            pygame.draw.rect(self.render_surface, box_color, 
                           (x - ship_width//2, y - 20, ship_width, 140), 0, 8)
            
            # Selection border
            border_color = (255, 255, 255) if is_selected else (100, 100, 100)
            pygame.draw.rect(self.render_surface, border_color,
                           (x - ship_width//2, y - 20, ship_width, 140), 2, 8)
            
            # Draw ship sprite preview
            preview = self._create_ship_preview(ship)
            preview_rect = preview.get_rect(center=(x, y + 30))
            self.render_surface.blit(preview, preview_rect)
            
            # Ship name
            info = T2_SHIP_INFO[ship]
            name_color = (255, 255, 255) if is_unlocked else (150, 150, 150)
            name_text = self.font.render(info['name'], True, name_color)
            name_rect = name_text.get_rect(center=(x, y + 75))
            self.render_surface.blit(name_text, name_rect)
            
            # Ship type
            type_text = self.font_small.render(info['type'], True, (150, 150, 150))
            type_rect = type_text.get_rect(center=(x, y + 95))
            self.render_surface.blit(type_text, type_rect)
            
            # Lock/unlock status
            if not is_unlocked:
                cost = T2_SHIP_COSTS.get(ship, 0)
                lock_color = (100, 255, 100) if self.total_skill_points >= cost else (255, 100, 100)
                lock_text = self.font_small.render(f"LOCKED ({cost} SP)", True, lock_color)
                lock_rect = lock_text.get_rect(center=(x, y + 115))
                self.render_surface.blit(lock_text, lock_rect)
        
        # Get selected ship for instructions
        selected_ship = ships[self.ship_select_index]
        
        # Draw info bubble for selected ship (if toggled on)
        if self.show_ship_info:
            self.draw_ship_info_bubble(selected_ship)
        
        # Instructions
        y = 620
        if selected_ship in self.unlocked_ships:
            text = self.font.render("[ENTER] Launch Mission", True, (100, 255, 100))
        else:
            cost = T2_SHIP_COSTS.get(selected_ship, 0)
            if self.total_skill_points >= cost:
                text = self.font.render(f"[U] Unlock ({cost} SP)", True, (100, 255, 100))
            else:
                text = self.font.render(f"Need {cost} SP to unlock", True, (255, 100, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
        
        y += 30
        text = self.font_small.render("[LEFT/RIGHT] Select    [I] Info    [ESC] Back", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def _create_ship_preview(self, ship_type):
        """Create a preview sprite for ship selection"""
        width, height = 50, 60
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        if ship_type == 'wolf':
            color = COLOR_MINMATAR_ACCENT
            pygame.draw.polygon(surf, color, [
                (width//2, 0),
                (width-5, height-12),
                (width//2, height-5),
                (5, height-12)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (0, height-15),
                (12, height//2),
                (12, height-5)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (width, height-15),
                (width-12, height//2),
                (width-12, height-5)
            ])
            pygame.draw.circle(surf, (255, 150, 50), (width//2, height-8), 6)
        elif ship_type == 'jaguar':
            color = (100, 150, 180)
            pygame.draw.polygon(surf, color, [
                (width//2, 0),
                (width-3, height-12),
                (width//2, height-3),
                (3, height-12)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (0, height-12),
                (10, height//3),
                (14, height-8)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_HULL, [
                (width, height-12),
                (width-10, height//3),
                (width-14, height-8)
            ])
            pygame.draw.circle(surf, (100, 180, 255), (width//2, height-6), 6)
        else:  # rifter
            color = COLOR_MINMATAR_HULL
            pygame.draw.polygon(surf, color, [
                (width//2 - 3, 0),
                (width-8, height-15),
                (width//2, height),
                (8, height-15)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_DARK, [
                (0, height-10),
                (6, height//3),
                (14, height-5)
            ])
            pygame.draw.polygon(surf, COLOR_MINMATAR_DARK, [
                (width-3, height-20),
                (width-8, height//2),
                (width-14, height-8)
            ])
            pygame.draw.circle(surf, (255, 100, 0), (width//2, height-5), 5)
        
        return surf
    
    def draw_ship_info_bubble(self, ship_type):
        """Draw detailed info bubble for selected ship"""
        info = T2_SHIP_INFO[ship_type]
        
        # Info box position
        box_x = 50
        box_y = 380
        box_width = SCREEN_WIDTH - 100
        box_height = 180
        
        # Draw box background
        pygame.draw.rect(self.render_surface, (30, 30, 40), 
                        (box_x, box_y, box_width, box_height), 0, 8)
        pygame.draw.rect(self.render_surface, (80, 80, 100),
                        (box_x, box_y, box_width, box_height), 2, 8)
        
        # Ship name and type
        y = box_y + 15
        title = self.font.render(f"{info['name']} - {info['type']}", True, COLOR_MINMATAR_ACCENT)
        self.render_surface.blit(title, (box_x + 15, y))
        
        # Description
        y += 30
        desc = self.font_small.render(info['description'], True, COLOR_TEXT)
        self.render_surface.blit(desc, (box_x + 15, y))
        
        # Attributes
        y += 25
        attr_title = self.font_small.render("Attributes:", True, (150, 200, 255))
        self.render_surface.blit(attr_title, (box_x + 15, y))
        
        y += 20
        for attr in info['attributes']:
            attr_text = self.font_small.render(f"• {attr}", True, (150, 150, 150))
            self.render_surface.blit(attr_text, (box_x + 25, y))
            y += 18
        
        # Strategy
        y += 5
        strategy_title = self.font_small.render("Strategy:", True, (255, 200, 100))
        self.render_surface.blit(strategy_title, (box_x + 15, y))
        
        y += 20
        strategy = self.font_small.render(info['strategy'], True, (150, 150, 150))
        self.render_surface.blit(strategy, (box_x + 25, y))
    
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
        
        # Skill Points progress bar
        y += bar_height + 8
        sp_bar_width = 150
        sp_bar_height = 10
        # Calculate progress towards next T2 unlock using persistent total SP
        next_unlock_cost = min(T2_SHIP_COSTS.values()) if T2_SHIP_COSTS else 1
        # Show total persistent SP (used for unlocks) in progress bar
        total_sp = self.total_skill_points + self.player.skill_points
        sp_progress = min(total_sp / next_unlock_cost, 1.0)
        
        pygame.draw.rect(self.render_surface, (30, 30, 50), (x, y, sp_bar_width, sp_bar_height))
        pygame.draw.rect(self.render_surface, (200, 150, 255), (x, y, int(sp_bar_width * sp_progress), sp_bar_height))
        pygame.draw.rect(self.render_surface, (100, 80, 150), (x, y, sp_bar_width, sp_bar_height), 1)
        
        # Skill points text - show current game SP and total
        y += sp_bar_height + 2
        text = self.font_small.render(f"SP: {self.player.skill_points} (+{self.total_skill_points})", True, (200, 150, 255))
        self.render_surface.blit(text, (x, y))
        
        # Ammo indicator
        y += 18
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
        if self.current_stage < len(STAGES):
            y += 30
            stage = STAGES[self.current_stage]
            text = self.font_small.render(f"Stage {self.current_stage + 1}", True, COLOR_TEXT)
            self.render_surface.blit(text, (x, y))
        
        # Ship type indicator
        y += 20
        ship_name = self.player.ship_type.upper()
        ship_color = (200, 150, 255) if self.player.ship_type != 'rifter' else COLOR_TEXT
        text = self.font_small.render(f"Ship: {ship_name}", True, ship_color)
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
        # Title
        title = self.font_large.render("REBEL STATION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.render_surface.blit(title, rect)
        
        # Refugees
        text = self.font.render(f"Refugees Available: {self.player.refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.render_surface.blit(text, rect)
        
        # Skill Points
        text = self.font.render(f"Skill Points: {self.player.skill_points}", True, (200, 150, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 115))
        self.render_surface.blit(text, rect)
        
        # Upgrade options
        y = 155
        costs = UPGRADE_COSTS
        player = self.player
        
        # Check if player already has a T2 ship
        has_t2 = player.is_wolf or player.is_jaguar
        
        upgrades = [
            ("1", "Gyrostabilizer", costs['gyrostabilizer'], player.has_gyro, "+30% Fire Rate", "refugees"),
            ("2", "Armor Plate", costs['armor_plate'], False, "+30 Max Armor", "refugees"),
            ("3", "Tracking Enhancer", costs['tracking_enhancer'], player.has_tracking, "+1 Gun Spread", "refugees"),
            ("4", "EMP Ammo", costs['emp_ammo'], 'emp' in player.unlocked_ammo, "Strong vs Shields", "refugees"),
            ("5", "Phased Plasma", costs['plasma_ammo'], 'plasma' in player.unlocked_ammo, "Strong vs Armor", "refugees"),
            ("6", "Fusion Ammo", costs['fusion_ammo'], 'fusion' in player.unlocked_ammo, "High Damage", "refugees"),
            ("7", "Barrage Ammo", costs['barrage_ammo'], 'barrage' in player.unlocked_ammo, "Fast Fire", "refugees"),
        ]
        
        for key, name, cost, owned, desc, currency in upgrades:
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
            y += 32
        
        # T2 Ship upgrades (using refugees as in original, but mention they unlock permanently)
        y += 10
        t2_header = self.font_small.render("--- T2 Ship Upgrades (Use Refugees) ---", True, (150, 150, 200))
        rect = t2_header.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(t2_header, rect)
        y += 25
        
        # Wolf
        wolf_cost = costs['wolf_upgrade']
        if player.is_wolf:
            color = (80, 80, 80)
            status = "[EQUIPPED]"
        elif has_t2:
            color = (80, 80, 80)
            status = "[OTHER T2]"
        elif player.refugees >= wolf_cost:
            color = (100, 255, 100)
            status = f"[{wolf_cost} refugees]"
        else:
            color = (255, 100, 100)
            status = f"[{wolf_cost} refugees]"
        text = self.font.render(f"[8] WOLF - T2 Assault (Offense) {status}", True, color)
        self.render_surface.blit(text, (50, y))
        y += 32
        
        # Jaguar
        jaguar_cost = costs['jaguar_upgrade']
        if player.is_jaguar:
            color = (80, 80, 80)
            status = "[EQUIPPED]"
        elif has_t2:
            color = (80, 80, 80)
            status = "[OTHER T2]"
        elif player.refugees >= jaguar_cost:
            color = (100, 255, 100)
            status = f"[{jaguar_cost} refugees]"
        else:
            color = (255, 100, 100)
            status = f"[{jaguar_cost} refugees]"
        text = self.font.render(f"[9] JAGUAR - T2 Assault (Defense) {status}", True, color)
        self.render_surface.blit(text, (50, y))
        
        # Continue prompt
        y += 50
        text = self.font.render("Press ENTER to continue to next stage", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_gameover(self):
        """Draw game over screen"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((100, 0, 0, 150))
        self.render_surface.blit(overlay, (0, 0))
        
        text = self.font_large.render("SHIP DESTROYED", True, (255, 100, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.render_surface.blit(text, rect)
        
        # Show skill points earned
        text = self.font.render(f"Skill Points Earned: {self.player.skill_points}", True, (200, 150, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        self.render_surface.blit(text, rect)
        
        text = self.font_small.render("(Skill points saved for T2 ship unlocks)", True, (150, 150, 200))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Press ENTER to return to menu", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.render_surface.blit(text, rect)
    
    def draw_victory(self):
        """Draw victory screen"""
        title = self.font_large.render("VICTORY!", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.render_surface.blit(title, rect)
        
        text = self.font.render("The Amarr station has fallen.", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("The Minmatar Rebellion grows stronger!", True, COLOR_MINMATAR_ACCENT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.render_surface.blit(text, rect)
        
        y = 350
        text = self.font.render(f"Final Score: {self.player.score}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
        
        text = self.font.render(f"Souls Liberated: {self.player.total_refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 40))
        self.render_surface.blit(text, rect)
        
        # Skill points earned
        text = self.font.render(f"Skill Points Earned: {self.player.skill_points}", True, (200, 150, 255))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 80))
        self.render_surface.blit(text, rect)
        
        # Ship type
        if self.player.is_wolf:
            ship_type = "Wolf Assault Frigate"
        elif self.player.is_jaguar:
            ship_type = "Jaguar Assault Frigate"
        else:
            ship_type = "Rifter Frigate"
        text = self.font.render(f"Ship: {ship_type}", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 120))
        self.render_surface.blit(text, rect)
        
        diff_text = f"Difficulty: {self.difficulty_settings['name']}"
        text = self.font.render(diff_text, True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 150))
        self.render_surface.blit(text, rect)
        
        text = self.font_small.render("(Skill points saved for T2 ship unlocks)", True, (150, 150, 200))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 185))
        self.render_surface.blit(text, rect)
        
        text = self.font.render("Press ENTER to play again", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y + 220))
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
