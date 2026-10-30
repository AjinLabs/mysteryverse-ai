"""
MysteryVerse — What If the Sun Disappeared? (Shorts Production v2)
Resolution: 1080x1920 (9:16 Vertical)
Target Runtime: 53.66 seconds (Exact 50-60s range)

FIXES IMPLEMENTED:
1. Scientific Accuracy:
   - "Without sunlight, Earth's surface would gradually cool, though the rate would vary across the planet."
   - "the change in gravitational influence would reach Earth at approximately the same time as the last sunlight, sending our planet coasting in a straight line into deep interstellar space."
   - No claim of oceans freezing in weeks.
2. Unrelated Ending Visual:
   - Removed all black-hole imagery!
   - Ending finishes on Earth in darkness / geothermal sanctuary and host delivering the call to action.
3. Character Animation & Poses:
   - 6 distinct purposeful poses matching the narrative beats:
     * 0.0 - 4.0s: curiosity (looking up at the morning sky)
     * 4.0 - 9.9s: surprise (reacting to vanished Sun)
     * 9.9 - 22.0s: explanation (pointing to the Sun / orbital delay)
     * 22.0 - 34.0s: caution (analytical posture, gradual cooling)
     * 34.0 - 46.0s: talking_wide (explaining gravity speed & straight trajectory)
     * 46.0 - End: waving / welcome (direct eye contact, warm smile, subscribe CTA)
   - Natural, conversational lip-sync with 180ms decay, speech-responsive head nods, breathing sway.
   - Realistic blinks (180ms every 3.8s).
4. Captions:
   - Small, plain white English text with soft drop-shadow.
   - Zero black background boxes, banners, or frames.
   - Positioned at y=1420 (below character's face).
5. Audio:
   - Broadcast-standard AndrewNeural narration (-14 LUFS).
   - Cinematic ambient bed at -23dB with gentle end fade.
"""

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
REF_DIR = r"c:\m\references"
AUDIO_PATH = r"c:\m\output\audio\sun_short_en.wav"
BED_PATH = r"c:\m\output\audio\cinematic_ambient_bed.wav"
SRT_PATH = r"c:\m\output\subtitles\sun_short_en.srt"
OUT_DIR = r"c:\m\output"
FINAL_VIDEO = os.path.join(OUT_DIR, "mysteryverse_sun_short.mp4")

def parse_srt(srt_file):
    with open(srt_file, "r", encoding="utf-8") as f:
        content = f.read()
    cues = []
    blocks = content.strip().split("\n\n")
    for block in blocks:
        lines = block.strip().splitlines()
        if len(lines) >= 3:
            time_match = re.match(
                r"(\d+):(\d+):(\d+)[,\.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,\.](\d+)",
                lines[1]
            )
            if time_match:
                sh, sm, ss, sms, eh, em, es, ems = [int(x) for x in time_match.groups()]
                st = sh * 3600 + sm * 60 + ss + sms / 1000.0
                et = eh * 3600 + em * 60 + es + ems / 1000.0
                text = " ".join(lines[2:]).strip()
                cues.append((st, et, text))
    return cues

import re

def get_natural_speech_envelope(audio_path, fps=30):
    sample_rate, data = wav.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]
    data = data.astype(np.float32) / 32768.0

    total_sec = len(data) / sample_rate
    num_frames = int(math.ceil(total_sec * fps))

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

    dt = 1.0 / fps
    attack_alpha = 1.0 - math.exp(-dt / 0.06)
    decay_alpha = 1.0 - math.exp(-dt / 0.18)

    smoothed = np.zeros_like(norm_rms)
    cur = 0.0
    for i in range(len(norm_rms)):
        target = norm_rms[i]
        if target < 0.06:
            target = 0.0
        if target > cur:
            cur += attack_alpha * (target - cur)
        else:
            cur -= decay_alpha * (cur - target)
        smoothed[i] = cur

    viseme = np.clip(np.power(smoothed, 1.3) * 0.60, 0.0, 0.60)
    return total_sec, viseme

def main():
    width, height = 1080, 1920
    fps = 30
    print("Pre-loading assets for MysteryVerse Sun Short v2...", flush=True)

    target_ch_h = int(height * 0.58)  # 1113px
    scale = target_ch_h / 1200.0

    raw_poses = {
        "curiosity": Image.open(os.path.join(CHAR_DIR, "jobelessboy_curiosity.png")).convert("RGBA"),
        "surprise": Image.open(os.path.join(CHAR_DIR, "jobelessboy_surprise.png")).convert("RGBA"),
        "explanation": Image.open(os.path.join(CHAR_DIR, "jobelessboy_explanation.png")).convert("RGBA"),
        "caution": Image.open(os.path.join(CHAR_DIR, "jobelessboy_caution.png")).convert("RGBA"),
        "talking_wide": Image.open(os.path.join(CHAR_DIR, "jobelessboy_talking_wide.png")).convert("RGBA"),
        "waving": Image.open(os.path.join(CHAR_DIR, "jobelessboy_waving.png")).convert("RGBA"),
        "blink": Image.open(os.path.join(CHAR_DIR, "jobelessboy_blink.png")).convert("RGBA"),
    }

    poses = {}
    for k, img in raw_poses.items():
        nw = int(img.width * scale)
        poses[k] = img.resize((nw, target_ch_h), Image.Resampling.LANCZOS)

    orig_offsets = {
        "curiosity": (1, -1),
        "surprise": (18, 1),
        "explanation": (0, 0),
        "caution": (1, -1),
        "talking_wide": (0, 0),
        "waving": (0, 0),
    }
    pose_offsets = {k: (int(v[0] * scale), int(v[1] * scale)) for k, v in orig_offsets.items()}

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

    # Environmental background assets
    observatory_bg = Image.open(os.path.join(SCENES_DIR, "scene1_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    freezing_bg = Image.open(os.path.join(SCENES_DIR, "scene2_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)
    shelter_bg = Image.open(os.path.join(SCENES_DIR, "wide_scene5_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS)

    ref_caps = {
        "sun": cv2.VideoCapture(os.path.join(REF_DIR, "Video-43510.mp4")),
        "orbit": cv2.VideoCapture(os.path.join(REF_DIR, "Video-97155.mp4")),
        "interstellar_earth": cv2.VideoCapture(os.path.join(REF_DIR, "Video-84151.mp4")),
    }

    font_path = r"C:\Windows\Fonts\segoeuib.ttf"
    try:
        font_sub = ImageFont.truetype(font_path, 44)
        font_logo = ImageFont.truetype(font_path, 68)
        font_tag = ImageFont.truetype(font_path, 34)
    except Exception:
        font_sub = ImageFont.load_default()
        font_logo = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    total_sec, viseme_env = get_natural_speech_envelope(AUDIO_PATH, fps=fps)
    total_frames = len(viseme_env)
    subtitles = parse_srt(SRT_PATH)
    print(f"Total video duration: {total_sec:.2f}s ({total_frames} frames)", flush=True)

    def get_ref_vertical(cap):
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret or frame is None:
                return Image.new("RGBA", (width, height), (5, 8, 20, 255))
        fh, fw = frame.shape[:2]
        sc = max(width / fw, height / fh)
        nw, nh = int(fw * sc), int(fh * sc)
        frame_res = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_LINEAR)
        cx, cy = (nw - width) // 2, (nh - height) // 2
        cropped = frame_res[cy:cy + height, cx:cx + width]
        rgba = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGBA)
        return Image.fromarray(rgba)

    # 5 Narrative Visual Beats (NO Black Hole!)
    # Beat 1: 0.00 -> 9.90s (Vanished Sun Hook) -> observatory_bg
    # Beat 2: 9.90 -> 22.00s (8 min 20 sec delay) -> Sun / Orbit video
    # Beat 3: 22.00 -> 34.00s (Gradual cooling / thermal inertia) -> freezing_bg
    # Beat 4: 34.00 -> 46.00s (Gravity speed & straight-line interstellar Earth) -> interstellar_earth video
    # Beat 5: 46.00 -> End (Geothermal underground survival & MysteryVerse call to action) -> shelter_bg
    temp_video = os.path.join(OUT_DIR, "temp_sun_short_v2.mp4")
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
        temp_video
    ]
    proc_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    bg_darken = Image.new("RGBA", (width, height), (0, 0, 0, 50))

    saved_preview_times = [2.0, 7.0, 15.0, 28.0, 40.0, 50.0]
    saved_frames = [int(pt * fps) for pt in saved_preview_times]

    for f_idx in range(total_frames):
        t = f_idx / fps
        speech_val = viseme_env[f_idx]

        # Select environment and pose according to timeline
        if t < 4.0:
            bg = observatory_bg.copy()
            pose_name = "curiosity"
        elif t < 9.9:
            bg = observatory_bg.copy()
            pose_name = "surprise"
        elif t < 22.0:
            bg = get_ref_vertical(ref_caps["sun" if t < 16.0 else "orbit"])
            pose_name = "explanation"
        elif t < 34.0:
            bg = freezing_bg.copy()
            pose_name = "caution"
        elif t < 46.0:
            bg = get_ref_vertical(ref_caps["interstellar_earth"])
            pose_name = "talking_wide"
        else:
            bg = shelter_bg.copy()
            pose_name = "waving"

        bg.alpha_composite(bg_darken)

        char_base = poses[pose_name].copy()
        dx, dy = pose_offsets.get(pose_name, (0, 0))

        # Conversational lip-sync
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

        # Realistic human eye-blink cycle
        blink_cycle = t % 3.8
        blink_factor = 0.0
        if blink_cycle < 0.18:
            blink_factor = math.sin((blink_cycle / 0.18) * math.pi)
        if blink_factor > 0.05:
            cur_eye_band = (eye_band[0] + dx, eye_band[1] + dy, eye_band[2] + dx, eye_band[3] + dy)
            lut_b = make_lut(blink_factor)
            scaled_blink_mask = mask_band.point(lut_b)
            char_base.paste(blink_crop, cur_eye_band, scaled_blink_mask)

        # Subtle breathing & head gesture
        head_nod = int(speech_val * 3.5)
        sway_y = int(4.0 * math.sin(t * 1.8)) + head_nod
        sway_x = int(2.5 * math.cos(t * 1.2))

        pos_x = (width - char_base.width) // 2 + sway_x
        pos_y = height - target_ch_h + 30 + sway_y
        bg.alpha_composite(char_base, (pos_x, pos_y))

        # Synchronized English Caption (plain white, soft drop shadow, placed at y=1420)
        draw = ImageDraw.Draw(bg)
        active_sub = ""
        for st, et, text in subtitles:
            if st <= t <= et:
                active_sub = text
                break

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
                for sx, sy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
                    draw.text((tx + sx, ty + sy), line, font=font_sub, fill=(0, 0, 0, 230))
                draw.text((tx, ty), line, font=font_sub, fill=(255, 255, 255, 255))

        # Brand callout in final 3 seconds
        if t >= (total_sec - 3.2):
            logo_alpha = min(1.0, (t - (total_sec - 3.2)) / 1.0)
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(logo_alpha * 190)))
            bg.alpha_composite(overlay)
            draw_ov = ImageDraw.Draw(bg)

            logo_text = "MYSTERYVERSE"
            bbox_logo = draw_ov.textbbox((0, 0), logo_text, font=font_logo)
            lw = bbox_logo[2] - bbox_logo[0]
            lx = (width - lw) // 2
            ly = height // 2 - 80

            glow_c = (255, 215, 0, int(logo_alpha * 240))
            for gx in range(-4, 5):
                for gy in range(-4, 5):
                    draw_ov.text((lx + gx, ly + gy), logo_text, font=font_logo, fill=glow_c)
            draw_ov.text((lx, ly), logo_text, font=font_logo, fill=(255, 255, 255, int(logo_alpha * 255)))

            tag_text = "STAY CURIOUS"
            bbox_tag = draw_ov.textbbox((0, 0), tag_text, font=font_tag)
            tw = bbox_tag[2] - bbox_tag[0]
            tx = (width - tw) // 2
            ty = ly + 95
            draw_ov.text((tx, ty), tag_text, font=font_tag, fill=(200, 225, 255, int(logo_alpha * 240)))

        rgb_frame = bg.convert("RGB")
        proc_out.stdin.write(rgb_frame.tobytes())

        if f_idx in saved_frames:
            preview_path = os.path.join(r"C:\Users\ajina\.gemini\antigravity\brain\22f0269a-8272-4df5-a358-12535e6b146f", f"sun_short_v2_f{f_idx:04d}.jpg")
            rgb_frame.save(preview_path, quality=95)
            print(f"Extracted preview {preview_path} at t={t:.1f}s")

        if f_idx % 300 == 0 or f_idx == total_frames - 1:
            print(f"Rendered {f_idx}/{total_frames} frames ({f_idx * 100 // total_frames}%)", flush=True)

    proc_out.stdin.close()
    proc_out.communicate()

    for cap in ref_caps.values():
        cap.release()

    print("Muxing final audio with ambient soundtrack...", flush=True)
    fade_st = max(0.0, total_sec - 3.2)
    cmd_mux = [
        FFMPEG_BIN, "-y",
        "-i", temp_video,
        "-i", AUDIO_PATH,
        "-stream_loop", "-1", "-i", BED_PATH,
        "-filter_complex",
        f"[1:a]volume=1.0[v];[2:a]volume=0.07,afade=t=out:st={fade_st:.1f}:d=3.2[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        FINAL_VIDEO
    ]
    subprocess.run(cmd_mux, check=True)
    print(f"Final 1080x1920 Short successfully rendered: {FINAL_VIDEO}", flush=True)

    # Sync to frontend and backend public static
    fe_dir = r"c:\m\frontend\public\static\videos"
    be_dir = r"c:\m\backend\static\videos"
    os.makedirs(fe_dir, exist_ok=True)
    os.makedirs(be_dir, exist_ok=True)
    import shutil
    shutil.copy2(FINAL_VIDEO, os.path.join(fe_dir, "mysteryverse_sun_short.mp4"))
    shutil.copy2(FINAL_VIDEO, os.path.join(be_dir, "mysteryverse_sun_short.mp4"))
    print("Synced video to frontend and backend static.")

if __name__ == "__main__":
    main()
