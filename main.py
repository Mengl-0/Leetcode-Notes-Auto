#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
项目入口：leetcode-notes-auto 刷题自动化知识库系统
运行命令：python main.py
功能：命令行菜单，统一调度一期（自动化）/ 二期（AI 增强）/ 三期（RAG 知识库）功能

菜单调度方式（审计问题 4）：各脚本均暴露 run() 函数，主菜单进程内直接调用，
不再为每个菜单项重启 Python 解释器（省去重复 import、重读密钥、重建日志 handler
与 RAG 索引重载），切换显著更快；各 scripts/*.py 保留 __main__ 块，仍可单独运行。
"""
import importlib
import sys
from pathlib import Path

# Windows 下标准输出默认 GBK 编码、错误处理为 strict，print 到 emoji 会抛
# UnicodeEncodeError 崩溃。真实终端走宽字符 API 本就能显示 emoji，仅改 errors
# 防崩溃；输出被捕获重定向时（VS Code 等）改按 UTF-8 输出，emoji 不再变 '?'
# （审计问题 8）。脚本侧由 config/settings.py 兜底；main.py 在导入 settings
# 之前就打印菜单，因此需单独兜底。
for _stream in (sys.stdout, sys.stderr):
    if _stream is None or not hasattr(_stream, "reconfigure"):
        continue
    try:
        if _stream.isatty():
            _stream.reconfigure(errors="replace")
        else:
            _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# 菜单项 -> (描述, 模块名（scripts 包下，None 表示配置体检）, 分组标题)
MENU = {
    "1": ("新建【每日刷题打卡笔记】", "new_daily_note", "一期 · 笔记与同步自动化"),
    "2": ("新建【单题算法题解笔记】", "new_problem", "一期 · 笔记与同步自动化"),
    "3": ("上传图片并替换 md 文档内图片链接", "upload_img", "一期 · 笔记与同步自动化"),
    "4": ("一键同步：上传 + 替换 + 索引 + Git 推送", "auto_sync", "一期 · 笔记与同步自动化"),
    "5": ("更新笔记目录索引 NOTES_INDEX.md", "update_index", "一期 · 笔记与同步自动化"),
    "6": ("AI 增强：题解分析 / 每日总结 / 代码转换 / 代码检查", "ai_assist", "二期 · AI 增强"),
    "7": ("RAG 私有知识库：建索引 / 笔记问答 / 检索", "rag_query", "三期 · RAG 知识库"),
    "8": ("配置体检：查看各模块配置是否就绪", None, "系统"),
}


def show_menu() -> None:
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


def run_script(module_name: str) -> None:
    """进程内调用 scripts 包下模块的 run()（审计问题 4：不再 subprocess 重启解释器）"""
    try:
        module = importlib.import_module(f"scripts.{module_name}")
        module.run()
    except KeyboardInterrupt:
        print("\n⏹️ 已中断当前功能")
    except Exception as e:
        print(f"❌ 运行 {module_name} 失败：{e}")


def run_config_check() -> None:
    """菜单 8：配置体检（进程内直接调用，避免子进程重复初始化）"""
    try:
        from config.settings import check_config, init_dir
        init_dir()
        check_config()
    except Exception as e:
        print(f"❌ 配置体检失败：{e}")


def main() -> None:
    # 目录初始化从 settings 模块导入副作用改为入口显式调用（审计问题 11）
    from config.settings import init_dir
    init_dir()

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

        _, module_name, _ = MENU[choice]
        if module_name is None:
            run_config_check()
        else:
            run_script(module_name)

        try:
            input("\n按回车返回菜单...")
        except (KeyboardInterrupt, EOFError):
            print("\n👋 程序退出")
            break


if __name__ == "__main__":
    main()
