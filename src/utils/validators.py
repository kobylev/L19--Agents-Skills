"""Input validation utilities."""

import re
from pathlib import Path


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL.

    Args:
        url: URL to validate

    Returns:
        True if valid GitHub repository URL
    """
    pattern = r'^https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(?:\.git)?$'
    return bool(re.match(pattern, url))


def sanitize_github_url(url: str) -> str:
    """
    Normalize GitHub URL (remove .git if present).

    Args:
        url: GitHub URL to sanitize

    Returns:
        Sanitized URL
    """
    return url.rstrip('.git') if url.endswith('.git') else url


def extract_github_url(text: str) -> str:
    """
    Extract GitHub repository URL from text.

    Args:
        text: Text containing GitHub URL

    Returns:
        GitHub URL if found, empty string otherwise
    """
    pattern = r'https://github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_.-]+(?:\.git)?'
    match = re.search(pattern, text)
    return match.group(0) if match else ""


def safe_path_join(base_dir: str, user_input: str) -> str:
    """
    Safely join paths to prevent directory traversal.

    Args:
        base_dir: Base directory
        user_input: User-provided path component

    Returns:
        Safe joined path

    Raises:
        ValueError: If path traversal detected
    """
    base = Path(base_dir).resolve()
    target = (base / user_input).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Path traversal detected: {user_input}")

    return str(target)
