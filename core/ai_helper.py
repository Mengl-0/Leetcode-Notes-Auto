# -*- coding:utf-8 -*-
"""
AI 增强模块（二期）

对接 DeepSeek（OpenAI 兼容接口），提供：
  - chat():               底层对话封装（标准库 urllib，无需安装第三方包）
  - analyze_problem():    读取单题题解，生成思路 / 复杂度 / 易错点分析
  - summarize_daily():    读取当日全部笔记，生成刷题收获总结
  - convert_py_to_go():   Python 代码转 Go 代码
  - review_code():        代码 bug 检测与改进建议

密钥读取：环境变量 / config/secret.env（见 config/settings.py）
未配置密钥或未联网时给出友好提示并安全降级，不抛异常中断主流程。
"""
import json
import time
import urllib.error
import urllib.request

from config.settings import DEEPSEEK_CONFIG, validate_deepseek_config
from core.logger import get_logger

logger = get_logger("ai")

# 网络抖动 / 服务端 5xx 时自动重试的次数与间隔（审计问题 5）
_MAX_RETRIES = 2
_RETRY_INTERVAL = 2.0


class TransientError(RuntimeError):
    """临时性错误（网络异常、5xx、429），可自动重试"""


class PermanentError(RuntimeError):
    """永久性错误（鉴权失败、参数错误、响应解析失败），重试无意义"""


def is_configured() -> bool:
    """DeepSeek 是否已正确配置（密钥非占位）"""
    return not validate_deepseek_config()


def _print_missing() -> None:
    missing = validate_deepseek_config()
    print("❌ DeepSeek 配置不完整，缺少：")
    for m in missing:
        print(f"   - {m}")
    print("💡 请设置环境变量 DEEPSEEK_API_KEY，或复制 config/config.example.env 为 config/secret.env 后填写")


def _is_transient(status_code: int) -> bool:
    """5xx 与 429 视为可重试的临时错误；4xx（鉴权/参数错误）重试无意义"""
    return status_code >= 500 or status_code == 429


def _chat_once(url: str, data: bytes) -> str:
    """
    单次调用 DeepSeek，成功返回回复文本。
    临时性错误（网络异常 / 5xx / 429）抛 RuntimeError 供上层重试；
    其它错误抛 RuntimeError 且标记不可重试。
    """
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_CONFIG['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=DEEPSEEK_CONFIG["timeout"]) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        logger.error("DeepSeek HTTPError %s：%s", e.code, detail)
        msg = f"接口返回错误 HTTP {e.code}：{detail or e.reason}"
        if _is_transient(e.code):
            raise TransientError(msg) from e
        raise PermanentError(msg) from e
    except urllib.error.URLError as e:
        logger.error("DeepSeek URLError：%s", e.reason)
        raise TransientError(f"无法连接 DeepSeek 服务（网络异常）：{e.reason}") from e
    except TimeoutError as e:
        logger.error("DeepSeek 请求超时：%s", e)
        raise TransientError("请求超时") from e
    try:
        content = body["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        logger.error("DeepSeek 响应解析失败：%s", e, exc_info=True)
        raise PermanentError(f"DeepSeek 返回内容解析失败：{e}") from e
    logger.info("DeepSeek 调用成功，model=%s，返回 %d 字符", DEEPSEEK_CONFIG["model"], len(content))
    return content


def chat(system_prompt: str, user_prompt: str) -> "str | None":
    """
    调用 DeepSeek /chat/completions，返回模型回复文本；失败返回 None。
    网络异常 / 5xx / 429 自动重试最多 2 次，间隔 2s（审计问题 5）；
    鉴权失败、参数错误等永久性错误不重试，直接提示。
    """
    if not is_configured():
        _print_missing()
        return None

    url = DEEPSEEK_CONFIG["base_url"].rstrip("/") + "/chat/completions"
    payload = {
        "model": DEEPSEEK_CONFIG["model"],
        "temperature": DEEPSEEK_CONFIG["temperature"],
        "max_tokens": DEEPSEEK_CONFIG["max_tokens"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    data = json.dumps(payload).encode("utf-8")

    last_err = ""
    for attempt in range(_MAX_RETRIES + 1):
        try:
            return _chat_once(url, data)
        except TransientError as e:
            last_err = str(e)
            if attempt < _MAX_RETRIES:
                print(f"⚠️ {last_err}，{int(_RETRY_INTERVAL)}s 后重试（{attempt + 1}/{_MAX_RETRIES}）...")
                time.sleep(_RETRY_INTERVAL)
        except PermanentError as e:
            print(f"❌ {e}")
            return None
        except Exception as e:  # 兜底：未预期异常不重试，避免掩盖问题
            print(f"❌ 调用 DeepSeek 失败：{e}")
            logger.error("DeepSeek 调用异常：%s", e, exc_info=True)
            return None

    print(f"❌ DeepSeek 调用失败（已重试 {_MAX_RETRIES} 次）：{last_err}")
    return None


_BASE_SYSTEM = (
    "你是一名资深算法竞赛教练，精通 Python 与 Go。"
    "回答简洁、准确、结构化，使用中文，必要处用 Markdown。不要编造题目条件。"
)


def analyze_problem(problem_text: str) -> "str | None":
    """
    针对一道题的题解内容，生成思路梳理、复杂度分析、易错点提示
    :param problem_text: 题解 md 全文（或题目 + 代码片段）
    """
    if not problem_text.strip():
        print("⚠️ 题解内容为空，无法分析")
        return None
    user = (
        "下面是我的算法题解，请帮我：1) 用一段话讲清核心思路；"
        "2) 给出时间与空间复杂度并说明理由；3) 指出容易出错的边界或陷阱；"
        "4) 若有更优解法，简述思路。\n\n" + problem_text
    )
    return chat(_BASE_SYSTEM, user)


def summarize_daily(daily_text: str) -> "str | None":
    """
    针对当日刷题笔记，生成收获总结与后续建议
    :param daily_text: 当日每日打卡 md 全文（可拼接多篇题解）
    """
    if not daily_text.strip():
        print("⚠️ 当日笔记为空，无法总结")
        return None
    user = (
        "下面是我今天全部的刷题笔记，请生成一段「今日刷题收获总结」："
        "概括今天掌握的知识点、共性问题、以及明天可改进的 2~3 条建议。"
        "语气鼓励、简洁，输出 Markdown。\n\n" + daily_text
    )
    return chat(_BASE_SYSTEM, user)


def convert_py_to_go(py_code: str) -> "str | None":
    """把 Python 代码转换为等价 Go 代码"""
    if not py_code.strip():
        print("⚠️ Python 代码为空，无法转换")
        return None
    user = (
        "把下面这段 Python 代码等价转换为 Go 代码，保持算法逻辑一致，"
        "输出可直接运行的 Go 片段（含必要 import），并在代码后用 2~3 句说明关键差异。\n\n"
        "```python\n" + py_code + "\n```"
    )
    return chat(_BASE_SYSTEM, user)


def review_code(code: str, lang: str = "python") -> "str | None":
    """代码 bug 检测与改进建议"""
    if not code.strip():
        print("⚠️ 代码为空，无法检查")
        return None
    user = (
        f"下面是一段 {lang} 代码，请做 code review："
        "1) 是否存在 bug / 边界错误 / 潜在崩溃；2) 复杂度是否最优；"
        "3) 可读性与命名改进建议。分点输出。\n\n"
        "```" + lang + "\n" + code + "\n```"
    )
    return chat(_BASE_SYSTEM, user)
