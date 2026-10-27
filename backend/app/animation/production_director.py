"""
MysteryVerse Malayalam — Cinematic Production Director
Renders broadcast-quality animated videos featuring host 'jobelessboy':
- Video 1: Introduction Short (9:16 Vertical, 1080x1920)
- Video 2: Introduction Long (16:9 Horizontal, 1920x1080)
STRICT REQUIREMENT: NO MALAYALAM TEXT ON SCREEN. ONLY ENGLISH SUBTITLES & CHANNEL NAME.
"""

import os
import math
import random
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import Dict, Any, List, Optional, Tuple

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    get_ffmpeg_path
)
from app.character.assets_manager import CHARACTER_DIR
from app.audio.music_effects import ProceduralAudioEngine

class CinematicProductionDirector:
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_short = (width < height)

        # Load clean English system fonts
        self.font_logo = self._load_font(52, bold=True)
        self.font_tag = self._load_font(26, bold=False)
        self.font_hud_title = self._load_font(22, bold=True)
        self.font_hud_sub = self._load_font(16, bold=False)
        self.font_sub_en = self._load_font(30 if self.is_short else 34, bold=True)
        self.font_sub_sm = self._load_font(22 if self.is_short else 24, bold=False)

        # Preload character poses and animation parts
        self._load_character_sprites()

        # Cache stars for consistent background
        random.seed(1337)
        self.stars = [
            (random.randint(0, self.width), random.randint(0, self.height), random.randint(1, 3), random.random())
            for _ in range(180)
        ]

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        fonts = [
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\tahoma.ttf"
        ]
        for f in fonts:
            if os.path.exists(f):
                try:
                    return ImageFont.truetype(f, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _load_character_sprites(self):
        """Loads all transparent jobelessboy sprites and sets up eye/mouth animation masks."""
        self.sprites = {}
        poses = ["explanation", "waving", "talking_wide", "blink", "excitement", "welcome", "surprise", "curiosity"]
        for p in poses:
            p_file = CHARACTER_DIR / f"jobelessboy_{p}.png"
            if p_file.exists():
                self.sprites[p] = Image.open(p_file).convert("RGBA")
            else:
                self.sprites[p] = Image.open(CHARACTER_DIR / "jobelessboy_explanation.png").convert("RGBA")

        # Eye blink patch
        blink_img = self.sprites.get("blink", self.sprites["explanation"])
        self.eye_box = (330, 280, 590, 420)
        self.eye_crop = blink_img.crop(self.eye_box)
        ew, eh = self.eye_crop.size
        eye_mask = Image.new("L", (ew, eh), 0)
        d_eye = ImageDraw.Draw(eye_mask)
        d_eye.ellipse([10, 10, ew - 10, eh - 10], fill=255)
        self.eye_mask = eye_mask.filter(ImageFilter.GaussianBlur(radius=8))

        # Talking mouth patch
        talk_img = self.sprites.get("talking_wide", self.sprites["explanation"])
        self.mouth_box = (430, 460, 590, 550)
        self.mouth_crop = talk_img.crop(self.mouth_box)
        mw, mh = self.mouth_crop.size
        mouth_mask = Image.new("L", (mw, mh), 0)
        d_mouth = ImageDraw.Draw(mouth_mask)
        d_mouth.ellipse([8, 8, mw - 8, mh - 8], fill=255)
        self.mouth_mask = mouth_mask.filter(ImageFilter.GaussianBlur(radius=6))

    def _extract_speech_envelope(self, audio_path: str, total_duration: float) -> np.ndarray:
        """Calculates RMS volume per frame to drive accurate lip movement."""
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
        return np.clip(arr / (peak if peak > 0 else 1.0), 0.0, 1.0)

    # -------------------------------------------------------------
    # CINEMATIC PROCEDURAL BACKGROUND ENVIRONMENTS (ENGLISH ONLY)
    # -------------------------------------------------------------

    def _draw_starfield(self, draw: ImageDraw.Draw, t: float):
        for sx, sy, sr, phase in self.stars:
            twinkle = int(130 + 110 * math.sin(t * 3.8 + phase * 6.28))
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(twinkle, twinkle, min(255, twinkle + 35)))

    def _render_env_observatory(self, t: float) -> Image.Image:
        """Futuristic space observatory / laboratory entrance."""
        bg = Image.new("RGBA", (self.width, self.height), (6, 9, 22, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        cx, cy = int(self.width * 0.5), int(self.height * 0.4)
        # Giant observatory portal ring
        r = int(min(self.width, self.height) * 0.42)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(6, 182, 212, 140), width=4)
        draw.ellipse([cx - int(r*0.9), cy - int(r*0.9), cx + int(r*0.9), cy + int(r*0.9)], outline=(59, 130, 246, 80), width=2)

        # Distant nebula inside ring
        for gi, gc in [(r*0.7, (15, 23, 42, 120)), (r*0.45, (14, 165, 233, 50)), (r*0.25, (236, 72, 153, 60))]:
            draw.ellipse([cx - gi, cy - gi, cx + gi, cy + gi], fill=gc)

        self._render_hud_banner(draw, "OBSERVATORY ARCHIVE", "FACILITY STATUS // ACTIVE")
        return bg

    def _render_env_earth_space(self, t: float) -> Image.Image:
        """Spectacular 3D rotating Earth & solar planets."""
        bg = Image.new("RGBA", (self.width, self.height), (4, 6, 18, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        # 3D Earth Globe
        ecx = int(self.width * 0.42) if not self.is_short else int(self.width * 0.5)
        ecy = int(self.height * 0.42) if not self.is_short else int(self.height * 0.32)
        er = int(min(self.width, self.height) * 0.28)

        # Atmosphere glow
        draw.ellipse([ecx - int(er*1.15), ecy - int(er*1.15), ecx + int(er*1.15), ecy + int(er*1.15)], fill=(37, 99, 235, 60))
        draw.ellipse([ecx - int(er*1.06), ecy - int(er*1.06), ecx + int(er*1.06), ecy + int(er*1.06)], fill=(56, 189, 248, 90))

        # Ocean Sphere
        draw.ellipse([ecx - er, ecy - er, ecx + er, ecy + er], fill=(29, 78, 216, 255))

        # Rotating Continents
        rot_x = (t * 22.0) % (er * 2)
        draw.chord([ecx - er + rot_x - er, ecy - int(er*0.5), ecx - er + rot_x + er, ecy + int(er*0.5)], start=30, end=150, fill=(34, 197, 94, 230))
        draw.chord([ecx - er + ((rot_x + er) % (er*2)) - er, ecy - int(er*0.6), ecx - er + ((rot_x + er) % (er*2)) + er, ecy + int(er*0.2)], start=20, end=160, fill=(22, 163, 74, 210))

        # Orbiting Moon
        m_angle = t * 1.1
        mx = int(ecx + (er * 1.55) * math.cos(m_angle))
        my = int(ecy + (er * 0.45) * math.sin(m_angle))
        draw.ellipse([ecx - int(er*1.55), ecy - int(er*0.45), ecx + int(er*1.55), ecy + int(er*0.45)], outline=(148, 163, 184, 50), width=1)
        draw.ellipse([mx - 14, my - 14, mx + 14, my + 14], fill=(226, 232, 240, 255))

        self._render_hud_banner(draw, "ASTRONOMICAL MATRIX", "PLANETARY ROTATION // 1.0X")
        return bg

    def _render_env_molecules_lab(self, t: float) -> Image.Image:
        """Quantum molecules, DNA helix, and atomic laboratory."""
        bg = Image.new("RGBA", (self.width, self.height), (7, 10, 24, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        cx = int(self.width * 0.45) if not self.is_short else int(self.width * 0.5)
        cy = int(self.height * 0.42) if not self.is_short else int(self.height * 0.35)

        # 3D Double Helix DNA Animation
        num_rungs = 14
        spacing = 30
        for i in range(num_rungs):
            phase = t * 3.0 + i * 0.45
            x_offset = int(120 * math.sin(phase))
            y_pos = cy - int((num_rungs * spacing) / 2) + i * spacing
            z_scale = 0.5 + 0.5 * math.cos(phase)

            # Left and right nucleotides
            lx, rx = cx - x_offset, cx + x_offset
            # Connecting bond line
            draw.line([lx, y_pos, rx, y_pos], fill=(148, 163, 184, int(180 * z_scale)), width=3)
            # Atom spheres
            r_size = int(8 + 6 * z_scale)
            draw.ellipse([lx - r_size, y_pos - r_size, lx + r_size, y_pos + r_size], fill=(244, 63, 94, 255))
            draw.ellipse([rx - r_size, y_pos - r_size, rx + r_size, y_pos + r_size], fill=(6, 182, 212, 255))

        # Orbiting Atomic Electrons
        for orbit_i in range(3):
            oa = t * (2.2 + orbit_i * 0.7)
            or_rx = 260
            or_ry = 90
            draw.arc([cx - or_rx, cy - or_ry, cx + or_rx, cy + or_ry], start=0, end=360, fill=(168, 85, 247, 60), width=1)
            ex = int(cx + or_rx * math.cos(oa + orbit_i * 2.1))
            ey = int(cy + or_ry * math.sin(oa + orbit_i * 2.1))
            draw.ellipse([ex - 7, ey - 7, ex + 7, ey + 7], fill=(250, 204, 21, 255))

        self._render_hud_banner(draw, "PHYSICAL & LIFE SCIENCES", "QUANTUM ANALYSIS // NOMINAL")
        return bg

    def _render_env_history_pyramids(self, t: float) -> Image.Image:
        """Ancient Egyptian Pyramids under starlight with golden apex beam."""
        bg = Image.new("RGBA", (self.width, self.height), (12, 8, 26, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        cx = int(self.width * 0.45) if not self.is_short else int(self.width * 0.5)
        base_y = int(self.height * 0.65) if not self.is_short else int(self.height * 0.55)

        # Golden Beam of Light from Great Pyramid Apex
        apex_x = cx
        apex_y = base_y - 240
        draw.polygon([(apex_x - 30, 0), (apex_x + 30, 0), (apex_x + 10, apex_y), (apex_x - 10, apex_y)], fill=(251, 191, 36, 60))
        draw.line([apex_x, 0, apex_x, apex_y], fill=(254, 240, 138, 160), width=3)

        # 3D Great Pyramid
        p_left = [(apex_x - 280, base_y), (apex_x, apex_y), (apex_x + 40, base_y)]
        p_right = [(apex_x + 40, base_y), (apex_x, apex_y), (apex_x + 240, base_y)]
        draw.polygon(p_left, fill=(180, 83, 9, 255))
        draw.polygon(p_right, fill=(217, 119, 6, 255))
        draw.polygon([(apex_x - 20, apex_y + 40), (apex_x, apex_y), (apex_x + 20, apex_y + 40)], fill=(252, 211, 77, 255))

        # Distant Dunes
        draw.chord([-100, base_y - 40, self.width + 100, base_y + 300], start=180, end=360, fill=(120, 53, 15, 255))

        self._render_hud_banner(draw, "HISTORICAL CODEX", "ANCIENT CIVILISATIONS // CHRONOLOGY")
        return bg

    def _render_env_psychology_ocean(self, t: float) -> Image.Image:
        """Mind neural networks & bioluminescent deep ocean."""
        bg = Image.new("RGBA", (self.width, self.height), (4, 12, 28, 255))
        draw = ImageDraw.Draw(bg)

        # Bioluminescent floating particles
        for i in range(40):
            px = int((i * 47 + t * 18) % self.width)
            py = int((i * 61 + 30 * math.sin(t * 1.5 + i)) % self.height)
            size = 2 + (i % 4)
            p_glow = int(120 + 100 * math.sin(t * 4.0 + i))
            draw.ellipse([px - size, py - size, px + size, py + size], fill=(6, 182, 212, p_glow))

        # Neural Synapse Network
        nodes = [(int(self.width * 0.25), int(self.height * 0.35)),
                 (int(self.width * 0.40), int(self.height * 0.25)),
                 (int(self.width * 0.55), int(self.height * 0.38)),
                 (int(self.width * 0.35), int(self.height * 0.48)),
                 (int(self.width * 0.50), int(self.height * 0.50))]
        for i, (nx, ny) in enumerate(nodes):
            for j, (mx, my) in enumerate(nodes):
                if i < j:
                    draw.line([nx, ny, mx, my], fill=(147, 197, 253, 75), width=2)
            pulse = int(10 + 6 * math.sin(t * 5.0 + i * 1.2))
            draw.ellipse([nx - pulse, ny - pulse, nx + pulse, ny + pulse], fill=(96, 165, 250, 180))

        self._render_hud_banner(draw, "COGNITIVE & NATURAL REALMS", "NEURAL PATHWAYS // SYNERGY")
        return bg

    def _render_env_portal_cta(self, t: float) -> Image.Image:
        """Hyper-vibrant cosmic nebula portal with animated subscribe call-to-action."""
        bg = Image.new("RGBA", (self.width, self.height), (8, 6, 26, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        cx, cy = int(self.width * 0.5), int(self.height * 0.38)
        base_r = int(min(self.width, self.height) * 0.36)

        # Pulsing cosmic portal rings
        pulse = 1.0 + 0.08 * math.sin(t * 5.5)
        for r_factor, col in [
            (1.3 * pulse, (99, 102, 241, 40)),
            (1.0 * pulse, (168, 85, 247, 60)),
            (0.7 * pulse, (6, 182, 212, 90)),
            (0.4 * pulse, (244, 63, 94, 110))
        ]:
            ri = int(base_r * r_factor)
            draw.ellipse([cx - ri, cy - ri, cx + ri, cy + ri], fill=col)

        # Subscribe Pill Box
        sub_w, sub_h = (440, 68) if not self.is_short else (380, 62)
        sub_x = cx - sub_w // 2
        sub_y = cy + int(base_r * 0.75)
        # Pulsing outline
        draw.rounded_rectangle([sub_x - 3, sub_y - 3, sub_x + sub_w + 3, sub_y + sub_h + 3], radius=34, fill=None, outline=(239, 68, 68, 180), width=3)
        draw.rounded_rectangle([sub_x, sub_y, sub_x + sub_w, sub_y + sub_h], radius=31, fill=(220, 38, 38, 240))
        # Text inside button
        sub_text = "SUBSCRIBE // JOIN US"
        draw.text((sub_x + 48, sub_y + 18), sub_text, fill=(255, 255, 255), font=self.font_hud_title)

        self._render_hud_banner(draw, "COMMUNITY DISPATCH", "JOIN THE MYSTERYVERSE")
        return bg

    def _render_env_logo_outro(self, t: float) -> Image.Image:
        """Grand final channel logo reveal & outro."""
        bg = Image.new("RGBA", (self.width, self.height), (5, 5, 18, 255))
        draw = ImageDraw.Draw(bg)
        self._draw_starfield(draw, t)

        cx, cy = int(self.width * 0.5), int(self.height * 0.38)
        # Expanding radial rays
        for ray_i in range(24):
            ang = t * 0.4 + ray_i * (math.pi / 12)
            length = min(self.width, self.height) * 0.6
            x2 = int(cx + length * math.cos(ang))
            y2 = int(cy + length * math.sin(ang))
            draw.line([cx, cy, x2, y2], fill=(6, 182, 212, 45), width=2)

        # Glowing badge frame
        bw = int(self.width * 0.82)
        bh = 170
        bx = (self.width - bw) // 2
        by = cy - bh // 2
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=20, fill=(15, 23, 42, 235), outline=(245, 158, 11, 200), width=3)
        
        # Primary English Channel Name
        title = "MYSTERYVERSE MALAYALAM"
        draw.text((bx + 30, by + 30), title, fill=(255, 255, 255), font=self.font_logo)
        tag = "AUTONOMOUS SCIENCE & COSMIC MYSTERIES"
        draw.text((bx + 34, by + 105), tag, fill=(56, 189, 248), font=self.font_tag)

        self._render_hud_banner(draw, "OFFICIAL BROADCAST", "THANK YOU FOR WATCHING")
        return bg

    def _render_hud_banner(self, draw: ImageDraw.Draw, header: str, sub: str):
        """Clean scifi HUD telemetry card in English only."""
        x, y = 40, 40
        w, h = 340, 52
        draw.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=(15, 23, 42, 215), outline=(6, 182, 212, 160), width=1)
        draw.text((x + 14, y + 8), header, fill=(6, 182, 212), font=self.font_hud_title)
        draw.text((x + 14, y + 30), sub, fill=(203, 213, 225), font=self.font_hud_sub)

    # -------------------------------------------------------------
    # CHARACTER COMPOSITING & ANIMATION ENGINE
    # -------------------------------------------------------------

    def _composite_character(
        self,
        base: Image.Image,
        t: float,
        camera: str,
        pose: str,
        speech_energy: float
    ):
        """
        Composites 'jobelessboy' into foreground with:
        - Natural breathing (sine wave bob)
        - Subtle torso tilt & sway
        - Speech-synchronised lip-flap driven by audio energy
        - Natural eyelid blinking every 3.2s
        - Camera framing scale: Wide, Medium, Close-up
        """
        sprite = self.sprites.get(pose, self.sprites["explanation"]).copy()

        # 1. Mouth articulation
        if speech_energy > 0.08:
            factor = min(1.0, speech_energy * 1.35)
            flutter = 0.5 + 0.5 * math.sin(t * 26.0)
            eff = factor * (0.4 + 0.6 * flutter)
            cur_mouth_mask = Image.eval(self.mouth_mask, lambda v: int(v * eff))
            sprite.paste(self.mouth_crop, self.mouth_box, cur_mouth_mask)

        # 2. Eye blinking
        if (t % 3.2) < 0.22:
            phase = math.sin(((t % 3.2) / 0.22) * math.pi)
            cur_eye_mask = Image.eval(self.eye_mask, lambda v: int(v * phase))
            sprite.paste(self.eye_crop, self.eye_box, cur_eye_mask)

        # 3. Body breathing and idle tilt
        bob_y = int(8 * math.sin(t * 3.4))
        tilt = 1.2 * math.sin(t * 2.0)
        sprite_rot = sprite.rotate(tilt, resample=Image.Resampling.BICUBIC, expand=True)

        # 4. Camera scale
        if camera == "wide":
            scale = 0.76 if not self.is_short else 0.70
            pos_x_ratio = 0.68 if not self.is_short else 0.50
            pos_y_offset = 60
        elif camera == "medium":
            scale = 1.05 if not self.is_short else 0.95
            pos_x_ratio = 0.64 if not self.is_short else 0.52
            pos_y_offset = 40
        else:  # close_up
            scale = 1.38 if not self.is_short else 1.22
            pos_x_ratio = 0.58 if not self.is_short else 0.50
            pos_y_offset = 15

        target_h = int(self.height * scale)
        aspect = sprite_rot.width / sprite_rot.height
        target_w = int(target_h * aspect)

        scaled = sprite_rot.resize((target_w, target_h), Image.Resampling.LANCZOS)
        pos_x = int(self.width * pos_x_ratio - (target_w // 2))
        pos_y = self.height - target_h + pos_y_offset + bob_y

        # Soft character drop shadow
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.ellipse([pos_x + 60, pos_y + 120, pos_x + target_w - 60, self.height - 10], fill=(0, 0, 0, 160))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=26))
        base.paste(shadow, (0, 0), shadow)

        # Paste character
        base.paste(scaled, (pos_x, pos_y), scaled)

        # Host badge in English
        draw = ImageDraw.Draw(base)
        bx = max(40, pos_x - 170) if not self.is_short else 40
        by = min(self.height - 180, pos_y + int(target_h * 0.45))
        draw.rounded_rectangle([bx, by, bx + 210, by + 46], radius=8, fill=(15, 23, 42, 220), outline=(56, 189, 248, 150), width=1)
        draw.text((bx + 14, by + 6), "OFFICIAL HOST", fill=(56, 189, 248), font=self.font_hud_title)
        draw.text((bx + 14, by + 26), "jobelessboy", fill=(248, 250, 252), font=self.font_hud_sub)

    # -------------------------------------------------------------
    # ENGLISH-ONLY SUBTITLES RENDERER
    # -------------------------------------------------------------

    def _render_english_subtitles(self, base: Image.Image, text_en: str):
        """Renders styled, high-contrast English subtitles above platform UI areas."""
        draw = ImageDraw.Draw(base)
        box_h = 88 if self.is_short else 80
        box_y = self.height - box_h - (120 if self.is_short else 45)
        box_w = int(self.width * 0.88)
        box_x = (self.width - box_w) // 2

        # Translucent glass card
        draw.rounded_rectangle([box_x, box_y, box_x + box_w, box_y + box_h], radius=14, fill=(8, 12, 24, 220), outline=(245, 158, 11, 170), width=2)
        # Centered English text
        draw.text((box_x + 24, box_y + 24), text_en, fill=(255, 255, 255), font=self.font_sub_en)

    # -------------------------------------------------------------
    # VIDEO 1: INTRODUCTION SHORT FRAME RENDERER (6 SCENES)
    # -------------------------------------------------------------

    def render_short_frame(self, t: float, speech_energy: float) -> Image.Image:
        # Scene 1: 0.0s - 7.5s (Observatory, Waving, Entrance)
        if t < 7.5:
            base = self._render_env_observatory(t)
            self._composite_character(base, t, camera="wide", pose="waving", speech_energy=speech_energy)
            sub = "Hey, friends! Do you love discovering new knowledge?" if t < 3.5 else "Do you love discovering new knowledge and learning amazing things?"
            self._render_english_subtitles(base, sub)

        # Scene 2: 7.5s - 15.5s (Rotating Earth & Space)
        elif t < 15.5:
            base = self._render_env_earth_space(t - 7.5)
            self._composite_character(base, t, camera="medium", pose="explanation", speech_energy=speech_energy)
            sub = "Then you've come to the right place!" if t < 11.5 else "Here, we'll explore science and cosmic mysteries..."
            self._render_english_subtitles(base, sub)

        # Scene 3: 15.5s - 23.5s (Quantum Molecules & Lab)
        elif t < 23.5:
            base = self._render_env_molecules_lab(t - 15.5)
            self._composite_character(base, t, camera="medium", pose="curiosity", speech_energy=speech_energy)
            sub = "We will explore fascinating science, molecules, atoms..." if t < 19.5 else "...and thought-provoking questions about our universe."
            self._render_english_subtitles(base, sub)

        # Scene 4: 23.5s - 31.5s (Ancient Pyramids & Wonders)
        elif t < 31.5:
            base = self._render_env_history_pyramids(t - 23.5)
            self._composite_character(base, t, camera="medium", pose="explanation", speech_energy=speech_energy)
            sub = "Historical wonders, ancient civilisations, and enduring mysteries." if t < 27.5 else "Bringing all of this to you through entertaining animations!"
            self._render_english_subtitles(base, sub)

        # Scene 5: 31.5s - 40.5s (Direct Host Call-to-Action)
        elif t < 40.5:
            base = self._render_env_portal_cta(t - 31.5)
            self._composite_character(base, t, camera="close_up", pose="welcome", speech_energy=speech_energy)
            sub = "So, will you join us on this journey of discovery?" if t < 35.5 else "Subscribe to MysteryVerse Malayalam & comment your thoughts!"
            self._render_english_subtitles(base, sub)

        # Scene 6: 40.5s - End (Logo Outro & Farewell)
        else:
            base = self._render_env_logo_outro(t - 40.5)
            self._composite_character(base, t, camera="wide", pose="waving", speech_energy=speech_energy)
            self._render_english_subtitles(base, "Let's discover new things together. See you in the next video!")

        return base

    # -------------------------------------------------------------
    # VIDEO 2: INTRODUCTION LONG FRAME RENDERER (8 SCENES)
    # -------------------------------------------------------------

    def render_long_frame(self, t: float, speech_energy: float) -> Image.Image:
        # Scene 1: 0.0s - 22.0s (Opening & Welcome)
        if t < 22.0:
            base = self._render_env_observatory(t)
            self._composite_character(base, t, camera="wide", pose="waving" if t < 6.0 else "explanation", speech_energy=speech_energy)
            if t < 6.0:
                sub = "Hello friends! Welcome to MysteryVerse Malayalam!"
            elif t < 12.0:
                sub = "This world is filled with things that amaze us every single day."
            elif t < 17.0:
                sub = "Some can be explained through science, some through history."
            else:
                sub = "Bringing fascinating knowledge to you is our mission."
            self._render_english_subtitles(base, sub)

        # Scene 2: 22.0s - 47.0s (Science, Universe & Quantum)
        elif t < 47.0:
            base = self._render_env_earth_space(t - 22.0)
            self._composite_character(base, t, camera="medium", pose="explanation", speech_energy=speech_energy)
            if t < 29.0:
                sub = "First, let's journey into the vast realm of science."
            elif t < 35.0:
                sub = "How does Earth work? How immense is the universe?"
            elif t < 41.0:
                sub = "What are black holes? How does the human body function?"
            else:
                sub = "We will present all these questions through easy-to-understand animations."
            self._render_english_subtitles(base, sub)

        # Scene 3: 47.0s - 69.0s (General Knowledge & Inventions)
        elif t < 69.0:
            base = self._render_env_molecules_lab(t - 47.0)
            self._composite_character(base, t, camera="medium", pose="curiosity", speech_energy=speech_energy)
            if t < 55.0:
                sub = "Next, general knowledge and astonishing real-world facts."
            elif t < 62.0:
                sub = "Nations of our world, natural wonders, and technology breakthroughs..."
            else:
                sub = "...and the intriguing reasons behind everyday phenomena."
            self._render_english_subtitles(base, sub)

        # Scene 4: 69.0s - 87.0s (History & Ancient Civilisations)
        elif t < 87.0:
            base = self._render_env_history_pyramids(t - 69.0)
            self._composite_character(base, t, camera="medium", pose="explanation", speech_energy=speech_energy)
            if t < 78.0:
                sub = "History is an essential pillar of our exploration."
            else:
                sub = "Ancient civilisations, pivotal events, and enduring enigmas."
            self._render_english_subtitles(base, sub)

        # Scene 5: 87.0s - 105.0s (Controversial Questions & Inquiry)
        elif t < 105.0:
            base = self._render_env_observatory(t - 87.0)
            self._composite_character(base, t, camera="medium", pose="surprise", speech_energy=speech_energy)
            if t < 96.0:
                sub = "We will examine controversial questions with diverse viewpoints."
            else:
                sub = "Separating verified facts from opinions with scientific clarity."
            self._render_english_subtitles(base, sub)

        # Scene 6: 105.0s - 128.0s (Psychology, Mind & Deep Oceans)
        elif t < 128.0:
            base = self._render_env_psychology_ocean(t - 105.0)
            self._composite_character(base, t, camera="medium", pose="curiosity", speech_energy=speech_energy)
            if t < 116.0:
                sub = "The human mind, memory, psychology, deep oceans and wildlife."
            else:
                sub = "Every video should inspire you to look at the world with curiosity."
            self._render_english_subtitles(base, sub)

        # Scene 7: 128.0s - 152.0s (Community & Topics)
        elif t < 152.0:
            base = self._render_env_portal_cta(t - 128.0)
            self._composite_character(base, t, camera="close_up", pose="welcome", speech_energy=speech_energy)
            if t < 136.0:
                sub = "Animation, storytelling, and clear explanations matter most."
            elif t < 144.0:
                sub = "Share in the comments what mysteries you want us to explore!"
            else:
                sub = "Your support is vital on this expedition of discovery."
            self._render_english_subtitles(base, sub)

        # Scene 8: 152.0s - End (Farewell & Logo Outro)
        else:
            base = self._render_env_logo_outro(t - 152.0)
            self._composite_character(base, t, camera="wide", pose="waving", speech_energy=speech_energy)
            if t < 158.0:
                sub = "Subscribe to MysteryVerse Malayalam, like and share our videos!"
            else:
                sub = "Stay curious and keep exploring! Welcome to MysteryVerse Malayalam!"
            self._render_english_subtitles(base, sub)

        return base

    # -------------------------------------------------------------
    # HIGH-PERFORMANCE VIDEO RENDERING PIPELINE
    # -------------------------------------------------------------

    def render_video(
        self,
        output_mp4_path: str,
        audio_mp3_path: str,
        total_duration: float,
        mode: str = "short"
    ) -> str:
        """Renders frames to FFmpeg rawvideo pipe, mixes audio, and produces final broadcast MP4."""
        ffmpeg_bin = get_ffmpeg_path()
        if not ffmpeg_bin:
            raise RuntimeError("FFmpeg not detected!")

        total_frames = int(total_duration * self.fps)
        raw_tmp = str(Path(output_mp4_path).parent / f"tmp_raw_{mode}_{self.width}x{self.height}.mp4")
        music_tmp = str(Path(output_mp4_path).parent / f"tmp_ambient_{mode}_{self.width}x{self.height}.wav")

        # 1. Synthesize Procedural Ambient Background Music
        ProceduralAudioEngine.generate_ambient_track(music_tmp, duration_sec=total_duration + 2.0)

        # 2. Extract Speech Energy Envelope
        speech_envelope = self._extract_speech_envelope(audio_mp3_path, total_duration)

        # 3. Stream frames to FFmpeg
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
            raw_tmp
        ]

        proc = subprocess.Popen(cmd_raw, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for fi in range(total_frames):
            t = fi / self.fps
            s_energy = float(speech_envelope[min(fi, len(speech_envelope) - 1)]) if len(speech_envelope) > 0 else 0.0

            if mode == "short":
                frame = self.render_short_frame(t, s_energy)
            else:
                frame = self.render_long_frame(t, s_energy)

            proc.stdin.write(frame.tobytes())

        proc.stdin.close()
        proc.wait()

        # 4. Final Audio Mixing (Voiceover 1.0, Ambient music 0.18)
        cmd_mux = [
            ffmpeg_bin,
            "-y",
            "-i", raw_tmp,
            "-i", audio_mp3_path,
            "-i", music_tmp,
            "-filter_complex",
            "[1:a]volume=1.0[vocal]; [2:a]volume=0.18[bgm]; [vocal][bgm]amix=inputs=2:duration=first[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4_path
        ]

        subprocess.run(cmd_mux, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Cleanup temporary files
        for f in [raw_tmp, music_tmp]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

        return output_mp4_path
