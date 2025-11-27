"""Gmail OAuth Service for Authentication and Email Access"""
from typing import Tuple, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.core.config import settings


class GmailService:
    """Service for Gmail OAuth authentication and API access"""

    # OAuth scopes required for Gmail access
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]

    # OAuth credentials (loaded from settings which reads .env file)
    # Try both GMAIL_* and GOOGLE_* settings for compatibility
    CLIENT_ID = settings.GMAIL_CLIENT_ID or settings.GOOGLE_CLIENT_ID
    CLIENT_SECRET = settings.GMAIL_CLIENT_SECRET or settings.GOOGLE_CLIENT_SECRET

    def __init__(self, db: Session):
        self.db = db

        # Get redirect URI from settings or use default
        cors_origins = settings.BACKEND_CORS_ORIGINS
        backend_url = "http://localhost:8000"  # Default
        if cors_origins:
            # Use the first CORS origin as backend URL
            backend_url = "http://localhost:8000"  # Backend is always localhost:8000

        self.redirect_uri = f"{backend_url}{settings.API_V1_PREFIX}/auth/callback"

    def get_authorization_url(self, state: str) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL

        Args:
            state: State parameter for OAuth flow (employee_id or session identifier)

        Returns:
            Tuple of (auth_url, state)
        """
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError(
                "Google OAuth credentials not configured. "
                "Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables."
            )

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        authorization_url, returned_state = flow.authorization_url(
            access_type='offline',  # Request refresh token
            include_granted_scopes='true',
            state=state,
            prompt='consent'  # Force consent screen to get refresh token
        )

        return authorization_url, returned_state

    def exchange_code_for_token(self, code: str) -> Credentials:
        """
        Exchange authorization code for access token

        Args:
            code: Authorization code from OAuth callback

        Returns:
            Google OAuth credentials object
        """
        if not self.CLIENT_ID or not self.CLIENT_SECRET:
            raise ValueError("Google OAuth credentials not configured")

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.CLIENT_ID,
                    "client_secret": self.CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )

        flow.fetch_token(code=code)
        credentials = flow.credentials

        return credentials

    def get_user_info(self, credentials: Credentials) -> Dict:
        """
        Get user information from Gmail/Google API

        Args:
            credentials: OAuth credentials

        Returns:
            Dict with user info (email, name, picture, etc.)
        """
        # Build Gmail service
        gmail_service = build('gmail', 'v1', credentials=credentials)

        # Get user profile
        profile = gmail_service.users().getProfile(userId='me').execute()

        # Get additional info from People API if available
        try:
            people_service = build('people', 'v1', credentials=credentials)
            person = people_service.people().get(
                resourceName='people/me',
                personFields='names,emailAddresses,photos'
            ).execute()

            # Extract name and photo
            names = person.get('names', [])
            photos = person.get('photos', [])

            name = names[0].get('displayName') if names else None
            picture = photos[0].get('url') if photos else None
        except Exception:
            # If People API fails, use email prefix as name
            name = profile.get('emailAddress', '').split('@')[0]
            picture = None

        return {
            'emailAddress': profile.get('emailAddress'),
            'name': name,
            'picture': picture,
            'messagesTotal': profile.get('messagesTotal', 0),
            'threadsTotal': profile.get('threadsTotal', 0)
        }

    def refresh_access_token(self, refresh_token: str) -> Credentials:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token from OAuth flow

        Returns:
            New credentials with refreshed access token
        """
        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET
        )

        # This will automatically refresh the token
        from google.auth.transport.requests import Request
        credentials.refresh(Request())

        return credentials
