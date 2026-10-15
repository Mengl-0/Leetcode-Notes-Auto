# -*- coding:utf-8 -*-
"""页面五：一键同步 GitHub 与配置体检（复用一期 auto_sync 流程与 config.settings 校验）

- 同步拆为四个显式步骤，逐步骤展示进度与捕获日志，函数序列与 scripts/auto_sync.py 同源
- 写操作（上传 + git 推送）二次确认后才执行
- 配置体检只展示 check_config 校验结果，不回显任何密钥明文
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

import common
from config.settings import check_config
from core.git_auto import get_change_summary, git_commit_and_push
from scripts.update_index import regenerate_index
from scripts.upload_img import batch_upload_assets, scan_all_md_replace


def _run_sync() -> None:
    """执行与 run_auto_sync 相同的四步流程，但分步反馈状态（界面化改造，不改下层）"""
    bar = st.progress(0.0, text="准备同步…")
    steps = [
        "1️⃣ 批量上传 assets 图片",
        "2️⃣ 扫描笔记替换图片链接",  # 需复用步骤 1 的 url_cache，循环内特判
        "3️⃣ 更新笔记目录索引",
        "4️⃣ Git 提交并推送",  # 提交信息含时间戳，循环内特判
    ]
    url_cache: dict = {}
    failed = False
    for i, name in enumerate(steps):
        bar.progress(i / len(steps), text=f"{name} …")
        if i == 0:
            res, logs, err = common.run_captured(batch_upload_assets)
            if isinstance(res, dict):
                url_cache = res
        elif i == 1:
            res, logs, err = common.run_captured(
                scan_all_md_replace, url_cache=url_cache
            )
        elif i == 2:
            res, logs, err = common.run_captured(regenerate_index)
        else:
            msg = (
                "auto update: 同步刷题笔记 "
                f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
            )
            res, logs, err = common.run_captured(git_commit_and_push, msg)
        if err:
            failed = True
            bar.progress(1.0, text=f"❌ {name} 失败")
            st.error(f"{name} 出错：{common.mask_sensitive(err)}")
        common.show_logs(logs, err)
        if failed:
            st.info("后续步骤已中止；修复后可重新发起同步。")
            return
    bar.progress(1.0, text="✅ 同步完成")
    st.success("一键同步完成（各步骤明细见上方日志）")


def render() -> None:
    c1, c2 = st.columns([1, 1])

    with c1:
        st.markdown("### 🔄 一键同步 GitHub")
        st.caption("流程：上传 assets 图片 → 替换笔记内图片链接 → 重建索引 → git 提交推送")
        changes = get_change_summary()
        if changes:
            st.info(
                f"检测到 {len(changes)} 个待同步变更：\n\n"
                + "\n".join(f"- `{c}`" for c in changes[:10])
            )
        else:
            st.caption("当前工作区无未提交变更。")

        if st.button("🚀 开始一键同步", key="btn_sync", type="primary"):
            st.session_state["sync_confirming"] = True

        if st.session_state.get("sync_confirming"):
            st.warning("⚠️ 即将执行：图片上传 + 索引重建 + 提交并推送到 GitHub 远端")
            b1, b2 = st.columns(2)
            if b1.button("确认执行", key="btn_sync_yes", type="primary"):
                st.session_state["sync_confirming"] = False
                _run_sync()
            if b2.button("取消", key="btn_sync_no"):
                st.session_state["sync_confirming"] = False

    with c2:
        st.markdown("### 🩺 配置体检")
        st.caption("复用 config.settings.check_config，仅展示已配/待补，不回显密钥明文")
        if st.button("运行体检", key="btn_check", type="primary"):
            report, logs, err = common.run_captured(check_config, False)
            common.show_logs(logs, err)
            if report:
                st.session_state["cfg_report"] = report
        report = st.session_state.get("cfg_report")
        if report:
            name_map = {
                "oss": "阿里云 OSS 图床",
                "deepseek": "DeepSeek AI",
                "embedding": "RAG 向量化",
            }
            for key, missing in report.items():
                label = name_map.get(key, key)
                if missing:
                    st.error(f"**{label}**：待补 {len(missing)} 项")
                    with st.expander(f"{label} 缺失项", expanded=False):
                        for m in missing:
                            st.markdown(f"- {m}")
                else:
                    st.success(f"**{label}**：✅ 已就绪")
