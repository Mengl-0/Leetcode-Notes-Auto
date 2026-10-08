# -*- coding:utf-8 -*-
"""
自动生成笔记目录索引（NOTES_INDEX.md）
扫描 notes/daily 与 notes/problems，按时间/题号列出导航链接
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, BASE_DIR

INDEX_PATH = os.path.join(BASE_DIR, "NOTES_INDEX.md")


def _collect(dir_path: str):
    if not os.path.isdir(dir_path):
        return []
    return sorted(f for f in os.listdir(dir_path) if f.endswith(".md"))


def regenerate_index():
    """重新生成 NOTES_INDEX.md 索引文件"""
    daily = _collect(NOTES_DAILY_PATH)
    problems = _collect(NOTES_PROBLEM_PATH)
    problems_sorted = sorted(
        problems,
        key=lambda f: (int(f.split("_")[0]) if f.split("_")[0].isdigit() else 10**9, f),
    )

    lines = ["# 刷题笔记索引", "", f"> 自动生成，请勿手动编辑。共 {len(daily)} 篇每日打卡、{len(problems_sorted)} 篇题解。", ""]
    lines.append("## 📅 每日打卡笔记")
    lines.append("")
    if daily:
        for f in daily:
            lines.append(f"- [{f[:-3]}](notes/daily/{f})")
    else:
        lines.append("- （暂无）")
    lines.append("")
    lines.append("## 🧗 单题题解")
    lines.append("")
    if problems_sorted:
        for f in problems_sorted:
            lines.append(f"- [{f[:-3]}](notes/problems/{f})")
    else:
        lines.append("- （暂无）")
    lines.append("")

    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"✅ 索引已更新：{INDEX_PATH}")
    return INDEX_PATH


if __name__ == "__main__":
    regenerate_index()
