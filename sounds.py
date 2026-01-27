"""Procedural sound effects for Minmatar Rebellion"""

import io

import numpy as np
import pygame


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
        self.sounds["autocannon"] = self._make_autocannon()
        self.sounds["rocket"] = self._make_rocket()

        # Ammo swap
        self.sounds["ammo_switch"] = self._make_ammo_switch()

        # Enemy laser
        self.sounds["laser"] = self._make_laser()

        # Explosions
        self.sounds["explosion_small"] = self._make_explosion(0.2, 200)
        self.sounds["explosion_medium"] = self._make_explosion(0.4, 150)
        self.sounds["explosion_large"] = self._make_explosion(0.7, 100)

        # Pickups
        self.sounds["pickup_refugee"] = self._make_pickup_refugee()
        self.sounds["pickup_powerup"] = self._make_pickup_powerup()

        # UI
        self.sounds["menu_select"] = self._make_menu_select()
        self.sounds["purchase"] = self._make_purchase()
        self.sounds["error"] = self._make_error()

        # Player damage
        self.sounds["shield_hit"] = self._make_shield_hit()
        self.sounds["armor_hit"] = self._make_armor_hit()
        self.sounds["hull_hit"] = self._make_hull_hit()

        # Alerts
        self.sounds["warning"] = self._make_warning()
        self.sounds["wave_start"] = self._make_wave_start()
        self.sounds["stage_complete"] = self._make_stage_complete()

        # Wolf upgrade
        self.sounds["upgrade"] = self._make_upgrade()

        # Berserk system sounds
        self.sounds["berserk_extreme"] = self._make_berserk_extreme()
        self.sounds["berserk_close"] = self._make_berserk_close()
        self.sounds["combo"] = self._make_combo()

        # Boss sounds
        self.sounds["boss_entrance"] = self._make_boss_entrance()
        self.sounds["boss_death"] = self._make_boss_death()
        self.sounds["boss_attack"] = self._make_boss_attack()
        self.sounds["boss_summon"] = self._make_boss_summon()
        self.sounds["bomb"] = self._make_bomb()

        # Alert sounds
        self.sounds["low_health"] = self._make_low_health()
        self.sounds["shield_down"] = self._make_shield_down()

        # Victory/defeat
        self.sounds["victory"] = self._make_victory_fanfare()
        self.sounds["defeat"] = self._make_defeat()

        # Unique powerup pickup sounds
        self.sounds["powerup_nanite"] = self._make_powerup_nanite()
        self.sounds["powerup_capacitor"] = self._make_powerup_capacitor()
        self.sounds["powerup_overdrive"] = self._make_powerup_overdrive()
        self.sounds["powerup_shield"] = self._make_powerup_shield()
        self.sounds["powerup_damage"] = self._make_powerup_damage()
        self.sounds["powerup_rapid"] = self._make_powerup_rapid()
        self.sounds["powerup_bomb"] = self._make_powerup_bomb()
        self.sounds["powerup_magnet"] = self._make_powerup_magnet()
        self.sounds["powerup_invuln"] = self._make_powerup_invuln()

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

        envelope = np.concatenate(
            [
                np.linspace(0, 1, attack_samples),
                np.linspace(1, sustain, decay_samples),
                np.ones(sustain_samples) * sustain,
                np.linspace(sustain, 0, release_samples),
            ]
        )

        # Pad or trim to match sample length
        if len(envelope) < length:
            envelope = np.pad(envelope, (0, length - len(envelope)))
        else:
            envelope = envelope[:length]

        return samples * envelope

    def _make_autocannon(self):
        """Chunky Minmatar autocannon - heavy, industrial, satisfying"""
        duration = 0.12
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Deep thump base (industrial Minmatar feel)
        freq = 100
        wave = np.sin(2 * np.pi * freq * t) * 0.6
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.4

        # Mid punch for presence
        wave += np.sin(2 * np.pi * 250 * t) * np.exp(-t * 60) * 0.5

        # High frequency crack (shell casing)
        crack = np.sin(2 * np.pi * 800 * t) * np.exp(-t * 100) * 0.3

        # Heavy mechanical noise burst
        noise = np.random.uniform(-0.5, 0.5, len(t))
        noise_filtered = np.convolve(noise, np.ones(20) / 20, mode="same")
        wave += noise_filtered * np.exp(-t * 35) * 0.4
        wave += crack

        # Punchy envelope - hard attack, quick decay
        envelope = np.exp(-t * 40) * (1 - np.exp(-t * 300))
        wave *= envelope * 0.55

        return self._numpy_to_sound(wave)

    def _make_rocket(self):
        """Aggressive rocket launch - ignition burst + whoosh"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Ignition burst (initial pop)
        ignition = np.sin(2 * np.pi * 200 * t) * np.exp(-t * 80) * 0.5
        ignition += np.random.uniform(-0.4, 0.4, len(t)) * np.exp(-t * 60) * 0.4

        # Rising frequency whoosh (rocket accelerating away)
        freq = 150 + t * 1000
        whoosh = np.sin(2 * np.pi * freq * t) * 0.35

        # Thrust noise (white noise filtered)
        noise = np.random.uniform(-0.6, 0.6, len(t))
        noise_filtered = np.convolve(noise, np.ones(30) / 30, mode="same")
        thrust = noise_filtered * np.exp(-t * 5) * 0.45

        wave = ignition + whoosh + thrust

        # Envelope - sharp attack, gradual fade
        envelope = (1 - np.exp(-t * 100)) * np.exp(-t * 5)
        wave *= envelope * 0.55

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
        """Amarr golden laser - crystalline, pure, holy-sounding"""
        duration = 0.18
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Pure crystalline tone (golden beam)
        freq = 800
        wave = np.sin(2 * np.pi * freq * t) * 0.35
        wave += np.sin(2 * np.pi * freq * 1.5 * t) * 0.2  # Perfect fifth
        wave += np.sin(2 * np.pi * freq * 2 * t) * 0.15  # Octave

        # Slight shimmer/pulse
        shimmer = 1 + 0.15 * np.sin(2 * np.pi * 50 * t)
        wave *= shimmer

        # Energy buildup at start
        buildup = np.sin(2 * np.pi * 1600 * t) * np.exp(-t * 40) * 0.2

        wave += buildup

        # Clean envelope
        envelope = (1 - np.exp(-t * 100)) * np.exp(-t * 15)
        wave *= envelope * 0.3

        return self._numpy_to_sound(wave)

    def _make_explosion(self, duration, base_freq):
        """Explosion with varying size"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Descending frequency noise burst
        freq = base_freq * np.exp(-t * 5)
        wave = np.sin(2 * np.pi * freq * t) * 0.4

        # Heavy noise component
        noise = np.random.uniform(-1, 1, len(t))
        noise_filtered = np.convolve(noise, np.ones(50) / 50, mode="same")
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
        noise_filtered = np.convolve(noise, np.ones(100) / 100, mode="same")
        wave += noise_filtered * np.exp(-t * 4) * 0.6

        # Add some metallic debris sounds
        debris_freq = 800 * np.exp(-t * 5)
        wave += np.sin(2 * np.pi * debris_freq * t) * np.exp(-t * 8) * 0.2

        envelope = (1 - np.exp(-t * 30)) * np.exp(-t * 2)
        wave *= envelope * 0.6

        return self._numpy_to_sound(wave)

    def _make_boss_attack(self):
        """Heavy boss special attack sound"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Deep bass whoosh
        freq = 150 + 200 * np.exp(-t * 8)
        wave = np.sin(2 * np.pi * freq * t) * 0.4

        # Add energy buildup
        buildup = np.sin(2 * np.pi * 600 * t) * t / duration * 0.3
        wave += buildup * np.exp(-t * 5)

        # Burst at end
        burst_t = t - 0.2
        burst_mask = burst_t > 0
        wave[burst_mask] += np.sin(2 * np.pi * 100 * burst_t[burst_mask]) * 0.4

        envelope = np.exp(-t * 4) * (1 - np.exp(-t * 30))
        wave *= envelope * 0.5

        return self._numpy_to_sound(wave)

    def _make_boss_summon(self):
        """Boss summoning minions sound"""
        duration = 0.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Warping effect
        freq = 300 + 400 * np.sin(t * 20) * np.exp(-t * 4)
        wave = np.sin(2 * np.pi * freq * t) * 0.3

        # Portal opening sound
        wave += np.sin(2 * np.pi * 200 * t) * (1 - np.exp(-t * 10)) * 0.3

        # Shimmer
        shimmer = np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 8) * 0.15
        wave += shimmer

        envelope = (1 - np.exp(-t * 15)) * np.exp(-t * 3)
        wave *= envelope * 0.5

        return self._numpy_to_sound(wave)

    def _make_bomb(self):
        """Massive screen-clearing explosion"""
        duration = 0.8
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Massive low frequency boom
        freq = 60 + 100 * np.exp(-t * 5)
        wave = np.sin(2 * np.pi * freq * t) * 0.6

        # Heavy noise burst
        noise = np.random.uniform(-1, 1, len(t))
        noise_filtered = np.convolve(noise, np.ones(150) / 150, mode="same")
        wave += noise_filtered * np.exp(-t * 3) * 0.5

        # High frequency sizzle
        sizzle = np.sin(2 * np.pi * 2000 * t) * np.exp(-t * 10) * 0.2
        wave += sizzle

        # Shockwave whoosh
        whoosh_freq = 500 * np.exp(-t * 4)
        wave += np.sin(2 * np.pi * whoosh_freq * t) * np.exp(-t * 5) * 0.3

        envelope = (1 - np.exp(-t * 50)) * np.exp(-t * 2.5)
        wave *= envelope * 0.7

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
                wave[start_idx : start_idx + len(note)] += note[: len(wave) - start_idx]

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
                wave[start_idx:end_idx] += note[: end_idx - start_idx]

        wave = np.clip(wave, -1, 1) * 0.4
        return self._numpy_to_sound(wave)

    def _make_powerup_nanite(self):
        """Healing/regeneration sound - warm, organic bubbling"""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Warm ascending tones
        wave = np.sin(2 * np.pi * 300 * t) * np.exp(-t * 8) * 0.3
        wave += np.sin(2 * np.pi * 400 * t) * np.exp(-(t - 0.08) * 8) * 0.25
        wave += np.sin(2 * np.pi * 500 * t) * np.exp(-(t - 0.16) * 8) * 0.2

        # Soft bubbling texture
        bubble = np.sin(2 * np.pi * 800 * t) * np.sin(2 * np.pi * 15 * t) * 0.1
        wave += bubble * np.exp(-t * 6)

        wave *= 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_capacitor(self):
        """Rocket reload - mechanical click and charge"""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Mechanical click
        click = np.random.uniform(-1, 1, len(t)) * np.exp(-t * 80) * 0.4

        # Charging whine
        charge_freq = 200 + t * 600
        charge = np.sin(2 * np.pi * charge_freq * t) * 0.3
        charge *= (1 - np.exp(-t * 30)) * np.exp(-t * 4)

        wave = click + charge
        wave *= 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_overdrive(self):
        """Speed boost - accelerating whoosh"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Accelerating sweep
        freq = 150 + t * 1200
        wave = np.sin(2 * np.pi * freq * t) * 0.3

        # Wind noise
        noise = np.random.uniform(-0.3, 0.3, len(t))
        noise_filtered = np.convolve(noise, np.ones(80) / 80, mode="same")
        wave += noise_filtered * 0.4

        envelope = (1 - np.exp(-t * 40)) * (1 - t / duration)
        wave *= envelope * 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_shield(self):
        """Shield boost - electric shimmer"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Electric shimmer
        wave = np.sin(2 * np.pi * 600 * t) * 0.25
        wave += np.sin(2 * np.pi * 900 * t) * 0.15
        wave += np.sin(2 * np.pi * 1200 * t) * 0.1

        # Sparkle modulation
        sparkle = 0.7 + 0.3 * np.sin(2 * np.pi * 40 * t)
        wave *= sparkle

        envelope = np.exp(-t * 6) * (1 - np.exp(-t * 60))
        wave *= envelope * 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_damage(self):
        """Damage amplifier - powerful aggressive charge"""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Deep powerful tone
        wave = np.sin(2 * np.pi * 120 * t) * 0.4
        wave += np.sin(2 * np.pi * 180 * t) * 0.3

        # Aggressive overtones
        wave += np.sin(2 * np.pi * 360 * t) * 0.2
        wave += np.sin(2 * np.pi * 540 * t) * 0.1

        # Punch
        punch = np.exp(-t * 25) * 0.5
        wave *= 0.5 + punch

        envelope = (1 - np.exp(-t * 50)) * np.exp(-t * 5)
        wave *= envelope * 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_rapid(self):
        """Rapid fire - fast clicking/whirring"""
        duration = 0.25
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Rapid clicks (machine gun like)
        click_freq = 30  # clicks per second
        clicks = np.sin(2 * np.pi * click_freq * t)
        clicks = (clicks > 0.8).astype(float) * 0.5

        # Whirring undertone
        whir = np.sin(2 * np.pi * 400 * t) * 0.2
        whir += np.sin(2 * np.pi * 800 * t) * 0.1

        wave = clicks + whir
        envelope = (1 - np.exp(-t * 40)) * np.exp(-t * 6)
        wave *= envelope * 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_bomb(self):
        """Bomb charge - heavy mechanical loading"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Heavy thunk
        thunk = np.sin(2 * np.pi * 80 * t) * np.exp(-t * 20) * 0.5

        # Mechanical slide
        slide_freq = 300 - t * 200
        slide = np.sin(2 * np.pi * slide_freq * t) * 0.3
        slide *= np.exp(-t * 8)

        # Lock click
        click_start = int(0.2 * self.sample_rate * duration)
        click = np.zeros_like(t)
        click[click_start:] = np.random.uniform(-0.4, 0.4, len(t) - click_start)
        click *= np.exp(-np.maximum(0, t - 0.06) * 50)

        wave = thunk + slide + click
        wave *= 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_magnet(self):
        """Tractor beam - humming pull"""
        duration = 0.35
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Humming base
        hum = np.sin(2 * np.pi * 150 * t) * 0.3
        hum += np.sin(2 * np.pi * 300 * t) * 0.2

        # Wobble effect (tractor beam pulsing)
        wobble = 0.7 + 0.3 * np.sin(2 * np.pi * 8 * t)
        hum *= wobble

        # High frequency attraction whine
        pull_freq = 800 + 200 * np.sin(2 * np.pi * 4 * t)
        pull = np.sin(2 * np.pi * pull_freq * t) * 0.15

        wave = hum + pull
        envelope = (1 - np.exp(-t * 30)) * np.exp(-t * 4)
        wave *= envelope * 0.5
        return self._numpy_to_sound(wave)

    def _make_powerup_invuln(self):
        """Invulnerability/hardener - solid protective golden tone"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Majestic chord (golden/powerful feel)
        wave = np.sin(2 * np.pi * 440 * t) * 0.25  # A
        wave += np.sin(2 * np.pi * 550 * t) * 0.2  # C#
        wave += np.sin(2 * np.pi * 660 * t) * 0.2  # E
        wave += np.sin(2 * np.pi * 880 * t) * 0.15  # A octave

        # Shimmering effect
        shimmer = 0.8 + 0.2 * np.sin(2 * np.pi * 12 * t)
        wave *= shimmer

        # Strong attack, sustained release
        envelope = (1 - np.exp(-t * 60)) * np.exp(-t * 3)
        wave *= envelope * 0.5
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

    def set_volume(self, volume):
        """Set the master volume for all sound effects (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        # Apply to all cached sounds
        for sound in self.sounds.values():
            if sound:
                try:
                    sound.set_volume(self.master_volume)
                except Exception:
                    pass


class MusicGenerator:
    """Vaporwave procedural background music with sick bass lines"""

    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.playing = False
        self.enabled = pygame.mixer.get_init() is not None
        self.current_stage = 0

    def _lowpass_filter(self, wave, cutoff_ratio=0.1):
        """Simple lowpass filter for that lo-fi vaporwave sound"""
        # Moving average filter
        window_size = max(1, int(1.0 / cutoff_ratio))
        kernel = np.ones(window_size) / window_size
        return np.convolve(wave, kernel, mode="same")

    def _add_reverb(self, wave, decay=0.4, delay_samples=None):
        """Add reverb/echo effect"""
        if delay_samples is None:
            delay_samples = int(self.sample_rate * 0.08)
        result = wave.copy()
        for i in range(1, 6):
            delayed = np.zeros_like(wave)
            shift = delay_samples * i
            if shift < len(wave):
                delayed[shift:] = wave[:-shift] * (decay**i)
                result += delayed
        return result / 2

    def _generate_bass_line(self, t, bpm, pattern, root_note=41.2):
        """Generate groovy bass line with sub-bass

        root_note: frequency in Hz (default E1 = 41.2 Hz)
        pattern: list of (note_offset_semitones, duration_beats)
        """
        beat_duration = 60.0 / bpm
        bass = np.zeros_like(t)

        # Note frequencies relative to root
        def note_freq(semitones):
            return root_note * (2 ** (semitones / 12.0))

        current_time = 0
        pattern_idx = 0

        while current_time < t[-1]:
            note_semitones, duration_beats = pattern[pattern_idx % len(pattern)]
            note_duration = duration_beats * beat_duration
            freq = note_freq(note_semitones)

            # Find samples for this note
            mask = (t >= current_time) & (t < current_time + note_duration)
            local_t = t[mask] - current_time

            if len(local_t) > 0:
                # Sub-bass (pure sine, very low)
                sub = np.sin(2 * np.pi * freq * local_t) * 0.5

                # Mid-bass with slight saturation for growl
                mid = np.sin(2 * np.pi * freq * 2 * local_t) * 0.3
                mid = np.tanh(mid * 2) * 0.5  # Soft saturation

                # Upper harmonics for punch
                upper = np.sin(2 * np.pi * freq * 3 * local_t) * 0.15
                upper += np.sin(2 * np.pi * freq * 4 * local_t) * 0.08

                # Envelope - punchy attack, smooth sustain
                env_attack = np.minimum(local_t / 0.02, 1.0)
                env_release = np.maximum(0, 1 - (local_t - note_duration + 0.1) / 0.1)
                envelope = env_attack * env_release

                bass[mask] = (sub + mid + upper) * envelope

            current_time += note_duration
            pattern_idx += 1

        return bass

    def _generate_synth_pad(self, t, chord_freqs, detune=0.02):
        """Generate lush detuned synth pad (classic vaporwave)"""
        pad = np.zeros_like(t)

        for freq in chord_freqs:
            # Multiple detuned oscillators per note
            for detune_amt in [-detune, 0, detune]:
                f = freq * (1 + detune_amt)
                # Saw wave approximation (sum of harmonics)
                for h in range(1, 6):
                    pad += np.sin(2 * np.pi * f * h * t) / h * 0.08

        # Slow filter sweep for movement
        sweep = 0.3 + 0.2 * np.sin(2 * np.pi * 0.03 * t)
        pad = self._lowpass_filter(pad, sweep.mean())

        return pad * 0.4

    def _generate_arp(self, t, bpm, notes, gate=0.5):
        """Generate arpeggiated synth line"""
        beat_duration = 60.0 / bpm
        note_duration = beat_duration * gate
        arp = np.zeros_like(t)

        current_time = 0
        note_idx = 0

        while current_time < t[-1]:
            freq = notes[note_idx % len(notes)]
            mask = (t >= current_time) & (t < current_time + note_duration)
            local_t = t[mask] - current_time

            if len(local_t) > 0:
                # Square-ish wave
                wave = np.sin(2 * np.pi * freq * local_t)
                wave += np.sin(2 * np.pi * freq * 2 * local_t) * 0.5
                wave = np.tanh(wave)

                # Sharp envelope
                env = np.exp(-local_t * 8)
                arp[mask] = wave * env * 0.15

            current_time += beat_duration / 2  # 8th notes
            note_idx += 1

        return arp

    def generate_stage_music(self, stage=0, duration=45.0):
        """Generate vaporwave music for specific stage"""
        t = np.linspace(0, duration, int(self.sample_rate * duration))

        # Stage-specific settings
        if stage == 0:  # Asteroid Belt Escape - chill intro
            bpm = 75
            root = 41.2  # E1
            bass_pattern = [
                (0, 2),
                (0, 1),
                (5, 1),  # E, E, A
                (7, 2),
                (5, 1),
                (3, 1),  # B, A, G
                (0, 2),
                (0, 1),
                (-2, 1),  # E, E, D
                (0, 2),
                (3, 1),
                (5, 1),  # E, G, A
            ]
            chord = [164.81, 196.00, 246.94, 329.63]  # E minor 7
            arp_notes = [329.63, 392.00, 493.88, 659.26]

        elif stage == 1:  # Amarr Patrol - tension building
            bpm = 82
            root = 36.71  # D1
            bass_pattern = [
                (0, 1),
                (0, 0.5),
                (12, 0.5),
                (10, 1),
                (7, 1),
                (5, 1),
                (5, 0.5),
                (7, 0.5),
                (5, 1),
                (3, 1),
                (0, 2),
                (0, 1),
                (5, 1),
                (7, 1),
                (10, 1),
                (12, 1),
                (10, 1),
            ]
            chord = [146.83, 174.61, 220.00, 293.66]  # D minor 7
            arp_notes = [293.66, 349.23, 440.00, 523.25]

        elif stage == 2:  # Slave Colony Liberation - emotional
            bpm = 70
            root = 43.65  # F1
            bass_pattern = [
                (0, 2),
                (0, 1),
                (0, 0.5),
                (3, 0.5),
                (5, 2),
                (3, 1),
                (0, 1),
                (-2, 2),
                (0, 1),
                (3, 1),
                (5, 1),
                (3, 1),
                (0, 2),
            ]
            chord = [174.61, 207.65, 261.63, 349.23]  # F major 7
            arp_notes = [523.25, 659.26, 783.99, 1046.50]

        elif stage == 3:  # Gate Assault - intense
            bpm = 90
            root = 32.70  # C1
            bass_pattern = [
                (0, 0.5),
                (0, 0.5),
                (12, 0.5),
                (0, 0.5),
                (10, 0.5),
                (0, 0.5),
                (7, 0.5),
                (0, 0.5),
                (5, 1),
                (7, 1),
                (10, 1),
                (12, 1),
                (0, 0.5),
                (0, 0.5),
                (0, 0.5),
                (15, 0.5),
                (12, 1),
                (10, 1),
            ]
            chord = [130.81, 155.56, 196.00, 261.63]  # C minor 7
            arp_notes = [261.63, 311.13, 392.00, 466.16, 523.25]

        else:  # Final Push / Boss - epic
            bpm = 95
            root = 27.50  # A0 - super deep
            bass_pattern = [
                (0, 1),
                (12, 0.5),
                (0, 0.5),
                (7, 1),
                (5, 1),
                (0, 0.5),
                (0, 0.5),
                (12, 0.5),
                (10, 0.5),
                (7, 1),
                (5, 1),
                (3, 1),
                (5, 1),
                (7, 2),
                (0, 0.5),
                (12, 0.5),
                (0, 0.5),
                (12, 0.5),
                (10, 1),
                (7, 1),
            ]
            chord = [110.00, 130.81, 164.81, 220.00]  # A minor 7
            arp_notes = [440.00, 523.25, 659.26, 783.99, 880.00]

        # Generate layers
        bass = self._generate_bass_line(t, bpm, bass_pattern, root)
        pad = self._generate_synth_pad(t, chord)
        arp = self._generate_arp(t, bpm, arp_notes)

        # Add subtle kick drum on beats
        kick = np.zeros_like(t)
        beat_duration = 60.0 / bpm
        for beat_time in np.arange(0, duration, beat_duration):
            mask = (t >= beat_time) & (t < beat_time + 0.15)
            local_t = t[mask] - beat_time
            if len(local_t) > 0:
                # Kick: pitch drop + noise
                kick_freq = 150 * np.exp(-local_t * 30) + 40
                kick_wave = np.sin(2 * np.pi * kick_freq * local_t)
                kick_env = np.exp(-local_t * 15)
                kick[mask] += kick_wave * kick_env * 0.4

        # Hi-hat pattern (offbeat for groove)
        hihat = np.zeros_like(t)
        for beat_time in np.arange(beat_duration / 2, duration, beat_duration):
            mask = (t >= beat_time) & (t < beat_time + 0.05)
            local_t = t[mask] - beat_time
            if len(local_t) > 3:  # Need enough samples for filter
                noise = np.random.uniform(-1, 1, len(local_t))
                noise = self._lowpass_filter(noise, 0.3)[: len(local_t)]
                hat_env = np.exp(-local_t * 40)
                hihat[mask] += noise * hat_env * 0.08

        # Mix everything
        mix = bass * 0.45 + pad * 0.25 + arp * 0.15 + kick * 0.35 + hihat * 0.1

        # Add reverb for space
        mix = self._add_reverb(mix, decay=0.35)

        # Slight tape wobble effect (vaporwave aesthetic)
        wobble = 1 + 0.002 * np.sin(2 * np.pi * 0.5 * t)
        # Apply wobble by resampling would be complex, so just modulate amplitude slightly
        mix = mix * wobble

        # Final compression and limiting
        mix = np.tanh(mix * 1.5) * 0.7

        # Normalize
        max_val = np.max(np.abs(mix))
        if max_val > 0:
            mix = mix / max_val * 0.85

        return mix

    def start_music(self, stage=0):
        """Start background music for specific stage"""
        if not self.enabled or self.playing:
            return

        self.current_stage = stage

        try:
            # Generate stage-specific music
            wave = self.generate_stage_music(stage, 45.0)
            wave = np.clip(wave, -1, 1)
            samples = (wave * 32767).astype(np.int16)
            stereo = np.column_stack((samples, samples))

            # Save as WAV in memory
            import wave as wave_module

            buffer = io.BytesIO()
            with wave_module.open(buffer, "wb") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes(stereo.tobytes())

            buffer.seek(0)
            pygame.mixer.music.load(buffer, "wav")
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)  # Loop forever
            self.playing = True
        except Exception as e:
            print(f"Could not start music: {e}")
            self.enabled = False

    def change_stage(self, stage):
        """Change to music for a different stage"""
        if stage != self.current_stage:
            self.stop_music()
            self.start_music(stage)

    def stop_music(self):
        """Stop background music"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.playing = False

    def set_volume(self, volume):
        """Set music volume (0.0 to 1.0)"""
        if not self.enabled:
            return
        try:
            pygame.mixer.music.set_volume(volume)
        except Exception:
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
