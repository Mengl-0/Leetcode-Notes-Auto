# LeetCode 1422. 分割字符串的最大得分

> 难度：简单｜ 标签：数组&字符串｜ 链接：https://leetcode.cn/problems/maximum-score-after-splitting-a-string/
>
> 首次记录：2026-10-03  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def maxScore(self,s: str) -> int:
        total1 = s.count('1')
        left0 = 0
        max_val = 0
        n = len(s)
        for i in range(n-1):
            c = s[i]
            if c == '0'{
                left0 += 1
            }
            left1 = i+1 -left0
            right1 = total1 - left1
            score = left0 + right1
            max_val = max(max_val, score)
        return max_val
```

## Go 代码

```go
func maxScore(s string) int{
    n := len(s)
    if n < 2{
        return 0
    }
    score := 0
    if score == '0'{
        score = 1
    }else {
        score = -1
    }
    diff := 0
    maxDiff :=  -1<<31
    pre1 := 0
    for i :=0;i< n-1;i++{
        if s[i] == '0'{
            diff++
        }else{
            diff--
            pre1++
        }
        if diff > maxDiff{
            maxDiff = diff
        }
    }
    total := pre1
    if s[n-1] == '1'{
        total++
    }
    return maxDiff + total
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
