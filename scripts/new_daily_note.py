# -*- coding:utf-8 -*-
"""
新建每日刷题打卡笔记脚本
用法：python scripts/new_daily_note.py [yyyy-mm-dd]  不传日期默认今天
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_DAILY_PATH, DATE_FORMAT
from core.md_template import get_daily_note_template


def create_daily_note(date_str: str = None):
    if date_str:
        try:
            date_str = datetime.strptime(date_str, DATE_FORMAT).strftime(DATE_FORMAT)
        except ValueError:
            print(f"❌ 日期格式错误：{date_str}，应为 yyyy-mm-dd")
            return None
    else:
        date_str = datetime.now().strftime(DATE_FORMAT)

    filename = f"{date_str}.md"
    full_path = os.path.join(NOTES_DAILY_PATH, filename)

    if os.path.exists(full_path):
        print(f"⚠️ 今日笔记已存在：{full_path}")
        return full_path

    content = get_daily_note_template(date_str)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 新建每日笔记成功：{full_path}")
    return full_path


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    create_daily_note(arg)
