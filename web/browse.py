# -*- coding:utf-8 -*-
"""页面一：笔记浏览与管理（只读浏览 + 新建写操作带二次确认）"""
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


# 笔记模板里的结构标记（<!-- weather-start --> 等）供脚本定位使用，展示时应剥离，
# 否则会被 st.markdown 当普通文本原样打印出来
_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
# 独占一行的图片语法（模板截图均为整行）
_IMG_LINE_RE = re.compile(
    r"^\s*!\[(?P<alt>[^\]]*)\]\(\s*<?(?P<url>[^)\s>]+)>?(?:\s+[^)]*)?\)\s*$"
)
# 代码围栏：``` 或 ~~~，围栏内的图片语法按普通代码文本处理
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
_REMOTE_RE = re.compile(r"^(?:https?:)?//", re.I)


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


def _render_note(path: str) -> None:
    text = notes_io.read_text(path)
    if not text:
        st.warning("笔记内容为空或读取失败")
        return

    remote_imgs = 0
    missing: list = []
    for block in _iter_note_blocks(text):
        if block[0] == "md":
            # 剥离结构注释后再渲染，顺带做敏感信息脱敏
            body = _COMMENT_RE.sub("", block[1]).strip("\n")
            if body.strip():
                common.safe_markdown(body)
            continue

        _, alt, url = block
        caption = alt or None
        if caption and caption.lower() in ("alt text", "image", "图片"):
            caption = None
        local = _local_image(path, url)
        if local:
            st.image(local, caption=caption)          # 原生组件，随明暗主题自适应
        elif _REMOTE_RE.match(url):
            remote_imgs += 1                          # 图床外链：脱敏后不回显
        else:
            missing.append(url)

    if remote_imgs:
        st.caption(
            "💡 笔记中的图床链接已脱敏，不在此回显；原始图片仍保留在本地 assets/ 或 OSS 图床。"
        )
    if missing:
        st.caption(f"⚠️ 有 {len(missing)} 张本地图片未找到（可能未同步或路径已变更）。")


def render() -> None:
    tab_daily, tab_problem, tab_new = st.tabs(
        ["📅 每日打卡", "🧗 单题题解", "✚ 新建笔记"]
    )

    with tab_daily:
        dailies = notes_io.list_daily_notes()
        if not dailies:
            st.info("暂无每日打卡笔记，可在「新建笔记」创建。")
        else:
            opts = {os.path.basename(p): p for p in dailies}
            picked = st.selectbox(
                "选择打卡日期", list(opts.keys()), key="daily_pick",
                format_func=lambda k: k.replace(".md", ""),
            )
            _render_note(opts[picked])

    with tab_problem:
        rows = common.problem_rows()
        if not rows:
            st.info("暂无题解笔记。")
            return
        c1, c2, c3 = st.columns([2, 1, 2])
        kw = c1.text_input("按题号 / 标题 / 标签搜索", key="prob_kw")
        diff_opt = c2.selectbox(
            "难度", ["全部", *common.DIFFICULTY_ORDER], key="prob_diff"
        )
        today = datetime.now().date()
        range_opt = c3.selectbox(
            "时间范围", ["全部", "近 7 天", "近 30 天"], key="prob_range"
        )
        days = {"全部": None, "近 7 天": 7, "近 30 天": 30}[range_opt]

        filtered = []
        for r in rows:
            if diff_opt != "全部" and r["difficulty"] != diff_opt:
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

        st.caption(f"共 {len(rows)} 篇，筛选后 {len(filtered)} 篇")
        if not filtered:
            st.warning("无符合条件的题解，请调整筛选条件。")
            return

        labels = [f"{r['pid']} · {r['title']}" for r in filtered]
        # 统计页跳转带来的定位请求（从统计回到明细）
        jump = st.session_state.pop("jump_to_fname", None)
        idx = 0
        if jump:
            for i, r in enumerate(filtered):
                if r["fname"] == jump:
                    idx = i
                    break
        picked_i = st.selectbox("选择题解", range(len(filtered)), index=idx,
                                format_func=lambda i: labels[i], key="prob_pick")
        row = filtered[picked_i]

        meta = st.columns(4)
        meta[0].metric("难度", row["difficulty"])
        meta[1].metric("复习次数", row["reviews"])
        meta[2].metric("首次记录", row["date_str"])
        meta[3].metric("标签", " ".join(row["tags"]) or "—")
        if row["tags"]:
            st.markdown(
                " ｜ ".join(
                    f"`{t}`" for t in row["tags"]
                )
            )
        st.divider()
        _render_note(row["path"])

    with tab_new:
        n1, n2 = st.columns(2)
        with n1:
            st.markdown("### 📅 新建每日打卡")
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
            st.markdown("### 🧗 新建单题题解")
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
                    # 写操作二次确认（方案约束：写入类操作保留确认）
                    if st.button(
                        f"确认在 notes/problems 创建 {p_id.strip()}-{slugify(p_slug)}.md？",
                        key="btn_new_prob_confirm",
                    ):
                        path, logs, err = common.run_captured(
                            create_problem_note, p_id, p_slug, p_title
                        )
                        common.show_logs(logs, err)
                        if path:
                            st.success(f"已生成：{os.path.basename(path)}")
                            _rebuild_index()
