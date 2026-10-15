# LeetCode 128. 最长连续序列

> 难度：中等｜ 标签：哈希｜ 链接：https://leetcode.cn/problems/longest-consecutive-sequence/
>
> 首次记录：2026-10-05  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def longestConsecutive(self,nums:[]int)->int:
        set = sort(nums)
        maxLen = 0
        for num in set:
            if num - 1 not in set:
                cur = num
                cur_len = 1
                while num+1 in set:
                    cur += 1
                    cur_len += 1
                maxLen = max(maxLen,cur_len)
        return maxLen
```

## Go 代码

```go
func longestConsecutive(nums []int) int{
    set = make(map[int]bool)
    if _,v := range nums{
        set[v] = true
    }
    maxLen := 0
    for num := range set{
        if !set[num-1]{
            curNum := num
            curLen := 1
            for set[curNum+1]{
                curNum ++
                curLen ++
            }
            if curLen > maxLen{
                maxLen = curLen
            }
        }
    }
    return maxLen
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
| 2026-10-05 | 初学 | 来自 daily 笔记自动提取 |
