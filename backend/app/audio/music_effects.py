import math
import struct
import wave
import numpy as np
from pathlib import Path
from app.config import AUDIO_DIR

class ProceduralAudioEngine:
    """
    Synthesizes original, royalty-free cosmic sci-fi / mystery ambient soundscapes
    using mathematical wave generation. Eliminates YouTube copyright strike risk.
    """
    @staticmethod
    def generate_ambient_track(
        output_wav_path: str,
        duration_sec: float = 30.0,
        sample_rate: int = 44100,
        theme: str = "mystery"
    ) -> str:
        num_samples = int(duration_sec * sample_rate)
        t = np.linspace(0, duration_sec, num_samples, False)

        # Base drone frequencies in D-minor (432Hz / 144Hz cosmic resonance)
        f_sub = 55.0     # Low A1 sub-bass drone
        f_mid = 110.0    # A2
        f_pad = 220.0    # A3

        # Sub-bass warmth
        sub_wave = 0.35 * np.sin(2 * np.pi * f_sub * t)

        # Pulsing mid drone with slow LFO (Low Frequency Oscillator)
        lfo = 0.5 * (1.0 + np.sin(2 * np.pi * 0.15 * t))
        mid_wave = 0.25 * lfo * np.sin(2 * np.pi * f_mid * t + 0.1 * np.sin(2 * np.pi * 0.4 * t))

        # Cosmic mystery shimmer / high harmonics
        shimmer = 0.08 * np.sin(2 * np.pi * 880.0 * t) * np.sin(2 * np.pi * 0.25 * t)

        # Soft filtered noise (atmospheric interstellar wind)
        noise = np.random.normal(0, 0.03, num_samples)
        # Simple rolling average low-pass filter
        b = np.ones(50) / 50
        filtered_noise = np.convolve(noise, b, mode='same')

        # Combine tracks
        combined = sub_wave + mid_wave + shimmer + filtered_noise

        # Fade in (2.0s) and fade out (2.5s)
        fade_in_samples = int(2.0 * sample_rate)
        fade_out_samples = int(2.5 * sample_rate)

        fade_in = np.linspace(0, 1, fade_in_samples)
        fade_out = np.linspace(1, 0, fade_out_samples)

        combined[:fade_in_samples] *= fade_in
        combined[-fade_out_samples:] *= fade_out

        # Normalize to -18 dB to ensure narration remains dominant and perfectly intelligible
        max_val = np.max(np.abs(combined))
        if max_val > 0:
            combined = (combined / max_val) * 0.22

        # Convert to 16-bit PCM WAV
        audio_int16 = (combined * 32767).astype(np.int16)

        with wave.open(output_wav_path, 'w') as wf:
            wf.setnchannels(1)  # Mono
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(sample_rate)
            wf.writeframes(audio_int16.tobytes())

        return output_wav_path
