import gradio as gr
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from graph import build_graph

graph = build_graph()

REQUESTS_TOTAL = Counter("app_requests_total", "Total requests", ["path"])

def respond(user_input, history):
    time.sleep(0.1)  # 最小限流，避免突刺；如需更严谨可替换为令牌桶
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for h in history:
        messages += [{"role": "user", "content": h[0]}, {"role": "assistant", "content": h[1]}]
    messages.append({"role": "user", "content": user_input})
    final_state = graph.invoke({"messages": messages})
    return final_state["messages"][-1]["content"]

ui = gr.ChatInterface(fn=respond, title="LangGraph + OpenRouter", fill_height=True)

app = FastAPI()

@app.middleware("http")
async def _metrics_mw(request, call_next):
    resp = await call_next(request)
    try:
        REQUESTS_TOTAL.labels(request.url.path).inc()
    except Exception:
        pass
    return resp

@app.get("/health")
def health():
    return JSONResponse({"status": "ok"})

@app.get("/ready")   # 依赖就绪（可扩展外部依赖检查）
def ready():
    return JSONResponse({"status": "ok"})

@app.get("/live")    # 进程存活（轻量探活）
def live():
    return JSONResponse({"status": "ok"})

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=405,
        content={"detail": f"Method {request.method} not allowed"},
        headers={"Allow": "GET, POST, PUT, DELETE, OPTIONS"}
    )

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app = gr.mount_gradio_app(app, ui, path="/")