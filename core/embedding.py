# -*- coding:utf-8 -*-
"""
向量化模块（三期 RAG 基础设施）

支持三种 provider，由 EMBEDDING_PROVIDER 配置决定：
  1. hash                  零依赖本地特征哈希向量（默认）
                           基于字符 n-gram + 英文单词 + 中文双字的确定性哈希，
                           完全离线、无需安装任何包，适合数百篇笔记规模
  2. sentence_transformers 本地语义模型（需 pip install sentence-transformers）
                           检索质量最好，首次使用需联网下载模型
  3. openai_compatible     第三方 OpenAI 兼容 embedding 接口
                           （阿里云百炼 / 硅基流动等，标准库 urllib 调用，无需装包）

统一约定：所有 provider 返回的向量均已归一化，可直接用点积作为余弦相似度。
"""
import hashlib
import json
import math
import os
import re
import urllib.error
import urllib.request

from config.settings import (
    EMBEDDING_CONFIG,
    EMBEDDING_PROVIDERS,
    VECTOR_STORE_PATH,
    validate_embedding_config,
)
from core.logger import get_logger

logger = get_logger("embedding")

# 向量算法版本：hash 模式的实现一旦调整（如引入 IDF），必须让旧索引失效重建，
# 否则「建索引用的向量空间」与「查询用的向量空间」不一致，检索结果会失真。
SCHEMA_VERSION = "hash-tfidf-v1"

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")

_ST_MODEL = None  # sentence-transformers 模型缓存（进程内只加载一次）
_IDF_STATE = None  # hash 模式的 IDF 权重缓存（进程内只加载一次）


def get_provider() -> str:
    return EMBEDDING_CONFIG["provider"]


def is_available() -> bool:
    """当前 provider 是否可用（配置合法且依赖就绪）"""
    problems = validate_embedding_config()
    if problems:
        return False
    if get_provider() == "sentence_transformers":
        try:
            import sentence_transformers  # noqa: F401
            return True
        except ImportError:
            return False
    return True


def missing_hint() -> str:
    """返回当前 provider 不可用的原因说明"""
    problems = validate_embedding_config()
    if problems:
        return "配置问题：" + "；".join(problems)
    if get_provider() == "sentence_transformers":
        return "未安装依赖：pip install sentence-transformers"
    return ""


def _normalize(vec):
    """L2 归一化，使点积等价于余弦相似度"""
    norm = sum(x * x for x in vec) ** 0.5
    if norm == 0:
        return [0.0] * len(vec)
    return [x / norm for x in vec]


def _tokenize(text: str):
    """
    轻量分词：英文单词 + 中文单字 + 中文双字 + 字符 3-gram
    多粒度组合，兼顾代码标识符与中文语义的检索效果
    """
    text = text.lower()
    tokens = []
    tokens.extend(_WORD_RE.findall(text))
    cjk = "".join(_CJK_RE.findall(text))
    tokens.extend(list(cjk))
    tokens.extend(cjk[i:i + 2] for i in range(len(cjk) - 1))
    compact = re.sub(r"\s+", "", text)
    tokens.extend(compact[i:i + 3] for i in range(max(0, len(compact) - 2)))
    return tokens


def _idf_path() -> str:
    return os.path.join(VECTOR_STORE_PATH, "idf.json")


def _load_idf():
    """加载已持久化的 IDF 权重；无缓存返回 (None, 0)"""
    global _IDF_STATE
    if _IDF_STATE is not None:
        return _IDF_STATE
    path = _idf_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("schema") == SCHEMA_VERSION:
                _IDF_STATE = (data.get("df", {}), int(data.get("n", 0)))
                return _IDF_STATE
        except (OSError, json.JSONDecodeError) as e:
            logger.warning("IDF 缓存读取失败，将忽略：%s", e)
    _IDF_STATE = (None, 0)
    return _IDF_STATE


def _save_idf(df: dict, n: int):
    """持久化 IDF 权重，供后续查询复用同一套权重"""
    global _IDF_STATE
    try:
        os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
        with open(_idf_path(), "w", encoding="utf-8") as f:
            json.dump({"schema": SCHEMA_VERSION, "df": df, "n": n}, f, ensure_ascii=False)
    except OSError as e:
        logger.warning("IDF 缓存写入失败：%s", e)
    _IDF_STATE = (df, n)


def _idf_weight(token: str, df: dict, n: int) -> float:
    """
    IDF 权重：出现文档数越多的词权重越低。
    df/n 为文档频率，取 log 平滑；未在语料出现过的词（如查询新词）给中性权重。
    """
    if not df or n <= 0:
        return 1.0
    cnt = df.get(token, 0)
    if cnt == 0:
        # 语料未见过的查询词：给中等权重，避免完全压掉有效信号
        return math.log(1.0 + n / 1.0) * 0.5
    return math.log(1.0 + n / cnt)


def _hash_embed_one(text: str, dim: int, df: dict = None, n: int = 0):
    """
    特征哈希 + TF-IDF 向量化单条文本（确定性、可复现）。
    df/n 提供时对每个 token 施加 IDF 权重，抑制高频虚词、突出区分性词汇。
    """
    vec = [0.0] * dim
    for tok in _tokenize(text):
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "little") % dim
        # 用后 4 字节决定符号，降低哈希冲突导致的系统性偏差
        sign = 1.0 if int.from_bytes(h[4:], "little") % 2 == 0 else -1.0
        weight = _idf_weight(tok, df, n) if df else 1.0
        vec[idx] += sign * weight
    return _normalize(vec)


def _hash_embed_corpus(texts, dim: int):
    """
    语料模式：先统计各 token 的文档频率（DF），持久化 IDF，再加权向量化。
    建索引时调用，保证与后续查询处于同一套 IDF 权重下。
    """
    token_sets = [set(_tokenize(t)) for t in texts]
    df = {}
    for ts in token_sets:
        for tok in ts:
            df[tok] = df.get(tok, 0) + 1
    n = len(texts)
    _save_idf(df, n)
    logger.info("已计算 IDF：%d 个特征，语料 %d 篇", len(df), n)
    return [_hash_embed_one(t, dim, df, n) for t in texts]


def _hash_embed_query(text: str, dim: int):
    """
    查询模式：复用建索引时持久化的 IDF 权重。
    若尚无 IDF（用户未建索引就直接查），退化为无权重哈希，仍能工作。
    """
    df, n = _load_idf()
    return _hash_embed_one(text, dim, df, n)


def _st_embed(texts):
    global _ST_MODEL
    from sentence_transformers import SentenceTransformer

    if _ST_MODEL is None:
        model_name = EMBEDDING_CONFIG["model"]
        logger.info("加载本地向量模型：%s", model_name)
        _ST_MODEL = SentenceTransformer(model_name)
    vecs = _ST_MODEL.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    return [list(map(float, v)) for v in vecs]


def _api_embed(texts):
    """调用 OpenAI 兼容 embedding 接口"""
    base = EMBEDDING_CONFIG["api_base"].rstrip("/")
    url = base + "/embeddings"
    payload = {"model": EMBEDDING_CONFIG["model"], "input": texts}
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {EMBEDDING_CONFIG['api_key']}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        items = sorted(body["data"], key=lambda d: d.get("index", 0))
        return [_normalize(d["embedding"]) for d in items]
    except urllib.error.HTTPError as e:
        detail = ""
        try:
            detail = e.read().decode("utf-8", errors="replace")[:300]
        except Exception:
            pass
        raise RuntimeError(f"embedding 接口 HTTP {e.code}：{detail or e.reason}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"无法连接 embedding 服务：{e.reason}") from e


def embed_texts(texts):
    """
    批量向量化（语料模式），返回与 texts 等长的向量列表；失败抛出 RuntimeError。
    hash provider 下会重新统计并持久化 IDF 权重——仅在构建索引时调用。
    """
    if not texts:
        return []
    provider = get_provider()
    if provider not in EMBEDDING_PROVIDERS:
        raise RuntimeError(f"不支持的 embedding provider：{provider}")

    if provider == "hash":
        dim = EMBEDDING_CONFIG["dim"]
        return _hash_embed_corpus(texts, dim)
    if provider == "sentence_transformers":
        try:
            return _st_embed(texts)
        except Exception as e:
            raise RuntimeError(f"本地模型向量化失败：{e}") from e
    # openai_compatible
    return _api_embed(texts)


def embed_query(text: str):
    """
    查询文本向量化，返回单条向量。
    hash provider 下复用建索引时持久化的 IDF 权重，保证与索引同一向量空间。
    """
    provider = get_provider()
    if provider == "hash":
        dim = EMBEDDING_CONFIG["dim"]
        return _hash_embed_query(text, dim)
    # 语义模型 / API 模式：查询与语料走同一编码逻辑
    return embed_texts([text])[0]


def vector_dim() -> int:
    """当前 provider 实际输出的向量维度（hash 由配置决定，其余在首次调用后确定）"""
    if get_provider() == "hash":
        return EMBEDDING_CONFIG["dim"]
    try:
        return len(embed_query("dim probe"))
    except Exception:
        return 0


def cosine(a, b) -> float:
    """
    余弦相似度。向量已归一化时用点积；维度不一致时按最短长度截断计算。
    """
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(a[i] * b[i] for i in range(n))
