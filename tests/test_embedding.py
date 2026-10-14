# -*- coding:utf-8 -*-
"""
core.embedding 单元测试（hash provider，零依赖离线）
重点覆盖：分词、归一化、余弦相似度、确定性
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestTokenize:
    def test_english_words(self):
        from core.embedding import _tokenize
        tokens = _tokenize("Two Sum")
        assert "two" in tokens
        assert "sum" in tokens

    def test_chinese_bigram(self):
        from core.embedding import _tokenize
        tokens = _tokenize("两数之和")
        # 中文双字
        assert "两数" in tokens
        assert "数之" in tokens
        assert "之和" in tokens

    def test_code_identifier(self):
        from core.embedding import _tokenize
        tokens = _tokenize("two_sum")
        assert "two_sum" in tokens or "two" in tokens


class TestHashEmbed:
    def test_deterministic(self):
        """同一文本两次向量化结果一致"""
        from core.embedding import _hash_embed_one
        v1 = _hash_embed_one("hello world", 256)
        v2 = _hash_embed_one("hello world", 256)
        assert v1 == v2

    def test_normalized(self):
        """向量 L2 归一化后模长约等于 1"""
        from core.embedding import _hash_embed_one
        v = _hash_embed_one("test text", 256)
        norm = sum(x * x for x in v) ** 0.5
        assert abs(norm - 1.0) < 1e-6

    def test_dim_matches(self):
        from core.embedding import _hash_embed_one
        v = _hash_embed_one("hello", 128)
        assert len(v) == 128


class TestCosine:
    def test_identical_vectors(self):
        from core.embedding import cosine
        v = [1.0, 0.0, 0.0]
        assert abs(cosine(v, v) - 1.0) < 1e-6

    def test_orthogonal(self):
        from core.embedding import cosine
        assert cosine([1.0, 0.0], [0.0, 1.0]) == 0.0

    def test_dim_mismatch_truncates(self):
        """维度不一致时按最短长度截断"""
        from core.embedding import cosine
        s = cosine([1.0, 2.0, 3.0], [1.0, 2.0])
        # 只用前两位计算
        expected = (1 + 4) / ((1 + 4) ** 0.5 * (1 + 4) ** 0.5)
        assert abs(s - expected) < 1e-6
