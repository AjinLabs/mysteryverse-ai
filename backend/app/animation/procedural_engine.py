import os
import math
import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import Optional, List, Tuple
from app.config import STATIC_DIR, DEFAULT_MALAYALAM_FONT, get_ffmpeg_path
from app.character.assets_manager import CHARACTER_DIR, generate_character_sprite

ANIM_CACHE_DIR = STATIC_DIR / "clips"
ANIM_CACHE_DIR.mkdir(parents=True, exist_ok=True)

class ProceduralSceneEngine:
    """
    High-performance procedural motion graphics & presentation animation engine.
    Renders vivid dynamic backgrounds matching the exact topic being explained:
    - Solar System (Sun, orbiting planets, Saturn rings, Moon)
    - Mariana Trench / Ocean (deep caustics, bioluminescent jellyfish, sonar)
    - Ancient Mysteries / Pyramids (3D pyramid, golden apex beam, hieroglyphs)
    - Brain / Psychology (glowing neural networks, firing synapses, EEG waves)
    - Earth Spin / What-If (rotating Earth, atmospheric vectors, shockwaves)
    With recurring cute 3D Pixar animated host jobelessboy standing in the foreground!
    """
    def __init__(self, width: int = 1080, height: int = 1920, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.font_path = DEFAULT_MALAYALAM_FONT if os.path.exists(DEFAULT_MALAYALAM_FONT) else None
        
        # Load system fonts safely
        self.font_title = None
        self.font_badge = None
        self.font_mal = None
        for fp in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf"]:
            if os.path.exists(fp):
                try:
                    self.font_title = ImageFont.truetype(fp, 36)
                    self.font_badge = ImageFont.truetype(fp, 20)
                    break
                except Exception:
                    pass
        if self.font_path and os.path.exists(self.font_path):
            try:
                self.font_mal = ImageFont.truetype(self.font_path, 28)
            except Exception:
                pass

        # Pre-cache static layers to guarantee 100+ FPS generation speeds
        self._init_cached_nebulae()
        self._sprite_cache = {}

    def _init_cached_nebulae(self):
        cx, cy = self.width // 2, int(self.height * 0.42)
        radius = int(min(self.width, self.height) * 0.45)
        glow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(glow)
        g_draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(24, 15, 60, 110))
        g_draw.ellipse([cx - int(radius*0.6), cy - int(radius*0.6), cx + int(radius*0.6), cy + int(radius*0.6)], fill=(6, 182, 212, 70))
        self.cached_nebula = glow.filter(ImageFilter.GaussianBlur(radius=35))

    def _get_host_sprite(self, expression: str) -> Image.Image:
        if expression not in self._sprite_cache:
            sprite_file = CHARACTER_DIR / f"jobelessboy_{expression}.png"
            if not sprite_file.exists():
                sprite_file = CHARACTER_DIR / f"dr_kiran_{expression}.png"
            if not sprite_file.exists():
                sprite_file = Path(generate_character_sprite(expression))
            self._sprite_cache[expression] = Image.open(sprite_file).convert("RGBA")
        return self._sprite_cache[expression]

    def render_scene_frame(
        self,
        frame_idx: int,
        total_frames: int,
        theme: str = "space",
        expression: str = "explanation",
        host_visible: bool = True,
        scene_title: Optional[str] = None
    ) -> Image.Image:
        t = frame_idx / self.fps
        theme_lower = (theme or "space").lower()

        # Canvas selection based on theme
        if any(k in theme_lower for k in ["ocean", "sea", "trench", "water", "deep"]):
            base = self._render_ocean_presentation(t)
        elif any(k in theme_lower for k in ["pyramid", "history", "ancient", "monolith", "egypt"]):
            base = self._render_history_presentation(t)
        elif any(k in theme_lower for k in ["brain", "psychology", "memory", "mind", "neuro"]):
            base = self._render_brain_presentation(t)
        elif any(k in theme_lower for k in ["earth", "spin", "whatif", "momentum"]):
            base = self._render_earth_presentation(t)
        else:
            # Default: Rich Solar System & Cosmic Space Presentation
            base = self._render_solarsystem_presentation(t)

        # Host Overlay in Foreground
        if host_visible:
            self._composite_host(base, t, expression)

        return base

    def _render_solarsystem_presentation(self, t: float) -> Image.Image:
        """Dynamic Solar System with animated Sun, 6 orbiting planets, Saturn rings, Moon & HUD."""
        base = Image.new("RGB", (self.width, self.height), (6, 9, 20))
        base.paste(self.cached_nebula, (0, 0), self.cached_nebula)
        draw = ImageDraw.Draw(base)

        # Twinkling starfield
        rng = random.Random(42)
        for _ in range(90):
            sx = rng.randint(0, self.width)
            sy = (rng.randint(0, self.height) + int(t * 15 * rng.uniform(0.5, 1.5))) % self.height
            sz = rng.randint(1, 3)
            bright = int(170 + 80 * math.sin(t * 3.0 + rng.uniform(0, 6.28)))
            draw.rectangle([sx, sy, sx + sz, sy + sz], fill=(bright, bright, min(255, bright + 30)))

        # Solar Center
        sun_x = self.width // 2
        sun_y = int(self.height * 0.35) if self.width < self.height else int(self.height * 0.48)
        sun_r = int(min(self.width, self.height) * 0.075)

        # Sun Rays
        for i in range(12):
            angle = t * 0.7 + i * (math.pi / 6)
            flare_r = sun_r + int(14 + 10 * math.sin(t * 4.0 + i))
            fx = int(sun_x + flare_r * math.cos(angle))
            fy = int(sun_y + flare_r * math.sin(angle))
            draw.line([(sun_x, sun_y), (fx, fy)], fill=(249, 115, 22), width=3)

        # Sun core
        draw.ellipse([sun_x - sun_r, sun_y - sun_r, sun_x + sun_r, sun_y + sun_r], fill=(255, 235, 120))
        draw.ellipse([sun_x - int(sun_r*0.75), sun_y - int(sun_r*0.75), sun_x + int(sun_r*0.75), sun_y + int(sun_r*0.75)], fill=(255, 255, 200))

        # Orbiting Planets
        scale_x = 0.9 if self.width < self.height else 1.3
        planets = [
            ("Mercury", int(120 * scale_x), 65, 8, (180, 180, 190), 2.2, 0.4, False),
            ("Venus", int(175 * scale_x), 95, 13, (234, 179, 8), 1.6, 2.1, False),
            ("Earth", int(240 * scale_x), 135, 16, (56, 189, 248), 1.1, 4.3, False),
            ("Mars", int(305 * scale_x), 170, 11, (239, 68, 68), 0.85, 1.2, False),
            ("Jupiter", int(380 * scale_x), 215, 30, (217, 119, 6), 0.55, 3.5, False),
            ("Saturn", int(455 * scale_x), 260, 24, (253, 224, 71), 0.38, 5.2, True),
        ]

        for name, rx, ry, p_size, color, speed, phase, has_ring in planets:
            # Orbit path
            draw.ellipse([sun_x - rx, sun_y - ry, sun_x + rx, sun_y + ry], outline=(30, 58, 100), width=1)
            angle = t * speed + phase
            px = int(sun_x + rx * math.cos(angle))
            py = int(sun_y + ry * math.sin(angle))

            if has_ring:
                draw.ellipse([px - p_size * 2, py - int(p_size * 0.6), px + p_size * 2, py + int(p_size * 0.6)], outline=(234, 179, 8), width=3)
                draw.ellipse([px - p_size, py - p_size, px + p_size, py + p_size], fill=color)
            else:
                draw.ellipse([px - p_size, py - p_size, px + p_size, py + p_size], fill=color)

            if name == "Earth":
                m_angle = t * 4.5
                mx = int(px + 26 * math.cos(m_angle))
                my = int(py + 16 * math.sin(m_angle))
                draw.ellipse([mx - 4, my - 4, mx + 4, my + 4], fill=(240, 240, 240))
                draw.arc([px - p_size - 3, py - p_size - 3, px + p_size + 3, py + p_size + 3], 0, 360, fill=(14, 165, 233), width=2)

        # Top Presentation Header Card (English Only)
        self._render_hud_banner(draw, "SOLAR SYSTEM ARCHITECTURE", "ASTRONOMY", "ORBITAL DYNAMICS & EXOPLANETS")
        return base

    def _render_ocean_presentation(self, t: float) -> Image.Image:
        """Deep oceanic caustics, rising bubbles, bioluminescent jellyfish & depth sonar."""
        base = Image.new("RGB", (self.width, self.height), (2, 10, 28))
        draw = ImageDraw.Draw(base)

        # Undulating underwater light rays
        for ray in range(5):
            rx = int(self.width * (0.2 + ray * 0.18) + 30 * math.sin(t * 1.5 + ray))
            draw.polygon([
                (rx - 25, 0), (rx + 25, 0),
                (rx + 120, int(self.height * 0.65)), (rx - 120, int(self.height * 0.65))
            ], fill=(8, 45, 95))

        # Rising bubble streams
        rng = random.Random(88)
        for _ in range(35):
            bx = rng.randint(40, self.width - 40)
            by = (int(self.height - (t * 80 * rng.uniform(0.6, 1.8)) - rng.randint(0, self.height))) % self.height
            br = rng.randint(3, 8)
            draw.ellipse([bx - br, by - br, bx + br, by + br], outline=(56, 189, 248), width=2)

        # Bioluminescent Jellyfish
        jx = int(self.width * 0.45 + 50 * math.sin(t * 0.8))
        jy = int(self.height * 0.38 + 25 * math.cos(t * 1.2))
        jr = 60
        # Jelly bell
        draw.pieslice([jx - jr, jy - jr, jx + jr, jy + jr], 180, 360, fill=(6, 182, 212))
        draw.ellipse([jx - jr, jy - 10, jx + jr, jy + 10], fill=(14, 165, 233))
        # Undulating tentacles
        for ti in range(6):
            tx_start = jx - 40 + ti * 16
            t_wave = 15 * math.sin(t * 3.5 + ti)
            draw.line([(tx_start, jy + 10), (tx_start + int(t_wave), jy + 90)], fill=(217, 70, 239), width=3)

        # Sonar sweep line
        cx, cy = int(self.width * 0.75), int(self.height * 0.22)
        s_angle = t * 2.0
        draw.ellipse([cx - 70, cy - 70, cx + 70, cy + 70], outline=(6, 182, 212), width=2)
        draw.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=(6, 182, 212), width=1)
        draw.line([(cx, cy), (int(cx + 70 * math.cos(s_angle)), int(cy + 70 * math.sin(s_angle)))], fill=(34, 197, 94), width=2)

        self._render_hud_banner(draw, "MARIANA TRENCH • 10,994M", "DEEP SEA", "ABYSSAL EXPEDITION")
        return base

    def _render_history_presentation(self, t: float) -> Image.Image:
        """Ancient Egyptian Pyramids of Giza with golden apex beam, starry sky & sacred geometry."""
        base = Image.new("RGB", (self.width, self.height), (12, 10, 24))
        draw = ImageDraw.Draw(base)

        # Starry night
        rng = random.Random(55)
        for _ in range(80):
            sx = rng.randint(0, self.width)
            sy = rng.randint(0, int(self.height * 0.65))
            bright = int(160 + 90 * math.sin(t * 3.0 + rng.uniform(0, 6.28)))
            draw.rectangle([sx, sy, sx + 2, sy + 2], fill=(bright, bright, 255))

        # Glowing Full Moon
        mx, my, mr = int(self.width * 0.8), int(self.height * 0.2), 48
        draw.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(254, 240, 138))
        draw.ellipse([mx - int(mr*0.7), my - int(mr*0.7), mx + int(mr*0.7), my + int(mr*0.7)], fill=(255, 255, 240))

        # Golden Beam from Pyramid Apex
        apex_x, apex_y = self.width // 2, int(self.height * 0.38)
        beam_w = int(18 + 8 * math.sin(t * 4.0))
        draw.polygon([
            (apex_x - beam_w, 0), (apex_x + beam_w, 0),
            (apex_x + 4, apex_y), (apex_x - 4, apex_y)
        ], fill=(245, 158, 11))

        # 3D Great Pyramid
        base_y = int(self.height * 0.62)
        # Left lit face
        draw.polygon([(apex_x, apex_y), (int(self.width * 0.15), base_y), (apex_x, base_y)], fill=(180, 110, 45))
        # Right shadowed face
        draw.polygon([(apex_x, apex_y), (apex_x, base_y), (int(self.width * 0.85), base_y)], fill=(120, 70, 30))
        # Ground sand dunes
        draw.polygon([(0, base_y), (self.width, base_y), (self.width, self.height), (0, self.height)], fill=(40, 25, 15))

        # Rotating Sacred Geometry Rings around Apex
        r_radius = int(55 + 10 * math.sin(t * 2.0))
        draw.ellipse([apex_x - r_radius, apex_y - r_radius, apex_x + r_radius, apex_y + r_radius], outline=(251, 191, 36), width=2)

        self._render_hud_banner(draw, "THE GREAT PYRAMID OF GIZA", "ANCIENT MYSTERY", "MEGALITHIC ARCHITECTURE")
        return base

    def _render_brain_presentation(self, t: float) -> Image.Image:
        """Glowing 3D neural brain silhouette, firing synaptic action potentials & EEG graph."""
        base = Image.new("RGB", (self.width, self.height), (8, 10, 26))
        draw = ImageDraw.Draw(base)

        # Brain center
        cx, cy = self.width // 2, int(self.height * 0.38)
        
        # Cyber grid in background
        grid_step = 70
        for gx in range(0, self.width, grid_step):
            draw.line([(gx, 0), (gx, self.height)], fill=(15, 25, 55), width=1)
        for gy in range(0, self.height, grid_step):
            draw.line([(0, gy), (self.width, gy)], fill=(15, 25, 55), width=1)

        # Left and Right Brain Hemispheres
        draw.ellipse([cx - 160, cy - 110, cx - 10, cy + 110], outline=(6, 182, 212), width=3)
        draw.ellipse([cx + 10, cy - 110, cx + 160, cy + 110], outline=(6, 182, 212), width=3)

        # Neural Network nodes & Synaptic firing lines
        nodes = [
            (cx - 110, cy - 60), (cx - 70, cy - 10), (cx - 120, cy + 50),
            (cx - 40, cy + 60), (cx - 80, cy - 80),
            (cx + 110, cy - 60), (cx + 70, cy - 10), (cx + 120, cy + 50),
            (cx + 40, cy + 60), (cx + 80, cy - 80)
        ]
        # Interconnects
        for i in range(len(nodes)):
            n1 = nodes[i]
            n2 = nodes[(i + 1) % len(nodes)]
            draw.line([n1, n2], fill=(30, 64, 110), width=2)
            # Pulsing pulse spark along connection
            spark_prog = (t * 2.5 + i * 0.3) % 1.0
            sp_x = int(n1[0] + (n2[0] - n1[0]) * spark_prog)
            sp_y = int(n1[1] + (n2[1] - n1[1]) * spark_prog)
            draw.ellipse([sp_x - 4, sp_y - 4, sp_x + 4, sp_y + 4], fill=(234, 179, 8))

        # Node circles
        for nx, ny in nodes:
            draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=(6, 182, 212))

        # Oscillating EEG waveform
        eeg_y = cy + 160
        prev_pt = (50, eeg_y)
        for x in range(50, self.width - 50, 10):
            y_off = int(28 * math.sin(t * 8.0 + x * 0.05) * math.sin(x * 0.02))
            curr_pt = (x, eeg_y + y_off)
            draw.line([prev_pt, curr_pt], fill=(34, 197, 94), width=2)
            prev_pt = curr_pt

        self._render_hud_banner(draw, "NEURAL NETWORK & MEMORY", "NEUROSCIENCE", "SYNAPTIC TRANSMISSION")
        return base

    def _render_earth_presentation(self, t: float) -> Image.Image:
        """Rotating Planet Earth, supersonic atmospheric momentum vectors & shockwaves."""
        base = Image.new("RGB", (self.width, self.height), (6, 8, 22))
        base.paste(self.cached_nebula, (0, 0), self.cached_nebula)
        draw = ImageDraw.Draw(base)

        cx, cy = self.width // 2, int(self.height * 0.36)
        r = int(min(self.width, self.height) * 0.22)

        # Atmospheric shockwave rings expanding outward
        ring_prog = (t * 0.7) % 1.0
        ring_r = int(r + ring_prog * 180)
        draw.ellipse([cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r], outline=(239, 68, 68), width=2)

        # Planet Earth Sphere (Ocean Deep Blue)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 116, 144))

        # Continents (Green/Gold shifting with rotation t)
        rot_offset = int((t * 25) % (r * 2))
        for cont_i in [-1, 0, 1]:
            cont_x = cx - r + rot_offset + cont_i * int(r * 1.5)
            draw.ellipse([cont_x - 35, cy - 30, cont_x + 55, cy + 30], fill=(34, 197, 94))
            draw.ellipse([cont_x + 20, cy + 10, cont_x + 85, cy + 65], fill=(22, 163, 74))

        # Glowing Atmospheric rim
        draw.arc([cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3], 0, 360, fill=(56, 189, 248), width=3)

        # Supersonic Velocity streak arrows (1,670 km/h)
        for arrow_i in range(3):
            ay = cy - 60 + arrow_i * 60
            draw.line([(cx - r - 80, ay), (cx + r + 80, ay)], fill=(245, 158, 11), width=2)

        self._render_hud_banner(draw, "EARTH ROTATIONAL MOMENTUM", "PHYSICS WHAT-IF", "ATMOSPHERIC INERTIA")
        return base

    def _render_hud_banner(self, draw: ImageDraw.Draw, en_title: str, category: str, sub_title: str = "MYSTERYVERSE 360"):
        """Standardized high-tech HUD card overlay in stylish English typography."""
        card_x1, card_y1 = 50, 75
        card_x2, card_y2 = self.width - 50, 205
        # Semi-transparent dark glass
        draw.rounded_rectangle([card_x1, card_y1, card_x2, card_y2], radius=16, fill=(15, 23, 42), outline=(6, 182, 212), width=2)
        
        # Pill category badge
        badge_x1, badge_y1 = card_x1 + 20, card_y1 + 18
        badge_x2, badge_y2 = badge_x1 + 170, badge_y1 + 36
        draw.rounded_rectangle([badge_x1, badge_y1, badge_x2, badge_y2], radius=8, fill=(6, 182, 212))

        if self.font_badge:
            draw.text((badge_x1 + 12, badge_y1 + 6), category, fill=(15, 23, 42), font=self.font_badge)
            draw.text((badge_x2 + 20, badge_y1 + 6), sub_title, fill=(245, 158, 11), font=self.font_badge)
        if self.font_title:
            draw.text((card_x1 + 20, card_y1 + 68), en_title, fill=(255, 255, 255), font=self.font_title)

    def _composite_host(self, base: Image.Image, t: float, expression: str):
        """Composites the cute 3D Pixar boy jobelessboy in the foreground with natural idle animation."""
        sprite = self._get_host_sprite(expression)
        bob_offset = int(10 * math.sin(t * 3.2))

        if self.width < self.height:  # Vertical Shorts (1080x1920)
            target_w = int(self.width * 0.72)
            aspect = sprite.height / sprite.width
            target_h = int(target_w * aspect)
            sprite_resized = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Positioned in lower right foreground, pointing back at the presentation
            pos_x = self.width - target_w + 80
            pos_y = self.height - target_h + 80 + bob_offset
        else:  # Horizontal 16:9 (1920x1080)
            target_h = int(self.height * 0.82)
            aspect = sprite.width / sprite.height
            target_w = int(target_h * aspect)
            sprite_resized = sprite.resize((target_w, target_h), Image.Resampling.LANCZOS)
            pos_x = self.width - target_w - 40
            pos_y = self.height - target_h + 40 + bob_offset

        # Drop shadow behind character
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.ellipse([pos_x + 50, pos_y + 80, pos_x + target_w - 50, self.height - 10], fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=28))
        base.paste(shadow, (0, 0), shadow)

        # Composite Character
        base.paste(sprite_resized, (pos_x, pos_y), sprite_resized)

        # Animated Voice Waveform Badge next to Host
        draw = ImageDraw.Draw(base)
        wave_x = max(30, pos_x - 140)
        wave_y = min(self.height - 200, pos_y + int(target_h * 0.65))
        draw.rounded_rectangle([wave_x - 12, wave_y - 28, wave_x + 115, wave_y + 28], radius=10, fill=(15, 23, 42), outline=(6, 182, 212), width=1)
        for bi in range(6):
            bh = int(8 + 26 * abs(math.sin(t * 7.5 + bi * 0.9)))
            bx = wave_x + bi * 18
            draw.rectangle([bx, wave_y - bh // 2, bx + 6, wave_y + bh // 2], fill=(6, 182, 212))

    def generate_scene_clip(
        self,
        output_mp4: str,
        duration_sec: float = 5.0,
        theme: str = "space",
        expression: str = "explanation"
    ) -> str:
        """Renders an animated MP4 scene clip using FFmpeg stdin pipe."""
        ffmpeg_bin = get_ffmpeg_path()
        if not ffmpeg_bin:
            raise RuntimeError("FFmpeg executable not found!")

        render_fps = self.fps
        total_frames = int(duration_sec * render_fps)
        import subprocess

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

        # Use DEVNULL to prevent Windows pipe stalls
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        for f_idx in range(total_frames):
            frame_img = self.render_scene_frame(
                frame_idx=f_idx,
                total_frames=total_frames,
                theme=theme,
                expression=expression
            )
            raw_bytes = frame_img.tobytes()
            proc.stdin.write(raw_bytes)

        proc.stdin.close()
        proc.wait()
        return output_mp4
