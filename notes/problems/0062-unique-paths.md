# LeetCode 62. 不同路径

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/unique-paths/
>
> 首次记录：2026-10-10  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def uniquePaths(self, m int, n int) -> int:
        dp = [[0]*n for _ in range(m)]
        for i in range(m):
            dp[i][0] = 1
        for i in range(n):
            dp[0][i] = 1
        for i in range(1,m):
            for j in range(1,n):
                dp[i][j] = dp[i-1][j] + dp[i][j-1]
        return dp[-1][-1]
```

## Go 代码

```go
func uniquePaths(m int,n int) int{
    dp := make([][]int , m)
    for i := range(m){
        dp[i] = make([]int,n)
    }
    for i := range(m){
        dp[i][0] = 1
    }
    for i := range(n){
        dp[0][i] = 1
    }
    for i:= 1;i<m;i++{
        for j:=1;j<n;j++{
            dp[i][j] = dp[i-1][j] + dp[i][j-1]
        }
    }
    return dp[m-1][n-1]
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
| 2026-10-10 | 初学 | 来自 daily 笔记自动提取 |
