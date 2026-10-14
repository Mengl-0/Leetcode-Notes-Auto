# -*- coding:utf-8 -*-
"""
AI 增强脚本（二期）
子菜单：
  1. 分析某道题目题解（思路 / 复杂度 / 易错点）
  2. 生成今日刷题收获总结
  3. Python 代码转 Go 代码
  4. 代码 bug 检测

用法：python scripts/ai_assist.py  （交互选择）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import ai_helper
from config.settings import init_dir
from core.notes_io import (
    list_problem_notes,
    latest_daily_note,
    read_text,
    find_problem_note,
    today_str,
)


def _print_divider(title: str = "") -> None:
    print("\n" + "=" * 50)
    if title:
        print(title)
        print("=" * 50)


def analyze_problem_flow() -> None:
    """菜单 1：分析某道题目题解"""
    _print_divider("🧠 AI 分析题目题解")
    notes = list_problem_notes()
    if not notes:
        print("ℹ️ 还没有题解笔记，请先用【新建题目笔记】创建")
        return
    print("已有题解笔记：")
    for i, p in enumerate(notes, 1):
        print(f"  {i}. {os.path.basename(p)}")
    key = input("请输入题号 / slug / 序号：").strip()
    if not key:
        return

    path = None
    if key.isdigit() and int(key) <= len(notes):
        path = notes[int(key) - 1]
    else:
        path = find_problem_note(key)
    if not path:
        print(f"❌ 未找到匹配的题解笔记：{key}")
        return

    text = read_text(path)
    print(f"\n正在分析：{os.path.basename(path)} ...")
    result = ai_helper.analyze_problem(text)
    if result:
        print("\n----- AI 分析结果 -----\n")
        print(result)


def summarize_daily_flow() -> None:
    """菜单 2：生成今日刷题收获总结"""
    _print_divider("📝 AI 生成每日刷题总结")
    date_str = input(f"请输入日期（YYYY-MM-DD，回车默认今天 {today_str()}）：").strip()
    path = latest_daily_note(date_str)
    if not path:
        print("❌ 未找到该日期的每日笔记")
        return
    text = read_text(path)
    # 附带当天相关的题解内容，让总结更有依据
    print(f"\n正在总结：{os.path.basename(path)} ...")
    result = ai_helper.summarize_daily(text)
    if result:
        print("\n----- AI 总结结果 -----\n")
        print(result)
        save = input("\n是否把总结追加写入该笔记？(y/N)：").strip().lower()
        if save == "y":
            # 日期标签用所选笔记对应的日期（文件名），而不是运行当天，
            # 避免对历史笔记生成总结时把标签写错（审计问题 2）
            note_date = os.path.splitext(os.path.basename(path))[0]
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n\n## 🤖 AI 总结（{note_date}）\n\n{result}\n")
            print("✅ 已追加写入笔记")


def convert_flow() -> None:
    """菜单 3：Python 代码转 Go"""
    _print_divider("🔄 Python 转 Go")
    print("粘贴 Python 代码，输入单独一行 EOF 结束：")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "EOF":
            break
        lines.append(line)
    code = "\n".join(lines)
    result = ai_helper.convert_py_to_go(code)
    if result:
        print("\n----- 转换结果 -----\n")
        print(result)


def review_flow() -> None:
    """菜单 4：代码 bug 检测"""
    _print_divider("🔍 代码 bug 检测")
    lang = input("代码语言（python/go，默认 python）：").strip().lower() or "python"
    print("粘贴代码，输入单独一行 EOF 结束：")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line.strip() == "EOF":
            break
        lines.append(line)
    code = "\n".join(lines)
    result = ai_helper.review_code(code, lang)
    if result:
        print("\n----- Review 结果 -----\n")
        print(result)


def main() -> None:
    if not ai_helper.is_configured():
        print("❌ 尚未配置 DeepSeek，无法使用 AI 功能。")
        print("💡 复制 config/config.example.env 为 config/secret.env 并填写 DEEPSEEK_API_KEY 后重试")
        return
    while True:
        _print_divider("🤖 AI 增强功能（二期）")
        print("1. 分析某道题目题解")
        print("2. 生成每日刷题收获总结")
        print("3. Python 代码转 Go 代码")
        print("4. 代码 bug 检测")
        print("0. 返回")
        opt = input("请选择：").strip()
        if opt == "0":
            break
        elif opt == "1":
            analyze_problem_flow()
        elif opt == "2":
            summarize_daily_flow()
        elif opt == "3":
            convert_flow()
        elif opt == "4":
            review_flow()
        else:
            print("❌ 无效选择")


def run() -> None:
    """供 main.py 进程内调用的入口（审计问题 4）"""
    init_dir()
    main()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n⏹️ 已取消")
