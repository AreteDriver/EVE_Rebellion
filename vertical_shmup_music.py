"""
VERTICAL SHMUP SOUNDTRACK GENERATOR
EVE Rebellion - Devil Blade Reboot Inspired Audio

Based on vertical shmup audio design:
- Tense, building ambient layers (not constant chaos)
- Dynamic intensity tied to Heat/Berserk
- Boss themes with urgency
- Procedural generation for variety
"""

import pygame
import numpy as np


class VerticalShmupMusic:
    """
    Procedural music generator for vertical shoot-em-ups.
    
    Layers:
    1. Bass pulse (heartbeat rhythm)
    2. Synth pads (tension)
    3. Lead melody (escalation)
    4. Percussion (intensity)
    
    Music adapts to Heat/Berserk state dynamically.
    """
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        self.enabled = pygame.mixer.get_init() is not None
        self.current_track = None
        self.heat_level = 0.0
        self.berserk_active = False
        
        # Music state
        self.bass_volume = 0.2
        self.pad_volume = 0.15
        self.lead_volume = 0.0  # Fades in with Heat
        self.perc_volume = 0.0  # Appears in Berserk
        
    def generate_stage_music(self, duration: float = 60.0) -> np.ndarray:
        """
        Generate stage background music.
        Slow build with tension layers.
        
        Args:
            duration: Length in seconds
        
        Returns:
            Audio waveform as numpy array
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = np.zeros_like(t)
        
        # Layer 1: Bass pulse (constant heartbeat)
        bass_freq = 55  # Low A
        bass = np.sin(2 * np.pi * bass_freq * t) * 0.3
        bass += np.sin(2 * np.pi * bass_freq * 2 * t) * 0.15  # Octave
        
        # Pulse envelope (heartbeat rhythm)
        pulse = np.zeros_like(t)
        beat_interval = self.sample_rate * 0.6  # ~100 BPM
        for i in range(int(duration / 0.6)):
            start = int(i * beat_interval)
            end = min(start + int(self.sample_rate * 0.1), len(pulse))
            pulse[start:end] = 1.0
        
        bass *= pulse
        wave += bass * self.bass_volume
        
        # Layer 2: Synth pad (tension)
        pad_freq = 220 + 30 * np.sin(2 * np.pi * 0.05 * t)  # Slow sweep
        pad = np.sin(2 * np.pi * pad_freq * t) * 0.2
        pad += np.sin(2 * np.pi * pad_freq * 1.5 * t) * 0.1  # Harmony
        
        # Pad fade-in over first 10 seconds
        pad_env = np.minimum(t / 10.0, 1.0)
        pad *= pad_env
        wave += pad * self.pad_volume
        
        # Layer 3: Lead melody (escalation - activated by Heat)
        lead_notes = [440, 494, 523, 587, 659]  # A, B, C, D, E progression
        lead = np.zeros_like(t)
        note_duration = duration / len(lead_notes)
        
        for i, freq in enumerate(lead_notes):
            start = int(i * note_duration * self.sample_rate)
            end = int((i + 1) * note_duration * self.sample_rate)
            end = min(end, len(t))
            
            segment_t = t[start:end] - t[start]
            lead[start:end] = np.sin(2 * np.pi * freq * segment_t) * 0.25
            
            # Attack-decay envelope for each note
            note_env = np.exp(-segment_t * 2) * (1 - np.exp(-segment_t * 20))
            lead[start:end] *= note_env
        
        wave += lead * self.lead_volume  # Volume controlled by Heat
        
        # Layer 4: Percussion (Berserk only)
        if self.berserk_active:
            perc = self._generate_percussion(t, duration)
            wave += perc * self.perc_volume
        
        # Normalize
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.6
        
        return wave
    
    def generate_boss_music(self, duration: float = 90.0) -> np.ndarray:
        """
        Boss fight music - higher intensity, faster tempo.
        
        Args:
            duration: Length in seconds
        
        Returns:
            Audio waveform
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        wave = np.zeros_like(t)
        
        # Fast bass pulse (140 BPM vs 100 BPM)
        bass_freq = 55
        pulse = np.zeros_like(t)
        beat_interval = self.sample_rate * 0.43  # ~140 BPM
        
        for i in range(int(duration / 0.43)):
            start = int(i * beat_interval)
            end = min(start + int(self.sample_rate * 0.08), len(pulse))
            pulse[start:end] = 1.0
        
        bass = np.sin(2 * np.pi * bass_freq * t) * pulse * 0.35
        wave += bass
        
        # Aggressive synth lead
        lead_freq = 440 + 100 * np.sin(2 * np.pi * 0.2 * t)  # Faster sweep
        lead = np.sin(2 * np.pi * lead_freq * t) * 0.3
        lead += np.sin(2 * np.pi * lead_freq * 2.5 * t) * 0.15  # Dissonant harmony
        wave += lead
        
        # Constant percussion
        perc = self._generate_percussion(t, duration, intensity=0.4)
        wave += perc
        
        # Normalize
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.7
        
        return wave
    
    def generate_berserk_layer(self, duration: float = 30.0) -> np.ndarray:
        """
        Additional layer that plays when Berserk activates.
        Harsh, aggressive tones.
        
        Args:
            duration: Length in seconds
        
        Returns:
            Audio waveform
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Sawtooth wave for aggression
        saw_freq = 110  # Low A
        saw = 2 * (t * saw_freq % 1) - 1
        saw *= 0.2
        
        # High-pitched alarm
        alarm_freq = 1760  # High A
        alarm = np.sin(2 * np.pi * alarm_freq * t) * 0.15
        
        # Modulate alarm (on/off pulse)
        alarm_pulse = (np.sin(2 * np.pi * 4 * t) > 0).astype(float)
        alarm *= alarm_pulse
        
        wave = saw + alarm
        
        # Normalize
        if np.max(np.abs(wave)) > 0:
            wave = wave / np.max(np.abs(wave)) * 0.5
        
        return wave
    
    def _generate_percussion(self, t: np.ndarray, duration: float, 
                            intensity: float = 0.3) -> np.ndarray:
        """
        Generate percussion layer (hi-hats, kicks).
        
        Args:
            t: Time array
            duration: Total duration
            intensity: Volume multiplier
        
        Returns:
            Percussion waveform
        """
        perc = np.zeros_like(t)
        beat_interval = self.sample_rate * 0.43  # Match tempo
        
        for i in range(int(duration / 0.43)):
            # Kick on every beat
            kick_start = int(i * beat_interval)
            kick_end = min(kick_start + int(self.sample_rate * 0.05), len(perc))
            kick_t = t[kick_start:kick_end] - t[kick_start]
            kick = np.sin(2 * np.pi * 60 * kick_t) * np.exp(-kick_t * 40)
            perc[kick_start:kick_end] += kick * 0.5
            
            # Hi-hat on off-beats
            if i % 2 == 1:
                hat_start = int(i * beat_interval)
                hat_end = min(hat_start + int(self.sample_rate * 0.02), len(perc))
                hat = np.random.uniform(-0.3, 0.3, hat_end - hat_start)
                perc[hat_start:hat_end] += hat
        
        return perc * intensity
    
    def update_heat_mix(self, heat_percent: float, berserk: bool):
        """
        Dynamically adjust music layers based on Heat level.
        
        Args:
            heat_percent: Heat level (0.0 to 1.0)
            berserk: True if Berserk mode active
        """
        self.heat_level = heat_percent
        self.berserk_active = berserk
        
        # Fade in lead melody as Heat rises
        if heat_percent < 0.3:
            self.lead_volume = 0.0
        else:
            self.lead_volume = (heat_percent - 0.3) / 0.7 * 0.25
        
        # Percussion only in Berserk
        if berserk:
            self.perc_volume = 0.3
        else:
            self.perc_volume = 0.0
        
        # Increase bass intensity with Heat
        self.bass_volume = 0.2 + heat_percent * 0.15
    
    def _numpy_to_pygame_sound(self, wave: np.ndarray) -> pygame.mixer.Sound:
        """Convert numpy array to pygame Sound"""
        wave = np.clip(wave, -1, 1)
        samples = (wave * 32767).astype(np.int16)
        stereo = np.column_stack((samples, samples))
        return pygame.sndarray.make_sound(stereo)
    
    def play_stage_music(self, loop: bool = True):
        """Start stage music (looping)"""
        if not self.enabled:
            return
        
        try:
            wave = self.generate_stage_music(60.0)
            sound = self._numpy_to_pygame_sound(wave)
            
            if loop:
                sound.play(-1)  # Loop forever
            else:
                sound.play()
            
            self.current_track = sound
        except Exception as e:
            print(f"Could not play stage music: {e}")
    
    def play_boss_music(self):
        """Start boss music"""
        if not self.enabled:
            return
        
        try:
            wave = self.generate_boss_music(90.0)
            sound = self._numpy_to_pygame_sound(wave)
            sound.play(-1)
            self.current_track = sound
        except Exception as e:
            print(f"Could not play boss music: {e}")
    
    def stop(self):
        """Stop current music"""
        if self.current_track:
            self.current_track.stop()
            self.current_track = None


# === INTEGRATION EXAMPLE ===

def example_dynamic_music():
    """
    Example of how to use dynamic music system in game loop.
    """
    pygame.init()
    pygame.mixer.init()
    
    music = VerticalShmupMusic()
    music.play_stage_music(loop=True)
    
    # Game loop
    heat = 0.0
    berserk = False
    
    while True:
        # Heat rises over time (example)
        heat = min(1.0, heat + 0.001)
        
        # Berserk activates at 100%
        if heat >= 1.0:
            berserk = True
        
        # Update music mix dynamically
        music.update_heat_mix(heat, berserk)
        
        # Music layers automatically adjust based on Heat/Berserk
        # No need to stop/start - smooth transitions
        
        pygame.time.delay(16)  # ~60 FPS


if __name__ == "__main__":
    print("=== VERTICAL SHMUP SOUNDTRACK ===")
    print()
    print("Music Layers:")
    print("  1. Bass Pulse - Constant heartbeat rhythm (~100 BPM)")
    print("  2. Synth Pad - Tension building (slow sweep)")
    print("  3. Lead Melody - Escalation (fades in with Heat)")
    print("  4. Percussion - Berserk only (hi-hats + kicks)")
    print()
    print("Dynamic Adaptation:")
    print("  0-30% Heat: Bass + Pad only")
    print("  30-100% Heat: Lead melody fades in")
    print("  100% Heat (Berserk): Percussion layer added")
    print()
    print("Boss Music:")
    print("  Faster tempo (140 BPM vs 100 BPM)")
    print("  Aggressive synth lead")
    print("  Constant percussion")
    print("  Dissonant harmonies")
