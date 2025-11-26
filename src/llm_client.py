import os
from google import genai

# Single client reused everywhere
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is not set")
        _client = genai.Client(api_key=api_key)
    return _client


def generate_text(prompt: str, model: str = "gemini-2.0-flash") -> str:
    client = get_client()

    response = client.models.generate_content(
        model=model,
        contents=prompt,
    )

    # Safely extract text from candidates
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

    return str(response)
