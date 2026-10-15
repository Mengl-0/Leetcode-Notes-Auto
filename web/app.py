#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
LeetCode-Notes-Auto Web 可视化界面（四期 · 可视化界面）

启动命令（项目根目录）：streamlit run web/app.py

设计约束（见《可视化界面后续优化方案》）：
- 依赖方向 web/ -> scripts/ -> core/ -> config/，界面层只调用不修改下层
- 每个页面功能与 main.py 命令行菜单对齐，无界面环境仍可用命令行兜底
- 浏览/统计/检索只读；新建、写回、同步等写操作保留二次确认
"""
import streamlit as st

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

PAGES = {
    "📒 笔记浏览与管理": browse.render,
    "📊 刷题统计看板": dashboard.render,
    "🤖 AI 增强": ai_page.render,
    "🔍 RAG 知识库问答": rag_page.render,
    "🔄 一键同步与配置体检": sync_page.render,
}

with st.sidebar:
    st.title("📖 LeetCode 知识库")
    st.caption("刷题 · 沉淀 · 复盘 · 问答")
    choice = st.radio("功能导航", list(PAGES.keys()), label_visibility="collapsed")

st.markdown(f"## {choice}")
try:
    PAGES[choice]()
except Exception as e:  # 单页异常不崩整个应用，引导回命令行兜底
    st.error(f"页面渲染出错：{type(e).__name__}: {e}")
    st.info("该功能仍可退回命令行入口使用：python main.py")
