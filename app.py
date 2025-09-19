import gradio as gr
import time
from time import monotonic
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, PlainTextResponse
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

# 1) 默认响应统一为 JSON（让 OpenAPI 对未显式声明的路由有明确 content-type）
app = FastAPI(default_response_class=JSONResponse)

# --- begin: metrics rate limit ---
_LAST_METRICS_TS = 0.0
@app.middleware("http")
async def _rate_limit_metrics(request: Request, call_next):
    global _LAST_METRICS_TS
    if request.url.path == "/metrics":
        now = monotonic()
        if now - _LAST_METRICS_TS < 1.0:  # 最多 1 QPS
            return PlainTextResponse("rate limited", status_code=429)
        _LAST_METRICS_TS = now
    return await call_next(request)
# --- end: metrics rate limit ---

@app.middleware("http")
async def _metrics_mw(request, call_next):
    resp = await call_next(request)
    try:
        REQUESTS_TOTAL.labels(request.url.path).inc()
    except Exception:
        pass
    return resp

# 4) 可选的 TRACE/非常规方法兜底（部分环境下 TRACE 会走到 404）
@app.middleware("http")
async def reject_unsupported_methods(request: Request, call_next):
    if request.method not in ("GET", "OPTIONS"):
        # 尽早返回 405，避免被其它中间件吞掉变成 404/200
        return JSONResponse(
            status_code=405,
            content={"detail": f"Method {request.method} not allowed"},
            headers={"Allow": "GET, OPTIONS"},
        )
    return await call_next(request)

# === 健康/诊断端点：明确只有 GET，OpenAPI 会标注 application/json ===
@app.get("/health", summary="Liveness probe", responses={200: {"content": {"application/json": {}}}})
def health():
    return JSONResponse({"status": "ok"})

@app.get("/ready", summary="Readiness probe", responses={200: {"content": {"application/json": {}}}})
def ready():
    return JSONResponse({"status": "ok"})

@app.get("/live", summary="Lightweight live probe", responses={200: {"content": {"application/json": {}}}})
def live():
    return JSONResponse({"status": "ok"})

# 2) /metrics：显式声明 text/plain；否则 Schemathesis 会认为未记录的 content-type
@app.get(
    "/metrics",
    response_class=PlainTextResponse,
    summary="Prometheus metrics",
    responses={200: {"content": {"text/plain": {}}}},
)
def metrics():
    # CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# 5) CORS：不要用 allow_methods="*"，只暴露你允许的方法，避免语义混淆
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# 保持原有 Gradio 挂载
app = gr.mount_gradio_app(app, ui, path="/")