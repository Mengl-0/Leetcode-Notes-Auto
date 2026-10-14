# LeetCode 516. 最长回文子序列

> 难度：中等 ｜ 标签：字符串、动态规划 ｜ 链接：https://leetcode.cn/problems/longest-palindromic-subsequence/
>
> 首次记录：2026-10-14  ｜  复习次数：0

## 题目描述

给你一个字符串 `s`，找出其中最长的回文子序列，并返回该序列的长度。子序列不要求连续。

## 思路分析

**区间 DP**：`dp[i][j]` 表示子串 `s[i..j]` 的最长回文子序列长度。
- `s[i]==s[j]`：`dp[i][j] = dp[i+1][j-1] + 2`（两端字符都算上）
- `s[i]!=s[j]`：`dp[i][j] = max(dp[i+1][j], dp[i][j-1])`（舍弃一端）
- 初始化：`dp[i][i] = 1`（单个字符长度为 1）
- 遍历顺序：先枚举区间长度，再枚举左端点，右端点由左端点+长度推出

## Python 代码

```python
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        n = len(s)
        if n <= 1:
            return n
        dp = [[0]*n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for lenL in range(2, n+1):
            for i in range(n-lenL+1):
                j = i + lenL - 1
                if s[i] == s[j]:
                    if lenL == 2:
                        dp[i][j] = 2
                    else:
                        dp[i][j] = dp[i+1][j-1] + 2
                else:
                    dp[i][j] = max(dp[i+1][j], dp[i][j-1])
        return dp[0][n-1]
```

## Go 代码

```go
func longestPalindromeSubseq(s string) int {
    n := len(s)
    if n <= 1 {
        return n
    }
    dp := make([][]int, n)
    for i := range dp {
        dp[i] = make([]int, n)
    }
    for i := 0; i < n; i++ {
        dp[i][i] = 1
    }
    for lenL := 2; lenL <= n; lenL++ {
        for i := 0; i+lenL-1 < n; i++ {
            j := i + lenL - 1
            if s[i] == s[j] {
                if lenL == 2 {
                    dp[i][j] = 2
                } else {
                    dp[i][j] = dp[i+1][j-1] + 2
                }
            } else {
                if dp[i+1][j] > dp[i][j-1] {
                    dp[i][j] = dp[i+1][j]
                } else {
                    dp[i][j] = dp[i][j-1]
                }
            }
        }
    }
    return dp[0][n-1]
}
```

## 复杂度分析

- 时间复杂度：O(n²)，两层循环
- 空间复杂度：O(n²)，dp 矩阵；可优化到 O(n) 滚动数组

## ⚠️ 踩坑记录

- 子序列 vs 子串：子序列不连续，dp 存长度不是 bool
- 遍历顺序：外层枚举区间长度，内层枚举左端点
- `dp[i][i]=1` 初始化，不是 0

## 💡 收获与延伸

- 与最长回文子串（LeetCode 5）对比：子串 dp 存 bool，子序列 dp 存长度
- 空间优化：一维滚动数组

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-14 | 初学 | 来自 daily 笔记自动提取 |
