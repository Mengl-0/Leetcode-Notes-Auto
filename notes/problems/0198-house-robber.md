# LeetCode 198. 打家劫舍

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/house-robber/
>
> 首次记录：2026-10-10  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def rob(self,nums:List[int]) -> int:
        n = len(nums)
        if n == 0:
            return 0
        if n == 1:
            return nums[0]
        dp = [0]*n
        dp[0] = nums[0]
        dp[1] = max(nums[0],nums[1])
        for i in range(2,n):
            dp[i] = max(dp[i-1],dp[i-2] + nums[i])
        return dp[-1]
```

## Go 代码

```go
func rob(nums []int) int{
    n := len(nums)
    if n == 0{
        return 0
    }
    if n ==1{
        return nums[0]
    }
    dp := make([]int,n)
    dp[0] = nums[0]
    dp[1] = max(nums[0],nums[1])
    for i:= 2;i<n;i++{
        dp[i] = max(dp[i-1],dp[i-2]+nums[i])
    }
    return dp[n-1]
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
| 2026-10-10 | 初学 | 来自 daily 笔记自动提取 |
