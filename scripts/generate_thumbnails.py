import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CHAR_DIR = r"c:\m\backend\static\character"
SCENES_DIR = r"c:\m\backend\static\scenes\layers"
REF_DIR = r"c:\m\references"
OUT_DIR = r"c:\m\output"
os.makedirs(OUT_DIR, exist_ok=True)

font_path = r"C:\Windows\Fonts\impact.ttf"
try:
    font_main_wide = ImageFont.truetype(font_path, 88)
    font_sub_wide = ImageFont.truetype(font_path, 52)
    font_badge_wide = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 32)
    
    font_main_short = ImageFont.truetype(font_path, 96)
    font_sub_short = ImageFont.truetype(font_path, 58)
    font_badge_short = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 36)
except Exception:
    font_main_wide = ImageFont.load_default()
    font_sub_wide = ImageFont.load_default()
    font_badge_wide = ImageFont.load_default()
    font_main_short = ImageFont.load_default()
    font_sub_short = ImageFont.load_default()
    font_badge_short = ImageFont.load_default()

def draw_text_with_effects(draw, text, pos, font, fill_color, stroke_color=(0, 0, 0), stroke_w=6, glow_color=None):
    x, y = pos
    if glow_color:
        for gx in range(-8, 9, 2):
            for gy in range(-8, 9, 2):
                draw.text((x + gx, y + gy), text, font=font, fill=glow_color)
    for sx in range(-stroke_w, stroke_w + 1):
        for sy in range(-stroke_w, stroke_w + 1):
            if sx*sx + sy*sy <= stroke_w*stroke_w:
                draw.text((x + sx, y + sy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=fill_color)

def generate_long_thumbnail():
    w, h = 1920, 1080
    bg = Image.open(os.path.join(SCENES_DIR, "wide_scene1_bg.jpg")).convert("RGBA").resize((w, h), Image.Resampling.LANCZOS)
    
    gradient = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d_g = ImageDraw.Draw(gradient)
    for x in range(int(w * 0.65)):
        alpha = int(220 * (1.0 - (x / (w * 0.65))))
        d_g.line([(x, 0), (x, h)], fill=(0, 5, 15, alpha))
    bg.alpha_composite(gradient)
    
    char = Image.open(os.path.join(CHAR_DIR, "jobelessboy_surprise.png")).convert("RGBA")
    ch_h = int(h * 0.95)
    ch_w = int(char.width * (ch_h / char.height))
    char = char.resize((ch_w, ch_h), Image.Resampling.LANCZOS)
    
    char_mask = char.split()[3].filter(ImageFilter.GaussianBlur(15))
    glow_char = Image.new("RGBA", (ch_w, ch_h), (0, 180, 255, 120))
    bg.paste(glow_char, (w - ch_w + 40, h - ch_h + 30), char_mask)
    bg.alpha_composite(char, (w - ch_w + 40, h - ch_h + 30))
    
    draw = ImageDraw.Draw(bg)
    
    badge_text = "● MYSTERYVERSE SPECIAL INVESTIGATION"
    draw.rounded_rectangle([90, 110, 720, 165], radius=10, fill=(200, 20, 20, 240), outline=(255, 80, 80, 255), width=2)
    draw.text((115, 122), badge_text, font=font_badge_wide, fill=(255, 255, 255))
    
    draw_text_with_effects(draw, "WHAT IF THE SUN", (90, 210), font_main_wide, fill_color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_w=7)
    draw_text_with_effects(draw, "DISAPPEARED?", (90, 315), font_main_wide, fill_color=(255, 215, 0), stroke_color=(0, 0, 0), stroke_w=8, glow_color=(255, 120, 0, 80))
    
    draw.rounded_rectangle([90, 445, 780, 530], radius=12, fill=(255, 210, 0, 255))
    draw.text((115, 458), "8 MINUTES OF LIGHT REMAINING", font=font_sub_wide, fill=(10, 10, 20))
    
    points = ["✓ Instant Darkness?", "✓ Does Earth Freeze?", "✓ Can Humanity Survive?"]
    for i, pt in enumerate(points):
        draw.text((95, 570 + i * 55), pt, font=font_sub_wide, fill=(180, 220, 255))
    
    out_path = os.path.join(OUT_DIR, "mysteryverse_sun_long_thumb.jpg")
    bg.convert("RGB").save(out_path, quality=95)
    print(f"Generated Long Thumbnail: {out_path}")
    return out_path

def generate_short_thumbnail():
    w, h = 1080, 1920
    cap = cv2.VideoCapture(os.path.join(REF_DIR, "Video-43510.mp4"))
    ret, frame = cap.read()
    cap.release()
    if ret and frame is not None:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        bg = Image.fromarray(frame_rgb).convert("RGBA")
        iw, ih = bg.size
        scale = max(w / iw, h / ih)
        bg = bg.resize((int(iw * scale), int(ih * scale)), Image.Resampling.BILINEAR)
        cx, cy = (bg.width - w) // 2, (bg.height - h) // 2
        bg = bg.crop((cx, cy, cx + w, cy + h))
    else:
        bg = Image.new("RGBA", (w, h), (10, 15, 30, 255))
        
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 110))
    bg.alpha_composite(overlay)
    
    char = Image.open(os.path.join(CHAR_DIR, "jobelessboy_curiosity.png")).convert("RGBA")
    ch_h = int(h * 0.62)
    ch_w = int(char.width * (ch_h / char.height))
    char = char.resize((ch_w, ch_h), Image.Resampling.LANCZOS)
    
    char_mask = char.split()[3].filter(ImageFilter.GaussianBlur(15))
    glow_char = Image.new("RGBA", (ch_w, ch_h), (255, 140, 0, 110))
    bg.paste(glow_char, ((w - ch_w) // 2, h - ch_h + 30), char_mask)
    bg.alpha_composite(char, ((w - ch_w) // 2, h - ch_h + 30))
    
    draw = ImageDraw.Draw(bg)
    
    draw.rounded_rectangle([70, 140, 500, 210], radius=12, fill=(20, 20, 40, 230), outline=(0, 200, 255, 255), width=3)
    draw.text((95, 153), "MYSTERYVERSE SHORTS", font=font_badge_short, fill=(0, 230, 255))
    
    draw_text_with_effects(draw, "THE SUN", (70, 260), font_main_short, fill_color=(255, 255, 255), stroke_color=(0, 0, 0), stroke_w=8)
    draw_text_with_effects(draw, "DISAPPEARED!", (70, 370), font_main_short, fill_color=(255, 50, 50), stroke_color=(0, 0, 0), stroke_w=9, glow_color=(255, 20, 20, 120))
    
    draw.rounded_rectangle([70, 510, 1010, 610], radius=15, fill=(255, 215, 0, 255))
    draw.text((100, 528), "COULD WE SURVIVE? ⚡", font=font_sub_short, fill=(10, 10, 20))
    
    out_path = os.path.join(OUT_DIR, "mysteryverse_sun_short_thumb.jpg")
    bg.convert("RGB").save(out_path, quality=95)
    print(f"Generated Shorts Thumbnail: {out_path}")
    return out_path

if __name__ == "__main__":
    generate_long_thumbnail()
    generate_short_thumbnail()
