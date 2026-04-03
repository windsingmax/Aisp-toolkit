# AIServiceProxy — Skill + MCP 调用指南

本文档说明如何通过 **Cursor Skill** 与 **MCP Server** 两种方式调用吉比特内网 AIServiceProxy 网关，覆盖密钥配置、可用工具、实际调用示例与排错流程。

---

## 目录

1. [架构总览](#1-架构总览)
2. [密钥配置（前置必做）](#2-密钥配置前置必做)
3. [方式一：MCP Server 调用](#3-方式一mcp-server-调用)
4. [方式二：Skill 脚本调用](#4-方式二skill-脚本调用)
5. [方式三：手动 curl / HTTP 调用](#5-方式三手动-curl--http-调用)
6. [API 速查表](#6-api-速查表)
7. [模型速查与别名](#7-模型速查与别名)
8. [同步与异步任务](#8-同步与异步任务)
9. [常见错误与排错](#9-常见错误与排错)
10. [安全守则](#10-安全守则)

---

## 1. 架构总览

```
用户请求
  │
  ├─→ [MCP Server]  gbits-aiserviceproxy     ← Cursor 内置，AI 自动调用
  │     ├── ping_gateway        （连通性测试）
  │     ├── get_available_models （查可用模型）
  │     └── generate_image      （图片生成 + 自动下载）
  │
  ├─→ [Skill 脚本]  invoke-aisp.ps1           ← 从本机文件读 Key，避免审批框泄露
  │     └── 支持 GET / POST，JSON Body 通过文件传入
  │
  └─→ [手动 curl]   环境变量引用 Key          ← 灵活但需注意安全
        └── 适用于 LLM / 图片 / 视频等全部接口
                       │
                       ▼
          http://aitools.g-bits.com/aiserviceproxy/api/v1/...
```

**三种方式对比**：

| 维度 | MCP Server | Skill 脚本 | 手动 curl |
|------|-----------|------------|----------|
| 密钥安全 | MCP 进程内读取，不会出现在审批框 | 脚本内从文件读取，审批框只显示脚本路径 | 必须用环境变量，否则会暴露 |
| 使用门槛 | 零配置（MCP 已连接即可） | 需要放置密钥文件 | 需要手动设置环境变量 |
| 覆盖接口 | 仅图片生成 + 模型查询 + 连通测试 | 全部接口 | 全部接口 |
| 适用场景 | 日常出图、快速查模型 | 需要调用 LLM/视频等 MCP 未覆盖的接口 | 调试、一次性测试 |

---

## 2. 密钥配置（前置必做）

### 2.1 MCP Server 方式

MCP Server 的 Key 在 Cursor MCP 配置中设置，通常已由项目初始化完成。若未配置，在 Cursor Settings → MCP 中找到 `gbits-aiserviceproxy`，添加环境变量：

```
AISERVICEPROXY_API_KEY = <你的 Key>
```

### 2.2 Skill 脚本方式

一次性在本机创建密钥文件（**不要把 Key 发给 AI 助手**）：

```powershell
mkdir "$HOME\.gbits" -Force
# 用记事本或 echo 写入 Key（单行、仅 Key 内容）
notepad "$HOME\.gbits\aiserviceproxy_api_key.txt"
```

脚本 `invoke-aisp.ps1` 运行时自动从此文件读取 Key。

### 2.3 手动 curl 方式

在**当前终端会话**中设置环境变量：

```powershell
# PowerShell（仅当前会话生效）
$env:AISERVICEPROXY_API_KEY = '你的Key'
```

```bash
# Bash / Git Bash
export AISERVICEPROXY_API_KEY='你的Key'
```

---

## 3. 方式一：MCP Server 调用

MCP Server 标识符：`user-gbits-aiserviceproxy`

### 3.1 ping_gateway — 连通性测试

测试 MCP Server 是否正确读取了 API Key 并能访问内网。

```
工具：ping_gateway
参数：无
```

调用示例（Cursor 中 AI 自动调用）：

```json
{
  "server": "user-gbits-aiserviceproxy",
  "toolName": "ping_gateway",
  "arguments": {}
}
```

### 3.2 get_available_models — 查询可用模型

查询网关当前支持的模型列表，可按 `service_type` 筛选。

```
工具：get_available_models
参数：
  - service_type (可选): llm / image / video / audio / search / file
                         留空返回全部
```

调用示例：

```json
{
  "server": "user-gbits-aiserviceproxy",
  "toolName": "get_available_models",
  "arguments": { "service_type": "image" }
}
```

### 3.3 generate_image — 图片生成

调用网关生成图片并自动下载到本地。

```
工具：generate_image
参数：
  - prompt (必填): 图片的详细描述提示词
  - model (可选):  模型名称，默认 jimeng-4.5
                   别名：大香蕉/banana-pro → gemini-3-pro
                         小香蕉/banana2   → gemini-3.1-flash-image
  - save_path (可选): 本地保存目录
                      未指定则存到默认路径 e:\claude\img
```

调用示例：

```json
{
  "server": "user-gbits-aiserviceproxy",
  "toolName": "generate_image",
  "arguments": {
    "prompt": "一只火焰猎犬站在熔岩洞窟入口，pixel art style, 64x64",
    "model": "jimeng-4.5",
    "save_path": "E:\\Ai\\Vibecoding_Game\\assets\\monsters"
  }
}
```

**注意**：`save_path` 应在调用时直接指定，**禁止**调用完成后再用 `Copy-Item` 二次复制。

---

## 4. 方式二：Skill 脚本调用

脚本路径：`~/.claude/skills/gbits-aiserviceproxy-api/scripts/invoke-aisp.ps1`

### 4.1 GET 请求（查询模型）

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "$HOME\.claude\skills\gbits-aiserviceproxy-api\scripts\invoke-aisp.ps1" `
  -Method GET `
  -Uri "http://aitools.g-bits.com/aiserviceproxy/api/v1/config/models?service_type=image"
```

### 4.2 POST 请求（LLM 对话）

先将请求体写入 JSON 文件：

```json
{
  "service_type": "llm",
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "你好，请介绍一下自己" }
  ],
  "stream": false
}
```

然后调用脚本：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "$HOME\.claude\skills\gbits-aiserviceproxy-api\scripts\invoke-aisp.ps1" `
  -Method POST `
  -Uri "http://aitools.g-bits.com/aiserviceproxy/api/v1/llm/chat" `
  -BodyPath "C:\Users\cenjy\tmp_llm_body.json"
```

### 4.3 POST 请求（图片生成）

请求体示例（文生图）：

```json
{
  "service_type": "image",
  "model": "gemini-3-pro",
  "prompt": "一只可爱的岩石犀牛幼崽，pixel art, 透明背景",
  "async": false
}
```

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "$HOME\.claude\skills\gbits-aiserviceproxy-api\scripts\invoke-aisp.ps1" `
  -Method POST `
  -Uri "http://aitools.g-bits.com/aiserviceproxy/api/v1/image/generate" `
  -BodyPath "C:\Users\cenjy\tmp_img_body.json"
```

---

## 5. 方式三：手动 curl / HTTP 调用

**前提**：已在当前终端会话中设置了 `AISERVICEPROXY_API_KEY` 环境变量。

### PowerShell 示例

```powershell
# 查询可用模型
curl.exe -s "http://aitools.g-bits.com/aiserviceproxy/api/v1/config/models" `
  -H "Authorization: Bearer $env:AISERVICEPROXY_API_KEY"
```

```powershell
# LLM 对话（Body 放文件避免引号问题）
curl.exe -s -X POST "http://aitools.g-bits.com/aiserviceproxy/api/v1/llm/chat" `
  -H "Authorization: Bearer $env:AISERVICEPROXY_API_KEY" `
  -H "Content-Type: application/json" `
  -d "@body.json"
```

### Bash 示例

```bash
# 查询可用模型
curl -s "http://aitools.g-bits.com/aiserviceproxy/api/v1/config/models" \
  -H "Authorization: Bearer $AISERVICEPROXY_API_KEY"
```

```bash
# 图片生成
curl -s -X POST "http://aitools.g-bits.com/aiserviceproxy/api/v1/image/generate" \
  -H "Authorization: Bearer $AISERVICEPROXY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"service_type":"image","model":"jimeng-4.5","prompt":"火焰猎犬"}'
```

---

## 6. API 速查表

**基础 URL**：`http://aitools.g-bits.com/aiserviceproxy`

| 用途 | 方法 | 路径 | MCP 工具覆盖 |
|------|------|------|-------------|
| LLM 对话（含多模态） | POST | `/api/v1/llm/chat` | - |
| 图片生成 | POST | `/api/v1/image/generate` | generate_image |
| 视频生成 | POST | `/api/v1/video/generate` | - |
| 任务查询（异步） | GET | `/api/v1/tasks/{task_id}` | - |
| 可用模型查询 | GET | `/api/v1/config/models` | get_available_models |
| 连通性测试 | - | - | ping_gateway |

### 统一响应格式

```json
// 成功
{
  "success": true,
  "data": { ... },
  "cost": { ... },
  "metadata": { "request_id": "..." }
}

// 失败
{
  "success": false,
  "error": {
    "code": "INVALID_MODEL",
    "message": "...",
    "detail": { "available_models": [...] }
  }
}
```

---

## 7. 模型速查与别名

### LLM 模型（`service_type: llm`）

| 厂商 | 模型名 |
|------|--------|
| OpenAI | `gpt-5.4`, `gpt-5.2`, `gpt-5-mini` |
| Anthropic | `claude-opus-4.6`, `claude-sonnet-4.6`, `claude-opus-4.5`, `claude-sonnet-4.5` |
| Google | `gemini-3.1-pro`, `gemini-3-pro`, `gemini-3-flash` |
| DeepSeek | `deepseek-3.2` |

### 图片生成模型（`service_type: image`）

| 模型名 | 厂商 |
|--------|------|
| `gpt-image-1.5` | OpenAI |
| `gemini-3-pro` / `banana-pro` | Google（团队称「大香蕉」） |
| `gemini-3.1-flash-image` / `banana-2` | Google（团队称「小香蕉」） |
| `jimeng-4.5` | 火山即梦（MCP 默认模型） |
| `flux-2-pro` | Flux |
| `midjourney-7` | Midjourney |

### 视频生成模型（`service_type: video`）

`jimeng-3.5-pro`, `veo-3.1`, `vidu-q3-pro`, `vidu-q2`, `hailuo-2.3`, `hailuo-2`, `kling-2.6`, `sora-2`

### 别名映射

| 口语/别名 | 实际 model 值 |
|-----------|-------------|
| 大香蕉 / banana-pro | `gemini-3-pro` |
| 小香蕉 / banana-2 | `gemini-3.1-flash-image` |

> **以线上为准**：模型列表可能变动，不确定时先调 `get_available_models` 或 `GET /api/v1/config/models` 确认。

---

## 8. 同步与异步任务

### 同步（默认）

请求体中不带 `async` 或设为 `false`，服务端等待处理完成后一次性返回结果。适用于 LLM 对话、快速出图等。

### 异步

请求体中设 `async: true`，服务端立即返回 `task_id`：

```json
{ "success": true, "data": { "task_id": "abc-123" } }
```

凭 `task_id` 轮询任务状态：

```
GET /api/v1/tasks/abc-123
```

直到返回终态（`completed` / `failed`）。适用于视频生成等长耗时任务。

---

## 9. 常见错误与排错

| 状态码 / 错误码 | 含义 | 排查方向 |
|----------------|------|---------|
| 401 / `INVALID_API_KEY` | Key 错误或过期 | 检查 Key 是否正确，是否已在密钥文件/环境变量中配置 |
| 403 / 权限不足 | Key 不含对应 `service_type` 权限 | 确认 Key 权限覆盖 `llm`/`image`/`video` 等 |
| 403 / `INSUFFICIENT_QUOTA` | 额度耗尽 | 联系管理员充值或更换 Key |
| 429 / `RATE_LIMIT_EXCEEDED` | 请求频率过高 | 退避重试（建议指数退避） |
| 504 / `PROVIDER_TIMEOUT` | 上游模型超时 | 重试或改用异步模式 |
| `INVALID_MODEL` | 模型名不正确 | 检查 `model` 字段拼写，调 `get_available_models` 确认 |

### MCP 特定排查

1. **MCP Server 未连接**：检查 Cursor Settings → MCP → `gbits-aiserviceproxy` 状态
2. **ping_gateway 失败**：确认内网可达（外网需 VPN），确认 MCP 配置中 Key 正确
3. **generate_image 返回空**：检查 `prompt` 是否为空，`model` 是否在可用列表中

---

## 10. 安全守则

1. **禁止**在对话、截图、PR、公开文档中粘贴完整 API Key
2. **禁止**在 AI 助手发起的 curl 命令中内联 Key 明文（`-H "Authorization: Bearer asp_..."` 这种形式）
3. **必须**通过以下安全方式传递 Key：
   - MCP Server 自动处理（推荐）
   - `invoke-aisp.ps1` 从本机文件读取（推荐）
   - 环境变量引用 `$env:AISERVICEPROXY_API_KEY`
4. Key 已在聊天或截图中出现 → 视为泄露 → 立即在管理后台轮换
5. AI 助手在示例中只写 `YOUR_API_KEY`，执行时只用变量引用

---

## 附录：Key 权限类型

API Key 可对应以下权限，调用前确认覆盖：

`llm` / `image` / `video` / `audio` / `search` / `file` / `admin`（全开）

---

## 附录：文件位置速查

| 文件 | 路径 | 用途 |
|------|------|------|
| Skill 文档 | `~/.claude/skills/gbits-aiserviceproxy-api/SKILL.md` | AI 助手参考的完整规范 |
| 包装脚本 | `~/.claude/skills/gbits-aiserviceproxy-api/scripts/invoke-aisp.ps1` | 安全调用网关 |
| 密钥文件 | `%USERPROFILE%\.gbits\aiserviceproxy_api_key.txt` | 存放 API Key（用户创建） |
| MCP 工具描述 | `mcps/user-gbits-aiserviceproxy/tools/*.json` | Cursor MCP 工具 schema |
| API 详细规范 | `~/.claude/skills/gbits-aiserviceproxy-api/reference.md` | 指向团队 HTTP_GUIDE.md |
