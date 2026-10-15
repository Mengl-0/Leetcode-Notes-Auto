# LeetCode 283. 移动零

> 难度：简单｜ 标签：双指针｜ 链接：https://leetcode.cn/problems/move-zeroes/
>
> 首次记录：2026-10-05  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def moveZeroes(self,nums:[]int) -> None:
        left = 0
        for right in range nums:
            if nums[right] !=0{
                nums[left],nums[right] = nums[right],nums[left]
                left += 1
            }
```

## Go 代码

```go
func moveZeroes(nums []int){
    left := 0
    for right := 0;right < len(nums);i++{
        if nums[right] !=0{
            nums[left],nums[right] = nums[right],nums[left]
            left++
        }
    }
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
