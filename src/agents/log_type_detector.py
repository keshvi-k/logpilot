from dataclasses import dataclass
from typing import Dict, Any
from ..llm_client import generate_text

@dataclass
class LogTypeResult:
    log_type: str
    severity_summary: Dict[str, int] | None = None
    notes: str | None = None


def run(log_text: str) -> LogTypeResult:
    """
    Ask Gemini to:
      - guess log type
      - rough severity distribution
    """
    prompt = f"""
You are a log classification assistant.

Classify the following logs and estimate severity counts.

<logs>
{log_text}
</logs>

Respond in this format exactly:

Log type: <one short phrase, e.g. "Java app", "Airflow", "Kubernetes", "Spark">
Severities:
- INFO: <number or estimate>
- WARN: <number or estimate>
- ERROR: <number or estimate>
Notes: <1 short line>
"""

    text = generate_text(prompt)

    # very light parsing (no need to be perfect)
    log_type = "unknown"
    severities: Dict[str, int] = {}

    for line in text.splitlines():
        line_lower = line.lower().strip()
        if line_lower.startswith("log type:"):
            log_type = line.split(":", 1)[1].strip()
        elif line_lower.startswith("- info"):
            # try to extract number at end
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    severities["INFO"] = int(parts[1])
                except ValueError:
                    pass
        elif line_lower.startswith("- warn"):
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    severities["WARN"] = int(parts[1])
                except ValueError:
                    pass
        elif line_lower.startswith("- error"):
            parts = line.split(":")
            if len(parts) > 1:
                try:
                    severities["ERROR"] = int(parts[1])
                except ValueError:
                    pass

    return LogTypeResult(
        log_type=log_type,
        severity_summary=severities or None,
        notes=text,
    )

