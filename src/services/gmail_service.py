"""Gmail API service wrapper."""

import os
import pickle
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from src.utils.logger import logger


class GmailService:
    """Wrapper for Gmail API operations."""

    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.compose',
        'https://www.googleapis.com/auth/gmail.modify',
    ]

    def __init__(self, credentials_path: str, token_path: str):
        """
        Initialize Gmail service.

        Args:
            credentials_path: Path to credentials.json
            token_path: Path to token.json (will be created on first run)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate and create Gmail service."""
        creds = None

        # Check for existing token
        if os.path.exists(self.token_path):
            try:
                with open(self.token_path, 'rb') as token:
                    creds = pickle.load(token)
                logger.debug("Loaded existing token")
            except Exception as e:
                logger.warning(f"Failed to load token: {e}")

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download credentials.json from Google Cloud Console"
                    )

                logger.info("Starting OAuth2 authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)

            # Save the credentials for next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
            logger.info("Token saved successfully")

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail service authenticated successfully")

    def search_emails(self, query: str, max_results: Optional[int] = None) -> List[Dict]:
        """
        Search emails using Gmail query syntax.

        Args:
            query: Gmail search query
            max_results: Maximum number of results to return

        Returns:
            List of message dictionaries
        """
        try:
            logger.debug(f"Searching emails with query: {query}")

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} email(s)")
            return messages

        except Exception as e:
            logger.error(f"Email search failed: {e}")
            raise

    def get_email_details(self, message_id: str) -> Dict:
        """
        Get full email details.

        Args:
            message_id: Gmail message ID

        Returns:
            Complete message dictionary
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return message
        except Exception as e:
            logger.error(f"Failed to get email details: {e}")
            raise

    def create_draft(self, to: str, subject: str, body: str, thread_id: Optional[str] = None) -> str:
        """
        Create a draft email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            thread_id: Optional thread ID to reply to

        Returns:
            Draft ID
        """
        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            draft_body = {'message': {'raw': raw_message}}
            if thread_id:
                draft_body['message']['threadId'] = thread_id

            draft = self.service.users().drafts().create(
                userId='me',
                body=draft_body
            ).execute()

            logger.debug(f"Draft created with ID: {draft['id']}")
            return draft['id']

        except Exception as e:
            logger.error(f"Draft creation failed: {e}")
            raise

    def extract_email_data(self, message: Dict) -> Dict:
        """
        Extract relevant data from Gmail message.

        Args:
            message: Gmail message dictionary

        Returns:
            Dictionary with extracted data
        """
        headers = message['payload']['headers']
        header_dict = {h['name']: h['value'] for h in headers}

        # Get email body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body'].get('data', '')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')
                        break
        else:
            body_data = message['payload']['body'].get('data', '')
            if body_data:
                body = base64.urlsafe_b64decode(body_data).decode('utf-8', errors='ignore')

        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'from': header_dict.get('From', ''),
            'subject': header_dict.get('Subject', ''),
            'date': header_dict.get('Date', ''),
            'body': body,
            'internal_date': message.get('internalDate', '')
        }
