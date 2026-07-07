"""Unit tests for utils.py — validation, text metrics, cleaning."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from utils import (  # noqa: E402
    clean_extracted_text,
    count_words,
    estimate_reading_time_minutes,
    truncate_text,
    validate_upload,
)


def test_validate_upload_rejects_wrong_extension():
    result = validate_upload("resume.docx", 1000)
    assert not result.is_valid
    assert "PDF" in result.message


def test_validate_upload_rejects_empty_file():
    result = validate_upload("resume.pdf", 0)
    assert not result.is_valid


def test_validate_upload_rejects_oversized_file():
    too_big = 100 * 1024 * 1024  # 100 MB
    result = validate_upload("resume.pdf", too_big)
    assert not result.is_valid
    assert "large" in result.message.lower()


def test_validate_upload_accepts_valid_pdf():
    result = validate_upload("resume.pdf", 500_000)
    assert result.is_valid


def test_count_words_basic():
    assert count_words("Senior Software Engineer, 5+ years") == 5


def test_count_words_empty_string():
    assert count_words("") == 0
    assert count_words(None) == 0  # type: ignore[arg-type]


def test_estimate_reading_time_minimum_one_minute():
    assert estimate_reading_time_minutes(50) == 1


def test_estimate_reading_time_zero_words():
    assert estimate_reading_time_minutes(0) == 0


def test_truncate_text_preserves_whole_words():
    text = "one two three four five"
    truncated = truncate_text(text, 10)
    assert not truncated.endswith("t")  # never cuts mid-word
    assert truncated in text


def test_clean_extracted_text_collapses_whitespace():
    messy = "Line one\n\n\n\nLine   two\t\tend"
    cleaned = clean_extracted_text(messy)
    assert "\n\n\n" not in cleaned
    assert "  " not in cleaned.split("\n")[0]
