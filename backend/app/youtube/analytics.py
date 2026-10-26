from datetime import datetime, timezone
from typing import Dict, Any, List
from app.youtube.oauth_manager import YouTubeOAuthManager
from app.database import get_db_connection

class AnalyticsManager:
    def __init__(self):
        self.oauth_mgr = YouTubeOAuthManager()

    def get_monetisation_metrics(self) -> Dict[str, Any]:
        """
        Retrieves live or estimated channel telemetry and computes
        progress towards YouTube Partner Program (YPP) monetisation thresholds.
        """
        channel_info = self.oauth_mgr.verify_channel_identity() if self.oauth_mgr.is_authenticated() else {}
        
        subs = channel_info.get("subscriber_count", 0)
        views = channel_info.get("view_count", 0)
        videos_count = channel_info.get("video_count", 0)

        # Get local database upload records to supplement
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM channel_uploads WHERE upload_status = 'scheduled' OR upload_status = 'published'")
        local_published_count = cursor.fetchone()["cnt"]
        conn.close()

        # Estimated Public Watch Hours (based on average retention)
        # Note: True eligible watch hours come from YouTube Studio Analytics API when approved
        estimated_watch_hours = round((views * 2.2) / 60.0, 1) if views > 0 else 0.0
        estimated_shorts_views = int(views * 0.7) if views > 0 else 0

        subs_required = 1000
        watch_hours_required = 4000.0
        shorts_views_required = 10000000

        subs_progress = min(100.0, round((subs / subs_required) * 100.0, 1))
        hours_progress = min(100.0, round((estimated_watch_hours / watch_hours_required) * 100.0, 1))
        shorts_progress = min(100.0, round((estimated_shorts_views / shorts_views_required) * 100.0, 2))

        is_eligible_standard = subs >= subs_required and estimated_watch_hours >= watch_hours_required
        is_eligible_shorts = subs >= subs_required and estimated_shorts_views >= shorts_views_required

        status = "ELIGIBLE_FOR_REVIEW" if (is_eligible_standard or is_eligible_shorts) else "BUILDING_AUDIENCE"

        return {
            "subscriber_count": subs,
            "subscribers_required": subs_required,
            "subscribers_progress_pct": subs_progress,
            "watch_hours": estimated_watch_hours,
            "watch_hours_required": watch_hours_required,
            "watch_hours_progress_pct": hours_progress,
            "shorts_views_90d": estimated_shorts_views,
            "shorts_views_required": shorts_views_required,
            "shorts_views_progress_pct": shorts_progress,
            "is_eligible_standard": is_eligible_standard,
            "is_eligible_shorts": is_eligible_shorts,
            "monetisation_status": status,
            "published_videos_count": max(videos_count, local_published_count),
            "educational_notes": [
                "Only valid public watch hours from long-form videos count toward the 4,000-hour requirement.",
                "Shorts views do NOT count toward the 4,000 watch hours, but count toward the 10M Shorts views threshold.",
                "Private, unlisted, or deleted video watch time is strictly excluded by YouTube algorithms.",
                "Estimated YouTube analytics in Studio differ from finalized AdSense earnings, which are paid out monthly after reaching the $100/₹8000 payout threshold."
            ]
        }
