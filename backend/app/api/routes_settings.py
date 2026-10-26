import os
from fastapi import APIRouter
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings, DEFAULT_MALE_VOICE, DEFAULT_FEMALE_VOICE
from app.database import get_setting, set_setting

router = APIRouter(prefix="/settings", tags=["Settings"])

class SettingsUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    default_voice: Optional[str] = None
    auto_publish_enabled: Optional[bool] = None

@router.get("/")
def get_system_settings() -> Dict[str, Any]:
    return {
        "gemini_api_key_configured": bool(settings.GEMINI_API_KEY or get_setting("GEMINI_API_KEY")),
        "default_voice": get_setting("DEFAULT_VOICE", DEFAULT_MALE_VOICE),
        "available_voices": [
            {"id": "ml-IN-MidhunNeural", "name": "Midhun (Male - Energetic/Authoritative)", "language": "Malayalam"},
            {"id": "ml-IN-SobhanaNeural", "name": "Sobhana (Female - Articulate/Warm)", "language": "Malayalam"}
        ],
        "auto_publish_enabled": get_setting("AUTO_PUBLISH_ENABLED", "true") == "true",
        "min_originality_score": settings.MIN_ORIGINALITY_SCORE,
        "min_fact_check_confidence": settings.MIN_FACT_CHECK_CONFIDENCE
    }

@router.post("/")
def update_system_settings(req: SettingsUpdateRequest) -> Dict[str, Any]:
    if req.gemini_api_key is not None:
        set_setting("GEMINI_API_KEY", req.gemini_api_key)
        settings.GEMINI_API_KEY = req.gemini_api_key

    if req.default_voice is not None:
        set_setting("DEFAULT_VOICE", req.default_voice)

    if req.auto_publish_enabled is not None:
        set_setting("AUTO_PUBLISH_ENABLED", "true" if req.auto_publish_enabled else "false")

    return {"status": "updated", "settings": get_system_settings()}
