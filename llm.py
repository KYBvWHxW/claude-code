import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)

def chat(messages):
    extra_headers = {
        "HTTP-Referer": os.getenv("APP_URL", "http://localhost:7860"),
        "X-Title": os.getenv("APP_TITLE", "LangGraph Gradio Starter"),
    }
    resp = client.chat.completions.create(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
        messages=messages,
        extra_headers=extra_headers,
    )
    return resp.choices[0].message.content