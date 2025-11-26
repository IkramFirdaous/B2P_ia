"""Gmail API Service - OAuth2 and Email Fetching"""
import base64
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import secrets
from email.utils import parsedate_to_datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.email_credential import EmailCredential, EmailProvider


class GmailService:
    """Service for Gmail API integration with OAuth2"""
    
    # Gmail API scopes
    # Note: gmail.readonly includes all metadata capabilities, so we only need this one
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly'
    ]
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_authorization_url(self, employee_id: str) -> Tuple[str, str]:
        """
        Generate Gmail OAuth2 authorization URL
        
        Returns:
            Tuple of (authorization_url, state)
        """
        # Generate state for security
        state = secrets.token_urlsafe(32)
        
        # Create OAuth2 flow
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        
        # Generate authorization URL
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=f"{employee_id}:{state}",
            prompt='consent'
        )
        
        return authorization_url, state
    
    def handle_oauth_callback(self, code: str, state: str) -> EmailCredential:
        """
        Handle OAuth2 callback and store credentials
        
        Args:
            code: Authorization code from Google
            state: State parameter containing employee_id
            
        Returns:
            EmailCredential object
        """
        # Extract employee_id from state
        employee_id_str, _ = state.split(':', 1)
        
        # Exchange code for tokens
        import warnings
        from warnings import warn
        
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [settings.GMAIL_REDIRECT_URI]
                }
            },
            scopes=self.SCOPES,
            redirect_uri=settings.GMAIL_REDIRECT_URI
        )
        
        # Fetch token - Google OAuth library raises UserWarning for scope changes
        # We need to catch this and continue anyway
        credentials = None
        
        try:
            # Try normal token fetch
            flow.fetch_token(code=code)
            credentials = flow.credentials
            print(f"✅ Successfully fetched OAuth token")
            
        except UserWarning as w:
            # Scope mismatch warning - get credentials anyway
            warning_msg = str(w)
            print(f"⚠️  OAuth warning (continuing): {warning_msg}")
            
            # Credentials should still be available
            credentials = flow.credentials
            if not credentials or not credentials.token:
                raise ValueError(f"OAuth warning occurred but no credentials available: {warning_msg}")
                
            print(f"✅ Token fetched successfully despite scope warning")
            
        except Exception as e:
            error_msg = str(e)
            
            # Check if error message indicates it's just a scope warning
            if "Scope has changed" in error_msg or "Warning" in error_msg:
                print(f"⚠️  Scope change detected (attempting to continue): {error_msg}")
                
                # Try to get credentials even though there was an exception
                try:
                    credentials = flow.credentials
                    if credentials and credentials.token:
                        print(f"✅ Credentials obtained despite scope warning")
                    else:
                        raise ValueError("No valid credentials after scope warning")
                except AttributeError:
                    raise ValueError(f"Cannot obtain credentials after scope error: {error_msg}")
            else:
                print(f"❌ Token fetch failed: {error_msg}")
                raise
        
        if not credentials or not credentials.token:
            raise ValueError("Failed to obtain valid OAuth credentials")
        
        print(f"   Access token: {credentials.token[:20]}...")
        
        # Get email address
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        email_address = profile.get('emailAddress')
        
        # Store or update credentials
        try:
            credential = self.db.query(EmailCredential).filter(
                EmailCredential.employee_id == employee_id_str
            ).first()
            
            if credential:
                # Update existing
                print(f"Updating existing credential for employee: {employee_id_str}")
                credential.access_token = credentials.token
                credential.refresh_token = credentials.refresh_token or credential.refresh_token
                credential.token_expiry = credentials.expiry
                credential.email_address = email_address
            else:
                # Create new
                print(f"Creating new credential for employee: {employee_id_str}, email: {email_address}")
                credential = EmailCredential(
                    employee_id=employee_id_str,
                    email_provider=EmailProvider.GMAIL,
                    access_token=credentials.token,
                    refresh_token=credentials.refresh_token,
                    token_expiry=credentials.expiry,
                    email_address=email_address
                )
                self.db.add(credential)
            
            self.db.commit()
            self.db.refresh(credential)
            print(f"✅ Successfully saved Gmail credentials for {email_address}")
            
            return credential
        except Exception as e:
            self.db.rollback()
            print(f"❌ ERROR saving credentials: {type(e).__name__}: {str(e)}")
            raise
    
    def _get_credentials(self, employee_id: str) -> Optional[Credentials]:
        """Get stored credentials for employee"""
        credential = self.db.query(EmailCredential).filter(
            EmailCredential.employee_id == employee_id
        ).first()
        
        if not credential:
            return None
        
        creds = Credentials(
            token=credential.access_token,
            refresh_token=credential.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GMAIL_CLIENT_ID,
            client_secret=settings.GMAIL_CLIENT_SECRET,
            scopes=self.SCOPES
        )
        
        # Check if token needs refresh
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
            
            # Update stored credentials
            credential.access_token = creds.token
            credential.token_expiry = creds.expiry
            self.db.commit()
        
        return creds
    
    def fetch_emails(
        self,
        employee_id: str,
        max_results: int = 10,
        unread_only: bool = True
    ) -> List[Dict]:
        """
        Fetch emails from Gmail
        
        Args:
            employee_id: Employee ID
            max_results: Maximum number of emails to fetch
            unread_only: Only fetch unread emails
            
        Returns:
            List of email dictionaries with metadata and content
        """
        credentials = self._get_credentials(employee_id)
        if not credentials:
            raise ValueError("No Gmail credentials found for employee")
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            
            # Build query to EXCLUDE promotional/marketing emails
            # Gmail automatically categorizes emails, we exclude:
            # - category:promotions (newsletters, ads)
            # - category:social (social networks notifications)
            # - category:updates (automated updates)
            # We KEEP: category:primary (real people) and uncategorized
            query_parts = []
            
            if unread_only:
                query_parts.append('is:unread')
            
            # Exclude promotional categories
            query_parts.append('-category:promotions')
            query_parts.append('-category:social')
            query_parts.append('-category:updates')
            
            # Exclude common automated senders
            query_parts.append('-from:noreply')
            query_parts.append('-from:no-reply')
            query_parts.append('-from:donotreply')
            query_parts.append('-from:marketing')
            query_parts.append('-from:newsletter')
            query_parts.append('-from:notifications')
            
            query = ' '.join(query_parts)
            print(f"📧 Gmail query: {query}")
            
            # List messages
            results = service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            print(f"📨 Found {len(messages)} messages from Gmail API")
            
            emails = []
            filtered_count = 0
            
            for msg in messages:
                # Get full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract email data
                email_data = self._parse_email_message(message)
                
                # Filter out automated/promotional emails
                if email_data.get('is_automated', False):
                    filtered_count += 1
                    print(f"   🚫 Filtered automated email from: {email_data['sender'][:50]}")
                    continue
                
                print(f"   ✅ Real email from: {email_data['sender'][:50]}")
                emails.append(email_data)
            
            print(f"📊 Result: {len(emails)} real work emails, {filtered_count} automated/promotional filtered")
            return emails
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            raise
    
    def _is_automated_sender(self, sender: str) -> bool:
        """Check if sender is automated/promotional (not a real person)"""
        sender_lower = sender.lower()
        
        # Common automated sender patterns
        automated_patterns = [
            'noreply@', 'no-reply@', 'donotreply@', 'do-not-reply@',
            'marketing@', 'newsletter@', 'notifications@', 'notify@',
            'news@', 'info@', 'hello@', 'hi@', 'team@',
            'support@', 'help@', 'service@', 'automated@',
            'bot@', 'mailer@', 'alert@', 'system@'
        ]
        
        for pattern in automated_patterns:
            if pattern in sender_lower:
                return True
        
        # Check for promotional keywords
        promo_keywords = [
            'promotion', 'offer', 'sale', 'discount', 'deal',
            'subscribe', 'unsubscribe', 'newsletter', 'digest'
        ]
        
        for keyword in promo_keywords:
            if keyword in sender_lower:
                return True
        
        return False
    
    def _parse_email_message(self, message: Dict) -> Dict:
        """Parse Gmail API message into structured format"""
        headers = {h['name'].lower(): h['value'] 
                  for h in message['payload'].get('headers', [])}
        
        # Get email body
        body = self._get_email_body(message['payload'])
        
        # Parse date
        date_str = headers.get('date', '')
        try:
            received_at = parsedate_to_datetime(date_str)
        except:
            received_at = datetime.now()
        
        sender = headers.get('from', '')
        
        return {
            'email_id': message['id'],
            'thread_id': message.get('threadId'),
            'subject': headers.get('subject', '(No Subject)'),
            'sender': sender,
            'to': headers.get('to', ''),
            'received_at': received_at,
            'body': body,
            'snippet': message.get('snippet', ''),
            'labels': message.get('labelIds', []),
            'is_automated': self._is_automated_sender(sender)  # Flag automated emails
        }
    
    def _get_email_body(self, payload: Dict) -> str:
        """Extract email body from payload"""
        body = ""
        
        if 'parts' in payload:
            # Multi-part email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        else:
            # Single part email
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        
        return body
    
    def mark_as_read(self, employee_id: str, email_id: str):
        """Mark email as read"""
        credentials = self._get_credentials(employee_id)
        if not credentials:
            return
        
        try:
            service = build('gmail', 'v1', credentials=credentials)
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except HttpError as error:
            print(f'Error marking email as read: {error}')

