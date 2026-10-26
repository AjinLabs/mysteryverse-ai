import os
import math
import random
import time
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import Dict, Any, Optional

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    SUBTITLES_DIR,
    THUMBNAILS_DIR,
    DEFAULT_MALAYALAM_FONT,
    get_ffmpeg_path
)
from app.character.assets_manager import CHARACTER_DIR, generate_character_sprite
from app.audio.tts_service import MalayalamTTSService
from app.audio.subtitle_service import SubtitleService
from app.audio.music_effects import ProceduralAudioEngine
from app.video.ffmpeg_compositor import FFmpegCompositor
from app.database import get_db_connection, log_event

INTRO_SCRIPT_MAL = """നമസ്കാരം കൂട്ടുകാരേ!

ഈ ലോകത്ത് നമുക്കറിയാത്ത ഒരുപാട് കാര്യങ്ങളുണ്ട്. ശാസ്ത്രലോകത്തിലെ അത്ഭുതങ്ങൾ, പ്രപഞ്ചത്തിന്റെ രഹസ്യങ്ങൾ, ആരെയും അമ്പരപ്പിക്കുന്ന ജനറൽ നോളജ്, ചരിത്രത്തിലെ വിസ്മയങ്ങൾ, ചിന്തിപ്പിക്കുന്ന ചോദ്യങ്ങൾ…

ഇതെല്ലാം രസകരമായ അനിമേഷനുകളിലൂടെ നിങ്ങളിലേക്ക് എത്തിക്കാനാണ് ഞങ്ങൾ വരുന്നത്.

ഓരോ വീഡിയോയിലും പുതിയ അറിവുകൾ, പുതിയ ചിന്തകൾ, അത്ഭുതപ്പെടുത്തുന്ന വസ്തുതകൾ!

അപ്പോൾ നമ്മുടെ ഈ അറിവിന്റെ യാത്രയിൽ നിങ്ങളും കൂടെയുണ്ടാകണം.

MysteryVerse Malayalam ചാനൽ സബ്സ്ക്രൈബ് ചെയ്യൂ, ഫോളോ ചെയ്യൂ, നിങ്ങളുടെ സപ്പോർട്ട് ഞങ്ങൾക്ക് നൽകൂ.

അറിവിന്റെ ലോകത്തേക്ക് സ്വാഗതം!"""

class ChannelIntroGenerator:
    """
    Renders the official cinematic 3D channel introduction video for MYSTERYVERSE MALAYALAM
    in both 9:16 (Shorts) and 16:9 (Widescreen) formats.
    """
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_short = (width < height)
        self.font_path = DEFAULT_MALAYALAM_FONT if os.path.exists(DEFAULT_MALAYALAM_FONT) else None

        # Load fonts
        self.f_hero = self._load_font(56, bold=True)
        self.f_title = self._load_font(40, bold=True)
        self.f_sub = self._load_font(26, bold=False)
        self.f_mal_large = self._load_mal_font(42)
        self.f_mal_med = self._load_mal_font(30)
        self.f_mal_tag = self._load_mal_font(24)
        self.f_eq = self._load_font(32, bold=True)

        # Pre-cache static layers and sprites
        self._init_nebula()
        self._sprite_cache = {}

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        font_files = [
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\seguiemj.ttf",
            r"C:\Windows\Fonts\tahoma.ttf"
        ]
        for f in font_files:
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

    def _init_nebula(self):
        cx, cy = self.width // 2, int(self.height * 0.45)
        r = int(min(self.width, self.height) * 0.5)
        glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(20, 15, 65, 110))
        g_draw.ellipse([cx - int(r*0.6), cy - int(r*0.6), cx + int(r*0.6), cy + int(r*0.6)], fill=(6, 182, 212, 75))
        g_draw.ellipse([cx - int(r*0.3), cy - int(r*0.3), cx + int(r*0.3), cy + int(r*0.3)], fill=(245, 158, 11, 45))
        self.cached_nebula = glow.filter(ImageFilter.GaussianBlur(radius=35))

    def _get_host_sprite(self, expression: str) -> Image.Image:
        if expression not in self._sprite_cache:
            p = CHARACTER_DIR / f"jobelessboy_{expression}.png"
            if not p.exists():
                p = CHARACTER_DIR / f"dr_kiran_{expression}.png"
            if not p.exists():
                p = Path(generate_character_sprite(expression))
            self._sprite_cache[expression] = Image.open(p).convert("RGBA")
        return self._sprite_cache[expression]

    def render_frame(self, t: float, total_duration: float) -> Image.Image:
        """
        Renders an individual frame based on the cinematic storyboard:
        0.0s - 5.5s: Scene 1 - Cosmic Deep Space & Zooming Earth with Floating Scientific Equations
        5.5s - 12.0s: Scene 2 - Brain Synapses, Ancient Pyramids & World Wireframe
        12.0s - 20.0s: Scene 3 - jobelessboy Host Entrance & Revolving Universe
        20.0s - 27.5s: Scene 4 - jobelessboy Points to Mysteries & Subscribe Pulse
        27.5s - end: Scene 5 - Grand Final Logo Reveal & Channel Tagline
        """
        if t < 5.5:
            return self._render_scene_cosmic_earth(t)
        elif t < 12.0:
            return self._render_scene_brain_pyramids(t - 5.5)
        elif t < 20.0:
            return self._render_scene_host_entrance(t - 12.0)
        elif t < 27.5:
            return self._render_scene_host_cta(t - 20.0)
        else:
            return self._render_scene_final_reveal(t - 27.5)

    def _render_scene_cosmic_earth(self, t: float) -> Image.Image:
        """Scene 1: Cosmic zoom-in to Earth with glowing scientific equations."""
        base = Image.new("RGB", (self.width, self.height), (4, 6, 16))
        base.paste(self.cached_nebula, (0, 0), self.cached_nebula)
        draw = ImageDraw.Draw(base)

        # Starfield with forward warp motion
        rng = random.Random(12)
        cx, cy = self.width // 2, int(self.height * 0.45)
        for _ in range(100):
            sx = rng.randint(0, self.width)
            sy = rng.randint(0, self.height)
            dist = math.hypot(sx - cx, sy - cy) + 1.0
            warp_speed = t * 15 * (dist / self.width)
            sx_w = int(cx + (sx - cx) * (1.0 + warp_speed * 0.05))
            sy_w = int(cy + (sy - cy) * (1.0 + warp_speed * 0.05))
            bright = int(180 + 75 * math.sin(t * 4.0 + rng.uniform(0, 6.28)))
            if 0 <= sx_w < self.width and 0 <= sy_w < self.height:
                draw.rectangle([sx_w, sy_w, sx_w + 2, sy_w + 2], fill=(bright, bright, 255))

        # Zooming 3D Planet Earth
        # Starts at radius 110, expands to 180 as camera zooms in
        zoom_prog = min(1.0, t / 5.5)
        earth_r = int((min(self.width, self.height) * 0.16) + (min(self.width, self.height) * 0.10) * zoom_prog)
        ey = int(self.height * 0.44)

        # Atmosphere Glow
        draw.arc([cx - earth_r - 6, ey - earth_r - 6, cx + earth_r + 6, ey + earth_r + 6], 0, 360, fill=(6, 182, 212), width=4)
        draw.ellipse([cx - earth_r, ey - earth_r, cx + earth_r, ey + earth_r], fill=(14, 116, 144))

        # Rotating Continents
        rot = int(t * 30) % (earth_r * 2)
        for c_idx in [-1, 0, 1]:
            cont_x = cx - earth_r + rot + c_idx * int(earth_r * 1.4)
            if cx - earth_r - 40 < cont_x < cx + earth_r + 40:
                draw.ellipse([cont_x - 30, ey - 35, cont_x + 50, ey + 35], fill=(34, 197, 94))
                draw.ellipse([cont_x + 15, ey + 5, cont_x + 75, ey + 60], fill=(22, 163, 74))

        # Floating glowing scientific equations
        equations = [
            ("E = mc²", 0.18, 0.22, (6, 182, 212)),
            ("∇ × B = μ₀J", 0.72, 0.26, (245, 158, 11)),
            ("Δx · Δp ≥ ℏ/2", 0.20, 0.68, (56, 189, 248)),
            ("iℏ ∂ψ/∂t = Ĥψ", 0.68, 0.72, (217, 70, 239)),
            ("G_μν + Λg_μν = 8πG/c⁴ T_μν", 0.35, 0.82, (253, 224, 71)),
        ]
        for eq_text, rel_x, rel_y, col in equations:
            eq_x = int(self.width * rel_x + 15 * math.sin(t * 2.0 + rel_x * 10))
            eq_y = int(self.height * rel_y + 12 * math.cos(t * 1.8 + rel_y * 10))
            draw.text((eq_x, eq_y), eq_text, fill=col, font=self.f_eq)

        # Header Badge
        self._render_cinematic_badge(draw, "COSMIC ODYSSEY BEGINS", "EXPLORING THE UNKNOWN")
        return base

    def _render_scene_brain_pyramids(self, t: float) -> Image.Image:
        """Scene 2: Glowing 3D brain synapses, Great Pyramids & world geometry."""
        base = Image.new("RGB", (self.width, self.height), (6, 9, 22))
        draw = ImageDraw.Draw(base)

        # Background grid
        for gy in range(0, self.height, 80):
            draw.line([(0, gy), (self.width, gy)], fill=(12, 25, 50), width=1)
        for gx in range(0, self.width, 80):
            draw.line([(gx, 0), (gx, self.height)], fill=(12, 25, 50), width=1)

        # Upper Area: Glowing 3D Brain & Synapses
        bx, by = self.width // 2, int(self.height * 0.32)
        draw.ellipse([bx - 140, by - 90, bx - 10, by + 90], outline=(6, 182, 212), width=3)
        draw.ellipse([bx + 10, by - 90, bx + 140, by + 90], outline=(6, 182, 212), width=3)

        # Synapses firing
        nodes = [(bx-100, by-40), (bx-50, by), (bx-90, by+50), (bx+100, by-40), (bx+50, by), (bx+90, by+50)]
        for i in range(len(nodes)):
            n1 = nodes[i]
            n2 = nodes[(i + 1) % len(nodes)]
            draw.line([n1, n2], fill=(30, 60, 110), width=2)
            prog = (t * 3.0 + i * 0.4) % 1.0
            sx = int(n1[0] + (n2[0] - n1[0]) * prog)
            sy = int(n1[1] + (n2[1] - n1[1]) * prog)
            draw.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(245, 158, 11))

        # Lower Area: 3D Great Pyramids with golden apex alignment ray
        apex_x, apex_y = self.width // 2, int(self.height * 0.65)
        base_y = int(self.height * 0.88)
        
        # Golden Beam shooting up to Brain
        draw.polygon([(apex_x - 12, by + 90), (apex_x + 12, by + 90), (apex_x + 4, apex_y), (apex_x - 4, apex_y)], fill=(245, 158, 11))
        # Pyramid faces
        draw.polygon([(apex_x, apex_y), (int(self.width * 0.18), base_y), (apex_x, base_y)], fill=(180, 110, 45))
        draw.polygon([(apex_x, apex_y), (apex_x, base_y), (int(self.width * 0.82), base_y)], fill=(120, 70, 30))

        # Rotating sacred geometry ring
        geom_r = int(70 + 12 * math.sin(t * 3.0))
        draw.ellipse([apex_x - geom_r, apex_y - geom_r, apex_x + geom_r, apex_y + geom_r], outline=(251, 191, 36), width=2)

        self._render_cinematic_badge(draw, "SCIENCE & ANCIENT MYSTERIES", "NEUROSCIENCE & ARCHAEOLOGY")
        return base

    def _render_scene_host_entrance(self, t: float) -> Image.Image:
        """Scene 3: Cute 3D host jobelessboy steps in, welcoming audience in front of revolving cosmos."""
        base = Image.new("RGB", (self.width, self.height), (6, 9, 20))
        base.paste(self.cached_nebula, (0, 0), self.cached_nebula)
        draw = ImageDraw.Draw(base)

        # Revolving Solar System in Background
        sun_x, sun_y = self.width // 2, int(self.height * 0.35) if self.is_short else int(self.height * 0.48)
        sun_r = int(min(self.width, self.height) * 0.07)
        draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(255, 235, 120))
        for i in range(8):
            ang = t * 1.0 + i * (math.pi / 4)
            fx = int(sun_x + (sun_r + 14) * math.cos(ang))
            fy = int(sun_y + (sun_r + 14) * math.sin(ang))
            draw.line([(sun_x, sun_y), (fx, fy)], fill=(249, 115, 22), width=2)

        # Orbiting Earth and Saturn
        e_ang = t * 1.5
        ex = int(sun_x + 190 * math.cos(e_ang))
        ey = int(sun_y + 110 * math.sin(e_ang))
        draw.ellipse([sun_x - 190, sun_y - 110, sun_x + 190, sun_y + 110], outline=(30, 58, 100), width=1)
        draw.ellipse([ex - 12, ey - 12, ex + 12, ey + 12], fill=(56, 189, 248))

        s_ang = t * 0.7 + 2.0
        sx = int(sun_x + 320 * math.cos(s_ang))
        sy = int(sun_y + 180 * math.sin(s_ang))
        draw.ellipse([sun_x - 320, sun_y - 180, sun_x + 320, sun_y + 180], outline=(30, 58, 100), width=1)
        draw.ellipse([sx - 24, sy - 8, sx + 24, sy + 8], outline=(234, 179, 8), width=2)
        draw.ellipse([sx - 16, sy - 16, sx + 16, sy + 16], fill=(253, 224, 71))

        # Host Entrance Animation: Slides up smoothly into foreground
        slide_in = min(1.0, t / 1.0)
        bob = int(10 * math.sin(t * 3.0))

        sprite = self._get_host_sprite("explanation")
        self._draw_host_in_foreground(base, sprite, slide_in, bob)

        self._render_cinematic_badge(draw, "MEET JOBELESSBOY", "YOUR EXPLORATION GUIDE")
        return base

    def _render_scene_host_cta(self, t: float) -> Image.Image:
        """Scene 4: jobelessboy excited pointing at the cosmos & Subscribe Callout."""
        base = Image.new("RGB", (self.width, self.height), (6, 9, 20))
        base.paste(self.cached_nebula, (0, 0), self.cached_nebula)
        draw = ImageDraw.Draw(base)

        # Animated Cyber Grid & Starfield
        rng = random.Random(99)
        for _ in range(80):
            sx = rng.randint(0, self.width)
            sy = rng.randint(0, self.height)
            draw.rectangle([sx, sy, sx + 2, sy + 2], fill=(200, 220, 255))

        # Central Cosmic Anomaly Ring
        cx, cy = self.width // 2, int(self.height * 0.35)
        for r_i in range(1, 4):
            r = int(r_i * 90 + 15 * math.sin(t * 2.5 + r_i))
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(6, 182, 212), width=2)

        # Host Excited Pointing Sprite
        bob = int(10 * math.sin(t * 3.5))
        sprite = self._get_host_sprite("surprise")
        self._draw_host_in_foreground(base, sprite, 1.0, bob)

        # Subscribe & Bell Notification Card (Left of Host)
        card_w, card_h = 420, 110
        card_x = 70
        card_y = int(self.height * 0.62) if self.is_short else int(self.height * 0.55)
        
        pulse_scale = 1.0 + 0.05 * math.sin(t * 6.0)
        pw = int(card_w * pulse_scale)
        ph = int(card_h * pulse_scale)
        
        draw.rounded_rectangle([card_x, card_y, card_x + pw, card_y + ph], radius=16, fill=(220, 38, 38), outline=(255, 255, 255), width=3)
        draw.text((card_x + 30, card_y + 20), "▶ SUBSCRIBE", fill=(255, 255, 255), font=self.f_hero)
        draw.text((card_x + 30, card_y + 70), "MYSTERY VERSE MALAYALAM", fill=(255, 255, 255), font=self.f_sub)

        self._render_cinematic_badge(draw, "JOIN THE VOYAGE", "SUBSCRIBE & EXPLORE")
        return base

    def _render_scene_final_reveal(self, t: float) -> Image.Image:
        """Scene 5: Grand Epic Channel Logo Reveal with Taglines."""
        base = Image.new("RGB", (self.width, self.height), (4, 6, 16))
        draw = ImageDraw.Draw(base)

        # Luminous Center Aura Burst
        cx, cy = self.width // 2, int(self.height * 0.45)
        burst_r = int(min(self.width, self.height) * 0.48)
        burst = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        b_draw = ImageDraw.Draw(burst)
        b_draw.ellipse([cx - burst_r, cy - burst_r, cx + burst_r, cy + burst_r], fill=(6, 182, 212, 130))
        b_draw.ellipse([cx - int(burst_r*0.5), cy - int(burst_r*0.5), cx + int(burst_r*0.5), cy + int(burst_r*0.5)], fill=(245, 158, 11, 110))
        burst = burst.filter(ImageFilter.GaussianBlur(radius=45))
        base.paste(burst, (0, 0), burst)

        # Orbiting Particle Rings
        for ring_i in range(3):
            r = int(burst_r * (0.6 + ring_i * 0.25))
            draw.ellipse([cx - r, cy - int(r*0.4), cx + r, cy + int(r*0.4)], outline=(255, 255, 255, 60), width=1)

        # Channel Title: MYSTERYVERSE MALAYALAM
        title_top = cy - 140
        # Shadow/glow
        draw.text((cx - 322, title_top + 2), "MYSTERYVERSE", fill=(0, 0, 0), font=self.f_hero)
        draw.text((cx - 320, title_top), "MYSTERYVERSE", fill=(6, 182, 212), font=self.f_hero)

        draw.text((cx - 302, title_top + 72), "MALAYALAM", fill=(0, 0, 0), font=self.f_hero)
        draw.text((cx - 300, title_top + 70), "MALAYALAM", fill=(245, 158, 11), font=self.f_hero)

        # English Channel Badge
        badge_y = title_top + 160
        draw.rounded_rectangle([cx - 260, badge_y, cx + 260, badge_y + 46], radius=12, fill=(15, 23, 42), outline=(6, 182, 212), width=2)
        draw.text((cx - 210, badge_y + 8), "OFFICIAL CHANNEL INTRO", fill=(255, 255, 255), font=self.f_sub)

        # Tagline in English:
        tag_y = badge_y + 75
        draw.text((cx - 330, tag_y), "UNCOVER THE UNKNOWN • QUESTION EVERYTHING", fill=(226, 232, 240), font=self.f_sub)
        draw.text((cx - 160, tag_y + 36), "EXPLORE THE COSMOS", fill=(253, 224, 71), font=self.f_sub)

        # Call to Action Pill
        cta_y = tag_y + 95
        draw.rounded_rectangle([cx - 280, cta_y, cx + 280, cta_y + 55], radius=28, fill=(220, 38, 38), outline=(255, 255, 255), width=2)
        draw.text((cx - 210, cta_y + 12), "SUBSCRIBE • FOLLOW • EXPLORE", fill=(255, 255, 255), font=self.f_sub)

        return base

    def _draw_host_in_foreground(self, base: Image.Image, sprite: Image.Image, slide_in: float, bob: int):
        """Draws jobelessboy smoothly in the lower-right foreground with drop shadow."""
        if self.is_short:
            target_w = int(self.width * 0.72)
            aspect = sprite.height / sprite.width
            target_h = int(target_w * aspect)
            sprite_res = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            pos_x = self.width - target_w + 80
            final_y = self.height - target_h + 80 + bob
            start_y = self.height + 50
            pos_y = int(start_y + (final_y - start_y) * slide_in)
        else:
            target_h = int(self.height * 0.82)
            aspect = sprite.width / sprite.height
            target_w = int(target_h * aspect)
            sprite_res = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            pos_x = self.width - target_w - 50
            final_y = self.height - target_h + 40 + bob
            start_y = self.height + 50
            pos_y = int(start_y + (final_y - start_y) * slide_in)

        # Drop shadow
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        sy0 = pos_y + int(target_h * 0.7)
        sy1 = pos_y + target_h + 20
        if sy1 > sy0 and pos_x + target_w - 50 > pos_x + 50:
            s_draw.ellipse([pos_x + 50, sy0, pos_x + target_w - 50, sy1], fill=(0, 0, 0, 160))
            shadow = shadow.filter(ImageFilter.GaussianBlur(radius=28))
            base.paste(shadow, (0, 0), shadow)

        # Paste character
        base.paste(sprite_res, (pos_x, pos_y), sprite_res)

    def _render_cinematic_badge(self, draw: ImageDraw.Draw, en_text: str, sub_text: str = "MYSTERYVERSE 360"):
        card_x1, card_y1 = 50, 75
        card_x2, card_y2 = self.width - 50, 195
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill=(15, 23, 42), outline=(6, 182, 212), width=2)
        
        badge_x1, badge_y1 = card_x1 + 20, card_y1 + 16
        draw.rounded_rectangle([badge_x1, badge_y1, badge_x1 + 220, badge_y1 + 36], radius=8, fill=(6, 182, 212))
        draw.text((badge_x1 + 14, badge_y1 + 6), "OFFICIAL INTRO", fill=(15, 23, 42), font=self.f_sub)
        draw.text((badge_x1 + 240, badge_y1 + 6), sub_text, fill=(245, 158, 11), font=self.f_sub)
        draw.text((card_x1 + 20, card_y1 + 68), en_text, fill=(255, 255, 255), font=self.f_title)

    def generate_video(self, output_mp4: str, total_duration_sec: float) -> str:
        ffmpeg_bin = get_ffmpeg_path()
        if not ffmpeg_bin:
            raise RuntimeError("FFmpeg executable not found!")

        render_fps = self.fps
        total_frames = int(total_duration_sec * render_fps)

        cmd = [
            ffmpeg_bin,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgb24",
            "-r", str(render_fps),
            "-i", "-",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "22",
            "-pix_fmt", "yuv420p",
            output_mp4
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for f_idx in range(total_frames):
            t = f_idx / render_fps
            frame_img = self.render_frame(t, total_duration_sec)
            proc.stdin.write(frame_img.tobytes())

        proc.stdin.close()
        proc.wait()
        return output_mp4


def produce_channel_introduction_package() -> Dict[str, Any]:
    """
    End-to-end production of both:
    1. YouTube Shorts (9:16, 1080x1920) Channel Introduction
    2. YouTube Intro / Widescreen (16:9, 1920x1080) Channel Introduction
    """
    compositor = FFmpegCompositor()
    tts = MalayalamTTSService()

    # 1. Synthesize Malayalam Voiceover
    voice_path = str(AUDIO_DIR / "channel_intro_voice.mp3")
    tts.generate_speech_sync(INTRO_SCRIPT_MAL, voice_path)
    audio_dur = compositor.get_media_duration(voice_path)
    if audio_dur <= 0:
        audio_dur = 33.5

    # 2. Generate Cinematic Ambient Audio Track
    bgm_path = str(AUDIO_DIR / "channel_intro_bgm.wav")
    ProceduralAudioEngine.generate_ambient_track(bgm_path, duration_sec=audio_dur + 2.0)

    # 3. Generate Timed English Subtitles (Styled with clean font, no broken glyphs)
    intro_english_phrases = [
        {"start": 0.0, "end": 2.2, "text": "Hello friends! Welcome to our world."},
        {"start": 2.2, "end": 5.5, "text": "There are countless mysteries around us..."},
        {"start": 5.5, "end": 7.5, "text": "Wonders of cutting-edge science,"},
        {"start": 7.5, "end": 9.5, "text": "The deepest secrets of the universe,"},
        {"start": 9.5, "end": 11.2, "text": "Mind-blowing facts & knowledge,"},
        {"start": 11.2, "end": 13.0, "text": "Marvels of ancient human history,"},
        {"start": 13.0, "end": 15.5, "text": "And questions that spark your mind!"},
        {"start": 15.5, "end": 18.5, "text": "We bring all of this to life..."},
        {"start": 18.5, "end": 21.0, "text": "Through thrilling 3D animations!"},
        {"start": 21.0, "end": 23.5, "text": "Fresh insights & new perspectives,"},
        {"start": 23.5, "end": 26.0, "text": "Astonishing truths in every video!"},
        {"start": 26.0, "end": 28.5, "text": "Join us on this incredible voyage."},
        {"start": 28.5, "end": 31.0, "text": "Subscribe to MysteryVerse Malayalam!"},
        {"start": 31.0, "end": 33.5, "text": "Welcome to the world of knowledge!"}
    ]
    ass_path_short = str(SUBTITLES_DIR / "channel_intro_short.ass")
    SubtitleService.create_ass_from_segments(intro_english_phrases, ass_path_short, is_short=True)

    ass_path_wide = str(SUBTITLES_DIR / "channel_intro_wide.ass")
    SubtitleService.create_ass_from_segments(intro_english_phrases, ass_path_wide, is_short=False)

    # 4. Render Raw Visual Clips
    # Format A: Shorts (9:16, 1080x1920)
    print("Rendering 9:16 Shorts raw clip...")
    gen_short = ChannelIntroGenerator(width=1080, height=1920, fps=24)
    raw_short = str(VIDEOS_DIR / "channel_intro_raw_916.mp4")
    gen_short.generate_video(raw_short, audio_dur)

    # Format B: Widescreen (16:9, 1920x1080)
    print("Rendering 16:9 Widescreen raw clip...")
    gen_wide = ChannelIntroGenerator(width=1920, height=1080, fps=24)
    raw_wide = str(VIDEOS_DIR / "channel_intro_raw_169.mp4")
    gen_wide.generate_video(raw_wide, audio_dur)

    # 5. Assemble Final Videos with Audio Mixing & Subtitles
    final_short = str(VIDEOS_DIR / "channel_intro_shorts_916_final.mp4")
    print("Assembling final 9:16 Shorts video...")
    res_short = compositor.assemble_final_video(
        video_clip_path=raw_short,
        voiceover_audio_path=voice_path,
        ambient_music_path=bgm_path,
        subtitles_path=ass_path_short,
        output_mp4_path=final_short,
        is_short=True
    )

    final_wide = str(VIDEOS_DIR / "channel_intro_widescreen_169_final.mp4")
    print("Assembling final 16:9 Widescreen video...")
    res_wide = compositor.assemble_final_video(
        video_clip_path=raw_wide,
        voiceover_audio_path=voice_path,
        ambient_music_path=bgm_path,
        subtitles_path=ass_path_wide,
        output_mp4_path=final_wide,
        is_short=False
    )

    # 6. Generate Channel Intro Thumbnails
    thumb_wide = str(THUMBNAILS_DIR / "channel_intro_thumb_169.jpg")
    from app.thumbnail.thumbnail_engine import ThumbnailEngine
    te = ThumbnailEngine()
    te.generate_thumbnail(
        output_path=thumb_wide,
        title_mal="അറിവിന്റെ ലോകത്തേക്ക് സ്വാഗതം! | Official Intro",
        category="Channel Intro",
        expression="surprise",
        width=1280,
        height=720,
        badge_text="OFFICIAL INTRO"
    )

    # Record in database
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    for vid_id, vid_path, is_s in [
        ("job_channel_intro_shorts", final_short, True),
        ("job_channel_intro_wide", final_wide, False)
    ]:
        cursor.execute("""
        INSERT OR REPLACE INTO video_jobs (
            id, video_type, resolution, render_engine,
            audio_path, subtitles_path, thumbnail_path, video_path,
            duration_sec, status, quality_passed, created_at, completed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            vid_id,
            "short" if is_s else "long",
            "1080x1920" if is_s else "1920x1080",
            "cinematic_3d_procedural",
            voice_path,
            ass_path_short if is_s else ass_path_wide,
            thumb_wide,
            vid_path,
            audio_dur,
            "ready_for_upload",
            True,
            now_iso,
            now_iso
        ))
    conn.commit()
    conn.close()

    log_event("INFO", "IntroGenerator", "Successfully produced official channel introduction package (Shorts & Widescreen)")

    return {
        "audio_duration": audio_dur,
        "shorts_video": final_short,
        "widescreen_video": final_wide,
        "thumbnail": thumb_wide,
        "validation_shorts": res_short["validation"],
        "validation_wide": res_wide["validation"]
    }

if __name__ == "__main__":
    print("Producing MysteryVerse Malayalam Channel Introduction Package...")
    result = produce_channel_introduction_package()
    print("Complete Result:", result)
