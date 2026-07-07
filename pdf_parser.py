"""
pdf_parser.py
-------------
Handles all PDF ingestion concerns: opening the file, guarding against
encrypted/corrupted/oversized documents, and extracting clean text exactly
once per upload (the extracted text is cached upstream by app.py so we
never re-parse the same file on rerun).

This module raises `PDFParsingError` for every failure mode instead of
letting exceptions bubble up as raw tracebacks — app.py turns these into
friendly UI messages.
"""

from __future__ import annotations

import io
from dataclasses import dataclass

import pdfplumber

from config import settings
from utils import clean_extracted_text, get_logger

logger = get_logger(__name__)


class PDFParsingError(Exception):
    """Raised for any recoverable PDF parsing failure. Message is user-safe."""


@dataclass(frozen=True)
class ParsedResume:
    """Result of a successful PDF parse."""

    text: str
    page_count: int


def parse_resume_pdf(file_bytes: bytes) -> ParsedResume:
    """Extract text from an uploaded resume PDF.

    Raises:
        PDFParsingError: with a friendly, user-facing message for every
        failure mode (encrypted, corrupted, empty, too many pages).
    """
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if pdf.metadata is None and len(pdf.pages) == 0:
                raise PDFParsingError(
                    "This PDF appears to be empty. Please upload a resume with content."
                )

            if len(pdf.pages) > settings.max_pages:
                raise PDFParsingError(
                    f"This PDF has {len(pdf.pages)} pages, which exceeds our "
                    f"{settings.max_pages}-page limit for resumes. Please upload a "
                    "more concise document."
                )

            page_texts = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                page_texts.append(page_text)

            raw_text = "\n".join(page_texts)
            cleaned = clean_extracted_text(raw_text)

            if len(cleaned) < settings.min_extracted_chars:
                raise PDFParsingError(
                    "We couldn't extract readable text from this PDF. It may be "
                    "a scanned image, password-protected, or contain no text. "
                    "Please upload a text-based PDF resume."
                )

            truncated = len(cleaned) > settings.max_extracted_chars
            final_text = cleaned[: settings.max_extracted_chars] if truncated else cleaned

            logger.info(
                "Parsed resume PDF: pages=%d chars=%d truncated=%s",
                len(pdf.pages),
                len(final_text),
                truncated,
            )

            return ParsedResume(text=final_text, page_count=len(pdf.pages))

    except PDFParsingError:
        raise
    except pdfplumber.pdfminer.pdfdocument.PDFPasswordIncorrect as exc:
        raise PDFParsingError(
            "This PDF is password-protected. Please upload an unencrypted resume."
        ) from exc
    except Exception as exc:  # noqa: BLE001 - we deliberately catch-all at this boundary
        logger.error("PDF parsing failed: %s", type(exc).__name__)
        raise PDFParsingError(
            "We couldn't read this PDF. It may be corrupted or in an unsupported "
            "format. Please try re-exporting it and uploading again."
        ) from exc
