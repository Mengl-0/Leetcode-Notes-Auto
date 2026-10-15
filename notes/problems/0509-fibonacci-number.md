# LeetCode 509. 斐波那契数列

> 难度：简单｜ 标签：动态规划｜ 链接：https://leetcode.cn/problems/fibonacci-number/
>
> 首次记录：2026-10-08  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def fib(self,n: int) -> int:
        if n <=1:
            return n
        a = 1
        b = 2
        for i in range(2,n+1):
            a,b = b,a+b
        return b
```

## Go 代码

```go
func fib(n int) int{
    if n <= 1{
        return n
    }
    nums :=make([]int,n+1)
    nums[0] = 0
    nums[1] = 1
    for i:= 2;i<=n;i++{
        nums[i] = nums[i-1] + nums[i-2]
    }
    return nums[n]
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
| 2026-10-08 | 初学 | 来自 daily 笔记自动提取 |
