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
import urllib.error
import urllib.request

from config.settings import DEEPSEEK_CONFIG, validate_deepseek_config
from core.logger import get_logger

logger = get_logger("ai")


def is_configured() -> bool:
    """DeepSeek 是否已正确配置（密钥非占位）"""
    return not validate_deepseek_config()


def _print_missing():
    missing = validate_deepseek_config()
    print("❌ DeepSeek 配置不完整，缺少：")
    for m in missing:
        print(f"   - {m}")
    print("💡 请设置环境变量 DEEPSEEK_API_KEY，或复制 config/config.example.env 为 config/secret.env 后填写")


def chat(system_prompt: str, user_prompt: str) -> str:
    """
    调用 DeepSeek /chat/completions，返回模型回复文本；失败返回 None
    使用标准库 urllib，避免引入 openai 等第三方依赖。
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
        content = body["choices"][0]["message"]["content"].strip()
        logger.info("DeepSeek 调用成功，model=%s，返回 %d 字符", DEEPSEEK_CONFIG["model"], len(content))
        return content
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:500]
        except Exception:
            pass
        print(f"❌ DeepSeek 接口返回错误 HTTP {e.code}：{detail or e.reason}")
        logger.error("DeepSeek HTTPError %s：%s", e.code, detail)
        return None
    except urllib.error.URLError as e:
        print(f"❌ 无法连接 DeepSeek 服务（网络异常）：{e.reason}")
        logger.error("DeepSeek URLError：%s", e.reason)
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print(f"❌ DeepSeek 返回内容解析失败：{e}")
        logger.error("DeepSeek 响应解析失败：%s", e, exc_info=True)
        return None
    except Exception as e:  # 兜底：超时等其它异常
        print(f"❌ 调用 DeepSeek 失败：{e}")
        logger.error("DeepSeek 调用异常：%s", e, exc_info=True)
        return None


_BASE_SYSTEM = (
    "你是一名资深算法竞赛教练，精通 Python 与 Go。"
    "回答简洁、准确、结构化，使用中文，必要处用 Markdown。不要编造题目条件。"
)


def analyze_problem(problem_text: str) -> str:
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


def summarize_daily(daily_text: str) -> str:
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


def convert_py_to_go(py_code: str) -> str:
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


def review_code(code: str, lang: str = "python") -> str:
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
