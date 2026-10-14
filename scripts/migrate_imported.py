# -*- coding:utf-8 -*-
"""
导入数据迁移脚本（一次性使用）

处理用户批量导入笔记后遇到的问题：
  1. 图片从 notes/images/ 移到 assets/，并更新 daily 笔记里的相对链接
  2. 从 daily 笔记提取每道题，自动生成 notes/problems/NNNN-slug.md
  3. 修复 daily 笔记里 Python 代码的常见语法错误（fori / dp[[ / word[j-1] / d[m][n] 等）

用法：
  python scripts/migrate_imported.py           # 执行迁移
  python scripts/migrate_imported.py --dry-run # 只看会改什么，不写盘
"""
import os
import re
import shutil
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, ASSETS_PATH, init_dir


DRY_RUN = "--dry-run" in sys.argv

# ---------------------------------------------------------------------------
# 1. 图片迁移：notes/images/ -> assets/
# ---------------------------------------------------------------------------
def migrate_images() -> None:
    """把 notes/images/ 下所有图片移到 assets/，并更新 daily md 里的链接"""
    src_dir = os.path.join(os.path.dirname(NOTES_DAILY_PATH), "images")
    if not os.path.isdir(src_dir):
        print(f"ℹ️ 没有发现 {src_dir}，跳过图片迁移")
        return

    os.makedirs(ASSETS_PATH, exist_ok=True)
    moved = 0
    for fname in os.listdir(src_dir):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")):
            continue
        src = os.path.join(src_dir, fname)
        dst = os.path.join(ASSETS_PATH, fname)
        if os.path.exists(dst):
            print(f"⚠️ 目标已存在，跳过：{fname}")
            continue
        if DRY_RUN:
            print(f"[dry] 移动图片 {fname} -> assets/")
        else:
            shutil.move(src, dst)
        moved += 1
    print(f"📦 图片迁移完成：{moved} 张")

    # 更新 daily md 里的链接：../images/ -> ../../assets/
    updated = 0
    for fname in os.listdir(NOTES_DAILY_PATH):
        if not fname.endswith(".md"):
            continue
        p = os.path.join(NOTES_DAILY_PATH, fname)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        new_text = text.replace("../images/", "../../assets/")
        if new_text != text:
            if DRY_RUN:
                print(f"[dry] 更新链接：{fname}")
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(new_text)
            updated += 1
    print(f"🔗 更新 daily 图片链接：{updated} 篇")


# ---------------------------------------------------------------------------
# 2. 从 daily 笔记提取题解，生成 problems 文件
# ---------------------------------------------------------------------------
# 题目名 -> (LeetCode 题号, 英文 slug) 映射表
# 优先匹配题目中文名称
PROBLEM_MAP = {
    "两数之和": (1, "two-sum"),
    "字母异位词分组": (49, "group-anagrams"),
    "数组异或操作": (1486, "xor-operation"),
    "好数对的数目": (1512, "number-of-good-pairs"),
    "统计好三元数组": (1534, "number-of-good-triplets"),
    "可回收且低脂产品": (1784, "recyclable-and-low-fat-products"),
    "转化成小写字母": (709, "to-lower-case"),
    "各位相加": (258, "add-digits"),
    "2的幂": (231, "power-of-two"),
    "3的幂": (326, "power-of-three"),
    "丑数": (263, "ugly-number"),
    "重新排列数组": (1470, "shuffle-the-array"),
    "转置矩阵": (867, "transpose-matrix"),
    "分割字符串的最大得分": (1422, "maximum-score-after-splitting-a-string"),
    "统计范围内的元音字符串数": (2586, "count-vowel-strings-in-ranges"),
    "山脉数组的峰顶索引": (852, "peak-index-in-a-mountain-array"),
    "移动零": (283, "move-zeroes"),
    "相交链表": (160, "intersection-of-two-linked-lists"),
    "最长连续序列": (128, "longest-consecutive-sequence"),
    "盛最多水的容器": (11, "container-with-most-water"),
    "三数之和": (15, "3sum"),
    "接雨水": (42, "trapping-rain-water"),
    "无重复字符的最长子串": (3, "longest-substring-without-repeating-characters"),
    "找到字符串中所有字母异位词": (438, "find-all-anagrams-in-a-string"),
    "只出现一次的数字": (136, "single-number"),
    "爬楼梯": (70, "climbing-stairs"),
    "斐波那契数列": (509, "fibonacci-number"),
    "第N个泰波那契数": (1137, "n-th-tribonacci-number"),
    "使用最小花费爬楼梯": (746, "min-cost-climbing-stairs"),
    "打家劫舍": (198, "house-robber"),
    "删除并获得点数": (740, "delete-and-earn"),
    "不同路径": (62, "unique-paths"),
    "最小路径和": (64, "minimum-path-sum"),
    "不同路径II": (63, "unique-paths-ii"),
    "三角形最小路径和": (120, "triangle"),
    "下降路径和": (931, "minimum-falling-path-sum"),
    "最大正方形": (221, "maximal-square"),
    "最长回文子串": (5, "longest-palindromic-substring"),
    "单词拆分": (139, "word-break"),
    "最长回文子序列": (516, "longest-palindromic-subsequence"),
    "编辑距离": (72, "edit-distance"),
}

# 题目行的正则：题目1：xxx 或 题目1：[xxx](url)
_PROBLEM_LINE_RE = re.compile(r"^题目\d+[：:]\s*(.+)$")
# 代码块
_CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)


def _extract_problems_from_daily(text: str) -> list[dict]:
    """
    从 daily 笔记文本提取每道题的信息
    :return: [{title, go_code, py_code, image}, ...]
    """
    lines = text.splitlines()
    problems = []
    current = None
    in_code = False
    code_lang = ""
    code_buf = []

    for line in lines:
        m = _PROBLEM_LINE_RE.match(line.strip())
        if m:
            if current:
                problems.append(current)
            title = m.group(1).strip()
            # 去掉 markdown 链接
            title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title).strip()
            current = {"title": title, "go_code": "", "py_code": "", "image": ""}
            continue

        # 图片
        if current and line.strip().startswith("!["):
            img_m = re.search(r"\(([^)]+)\)", line)
            if img_m:
                current["image"] = img_m.group(1)
            continue

        # 代码块
        if line.strip().startswith("```"):
            if not in_code:
                in_code = True
                code_lang = line.strip()[3:].lower()
                code_buf = []
            else:
                in_code = False
                code = "\n".join(code_buf)
                if current:
                    if "go" in code_lang:
                        current["go_code"] = code
                    elif "py" in code_lang:
                        current["py_code"] = code
            continue

        if in_code:
            code_buf.append(line)

    if current:
        problems.append(current)
    return problems


def _fix_python_code(code: str) -> str:
    """修复 daily 笔记里 Python 代码的常见语法错误"""
    if not code:
        return code
    lines = code.splitlines()
    fixed = []
    for line in lines:
        # fori -> for i
        line = re.sub(r"\bfori\b", "for i", line)
        # dp[[0]*(n+1) for _ in range(m+1)] -> dp = [[0]*(n+1) for _ in range(m+1)]
        line = re.sub(r"^(\s*)dp\[\[0\]", r"\1dp = [[0]", line)
        # word[j-1] -> word2[j-1]（在编辑距离上下文中）
        line = line.replace("word[j-1]", "word2[j-1]")
        # d[m][n] -> dp[m][n]
        line = re.sub(r"\bd\[m\]\[n\]", "dp[m][n]", line)
        # return start[...] -> return s[...]
        line = re.sub(r"\breturn start\[", "return s[", line)
        fixed.append(line)
    return "\n".join(fixed)


def _fix_go_code(code: str) -> str:
    """修复 Go 代码常见问题"""
    if not code:
        return code
    # maxsid -> maxside（最大正方形）
    code = code.replace("maxsid := 0", "maxside := 0")
    return code


def migrate_problems() -> None:
    """从 daily 笔记提取题解，生成 problems 文件"""
    os.makedirs(NOTES_PROBLEM_PATH, exist_ok=True)
    created = 0
    skipped = 0

    for fname in sorted(os.listdir(NOTES_DAILY_PATH)):
        if not fname.endswith(".md"):
            continue
        p = os.path.join(NOTES_DAILY_PATH, fname)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        for prob in _extract_problems_from_daily(text):
            title = prob["title"].strip()
            # 查题号和 slug
            pid_slug = None
            for k, v in PROBLEM_MAP.items():
                if k in title or title in k:
                    pid_slug = v
                    break
            if not pid_slug:
                print(f"⚠️ 未匹配题号：{title}（来自 {fname}），跳过")
                continue
            pid, slug = pid_slug
            filename = f"{pid:04d}-{slug}.md"
            fpath = os.path.join(NOTES_PROBLEM_PATH, filename)
            if os.path.exists(fpath):
                skipped += 1
                continue

            go_code = _fix_go_code(prob["go_code"])
            py_code = _fix_python_code(prob["py_code"])
            date_str = fname.replace(".md", "")

            content = f"""# LeetCode {pid}. {title}

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/{slug}/
>
> 首次记录：{date_str}  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
{py_code}
```

## Go 代码

```go
{go_code}
```

## 复杂度分析

- 时间复杂度：
- 空间复杂度：

## ⚠️ 踩坑记录

-

## 💡 收获与延伸

-

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| {date_str} | 初学 | 来自 daily 笔记自动提取 |
"""
            if DRY_RUN:
                print(f"[dry] 生成题解：{filename}")
            else:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
            created += 1

    print(f"📝 题解迁移完成：新建 {created} 篇，跳过已存在 {skipped} 篇")


# ---------------------------------------------------------------------------
# 3. 修复 daily 笔记里的代码语法错误
# ---------------------------------------------------------------------------
def fix_daily_code() -> None:
    """直接修复 daily 笔记里的 Python 代码语法错误"""
    fixed_count = 0
    for fname in sorted(os.listdir(NOTES_DAILY_PATH)):
        if not fname.endswith(".md"):
            continue
        p = os.path.join(NOTES_DAILY_PATH, fname)
        with open(p, "r", encoding="utf-8") as f:
            text = f.read()
        new_text = _fix_python_code(text)
        new_text = _fix_go_code(new_text)
        if new_text != text:
            if DRY_RUN:
                print(f"[dry] 修复代码：{fname}")
            else:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(new_text)
            fixed_count += 1
    print(f"🔧 修复 daily 代码语法错误：{fixed_count} 篇")


if __name__ == "__main__":
    init_dir()
    print("===== 开始迁移导入数据 =====")
    migrate_images()
    migrate_problems()
    fix_daily_code()
    print("===== 迁移完成 =====")
