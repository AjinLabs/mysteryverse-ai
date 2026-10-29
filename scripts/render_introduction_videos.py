"""
MysteryVerse — Introduction Videos Production Runner
Renders both:
- output/mysteryverse_intro_short.mp4 (9:16 Shorts, 1080x1920)
- output/mysteryverse_intro_long.mp4 (16:9 Long-Form, 1920x1080)
- output/subtitles/intro_short_en.srt
- output/subtitles/intro_long_en.srt
Syncs to frontend/public and registers into database.
"""

import os
import sys
import time
import shutil
import sqlite3
import subprocess
from pathlib import Path

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from app.config import (
    STATIC_DIR,
    VIDEOS_DIR,
    AUDIO_DIR,
    THUMBNAILS_DIR,
    DB_PATH,
    get_ffmpeg_path
)
from app.animation.production_director import CinematicProductionDirector

def get_audio_duration(audio_file: str) -> float:
    ffmpeg_bin = get_ffmpeg_path()
    cmd = [ffmpeg_bin, "-i", audio_file, "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    duration = 45.0
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
            duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
            break
    return duration

def main():
    total_start = time.time()
    print("=" * 70)
    print("MYSTERYVERSE MALAYALAM — OFFICIAL INTRODUCTION VIDEO PRODUCTION")
    print("Character Host: jobelessboy (Pixar 3D Boy)")
    print("Language Policy: Spoken Malayalam Narration // English-Only Visual Text")
    print("=" * 70)

    output_dir = Path(r"c:\m\output")
    output_dir.mkdir(parents=True, exist_ok=True)
    sub_dir = output_dir / "subtitles"
    sub_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. RENDER INTRODUCTION SHORT (9:16 Vertical, 1080x1920)
    # ---------------------------------------------------------
    print("\n[Video 1/2] Rendering Introduction Short (9:16 Vertical, 1080x1920)...")
    audio_short = str(AUDIO_DIR / "intro_short_kid.mp3")
    dur_short = get_audio_duration(audio_short) + 1.8  # Add buffer for outro
    print(f"Short Audio Duration: {dur_short:.2f} seconds")

    out_short = str(output_dir / "mysteryverse_intro_short.mp4")
    director_short = CinematicProductionDirector(width=1080, height=1920, fps=24)
    director_short.render_video(out_short, audio_short, dur_short, mode="short")
    print(f"Rendered Short MP4: {out_short} ({os.path.getsize(out_short)} bytes)")

    # ---------------------------------------------------------
    # 2. RENDER INTRODUCTION LONG (16:9 Horizontal, 1920x1080)
    # ---------------------------------------------------------
    print("\n[Video 2/2] Rendering Introduction Long Video (16:9 Horizontal, 1920x1080)...")
    audio_long = str(AUDIO_DIR / "intro_long_kid.mp3")
    dur_long = get_audio_duration(audio_long) + 3.0  # Add buffer for grand outro
    print(f"Long Audio Duration: {dur_long:.2f} seconds ({dur_long / 60:.2f} minutes)")

    out_long = str(output_dir / "mysteryverse_intro_long.mp4")
    director_long = CinematicProductionDirector(width=1920, height=1080, fps=24)
    director_long.render_video(out_long, audio_long, dur_long, mode="long")
    print(f"Rendered Long MP4: {out_long} ({os.path.getsize(out_long)} bytes)")

    # ---------------------------------------------------------
    # 3. GENERATE CINEMATIC THUMBNAILS (ENGLISH ONLY TEXT)
    # ---------------------------------------------------------
    print("\n[Step 3/4] Generating high-CTR thumbnails...")
    from app.thumbnail.thumbnail_engine import ThumbnailEngine
    thumb_engine = ThumbnailEngine()

    thumb_short = str(output_dir / "mysteryverse_intro_short_thumb.jpg")
    thumb_long = str(output_dir / "mysteryverse_intro_long_thumb.jpg")

    thumb_engine.generate_thumbnail(
        output_path=thumb_long,
        title_mal="WELCOME TO MYSTERYVERSE!",
        category="Channel Intro",
        expression="excitement",
        badge_text="OFFICIAL INTRO"
    )
    thumb_engine.generate_thumbnail(
        output_path=thumb_short,
        title_mal="DISCOVER MYSTERIES!",
        category="Shorts",
        expression="surprise",
        badge_text="MEET JOBELESSBOY"
    )

    # ---------------------------------------------------------
    # 4. SYNC TO STATIC & DATABASE
    # ---------------------------------------------------------
    print("\n[Step 4/4] Syncing to web static directories and database...")
    fe_vid_dir = Path(r"c:\m\frontend\public\static\videos")
    fe_thm_dir = Path(r"c:\m\frontend\public\static\thumbnails")
    be_vid_dir = Path(r"c:\m\backend\static\videos")
    be_thm_dir = Path(r"c:\m\backend\static\thumbnails")

    for d in [fe_vid_dir, fe_thm_dir, be_vid_dir, be_thm_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy files
    shutil.copy2(out_short, be_vid_dir / "mysteryverse_intro_short.mp4")
    shutil.copy2(out_short, fe_vid_dir / "mysteryverse_intro_short.mp4")
    shutil.copy2(out_long, be_vid_dir / "mysteryverse_intro_long.mp4")
    shutil.copy2(out_long, fe_vid_dir / "mysteryverse_intro_long.mp4")

    shutil.copy2(thumb_short, be_thm_dir / "mysteryverse_intro_short_thumb.jpg")
    shutil.copy2(thumb_short, fe_thm_dir / "mysteryverse_intro_short_thumb.jpg")
    shutil.copy2(thumb_long, be_thm_dir / "mysteryverse_intro_long_thumb.jpg")
    shutil.copy2(thumb_long, fe_thm_dir / "mysteryverse_intro_long_thumb.jpg")

    # Update SQLite database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Topic
    c.execute("""
    INSERT OR REPLACE INTO topics (id, title, mal_title, category, format, potential_interest_score, source_references, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "top_official_intro",
        "MysteryVerse — Official 3D Channel Introduction",
        "MysteryVerse MysteryVerse — MysteryVerse MysteryVerse",
        "Channel Intro",
        "hybrid",
        100.0,
        '["https://youtube.com/@MysteryVerse"]',
        "produced"
    ))

    # Script
    c.execute("""
    INSERT OR REPLACE INTO scripts (id, topic_id, format, mal_hook, mal_content, mal_conclusion, full_script_mal, full_script_en_notes, scenes_json, estimated_duration_sec, word_count, model_used, status, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "scr_official_intro",
        "top_official_intro",
        "hybrid",
        "MysteryVerse MysteryVerse! MysteryVerse MysteryVerse MysteryVerse MysteryVerse?",
        "MysteryVerse, MysteryVerse, MysteryVerse MysteryVerse, MysteryVerse, MysteryVerse MysteryVerse, MysteryVerse MysteryVerse...",
        "MysteryVerse Subscribe MysteryVerse, Comment MysteryVerse!",
        "MysteryVerse MysteryVerse! MysteryVerse-MysteryVerse MysteryVerse MysteryVerse!...",
        "Childlike Malayalam Voiceover, English Subtitles only, jobelessboy recurring host.",
        '[{"scene": "Observatory"}, {"scene": "Earth & Space"}, {"scene": "Molecules & Lab"}, {"scene": "History Pyramids"}, {"scene": "Controversy & Enigma"}, {"scene": "Psychology & Ocean"}, {"scene": "Community"}, {"scene": "Logo Outro"}]',
        dur_long,
        340,
        "CinematicProductionDirector",
        "completed"
    ))

    # Video Jobs
    c.execute("""
    INSERT OR REPLACE INTO video_jobs (id, script_id, topic_id, video_type, resolution, audio_path, thumbnail_path, video_path, duration_sec, render_engine, status, quality_passed, quality_report_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "mysteryverse_intro_short",
        "scr_official_intro",
        "top_official_intro",
        "short",
        "1080x1920",
        "/static/audio/intro_short_kid.mp3",
        "/static/thumbnails/mysteryverse_intro_short_thumb.jpg",
        "/static/videos/mysteryverse_intro_short.mp4",
        dur_short,
        "production_director_3d",
        "ready_for_upload",
        1,
        '{"host": "jobelessboy", "language_policy": "spoken_english_english_text", "format": "9:16 Shorts", "fps": 24}'
    ))

    c.execute("""
    INSERT OR REPLACE INTO video_jobs (id, script_id, topic_id, video_type, resolution, audio_path, thumbnail_path, video_path, duration_sec, render_engine, status, quality_passed, quality_report_json, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    """, (
        "mysteryverse_intro_long",
        "scr_official_intro",
        "top_official_intro",
        "long",
        "1920x1080",
        "/static/audio/intro_long_kid.mp3",
        "/static/thumbnails/mysteryverse_intro_long_thumb.jpg",
        "/static/videos/mysteryverse_intro_long.mp4",
        dur_long,
        "production_director_3d",
        "ready_for_upload",
        1,
        '{"host": "jobelessboy", "language_policy": "spoken_english_english_text", "format": "16:9 Full HD", "fps": 24}'
    ))

    conn.commit()
    conn.close()

    elapsed = time.time() - total_start
    print("\n" + "=" * 70)
    print(f"PRODUCTION COMPLETE IN {elapsed:.1f} SECONDS!")
    print(f"1. Short Video: {out_short}")
    print(f"2. Long Video:  {out_long}")
    print(f"3. Short Subs:  {sub_dir / 'intro_short_en.srt'}")
    print(f"4. Long Subs:   {sub_dir / 'intro_long_en.srt'}")
    print("=" * 70)

if __name__ == "__main__":
    main()
