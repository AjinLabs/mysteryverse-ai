from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TopicModel(BaseModel):
    id: str
    title: str
    mal_title: str
    core_question: Optional[str] = None
    target_audience: Optional[str] = "Malayalam learners, science enthusiasts, mystery seekers"
    category: str
    format: str = "short"  # "short" or "long"
    potential_interest_score: float = 90.0
    source_references: List[str] = []
    retrieved_at: str
    fact_status: str = "verified"
    fact_confidence: float = 95.0
    originality_score: float = 92.0
    originality_explanation: Optional[str] = None
    status: str = "discovered"
    created_at: str

class SceneCue(BaseModel):
    scene_number: int
    duration_sec: float
    visual_description: str
    camera_movement: str  # e.g., "zoom_in", "pan_right", "slow_orbit", "static_wide"
    character_expression: str  # "curiosity", "surprise", "explanation", "excitement", "caution", "humour"
    character_pose: str  # "pointing_right", "holding_tablet", "pensive", "greeting"
    background_theme: str  # "space", "lab", "ancient_ruins", "ocean", "abstract"
    speech_segment_mal: str

class ScriptModel(BaseModel):
    id: str
    topic_id: str
    format: str
    mal_hook: str
    mal_content: str
    mal_conclusion: str
    full_script_mal: str
    full_script_en_notes: Optional[str] = None
    scenes: List[SceneCue] = []
    estimated_duration_sec: float
    word_count: int
    model_used: str = "Gemini-Free / Neural-Malayalam"
    status: str = "draft"
    created_at: str

class VideoJobModel(BaseModel):
    id: str
    script_id: str
    topic_id: str
    video_type: str
    resolution: str
    audio_path: Optional[str] = None
    subtitles_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    video_path: Optional[str] = None
    duration_sec: Optional[float] = None
    render_engine: str = "procedural_motion"
    status: str = "pending"
    quality_passed: bool = False
    quality_report: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class ChannelUploadModel(BaseModel):
    id: str
    video_job_id: str
    youtube_video_id: Optional[str] = None
    title: str
    description: str
    tags: List[str] = []
    category_id: str = "27"  # Education
    privacy_status: str = "private"  # 'private', 'unlisted', 'public'
    scheduled_publish_time: Optional[str] = None
    upload_status: str = "scheduled"
    youtube_url: Optional[str] = None
    synthetic_disclosure: bool = True
    idempotency_key: str
    uploaded_at: str

class QualityGateReport(BaseModel):
    passed: bool
    originality_score: float
    fact_confidence: float
    audio_video_sync_ms: float
    subtitles_valid: bool
    video_file_valid: bool
    thumbnail_valid: bool
    platform_disclosure_set: bool
    details: Dict[str, Any]

class ChannelAuditResult(BaseModel):
    is_authorized: bool
    channel_id: Optional[str] = None
    channel_title: Optional[str] = None
    channel_handle: Optional[str] = None
    api_accessible_settings: Dict[str, Any]
    manual_action_items: List[Dict[str, str]]
    match_target: bool

class MonetisationMetrics(BaseModel):
    subscriber_count: int
    subscribers_required: int = 1000
    subscribers_progress_pct: float
    watch_hours: float
    watch_hours_required: float = 4000.0
    watch_hours_progress_pct: float
    shorts_views_90d: int
    shorts_views_required: int = 10000000
    shorts_views_progress_pct: float
    is_eligible_standard: bool
    is_eligible_shorts: bool
    monetisation_status: str
    explanation_notes: List[str]

class SystemHealthResponse(BaseModel):
    app_name: str
    version: str
    status: str
    killswitch_active: bool
    autonomous_scheduler_active: bool
    demo_mode: bool
    ffmpeg_detected: bool
    ffmpeg_path: Optional[str] = None
    blender_detected: bool
    blender_path: Optional[str] = None
    edge_tts_available: bool
    database_connected: bool
    youtube_connected: bool
    channel_name: Optional[str] = None
    monthly_shorts_produced: int
    monthly_shorts_target: int
    monthly_longs_produced: int
    monthly_longs_target: int
    disk_free_gb: float
    daily_quota_used: int
    daily_quota_limit: int
