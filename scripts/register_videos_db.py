import sqlite3
import sys
from pathlib import Path

# Ensure UTF-8 on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# 1. Topic
c.execute('''
INSERT OR REPLACE INTO topics (id, title, mal_title, category, format, potential_interest_score, source_references, status, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
''', (
    'top_solarsystem_secrets',
    'Solar System Secrets and Saturn Rings',
    'MysteryVerse MysteryVerse MysteryVerse MysteryVerse',
    'Space',
    'hybrid',
    99.8,
    '["https://science.nasa.gov/saturn/rings"]',
    'produced'
))

# 2. Script
c.execute('''
INSERT OR REPLACE INTO scripts (id, topic_id, format, mal_hook, mal_content, mal_conclusion, full_script_mal, full_script_en_notes, scenes_json, estimated_duration_sec, word_count, model_used, status, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
''', (
    'scr_solarsystem_secrets',
    'top_solarsystem_secrets',
    'hybrid',
    'MysteryVerse MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse‌MysteryVerse MysteryVerse!',
    'MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse!',
    'MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse!',
    'MysteryVerse MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse‌MysteryVerse MysteryVerse! MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse? MysteryVerse, MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse! MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse MysteryVerse!',
    'Scene 1: Wide shot Sun and Planets, Scene 2: Medium shot Saturn Rings, Scene 3: Close-up Subscribe CTA',
    '[{"scene_num": 1, "camera": "wide", "host": "waving", "topic": "Sun and Planets"}, {"scene_num": 2, "camera": "medium", "host": "explanation", "topic": "Saturn Rings"}, {"scene_num": 3, "camera": "close_up", "host": "welcome", "topic": "Subscribe CTA"}]',
    20.5,
    38,
    'CinematicCharacterEngine',
    'completed'
))

# 3. Video Jobs (Widescreen 16:9 and Shorts 9:16)
c.execute('''
INSERT OR REPLACE INTO video_jobs (id, script_id, topic_id, video_type, resolution, audio_path, thumbnail_path, video_path, duration_sec, render_engine, status, quality_passed, quality_report_json, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
''', (
    'cinematic_jobelessboy_solarsystem_169',
    'scr_solarsystem_secrets',
    'top_solarsystem_secrets',
    'long',
    '1920x1080',
    '/static/audio/cinematic_jobelessboy_audio.mp3',
    '/static/thumbnails/cinematic_jobelessboy_solarsystem_thumb_169.jpg',
    '/static/videos/cinematic_jobelessboy_solarsystem_169.mp4',
    20.46,
    'cinematic_character_engine',
    'ready_for_upload',
    1,
    '{"speech_sync": true, "multi_camera": true, "host": "jobelessboy", "format": "16:9 Full HD"}'
))

c.execute('''
INSERT OR REPLACE INTO video_jobs (id, script_id, topic_id, video_type, resolution, audio_path, thumbnail_path, video_path, duration_sec, render_engine, status, quality_passed, quality_report_json, created_at)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
''', (
    'cinematic_jobelessboy_solarsystem_916',
    'scr_solarsystem_secrets',
    'top_solarsystem_secrets',
    'short',
    '1080x1920',
    '/static/audio/cinematic_jobelessboy_audio.mp3',
    '/static/thumbnails/cinematic_jobelessboy_solarsystem_thumb_169.jpg',
    '/static/videos/cinematic_jobelessboy_solarsystem_916.mp4',
    20.46,
    'cinematic_character_engine',
    'ready_for_upload',
    1,
    '{"speech_sync": true, "multi_camera": true, "host": "jobelessboy", "format": "9:16 Shorts"}'
))

conn.commit()
conn.close()
print('Registered topic, script, and video_jobs in database successfully!')
