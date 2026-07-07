"""
analysis_view.py
-----------------
Pure rendering layer: takes a `ResumeAnalysis` (and optionally a
`JDMatchResult`) plus a Streamlit module reference and draws the results
dashboard. Contains no business logic and never calls the Gemini API or
parses PDFs — app.py is responsible for orchestration.
"""

from __future__ import annotations

from analyzer import JDMatchResult, ResumeAnalysis
from styles import render_badge, render_gauge_card, render_pill_list


def _hiring_badge_level(recommendation: str) -> str:
    mapping = {
        "Strong Fit": "good",
        "Potential Fit": "warn",
        "Needs Development": "bad",
        "Not Enough Information": "warn",
    }
    return mapping.get(recommendation, "warn")


def render_overview(st, analysis: ResumeAnalysis, word_count: int, reading_time: int) -> None:
    """Top-of-dashboard score gauges and quick metrics."""
    st.markdown('<div class="riq-section-label">Scan results</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        render_gauge_card(st, "ATS Score", "Automated screening compatibility", analysis.ats_score)
    with col2:
        render_gauge_card(st, "AI Confidence", "Certainty of this analysis", analysis.ai_confidence_score)
    with col3:
        st.markdown('<div class="riq-card">', unsafe_allow_html=True)
        st.markdown('<div class="riq-card-label">Hiring recommendation</div>', unsafe_allow_html=True)
        render_badge(st, analysis.hiring_recommendation, _hiring_badge_level(analysis.hiring_recommendation))
        st.markdown(
            f'<p style="margin-top:0.7rem; color:#5B6B82; font-size:0.85rem;">'
            f"{word_count:,} words &middot; ~{reading_time} min read</p>",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def render_summary(st, analysis: ResumeAnalysis) -> None:
    st.markdown('<div class="riq-section-label">Executive summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="riq-card">{analysis.summary}</div>', unsafe_allow_html=True)


def render_strengths_weaknesses(st, analysis: ResumeAnalysis) -> None:
    st.markdown('<div class="riq-section-label">Strengths & weaknesses</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="riq-card"><h4>✅ Strengths</h4></div>', unsafe_allow_html=True)
        for item in analysis.strengths:
            st.markdown(f"- {item}")
    with col2:
        st.markdown('<div class="riq-card"><h4>⚠️ Weaknesses</h4></div>', unsafe_allow_html=True)
        for item in analysis.weaknesses:
            st.markdown(f"- {item}")


def render_skills(st, analysis: ResumeAnalysis) -> None:
    st.markdown('<div class="riq-section-label">Skills breakdown</div>', unsafe_allow_html=True)
    st.markdown('<div class="riq-card"><div class="riq-card-label">Technical skills</div></div>', unsafe_allow_html=True)
    render_pill_list(st, analysis.technical_skills, "match")
    st.markdown('<div class="riq-card"><div class="riq-card-label">Soft skills</div></div>', unsafe_allow_html=True)
    render_pill_list(st, analysis.soft_skills)
    st.markdown('<div class="riq-card"><div class="riq-card-label">Missing skills</div></div>', unsafe_allow_html=True)
    render_pill_list(st, analysis.missing_skills, "missing")


def render_deep_dive(st, analysis: ResumeAnalysis) -> None:
    st.markdown('<div class="riq-section-label">Deep dive</div>', unsafe_allow_html=True)
    sections = [
        ("🔑 Keyword Analysis", analysis.keyword_analysis),
        ("💼 Experience Analysis", analysis.experience_analysis),
        ("🛠️ Project Quality Analysis", analysis.project_quality_analysis),
        ("🎓 Education Review", analysis.education_review),
        ("✍️ Grammar Review", analysis.grammar_review),
        ("📐 Formatting Review", analysis.formatting_review),
    ]
    for title, content in sections:
        with st.expander(title):
            st.write(content)


def render_growth_plan(st, analysis: ResumeAnalysis) -> None:
    st.markdown('<div class="riq-section-label">Growth plan</div>', unsafe_allow_html=True)
    with st.expander("🚀 Resume Improvements", expanded=True):
        for item in analysis.improvements:
            st.markdown(f"- {item}")
    with st.expander("🎯 Recommended Job Roles"):
        render_pill_list(st, analysis.recommended_job_roles, "match")
    with st.expander("📚 Learning Roadmap"):
        for item in analysis.learning_roadmap:
            st.markdown(f"- {item}")
    with st.expander("🗣️ Likely Interview Questions"):
        for i, q in enumerate(analysis.interview_questions, start=1):
            st.markdown(f"**{i}.** {q}")


def render_jd_match(st, jd_match: JDMatchResult) -> None:
    st.markdown('<div class="riq-section-label">Resume vs. job description</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        render_gauge_card(st, "Match Score", "Overall fit for this role", jd_match.match_score)
    with col2:
        render_gauge_card(st, "ATS Probability", "Chance of clearing this job's ATS", jd_match.ats_probability)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="riq-card"><div class="riq-card-label">Matching skills</div></div>', unsafe_allow_html=True)
        render_pill_list(st, jd_match.matching_skills, "match")
    with col2:
        st.markdown('<div class="riq-card"><div class="riq-card-label">Missing skills</div></div>', unsafe_allow_html=True)
        render_pill_list(st, jd_match.missing_skills, "missing")

    st.markdown('<div class="riq-card"><div class="riq-card-label">Missing keywords</div></div>', unsafe_allow_html=True)
    render_pill_list(st, jd_match.missing_keywords, "missing")

    with st.expander("✏️ Suggestions"):
        for item in jd_match.suggestions:
            st.markdown(f"- {item}")
    with st.expander("📝 Recommended Resume Changes"):
        for item in jd_match.recommended_changes:
            st.markdown(f"- {item}")


def render_full_dashboard(
    st,
    analysis: ResumeAnalysis,
    word_count: int,
    reading_time: int,
    jd_match: JDMatchResult | None = None,
) -> None:
    """Render the entire results dashboard in order."""
    render_overview(st, analysis, word_count, reading_time)
    render_summary(st, analysis)
    render_strengths_weaknesses(st, analysis)
    render_skills(st, analysis)
    render_deep_dive(st, analysis)
    render_growth_plan(st, analysis)
    if jd_match is not None:
        render_jd_match(st, jd_match)
