from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime

app = FastAPI(
    title="MysteryVerse AI Autonomous Media Suite",
    description="Fullstack API for MysteryVerse Malayalam (@MYSTERYVERSE-MALAYALAM)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MOCK_TOPICS = [
    {
        "id": "top_official_intro",
        "title": "MysteryVerse Malayalam — Official 3D Channel Introduction",
        "mal_title": "അറിവിന്റെ ലോകത്തേക്ക് സ്വാഗതം! | Official 3D Intro",
        "category": "Official Introduction",
        "format": "both",
        "potential_interest_score": 99.9,
        "source_references": ["https://youtube.com/@MYSTERYVERSE-MALAYALAM"],
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
        "mal_title": "സൗരയൂഥത്തിന്റെ അത്ഭുത രഹസ്യങ്ങൾ!",
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
        "mal_title": "സമുദ്രത്തിന്റെ അഗാധതയിൽ 11 കിലോമീറ്റർ താഴെ! മരിയാന ട്രെഞ്ചിലെ അജ്ഞാത ജീവികൾ",
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
        "mal_title": "ഗിസയിലെ പിരമിഡുകൾ നിർമ്മിച്ചതിന്റെ അവിശ്വസനീയ രഹസ്യം!",
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
        "id": "mysteryverse_intro_short",
        "title": "MysteryVerse Malayalam — Introduction Short (9:16 Vertical)",
        "script_id": "scr_mysteryverse_intro_short",
        "topic_id": "top_official_intro",
        "topic_title": "MysteryVerse Malayalam Channel Introduction Short",
        "mal_title": "അറിവിന്റെ ലോകത്തേക്ക് സ്വാഗതം! | Official Short",
        "video_type": "short",
        "resolution": "1080x1920",
        "duration_sec": 44.57,
        "render_engine": "cinematic_production_director",
        "status": "ready_for_upload",
        "quality_passed": True,
        "thumbnail_url": "/static/thumbnails/mysteryverse_intro_short_thumb.jpg",
        "video_url": "/static/videos/mysteryverse_intro_short.mp4",
        "subtitles_url": "/static/subtitles/intro_short_en.srt",
        "created_at": "2026-10-27T06:52:49Z"
    },
    {
        "id": "mysteryverse_intro_long",
        "title": "MysteryVerse Malayalam — Cinematic Channel Introduction (16:9 Full HD)",
        "script_id": "scr_mysteryverse_intro_long",
        "topic_id": "top_official_intro",
        "topic_title": "MysteryVerse Malayalam Full Channel Introduction",
        "mal_title": "അറിവിന്റെ ലോകത്തേക്ക് സ്വാഗതം! | 16:9 Cinematic Video",
        "video_type": "long",
        "resolution": "1920x1080",
        "duration_sec": 160.68,
        "render_engine": "cinematic_production_director",
        "status": "ready_for_upload",
        "quality_passed": True,
        "thumbnail_url": "/static/thumbnails/mysteryverse_intro_long_thumb.jpg",
        "video_url": "/static/videos/mysteryverse_intro_long.mp4",
        "subtitles_url": "/static/subtitles/intro_long_en.srt",
        "created_at": "2026-10-27T06:52:49Z"
    }
]

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "app": "MYSTERYVERSE AI",
        "version": "1.0.0",
        "platform": "Vercel Fullstack",
        "host": "jobelessboy",
        "channel": "@MYSTERYVERSE-MALAYALAM"
    }

@app.get("/api/dashboard/stats")
def dashboard_stats():
    return {
        "channel": {
            "name": "MYSTERY VERSE MALAYALAM",
            "handle": "@MYSTERYVERSE-MALAYALAM",
            "is_connected": True,
            "connected_info": {
                "channel_id": "UC_mysteryverse_official",
                "title": "MYSTERY VERSE MALAYALAM",
                "handle": "@MYSTERYVERSE-MALAYALAM",
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
                "message": "Rendered mysteryverse_intro_long.mp4 (16:9 Full HD) with jobelessboy host"
            },
            {
                "id": 2,
                "timestamp": datetime.datetime.now().isoformat(),
                "level": "INFO",
                "component": "ProductionDirector",
                "message": "Rendered mysteryverse_intro_short.mp4 (9:16 Shorts) with jobelessboy host"
            }
        ]
    }

@app.get("/api/dashboard/system-status")
def system_status():
    return {
        "status": "healthy",
        "killswitch_active": False,
        "autonomous_mode": True,
        "host": "jobelessboy",
        "scheduler_running": True
    }

@app.get("/api/content/topics")
def get_topics():
    return MOCK_TOPICS

@app.get("/api/content/scripts")
def get_scripts():
    return [
        {
            "id": "scr_mysteryverse_intro_official",
            "topic_id": "top_official_intro",
            "malayalam_narration": "നമസ്കാരം കൂട്ടുകാരേ! MysteryVerse Malayalam-ലേക്ക് എല്ലാവർക്കും സ്വാഗതം! ഈ ലോകം നിറയെ നമ്മളെ അത്ഭുതപ്പെടുത്തുന്ന കാര്യങ്ങളുണ്ട്...",
            "english_translation": "Hey friends! Welcome to MysteryVerse Malayalam! This world is full of things that amaze us...",
            "status": "approved",
            "created_at": datetime.datetime.now().isoformat()
        }
    ]

@app.get("/api/content/videos")
def get_videos():
    return OFFICIAL_VIDEOS

@app.post("/api/workflow/run-cycle")
def run_cycle():
    return {
        "status": "success",
        "message": "Autonomous workflow cycle processed successfully for @MYSTERYVERSE-MALAYALAM"
    }

@app.post("/api/workflow/discover")
def discover(limit: int = 3):
    return {"status": "success", "count": limit}

@app.post("/api/workflow/generate-script")
def generate_script(topic_id: str = ""):
    return {"status": "success", "topic_id": topic_id}

@app.post("/api/workflow/produce-video")
def produce_video(data: Dict[str, Any] = None):
    return {"status": "success", "message": "Video production queued"}

@app.post("/api/workflow/scheduler/start")
def start_scheduler():
    return {"status": "running", "autonomous_mode": True}

@app.post("/api/workflow/scheduler/stop")
def stop_scheduler():
    return {"status": "stopped", "autonomous_mode": False}

@app.get("/api/youtube/status")
def youtube_status():
    return {
        "is_authenticated": True,
        "channel_name": "MYSTERY VERSE MALAYALAM",
        "channel_handle": "@MYSTERYVERSE-MALAYALAM"
    }

@app.get("/api/youtube/auth-url")
def youtube_auth_url():
    return {"auth_url": "https://accounts.google.com/o/oauth2/auth"}

@app.post("/api/youtube/demo-connect")
def demo_connect(data: Dict[str, Any] = None):
    return {"connected": True}

@app.post("/api/youtube/disconnect")
def youtube_disconnect():
    return {"disconnected": True}

@app.get("/api/youtube/audit")
def youtube_audit():
    return {
        "is_authorized": True,
        "target_channel_name": "MYSTERY VERSE MALAYALAM",
        "target_channel_handle": "@MYSTERYVERSE-MALAYALAM",
        "target_channel_url": "https://www.youtube.com/@MYSTERYVERSE-MALAYALAM",
        "connected_channel": {
            "channel_id": "UC_mysteryverse_official",
            "title": "MYSTERY VERSE MALAYALAM",
            "handle": "@MYSTERYVERSE-MALAYALAM",
            "subscriber_count": 14200,
            "video_count": 60,
            "view_count": 894000,
            "is_target_match": True,
            "authenticated": True,
            "mode": "autonomous_production"
        },
        "target_matched": True,
        "api_accessible_settings": {
            "title": "MYSTERY VERSE MALAYALAM",
            "category_id": "27 (Education)",
            "default_language": "ml (Malayalam)"
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
                "reason": "Video spoken language is Malayalam, subtitles are in English.",
                "instruction": "Set Video language to Malayalam and Captions to 'None' or English captions provided by system."
            }
        ]
    }

@app.get("/api/settings/monetisation")
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
