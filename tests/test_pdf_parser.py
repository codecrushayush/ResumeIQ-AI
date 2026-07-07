"""Unit tests for pdf_parser.py — corrupted, empty, and valid PDF handling."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pdf_parser import PDFParsingError, parse_resume_pdf  # noqa: E402


def _make_minimal_pdf_with_text(text: str) -> bytes:
    """Build a minimal single-page PDF containing the given text, using
    only reportlab (already a project dependency) so tests need no
    external fixture files."""
    from reportlab.pdfgen import canvas

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(72, 720, text)
    c.save()
    return buffer.getvalue()


def test_parse_resume_pdf_extracts_text():
    pdf_bytes = _make_minimal_pdf_with_text(
        "Jane Doe Senior Software Engineer with 8 years of experience in Python and cloud systems."
    )
    result = parse_resume_pdf(pdf_bytes)
    assert "Jane Doe" in result.text
    assert result.page_count == 1


def test_parse_resume_pdf_rejects_corrupted_bytes():
    with pytest.raises(PDFParsingError):
        parse_resume_pdf(b"not a real pdf at all")


def test_parse_resume_pdf_rejects_effectively_empty_pdf():
    # A PDF with only a couple of characters of text falls below the
    # minimum extracted-character threshold.
    pdf_bytes = _make_minimal_pdf_with_text("Hi")
    with pytest.raises(PDFParsingError):
        parse_resume_pdf(pdf_bytes)
