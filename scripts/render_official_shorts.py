import os
import sys
import math
import subprocess
import re
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import imageio_ffmpeg

FFMPEG_BIN = imageio_ffmpeg.get_ffmpeg_exe()

OUT_DIR = r"c:\m\output"
AUDIO_PATH = r"c:\m\output\audio\intro_short_en.wav"
BED_PATH = r"c:\m\output\audio\cinematic_ambient_bed.wav"
SRT_PATH = r"c:\m\output\subtitles\intro_short_en.srt"
CHAR_DIR = r"c:\m\backend\static\character"
REF_DIR = r"c:\m\references"
SCENES_DIR = r"c:\m\backend\static\scenes\layers"

OUTPUT_VIDEO = r"c:\m\output\mysteryverse_intro_short.mp4"

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

def main():
    print("Pre-loading Character Assets...")
    poses = {
        "welcome": Image.open(os.path.join(CHAR_DIR, "jobelessboy_welcome.png")).convert("RGBA"),
        "talking_wide": Image.open(os.path.join(CHAR_DIR, "jobelessboy_talking_wide.png")).convert("RGBA"),
        "blink": Image.open(os.path.join(CHAR_DIR, "jobelessboy_blink.png")).convert("RGBA"),
        "curiosity": Image.open(os.path.join(CHAR_DIR, "jobelessboy_curiosity.png")).convert("RGBA"),
        "explanation": Image.open(os.path.join(CHAR_DIR, "jobelessboy_explanation.png")).convert("RGBA"),
        "surprise": Image.open(os.path.join(CHAR_DIR, "jobelessboy_surprise.png")).convert("RGBA"),
        "caution": Image.open(os.path.join(CHAR_DIR, "jobelessboy_caution.png")).convert("RGBA"),
        "excitement": Image.open(os.path.join(CHAR_DIR, "jobelessboy_excitement.png")).convert("RGBA"),
        "humour": Image.open(os.path.join(CHAR_DIR, "jobelessboy_humour.png")).convert("RGBA"),
        "waving": Image.open(os.path.join(CHAR_DIR, "jobelessboy_waving.png")).convert("RGBA"),
    }

    pose_offsets = {
        "welcome": (0, 0),
        "explanation": (0, 0),
        "waving": (0, 0),
        "curiosity": (1, -1),
        "caution": (1, -1),
        "surprise": (18, 1),
        "excitement": (18, 1),
        "humour": (0, 0)
    }

    mouth_box = (380, 430, 560, 550)
    mw, mh = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]
    mask_mouth = Image.new("L", (mw, mh), 0)
    d_m = ImageDraw.Draw(mask_mouth)
    d_m.ellipse([10, 12, mw - 10, mh - 12], fill=255)
    mask_mouth = mask_mouth.filter(ImageFilter.GaussianBlur(radius=8))
    mouth_open = poses["talking_wide"].crop(mouth_box)

    eye_band = (340, 280, 670, 410)
    bw, bh = eye_band[2] - eye_band[0], eye_band[3] - eye_band[1]
    mask_band = Image.new("L", (bw, bh), 255)
    for border_step in range(8):
        b_alpha = int(255 * (border_step / 8.0))
        d_b = ImageDraw.Draw(mask_band)
        d_b.rectangle([border_step, border_step, bw - border_step, bh - border_step], outline=b_alpha)
    mask_band = mask_band.filter(ImageFilter.GaussianBlur(radius=6))
    blink_crop = poses["blink"].crop(eye_band)

    # Static Scene Layer Assets for History & Psychology
    img_pyramids = Image.open(os.path.join(SCENES_DIR, "scene4_bg.jpg")).convert("RGBA")
    img_portal = Image.open(os.path.join(SCENES_DIR, "scene5_bg.jpg")).convert("RGBA")

    font_path = r"C:\Windows\Fonts\segoeuib.ttf"
    try:
        font_sub = ImageFont.truetype(font_path, 42)
        font_logo = ImageFont.truetype(font_path, 68)
        font_tag = ImageFont.truetype(font_path, 32)
    except Exception:
        font_sub = ImageFont.load_default()
        font_logo = ImageFont.load_default()
        font_tag = ImageFont.load_default()

    fps = 30
    total_sec, envelope = get_audio_envelope(AUDIO_PATH, fps=fps)
    total_frames = len(envelope)
    subtitles = parse_srt(SRT_PATH)

    ref_caps = {
        "space_system": cv2.VideoCapture(os.path.join(REF_DIR, "Video-97155.mp4")),
        "sun_planets": cv2.VideoCapture(os.path.join(REF_DIR, "Video-43510.mp4")),
        "jupiter": cv2.VideoCapture(os.path.join(REF_DIR, "Video-84151.mp4")),
        "blackhole": cv2.VideoCapture(os.path.join(REF_DIR, "Video-59744.mp4")),
    }

    def get_bg_frame(cap, target_w=1080, target_h=1920, top_crop=0.0):
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret or frame is None:
                return Image.new("RGBA", (target_w, target_h), (5, 8, 20, 255))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(frame_rgb).convert("RGBA")
        iw, ih = im.size
        if top_crop > 0:
            # Crop off the top area to completely remove any third-party titles
            im = im.crop((0, int(ih * top_crop), iw, ih))
            iw, ih = im.size
        scale = max(target_w / iw, target_h / ih)
        nw, nh = int(iw * scale), int(ih * scale)
        im_resized = im.resize((nw, nh), Image.Resampling.BILINEAR)
        cx, cy = (nw - target_w) // 2, (nh - target_h) // 2
        return im_resized.crop((cx, cy, cx + target_w, cy + target_h))

    def get_pan_zoom_scene(base_img, t_rel, dur, target_w=1080, target_h=1920):
        prog = min(1.0, max(0.0, t_rel / max(0.001, dur)))
        # Slow dynamic camera zoom 1.0 -> 1.08
        zoom = 1.0 + 0.08 * prog
        iw, ih = base_img.size
        crop_w = int(iw / zoom)
        crop_h = int(ih / zoom)
        cx = int((iw - crop_w) * 0.5)
        cy = int((ih - crop_h) * (0.35 + 0.20 * prog))
        cropped = base_img.crop((cx, cy, cx + crop_w, cy + crop_h))
        return cropped.resize((target_w, target_h), Image.Resampling.BICUBIC)

    temp_video = os.path.join(OUT_DIR, "temp_shorts_video.mp4")
    cmd_out = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", "1080x1920",
        "-pix_fmt", "bgr24",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "faster",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        temp_video
    ]
    proc_out = subprocess.Popen(cmd_out, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
    width, height = 1080, 1920

    print("Rendering Cinematic Shorts (Cleaned & Upgraded)...")
    for f_idx in range(total_frames):
        t = f_idx / float(fps)
        progress = f_idx / float(total_frames)
        speech_rms = float(envelope[f_idx])

        # Exact Scene Switching
        if t < 4.0:
            bg = get_bg_frame(ref_caps["space_system"], width, height)
            pose_name = "welcome"
        elif t < 7.5:
            bg = get_bg_frame(ref_caps["sun_planets"], width, height)
            pose_name = "curiosity"
        elif t < 11.0:
            # Pyramids & Ancient Mysteries (100% clean, no text, dynamic camera push)
            bg = get_pan_zoom_scene(img_pyramids, t - 7.5, 3.5, width, height)
            pose_name = "explanation"
        elif t < 15.0:
            # Jupiter (cropped top 28% to remove third-party title)
            bg = get_bg_frame(ref_caps["jupiter"], width, height, top_crop=0.28)
            pose_name = "excitement"
        elif t < 19.0:
            bg = get_bg_frame(ref_caps["sun_planets"], width, height)
            pose_name = "explanation"
        elif t < 24.0:
            bg = get_bg_frame(ref_caps["blackhole"], width, height)
            pose_name = "caution"
        elif t < 27.5:
            bg = get_bg_frame(ref_caps["blackhole"], width, height)
            pose_name = "surprise"
        elif t < 33.0:
            # Cosmic Mind Portal
            bg = get_pan_zoom_scene(img_portal, t - 27.5, 5.5, width, height)
            pose_name = "curiosity"
        else:
            bg = get_bg_frame(ref_caps["space_system"], width, height)
            pose_name = "waving"

        # Background vignette
        bg_darken = Image.new("RGBA", (width, height), (0, 0, 0, 45))
        bg.alpha_composite(bg_darken)

        # Character Composite
        char_base = poses[pose_name].copy()
        dx, dy = pose_offsets.get(pose_name, (0, 0))

        # Audio-driven lip sync
        if speech_rms > 0.08:
            mouth_alpha = int(min(255, speech_rms * 300))
            scaled_mask = mask_mouth.point(lambda p: int(p * (mouth_alpha / 255.0)))
            cur_mouth_box = (mouth_box[0] + dx, mouth_box[1] + dy, mouth_box[2] + dx, mouth_box[3] + dy)
            char_base.paste(mouth_open, cur_mouth_box, scaled_mask)

        # Eyelid blink
        blink_cycle = t % 2.8
        blink_factor = 0.0
        if blink_cycle < 0.22:
            blink_factor = math.sin((blink_cycle / 0.22) * math.pi)
        if blink_factor > 0.05:
            cur_eye_band = (eye_band[0] + dx, eye_band[1] + dy, eye_band[2] + dx, eye_band[3] + dy)
            scaled_blink_mask = mask_band.point(lambda p: int(p * blink_factor))
            char_base.paste(blink_crop, cur_eye_band, scaled_blink_mask)

        # Natural body sway
        sway_y = int(6.0 * math.sin(t * 2.4))
        sway_x = int(3.0 * math.cos(t * 1.6))
        char_tilt = math.sin(t * 1.8) * 0.4

        target_ch_h = int(height * 0.61)
        target_ch_w = int(char_base.width * (target_ch_h / char_base.height))
        char_scaled = char_base.resize((target_ch_w, target_ch_h), Image.Resampling.LANCZOS)
        if abs(char_tilt) > 0.1:
            char_scaled = char_scaled.rotate(char_tilt, resample=Image.Resampling.BICUBIC, expand=False)

        pos_x = (width - target_ch_w) // 2 + sway_x
        pos_y = height - target_ch_h + 80 + sway_y
        bg.alpha_composite(char_scaled, (pos_x, pos_y))

        # Drifting light motes
        draw = ImageDraw.Draw(bg)
        np.random.seed(42)
        for i in range(35):
            px = int((np.random.rand() * width * 1.2 + t * 40.0) % (width + 60)) - 30
            py = int((np.random.rand() * height + t * 30.0 * (1 + (i % 2))) % height)
            pr = 2 + (i % 3)
            draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(255, 255, 255, 70))

        # Subtitles (Safe margin, clean white, drop shadow)
        active_sub = None
        for s_start, s_end, s_text in subtitles:
            if s_start <= t <= s_end:
                active_sub = s_text
                break

        if active_sub and t < (total_sec - 2.0):
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

            total_sub_h = len(lines) * 55
            base_ty = 1450 - (total_sub_h // 2)

            for l_idx, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font_sub)
                tw = bbox[2] - bbox[0]
                tx = (width - tw) // 2
                ty = base_ty + l_idx * 55
                for sx, sy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-2, -2), (2, 2)]:
                    draw.text((tx + sx, ty + sy), line, font=font_sub, fill=(0, 0, 0, 220))
                draw.text((tx, ty), line, font=font_sub, fill=(255, 255, 255, 255))

        # Outro Logo Reveal
        if t >= (total_sec - 2.5):
            logo_alpha = min(1.0, (t - (total_sec - 2.5)) / 0.8)
            overlay = Image.new("RGBA", (width, height), (0, 0, 0, int(logo_alpha * 180)))
            bg.alpha_composite(overlay)
            draw_ov = ImageDraw.Draw(bg)
            
            logo_text = "MYSTERYVERSE"
            bbox_logo = draw_ov.textbbox((0, 0), logo_text, font=font_logo)
            lw = bbox_logo[2] - bbox_logo[0]
            lx = (width - lw) // 2
            ly = height // 2 - 80

            glow_c = (255, 215, 0, int(logo_alpha * 240))
            for gx in range(-3, 4):
                for gy in range(-3, 4):
                    draw_ov.text((lx + gx, ly + gy), logo_text, font=font_logo, fill=glow_c)
            draw_ov.text((lx, ly), logo_text, font=font_logo, fill=(255, 255, 255, int(logo_alpha * 255)))

            tag_text = "EXPLORE THE UNKNOWN"
            bbox_tag = draw_ov.textbbox((0, 0), tag_text, font=font_tag)
            tw = bbox_tag[2] - bbox_tag[0]
            tx = (width - tw) // 2
            ty = ly + 90
            draw_ov.text((tx, ty), tag_text, font=font_tag, fill=(200, 225, 255, int(logo_alpha * 240)))

        frame_bgr = cv2.cvtColor(np.array(bg.convert("RGB")), cv2.COLOR_RGB2BGR)
        proc_out.stdin.write(frame_bgr.tobytes())

    proc_out.stdin.close()
    proc_out.wait()

    for cap in ref_caps.values():
        cap.release()

    print("Muxing final audio...")
    cmd_mux = [
        FFMPEG_BIN, "-y",
        "-i", temp_video,
        "-i", AUDIO_PATH,
        "-i", BED_PATH,
        "-filter_complex",
        "[1:a]volume=1.0[v];[2:a]volume=0.08,afade=t=out:st=36.0:d=2.5[m];[v][m]amix=inputs=2:duration=first[a]",
        "-map", "0:v",
        "-map", "[a]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        OUTPUT_VIDEO
    ]
    subprocess.run(cmd_mux, check=True)
    if os.path.exists(temp_video):
        os.remove(temp_video)
    print(f"Finished rendering Shorts: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    main()
