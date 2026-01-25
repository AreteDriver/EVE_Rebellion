"""
VERTICAL SHMUP SOUND EFFECTS
EVE Rebellion - Devil Blade Reboot Style

Procedurally generated sound effects for:
- Weapons (autocannon, missiles, lasers)
- Point-blank kills (proximity-based feedback)
- Berserk activation/deactivation
- Heat buildup warnings
- Boss appearances
- Shield hits, explosions, UI feedback
"""

import pygame
import numpy as np
from typing import Dict, Optional


class VerticalShmupSFX:
    """
    Sound effects generator for vertical shoot-em-ups.
    All sounds procedurally generated for variation.
    """
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.enabled = pygame.mixer.get_init() is not None
        
        if not self.enabled:
            print("Audio disabled - pygame.mixer not initialized")
            return
        
        # Pre-generate common sounds
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self._generate_all_sounds()
    
    def _generate_all_sounds(self):
        """Pre-generate all sound effects"""
        print("Generating vertical shmup sound effects...")
        
        # Weapons
        self.sounds['autocannon'] = self._make_autocannon()
        self.sounds['missile'] = self._make_missile()
        self.sounds['laser'] = self._make_laser()
        self.sounds['rocket'] = self._make_rocket()
        
        # Point-blank kills (proximity feedback)
        self.sounds['kill_far'] = self._make_kill_far()
        self.sounds['kill_close'] = self._make_kill_close()
        self.sounds['kill_pointblank'] = self._make_kill_pointblank()
        
        # Berserk system
        self.sounds['berserk_activate'] = self._make_berserk_activate()
        self.sounds['berserk_warning'] = self._make_berserk_warning()
        self.sounds['berserk_expire'] = self._make_berserk_expire()
        self.sounds['boost_start'] = self._make_boost_start()
        self.sounds['boost_loop'] = self._make_boost_loop()
        
        # Heat warnings
        self.sounds['heat_25'] = self._make_heat_warning(0.25)
        self.sounds['heat_50'] = self._make_heat_warning(0.50)
        self.sounds['heat_75'] = self._make_heat_warning(0.75)
        
        # Combat
        self.sounds['explosion_small'] = self._make_explosion_small()
        self.sounds['explosion_large'] = self._make_explosion_large()
        self.sounds['shield_hit'] = self._make_shield_hit()
        self.sounds['shield_break'] = self._make_shield_break()
        self.sounds['player_hit'] = self._make_player_hit()
        
        # Bosses
        self.sounds['boss_warning'] = self._make_boss_warning()
        self.sounds['boss_spawn'] = self._make_boss_spawn()
        self.sounds['boss_death'] = self._make_boss_death()
        
        # Pickups
        self.sounds['refugee_rescue'] = self._make_refugee_rescue()
        self.sounds['powerup'] = self._make_powerup()
        self.sounds['bomb_pickup'] = self._make_bomb_pickup()
        
        # UI
        self.sounds['ui_select'] = self._make_ui_select()
        self.sounds['ui_confirm'] = self._make_ui_confirm()
        self.sounds['ui_cancel'] = self._make_ui_cancel()
        self.sounds['formation_switch'] = self._make_formation_switch()
        
        print(f"✓ Generated {len(self.sounds)} sound effects")
    
    # === WEAPON SOUNDS ===
    
    def _make_autocannon(self) -> pygame.mixer.Sound:
        """Short, punchy autocannon burst"""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Metallic impact
        freq = 150 + 80 * np.exp(-t * 30)
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Noise burst
        noise = np.random.uniform(-0.3, 0.3, len(t))
        wave += noise * np.exp(-t * 40)
        
        # Sharp attack
        envelope = np.exp(-t * 25)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_missile(self) -> pygame.mixer.Sound:
        """Whoosh + explosion"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Whoosh (frequency sweep)
        freq = 200 + 300 * t / duration
        whoosh = np.sin(2 * np.pi * freq * t) * 0.3
        
        # Explosion at end
        explosion_start = int(0.3 * self.sample_rate)
        explosion = np.random.uniform(-0.5, 0.5, len(t) - explosion_start)
        explosion *= np.exp(-(t[explosion_start:] - t[explosion_start]) * 15)
        
        wave = whoosh
        wave[explosion_start:] += explosion * 0.6
        
        envelope = 1 - np.exp(-t * 10)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_laser(self) -> pygame.mixer.Sound:
        """Clean energy beam"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Pure sine with slight vibrato
        freq = 880 + 50 * np.sin(2 * np.pi * 20 * t)
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        
        # Attack-sustain-release
        attack = np.minimum(t / 0.02, 1.0)
        release = np.maximum(1 - (t - 0.1) / 0.05, 0.0)
        envelope = attack * release
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.4)
    
    def _make_rocket(self) -> pygame.mixer.Sound:
        """Heavy explosive projectile"""
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Low rumble
        bass = np.sin(2 * np.pi * 80 * t) * 0.4
        
        # High-pitched trail
        trail_freq = 1000 + 200 * np.sin(2 * np.pi * 10 * t)
        trail = np.sin(2 * np.pi * trail_freq * t) * 0.2
        
        wave = bass + trail
        envelope = np.exp(-t * 3)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    # === POINT-BLANK KILL SOUNDS ===
    
    def _make_kill_far(self) -> pygame.mixer.Sound:
        """Basic kill (x1 multiplier)"""
        duration = 0.1
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        freq = 300
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave *= np.exp(-t * 20)
        
        return self._numpy_to_sound(wave * 0.4)
    
    def _make_kill_close(self) -> pygame.mixer.Sound:
        """Close kill (x2-x3 multiplier)"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Two-tone chime
        freq1 = 400
        freq2 = 600
        wave = np.sin(2 * np.pi * freq1 * t) * 0.3
        wave += np.sin(2 * np.pi * freq2 * t) * 0.2
        wave *= np.exp(-t * 15)
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_kill_pointblank(self) -> pygame.mixer.Sound:
        """
        Point-blank kill (x4 multiplier, x20 in Berserk).
        Satisfying "crunch" sound.
        """
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Impact hit
        impact_freq = 200 + 300 * np.exp(-t * 20)
        impact = np.sin(2 * np.pi * impact_freq * t) * 0.5
        
        # Metallic ring
        ring_freq = 800
        ring = np.sin(2 * np.pi * ring_freq * t) * 0.3
        
        # Noise crunch
        noise = np.random.uniform(-0.4, 0.4, len(t))
        noise *= np.exp(-t * 10)
        
        wave = impact + ring + noise * 0.5
        envelope = np.exp(-t * 12)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.7)
    
    # === BERSERK SYSTEM SOUNDS ===
    
    def _make_berserk_activate(self) -> pygame.mixer.Sound:
        """
        Berserk mode activation.
        Big, powerful, unmistakable.
        """
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rising sweep
        freq = 100 + 500 * (t / duration) ** 2
        sweep = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Harmonic layer
        harmony = np.sin(2 * np.pi * freq * 1.5 * t) * 0.2
        
        # Impact at end
        impact_start = int(0.7 * self.sample_rate)
        impact = np.random.uniform(-0.5, 0.5, len(t) - impact_start)
        impact *= np.exp(-(t[impact_start:] - t[impact_start]) * 10)
        
        wave = sweep + harmony
        wave[impact_start:] += impact * 0.6
        
        envelope = 1 - np.exp(-t * 5)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.8)
    
    def _make_berserk_warning(self) -> pygame.mixer.Sound:
        """Heat approaching 100% (Berserk threshold)"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Alarm beep
        freq = 1200
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Pulse envelope
        pulse = (np.sin(2 * np.pi * 5 * t) > 0).astype(float)
        wave *= pulse
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_berserk_expire(self) -> pygame.mixer.Sound:
        """Berserk timer ran out (sad trombone)"""
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Falling sweep
        freq = 400 - 200 * (t / duration)
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        wave *= np.exp(-t * 3)
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_boost_start(self) -> pygame.mixer.Sound:
        """Boost activation (LT/L2 held)"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Power-up surge
        freq = 200 + 400 * (t / duration)
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        
        envelope = 1 - np.exp(-t * 10)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_boost_loop(self) -> pygame.mixer.Sound:
        """Looping hum while Boost active"""
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Engine hum
        freq = 150 + 30 * np.sin(2 * np.pi * 4 * t)
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        
        # Subtle harmonics
        wave += np.sin(2 * np.pi * freq * 2 * t) * 0.1
        
        return self._numpy_to_sound(wave * 0.4)
    
    # === HEAT WARNING SOUNDS ===
    
    def _make_heat_warning(self, threshold: float) -> pygame.mixer.Sound:
        """
        Heat threshold crossed (25%, 50%, 75%).
        Urgency increases with threshold.
        """
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Higher pitch = higher urgency
        freq = 600 + threshold * 600
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Double beep at higher thresholds
        if threshold >= 0.5:
            beep_gap = int(0.1 * self.sample_rate)
            wave[beep_gap:] *= 0.5  # Second beep softer
        
        envelope = np.exp(-t * 15)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    # === COMBAT SOUNDS ===
    
    def _make_explosion_small(self) -> pygame.mixer.Sound:
        """Small enemy explosion"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Noise burst
        noise = np.random.uniform(-0.5, 0.5, len(t))
        
        # Low rumble
        rumble = np.sin(2 * np.pi * 100 * t) * 0.3
        
        wave = noise * 0.7 + rumble
        envelope = np.exp(-t * 10)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_explosion_large(self) -> pygame.mixer.Sound:
        """Boss/large enemy explosion"""
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Heavy bass
        bass = np.sin(2 * np.pi * 60 * t) * 0.5
        
        # Noise
        noise = np.random.uniform(-0.6, 0.6, len(t))
        
        wave = bass + noise * 0.8
        envelope = np.exp(-t * 2)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.7)
    
    def _make_shield_hit(self) -> pygame.mixer.Sound:
        """Shield absorbs hit"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Crystalline impact
        freq = 1200
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2
        
        envelope = np.exp(-t * 20)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_shield_break(self) -> pygame.mixer.Sound:
        """Shield depleted"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Shattering glass
        freq = 1500 - 1000 * (t / duration)
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        
        # Noise crackle
        noise = np.random.uniform(-0.4, 0.4, len(t))
        wave += noise * 0.5
        
        envelope = np.exp(-t * 8)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_player_hit(self) -> pygame.mixer.Sound:
        """Player takes damage"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Harsh impact
        freq = 200 + 100 * np.exp(-t * 10)
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        
        # Distortion
        wave = np.clip(wave * 2, -1, 1)
        
        envelope = np.exp(-t * 12)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    # === BOSS SOUNDS ===
    
    def _make_boss_warning(self) -> pygame.mixer.Sound:
        """Boss incoming alert"""
        duration = 1.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Siren
        freq = 440 + 200 * np.sin(2 * np.pi * 2 * t)
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_boss_spawn(self) -> pygame.mixer.Sound:
        """Boss appears"""
        duration = 2.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Deep rumble building
        freq = 40 + 60 * (t / duration)
        rumble = np.sin(2 * np.pi * freq * t) * 0.6
        
        # High-pitched arrival
        arrival_start = int(1.5 * self.sample_rate)
        arrival = np.sin(2 * np.pi * 1200 * t[arrival_start:]) * 0.4
        arrival *= np.exp(-(t[arrival_start:] - t[arrival_start]) * 10)
        
        wave = rumble
        wave[arrival_start:] += arrival
        
        return self._numpy_to_sound(wave * 0.7)
    
    def _make_boss_death(self) -> pygame.mixer.Sound:
        """Boss defeated"""
        duration = 3.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Cascading explosions
        wave = np.zeros_like(t)
        for i in range(5):
            start = int(i * 0.5 * self.sample_rate)
            end = min(start + int(0.5 * self.sample_rate), len(t))
            segment = t[start:end] - t[start]
            
            explosion = np.random.uniform(-0.6, 0.6, len(segment))
            explosion *= np.exp(-segment * 5)
            wave[start:end] += explosion
        
        return self._numpy_to_sound(wave * 0.8)
    
    # === PICKUP SOUNDS ===
    
    def _make_refugee_rescue(self) -> pygame.mixer.Sound:
        """Refugee rescued"""
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Uplifting chime
        notes = [523, 659, 784]  # C, E, G major chord
        wave = np.zeros_like(t)
        for freq in notes:
            wave += np.sin(2 * np.pi * freq * t) * 0.3
        
        envelope = np.exp(-t * 5)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    def _make_powerup(self) -> pygame.mixer.Sound:
        """Generic powerup"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rising arpeggio
        freq = 400 + 400 * (t / duration) ** 2
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        envelope = 1 - np.exp(-t * 10)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_bomb_pickup(self) -> pygame.mixer.Sound:
        """Bomb capsule collected"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Heavy clunk
        freq = 150
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        wave += np.random.uniform(-0.2, 0.2, len(t))
        
        envelope = np.exp(-t * 15)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.6)
    
    # === UI SOUNDS ===
    
    def _make_ui_select(self) -> pygame.mixer.Sound:
        """Menu navigation"""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        freq = 800
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave *= np.exp(-t * 30)
        
        return self._numpy_to_sound(wave * 0.4)
    
    def _make_ui_confirm(self) -> pygame.mixer.Sound:
        """Confirm selection"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Two-tone confirm
        wave = np.sin(2 * np.pi * 600 * t[:len(t)//2]) * 0.4
        wave = np.concatenate([wave, np.sin(2 * np.pi * 800 * t[len(t)//2:]) * 0.4])
        
        envelope = np.exp(-t * 12)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    def _make_ui_cancel(self) -> pygame.mixer.Sound:
        """Cancel/back"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        freq = 400 - 100 * (t / duration)
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave *= np.exp(-t * 15)
        
        return self._numpy_to_sound(wave * 0.4)
    
    def _make_formation_switch(self) -> pygame.mixer.Sound:
        """Formation toggle (Y/Triangle)"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Quick blip
        freq = 1000
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2
        
        envelope = np.exp(-t * 20)
        wave *= envelope
        
        return self._numpy_to_sound(wave * 0.5)
    
    # === UTILITY ===
    
    def _numpy_to_sound(self, wave: np.ndarray) -> pygame.mixer.Sound:
        """Convert numpy array to pygame Sound"""
        wave = np.clip(wave, -1, 1)
        samples = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((samples, samples))
        return pygame.sndarray.make_sound(stereo)
    
    def play(self, sound_name: str, volume: float = 1.0):
        """Play a sound effect"""
        if not self.enabled:
            return
        
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
        else:
            print(f"Sound '{sound_name}' not found")
    
    def play_proximity_kill(self, distance: float):
        """
        Play appropriate kill sound based on distance.
        
        Args:
            distance: Distance from player when enemy died (pixels)
        """
        if distance < 50:
            self.play('kill_pointblank', 1.0)
        elif distance < 100:
            self.play('kill_close', 0.8)
        else:
            self.play('kill_far', 0.6)


if __name__ == "__main__":
    print("=== VERTICAL SHMUP SOUND EFFECTS ===")
    print(f"Total sounds: 30+")
    print()
    print("Categories:")
    print("  Weapons: autocannon, missile, laser, rocket")
    print("  Point-blank: far, close, pointblank")
    print("  Berserk: activate, warning, expire, boost")
    print("  Heat: 25%, 50%, 75% warnings")
    print("  Combat: explosions, shield, player_hit")
    print("  Boss: warning, spawn, death")
    print("  Pickups: refugee, powerup, bomb")
    print("  UI: select, confirm, cancel, formation")
