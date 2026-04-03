# gbits-aisp-toolkit

吉比特内网 AIServiceProxy 网关的 AI 助手工具集，包含 **MCP Server** 和 **Cursor/Claude Skill** 两部分。

## 仓库结构

```
gbits-aisp-toolkit/
├── mcp-server/             # MCP Server（Python）
│   ├── server.py           # 服务主入口
│   └── requirements.txt    # Python 依赖
├── skill/                  # Cursor / Claude Skill
│   ├── SKILL.md            # Skill 主文档（AI 参考规范）
│   ├── reference.md        # API 详细参考
│   └── scripts/
│       └── invoke-aisp.ps1 # 安全调用包装脚本
└── docs/
    └── guide.md            # 完整使用指南
```

## 快速开始

### 方式一：MCP Server（推荐）

MCP Server 让 Cursor/Claude 等 AI 助手直接调用网关接口，无需手动 curl，无需在终端暴露 API Key。

**1. 安装依赖**

```bash
cd mcp-server
python -m venv .venv
.venv/Scripts/activate    # Windows
pip install -r requirements.txt
```

**2. 在 Cursor 中配置 MCP**

打开 Cursor Settings → Features → MCP → Add New MCP Server：

- **Name**: `gbits-aiserviceproxy`
- **Type**: `command`
- **Command**: `<仓库路径>/mcp-server/.venv/Scripts/python.exe`
- **Args**: `<仓库路径>/mcp-server/server.py`
- **Env**: `AISERVICEPROXY_API_KEY` = `你的 API Key`

**3. 测试连通性**

在 Cursor 聊天中输入：「帮我测试一下 AIServiceProxy 的连通性」

### 方式二：Skill 脚本

适用于 MCP 未覆盖的接口（LLM 对话、视频生成等）。

**1. 创建密钥文件**（一次性，不要把 Key 发给 AI）

```powershell
mkdir "$HOME\.gbits" -Force
notepad "$HOME\.gbits\aiserviceproxy_api_key.txt"
```

**2. 安装 Skill**

将 `skill/` 目录复制到对应位置：

```powershell
# Cursor
Copy-Item -Recurse skill "$HOME\.cursor\skills\gbits-aiserviceproxy-api"

# Claude Code
Copy-Item -Recurse skill "$HOME\.claude\skills\gbits-aiserviceproxy-api"
```

**3. 使用**

Skill 脚本通过 `invoke-aisp.ps1` 安全调用网关，审批框中不会出现 API Key：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File `
  "skill/scripts/invoke-aisp.ps1" `
  -Method GET `
  -Uri "http://aitools.g-bits.com/aiserviceproxy/api/v1/config/models"
```

## MCP 提供的工具

| 工具 | 功能 |
|------|------|
| `ping_gateway` | 测试网关连通性与 Key 有效性 |
| `get_available_models` | 查询可用模型列表，支持按类型筛选 |
| `generate_image` | 文生图，支持别名（大香蕉→gemini-3-pro），自动下载到本地 |

## 支持的模型（部分）

| 类型 | 模型 |
|------|------|
| LLM | gpt-5.4, claude-sonnet-4.6, gemini-3-pro, deepseek-3.2 |
| 图片 | jimeng-4.5, gemini-3-pro (banana-pro), gpt-image-1.5, flux-2-pro |
| 视频 | veo-3.1, kling-2.6, sora-2 |

> 以 `get_available_models` 或 `GET /api/v1/config/models` 线上结果为准。

## 安全须知

- **禁止**在对话、PR、截图中暴露 API Key
- MCP Server 通过环境变量传入 Key，进程内使用，不会出现在终端
- Skill 脚本从本机文件 `~/.gbits/aiserviceproxy_api_key.txt` 读取 Key
- 详见 [docs/guide.md](docs/guide.md) 安全守则章节

## 前置要求

- Python 3.10+
- 内网可达 `aitools.g-bits.com`（外网需 VPN）
- 有效的 AIServiceProxy API Key（需含对应 service_type 权限）

## 详细文档

- [完整使用指南](docs/guide.md) — Skill + MCP + curl 三种调用方式详解
- [Skill 规范](skill/SKILL.md) — AI 助手参考的完整规范
- [API 参考](skill/reference.md) — 指向团队 HTTP_GUIDE.md
