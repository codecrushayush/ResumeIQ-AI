# 🧠 ResumeIQ AI

**AI-powered resume intelligence** — instant ATS scoring, skills breakdown, and hiring-manager-level feedback, plus resume-vs-job-description matching. Built with Python, Streamlit, and the Google Gemini API.

> Upload a resume. Get a full diagnostic scan: ATS compatibility, strengths & weaknesses, missing skills, grammar and formatting review, a learning roadmap, likely interview questions, and a downloadable PDF report — all in one pass.

![ResumeIQ AI screenshot placeholder](assets/screenshot-hero.png)
![ResumeIQ AI dashboard placeholder](assets/screenshot-dashboard.png)

---

## ✨ Features

- **📄 PDF Resume Upload** — drag-and-drop, validated for type, size, and page count.
- **🎯 ATS Score** — likelihood of passing automated resume screening.
- **🧾 Resume Summary** — a concise, grounded executive summary.
- **✅ Strengths & ⚠️ Weaknesses** — concrete, resume-specific observations.
- **🛠️ Technical & 🤝 Soft Skills** — extracted directly from the resume text.
- **🚫 Missing Skills** — gaps relative to the candidate's apparent target roles.
- **🔑 Keyword Analysis** — which industry keywords are present vs. absent.
- **💼 Experience Analysis** · **🧩 Project Quality Analysis** · **🎓 Education Review**
- **✍️ Grammar Review** · **📐 Formatting Review**
- **🚀 Resume Improvements** — specific, actionable rewrites.
- **🧭 Recommended Job Roles** · **📚 Learning Roadmap** · **🗣️ Interview Questions**
- **📊 Hiring Recommendation** with an **AI Confidence Score**
- **📈 Word Count & Reading Time**
- **📥 Downloadable PDF Report** — charts, sections, footer, and page numbers.
- **🆚 Resume vs. Job Description Match** — match score, ATS probability, matching/missing skills and keywords, and tailored suggestions.

## 🏗️ Architecture

Clean, single-responsibility modules — no business logic in the UI layer, no UI code in the AI layer:

```
ResumeIQ-AI/
├── app.py                # Streamlit entrypoint: page orchestration & session state only
├── config.py              # Environment loading & app-wide settings (Settings dataclass)
├── analyzer.py             # All Gemini API calls, structured-output schemas, retries
├── pdf_parser.py           # PDF validation & text extraction (pdfplumber)
├── report_generator.py     # PDF report rendering (ReportLab)
├── analysis_view.py        # Streamlit rendering components (pure UI, no logic)
├── styles.py                # Design tokens, custom CSS, gauge/badge/pill components
├── utils.py                 # Logging, validation, text metrics — no side effects
├── prompts.py                # Prompt templates, isolated from API-calling code
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── assets/
└── tests/
    ├── test_utils.py
    ├── test_pdf_parser.py
    └── test_analyzer.py
```

**Data flow:** `app.py` → `pdf_parser.parse_resume_pdf()` → `analyzer.analyze_resume()` (single structured Gemini call, cached in session state) → `analysis_view.render_full_dashboard()` → optional `report_generator.generate_pdf_report()` for download.

Only one Gemini call is made per resume scan (plus one more only if a job description is provided) — results are cached in `st.session_state` so re-rendering the page never triggers duplicate API calls.

## 🎨 Design language

ResumeIQ AI frames resume analysis as a **diagnostic scan**: a dark "control panel" sidebar, a light "scan surface" canvas, and a recurring **scan-ring gauge** (a conic-gradient circular meter) used consistently for every score — ATS Score, AI Confidence, and JD Match Score — so the whole product reads as one coherent instrument rather than a stack of generic Streamlit widgets.

| Token | Value |
|---|---|
| Ink (text/dark surfaces) | `#0F1B33` |
| Indigo (brand/actions) | `#1E3A5F` |
| Signal Teal (positive scores) | `#12A594` |
| Amber (attention/gaps) | `#E8A33D` |
| Paper (background) | `#F6F7F9` |
| Display type | Space Grotesk |
| Body type | Inter |
| Data/mono type | JetBrains Mono |

## 🧰 Tech Stack

- **Python 3.11+**
- **Streamlit** — UI framework
- **google-genai** — official Google Gemini SDK (structured JSON output via `response_schema`)
- **pdfplumber** — PDF text extraction
- **Pydantic** — typed, validated AI response schemas
- **ReportLab** — PDF report generation
- **python-dotenv** — environment configuration
- **Pandas** — lightweight data handling

## 🚀 Installation

```bash
git clone https://github.com/<your-username>/ResumeIQ-AI.git
cd ResumeIQ-AI

python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your GEMINI_API_KEY
```

Get a free Gemini API key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

## ▶️ Running the app

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## ✅ Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Tests cover file validation, text metrics, PDF parsing (valid, corrupted, and empty/unreadable PDFs), and analyzer error handling (missing API key, invalid job description, schema validation) — all mocked to run offline without real API calls.

## 🔒 Security & Privacy

- Resumes are processed **in memory only** and are never written to disk or a database.
- Resume content is **never logged** — only metadata (file size, page count, elapsed time).
- Uploads are validated for file type, size, and page count before parsing.
- The Gemini API key is loaded from environment variables only and never exposed to the client or committed to source control (`.env` is git-ignored).
- All external failures (missing/invalid API key, network errors, timeouts, malformed PDFs) are caught and surfaced as friendly messages — the app is designed to never crash.

## 📁 Project Structure

See [Architecture](#-architecture) above.

## 🔭 Future Improvements

- Multi-resume batch analysis for recruiters
- Resume version history & diffing
- LinkedIn profile import
- Multi-language resume support
- Team/workspace accounts with shared scoring rubrics

## 📄 License

MIT — see `LICENSE` (add one appropriate for your use case before publishing).

---

Built as a portfolio project demonstrating production-quality AI application architecture: clean separation of concerns, typed & validated AI outputs, defensive error handling, and an original design system.
