# LeetCode 852. 山脉数组的峰顶索引

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/peak-index-in-a-mountain-array/
>
> 首次记录：2026-10-03  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def peakIndexInMountainArray(self, arr:List[int]) -> int:
        left = 0
        right = len(arr) -1
        while left < right:
            mid = (left+right) / 2
            if arr[mid] < arr[mid+1]:
                left += 1
            else:
                right = mid
        return left
```

## Go 代码

```go
func peakIndexInMountainArray(arr []int) int{
    left := 0
    right := len(arr) - 1
    for left < right{
        mid = (left + right) / 2
        if arr[mid] < arr[mid + 1]{
            left ++
        }else{
            right = mid
        }
    }
    return left
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
| 2026-10-03 | 初学 | 来自 daily 笔记自动提取 |
