"""Email processing module - Step 1."""

import re
from datetime import datetime
from typing import List, Dict, Optional
from email.utils import parsedate_to_datetime

from src.services.gmail_service import GmailService
from src.modules.data_manager import DataManager
from src.utils.hash_utils import generate_email_id, hash_email
from src.utils.validators import extract_github_url, validate_github_url
from src.utils.logger import logger


class EmailProcessor:
    """Handles email search and parsing - Step 1."""

    SUBJECT_PATTERN = re.compile(
        r'self\s+check\s+of\s+homework\s+(\d{1,3})',
        re.IGNORECASE
    )

    def __init__(self, gmail_service: GmailService):
        """
        Initialize email processor.

        Args:
            gmail_service: Gmail service instance
        """
        self.gmail_service = gmail_service
        self.data_manager = DataManager()

    def matches_pattern(self, subject: str) -> bool:
        """
        Check if email subject matches the pattern.

        Args:
            subject: Email subject

        Returns:
            True if matches pattern
        """
        return bool(self.SUBJECT_PATTERN.search(subject))

    def extract_sender_email(self, from_header: str) -> str:
        """
        Extract email address from 'From' header.

        Args:
            from_header: Email 'From' header (e.g., "Name <email@example.com>")

        Returns:
            Email address
        """
        # Extract email from format "Name <email@example.com>"
        match = re.search(r'<([^>]+)>', from_header)
        if match:
            return match.group(1).strip().lower()
        # If no brackets, assume it's just the email
        return from_header.strip().lower()

    def process_emails(self, limit: Optional[int] = None) -> Dict:
        """
        Search and process emails.

        Args:
            limit: Maximum number of emails to process

        Returns:
            Dictionary with processing results
        """
        try:
            logger.info(f"Starting email search (limit: {limit or 'unlimited'})")

            # Search for unread emails with "self check of homework" in subject
            query = 'is:unread subject:"self check of homework"'
            messages = self.gmail_service.search_emails(query, max_results=limit)

            if not messages:
                logger.warning("No matching emails found")
                return {
                    'processed': 0,
                    'data': []
                }

            processed_data = []
            for msg_info in messages:
                try:
                    # Get full email details
                    message = self.gmail_service.get_email_details(msg_info['id'])
                    email_data = self.gmail_service.extract_email_data(message)

                    # Check if subject matches pattern
                    if not self.matches_pattern(email_data['subject']):
                        logger.debug(f"Subject doesn't match pattern: {email_data['subject']}")
                        continue

                    # Extract sender email
                    sender_email = self.extract_sender_email(email_data['from'])

                    # Parse datetime
                    try:
                        email_datetime = parsedate_to_datetime(email_data['date'])
                    except:
                        # Fallback to internal date
                        internal_timestamp = int(email_data['internal_date']) / 1000
                        email_datetime = datetime.fromtimestamp(internal_timestamp)

                    # Generate email_id
                    email_id = generate_email_id(
                        sender_email,
                        email_data['subject'],
                        email_datetime.isoformat()
                    )

                    # Extract GitHub URL from body
                    repo_url = extract_github_url(email_data['body'])

                    # Validate and prepare data
                    row_data = {
                        'email_id': email_id,
                        'email_datetime': email_datetime.isoformat(),
                        'email_subject': email_data['subject'],
                        'repo_url': repo_url if repo_url else None,
                        'hashed_email_address': hash_email(sender_email),
                        'sender_email': sender_email,  # Store for draft creation
                        'thread_id': email_data['thread_id'],  # Store for reply threading
                        'status': self._determine_status({
                            'email_id': email_id,
                            'email_datetime': email_datetime,
                            'email_subject': email_data['subject'],
                            'repo_url': repo_url,
                            'hashed_email_address': hash_email(sender_email)
                        })
                    }

                    processed_data.append(row_data)
                    logger.info(f"Processed: {email_data['subject']} (status: {row_data['status']})")

                except Exception as e:
                    logger.error(f"Error processing email {msg_info['id']}: {e}")
                    continue

            logger.info(f"Email processing complete: {len(processed_data)} email(s) processed")

            return {
                'processed': len(processed_data),
                'data': processed_data
            }

        except Exception as e:
            logger.error(f"Email processing failed: {e}")
            raise

    def _determine_status(self, data: Dict) -> str:
        """
        Determine row status based on field completeness.

        Args:
            data: Row data dictionary

        Returns:
            Status string
        """
        missing = []

        if not data.get('email_id'):
            missing.append('email_id')
        if not data.get('email_datetime'):
            missing.append('email_datetime')
        if not data.get('email_subject'):
            missing.append('email_subject')
        if not data.get('repo_url'):
            missing.append('repo_url')
        if not data.get('hashed_email_address'):
            missing.append('hashed_email_address')

        if missing:
            return f"Missing: {', '.join(missing)}"
        return "Ready"

    def save_to_excel(self, data: List[Dict], output_path: str):
        """
        Save processed email data to Excel.

        Args:
            data: List of email data dictionaries
            output_path: Output file path
        """
        # Keep all fields including sender_email and thread_id for later steps
        excel_data = []
        for row in data:
            excel_row = {
                'email_id': row['email_id'],
                'email_datetime': row['email_datetime'],
                'email_subject': row['email_subject'],
                'repo_url': row['repo_url'],
                'status': row['status'],
                'hashed_email_address': row['hashed_email_address'],
                'sender_email': row['sender_email'],
                'thread_id': row['thread_id']
            }
            excel_data.append(excel_row)

        self.data_manager.write_to_excel(excel_data, output_path)
