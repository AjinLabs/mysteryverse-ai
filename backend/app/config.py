import os
import shutil
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
VIDEOS_DIR = STATIC_DIR / "videos"
THUMBNAILS_DIR = STATIC_DIR / "thumbnails"
AUDIO_DIR = STATIC_DIR / "audio"
SUBTITLES_DIR = STATIC_DIR / "subtitles"
TEMP_DIR = DATA_DIR / "temp"

for directory in [DATA_DIR, STATIC_DIR, VIDEOS_DIR, THUMBNAILS_DIR, AUDIO_DIR, SUBTITLES_DIR, TEMP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "mysteryverse.db"

# Official Channel Target
TARGET_CHANNEL_NAME = "MYSTERY VERSE MALAYALAM"
TARGET_CHANNEL_HANDLE = "@MYSTERYVERSE-MALAYALAM"
TARGET_CHANNEL_URL = "https://www.youtube.com/@MYSTERYVERSE-MALAYALAM"

# Monthly Production Targets
TARGET_SHORTS_PER_MONTH = 30
TARGET_LONGS_PER_MONTH = 30

# Free-Tier Audio Settings (Malayalam Neural Voices)
# Tuned for energetic, high-reach, charismatic Malayalam kid voice for jobelessboy
DEFAULT_MALE_VOICE = "ml-IN-MidhunNeural"
DEFAULT_FEMALE_VOICE = "ml-IN-SobhanaNeural"
DEFAULT_VOICE_RATE = "+10%"
DEFAULT_VOICE_PITCH = "+24Hz"

HOST_CHARACTER_NAME = "jobelessboy"

# Preferred indic font for Malayalam rendering
DEFAULT_MALAYALAM_FONT = r"C:\Windows\Fonts\Nirmala.ttc"

def get_ffmpeg_path() -> Optional[str]:
    """Detect FFmpeg executable via imageio_ffmpeg, system PATH or custom location."""
    try:
        import imageio_ffmpeg
        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.path.exists(exe):
            return exe
    except Exception:
        pass
    
    path = shutil.which("ffmpeg")
    if path:
        return path
    
    # Common Windows fallback paths
    common_paths = [
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\ffmpeg\bin\ffmpeg.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe")
    ]
    for p in common_paths:
        if os.path.exists(p):
            return p
    return None

def get_blender_path() -> Optional[str]:
    """Detect Blender executable via PATH or common Windows installation directories."""
    path = shutil.which("blender")
    if path:
        return path
    
    candidates = [
        r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
        r"C:\Program Files\Blender Foundation\Blender\blender.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

class Settings:
    APP_NAME: str = "MYSTERYVERSE AI Autonomous Media Suite"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    OAUTH_CLIENT_SECRETS_FILE: str = str(DATA_DIR / "client_secrets.json")
    OAUTH_TOKEN_FILE: str = str(DATA_DIR / "oauth_token.json")
    EMERGENCY_KILLSWITCH_FILE: str = str(DATA_DIR / "KILLSWITCH_ACTIVE")
    
    # Quality & Publishing Gate Policies
    MIN_ORIGINALITY_SCORE: float = 85.0
    MIN_FACT_CHECK_CONFIDENCE: float = 80.0
    AUTO_PUBLISH_DEFAULT: bool = False  # Start in safe staging mode; user can toggle to full autonomous
    DEMO_MODE: bool = False
    
    # Quota Limits
    YOUTUBE_DAILY_QUOTA_LIMIT: int = 10000
    YOUTUBE_UPLOAD_COST: int = 1600
    
settings = Settings()
