import streamlit as st

from src.agents.log_type_detector import run as detect_log_type
from src.agents.segmenter_cluster import run as segment_logs
from src.agents.root_cause_analyst import run as analyze_root_cause
from src.agents.fix_recommender import run as recommend_fixes
from src.agents.knowledge_memory_agent import store_incident, find_similar

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="LogPilot – AI Log Incident Analyzer",
    layout="wide",
)

# =========================
# GLOBAL STYLES (NETFLIX THEME)
# =========================
st.markdown(
    """
    <style>
    /* Remove default padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }

    /* App background */
    .stApp {
        background: radial-gradient(circle at top, #111827 0, #020617 40%, #020617 100%);
        color: #e5e7eb;
        font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    /* Top navbar */
    .lp-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.25rem 0 0.75rem 0;
        border-bottom: 1px solid #1f2933;
        margin-bottom: 1.25rem;
    }
    .lp-logo {
        font-size: 1.5rem;
        font-weight: 900;
        letter-spacing: 0.08em;
        color: #ef4444;
    }
    .lp-nav-links {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #9ca3af;
    }
    .lp-nav-links span {
        margin-left: 1.5rem;
        cursor: default;
    }

    /* Hero section */
    .lp-hero {
        border-radius: 18px;
        padding: 1.75rem 2rem 1.5rem 2rem;
        background: radial-gradient(circle at top left, #7f1d1d 0, #111827 40%, #020617 100%);
        border: 1px solid rgba(248,113,113,0.18);
        box-shadow: 0 30px 80px rgba(0,0,0,0.75);
        margin-bottom: 1.75rem;
    }
    .lp-hero-eyebrow {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        color: #f97373;
        margin-bottom: 0.4rem;
    }
    .lp-hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.6rem;
    }
    .lp-hero-title span {
        color: #ef4444;
    }
    .lp-hero-subtitle {
        font-size: 0.95rem;
        color: #e5e7eb;
        max-width: 780px;
        line-height: 1.6;
        margin-bottom: 1rem;
    }
    .lp-tag-row {
        margin-top: 0.3rem;
    }
    .lp-tag {
        display: inline-flex;
        align-items: center;
        font-size: 0.78rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        border: 1px solid rgba(248,250,252,0.12);
        background: rgba(15,23,42,0.7);
        margin-right: 0.45rem;
        margin-bottom: 0.35rem;
        color: #e5e7eb;
    }

    /* Step heading */
    .lp-step-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
    }
    .lp-step-caption {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-bottom: 0.9rem;
    }

    /* Input cards */
    .lp-card {
        border-radius: 14px;
        padding: 1rem 1.1rem;
        background: linear-gradient(145deg, rgba(15,23,42,0.95), rgba(15,23,42,0.92));
        border: 1px solid rgba(148,163,184,0.35);
        box-shadow: 0 20px 60px rgba(15,23,42,0.85);
    }
    .lp-card-header {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .lp-card-sub {
        font-size: 0.8rem;
        color: #9ca3af;
        margin-bottom: 0.6rem;
    }

    /* Metrics row */
    .lp-metric-card {
        border-radius: 14px;
        padding: 0.9rem 1rem;
        background: linear-gradient(145deg, #020617, #020617);
        border: 1px solid rgba(75,85,99,0.9);
    }
    .lp-metric-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #9ca3af;
        margin-bottom: 0.2rem;
    }
    .lp-metric-value {
        font-size: 1.35rem;
        font-weight: 700;
        color: #f9fafb;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.4rem;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding-top: 0.25rem;
        padding-bottom: 0.25rem;
        padding-left: 1rem;
        padding-right: 1rem;
        background-color: #020617;
        border: 1px solid #374151;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #ef4444, #f97316);
        border-color: #f97316 !important;
        color: white !important;
    }

    /* Primary button */
    .stButton>button {
        border-radius: 999px;
        border: none;
        background: linear-gradient(135deg, #ef4444, #f97316);
        color: white;
        font-weight: 600;
        padding-top: 0.55rem;
        padding-bottom: 0.55rem;
        box-shadow: 0 12px 30px rgba(239,68,68,0.45);
    }
    .stButton>button:hover {
        opacity: 0.96;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# NAVBAR
# =========================
st.markdown(
    """
    <div class="lp-nav">
        <div class="lp-logo">LOGPILOT</div>
        <div class="lp-nav-links">
            <span>LOG ANALYTICS</span>
            <span>RCA</span>
            <span>DEVOPS COPILOT</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# HERO SECTION
# =========================
st.markdown(
    """
    <div class="lp-hero">
        <div class="lp-hero-eyebrow">AI INCIDENT ANALYSIS FOR ENGINEERING TEAMS</div>
        <div class="lp-hero-title"><span>LogPilot</span> – AI Log Incident Analyzer</div>
        <div class="lp-hero-subtitle">
            Drop in your application or infrastructure logs and get a Netflix-style incident report:
            detected log type, severity breakdown, segmented errors, root-cause explanation, and
            production-ready remediation steps powered by multi-agent reasoning.
        </div>
        <div class="lp-tag-row">
            <span class="lp-tag">Multi-agent LLM pipeline</span>
            <span class="lp-tag">Root cause analysis</span>
            <span class="lp-tag">Quick & long-term fixes</span>
            <span class="lp-tag">Memory of past incidents</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# STEP 1: INPUT AREA (SIDE-BY-SIDE)
# =========================
st.markdown('<div class="lp-step-title">Step 1 • Provide your logs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lp-step-caption">Upload a .log/.txt file or paste raw log text into LogPilot.</div>',
    unsafe_allow_html=True,
)

left_col, right_col = st.columns([1, 1.25])

with left_col:
    st.markdown('<div class="lp-card">', unsafe_allow_html=True)
    st.markdown('<div class="lp-card-header">📁 Upload log file</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lp-card-sub">Best for real application or infrastructure log exports.</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Upload .log or .txt",
        type=["log", "txt"],
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="lp-card">', unsafe_allow_html=True)
    st.markdown('<div class="lp-card-header">📝 Paste log text</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="lp-card-sub">Copy–paste a log snippet directly from your terminal or console.</div>',
        unsafe_allow_html=True,
    )
    pasted_text = st.text_area(
        label="Paste logs here",
        label_visibility="collapsed",
        height=220,
        placeholder="Paste logs here…",
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")
analyze_clicked = st.button("Analyze logs", use_container_width=True)

# =========================
# BACKEND + RESULTS
# =========================
log_text = None
if uploaded_file is not None:
    log_text = uploaded_file.read().decode("utf-8", errors="ignore")
if pasted_text and pasted_text.strip():
    # Pasted text wins if both are provided
    log_text = pasted_text

if analyze_clicked:
    if not log_text:
        st.error("Please upload a log file or paste log text before analyzing.")
    else:
        with st.spinner("Analyzing logs with LogPilot agents…"):
            # ----- Agent calls -----
            lt_result = detect_log_type(log_text)
            seg_result = segment_logs(log_text)
            rc_result = analyze_root_cause(
                log_type=lt_result.log_type,
                segments=seg_result.segments,
                error_samples=seg_result.error_samples,
            )
            fix_result = recommend_fixes(
                log_type=lt_result.log_type,
                primary_root_cause=rc_result.primary_root_cause,
                symptoms=rc_result.symptoms,
            )

            # Prepare example data for memory
            example_error = seg_result.error_samples[0] if seg_result.error_samples else ""
            first_quick = fix_result.quick_fixes[0] if fix_result.quick_fixes else ""
            first_long = fix_result.long_term_fixes[0] if fix_result.long_term_fixes else ""

            store_incident(
                log_type=lt_result.log_type,
                primary_root_cause=rc_result.primary_root_cause,
                example_error=example_error,
                quick_fix=first_quick,
                long_term_fix=first_long,
            )

        # =========================
        # METRICS ROW
        # =========================
        st.markdown("### Step 2 • Review the incident breakdown")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown('<div class="lp-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="lp-metric-label">Log type</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="lp-metric-value">{lt_result.log_type}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with m2:
            total_errors = len(seg_result.error_samples)
            st.markdown('<div class="lp-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="lp-metric-label">Detected errors</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="lp-metric-value">{total_errors}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with m3:
            conf_display = rc_result.confidence if rc_result.confidence is not None else "N/A"
            st.markdown('<div class="lp-metric-card">', unsafe_allow_html=True)
            st.markdown('<div class="lp-metric-label">Model confidence</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="lp-metric-value">{conf_display}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")

        # =========================
        # TABS: RCA / SEGMENTS / FIXES / MEMORY
        # =========================
        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Log type & severity",
                "Segments & error samples",
                "Root cause analysis",
                "Fixes & memory",
            ]
        )

        # ---- TAB 1 ----
        with tab1:
            st.subheader("Log type & severity")
            st.write("**Detected log type:**", lt_result.log_type)
            if lt_result.severity_summary:
                st.write("**Severity estimate:**")
                st.json(lt_result.severity_summary)
            if lt_result.notes:
                st.caption("Classifier notes:")
                st.code(lt_result.notes)

        # ---- TAB 2 ----
        with tab2:
            st.subheader("Segments & error samples")
            st.write("**Segments found:**", [s.id for s in seg_result.segments])

            for seg in seg_result.segments:
                with st.expander(f"Segment `{seg.id}` – {seg.summary}"):
                    sample = "\n".join(seg.sample_lines[:25])
                    st.code(sample or "(no sample lines)")

            st.markdown("**Error samples (up to 10):**")
            if seg_result.error_samples:
                st.code("\n".join(seg_result.error_samples))
            else:
                st.info("No obvious error lines found.")

        # ---- TAB 3 ----
        with tab3:
            st.subheader("Root cause analysis")
            st.markdown("**Primary root cause:**")
            st.info(rc_result.primary_root_cause)

            if rc_result.symptoms:
                st.markdown("**Symptoms observed:**")
                for s in rc_result.symptoms:
                    st.markdown(f"- {s}")

            if rc_result.confidence is not None:
                st.markdown(f"**Model confidence:** `{rc_result.confidence}`")

        # ---- TAB 4 ----
        with tab4:
            st.subheader("Fix recommendations & memory lookup")

            similar = find_similar(
                log_type=lt_result.log_type,
                primary_root_cause=rc_result.primary_root_cause,
            )
            if similar:
                st.success("Similar past incident found in memory.")
                st.write("**Past root cause:**", similar.primary_root_cause)
                st.write("**Past quick fix:**", similar.quick_fix)
                st.write("**Past long-term fix:**", similar.long_term_fix)
            else:
                st.warning("No similar past incident found in memory yet for this pattern.")

            st.markdown("---")
            st.markdown("#### Quick fixes")
            if fix_result.quick_fixes:
                for q in fix_result.quick_fixes:
                    st.markdown(f"- {q}")
            else:
                st.write("_No quick fixes parsed._")

            st.markdown("#### Long-term prevention")
            if fix_result.long_term_fixes:
                for item in fix_result.long_term_fixes:
                    st.markdown(f"- {item}")
            else:
                st.write("_No long-term fixes parsed._")

        st.success("Analysis complete and incident stored in memory.")

else:
    st.info("Upload a log file or paste log text above, then click **Analyze logs** to generate your incident report.")
