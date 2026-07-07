"""
analyzer.py
-----------
All Gemini API interaction lives here. app.py and analysis_view.py must
never import `google.genai` directly — they only call the functions in
this module and work with the Pydantic models defined below.

Design notes:
- We request structured JSON output (response_schema) so we get typed,
  parseable results instead of scraping Markdown.
- One resume analysis is a single API call (not 25), and JD matching is a
  second, separate call only triggered when the user pastes a JD. This
  satisfies the "avoid duplicate API calls" performance requirement.
- Every failure mode is caught and re-raised as `AnalyzerError` with a
  friendly, user-safe message. Resume/JD content is never logged.
"""

from __future__ import annotations

import time
from typing import Literal

from google import genai
from google.genai import errors as genai_errors
from google.genai import types as genai_types
from pydantic import BaseModel, Field

from config import settings
from prompts import build_jd_match_prompt, build_resume_analysis_prompt
from utils import get_logger

logger = get_logger(__name__)


class AnalyzerError(Exception):
    """Raised for any recoverable analyzer failure. Message is user-safe."""


# ---------------------------------------------------------------------------
# Structured output schemas
# ---------------------------------------------------------------------------


class ResumeAnalysis(BaseModel):
    """Full structured result of a single resume analysis pass."""

    ats_score: int = Field(ge=0, le=100)
    ai_confidence_score: int = Field(ge=0, le=100)
    summary: str
    strengths: list[str]
    weaknesses: list[str]
    technical_skills: list[str]
    soft_skills: list[str]
    missing_skills: list[str]
    keyword_analysis: str
    experience_analysis: str
    project_quality_analysis: str
    education_review: str
    grammar_review: str
    formatting_review: str
    improvements: list[str]
    recommended_job_roles: list[str]
    learning_roadmap: list[str]
    interview_questions: list[str]
    hiring_recommendation: Literal[
        "Strong Fit", "Potential Fit", "Needs Development", "Not Enough Information"
    ]


class JDMatchResult(BaseModel):
    """Structured result of comparing a resume against a job description."""

    match_score: int = Field(ge=0, le=100)
    ats_probability: int = Field(ge=0, le=100)
    matching_skills: list[str]
    missing_skills: list[str]
    missing_keywords: list[str]
    suggestions: list[str]
    recommended_changes: list[str]


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


def _get_client() -> genai.Client:
    if not settings.has_valid_api_key:
        raise AnalyzerError(
            "AI analysis is not configured. Please set GEMINI_API_KEY in your "
            "environment and restart the app."
        )
    return genai.Client(api_key=settings.gemini_api_key)


def _generate_structured(prompt: str, schema: type[BaseModel]) -> BaseModel:
    """Call Gemini with structured-output config and typed retries.

    Retries only on transient errors (timeouts, 5xx, rate limits). Auth and
    validation errors fail fast since retrying won't help.
    """
    client = _get_client()
    last_exception: Exception | None = None

    for attempt in range(1, settings.gemini_max_retries + 2):
        try:
            response = client.models.generate_content(
                model=settings.gemini_model,
                contents=prompt,
                config=genai_types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.4,
                ),
            )

            if not response.parsed:
                raise AnalyzerError(
                    "The AI returned an unexpected response format. Please try again."
                )
            return response.parsed

        except genai_errors.ClientError as exc:
            status = getattr(exc, "status_code", None) or getattr(exc, "code", None)
            if status == 401 or status == 403:
                raise AnalyzerError(
                    "The Gemini API key was rejected. Please check that "
                    "GEMINI_API_KEY is valid."
                ) from exc
            if status == 429:
                last_exception = exc
                logger.warning("Gemini rate-limited (attempt %d)", attempt)
            else:
                raise AnalyzerError(
                    "The AI service rejected this request. Please try a "
                    "different file or try again shortly."
                ) from exc

        except genai_errors.ServerError as exc:
            last_exception = exc
            logger.warning("Gemini server error (attempt %d): %s", attempt, exc)

        except TimeoutError as exc:
            last_exception = exc
            logger.warning("Gemini timeout (attempt %d)", attempt)

        except Exception as exc:  # noqa: BLE001 - final safety net
            logger.error("Unexpected analyzer error: %s", type(exc).__name__)
            raise AnalyzerError(
                "Something went wrong while analyzing your resume. Please try again."
            ) from exc

        if attempt <= settings.gemini_max_retries:
            time.sleep(min(2 ** attempt, 8))

    logger.error("Gemini call failed after retries: %s", type(last_exception).__name__)
    raise AnalyzerError(
        "The AI service is temporarily unavailable. Please try again in a few moments."
    ) from last_exception


def analyze_resume(resume_text: str) -> ResumeAnalysis:
    """Run the full resume analysis and return a validated result."""
    prompt = build_resume_analysis_prompt(resume_text)
    result = _generate_structured(prompt, ResumeAnalysis)
    logger.info("Resume analysis complete: ats_score=%s", result.ats_score)
    return result  # type: ignore[return-value]


def match_resume_to_job(resume_text: str, job_description: str) -> JDMatchResult:
    """Compare a resume against a job description and return a validated result."""
    if not job_description or not job_description.strip():
        raise AnalyzerError("Please paste a job description to compare against.")

    prompt = build_jd_match_prompt(resume_text, job_description)
    result = _generate_structured(prompt, JDMatchResult)
    logger.info("JD match complete: match_score=%s", result.match_score)
    return result  # type: ignore[return-value]
