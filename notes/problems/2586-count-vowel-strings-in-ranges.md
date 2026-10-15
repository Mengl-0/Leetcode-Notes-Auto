# LeetCode 2586. 统计范围内的元音字符串数

> 难度：简单｜ 标签：数组&字符串｜ 链接：https://leetcode.cn/problems/count-vowel-strings-in-ranges/
>
> 首次记录：2026-10-03  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Solution:
    def vowelString(stlf, words: List[str],left:int,right:int) -> int:
        isVowel = {'a','e','i','o','u'}
        count = 0
        for i in range(left, right+1):
            s = words[i]
            first = s[0]
            last = s[-1]
            if first in isVowel and last in isVowel:
                count +=1
        return count
```

## Go 代码

```go
func vowelStrings(words []string,left int,right int) int{
    isVowel :=  func(c byte) bool{
        return c=='a'||c=='e'||c=='i'||c=='o'||c=='u'
    }
    count := 0
    for i:= left;i <= right;i++{
        c := word[i]
        first := c[0]
        last := c[len(c)-1]
        if isVowel(first) && isVowel(last){
            count++
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
| 2026-10-03 | 初学 | 来自 daily 笔记自动提取 |
