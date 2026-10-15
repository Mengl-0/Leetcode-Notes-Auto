# -*- coding:utf-8 -*-
"""页面三：AI 增强可视化（复用 core/ai_helper，与二期命令行四项能力对齐）

未配置 DEEPSEEK_API_KEY 时全部按钮置灰并给出配置指引，与现有降级逻辑一致。
"""
from __future__ import annotations

import os

import streamlit as st

import common
from core import ai_helper, notes_io

_GO2PY_SYSTEM = (
    "你是资深算法工程师，负责把用户给出的 Go 语言解法转换为等价 Python3 实现。"
    "要求：1) 输出完整可运行的 LeetCode 风格 class Solution 方法；"
    "2) 保持与原 Go 实现相同的算法思路；"
    "3) 在代码之后用不超过 5 条要点说明两种语言实现的关键差异。"
    "只输出 Markdown，不要额外寒暄。"
)


def _run_ai(fn, *args) -> "str | None":
    """调用 ai_helper 能力函数：捕获降级 print；返回 None 时把原因展示为日志"""
    result, logs, err = common.run_captured(fn, *args)
    if err:
        st.error(f"AI 调用异常：{err}")
    if result is None:
        common.show_logs(logs or "（无输出：输入为空或密钥校验未通过）", None)
    return result


def _key_guide() -> None:
    st.warning("🔒 未配置 DeepSeek 密钥，AI 功能已禁用（与命令行入口同一降级逻辑）。")
    st.code("config/secret.env 中填入：\nDEEPSEEK_API_KEY=你的密钥", language="ini")
    st.caption("配置完成后刷新本页面即可使用。")


def render() -> None:
    ok = ai_helper.is_configured()
    if not ok:
        _key_guide()

    rows = common.problem_rows()
    dailies = [p for p in notes_io.list_daily_notes()]

    t1, t2, t3, t4 = st.tabs(
        ["🧠 题解分析", "📝 每日总结", "🔄 代码转换", "🔎 代码检查"]
    )

    with t1:
        if not rows:
            st.info("暂无题解笔记。")
        else:
            idx = st.selectbox(
                "选择题解笔记", range(len(rows)),
                format_func=lambda i: f"{rows[i]['pid']} · {rows[i]['title']}",
                key="ai_prob_pick",
            )
            text = notes_io.read_text(rows[idx]["path"])
            st.caption(f"将分析 {len(text)} 字符的笔记正文")
            if st.button("开始题解分析", key="btn_ai_analyze",
                         disabled=not ok, type="primary"):
                with st.spinner("DeepSeek 分析中…"):
                    out = _run_ai(ai_helper.analyze_problem, text)
                if out:
                    st.markdown("### 分析结果")
                    st.markdown(out)

    with t2:
        if not dailies:
            st.info("暂无每日打卡笔记。")
        else:
            di = st.selectbox(
                "选择打卡笔记", range(len(dailies)),
                format_func=lambda i: os.path.basename(dailies[i])[:-3],
                key="ai_daily_pick",
            )
            path = dailies[di]
            text = notes_io.read_text(path)
            if st.button("生成每日总结", key="btn_ai_summary",
                         disabled=not ok, type="primary"):
                with st.spinner("DeepSeek 总结中…"):
                    out = _run_ai(ai_helper.summarize_daily, text)
                if out:
                    st.markdown("### 总结结果")
                    st.markdown(out)
                    st.markdown("---")
                    if st.button("✍️ 追加写回该笔记", key="btn_ai_writeback"):
                        try:
                            with open(path, "a", encoding="utf-8") as f:
                                f.write("\n\n## 🤖 AI 每日总结\n\n" + out + "\n")
                            st.success(f"已追加写入 {os.path.basename(path)}")
                        except OSError as e:
                            st.error(f"写回失败：{e}")

    with t3:
        direction = st.radio("转换方向", ["Python → Go", "Go → Python"],
                             horizontal=True, key="ai_convert_dir")
        src = st.text_area("粘贴源代码", height=220, key="ai_convert_src",
                           placeholder="class Solution:\n    def twoSum(self, nums, target): ...")
        if st.button("开始转换", key="btn_ai_convert",
                     disabled=not ok or not src.strip(), type="primary"):
            with st.spinner("转换中…"):
                if direction == "Python → Go":
                    out = _run_ai(ai_helper.convert_py_to_go, src)
                else:
                    # 反向不在 core 预置四项能力内，用公开 chat API 组装，不改动下层
                    out = _run_ai(ai_helper.chat, _GO2PY_SYSTEM, src)
            if out:
                c1, c2 = st.columns(2)
                c1.markdown("**源代码**")
                c1.code(src, language="go" if direction.startswith("Go") else "python")
                c2.markdown("**转换结果**")
                c2.markdown(out)

    with t4:
        lang = st.selectbox("代码语言", ["python", "go"], key="ai_review_lang")
        code = st.text_area("粘贴待检查代码", height=220, key="ai_review_code")
        if st.button("开始检查", key="btn_ai_review",
                     disabled=not ok or not code.strip(), type="primary"):
            with st.spinner("检查中…"):
                out = _run_ai(ai_helper.review_code, code, lang)
            if out:
                st.markdown("### Review 结果")
                st.markdown(out)
