import streamlit as st

from src.agents.log_type_detector import run as detect_log_type
from src.agents.segmenter_cluster import run as segment_logs
from src.agents.root_cause_analyst import run as analyze_root_cause
from src.agents.fix_recommender import run as recommend_fixes
from src.agents.knowledge_memory_agent import store_incident, find_similar

# ---------- PAGE CONFIG ---------- #
st.set_page_config(
    page_title="LogPilot – AI Log Incident Analyzer",
    layout="wide",
)

# ---------- CUSTOM CSS ---------- #
st.markdown(
    """
    <style>
    /* Global background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #020617 40%, #1e293b 100%);
        color: #e5e7eb;
    }
    /* Main title */
    .big-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #f97316);
        -webkit-background-clip: text;
        color: transparent;
        margin-bottom: 0.3rem;
    }
    .subtitle {
        font-size: 0.95rem;
        color: #9ca3af;
        margin-bottom: 1.5rem;
    }
    /* Card style */
    .card {
        border-radius: 14px;
        padding: 1rem 1.2rem;
        background: rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.25);
        box-shadow: 0 18px 45px rgba(15,23,42,0.75);
    }
    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #9ca3af;
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e5e7eb;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #020617;
        border-right: 1px solid #1f2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ---------- #
st.markdown('<div class="big-title">🛠️ LogPilot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">AI co-pilot for logs: detects issues, finds root causes, '
    'recommends fixes, and learns from past incidents.</div>',
    unsafe_allow_html=True,
)

# ---------- SIDEBAR: INPUT ---------- #
st.sidebar.header("📥 Log Input")

upload = st.sidebar.file_uploader("Upload log file (.log, .txt)", type=["log", "txt"])
manual_text = st.sidebar.text_area(
    "Or paste log text here",
    height=220,
    placeholder="Paste logs here if you don't want to upload a file...",
)

log_text = None
if upload is not None:
    log_text = upload.read().decode("utf-8", errors="ignore")
elif manual_text.strip():
    log_text = manual_text

analyze_clicked = st.sidebar.button("🔍 Analyze Logs", type="primary")
st.sidebar.markdown("---")
st.sidebar.caption("Tip: Run the same log again to see memory-based suggestions ✨")

# ---------- MAIN CONTENT ---------- #
if analyze_clicked:
    if not log_text:
        st.error("Please upload a log file or paste log text before analyzing.")
    else:
        # Run agents
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

        example_error = seg_result.error_samples[0] if seg_result.error_samples else ""
        first_quick = fix_result.quick_fixes[0] if fix_result.quick_fixes else ""
        first_long = fix_result.long_term_fixes[0] if fix_result.long_term_fixes else ""

        # Store incident in memory
        store_incident(
            log_type=lt_result.log_type,
            primary_root_cause=rc_result.primary_root_cause,
            example_error=example_error,
            quick_fix=first_quick,
            long_term_fix=first_long,
        )

        # ---------- TOP METRICS ROW ---------- #
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Log Type</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{lt_result.log_type}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            total_errors = len(seg_result.error_samples)
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Detected Errors</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{total_errors}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            conf_display = rc_result.confidence if rc_result.confidence is not None else "N/A"
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Model Confidence</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{conf_display}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")  # spacing

        # ---------- SECTIONS ---------- #
        tab1, tab2, tab3, tab4 = st.tabs(
            ["🧮 Log Type & Severity", "🧩 Segments & Errors", "🧠 Root Cause", "🛡 Fixes & Memory"]
        )

        # --- Tab 1: Log Type --- #
        with tab1:
            st.subheader("🧮 Log Type & Severity")
            st.write("**Detected log type:**", lt_result.log_type)
            if lt_result.severity_summary:
                st.write("**Severity estimate:**")
                st.json(lt_result.severity_summary)
            if lt_result.notes:
                st.caption("Classifier notes:")
                st.code(lt_result.notes)

        # --- Tab 2: Segments --- #
        with tab2:
            st.subheader("🧩 Segments & Error Samples")
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

        # --- Tab 3: Root Cause --- #
        with tab3:
            st.subheader("🧠 Root Cause Analysis")
            st.markdown("**Primary root cause:**")
            st.info(rc_result.primary_root_cause)

            if rc_result.symptoms:
                st.markdown("**Symptoms observed:**")
                for s in rc_result.symptoms:
                    st.markdown(f"- {s}")

            if rc_result.confidence is not None:
                st.markdown(f"**Model confidence:** `{rc_result.confidence}`")

        # --- Tab 4: Fixes & Memory --- #
        with tab4:
            st.subheader("🛡 Fix Recommendations & Memory")

            similar = find_similar(
                log_type=lt_result.log_type,
                primary_root_cause=rc_result.primary_root_cause,
            )
            if similar:
                st.success("✅ Similar past incident found in memory.")
                st.write("**Past root cause:**", similar.primary_root_cause)
                st.write("**Past quick fix:**", similar.quick_fix)
                st.write("**Past long-term fix:**", similar.long_term_fix)
            else:
                st.warning("No similar past incident found in memory yet for this pattern.")

            st.markdown("---")
            st.subheader("⚡ Quick Fixes")
            if fix_result.quick_fixes:
                for q in fix_result.quick_fixes:
                    st.markdown(f"- {q}")
            else:
                st.write("_No quick fixes parsed._")

            st.subheader("🏗 Long-term Prevention")
            if fix_result.long_term_fixes:
                for item in fix_result.long_term_fixes:
                    st.markdown(f"- {item}")
            else:
                st.write("_No long-term fixes parsed._")

        st.success("Analysis complete and incident stored in memory 🎉")

else:
    st.info("Use the sidebar to upload a log file or paste log text, then click **🔍 Analyze Logs**.")
    st.code(
        "Tip: start with your sample files like `java_error.log`, `airflow_failure.log`, or `k8s_crashloop.log`.",
        language="bash",
    )
