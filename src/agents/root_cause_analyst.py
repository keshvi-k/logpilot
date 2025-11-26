from dataclasses import dataclass
from typing import List
from ..llm_client import generate_text
from .segmenter_cluster import LogSegment

@dataclass
class RootCauseResult:
    primary_root_cause: str
    symptoms: List[str]
    confidence: float | None = None
    raw_analysis: str | None = None


def run(
    log_type: str,
    segments: List[LogSegment],
    error_samples: List[str],
) -> RootCauseResult:

    # Build a concise context without ANY backslashes inside {}
    segment_snippets = []
    for seg in segments:
        snippet = "\n".join(seg.sample_lines[:15])
        segment_snippets.append(f"[Segment {seg.id} - {seg.summary}]\n{snippet}")

    error_block = "\n".join(error_samples)

    prompt = (
        "You are an expert incident analyst.\n\n"
        f"Log type: {log_type}\n\n"
        "Here are key log segments:\n"
        f"{chr(10).join(segment_snippets)}\n\n"
        "Here are some representative error lines:\n"
        f"{error_block}\n\n"
        "From this, identify:\n\n"
        "1. Primary root cause: <1–3 sentences>\n"
        "2. Key symptoms: <bullet list>\n"
        "3. Confidence: <number between 0 and 1>\n\n"
        "Respond in this format:\n\n"
        "Primary root cause: ...\n"
        "Symptoms:\n"
        "- ...\n"
        "- ...\n"
        "Confidence: ...\n"
    )

    text = generate_text(prompt)

    primary_root_cause = ""
    symptoms: List[str] = []
    confidence = None

    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("primary root cause:"):
            primary_root_cause = stripped.split(":", 1)[1].strip()
        elif stripped.startswith("- "):
            symptoms.append(stripped[2:].strip())
        elif lower.startswith("confidence:"):
            val = stripped.split(":", 1)[1].strip()
            try:
                confidence = float(val)
            except ValueError:
                pass

    return RootCauseResult(
        primary_root_cause=primary_root_cause or text,
        symptoms=symptoms,
        confidence=confidence,
        raw_analysis=text,
    )
