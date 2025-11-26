from dataclasses import dataclass
from typing import List
from ..llm_client import generate_text

@dataclass
class FixResult:
    quick_fixes: List[str]
    long_term_fixes: List[str]
    raw_text: str | None = None


def run(log_type: str, primary_root_cause: str, symptoms: List[str]) -> FixResult:
    symptom_text = "\n".join(f"- {s}" for s in symptoms) if symptoms else "None listed."

    prompt = f"""
You are an SRE and reliability engineer.

Log type: {log_type}
Primary root cause: {primary_root_cause}
Symptoms:
{symptom_text}

Propose concrete fixes.

⚠️ IMPORTANT: Follow this EXACT format. Use these exact headings and bullet style.

Quick fixes:
- <short concrete action>
- <short concrete action>

Long-term prevention:
- <short concrete action>
- <short concrete action>
"""

    text = generate_text(prompt)

    quick: List[str] = []
    long_term: List[str] = []
    current_section = None

    for line in text.splitlines():
        stripped = line.strip()
        lower = stripped.lower()

        # Detect section headers (be a bit flexible)
        if lower.startswith("quick fixes"):
            current_section = "quick"
            continue
        if "long-term prevention" in lower or "long term prevention" in lower:
            current_section = "long"
            continue

        # Bullets
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            if current_section == "quick":
                quick.append(item)
            elif current_section == "long":
                long_term.append(item)

    # Fallback: if parsing failed, just put whole text in one list
    # Fallbacks

    # If parsing totally failed, put entire raw text as one quick fix
    if not quick and not long_term:
        quick = [text]

    return FixResult(
        quick_fixes=quick,
        long_term_fixes=long_term,
        raw_text=text,
    )

    
