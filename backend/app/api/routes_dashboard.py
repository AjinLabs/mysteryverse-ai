import os
import shutil
from fastapi import APIRouter
from typing import Dict, Any
from app.config import (
    settings, TARGET_CHANNEL_NAME, TARGET_CHANNEL_HANDLE,
    TARGET_SHORTS_PER_MONTH, TARGET_LONGS_PER_MONTH,
    get_ffmpeg_path, get_blender_path
)
from app.database import get_db_connection, get_setting
from app.youtube.oauth_manager import YouTubeOAuthManager
from app.youtube.uploader import YouTubeUploader
from app.youtube.analytics import AnalyticsManager
from app.youtube.channel_audit import ChannelAuditor
from app.character.bible import CHARACTER_BIBLE

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
def get_dashboard_stats() -> Dict[str, Any]:
    conn = get_db_connection()
    cursor = conn.cursor()

    # Topic counts
    cursor.execute("SELECT COUNT(*) as cnt FROM topics")
    total_topics = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM topics WHERE status = 'discovered'")
    discovered_topics = cursor.fetchone()["cnt"]

    # Script counts
    cursor.execute("SELECT COUNT(*) as cnt FROM scripts")
    total_scripts = cursor.fetchone()["cnt"]

    # Video Job counts
    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE status = 'rendering'")
    rendering_jobs = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE status = 'ready_for_upload'")
    ready_for_upload = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE status = 'scheduled'")
    scheduled_videos = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE status = 'failed'")
    failed_jobs = cursor.fetchone()["cnt"]

    # Monthly production count towards 30 Shorts & 30 Longs
    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE video_type = 'short' AND status IN ('ready_for_upload', 'scheduled', 'uploaded')")
    shorts_produced = cursor.fetchone()["cnt"]

    cursor.execute("SELECT COUNT(*) as cnt FROM video_jobs WHERE video_type = 'long' AND status IN ('ready_for_upload', 'scheduled', 'uploaded')")
    longs_produced = cursor.fetchone()["cnt"]

    # Recent activity logs
    cursor.execute("SELECT * FROM system_logs ORDER BY id DESC LIMIT 15")
    recent_logs = [dict(r) for r in cursor.fetchall()]

    conn.close()

    # System Health & Disk space
    disk_usage = shutil.disk_usage(os.path.abspath("."))
    disk_free_gb = round(disk_usage.free / (1024 ** 3), 1)

    uploader = YouTubeUploader()
    oauth_mgr = YouTubeOAuthManager()
    is_authenticated = oauth_mgr.is_authenticated()
    channel_info = oauth_mgr.verify_channel_identity() if is_authenticated else {}

    killswitch_active = (
        os.path.exists(settings.EMERGENCY_KILLSWITCH_FILE) or
        get_setting("EMERGENCY_KILLSWITCH", "false") == "true"
    )

    scheduler_active = get_setting("AUTONOMOUS_SCHEDULER_ACTIVE", "false") == "true"
    auto_publish_enabled = get_setting("AUTO_PUBLISH_ENABLED", "true") == "true"

    return {
        "channel": {
            "name": TARGET_CHANNEL_NAME,
            "handle": TARGET_CHANNEL_HANDLE,
            "is_connected": is_authenticated,
            "connected_info": channel_info
        },
        "monthly_progress": {
            "shorts_produced": shorts_produced,
            "shorts_target": TARGET_SHORTS_PER_MONTH,
            "shorts_pct": min(100.0, round((shorts_produced / TARGET_SHORTS_PER_MONTH) * 100.0, 1)),
            "longs_produced": longs_produced,
            "longs_target": TARGET_LONGS_PER_MONTH,
            "longs_pct": min(100.0, round((longs_produced / TARGET_LONGS_PER_MONTH) * 100.0, 1)),
            "total_produced": shorts_produced + longs_produced,
            "total_target": TARGET_SHORTS_PER_MONTH + TARGET_LONGS_PER_MONTH
        },
        "pipeline_counts": {
            "total_topics": total_topics,
            "discovered_topics": discovered_topics,
            "total_scripts": total_scripts,
            "rendering_jobs": rendering_jobs,
            "ready_for_upload": ready_for_upload,
            "scheduled_videos": scheduled_videos,
            "failed_jobs": failed_jobs
        },
        "system_status": {
            "killswitch_active": killswitch_active,
            "autonomous_scheduler_active": scheduler_active,
            "auto_publish_enabled": auto_publish_enabled,
            "ffmpeg_detected": get_ffmpeg_path() is not None,
            "ffmpeg_path": get_ffmpeg_path(),
            "blender_detected": get_blender_path() is not None,
            "blender_path": get_blender_path(),
            "disk_free_gb": disk_free_gb,
            "daily_quota_used": uploader.get_daily_quota_used(),
            "daily_quota_limit": settings.YOUTUBE_DAILY_QUOTA_LIMIT
        },
        "character": CHARACTER_BIBLE["identity"],
        "recent_logs": recent_logs
    }
