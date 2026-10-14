# Changelog

本项目的重要变更都记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [Semantic Versioning](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### Added
- 初始化三期功能骨架：自动化笔记 / AI 增强 / RAG 私有知识库
- 阿里云 OSS 图床上传与 md 图片链接自动替换
- DeepSeek 题解分析、每日总结、Python↔Go 互转、代码 review
- hash 离线向量 / sentence_transformers 本地模型 / openai_compatible API 三种向量化 provider
- 配置体检（菜单 8）

### Fixed（2026-10-14 审计修复）
- **P0** 一键同步时图片重复上传：`batch_upload_assets` 与 `scan_all_md_replace` 之间共享 `url_cache`，已上传图片不再二次 PUT
- **P0** AI 每日总结写入笔记时日期标签错误：改用笔记文件名日期，不再用运行当天日期
- **P0** 配置读取空值处理：`secret.env` 中显式留空（`KEY=`）现在能正确覆盖默认值
- **P1** 主菜单不再为每个功能 subprocess 重启 Python 解释器，改为进程内 `importlib` 调用 `run()`
- **P1** DeepSeek 网络抖动 / 5xx / 429 自动重试 2 次，间隔 2s；区分临时错误与永久错误
- **P1** RAG 索引支持文件粒度增量重建（非 hash provider），未变更文件向量直接复用
- **P1** Git push 被远程拒绝时自动 `pull --rebase` 并重试一次；真冲突时自动 abort 并提示
- **P1** Windows 非 tty 环境（VS Code 输出捕获）下改用 UTF-8 输出，emoji 不再变 `?`
- **P1** 上传成功的图片自动归档到 `assets/uploaded/YYYY-MM-DD/`，避免根目录堆积
- **P2** `build_index` 失败统一返回 `None`，成功返回 chunk 列表，返回值约定统一
- **P2** `init_dir()` 从模块导入副作用改为入口显式调用，测试 / CI 不再自动建目录

## [0.1.0] - 2026-10-08

### Added
- 首次可运行版本：每日打卡 / 单题题解模板、OSS 图床、Git 一键同步
