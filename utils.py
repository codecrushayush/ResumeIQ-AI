"""
utils.py
--------
Small, reusable, side-effect-free helpers used across the application:
logging setup, file validation, and text metrics.

IMPORTANT (security): `get_logger` is configured to never receive resume
content. Callers must log metadata (file size, page count, elapsed time)
and never the extracted resume text itself.
"""

from __future__ import annotations

import logging
import re
import sys
from dataclasses import dataclass

from config import settings


def get_logger(name: str) -> logging.Logger:
    """Return a configured module-level logger.

    Logs go to stdout only. Callers must never pass resume content to this
    logger — only metadata (sizes, durations, status codes).
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(settings.log_level)
        logger.propagate = False
    return logger


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of a validation check, with a user-facing message on failure."""

    is_valid: bool
    message: str = ""


def validate_upload(filename: str, size_bytes: int) -> ValidationResult:
    """Validate a file's extension and size before it is ever parsed.

    This is the first line of defense against malicious or oversized
    uploads and never inspects file content.
    """
    lower_name = filename.lower()
    if not any(lower_name.endswith(ext) for ext in settings.allowed_extensions):
        return ValidationResult(
            False,
            f"Unsupported file type. Please upload a PDF ({', '.join(settings.allowed_extensions)}).",
        )

    if size_bytes <= 0:
        return ValidationResult(False, "The uploaded file appears to be empty.")

    if size_bytes > settings.max_upload_size_bytes:
        return ValidationResult(
            False,
            f"File is too large. Maximum allowed size is {settings.max_upload_size_mb} MB.",
        )

    return ValidationResult(True)


def count_words(text: str) -> int:
    """Count words in a way that's robust to extra whitespace/newlines."""
    return len(re.findall(r"\b[\w'-]+\b", text or ""))


def estimate_reading_time_minutes(word_count: int, words_per_minute: int = 200) -> int:
    """Estimate reading time in whole minutes, minimum of 1."""
    if word_count <= 0:
        return 0
    return max(1, round(word_count / words_per_minute))


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text to a maximum character count, preserving whole words."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    return truncated[:last_space] if last_space > 0 else truncated


def clean_extracted_text(text: str) -> str:
    """Normalize whitespace produced by PDF extraction."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
