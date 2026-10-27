"""
Cinematic Character Video Engine for MysteryVerse AI
Features official host 'jobelessboy' with:
- Natural upper body breathing & subtle angular sway
- Periodic natural eye blinking using feathered alpha compositing
- Speech-synchronized lip-flap driven by audio RMS envelope
- Multi-camera director (Wide shot, Medium shot, Dynamic Close-up)
- 3 connected realistic cinematic environments (Deep Cosmos & Sun, 3D Saturn & Rings, Nebula Warp & Subscribe)
- Malayalam audio voiceover & styled on-screen subtitles
- Multi-format support: 16:9 Widescreen (1920x1080) and 9:16 Shorts (1080x1920)
"""

import os
import math
import random
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import Dict, Any, Optional, List, Tuple

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    SUBTITLES_DIR,
    THUMBNAILS_DIR,
    DEFAULT_MALAYALAM_FONT,
    get_ffmpeg_path
)
from app.character.assets_manager import CHARACTER_DIR
from app.audio.tts_service import MalayalamTTSService
from app.audio.music_effects import ProceduralAudioEngine

class CinematicCharacterEngine:
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_short = (width < height)
        self.font_path = DEFAULT_MALAYALAM_FONT if os.path.exists(DEFAULT_MALAYALAM_FONT) else None

        # System fonts
        self.font_title = self._load_font(42, bold=True)
        self.font_sub = self._load_font(24, bold=False)
        self.font_badge = self._load_font(20, bold=True)
        self.font_hud = self._load_font(18, bold=True)
        self.font_mal_title = self._load_mal_font(38)
        self.font_mal_body = self._load_mal_font(28)

        # Preload and prepare character sprite components
        self._load_character_sprites()

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        candidates = [
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\seguiemj.ttf",
            r"C:\Windows\Fonts\tahoma.ttf"
        ]
        for f in candidates:
            if os.path.exists(f):
                try:
                    return ImageFont.truetype(f, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _load_mal_font(self, size: int) -> ImageFont.FreeTypeFont:
        if self.font_path and os.path.exists(self.font_path):
            try:
                return ImageFont.truetype(self.font_path, size)
            except Exception:
                pass
        return self._load_font(size, bold=True)

    def _load_character_sprites(self):
        """Preloads base sprites and prepares feathered eye and mouth patches."""
        self.sprites = {}
        pose_names = ["explanation", "waving", "talking_wide", "blink", "excitement", "welcome", "surprise"]
        for p in pose_names:
            file_path = CHARACTER_DIR / f"jobelessboy_{p}.png"
            if file_path.exists():
                self.sprites[p] = Image.open(file_path).convert("RGBA")
            else:
                self.sprites[p] = Image.open(CHARACTER_DIR / "jobelessboy_explanation.png").convert("RGBA")

        # 1. Prepare Eye Blink Patch with feathered radial mask
        blink_img = self.sprites.get("blink", self.sprites["explanation"])
        self.eye_box = (330, 280, 590, 420)
        self.eye_crop = blink_img.crop(self.eye_box)
        ew, eh = self.eye_crop.size
        eye_mask = Image.new("L", (ew, eh), 0)
        d_eye = ImageDraw.Draw(eye_mask)
        d_eye.ellipse([10, 10, ew - 10, eh - 10], fill=255)
        self.eye_mask = eye_mask.filter(ImageFilter.GaussianBlur(radius=8))

        # 2. Prepare Talking Mouth Patch with feathered mask
        talk_img = self.sprites.get("talking_wide", self.sprites["explanation"])
        self.mouth_box = (430, 460, 590, 550)
        self.mouth_crop = talk_img.crop(self.mouth_box)
        mw, mh = self.mouth_crop.size
        mouth_mask = Image.new("L", (mw, mh), 0)
        d_mouth = ImageDraw.Draw(mouth_mask)
        d_mouth.ellipse([8, 8, mw - 8, mh - 8], fill=255)
        self.mouth_mask = mouth_mask.filter(ImageFilter.GaussianBlur(radius=6))

        # Pre-generate starry background cache
        random.seed(42)
        self.stars = [
            (random.randint(0, self.width), random.randint(0, self.height), random.randint(1, 3), random.random())
            for _ in range(160)
        ]

    def _extract_audio_envelope(self, audio_path: str, total_duration: float) -> np.ndarray:
        """Extracts per-frame RMS speech amplitude from narration audio."""
        ffmpeg_bin = get_ffmpeg_path()
        cmd = [ffmpeg_bin, "-y", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        raw, _ = proc.communicate()

        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        samples_per_frame = int(16000 / self.fps)
        total_frames = int(total_duration * self.fps)

        envelope = []
        for i in range(total_frames):
            chunk = samples[i * samples_per_frame : (i + 1) * samples_per_frame]
            rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
            envelope.append(rms)

        arr = np.array(envelope)
        peak = np.percentile(arr, 95) if len(arr) > 0 and np.max(arr) > 0 else 1.0
        norm = np.clip(arr / (peak if peak > 0 else 1.0), 0.0, 1.0)
        return norm

    def _render_background_scene1_sun(self, t: float) -> Image.Image:
        """Scene 1 (Wide Shot): Cosmic Space & Blazing Sun with Solar Flares and Orbiting Planets."""
        bg = Image.new("RGBA", (self.width, self.height), (5, 8, 20, 255))
        draw = ImageDraw.Draw(bg)

        # Starfield with twinkle
        for sx, sy, sr, phase in self.stars:
            twinkle = int(140 + 115 * math.sin(t * 4.0 + phase * 6.28))
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(twinkle, twinkle, min(255, twinkle + 40)))

        # Solar Sun Center (positioned upper-left in 16:9, or top-center in 9:16)
        sun_cx = int(self.width * 0.32) if not self.is_short else int(self.width * 0.5)
        sun_cy = int(self.height * 0.38) if not self.is_short else int(self.height * 0.28)
        sun_r = int(min(self.width, self.height) * 0.18)

        # Sun Corona Glow Layers
        for g_step, g_alpha, g_col in [
            (sun_r * 2.4, 25, (255, 120, 20)),
            (sun_r * 1.8, 45, (255, 170, 30)),
            (sun_r * 1.3, 80, (255, 210, 60)),
            (sun_r * 1.05, 180, (255, 245, 160))
        ]:
            draw.ellipse([sun_cx - g_step, sun_cy - g_step, sun_cx + g_step, sun_cy + g_step], fill=(*g_col, g_alpha))

        # Solar Body with pulsing surface
        draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r], fill=(255, 230, 90, 255))

        # Orbiting Planet (Mercury/Venus)
        orbit_r = sun_r * 1.75
        orb_angle = t * 1.2
        px = int(sun_cx + orbit_r * math.cos(orb_angle))
        py = int(sun_cy + orbit_r * 0.5 * math.sin(orb_angle))
        # Orbit line
        draw.ellipse([sun_cx - orbit_r, sun_cy - orbit_r * 0.5, sun_cx + orbit_r, sun_cy + orbit_r * 0.5], outline=(6, 182, 212, 60), width=1)
        # Planet sphere & shadow
        draw.ellipse([px - 14, py - 14, px + 14, py + 14], fill=(56, 189, 248, 255))
        draw.arc([px - 14, py - 14, px + 14, py + 14], start=0, end=360, fill=(255, 255, 255, 200), width=2)

        # Distant Earth Sphere
        e_orbit = sun_r * 2.3
        e_angle = t * 0.7 + 1.8
        ex = int(sun_cx + e_orbit * math.cos(e_angle))
        ey = int(sun_cy + e_orbit * 0.45 * math.sin(e_angle))
        draw.ellipse([sun_cx - e_orbit, sun_cy - e_orbit * 0.45, sun_cx + e_orbit, sun_cy + e_orbit * 0.45], outline=(100, 116, 139, 40), width=1)
        draw.ellipse([ex - 20, ey - 20, ex + 20, ey + 20], fill=(37, 99, 235, 255))
        draw.ellipse([ex - 12, ey - 10, ex + 6, ey + 6], fill=(34, 197, 94, 220))

        # Scientific telemetry badge
        self._render_hud_box(draw, 50, 40, "SOLAR SYSTEM ARCHIVE", "SCENE 01 // WIDE ESTABLISHING ANGLE")
        return bg

    def _render_background_scene2_saturn(self, t: float) -> Image.Image:
        """Scene 2 (Medium Shot): Majestic Rotating 3D Saturn with Glowing Ice Rings & Asteroid Field."""
        bg = Image.new("RGBA", (self.width, self.height), (4, 6, 18, 255))
        draw = ImageDraw.Draw(bg)

        # Starfield
        for sx, sy, sr, phase in self.stars:
            twinkle = int(120 + 100 * math.sin(t * 3.5 + phase * 6.28))
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(twinkle, twinkle, twinkle))

        # Saturn Positioned on Left-Center (allowing host on Right)
        sat_cx = int(self.width * 0.35) if not self.is_short else int(self.width * 0.45)
        sat_cy = int(self.height * 0.45) if not self.is_short else int(self.height * 0.32)
        sat_r = int(min(self.width, self.height) * 0.22)

        # Background Ring Half (behind planet)
        ring_rx = int(sat_r * 2.3)
        ring_ry = int(sat_r * 0.65)
        tilt_deg = -18.0
        # Draw ring ellipse
        draw.ellipse([sat_cx - ring_rx, sat_cy - ring_ry, sat_cx + ring_rx, sat_cy + ring_ry], outline=(245, 158, 11, 140), width=18)
        draw.ellipse([sat_cx - int(ring_rx * 0.88), sat_cy - int(ring_ry * 0.88), sat_cx + int(ring_rx * 0.88), sat_cy + int(ring_ry * 0.88)], outline=(251, 191, 36, 180), width=12)

        # Saturn Sphere with Atmospheric Banding
        draw.ellipse([sat_cx - sat_r, sat_cy - sat_r, sat_cx + sat_r, sat_cy + sat_r], fill=(217, 119, 6, 255))
        # Atmospheric bands
        for b_offset, b_col in [
            (-int(sat_r * 0.4), (180, 83, 9)),
            (-int(sat_r * 0.15), (245, 158, 11)),
            (int(sat_r * 0.1), (217, 119, 6)),
            (int(sat_r * 0.35), (146, 64, 14))
        ]:
            b_w = int(sat_r * 0.92)
            draw.chord([sat_cx - b_w, sat_cy + b_offset - 12, sat_cx + b_w, sat_cy + b_offset + 12], start=10, end=170, fill=(*b_col, 200))

        # Foreground Ring Half (in front of planet)
        draw.arc([sat_cx - ring_rx, sat_cy - ring_ry, sat_cx + ring_rx, sat_cy + ring_ry], start=0, end=180, fill=(251, 191, 36, 230), width=20)
        draw.arc([sat_cx - int(ring_rx * 0.88), sat_cy - int(ring_ry * 0.88), sat_cx + int(ring_rx * 0.88), sat_cy + int(ring_ry * 0.88)], start=0, end=180, fill=(254, 240, 138, 255), width=10)

        # Moving Ice and Rock Asteroids along the ring plane
        for ai in range(18):
            a_angle = (t * 0.8 + ai * 0.35) % 6.28
            ax = int(sat_cx + (ring_rx * 0.95) * math.cos(a_angle))
            ay = int(sat_cy + (ring_ry * 0.95) * math.sin(a_angle))
            if ay > sat_cy:  # Only foreground asteroids
                asize = 3 + (ai % 4)
                draw.ellipse([ax - asize, ay - asize, ax + asize, ay + asize], fill=(255, 255, 255, 230))

        # Scientific HUD
        self._render_hud_box(draw, 50, 40, "RING DYNAMICS: ICE & ROCK", "SCENE 02 // MEDIUM EXPLANATION ANGLE")
        return bg

    def _render_background_scene3_portal(self, t: float) -> Image.Image:
        """Scene 3 (Dynamic Close-Up): Cosmic Portal & Hyper-Vibrant Starfield with Pulsing Call-to-Action."""
        bg = Image.new("RGBA", (self.width, self.height), (8, 6, 24, 255))
        draw = ImageDraw.Draw(bg)

        # Swirling Nebula Core
        portal_cx = int(self.width * 0.45) if not self.is_short else int(self.width * 0.5)
        portal_cy = int(self.height * 0.48) if not self.is_short else int(self.height * 0.38)
        base_r = int(min(self.width, self.height) * 0.35)

        # Pulsing concentric energy rings
        pulse = 1.0 + 0.08 * math.sin(t * 6.0)
        for ri, rcol in [
            (base_r * 1.35 * pulse, (99, 102, 241, 35)),
            (base_r * 1.10 * pulse, (168, 85, 247, 55)),
            (base_r * 0.85 * pulse, (6, 182, 212, 85)),
            (base_r * 0.55 * pulse, (236, 72, 153, 115))
        ]:
            r_int = int(ri)
            draw.ellipse([portal_cx - r_int, portal_cy - r_int, portal_cx + r_int, portal_cy + r_int], fill=rcol)

        # Cosmic light rays
        for ray_i in range(16):
            ang = t * 0.6 + ray_i * (math.pi / 8)
            ray_len = base_r * (1.2 + 0.3 * math.sin(t * 4.0 + ray_i))
            x2 = int(portal_cx + ray_len * math.cos(ang))
            y2 = int(portal_cy + ray_len * math.sin(ang))
            draw.line([portal_cx, portal_cy, x2, y2], fill=(244, 114, 182, 60), width=2)

        # Scientific HUD
        self._render_hud_box(draw, 50, 40, "COSMIC DISCOVERY DISPATCH", "SCENE 03 // DYNAMIC CLOSE-UP & CTA")
        return bg

    def _render_hud_box(self, draw: ImageDraw.Draw, x: int, y: int, badge: str, title: str):
        """Draws glowing scifi telemetry header badge."""
        draw.rounded_rectangle([x, y, x + 380, y + 54], radius=8, fill=(15, 23, 42, 210), outline=(6, 182, 212, 180), width=1)
        draw.text((x + 14, y + 8), badge, fill=(6, 182, 212), font=self.font_badge)
        draw.text((x + 14, y + 30), title, fill=(241, 245, 249), font=self.font_hud)

    def _composite_animated_character(
        self,
        base: Image.Image,
        t: float,
        camera_angle: str,
        pose_name: str,
        speech_energy: float
    ):
        """
        Composites animated 'jobelessboy' into foreground with:
        - Natural breathing (vertical sin wave)
        - Subtle torso sway & tilt (angular rotation)
        - Speech-synchronized mouth flap (feathered blend proportional to energy)
        - Periodic natural eye blinking (every 3.0s, lasts 0.22s)
        - Camera framing scale: Wide (0.78x), Medium (1.05x), Close-up (1.40x)
        """
        # Select base pose
        base_sprite = self.sprites.get(pose_name, self.sprites["explanation"]).copy()

        # 1. Lip-Sync / Mouth Articulation
        # When speech energy > 0.08, blend open talking mouth
        if speech_energy > 0.08:
            # Dynamic mouth flap intensity based on audio volume
            mouth_factor = min(1.0, speech_energy * 1.35)
            # Modulate with phoneme flutter
            flutter = 0.5 + 0.5 * math.sin(t * 26.0)
            effective_factor = mouth_factor * (0.4 + 0.6 * flutter)

            cur_mouth_mask = Image.eval(self.mouth_mask, lambda v: int(v * effective_factor))
            base_sprite.paste(self.mouth_crop, self.mouth_box, cur_mouth_mask)

        # 2. Eye Blinking
        # Blink every 3.2 seconds, lasting 0.22 seconds
        cycle_t = t % 3.2
        if cycle_t < 0.22:
            blink_phase = math.sin((cycle_t / 0.22) * math.pi)
            cur_eye_mask = Image.eval(self.eye_mask, lambda v: int(v * blink_phase))
            base_sprite.paste(self.eye_crop, self.eye_box, cur_eye_mask)

        # 3. Upper Body Breathing & Idle Sway
        bob_y = int(8 * math.sin(t * 3.4))
        tilt_angle = 1.3 * math.sin(t * 2.2)

        # Apply gentle rotation
        rotated_sprite = base_sprite.rotate(tilt_angle, resample=Image.Resampling.BICUBIC, expand=True)

        # 4. Camera Angle Scale & Positioning
        if camera_angle == "wide":
            scale = 0.76 if not self.is_short else 0.70
            pos_x_ratio = 0.68 if not self.is_short else 0.50
            pos_y_offset = 60
        elif camera_angle == "medium":
            scale = 1.05 if not self.is_short else 0.95
            pos_x_ratio = 0.64 if not self.is_short else 0.52
            pos_y_offset = 40
        else:  # close_up
            scale = 1.40 if not self.is_short else 1.25
            pos_x_ratio = 0.58 if not self.is_short else 0.50
            pos_y_offset = 10

        target_h = int(self.height * scale)
        aspect = rotated_sprite.width / rotated_sprite.height
        target_w = int(target_h * aspect)

        sprite_scaled = rotated_sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)

        pos_x = int(self.width * pos_x_ratio - (target_w // 2))
        pos_y = self.height - target_h + pos_y_offset + bob_y

        # Drop shadow behind character
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.ellipse([pos_x + 60, pos_y + 120, pos_x + target_w - 60, self.height - 10], fill=(0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=26))
        base.paste(shadow, (0, 0), shadow)

        # Composite Character onto Canvas
        base.paste(sprite_scaled, (pos_x, pos_y), sprite_scaled)

        # Character HUD Host Nameplate Badge
        draw = ImageDraw.Draw(base)
        badge_x = max(40, pos_x - 180) if not self.is_short else 40
        badge_y = min(self.height - 180, pos_y + int(target_h * 0.45))
        draw.rounded_rectangle([badge_x, badge_y, badge_x + 220, badge_y + 48], radius=8, fill=(15, 23, 42, 220), outline=(56, 189, 248, 160), width=1)
        draw.text((badge_x + 14, badge_y + 6), "HOST: jobelessboy", fill=(56, 189, 248), font=self.font_badge)
        draw.text((badge_x + 14, badge_y + 26), "ജോബ്‌ലെസ് ബോയ്", fill=(248, 250, 252), font=self.font_hud)

        # Animated Voice Waveform Badge indicating live speech
        if speech_energy > 0.08:
            wave_w = 90
            wave_x = badge_x + 230
            wave_y = badge_y + 4
            draw.rounded_rectangle([wave_x, wave_y, wave_x + wave_w, wave_y + 40], radius=6, fill=(15, 23, 42, 200), outline=(6, 182, 212, 140), width=1)
            for bi in range(5):
                bh = int(6 + 26 * speech_energy * abs(math.sin(t * 18.0 + bi * 1.1)))
                bx = wave_x + 12 + bi * 15
                draw.rectangle([bx, wave_y + 20 - bh // 2, bx + 6, wave_y + 20 + bh // 2], fill=(6, 182, 212))

    def _render_subtitles(self, base: Image.Image, text_mal: str, text_en: str):
        """Renders styled bilingual Malayalam and English subtitles at the bottom."""
        draw = ImageDraw.Draw(base)
        box_h = 100
        box_y = self.height - box_h - 40
        box_w = int(self.width * 0.88)
        box_x = (self.width - box_w) // 2

        # Translucent glass banner
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=16, fill=(10, 15, 30, 225), outline=(245, 158, 11, 180), width=2)

        # Malayalam line (large & bright yellow/white)
        draw.text((box_x + 30, box_y + 16), text_mal, fill=(255, 245, 160), font=self.font_mal_title)
        # English translation summary
        draw.text((box_x + 30, box_y + 60), text_en, fill=(203, 213, 225), font=self.font_sub)

    def render_frame(
        self,
        frame_idx: int,
        total_duration: float,
        speech_envelope: np.ndarray
    ) -> Image.Image:
        """Renders a single frame according to the 3-scene storyboard."""
        t = frame_idx / self.fps
        speech_energy = float(speech_envelope[min(frame_idx, len(speech_envelope) - 1)]) if len(speech_envelope) > 0 else 0.0

        # Scene Cut Timing:
        # Scene 1: 0.0s - 6.5s -> Wide establishing angle, Solar Sun, Host Waving
        # Scene 2: 6.5s - 14.5s -> Medium explanation angle, 3D Saturn, Host Explaining
        # Scene 3: 14.5s - End -> Dynamic Close-Up reaction angle, Cosmic Portal, Host Calling to Action
        if t < 6.5:
            base = self._render_background_scene1_sun(t)
            self._composite_animated_character(base, t, camera_angle="wide", pose_name="waving", speech_energy=speech_energy)
            self._render_subtitles(
                base,
                "നമസ്കാരം കൂട്ടുകാരേ, ഞാൻ നിങ്ങളുടെ സ്വന്തം ജോബ്‌ലെസ് ബോയ്!",
                "Hello friends, I am your own Jobelessboy! Ready for cosmic mysteries?"
            )
        elif t < 14.5:
            base = self._render_background_scene2_saturn(t - 6.5)
            self._composite_animated_character(base, t, camera_angle="medium", pose_name="explanation", speech_energy=speech_energy)
            self._render_subtitles(
                base,
                "നോക്കൂ! ശനിയുടെ ഈ അത്ഭുത വളയങ്ങൾ മഞ്ഞുപാളികളും പാറകളും കൊണ്ടാണ് നിർമ്മിച്ചിരിക്കുന്നത്!",
                "Look! Saturn's wondrous rings are sculpted from millions of ice crystals & rocks!"
            )
        else:
            base = self._render_background_scene3_portal(t - 14.5)
            self._composite_animated_character(base, t, camera_angle="close_up", pose_name="welcome", speech_energy=speech_energy)
            self._render_subtitles(
                base,
                "കൂടുതൽ പ്രപഞ്ച സത്യങ്ങൾ അറിയാൻ MysteryVerse Malayalam ഇപ്പോൾത്തന്നെ സബ്സ്ക്രൈബ് ചെയ്യൂ!",
                "To explore deep cosmic enigmas, SUBSCRIBE to MysteryVerse Malayalam right now!"
            )

        return base

    def generate_cinematic_video(
        self,
        output_mp4_path: str,
        audio_mp3_path: str,
        duration_sec: float
    ) -> str:
        """
        Renders raw frames into video stream, synthesizes procedural sci-fi ambient music,
        and uses FFmpeg to encode and mix the final broadcast-quality MP4.
        """
        ffmpeg_bin = get_ffmpeg_path()
        if not ffmpeg_bin:
            raise RuntimeError("FFmpeg binary not detected!")

        total_frames = int(duration_sec * self.fps)
        raw_video_tmp = str(Path(output_mp4_path).parent / f"raw_cinematic_{self.width}x{self.height}.mp4")
        ambient_music_tmp = str(Path(output_mp4_path).parent / f"ambient_cosmic_{self.width}x{self.height}.wav")

        # 1. Synthesize Procedural Ambient Sci-Fi Music
        ProceduralAudioEngine.generate_ambient_track(ambient_music_tmp, duration_sec=duration_sec + 2.0)

        # 2. Extract Speech Energy Envelope
        speech_envelope = self._extract_audio_envelope(audio_mp3_path, duration_sec)

        # 3. Render Video Frames directly to FFmpeg rawvideo pipe
        cmd_raw = [
            ffmpeg_bin,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgba",
            "-r", str(self.fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            raw_video_tmp
        ]

        proc = subprocess.Popen(cmd_raw, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for fi in range(total_frames):
            frame = self.render_frame(fi, duration_sec, speech_envelope)
            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()

        # 4. Final Master Audio Mixing & MP4 Assembly
        cmd_mux = [
            ffmpeg_bin,
            "-y",
            "-i", raw_video_tmp,
            "-i", audio_mp3_path,
            "-i", ambient_music_tmp,
            "-filter_complex",
            "[1:a]volume=1.0[vocal]; [2:a]volume=0.22[bgm]; [vocal][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4_path
        ]

        subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Clean temporary intermediate files
        for tmp_f in [raw_video_tmp, ambient_music_tmp]:
            if os.path.exists(tmp_f):
                try:
                    os.remove(tmp_f)
                except Exception:
                    pass

        return output_mp4_path
