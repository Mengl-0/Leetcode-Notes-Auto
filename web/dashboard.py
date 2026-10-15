# -*- coding:utf-8 -*-
"""页面二：刷题统计看板（只读，口径可解释）

数据来源：notes/problems 题解元数据头（难度/标签/首次记录/复习次数）与 notes/daily 打卡文件。
清洗规则（与方案第四章一致）：
- 难度缺失 → 归「未标注」单独统计，不污染分布
- 首次记录非法 → 回退文件修改时间并计数提示
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

import common
from core import notes_io

try:  # plotly 仅作可选点缀（难度环形图）；未安装时自动降级为原生条形图
    import plotly.express as px
except Exception:  # pragma: no cover - 取决于运行环境
    px = None

_PIE_COLORS = {"简单": "#2ecc71", "中等": "#f1c40f", "困难": "#e74c3c", "未标注": "#95a5a6"}


def _to_df(rows: "list[dict]") -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["tags_str"] = df["tags"].apply(lambda ts: "、".join(ts) if isinstance(ts, list) else "")
    return df


def _apply_filter(df: pd.DataFrame, days: "int | None", diff: str, tag: str) -> pd.DataFrame:
    out = df
    if days is not None:
        today = pd.Timestamp(datetime.now().date())
        out = out[(out["date"] >= today - pd.Timedelta(days=days)) & (out["date"] <= today)]
    if diff != "全部":
        out = out[out["difficulty"] == diff]
    if tag != "全部":
        out = out[out["tags"].apply(lambda ts: tag in ts)]
    return out


def render() -> None:
    rows = common.problem_rows()
    if not rows:
        st.info("还没有题解笔记，先去「笔记浏览与管理」建一篇吧。")
        return

    df_all = _to_df(rows)
    dates = set(common.daily_dates())
    today_str = datetime.now().strftime("%Y-%m-%d")

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        range_opt = st.selectbox("时间区间", ["全部", "近 7 天", "近 30 天"], key="dash_range")
    days = {"全部": None, "近 7 天": 7, "近 30 天": 30}[range_opt]
    with c2:
        diff_f = st.selectbox("难度", ["全部", *common.DIFFICULTY_ORDER], key="dash_diff")
    with c3:
        all_tags = sorted({t for r in rows for t in r["tags"]})
        tag_f = st.selectbox("标签", ["全部", *all_tags], key="dash_tag")

    df = _apply_filter(df_all, days, diff_f, tag_f)
    fallback_n = common.problem_fallback_count()

    st.markdown("### 关键指标")
    k = st.columns(5)
    this_week = df_all[
        df_all["date"] >= pd.Timestamp(datetime.now().date()) - timedelta(days=6)
    ]
    k[0].metric("题解总数", len(df_all))
    k[1].metric("区间题数", len(df))
    k[2].metric("本周新增", len(this_week))
    k[3].metric("连续打卡", f"{common.compute_streak(dates, today_str)} 天")
    k[4].metric("打卡总天数", len(dates))
    if diff_f == "全部" and tag_f == "全部" and days is None:
        unlabeled = int((df_all["difficulty"] == "未标注").sum())
        tips = []
        if unlabeled:
            tips.append(f"{unlabeled} 篇题解未标注难度（已单独归类，建议补全元数据）")
        if fallback_n:
            tips.append(f"{fallback_n} 篇首次记录日期非法，已回退为文件修改时间")
        if tips:
            st.caption("⚠️ 数据质量：" + "；".join(tips))

    st.markdown("### 刷题趋势")
    if df.empty:
        st.warning("筛选后无数据，无法绘制趋势。")
        trend_ok = False
    else:
        trend_ok = True
        daily = df.groupby(df["date"].dt.date).size().rename("题数").reset_index()
        daily["date"] = pd.to_datetime(daily["date"])
        t1, t2 = st.columns(2)
        with t1:
            st.caption("每日题数")
            st.line_chart(daily, x="date", y="题数", x_label="日期", y_label="当日题数")
        with t2:
            st.caption("每周题数")
            weekly = (
                df.set_index("date").resample("W-SUN").size().rename("题数").reset_index()
            )
            st.bar_chart(weekly, x="date", y="题数", x_label="周", y_label="每周题数")

    if trend_ok:
        st.markdown("### 进度与分布")
        p1, p2, p3 = st.columns(3)
        with p1:
            target = st.number_input("目标题数", min_value=1, value=max(50, len(df_all) + 10),
                                     step=10, key="dash_target")
            ratio = min(len(df_all) / target, 1.0)
            st.progress(ratio, text=f"累计完成 {len(df_all)} / {target}（{ratio:.0%}）")
            if len(df):
                st.metric("当前区间平均复习次数", f"{df['reviews'].mean():.2f}")
        with p2:
            dist = df["difficulty"].value_counts().reindex(
                [d for d in common.DIFFICULTY_ORDER if d in set(df["difficulty"])]
            )
            if px is not None:  # 可选点缀：装了 plotly 就用环形图
                fig_p = px.pie(names=dist.index, values=dist.values, hole=0.45,
                               color=dist.index, color_discrete_map=_PIE_COLORS)
                fig_p.update_layout(showlegend=True, margin=dict(l=0, r=0, t=10, b=0))
                st.plotly_chart(fig_p, width="stretch")
            else:  # 原生兜底，且随明暗主题自动换色
                st.caption("难度分布")
                st.bar_chart(dist.rename("题数"), horizontal=True,
                             x_label="难度", y_label="题数")
        with p3:
            tag_cnt: "dict[str, int]" = {}
            for ts in df["tags"]:
                for t in ts:
                    tag_cnt[t] = tag_cnt.get(t, 0) + 1
            if tag_cnt:
                s = pd.Series(tag_cnt).sort_values().rename("题数")
                st.caption("标签分布")
                st.bar_chart(s, horizontal=True, x_label="标签", y_label="题数")
            else:
                st.info("当前区间内题目均未打标签。")

        st.markdown("### 待复习 Top 榜（复习次数少且记录较早优先）")
        top = df.assign(age=(pd.Timestamp(datetime.now().date()) - df["date"]).dt.days)
        top = top.sort_values(["reviews", "age"], ascending=[True, False]).head(10)
        st.dataframe(
            top[["pid", "title", "difficulty", "tags_str", "date_str", "reviews", "age"]],
            width="stretch", hide_index=True,
            column_config={
                "pid": "题号", "title": "题目", "difficulty": "难度",
                "tags_str": "标签", "date_str": "首次记录",
                "reviews": "复习次数", "age": "距今(天)",
            },
        )

        st.markdown("### 从统计回到明细")
        pick_pid = st.text_input("输入题号定位该题在明细中的位置", key="dash_jump")
        if pick_pid.strip():
            path, _logs, _err = common.run_captured(
                notes_io.find_problem_note, pick_pid
            )
            if path:
                st.session_state["jump_to_fname"] = os.path.basename(path)
                st.success(
                    f"已定位 {os.path.basename(path)}，请切换到「笔记浏览与管理 → 单题题解」查看正文。"
                )
            else:
                st.warning("未找到该题号对应的题解笔记。")
