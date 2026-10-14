# -*- coding:utf-8 -*-
"""
Markdown 模板生成模块

提供两套模板：
  - get_daily_note_template():  每日刷题打卡模板
  - get_problem_template():     单题算法题解模板

模板设计兼顾二期 AI 分析与三期 RAG 检索：
  - 每个章节都有独立二级标题，便于按标题层级切分知识块
  - 题解模板保留「标签 / 难度 / 考点」等结构化字段，便于后续按标签检索与统计
"""
from datetime import datetime

from config.settings import DATE_FORMAT


def get_daily_note_template(date_str: str) -> str:
    """
    返回每日刷题打卡笔记模板
    :param date_str: 日期字符串，例如 2026-10-08
    """
    return f"""# {date_str} 刷题打卡

> 记录算法刷题、学习收获、踩坑记录

## ✅ 今日完成题目

| 题号 | 题目 | 难度 | 用时 | 是否独立完成 | 题解链接 |
| ---- | ---- | ---- | ---- | ------------ | -------- |
|      |      |      |      |              |          |

> 题解链接填相对路径，如 [0001-two-sum](../problems/0001-two-sum.md)

## 📝 知识点收获

-

## ⚠️ 踩坑记录

-

## 🎯 后续计划

-

## 💡 今日总结

"""


def get_problem_template(problem_id: str, problem_name: str) -> str:
    """
    返回单道算法题题解模板
    :param problem_id: 题号，如 1
    :param problem_name: 题目名称，如 两数之和 / two-sum
    """
    created = datetime.now().strftime(DATE_FORMAT)
    return f"""# LeetCode {problem_id}. {problem_name}

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/
>
> 首次记录：{created}  ｜  复习次数：0

## 题目描述



## 思路分析



## Python 代码

```python

```

## Go 代码

```go

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
|      |          |      |
"""
