# LeetCode 867. 转置矩阵

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/transpose-matrix/
>
> 首次记录：2026-10-02  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def isPowerOfThree(self, n: int) -> bool:
        while n and n%3 == 0:
            n /= 3
        return n == 1
```

## Go 代码

```go
func transpose(matrix [][]int) [][]int{
    rows, cols := len(matrix), len(matrix[0])
    res := make([][]int, cols)
    for i := range(cols){
        res[i] := make([]int, rows)
    }
    for i := range(rows){
        for j := range(cols){
            res[j][i] = matrix [i][j]
        }
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
