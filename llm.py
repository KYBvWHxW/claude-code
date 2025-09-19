import os
import time
from openai import OpenAI, APIConnectionError, RateLimitError

TIMEOUT = float(os.getenv("OPENROUTER_TIMEOUT", "30"))
MAX_RETRIES = int(os.getenv("OPENROUTER_MAX_RETRIES", "3"))

# Initialize client with fallback for testing
_api_key = os.getenv("OPENROUTER_API_KEY", "test-key-for-ci")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=_api_key,
) if _api_key != "test-key-for-ci" else None

def chat(messages):
    if client is None:
        return "Mock response for testing"

    extra_headers = {
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost:7860"),
        "X-Title": os.getenv("APP_TITLE", "LangGraph Gradio Starter"),
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
                messages=messages,
                extra_headers=extra_headers,
                timeout=TIMEOUT,
            )
            return resp.choices[0].message.content
        except (APIConnectionError, RateLimitError) as e:
            if attempt == MAX_RETRIES:
                raise
            time.sleep(min(2 ** attempt, 8))