import os
import math
import subprocess
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = r"c:\m\output"
AUDIO_PATH = r"c:\m\output\audio\sun_short_en.wav"
BED_PATH = r"c:\m\output\audio\cinematic_ambient_bed.wav"
SRT_PATH = r"c:\m\output\subtitles\sun_short_en.srt"
CHAR_DIR = r"c:\m\backend\static\character"
REF_DIR = r"c:\m\references"
SCENES_DIR = r"c:\m\backend\static\scenes\layers"

OUTPUT_VIDEO = r"c:\m\output\mysteryverse_sun_short.mp4"

def parse_srt(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    entries = []
    blocks = re.split(r'\n\s*\n', content.strip())
    for block in blocks:
        lines = block.split('\n')
        if len(lines) >= 3:
            time_match = re.search(r'(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)', lines[1])
            if time_match:
                h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, time_match.groups())
                start_sec = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000.0
                end_sec = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000.0
                text = ' '.join(lines[2:]).strip()
                entries.append((start_sec, end_sec, text))
    return entries

def get_smooth_speech_envelope(audio_path, fps=30):
    cmd = [FFMPEG_BIN, "-y", "-i", audio_path, "-f", "s16le", "-ac", "1", "-ar", "16000", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    raw, _ = proc.communicate()
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    total_sec = len(samples) / 16000.0
    total_frames = int(math.ceil(total_sec * fps))

    spf = int(16000 / fps)
    raw_rms = []
    for i in range(total_frames):
        chunk = samples[i * spf : (i + 1) * spf]
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
        raw_rms.append(rms)

    raw_rms = np.array(raw_rms)
    peak = np.percentile(raw_rms, 95)
    norm_rms = np.clip(raw_rms / (peak if peak > 0 else 1.0), 0.0, 1.0)

    dt = 1.0 / fps
    attack_alpha = 1.0 - math.exp(-dt / 0.06)
    decay_alpha = 1.0 - math.exp(-dt / 0.12)

    smoothed = np.zeros_like(norm_rms)
    cur = 0.0
    for i in range(len(norm_rms)):
        target = norm_rms[i]
        if target < 0.08:
            target = 0.0
        if target > cur:
            cur += attack_alpha * (target - cur)
        else:
            cur -= decay_alpha * (cur - target)
        smoothed[i] = cur

    viseme = np.clip(np.power(smoothed, 1.25) * 0.65, 0.0, 0.65)
    return total_sec, viseme

def main():
    width, height = 1080, 1920
    fps = 30
    print("Pre-loading assets for Sun Shorts (9:16 Vertical)...", flush=True)

    target_ch_h = int(height * 0.60)  # 1152px
    scale = target_ch_h / 1200.0      # 0.96

    raw_poses = {
        "welcome": Image.open(os.path.join(CHAR_DIR, "jobelessboy_welcome.png")).convert("RGBA"),
        "curiosity": Image.open(os.path.join(CHAR_DIR, "jobelessboy_curiosity.png")).convert("RGBA"),
        "explanation": Image.open(os.path.join(CHAR_DIR, "jobelessboy_explanation.png")).convert("RGBA"),
        "surprise": Image.open(os.path.join(CHAR_DIR, "jobelessboy_surprise.png")).convert("RGBA"),
        "caution": Image.open(os.path.join(CHAR_DIR, "jobelessboy_caution.png")).convert("RGBA"),
        "talking_wide": Image.open(os.path.join(CHAR_DIR, "jobelessboy_talking_wide.png")).convert("RGBA"),
        "blink": Image.open(os.path.join(CHAR_DIR, "jobelessboy_blink.png")).convert("RGBA"),
    }

    poses = {}
    for k, img in raw_poses.items():
        nw = int(img.width * scale)
        poses[k] = img.resize((nw, target_ch_h), Image.Resampling.LANCZOS)

    orig_offsets = {
        "welcome": (0, 0),
        "explanation": (0, 0),
        "curiosity": (1, -1),
        "caution": (1, -1),
        "surprise": (18, 1),
    }
    pose_offsets = {k: (int(v[0] * scale), int(v[1] * scale)) for k, v in orig_offsets.items()}

    mouth_box = (int(380 * scale), int(430 * scale), int(560 * scale), int(550 * scale))
    mw, mh = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]
    mask_mouth = Image.new("L", (mw, mh), 0)
    d_m = ImageDraw.Draw(mask_mouth)
    d_m.ellipse([int(12 * scale), int(14 * scale), mw - int(12 * scale), mh - int(14 * scale)], fill=255)
    mask_mouth = mask_mouth.filter(ImageFilter.GaussianBlur(radius=5))
    mouth_open = poses["talking_wide"].crop(mouth_box)

    eye_band = (int(340 * scale), int(280 * scale), int(670 * scale), int(410 * scale))
    bw, bh = eye_band[2] - eye_band[0], eye_band[3] - eye_band[1]
    mask_band = Image.new("L", (bw, bh), 255)
    for border_step in range(6):
        b_alpha = int(255 * (border_step / 6.0))
        d_b = ImageDraw.Draw(mask_band)
        d_b.rectangle([border_step, border_step, bw - border_step, bh - border_step], outline=b_alpha)
    mask_band = mask_band.filter(ImageFilter.GaussianBlur(radius=5))
    blink_crop = poses["blink"].crop(eye_band)

    def make_lut(factor):
        return [int(p * factor) for p in range(256)]

    vertical_bgs = {
        "observatory": Image.open(os.path.join(SCENES_DIR, "scene1_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS),
        "freezing": Image.open(os.path.join(SCENES_DIR, "scene2_bg.jpg")).convert("RGBA").resize((width, height), Image.Resampling.LANCZOS),
    }

    ref_caps = {
        "sun": cv2.VideoCapture(os.path.join(REF_DIR, "Video-43510.mp4")),
        "orbit": cv2.VideoCapture(os.path.join(REF_DIR, "Video-97155.mp4")),
        "darkness": cv2.VideoCapture(os.path.join(REF_DIR, "Video-59744.mp4")),
    }

    font_path = r"C:\Windows\Fonts\segoeuib.ttf"
    try:
        font_sub = ImageFont.truetype(font_path, 48)
        font_logo = ImageFont.truetype(font_path, 72)
        font_tag = ImageFont.truetype(font_path, 36)
    except Exception:
        font_sub = ImageFont.load_default()
        font_logo = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    total_sec, viseme_env = get_smooth_speech_envelope(AUDIO_PATH, fps=fps)
    total_frames = len(viseme_env)
    subtitles = parse_srt(SRT_PATH)

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

    # 4-Scene Short Timeline
    # 0 -> 10s: Pitch black / What if Sun disappeared (sun reference / observatory)
    # 10 -> 22s: 8 minutes 20 seconds mystery (orbit reference)
    # 22 -> 34s: Freezing cold (freezing background)
    # 34 -> End: Survival underground & Outro (darkness/space reference)
    scenes = [
        (0.00, 10.00, "sun", "surprise"),
        (10.00, 22.00, "orbit", "explanation"),
        (22.00, 34.00, "freezing", "caution"),
        (34.00, 999.00, "darkness", "curiosity")
    ]

    temp_video = os.path.join(OUT_DIR, "temp_sun_short.mp4")
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

    bg_darken = Image.new("RGBA", (width, height), (0, 0, 0, 45))

    np.random.seed(42)
    dust_x = np.random.rand(30) * width
    dust_y = np.random.rand(30) * height
    dust_r = np.random.randint(2, 5, 30)

    print(f"Rendering Sun Shorts ({total_frames} frames, 1080x1920 30fps)...", flush=True)
    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        speech_val = float(viseme_env[f_idx])

        active_scene = scenes[-1]
        for s in scenes:
            if s[0] <= t < s[1]:
                active_scene = s
                break

        _, _, bg_key, pose_name = active_scene

        if bg_key in ref_caps:
            bg = get_ref_vertical(ref_caps[bg_key])
        else:
            bg = vertical_bgs[bg_key].copy()

        bg.alpha_composite(bg_darken)

        char_base = poses[pose_name].copy()
        dx, dy = pose_offsets.get(pose_name, (0, 0))

        if speech_val > 0.02:
            lut = make_lut(speech_val)
            scaled_mask = mask_mouth.point(lut)
            jaw_drop = int(speech_val * 3.5 * scale)
            cur_mouth_box = (
                mouth_box[0] + dx,
                mouth_box[1] + dy + jaw_drop,
                mouth_box[2] + dx,
                mouth_box[3] + dy + jaw_drop
            )
            char_base.paste(mouth_open, cur_mouth_box, scaled_mask)

        blink_cycle = t % 2.9
        blink_factor = 0.0
        if blink_cycle < 0.22:
            blink_factor = math.sin((blink_cycle / 0.22) * math.pi)
        if blink_factor > 0.05:
            cur_eye_band = (eye_band[0] + dx, eye_band[1] + dy, eye_band[2] + dx, eye_band[3] + dy)
            lut_b = make_lut(blink_factor)
            scaled_blink_mask = mask_band.point(lut_b)
            char_base.paste(blink_crop, cur_eye_band, scaled_blink_mask)

        sway_y = int(5.0 * math.sin(t * 2.3))
        sway_x = int(3.0 * math.cos(t * 1.5))

        pos_x = (width - char_base.width) // 2 + sway_x
        pos_y = height - target_ch_h + 30 + sway_y
        bg.alpha_composite(char_base, (pos_x, pos_y))

        draw = ImageDraw.Draw(bg)
        for i in range(30):
            px = int((dust_x[i] + t * 45.0) % (width + 40)) - 20
            py = int((dust_y[i] + t * 25.0 * (1 + (i % 2))) % height)
            pr = dust_r[i]
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 255, 255, 65))

        # Top Channel Watermark Badge
        draw.rounded_rectangle([60, 90, 480, 155], radius=12, fill=(15, 20, 35, 220), outline=(0, 200, 255, 200), width=2)
        draw.text((85, 103), "MYSTERYVERSE SHORTS", font=font_tag, fill=(0, 220, 255))

        # Clean White Centered Subtitles at Safe Zone y=1340 (above character)
        active_sub = None
        for s_start, s_end, s_text in subtitles:
            if s_start <= t <= s_end:
                active_sub = s_text
                break

        if active_sub and t < (total_sec - 2.5):
            words = active_sub.split()
            lines = []
            cur_line = []
            for w in words:
                cur_line.append(w)
                bbox = draw.textbbox((0, 0), ' '.join(cur_line), font=font_sub)
                if (bbox[2] - bbox[0]) > (width - 160):
                    cur_line.pop()
                    lines.append(' '.join(cur_line))
                    cur_line = [w]
            if cur_line:
                lines.append(' '.join(cur_line))

            total_sub_h = len(lines) * 58
            base_ty = 1340 - (total_sub_h // 2)

            for l_idx, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                tw = bbox[2] - bbox[0]
                tx = (width - tw) // 2
                ty = base_ty + l_idx * 58
                for sx, sy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
                    draw.text((tx + sx, ty + sy), line, font=font_sub, fill=(0, 0, 0, 240))
                draw.text((tx, ty), line, font=font_sub, fill=(255, 255, 255, 255))

        # Grand Finale Reveal in last 3.5s
        if t >= (total_sec - 3.5):
            logo_alpha = min(1.0, (t - (total_sec - 3.5)) / 1.0)
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(logo_alpha * 200)))
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
            ty = ly + 100
            draw_ov.text((tx, ty), tag_text, font=font_tag, fill=(200, 225, 255, int(logo_alpha * 240)))

        proc_out.stdin.write(bg.convert("RGB").tobytes())

        if f_idx % 300 == 0 or f_idx == total_frames - 1:
            print(f"Rendered {f_idx}/{total_frames} frames ({f_idx * 100 // total_frames}%)", flush=True)

    proc_out.stdin.close()
    out, err = proc_out.communicate()
    if proc_out.returncode != 0:
        print("FFmpeg pipe error:", err.decode('utf-8', errors='ignore')[-500:], flush=True)

    for cap in ref_caps.values():
        cap.release()

    print("Muxing final Shorts audio with background music...", flush=True)
    fade_st = max(0.0, total_sec - 3.5)
    cmd_mux = [
        FFMPEG_BIN, "-y",
        "-i", temp_video,
        "-i", AUDIO_PATH,
        "-stream_loop", "-1", "-i", BED_PATH,
        "-filter_complex",
        f"[1:a]volume=1.0[v];[2:a]volume=0.08,afade=t=out:st={fade_st:.1f}:d=3.5[m];[v][m]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd_mux, check=True)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    print(f"Finished rendering Sun Shorts: {OUTPUT_VIDEO}", flush=True)

if __name__ == "__main__":
    main()
