# LeetCode 1470. 重新排列数组

> 难度：简单｜ 标签：数组&矩阵｜ 链接：https://leetcode.cn/problems/shuffle-the-array/
>
> 首次记录：2026-10-02  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def shuffle(self, nums: List[int], n: int) -> List[int]:
        res = []
        for i in range n:
            res.append(nums[i])
            res.append(nums[1+n]) 
        return res
```

## Go 代码

```go
func shuffle(nums []int, n int) []int {
    res = make([]int, 0, 2*n)
    for i := range(n){
        res = append(res, nums[i])
        res = append(res, nums[i+n])
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
| 2026-10-02 | 初学 | 来自 daily 笔记自动提取 |
