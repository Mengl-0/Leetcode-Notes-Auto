# LeetCode 931. 下降路径和

> 难度：中等｜ 标签：矩阵、动态规划｜ 链接：https://leetcode.cn/problems/minimum-falling-path-sum/
>
> 首次记录：2026-10-12  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def minFallingPathSum(self, matrix: list[list[int]]) -> int:
        n = len(matrix)
        dp = [[0]*n for _ in range(n)]
        for i in range(n):
            dp[0][i] = matrix[0][i]
        for i in range(1,n):
            for j in range(n):
                if j==0:
                    dp[i][j] = min(dp[i-1][j],dp[i-1][j+1]) + matrix[i][j]
                elif j==n-1:
                    dp[i][j] = min(dp[i-1][j],dp[i-1][j-1]) + matrix[i][j]
                else:
                    dp[i][j] = min(min(dp[i-1][j-1],dp[i-1][j]),dp[i-1][j+1]) + matrix[i][j]
        return min(dp[-1])
```

## Go 代码

```go
func minFallingPathSum(matrix [][]int) int {
    n := len(matrix)
    dp := make([][]int,n)
    for i:=0;i<n;i++{
        dp[i] = make([]int,n)
    }
    for i :=0;i<n;i++{
        dp[0][i] = matrix[0][i]
    }
    for i:=1;i<n;i++{
        for j:=0;j<n;j++{
            if j==0{
                dp[i][j] = min(dp[i-1][j],dp[i-1][j+1]) + matrix[i][j]
            }else if j==n-1{
                dp[i][j] = min(dp[i-1][j-1],dp[i-1][j]) + matrix[i][j]
            }else{
                dp[i][j] = min(min(dp[i-1][j-1],dp[i-1][j]),dp[i-1][j+1]) + matrix[i][j]
            }
        }
    }
    minVal := dp[n-1][0]
    for i :=1;i<n;i++{
        if minVal > dp[n-1][i]{
            minVal = dp[n-1][i]
        }
    }
    return  minVal
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
| 2026-10-12 | 初学 | 来自 daily 笔记自动提取 |
