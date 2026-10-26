import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from typing import Dict, Any, List, Optional
from app.config import THUMBNAILS_DIR, DEFAULT_MALAYALAM_FONT
from app.character.assets_manager import CHARACTER_DIR, generate_character_sprite

class ThumbnailEngine:
    def __init__(self, font_path: Optional[str] = None):
        self.font_path = font_path or (DEFAULT_MALAYALAM_FONT if os.path.exists(DEFAULT_MALAYALAM_FONT) else None)

    def _get_font(self, size: int) -> ImageFont.FreeTypeFont:
        if self.font_path and os.path.exists(self.font_path):
            try:
                return ImageFont.truetype(self.font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def generate_thumbnail(
        self,
        output_path: str,
        title_mal: str,
        category: str = "Science",
        expression: str = "surprise",
        width: int = 1280,
        height: int = 720,
        badge_text: str = "സത്യം ഇതാണ്!"
    ) -> str:
        """
        Creates a high-CTR, cinematic YouTube thumbnail with Malayalam typography,
        dramatic lighting, and recurring animated host Dr. Kiran.
        """
        base = Image.new("RGBA", (width, height), (10, 15, 26, 255))
        draw = ImageDraw.Draw(base)

        # 1. Background dramatic gradient & glow
        cx, cy = int(width * 0.35), int(height * 0.45)
        bg_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(bg_glow)
        # Deep cosmic indigo + electric cyan
        g_draw.ellipse([cx - 450, cy - 350, cx + 450, cy + 350], fill=(6, 182, 212, 100))
        g_draw.ellipse([int(width * 0.8) - 300, int(height * 0.3) - 300, int(width * 0.8) + 300, int(height * 0.3) + 300], fill=(245, 158, 11, 70))
        bg_glow = bg_glow.filter(ImageFilter.GaussianBlur(radius=80))
        base.alpha_composite(bg_glow)

        # 2. Cyber grid / cosmic stars
        draw.line([(0, height - 120), (width, height - 120)], fill=(30, 41, 59, 200), width=2)
        draw.line([(0, height - 60), (width, height - 60)], fill=(30, 41, 59, 200), width=2)

        # 3. Add Host jobelessboy sprite (Right side, large and expressive)
        sprite_path = CHARACTER_DIR / f"jobelessboy_{expression}.png"
        if not sprite_path.exists():
            sprite_path = CHARACTER_DIR / f"dr_kiran_{expression}.png"
        if not sprite_path.exists():
            sprite_path = Path(generate_character_sprite(expression))
        
        host_img = Image.open(sprite_path).convert("RGBA")
        host_size = int(height * 0.98)
        host_resized = host_img.resize((host_size, host_size), Image.Resampling.LANCZOS)
        
        # Add outer glow to character silhouette
        mask = host_resized.split()[3]
        outline = Image.new("RGBA", host_resized.size, (6, 182, 212, 180))
        glow_outline = Image.new("RGBA", host_resized.size, (0, 0, 0, 0))
        glow_outline.paste(outline, (0, 0), mask)
        glow_outline = glow_outline.filter(ImageFilter.GaussianBlur(radius=8))

        host_x = width - host_size + 40
        host_y = height - host_size + 20
        base.paste(glow_outline, (host_x, host_y), glow_outline)
        base.paste(host_resized, (host_x, host_y), host_resized)

        # 4. Attention Badge (e.g. "സത്യം ഇതാണ്!" / "രഹസ്യം വെളിപ്പെടുന്നു!")
        badge_font = self._get_font(28)
        badge_w, badge_h = 240, 50
        bx, by = 60, 60
        # Rounded pill badge with amber neon border
        draw.rounded_rectangle([bx, by, bx + badge_w, by + badge_h], radius=10, fill=(245, 158, 11, 230), outline=(255, 255, 255, 255), width=2)
        draw.text((bx + 18, by + 8), badge_text, font=badge_font, fill=(0, 0, 0, 255))

        # 5. Large, Bold Malayalam Title (High contrast with dark drop shadow)
        title_font = self._get_font(54)
        
        # Wrap title into 2-3 punchy lines
        words = title_mal.split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 18:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))
        lines = lines[:3]  # Max 3 lines

        ty = 140
        for line in lines:
            tx = 60
            # Dark backing banner for ultra readability
            text_box = [tx - 15, ty - 8, tx + min(width * 0.55, len(line) * 38), ty + 68]
            draw.rounded_rectangle(text_box, radius=8, fill=(15, 23, 42, 230))
            
            # Text shadow
            draw.text((tx + 3, ty + 3), line, font=title_font, fill=(0, 0, 0, 255))
            # Text primary (bright yellow / white for contrast)
            draw.text((tx, ty), line, font=title_font, fill=(255, 240, 50, 255))
            ty += 80

        # 6. Channel tag footer
        tag_font = self._get_font(24)
        draw.text((60, height - 70), "MYSTERY VERSE MALAYALAM  |  4K UHD", font=tag_font, fill=(6, 182, 212, 220))

        # Final save
        rgb_base = base.convert("RGB")
        rgb_base.save(output_path, "JPEG", quality=95)
        return output_path
