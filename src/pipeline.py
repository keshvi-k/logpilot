import pathlib

from .agents.log_type_detector import run as detect_log_type
from .agents.segmenter_cluster import run as segment_logs
from .agents.root_cause_analyst import run as analyze_root_cause
from .agents.fix_recommender import run as recommend_fixes

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

def read_log_file(rel_path: str) -> str:
    path = BASE_DIR / rel_path
    return path.read_text(encoding="utf-8", errors="ignore")


def analyze_log_file(rel_path: str):
    full_path = BASE_DIR / rel_path
    print(f"\n=== Analyzing: {full_path} ===")

    log_text = read_log_file(rel_path)

    # 1) detect log type
    lt_result = detect_log_type(log_text)
    print(f"\n[1] Log type detected: {lt_result.log_type}")
    if lt_result.severity_summary:
        print(f"    Severities: {lt_result.severity_summary}")

    # 2) segment logs & extract errors
    seg_result = segment_logs(log_text)
    print(f"\n[2] Segments found: {[s.id for s in seg_result.segments]}")
    print(f"    Error samples: {len(seg_result.error_samples)} lines")

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


def main():
    # change this path to test other logs
    analyze_log_file("examples/java_error.log")


if __name__ == "__main__":
    main()

