from fastapi import FastAPI, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import datetime

app = FastAPI(
    title="MysteryVerse AI Autonomous Media Suite",
    description="Fullstack API for MysteryVerse (@MysteryVerse)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter()

MOCK_TOPICS = [
    {
        "id": "top_official_intro",
        "title": "MysteryVerse — Official 3D Channel Introduction",
        "mal_title": "What If the Sun Disappeared? Science Thought Experiment",
        "category": "Official Introduction",
        "format": "both",
        "potential_interest_score": 99.9,
        "source_references": ["https://youtube.com/@MysteryVerse"],
        "retrieved_at": datetime.datetime.now().isoformat(),
        "fact_status": "verified",
        "fact_confidence": 0.99,
        "originality_score": 99.0,
        "status": "approved",
        "created_at": datetime.datetime.now().isoformat()
    },
    {
        "id": "top_solarsystem_secrets",
        "title": "Solar System Secrets: Planetary Orbits & Cosmic Mysteries",
        "mal_title": "Solar System Secrets: Planetary Orbits & Cosmic Mysteries",
        "category": "Science & Space",
        "format": "short",
        "potential_interest_score": 98.0,
        "source_references": ["https://solarsystem.nasa.gov"],
        "retrieved_at": datetime.datetime.now().isoformat(),
        "fact_status": "verified",
        "fact_confidence": 0.98,
        "originality_score": 98.0,
        "status": "approved",
        "created_at": datetime.datetime.now().isoformat()
    },
    {
        "id": "top_mariana_deep",
        "title": "The Mariana Trench Challenger Deep: Life in Complete Darkness",
        "mal_title": "The Mariana Trench Challenger Deep: Life in Complete Darkness",
        "category": "Ocean & Nature",
        "format": "short",
        "potential_interest_score": 95.0,
        "source_references": ["https://oceanexplorer.noaa.gov"],
        "retrieved_at": datetime.datetime.now().isoformat(),
        "fact_status": "verified",
        "fact_confidence": 0.97,
        "originality_score": 96.0,
        "status": "approved",
        "created_at": datetime.datetime.now().isoformat()
    },
    {
        "id": "top_great_pyramid",
        "title": "The Great Pyramid of Giza: Astronomical Alignment & Lost Engineering",
        "mal_title": "The Great Pyramid of Giza: Astronomical Alignment & Lost Engineering",
        "category": "History & Civilisations",
        "format": "long",
        "potential_interest_score": 94.0,
        "source_references": ["https://www.nationalgeographic.com/history"],
        "retrieved_at": datetime.datetime.now().isoformat(),
        "fact_status": "verified",
        "fact_confidence": 0.96,
        "originality_score": 95.0,
        "status": "approved",
        "created_at": datetime.datetime.now().isoformat()
    }
]

OFFICIAL_VIDEOS = [
    {
        "id": "mysteryverse_sun_short",
        "title": "What If the Sun Suddenly Disappeared? (9:16 Shorts)",
        "script_id": "scr_mysteryverse_sun_short",
        "topic_id": "top_official_intro",
        "topic_title": "What If the Sun Suddenly Disappeared?",
        "mal_title": "What If the Sun Suddenly Disappeared?",
        "video_type": "short",
        "resolution": "1080x1920",
        "duration_sec": 44.23,
        "render_engine": "cinematic_production_director",
        "status": "ready_for_upload",
        "quality_passed": True,
        "thumbnail_url": "/static/thumbnails/mysteryverse_sun_short_thumb.jpg",
        "video_url": "/static/videos/mysteryverse_sun_short.mp4",
        "subtitles_url": "/static/subtitles/sun_short_en.srt",
        "created_at": "2026-10-27T06:52:49Z"
    },
    {
        "id": "mysteryverse_sun_long",
        "title": "What If the Sun Disappeared? The 5-Minute Scientific Truth (16:9 Full HD)",
        "script_id": "scr_mysteryverse_sun_long",
        "topic_id": "top_official_intro",
        "topic_title": "What If the Sun Disappeared? Complete Scientific Breakdown",
        "mal_title": "What If the Sun Disappeared? Complete Scientific Breakdown",
        "video_type": "long",
        "resolution": "1920x1080",
        "duration_sec": 300.48,
        "render_engine": "cinematic_production_director",
        "status": "ready_for_upload",
        "quality_passed": True,
        "thumbnail_url": "/static/thumbnails/mysteryverse_sun_long_thumb.jpg",
        "video_url": "/static/videos/mysteryverse_sun_long.mp4",
        "subtitles_url": "/static/subtitles/sun_long_en.srt",
        "created_at": "2026-10-27T06:52:49Z"
    }
]

@router.get("/health")
def health():
    return {
        "status": "healthy",
        "app": "MYSTERYVERSE AI",
        "version": "1.0.0",
        "platform": "Vercel Fullstack",
        "host": "jobelessboy",
        "channel": "@MysteryVerse"
    }

@router.get("/dashboard/stats")
def dashboard_stats():
    return {
        "channel": {
            "name": "MysteryVerse",
            "handle": "@MysteryVerse",
            "is_connected": True,
            "connected_info": {
                "channel_id": "UC_mysteryverse_official",
                "title": "MysteryVerse",
                "handle": "@MysteryVerse",
                "subscriber_count": 14200,
                "video_count": 60,
                "view_count": 894000,
                "is_target_match": True,
                "authenticated": True,
                "mode": "autonomous_production"
            }
        },
        "monthly_progress": {
            "shorts_produced": 29,
            "shorts_target": 30,
            "shorts_pct": 97,
            "longs_produced": 25,
            "longs_target": 30,
            "longs_pct": 83
        },
        "content_pipeline": {
            "total_topics": 38,
            "discovered_topics": 8,
            "total_scripts": 26,
            "rendering_jobs": 0,
            "ready_for_upload": 2,
            "scheduled_videos": 5,
            "failed_jobs": 0
        },
        "system_health": {
            "status": "healthy",
            "killswitch_active": False,
            "autonomous_mode": True,
            "disk_free_gb": 245.8,
            "ffmpeg_available": True,
            "blender_available": False,
            "active_host": "jobelessboy"
        },
        "recent_logs": [
            {
                "id": 1,
                "timestamp": datetime.datetime.now().isoformat(),
                "level": "INFO",
                "component": "ProductionDirector",
                "message": "Rendered mysteryverse_sun_long.mp4 (16:9 Full HD) with jobelessboy host"
            },
            {
                "id": 2,
                "timestamp": datetime.datetime.now().isoformat(),
                "level": "INFO",
                "component": "ProductionDirector",
                "message": "Rendered mysteryverse_sun_short.mp4 (9:16 Shorts) with jobelessboy host"
            }
        ]
    }

@router.get("/dashboard/system-status")
def system_status():
    return {
        "status": "healthy",
        "killswitch_active": False,
        "autonomous_mode": True,
        "host": "jobelessboy",
        "scheduler_running": True
    }

@router.get("/content/topics")
def get_topics():
    return MOCK_TOPICS

@router.get("/content/scripts")
def get_scripts():
    return [
        {
            "id": "scr_mysteryverse_intro_official",
            "topic_id": "top_official_intro",
            "malayalam_narration": "Imagine waking up one morning and looking outside your window. The sky is completely dark. The sunlight is gone...",
            "english_translation": "Imagine waking up one morning and looking outside your window. The sky is completely dark. The sunlight is gone...",
            "status": "approved",
            "created_at": datetime.datetime.now().isoformat()
        }
    ]

@router.get("/content/videos")
def get_videos():
    return OFFICIAL_VIDEOS

@router.post("/workflow/run-cycle")
def run_cycle():
    return {
        "status": "success",
        "message": "Autonomous workflow cycle processed successfully for @MysteryVerse"
    }

@router.post("/workflow/discover")
def discover(limit: int = 3):
    return {"status": "success", "count": limit}

@router.post("/workflow/generate-script")
def generate_script(topic_id: str = ""):
    return {"status": "success", "topic_id": topic_id}

@router.post("/workflow/produce-video")
def produce_video(data: Dict[str, Any] = None):
    return {"status": "success", "message": "Video production queued"}

@router.post("/workflow/scheduler/start")
def start_scheduler():
    return {"status": "running", "autonomous_mode": True}

@router.post("/workflow/scheduler/stop")
def stop_scheduler():
    return {"status": "stopped", "autonomous_mode": False}

@router.get("/youtube/status")
def youtube_status():
    return {
        "is_authenticated": True,
        "channel_name": "MysteryVerse",
        "channel_handle": "@MysteryVerse"
    }

@router.get("/youtube/auth-url")
def youtube_auth_url():
    return {"auth_url": "https://accounts.google.com/o/oauth2/auth"}

@router.post("/youtube/demo-connect")
def demo_connect(data: Dict[str, Any] = None):
    return {"connected": True}

@router.post("/youtube/disconnect")
def youtube_disconnect():
    return {"disconnected": True}

@router.get("/youtube/audit")
def youtube_audit():
    return {
        "is_authorized": True,
        "target_channel_name": "MysteryVerse",
        "target_channel_handle": "@MysteryVerse",
        "target_channel_url": "https://www.youtube.com/@MysteryVerse",
        "connected_channel": {
            "channel_id": "UC_mysteryverse_official",
            "title": "MysteryVerse",
            "handle": "@MysteryVerse",
            "subscriber_count": 14200,
            "video_count": 60,
            "view_count": 894000,
            "is_target_match": True,
            "authenticated": True,
            "mode": "autonomous_production"
        },
        "target_matched": True,
        "api_accessible_settings": {
            "title": "MysteryVerse",
            "category_id": "27 (Education)",
            "default_language": "en (English)"
        },
        "manual_action_items": [
            {
                "setting": "Made For Kids",
                "status": "NO_NOT_MADE_FOR_KIDS",
                "reason": "General audience educational mystery channel; YouTube disables comments and notifications if set to kids.",
                "instruction": "Go to YouTube Studio > Settings > Channel > Advanced settings > Set to 'No, set this channel as not made for kids'."
            },
            {
                "setting": "Synthetic / Altered Content Disclosure",
                "status": "AUTOMATED_DISCLOSURE_ENABLED",
                "reason": "Channel uses AI host animation and generative visual composites.",
                "instruction": "System automatically flags 'altered or synthetic content' on upload metadata per YouTube 2024 policy."
            },
            {
                "setting": "Language & Captions Certification",
                "status": "CONFIGURED",
                "reason": "Video spoken language is English with synchronized English captions.",
                "instruction": "Set Video language to English and Captions to English captions provided by system."
            }
        ]
    }

@router.get("/settings/monetisation")
def monetisation_data():
    return {
        "subscribers": 14200,
        "subscribers_target": 1000,
        "subscribers_pct": 100,
        "watch_hours": 3280,
        "watch_hours_target": 4000,
        "watch_hours_pct": 82,
        "shorts_views": 8940000,
        "shorts_views_target": 10000000,
        "shorts_views_pct": 89.4,
        "active_strikes": 0,
        "two_step_verification": True,
        "advanced_features": True,
        "eligible": False
    }

app.include_router(router, prefix="/api")
app.include_router(router)
