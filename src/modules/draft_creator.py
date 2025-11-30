"""Draft email creation module - Step 4."""

from typing import Dict
import pandas as pd

from src.services.gmail_service import GmailService
from src.modules.data_manager import DataManager
from src.utils.logger import logger
from config.settings import settings


class DraftCreator:
    """Handles email draft creation - Step 4."""

    def __init__(self, gmail_service: GmailService):
        """
        Initialize draft creator.

        Args:
            gmail_service: Gmail service instance
        """
        self.gmail_service = gmail_service
        self.data_manager = DataManager()

    def create_all_drafts(self, file_3_4: str, file_1_2: str, mapping_file: str):
        """
        Create email drafts for all students.

        Args:
            file_3_4: Path to file_3_4.xlsx (feedback data)
            file_1_2: Path to file_1_2.xlsx (email metadata)
            mapping_file: Path to students_mapping.xlsx
        """
        try:
            logger.info("Starting draft creation")

            # Load feedback data
            feedback_df = self.data_manager.read_from_excel(file_3_4)
            ready_feedback_df = self.data_manager.filter_ready_rows(feedback_df)

            if ready_feedback_df.empty:
                logger.warning("No 'Ready' rows found in feedback file")
                return {'created': 0, 'failed': 0}

            # Load email metadata
            email_df = self.data_manager.read_from_excel(file_1_2)

            # Load student mapping
            student_mapping = self.data_manager.load_student_mapping(mapping_file)

            logger.info(f"Creating drafts for {len(ready_feedback_df)} students")

            created = 0
            failed = 0

            for _, feedback_row in ready_feedback_df.iterrows():
                try:
                    email_id = feedback_row['email_id']
                    reply = feedback_row['reply']

                    # Find corresponding email metadata
                    email_row = email_df[email_df['email_id'] == email_id]
                    if email_row.empty:
                        logger.error(f"Email metadata not found for {email_id}")
                        failed += 1
                        continue

                    email_row = email_row.iloc[0]

                    # Get data from email metadata
                    repo_url = email_row['repo_url']
                    sender_email = email_row['sender_email']
                    thread_id = email_row['thread_id']
                    subject = email_row['email_subject']

                    # Get student name from mapping
                    student_name = student_mapping.get(sender_email.lower(), "Student")

                    # Compose draft
                    draft_body = self.compose_draft(student_name, reply, repo_url)

                    # Create draft in Gmail
                    draft_id = self.gmail_service.create_draft(
                        to=sender_email,
                        subject=f"Re: {subject}",
                        body=draft_body,
                        thread_id=thread_id
                    )

                    created += 1
                    logger.info(f"Draft created for {email_id} (draft_id: {draft_id}, name: {student_name})")

                except Exception as e:
                    logger.error(f"Failed to create draft for {email_id}: {e}")
                    failed += 1

            logger.info(f"Draft creation complete: {created} created, {failed} failed")

            return {
                'created': created,
                'failed': failed
            }

        except Exception as e:
            logger.error(f"Draft creation failed: {e}")
            raise

    def compose_draft(self, name: str, reply: str, repo_url: str) -> str:
        """
        Compose draft email body.

        Args:
            name: Student name
            reply: Feedback text
            repo_url: Repository URL

        Returns:
            Composed email body
        """
        template = f"""Hi, {name}!

{reply}

Your code repository reviewed: {repo_url}

Thanks,
Koby"""

        return template
