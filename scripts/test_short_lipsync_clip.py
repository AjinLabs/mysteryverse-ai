import os
import sys
import math
import subprocess
import numpy as np
import scipy.io.wavfile as wav
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cv2

sys.path.insert(0, r"c:\m\backend")
from app.config import get_ffmpeg_path

FFMPEG_BIN = get_ffmpeg_path()
CHAR_DIR = r"c:\m\backend\static\character"
SCENES_DIR = r"c:\m\backend\static\scenes\layers"
AUDIO_PATH = r"c:\m\output\audio\sun_short_en.wav"
OUT_DIR = r"c:\m\output"
os.makedirs(r"c:\m\output\test_clip", exist_ok=True)

def get_natural_speech_envelope(audio_path, fps=30):
    sample_rate, data = wav.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0

    total_sec = len(data) / sample_rate
    num_frames = int(math.ceil(total_sec * fps))

    # 1. Calculate frame RMS with 45ms window
    window_size = int(sample_rate * 0.045)
    rms_raw = np.zeros(num_frames, dtype=np.float32)

    for f in range(num_frames):
        center = int(f * sample_rate / fps)
        start = max(0, center - window_size // 2)
        end = min(len(data), center + window_size // 2)
        if end > start:
            chunk = data[start:end]
            rms_raw[f] = np.sqrt(np.mean(chunk**2))

    max_rms = np.percentile(rms_raw, 95) if len(rms_raw) > 0 else 1.0
    if max_rms < 1e-4:
        max_rms = 1.0
    norm_rms = np.clip(rms_raw / max_rms, 0.0, 1.0)

    # 2. Conversational Asymmetric Filter:
    # Quick natural attack (60ms) so mouth opens as sound starts.
    # Slow, natural conversational decay (180ms) so mouth doesn't flutter/snap shut between syllables.
    dt = 1.0 / fps
    attack_alpha = 1.0 - math.exp(-dt / 0.06)
    decay_alpha = 1.0 - math.exp(-dt / 0.18)

    smoothed = np.zeros_like(norm_rms)
    cur = 0.0
    for i in range(len(norm_rms)):
        target = norm_rms[i]
        # Low noise gate: below 0.06 is silence between words/sentences
        if target < 0.06:
            target = 0.0
        if target > cur:
            cur += attack_alpha * (target - cur)
        else:
            cur -= decay_alpha * (cur - target)
        smoothed[i] = cur

    # 3. Non-linear mapping:
    # Avoid wide flapping by gentle power curve and max cap 0.60
    viseme = np.clip(np.power(smoothed, 1.3) * 0.60, 0.0, 0.60)
    return total_sec, viseme

def render_test_clip(duration_sec=6.0):
    width, height = 1080, 1920
    fps = 30
    total_frames = int(duration_sec * fps)

    print(f"Rendering {duration_sec}s Natural Lip-Sync Test Clip ({total_frames} frames)...", flush=True)

    target_ch_h = int(height * 0.60) # 1152px
    scale = target_ch_h / 1200.0

    raw_poses = {
        "curiosity": Image.open(os.path.join(CHAR_DIR, "jobelessboy_curiosity.png")).convert("RGBA"),
        "surprise": Image.open(os.path.join(CHAR_DIR, "jobelessboy_surprise.png")).convert("RGBA"),
        "talking_wide": Image.open(os.path.join(CHAR_DIR, "jobelessboy_talking_wide.png")).convert("RGBA"),
        "blink": Image.open(os.path.join(CHAR_DIR, "jobelessboy_blink.png")).convert("RGBA"),
    }

    poses = {}
    for k, img in raw_poses.items():
        nw = int(img.width * scale)
        poses[k] = img.resize((nw, target_ch_h), Image.Resampling.LANCZOS)

    pose_offsets = {
        "curiosity": (int(1 * scale), int(-1 * scale)),
        "surprise": (int(18 * scale), int(1 * scale)),
    }

    mouth_box = (int(380 * scale), int(430 * scale), int(560 * scale), int(550 * scale))
    mw, mh = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]
    mask_mouth = Image.new("L", (mw, mh), 0)
    d_m = ImageDraw.Draw(mask_mouth)
    d_m.ellipse([int(12 * scale), int(14 * scale), mw - int(12 * scale), mh - int(14 * scale)], fill=255)
    mask_mouth = mask_mouth.filter(ImageFilter.GaussianBlur(radius=6))
    mouth_open = poses["talking_wide"].crop(mouth_box)

    eye_band = (int(340 * scale), int(280 * scale), int(670 * scale), int(410 * scale))
    bw, bh = eye_band[2] - eye_band[0], eye_band[3] - eye_band[1]
    mask_band = Image.new("L", (bw, bh), 255)
    for b_step in range(6):
        b_alpha = int(255 * (b_step / 6.0))
        d_b = ImageDraw.Draw(mask_band)
        d_b.rectangle([b_step, b_step, bw - b_step, bh - b_step], outline=b_alpha)
    mask_band = mask_band.filter(ImageFilter.GaussianBlur(radius=5))
    blink_crop = poses["blink"].crop(eye_band)

    def make_lut(factor):
        return [int(p * factor) for p in range(256)]

    bg_observatory = Image.open(os.path.join(SCENES_DIR, "scene1_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    bg_darken = Image.new("RGBA", (width, height), (0, 0, 0, 50))

    font_path = r"C:\Windows\Fonts\segoeuib.ttf"
    try:
        font_sub = ImageFont.truetype(font_path, 44)
    except Exception:
        font_sub = ImageFont.load_default()

    total_sec, viseme_env = get_natural_speech_envelope(AUDIO_PATH, fps=fps)

    clip_video_raw = os.path.join(OUT_DIR, "test_clip", "raw_test_clip.mp4")
    cmd_out = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        clip_video_raw
    ]
    proc_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    saved_frames = [15, 45, 90, 135, 170]

    for f_idx in range(total_frames):
        t = f_idx / fps
        speech_val = viseme_env[f_idx] if f_idx < len(viseme_env) else 0.0

        bg = bg_observatory.copy()
        bg.alpha_composite(bg_darken)

        # Beat 1: Host looks up at window in curiosity, then reacts with shock at vanished Sun
        pose_name = "curiosity" if t < 3.8 else "surprise"
        char_base = poses[pose_name].copy()
        dx, dy = pose_offsets.get(pose_name, (0, 0))

        # Natural Lip-Sync:
        # Subtle jaw translation and smooth alpha modulation
        if speech_val > 0.02:
            lut = make_lut(speech_val)
            scaled_mask = mask_mouth.point(lut)
            jaw_drop = int(speech_val * 3.0 * scale)
            cur_mouth_box = (
                mouth_box[0] + dx,
                mouth_box[1] + dy + jaw_drop,
                mouth_box[2] + dx,
                mouth_box[3] + dy + jaw_drop
            )
            char_base.paste(mouth_open, cur_mouth_box, scaled_mask)

        # Realistic Human Blink: 180ms duration every 4.0 seconds
        blink_cycle = t % 4.0
        blink_factor = 0.0
        if blink_cycle < 0.18:
            blink_factor = math.sin((blink_cycle / 0.18) * math.pi)
        if blink_factor > 0.05:
            cur_eye_band = (eye_band[0] + dx, eye_band[1] + dy, eye_band[2] + dx, eye_band[3] + dy)
            lut_b = make_lut(blink_factor)
            scaled_blink_mask = mask_band.point(lut_b)
            char_base.paste(blink_crop, cur_eye_band, scaled_blink_mask)

        # Purposeful head nod & subtle breathing micro-sway
        # Character nods slightly when speaking key syllables (speech_val)
        head_nod = int(speech_val * 4.0)
        sway_y = int(4.0 * math.sin(t * 2.0)) + head_nod
        sway_x = int(2.5 * math.cos(t * 1.3))

        pos_x = (width - char_base.width) // 2 + sway_x
        pos_y = height - target_ch_h + 30 + sway_y
        bg.alpha_composite(char_base, (pos_x, pos_y))

        # Synchronized English Caption (Small, plain white, soft shadow, away from face)
        draw = ImageDraw.Draw(bg)
        active_sub = ""
        if 0.4 <= t < 3.8:
            active_sub = "Imagine waking up one morning and looking outside your window."
        elif 3.8 <= t < 6.0:
            active_sub = "The sky is completely dark, and the Sun has vanished!"

        if active_sub:
            words = active_sub.split()
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                bbox = draw.textbbox((0, 0), ' '.join(cur_line), font=font_sub)
                if (bbox[2] - bbox[0]) > (width - 180):
                    cur_line.pop()
                    lines.append(' '.join(cur_line))
                    cur_line = [w]
            if cur_line:
                lines.append(' '.join(cur_line))

            base_ty = 1420
            for l_idx, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                tw = bbox[2] - bbox[0]
                tx = (width - tw) // 2
                ty = base_ty + l_idx * 52
                # Clean soft drop shadow
                for sx, sy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                    draw.text((tx + sx, ty + sy), line, font=font_sub, fill=(0, 0, 0, 220))
                draw.text((tx, ty), line, font=font_sub, fill=(255, 255, 255, 255))

        rgb_frame = bg.convert("RGB")
        proc_out.stdin.write(rgb_frame.tobytes())

        if f_idx in saved_frames:
            preview_path = os.path.join(r"C:\Users\ajina\.gemini\antigravity\brain\22f0269a-8272-4df5-a358-12535e6b146f", f"test_lipsync_f{f_idx:03d}.jpg")
            rgb_frame.save(preview_path, quality=95)
            print(f"Saved preview frame {preview_path} (t={t:.2f}s, speech={speech_val:.2f})")

    proc_out.stdin.close()
    proc_out.communicate()

    # Mux with the first 6.0 seconds of audio
    clip_video_final = os.path.join(OUT_DIR, "test_clip", "lipsync_test_clip.mp4")
    cmd_mux = [
        FFMPEG_BIN, "-y",
        "-i", clip_video_raw,
        "-ss", "0.0", "-t", str(duration_sec), "-i", AUDIO_PATH,
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        clip_video_final
    ]
    subprocess.run(cmd_mux, check=True)
    print(f"Lip-sync test clip ready: {clip_video_final}", flush=True)

if __name__ == "__main__":
    render_test_clip()

