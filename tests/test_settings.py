# -*- coding:utf-8 -*-
"""
config.settings 单元测试
重点覆盖：配置读取优先级、空值处理、占位符判断
"""
import os
import sys
from pathlib import Path

import pytest

# 确保项目根目录在 sys.path 中
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class TestPlaceholder:
    """is_placeholder 占位符判断"""

    def test_empty_string_is_placeholder(self):
        from config.settings import is_placeholder
        assert is_placeholder("") is True

    def test_your_prefix_is_placeholder(self):
        from config.settings import is_placeholder
        assert is_placeholder("your-bucket-name") is True
        assert is_placeholder("YOUR-BUCKET") is True

    def test_real_value_is_not_placeholder(self):
        from config.settings import is_placeholder
        assert is_placeholder("my-bucket-123") is False
        assert is_placeholder("https://example.com") is False


class TestParseEnv:
    """_parse_env_text 解析 KEY=VALUE"""

    def test_basic_kv(self):
        from config.settings import _parse_env_text
        text = "A=1\nB=hello\n"
        assert _parse_env_text(text) == {"A": "1", "B": "hello"}

    def test_ignore_comments_and_empty(self):
        from config.settings import _parse_env_text
        text = "# comment\n\nA=1\n   \nB=2"
        assert _parse_env_text(text) == {"A": "1", "B": "2"}

    def test_strip_quotes(self):
        from config.settings import _parse_env_text
        text = 'A="hello"\nB=\'world\''
        assert _parse_env_text(text) == {"A": "hello", "B": "world"}

    def test_empty_value_kept(self):
        """审计问题 3：显式留空的 KEY= 应返回空串，而不是被丢弃"""
        from config.settings import _parse_env_text
        text = "A=\nB=1"
        result = _parse_env_text(text)
        assert result["A"] == ""
        assert result["B"] == "1"


class TestGetConfig:
    """_get 配置读取优先级（环境变量 > 本地密钥 > 默认值）"""

    def test_env_overrides_local(self, monkeypatch):
        from config import settings
        monkeypatch.setenv("TEST_KEY_XYZ", "from_env")
        monkeypatch.setattr(settings, "_LOCAL", {"TEST_KEY_XYZ": "from_local"})
        assert settings._get("TEST_KEY_XYZ", "default") == "from_env"

    def test_local_used_when_no_env(self, monkeypatch):
        from config import settings
        monkeypatch.delenv("TEST_KEY_XYZ", raising=False)
        monkeypatch.setattr(settings, "_LOCAL", {"TEST_KEY_XYZ": "from_local"})
        assert settings._get("TEST_KEY_XYZ", "default") == "from_local"

    def test_empty_local_overrides_default(self, monkeypatch):
        """审计问题 3：本地显式空值应返回空串，而不是回退默认值"""
        from config import settings
        monkeypatch.delenv("TEST_KEY_XYZ", raising=False)
        monkeypatch.setattr(settings, "_LOCAL", {"TEST_KEY_XYZ": ""})
        assert settings._get("TEST_KEY_XYZ", "default") == ""
