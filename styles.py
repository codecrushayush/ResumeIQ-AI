"""
styles.py
---------
Design tokens and custom CSS for ResumeIQ AI's "diagnostic scan" visual
language: the product frames resume analysis as a scan/read-out, with a
recurring circular gauge motif for scores (ATS Score, Match Score, AI
Confidence) instead of generic progress bars.

Token system:
  Color   -- ink navy / deep indigo / signal teal / amber flag / paper / slate line
  Type    -- Space Grotesk (display), Inter (body), JetBrains Mono (data/scores)
  Layout  -- fixed dark sidebar "control panel" + light "scan surface" canvas
  Signature -- conic-gradient scan-ring gauges shared across every score
"""

from __future__ import annotations

# --- Design tokens ---------------------------------------------------------

COLOR_INK = "#0F1B33"
COLOR_INDIGO = "#1E3A5F"
COLOR_INDIGO_LIGHT = "#2C5282"
COLOR_TEAL = "#12A594"
COLOR_TEAL_SOFT = "#E3F7F4"
COLOR_AMBER = "#E8A33D"
COLOR_AMBER_SOFT = "#FCF0DD"
COLOR_RED = "#D64545"
COLOR_RED_SOFT = "#FBE7E7"
COLOR_PAPER = "#F6F7F9"
COLOR_SURFACE = "#FFFFFF"
COLOR_SLATE_LINE = "#DDE3EC"
COLOR_TEXT_MUTED = "#5B6B82"

FONT_DISPLAY = "'Space Grotesk', sans-serif"
FONT_BODY = "'Inter', sans-serif"
FONT_MONO = "'JetBrains Mono', monospace"

CUSTOM_CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">

<style>
    :root {{
        --ink: {COLOR_INK};
        --indigo: {COLOR_INDIGO};
        --indigo-light: {COLOR_INDIGO_LIGHT};
        --teal: {COLOR_TEAL};
        --teal-soft: {COLOR_TEAL_SOFT};
        --amber: {COLOR_AMBER};
        --amber-soft: {COLOR_AMBER_SOFT};
        --red: {COLOR_RED};
        --red-soft: {COLOR_RED_SOFT};
        --paper: {COLOR_PAPER};
        --surface: {COLOR_SURFACE};
        --line: {COLOR_SLATE_LINE};
        --muted: {COLOR_TEXT_MUTED};
    }}

    html, body, [class*="css"] {{
        font-family: {FONT_BODY};
        color: var(--ink);
    }}

    .stApp {{
        background: var(--paper);
    }}

    h1, h2, h3, h4 {{
        font-family: {FONT_DISPLAY} !important;
        letter-spacing: -0.01em;
        color: var(--ink);
    }}

    /* ---- Sidebar: control panel ---------------------------------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--ink) 0%, #142440 100%);
    }}
    section[data-testid="stSidebar"] * {{
        color: #EAF0FA !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.12);
    }}

    /* ---- Hero -------------------------------------------------------- */
    .riq-hero {{
        background: linear-gradient(120deg, var(--indigo) 0%, var(--ink) 100%);
        border-radius: 20px;
        padding: 2.75rem 3rem;
        margin-bottom: 1.75rem;
        position: relative;
        overflow: hidden;
    }}
    .riq-hero::after {{
        content: "";
        position: absolute;
        top: -60px; right: -60px;
        width: 260px; height: 260px;
        border-radius: 50%;
        border: 2px solid rgba(18,165,148,0.35);
    }}
    .riq-hero::before {{
        content: "";
        position: absolute;
        top: -20px; right: -20px;
        width: 180px; height: 180px;
        border-radius: 50%;
        border: 2px solid rgba(18,165,148,0.25);
    }}
    .riq-hero-eyebrow {{
        font-family: {FONT_MONO};
        font-size: 0.75rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--teal);
        margin-bottom: 0.6rem;
    }}
    .riq-hero h1 {{
        color: #FFFFFF !important;
        font-size: 2.4rem;
        margin: 0 0 0.5rem 0;
    }}
    .riq-hero p {{
        color: #C6D3E8;
        font-size: 1.02rem;
        max-width: 620px;
        margin: 0;
    }}

    /* ---- Cards --------------------------------------------------- */
    .riq-card {{
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 1.5rem 1.6rem;
        box-shadow: 0 1px 2px rgba(15,27,51,0.04), 0 8px 24px rgba(15,27,51,0.04);
        margin-bottom: 1.1rem;
    }}
    .riq-card h4 {{
        margin-top: 0;
        font-size: 1.05rem;
    }}
    .riq-card-label {{
        font-family: {FONT_MONO};
        font-size: 0.72rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }}

    /* ---- Signature element: scan-ring gauge ----------------------- */
    .riq-gauge-wrap {{
        display: flex;
        align-items: center;
        gap: 1.1rem;
    }}
    .riq-gauge {{
        position: relative;
        width: 92px;
        height: 92px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }}
    .riq-gauge-inner {{
        position: absolute;
        inset: 8px;
        background: var(--surface);
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}
    .riq-gauge-value {{
        font-family: {FONT_MONO};
        font-weight: 600;
        font-size: 1.3rem;
        line-height: 1;
        color: var(--ink);
    }}
    .riq-gauge-max {{
        font-family: {FONT_MONO};
        font-size: 0.6rem;
        color: var(--muted);
    }}
    .riq-gauge-title {{
        font-family: {FONT_DISPLAY};
        font-weight: 600;
        font-size: 0.95rem;
        color: var(--ink);
        margin: 0 0 0.15rem 0;
    }}
    .riq-gauge-sub {{
        font-size: 0.82rem;
        color: var(--muted);
        margin: 0;
    }}

    /* ---- Status badges --------------------------------------------- */
    .riq-badge {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        font-family: {FONT_MONO};
        font-size: 0.72rem;
        letter-spacing: 0.04em;
        font-weight: 600;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
    }}
    .riq-badge-good {{ background: var(--teal-soft); color: #0B7A6E; }}
    .riq-badge-warn {{ background: var(--amber-soft); color: #966017; }}
    .riq-badge-bad  {{ background: var(--red-soft); color: #A93131; }}
    .riq-badge-dot {{ width: 6px; height: 6px; border-radius: 50%; background: currentColor; }}

    /* ---- Pill list items -------------------------------------------- */
    .riq-pill {{
        display: inline-block;
        font-size: 0.82rem;
        padding: 0.28rem 0.7rem;
        border-radius: 8px;
        margin: 0 0.35rem 0.35rem 0;
        background: var(--paper);
        border: 1px solid var(--line);
        color: var(--ink);
    }}
    .riq-pill-missing {{
        background: var(--amber-soft);
        border-color: rgba(232,163,61,0.35);
        color: #7A501C;
    }}
    .riq-pill-match {{
        background: var(--teal-soft);
        border-color: rgba(18,165,148,0.3);
        color: #0B7A6E;
    }}

    /* ---- Upload zone -------------------------------------------------- */
    [data-testid="stFileUploaderDropzone"] {{
        background: var(--surface);
        border: 1.5px dashed var(--line);
        border-radius: 16px;
    }}

    /* ---- Buttons -------------------------------------------------------- */
    .stButton > button, .stDownloadButton > button {{
        background: var(--indigo);
        color: #fff;
        border: none;
        border-radius: 10px;
        padding: 0.55rem 1.3rem;
        font-weight: 600;
        transition: background 0.15s ease;
    }}
    .stButton > button:hover, .stDownloadButton > button:hover {{
        background: var(--indigo-light);
        color: #fff;
    }}

    /* ---- Divider label ------------------------------------------------- */
    .riq-section-label {{
        font-family: {FONT_MONO};
        font-size: 0.75rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: var(--muted);
        border-bottom: 1px solid var(--line);
        padding-bottom: 0.5rem;
        margin: 1.8rem 0 1rem 0;
    }}
</style>
"""


def inject_custom_css(st) -> None:
    """Inject the global stylesheet. Called once per page render."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def _gauge_color(value: int) -> str:
    if value >= 75:
        return COLOR_TEAL
    if value >= 50:
        return COLOR_AMBER
    return COLOR_RED


def render_gauge_card(st, title: str, subtitle: str, value: int, max_value: int = 100) -> None:
    """Render the signature scan-ring gauge inside a card.

    Uses a conic-gradient div (no JS/canvas needed) so it renders reliably
    inside Streamlit's sandboxed markdown.
    """
    pct = max(0, min(100, round((value / max_value) * 100))) if max_value else 0
    color = _gauge_color(pct)
    html = f"""
    <div class="riq-card">
        <div class="riq-gauge-wrap">
            <div class="riq-gauge" style="background: conic-gradient({color} {pct}%, #EDF0F5 {pct}%);">
                <div class="riq-gauge-inner">
                    <span class="riq-gauge-value">{value}</span>
                    <span class="riq-gauge-max">/ {max_value}</span>
                </div>
            </div>
            <div>
                <p class="riq-gauge-title">{title}</p>
                <p class="riq-gauge-sub">{subtitle}</p>
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_badge(st, label: str, level: str = "good") -> None:
    """Render a status badge. level: 'good' | 'warn' | 'bad'."""
    css_class = {"good": "riq-badge-good", "warn": "riq-badge-warn", "bad": "riq-badge-bad"}.get(
        level, "riq-badge-good"
    )
    st.markdown(
        f'<span class="riq-badge {css_class}"><span class="riq-badge-dot"></span>{label}</span>',
        unsafe_allow_html=True,
    )


def render_pill_list(st, items: list[str], variant: str = "default") -> None:
    """Render a wrapped list of pill-style tags. variant: 'default' | 'missing' | 'match'."""
    css_class = {
        "default": "riq-pill",
        "missing": "riq-pill riq-pill-missing",
        "match": "riq-pill riq-pill-match",
    }.get(variant, "riq-pill")
    if not items:
        st.markdown('<span class="riq-gauge-sub">Not enough information available.</span>', unsafe_allow_html=True)
        return
    html = "".join(f'<span class="{css_class}">{item}</span>' for item in items)
    st.markdown(html, unsafe_allow_html=True)
