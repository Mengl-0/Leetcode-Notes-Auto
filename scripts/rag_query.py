# -*- coding:utf-8 -*-
"""
RAG 私有知识库脚本（三期）
子菜单：
  1. 构建 / 更新知识库索引
  2. 基于笔记问答
  3. 纯检索（查看命中片段，不调用 AI）

用法：python scripts/rag_query.py  （交互选择）
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import rag, embedding
from config.settings import RAG_CONFIG, init_dir


def _divider(title: str = "") -> None:
    print("\n" + "=" * 50)
    if title:
        print(title)
        print("=" * 50)


def build_flow() -> None:
    """菜单 1：构建 / 更新索引"""
    _divider("🗂️ 构建 / 更新知识库索引")
    rag.build_index()


def query_flow() -> None:
    """菜单 2：基于笔记问答"""
    _divider("💬 基于我的笔记问答")
    if not embedding.is_available():
        print(f"❌ 向量化不可用：{embedding.missing_hint()}")
        return
    q = input("请输入问题（如：两数之和用了什么思路？）：").strip()
    if not q:
        return
    rag.answer(q)


def search_flow() -> None:
    """菜单 3：纯检索，只看命中片段"""
    _divider("🔍 纯检索（展示命中片段）")
    if not embedding.is_available():
        print(f"❌ 向量化不可用：{embedding.missing_hint()}")
        return
    q = input("请输入检索关键词：").strip()
    if not q:
        return
    hits = rag.search(q)
    if not hits:
        print("ℹ️ 没有检索到相关内容")
        return
    print(rag.build_context(hits))


def main() -> None:
    print(f"ℹ️ 当前向量化模式：{embedding.get_provider()}；检索 top_k={RAG_CONFIG['top_k']}")
    while True:
        _divider("📚 RAG 私有知识库（三期）")
        print("1. 构建 / 更新知识库索引")
        print("2. 基于笔记问答（RAG）")
        print("3. 纯检索（只看命中片段）")
        print("0. 返回")
        opt = input("请选择：").strip()
        if opt == "0":
            break
        elif opt == "1":
            build_flow()
        elif opt == "2":
            query_flow()
        elif opt == "3":
            search_flow()
        else:
            print("❌ 无效选择")


def run() -> None:
    """供 main.py 进程内调用的入口（审计问题 4）"""
    init_dir()
    main()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print("\n⏹️ 已取消")
