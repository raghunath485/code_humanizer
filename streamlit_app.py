"""
Code Humanizer — Streamlit Frontend
A premium, dark-themed UI for the Code Humanizer service.
"""

import streamlit as st

from app_backend.humanizer_engine import humanize, HumanizeOptions
from app_backend.converter_engine import convert_code
from app_backend.concept_engine import build_concept_plan
from app_backend.career_engine import build_career_pack
from app_backend.quality_engine import score_quality
from app_backend.security_engine import analyze_security
from app_backend.schemas import HumanizeOptions as _HumanizeOpts


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Code Humanizer",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }

    .sub-header {
        text-align: center;
        color: #9ca3af;
        font-size: 1.05rem;
        margin-bottom: 2rem;
    }

    .metric-card {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        border: 1px solid #3b3b5c;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        color: #e2e8f0;
        font-size: 1.6rem;
        font-weight: 700;
    }

    .insight-card {
        background: #1a1a2e;
        border-left: 4px solid #667eea;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.2rem;
        margin-bottom: 0.6rem;
    }
    .insight-title {
        color: #a78bfa;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 0.3rem;
    }
    .insight-body {
        color: #d1d5db;
        font-size: 0.88rem;
        line-height: 1.5;
    }

    .badge {
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 0.4rem;
        margin-bottom: 0.3rem;
    }
    .badge-green  { background: #065f46; color: #6ee7b7; }
    .badge-yellow { background: #78350f; color: #fcd34d; }
    .badge-red    { background: #7f1d1d; color: #fca5a5; }
    .badge-blue   { background: #1e3a5f; color: #93c5fd; }

    div[data-testid="stTabs"] button {
        font-weight: 600;
        font-size: 1rem;
    }

    .stCodeBlock {
        border-radius: 10px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Header ───────────────────────────────────────────────────────────────────

st.markdown('<p class="main-header">✨ Code Humanizer</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Transform, analyze, and understand your code — powered by intelligent heuristics</p>',
    unsafe_allow_html=True,
)


# ── Helper renderers ────────────────────────────────────────────────────────

def render_metric(label: str, value: str):
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_insight(title: str, body: str):
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">{title}</div>'
        f'<div class="insight-body">{body}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def badge(text: str, variant: str = "blue"):
    return f'<span class="badge badge-{variant}">{text}</span>'


def risk_badge(level: str):
    colors = {"Low": "green", "Medium": "yellow", "High": "red"}
    return badge(level, colors.get(level, "blue"))


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Options")

    st.markdown("**Humanizer**")
    rename = st.checkbox("Rename identifiers", value=True)
    docstrings = st.checkbox("Add docstrings", value=True)
    spacing = st.checkbox("Normalize spacing", value=True)
    summary_comment = st.checkbox("Add summary comment", value=True)
    complexity = st.checkbox("Explain complexity", value=True)
    dead_code = st.checkbox("Detect dead code", value=True)

    st.divider()
    lang_hint = st.selectbox("Language hint", ["auto", "python", "javascript", "java", "c", "cpp"])
    profile = st.selectbox("Target profile", ["developer_friendly", "production", "educational"])
    refactor_mode = st.selectbox("Refactor mode", ["intermediate", "beginner", "professional"])

    concept_options = ["functions", "loops", "oop", "async", "api", "error_handling"]
    concepts = st.multiselect("Concept preferences", concept_options)

    st.divider()
    st.markdown(
        '<p style="color:#6b7280;font-size:0.75rem;text-align:center;">'
        'Code Humanizer v2 · Built with Streamlit</p>',
        unsafe_allow_html=True,
    )


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_humanize, tab_convert, tab_career = st.tabs(["🔧 Humanize", "🔄 Convert", "💼 Career Assistant"])

# ── Tab 1: Humanize ──────────────────────────────────────────────────────────

with tab_humanize:
    code_input = st.text_area(
        "Paste your code below",
        height=260,
        placeholder="def calc_resp(usr_msg, ctx):\n    ...",
        key="humanize_input",
    )

    if st.button("✨ Humanize", type="primary", use_container_width=True, key="btn_humanize"):
        if not code_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Humanizing your code…"):
                options = HumanizeOptions(
                    add_summary_comment=summary_comment,
                    rename_identifiers=rename,
                    normalize_spacing=spacing,
                    language_hint=lang_hint,
                    target_profile=profile,
                    add_docstrings=docstrings,
                    explain_complexity=complexity,
                    detect_dead_code=dead_code,
                    concept_preferences=concepts,
                    refactor_mode=refactor_mode,
                )
                result = humanize(code_input, options)

            # ── Metrics row ──
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                render_metric("Language", result.get("language", "—").title())
            with m2:
                comp = result.get("complexity", {})
                render_metric("Complexity", comp.get("level", "—") if comp else "—")
            with m3:
                q = result.get("quality", {})
                render_metric("Quality", f"{q.get('overall', '—')}/100")
            with m4:
                sec = result.get("security", {})
                render_metric("Security", sec.get("risk_level", "—"))

            # ── Humanized code ──
            st.markdown("#### 📝 Humanized Code")
            st.code(result.get("code", ""), language=result.get("language", "python"))

            # ── Insights ──
            st.markdown("#### 💡 Insights")
            for card in result.get("insights", []):
                render_insight(card["title"], card["body"])

            # ── Chatbot signals ──
            signals = result.get("chatbot_signals", [])
            if signals:
                st.markdown("#### 🤖 Chatbot Signals")
                st.markdown(" ".join(badge(s, "blue") for s in signals), unsafe_allow_html=True)

            # ── Dead code ──
            dc = result.get("dead_code", [])
            if dc:
                st.markdown("#### 🗑️ Dead Code Findings")
                for finding in dc:
                    st.markdown(f"- {finding}")

            # ── Security findings ──
            sec_findings = result.get("security", {}).get("findings", [])
            if sec_findings:
                st.markdown("#### 🔒 Security Findings")
                for f in sec_findings:
                    st.markdown(
                        f"- **{f.get('rule', '')}** — {f.get('message', '')} "
                        f"(severity: {f.get('severity', 'info')})"
                    )

# ── Tab 2: Convert ───────────────────────────────────────────────────────────

with tab_convert:
    col_src, col_tgt = st.columns(2)
    with col_src:
        src_lang = st.selectbox("Source language", ["auto", "python", "javascript", "java", "c", "cpp"], key="src_lang")
    with col_tgt:
        tgt_lang = st.selectbox("Target language", ["python", "javascript", "java", "c", "cpp"], key="tgt_lang")

    convert_input = st.text_area(
        "Code to convert",
        height=220,
        placeholder="public static void main(String[] args) { ... }",
        key="convert_input",
    )

    if st.button("🔄 Convert", type="primary", use_container_width=True, key="btn_convert"):
        if not convert_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Converting…"):
                plan = build_concept_plan(concepts)
                conv = convert_code(convert_input, src_lang, tgt_lang, plan, refactor_mode)

            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                render_metric("Confidence", f"{conv.get('confidence_score', 0)}%")
            with c2:
                render_metric("Direction", f"{conv.get('source_language', '?')} → {conv.get('target_language', '?')}")

            st.markdown("#### 📝 Converted Code")
            st.code(conv.get("converted_code", ""), language=tgt_lang)

            warns = conv.get("warnings", [])
            if warns:
                st.markdown("#### ⚠️ Warnings")
                for w in warns:
                    st.markdown(f"- {w}")

# ── Tab 3: Career Assistant ──────────────────────────────────────────────────

with tab_career:
    career_input = st.text_area(
        "Paste code to generate career material from",
        height=220,
        placeholder="# Paste your project code here…",
        key="career_input",
    )

    if st.button("💼 Generate Career Pack", type="primary", use_container_width=True, key="btn_career"):
        if not career_input.strip():
            st.warning("Please paste some code first.")
        else:
            with st.spinner("Generating career materials…"):
                from app_backend.humanizer_engine import calculate_complexity, detect_dead_code
                sec = analyze_security(career_input)
                comp = calculate_complexity(career_input)
                dc = detect_dead_code(career_input)
                qual = score_quality(career_input, comp, dc, sec["findings"])
                pack = build_career_pack(career_input, lang_hint, qual, sec)

            st.markdown("---")

            st.markdown("#### 📋 Project Summary")
            st.info(pack.get("project_summary", ""))

            st.markdown("#### 🎯 Resume Bullet Points")
            for point in pack.get("resume_bullet_points", []):
                st.markdown(f"- {point}")

            st.markdown("#### 🔬 Technical Highlights")
            for h in pack.get("technical_highlights", []):
                st.markdown(f"- {h}")

            st.markdown("#### 🎤 Interview Questions & Answers")
            questions = pack.get("interview_questions", [])
            answers = pack.get("interview_answers", [])
            for q, a in zip(questions, answers):
                with st.expander(f"❓ {q}"):
                    st.markdown(a)

            st.markdown("#### 📊 Complexity Explanation")
            st.markdown(pack.get("complexity_explanation", ""))
