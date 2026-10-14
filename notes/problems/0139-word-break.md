# LeetCode 139. 单词拆分

> 难度：中等 ｜ 标签：动态规划、哈希表、字符串 ｜ 链接：https://leetcode.cn/problems/word-break/
>
> 首次记录：2026-10-13  ｜  复习次数：0

## 题目描述

给定字符串 `s` 和字典 `wordDict`，判断 `s` 是否可以拆分成字典中若干单词的拼接。

## 思路分析

**一维前缀 DP**：`dp[i]` 表示 `s[0:i]` 前 i 个字符能否被拆分。
- `dp[0] = True`，空串可拆分
- 枚举分割点 `j`：若 `dp[j]==True` 且 `s[j:i]` 在字典中，则 `dp[i]=True`

## Python 代码

```python
class Solution:
    def wordBreak(self, s: str, wordDict: List[str]) -> bool:
        word_set = set(wordDict)
        n = len(s)
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(1, n + 1):
            for j in range(i):
                if dp[j] and s[j:i] in word_set:
                    dp[i] = True
                    break
        return dp[n]
```

## Go 代码

```go
func wordBreak(s string, wordDict []string) bool {
    wordMap := make(map[string]bool)
    for _, v := range wordDict {
        wordMap[v] = true
    }
    n := len(s)
    dp := make([]bool, n+1)
    dp[0] = true
    for i := 1; i <= n; i++ {
        for j := 0; j < i; j++ {
            if dp[j] && wordMap[s[j:i]] {
                dp[i] = true
                break
            }
        }
    }
    return dp[n]
}
```

## 复杂度分析

- 时间复杂度：O(n²)，两层循环
- 空间复杂度：O(n)，dp 数组 + 哈希集合

## ⚠️ 踩坑记录

- `dp[0]=True` 是关键基准，空串可拆分
- 单词列表转集合，查找 O(1)

## 💡 收获与延伸

- 一维前缀 DP：只看从开头到 i 的前缀，不需要二维矩阵
- 与 LCS、回文子串等二维字符串 DP 区分开

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-13 | 初学 | 来自 daily 笔记自动提取 |
