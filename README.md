# LeetCode-Notes-Auto 刷题自动化知识库系统

面向个人算法刷题场景的自动化笔记管理工具，分四期迭代：

- **一期 · 自动化**：命令行菜单调度、Markdown 笔记模板、阿里云 OSS 图床上传、md 图片链接替换、笔记目录索引、Git 一键提交推送。
- **二期 · AI 增强**：接入 DeepSeek，自动分析题解思路/复杂度/易错点、生成每日刷题总结、Python↔Go 代码转换、代码 bug 检测。
- **三期 · RAG 知识库**：把全部笔记向量化，搭建私有刷题知识库，只基于你自己的笔记做检索问答。
- **四期 · Web 可视化界面**：Streamlit 图形界面（`web/`）——笔记浏览与管理、刷题统计看板、AI 增强、RAG 问答、一键同步与配置体检，与命令行入口功能对齐。

> 🌐 **在线入口（Streamlit 社区云）**：<https://mengl-0-leetcode-notes-auto-webapp-jjgrdx.streamlit.app/>
>
> 二三期功能全部**零依赖可跑**：AI 调用用标准库 urllib，向量化默认用离线哈希（TF-IDF 加权），未配置密钥时安全降级、不崩溃。

## 功能菜单（`python main.py`）

| 序号 | 分期 | 功能 |
| ---- | ---- | ---- |
| 1 | 一期 | 新建每日打卡笔记 `notes/daily/YYYY-MM-DD.md` |
| 2 | 一期 | 新建单题题解笔记 `notes/problems/NNNN-english-slug.md`（含 Python/Go 双代码区） |
| 3 | 一期 | 上传图片并替换 md 内本地图片链接 |
| 4 | 一期 | 一键同步：上传 + 链接替换 + 索引更新 + Git 提交推送 |
| 5 | 一期 | 更新笔记目录索引 `NOTES_INDEX.md` |
| 6 | 二期 | AI 增强：题解分析 / 每日总结 / 代码转换 / 代码检查 |
| 7 | 三期 | RAG 私有知识库：建索引 / 笔记问答 / 纯检索 |
| 8 | 系统 | 配置体检：查看各模块配置是否就绪 |

## 命名与目录规范

- 文件、目录名一律全英文小写，分隔符统一用连字符 `-`，禁止空格、中文、括号。
- 每日笔记：`YYYY-MM-DD.md`（例：`2026-10-08.md`）。
- 题解笔记：4 位补零题号 + 英文 slug（例：`0001-two-sum.md`）。
- 项目文档统一放在 `docs/` 目录。
- 依赖方向保持单向：`scripts/ → core/ → config/`，禁止反向引用。
- 所有路径由 `Path(__file__)` 推导，禁止硬编码绝对路径。

## 自动生成文件

- `NOTES_INDEX.md`：由 `scripts/update_index.py` 自动生成的笔记目录索引，**自动生成，勿手改**。保留在 Git 中（勿加入 `.gitignore`），每次同步会自动刷新。
- `vector_store/`：三期 RAG 的向量索引与 IDF 权重缓存，本地自动生成、体积可大，已被 `.gitignore` 忽略，可随时删除重建。

## 快速开始

```bash
# 1. 安装可选依赖（不装也能跑，仅 OSS 真实上传需要 oss2）
pip install -r requirements.txt

# 2. 配置密钥：复制模板后填写（推荐方式，config/secret.env 已被 .gitignore 忽略）
copy config\config.example.env config\secret.env
# 编辑 config\secret.env，填入 OSS / DeepSeek 的真实值

#    或改用环境变量（优先级高于 secret.env）
setx OSS_ACCESS_KEY_ID "你的AccessKeyId"
setx DEEPSEEK_API_KEY "sk-你的密钥"

# 3. 运行
python main.py
#    先选菜单 8「配置体检」，确认各模块缺哪些配置

# 4. Web 可视化界面（四期，需先安装 streamlit / plotly / pandas）
streamlit run web/app.py
#    已部署 Streamlit 社区云，可直接访问：https://mengl-0-leetcode-notes-auto-webapp-jjgrdx.streamlit.app/
```

> 密钥读取优先级：**环境变量 > `config/secret.env` > `config/.env` > 占位符**。三者都已被 `.gitignore` 忽略，切勿把真实密钥写进代码提交。

## 目录结构

```text
leetcode-notes-auto/
├─ main.py                 # 程序总入口（命令行菜单，调度一二三/四期功能）
├─ README.md               # 项目介绍（GitHub 仓库首页）
├─ requirements.txt        # 依赖清单（均可选，缺失时安全降级）
├─ NOTES_INDEX.md          # 自动生成的笔记索引，勿手改（保留在 Git）
├─ .gitignore              # 忽略密钥、临时图片、向量索引、缓存、日志
├─ docs/
│   └─ project-plan.md     # 项目方案文档（设计、任务清单、优化记录）
├─ config/
│   ├─ settings.py         # 唯一配置中心：路径 + OSS + DeepSeek + Embedding/RAG
│   └─ config.example.env  # 配置模板（复制为 secret.env 后填写，不含真实密钥）
├─ core/                   # 核心模块（只依赖 config/）
│   ├─ md_template.py      # Markdown 模板（每日打卡 / 单题题解）
│   ├─ oss_upload.py       # OSS 上传 + md 图片链接替换
│   ├─ git_auto.py         # Git add/commit/push 封装（带超时、校验远程）
│   ├─ logger.py           # 统一日志（写 logs/，已忽略）
│   ├─ notes_io.py         # 笔记读写公共模块（二三期共用）
│   ├─ ai_helper.py        # 二期：DeepSeek 调用（分析/总结/转换/检查）
│   ├─ embedding.py        # 三期：向量化（hash / 本地模型 / API 三种 provider）
│   └─ rag.py              # 三期：分块、建索引、检索、基于笔记问答
├─ scripts/                # 功能脚本（依赖 core/ 与 config/，可单跑也可经菜单调度）
│   ├─ new_daily_note.py   # 新建每日打卡笔记
│   ├─ new_problem.py      # 新建单题题解笔记
│   ├─ upload_img.py       # 单张/批量图片上传、链接替换
│   ├─ update_index.py     # 生成 NOTES_INDEX.md 目录索引
│   ├─ auto_sync.py        # 一键全流程同步
│   ├─ ai_assist.py        # 二期：AI 增强子菜单
│   └─ rag_query.py        # 三期：RAG 知识库子菜单
├─ web/                    # 四期：Streamlit Web 可视化界面（只调用 scripts/core，不改下层）
│   ├─ app.py              # 界面入口（streamlit run web/app.py，线上同左）
│   ├─ common.py           # 路径引导、题解元数据解析、终端输出捕获工具
│   ├─ browse.py           # 笔记浏览与管理
│   ├─ dashboard.py        # 刷题统计看板
│   ├─ ai_page.py          # AI 增强可视化
│   ├─ rag_page.py         # RAG 知识库问答
│   └─ sync_page.py        # 一键同步与配置体检
├─ notes/
│   ├─ daily/              # 每日打卡笔记（YYYY-MM-DD.md）
│   └─ problems/           # 单题题解（NNNN-english-slug.md）
└─ assets/                 # 本地截图临时目录（Git 忽略，仅保留 .gitkeep）
```

## 日常刷题工作流

1. `python main.py` 打开主菜单；
2. 选【1. 新建今日笔记】自动生成本日打卡 md；
3. 选【2. 新建题目笔记】输入题号与英文 slug 生成题解模板；
4. 写题解，把截图丢进 `assets/`；
5. 选【3. 上传图片并替换文档链接】一键上传并替换；
6. 选【6. AI 增强】分析题解、生成当日总结（需配 DeepSeek 密钥）；
7. 选【7. RAG 知识库】建索引后，用自然语言提问历史笔记；
8. 选【4. 一键同步 GitHub】自动上传 + 替换 + 更新索引 + 提交推送。

## 三期 RAG 说明与检索能力边界

默认 `EMBEDDING_PROVIDER=hash`：零依赖、完全离线，基于「字符 n-gram + 中英文词 + TF-IDF 加权」的特征哈希向量。

- **优点**：无需安装任何包、不联网、开箱即用，适合数十到数百篇笔记。
- **能力边界**：哈希向量本质是**关键词/字面匹配**，能精准命中「含相同术语」的提问（如问「时间复杂度」会高分命中复杂度章节），但**无法理解同义改写**（问「怎么求两数之和」不含「哈希表」字面时可能召回偏弱）。这是「零依赖离线」方案的固有取舍，非缺陷。
- **需要语义检索时**：把 `EMBEDDING_PROVIDER` 改为 `sentence_transformers`（本地模型，需 `pip install sentence-transformers`）或 `openai_compatible`（第三方 embedding 接口），检索质量显著提升；索引会因算法版本变更自动重建。
- 相关度低于 `RAG_MIN_SCORE` 的片段不参与回答，避免答非所问；未配置 DeepSeek 时，问答降级为直接展示检索到的原文片段。

## 安全说明

- OSS AccessKey、DeepSeek API Key 一律通过环境变量或本地密钥文件（`config/secret.env`）提供，代码仓库不落盘；
- `.gitignore` 已忽略 `config/secret.env`、`config/.env`、`config/secret.py`、`assets/` 图片、`vector_store/`、`__pycache__/`、`*.py[cod]`、`logs/` 与编辑器缓存；
- 配置层不再执行 `config/secret.py`（避免 `exec()` 执行任意代码的风险），改用纯文本 `secret.env`；
- Git 操作参数化调用且带超时，提交信息不会引发 shell 注入，网络异常不会永久挂起。

## 后续路线图

- Web 界面：✅ 已实现（四期 `web/` + Streamlit，本地 `streamlit run web/app.py`；线上：https://mengl-0-leetcode-notes-auto-webapp-jjgrdx.streamlit.app/）；
- 代码沙箱：本地运行 Python/Go 样例，把运行结果写入笔记；
- 导出功能：Markdown 笔记批量导出 PDF；
- 统计看板：✅ 已实现（四期看板：难度/标签分布、趋势、进度、待复习 Top）；周报导出待实现。
