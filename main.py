#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
项目入口：leetcode-notes-auto 刷题笔记自动化系统
运行命令：python main.py
功能：命令行菜单，选择调用各个脚本模块
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR / "scripts"

# 菜单项 -> 脚本文件
MENU = {
    "1": ("新建【每日刷题打卡笔记】", "new_daily_note.py"),
    "2": ("新建【单题算法题解笔记】", "new_problem.py"),
    "3": ("上传图片并替换md文档内图片链接", "upload_img.py"),
    "4": ("一键同步：上传图片 + Git提交推送到GitHub", "auto_sync.py"),
}


def show_menu():
    print("=" * 50)
    print("📖 LeetCode Notes Auto 刷题笔记自动化工具")
    print("=" * 50)
    for key, (desc, _) in MENU.items():
        print(f"{key}. {desc}")
    print("0. 退出程序")
    print("=" * 50)


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


def main():
    while True:
        show_menu()
        choice = input("👉 请输入功能序号：").strip()

        if choice == "0":
            print("👋 程序退出")
            break

        if choice in MENU:
            _, script_name = MENU[choice]
            run_script(script_name)
        else:
            print("❌ 输入无效，请重新选择！")

        input("\n按回车返回菜单...")


if __name__ == "__main__":
    main()