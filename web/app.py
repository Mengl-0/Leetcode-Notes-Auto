#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
LeetCode Notes Auto · Web 可视化界面（四期）

启动（项目根目录）：streamlit run web/app.py

- 依赖方向 web/ -> scripts/ -> core/ -> config/：界面层只调用不修改下层
- 只用 Streamlit 原生组件，不引第三方 UI 库、不写自定义 CSS、无动画
- 浏览/统计/检索只读；新建、写回、同步等写操作保留二次确认
"""
import streamlit as st
from datetime import datetime

import common  # noqa: F401  先导入：完成 sys.path 注入与 init_dir()
from common import run_captured, show_logs  # noqa: F401 供各页面复用

st.set_page_config(
    page_title="LeetCode 刷题知识库",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

import browse
import dashboard
import ai_page
import rag_page
import sync_page

# 菜单项：图标统一风格 + 精简文字（保持单选导航）
PAGES = {
    "📒 笔记": browse.render,
    "📊 看板": dashboard.render,
    "🤖 AI": ai_page.render,
    "🔍 问答": rag_page.render,
    "🔄 同步": sync_page.render,
}

with st.sidebar:
    st.title("📖 刷题知识库")

    # ── 模块一：刷题统计（独立卡片，小标题说明数字含义）──
    with st.container(border=True):
        st.caption("刷题统计")
        try:
            _rows = common.problem_rows()
            _dates = common.daily_dates()
            _streak = common.compute_streak(
                set(_dates), datetime.now().strftime("%Y-%m-%d")
            )
            _m1, _m2, _m3 = st.columns(3)
            _m1.metric("题解", len(_rows))
            _m2.metric("打卡", len(_dates))
            _m3.metric("连击", f"{_streak} 天")
        except Exception:
            st.caption("统计数据暂不可用")

    st.divider()

    # ── 模块二：导航（单选样式保持不变）──
    choice = st.radio("功能导航", list(PAGES.keys()), label_visibility="collapsed")

    # ── 底部备注：明暗模式提示，小字弱化 ──
    st.divider()
    st.caption(
        "🌗 明暗模式初始跟随系统；如需指定，点右上角 ⋮ → Settings → Theme"
        "（仅对你的浏览器生效）。"
    )

PAGE_TITLES = {
    "📒 笔记": "笔记浏览与管理",
    "📊 看板": "刷题统计看板",
    "🤖 AI": "AI 增强",
    "🔍 问答": "RAG 知识库问答",
    "🔄 同步": "一键同步与配置体检",
}

st.markdown(f"## {PAGE_TITLES[choice]}")
try:
    PAGES[choice]()
except Exception as e:  # 单页异常不崩整个应用，引导回命令行兜底
    st.error(f"页面渲染出错：{common.mask_sensitive(f'{type(e).__name__}: {e}')}")
    st.info("该功能仍可退回命令行入口使用：python main.py")
