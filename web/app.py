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
from datetime import datetime
from streamlit import config as st_config  # 用于运行时切换原生明暗主题

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

def _native_dark() -> bool:
    """当前 Streamlit 原生主题是否为暗色；取不到（旧版本）时按浅色处理"""
    try:
        return str(st.context.theme.get("type") or "").lower() == "dark"
    except Exception:
        return False


def _theme_switch() -> None:
    """明暗主题开关（纯原生实现：不注入 CSS、不引入任何第三方组件库）

    暗色适合读代码，浅色适合读长笔记。三种切换方式互为兜底：
    1. 本开关 —— 调用 Streamlit 自带 theme 配置，即时生效
    2. 右上角 ⋮ → Settings → Theme —— Streamlit 原生菜单，始终可用
    3. .streamlit/config.toml 的 [theme] / [theme.light] / [theme.dark] —— 改默认配色
    """
    cur_dark = _native_dark()
    if "ui_dark_mode" not in st.session_state:
        st.session_state["ui_dark_mode"] = cur_dark  # 首启跟随原生主题
    dark = st.toggle(
        "🌙 暗色模式",
        key="ui_dark_mode",
        help=(
            "暗色适合读代码，浅色适合读长笔记。"
            "此开关作用于当前应用实例（本地自用无差异；线上为共享实例，会影响所有访客）；"
            "若只想改自己的显示，请用右上角 ⋮ → Settings → Theme。"
        ),
    )
    prev = st.session_state.get("_theme_prev")
    if prev is None:
        st.session_state["_theme_prev"] = dark  # 记录基线，避免与原生菜单互相覆盖
        return
    if dark == prev:
        return
    st.session_state["_theme_prev"] = dark  # 仅响应用户手动切换
    if dark == cur_dark:
        return
    try:
        st_config.set_option("theme.base", "dark" if dark else "light")
        st.rerun()
    except Exception:
        st.caption("⚠️ 应用内切换不可用，请改用右上角 ⋮ → Settings → Theme 切换明暗主题。")


with st.sidebar:
    st.title("📖 LeetCode 知识库")
    st.caption("刷题 · 沉淀 · 复盘 · 问答")
    # 轻量总览：无论停在哪个页面，侧栏都能看到进度（统计失败不影响导航）
    try:
        _rows = common.problem_rows()
        _dates = common.daily_dates()
        _streak = common.compute_streak(set(_dates), datetime.now().strftime("%Y-%m-%d"))
        _m1, _m2, _m3 = st.columns(3)
        _m1.metric("题解", len(_rows))
        _m2.metric("打卡", len(_dates))
        _m3.metric("连击", f"{_streak}天")
    except Exception:
        pass
    choice = st.radio("功能导航", list(PAGES.keys()), label_visibility="collapsed")
    st.divider()
    _theme_switch()

st.markdown(f"## {choice}")
try:
    PAGES[choice]()
except Exception as e:  # 单页异常不崩整个应用，引导回命令行兜底
    st.error(f"页面渲染出错：{common.mask_sensitive(f'{type(e).__name__}: {e}')}")
    st.info("该功能仍可退回命令行入口使用：python main.py")
