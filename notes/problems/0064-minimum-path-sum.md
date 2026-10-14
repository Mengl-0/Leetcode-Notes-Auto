# LeetCode 64. 最小路径和

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/minimum-path-sum/
>
> 首次记录：2026-10-11  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def minPathSum(self, grid:List[List[int]]) -> int:
        m = len(grid)
        n = len(grid[i])
        dp = [[0]*n for _ in range m]
        for i in range m:
            if i ==0:
                dp[i][0] = grid[i][0]
            else:
                dp[i][0] = dp[i-1][0] + grid[i][0]
        for j in range n:
            if j == 0:
                dp[j][0] = grid[j][0]
            else:
                dp[0][j] = dp[0][j-1] + grid[0][j]
        for i in range(1,m):
            for j in range(1,n):
                dp[i][j] = min(dp[i-1][j],dp[i][j-1]) + grid[i][j]
        return dp[-1][-1]
```

## Go 代码

```go
func minPathSum(grid [][]int) int {
    m := len(grid)
    n := len(grid[0])
    dp := make([][]int, n)
    for i in range m{
        dp[i] = make([]int,n)
    }
    for i := range m{
        if i == 0{
            dp[i][0] = grid[i][0]
        }else{
            dp[i][0] = dp[i-1][0] + grid[i][0]
        }
    }
    for j := range n{
        if j == 0{
            dp[0][j] = grid[0][j]
        }else{
            dp[0][j] = dp[0][j-1] + grid[0][j]
        }
    }
    for i:= 1;i<m;i++{
        for j:= 1;j<n;j++{
            dp[i][j] = min(dp[i-1][j],dp[i][j-1]) + grid[i][j]
        }
    }
    return dp[i-1][j-1]
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
| 2026-10-11 | 初学 | 来自 daily 笔记自动提取 |
