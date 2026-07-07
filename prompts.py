"""
prompts.py
----------
All prompt text lives here, isolated from the API-calling logic in
analyzer.py. This keeps prompt iteration low-risk and reviewable in
isolation, and makes it trivial to unit test prompt construction without
touching network code.
"""

from __future__ import annotations

PERSONA_INSTRUCTIONS = """
You are a panel of four experts reviewing a single resume together:
1. An ATS (Applicant Tracking System) recruiter who evaluates keyword and
   formatting compatibility with automated screening software.
2. An HR Manager who evaluates clarity, professionalism, and red flags.
3. A Senior Technical Hiring Manager who evaluates technical depth,
   project quality, and seniority signals.
4. A Career Coach who evaluates growth trajectory and framing.

Ground every judgment strictly in the resume text provided. Never invent
employers, dates, technologies, metrics, or achievements that are not
present in the text. If information needed for a field is genuinely
absent from the resume, use exactly the string "Not enough information
available." for that field instead of guessing.
""".strip()

RESUME_ANALYSIS_INSTRUCTIONS = """
Analyze the resume below and return your findings as JSON matching the
provided schema exactly. Scores are integers from 0 to 100.

Guidance for specific fields:
- ats_score: likelihood this resume passes automated ATS keyword/format screening.
- ai_confidence_score: your confidence in the overall analysis (100 = the
  resume text was complete and unambiguous; lower if text extraction
  looked incomplete or garbled).
- strengths / weaknesses: concrete, resume-specific observations, not generic advice.
- keyword_analysis: important industry/role keywords that are present vs. notably absent.
- interview_questions: 5 questions a hiring manager would realistically ask THIS candidate.
- hiring_recommendation: one of "Strong Fit", "Potential Fit", "Needs Development", or "Not Enough Information".

Resume text:
---
{resume_text}
---
""".strip()

JD_MATCH_INSTRUCTIONS = """
Compare the resume to the job description below and return your findings
as JSON matching the provided schema exactly. Ground every judgment
strictly in the two texts provided; never invent skills or requirements
that are not present in the job description.

- match_score: overall fit of this resume for this specific job, 0-100.
- ats_probability: likelihood an ATS configured for this job description
  would surface this resume to a human recruiter, 0-100.
- matching_skills / missing_skills: compare resume content directly against
  the job description's stated requirements.
- recommended_changes: specific, actionable rewrites tied to this job description.

Resume text:
---
{resume_text}
---

Job description:
---
{job_description}
---
""".strip()


def build_resume_analysis_prompt(resume_text: str) -> str:
    return (
        PERSONA_INSTRUCTIONS
        + "\n\n"
        + RESUME_ANALYSIS_INSTRUCTIONS.format(resume_text=resume_text)
    )


def build_jd_match_prompt(resume_text: str, job_description: str) -> str:
    return (
        PERSONA_INSTRUCTIONS
        + "\n\n"
        + JD_MATCH_INSTRUCTIONS.format(
            resume_text=resume_text, job_description=job_description
        )
    )
