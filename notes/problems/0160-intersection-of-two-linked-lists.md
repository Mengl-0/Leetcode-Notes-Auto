# LeetCode 160. 相交链表

> 难度：  ｜ 标签：  ｜ 链接：https://leetcode.cn/problems/intersection-of-two-linked-lists/
>
> 首次记录：2026-10-05  ｜  复习次数：0

## 题目描述

（待补充）

## 思路分析

（待补充）

## Python 代码

```python
class ListNode:
    def __init__(self,x):
        self.val = x
        self.next = None
class Solution:
    def getIntersectionNode(self,headA:ListNode,headB:ListNode) -> Optional[ListNode]:
        pa ,pb =headA,headB
        while pa != pb:
            pa = pa.next if pa else headB
            pb = pb.next if pb else headA
        return pa
```

## Go 代码

```go
type ListNode struct{
    Val int
    Next *ListNode
}
func getIntersectionNode(headA,headB *ListNode) *ListNode{
    pA,PB := headA,headB
    for pA != pB{
        if pA == nil{
            pA = headB
        }else {
            pA = PA.Next
        }
        if pB == nil{
            pB = headA
        }else {
            pB =PB.Next
        }
    }
    return pA
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
| 2026-10-05 | 初学 | 来自 daily 笔记自动提取 |
