# LeetCode 5. 最长回文子串

> 难度：中等 ｜ 标签：字符串、动态规划、中心扩展 ｜ 链接：https://leetcode.cn/problems/longest-palindromic-substring/
>
> 首次记录：2026-10-13  ｜  复习次数：0

## 题目描述

给你一个字符串 `s`，找到 `s` 中最长的回文子串。

## 思路分析

**DP 解法**：`dp[i][j]` 表示子串 `s[i..j]` 是否为回文。
- `s[i]==s[j]` 且 `j-i<=2`：直接是回文（长度 1/2/3）
- `s[i]==s[j]` 且 `j-i>2`：看内层 `dp[i+1][j-1]` 是否为回文
- 遍历顺序：先枚举子串长度，再枚举左端点，保证小区间先算

**中心扩展法**：空间 O(1)，以每个字符为中心向两边扩展。

## Python 代码

```python
class Solution:
    def longestPalindrome(self, s: str) -> str:
        n = len(s)
        if n <= 1:
            return s
        dp = [[False]*n for _ in range(n)]
        for i in range(n):
            dp[i][i] = True
        maxlen = 1
        start = 0
        for j in range(n):
            for i in range(j):
                if s[i] == s[j]:
                    if j - i <= 2:
                        dp[i][j] = True
                    else:
                        dp[i][j] = dp[i+1][j-1]
                if dp[i][j]:
                    curlen = j - i + 1
                    if curlen > maxlen:
                        maxlen = curlen
                        start = i
        return s[start:start+maxlen]
```

## Go 代码

```go
func longestPalindrome(s string) string {
    n := len(s)
    if n <= 1 {
        return s
    }
    dp := make([][]bool, n)
    for i := range dp {
        dp[i] = make([]bool, n)
    }
    for i := 0; i < n; i++ {
        dp[i][i] = true
    }
    maxlen := 1
    start := 0
    for j := 0; j < n; j++ {
        for i := 0; i < j; i++ {
            if s[i] == s[j] {
                if j-i <= 2 {
                    dp[i][j] = true
                } else {
                    dp[i][j] = dp[i+1][j-1]
                }
            }
            if dp[i][j] {
                curlen := j - i + 1
                if curlen > maxlen {
                    maxlen = curlen
                    start = i
                }
            }
        }
    }
    return s[start : start+maxlen]
}
```

## 复杂度分析

- 时间复杂度：O(n²)，两层循环
- 空间复杂度：O(n²)，dp 矩阵；中心扩展法可降到 O(1)

## ⚠️ 踩坑记录

- 遍历顺序：先枚举右端点 j，再枚举左端点 i，保证 `dp[i+1][j-1]` 已计算
- `maxlen` 和 `start` 要初始化，默认值 1 和 0
- `return s[...]` 不是 `return start[...]`

## 💡 收获与延伸

- 区间 DP：大区间依赖内层小区间，必须由短到长枚举
- 中心扩展法面试更常用，空间 O(1)

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-13 | 初学 | 来自 daily 笔记自动提取 |
