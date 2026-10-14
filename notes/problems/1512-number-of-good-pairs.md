# LeetCode 1512. 好数对的数目

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/number-of-good-pairs/
>
> 首次记录：2026-09-30  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python

```

## Go 代码

```go
func numIdenticalPairs(nums []int) int {
    countMap := make(map[int]int)
    for _, num := range nums{
        countMap[num]++
    }
    res := 0
    for _, v := range countMap{
        res += v * (v-1) / 2
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
| 2026-09-30 | 初学 | 来自 daily 笔记自动提取 |
