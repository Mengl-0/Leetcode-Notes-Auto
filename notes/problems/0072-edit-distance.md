# LeetCode 72. 编辑距离

> 难度：困难 ｜ 标签：字符串、动态规划 ｜ 链接：https://leetcode.cn/problems/edit-distance/
>
> 首次记录：2026-10-14  ｜  复习次数：0

## 题目描述

给你两个单词 `word1` 和 `word2`，请返回将 `word1` 转换成 `word2` 所使用的最少操作数。操作：插入、删除、替换一个字符。

## 思路分析

**双字符串 DP**：`dp[i][j]` 表示 `word1` 前 i 个字符转成 `word2` 前 j 个字符的最少操作数。
- `word1[i-1]==word2[j-1]`：不用操作，`dp[i][j] = dp[i-1][j-1]`
- 不等：取三种操作最小值 + 1
  - 替换：`dp[i-1][j-1]`
  - 删除 word1 字符：`dp[i-1][j]`
  - 插入字符到 word1：`dp[i][j-1]`
- 边界：`dp[i][0]=i`（全删），`dp[0][j]=j`（全插）

## Python 代码

```python
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        m, n = len(word1), len(word2)
        dp = [[0]*(n+1) for _ in range(m+1)]
        for i in range(m+1):
            dp[i][0] = i
        for j in range(n+1):
            dp[0][j] = j
        for i in range(1, m+1):
            for j in range(1, n+1):
                if word1[i-1] == word2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1]) + 1
        return dp[m][n]
```

## Go 代码

```go
func minDistance(word1 string, word2 string) int {
    m := len(word1)
    n := len(word2)
    dp := make([][]int, m+1)
    for i := range dp {
        dp[i] = make([]int, n+1)
    }
    for i := 0; i <= m; i++ {
        dp[i][0] = i
    }
    for j := 0; j <= n; j++ {
        dp[0][j] = j
    }
    for i := 1; i <= m; i++ {
        for j := 1; j <= n; j++ {
            if word1[i-1] == word2[j-1] {
                dp[i][j] = dp[i-1][j-1]
            } else {
                dp[i][j] = min(dp[i-1][j-1], min(dp[i-1][j], dp[i][j-1])) + 1
            }
        }
    }
    return dp[m][n]
}
```

## 复杂度分析

- 时间复杂度：O(mn)，两层循环
- 空间复杂度：O(mn)，dp 矩阵；可优化到 O(n) 滚动数组

## ⚠️ 踩坑记录

- dp 大小是 `(m+1) x (n+1)`，因为有空串边界
- `dp[i][0]=i`，`dp[0][j]=j`，初始化不要漏
- 三个操作取 min，不是 max

## 💡 收获与延伸

- 双字符串 DP 的经典题：LCS、编辑距离都用 `(m+1)x(n+1)` 矩阵
- 空间优化：一维滚动数组，需要临时变量保存左上角值

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-14 | 初学 | 来自 daily 笔记自动提取 |
