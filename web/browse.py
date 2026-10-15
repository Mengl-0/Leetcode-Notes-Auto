# -*- coding:utf-8 -*-
"""页面一：笔记浏览与管理（只读浏览 + 新建写操作带二次确认）

布局规范（毕业设计展示向，纯原生组件）：
- 头部：标题居左、视图切换按钮组居右，下方分隔线
- 筛选：单行三栏（搜索 / 难度 / 时间），下方小字结果统计，再分隔线
- 元信息：边框卡片集中展示，标签用 badge 样式
- 正文：标题层级降级规范、长内容折叠、图片限宽居中、底部小字辅助信息
"""
from __future__ import annotations

import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import streamlit as st

import common
from core import notes_io
from scripts.new_daily_note import create_daily_note
from scripts.new_problem import create_problem_note, slugify


def _rebuild_index() -> None:
    """新建笔记后刷新 NOTES_INDEX.md（复用一期 update_index 流程）"""
    from scripts.update_index import regenerate_index

    _, logs, err = common.run_captured(regenerate_index)
    if err:
        st.warning(f"索引更新失败：{common.mask_sensitive(err)}")


# ---------------------------------------------------------------------------
# 笔记正文解析
# ---------------------------------------------------------------------------
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
_IMG_LINE_RE = re.compile(
    r"^\s*!\[(?P<alt>[^\]]*)\]\(\s*<?(?P<url>[^)\s>]+)>?(?:\s+[^)]*)?\)\s*$"
)
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
_H2_RE = re.compile(r"^## (.+)$", re.M)
_REMOTE_RE = re.compile(r"^(?:https?:)?//", re.I)
# 模板占位与空小节：不展示，减少页面噪音
_PLACEHOLDER_RE = re.compile(r"^\s*（待补充）\s*$")

_DIFFICULTY_BADGE = {"简单": "green", "中等": "yellow", "困难": "red"}
_CODE_HINTS = ("代码", "code")
_LONG_FOLD_SECTIONS = ("思路分析", "推导", "复盘")
_META_QUOTE_RE = re.compile(r"^\s*>\s*(难度|首次记录)")


def _iter_note_blocks(text: str):
    """把笔记按「markdown 文本块 / 独占一行的图片」切分；代码围栏内不做图片识别。

    产出 ("md", 文本) 或 ("img", alt, url)。
    """
    buf: list = []
    in_fence = False
    for line in text.splitlines(keepends=True):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            buf.append(line)
            continue
        match = None if in_fence else _IMG_LINE_RE.match(line)
        if match is None:
            buf.append(line)
            continue
        if buf:
            yield ("md", "".join(buf))
            buf = []
        yield ("img", match.group("alt").strip(), match.group("url").strip())
    if buf:
        yield ("md", "".join(buf))


def _local_image(note_path: str, url: str):
    """把笔记里的图片地址解析为真实存在的本地文件；外链 / 不存在则返回 None"""
    if not url or url.startswith("data:") or _REMOTE_RE.match(url):
        return None
    p = Path(url) if os.path.isabs(url) else (Path(note_path).parent / url)
    try:
        return str(p.resolve()) if p.is_file() else None
    except OSError:
        return None


def _demote_headings(body: str) -> str:
    """标题层级规范：页面主标题（题名）由界面渲染为最高层级 H1，
    笔记内部的 # / ## 小节统一降级为 ###，避免重复大标题、层级混乱。
    """
    body = re.sub(r"(?m)^#(?!#) ", "### ", body)
    return _H2_RE.sub(r"### \1", body)


def _split_sections(body: str) -> "list[tuple[str, str]]":
    """按 ### 小节切分正文；返回 (小节标题或'', 该段文本) 列表"""
    parts = re.split(r"(?m)^(?=### )", body)
    out: "list[tuple[str, str]]" = []
    for seg in parts:
        if not seg.strip():
            continue
        m = re.match(r"### (.+?)\s*$", seg)
        out.append((m.group(1).strip() if m else "", seg))
    return out


def _should_fold(title: str, seg: str) -> bool:
    """长内容折叠策略：思路/推导/复盘等小节默认折叠；代码小节默认折叠；其余展开"""
    if not title:
        return False
    if any(h in title for h in _CODE_HINTS):
        return True
    if any(h in title for h in _LONG_FOLD_SECTIONS):
        return True
    return len(seg) > 1200


def _render_body(text: str, note_path: str) -> None:
    """渲染笔记正文：占位小节跳过、长内容折叠、图片限宽居中、外链容错"""
    missing: list = []

    for block in _iter_note_blocks(text):
        if block[0] == "md":
            body = _COMMENT_RE.sub("", block[1]).strip("\n")
            if not body.strip():
                continue
            body = _demote_headings(body)
            for seg_title, seg in _split_sections(body):
                content = seg.split("\n", 1)[1] if seg.startswith("### ") else seg
                core = (content or "").strip()
                if not seg_title and _META_QUOTE_RE.search(core):
                    # 头部元信息引用行：卡片已集中展示，正文降级为小字辅助文本
                    st.caption(core.replace("\n>", " ").lstrip("> ").replace("｜", " ｜ "))
                    continue
                if _PLACEHOLDER_RE.fullmatch(core) or (
                        "（待补充）" in core and len(core) < 20):
                    # 模板占位小节跳过，减少页面噪音
                    continue
                if _should_fold(seg_title, seg):
                    label = f"📂 {seg_title}" if seg_title else "展开内容"
                    with st.expander(label, expanded=False):
                        common.safe_markdown(seg)
                else:
                    common.safe_markdown(seg)
            continue

        _, alt, url = block
        caption = alt or None
        if caption and caption.lower() in ("alt text", "image", "图片"):
            caption = None
        local = _local_image(note_path, url)
        # 图片统一限宽 + 居中 + 前后留白（原生三栏布局实现，不写 CSS）
        _, img_col, _ = st.columns([1, 2, 1])
        with img_col:
            st.markdown("&nbsp;")  # 图片前留白（纯实体占位，非样式代码）
            rendered = False
            if local:
                try:
                    st.image(local, caption=caption, width="stretch")
                    rendered = True
                except Exception:
                    pass
            elif _REMOTE_RE.match(url):
                try:
                    st.image(url, caption=caption, width="stretch")
                    rendered = True
                except Exception:
                    pass
            if not rendered:
                missing.append(url)
            st.markdown("&nbsp;")  # 图片后留白

    if missing:
        st.caption(f"⚠️ 有 {len(missing)} 张图片未能显示（本地文件缺失或外链不可达）。")


def _badge_row(row: dict) -> None:
    """元信息卡片里的标签行：badge 样式，区分普通文字"""
    cols = st.columns(min(len(row["tags"]), 8) or 1)
    for i, t in enumerate(row["tags"][:8]):
        with cols[i]:
            st.badge(t, color="blue")


# ---------------------------------------------------------------------------
# 视图一：单题题解
# ---------------------------------------------------------------------------
def _view_problems() -> None:
    rows = common.problem_rows()
    if not rows:
        st.info("暂无题解笔记，可在「新建」中创建。")
        return

    c1, c2, c3 = st.columns([2, 1, 1])
    kw = c1.text_input(
        "搜索题解", key="prob_kw", placeholder="支持题号 / 标题 / 标签检索…",
        label_visibility="collapsed",
    )
    diff_opt = c2.selectbox(
        "难度", ["全部难度", *common.DIFFICULTY_ORDER], key="prob_diff",
        label_visibility="collapsed",
    )
    today = datetime.now().date()
    range_opt = c3.selectbox(
        "时间", ["全部时间", "近 7 天", "近 30 天"], key="prob_range",
        label_visibility="collapsed",
    )
    days = {"全部时间": None, "近 7 天": 7, "近 30 天": 30}[range_opt]
    diff_key = diff_opt if diff_opt != "全部难度" else "全部"

    filtered = []
    for r in rows:
        if diff_key != "全部" and r["difficulty"] != diff_key:
            continue
        if kw:
            hay = f"{r['pid']} {r['title']} {r['slug']} {' '.join(r['tags'])}".lower()
            if kw.strip().lower() not in hay:
                continue
        if days is not None:
            span = timedelta(days=days)
            if today - r["date"].date() > span or r["date"].date() > today:
                continue
        filtered.append(r)

    st.caption(f"共 {len(rows)} 篇 ｜ 筛选后 {len(filtered)} 篇")
    st.divider()

    if not filtered:
        st.info("🔍 没有符合条件的笔记。试试放宽搜索关键词、切换难度或时间范围。")
        return

    labels = [f"{r['pid']} · {r['title']}" for r in filtered]
    jump = st.session_state.pop("jump_to_fname", None)
    idx = 0
    if jump:
        for i, r in enumerate(filtered):
            if r["fname"] == jump:
                idx = i
                break
    picked_i = st.selectbox("选择题解", range(len(filtered)), index=idx,
                            format_func=lambda i: labels[i], key="prob_pick",
                            label_visibility="collapsed")
    row = filtered[picked_i]

    # ── 元信息卡片：带边框容器，横向均分，标签用 badge ──
    with st.container(border=True):
        m1, m2, m3, m4 = st.columns([1, 1, 2, 3])
        m1.markdown("**难度**")
        m1.badge(
            row["difficulty"],
            color=_DIFFICULTY_BADGE.get(row["difficulty"], "gray"),
        )
        m2.markdown("**复习次数**")
        m2.write(str(row["reviews"]))
        m3.markdown("**首次记录**")
        m3.write(row["date_str"])
        m4.markdown("**标签**")
        if row["tags"]:
            _badge_row(row)
        else:
            m4.caption("未打标签")
    st.divider()

    st.markdown(f"# {row['title']}")
    _render_body(notes_io.read_text(row["path"]), row["path"])

    # 底部小字辅助信息：原题链接（弱化权重）
    text = notes_io.read_text(row["path"])
    m = re.search(r"https://leetcode\.cn/problems/[a-z0-9-]+/", text)
    if m:
        st.caption(f"🔗 原题链接：{m.group(0)}")


# ---------------------------------------------------------------------------
# 视图二：每日打卡
# ---------------------------------------------------------------------------
def _view_daily() -> None:
    dailies = notes_io.list_daily_notes()
    if not dailies:
        st.info("暂无每日打卡笔记，可在「新建」中创建。")
        return
    opts = {os.path.basename(p): p for p in dailies}
    picked = st.selectbox(
        "选择打卡日期", list(opts.keys()), key="daily_pick",
        format_func=lambda k: k.replace(".md", ""),
    )
    st.divider()
    st.markdown(f"# 📅 {picked[:-3]} 刷题打卡")
    _render_body(notes_io.read_text(opts[picked]), opts[picked])


# ---------------------------------------------------------------------------
# 视图三：新建笔记（写操作，保留二次确认）
# ---------------------------------------------------------------------------
def _view_new() -> None:
    n1, n2 = st.columns(2)
    with n1:
        with st.container(border=True):
            st.markdown("**📅 新建每日打卡**")
            d_date = st.date_input("打卡日期", value=datetime.now().date(),
                                   key="new_daily_date")
            if st.button("生成每日笔记", key="btn_new_daily", type="primary"):
                ds = d_date.strftime("%Y-%m-%d")
                path, logs, err = common.run_captured(create_daily_note, ds)
                common.show_logs(logs, err)
                if path:
                    st.success(f"已生成：{os.path.basename(path)}")
                    _rebuild_index()
    with n2:
        with st.container(border=True):
            st.markdown("**🧗 新建单题题解**")
            p_id = st.text_input("题号（数字）", key="new_prob_id")
            p_slug = st.text_input("英文 slug（如 two-sum）", key="new_prob_slug")
            p_title = st.text_input("中文标题（可留空，默认用 slug）",
                                    key="new_prob_title")
            if p_slug:
                st.caption(f"规范化预览：`{slugify(p_slug) or '（非法 slug）'}`")
            if st.button("生成题解笔记", key="btn_new_prob", type="primary"):
                if not p_id.strip() or not p_slug.strip():
                    st.error("题号与 slug 均不能为空")
                else:
                    if st.button(
                        f"确认创建 {p_id.strip()}-{slugify(p_slug)}.md？",
                        key="btn_new_prob_confirm",
                    ):
                        path, logs, err = common.run_captured(
                            create_problem_note, p_id, p_slug, p_title
                        )
                        common.show_logs(logs, err)
                        if path:
                            st.success(f"已生成：{os.path.basename(path)}")
                            _rebuild_index()


# ---------------------------------------------------------------------------
# 页面入口：头部左右分栏（标题区由 app.py 渲染，此处放视图切换）
# ---------------------------------------------------------------------------
def render() -> None:
    head_l, head_r = st.columns([3, 2])
    with head_l:
        st.caption("浏览、筛选与管理刷题笔记")
    with head_r:
        view = st.segmented_control(
            "视图", ["单题题解", "每日打卡", "新建笔记"],
            default="单题题解", key="browse_view",
            label_visibility="collapsed",
        )
    st.divider()

    if view == "每日打卡":
        _view_daily()
    elif view == "新建笔记":
        _view_new()
    else:
        _view_problems()
