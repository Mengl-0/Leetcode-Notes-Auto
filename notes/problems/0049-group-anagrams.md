# LeetCode 49. 字母异位词分组

> 难度：中等｜ 标签：哈希｜ 链接：https://leetcode.cn/problems/group-anagrams/
>
> 首次记录：2026-10-04  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
from collections import defaultdict
class Solution:
    def groupAnagrams(self,strs:list[str]) -> list[list[str]]:
        m = defaultdict(list)
        for s in strs:
            cnt = [0]*26
            for c in s:
                cnt[ord(c) - ord('a')] += 1
            m[tuple(cnt)].append(s)
        return list(m.values())
```

## Go 代码

```go
func groupAnagrams(strs :string) [][]string{
    m := make(map[[26]int][]string)
    for _,s := range strs{
        var cnt [26]int
        for _,c := range s{
            cnt[c-'a']++
        }
        m[cnt] = append(m[cnt],s)
    }
    res := make([][]string,0,len(m))
    for _,v := range m{
        res = append(res, v)
    }
    return res
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
| 2026-10-04 | 初学 | 来自 daily 笔记自动提取 |
