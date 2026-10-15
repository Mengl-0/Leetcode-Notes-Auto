# LeetCode 258. 各位相加

> 难度：简单｜ 标签：数学｜ 链接：https://leetcode.cn/problems/add-digits/
>
> 首次记录：2026-10-01  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def addGigits(self, num: int) -> int:
        if num == 0:
            return 0
        return 9 if num % 9 == 9 else num % 9
```

## Go 代码

```go
func addGigits(num int) int {
    if num == 0{
        return 0
    }
    if num % 9 == 0{
        return  9
    }
    return num % 9
}
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
| 2026-10-01 | 初学 | 来自 daily 笔记自动提取 |
