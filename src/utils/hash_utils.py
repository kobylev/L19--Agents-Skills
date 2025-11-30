"""Hashing utilities for email and ID generation."""

import hashlib


def hash_email(email: str) -> str:
    """
    Generate SHA-256 hash of email address.

    Args:
        email: Email address to hash

    Returns:
        64-character hexadecimal hash
    """
    return hashlib.sha256(email.lower().strip().encode()).hexdigest()


def generate_email_id(email: str, subject: str, datetime_str: str) -> str:
    """
    Generate unique email ID from email, subject, and datetime.

    Args:
        email: Sender email address
        subject: Email subject
        datetime_str: Email datetime as string

    Returns:
        64-character hexadecimal hash
    """
    combined = f"{email.lower().strip()}|{subject}|{datetime_str}"
    return hashlib.sha256(combined.encode()).hexdigest()
