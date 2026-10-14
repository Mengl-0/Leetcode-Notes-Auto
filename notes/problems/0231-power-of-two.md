# LeetCode 231. 2的幂

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/power-of-two/
>
> 首次记录：2026-10-02  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def isPowerOfTwo(self,  n: int) -> bool:
        return n > 0 and (n & (n-1)) == 0
```

## Go 代码

```go
func isPowerOfTwo(n int) bool {
    return n > 0 && (n & (n-1)) == 0
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
