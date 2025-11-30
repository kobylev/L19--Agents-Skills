"""Feedback generation module - Step 3."""

import time
from typing import List, Dict

from src.services.gemini_service import GeminiService, RateLimiter
from src.modules.data_manager import DataManager
from src.utils.logger import logger
from config.settings import settings


class FeedbackGenerator:
    """Handles AI-powered feedback generation - Step 3."""

    def __init__(self, gemini_service: GeminiService):
        """
        Initialize feedback generator.

        Args:
            gemini_service: Gemini service instance
        """
        self.gemini_service = gemini_service
        self.data_manager = DataManager()
        self.rate_limiter = RateLimiter(max_calls=60, time_window=60)

    def generate_all_feedback(self, input_file: str, output_file: str):
        """
        Generate feedback for all students.

        Args:
            input_file: Path to file_2_3.xlsx
            output_file: Path to file_3_4.xlsx
        """
        try:
            logger.info("Starting feedback generation")

            # Read input file
            df = self.data_manager.read_from_excel(input_file)

            # Filter rows with status='Ready'
            ready_df = self.data_manager.filter_ready_rows(df)

            if ready_df.empty:
                logger.warning("No 'Ready' rows found in input file")
                self.data_manager.write_to_excel([], output_file)
                return {'generated': 0, 'failed': 0}

            students = ready_df.to_dict('records')
            logger.info(f"Generating feedback for {len(students)} students")

            results = []
            successful = 0
            failed = 0

            for student in students:
                try:
                    # Rate limiting
                    self.rate_limiter.wait_if_needed()
                    time.sleep(settings.gemini_request_delay)

                    # Determine style based on grade
                    grade = float(student['grade'])
                    style = self.get_style(grade)

                    logger.debug(f"Generating feedback for {student['email_id']} (grade: {grade}, style: {style})")

                    # Generate feedback
                    reply = self.gemini_service.generate_feedback(grade, style)

                    # Check if feedback was generated successfully
                    if reply and len(reply) >= 50:
                        results.append({
                            'email_id': student['email_id'],
                            'reply': reply,
                            'status': 'Ready'
                        })
                        successful += 1
                        logger.info(f"Feedback generated for {student['email_id']}")
                    else:
                        if reply:
                            logger.warning(f"Feedback too short ({len(reply)} chars) for {student['email_id']}")
                        else:
                            logger.warning(f"No feedback generated for {student['email_id']}")

                        results.append({
                            'email_id': student['email_id'],
                            'reply': None,
                            'status': 'Missing: reply'
                        })
                        failed += 1

                except Exception as e:
                    logger.error(f"Failed to generate feedback for {student['email_id']}: {e}")
                    failed += 1
                    results.append({
                        'email_id': student['email_id'],
                        'reply': None,
                        'status': 'Missing: reply'
                    })

            # Save results
            self.data_manager.write_to_excel(results, output_file)

            logger.info(f"Feedback generation complete: {successful} generated, {failed} failed")

            return {
                'generated': successful,
                'failed': failed
            }

        except Exception as e:
            logger.error(f"Feedback generation failed: {e}")
            raise

    def get_style(self, grade: float) -> str:
        """
        Determine feedback style based on grade.

        Args:
            grade: Student grade (0-100)

        Returns:
            Style name
        """
        if grade >= 90:
            return "trump"
        elif grade >= 70:
            return "hason"
        elif grade >= 55:
            return "constructive"
        else:
            return "amsalem"
