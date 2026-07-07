"""
app.py
------
Main Streamlit entrypoint for ResumeIQ AI. This module owns page
orchestration and Streamlit session state only — it never calls the
Gemini API or parses PDF bytes directly. Those concerns live in
analyzer.py and pdf_parser.py respectively, so this file stays thin
and easy to reason about.
"""

from __future__ import annotations

import streamlit as st

from analyzer import AnalyzerError, analyze_resume, match_resume_to_job
from config import settings
from pdf_parser import PDFParsingError, parse_resume_pdf
from report_generator import generate_pdf_report
from styles import inject_custom_css
from utils import (
    count_words,
    estimate_reading_time_minutes,
    get_logger,
    validate_upload,
)
import analysis_view

logger = get_logger(__name__)

st.set_page_config(
    page_title=f"{settings.app_name} — Resume Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css(st)

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

for key, default in {
    "parsed_text": None,
    "parsed_filename": None,
    "analysis": None,
    "jd_match": None,
    "job_description": "",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Sidebar — control panel
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown(f"### 🧠 {settings.app_name}")
    st.caption(settings.app_tagline)
    st.markdown("---")

    if settings.has_valid_api_key:
        st.success("AI engine connected", icon="✅")
    else:
        st.error("GEMINI_API_KEY not set", icon="⚠️")
        st.caption(
            "Add `GEMINI_API_KEY` to your `.env` file (see `.env.example`) "
            "and restart the app."
        )

    st.markdown("---")
    st.markdown("**How it works**")
    st.markdown(
        "1. Upload a PDF resume\n"
        "2. Optionally paste a job description\n"
        "3. Run the scan\n"
        "4. Review results & download the report"
    )
    st.markdown("---")
    st.caption(f"Need help? {settings.support_email}")
    st.caption("Resumes are analyzed in memory and never stored permanently.")


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <div class="riq-hero">
        <div class="riq-hero-eyebrow">AI Resume Intelligence</div>
        <h1>Know exactly how your resume reads<br>before a recruiter does.</h1>
        <p>Upload your resume for an instant ATS scan, skills breakdown, and
        hiring-manager-level feedback — then match it against any job
        description to see exactly what's missing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Upload section
# ---------------------------------------------------------------------------

upload_col, jd_col = st.columns([1, 1])

with upload_col:
    st.markdown("#### 📄 Upload your resume")
    uploaded_file = st.file_uploader(
        "PDF only, up to {} MB".format(settings.max_upload_size_mb),
        type=["pdf"],
        label_visibility="collapsed",
    )

with jd_col:
    st.markdown("#### 🎯 Job description (optional)")
    st.session_state.job_description = st.text_area(
        "Paste a job description to compare against",
        value=st.session_state.job_description,
        height=180,
        label_visibility="collapsed",
        placeholder="Paste the job description here to run a Resume vs. Job Description match...",
    )

run_clicked = st.button("🔍 Run scan", type="primary", use_container_width=False)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _handle_upload_and_analysis() -> None:
    if uploaded_file is None:
        st.warning("Please upload a PDF resume first.")
        return

    file_bytes = uploaded_file.getvalue()
    validation = validate_upload(uploaded_file.name, len(file_bytes))
    if not validation.is_valid:
        st.error(validation.message)
        return

    # Parse PDF only if this is a new file (avoid duplicate extraction).
    needs_parse = (
        st.session_state.parsed_filename != uploaded_file.name
        or st.session_state.parsed_text is None
    )
    if needs_parse:
        with st.spinner("Extracting resume text..."):
            try:
                parsed = parse_resume_pdf(file_bytes)
            except PDFParsingError as exc:
                st.error(str(exc))
                return
        st.session_state.parsed_text = parsed.text
        st.session_state.parsed_filename = uploaded_file.name
        st.session_state.analysis = None  # Invalidate any prior analysis.
        st.session_state.jd_match = None

    if not settings.has_valid_api_key:
        st.error(
            "AI analysis is not configured. Please set GEMINI_API_KEY in your "
            "environment and restart the app."
        )
        return

    with st.spinner("Running full resume scan — ATS, skills, and hiring signals..."):
        try:
            st.session_state.analysis = analyze_resume(st.session_state.parsed_text)
        except AnalyzerError as exc:
            st.error(str(exc))
            return

    jd_text = st.session_state.job_description.strip()
    if jd_text:
        with st.spinner("Matching resume against job description..."):
            try:
                st.session_state.jd_match = match_resume_to_job(
                    st.session_state.parsed_text, jd_text
                )
            except AnalyzerError as exc:
                st.warning(f"Resume analysis succeeded, but JD matching failed: {exc}")
                st.session_state.jd_match = None
    else:
        st.session_state.jd_match = None


if run_clicked:
    try:
        _handle_upload_and_analysis()
    except Exception:  # noqa: BLE001 - top-level safety net, never crash the app
        logger.exception("Unhandled error during scan")
        st.error(
            "An unexpected error occurred while processing your resume. "
            "Please try again, and contact support if the issue persists."
        )

# ---------------------------------------------------------------------------
# Results dashboard
# ---------------------------------------------------------------------------

if st.session_state.analysis is not None:
    word_count = count_words(st.session_state.parsed_text)
    reading_time = estimate_reading_time_minutes(word_count)

    analysis_view.render_full_dashboard(
        st,
        st.session_state.analysis,
        word_count,
        reading_time,
        st.session_state.jd_match,
    )

    st.markdown('<div class="riq-section-label">Export</div>', unsafe_allow_html=True)
    try:
        pdf_bytes = generate_pdf_report(
            st.session_state.analysis,
            candidate_label=st.session_state.parsed_filename or "Candidate",
            jd_match=st.session_state.jd_match,
        )
        st.download_button(
            "⬇️ Download full report (PDF)",
            data=pdf_bytes,
            file_name="ResumeIQ_Analysis_Report.pdf",
            mime="application/pdf",
        )
    except Exception:  # noqa: BLE001
        logger.exception("PDF report generation failed")
        st.warning("We couldn't generate the downloadable report this time. Your results above are unaffected.")
else:
    st.info("Upload a resume and click **Run scan** to see your results here.")
