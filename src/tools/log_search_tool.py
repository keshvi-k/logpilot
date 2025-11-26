# src/tools/log_search_tool.py

from dataclasses import dataclass
from typing import List

@dataclass
class LogMatch:
    line_number: int
    line: str
    context_before: List[str]
    context_after: List[str]


def search_log(
    log_text: str,
    query: str,
    context_lines: int = 2,
) -> List[LogMatch]:
    """
    Simple log search tool.
    Given a keyword, returns matching lines with surrounding context.
    """
    lines = log_text.splitlines()
    matches: List[LogMatch] = []

    for i, line in enumerate(lines):
        if query.lower() in line.lower():
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            before = lines[start:i]
            after = lines[i + 1:end]
            matches.append(
                LogMatch(
                    line_number=i + 1,
                    line=line,
                    context_before=before,
                    context_after=after,
                )
            )
    return matches

