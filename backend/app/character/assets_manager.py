import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
from app.config import STATIC_DIR
from app.character.bible import CHARACTER_BIBLE

CHARACTER_DIR = STATIC_DIR / "character"
CHARACTER_DIR.mkdir(parents=True, exist_ok=True)

def generate_character_sprite(expression: str = "explanation", size: int = 512) -> str:
    """
    Returns or synthesizes the official high-res 3D Pixar host sprite
    for jobelessboy in the specified emotional state with alpha transparency.
    """
    valid_expressions = ["curiosity", "surprise", "explanation", "excitement", "caution", "humour"]
    if expression not in valid_expressions:
        expression = "explanation"

    pixar_path = CHARACTER_DIR / f"jobelessboy_{expression}.png"
    if pixar_path.exists() and pixar_path.stat().st_size > 50000:
        return str(pixar_path)

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center_x = size // 2
    center_y = size // 2

    # Color Palette from Character Bible
    c_skin = (235, 185, 150, 255)
    c_skin_shadow = (205, 155, 120, 255)
    c_hair = (25, 25, 30, 255)
    c_hair_highlight = (50, 60, 75, 255)
    c_coat = (30, 41, 59, 255)
    c_cyan_glow = (6, 182, 212, 255)
    c_amber_glow = (245, 158, 11, 255)
    c_white = (255, 255, 255, 255)
    c_pupil = (2, 132, 199, 255)

    # 1. Background subtle cyber aura glow
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    glow_draw.ellipse(
        [center_x - 170, center_y - 170, center_x + 170, center_y + 170],
        fill=(6, 182, 212, 45)
    )
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(radius=25))
    img.alpha_composite(glow_layer)

    # 2. Torso / Field Explorer Coat
    coat_top = center_y + 110
    draw.polygon([
        (center_x - 160, size),
        (center_x - 90, coat_top),
        (center_x + 90, coat_top),
        (center_x + 160, size)
    ], fill=c_coat)

    # Coat collar neon trim
    draw.line([(center_x - 90, coat_top), (center_x, coat_top + 45)], fill=c_cyan_glow, width=4)
    draw.line([(center_x + 90, coat_top), (center_x, coat_top + 45)], fill=c_cyan_glow, width=4)
    draw.polygon([(center_x - 30, coat_top), (center_x + 30, coat_top), (center_x, coat_top + 50)], fill=(15, 23, 42, 255))

    # 3. Neck
    draw.rectangle([center_x - 32, center_y + 60, center_x + 32, coat_top + 5], fill=c_skin_shadow)

    # 4. Head / Jaw
    head_box = [center_x - 95, center_y - 95, center_x + 95, center_y + 85]
    draw.ellipse(head_box, fill=c_skin)
    # Chin taper
    draw.polygon([
        (center_x - 70, center_y + 40),
        (center_x + 70, center_y + 40),
        (center_x, center_y + 98)
    ], fill=c_skin)

    # 5. Ears & Holographic Earpiece
    # Left Ear
    draw.ellipse([center_x - 105, center_y - 15, center_x - 85, center_y + 35], fill=c_skin_shadow)
    # Right Ear with Holo-Lens Earpiece
    draw.ellipse([center_x + 85, center_y - 15, center_x + 105, center_y + 35], fill=c_skin_shadow)
    # Holographic gear (Right side earpiece)
    draw.ellipse([center_x + 92, center_y - 5, center_x + 108, center_y + 15], fill=c_cyan_glow)
    draw.line([(center_x + 100, center_y + 5), (center_x + 75, center_y + 2)], fill=c_cyan_glow, width=2)

    # 6. Hair
    # Main hair mass
    draw.ellipse([center_x - 105, center_y - 135, center_x + 105, center_y - 20], fill=c_hair)
    # Stylized exploratory tufts
    draw.polygon([(center_x - 90, center_y - 80), (center_x - 110, center_y - 120), (center_x - 60, center_y - 105)], fill=c_hair)
    draw.polygon([(center_x + 90, center_y - 80), (center_x + 115, center_y - 115), (center_x + 55, center_y - 110)], fill=c_hair)
    draw.polygon([(center_x - 40, center_y - 120), (center_x, center_y - 150), (center_x + 30, center_y - 115)], fill=c_hair_highlight)

    # 7. Expressions (Dynamic based on parameter)
    eye_y = center_y + 5
    eye_offset = 38

    # Left & Right Eye Positions
    left_eye_center = (center_x - eye_offset, eye_y)
    right_eye_center = (center_x + eye_offset, eye_y)

    if expression == "curiosity":
        # One eyebrow raised, head tilted thought
        draw.arc([center_x - 55, eye_y - 25, center_x - 20, eye_y - 5], 180, 360, fill=c_hair, width=5)
        draw.arc([center_x + 20, eye_y - 38, center_x + 55, eye_y - 15], 180, 360, fill=c_hair, width=6)  # High raised
        # Eyes
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 16, ec[1] - 12, ec[0] + 16, ec[1] + 12], fill=c_white)
            draw.ellipse([ec[0] - 8, ec[1] - 10, ec[0] + 8, ec[1] + 6], fill=c_pupil)
            draw.ellipse([ec[0] - 3, ec[1] - 6, ec[0] + 2, ec[1] - 1], fill=c_white)
        # Mouth: analytical purse
        draw.ellipse([center_x - 8, center_y + 55, center_x + 8, center_y + 65], fill=(160, 80, 70, 255))

    elif expression == "surprise":
        # Both brows high, mouth O-shaped
        draw.arc([center_x - 55, eye_y - 35, center_x - 20, eye_y - 15], 180, 360, fill=c_hair, width=5)
        draw.arc([center_x + 20, eye_y - 35, center_x + 55, eye_y - 15], 180, 360, fill=c_hair, width=5)
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 18, ec[1] - 16, ec[0] + 18, ec[1] + 16], fill=c_white)
            draw.ellipse([ec[0] - 9, ec[1] - 9, ec[0] + 9, ec[1] + 9], fill=c_pupil)
            draw.ellipse([ec[0] - 4, ec[1] - 6, ec[0] + 2, ec[1]], fill=c_white)
        draw.ellipse([center_x - 14, center_y + 50, center_x + 14, center_y + 75], fill=(120, 50, 50, 255))

    elif expression == "excitement":
        # Happy arched brows, wide smile
        draw.arc([center_x - 55, eye_y - 28, center_x - 20, eye_y - 10], 190, 350, fill=c_hair, width=5)
        draw.arc([center_x + 20, eye_y - 28, center_x + 55, eye_y - 10], 190, 350, fill=c_hair, width=5)
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 16, ec[1] - 12, ec[0] + 16, ec[1] + 12], fill=c_white)
            draw.ellipse([ec[0] - 8, ec[1] - 8, ec[0] + 8, ec[1] + 8], fill=c_pupil)
            draw.ellipse([ec[0] - 2, ec[1] - 4, ec[0] + 3, ec[1] + 1], fill=c_white)
        # Wide enthusiastic grin
        draw.pieslice([center_x - 28, center_y + 40, center_x + 28, center_y + 75], 0, 180, fill=(160, 40, 40, 255))
        draw.rectangle([center_x - 20, center_y + 42, center_x + 20, center_y + 52], fill=c_white)  # Teeth

    elif expression == "caution":
        # Serious furrowed brows, stern mouth
        draw.line([(center_x - 55, eye_y - 15), (center_x - 20, eye_y - 24)], fill=c_hair, width=5)
        draw.line([(center_x + 20, eye_y - 24), (center_x + 55, eye_y - 15)], fill=c_hair, width=5)
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 15, ec[1] - 9, ec[0] + 15, ec[1] + 9], fill=c_white)
            draw.ellipse([ec[0] - 7, ec[1] - 7, ec[0] + 7, ec[1] + 7], fill=c_pupil)
        draw.line([(center_x - 22, center_y + 58), (center_x + 22, center_y + 58)], fill=(130, 60, 60, 255), width=4)

    elif expression == "humour":
        # Wry smile, amused brow
        draw.arc([center_x - 55, eye_y - 22, center_x - 20, eye_y - 10], 190, 350, fill=c_hair, width=4)
        draw.arc([center_x + 20, eye_y - 32, center_x + 55, eye_y - 12], 180, 360, fill=c_hair, width=5)
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 15, ec[1] - 10, ec[0] + 15, ec[1] + 10], fill=c_white)
            draw.ellipse([ec[0] - 7, ec[1] - 7, ec[0] + 7, ec[1] + 7], fill=c_pupil)
        # Asymmetrical smirk
        draw.arc([center_x - 20, center_y + 40, center_x + 26, center_y + 68], 20, 160, fill=(150, 50, 50, 255), width=5)

    else:  # "explanation" (default)
        # Articulate, engaging, neutral-confident
        draw.arc([center_x - 55, eye_y - 25, center_x - 20, eye_y - 10], 190, 350, fill=c_hair, width=5)
        draw.arc([center_x + 20, eye_y - 25, center_x + 55, eye_y - 10], 190, 350, fill=c_hair, width=5)
        for ec in [left_eye_center, right_eye_center]:
            draw.ellipse([ec[0] - 16, ec[1] - 11, ec[0] + 16, ec[1] + 11], fill=c_white)
            draw.ellipse([ec[0] - 8, ec[1] - 8, ec[0] + 8, ec[1] + 8], fill=c_pupil)
            draw.ellipse([ec[0] - 3, ec[1] - 4, ec[0] + 2, ec[1] + 1], fill=c_white)
        # Gentle open smile
        draw.arc([center_x - 22, center_y + 45, center_x + 22, center_y + 65], 10, 170, fill=(160, 60, 60, 255), width=4)

    # 8. Nose
    draw.polygon([
        (center_x, center_y + 15),
        (center_x - 6, center_y + 35),
        (center_x + 6, center_y + 35)
    ], fill=c_skin_shadow)

    out_path = CHARACTER_DIR / f"jobelessboy_{expression}.png"
    img.save(str(out_path), "PNG")
    
    # Backward compatible alias
    legacy_path = CHARACTER_DIR / f"dr_kiran_{expression}.png"
    img.save(str(legacy_path), "PNG")
    return str(out_path)

def initialize_character_assets() -> dict:
    """Generates all 6 canonical character expressions for jobelessboy (and aliases)."""
    paths = {}
    for expr in ["curiosity", "surprise", "explanation", "excitement", "caution", "humour"]:
        p = generate_character_sprite(expr, size=512)
        paths[expr] = p
    return paths

if __name__ == "__main__":
    generated = initialize_character_assets()
    print("Generated Dr. Kiran sprites:", generated)
