# LeetCode 1. 两数之和

> 难度：简单 ｜ 标签：数组、哈希表 ｜ 链接：https://leetcode.cn/problems/two-sum/
>
> 首次记录：2026-10-08  ｜  复习次数：1

## 题目描述

给定一个整数数组 `nums` 和一个整数目标值 `target`，请你在该数组中找出**和为目标值** `target` 的那两个整数，并返回它们的数组下标。假设每种输入只会对应一个答案，且同一个元素不能使用两遍。

## 思路分析

核心是「用空间换时间」。暴力枚举两层循环是 O(n²)；改用哈希表记录「已遍历过的值 -> 下标」，遍历到 `x` 时直接查 `target - x` 是否已存在，把查找降到 O(1)，整体 O(n)。

关键点：一边遍历一边存，能保证不会用到同一个元素两次（查的是之前存进去的）。

## Python 代码

```python
def twoSum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        need = target - x
        if need in seen:
            return [seen[need], i]
        seen[x] = i
    return []
```

## Go 代码

```go
func twoSum(nums []int, target int) []int {
    seen := make(map[int]int)
    for i, x := range nums {
        if j, ok := seen[target-x]; ok {
            return []int{j, i}
        }
        seen[x] = i
    }
    return nil
}
```

## 复杂度分析

- 时间复杂度：O(n)，只遍历数组一次，哈希查找 O(1)
- 空间复杂度：O(n)，最坏情况哈希表存下 n 个元素

## ⚠️ 踩坑记录

- 返回的是「下标」不是「值」，别写错。
- 必须先查后存，否则遇到 `target = 2*x` 且数组里只有一个 `x` 时会误用自己。

## 💡 收获与延伸

- 这是「哈希表空间换时间」的最典型例题，很多求配对/差值问题都能套这个模式。
- 延伸：若数组有序，可改用双指针 O(1) 空间；若要求所有组合，需处理重复元素去重。

## 📌 复盘记录

| 日期 | 掌握程度 | 备注 |
| ---- | -------- | ---- |
| 2026-10-08 | 熟练 | 哈希表一次遍历，独立完成 |
