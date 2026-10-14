# -*- coding:utf-8 -*-
"""
统一日志模块

- 日志写入 logs/ 目录（已被 .gitignore 忽略），按大小滚动
- 只落文件、不打印到控制台，避免干扰菜单交互输出
- 供 OSS 上传、AI 调用、RAG 检索等模块记录运行轨迹，便于排查问题
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from config.settings import LOGS_PATH

_LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
_MAX_BYTES = 1 * 1024 * 1024  # 单文件 1MB
_BACKUP_COUNT = 3
_INITIALIZED = set()


def get_logger(name: str = "app") -> logging.Logger:
    """
    获取（或创建）一个只写文件的 logger。
    :param name: 日志子名称，最终 logger 名为 leetcode-notes-auto.<name>
    """
    full_name = f"leetcode-notes-auto.{name}"
    logger = logging.getLogger(full_name)

    if full_name in _INITIALIZED:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False  # 不向 root 传播，避免重复输出到控制台

    try:
        os.makedirs(LOGS_PATH, exist_ok=True)
        handler = RotatingFileHandler(
            os.path.join(LOGS_PATH, "run.log"),
            maxBytes=_MAX_BYTES,
            backupCount=_BACKUP_COUNT,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        logger.addHandler(handler)
    except OSError:
        # 日志目录不可写时降级为空 logger，绝不影响主流程
        logger.addHandler(logging.NullHandler())

    _INITIALIZED.add(full_name)
    return logger
