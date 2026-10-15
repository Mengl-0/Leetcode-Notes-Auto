# LeetCode 438. 找到字符串中所有字母异位词

> 难度：中等｜ 标签：滑动窗口｜ 链接：https://leetcode.cn/problems/find-all-anagrams-in-a-string/
>
> 首次记录：2026-10-07  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def findAnagrams(self, s: str, p: str) -> List[int]:
        n,m := len(s), len(p)
        if n < m:
            return []
        result []
        sCont [0]*26
        pCont [0]*26
        for i in range(m):
            sCont[ord(s[i]) - ord('a')] += 1
            pCont[ord(p[i]) - ord('a')] -= 1
        if sCont == pCont:
            result.append(0)
        for i in range(m,n):
            sCont[ord(s[i]) - ord('a')] += 1
            sCont[ord(s[i-m]) - ord('a')] -= 1
            if sCont == pCont:
                result.append(i-m+1)
        return result
```

## Go 代码

```go
func findAnagrams(s string, p string) []int{
    n,m := len(s), len(p)
    if n < m{
        return []int{}
    }
    var result []int
    var sCont,pCont [26]int
    for i := range(m){
        pCont[p[i] - 'a']++
        sCont[s[i] - 'a']++
    }
    if sCont == pCont{
        result = append(result, 0)
    }
    for i := m;i < n;i++{
        sCont[p[i] - 'a']++
        sCont[p[i-m] - 'a']--
        if sCont == pCont{
            result = append(result, i-m+1)
        }
    }
    return result
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
