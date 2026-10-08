# -*- coding:utf-8 -*-
"""
阿里云 OSS 图片上传核心模块
- upload_file: 上传单张图片并返回线上链接
- replace_img_in_md: 扫描 md 文档，把本地图片引用替换为 OSS 线上链接
依赖：oss2（pip install oss2）。未安装或缺少密钥时给出友好提示并安全降级。
"""
import os
import re
import hashlib
import mimetypes

from config.settings import OSS_CONFIG, ASSETS_PATH, validate_oss_config

# md 图片语法：![alt](路径 "可选title")，只处理本地相对/绝对路径，不处理 http(s) 链接
MD_IMG_PATTERN = re.compile(r'(!\[[^\]]*\]\()\s*<?([^)\s]+?)>?(?:\s+[^)]*)?(\))')


def _oss_enabled():
    """检查 oss2 SDK 是否可用；不可用则提示安装方式"""
    try:
        import oss2  # noqa: F401
        return True
    except ImportError:
        print("❌ 未安装 oss2 SDK，请先执行：pip install oss2")
        return False


def _get_bucket():
    """创建 OSS Bucket 连接对象，配置缺失时返回 None"""
    missing = validate_oss_config()
    if missing:
        print("❌ OSS 配置不完整，缺少：")
        for m in missing:
            print(f"   - {m}")
        print("💡 请配置环境变量（推荐），或在 config/secret.py / config/.env 中填写，详见 README")
        return None
    if not _oss_enabled():
        return None
    import oss2
    auth = oss2.Auth(OSS_CONFIG["access_key_id"], OSS_CONFIG["access_key_secret"])
    return oss2.Bucket(auth, "https://" + OSS_CONFIG["endpoint"], OSS_CONFIG["bucket_name"])


def upload_file(local_path: str):
    """
    上传单张图片到 OSS，返回线上访问链接；失败返回 None
    远端 key 规则：<prefix>/<文件内容sha1前8位>_<原文件名>，同图去重、避免覆盖
    """
    if not os.path.exists(local_path):
        print(f"❌ 本地图片不存在：{local_path}")
        return None
    bucket = _get_bucket()
    if bucket is None:
        return None
    try:
        with open(local_path, "rb") as f:
            digest = hashlib.sha1(f.read()).hexdigest()[:8]
        fname = os.path.basename(local_path)
        key = f"{OSS_CONFIG['prefix']}{digest}_{fname}"
        # 显式指定 Content-Type，规避常见的图片类型识别问题
        ctype = mimetypes.guess_type(fname)[0] or "application/octet-stream"
        bucket.put_object_from_file(key, local_path, headers={"Content-Type": ctype})
        url = f"{OSS_CONFIG['public_url_base'].rstrip('/')}/{key}"
        return url
    except Exception as e:
        print(f"❌ 上传失败 {fname}：{e}")
        return None


def _resolve_local_path(md_path: str, img_src: str):
    """把 md 中的图片引用解析为本地绝对路径；解析不出（已是线上链接等）返回 None"""
    if img_src.startswith(("http://", "https://", "data:")):
        return None
    cleaned = img_src.replace("\\", "/")
    candidates = [
        os.path.abspath(cleaned),
        os.path.join(os.path.dirname(os.path.abspath(md_path)), cleaned),
        os.path.join(ASSETS_PATH, os.path.basename(cleaned)),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def replace_img_in_md(md_path: str):
    """
    扫描单个 md 文件，把 ![xxx](本地路径) 的图片上传 OSS 并替换为线上链接
    返回替换次数
    """
    if not os.path.exists(md_path):
        print(f"❌ md 文件不存在：{md_path}")
        return 0
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    url_cache = {}
    replaced = [0]

    def _sub(m):
        src = m.group(2)
        local = _resolve_local_path(md_path, src)
        if not local:
            return m.group(0)
        if local not in url_cache:
            url_cache[local] = upload_file(local)
        url = url_cache[local]
        if not url:
            print(f"⚠️ 图片 {os.path.basename(local)} 上传失败，保留原链接")
            return m.group(0)
        replaced[0] += 1
        return f"{m.group(1)}{url}{m.group(3)}"

    new_text = MD_IMG_PATTERN.sub(_sub, text)
    if replaced[0]:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"✅ 已替换 {md_path} 中 {replaced[0]} 处图片链接")
    else:
        print(f"ℹ️ {os.path.basename(md_path)} 无需替换")
    return replaced[0]
