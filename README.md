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

> **最简单的方式**：把下面的提示词复制粘贴进 Cursor 聊天框（Agent 模式），让 AI 帮你搞定。

#### 一键安装提示词（复制粘贴进 Cursor 就行）

把下面这段话**整段复制**，粘贴到 Cursor 聊天框，**把两处需要填的地方改掉**，回车发送：

---

> 帮我安装 AIServiceProxy 工具包。请按以下步骤操作：
>
> 1. 克隆仓库：`git clone https://comgitlab.g-bits.com/cenjy/gbits-aisp-toolkit.git`（如果本地已有就跳过）
> 2. 进入 `gbits-aisp-toolkit/mcp-server` 目录，创建 Python 虚拟环境并安装依赖：`python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
> 3. 把 `gbits-aisp-toolkit/skill` 整个目录复制到 `%USERPROFILE%\.cursor\skills\gbits-aiserviceproxy-api`
> 4. 帮我编辑 `%USERPROFILE%\.cursor\mcp.json`，在 mcpServers 中添加 `gbits-aiserviceproxy`，command 指向刚才创建的 `.venv\Scripts\python.exe`，args 指向 `server.py`，env 里的 AISERVICEPROXY_API_KEY 设为：`这里换成你的Key`
> 5. 完成后帮我测试一下 AIServiceProxy 的连通性

---

**你只需要改一个地方**：把 `这里换成你的Key` 替换成管理员给你的 Key（以 `asp_` 开头的那串）。

发送后 Cursor 会自动帮你完成所有步骤。最后看到 MCP 设置页面 `gbits-aiserviceproxy` 旁边出现**绿点**就成功了。

#### 如果你想手动配

<details>
<summary>点击展开手动配置步骤</summary>

**配置 MCP Server**

1. 打开 Cursor → 点左上角 **齿轮图标** → **Settings** → 左侧找到 **MCP**
2. 点 **+ Add new global MCP server**
3. 把打开的 JSON 文件内容替换成：

```json
{
  "mcpServers": {
    "gbits-aiserviceproxy": {
      "command": "这里换成你的路径\\mcp-server\\.venv\\Scripts\\python.exe",
      "args": [
        "这里换成你的路径\\mcp-server\\server.py"
      ],
      "env": {
        "AISERVICEPROXY_API_KEY": "这里换成你的Key"
      }
    }
  }
}
```

> **路径示例**：仓库在 `D:\gbits-aisp-toolkit` 时：
> - command: `D:\\gbits-aisp-toolkit\\mcp-server\\.venv\\Scripts\\python.exe`
> - args: `D:\\gbits-aisp-toolkit\\mcp-server\\server.py`
>
> JSON 里的路径要用 `\\`（双反斜杠）。

4. 保存，确认旁边出现**绿点**就成功了

**配置 Skill**

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.cursor\skills\gbits-aiserviceproxy-api"
```

**验证**

在 Cursor 聊天框里输入：「帮我测试一下 AIServiceProxy 的连通性」

</details>

---

### 用 Codex 的同事看这里

> **最简单的方式**：把下面的提示词复制粘贴进 Codex，让 Codex 帮你搞定一切。

#### 一键安装提示词（复制粘贴进 Codex 就行）

把下面这段话**整段复制**，粘贴到 Codex 对话框，然后**把里面两处需要你填的地方改掉**，回车发送：

---

> 帮我安装 AIServiceProxy 工具包。请按以下步骤操作：
>
> 1. 克隆仓库：`git clone https://comgitlab.g-bits.com/cenjy/gbits-aisp-toolkit.git`（如果本地已有就跳过）
> 2. 进入 `gbits-aisp-toolkit/mcp-server` 目录，创建 Python 虚拟环境并安装依赖：`python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt`
> 3. 把 `gbits-aisp-toolkit/skill` 整个目录复制到 `%USERPROFILE%\.codex\skills\gbits-aiserviceproxy-api`
> 4. 在 `%USERPROFILE%\.codex\config.toml` 末尾追加 MCP 配置，command 指向刚才创建的 `.venv\Scripts\python.exe`，args 指向 `server.py`，env 里的 AISERVICEPROXY_API_KEY 设为：`这里换成你的Key`
> 5. 完成后帮我测试一下 AIServiceProxy 的连通性

---

**你只需要改一个地方**：把 `这里换成你的Key` 替换成管理员给你的 Key（以 `asp_` 开头的那串）。

发送后 Codex 会自动帮你完成所有步骤。看到「连接成功」就说明装好了。

#### 如果你想手动配

<details>
<summary>点击展开手动配置步骤</summary>

**配置 MCP Server**

打开终端，输入：

```powershell
codex mcp add gbits-aiserviceproxy --env AISERVICEPROXY_API_KEY=你的Key -- "你的仓库路径\mcp-server\.venv\Scripts\python.exe" "你的仓库路径\mcp-server\server.py"
```

> **举个例子**：如果仓库在 `D:\gbits-aisp-toolkit`，Key 是 `asp_abc123`，完整命令是：
>
> ```powershell
> codex mcp add gbits-aiserviceproxy --env AISERVICEPROXY_API_KEY=asp_abc123 -- "D:\gbits-aisp-toolkit\mcp-server\.venv\Scripts\python.exe" "D:\gbits-aisp-toolkit\mcp-server\server.py"
> ```

或者手动编辑 `%USERPROFILE%\.codex\config.toml`，在末尾加上：

```toml
[mcp_servers.gbits-aiserviceproxy]
command = "你的仓库路径\\mcp-server\\.venv\\Scripts\\python.exe"
args = ["你的仓库路径\\mcp-server\\server.py"]

[mcp_servers.gbits-aiserviceproxy.env]
AISERVICEPROXY_API_KEY = "你的Key"
```

**配置 Skill**

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.codex\skills\gbits-aiserviceproxy-api"
```

**验证**

启动 Codex，输入：「帮我测试一下 AIServiceProxy 的连通性」

</details>

---

### 用 Claude Code 的同事看这里

> **最简单的方式**：把下面的提示词复制粘贴进 Claude Code，让 AI 帮你搞定。

#### 一键安装提示词（复制粘贴进 Claude Code 就行）

---

> 帮我安装 AIServiceProxy 工具包。请按以下步骤操作：
>
> 1. 克隆仓库：`git clone https://comgitlab.g-bits.com/cenjy/gbits-aisp-toolkit.git`（如果本地已有就跳过）
> 2. 进入 `gbits-aisp-toolkit/mcp-server` 目录，创建 Python 虚拟环境并安装依赖：`python -m venv .venv && .venv/Scripts/activate && pip install -r requirements.txt`
> 3. 把 `gbits-aisp-toolkit/skill` 整个目录复制到 `~/.claude/skills/gbits-aiserviceproxy-api`
> 4. 在当前项目目录创建 `.mcp.json`，添加 `gbits-aiserviceproxy`，command 指向 `.venv/Scripts/python.exe`，args 指向 `server.py`，env 里的 AISERVICEPROXY_API_KEY 设为：`这里换成你的Key`
> 5. 完成后帮我测试一下 AIServiceProxy 的连通性

---

**你只需要改一个地方**：把 `这里换成你的Key` 替换成管理员给你的 Key。

#### 如果你想手动配

<details>
<summary>点击展开手动配置步骤</summary>

**配置 MCP Server**

在项目目录下创建或编辑 `.mcp.json`：

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

**配置 Skill**

```powershell
Copy-Item -Recurse "你的仓库路径\skill" "$HOME\.claude\skills\gbits-aiserviceproxy-api"
```

**验证**

在 Claude Code 中输入：「帮我测试一下 AIServiceProxy 的连通性」

</details>

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

## 实际使用示例：用大香蕉出图

下面演示**配好以后**，在 Claude Code 中用大香蕉（gemini-3-pro）生成一张图片的完整过程。Cursor 和 Codex 的用法完全一样，只是界面不同。

### 示例 1：最简单的用法

你在聊天框里输入：

> 用大香蕉帮我画一只正在喷火的小龙，卡通风格

AI 会自动：
1. 识别到「大香蕉」→ 使用 `gemini-3-pro` 模型
2. 调用 MCP 的 `generate_image` 工具
3. 把图片下载到本地
4. 回复你图片的保存路径

你不需要写任何代码或命令，直接说就行。

### 示例 2：指定保存位置

> 用大香蕉画一个像素风格的森林场景，存到桌面

AI 会把 `save_path` 设为你的桌面路径，图片直接出现在桌面上。

### 示例 3：批量出图

> 用 banana-pro 帮我生成 3 张图：
> 1. 一只火焰猎犬，像素风，64x64，透明背景
> 2. 一只岩石犀牛幼崽，像素风，64x64，透明背景
> 3. 一只水系海豚，像素风，64x64，透明背景
>
> 全部存到 D:\my-project\assets 目录

AI 会连续调用 3 次 `generate_image`，每张图自动命名并存到你指定的目录。

### 示例 4：先查模型再出图

如果你不确定现在有哪些模型可以用：

> 帮我查一下现在有哪些出图模型

AI 会调用 `get_available_models` 返回当前可用列表，然后你再选一个：

> 用 midjourney-7 画一个赛博朋克风格的城市夜景

### 背后发生了什么？

当你说「用大香蕉画一只小猫」时，AI 在后台做了这些（你不用管，了解一下就行）：

```
你说：「用大香蕉画一只小猫」
        │
        ▼
AI 读取 Skill 中的别名映射：大香蕉 → gemini-3-pro
        │
        ▼
AI 调用 MCP 工具 generate_image：
  prompt = "一只小猫"
  model  = "gemini-3-pro"
        │
        ▼
MCP Server (server.py) 发送请求到内网网关：
  POST http://aitools.g-bits.com/aiserviceproxy/api/v1/image/generate
  （Key 在进程内自动带上，你看不到也不用管）
        │
        ▼
网关返回图片 URL → server.py 自动下载到本地
        │
        ▼
AI 告诉你：「图片已保存到 D:\xxx\20260403_142530_一只小猫.png」
```

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
