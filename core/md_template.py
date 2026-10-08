# -*- coding:utf-8 -*-
"""
Markdown 模板生成模块
提供两套模板：每日刷题打卡模板、单题算法题解模板
"""


def get_daily_note_template(date_str: str) -> str:
    """
    返回每日刷题打卡笔记模板
    :param date_str: 日期字符串，例如 2026-10-08
    """
    return f"""# {date_str} 刷题打卡

> 记录算法刷题、学习收获、踩坑记录

## ✅ 今日完成题目

| 题号 | 题目 | 难度 | 用时 | 是否独立完成 |
| ---- | ---- | ---- | ---- | ------------ |
|      |      |      |      |              |

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
    :param problem_name: 题目名称，如 两数之和
    """
    return f"""# LeetCode {problem_id}. {problem_name}

> 难度：  ｜ 标签：  ｜ 链接：

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
