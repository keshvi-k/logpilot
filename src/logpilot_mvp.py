import pathlib
import os
from google import genai

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent

def analyze_logs_with_llm(log_text: str):
    prompt = f"""
You are an expert DevOps and software engineer.

Here are logs:

<logs>
{log_text}
</logs>

Provide response in this format:

1. Detected log type:
2. High-level summary:
3. Likely root cause:
4. Suggested quick fix:
5. Suggested long-term prevention:
"""

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set")

    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    # 🔽 Safely extract text from candidates
    try:
        texts = []
        if getattr(response, "candidates", None):
            for cand in response.candidates:
                content = getattr(cand, "content", None)
                if content and getattr(content, "parts", None):
                    for part in content.parts:
                        t = getattr(part, "text", None)
                        if t:
                            texts.append(t)
        if texts:
            return "\n".join(texts)

        # Fallback: string representation
        return str(response)

    except Exception as e:
        return f"[Failed to parse response text: {e}]\nRaw response:\n{response}"

def read_log_file(rel_path: str):
    path = BASE_DIR / rel_path
    return path.read_text(encoding="utf-8", errors="ignore")


def main():
    log_path = "examples/java_error.log"
    log_text = read_log_file(log_path)

    print(f"\n=== Analyzing log file: {log_path} ===\n")
    analysis = analyze_logs_with_llm(log_text)

    print("\n=== LLM Analysis ===\n")
    print(analysis)


if __name__ == "__main__":
    main()
