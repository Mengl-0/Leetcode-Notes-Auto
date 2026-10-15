# -*- coding:utf-8 -*-
"""页面四：RAG 私有知识库问答（复用 core/rag，与三期命令行能力对齐）

- 建/更新索引为显式按钮触发（耗时操作不进自动渲染路径）
- 回答下方折叠展示命中来源片段与相似度得分，体现可追溯性
- 无密钥时 rag.answer 内部已有降级文案，界面同样安全兜底
"""
from __future__ import annotations

import streamlit as st

import common
from config.settings import RAG_CONFIG
from core import embedding, rag


def _index_status() -> None:
    """展示当前索引状态摘要"""
    idx = rag.load_index()
    if not idx:
        st.info("尚未建立索引（vector_store/index.json 不存在），点击下方按钮构建。")
        return
    st.caption(
        f"索引状态：schema `{idx.get('schema', '?')}` ｜ provider "
        f"`{idx.get('provider', '?')}` ｜ 知识块 {len(idx.get('chunks', []))} 个 "
        f"｜ 向量维度 {idx.get('dim', '?')}"
    )


def render() -> None:
    st.markdown("### 索引管理")
    _index_status()
    if not embedding.is_available():
        st.warning(f"⚠️ 向量化不可用：{embedding.missing_hint()}")
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🔨 建立 / 更新索引", key="btn_rag_build", type="primary"):
            with st.status("正在扫描笔记并构建索引…", expanded=True) as status:
                chunks, logs, err = common.run_captured(rag.build_index)
                common.show_logs(logs, err)
                if chunks is None:
                    status.update(label="索引构建失败（详见日志）", state="error")
                else:
                    st.write(f"共切分 {len(chunks)} 个知识块")
                    status.update(label="索引已更新", state="complete")
    with c2:
        if st.button("♻️ 强制重建索引", key="btn_rag_force",
                     help="schema 或 provider 变更后按钮会自动触发重建，此为手动兜底"):
            with st.status("正在强制重建…", expanded=True) as status:
                chunks, logs, err = common.run_captured(rag.build_index, True)
                common.show_logs(logs, err)
                if chunks is None:
                    status.update(label="重建失败（详见日志）", state="error")
                else:
                    st.write(f"共切分 {len(chunks)} 个知识块")
                    status.update(label="索引已重建", state="complete")

    st.markdown("---")
    mode = st.radio("模式", ["💬 问答", "🔎 纯检索"], horizontal=True, key="rag_mode")
    top_k = st.slider("返回片段数 top_k", 1, 10, RAG_CONFIG["top_k"], key="rag_topk")
    question = st.text_input("基于你的笔记提问", key="rag_q",
                             placeholder="例如：我记录过的动态规划题有哪些思路？")

    if mode == "🔎 纯检索":
        if question.strip() and st.button("检索", key="btn_rag_search", type="primary"):
            with st.spinner("检索中…"):
                hits, logs, err = common.run_captured(rag.search, question, top_k)
                common.show_logs(logs, err)
            if err:
                pass
            elif not hits:
                st.warning("没有命中片段：可先构建索引，或确认问题与笔记内容的关键词重合度。")
            else:
                for score, chunk in hits:
                    _hit_card(score, chunk)
    else:
        if question.strip() and st.button("提问", key="btn_rag_ask", type="primary"):
            with st.spinner("检索笔记并组织回答…"):
                result, logs, err = common.run_captured(rag.answer, question, top_k)
                common.show_logs(logs, err)
            if err:
                st.error(f"问答失败：{common.mask_sensitive(err)}")
            else:
                ans, hits = result if result else ("（无回答）", [])
                st.session_state.setdefault("rag_history", []).append(
                    (question, ans, hits or [])
                )
        for q, a, hits in reversed(st.session_state.get("rag_history", [])):
            st.chat_message("user").markdown(f"**{q}**")
            with st.chat_message("assistant"):
                common.safe_markdown(a or "（无回答）")
                if hits:
                    with st.expander(f"📎 来源片段（{len(hits)}）"):
                        for score, chunk in hits:
                            _hit_card(score, chunk, plain=True)


def _hit_card(score: float, chunk: dict, plain: bool = False) -> None:
    """单个命中片段卡片：来源路径 + 标题 + 相似度得分 + 原文（原文先脱敏）"""
    head = f"`{chunk.get('source', '?')}` ｜ {chunk.get('heading', '')} ｜ 相似度 {score:.3f}"
    if plain:
        common.safe_markdown(head)
        common.safe_markdown(chunk.get("text", "")[:800])
        st.divider()
    else:
        with st.container(border=True):
            common.safe_markdown(head)
            common.safe_markdown(chunk.get("text", "")[:800])
