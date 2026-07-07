"""
config.py
---------
Central configuration for ResumeIQ AI.

Loads environment variables, defines application-wide constants, and
exposes a single `Settings` object that the rest of the codebase imports
from. Keeping configuration in one place avoids scattering magic numbers
and `os.environ` calls throughout the app.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()  # Loads variables from a local .env file if present.


@dataclass(frozen=True)
class Settings:
    """Immutable application settings, sourced from environment variables."""

    # --- Gemini / AI configuration -----------------------------------
    gemini_api_key: str | None = field(
        default_factory=lambda: os.getenv("GEMINI_API_KEY")
    )
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    gemini_timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))
    )
    gemini_max_retries: int = field(
        default_factory=lambda: int(os.getenv("GEMINI_MAX_RETRIES", "2"))
    )

    # --- Upload constraints ---------------------------------------------
    max_upload_size_mb: int = field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_SIZE_MB", "8"))
    )
    allowed_extensions: tuple[str, ...] = (".pdf",)
    max_pages: int = field(
        default_factory=lambda: int(os.getenv("MAX_PDF_PAGES", "12"))
    )
    min_extracted_chars: int = 50  # Below this, we treat the PDF as empty/unreadable.
    max_extracted_chars: int = 60_000  # Hard cap sent to the model, for cost/safety.

    # --- App metadata ----------------------------------------------------
    app_name: str = "ResumeIQ AI"
    app_tagline: str = "AI-powered resume intelligence for job seekers who mean business."
    support_email: str = field(
        default_factory=lambda: os.getenv("SUPPORT_EMAIL", "support@resumeiq.ai")
    )

    # --- Logging ----------------------------------------------------------
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def has_valid_api_key(self) -> bool:
        return bool(self.gemini_api_key and self.gemini_api_key.strip())


settings = Settings()
