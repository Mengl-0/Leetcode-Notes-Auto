# -*- coding:utf-8 -*-
"""
笔记读写公共模块（供二期 AI、三期 RAG 复用）

- list_problem_notes():   列出全部题解笔记路径（按 4 位题号排序）
- list_daily_notes():     列出全部每日打卡笔记路径（按日期倒序）
- read_text():            读取单个 md 文本
- latest_daily_note():    取最近一篇每日笔记（可传指定日期）
- find_problem_note():    按题号或文件名关键字定位题解笔记
"""
import os
import re

from config.settings import NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, DATE_FORMAT

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.md$")
_PROBLEM_RE = re.compile(r"^(\d{4})-([a-z0-9-]+)\.md$")


def _list_md(dir_path: str):
    if not os.path.isdir(dir_path):
        return []
    return [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith(".md")]


def list_problem_notes():
    """题解笔记路径列表，按题号升序；命名不规范的排在最后"""
    files = _list_md(NOTES_PROBLEM_PATH)

    def key(p):
        m = _PROBLEM_RE.match(os.path.basename(p))
        return (0, int(m.group(1)), p) if m else (1, 0, p)

    return sorted(files, key=key)


def list_daily_notes():
    """每日笔记路径列表，按日期倒序（最新在前）；非规范命名按字典序排在最后"""
    files = _list_md(NOTES_DAILY_PATH)
    dated = [f for f in files if _DATE_RE.match(os.path.basename(f))]
    others = [f for f in files if not _DATE_RE.match(os.path.basename(f))]
    return sorted(dated, reverse=True) + sorted(others)


def read_text(path: str) -> str:
    """读取 md 文本；文件不存在或读取失败返回空串"""
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def latest_daily_note(date_str: str = "") -> str:
    """
    取指定日期（默认最近一篇）的每日笔记路径
    :param date_str: YYYY-MM-DD，留空表示最近一篇
    :return: 笔记路径，找不到返回 None
    """
    if date_str:
        p = os.path.join(NOTES_DAILY_PATH, f"{date_str}.md")
        return p if os.path.exists(p) else None
    dailies = list_daily_notes()
    return dailies[0] if dailies else None


def find_problem_note(keyword: str) -> str:
    """
    按题号或 slug 关键字定位题解笔记
    :param keyword: 如 "1" / "0001" / "two-sum" / "two sum"
    :return: 笔记路径，找不到返回 None
    """
    kw = keyword.strip().lower().replace(" ", "-")
    if not kw:
        return None

    exact_pid = kw.lstrip("0") or "0"
    for p in list_problem_notes():
        m = _PROBLEM_RE.match(os.path.basename(p))
        if not m:
            continue
        pid, slug = m.group(1), m.group(2)
        if str(int(pid)) == exact_pid or pid == kw or kw in slug:
            return p
    return None


def dailies_on(date_str: str):
    """取某日的每日笔记文本（含路径），供 AI 总结使用"""
    p = latest_daily_note(date_str)
    return (p, read_text(p)) if p else (None, "")


def today_str() -> str:
    from datetime import datetime
    return datetime.now().strftime(DATE_FORMAT)
