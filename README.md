# LangGraph Gradio Starter

[![tests](https://github.com/KYBvWHxW/claude-code/actions/workflows/test.yml/badge.svg)](https://github.com/KYBvWHxW/claude-code/actions/workflows/test.yml)

基于FastAPI + Gradio + LangGraph的聊天机器人应用，集成OpenRouter API，提供Web界面的智能对话服务。

## 特性

- 🤖 基于LangGraph的对话流管理
- 🌐 Gradio Web界面，支持实时聊天
- ⚡ FastAPI后端，提供RESTful API
- 🔌 OpenRouter API集成，支持多种AI模型
- 🐳 Docker容器化部署
- ☁️ Fly.io云部署支持
- 🧪 完整的测试覆盖(pytest + schemathesis)
- 🔄 CI/CD自动化工作流

## 快速开始

### 环境要求
- Python 3.11+
- Docker (可选)
- Fly.io CLI (部署时需要)

### 本地开发

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd langgraph-gradio-starter
   ```

2. **设置虚拟环境**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或 .venv\Scripts\activate  # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置环境变量**
   ```bash
   export OPENROUTER_API_KEY="your_openrouter_api_key"
   ```

5. **启动应用**
   ```bash
   python -m uvicorn app:app --reload --host 0.0.0.0 --port 7860
   ```

6. **访问应用**
   - Web界面: http://localhost:7860
   - API文档: http://localhost:7860/docs
   - 健康检查: http://localhost:7860/health

### 测试

```bash
# 运行单元测试
pytest tests/ -v

# 运行API测试
python -m uvicorn app:app --host 0.0.0.0 --port 8080 &
sleep 10
schemathesis run openapi.yaml --base-url http://localhost:8080 --checks all
```

## 部署

### Fly.io部署

1. **安装Fly.io CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **登录并创建应用**
   ```bash
   flyctl auth login
   flyctl apps create langgraph-gradio-starter
   ```

3. **设置环境变量**
   ```bash
   flyctl secrets set OPENROUTER_API_KEY="your_api_key" --app langgraph-gradio-starter
   ```

4. **部署应用**
   ```bash
   flyctl deploy --app langgraph-gradio-starter
   ```

5. **验证部署**
   ```bash
   curl https://langgraph-gradio-starter.fly.dev/health
   ```

### Docker部署

```bash
# 构建镜像
docker build -t langgraph-gradio-starter .

# 运行容器
docker run -p 8080:8080 -e OPENROUTER_API_KEY="your_api_key" langgraph-gradio-starter
```

## API文档

### 端点

- `GET /` - Gradio Web界面
- `GET /docs` - OpenAPI文档
- `GET /health` - 健康检查
- `POST /gradio_api/*` - Gradio API端点

### 健康检查

```bash
curl https://langgraph-gradio-starter.fly.dev/health
# 响应: {"status": "ok"}
```

## 架构说明

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Gradio UI     │────│   FastAPI       │────│   LangGraph     │
│   (前端界面)     │    │   (Web服务器)    │    │   (对话流)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  OpenRouter API │
                       │  (AI模型接口)    │
                       └─────────────────┘
```

## 开发指南

### 项目结构

```
├── app.py              # FastAPI应用主文件
├── graph.py            # LangGraph对话流定义
├── llm.py             # OpenRouter客户端
├── requirements.txt    # Python依赖
├── Dockerfile         # Docker构建文件
├── fly.toml           # Fly.io配置
├── openapi.yaml       # OpenAPI规范
├── tests/             # 测试文件
│   ├── test_sample.py
│   └── test_api_schema.py
├── .github/workflows/ # CI/CD工作流
│   └── test.yml
├── .claude/           # Claude Code Hooks
│   └── settings.json
├── OPERATIONS.md      # 运行手册
└── README.md          # 项目说明
```

### Claude Code Hooks

项目配置了Claude Code Hooks，在文件修改时自动运行测试：

```json
{
  "postToolUse": "python -c \"import subprocess, sys, os; result1 = subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests/'], capture_output=True, text=True); result2 = subprocess.run([sys.executable, '-m', 'schemathesis', 'run', 'openapi.yaml', '--base-url', 'http://localhost:7860', '--checks', 'all'], capture_output=True, text=True) if os.path.exists('openapi.yaml') else subprocess.CompletedProcess([], 0, '', ''); print('🧪 pytest:', 'PASSED' if result1.returncode == 0 else 'FAILED'); print('🔍 schemathesis:', 'PASSED' if result2.returncode == 0 else 'FAILED'); sys.exit(max(result1.returncode, result2.returncode))\""
}
```

## 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 支持

- 查看 [OPERATIONS.md](OPERATIONS.md) 了解运维详情
- 报告问题请使用 [GitHub Issues](../../issues)
- 技术支持请参考项目文档