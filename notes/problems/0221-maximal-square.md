# LeetCode 221. 最大正方形

> 难度：中等 ｜ 标签：动态规划、矩阵 ｜ 链接：https://leetcode.cn/problems/maximal-square/
>
> 首次记录：2026-10-13  ｜  复习次数：0

## 题目描述

在由 `'0'` 和 `'1'` 组成的二维矩阵内，找到只包含 `'1'` 的最大正方形，并返回其面积。

## 思路分析

`dp[i][j]` 表示以 `(i,j)` 为右下角的最大正方形边长。
- 第一行/第一列：值为 `'1'` 时 dp=1
- 其他位置：若 `matrix[i][j]=='1'`，则 `dp[i][j] = min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]) + 1`
- 三个方向最小值决定当前能拓展多大正方形

## Python 代码

```python
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        m = len(matrix)
        if m == 0:
            return 0
        n = len(matrix[0])
        dp = [[0]*n for _ in range(m)]
        maxside = 0
        for i in range(m):
            for j in range(n):
                if matrix[i][j] == '1':
                    if i == 0 or j == 0:
                        dp[i][j] = 1
                    else:
                        dp[i][j] = min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]) + 1
                    maxside = max(maxside, dp[i][j])
        return maxside * maxside
```

## Go 代码

```go
func maximalSquare(matrix [][]byte) int {
    m := len(matrix)
    if m == 0 {
        return 0
    }
    n := len(matrix[0])
    dp := make([][]int, m)
    for i := range dp {
        dp[i] = make([]int, n)
    }
    maxside := 0
    for i := 0; i < m; i++ {
        for j := 0; j < n; j++ {
            if matrix[i][j] == '1' {
                if i == 0 || j == 0 {
                    dp[i][j] = 1
                } else {
                    dp[i][j] = min(dp[i-1][j-1], min(dp[i-1][j], dp[i][j-1])) + 1
                }
                maxside = max(maxside, dp[i][j])
            }
        }
    }
    return maxside * maxside
}
```

## 复杂度分析

- 时间复杂度：O(mn)，遍历矩阵一次
- 空间复杂度：O(mn)，dp 矩阵；可优化到 O(n) 滚动数组

## ⚠️ 踩坑记录

- dp 存的是边长，不是面积；最后要平方
- 三个方向取 min，不是 max

## 💡 收获与延伸

- 网格 DP 的典型题：当前位置依赖上方、左方、左上方三个位置
- 空间优化：一维滚动数组

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-13 | 初学 | 来自 daily 笔记自动提取 |
