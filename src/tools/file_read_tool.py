import pathlib

# __file__ → .../src/tools/file_read_tool.py
# parents[2] → project root directory "logpilot"
BASE_DIR = pathlib.Path(__file__).resolve().parents[2]

def read_log_file(rel_path: str) -> str:
    """
    Read a log file relative to the PROJECT ROOT.
    Example usage:
        read_log_file("examples/java_error.log")
    """
    path = BASE_DIR / rel_path
    return path.read_text(encoding="utf-8", errors="ignore")

