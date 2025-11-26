import json
import pathlib
from dataclasses import dataclass, asdict
from typing import List, Optional

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MEMORY_PATH = BASE_DIR / "incident_memory.json"

@dataclass
class Incident:
    log_type: str
    primary_root_cause: str
    example_error: str
    quick_fix: str
    long_term_fix: str


def _load_all() -> List[Incident]:
    if not MEMORY_PATH.exists():
        return []
    try:
        raw = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
        return [Incident(**item) for item in raw]
    except Exception:
        return []


def _save_all(incidents: List[Incident]) -> None:
    data = [asdict(i) for i in incidents]
    MEMORY_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def add_incident(incident: Incident) -> None:
    incidents = _load_all()
    incidents.append(incident)
    _save_all(incidents)


def find_similar_incident(
    log_type: str,
    primary_root_cause: str,
) -> Optional[Incident]:
    """
    Very simple similarity: same log type + overlapping words in root cause.
    """
    incidents = _load_all()
    root_words = set(primary_root_cause.lower().split())
    best_match = None
    best_overlap = 0

    for inc in incidents:
        if inc.log_type.lower() != log_type.lower():
            continue
        inc_words = set(inc.primary_root_cause.lower().split())
        overlap = len(root_words & inc_words)
        if overlap > best_overlap:
            best_overlap = overlap
            best_match = inc

    if best_overlap >= 3:
        return best_match
    return None

