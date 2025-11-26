from dataclasses import dataclass
from typing import List
from ..tools.log_search_tool import search_log, LogMatch

@dataclass
class LogSegment:
    id: str
    summary: str
    sample_lines: List[str]

@dataclass
class SegmentResult:
    segments: List[LogSegment]
    error_samples: List[str]


def run(log_text: str) -> SegmentResult:
    lines = log_text.splitlines()

    # Use our tool to find error-like lines
    error_matches: List[LogMatch] = []
    for keyword in ["error", "exception", "failed"]:
        error_matches.extend(search_log(log_text, keyword, context_lines=1))

    # Deduplicate by line number
    seen = set()
    error_lines = []
    for m in error_matches:
        if m.line_number not in seen:
            seen.add(m.line_number)
            error_lines.append(m.line)

    segments: List[LogSegment] = []

    if lines:
        segments.append(LogSegment(
            id="start",
            summary="Beginning of log",
            sample_lines=lines[:30]
        ))

    if error_lines:
        # region around first error using its line_number
        first_error_idx = next(
            (i for i, ln in enumerate(lines) if ln == error_lines[0]),
            0
        )
        start = max(0, first_error_idx - 15)
        end = min(len(lines), first_error_idx + 15)
        segments.append(LogSegment(
            id="error_region",
            summary="Region around first error",
            sample_lines=lines[start:end]
        ))

    if len(lines) > 30:
        segments.append(LogSegment(
            id="end",
            summary="End of log",
            sample_lines=lines[-30:]
        ))

    return SegmentResult(
        segments=segments,
        error_samples=error_lines[:10],
    )


