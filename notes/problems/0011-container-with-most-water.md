# LeetCode 11. 盛最多水的容器

> 难度：中等 ｜ 标签：双指针｜ 链接：https://leetcode.cn/problems/container-with-most-water/
>
> 首次记录：2026-10-06  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def maxArea(self, heiht: list[int]) -> int:
        left = 0
        right = len(heiht) - 1
        max_w = 0
        while left < right:
            cur = min(height[left], height[right])
            cur_w = (right - left) * cur
            max_w = max(cur_w, max_w)
            if height[left] < height[right]:
                left += 1
            else:
                right -= 1
        return max_w
```

## Go 代码

```go
func maxArea(height []int) int{
    left := 0
    right := len(height) - 1
    max_w := 0
    for left < right{
        cur := min(height[left], height[right])
        cur_w := (right - left) * cur
        max_w = max(cur_w, max_w)
        if height[left] < height[right]{
            left ++
        }else{
            right --
        }
    }
    return max_w
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
| 2026-10-06 | 初学 | 来自 daily 笔记自动提取 |
