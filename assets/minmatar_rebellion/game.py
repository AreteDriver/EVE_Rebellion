"""Main game logic for Minmatar Rebellion"""
import pygame
import random
import math
from constants import *
from sprites import (Player, Enemy, Bullet, EnemyBullet, Rocket, 
                     RefugeePod, Powerup, Explosion, Star)
from sounds import get_sound_manager, get_music_manager, play_sound
from controller import Controller


class ScreenShake:
    """Manages screen shake effects"""
    
    def __init__(self):
        self.intensity = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def add(self, intensity):
        self.intensity = max(self.intensity, intensity)
    
    def update(self):
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
        
        self.sound_manager = get_sound_manager()
        self.music_manager = get_music_manager()
        self.sound_enabled = True
        self.music_enabled = True
        
        # Initialize controller
        self.controller = Controller()
        
        self.shake = ScreenShake()
        
        self.state = 'menu'
        self.running = True
        self.difficulty = 'normal'
        self.difficulty_settings = DIFFICULTY_SETTINGS['normal']
        
        self.stars = [Star() for _ in range(100)]
        
        self.reset_game()
    
    def play_sound(self, sound_name, volume=1.0):
        if self.sound_enabled:
            self.sound_manager.play(sound_name, volume)
    
    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.pods = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.current_stage = 0
        self.current_wave = 0
        self.wave_enemies = 0
        self.wave_spawned = 0
        self.spawn_timer = 0
        self.wave_delay = 0
        self.stage_complete = False
        
        self.message = ""
        self.message_timer = 0
    
    def show_message(self, text, duration=120):
        self.message = text
        self.message_timer = duration
    
    def spawn_wave(self):
        stage = STAGES[self.current_stage]
        num_enemies = 3 + self.current_wave + self.current_stage
        
        if stage.get('boss') and self.current_wave == stage.get('waves', 0) - 1:
            boss = Enemy(stage['boss'], SCREEN_WIDTH // 2, -100, self.difficulty_settings)
            self.enemies.add(boss)
            self.all_sprites.add(boss)
            self.wave_enemies = 1
            self.wave_spawned = 1
            self.show_message(f"WARNING: {boss.stats['name'].upper()} APPROACHING!", 180)
            self.play_sound('warning')
            return
        
        self.wave_enemies = num_enemies
        self.wave_spawned = 0
        
        if random.random() < stage['industrial_chance']:
            self.wave_enemies += 1
    
    def spawn_enemy(self):
        if self.wave_spawned >= self.wave_enemies:
            return
        
        stage = STAGES[self.current_stage]
        
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
        chance = self.difficulty_settings.get('powerup_chance', 0.15)
        if random.random() < chance:
            powerup_type = random.choice(list(POWERUP_TYPES.keys()))
            powerup = Powerup(x, y, powerup_type)
            self.powerups.add(powerup)
            self.all_sprites.add(powerup)
    
    def handle_events(self):
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
                
                elif self.state == 'playing':
                    if event.key == pygame.K_ESCAPE:
                        self.state = 'paused'
                        self.play_sound('menu_select')
                    elif event.key == pygame.K_q or event.key == pygame.K_TAB:
                        self.player.cycle_ammo()
                        self.play_sound('ammo_switch')
                    else:
                        for ammo_type, data in AMMO_TYPES.items():
                            if event.key == data['key']:
                                if self.player.switch_ammo(ammo_type):
                                    self.show_message(f"Ammo: {data['name']}", 60)
                                    self.play_sound('ammo_switch')
                                break
            
            # Controller button events
            elif event.type == pygame.JOYBUTTONDOWN:
                if self.state == 'playing':
                    if self.controller.pause_pressed():
                        self.state = 'paused'
                        self.play_sound('menu_select')
                    elif event.button == self.controller.BUTTON_X or event.button == self.controller.BUTTON_LB:
                        self.player.cycle_ammo()
                        self.play_sound('ammo_switch')
                
                elif self.state == 'paused':
                    if self.controller.pause_pressed() or self.controller.select_pressed():
                        self.state = 'playing'
                        self.play_sound('menu_select')
                
                elif self.state == 'menu':
                    if self.controller.select_pressed():
                        self.state = 'difficulty'
                        self.play_sound('menu_select')
                
                elif self.state == 'difficulty':
                    if event.button == self.controller.BUTTON_A:
                        self.set_difficulty('normal')
                
                elif self.state in ['gameover', 'victory']:
                    if self.controller.select_pressed():
                        self.reset_game()
                        self.state = 'menu'
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
    
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.difficulty_settings = DIFFICULTY_SETTINGS[difficulty]
        self.reset_game()
        self.state = 'playing'
        self.show_message(STAGES[0]['name'], 180)
        self.play_sound('wave_start')
        if self.music_enabled:
            self.music_manager.start_music()
    
    def handle_shop_input(self, key):
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
        if self.state != 'playing':
            return
        
        keys = pygame.key.get_pressed()
        
        # Get controller input
        move_x, move_y = self.controller.get_movement()
        
        # Update player with keyboard or controller
        if self.controller.enabled and (abs(move_x) > 0 or abs(move_y) > 0):
            # Use controller for movement
            speed = self.player.speed
            if pygame.time.get_ticks() < self.player.overdrive_until:
                speed *= 1.5
            
            self.player.rect.x += move_x * speed
            self.player.rect.y += move_y * speed
            self.player.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            # Use keyboard
            self.player.update(keys)
        
        # Shooting - keyboard or controller
        if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] or self.controller.fire_pressed():
            bullets = self.player.shoot()
            if bullets:
                self.play_sound('autocannon', 0.3)
            for bullet in bullets:
                self.player_bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        # Rockets - keyboard, mouse, or controller
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] or pygame.mouse.get_pressed()[2] or self.controller.rocket_pressed():
            rocket = self.player.shoot_rocket()
            if rocket:
                self.play_sound('rocket', 0.5)
                self.player_bullets.add(rocket)
                self.all_sprites.add(rocket)
        
        for star in self.stars:
            star.update()
        
        self.player_bullets.update()
        self.enemy_bullets.update()
        
        for enemy in self.enemies:
            enemy.update(self.player.rect)
        
        self.pods.update()
        self.powerups.update()
        self.effects.update()
        
        self.shake.update()
        
        for enemy in self.enemies:
            bullets = enemy.shoot(self.player.rect)
            if bullets:
                self.play_sound('laser', 0.2)
            for bullet in bullets:
                self.enemy_bullets.add(bullet)
                self.all_sprites.add(bullet)
        
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
            for enemy in hits:
                bullet.kill()
                if enemy.take_damage(bullet):
                    self.player.score += enemy.score
                    
                    if enemy.is_boss:
                        self.shake.add(SHAKE_LARGE)
                        self.play_sound('explosion_large')
                    elif enemy.enemy_type in ['omen', 'maller']:
                        self.shake.add(SHAKE_MEDIUM)
                        self.play_sound('explosion_medium')
                    else:
                        self.shake.add(SHAKE_SMALL)
                        self.play_sound('explosion_small', 0.6)
                    
                    exp_size = 30 if not enemy.is_boss else 80
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery, 
                                        exp_size, COLOR_AMARR_ACCENT)
                    self.effects.add(explosion)
                    self.all_sprites.add(explosion)
                    
                    if enemy.refugees > 0:
                        refugee_count = int(enemy.refugees * self.difficulty_settings['refugee_mult'])
                        for _ in range(max(1, refugee_count)):
                            pod = RefugeePod(
                                enemy.rect.centerx + random.randint(-20, 20),
                                enemy.rect.centery + random.randint(-20, 20)
                            )
                            self.pods.add(pod)
                            self.all_sprites.add(pod)
                    
                    self.spawn_powerup(enemy.rect.centerx, enemy.rect.centery)
                    
                    enemy.kill()
                break
        
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
                self.music_manager.stop_music()
                return
        
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
        
        hits = pygame.sprite.spritecollide(self.player, self.pods, True)
        for pod in hits:
            self.player.collect_refugee(pod.count)
            self.play_sound('pickup_refugee', 0.5)
        
        hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for powerup in hits:
            self.apply_powerup(powerup)
            self.play_sound('pickup_powerup', 0.6)
        
        self.update_waves()
        
        if self.message_timer > 0:
            self.message_timer -= 1
    
    def apply_powerup(self, powerup):
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
        stage = STAGES[self.current_stage]
        
        if self.wave_delay > 0:
            self.wave_delay -= 1
            return
        
        if self.wave_enemies == 0 and not self.stage_complete:
            if self.current_wave < stage['waves']:
                self.spawn_wave()
                if not (stage['boss'] and self.current_wave == stage['waves'] - 1):
                    self.show_message(f"Wave {self.current_wave + 1}/{stage['waves']}", 90)
                    self.play_sound('wave_start', 0.4)
        
        self.spawn_timer += 1
        if self.spawn_timer >= 45 and self.wave_spawned < self.wave_enemies:
            self.spawn_timer = 0
            self.spawn_enemy()
        
        if len(self.enemies) == 0 and self.wave_spawned >= self.wave_enemies and self.wave_enemies > 0:
            self.current_wave += 1
            self.wave_enemies = 0
            self.wave_spawned = 0
            self.wave_delay = 90
            
            if self.current_wave >= stage['waves']:
                self.stage_complete = True
                self.wave_delay = 120
                self.show_message("STAGE COMPLETE!", 120)
                self.play_sound('stage_complete')
                pygame.time.set_timer(pygame.USEREVENT + 1, 2000, 1)
        
        for event in pygame.event.get(pygame.USEREVENT + 1):
            if self.stage_complete:
                self.state = 'shop'
    
    def draw(self):
        self.render_surface.fill((10, 10, 20))
        
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
        
        shake_x, shake_y = self.shake.offset_x, self.shake.offset_y
        self.screen.blit(self.render_surface, (shake_x, shake_y))
        
        pygame.display.flip()
    
    def draw_difficulty(self):
        title = self.font_large.render("SELECT DIFFICULTY", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.render_surface.blit(title, rect)
        
        y = 250
        difficulties = [
            ('1', 'easy', 'Easy', 'Reduced enemy health and damage'),
            ('2', 'normal', 'Normal', 'Standard experience'),
            ('3', 'hard', 'Hard', 'Tougher enemies, faster attacks'),
            ('4', 'nightmare', 'Nightmare', 'For veteran pilots only')
        ]
        
        for key, diff_id, name, desc in difficulties:
            color = COLOR_MINMATAR_ACCENT if diff_id == 'normal' else COLOR_TEXT
            if diff_id == 'nightmare':
                color = (255, 100, 100)
            
            text = self.font.render(f"[{key}] {name}", True, color)
            self.render_surface.blit(text, (150, y))
            
            desc_text = self.font_small.render(desc, True, (150, 150, 150))
            self.render_surface.blit(desc_text, (150, y + 25))
            
            y += 70
        
        y += 30
        text = self.font.render("[ESC] Back to Menu", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_game(self):
        for sprite in self.all_sprites:
            if sprite != self.player:
                self.render_surface.blit(sprite.image, sprite.rect)
        
        self.render_surface.blit(self.player.image, self.player.rect)
        
        self.draw_hud()
        
        if self.message_timer > 0:
            text = self.font_large.render(self.message, True, (255, 255, 255))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            self.render_surface.blit(text, rect)
    
    def draw_hud(self):
        bar_width = 150
        bar_height = 12
        x = 10
        y = 10
        
        pygame.draw.rect(self.render_surface, (50, 50, 80), (x, y, bar_width, bar_height))
        shield_pct = self.player.shields / self.player.max_shields
        pygame.draw.rect(self.render_surface, COLOR_SHIELD, (x, y, int(bar_width * shield_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 100, 150), (x, y, bar_width, bar_height), 1)
        
        y += bar_height + 3
        pygame.draw.rect(self.render_surface, (50, 40, 30), (x, y, bar_width, bar_height))
        armor_pct = self.player.armor / self.player.max_armor
        pygame.draw.rect(self.render_surface, COLOR_ARMOR, (x, y, int(bar_width * armor_pct), bar_height))
        pygame.draw.rect(self.render_surface, (100, 80, 60), (x, y, bar_width, bar_height), 1)
        
        y += bar_height + 3
        pygame.draw.rect(self.render_surface, (40, 40, 40), (x, y, bar_width, bar_height))
        hull_pct = self.player.hull / self.player.max_hull
        pygame.draw.rect(self.render_surface, COLOR_HULL, (x, y, int(bar_width * hull_pct), bar_height))
        pygame.draw.rect(self.render_surface, (80, 80, 80), (x, y, bar_width, bar_height), 1)
        
        y += bar_height + 10
        ammo = AMMO_TYPES[self.player.current_ammo]
        pygame.draw.rect(self.render_surface, ammo['color'], (x, y, 20, 20))
        text = self.font_small.render(ammo['name'], True, COLOR_TEXT)
        self.render_surface.blit(text, (x + 25, y + 2))
        
        y += 25
        text = self.font_small.render(f"Rockets: {self.player.rockets}", True, COLOR_TEXT)
        self.render_surface.blit(text, (x, y))
        
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
        
        if self.current_stage < len(STAGES):
            y += 30
            stage = STAGES[self.current_stage]
            text = self.font_small.render(f"Stage {self.current_stage + 1}", True, COLOR_TEXT)
            self.render_surface.blit(text, (x, y))
        
        y += 20
        diff_color = (100, 255, 100) if self.difficulty == 'easy' else (
            COLOR_TEXT if self.difficulty == 'normal' else (
            (255, 200, 100) if self.difficulty == 'hard' else (255, 100, 100)
        ))
        text = self.font_small.render(f"[{self.difficulty_settings['name']}]", True, diff_color)
        self.render_surface.blit(text, (x, y))
    
    def draw_menu(self):
        title = self.font_large.render("MINMATAR REBELLION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.render_surface.blit(title, rect)
        
        sub = self.font.render("A Top-Down Space Shooter", True, COLOR_TEXT)
        rect = sub.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.render_surface.blit(sub, rect)
        
        y = 320
        
        # Show controller status
        if self.controller.enabled:
            ctrl_text = self.font_small.render(f"Controller: {self.controller.joystick.get_name()}", True, (100, 255, 100))
            rect = ctrl_text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.render_surface.blit(ctrl_text, rect)
            y += 25
        
        y += 15
        instructions = [
            "WASD or Arrow Keys - Move",
            "Space or Left Click - Fire Autocannons",
            "Shift or Right Click - Fire Rockets",
            "1-5 or Q/Tab - Switch Ammo",
        ]
        
        if self.controller.enabled:
            instructions.append("")
            instructions.append("Left Stick - Move | A/RT - Fire")
            instructions.append("B/LT - Rockets | X/LB - Cycle Ammo")
        
        instructions.append("")
        instructions.append("Press ENTER or A to Start")
        
        for line in instructions:
            text = self.font_small.render(line, True, COLOR_TEXT)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.render_surface.blit(text, rect)
            y += 26
        
        y += 30
        sound_status = "ON" if self.sound_enabled else "OFF"
        music_status = "ON" if self.music_enabled else "OFF"
        text = self.font_small.render(f"[S] Sound: {sound_status}  [M] Music: {music_status}", True, (150, 150, 150))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_pause(self):
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
        title = self.font_large.render("REBEL STATION", True, COLOR_MINMATAR_ACCENT)
        rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.render_surface.blit(title, rect)
        
        text = self.font.render(f"Refugees Available: {self.player.refugees}", True, (100, 255, 100))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.render_surface.blit(text, rect)
        
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
        
        y += 30
        text = self.font.render("Press ENTER to continue to next stage", True, COLOR_TEXT)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
        self.render_surface.blit(text, rect)
    
    def draw_gameover(self):
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
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
