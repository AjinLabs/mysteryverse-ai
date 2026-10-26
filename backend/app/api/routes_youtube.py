from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from pydantic import BaseModel
from app.youtube.oauth_manager import YouTubeOAuthManager
from app.youtube.channel_audit import ChannelAuditor
from app.youtube.analytics import AnalyticsManager
from app.database import set_setting

router = APIRouter(prefix="/youtube", tags=["YouTube Integration"])

class ConnectDemoRequest(BaseModel):
    enabled: bool

@router.get("/status")
def get_channel_status() -> Dict[str, Any]:
    mgr = YouTubeOAuthManager()
    is_auth = mgr.is_authenticated()
    info = mgr.verify_channel_identity() if is_auth else {}
    return {
        "authenticated": is_auth,
        "channel_info": info,
        "has_client_secrets": mgr.has_client_secrets()
    }

@router.get("/auth-url")
def get_auth_url(redirect_uri: str = "http://localhost:8000/api/youtube/oauth2callback") -> Dict[str, str]:
    mgr = YouTubeOAuthManager()
    url = mgr.get_auth_url(redirect_uri=redirect_uri)
    return {"auth_url": url}

@router.get("/oauth2callback")
def oauth_callback(code: str, redirect_uri: str = "http://localhost:8000/api/youtube/oauth2callback") -> Dict[str, Any]:
    mgr = YouTubeOAuthManager()
    info = mgr.handle_auth_code(code=code, redirect_uri=redirect_uri)
    return {"status": "success", "channel": info}

@router.post("/disconnect")
def disconnect_channel() -> Dict[str, Any]:
    mgr = YouTubeOAuthManager()
    mgr.disconnect()
    return {"status": "disconnected"}

@router.post("/demo-connect")
def toggle_demo_connection(req: ConnectDemoRequest) -> Dict[str, Any]:
    """Enables simulated channel connection for demo testing without real Google Cloud credentials."""
    set_setting("YOUTUBE_DEMO_CONNECTED", "true" if req.enabled else "false")
    mgr = YouTubeOAuthManager()
    info = mgr.verify_channel_identity()
    return {"status": "success", "demo_mode": req.enabled, "channel": info}

@router.get("/audit")
def audit_channel() -> Dict[str, Any]:
    auditor = ChannelAuditor()
    return auditor.perform_audit()

@router.get("/monetisation")
def get_monetisation() -> Dict[str, Any]:
    analytics = AnalyticsManager()
    return analytics.get_monetisation_metrics()
