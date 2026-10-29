"""
MysteryVerse Malayalam — Cinematic Character Animation Test
Renders an authentic, playable MP4 character test video (1920x1080, 30fps):
- Official 3D host: jobelessboy
- Cinematic space observatory environment
- Multi-layer optical parallax & slow camera push-in
- Natural breathing & posture micro-sway
- Smooth dialogue-synchronized lip-sync (audio RMS speech envelope)
- Natural eye blink cycle
- Authentic Malayalam neural narration: 'നമസ്കാരം കൂട്ടുകാരേ!'
- Clean white English subtitles: 'Hello, friends!' (no black boxes)
- Zero Malayalam text on screen
"""

import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"c:\m\backend")
from app.config import get_ffmpeg_path

FFMPEG_BIN = get_ffmpeg_path()
OUT_DIR = r"c:\m\output"
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(r"c:\m\output\preview_frames", exist_ok=True)

AUDIO_PATH = r"c:\m\output\audio\character_test_padded.wav"
CHAR_DIR = r"c:\m\backend\static\character"
SCENES_DIR = r"c:\m\backend\static\scenes\layers"

# 1. Preload character layers
img_welcome = Image.open(os.path.join(CHAR_DIR, "jobelessboy_welcome.png")).convert("RGBA")
img_blink = Image.open(os.path.join(CHAR_DIR, "jobelessboy_blink.png")).convert("RGBA")
img_talking = Image.open(os.path.join(CHAR_DIR, "jobelessboy_talking_wide.png")).convert("RGBA")
img_bg_base = Image.open(os.path.join(SCENES_DIR, "wide_scene1_bg.jpg")).convert("RGBA")

# 2. Extract mouth patches
mouth_box = (380, 430, 560, 550)
mw, mh = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]
mask_mouth = Image.new("L", (mw, mh), 0)
d_m = ImageDraw.Draw(mask_mouth)
d_m.ellipse([10, 12, mw - 10, mh - 12], fill=255)
mask_mouth = mask_mouth.filter(ImageFilter.GaussianBlur(radius=8))

mouth_open = img_talking.crop(mouth_box)
mouth_closed = img_welcome.crop(mouth_box)

# 3. Extract eye blink band
eye_band = (340, 280, 670, 410)
bw, bh = eye_band[2] - eye_band[0], eye_band[3] - eye_band[1]
mask_band = Image.new("L", (bw, bh), 255)
# Soften outer boundary
for border_step in range(8):
    b_alpha = int(255 * (border_step / 8.0))
    d_b = ImageDraw.Draw(mask_band)
    d_b.rectangle([border_step, border_step, bw - border_step, bh - border_step], outline=b_alpha)
mask_band = mask_band.filter(ImageFilter.GaussianBlur(radius=6))
blink_crop = img_blink.crop(eye_band)


def get_audio_envelope(audio_path, fps=30):
    cmd = [FFMPEG_BIN, "-y", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw, _ = proc.communicate()
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
    norm = np.clip(arr / (peak if peak > 0 else 1.0), 0.0, 1.0)
    return total_sec, norm


def render_test_frame(width, height, t, progress, speech_rms, blink_progress):
    """
    Renders 1 frame (1920x1080) with:
    - Cinematic camera push-in
    - Multi-plane optical depth
    - Natural breathing sway
    - Speech-synchronized lip-flap
    - Natural ease-in/out eyelid blinking
    - Safe white English subtitle
    """
    # 1. Camera Zoom / Dolly Factor
    cam_scale = 1.0 + 0.05 * progress

    # 2. Background with slow optical drift
    bg_w, bg_h = img_bg_base.size
    crop_w = int(bg_w / cam_scale)
    crop_h = int(bg_h / cam_scale)
    # Slow drift leftwards to simulate satellite orbit
    drift_x = int((bg_w - crop_w) * (0.50 + 0.15 * progress))
    drift_y = int((bg_h - crop_h) * 0.50)
    bg_cropped = img_bg_base.crop((drift_x, drift_y, drift_x + crop_w, drift_y + crop_h))
    frame = bg_cropped.resize((width, height), Image.Resampling.LANCZOS)

    # 3. Construct Character Face with Lip Sync and Blink
    char_base = img_welcome.copy()

    # Apply Lip Sync
    if speech_rms > 0.10:
        mouth_alpha = int(min(255, speech_rms * 280))
        scaled_mask = mask_mouth.point(lambda p: int(p * (mouth_alpha / 255.0)))
        char_base.paste(mouth_open, mouth_box, scaled_mask)

    # Apply Eye Blink with smooth interpolation
    if blink_progress > 0.05:
        # Scale eye band mask by blink factor
        blink_mask = mask_band.point(lambda p: int(p * blink_progress))
        char_base.paste(blink_crop, eye_band, blink_mask)

    # 4. Breathing & Posture Sway
    sway_y = int(5.0 * math.sin(t * 2.5))
    sway_x = int(3.0 * math.cos(t * 1.8))
    char_tilt = math.sin(t * 2.0) * 0.5  # Subtle 0.5 deg head angle

    # Character Dimensions: scale to ~94% height in 16:9
    ch_h = int(height * 0.94 * cam_scale)
    ch_w = int(char_base.width * (ch_h / char_base.height))
    char_resized = char_base.resize((ch_w, ch_h), Image.Resampling.LANCZOS)
    if abs(char_tilt) > 0.1:
        char_resized = char_resized.rotate(char_tilt, resample=Image.Resampling.BICUBIC, expand=False)

    pos_x = (width - ch_w) // 2 + 80 + sway_x
    pos_y = height - ch_h + 30 + sway_y

    frame.alpha_composite(char_resized, (pos_x, pos_y))

    # 5. Drifting Foreground Dust / Light motes (Parallax depth)
    draw = ImageDraw.Draw(frame)
    np.random.seed(42)
    for i in range(30):
        dx = int((np.random.rand() * width * 1.2 + t * 50.0) % (width + 60)) - 30
        dy = int((np.random.rand() * height + t * 25.0 * (1 + (i % 2))) % height)
        dr = 2 + (i % 3)
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr], fill=(255, 255, 255, 80))

    # 6. Clean White English Subtitle (Safe margin, subtle drop-shadow)
    # Spoken audio is active between approx t=0.5s and t=2.8s
    if 0.5 <= t <= 2.9:
        sub_text = "Hello, friends!"
        font_path = r"C:\Windows\Fonts\segoeuib.ttf"
        try:
            font = ImageFont.truetype(font_path, 40)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), sub_text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = (width - tw) // 2
        ty = height - 120

        # Subtle dark shadow for readability
        for off_x, off_y in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
            draw.text((tx + off_x, ty + off_y), sub_text, font=font, fill=(0, 0, 0, 200))
        # Pure crisp white text
        draw.text((tx, ty), sub_text, font=font, fill=(255, 255, 255, 255))

    return frame.convert("RGB")


def main():
    print("Generating Cinematic Character Test Video...")
    fps = 30
    width = 1920
    height = 1080

    total_sec, envelope = get_audio_envelope(AUDIO_PATH, fps=fps)
    total_frames = len(envelope)
    print(f"Total audio duration: {total_sec:.2f}s, frames: {total_frames}")

    frames_dir = os.path.join(OUT_DIR, "test_cinematic_frames")
    os.makedirs(frames_dir, exist_ok=True)

    # Blink cycle: smooth bell curve between t=1.35s and t=1.65s (peak at 1.50s)
    blink_center = 1.50
    blink_duration = 0.25

    preview_saved = {}

    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        progress = f_idx / float(total_frames)
        speech_rms = float(envelope[f_idx])

        # Smooth blink calculation
        dt = abs(t - blink_center)
        if dt < blink_duration:
            blink_prog = 0.5 * (1.0 + math.cos(math.pi * dt / blink_duration))
        else:
            blink_prog = 0.0

        frame_img = render_test_frame(width, height, t, progress, speech_rms, blink_prog)
        frame_path = os.path.join(frames_dir, f"frame_{f_idx:04d}.png")
        frame_img.save(frame_path)

        # Save preview inspection frames
        if f_idx == int(0.7 * fps) and "intro" not in preview_saved:
            frame_img.save(os.path.join(OUT_DIR, "preview_frames", "cinematic_test_intro.jpg"), quality=95)
            preview_saved["intro"] = True
        elif f_idx == int(1.5 * fps) and "blink" not in preview_saved:
            frame_img.save(os.path.join(OUT_DIR, "preview_frames", "cinematic_test_blink.jpg"), quality=95)
            preview_saved["blink"] = True
        elif f_idx == int(2.1 * fps) and "speaking" not in preview_saved:
            frame_img.save(os.path.join(OUT_DIR, "preview_frames", "cinematic_test_speaking.jpg"), quality=95)
            preview_saved["speaking"] = True

        if f_idx % 25 == 0 or f_idx == total_frames - 1:
            print(f"Rendered frame {f_idx+1}/{total_frames} (t={t:.2f}s)")

    # Encode with FFmpeg
    out_mp4 = os.path.join(OUT_DIR, "mysteryverse_character_test.mp4")
    print(f"Encoding MP4: {out_mp4}...")
    cmd = [
        FFMPEG_BIN, "-y",
        "-r", str(fps),
        "-i", os.path.join(frames_dir, "frame_%04d.png"),
        "-i", AUDIO_PATH,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        out_mp4
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(out_mp4):
        size = os.path.getsize(out_mp4)
        print(f"Cinematic Character Test MP4 successfully created! Size: {size} bytes ({size/(1024*1024):.2f} MB)")
    else:
        print("Error: Render failed!")


if __name__ == "__main__":
    main()
