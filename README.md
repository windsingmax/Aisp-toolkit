# gbits-aisp-toolkit

让 AI 助手（Cursor / Codex / Claude Code）能直接调用公司内网的 AIServiceProxy 网关。

配好之后你可以直接对 AI 说「帮我用大香蕉出一张图」「查一下有哪些模型」，AI 会自动帮你调接口。

---

## 支持的 AI 工具

| AI 工具 | Skill | MCP Server |
|---------|-------|------------|
| Cursor | 支持 | 支持 |
| Codex CLI | 支持 | 支持 |
| Claude Code | 支持 | 支持 |

---

## 第一步：下载本仓库

打开终端（PowerShell），复制粘贴下面的命令：

```powershell
git clone https://comgitlab.g-bits.com/cenjy/gbits-aisp-toolkit.git
```

记住下载到的文件夹路径，后面要用（比如 `D:\gbits-aisp-toolkit`）。

---

## 第二步：安装 Python 依赖

```powershell
cd gbits-aisp-toolkit\mcp-server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

> 需要 Python 3.10 以上。不确定有没有装？终端输入 `python --version` 看一下。

---

## 第三步：拿到你的 API Key

找管理员要一个 AIServiceProxy 的 API Key（以 `asp_` 开头的一串字符）。

**注意**：拿到 Key 以后不要发到群里、不要截图、不要贴进文档，只在下面的配置步骤中使用。

---

## 第四步：配置你的 AI 工具

根据你用的 AI 工具，选对应的配置方法：

---

### 用 Cursor 的同事看这里

#### 配置 MCP Server（让 AI 能出图、查模型）

1. 打开 Cursor
2. 点左上角 **齿轮图标** → 进入 **Settings**
3. 左侧找到 **MCP** 一栏
4. 点 **+ Add new global MCP server**
5. 会打开一个 JSON 文件，把里面的内容替换成：

```json
{
  "mcpServers": {
    "gbits-aiserviceproxy": {
      "command": "这里换成你的路径/mcp-server/.venv/Scripts/python.exe",
      "args": [
        "这里换成你的路径/mcp-server/server.py"
      ],
      "env": {
        "AISERVICEPROXY_API_KEY": "这里换成你的Key"
      }
    }
  }
}
```

> **路径示例**：如果你把仓库下载到了 `D:\gbits-aisp-toolkit`，那就是：
> - command: `D:\\gbits-aisp-toolkit\\mcp-server\\.venv\\Scripts\\python.exe`
> - args 里: `D:\\gbits-aisp-toolkit\\mcp-server\\server.py`
>
> 注意 JSON 里的路径要用 `\\`（双反斜杠）。

6. 保存文件，回到 MCP 设置页面，确认 `gbits-aiserviceproxy` 旁边出现**绿点**就说明成功了

#### 配置 Skill（让 AI 懂得怎么用网关）

打开终端，复制粘贴：

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.cursor\skills\gbits-aiserviceproxy-api"
```

#### 验证

在 Cursor 聊天框里输入：「帮我测试一下 AIServiceProxy 的连通性」

看到「连接成功」就好了！

---

### 用 Codex 的同事看这里

#### 配置 MCP Server

打开终端，输入：

```powershell
codex mcp add gbits-aiserviceproxy --env AISERVICEPROXY_API_KEY=你的Key -- "你的仓库路径\mcp-server\.venv\Scripts\python.exe" "你的仓库路径\mcp-server\server.py"
```

> **举个例子**：如果仓库在 `D:\gbits-aisp-toolkit`，Key 是 `asp_abc123`，完整命令是：
>
> ```powershell
> codex mcp add gbits-aiserviceproxy --env AISERVICEPROXY_API_KEY=asp_abc123 -- "D:\gbits-aisp-toolkit\mcp-server\.venv\Scripts\python.exe" "D:\gbits-aisp-toolkit\mcp-server\server.py"
> ```

如果更习惯手动编辑，也可以打开 `%USERPROFILE%\.codex\config.toml`，在末尾加上：

```toml
[mcp_servers.gbits-aiserviceproxy]
command = "你的仓库路径\\mcp-server\\.venv\\Scripts\\python.exe"
args = ["你的仓库路径\\mcp-server\\server.py"]

[mcp_servers.gbits-aiserviceproxy.env]
AISERVICEPROXY_API_KEY = "你的Key"
```

#### 配置 Skill

打开终端，复制粘贴：

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.codex\skills\gbits-aiserviceproxy-api"
```

#### 验证

启动 Codex，输入：「帮我测试一下 AIServiceProxy 的连通性」

---

### 用 Claude Code 的同事看这里

#### 配置 MCP Server

在你的项目目录下创建或编辑 `.mcp.json` 文件：

```json
{
  "mcpServers": {
    "gbits-aiserviceproxy": {
      "command": "你的仓库路径/mcp-server/.venv/Scripts/python.exe",
      "args": [
        "你的仓库路径/mcp-server/server.py"
      ],
      "env": {
        "AISERVICEPROXY_API_KEY": "你的Key"
      }
    }
  }
}
```

#### 配置 Skill

打开终端，复制粘贴：

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.claude\skills\gbits-aiserviceproxy-api"
```

#### 验证

在 Claude Code 中输入：「帮我测试一下 AIServiceProxy 的连通性」

---

## 配好以后能干什么？

直接用自然语言让 AI 帮你操作：

| 你说的话 | AI 会做的事 |
|---------|------------|
| 「帮我出一张图：一只可爱的小猫」 | 调用 `generate_image`，自动生成并下载图片 |
| 「用大香蕉出图」 | 用 gemini-3-pro 模型生成图片 |
| 「查一下有哪些出图模型」 | 调用 `get_available_models` 查询 |
| 「测试一下网关连通性」 | 调用 `ping_gateway` 检查 Key 和网络 |

## 常用出图模型

| 说法 | 实际模型 |
|------|---------|
| 「用即梦」 | jimeng-4.5（默认） |
| 「用大香蕉」 | gemini-3-pro |
| 「用小香蕉」 | gemini-3.1-flash-image |
| 「用 MJ」 | midjourney-7 |
| 「用 GPT 出图」 | gpt-image-1.5 |

---

## 遇到问题？

| 问题 | 解决办法 |
|------|---------|
| MCP 旁边是红点 / 连接失败 | 检查路径有没有写错，Key 有没有粘贴完整 |
| 提示 401 / Key 无效 | Key 过期了，找管理员重新要一个 |
| 提示 403 / 权限不足 | Key 没有出图/对话的权限，找管理员开通 |
| 提示网络错误 | 确认你在公司内网（或开了 VPN） |
| 什么模型都找不到 | 先让 AI 执行「查一下有哪些模型」确认 |

---

## 仓库结构

```
gbits-aisp-toolkit/
├── mcp-server/             # MCP Server 源码
│   ├── server.py           # 主程序
│   └── requirements.txt    # Python 依赖
├── skill/                  # AI Skill 配置
│   ├── SKILL.md            # AI 参考规范
│   ├── reference.md        # API 参考
│   └── scripts/
│       └── invoke-aisp.ps1 # 安全调用脚本
└── docs/
    └── guide.md            # 详细技术文档
```

## 详细文档

技术细节请看 [docs/guide.md](docs/guide.md)。
