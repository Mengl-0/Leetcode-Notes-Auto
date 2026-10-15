# LeetCode 1486. 数组异或操作

> 难度：简单｜ 标签：循环｜ 链接：https://leetcode.cn/problems/xor-operation/
>
> 首次记录：2026-09-30  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python

```

## Go 代码

```go
func xorOperation(n int,start int) int{
    res, num := 0, 0
    for i :=0; i < n; i++ {
        num = start + 2 * i
        res ^= num
    }
    return res
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
| 2026-09-30 | 初学 | 来自 daily 笔记自动提取 |
