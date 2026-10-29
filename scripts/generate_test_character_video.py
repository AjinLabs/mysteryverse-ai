"""
Execute full pipeline rendering for the Cinematic Character Video Engine test video
featuring official host 'jobelessboy'.
Generates:
- 16:9 Widescreen Full HD MP4 (1920x1080)
- 9:16 Vertical Shorts Full HD MP4 (1080x1920)
- High-res thumbnails with host overlay
- Syncs to frontend/public
- Registers into SQLite database
"""

import os
import sys
import time
import asyncio
import subprocess
import sqlite3
import shutil
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    THUMBNAILS_DIR,
    DB_PATH,
    get_ffmpeg_path
)
from app.audio.tts_service import MalayalamTTSService
from app.animation.cinematic_character_engine import CinematicCharacterEngine
from app.thumbnail.thumbnail_engine import ThumbnailEngine

async def run_pipeline():
    start_time = time.time()
    print("=" * 70)
    print("MYSTERYVERSE AI - CINEMATIC CHARACTER VIDEO ENGINE")
    print("Target Character: jobelessboy (MysteryVerse‌MysteryVerse MysteryVerse)")
    print("=" * 70)

    # 1. Synthesize Malayalam Voiceover Audio
    print("\n[Step 1/5] Synthesizing authentic English narration...")
    audio_path = str(AUDIO_DIR / "cinematic_jobelessboy_audio.mp3")
    script_mal = (
        "MysteryVerse MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse‌MysteryVerse MysteryVerse! "
        "MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse? "
        "MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse! "
        "MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse!"
    )
    tts = MalayalamTTSService()
    res = await tts.synthesize(script_mal, audio_path, rate="+8%", pitch="+10Hz")
    print(f"Generated speech audio: {audio_path} ({res['file_size']} bytes)")

    # Measure exact audio duration
    ffmpeg_bin = get_ffmpeg_path()
    cmd = [ffmpeg_bin, "-i", audio_path, "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration = 20.5
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break
    print(f"Verified Audio Duration: {duration:.2f} seconds")

    # 2. Render 16:9 Widescreen Cinematic Video (1920x1080)
    print("\n[Step 2/5] Rendering 16:9 Widescreen Broadcast Video (1920x1080)...")
    out_169 = str(VIDEOS_DIR / "cinematic_jobelessboy_solarsystem_169.mp4")
    engine_169 = CinematicCharacterEngine(width=1920, height=1080, fps=24)
    engine_169.generate_cinematic_video(out_169, audio_path, duration)
    print(f"Successfully rendered 16:9 Video: {out_169} ({os.path.getsize(out_169)} bytes)")

    # 3. Render 9:16 Vertical Shorts Video (1080x1920)
    print("\n[Step 3/5] Rendering 9:16 YouTube Shorts Video (1080x1920)...")
    out_916 = str(VIDEOS_DIR / "cinematic_jobelessboy_solarsystem_916.mp4")
    engine_916 = CinematicCharacterEngine(width=1080, height=1920, fps=24)
    engine_916.generate_cinematic_video(out_916, audio_path, duration)
    print(f"Successfully rendered 9:16 Video: {out_916} ({os.path.getsize(out_916)} bytes)")

    # 4. Generate High-Impact 3D Thumbnails with jobelessboy host
    print("\n[Step 4/5] Generating thumbnails with jobelessboy host...")
    thumb_engine = ThumbnailEngine()
    thumb_169 = str(THUMBNAILS_DIR / "cinematic_jobelessboy_solarsystem_thumb_169.jpg")
    thumb_engine.generate_thumbnail(
        output_path=thumb_169,
        title_mal="MysteryVerse MysteryVerse!",
        category="Space",
        expression="excitement",
        badge_text="MysteryVerse MysteryVerse!"
    )
    print(f"Generated 16:9 Thumbnail: {thumb_169}")

    # 5. Sync to Frontend Public Directory and Database
    print("\n[Step 5/5] Syncing to frontend and registering into database...")
    fe_videos = Path(r"c:\m\frontend\public\static\videos")
    fe_thumbs = Path(r"c:\m\frontend\public\static\thumbnails")
    fe_videos.mkdir(parents=True, exist_ok=True)
    fe_thumbs.mkdir(parents=True, exist_ok=True)

    shutil.copy2(out_169, fe_videos / "cinematic_jobelessboy_solarsystem_169.mp4")
    shutil.copy2(out_916, fe_videos / "cinematic_jobelessboy_solarsystem_916.mp4")
    shutil.copy2(thumb_169, fe_thumbs / "cinematic_jobelessboy_solarsystem_thumb_169.jpg")

    # Register into SQLite Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO published_videos 
        (id, topic_title, format_type, video_path, thumbnail_path, title_malayalam, title_english, description_malayalam, duration_sec, published_to_youtube, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "cinematic_jobelessboy_solarsystem_169",
        "MysteryVerse MysteryVerse (Solar System Mysteries)",
        "widescreen_169",
        "/static/videos/cinematic_jobelessboy_solarsystem_169.mp4",
        "/static/thumbnails/cinematic_jobelessboy_solarsystem_thumb_169.jpg",
        "MysteryVerse MysteryVerse MysteryVerse — MysteryVerse‌MysteryVerse MysteryVerse MysteryVerse!",
        "Astonishing Mysteries of the Solar System with jobelessboy",
        "MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse‌MysteryVerse MysteryVerse!",
        duration,
        0
    ))
    cursor.execute("""
        INSERT OR REPLACE INTO published_videos 
        (id, topic_title, format_type, video_path, thumbnail_path, title_malayalam, title_english, description_malayalam, duration_sec, published_to_youtube, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "cinematic_jobelessboy_solarsystem_916",
        "MysteryVerse MysteryVerse (Solar System Mysteries Shorts)",
        "shorts_916",
        "/static/videos/cinematic_jobelessboy_solarsystem_916.mp4",
        "/static/thumbnails/cinematic_jobelessboy_solarsystem_thumb_169.jpg",
        "MysteryVerse MysteryVerse MysteryVerse MysteryVerse? 🪐✨ #Shorts",
        "How Were Saturn's Rings Formed? with jobelessboy #Shorts",
        "MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse! #shorts #space #malayalam",
        duration,
        0
    ))
    conn.commit()
    conn.close()

    total_time = time.time() - start_time
    print(f"\nAll operations completed successfully in {total_time:.1f} seconds!")
    print(f"16:9 Video: file:///{out_169}")
    print(f"9:16 Video: file:///{out_916}")

if __name__ == "__main__":
    asyncio.run(run_pipeline())
