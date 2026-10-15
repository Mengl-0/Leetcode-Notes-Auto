# -*- coding:utf-8 -*-
"""
Web 界面层公共工具（四期 · 可视化界面）

- 统一注入项目根路径并初始化目录（与 main.py 同一心智，界面层只调用不修改下层）
- 题解 / 每日笔记元数据解析与缓存聚合，供「笔记浏览」与「统计看板」复用
- stdout 捕获：core / scripts 各函数以 print 汇报进度，界面转为日志文本展示
"""
from __future__ import annotations

import contextlib
import io
import os
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
for _p in (str(BASE_DIR), str(Path(__file__).resolve().parent)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st  # noqa: E402

from config.settings import DATE_FORMAT, init_dir  # noqa: E402

init_dir()

from core import notes_io  # noqa: E402

DIFFICULTY_ORDER = ["简单", "中等", "困难", "未标注"]

# 题解元数据行（模板见 core/md_template.py：全角冒号与竖线，兼容半角写法）
_META_HEAD_RE = re.compile(r"^\s*>\s*难度[：:]\s*([^｜|]*)[｜|]\s*标签[：:]\s*([^｜|]*)")
_META_DATE_RE = re.compile(
    r"^\s*>\s*首次记录[：:]\s*(\S{4,10})\s*[^｜|]*[｜|]\s*复习次数[：:]\s*(\d+)"
)
_PROBLEM_FILE_RE = re.compile(r"^(\d{4})-([a-z0-9-]+)\.md$")
_DAILY_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.md$")


def _split_tags(raw: str) -> "list[str]":
    """标签串按顿号/逗号/分号/斜杠拆分为列表，去空白"""
    parts = re.split(r"[、，,;；/]", raw or "")
    return [t.strip() for t in parts if t.strip()]


def _parse_date(text: str) -> "datetime | None":
    try:
        return datetime.strptime(text, DATE_FORMAT)
    except (ValueError, TypeError):
        return None


def _files_sig(paths: "list[str]") -> tuple:
    """目录快照指纹：文件数 + 最大修改时间，作为缓存 key"""
    return (len(paths), round(max((os.path.getmtime(p) for p in paths), default=0.0), 3))


def _scan_problems() -> "list[dict]":
    """扫描全部题解笔记并解析元数据头，缺失字段归「未标注」、非法日期回退文件修改时间"""
    rows = []
    fallback_dates = 0
    for path in notes_io.list_problem_notes():
        fname = os.path.basename(path)
        m = _PROBLEM_FILE_RE.match(fname)
        text = notes_io.read_text(path)
        title = fname[:-3]
        difficulty, tags = "", []
        date_dt, reviews, date_src = None, 0, "meta"
        head_done = False
        for line in text.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
            if not head_done:
                mh = _META_HEAD_RE.match(line)
                if mh:
                    difficulty, tags = mh.group(1).strip(), _split_tags(mh.group(2))
                    head_done = True
            md = _META_DATE_RE.match(line)
            if md and date_dt is None:
                date_dt = _parse_date(md.group(1))
                reviews = int(md.group(2))
        if date_dt is None:
            date_dt = datetime.fromtimestamp(os.path.getmtime(path))
            date_src = "mtime"
            fallback_dates += 1
        rows.append(
            {
                "path": path,
                "fname": fname,
                "pid": m.group(1) if m else "—",
                "slug": m.group(2) if m else fname[:-3],
                "title": title,
                "difficulty": difficulty if difficulty in DIFFICULTY_ORDER[:3] else (difficulty or "未标注"),
                "tags": tags,
                "date": date_dt,
                "date_str": date_dt.strftime(DATE_FORMAT),
                "date_src": date_src,
                "reviews": reviews,
            }
        )
    return rows, fallback_dates


@st.cache_data(show_spinner=False)
def _cached_problems(_sig: tuple):
    return _scan_problems()


def problem_rows() -> "list[dict]":
    """题解元数据行列表（带缓存，文件变动自动失效）"""
    rows, _ = _cached_problems(_files_sig(notes_io.list_problem_notes()))
    return rows


def problem_fallback_count() -> int:
    """元数据日期非法、回退为文件修改时间的题解数"""
    _, n = _cached_problems(_files_sig(notes_io.list_problem_notes()))
    return n


@st.cache_data(show_spinner=False)
def _cached_daily_dates(_sig: tuple) -> "list[str]":
    dates = []
    for p in notes_io.list_daily_notes():
        m = _DAILY_FILE_RE.match(os.path.basename(p))
        if m and _parse_date(m.group(1)):
            dates.append(m.group(1))
    return sorted(dates)


def daily_dates() -> "list[str]":
    """全部每日打卡日期（YYYY-MM-DD，升序）"""
    return _cached_daily_dates(_files_sig(notes_io.list_daily_notes()))


def compute_streak(dates: "set[str]", today: str) -> int:
    """连续打卡天数：今天无记录时从昨天起往前数"""
    cur = _parse_date(today)
    if cur is None:
        return 0
    if cur.strftime(DATE_FORMAT) not in dates:
        cur -= timedelta(days=1)
    n = 0
    while cur.strftime(DATE_FORMAT) in dates:
        n += 1
        cur -= timedelta(days=1)
    return n


# ---------------------------------------------------------------------------
# 敏感信息脱敏（展示层统一入口）
# ---------------------------------------------------------------------------
# Web 界面回显终端日志 / 笔记正文 / 检索片段 / AI 输出时，不得暴露三类敏感信息：
#   1) API 密钥 / AccessKey（sk- 与 LTAI 前缀）
#   2) Git 远程仓库地址与账号名
#   3) OSS 桶名 / 域名 / 图片公网地址
# 脱敏只作用于「展示」，绝不修改磁盘上的笔记原文（笔记正文本身不算敏感信息）。
_KEY_RE = re.compile(r"sk-[A-Za-z0-9_\-]{6,}")
_AKID_RE = re.compile(r"LTAI[A-Za-z0-9]{8,}")
# 阿里云 OSS 公网地址（https://<桶>.oss-<地域>.aliyuncs.com/...）：即使 config/secret.env
# 未部署（如 Streamlit Cloud 只部署了已提交的笔记），也能按模式脱敏桶名/域名。
_OSS_HOST_RE = re.compile(r"https?://[A-Za-z0-9._-]+\.oss-[a-z0-9-]+\.aliyuncs\.com")
_MASK = "***"


def _git_remote_parts() -> "tuple[str, str]":
    """读取 origin 远程地址与其账号名；本地无 .git / 云端部署时返回 ('', '')。"""
    import subprocess
    url = ""
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=str(BASE_DIR), timeout=5,
        )
        if proc.returncode == 0:
            url = proc.stdout.strip()
    except Exception:
        url = ""
    account = ""
    if url:
        m = re.search(r"(?:github\.com[:/])([^/]+)", url)
        if m:
            account = m.group(1)
    return url, account


@st.cache_data(show_spinner=False)
def _sensitive_substrings() -> "tuple[str, ...]":
    """汇总需脱敏的敏感子串，按长度降序（保证先替换长串，如完整域名先于其中的桶名）。"""
    from config.settings import (
        OSS_BUCKET_NAME, OSS_ENDPOINT, get_oss_public_url_base, is_placeholder,
    )
    subs = []
    if not is_placeholder(OSS_BUCKET_NAME):
        subs.append(OSS_BUCKET_NAME)
    try:
        base = get_oss_public_url_base()
    except Exception:
        base = ""
    if base and not is_placeholder(base):
        subs.append(base)
    # 域名仅在有真实桶时一并脱敏，避免默认端点字符串误伤无关文本
    if not is_placeholder(OSS_BUCKET_NAME) and not is_placeholder(OSS_ENDPOINT):
        subs.append(OSS_ENDPOINT)
    url, account = _git_remote_parts()
    if url:
        subs.append(url)
    if account:
        subs.append(account)
    seen, out = set(), []
    for s in subs:
        s = (s or "").strip()
        if s and len(s) >= 3 and s not in seen:
            seen.add(s)
            out.append(s)
    return tuple(sorted(out, key=len, reverse=True))


def mask_sensitive(text: str) -> str:
    """将文本中的密钥 / git 远程地址与账号 / OSS 桶名·域名·图片公网地址替换为掩码。

    供所有面向用户的展示（日志、笔记渲染、检索片段、AI 输出）调用，不修改原文。
    """
    if not text:
        return text
    text = _KEY_RE.sub("sk-***", text)
    text = _AKID_RE.sub("LTAI***", text)
    text = _OSS_HOST_RE.sub(_MASK, text)
    for s in _sensitive_substrings():
        text = text.replace(s, _MASK)
    return text


def safe_markdown(body: str, unsafe_allow_html: bool = False) -> None:
    """st.markdown 的脱敏封装：先掩码敏感信息再渲染。"""
    st.markdown(mask_sensitive(body), unsafe_allow_html=unsafe_allow_html)


def run_captured(fn, *args, **kwargs):
    """执行 core/scripts 函数并捕获其 print 进度输出

    :return: (result, logs, error)；error 非 None 表示函数抛出异常
    """
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            result = fn(*args, **kwargs)
            error = None
        except Exception as e:  # 界面兜底：下层异常不崩页面，转为文本提示
            result, error = None, f"{type(e).__name__}: {e}"
    return result, buf.getvalue(), error


def show_logs(logs: str, error: str | None = None) -> None:
    """把捕获到的终端输出折叠展示；有异常时红字提示（输出先脱敏，不暴露密钥/远程地址/图床地址）"""
    if error:
        st.error(f"执行出错：{mask_sensitive(error)}")
    if logs.strip():
        with st.expander("📜 执行日志", expanded=bool(error)):
            st.code(mask_sensitive(logs.strip()), language="text")


def note_label(row: dict) -> str:
    """题解行 → 下拉框展示文案"""
    return f"{row['pid']} · {row['title']}"
