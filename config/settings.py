# -*- coding:utf-8 -*-
"""
全局配置中心（唯一配置入口）

所有第三方服务配置统一集中在本文件：
  1) 阿里云 OSS 图床      -> OSS_CONFIG
  2) DeepSeek 大模型      -> DEEPSEEK_CONFIG
  3) 向量化 / RAG 知识库  -> EMBEDDING_CONFIG / RAG_CONFIG

密钥读取优先级：环境变量 > config/secret.env > config/.env（均已被 .gitignore 忽略）
禁止把真实 AccessKey / API Key 硬编码写入本文件并提交 GitHub。
新增配置项时，请同步更新模板 config/config.example.env。
"""
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Windows 终端编码兜底
# ---------------------------------------------------------------------------
# Windows 下 Python 的标准输出/错误默认按本地代码页（GBK/cp936）编码、错误处理为
# strict：一旦 print 到 emoji（如 ✅/🧮/📖）等代码页无法编码的字符，就会抛
# UnicodeEncodeError 使程序崩溃。这里保留系统原有编码（保证中文在 GBK 终端正常显示，
# UTF-8 终端也不受影响），仅把错误处理改为 replace（无法编码的字符降级为 '?'），
# 从而既不崩溃也不乱码。所有脚本都会导入本模块，因此只需在此处与 main.py（打印菜单
# 早于导入本模块）各兜底一次即可。
for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(errors="replace")
        except Exception:
            pass

# ---------------------------------------------------------------------------
# 路径：一律由 Path(__file__) 推导，禁止硬编码绝对路径
# ---------------------------------------------------------------------------
BASE_DIR = str(Path(__file__).resolve().parent.parent)

NOTES_DAILY_PATH = os.path.join(BASE_DIR, "notes", "daily")
NOTES_PROBLEM_PATH = os.path.join(BASE_DIR, "notes", "problems")
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
LOGS_PATH = os.path.join(BASE_DIR, "logs")
# RAG 向量索引存放目录（自动生成，不入库）
VECTOR_STORE_PATH = os.path.join(BASE_DIR, "vector_store")

IMAGE_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp")
DATE_FORMAT = "%Y-%m-%d"

# 需要从密钥文件 / 环境变量读取的配置项全集（用于统一加载与体检）
_SECRET_KEYS = (
    "OSS_ACCESS_KEY_ID", "OSS_ACCESS_KEY_SECRET", "OSS_ENDPOINT",
    "OSS_BUCKET_NAME", "OSS_URL_BASE", "OSS_PREFIX",
    "DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL", "DEEPSEEK_MODEL",
    "DEEPSEEK_TEMPERATURE", "DEEPSEEK_MAX_TOKENS", "DEEPSEEK_TIMEOUT",
    "EMBEDDING_PROVIDER", "EMBEDDING_MODEL", "EMBEDDING_API_BASE",
    "EMBEDDING_API_KEY", "EMBEDDING_DIM",
)


def _parse_env_text(text: str) -> dict:
    """解析 KEY=VALUE 文本，忽略空行与 # 注释，去掉首尾引号"""
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v:
            out[k] = v
    return out


def _load_local_secret() -> dict:
    """
    读取本地密钥文件（config/secret.env 优先，其次 config/.env）。
    只解析 KEY=VALUE 纯文本，不执行任何代码。
    """
    secret = {}
    for name in ("secret.env", ".env"):
        path = os.path.join(BASE_DIR, "config", name)
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = _parse_env_text(f.read())
        except OSError as e:
            print(f"⚠️ 读取 config/{name} 失败：{e}")
            continue
        for k, v in data.items():
            secret.setdefault(k, v)

    # 旧版 config/secret.py 依赖 exec() 执行任意代码，已停止支持（安全风险）。
    legacy = os.path.join(BASE_DIR, "config", "secret.py")
    if os.path.exists(legacy):
        print("⚠️ 检测到旧版 config/secret.py，出于安全已不再执行该文件；")
        print("   请把其中的配置迁移到 config/secret.env（格式 KEY=VALUE），参考 config/config.example.env")
    return secret


_LOCAL = _load_local_secret()


def _get(key: str, default: str = "") -> str:
    """环境变量优先，其次本地密钥文件，最后默认值"""
    return os.getenv(key) or _LOCAL.get(key) or default


def _get_float(key: str, default: float) -> float:
    raw = _get(key)
    try:
        return float(raw) if raw else default
    except ValueError:
        print(f"⚠️ 配置 {key}={raw!r} 不是合法数字，已回退为 {default}")
        return default


def _get_int(key: str, default: int) -> int:
    raw = _get(key)
    try:
        return int(float(raw)) if raw else default
    except ValueError:
        print(f"⚠️ 配置 {key}={raw!r} 不是合法整数，已回退为 {default}")
        return default


def is_placeholder(value: str) -> bool:
    """判断配置值是否仍是模板占位符（未填写真实值）"""
    v = (value or "").strip().lower()
    return (not v) or v.startswith("your") or v.startswith("sk-xxxxxxxx") or "请替换" in v


# ---------------------------------------------------------------------------
# 1) 阿里云 OSS 图床配置
# ---------------------------------------------------------------------------
OSS_ENDPOINT = _get("OSS_ENDPOINT", "oss-cn-hangzhou.aliyuncs.com")
OSS_BUCKET_NAME = _get("OSS_BUCKET_NAME", "your-bucket-name")
# prefix 只影响上传路径，允许留空；默认放在 img/ 下
OSS_PREFIX = _get("OSS_PREFIX", "img/")

OSS_CONFIG = {
    "access_key_id": _get("OSS_ACCESS_KEY_ID", "your-oss-access-key-id"),
    "access_key_secret": _get("OSS_ACCESS_KEY_SECRET", "your-oss-access-key-secret"),
    "endpoint": OSS_ENDPOINT,
    "bucket_name": OSS_BUCKET_NAME,
    "prefix": OSS_PREFIX,
}


def get_oss_public_url_base() -> str:
    """
    对外访问域名。延迟求值，确保始终跟随当前 bucket / endpoint 配置；
    可用 OSS_URL_BASE 覆盖（如自定义 CDN 域名）。
    """
    custom = _get("OSS_URL_BASE")
    if custom and not is_placeholder(custom):
        return custom.rstrip("/")
    return f"https://{OSS_BUCKET_NAME}.{OSS_ENDPOINT}".rstrip("/")


def validate_oss_config():
    """校验 OSS 配置是否可用，返回缺失/占位项列表（空列表表示配置完整）"""
    missing = []
    if is_placeholder(OSS_CONFIG["access_key_id"]):
        missing.append("access_key_id（OSS_ACCESS_KEY_ID）")
    if is_placeholder(OSS_CONFIG["access_key_secret"]):
        missing.append("access_key_secret（OSS_ACCESS_KEY_SECRET）")
    if is_placeholder(OSS_CONFIG["bucket_name"]):
        missing.append("bucket_name（OSS_BUCKET_NAME）")
    return missing


# ---------------------------------------------------------------------------
# 2) DeepSeek 大模型配置（OpenAI 兼容接口）
# ---------------------------------------------------------------------------
# 官方 base_url 为 https://api.deepseek.com，接口为 /chat/completions
# 模型名：deepseek-flash（默认，性价比高）/ deepseek-v4-pro（能力更强、更贵）
DEEPSEEK_CONFIG = {
    "api_key": _get("DEEPSEEK_API_KEY", "sk-xxxxxxxxxxxxxxxxxxxxxxxx"),
    "base_url": _get("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "model": _get("DEEPSEEK_MODEL", "deepseek-flash"),
    "temperature": _get_float("DEEPSEEK_TEMPERATURE", 0.3),
    "max_tokens": _get_int("DEEPSEEK_MAX_TOKENS", 2048),
    "timeout": _get_int("DEEPSEEK_TIMEOUT", 120),
}


def validate_deepseek_config():
    """校验 DeepSeek 配置，返回缺失/占位项列表"""
    missing = []
    if is_placeholder(DEEPSEEK_CONFIG["api_key"]):
        missing.append("api_key（DEEPSEEK_API_KEY）")
    if is_placeholder(DEEPSEEK_CONFIG["base_url"]):
        missing.append("base_url（DEEPSEEK_BASE_URL）")
    if is_placeholder(DEEPSEEK_CONFIG["model"]):
        missing.append("model（DEEPSEEK_MODEL）")
    return missing


# ---------------------------------------------------------------------------
# 3) 向量化 / RAG 配置
# ---------------------------------------------------------------------------
# provider 可选值：
#   hash                  零依赖本地哈希向量（默认，无需安装任何包，离线可用）
#   sentence_transformers 本地语义模型（需 pip install sentence-transformers，推荐 BAAI/bge-m3）
#   openai_compatible     第三方 OpenAI 兼容 embedding 接口（如阿里云百炼、硅基流动）
#                         注意：DeepSeek 官方不提供 embedding 接口，需另配服务商
EMBEDDING_CONFIG = {
    "provider": _get("EMBEDDING_PROVIDER", "hash").strip().lower(),
    "model": _get("EMBEDDING_MODEL", "BAAI/bge-m3"),
    "api_base": _get("EMBEDDING_API_BASE", ""),
    "api_key": _get("EMBEDDING_API_KEY", ""),
    "dim": _get_int("EMBEDDING_DIM", 512),
}

RAG_CONFIG = {
    # 单个知识块最大字符数，超出按标题层级继续切分
    "chunk_max_chars": _get_int("RAG_CHUNK_MAX_CHARS", 1200),
    # 检索返回的知识块数量
    "top_k": _get_int("RAG_TOP_K", 4),
    # 低于该相似度分数的片段不参与回答，避免答非所问
    "min_score": _get_float("RAG_MIN_SCORE", 0.02),
}

EMBEDDING_PROVIDERS = ("hash", "sentence_transformers", "openai_compatible")


def validate_embedding_config():
    """校验向量化配置，返回问题列表（空列表表示可用）"""
    problems = []
    provider = EMBEDDING_CONFIG["provider"]
    if provider not in EMBEDDING_PROVIDERS:
        problems.append(
            f"provider={provider!r} 不支持，可选：{' / '.join(EMBEDDING_PROVIDERS)}"
        )
    if provider == "openai_compatible":
        if is_placeholder(EMBEDDING_CONFIG["api_base"]):
            problems.append("api_base（EMBEDDING_API_BASE）")
        if is_placeholder(EMBEDDING_CONFIG["api_key"]):
            problems.append("api_key（EMBEDDING_API_KEY）")
    if provider == "hash" and not (64 <= EMBEDDING_CONFIG["dim"] <= 4096):
        problems.append(f"dim={EMBEDDING_CONFIG['dim']} 建议在 64~4096 之间")
    return problems


# ---------------------------------------------------------------------------
# 初始化与体检
# ---------------------------------------------------------------------------
def init_dir():
    """初始化所有运行时目录，不存在则自动创建"""
    for d in (NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, ASSETS_PATH, LOGS_PATH, VECTOR_STORE_PATH):
        os.makedirs(d, exist_ok=True)


def check_config(verbose: bool = True):
    """
    全量配置体检，返回 {模块: 问题列表}。
    用于快速确认「哪些功能已配置可用、哪些还差什么」。
    """
    report = {
        "oss": validate_oss_config(),
        "deepseek": validate_deepseek_config(),
        "embedding": validate_embedding_config(),
    }
    if verbose:
        titles = {
            "oss": "阿里云 OSS 图床",
            "deepseek": "DeepSeek 大模型",
            "embedding": f"向量化（provider={EMBEDDING_CONFIG['provider']}）",
        }
        print("=" * 50)
        print("🔎 配置体检结果")
        print("=" * 50)
        for key, issues in report.items():
            if issues:
                print(f"⚠️ {titles[key]}：待补充")
                for i in issues:
                    print(f"     - {i}")
            else:
                print(f"✅ {titles[key]}：配置完整")
        print("-" * 50)
        print("💡 填写方式：复制 config/config.example.env 为 config/secret.env 后补全，")
        print("   或设置同名环境变量（环境变量优先级更高）。")
        print("=" * 50)
    return report


init_dir()


if __name__ == "__main__":
    check_config()
