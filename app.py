import gradio as gr
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from graph import build_graph

graph = build_graph()

def respond(user_input, history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for h in history:
        messages += [{"role": "user", "content": h[0]}, {"role": "assistant", "content": h[1]}]
    messages.append({"role": "user", "content": user_input})
    final_state = graph.invoke({"messages": messages})
    return final_state["messages"][-1]["content"]

ui = gr.ChatInterface(fn=respond, title="LangGraph + OpenRouter", fill_height=True)

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app = gr.mount_gradio_app(app, ui, path="/")