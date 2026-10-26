import os
import json
import logging
import uuid
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, Any, List, Optional
from app.config import settings
from app.database import get_db_connection, log_event, get_setting, set_setting
from app.youtube.oauth_manager import YouTubeOAuthManager

logger = logging.getLogger("mysteryverse.uploader")

KOLKATA_TZ = ZoneInfo("Asia/Kolkata")

class YouTubeUploader:
    def __init__(self):
        self.oauth_mgr = YouTubeOAuthManager()

    def get_daily_quota_used(self) -> int:
        today_key = f"QUOTA_USED_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        val = get_setting(today_key, "0")
        return int(val)

    def record_quota_usage(self, units: int):
        today_key = f"QUOTA_USED_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"
        cur = self.get_daily_quota_used()
        set_setting(today_key, str(cur + units))

    def can_upload_today(self) -> bool:
        cur = self.get_daily_quota_used()
        return (cur + settings.YOUTUBE_UPLOAD_COST) <= settings.YOUTUBE_DAILY_QUOTA_LIMIT

    def calculate_next_publish_time(self, is_short: bool) -> datetime:
        """
        Calculates optimal publishing slot in Asia/Kolkata time.
        Shorts: 18:30 IST (Prime mobile browsing hour in Kerala)
        Long-form: 20:00 IST (Prime evening watch time in Kerala)
        """
        now_ist = datetime.now(KOLKATA_TZ)
        target_hour = 18 if is_short else 20
        target_minute = 30 if is_short else 0
        
        publish_dt = now_ist.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        # If today's slot has passed or is within 2 hours, schedule for tomorrow
        if publish_dt <= now_ist + timedelta(hours=2):
            publish_dt += timedelta(days=1)
        return publish_dt

    def schedule_video_upload(
        self,
        video_job_id: str,
        video_path: str,
        thumbnail_path: Optional[str],
        title: str,
        description: str,
        tags: List[str],
        is_short: bool = True,
        force_publish_at: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Uploads and schedules video using YouTube Data API v3 with resumable upload,
        Asia/Kolkata scheduling, and thumbnail linking.
        """
        # 1. Emergency Killswitch Check
        if os.path.exists(settings.EMERGENCY_KILLSWITCH_FILE) or get_setting("EMERGENCY_KILLSWITCH", "false") == "true":
            raise RuntimeError("Emergency Killswitch is ACTIVE! All upload and publishing operations are halted.")

        # 2. Daily Quota Check
        if not self.can_upload_today():
            raise RuntimeError(f"YouTube daily API quota limit reached ({self.get_daily_quota_used()}/{settings.YOUTUBE_DAILY_QUOTA_LIMIT}). Pausing until quota reset.")

        # 3. Idempotency Check
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, youtube_video_id, upload_status FROM channel_uploads WHERE video_job_id = ?", (video_job_id,))
        existing = cursor.fetchone()
        if existing:
            conn.close()
            logger.info("Video %s already uploaded / scheduled as %s", video_job_id, existing["youtube_video_id"])
            return {
                "upload_id": existing["id"],
                "youtube_video_id": existing["youtube_video_id"],
                "status": existing["upload_status"],
                "already_existed": True
            }

        # 4. Scheduling time
        if force_publish_at:
            publish_time_iso = force_publish_at
        else:
            publish_dt = self.calculate_next_publish_time(is_short)
            publish_time_iso = publish_dt.isoformat()

        upload_id = f"upl_{uuid.uuid4().hex[:10]}"
        idempotency_key = f"idemp_{video_job_id}"

        # 5. Check if real API or Demo/Staging Mode
        service = self.oauth_mgr.get_authenticated_service()

        if not service:
            # Safe Demo Mode or Staging
            logger.info("Executing simulated scheduled upload (Demo/Staging mode)")
            mock_video_id = f"demo_yt_{uuid.uuid4().hex[:11]}"
            youtube_url = f"https://youtu.be/{mock_video_id}"
            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
            INSERT INTO channel_uploads (
                id, video_job_id, youtube_video_id, title, description,
                tags_json, category_id, privacy_status, scheduled_publish_time,
                upload_status, youtube_url, synthetic_disclosure, idempotency_key, uploaded_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                upload_id, video_job_id, mock_video_id, title, description,
                json.dumps(tags), "27", "private", publish_time_iso,
                "scheduled", youtube_url, True, idempotency_key, now
            ))
            cursor.execute("UPDATE video_jobs SET status = 'scheduled' WHERE id = ?", (video_job_id,))
            conn.commit()
            conn.close()

            self.record_quota_usage(settings.YOUTUBE_UPLOAD_COST)
            log_event("INFO", "YouTubeUploader", f"Video {mock_video_id} scheduled in demo mode", {"publishAt": publish_time_iso})
            return {
                "upload_id": upload_id,
                "youtube_video_id": mock_video_id,
                "youtube_url": youtube_url,
                "scheduled_publish_time": publish_time_iso,
                "status": "scheduled",
                "mode": "demo"
            }

        # Real YouTube Data API v3 Upload
        from googleapiclient.http import MediaFileUpload
        body = {
            "snippet": {
                "title": title[:100],
                "description": description[:5000],
                "tags": tags[:20],
                "categoryId": "27",  # Education
                "defaultLanguage": "ml",
                "defaultAudioLanguage": "ml"
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_time_iso,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=1024*1024*4, resumable=True, mimetype="video/mp4")
        request = service.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                logger.info("Uploaded %d%% of video...", int(status.progress() * 100))

        real_video_id = response.get("id")
        youtube_url = f"https://youtu.be/{real_video_id}"

        # Upload Custom Thumbnail if available
        if thumbnail_path and os.path.exists(thumbnail_path):
            try:
                thumb_media = MediaFileUpload(thumbnail_path, mimetype="image/jpeg")
                service.thumbnails().set(videoId=real_video_id, media_body=thumb_media).execute()
                self.record_quota_usage(50)
            except Exception as te:
                logger.warning("Could not set custom thumbnail via API: %s", te)

        self.record_quota_usage(settings.YOUTUBE_UPLOAD_COST)
        now = datetime.now(timezone.utc).isoformat()

        cursor.execute("""
        INSERT INTO channel_uploads (
            id, video_job_id, youtube_video_id, title, description,
            tags_json, category_id, privacy_status, scheduled_publish_time,
            upload_status, youtube_url, synthetic_disclosure, idempotency_key, uploaded_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            upload_id, video_job_id, real_video_id, title, description,
            json.dumps(tags), "27", "private", publish_time_iso,
            "scheduled", youtube_url, True, idempotency_key, now
        ))
        cursor.execute("UPDATE video_jobs SET status = 'scheduled' WHERE id = ?", (video_job_id,))
        conn.commit()
        conn.close()

        log_event("INFO", "YouTubeUploader", f"Video {real_video_id} uploaded and scheduled successfully", {"url": youtube_url})
        return {
            "upload_id": upload_id,
            "youtube_video_id": real_video_id,
            "youtube_url": youtube_url,
            "scheduled_publish_time": publish_time_iso,
            "status": "scheduled",
            "mode": "production"
        }
