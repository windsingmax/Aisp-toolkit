# 完整 API 规范

- **团队文档**：与本 skill 同仓库根目录的 [`HTTP_GUIDE.md`](../../../HTTP_GUIDE.md)（若 skill 只放在 `~/.claude/skills/` 而无仓库，请向团队索取该文件或仅用下方线上接口）。
- **以线上为准**：内网调用 `GET .../api/v1/config/models`（及第十一章其它 config 接口）获取**当前**可用模型与能力。

内容包含：LLM / 图片 / 视频 / 音频 / 搜索 / 文件 / 任务 / 账户 / 管理 / 配置查询、SSE 流式、Webhook、限流、最佳实践等。
