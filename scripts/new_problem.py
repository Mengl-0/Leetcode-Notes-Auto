# -*- coding:utf-8 -*-
"""
新建单道算法题题解 md 文件
用法：python scripts/new_problem.py （交互输入题号与题目名称）
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_PROBLEM_PATH
from core.md_template import get_problem_template


def _safe_filename(name: str) -> str:
    """过滤 Windows/Linux 文件名非法字符"""
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip() or "未命名题目"


def create_problem_note(pid: str, pname: str):
    pid = _safe_filename(pid)
    pname = _safe_filename(pname)
    filename = f"{pid}_{pname}.md"
    full_path = os.path.join(NOTES_PROBLEM_PATH, filename)

    if os.path.exists(full_path):
        print(f"⚠️ 文件已存在：{full_path}")
        return full_path

    content = get_problem_template(pid, pname)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 新建题解笔记成功：{full_path}")
    return full_path


if __name__ == "__main__":
    try:
        pid = input("请输入LeetCode题号：").strip()
        pname = input("请输入题目名称：").strip()
        if not pid or not pname:
            print("❌ 题号和题目名称不能为空")
            sys.exit(1)
        create_problem_note(pid, pname)
    except KeyboardInterrupt:
        print("\n⏹️ 已取消")
