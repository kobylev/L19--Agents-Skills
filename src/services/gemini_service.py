"""Gemini API service wrapper."""

import time
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from src.utils.logger import logger


class GeminiService:
    """Wrapper for Gemini API operations."""

    def __init__(self, api_key: str):
        """
        Initialize Gemini service.

        Args:
            api_key: Gemini API key
        """
        if not genai:
            raise ImportError("google-generativeai package not installed")

        if not api_key:
            raise ValueError("Gemini API key is required")

        genai.configure(api_key=api_key)

        self.generation_config = {
            "temperature": 0.9,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }

        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ]

        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-pro",
            generation_config=self.generation_config,
            safety_settings=self.safety_settings
        )

        logger.info("Gemini service initialized")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def generate_feedback(self, grade: float, style: str) -> Optional[str]:
        """
        Generate feedback based on grade and style.

        Args:
            grade: Student grade (0-100)
            style: Feedback style (trump, hason, constructive, amsalem)

        Returns:
            Generated feedback text, or None if generation failed
        """
        prompt = self._build_prompt(grade, style)

        try:
            logger.debug(f"Generating feedback for grade {grade:.1f} with style '{style}'")
            response = self.model.generate_content(prompt)

            # Check if response has candidates before accessing text
            if not response.candidates or len(response.candidates) == 0:
                logger.warning("No candidates in Gemini response (likely blocked by safety filters)")
                return None

            # Safely access the text from the first candidate
            try:
                candidate = response.candidates[0]
                if hasattr(candidate.content, 'parts') and candidate.content.parts:
                    feedback = candidate.content.parts[0].text.strip()
                    if feedback:
                        logger.debug(f"Generated feedback: {len(feedback)} characters")
                        return feedback
                    else:
                        logger.warning("Empty text in Gemini response")
                        return None
                else:
                    logger.warning("No parts in candidate content")
                    return None
            except (AttributeError, IndexError) as e:
                logger.warning(f"Error accessing candidate text: {e}")
                return None

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return None

    def _build_prompt(self, grade: float, style: str) -> str:
        """
        Build prompt based on grade category.

        Args:
            grade: Student grade
            style: Feedback style

        Returns:
            Prompt string
        """
        prompts = {
            "trump": f"""Write a congratulatory message for a student who achieved a {grade:.1f}% grade on their homework.
Style: Donald Trump - enthusiastic, uses superlatives like "tremendous", "fantastic", "the best",
proud tone, confident, mentions winning and success. Keep it 3-5 sentences. Professional but energetic.

IMPORTANT: The response must comply with all Gemini safety policies and content guidelines.

Student grade: {grade:.1f}%""",

            "hason": f"""Write a witty, humorous congratulatory message for a student who achieved a {grade:.1f}% grade.
Style: Standup comedian - clever wordplay, light jokes about coding, relatable humor about
programming struggles, upbeat. Keep it 3-5 sentences. Funny but respectful.

IMPORTANT: The response must comply with all Gemini safety policies and content guidelines.

Student grade: {grade:.1f}%""",

            "constructive": f"""Write a constructive, encouraging message for a student who achieved a {grade:.1f}% grade.
Focus on: specific areas for improvement, positive reinforcement, actionable suggestions for
better code organization and structure. Keep it 3-5 sentences. Supportive and educational.

IMPORTANT: The response must comply with all Gemini safety policies and content guidelines.

Student grade: {grade:.1f}%""",

            "amsalem": f"""Write a direct, motivational message for a student who achieved a {grade:.1f}% grade.
Style: Tough-love mentor - honest and straightforward feedback, clear expectations, firm but constructive,
challenging tone that motivates improvement, accountability-focused. Keep it 3-5 sentences.
Direct and candid style that encourages the student to step up their effort.

IMPORTANT: The response must comply with all Gemini safety policies and content guidelines. Be direct but professional and educational.

Student grade: {grade:.1f}%"""
        }

        return prompts.get(style, prompts["constructive"])

    def _get_fallback_feedback(self, grade: float, style: str) -> str:
        """
        Fallback feedback if API fails.

        Args:
            grade: Student grade
            style: Feedback style

        Returns:
            Fallback feedback text
        """
        fallbacks = {
            "trump": f"Fantastic work! You achieved {grade:.1f}% - tremendous effort! Your code shows real winning potential. Keep up this great performance!",
            "hason": f"Great job on scoring {grade:.1f}%! Your code is solid. I bet your compiler had a good laugh at your variable names though!",
            "constructive": f"You scored {grade:.1f}%. Keep working on code structure and organization. Focus on breaking down larger problems into smaller functions.",
            "amsalem": f"A {grade:.1f}%? Really? This is unacceptable work. You need to wake up and take this seriously. Stop making excuses and actually put in the effort. Your code quality reflects your commitment - and right now, it's severely lacking!"
        }
        return fallbacks.get(style, f"You scored {grade:.1f}% on this assignment. Keep working hard!")


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, max_calls: int, time_window: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = time.time()

        # Remove calls outside time window
        self.calls = [call_time for call_time in self.calls
                      if now - call_time < self.time_window]

        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            wait_time = (oldest_call + self.time_window - now)
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)

        self.calls.append(now)
