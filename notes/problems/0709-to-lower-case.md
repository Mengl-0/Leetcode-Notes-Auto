# LeetCode 709. 转化成小写字母

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/to-lower-case/
>
> 首次记录：2026-10-01  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class Soution:
    def toLowerCase(self, s: str) -> str:
        b = list(s)
        for i in range(len(b)):
            if 'A' <= b[i] <= 'Z':
                b[i] = chr(ord(b[i]) + 32)
        return ''.join(b)
```

## Go 代码

```go
func toLoewrCase(s string) string{
    b := []byte(s)
    for i := range(b){
        if b[i] >= 'A' && b[i] <= 'Z'{
            b[i] += 32
        }
    }
    return string(b)
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
| 2026-10-01 | 初学 | 来自 daily 笔记自动提取 |
