# -*- coding:utf-8 -*-
"""
一键全流程同步：上传图片 → 替换 md 链接 → 更新索引 → Git 提交推送
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.upload_img import batch_upload_assets, scan_all_md_replace
from scripts.update_index import regenerate_index
from core.git_auto import git_commit_and_push


def run_auto_sync():
    print("===== 开始自动同步 =====")
    print("1️⃣ 批量上传 assets 图片")
    batch_upload_assets()
    print("2️⃣ 扫描 md 替换图片链接")
    scan_all_md_replace()
    print("3️⃣ 更新笔记目录索引")
    regenerate_index()
    changed = datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"auto update: 同步刷题笔记 {changed}"
    print("4️⃣ Git 提交推送")
    git_commit_and_push(commit_msg)
    print("===== 同步任务结束 =====")


if __name__ == "__main__":
    run_auto_sync()
