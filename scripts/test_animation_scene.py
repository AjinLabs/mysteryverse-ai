"""
Test script to verify 2.5D character facial animation, particle effects, and video rendering.
"""
import os
import sys
import math
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, r"c:\m\backend")
from app.config import get_ffmpeg_path

ffmpeg_bin = get_ffmpeg_path()
print(f"Using FFmpeg: {ffmpeg_bin}")

# Load scene 3
scene3_path = r"c:\m\backend\static\scenes\scene3.jpg"
img_base = Image.open(scene3_path).convert("RGBA")
w, h = img_base.size

# Target render size: 1080x1920
target_w, target_h = 1080, 1920

# Create a 2-second test (48 frames)
test_dir = r"c:\m\backend\static\test_frames"
os.makedirs(test_dir, exist_ok=True)

# Generate 48 frames with:
# 1. Subtle camera push-in
# 2. Breathing / head sway
# 3. Rotating electron particles around the atom
# 4. Lip-sync mouth movement
# 5. Blink cycle

for frame_idx in range(48):
    t = frame_idx / 24.0
    
    # 1. Camera scale
    cam_scale = 1.0 + 0.04 * (frame_idx / 48.0)
    
    # Base frame copy
    frame = img_base.copy()
    draw = ImageDraw.Draw(frame)
    
    # 2. Orbiting electron particles around atom in boy's hands (atom center approx x=420, y=860 in 768x1376)
    atom_cx, atom_cy = 425, 860
    for orbit_idx, (rx, ry, angle_offset, col) in enumerate([
        (130, 45, 0.0, (14, 165, 233, 240)),
        (120, 50, math.pi / 3, (16, 185, 129, 240)),
        (140, 40, 2 * math.pi / 3, (245, 158, 11, 240)),
    ]):
        theta = t * 4.0 + angle_offset
        ex = atom_cx + rx * math.cos(theta)
        ey = atom_cy + ry * math.sin(theta)
        # Draw glowing electron particle
        r_glow = 8
        draw.ellipse([ex - r_glow, ey - r_glow, ex + r_glow, ey + r_glow], fill=(*col[:3], 120))
        draw.ellipse([ex - 4, ey - 4, ex + 4, ey + 4], fill=(255, 255, 255, 255))
    
    # 3. Blink on frame 24-29
    if 24 <= frame_idx <= 28:
        # Draw soft eyelid closure over eyes
        # Eyes approx x=320..520, y=500..560
        blink_prog = math.sin((frame_idx - 24) / 4.0 * math.pi)
        eyelid_h = int(25 * blink_prog)
        if eyelid_h > 2:
            # Subtle skin-toned eyelid
            draw.ellipse([310, 500, 395, 520 + eyelid_h], fill=(195, 138, 102, 230))
            draw.ellipse([435, 505, 520, 525 + eyelid_h], fill=(195, 138, 102, 230))
    
    # 4. Mouth lip movement (simulate talking)
    speech_amp = abs(math.sin(t * 12.0)) * 0.8
    if speech_amp > 0.2:
        # Mouth center approx x=415, y=630
        mw = int(45 + speech_amp * 15)
        mh = int(12 + speech_amp * 22)
        mx, my = 420, 635
        # Soft dark interior + teeth
        draw.ellipse([mx - mw//2, my - mh//2, mx + mw//2, my + mh//2], fill=(60, 20, 25, 210))
        draw.arc([mx - mw//2 + 4, my - mh//2 + 2, mx + mw//2 - 4, my + mh//2], 0, 180, fill=(240, 240, 245, 220), width=3)
    
    # Resize to target 1080x1920
    frame_scaled = frame.resize((target_w, target_h), Image.Resampling.LANCZOS)
    frame_scaled.convert("RGB").save(os.path.join(test_dir, f"frame_{frame_idx:04d}.jpg"), quality=95)

print("Rendered 48 test frames successfully!")
