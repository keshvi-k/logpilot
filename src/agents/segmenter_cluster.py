from dataclasses import dataclass
from typing import List

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

    error_lines = [ln for ln in lines if "ERROR" in ln or "Error" in ln or "Exception" in ln]

    # Simple heuristic segments: first 30 lines, error zone around first error, last 30 lines
    segments: List[LogSegment] = []

    if lines:
        segments.append(LogSegment(
            id="start",
            summary="Beginning of log",
            sample_lines=lines[:30]
        ))

    if error_lines:
        # Take 30 lines around first error
        first_error = lines.index(error_lines[0])
        start = max(0, first_error - 15)
        end = min(len(lines), first_error + 15)
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
        error_samples=error_lines[:10],   # at most 10
    )

