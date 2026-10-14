# -*- coding:utf-8 -*-
"""
自动生成笔记目录索引（NOTES_INDEX.md）
扫描 notes/daily 与 notes/problems，读取标题，按时间/题号列出导航链接
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, BASE_DIR, init_dir

INDEX_PATH = os.path.join(BASE_DIR, "NOTES_INDEX.md")
_TITLE_RE = re.compile(r"^#\s+(.+?)\s*$")


def _collect(dir_path: str) -> "list[str]":
    if not os.path.isdir(dir_path):
        return []
    return sorted(f for f in os.listdir(dir_path) if f.endswith(".md"))


def _read_title(path: str, fallback: str) -> str:
    """读取 md 首个一级标题作为展示名，取不到用文件名"""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                m = _TITLE_RE.match(line.strip())
                if m:
                    return m.group(1).strip()
                if line.strip():
                    break
    except OSError:
        pass
    return fallback


def _problem_sort_key(fname: str) -> "tuple[int, int, str]":
    """题解按 4 位题号排序，命名不规范的排在最后"""
    head = fname.split("-")[0]
    return (0, int(head), fname) if head.isdigit() else (1, 0, fname)


def regenerate_index() -> str:
    """重新生成 NOTES_INDEX.md 索引文件"""
    # 每日笔记按日期倒序（最新在前），与 core/notes_io.list_daily_notes 保持一致
    daily = sorted(_collect(NOTES_DAILY_PATH), reverse=True)
    problems = sorted(_collect(NOTES_PROBLEM_PATH), key=_problem_sort_key)

    lines = [
        "# 刷题笔记索引",
        "",
        f"> 自动生成，请勿手动编辑。共 {len(daily)} 篇每日打卡、{len(problems)} 篇题解。",
        "",
        "## 📅 每日打卡笔记",
        "",
    ]
    if daily:
        for f in daily:
            title = _read_title(os.path.join(NOTES_DAILY_PATH, f), f[:-3])
            lines.append(f"- [{title}](notes/daily/{f})")
    else:
        lines.append("- （暂无）")

    lines += ["", "## 🧗 单题题解", ""]
    if problems:
        for f in problems:
            title = _read_title(os.path.join(NOTES_PROBLEM_PATH, f), f[:-3])
            lines.append(f"- [{title}](notes/problems/{f})")
    else:
        lines.append("- （暂无）")
    lines.append("")

    with open(INDEX_PATH, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    print(f"✅ 索引已更新：{INDEX_PATH}")
    return INDEX_PATH


def run() -> None:
    """供 main.py 进程内调用的入口（审计问题 4）"""
    init_dir()
    regenerate_index()


if __name__ == "__main__":
    run()
