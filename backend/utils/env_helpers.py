import os

def gemini_url():
    """Return the Gemini LLM API URL from environment variable or config."""
    return os.environ.get("GEMINI_API_URL")

# ...existing code...
