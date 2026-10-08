# LeetCode-Notes-Auto 刷题自动化知识库系统

面向个人算法刷题场景的自动化笔记管理工具：命令行菜单统一调度、Markdown 笔记模板自动生成、阿里云 OSS 图床自动上传、文档图片链接替换、笔记目录索引自动生成、Git 一键提交推送；预留 LLM / RAG 扩展接口。

## 功能一览

| 入口 | 功能 |
| ---- | ---- |
| `python main.py` | 主菜单，调度以下所有功能 |
| 新建每日打卡笔记 | 生成 `notes/daily/YYYY-MM-DD.md` |
| 新建单题题解笔记 | 输入题号+英文 slug，生成 `notes/problems/NNNN-english-slug.md`（含 Python/Go 双代码区） |
| 上传图片并替换链接 | 单张/批量上传 assets 图片到 OSS，并替换 md 内本地图片链接 |
| 一键同步 GitHub | 上传 + 链接替换 + 索引更新 + git add/commit/push |

## 命名与目录规范

- 文件、目录名一律全英文小写，分隔符统一用连字符 `-`，禁止空格、中文、括号。
- 每日笔记：`YYYY-MM-DD.md`（例：`2026-10-08.md`）。
- 题解笔记：4 位补零题号 + 英文 slug（例：`0001-two-sum.md`）。
- 项目文档统一放在 `docs/` 目录。
- 依赖方向保持单向：`scripts/ → core/ → config/`，禁止反向引用。
- 所有路径由 `Path(__file__)` 推导，禁止硬编码绝对路径。

## 自动生成文件

- `NOTES_INDEX.md`：由 `scripts/update_index.py` 自动生成的笔记目录索引，**自动生成，勿手改**。该文件保留在 Git 中（勿加入 `.gitignore`），每次同步流程会自动刷新。

## 快速开始

```bash
# 1. 安装依赖
pip install oss2

# 2. 配置 OSS 密钥（推荐环境变量，切勿把密钥写进代码提交）
setx OSS_ACCESS_KEY_ID "你的AccessKeyId"
setx OSS_ACCESS_KEY_SECRET "你的AccessKeySecret"
setx OSS_BUCKET_NAME "你的bucket名"
# 可选：setx OSS_ENDPOINT "oss-cn-hangzhou.aliyuncs.com"
#       setx OSS_URL_BASE "https://自定义域名或bucket默认域名"

# 3. 运行
python main.py
```

也可以把上述键值写入 `config/secret.py`（`OSS_ACCESS_KEY_ID = "..."`）或 `config/.env`（`OSS_ACCESS_KEY_ID=...`），二者均已被 `.gitignore` 忽略。

## 目录结构

```text
leetcode-notes-auto/
├─ main.py                 # 程序总入口（命令行菜单）
├─ README.md               # 项目介绍（GitHub 仓库首页）
├─ NOTES_INDEX.md          # 自动生成的笔记索引，勿手改（保留在 Git）
├─ .gitignore              # 忽略密钥、临时图片、缓存、日志
├─ docs/
│   └─ project-plan.md     # 项目方案文档（设计、任务清单、优化记录）
├─ config/
│   └─ settings.py         # 路径、OSS、日期格式配置（密钥走环境变量/本地密钥文件）
├─ core/                   # 核心模块（只依赖 config/）
│   ├─ md_template.py      # Markdown 模板（每日打卡 / 单题题解）
│   ├─ oss_upload.py       # OSS 上传 + md 图片链接替换
│   └─ git_auto.py         # Git add/commit/push 封装
├─ scripts/                # 功能脚本（依赖 core/ 与 config/，可单跑也可经菜单调度）
│   ├─ new_daily_note.py   # 新建每日打卡笔记
│   ├─ new_problem.py      # 新建单题题解笔记
│   ├─ upload_img.py       # 单张/批量图片上传、链接替换
│   ├─ update_index.py     # 生成 NOTES_INDEX.md 目录索引
│   └─ auto_sync.py        # 一键全流程同步
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
6. 选【4. 一键同步 GitHub】自动上传 + 替换 + 更新索引 + 提交推送。

## 安全说明

- OSS AccessKey 一律通过环境变量或本地密钥文件提供，代码仓库不落盘；
- `.gitignore` 已忽略 `config/secret.py`、`config/.env`、`assets/` 图片、`__pycache__/`、`*.py[cod]`、`logs/` 与编辑器缓存；
- Git 操作使用参数化调用，提交信息不会引发 shell 注入。

## 后续路线图

- 二期：接入 DeepSeek API，自动生成思路/复杂度分析、每日总结、Python→Go 转换；
- 三期：笔记向量化，搭建私有 RAG 刷题知识库问答；
- 其他：Streamlit Web 界面、代码沙箱运行样例、批量导出 PDF。
