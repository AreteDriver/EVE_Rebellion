"""Procedural sound effects for Minmatar Rebellion"""
import pygame
import numpy as np
import io


class SoundGenerator:
    """Generate retro-style sound effects procedurally"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.sounds = {}
        self.enabled = True
        
        try:
            pygame.mixer.init(frequency=sample_rate, size=-16, channels=2, buffer=512)
            self._generate_all_sounds()
        except pygame.error as e:
            print(f"Audio not available: {e}")
            print("Sound effects disabled.")
            self.enabled = False
    
    def _generate_all_sounds(self):
        """Generate all game sound effects"""
        # Player weapons
        self.sounds['autocannon'] = self._make_autocannon()
        self.sounds['rocket'] = self._make_rocket()
        
        # Ammo swap
        self.sounds['ammo_switch'] = self._make_ammo_switch()
        
        # Enemy laser
        self.sounds['laser'] = self._make_laser()
        
        # Explosions
        self.sounds['explosion_small'] = self._make_explosion(0.2, 200)
        self.sounds['explosion_medium'] = self._make_explosion(0.4, 150)
        self.sounds['explosion_large'] = self._make_explosion(0.7, 100)
        
        # Pickups
        self.sounds['pickup_refugee'] = self._make_pickup_refugee()
        self.sounds['pickup_powerup'] = self._make_pickup_powerup()
        
        # UI
        self.sounds['menu_select'] = self._make_menu_select()
        self.sounds['purchase'] = self._make_purchase()
        self.sounds['error'] = self._make_error()
        
        # Player damage
        self.sounds['shield_hit'] = self._make_shield_hit()
        self.sounds['armor_hit'] = self._make_armor_hit()
        self.sounds['hull_hit'] = self._make_hull_hit()
        
        # Alerts
        self.sounds['warning'] = self._make_warning()
        self.sounds['wave_start'] = self._make_wave_start()
        self.sounds['stage_complete'] = self._make_stage_complete()
        
        # Wolf upgrade
        self.sounds['upgrade'] = self._make_upgrade()

        # Berserk system sounds
        self.sounds['berserk_extreme'] = self._make_berserk_extreme()
        self.sounds['berserk_close'] = self._make_berserk_close()
        self.sounds['combo'] = self._make_combo()

        # Boss sounds
        self.sounds['boss_entrance'] = self._make_boss_entrance()
        self.sounds['boss_death'] = self._make_boss_death()

        # Alert sounds
        self.sounds['low_health'] = self._make_low_health()
        self.sounds['shield_down'] = self._make_shield_down()

        # Victory/defeat
        self.sounds['victory'] = self._make_victory_fanfare()
        self.sounds['defeat'] = self._make_defeat()
    
    def _numpy_to_sound(self, samples):
        """Convert numpy array to pygame Sound"""
        # Normalize to 16-bit range
        samples = np.clip(samples, -1, 1)
        samples = (samples * 32767).astype(np.int16)
        
        # Make stereo
        stereo = np.column_stack((samples, samples))
        
        # Create sound from buffer
        sound = pygame.sndarray.make_sound(stereo)
        return sound
    
    def _envelope(self, samples, attack=0.01, decay=0.1, sustain=0.7, release=0.2):
        """Apply ADSR envelope to samples"""
        length = len(samples)
        attack_samples = int(attack * length)
        decay_samples = int(decay * length)
        release_samples = int(release * length)
        sustain_samples = length - attack_samples - decay_samples - release_samples
        
        envelope = np.concatenate([
            np.linspace(0, 1, attack_samples),
            np.linspace(1, sustain, decay_samples),
            np.ones(sustain_samples) * sustain,
            np.linspace(sustain, 0, release_samples)
        ])
        
        # Pad or trim to match sample length
        if len(envelope) < length:
            envelope = np.pad(envelope, (0, length - len(envelope)))
        else:
            envelope = envelope[:length]
        
        return samples * envelope
    
    def _make_autocannon(self):
        """Punchy projectile weapon sound"""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Low frequency thump + noise burst
        freq = 150
        wave = np.sin(2 * np.pi * freq * t) * 0.5
        wave += np.sin(2 * np.pi * freq * 2 * t) * 0.3
        
        # Add noise for texture
        noise = np.random.uniform(-0.3, 0.3, len(t))
        wave += noise * np.exp(-t * 40)
        
        # Sharp attack, quick decay
        envelope = np.exp(-t * 50)
        wave *= envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_rocket(self):
        """Whooshing rocket launch"""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rising frequency sweep
        freq = 100 + t * 800
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        
        # Add white noise for thrust
        noise = np.random.uniform(-0.5, 0.5, len(t))
        noise_env = np.exp(-t * 8)
        wave += noise * noise_env * 0.5
        
        # Envelope
        envelope = np.exp(-t * 6) * (1 - np.exp(-t * 50))
        wave *= envelope * 0.5
        
        return self._numpy_to_sound(wave)
    
    def _make_ammo_switch(self):
        """Quick click/beep for ammo change"""
        duration = 0.1
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Two quick tones
        wave = np.sin(2 * np.pi * 800 * t) * 0.3
        wave += np.sin(2 * np.pi * 1200 * t) * 0.2
        
        envelope = np.exp(-t * 40)
        wave *= envelope * 0.3
        
        return self._numpy_to_sound(wave)
    
    def _make_laser(self):
        """Amarr laser beam sound"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # High frequency with slight wobble
        freq = 600 + np.sin(2 * np.pi * 30 * t) * 100
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.15
        
        envelope = np.exp(-t * 20)
        wave *= envelope * 0.25
        
        return self._numpy_to_sound(wave)
    
    def _make_explosion(self, duration, base_freq):
        """Explosion with varying size"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Descending frequency noise burst
        freq = base_freq * np.exp(-t * 5)
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        # Heavy noise component
        noise = np.random.uniform(-1, 1, len(t))
        noise_filtered = np.convolve(noise, np.ones(50)/50, mode='same')
        wave += noise_filtered * np.exp(-t * 8) * 0.6
        
        # Envelope with punch
        envelope = np.exp(-t * (3 / duration)) * (1 - np.exp(-t * 100))
        wave *= envelope * 0.6
        
        return self._numpy_to_sound(wave)
    
    def _make_pickup_refugee(self):
        """Warm, hopeful pickup sound"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Rising arpeggio feel
        wave = np.sin(2 * np.pi * 400 * t) * np.exp(-t * 15) * 0.3
        wave += np.sin(2 * np.pi * 500 * t) * np.exp(-(t - 0.05) * 15) * 0.3
        wave += np.sin(2 * np.pi * 600 * t) * np.exp(-(t - 0.1) * 15) * 0.3
        
        wave *= 0.4
        return self._numpy_to_sound(wave)
    
    def _make_pickup_powerup(self):
        """Bright powerup collection"""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Ascending sweep
        freq = 300 + t * 1500
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.15
        
        envelope = (1 - t / duration) * (1 - np.exp(-t * 50))
        wave *= envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_menu_select(self):
        """UI selection blip"""
        duration = 0.08
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        wave = np.sin(2 * np.pi * 600 * t) * 0.3
        envelope = np.exp(-t * 50)
        wave *= envelope * 0.3
        
        return self._numpy_to_sound(wave)
    
    def _make_purchase(self):
        """Satisfying purchase confirmation"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Two-tone confirmation
        wave = np.zeros_like(t)
        half = len(t) // 2
        wave[:half] = np.sin(2 * np.pi * 400 * t[:half]) * 0.3
        wave[half:] = np.sin(2 * np.pi * 600 * t[half:]) * 0.3
        
        envelope = self._envelope(wave, 0.05, 0.1, 0.8, 0.3)
        wave = envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_error(self):
        """Error/can't afford buzz"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Dissonant low buzz
        wave = np.sin(2 * np.pi * 150 * t) * 0.3
        wave += np.sin(2 * np.pi * 157 * t) * 0.3  # Slight detune for buzz
        
        envelope = np.exp(-t * 10)
        wave *= envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_shield_hit(self):
        """Electric shield impact"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # High frequency crackle
        freq = 1000 + np.random.uniform(-200, 200, len(t))
        wave = np.sin(2 * np.pi * freq * t) * 0.2
        
        # Add crackle noise
        noise = np.random.uniform(-0.3, 0.3, len(t))
        wave += noise * np.exp(-t * 30) * 0.3
        
        envelope = np.exp(-t * 25)
        wave *= envelope * 0.35
        
        return self._numpy_to_sound(wave)
    
    def _make_armor_hit(self):
        """Metallic armor clang"""
        duration = 0.12
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Metallic ring with decay
        wave = np.sin(2 * np.pi * 300 * t) * 0.3
        wave += np.sin(2 * np.pi * 450 * t) * 0.2
        wave += np.sin(2 * np.pi * 600 * t) * 0.1
        
        envelope = np.exp(-t * 35)
        wave *= envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_hull_hit(self):
        """Deep structural damage thud"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Low thump
        wave = np.sin(2 * np.pi * 80 * t) * 0.5
        wave += np.sin(2 * np.pi * 120 * t) * 0.3
        
        # Noise for impact
        noise = np.random.uniform(-0.4, 0.4, len(t))
        wave += noise * np.exp(-t * 20) * 0.3
        
        envelope = np.exp(-t * 15)
        wave *= envelope * 0.5
        
        return self._numpy_to_sound(wave)
    
    def _make_warning(self):
        """Boss/danger warning klaxon"""
        duration = 0.6
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Two-tone alarm
        freq = 400 + 200 * np.sign(np.sin(2 * np.pi * 4 * t))
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        
        envelope = 1 - 0.3 * np.sin(2 * np.pi * 4 * t)
        wave *= envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_wave_start(self):
        """New wave incoming alert"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Quick rising tone
        freq = 300 + t * 500
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        
        envelope = (1 - np.exp(-t * 30)) * np.exp(-t * 5)
        wave *= envelope * 0.35
        
        return self._numpy_to_sound(wave)
    
    def _make_stage_complete(self):
        """Victory fanfare"""
        duration = 0.8
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        wave = np.zeros_like(t)
        notes = [400, 500, 600, 800]  # Rising arpeggio
        note_len = len(t) // len(notes)
        
        for i, freq in enumerate(notes):
            start = i * note_len
            end = start + note_len
            segment = t[start:end] - t[start]
            wave[start:end] = np.sin(2 * np.pi * freq * segment) * 0.3
            wave[start:end] += np.sin(2 * np.pi * freq * 1.5 * segment) * 0.15
        
        envelope = self._envelope(wave, 0.02, 0.1, 0.7, 0.4)
        wave = envelope * 0.4
        
        return self._numpy_to_sound(wave)
    
    def _make_upgrade(self):
        """Wolf upgrade dramatic sound"""
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Building intensity sweep
        freq = 200 + t * 600
        wave = np.sin(2 * np.pi * freq * t) * 0.3
        wave += np.sin(2 * np.pi * freq * 0.5 * t) * 0.2
        
        # Add power noise
        noise = np.random.uniform(-0.3, 0.3, len(t))
        wave += noise * (t / duration) * 0.3
        
        envelope = t / duration * np.exp(-(t - duration) * 3)
        wave *= envelope * 0.5

        return self._numpy_to_sound(wave)

    def _make_berserk_extreme(self):
        """Intense sound for extreme close kill (5x multiplier)"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Aggressive distorted growl with rising pitch
        freq = 150 + t * 400
        wave = np.sin(2 * np.pi * freq * t) * 0.4
        wave += np.sin(2 * np.pi * freq * 2 * t) * 0.3
        wave += np.sin(2 * np.pi * freq * 3 * t) * 0.2

        # Add distortion
        wave = np.tanh(wave * 2) * 0.6

        # Noise burst for impact
        noise = np.random.uniform(-0.4, 0.4, len(t))
        wave += noise * np.exp(-t * 15) * 0.3

        envelope = (1 - np.exp(-t * 50)) * np.exp(-t * 6)
        wave *= envelope * 0.5

        return self._numpy_to_sound(wave)

    def _make_berserk_close(self):
        """Punchy sound for close range kill (3x multiplier)"""
        duration = 0.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Quick rising tone with punch
        freq = 200 + t * 300
        wave = np.sin(2 * np.pi * freq * t) * 0.35
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2

        # Light crunch
        noise = np.random.uniform(-0.2, 0.2, len(t))
        wave += noise * np.exp(-t * 25) * 0.2

        envelope = (1 - np.exp(-t * 60)) * np.exp(-t * 10)
        wave *= envelope * 0.4

        return self._numpy_to_sound(wave)

    def _make_combo(self):
        """Sound for achieving kill combo"""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Quick ascending arpeggio
        wave = np.zeros_like(t)
        notes = [600, 800, 1000, 1200]
        note_len = len(t) // len(notes)

        for i, freq in enumerate(notes):
            start = i * note_len
            end = min(start + note_len, len(t))
            segment = t[start:end] - t[start]
            note_env = np.exp(-segment * 30)
            wave[start:end] = np.sin(2 * np.pi * freq * segment) * note_env * 0.3

        wave *= 0.4
        return self._numpy_to_sound(wave)

    def _make_boss_entrance(self):
        """Dramatic boss entrance sound"""
        duration = 1.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Deep rumble building up
        rumble_freq = 40 + t * 30
        wave = np.sin(2 * np.pi * rumble_freq * t) * 0.3

        # Add ominous drone
        drone = np.sin(2 * np.pi * 110 * t) * 0.2
        drone += np.sin(2 * np.pi * 165 * t) * 0.15  # Perfect fifth

        # Building noise
        noise = np.random.uniform(-0.3, 0.3, len(t))
        noise_env = (t / duration) ** 2
        wave += noise * noise_env * 0.3

        wave += drone

        # Envelope builds then cuts
        envelope = (t / duration) ** 1.5
        wave *= envelope * 0.5

        return self._numpy_to_sound(wave)

    def _make_boss_death(self):
        """Epic boss destruction sound"""
        duration = 1.2
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Massive explosion
        freq = 200 * np.exp(-t * 3)
        wave = np.sin(2 * np.pi * freq * t) * 0.5

        # Heavy noise burst
        noise = np.random.uniform(-1, 1, len(t))
        noise_filtered = np.convolve(noise, np.ones(100)/100, mode='same')
        wave += noise_filtered * np.exp(-t * 4) * 0.6

        # Add some metallic debris sounds
        debris_freq = 800 * np.exp(-t * 5)
        wave += np.sin(2 * np.pi * debris_freq * t) * np.exp(-t * 8) * 0.2

        envelope = (1 - np.exp(-t * 30)) * np.exp(-t * 2)
        wave *= envelope * 0.6

        return self._numpy_to_sound(wave)

    def _make_low_health(self):
        """Warning beep for low health"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Two quick warning beeps
        wave = np.zeros_like(t)
        half = len(t) // 2

        beep1 = np.sin(2 * np.pi * 800 * t[:half]) * np.exp(-t[:half] * 15)
        beep2 = np.sin(2 * np.pi * 600 * t[half:]) * np.exp(-(t[half:] - t[half]) * 15)

        wave[:half] = beep1 * 0.3
        wave[half:] = beep2 * 0.3

        return self._numpy_to_sound(wave)

    def _make_shield_down(self):
        """Shield depleted warning"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Descending electric crackle
        freq = 1200 - t * 800
        wave = np.sin(2 * np.pi * freq * t) * 0.3

        # Electric noise
        noise = np.random.uniform(-0.4, 0.4, len(t))
        wave += noise * np.exp(-t * 10) * 0.3

        envelope = np.exp(-t * 8)
        wave *= envelope * 0.4

        return self._numpy_to_sound(wave)

    def _make_victory_fanfare(self):
        """Epic victory sound"""
        duration = 1.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        wave = np.zeros_like(t)
        # Triumphant chord progression
        notes = [(400, 0.0), (500, 0.1), (600, 0.2), (800, 0.4), (1000, 0.6)]

        for freq, start_time in notes:
            start_idx = int(start_time * self.sample_rate)
            if start_idx < len(t):
                segment_t = t[start_idx:] - t[start_idx]
                note = np.sin(2 * np.pi * freq * segment_t) * 0.25
                note += np.sin(2 * np.pi * freq * 1.5 * segment_t) * 0.12
                note *= np.exp(-segment_t * 2)
                wave[start_idx:start_idx + len(note)] += note[:len(wave) - start_idx]

        wave = np.clip(wave, -1, 1) * 0.5
        return self._numpy_to_sound(wave)

    def _make_defeat(self):
        """Game over sound"""
        duration = 1.0
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Descending mournful tones
        wave = np.zeros_like(t)
        notes = [(500, 0.0), (400, 0.25), (300, 0.5), (200, 0.75)]

        for freq, start_time in notes:
            start_idx = int(start_time * self.sample_rate)
            if start_idx < len(t):
                segment_t = t[start_idx:] - t[start_idx]
                note = np.sin(2 * np.pi * freq * segment_t) * 0.3
                note *= np.exp(-segment_t * 4)
                end_idx = min(start_idx + len(note), len(wave))
                wave[start_idx:end_idx] += note[:end_idx - start_idx]

        wave = np.clip(wave, -1, 1) * 0.4
        return self._numpy_to_sound(wave)

    def play(self, sound_name, volume=1.0):
        """Play a sound effect"""
        if not self.enabled:
            return
        if sound_name in self.sounds:
            sound = self.sounds[sound_name]
            sound.set_volume(volume)
            sound.play()
    
    def get_sound(self, sound_name):
        """Get a sound object for custom handling"""
        if not self.enabled:
            return None
        return self.sounds.get(sound_name)


class MusicGenerator:
    """Simple procedural background music"""
    
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.playing = False
        self.enabled = pygame.mixer.get_init() is not None
    
    def generate_ambient_loop(self, duration=30.0):
        """Generate ambient space music loop"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Deep drone bass
        bass = np.sin(2 * np.pi * 55 * t) * 0.15
        bass += np.sin(2 * np.pi * 82.5 * t) * 0.1
        
        # Slow pad with filter sweep
        pad_freq = 220 + 50 * np.sin(2 * np.pi * 0.05 * t)
        pad = np.sin(2 * np.pi * pad_freq * t) * 0.08
        pad += np.sin(2 * np.pi * pad_freq * 1.5 * t) * 0.05
        
        # Subtle high shimmer
        shimmer = np.sin(2 * np.pi * 880 * t) * 0.02
        shimmer *= 0.5 + 0.5 * np.sin(2 * np.pi * 0.2 * t)
        
        wave = bass + pad + shimmer
        
        # Normalize
        wave = wave / np.max(np.abs(wave)) * 0.3
        
        return wave
    
    def start_music(self):
        """Start background music"""
        if not self.enabled or self.playing:
            return
        
        try:
            # Generate and save to temp file
            wave = self.generate_ambient_loop(30.0)
            wave = np.clip(wave, -1, 1)
            samples = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((samples, samples))
            
            # Save as WAV in memory
            import wave as wave_module
            buffer = io.BytesIO()
            with wave_module.open(buffer, 'wb') as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(stereo.tobytes())
            
            buffer.seek(0)
            pygame.mixer.music.load(buffer, 'wav')
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # Loop forever
            self.playing = True
        except Exception as e:
            print(f"Could not start music: {e}")
            self.enabled = False
    
    def stop_music(self):
        """Stop background music"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except:
            pass
        self.playing = False
    
    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(volume)
        except:
            pass


# Global sound manager instance
_sound_manager = None
_music_manager = None


def get_sound_manager():
    """Get or create the global sound manager"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundGenerator()
    return _sound_manager


def get_music_manager():
    """Get or create the global music manager"""
    global _music_manager
    if _music_manager is None:
        _music_manager = MusicGenerator()
    return _music_manager


def play_sound(sound_name, volume=1.0):
    """Convenience function to play a sound"""
    get_sound_manager().play(sound_name, volume)
