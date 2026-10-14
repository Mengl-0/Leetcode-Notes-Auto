# LeetCode 42. 接雨水

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/trapping-rain-water/
>
> 首次记录：2026-10-06  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def trap(self,height:List[]) ->int:
        n = len(height)
        if n <=2 :
            return 0
        left,right= 0,n-1
        leftMax,rightMax= 0,0
        ans = 0
        while left < right:
            if height[left] < height[right]:
                if height[left] >= leftMax:
                    leftMax = height[left]
                else:
                    ans += leftMax - height[left]
                left +=1
            else:
                if height[right] >= rightMax:
                    rightMax = height[right]
                else:
                    ans += rightMax - height[right]
                right -=1
        return ans
```

## Go 代码

```go
func trap(height []int) int {
	n := len(height)
	if n == 0 {
		return 0
	}
	leftMax := make([]int, n)
	rightMax := make([]int, n)
	ans := 0
	leftMax[0] = height[0]
	for i := 1; i < n; i++ {
		leftMax[i] = max(leftMax[i-1], height[i])
	}
	rightMax[n-1] = height[n-1]
	for i := n - 2; i >= 0; i-- {
		rightMax[i] = max(rightMax[i+1], height[i])
	}
	for i := 0; i < n; i++ {
		ans += min(leftMax[i], rightMax[i]) - height[i]
	}
	return ans
}
func max(a, b int) int {
	if a > b {
		return a
	}
	return b
}
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
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
