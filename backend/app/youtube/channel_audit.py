import json
from typing import Dict, Any, List
from app.youtube.oauth_manager import YouTubeOAuthManager
from app.config import TARGET_CHANNEL_NAME, TARGET_CHANNEL_HANDLE, TARGET_CHANNEL_URL

class ChannelAuditor:
    def __init__(self):
        self.oauth_mgr = YouTubeOAuthManager()

    def perform_audit(self) -> Dict[str, Any]:
        """
        Audits channel settings: separates API-accessible properties from
        protected YouTube Studio manual settings.
        """
        is_auth = self.oauth_mgr.is_authenticated()
        channel_info = self.oauth_mgr.verify_channel_identity() if is_auth else {}

        # 1. API-Accessible Settings
        api_accessible = {
            "channel_title": channel_info.get("title", TARGET_CHANNEL_NAME),
            "custom_handle": channel_info.get("custom_url", TARGET_CHANNEL_HANDLE),
            "default_language": "ml (Malayalam)",
            "default_category": "27 (Education)",
            "privacy_mode": "Scheduled Private Uploads",
            "api_status": "Connected & Authorized" if is_auth else "Awaiting OAuth Authorization"
        }

        # 2. Manual Action Items in YouTube Studio (Mandatory human owner tasks)
        manual_actions = [
            {
                "setting": "Google AdSense Account Association",
                "status": "Required for Monetisation",
                "reason": "Google policy strictly forbids third-party apps from entering or modifying banking/tax credentials.",
                "instruction": "Open YouTube Studio -> Earn Tab -> Associate or Create your approved Google AdSense account."
            },
            {
                "setting": "2-Step Verification on Owner Google Account",
                "status": "Mandatory Security Gate",
                "reason": "Required by YouTube to access advanced features and prevent channel hijacking.",
                "instruction": "Go to myaccount.google.com/security -> Turn on 2-Step Verification with Security Key or Authenticator app."
            },
            {
                "setting": "Advanced Features Verification (Phone / Video Verification)",
                "status": "Required for Daily Upload Quotas > 10 videos",
                "reason": "YouTube restricts new channels to low daily upload quotas until owner verifies phone number or channel history builds.",
                "instruction": "Open YouTube Studio -> Settings -> Channel -> Feature Eligibility -> Verify Phone Number."
            },
            {
                "setting": "Channel Trailer & Custom Banner",
                "status": "Recommended for Branding",
                "reason": "Upload high-res banner (2560x1440) featuring Dr. Kiran and Malayalam tagline.",
                "instruction": "Open YouTube Studio -> Customization -> Branding -> Upload Banner Image."
            }
        ]

        target_match = bool(channel_info.get("is_target_match", False))

        return {
            "is_authorized": is_auth,
            "target_channel_name": TARGET_CHANNEL_NAME,
            "target_channel_handle": TARGET_CHANNEL_HANDLE,
            "target_channel_url": TARGET_CHANNEL_URL,
            "connected_channel": channel_info,
            "target_matched": target_match,
            "api_accessible_settings": api_accessible,
            "manual_action_items": manual_actions
        }
