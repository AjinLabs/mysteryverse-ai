import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.config import DB_PATH

logger = logging.getLogger("mysteryverse.database")

_initialized = False

def init_db():
    global _initialized
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # 1. Topics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS topics (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        mal_title TEXT NOT NULL,
        core_question TEXT,
        target_audience TEXT,
        category TEXT,
        format TEXT,
        potential_interest_score REAL,
        source_references TEXT,
        retrieved_at TEXT,
        fact_status TEXT,
        fact_confidence REAL,
        originality_score REAL,
        originality_explanation TEXT,
        status TEXT,
        created_at TEXT
    )
    """)
    
    # 2. Scripts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scripts (
        id TEXT PRIMARY KEY,
        topic_id TEXT,
        format TEXT,
        mal_hook TEXT,
        mal_content TEXT,
        mal_conclusion TEXT,
        full_script_mal TEXT,
        full_script_en_notes TEXT,
        scenes_json TEXT,
        estimated_duration_sec REAL,
        word_count INTEGER,
        model_used TEXT,
        status TEXT,
        created_at TEXT,
        FOREIGN KEY(topic_id) REFERENCES topics(id)
    )
    """)
    
    # 3. Character Assets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS character_assets (
        id TEXT PRIMARY KEY,
        character_name TEXT,
        expression TEXT,
        pose TEXT,
        asset_path TEXT,
        is_3d_render BOOLEAN,
        created_at TEXT
    )
    """)
    
    # 4. Video Jobs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS video_jobs (
        id TEXT PRIMARY KEY,
        script_id TEXT,
        topic_id TEXT,
        video_type TEXT,
        resolution TEXT,
        audio_path TEXT,
        subtitles_path TEXT,
        thumbnail_path TEXT,
        video_path TEXT,
        duration_sec REAL,
        render_engine TEXT,
        status TEXT,
        quality_passed BOOLEAN,
        quality_report_json TEXT,
        error_message TEXT,
        created_at TEXT,
        completed_at TEXT
    )
    """)
    
    # 5. Channel Uploads
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_uploads (
        id TEXT PRIMARY KEY,
        video_job_id TEXT,
        youtube_video_id TEXT,
        title TEXT,
        description TEXT,
        tags_json TEXT,
        category_id TEXT,
        privacy_status TEXT,
        scheduled_publish_time TEXT,
        upload_status TEXT,
        youtube_url TEXT,
        synthetic_disclosure BOOLEAN,
        idempotency_key TEXT UNIQUE,
        uploaded_at TEXT
    )
    """)
    
    # 6. Channel Analytics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_analytics (
        id TEXT PRIMARY KEY,
        recorded_at TEXT,
        subscriber_count INTEGER,
        eligible_subscribers INTEGER,
        total_views INTEGER,
        eligible_watch_hours REAL,
        eligible_shorts_views INTEGER,
        monetisation_status TEXT,
        raw_data_json TEXT
    )
    """)
    
    # 7. Channel Audit Records
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS channel_audit_records (
        id TEXT PRIMARY KEY,
        audited_at TEXT,
        is_authorized BOOLEAN,
        channel_id TEXT,
        channel_title TEXT,
        channel_handle TEXT,
        api_accessible_settings TEXT,
        manual_action_items TEXT
    )
    """)
    
    # 8. System Settings
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TEXT
    )
    """)
    
    # 9. System Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT,
        source TEXT,
        message TEXT,
        details_json TEXT,
        created_at TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    _initialized = True
    logger.info("Database initialized successfully at %s", DB_PATH)

def get_db_connection() -> sqlite3.Connection:
    global _initialized
    if not _initialized:
        init_db()
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def log_event(level: str, source: str, message: str, details: Optional[Dict[str, Any]] = None):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            "INSERT INTO system_logs (level, source, message, details_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (level, source, message, json.dumps(details or {}, ensure_ascii=False), now)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging to DB: {e}")

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM system_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "INSERT INTO system_settings (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
        (key, value, now)
    )
    conn.commit()
    conn.close()
