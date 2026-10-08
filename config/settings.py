# -*- coding:utf-8 -*-
"""
全局配置中心
- OSS 密钥读取优先级：环境变量 > config/secret.py / config/.env（可选本地文件，已被 .gitignore 忽略）> 占位符
- 禁止把真实 AccessKey 硬编码写入本文件并提交 GitHub
"""
import os
from pathlib import Path

# 项目根目录：一律由 Path(__file__) 推导，禁止硬编码绝对路径
BASE_DIR = str(Path(__file__).resolve().parent.parent)

# 笔记存放路径
NOTES_DAILY_PATH = os.path.join(BASE_DIR, "notes", "daily")
NOTES_PROBLEM_PATH = os.path.join(BASE_DIR, "notes", "problems")
ASSETS_PATH = os.path.join(BASE_DIR, "assets")

# 图片允许的扩展名
IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")

# 日期格式
DATE_FORMAT = "%Y-%m-%d"


def _load_local_secret():
    """尝试读取本地密钥文件 config/secret.py 或 config/.env（都不存在则跳过）"""
    secret = {}
    # 1) config/secret.py: 形如 OSS_ACCESS_KEY_ID = "xxx"
    secret_py = os.path.join(BASE_DIR, "config", "secret.py")
    if os.path.exists(secret_py):
        ns = {}
        try:
            with open(secret_py, "r", encoding="utf-8") as f:
                exec(compile(f.read(), secret_py, "exec"), ns)
            for k in ("OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET",
                      "OSS_ENDPOINT", "OSS_BUCKET_NAME", "OSS_URL_BASE"):
                if isinstance(ns.get(k), str) and ns[k]:
                    secret[k] = ns[k]
        except Exception as e:
            print(f"⚠️ 读取 config/secret.py 失败：{e}")
    # 2) config/.env: 形如 KEY=VALUE
    env_file = os.path.join(BASE_DIR, "config", ".env")
    if os.path.exists(env_file):
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip().strip('"').strip("'")
                    if k and v:
                        secret.setdefault(k, v)
        except Exception as e:
            print(f"⚠️ 读取 config/.env 失败：{e}")
    return secret


_local = _load_local_secret()


def _get(key, default=""):
    """环境变量优先，其次本地密钥文件，最后默认值"""
    return os.getenv(key) or _local.get(key) or default


# OSS 配置（endpoint / bucket 可在环境变量或 secret 文件中覆盖）
_endpoint = _get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
_bucket = _get("OSS_BUCKET_NAME")
# 对外访问域名：默认按 bucket+endpoint 推导，可在配置中覆盖（如自定义 CDN 域名）
_default_url_base = "https://{}.{}".format(_bucket or "your-bucket", _endpoint)

OSS_CONFIG = {
    "access_key_id": _get("OSS_ACCESS_KEY_ID"),
    "access_key_secret": _get("OSS_ACCESS_KEY_SECRET"),
    "endpoint": _endpoint,
    "bucket_name": _bucket,
    "prefix": _get("OSS_PREFIX", "img/"),
    "public_url_base": _get("OSS_URL_BASE", _default_url_base),
}


def validate_oss_config():
    """
    校验 OSS 配置是否可用，返回缺失项列表（空列表表示配置完整）
    提前捕获常见踩坑：密钥未填、bucket 为占位符
    """
    missing = []
    if not OSS_CONFIG["access_key_id"]:
        missing.append("access_key_id（环境变量 OSS_ACCESS_KEY_ID）")
    if not OSS_CONFIG["access_key_secret"]:
        missing.append("access_key_secret（环境变量 OSS_ACCESS_KEY_SECRET）")
    bucket = OSS_CONFIG["bucket_name"]
    if not bucket or bucket.startswith("your"):
        missing.append("bucket_name（环境变量 OSS_BUCKET_NAME）")
    return missing


def init_dir():
    """初始化所有目录，不存在则自动创建"""
    for d in (NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, ASSETS_PATH):
        if not os.path.exists(d):
            os.makedirs(d)


# 导入即自动创建笔记目录 / assets 目录
init_dir()
