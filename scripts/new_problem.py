# -*- coding:utf-8 -*-
"""
新建单道算法题题解 md 文件
命名规范：4 位补零题号 + 连字符 + 英文 slug，如 0001-two-sum.md
用法：python scripts/new_problem.py  （交互输入题号、英文 slug、文档标题）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_PROBLEM_PATH
from core.md_template import get_problem_template


def slugify(raw: str) -> str:
    """把 slug 规范为小写、仅含字母数字和连字符；非法则返回空串"""
    s = raw.strip().lower().replace("_", "-")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def build_filename(pid: str, slug: str) -> str:
    """按规范生成文件名：0001-two-sum.md"""
    if not pid.isdigit():
        raise ValueError(f"题号必须是数字：{pid}")
    if not slug:
        raise ValueError("英文 slug 不能为空（例如 two-sum）")
    return f"{int(pid):04d}-{slug}.md"


def create_problem_note(pid: str, slug_raw: str, title: str = ""):
    slug = slugify(slug_raw)
    try:
        filename = build_filename(pid.strip(), slug)
    except ValueError as e:
        print(f"❌ {e}")
        return None

    full_path = os.path.join(NOTES_PROBLEM_PATH, filename)
    if os.path.exists(full_path):
        print(f"⚠️ 文件已存在：{full_path}")
        return full_path

    display_title = (title or "").strip() or slug
    content = get_problem_template(str(int(pid)), display_title)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 新建题解笔记成功：{full_path}")
    return full_path


if __name__ == "__main__":
    try:
        pid = input("请输入LeetCode题号（数字）：").strip()
        slug = input("请输入英文slug（小写连字符，如 two-sum）：").strip()
        title = input("请输入文档标题（中/英文均可，回车默认用slug）：").strip()
        if not pid or not slug:
            print("❌ 题号和 slug 不能为空")
            sys.exit(1)
        create_problem_note(pid, slug, title)
    except KeyboardInterrupt:
        print("\n⏹️ 已取消")
