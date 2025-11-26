import pathlib

from .agents.log_type_detector import run as detect_log_type
from .agents.segmenter_cluster import run as segment_logs
from .agents.root_cause_analyst import run as analyze_root_cause
from .agents.fix_recommender import run as recommend_fixes
from .agents.knowledge_memory_agent import store_incident, find_similar
from .tools.file_read_tool import read_log_file

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

def analyze_log_file(rel_path: str):
    full_path = BASE_DIR / rel_path
    print(f"\n=== Analyzing: {full_path} ===")
    trace = []
    metrics = {
        "lines_total": 0,
        "error_samples_count": 0,
        "segments_count": 0,
    }
    # read log file
    log_text = read_log_file(rel_path)
    metrics["lines_total"] = len(log_text.splitlines())

    # 1) detect log type
    lt_result = detect_log_type(log_text)
    print(f"\n[1] Log type detected: {lt_result.log_type}")
    if lt_result.severity_summary:
        print(f"    Severities: {lt_result.severity_summary}")
    trace.append("LogTypeDetector: completed")

    # 2) segment logs & extract errors
    seg_result = segment_logs(log_text)
    print(f"\n[2] Segments found: {[s.id for s in seg_result.segments]}")
    print(f"    Error samples: {len(seg_result.error_samples)} lines")
    metrics["segments_count"] = len(seg_result.segments)
    metrics["error_samples_count"] = len(seg_result.error_samples)
    trace.append("SegmenterCluster: completed")

    # 3) root cause analysis
    rc_result = analyze_root_cause(
        log_type=lt_result.log_type,
        segments=seg_result.segments,
        error_samples=seg_result.error_samples,
    )
    print(f"\n[3] Primary root cause: {rc_result.primary_root_cause}")
    if rc_result.symptoms:
        print("    Symptoms:")
        for s in rc_result.symptoms:
            print(f"    - {s}")
    if rc_result.confidence is not None:
        print(f"    Confidence: {rc_result.confidence}")
    # 3.5) Memory lookup: has this happened before?
    similar = find_similar(
        log_type=lt_result.log_type,
        primary_root_cause=rc_result.primary_root_cause,
    )
    if similar:
        print("\n[3.5] Similar past incident found in memory:")
        print(f"     Past root cause: {similar.primary_root_cause}")
        print(f"     Past quick fix: {similar.quick_fix}")
        print(f"     Past long-term fix: {similar.long_term_fix}")
    else:
        print("\n[3.5] No similar past incident found in memory.")
    trace.append("RootCauseAnalyst: completed")

    # 4) fix recommendations
    fix_result = recommend_fixes(
        log_type=lt_result.log_type,
        primary_root_cause=rc_result.primary_root_cause,
        symptoms=rc_result.symptoms,
    )
    print("\n[4] Suggested quick fixes:")
    for q in fix_result.quick_fixes:
        print(f"   - {q}")

    print("\n[5] Suggested long-term prevention:")
    for item in fix_result.long_term_fixes:
        print(f"   - {item}")
    
    trace.append("FixRecommender: completed")

    # 5.5) Store this incident in memory for future use
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
    trace.append("KnowledgeMemoryAgent: stored_incident")
    print("\n[6] Trace:")
    for step in trace:
        print(f"   - {step}")

    print("\n[7] Metrics:")
    for k, v in metrics.items():
        print(f"   {k}: {v}")

def main():
    # change this path to test other logs
    analyze_log_file("examples/java_error.log")


if __name__ == "__main__":
    main()

