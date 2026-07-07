"""
report_generator.py
--------------------
Builds a downloadable, professionally formatted PDF report from a
completed ResumeAnalysis (and optionally a JDMatchResult). Uses ReportLab
directly rather than a templating shortcut so we have full control over
layout, charts, headers/footers, and page numbering.
"""

from __future__ import annotations

import io
from datetime import datetime

from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from analyzer import JDMatchResult, ResumeAnalysis
from config import settings
from utils import get_logger

logger = get_logger(__name__)

INK = colors.HexColor("#0F1B33")
INDIGO = colors.HexColor("#1E3A5F")
TEAL = colors.HexColor("#12A594")
AMBER = colors.HexColor("#E8A33D")
MUTED = colors.HexColor("#5B6B82")
LINE = colors.HexColor("#DDE3EC")


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"], textColor=INK, fontSize=22, spaceAfter=4
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle", parent=base["Normal"], textColor=MUTED, fontSize=10, spaceAfter=18
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], textColor=INDIGO, fontSize=13.5,
            spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["Normal"], fontSize=9.7, leading=14, textColor=INK
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["Normal"], fontSize=9.7, leading=13.5, textColor=INK
        ),
    }


def _score_pie(label: str, value: int, color: colors.Color) -> Drawing:
    """Small donut-style score chart used in the PDF, matching the app's gauge motif."""
    drawing = Drawing(150, 130)
    pie = Pie()
    pie.x, pie.y = 25, 20
    pie.width, pie.height = 90, 90
    pie.data = [value, max(0, 100 - value)]
    pie.labels = None
    pie.slices.strokeWidth = 0
    pie.slices[0].fillColor = color
    pie.slices[1].fillColor = colors.HexColor("#EDF0F5")
    drawing.add(pie)
    drawing.add(String(70, 65, f"{value}", fontSize=14, fillColor=INK, textAnchor="middle"))
    drawing.add(String(75, 5, label, fontSize=7.5, fillColor=MUTED, textAnchor="middle"))
    return drawing


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.line(0.75 * inch, 0.65 * inch, LETTER[0] - 0.75 * inch, 0.65 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(
        0.75 * inch, 0.48 * inch,
        f"{settings.app_name} \u2014 Confidential candidate report"
    )
    canvas.drawRightString(
        LETTER[0] - 0.75 * inch, 0.48 * inch, f"Page {doc.page}"
    )
    canvas.restoreState()


def _bullets(items: list[str], style: ParagraphStyle) -> ListFlowable:
    return ListFlowable(
        [ListItem(Paragraph(item, style), bulletColor=INDIGO) for item in items] or
        [ListItem(Paragraph("Not enough information available.", style))],
        bulletType="bullet",
        start="\u2022",
        leftIndent=14,
    )


def generate_pdf_report(
    analysis: ResumeAnalysis,
    candidate_label: str = "Candidate",
    jd_match: JDMatchResult | None = None,
) -> bytes:
    """Render a full PDF report and return its bytes for download."""
    buffer = io.BytesIO()
    doc = BaseDocTemplate(buffer, pagesize=LETTER,
                           leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                           topMargin=0.75 * inch, bottomMargin=0.9 * inch)
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=_footer)])

    s = _styles()
    story = []

    story.append(Paragraph(settings.app_name, s["title"]))
    story.append(Paragraph(
        f"Resume Analysis Report &mdash; {candidate_label} &mdash; "
        f"generated {datetime.now().strftime('%B %d, %Y')}",
        s["subtitle"],
    ))

    # --- Score charts row -------------------------------------------------
    chart_row = [
        _score_pie("ATS Score", analysis.ats_score, TEAL),
        _score_pie("AI Confidence", analysis.ai_confidence_score, AMBER),
    ]
    if jd_match is not None:
        chart_row.append(_score_pie("JD Match", jd_match.match_score, INDIGO))
    story.append(Table([chart_row], colWidths=[170] * len(chart_row)))

    story.append(Paragraph("Executive Summary", s["h2"]))
    story.append(Paragraph(analysis.summary, s["body"]))

    story.append(Paragraph("Strengths", s["h2"]))
    story.append(_bullets(analysis.strengths, s["bullet"]))

    story.append(Paragraph("Weaknesses", s["h2"]))
    story.append(_bullets(analysis.weaknesses, s["bullet"]))

    story.append(Paragraph("Technical Skills", s["h2"]))
    story.append(Paragraph(", ".join(analysis.technical_skills) or "Not enough information available.", s["body"]))

    story.append(Paragraph("Soft Skills", s["h2"]))
    story.append(Paragraph(", ".join(analysis.soft_skills) or "Not enough information available.", s["body"]))

    story.append(Paragraph("Missing Skills", s["h2"]))
    story.append(Paragraph(", ".join(analysis.missing_skills) or "Not enough information available.", s["body"]))

    story.append(Paragraph("Keyword Analysis", s["h2"]))
    story.append(Paragraph(analysis.keyword_analysis, s["body"]))

    story.append(Paragraph("Experience Analysis", s["h2"]))
    story.append(Paragraph(analysis.experience_analysis, s["body"]))

    story.append(Paragraph("Project Quality Analysis", s["h2"]))
    story.append(Paragraph(analysis.project_quality_analysis, s["body"]))

    story.append(Paragraph("Education Review", s["h2"]))
    story.append(Paragraph(analysis.education_review, s["body"]))

    story.append(Paragraph("Grammar Review", s["h2"]))
    story.append(Paragraph(analysis.grammar_review, s["body"]))

    story.append(Paragraph("Formatting Review", s["h2"]))
    story.append(Paragraph(analysis.formatting_review, s["body"]))

    story.append(Paragraph("Recommended Improvements", s["h2"]))
    story.append(_bullets(analysis.improvements, s["bullet"]))

    story.append(Paragraph("Recommended Job Roles", s["h2"]))
    story.append(Paragraph(", ".join(analysis.recommended_job_roles) or "Not enough information available.", s["body"]))

    story.append(Paragraph("Learning Roadmap", s["h2"]))
    story.append(_bullets(analysis.learning_roadmap, s["bullet"]))

    story.append(Paragraph("Likely Interview Questions", s["h2"]))
    story.append(_bullets(analysis.interview_questions, s["bullet"]))

    story.append(Paragraph("Hiring Recommendation", s["h2"]))
    story.append(Paragraph(analysis.hiring_recommendation, s["body"]))

    if jd_match is not None:
        story.append(Paragraph("Resume vs. Job Description Match", s["h2"]))
        story.append(Paragraph(
            f"ATS pass-through probability for this job: {jd_match.ats_probability}%", s["body"]
        ))
        story.append(Spacer(1, 4))
        story.append(Paragraph("Matching Skills", s["body"]))
        story.append(Paragraph(", ".join(jd_match.matching_skills) or "Not enough information available.", s["body"]))
        story.append(Paragraph("Missing Skills", s["body"]))
        story.append(Paragraph(", ".join(jd_match.missing_skills) or "Not enough information available.", s["body"]))
        story.append(Paragraph("Missing Keywords", s["body"]))
        story.append(Paragraph(", ".join(jd_match.missing_keywords) or "Not enough information available.", s["body"]))
        story.append(Paragraph("Recommended Changes", s["h2"]))
        story.append(_bullets(jd_match.recommended_changes, s["bullet"]))

    doc.build(story)
    logger.info("Generated PDF report (%d bytes)", buffer.tell())
    return buffer.getvalue()
