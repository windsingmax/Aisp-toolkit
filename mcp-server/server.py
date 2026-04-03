import os
import re
import httpx
import datetime
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Gbits-AIServiceProxy")

BASE_URL = "http://aitools.g-bits.com/aiserviceproxy/api/v1"
DEFAULT_SAVE_DIR = r"e:\claude\img"

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


if __name__ == "__main__":
    mcp.run()
