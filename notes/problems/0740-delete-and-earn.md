# LeetCode 740. 删除并获得点数

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/delete-and-earn/
>
> 首次记录：2026-10-10  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def deleteAndEarn(self,nums:List[int]) -> int:
        maxVal =0
        count = [0]*10001
        for v in nums:
            count[v] += v
            if v > maxVal:
                maxVal = v
        prev1,prev2 = 0,0
        for i in range(maxVal+1):
            cur = max(prev1,prev2+count[i])
            prev2= prev1
            prev1= cur
        return prev1
```

## Go 代码

```go
func deleteAndEarn(nums []int) int{
    maxVal := 0
    count := make([]int,10001)
    for _,v := range nums{
        count[v] += v
        if maxVal < v{
            maxVal = v
        }
    }
    prev1,prev2 := 0,0
    for i:=0;i<=maxVal;i++{
        cur := max(prev1, prev2 + count[i])
        prev2 = prev1
        prev1 = cur
    }
    return prev1
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
