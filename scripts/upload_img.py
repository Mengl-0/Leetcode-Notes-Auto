# -*- coding:utf-8 -*-
"""
图片上传脚本
支持：单张上传 / 批量上传 assets 下图片 / 扫描 md 替换本地图片链接
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import ASSETS_PATH, NOTES_DAILY_PATH, NOTES_PROBLEM_PATH, IMAGE_SUFFIXES
from core.oss_upload import upload_file, replace_img_in_md


def upload_single(path: str):
    """上传用户指定路径的单张图片"""
    url = upload_file(path)
    if url:
        print(f"✅ 上传成功：{path} -> {url}")
    return url


def batch_upload_assets():
    """批量上传 assets 文件夹下所有图片，返回 {本地路径: 线上链接} 映射"""
    result = {}
    files = [f for f in os.listdir(ASSETS_PATH)
             if f.lower().endswith(IMAGE_SUFFIXES)] if os.path.isdir(ASSETS_PATH) else []
    if not files:
        print(f"ℹ️ assets 目录没有待上传图片：{ASSETS_PATH}")
        return result
    for fname in files:
        full = os.path.join(ASSETS_PATH, fname)
        url = upload_file(full)
        if url:
            result[full] = url
            print(f"✅ {fname} -> {url}")
    print(f"📊 批量上传完成：成功 {len(result)} / 共 {len(files)}")
    return result


def _iter_md_files():
    for root in (NOTES_DAILY_PATH, NOTES_PROBLEM_PATH):
        for dirpath, _, files in os.walk(root):
            for f in files:
                if f.endswith(".md"):
                    yield os.path.join(dirpath, f)


def scan_all_md_replace():
    """扫描所有 md 文档，把本地图片链接替换为 OSS 线上链接"""
    total = 0
    count_md = 0
    for md in _iter_md_files():
        count_md += 1
        total += replace_img_in_md(md)
    print(f"📊 扫描 {count_md} 个 md 文件，共替换 {total} 处图片链接")
    return total


if __name__ == "__main__":
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
