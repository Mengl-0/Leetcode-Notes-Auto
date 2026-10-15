# LeetCode 136. 只出现一次的数字

> 难度：简单｜ 标签：位运算，栈｜ 链接：https://leetcode.cn/problems/single-number/
>
> 首次记录：2026-10-07  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def singleNumber(self,nums:List[int]) -> int:
        res = 0
        for num in nums:
            res ^= num
        return res
```

## Go 代码

```go
func singleNumber(nums []int) int{
    res := 0
    for i := range(nums){
        res ^= nums[i]
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
| 2026-10-07 | 初学 | 来自 daily 笔记自动提取 |
