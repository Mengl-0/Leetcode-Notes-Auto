# LeetCode 1137. 第N个泰波那契数

> 难度：简单｜ 标签：动态规划、斐波那契数列｜ 链接：https://leetcode.cn/problems/n-th-tribonacci-number/
>
> 首次记录：2026-10-08  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def tribonacci(self,n: int) -> int:
        if n == 0:
            return 0
        if n == 1 or n== 2:
            return 1
        a,b,c = 0,1,1
        for i in range(3,n+1):
            a,b,c = b,c,a+b+c
        return c
```

## Go 代码

```go
func tribonacci(n int) int{
    if n ==0{
        return 0
    }
    if n ==1||n==2{
        return 1
    }
    a,b,c := 0,1,1
    for i:=3;i<=n;i++{
        a,b,c = b,c,a+b+c
    }
    return c
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
