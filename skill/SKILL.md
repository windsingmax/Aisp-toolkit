---
name: gbits-aiserviceproxy-api
version: "1.0.5"
description: 吉比特内网 AIServiceProxy HTTP 网关（aitools.g-bits.com/aiserviceproxy）的接入、请求体与排错。含图像/LLM 等能力与 banana-pro 别名；Bearer 鉴权；**须避免审批框暴露 Key**（环境变量或本 skill 附带 invoke-aisp.ps1 从本机文件读 Key）。口语：出图、大香蕉、curl/网关。纯写 Cursor SKILL 文档且不调网关则不要用本 skill。
---

# 吉比特 AIServiceProxy API（速查）

## 版本记录（Version）
- 维护时请将上方 YAML 的 `version` 与本节**最新一条**保持同步；新版本在列表**顶部**追加一行说明即可。
- **1.0.5** — 明确 Git Bash 与 PowerShell 差异；**禁止**「变量未生效就从文件读 Key 拼进 curl」；新增 `scripts/invoke-aisp.ps1` 包装调用（审批框只出现脚本路径）。
- **1.0.4** — 硬性规定：助手不得在可回显的 Bash/curl 命令中内联用户 API Key；须用环境变量；补充 banana-pro 与网关命名说明。
- **1.0.3** — 图像生成当前可用模型清单（团队口径）+ 别名与「大香蕉」口语对应说明。
- **1.0.2** — 明确「无 Key 不可用」与用户同步；密钥安全规范；文档摘录模型速查表；说明以 `GET /config/models` 为准。
- **1.0.1** — 扩展 `description` 触发词（出图/修图/图生图等），并区分「写 Skill 文档」与「调网关 API」。
- **1.0.0** — 初版：速查、cURL、`reference` 指向 `HTTP_GUIDE.md`。

## Preconditions（前提条件）

- 已具备可访问内网 `aitools.g-bits.com` 的环境（外网不可用时需 VPN/内网）。
- **必须有有效 API Key**：无 Key 或 Key 无对应权限时，任何接口都会失败（通常 401/403）。**助手须先与用户确认**：用户是否已在安全位置配置好 Key，或是否同意仅在本地终端用环境变量注入，**不要把 Key 粘贴进聊天**。
- 详细字段、可选参数、各业务接口完整示例见 [reference.md](reference.md)。
- **边界**：本 skill 只管 **AIServiceProxy 的 HTTP 调用**；用户若只想学写 `.cursor/skills` 里的 `SKILL.md`（与网关无关），应走通用 Skill 入门，而不是本文件。

## 密钥与安全（Security）

- **禁止**在对话、截图、录屏、PR、公开文档中粘贴**完整**生产 Key；聊天与 IDE 历史可能被记录。
- **推荐**：在本机设置环境变量（示例名，团队可统一）`AISERVICEPROXY_API_KEY`，终端里 `curl`/脚本使用 `$env:AISERVICEPROXY_API_KEY`（PowerShell）或 `$AISERVICEPROXY_API_KEY`（bash），**不要**把展开后的值发回对话。
- **若 Key 已出现在聊天或截图中**：视为泄露，**立即在管理后台轮换/作废**并换新 Key。
- **助手行为**：需要演示命令时只写 `YOUR_API_KEY` 或「从环境变量读取」；**不要复述**用户发来的真实 Key。

## 助手调用终端 / Bash 的硬性规则（必守）

**问题背景**：Claude Code / Cursor 等工具会把**即将执行的命令全文**显示在界面里（含 `-H "Authorization: Bearer …"`）。若把用户提供的 Key **直接写进命令参数**，Key 会进入**会话记录、终端历史、截图**，等同二次泄露。

1. **禁止**：在助手发起或展示的 **Bash / `run_terminal_cmd` / curl 命令字符串**中出现用户真实 Key 的任何片段（包括 `asp_` 开头的长串）。**禁止** `-H "Authorization: Bearer <粘贴的完整 key>"` 这种形式。
2. **必须**：先让用户在**本机**把 Key 写入环境变量（仅用户本机可见，不必把变量值贴回对话），例如 PowerShell 当前会话：  
   `$env:AISERVICEPROXY_API_KEY = '（用户本地粘贴，勿发给助手）'`  
   或用户级持久化见团队规范。助手后续命令**只能**使用：  
   `-H "Authorization: Bearer $env:AISERVICEPROXY_API_KEY"`（PowerShell）或 bash 下 `$AISERVICEPROXY_API_KEY`。
3. **若用户只在聊天里贴了 Key**：助手**不得**把该 Key 复制进任何可展示命令；应提示：「请在本机终端自行设置 `AISERVICEPROXY_API_KEY` 后回复已就绪」，再仅用**变量引用**执行 curl。
4. **说明话术**：向用户解释「不是不信任你，而是工具会把整条命令记入日志；用环境变量可避免密钥出现在对话与终端回显里」。
5. **banana 与网关名称**：网关上模型 ID 为 **`gemini-3-pro`**，别名为 **`banana-pro`**（中间是**连字符**）。用户口语「banana pro」应映射为 **`banana-pro` 或 `gemini-3-pro`**，不要在文档里写带空格的 `banana pro` 当作 model 字段。

### 为什么「环境变量 + curl」仍会失败或仍暴露 Key？

1. **Claude Code / Cursor 的「Bash」常是 Git Bash（MSYS）**，不是 PowerShell：  
   - **`$env:AISERVICEPROXY_API_KEY` 在 Bash 里无效**（那是 PowerShell 语法），变量为空时模型容易乱试「别的办法」。  
   - 在 **Bash** 里应使用：`export AISERVICEPROXY_API_KEY='…'` 然后 `curl ... -H "Authorization: Bearer $AISERVICEPROXY_API_KEY"`。  
   - 注意：若把 **带 Key 的 `export` 整行**交给工具执行，**审批框里仍会出现一次明文 Key**；最稳是用户在 **IDE 外的本机终端**自己 `export`，再让助手只跑不含密钥的 `curl`（仅含 `$AISERVICEPROXY_API_KEY`）。

2. **禁止「捷径」（与直接贴 Key 等价）**  
   - **禁止**以「环境变量在当前会话没生效」「读用户机器上的 key 文件」为由，把文件里的 Key **读出来写进** `-H "Authorization: Bearer asp_……"`。  
   - **禁止**使用「我直接用文件里的 key 来执行」这类话术；审批 UI、会话记录、终端历史仍会**完整展示**该行。  
   - **禁止**在命令行使用 `$(cat ~/.key)` / `type key.txt` 把密钥展开后仍拼进**会被工具展示**的单行 curl（若审批展示展开后的命令，同样泄露）。

3. **推荐：包装脚本（审批里通常只出现「脚本路径 + 参数」，不出现 Key）**  
   - 使用本 skill 目录下 [`scripts/invoke-aisp.ps1`](scripts/invoke-aisp.ps1)。  
   - 用户**一次性**在本机创建密钥文件（**不要**把内容发给助手）：`%USERPROFILE%\.gbits\aiserviceproxy_api_key.txt`（单行、仅 Key）。  
   - 助手**仅**执行类似（路径按用户仓库调整）：  
     `powershell -NoProfile -ExecutionPolicy Bypass -File ".cursor/skills/gbits-aiserviceproxy-api/scripts/invoke-aisp.ps1" -Method POST -Uri "http://aitools.g-bits.com/aiserviceproxy/api/v1/image/generate" -BodyPath "C:/Users/xxx/tmp_img_body.json"`  
   - Key 只在 **脚本进程内**从文件读入，**不要**把 Key 写进 `-File` 这一行的参数里。

## Workflow / Instructions（执行步骤）

1. **与用户对齐密钥（且不泄露）**：确认 Key 已通过 **(a)** 用户本机私密文件 + `invoke-aisp.ps1`，或 **(b)** 在与工具**相同 shell 类型**下设置的变量（Bash 用 `export`，PowerShell 用 `$env:`）。**绝不**把 Key 拼进助手发起且会被审批展示的 curl 行；**禁止**因变量未生效就改从文件「抄 Key 到命令行」。
2. **拼完整 URL**：`基础 URL + 路径`（见下表）。
3. **Header**：`Authorization: Bearer` 后**仅接环境变量展开**（由 shell 在本地展开，不把值写进发给工具的参数字符串）；`Content-Type: application/json`（POST/PUT 等）。
4. **Body**：按服务传 `service_type`、`model` 等；长耗时接口可用 `async=true` 后凭 `task_id` 轮询 `GET /api/v1/tasks/{task_id}`。
5. **解析响应**：先看 `success`；失败读 `error.code` / `error.message`；成功数据在 `data`，追踪用 `metadata.request_id`。
6. **不确定模型名**：**以线上为准**——先调 `GET /api/v1/config/models`（可带 `service_type`、`vendor` 查询参数）；下方「模型速查」摘自 `HTTP_GUIDE.md`，可能与线上配置迭代不一致。

### 基础 URL 与常用路径（最小）

| 用途 | 方法 | 路径（接在基础 URL 后） |
|------|------|-------------------------|
| 基础前缀 | - | `http://aitools.g-bits.com/aiserviceproxy` |
| LLM 对话（含多模态同路径） | POST | `/api/v1/llm/chat` |
| 图片生成 | POST | `/api/v1/image/generate` |
| 视频生成 | POST | `/api/v1/video/generate` |
| 任务查询 | GET | `/api/v1/tasks/{task_id}` |
| 可用模型等配置 | GET | `/api/v1/config/models` |

### 认证（必须）

```http
Authorization: Bearer YOUR_API_KEY
```

### 统一响应（概念）

- 成功：`success: true`，业务在 `data`，可选 `cost`、`metadata`。
- 失败：`success: false`，`error.code` / `error.message`；参数类错误可能在 `error.detail` 中带 `available_models` 等提示。

### LLM 非流式最小请求示例

`POST {基础URL}/api/v1/llm/chat`

```json
{
  "service_type": "llm",
  "model": "gpt-5.2",
  "messages": [
    { "role": "user", "content": "你好" }
  ],
  "stream": false
}
```

### curl 示例（命令行）

**助手代跑 / 防泄露写法（PowerShell，推荐）**：先由用户在本机设好 `$env:AISERVICEPROXY_API_KEY`，命令里**只出现变量名**：

```powershell
# 查询模型（命令中不得出现 asp_ 密钥明文）
curl.exe -s "http://aitools.g-bits.com/aiserviceproxy/api/v1/config/models" `
  -H "Authorization: Bearer $env:AISERVICEPROXY_API_KEY"
```

```powershell
# LLM 非流式（JSON 可放文件后用 -d @body.json）
curl.exe -s -X POST "http://aitools.g-bits.com/aiserviceproxy/api/v1/llm/chat" `
  -H "Authorization: Bearer $env:AISERVICEPROXY_API_KEY" `
  -H "Content-Type: application/json" `
  -d '{"service_type":"llm","model":"gpt-5.2","messages":[{"role":"user","content":"你好"}],"stream":false}'
```

**bash**（同理只引用变量）：`-H "Authorization: Bearer $AISERVICEPROXY_API_KEY"`

**文档/教学用占位**（可复制给同事，勿填真 Key）：`YOUR_API_KEY` 仅用于静态文档，**助手执行时改用环境变量**，勿把 `YOUR_API_KEY` 替换成用户聊天里的真实字符串再执行。

Windows PowerShell 若对引号报错，可把 JSON 放进文件后用 `curl.exe ... -d @body.json`，或改用 `Invoke-RestMethod`。

**更稳妥（避免审批框出现 Bearer 明文）**：见上文 **包装脚本** `scripts/invoke-aisp.ps1` + `%USERPROFILE%\.gbits\aiserviceproxy_api_key.txt`。

### 同步 / 异步

- 默认同步：`async=false`（或省略），服务端内部等到结果再返回。
- 异步：`async=true`，先拿 `data.task_id`，再查任务接口直至完成。

### API Key 权限类型（与 403 相关）

`llm` / `image` / `video` / `audio` / `search` / `file` / `admin`（管理员全开）。调用前确认 Key 权限覆盖当前 `service_type`。

### 模型速查（摘自 `HTTP_GUIDE.md`，**以 `GET /api/v1/config/models` 线上结果为准**）

**LLM**（`POST /api/v1/llm/chat`，`service_type`: `llm`）

| Provider / 厂商 | 文档中的模型示例 |
|-----------------|------------------|
| OpenAI | `gpt-5.4`, `gpt-5.2`, `gpt-5-mini` |
| Anthropic | `claude-opus-4.6`, `claude-sonnet-4.6`, `claude-opus-4.5`, `claude-sonnet-4.5` |
| Google | `gemini-3.1-pro`, `gemini-3-pro`, `gemini-3-flash` |
| DeepSeek | `deepseek-3.2` |

**图片生成**（`POST /api/v1/image/generate`；文生图 / 图生图 / 遮罩编辑见文档第三章）

当前环境**常用/可用**图像生成模型（团队口径；**仍以** `GET /api/v1/config/models?service_type=image` **线上为准**）：

- `gpt-image-1.5`（OpenAI）
- `gemini-3-pro`、`gemini-3.1-flash-image`（Google；见下方**别名**）
- `jimeng-4.5`（火山即梦）
- `flux-2-pro`（Flux）
- `midjourney-7`（Midjourney）

**别名与口语（便于同事对齐说法）**

| 请求里可写的 model / 别名 | 等价主模型 | 备注 |
|---------------------------|------------|------|
| `banana-pro` | `gemini-3-pro` | 文档定义别名；团队口语 **「大香蕉」** 一般即指 **`gemini-3-pro` / `banana-pro`** 这条 Google 出图线。 |
| `banana-2` | `gemini-3.1-flash-image` | 文档定义别名；相对偏快出图时可选用。 |

若用户只说「大香蕉」「香蕉模型」，优先理解为 **`gemini-3-pro` 或 `banana-pro`**；不确定时再问一句或查 `/config/models`。

历史文档或示例里可能出现 `dall-e-3` 等，**是否仍开放以线上配置为准**。

**视频**（`POST /api/v1/video/generate`；文档 4.1 表格）

`jimeng-3.5-pro`, `veo-3.1`, `vidu-q3-pro`, `vidu-q2`, `hailuo-2.3`, `hailuo-2`, `kling-2.6`, `sora-2`（别名与能力见 `HTTP_GUIDE.md` 第四章）。

## Output Format（输出格式）

- **请求摘要**：方法、完整 URL、是否异步。
- **响应解读**：`success`、关键 `data` 字段、或 `error.code` 与建议下一步。
- **可追溯**：附上 `metadata.request_id`（若有）。

## Verification Checklist（验收清单）

- [ ] 已与用户确认 Key 可用；**未**在对话中回显完整明文 Key。
- [ ] 助手展示的 **Bash/curl 命令**中**仅**出现 `$env:AISERVICEPROXY_API_KEY` 或 `$AISERVICEPROXY_API_KEY`，**无** `asp_` 等密钥字面量。
- [ ] `Authorization` 已带且未把真实 Key 写进公开文档或代码库。
- [ ] URL 以 `http://aitools.g-bits.com/aiserviceproxy` 为前缀且路径与文档一致。
- [ ] `model` + `service_type` 与配置接口返回一致，避免 `INVALID_MODEL`。
- [ ] 异步任务已用 `task_id` 查询直至终态。

## Common Pitfalls（常见问题）

- 401 / `INVALID_API_KEY`：Key 错误或过期。
- 403 / 权限：Key 不含对应 `service_type` 或额度 `INSUFFICIENT_QUOTA`。
- 429：`RATE_LIMIT_EXCEEDED`，需退避重试。
- 504 / `PROVIDER_TIMEOUT`：上游超时，可重试或改异步。
- 流式（SSE）与非流式字段不同，实现前查 [reference.md](reference.md) 对应章节。
- **勿在 skill、示例代码、聊天记录、终端回显截图中粘贴生产环境真实 API Key**；已在聊天中出现的 Key 须轮换。
- **勿**在 Claude Code / Cursor 工具调用的命令字符串里内联 Bearer Token：界面会完整展示命令，密钥会进会话与终端历史；**必须**用环境变量。
