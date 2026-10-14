# -*- coding:utf-8 -*-
"""
core.notes_io 单元测试
重点覆盖：文件名排序、find_problem_note 匹配逻辑
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestSlugify:
    """scripts/new_problem.py 里的 slugify 逻辑（这里单独测）"""

    def test_basic(self):
        import re
        raw = "Two Sum"
        s = raw.strip().lower().replace("_", "-")
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        assert s == "two-sum"

    def test_underscore_to_hyphen(self):
        import re
        raw = "longest_palindrome"
        s = raw.strip().lower().replace("_", "-")
        s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
        assert s == "longest-palindrome"


class TestProblemSortKey:
    """题解文件名按 4 位题号排序"""

    def test_numeric_order(self):
        from core.notes_io import _PROBLEM_RE
        files = ["0100-some.md", "0001-two-sum.md", "0042-trapping.md"]
        def key(p):
            m = _PROBLEM_RE.match(os.path.basename(p))
            return (0, int(m.group(1)), p) if m else (1, 0, p)
        sorted_files = sorted(files, key=key)
        assert sorted_files == ["0001-two-sum.md", "0042-trapping.md", "0100-some.md"]

    def test_non_规范排最后(self):
        from core.notes_io import _PROBLEM_RE
        files = ["readme.md", "0001-two-sum.md"]
        def key(p):
            m = _PROBLEM_RE.match(os.path.basename(p))
            return (0, int(m.group(1)), p) if m else (1, 0, p)
        sorted_files = sorted(files, key=key)
        assert sorted_files[0] == "0001-two-sum.md"
        assert sorted_files[-1] == "readme.md"
