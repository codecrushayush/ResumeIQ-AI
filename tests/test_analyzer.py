"""
Unit tests for analyzer.py.

These tests never call the real Gemini API — the client is monkeypatched
so the test suite runs offline and deterministically.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import analyzer  # noqa: E402
from config import Settings  # noqa: E402


def test_match_resume_to_job_rejects_empty_job_description(monkeypatch):
    monkeypatch.setattr(analyzer.settings, "gemini_api_key", "fake-key")
    with pytest.raises(analyzer.AnalyzerError):
        analyzer.match_resume_to_job("Some resume text", "   ")


def test_generate_structured_fails_fast_without_api_key(monkeypatch):
    monkeypatch.setattr(analyzer.settings, "gemini_api_key", None)
    with pytest.raises(analyzer.AnalyzerError, match="not configured"):
        analyzer.analyze_resume("Some resume text")


def test_resume_analysis_schema_rejects_out_of_range_score():
    with pytest.raises(Exception):
        analyzer.ResumeAnalysis(
            ats_score=150,  # invalid: > 100
            ai_confidence_score=80,
            summary="ok",
            strengths=[],
            weaknesses=[],
            technical_skills=[],
            soft_skills=[],
            missing_skills=[],
            keyword_analysis="",
            experience_analysis="",
            project_quality_analysis="",
            education_review="",
            grammar_review="",
            formatting_review="",
            improvements=[],
            recommended_job_roles=[],
            learning_roadmap=[],
            interview_questions=[],
            hiring_recommendation="Strong Fit",
        )


def test_jd_match_result_valid_construction():
    result = analyzer.JDMatchResult(
        match_score=72,
        ats_probability=60,
        matching_skills=["Python"],
        missing_skills=["Kubernetes"],
        missing_keywords=["CI/CD"],
        suggestions=["Add a metrics-driven bullet point."],
        recommended_changes=["Mention deployment scale."],
    )
    assert result.match_score == 72
