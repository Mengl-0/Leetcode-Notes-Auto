# -*- coding:utf-8 -*-
"""
RAG 私有知识库模块（三期）

流程：
  1. build_index()   扫描 notes/ 下全部 md，按标题层级切分为知识块，
                     向量化后持久化到 vector_store/index.json
  2. search()        对问题向量化，检索 top_k 个最相关的知识块
  3. answer()        把检索到的笔记片段作为上下文交给 DeepSeek，
                     生成「只基于自己笔记」的回答

设计约束：
  - 检索阶段完全离线（provider=hash 时），不产生任何网络请求
  - 回答阶段才调用 DeepSeek；未配置密钥时降级为只展示检索到的原文片段
  - 索引与笔记的变更通过内容指纹判断，笔记未改动时重建可跳过向量化
"""
import hashlib
import json
import os
import re
from collections.abc import Iterator

from config.settings import VECTOR_STORE_PATH, RAG_CONFIG, NOTES_DAILY_PATH, NOTES_PROBLEM_PATH
from core import embedding
from core.logger import get_logger

logger = get_logger("rag")

INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.json")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_CODE_FENCE_RE = re.compile(r"^```")

# 增量构建时的文件指纹表：{笔记相对路径: 内容 sha1}，随索引一起持久化


def iter_note_files() -> "Iterator[str]":
    """遍历全部笔记文件：题解在前、每日笔记在后，各自按名称排序（生成器）"""
    for root in (NOTES_PROBLEM_PATH, NOTES_DAILY_PATH):
        if not os.path.isdir(root):
            continue
        for f in sorted(os.listdir(root)):
            if f.endswith(".md"):
                yield os.path.join(root, f)


def _split_by_heading(text: str, source: str, max_chars: int) -> "list[dict]":
    """
    按 Markdown 标题层级切分，代码块内部不切分。
    超长块继续按空行/句子二次切分，保证检索粒度合适。
    """
    lines = text.splitlines()
    sections = []  # (heading, [lines])
    current_heading = os.path.splitext(os.path.basename(source))[0]
    current = []
    in_fence = False

    for line in lines:
        if _CODE_FENCE_RE.match(line.strip()):
            in_fence = not in_fence
        m = None if in_fence else _HEADING_RE.match(line)
        if m:
            if current:
                sections.append((current_heading, current))
            current_heading = m.group(2).strip() or current_heading
            current = []
        else:
            current.append(line)
    if current:
        sections.append((current_heading, current))

    chunks = []
    for heading, body in sections:
        content = "\n".join(body).strip()
        if not content:
            continue
        for part in _split_long(content, max_chars):
            chunks.append({
                "source": source,
                "heading": heading,
                "text": part,
            })
    return chunks


def _split_long(content: str, max_chars: int) -> "list[str]":
    """超长内容按段落聚合切分，单段仍超长时按句子切"""
    if len(content) <= max_chars:
        return [content]

    parts = []
    buf = ""
    for para in re.split(r"\n\s*\n", content):
        para = para.strip()
        if not para:
            continue
        if len(buf) + len(para) + 2 <= max_chars:
            buf = f"{buf}\n\n{para}" if buf else para
            continue
        if buf:
            parts.append(buf)
            buf = ""
        if len(para) <= max_chars:
            buf = para
        else:
            parts.extend(_split_sentences(para, max_chars))
    if buf:
        parts.append(buf)
    return parts or [content[:max_chars]]


def _split_sentences(text: str, max_chars: int) -> "list[str]":
    """按中英文句末标点切分并聚合"""
    sents = re.split(r"(?<=[。！？；.!?;])\s*", text)
    parts, buf = [], ""
    for s in sents:
        if not s.strip():
            continue
        if len(buf) + len(s) <= max_chars:
            buf += s
        else:
            if buf:
                parts.append(buf)
            # 单句仍超长时硬切
            while len(s) > max_chars:
                parts.append(s[:max_chars])
                s = s[max_chars:]
            buf = s
    if buf:
        parts.append(buf)
    return parts


def load_index() -> "dict | None":
    """读取已持久化的索引；不存在或损坏返回 None"""
    if not os.path.exists(INDEX_FILE):
        return None
    try:
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "chunks" not in data:
            return None
        return data
    except (OSError, json.JSONDecodeError) as e:
        print(f"⚠️ 索引文件损坏，将重新构建：{e}")
        logger.warning("索引读取失败：%s", e)
        return None


def _file_fingerprint(text: str) -> str:
    """单篇笔记内容指纹，用于增量判断"""
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def _project_root() -> str:
    """项目根目录（vector_store 的上一级）"""
    return os.path.dirname(VECTOR_STORE_PATH)


def _collect_notes(max_chars: int) -> "dict[str, tuple[str, list]]":
    """
    读取全部笔记并按文件分组切块
    :return: {相对路径: (文件内容指纹, [chunk, ...])}，顺序与遍历顺序一致；
        chunk 中的 source 字段统一替换为相对路径
    """
    per_file: "dict[str, tuple[str, list]]" = {}
    for path in iter_note_files():
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except OSError as e:
            print(f"⚠️ 读取笔记失败，已跳过 {path}：{e}")
            continue
        rel = os.path.relpath(path, _project_root()).replace(os.sep, "/")
        chunks = [{**c, "source": rel} for c in _split_by_heading(text, path, max_chars)]
        per_file[rel] = (_file_fingerprint(text), chunks)
    return per_file


def _old_vectors_by_file(old) -> "dict[str, list]":
    """旧索引按文件分组：{相对路径: [(chunk, vector), ...]}"""
    grouped: "dict[str, list]" = {}
    for vec, chunk in zip(old.get("vectors", []), old.get("chunks", [])):
        grouped.setdefault(chunk.get("source", ""), []).append((chunk, vec))
    return grouped


def build_index(force: bool = False) -> "list[dict] | None":
    """
    构建/更新向量索引（审计问题 6：文件粒度的增量重建）
    - 全部笔记未变更：直接沿用现有索引，零向量化开销
    - 部分变更（语义模型 / API 模式）：只向量化变更文件的 chunk，未变更文件
      复用旧向量——这两类 provider 的单条向量互不耦合，可安全复用
    - hash 模式：向量与全局 IDF 权重耦合，语料一旦变化必须整体重建
      （IDF 变化即旧向量失效，这是 TF-IDF 的固有约束，与报告说明一致）
    :param force: True 表示忽略指纹强制全量重建
    :return: 知识块列表（成功，可能为空）；None 表示构建失败
        （审计问题 10：统一「失败返回 None / 成功返回非 None」约定）
    """
    problems = embedding.missing_hint() if not embedding.is_available() else ""
    if problems:
        print(f"❌ 向量化不可用：{problems}")
        print("💡 可把 EMBEDDING_PROVIDER 改为 hash（零依赖离线模式），详见 config/config.example.env")
        return None

    max_chars = RAG_CONFIG["chunk_max_chars"]
    per_file = _collect_notes(max_chars)

    all_chunks = [c for _, chunks in per_file.values() for c in chunks]
    if not all_chunks:
        print("ℹ️ 没有找到任何笔记内容，索引为空")
        return []

    fp_all = hashlib.sha1(
        "|".join(f"{rel}:{fp}" for rel, (fp, _) in sorted(per_file.items())).encode("utf-8")
    ).hexdigest()
    schema = embedding.SCHEMA_VERSION
    provider = embedding.get_provider()
    old = None if force else load_index()

    old_ok = bool(
        old
        and old.get("schema") == schema
        and old.get("provider") == provider
        and len(old.get("vectors", [])) == len(old.get("chunks", []))
    )

    # 1) 指纹一致且算法版本未变：整份索引直接复用
    if old_ok and old.get("fingerprint") == fp_all:
        print(f"ℹ️ 笔记未变更，沿用现有索引（{len(all_chunks)} 个知识块）")
        return old["chunks"]

    # 2) 计算可文件级复用的集合（hash 模式 IDF 全局耦合，不做局部复用）
    reuse_map: "dict[str, list]" = {}
    if old_ok and provider != "hash" and isinstance(old.get("file_fps"), dict):
        grouped = _old_vectors_by_file(old)
        for rel, (fp, chunks) in per_file.items():
            pairs = grouped.get(rel)
            if (
                pairs
                and old["file_fps"].get(rel) == fp
                and len(pairs) == len(chunks)
                and all(p[0].get("text") == c["text"] for p, c in zip(pairs, chunks))
            ):
                reuse_map[rel] = pairs

    # 3) 收集需要新向量化的 chunk（按 all_chunks 顺序）
    todo: "list[dict]" = []
    for rel, (_, chunks) in per_file.items():
        if rel not in reuse_map:
            todo.extend(chunks)

    if reuse_map:
        print(f"🧮 增量更新：复用 {sum(len(v) for v in reuse_map.values())} 个知识块向量，"
              f"仅向量化 {len(todo)} 个变更块（provider={provider}）...")
    else:
        print(f"🧮 正在向量化 {len(all_chunks)} 个知识块（provider={provider}）...")

    try:
        new_vecs = embedding.embed_texts([c["text"] for c in todo]) if todo else []
    except Exception as e:
        print(f"❌ 向量化失败：{e}")
        logger.error("向量化失败：%s", e, exc_info=True)
        return None

    # 4) 组装：按文件顺序，复用文件取旧向量，其余消费新向量迭代器
    rel_chunks: "list[dict]" = []
    vectors: "list[list[float]]" = []
    new_it = iter(new_vecs)
    for rel, (_, chunks) in per_file.items():
        if rel in reuse_map:
            for c, (_, vec) in zip(chunks, reuse_map[rel]):
                rel_chunks.append(c)
                vectors.append(vec)
        else:
            for c in chunks:
                rel_chunks.append(c)
                vectors.append(next(new_it))

    os.makedirs(VECTOR_STORE_PATH, exist_ok=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "schema": schema,
                "fingerprint": fp_all,
                "provider": provider,
                "dim": len(vectors[0]) if vectors else 0,
                "file_fps": {rel: fp for rel, (fp, _) in per_file.items()},
                "chunks": rel_chunks,
                "vectors": vectors,
            },
            f,
            ensure_ascii=False,
        )
    print(f"✅ 索引构建完成：{len(rel_chunks)} 个知识块 -> {INDEX_FILE}")
    logger.info("索引构建完成，%d 个知识块", len(rel_chunks))
    return rel_chunks


def search(question: str, top_k: int = 0) -> "list[tuple[float, dict]]":
    """
    检索与问题最相关的知识块
    :return: [(score, chunk), ...] 按分数降序；索引缺失或不可用时返回空列表
    """
    if not embedding.is_available():
        print(f"❌ 向量化不可用：{embedding.missing_hint()}")
        return []

    index = load_index()
    if not index:
        print("ℹ️ 尚未构建索引，正在自动构建 ...")
        build_index()
        index = load_index()

    # provider 或向量算法版本变更后向量空间不兼容，必须重建
    if index and (
        index.get("provider") != embedding.get_provider()
        or index.get("schema") != embedding.SCHEMA_VERSION
    ):
        print("⚠️ 索引与当前向量化配置不兼容（provider 或算法已变更），正在重建 ...")
        build_index(force=True)
        index = load_index()

    if not index:
        return []

    try:
        qvec = embedding.embed_query(question)
    except Exception as e:
        print(f"❌ 问题向量化失败：{e}")
        logger.error("查询向量化失败：%s", e, exc_info=True)
        return []

    k = top_k or RAG_CONFIG["top_k"]
    min_score = RAG_CONFIG["min_score"]
    scored = []
    for vec, chunk in zip(index["vectors"], index["chunks"]):
        s = embedding.cosine(qvec, vec)
        if s >= min_score:
            scored.append((s, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    logger.info("检索『%s』命中 %d 条", question[:30], len(scored))
    return scored[:k]


def build_context(hits: "list[tuple[float, dict]]") -> str:
    """把检索结果拼成带来源标注的上下文文本"""
    blocks = []
    for i, (score, chunk) in enumerate(hits, 1):
        blocks.append(
            f"【片段 {i}】来源：{chunk['source']} · 章节：{chunk['heading']} · 相关度：{score:.3f}\n{chunk['text']}"
        )
    return "\n\n".join(blocks)


def answer(question: str, top_k: int = 0) -> "tuple[str, list[tuple[float, dict]]]":
    """
    基于自己的笔记回答问题（RAG）
    - 先检索相关知识块
    - 已配置 DeepSeek 时生成整合回答；未配置时降级为直接展示原文片段
    :return: (回答文本, 检索命中列表)
    """
    hits = search(question, top_k)
    if not hits:
        msg = "🔍 没有从你的笔记中检索到相关内容。可以换个问法，或先补充相关笔记。"
        print(msg)
        return msg, hits

    context = build_context(hits)

    # 未配置 DeepSeek：降级为只展示检索片段，不做生成
    try:
        from core import ai_helper
    except ImportError:
        ai_helper = None

    if ai_helper is None or not ai_helper.is_configured():
        msg = (
            "🔍 已从你的笔记中检索到以下相关片段（未配置 DeepSeek，故直接展示原文）：\n\n"
            + context
        )
        print(msg)
        return msg, hits

    system = (
        "你是私人算法刷题知识库助手。你只能依据【我的笔记】内容回答，"
        "严禁编造笔记中不存在的结论。笔记未覆盖的部分，明确说明"
        "「我的笔记里没有这部分内容」，并可给出通用性建议但要标注这是笔记之外的补充。"
        "回答使用中文，结构清晰，引用片段时注明来源文件。"
    )
    user = f"【我的笔记】\n{context}\n\n【我的问题】\n{question}"
    result = ai_helper.chat(system, user)
    if not result:
        result = "⚠️ AI 回答生成失败，以下是检索到的原始笔记片段：\n\n" + context
    print("\n----- 📚 基于你笔记的回答 -----\n")
    print(result)
    print("\n----- 🔗 引用片段 -----\n")
    for i, (score, chunk) in enumerate(hits, 1):
        print(f"{i}. {chunk['source']} · {chunk['heading']}（相关度 {score:.3f}）")
    return result, hits
