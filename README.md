# LogPilot – Multi-Agent Log Incident Analyst

LogPilot is an AI-powered agent system that analyzes raw logs from any tech stack
(Java apps, Airflow, Kubernetes, Spark, etc.), identifies patterns, finds likely
root causes, and suggests concrete fixes.

## Goal 1:

- Have a simple script that:
  - Reads a log file
  - Sends it to an LLM (Gemini)
  - Returns:
    - guessed log type
    - short summary
    - likely root cause
    - suggested fixes

Later, this will be split into multiple agents:
- LogTypeDetectorAgent
- SegmenterClusterAgent
- RootCauseAnalystAgent
- FixRecommenderAgent
- KnowledgeMemoryAgent

