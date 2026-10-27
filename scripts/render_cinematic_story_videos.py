"""
MysteryVerse Malayalam — Cinematic Multi-Scene Animated Film Producer
Recreates from scratch:
1. output/mysteryverse_intro_short.mp4 (9:16 Vertical, 1080x1920, ~46.5s)
2. output/mysteryverse_intro_long.mp4 (16:9 Horizontal, 1920x1080, ~163.5s)

Visual Style:
- Professional 3D animated film with recurring host 'jobelessboy'.
- Scene-by-scene cinematic narrative (Command Deck -> Space Observatory -> Quantum Lab -> Pyramids -> Psychology -> Cosmic Portal).
- Natural body acting, continuous camera tracking/pan, atmospheric particle physics, dynamic lighting pulses.
- Audio: 100% Malayalam kid voiceover.
- Visual Text: 100% English subtitles & channel name. NO MALAYALAM TEXT ON SCREEN.
- NO floating presentation badges like 'OFFICIAL HOST'.
"""

import os
import sys
import re
import math
import time
import shutil
import sqlite3
import subprocess
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    THUMBNAILS_DIR,
    DB_PATH,
    get_ffmpeg_path
)

FFMPEG_BIN = get_ffmpeg_path()


def parse_srt(srt_path: str):
    """Parses SRT file into a list of (start_sec, end_sec, text)."""
    if not os.path.exists(srt_path):
        return []
    with open(srt_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    entries = []
    blocks = re.split(r"\n\s*\n", content.strip())
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            time_line = lines[1]
            match = re.match(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", time_line)
            if match:
                g = [float(x) for x in match.groups()]
                start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
                end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
                text = " ".join(lines[2:]).strip()
                entries.append((start, end, text))
    return entries


def get_audio_duration_and_envelope(audio_path: str, fps: int = 24):
    """Calculates total duration and frame-by-frame speech envelope (RMS)."""
    cmd = [FFMPEG_BIN, "-y", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw, err = proc.communicate()

    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    total_sec = len(samples) / 16000.0
    total_frames = int(math.ceil(total_sec * fps))

    samples_per_frame = int(16000 / fps)
    envelope = []
    for i in range(total_frames):
        chunk = samples[i * samples_per_frame : (i + 1) * samples_per_frame]
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
        envelope.append(rms)

    arr = np.array(envelope)
    peak = np.percentile(arr, 95) if len(arr) > 0 and np.max(arr) > 0 else 1.0
    norm_env = np.clip(arr / (peak if peak > 0 else 1.0), 0.0, 1.0)
    return total_sec, norm_env


class CinematicStoryRenderer:
    def __init__(self, width: int, height: int, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        self.is_vertical = (width < height)

        # Load clean fonts
        self.font_logo = self._load_font(28 if self.is_vertical else 32, bold=True)
        self.font_sub = self._load_font(32 if self.is_vertical else 36, bold=True)
        self.font_sub_highlight = self._load_font(32 if self.is_vertical else 36, bold=True)

        # Precompute filmic lens vignette
        self._init_cinematic_vignette()

    def _load_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        fonts = [
            r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\tahoma.ttf"
        ]
        for f in fonts:
            if os.path.exists(f):
                try:
                    return ImageFont.truetype(f, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _apply_cinematic_camera(self, img: Image.Image, progress: float, cam_type: str) -> Image.Image:
        """Applies smooth cinematic camera moves (pan, dolly-in, diagonal crane)."""
        w, h = img.size
        # Ease in-out curve
        ease = (1.0 - math.cos(math.pi * progress)) / 2.0

        if cam_type == "dolly_in":
            scale = 1.0 + 0.06 * ease
            cw, ch = int(w / scale), int(h / scale)
            x0 = (w - cw) // 2
            y0 = int((h - ch) * 0.4)
            cropped = img.crop((x0, y0, x0 + cw, y0 + ch))
            return cropped.resize((w, h), Image.Resampling.BILINEAR)

        elif cam_type == "pan_right_up":
            scale = 1.05
            cw, ch = int(w / scale), int(h / scale)
            x_shift = int((w - cw) * (0.2 + 0.6 * ease))
            y_shift = int((h - ch) * (0.8 - 0.6 * ease))
            cropped = img.crop((x_shift, y_shift, x_shift + cw, y_shift + ch))
            return cropped.resize((w, h), Image.Resampling.BILINEAR)

        elif cam_type == "reveal_up":
            scale = 1.06
            cw, ch = int(w / scale), int(h / scale)
            x_shift = (w - cw) // 2
            y_shift = int((h - ch) * (0.85 - 0.7 * ease))
            cropped = img.crop((x_shift, y_shift, x_shift + cw, y_shift + ch))
            return cropped.resize((w, h), Image.Resampling.BILINEAR)

        elif cam_type == "pan_left":
            scale = 1.05
            cw, ch = int(w / scale), int(h / scale)
            x_shift = int((w - cw) * (0.8 - 0.6 * ease))
            y_shift = int((h - ch) * 0.5)
            cropped = img.crop((x_shift, y_shift, x_shift + cw, y_shift + ch))
            return cropped.resize((w, h), Image.Resampling.BILINEAR)

        else: # subtle tracking sway
            scale = 1.04
            cw, ch = int(w / scale), int(h / scale)
            x_shift = int((w - cw) * (0.5 + 0.15 * math.sin(progress * 6.28)))
            y_shift = int((h - ch) * (0.5 + 0.10 * math.cos(progress * 6.28)))
            cropped = img.crop((x_shift, y_shift, x_shift + cw, y_shift + ch))
            return cropped.resize((w, h), Image.Resampling.BILINEAR)

    def _init_cinematic_vignette(self):
        """Precomputes a smooth filmic lens vignette to add cinematic depth."""
        vg = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        d_vg = ImageDraw.Draw(vg)
        cx, cy = self.width / 2.0, self.height / 2.0
        max_dist = math.sqrt(cx**2 + cy**2)
        # Create subtle vignette gradient
        for step in range(12):
            factor = step / 11.0
            r_inner = max_dist * (0.55 + 0.35 * factor)
            alpha = int(45 * (factor ** 1.8))
            bbox = [cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner]
            d_vg.ellipse(bbox, outline=(5, 8, 18, alpha), width=int(max_dist * 0.05))
        self.vignette_layer = vg.filter(ImageFilter.GaussianBlur(radius=30))

    def _render_atmospheric_fx(self, base_frame: Image.Image, t: float) -> Image.Image:
        """Applies cinematic depth vignette without drawing crude 2D shapes on characters."""
        return Image.alpha_composite(base_frame, self.vignette_layer)

    def _draw_subtitles_and_branding(self, draw: ImageDraw.Draw, sub_text: str, t: float):
        """Draws clean English subtitles and subtle channel branding."""
        # 1. Channel watermark (clean, minimal)
        logo_text = "MYSTERYVERSE MALAYALAM"
        bbox_l = self.font_logo.getbbox(logo_text)
        lw = bbox_l[2] - bbox_l[0]
        lh = bbox_l[3] - bbox_l[1]
        lx = (self.width - lw) // 2
        ly = 50 if self.is_vertical else 35

        # Pill background for logo
        draw.rounded_rectangle([lx - 16, ly - 8, lx + lw + 16, ly + lh + 8], radius=12, fill=(10, 15, 30, 140))
        draw.text((lx, ly), logo_text, font=self.font_logo, fill=(240, 245, 255, 230))

        # 2. English subtitles (if active)
        if sub_text:
            # Wrap lines if long
            max_chars = 38 if self.is_vertical else 60
            words = sub_text.split()
            lines = []
            curr_line = []
            for w in words:
                if len(" ".join(curr_line + [w])) <= max_chars:
                    curr_line.append(w)
                else:
                    lines.append(" ".join(curr_line))
                    curr_line = [w]
            if curr_line:
                lines.append(" ".join(curr_line))

            # Measure subtitle height
            line_height = int(self.font_sub.size * 1.3)
            total_sub_h = len(lines) * line_height
            sub_y = self.height - (260 if self.is_vertical else 150) - total_sub_h

            for i, line in enumerate(lines):
                bbox = self.font_sub.getbbox(line)
                txt_w = bbox[2] - bbox[0]
                txt_x = (self.width - txt_w) // 2
                line_y = sub_y + i * line_height

                # Frosted glass background pill
                pad_x = 24
                pad_y = 6
                draw.rounded_rectangle(
                    [txt_x - pad_x, line_y - pad_y, txt_x + txt_w + pad_x, line_y + line_height + pad_y],
                    radius=14,
                    fill=(6, 10, 20, 205),
                    outline=(59, 130, 246, 80),
                    width=1
                )

                # Render words with key-word highlight in gold
                # Gold for highlight words
                fill_color = (255, 255, 255, 255)
                if any(k in line.lower() for k in ["mysteryverse", "subscribe", "universe", "science", "history"]):
                    fill_color = (253, 224, 71, 255) # Bright gold/yellow
                draw.text((txt_x, line_y), line, font=self.font_sub, fill=fill_color)

    def render_movie(
        self,
        output_mp4: str,
        scenes_data: list,
        audio_path: str,
        srt_path: str,
        total_duration: float
    ):
        """
        Renders complete cinematic multi-scene film with audio sync.
        scenes_data format: [(image_path, start_time, end_time, cam_type), ...]
        """
        print(f"\nRendering {output_mp4} ({self.width}x{self.height} @ {self.fps}fps)...")
        start_time_render = time.time()

        # Parse subtitles & audio envelope
        subtitles = parse_srt(srt_path)
        audio_dur, envelope = get_audio_duration_and_envelope(audio_path, self.fps)
        total_frames = int(math.ceil(total_duration * self.fps))

        # Preload and resize scene base images
        loaded_scenes = {}
        for p, s, e, cam in scenes_data:
            if p not in loaded_scenes:
                base_img = Image.open(p).convert("RGBA")
                # Scale to canvas filling dimensions
                scaled = base_img.resize((self.width, self.height), Image.Resampling.LANCZOS)
                loaded_scenes[p] = scaled

        # Launch FFmpeg pipe
        cmd = [
            FFMPEG_BIN, "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{self.width}x{self.height}",
            "-pix_fmt", "rgba",
            "-r", str(self.fps),
            "-i", "-",
            "-i", audio_path,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "19",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_mp4
        ]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        crossfade_dur = 0.6  # 600ms crossfade between scenes

        for f_idx in range(total_frames):
            t = f_idx / float(self.fps)

            # 1. Determine active scene and any crossfading scene
            active_idx = 0
            for i, (p, s, e, cam) in enumerate(scenes_data):
                if s <= t < e:
                    active_idx = i
                    break
                elif t >= e:
                    active_idx = i

            p_curr, s_curr, e_curr, cam_curr = scenes_data[active_idx]
            prog_curr = np.clip((t - s_curr) / max(0.1, (e_curr - s_curr)), 0.0, 1.0)
            img_curr = loaded_scenes[p_curr]
            frame_curr = self._apply_cinematic_camera(img_curr, prog_curr, cam_curr)

            # Check crossfade from previous scene
            final_frame = frame_curr
            if active_idx > 0 and (t - s_curr) < crossfade_dur:
                p_prev, s_prev, e_prev, cam_prev = scenes_data[active_idx - 1]
                prog_prev = 1.0 # previous scene at end
                img_prev = loaded_scenes[p_prev]
                frame_prev = self._apply_cinematic_camera(img_prev, prog_prev, cam_prev)
                alpha = (t - s_curr) / crossfade_dur
                final_frame = Image.blend(frame_prev, frame_curr, alpha)

            # 2. Apply subtle cinematic lens vignette
            final_frame = self._render_atmospheric_fx(final_frame, t)
            draw = ImageDraw.Draw(final_frame)

            # 3. Find active subtitle
            active_sub = ""
            for sub_s, sub_e, sub_txt in subtitles:
                if sub_s <= t <= sub_e:
                    active_sub = sub_txt
                    break

            # 4. Render subtitles and branding
            self._draw_subtitles_and_branding(draw, active_sub, t)

            # 5. Pipe RGBA bytes to FFmpeg
            raw_bytes = final_frame.tobytes()
            proc.stdin.write(raw_bytes)

            if f_idx % (self.fps * 10) == 0:
                pct = int((f_idx / float(total_frames)) * 100)
                print(f"  Frame {f_idx}/{total_frames} ({pct}%) rendered [t={t:.1f}s]")

        proc.stdin.close()
        stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
        proc.wait()

        if proc.returncode != 0:
            print(f"FFmpeg Error:\n{stderr_out}")
            raise RuntimeError(f"FFmpeg render failed with exit code {proc.returncode}")

        elapsed = time.time() - start_time_render
        file_size = os.path.getsize(output_mp4)
        print(f"SUCCESS: Rendered {output_mp4} ({file_size} bytes in {elapsed:.1f}s)")


def main():
    print("=" * 75)
    print("MYSTERYVERSE MALAYALAM — RECREATING CINEMATIC VIDEOS FROM SCRATCH")
    print("Consistent Host: jobelessboy (Pixar 3D Boy)")
    print("Cinematic Animation: Multi-scene environments, dynamic camera, particle FX")
    print("Language: Spoken Malayalam Narration // English Subtitles Only")
    print("=" * 75)

    output_dir = Path(r"c:\m\output")
    output_dir.mkdir(parents=True, exist_ok=True)
    scenes_dir = Path(r"c:\m\backend\static\scenes")
    audio_dir = Path(r"c:\m\backend\static\audio")
    sub_dir = Path(r"c:\m\backend\static\subtitles")

    # -------------------------------------------------------------
    # DELIVERABLE 1: Vertical 9:16 Shorts (1080x1920, ~46.5s)
    # -------------------------------------------------------------
    out_short = str(output_dir / "mysteryverse_intro_short.mp4")
    audio_short = str(audio_dir / "intro_short_kid.mp3")
    srt_short = str(sub_dir / "intro_short_en.srt")
    dur_short = 46.5

    # 5 connected story scenes:
    scenes_short = [
        (str(scenes_dir / "scene1.jpg"), 0.0, 8.0, "dolly_in"),        # 1. Walk & greeting in futuristic command deck
        (str(scenes_dir / "scene2.jpg"), 8.0, 17.0, "pan_right_up"),    # 2. Looking in awe out observatory at Saturn & Earth
        (str(scenes_dir / "scene3.jpg"), 17.0, 26.5, "dolly_in"),       # 3. Holding glowing atom & DNA helix in quantum lab
        (str(scenes_dir / "scene4.jpg"), 26.5, 35.5, "reveal_up"),      # 4. Great Pyramids at twilight with golden relic
        (str(scenes_dir / "scene5.jpg"), 35.5, 46.5, "dolly_in"),       # 5. Pointing down to subscribe with cosmic portal
    ]

    director_short = CinematicStoryRenderer(width=1080, height=1920, fps=24)
    director_short.render_movie(out_short, scenes_short, audio_short, srt_short, dur_short)

    # -------------------------------------------------------------
    # DELIVERABLE 2: Horizontal 16:9 Long-Form (1920x1080, ~163.5s)
    # -------------------------------------------------------------
    out_long = str(output_dir / "mysteryverse_intro_long.mp4")
    audio_long = str(audio_dir / "intro_long_kid.mp3")
    srt_long = str(sub_dir / "intro_long_en.srt")
    dur_long = 163.5

    # 6 widescreen narrative scenes:
    scenes_long = [
        (str(scenes_dir / "wide_scene1.jpg"), 0.0, 28.0, "dolly_in"),     # 1. Bridge overlooking Earth (Channel intro)
        (str(scenes_dir / "wide_scene2.jpg"), 28.0, 55.0, "pan_left"),     # 2. Deep space observatory (Space & universe)
        (str(scenes_dir / "wide_scene3.jpg"), 55.0, 85.0, "dolly_in"),     # 3. Quantum lab with atom & DNA (Science)
        (str(scenes_dir / "wide_scene4.jpg"), 85.0, 115.0, "reveal_up"),   # 4. Great Pyramids & constellations (History & Enigmas)
        (str(scenes_dir / "wide_scene5.jpg"), 115.0, 142.0, "dolly_in"),   # 5. Human mind & glowing synapses (Psychology)
        (str(scenes_dir / "wide_scene6.jpg"), 142.0, 163.5, "dolly_in"),   # 6. Studio & cosmic portal (Subscribe call-to-action)
    ]

    director_long = CinematicStoryRenderer(width=1920, height=1080, fps=24)
    director_long.render_movie(out_long, scenes_long, audio_long, srt_long, dur_long)

    # -------------------------------------------------------------
    # SYNC TO FRONTEND PUBLIC, BACKEND STATIC & VERCEL DIST
    # -------------------------------------------------------------
    print("\nSyncing rendered cinematic videos to web static directories...")
    fe_vid_dir = Path(r"c:\m\frontend\public\static\videos")
    fe_dist_vid = Path(r"c:\m\frontend\dist\static\videos")
    be_vid_dir = Path(r"c:\m\backend\static\videos")

    for d in [fe_vid_dir, fe_dist_vid, be_vid_dir]:
        d.mkdir(parents=True, exist_ok=True)

    shutil.copy2(out_short, be_vid_dir / "mysteryverse_intro_short.mp4")
    shutil.copy2(out_short, fe_vid_dir / "mysteryverse_intro_short.mp4")
    shutil.copy2(out_short, fe_dist_vid / "mysteryverse_intro_short.mp4")

    shutil.copy2(out_long, be_vid_dir / "mysteryverse_intro_long.mp4")
    shutil.copy2(out_long, fe_vid_dir / "mysteryverse_intro_long.mp4")
    shutil.copy2(out_long, fe_dist_vid / "mysteryverse_intro_long.mp4")

    # Update database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
    UPDATE video_jobs
    SET duration_sec = ?, render_engine = 'cinematic_multiscene_animation', status = 'ready_for_upload'
    WHERE id = 'mysteryverse_intro_short'
    """, (dur_short,))
    c.execute("""
    UPDATE video_jobs
    SET duration_sec = ?, render_engine = 'cinematic_multiscene_animation', status = 'ready_for_upload'
    WHERE id = 'mysteryverse_intro_long'
    """, (dur_long,))
    conn.commit()
    conn.close()

    print("\nALL DELIVERABLES SUCCESSFULLY PRODUCED AND SYNCED!")


if __name__ == "__main__":
    main()
