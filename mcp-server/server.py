import os
import re
import time
import httpx
import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Gbits-AIServiceProxy")

BASE_URL = "http://aitools.g-bits.com/aiserviceproxy/api/v1"
DEFAULT_SAVE_DIR = r"e:\claude\img"
DEFAULT_VIDEO_DIR = r"e:\claude\video"

def get_headers():
    api_key = os.getenv("AISERVICEPROXY_API_KEY")
    if not api_key:
        raise ValueError("未设置环境变量 AISERVICEPROXY_API_KEY，请在 Cursor 的 MCP 配置中添加该环境变量。")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def resolve_model_alias(model: str) -> str:
    """处理口语别名到真实模型 ID 的映射"""
    aliases = {
        "大香蕉": "gemini-3-pro",
        "banana pro": "gemini-3-pro",
        "banana-pro": "gemini-3-pro",
        "banana2": "gemini-3.1-flash-image",
        "小香蕉": "gemini-3.1-flash-image",
    }
    return aliases.get(model.lower(), model)

def make_filename(prompt: str, ext: str = "png") -> str:
    """用时间戳 + prompt 前几个字生成不重复的文件名"""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 取 prompt 前 20 个字符，去掉非法文件名字符
    slug = re.sub(r'[\\/:*?"<>|\s]', "_", prompt[:20]).strip("_")
    return f"{ts}_{slug}.{ext}"

def download_file(url: str, save_dir: str, filename: str) -> str:
    """下载文件到指定目录，返回本地绝对路径"""
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)
    local_path = save_path / filename
    with httpx.stream("GET", url, timeout=60.0, follow_redirects=True) as r:
        r.raise_for_status()
        with open(local_path, "wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return str(local_path.resolve())


@mcp.tool()
def ping_gateway() -> str:
    """
    测试与吉比特内部 AI 网关的连通性。
    用于验证 MCP Server 是否正确读取了 API Key 并且能够访问内网。
    """
    try:
        response = httpx.get(f"{BASE_URL}/config/models", headers=get_headers(), timeout=10.0)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                total = data.get("data", {}).get("total", 0)
                return f"✅ 连接成功！API Key 鉴权通过，当前网关共支持 {total} 个模型。"
            return f"❌ 网关返回错误：{data.get('error', {}).get('message')}"
        elif response.status_code == 401:
            return "❌ 鉴权失败 (401)：API Key 无效或已过期。"
        return f"❌ HTTP 错误：{response.status_code}"
    except ValueError as e:
        return f"❌ 配置错误：{e}"
    except httpx.RequestError as e:
        return f"❌ 网络请求失败（请检查是否在内网）：{e}"


@mcp.tool()
def generate_image(
    prompt: str,
    model: str = "jimeng-4.5",
    save_path: str = ""
) -> str:
    """
    调用吉比特内部网关生成图片并自动下载到本地。
    当用户需要出图、画图、生成图像时使用此工具。

    Args:
        prompt: 图片的详细描述提示词。
        model: 模型名称。默认 jimeng-4.5。
               别名支持：大香蕉 / banana-pro → gemini-3-pro；小香蕉 / banana2 → gemini-3.1-flash-image。
        save_path: 本地保存目录。
                   【重要】用户说"存到桌面"请传入 C:\\Users\\cenjy\\Desktop；
                   用户说"存到 XXX 目录"请传入对应路径；
                   用户未指定则留空，工具自动存到默认路径 e:\\claude\\img。
                   【禁止】不得在工具调用完成后再用 Copy-Item 或其他命令二次复制，
                   必须在调用本工具时直接通过 save_path 指定目标路径，图片只保存一份。
    """
    try:
        model = resolve_model_alias(model)
        headers = get_headers()

        payload = {
            "model": model,
            "prompt": prompt,
            "n": 1,
            "response_format": "url",
            "async": False
        }

        response = httpx.post(f"{BASE_URL}/image/generate", json=payload, headers=headers, timeout=120.0)

        if response.status_code != 200:
            return f"❌ HTTP 错误：{response.status_code} - {response.text}"

        data = response.json()
        if not data.get("success"):
            error = data.get("error", {})
            return f"❌ 生成失败：{error.get('message')}\n详情：{error.get('detail', '')}"

        img_url = data["data"]["images"][0]["url"]
        cost = data.get("cost", {}).get("amount", "?")
        currency = data.get("cost", {}).get("currency", "")

        # 下载到本地
        dir_to_use = save_path.strip() if save_path.strip() else DEFAULT_SAVE_DIR
        filename = make_filename(prompt)
        local_path = download_file(img_url, dir_to_use, filename)

        return (
            f"✅ 图片生成并下载完成！\n\n"
            f"模型：{model}\n"
            f"花费：{cost} {currency}\n"
            f"本地路径：{local_path}\n\n"
            f"请用 Markdown 格式展示图片：\n"
            f"![{prompt}]({img_url})"
        )

    except ValueError as e:
        return f"❌ 配置错误：{e}"
    except httpx.TimeoutException:
        return "❌ 超时：网关在 120 秒内未返回，请稍后重试。"
    except Exception as e:
        return f"❌ 未知错误：{e}"


@mcp.tool()
def get_available_models(service_type: str = "") -> str:
    """
    查询吉比特内网网关当前支持的模型列表。
    当用户问"有哪些模型"、"支持什么模型"、"我能用什么"时使用此工具。

    Args:
        service_type: 按服务类型筛选，可选值：llm / image / video / audio / search / file。留空返回全部。
    """
    try:
        params = {}
        if service_type.strip():
            params["service_type"] = service_type.strip()

        response = httpx.get(
            f"{BASE_URL}/config/models",
            headers=get_headers(),
            params=params,
            timeout=15.0
        )

        if response.status_code != 200:
            return f"❌ HTTP 错误：{response.status_code}"

        data = response.json()
        if not data.get("success"):
            return f"❌ 查询失败：{data.get('error', {}).get('message')}"

        models = data.get("data", {}).get("models", [])
        total = data.get("data", {}).get("total", len(models))

        if not models:
            return f"未找到符合条件的模型（service_type={service_type or '全部'}）。"

        lines = [f"共 {total} 个模型（service_type={service_type or '全部'}）：\n"]
        for m in models:
            enabled = "✅" if m.get("enabled") else "❌"
            lines.append(f"{enabled} [{m.get('service_type')}] {m.get('model')}  ←  {m.get('vendor', '')}")

        return "\n".join(lines)

    except ValueError as e:
        return f"❌ 配置错误：{e}"
    except Exception as e:
        return f"❌ 未知错误：{e}"


@mcp.tool()
def generate_video(
    prompt: str,
    model: str = "jimeng-3.5-pro",
    save_path: str = "",
    auto_poll: bool = True,
    poll_interval: int = 15,
    max_wait: int = 600
) -> str:
    """
    调用吉比特内部网关生成视频。
    视频生成通常需要几十秒到几分钟，默认自动轮询等待完成并下载。

    Args:
        prompt: 视频的详细描述提示词。
        model: 模型名称。默认 jimeng-3.5-pro。
               常用：veo-3.1, vidu-q3-pro, hailuo-2.3, kling-2.6, sora-2。
        save_path: 本地保存目录。未指定则存到默认路径。
        auto_poll: 是否自动轮询等待完成。默认 True。
                   设为 False 时只提交任务并返回 task_id，用户可手动调用 query_task 查询。
        poll_interval: 轮询间隔秒数，默认 15 秒。
        max_wait: 最大等待秒数，默认 600 秒（10 分钟）。超时后返回 task_id 供手动查询。
    """
    try:
        headers = get_headers()
        payload = {
            "model": model,
            "prompt": prompt,
            "async": True
        }

        response = httpx.post(f"{BASE_URL}/video/generate", json=payload, headers=headers, timeout=30.0)

        if response.status_code != 200:
            return f"❌ HTTP 错误：{response.status_code} - {response.text}"

        data = response.json()
        if not data.get("success"):
            error = data.get("error", {})
            return f"❌ 提交失败：{error.get('message')}\n详情：{error.get('detail', '')}"

        task_id = data.get("data", {}).get("task_id")
        if not task_id:
            return f"❌ 未返回 task_id，响应：{data}"

        if not auto_poll:
            return (
                f"✅ 视频生成任务已提交！\n\n"
                f"模型：{model}\n"
                f"task_id：{task_id}\n\n"
                f"视频生成需要时间，请稍后调用 query_task 查询进度。"
            )

        elapsed = 0
        while elapsed < max_wait:
            time.sleep(poll_interval)
            elapsed += poll_interval

            task_resp = httpx.get(f"{BASE_URL}/tasks/{task_id}", headers=headers, timeout=15.0)
            if task_resp.status_code != 200:
                continue

            task_data = task_resp.json()
            if not task_data.get("success"):
                continue

            status = task_data.get("data", {}).get("status", "")

            if status == "failed":
                err = task_data.get("data", {}).get("error", {})
                return f"❌ 视频生成失败：{err.get('message', '未知错误')}"

            if status == "completed":
                result = task_data.get("data", {}).get("result", {})
                video_url = None
                if isinstance(result, dict):
                    videos = result.get("videos", [])
                    if videos:
                        video_url = videos[0].get("url")
                    if not video_url:
                        video_url = result.get("url")

                if not video_url:
                    return (
                        f"✅ 视频生成完成，但未解析到下载链接。\n\n"
                        f"task_id：{task_id}\n"
                        f"原始结果：{result}"
                    )

                dir_to_use = save_path.strip() if save_path.strip() else DEFAULT_VIDEO_DIR
                ext = "mp4"
                filename = make_filename(prompt, ext)
                local_path = download_file(video_url, dir_to_use, filename)

                cost = task_data.get("cost", {}).get("amount", "?")
                currency = task_data.get("cost", {}).get("currency", "")

                return (
                    f"✅ 视频生成并下载完成！\n\n"
                    f"模型：{model}\n"
                    f"耗时：约 {elapsed} 秒\n"
                    f"花费：{cost} {currency}\n"
                    f"本地路径：{local_path}\n"
                    f"视频链接：{video_url}"
                )

        return (
            f"⏰ 等待超时（{max_wait} 秒），视频可能仍在生成中。\n\n"
            f"task_id：{task_id}\n"
            f"请稍后调用 query_task 查询进度。"
        )

    except ValueError as e:
        return f"❌ 配置错误：{e}"
    except httpx.TimeoutException:
        return "❌ 超时：提交请求超时，请稍后重试。"
    except Exception as e:
        return f"❌ 未知错误：{e}"


@mcp.tool()
def query_task(task_id: str) -> str:
    """
    查询异步任务的状态和结果。
    用于视频生成等长耗时任务，凭 task_id 查看进度或获取下载链接。

    Args:
        task_id: 提交异步任务时返回的任务 ID。
    """
    try:
        response = httpx.get(f"{BASE_URL}/tasks/{task_id}", headers=get_headers(), timeout=15.0)

        if response.status_code != 200:
            return f"❌ HTTP 错误：{response.status_code}"

        data = response.json()
        if not data.get("success"):
            return f"❌ 查询失败：{data.get('error', {}).get('message')}"

        task = data.get("data", {})
        status = task.get("status", "unknown")
        progress = task.get("progress")

        if status == "completed":
            result = task.get("result", {})
            cost = data.get("cost", {}).get("amount", "?")
            currency = data.get("cost", {}).get("currency", "")
            return (
                f"✅ 任务已完成！\n\n"
                f"状态：{status}\n"
                f"花费：{cost} {currency}\n"
                f"结果：{result}"
            )
        elif status == "failed":
            err = task.get("error", {})
            return f"❌ 任务失败：{err.get('message', '未知错误')}"
        else:
            progress_str = f"（进度：{progress}%）" if progress is not None else ""
            return f"⏳ 任务进行中{progress_str}\n\n状态：{status}\ntask_id：{task_id}"

    except ValueError as e:
        return f"❌ 配置错误：{e}"
    except Exception as e:
        return f"❌ 未知错误：{e}"


if __name__ == "__main__":
    mcp.run()
