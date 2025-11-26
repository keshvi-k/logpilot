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
    # Build a concise context
    segment_snippets = []
    for seg in segments:
        snippet = "\n".join(seg.sample_lines[:15])
        segment_snippets.append(f"[Segment {seg.id} - {seg.summary}]\n{snippet}")

    error_block = "\n".join(error_samples)

    prompt = f"""
You are an expert incident analyst.

Log type: {log_type}

Here are key log segments:
{"\n\n".join(segment_snippets)}

Here are some representative error lines:
{error_block}

From this, please identify:

1. Primary root cause: <1–3 sentences>
2. Key symptoms: <bullet list>
3. Confidence: <number between 0 and 1>

Respond in this format:

Primary root cause: ...
Symptoms:
- ...
- ...
Confidence: ...
"""

    text = generate_text(prompt)

    primary_root_cause = ""
    symptoms: List[str] = []
    confidence = None

    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()
        if lower.startswith("primary root cause:"):
            primary_root_cause = stripped.split(":", 1)[1].strip()
        elif lower.startswith("- "):
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

