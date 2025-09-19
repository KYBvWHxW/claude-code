# 运行手册 Operations Manual

## 系统概述
本应用是基于FastAPI + Gradio + LangGraph的聊天机器人应用，集成了OpenRouter API，部署在Fly.io平台。

## 本地开发

### 环境准备
```bash
# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENROUTER_API_KEY="your_api_key_here"
```

### 启动服务
```bash
# 开发模式启动
python -m uvicorn app:app --reload --host 0.0.0.0 --port 7860

# 访问地址
# Web界面: http://localhost:7860
# API文档: http://localhost:7860/docs
# 健康检查: http://localhost:7860/health
```

### 测试
```bash
# 运行单元测试
pytest tests/ -v

# 运行API测试
schemathesis run openapi.yaml --base-url http://localhost:7860 --checks all
```

## 生产部署

### Fly.io部署
```bash
# 登录
flyctl auth login

# 设置secrets
flyctl secrets set OPENROUTER_API_KEY="your_api_key" --app langgraph-gradio-starter

# 部署
flyctl deploy --app langgraph-gradio-starter

# 查看状态
flyctl status --app langgraph-gradio-starter

# 查看日志
flyctl logs --app langgraph-gradio-starter
```

### 验证部署
```bash
# 检查健康状态
curl https://langgraph-gradio-starter.fly.dev/health

# 检查主界面
curl -I https://langgraph-gradio-starter.fly.dev/
```

## 监控与故障排除

### 健康检查
- 健康检查端点: `/health`
- 预期响应: `{"status": "ok"}`
- 检查间隔: 10秒

### 常见问题

#### 1. 502 Bad Gateway
- **原因**: OOM(内存不足)或API密钥缺失
- **解决方案**:
  ```bash
  # 检查内存使用
  flyctl scale vm shared-cpu-1x --app langgraph-gradio-starter

  # 检查API密钥
  flyctl secrets list --app langgraph-gradio-starter
  ```

#### 2. API调用失败
- **原因**: OpenRouter API密钥无效或额度不足
- **解决方案**: 检查API密钥有效性和账户余额

#### 3. 容器启动失败
- **原因**: 依赖安装失败或代码错误
- **解决方案**:
  ```bash
  # 查看详细日志
  flyctl logs --app langgraph-gradio-starter

  # 本地测试Docker构建
  docker build -t test .
  docker run -p 8080:8080 test
  ```

### 扩容操作
```bash
# 垂直扩容(增加内存/CPU)
flyctl scale vm performance-1x --app langgraph-gradio-starter

# 水平扩容(增加实例数)
flyctl scale count 3 --app langgraph-gradio-starter
```

### 备份与恢复
- 代码备份: 使用Git仓库
- 配置备份: 定期导出fly.toml和环境变量
- 数据备份: 当前应用为无状态应用，无需数据备份

## CI/CD

### GitHub Actions
- 触发条件: 推送到main/develop分支或创建PR到main分支
- 测试流程: pytest → schemathesis → Docker构建
- 工作流文件: `.github/workflows/test.yml`

### 手动部署流程
1. 代码提交和推送
2. CI测试通过
3. 执行部署命令
4. 验证部署状态

## 安全注意事项
- OpenRouter API密钥存储在Fly.io Secrets中
- 使用HTTPS强制连接
- 定期轮换API密钥
- 监控异常API调用模式

## 常见提示与替代命令

### Fly.io 命令替代
- **flyctl open 已弃用**，替代：`fly apps open -a <app>`
- **flyctl logs 无 --since**，用 `-n` 查看最近 N 条：`flyctl logs -a <app> -n 100`
- **构建成功但超时**：通常是镜像构建/拉取慢或机器滚动替换
  - 做法：先 `flyctl status` 检查状态，再 `curl` 验证是否已生效
  - 不要急于重新部署，等待滚动更新完成

### 当前应用信息
- **应用名称**: `langgraph-gradio-starter`
- **生产URL**: https://langgraph-gradio-starter.fly.dev
- **健康检查**: `/live` 端点（由 Fly.io 健康检查使用）
- **监控指标**: `/metrics` 端点（Prometheus 格式）

### 常见故障排查
- **502 Bad Gateway**: 检查 OOM 或 API 密钥缺失
- **Health check 失败**: 确认 `/live` 端点存在且响应正常
- **API 调用失败**: 验证 OpenRouter API 密钥和余额