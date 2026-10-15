# LeetCode 3. 无重复字符的最长子串

> 难度：中等｜ 标签：滑动窗口｜ 链接：https://leetcode.cn/problems/longest-substring-without-repeating-characters/
>
> 首次记录：2026-10-07  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def lengthOfLongestSubstring(self, s:str) -> int:
        char_set = []
        left = 0
        max_len = 0
        for right in range(len(s)):
            while s[right] in char_set:
                char_set.remove(s[left])
                left += 1
            char_ser.remove(s[right])
            char_len  = right - left +1
            max_len = max(max_len, char_len)
        return max_len
```

## Go 代码

```go
func lengthOfLongestSubstring(s string) int{
    left, maxlen := 0, 0
    charIndexMap := make([byte]int)
    n := []byte(s)
    for right := range(len(n)){
        char := n[right]
        if idx,ok := charIndexMap[char];ok && idx >= left{
            left ++
        }
        charIndexMap[char] = right
        charlen := right -left +1
        maxlen = max(maxlen,charlen)
    }
    return maxlen
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
| 2026-10-07 | 初学 | 来自 daily 笔记自动提取 |
