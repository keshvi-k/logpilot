# src/agents/knowledge_memory_agent.py

from typing import Optional
from ..memory.incident_store import Incident, add_incident, find_similar_incident as _find_similar


def store_incident(
    log_type: str,
    primary_root_cause: str,
    example_error: str,
    quick_fix: str,
    long_term_fix: str,
) -> None:
    incident = Incident(
        log_type=log_type,
        primary_root_cause=primary_root_cause,
        example_error=example_error,
        quick_fix=quick_fix,
        long_term_fix=long_term_fix,
    )
    add_incident(incident)


def find_similar(
    log_type: str,
    primary_root_cause: str,
) -> Optional[Incident]:
    return _find_similar(log_type, primary_root_cause)

