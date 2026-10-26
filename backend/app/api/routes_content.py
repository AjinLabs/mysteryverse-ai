import os
import json
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from app.database import get_db_connection

router = APIRouter(prefix="/content", tags=["Content"])

@router.get("/topics")
def list_topics(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM topics ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["source_references"] = json.loads(d.get("source_references") or "[]")
        result.append(d)
    return result

@router.get("/scripts")
def list_scripts(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT s.*, t.title as topic_title, t.mal_title, t.category
    FROM scripts s
    LEFT JOIN topics t ON s.topic_id = t.id
    ORDER BY s.created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["scenes"] = json.loads(d.get("scenes_json") or "[]")
        result.append(d)
    return result

@router.get("/videos")
def list_videos(limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT v.*, s.full_script_mal, t.title as topic_title, t.mal_title,
           u.youtube_video_id, u.youtube_url, u.scheduled_publish_time, u.upload_status
    FROM video_jobs v
    LEFT JOIN scripts s ON v.script_id = s.id
    LEFT JOIN topics t ON v.topic_id = t.id
    LEFT JOIN channel_uploads u ON v.id = u.video_job_id
    ORDER BY v.created_at DESC LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    result = []
    for r in rows:
        d = dict(r)
        d["quality_report"] = json.loads(d.get("quality_report_json") or "{}")
        # Relative static web path for frontend player
        if d.get("video_path"):
            v_name = os.path.basename(d["video_path"])
            d["video_url"] = f"/static/videos/{v_name}"
        if d.get("thumbnail_path"):
            t_name = os.path.basename(d["thumbnail_path"])
            d["thumbnail_url"] = f"/static/thumbnails/{t_name}"
        if d.get("subtitles_path"):
            s_name = os.path.basename(d["subtitles_path"])
            d["subtitles_url"] = f"/static/subtitles/{s_name}"
        result.append(d)
    return result
