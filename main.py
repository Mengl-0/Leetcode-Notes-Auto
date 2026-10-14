#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
项目入口：leetcode-notes-auto 刷题自动化知识库系统
运行命令：python main.py
功能：命令行菜单，统一调度一期（自动化）/ 二期（AI 增强）/ 三期（RAG 知识库）功能
"""
import subprocess
import sys
from pathlib import Path

# Windows 下标准输出默认 GBK 编码、错误处理为 strict，print 到 emoji 会抛
# UnicodeEncodeError 崩溃。这里保留原编码（保证中文不乱码）、仅把错误处理改为 replace
# （emoji 降级为 '?'），避免崩溃。脚本侧由 config/settings.py 兜底；main.py 在导入
# settings 之前就打印菜单，因此需单独兜底。
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# 菜单项 -> (描述, 脚本文件, 分组标题)
MENU = {
    "1": ("新建【每日刷题打卡笔记】", "new_daily_note.py", "一期 · 笔记与同步自动化"),
    "2": ("新建【单题算法题解笔记】", "new_problem.py", "一期 · 笔记与同步自动化"),
    "3": ("上传图片并替换 md 文档内图片链接", "upload_img.py", "一期 · 笔记与同步自动化"),
    "4": ("一键同步：上传 + 替换 + 索引 + Git 推送", "auto_sync.py", "一期 · 笔记与同步自动化"),
    "5": ("更新笔记目录索引 NOTES_INDEX.md", "update_index.py", "一期 · 笔记与同步自动化"),
    "6": ("AI 增强：题解分析 / 每日总结 / 代码转换 / 代码检查", "ai_assist.py", "二期 · AI 增强"),
    "7": ("RAG 私有知识库：建索引 / 笔记问答 / 检索", "rag_query.py", "三期 · RAG 知识库"),
    "8": ("配置体检：查看各模块配置是否就绪", None, "系统"),
}


def show_menu():
    print("=" * 60)
    print("📖 LeetCode Notes Auto · 刷题自动化知识库系统")
    print("=" * 60)
    current_group = None
    for key, (desc, _, group) in MENU.items():
        if group != current_group:
            print(f"\n【{group}】")
            current_group = group
        print(f"  {key}. {desc}")
    print("\n  0. 退出程序")
    print("=" * 60)


def run_script(script_name: str):
    """用 subprocess 运行 scripts 下的脚本"""
    script = SCRIPTS_DIR / script_name
    if not script.exists():
        print(f"❌ 脚本不存在：{script}")
        return
    try:
        result = subprocess.run([sys.executable, str(script)])
        if result.returncode != 0:
            print(f"⚠️ 脚本 {script_name} 退出码：{result.returncode}")
    except KeyboardInterrupt:
        print("\n⏹️ 已中断当前脚本")
    except Exception as e:
        print(f"❌ 运行 {script_name} 失败：{e}")


def run_config_check():
    """菜单 8：配置体检（进程内直接调用，避免子进程重复初始化）"""
    sys.path.insert(0, str(BASE_DIR))
    try:
        from config.settings import check_config
        check_config()
    except Exception as e:
        print(f"❌ 配置体检失败：{e}")


def main():
    while True:
        show_menu()
        try:
            choice = input("👉 请输入功能序号：").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n👋 程序退出")
            break

        if choice == "0":
            print("👋 程序退出")
            break

        if choice not in MENU:
            print("❌ 输入无效，请重新选择！")
            continue

        _, script_name, _ = MENU[choice]
        if script_name is None:
            run_config_check()
        else:
            run_script(script_name)

        try:
            input("\n按回车返回菜单...")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 程序退出")
            break


if __name__ == "__main__":
    main()
