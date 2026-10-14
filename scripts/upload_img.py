# -*- coding:utf-8 -*-
"""
图片上传脚本
支持：单张上传 / 批量上传 assets 下图片 / 扫描 md 替换本地图片链接
"""
import os
import sys
import shutil
from collections.abc import Iterator
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import ASSETS_PATH, NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, IMAGE_SUFFIXES, init_dir
from core.oss_upload import upload_file, replace_img_in_md


def _archive_uploaded(full_path: str) -> None:
    """
    上传成功的图片移入 assets/uploaded/YYYY-MM-DD/ 归档，避免根目录堆积（审计问题 9）。
    失败图片留在原地等待下次重试；目标已存在同名文件时跳过移动、保留两边，不覆盖。
    """
    dest_dir = os.path.join(ASSETS_PATH, "uploaded", datetime.now().strftime("%Y-%m-%d"))
    dest = os.path.join(dest_dir, os.path.basename(full_path))
    if os.path.exists(dest):
        print(f"⚠️ 归档目标已存在同名文件，跳过移动：{dest}")
        return
    try:
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(full_path, dest)
    except OSError as e:
        print(f"⚠️ 归档移动失败（不影响已上传结果）：{e}")


def upload_single(path: str) -> str | None:
    """上传用户指定路径的单张图片"""
    url = upload_file(path)
    if url:
        print(f"✅ 上传成功：{path} -> {url}")
    return url


def batch_upload_assets(url_cache: dict | None = None) -> dict:
    """
    批量上传 assets 文件夹下所有图片，返回 {本地路径: 线上链接} 映射。
    :param url_cache: 可选共享缓存，命中的路径直接跳过重复上传（审计问题 1）。
    """
    result = url_cache if url_cache is not None else {}
    files = [f for f in os.listdir(ASSETS_PATH)
             if f.lower().endswith(IMAGE_SUFFIXES)] if os.path.isdir(ASSETS_PATH) else []
    if not files:
        print(f"ℹ️ assets 目录没有待上传图片：{ASSETS_PATH}")
        return result
    skipped = 0
    ok = 0
    for fname in files:
        full = os.path.abspath(os.path.join(ASSETS_PATH, fname))
        if full in result:
            skipped += 1
            continue
        url = upload_file(full)
        result[full] = url
        if url:
            ok += 1
            print(f"✅ {fname} -> {url}")
    print(f"📊 批量上传完成：成功 {ok} / 共 {len(files)}"
          + (f"（缓存命中跳过 {skipped}）" if skipped else ""))
    return result


def _iter_md_files() -> "Iterator[str]":
    for root in (NOTES_DAILY_PATH, NOTES_PROBLEM_PATH):
        for dirpath, _, files in os.walk(root):
            for f in files:
                if f.endswith(".md"):
                    yield os.path.join(dirpath, f)


def scan_all_md_replace(url_cache: dict | None = None) -> int:
    """
    扫描所有 md 文档，把本地图片链接替换为 OSS 线上链接。
    :param url_cache: 可选的 {本地绝对路径: 线上链接} 缓存；一键同步时传入
        batch_upload_assets 的返回值，已上传过的图片不再二次上传（审计问题 1）。
        替换完成后，缓存中上传成功且位于 assets 根目录的图片会归档到
        assets/uploaded/日期/，失败图片留在原地等待下次重试（审计问题 9）。
    """
    total = 0
    count_md = 0
    for md in _iter_md_files():
        count_md += 1
        total += replace_img_in_md(md, url_cache=url_cache)
    print(f"📊 扫描 {count_md} 个 md 文件，共替换 {total} 处图片链接")
    if url_cache:
        archived = 0
        for p, url in list(url_cache.items()):
            if url and os.path.dirname(p) == ASSETS_PATH and os.path.exists(p):
                _archive_uploaded(p)
                archived += 1
        if archived:
            print(f"📦 已归档 {archived} 张上传成功的图片到 assets/uploaded/ 下")
    return total


def run() -> None:
    """供 main.py 进程内调用的入口（审计问题 4）；目录初始化显式执行（审计问题 11）"""
    init_dir()
    try:
        print("1. 上传单张图片（输入路径）")
        print("2. 批量上传 assets 目录图片")
        print("3. 扫描全部 md，替换本地图片链接")
        opt = input("请选择：").strip()
        if opt == "1":
            p = input("请输入图片路径：").strip().strip('"')
            if p:
                upload_single(p)
        elif opt == "2":
            batch_upload_assets()
        elif opt == "3":
            scan_all_md_replace()
        else:
            print("❌ 无效选择")
    except KeyboardInterrupt:
        print("\n⏹️ 已取消")


if __name__ == "__main__":
    run()
