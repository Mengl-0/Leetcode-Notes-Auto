# LeetCode 1534. 统计好三元数组

> 难度：简单｜ 标签：循环｜ 链接：https://leetcode.cn/problems/number-of-good-triplets/
>
> 首次记录：2026-09-30  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
s = start >> 1
loe_bit = start & 1
res = range_xor(s, s+n-1) << 1
if low_bit and n%2 == 1:
    res |= 1
return res
```

## Go 代码

```go
func ads(x int) int{
    if x < 0{
        return  -x
    }else{
        return x
    }
}
func countGoodTriplets(arr []int, a int, b int, c int) int{
    n := len(arr)
    count := 0
    for j := 1; j < n-1;j++{
        var left []int
        for i := 0; i < j;i++{
            if abs(arr[i] - arr[j]) <= a{
                left = append(left, i)
            }
        }
        var right []int
        for k := j+1; k < n;k++{
            if abs(arr[j] - arr[k]) <= b{
                right = append(right, k)
            }
        }
        for _,i := range left{
            for _, k:= range right{
                if abs(arr[i] - arr[k]) <= c{
                    count ++
                }
            }
        }
    }
    return count
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
| 2026-09-30 | 初学 | 来自 daily 笔记自动提取 |
