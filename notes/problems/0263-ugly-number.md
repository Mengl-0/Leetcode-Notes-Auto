# LeetCode 263. 丑数

> 难度：简单｜ 标签：数学｜ 链接：https://leetcode.cn/problems/ugly-number/
>
> 首次记录：2026-10-02  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def isUgly(self, n:int) -> bool:
        if n <= 0:
            return False
        for p in [2,3,5]:
            n /= p
        return n == 1
```

## Go 代码

```go
func isUgly(n int) bool{
    if n <= 0{
        return false
    }
    for n % 2 == 0{
        n /= 2
    }
    for n % 3 == 0{
        n /= 3
    }
    for n % 5 == 0{
        n /= 5
    }
    return n == 1
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
| 2026-10-02 | 初学 | 来自 daily 笔记自动提取 |
