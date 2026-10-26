import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings, TARGET_CHANNEL_NAME, TARGET_CHANNEL_HANDLE
from app.database import log_event, set_setting, get_setting

logger = logging.getLogger("mysteryverse.oauth")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

class YouTubeOAuthManager:
    def __init__(self):
        self.secrets_file = settings.OAUTH_CLIENT_SECRETS_FILE
        self.token_file = settings.OAUTH_TOKEN_FILE

    def has_client_secrets(self) -> bool:
        return os.path.exists(self.secrets_file)

    def is_authenticated(self) -> bool:
        if get_setting("YOUTUBE_DEMO_CONNECTED", "false") == "true":
            return True
        if not os.path.exists(self.token_file):
            return False
        try:
            with open(self.token_file, "r") as f:
                data = json.load(f)
                return bool(data.get("refresh_token") or data.get("token"))
        except Exception:
            return False

    def get_auth_url(self, redirect_uri: str = "http://localhost:8000/api/youtube/oauth2callback") -> str:
        """
        Builds the official Google OAuth 2.0 authorization URL.
        """
        if not self.has_client_secrets():
            # Return instructions if credentials have not been supplied yet
            return f"/settings?error=missing_secrets"

        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_secrets_file(
            self.secrets_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        return auth_url

    def handle_auth_code(self, code: str, redirect_uri: str = "http://localhost:8000/api/youtube/oauth2callback") -> Dict[str, Any]:
        """
        Exchanges authorization code for credentials and securely persists tokens.
        """
        from google_auth_oauthlib.flow import Flow
        flow = Flow.from_client_secrets_file(
            self.secrets_file,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        flow.fetch_token(code=code)
        creds = flow.credentials

        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }

        with open(self.token_file, "w") as f:
            json.dump(token_data, f, indent=2)

        # Verify connected channel
        channel_info = self.verify_channel_identity()
        log_event("INFO", "OAuthManager", "YouTube channel authenticated successfully", channel_info)
        return channel_info

    def get_authenticated_service(self):
        """Builds authorized YouTube Data API v3 client."""
        if not os.path.exists(self.token_file):
            return None

        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build

        with open(self.token_file, "r") as f:
            token_data = json.load(f)

        creds = Credentials(
            token=token_data.get("token"),
            refresh_token=token_data.get("refresh_token"),
            token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
            client_id=token_data.get("client_id"),
            client_secret=token_data.get("client_secret"),
            scopes=token_data.get("scopes", SCOPES)
        )

        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Save refreshed token
            token_data["token"] = creds.token
            with open(self.token_file, "w") as f:
                json.dump(token_data, f, indent=2)

        return build("youtube", "v3", credentials=creds)

    def verify_channel_identity(self) -> Dict[str, Any]:
        """
        Fetches the authorized channel profile and checks if it matches
        'MYSTERY VERSE MALAYALAM' (@MYSTERYVERSE-MALAYALAM).
        """
        if get_setting("YOUTUBE_DEMO_CONNECTED", "false") == "true":
            return {
                "channel_id": "UC_DEMO_MYSTERYVERSE_ML",
                "title": TARGET_CHANNEL_NAME,
                "handle": TARGET_CHANNEL_HANDLE,
                "custom_url": TARGET_CHANNEL_HANDLE,
                "is_target_match": True,
                "mode": "demo_verified"
            }

        service = self.get_authenticated_service()
        if not service:
            return {"authenticated": False, "error": "Not authenticated"}

        response = service.channels().list(part="snippet,contentDetails,statistics", mine=True).execute()
        items = response.get("items", [])
        if not items:
            return {"authenticated": False, "error": "No YouTube channel associated with this account"}

        ch = items[0]
        title = ch["snippet"]["title"]
        custom_url = ch["snippet"].get("customUrl", "")
        ch_id = ch["id"]

        is_match = (title.lower() == TARGET_CHANNEL_NAME.lower()) or (TARGET_CHANNEL_HANDLE.lower() in custom_url.lower())

        info = {
            "channel_id": ch_id,
            "title": title,
            "custom_url": custom_url,
            "subscriber_count": int(ch["statistics"].get("subscriberCount", 0)),
            "video_count": int(ch["statistics"].get("videoCount", 0)),
            "view_count": int(ch["statistics"].get("viewCount", 0)),
            "is_target_match": is_match,
            "authenticated": True
        }
        set_setting("CONNECTED_CHANNEL_INFO", json.dumps(info))
        return info

    def disconnect(self):
        """Revokes token and disconnects channel."""
        if os.path.exists(self.token_file):
            try:
                os.remove(self.token_file)
            except Exception:
                pass
        set_setting("YOUTUBE_DEMO_CONNECTED", "false")
        set_setting("CONNECTED_CHANNEL_INFO", "")
        log_event("WARNING", "OAuthManager", "YouTube channel disconnected by owner")
