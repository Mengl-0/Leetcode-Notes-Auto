# LeetCode-Notes-Auto 刷题自动化知识库系统（项目方案文档）

> 文档用途：项目设计文档、开发任务清单、实现状态记录、简历项目说明素材
> 当前状态：**一期（自动化）+ 二期（AI 增强）+ 三期（RAG 知识库）已全部实现并通过本地验证**
> - 2026-10-08：一期功能补全 + 结构规范化改造（见第 11、12 节）
> - 2026-10-10：二期 DeepSeek AI 增强、三期 RAG 私有知识库落地，并修复一期若干遗留问题（见第 13、14 节）

---

# LeetCode-Notes-Auto 刷题自动化知识库系统

## 1. 项目概述

### 1.1 项目名称

LeetCode-Notes-Auto：刷题自动化知识库系统

### 1.2 项目定位

面向个人算法刷题场景，一套自动化笔记管理工具。实现脚本统一调度、Markdown 笔记模板自动生成、阿里云 OSS 图床自动上传、文档图片链接替换、Git 一键提交推送、笔记目录索引自动生成，后期可扩展 AI 题解生成、私有 RAG 知识库。

解决痛点：刷题笔记零散、手动写模板重复劳动、截图上传图床繁琐、图片链接容易失效、笔记无法系统化沉淀，提升刷题记录效率。

### 1.3 适配技术背景

开发者掌握 Python / Go 双语言，熟悉阿里云 OSS 图床、Git/GitHub、Markdown 文档编写、VSCode 开发环境，掌握数组双指针类算法，项目全部技术栈均为现有掌握技能，无额外陡峭学习成本。

### 1.4 项目价值（简历可直接摘抄）

独立设计并实现一套面向算法刷题的自动化知识库工具，实现文档生成、图床上传、Git 版本同步全流程自动化，搭建标准化算法题解知识库；预留 LLM 扩展接口，具备 AI 增强能力，可迭代升级为私有 RAG 问答知识库。锻炼工程化思维、脚本开发、文件 IO、云存储 SDK 调用、自动化流水线设计能力。

## 2. 技术选型

| 模块 | 技术 | 说明 |
|---|---|---|
| 主体脚本开发 | Python3 | 文件处理、脚本调度、OSS SDK、Markdown 文本生成，开发效率高 |
| 算法代码存档 | Go / Python | 题解模板内置双语言代码区，保存 LeetCode 题解代码 |
| 图床存储 | 阿里云 OSS（oss2 SDK） | 存储截图，生成 Markdown 图片链接，内置配置校验与异常捕获 |
| 文档格式 | Markdown（UTF-8） | 刷题笔记、题解文档，适配 GitHub 渲染 |
| 版本管理 | Git | 自动提交、推送至 GitHub 仓库，参数化调用避免 shell 注入 |
| 扩展模块（二期） | DeepSeek LLM API | AI 自动生成题解、复杂度分析、刷题总结 |
| 扩展模块（三期） | 向量数据库 | RAG 私有刷题知识库，基于笔记问答算法题目 |

## 3. 项目目录结构（与实际代码一致）

命名规范：文件/目录名一律全英文小写、连字符 `-` 分隔，禁止空格、中文、括号；每日笔记 `YYYY-MM-DD.md`；题解笔记 `NNNN-english-slug.md`（如 `0001-two-sum.md`）。依赖方向单向：`scripts/ → core/ → config/`。

```text
leetcode-notes-auto/
├─ main.py                 # 程序总入口（命令行菜单，调度所有功能）
├─ README.md               # 项目介绍文档（GitHub 仓库首页）
├─ NOTES_INDEX.md          # 自动生成的笔记目录索引（保留在 Git，勿手改）
├─ .gitignore              # 忽略密钥、临时图片、缓存、日志
├─ docs/
│   └─ project-plan.md     # 本方案文档（设计、任务清单、优化记录）
├─ config/
│   ├─ settings.py         # 唯一配置中心：路径 + OSS + DeepSeek + Embedding/RAG
│   └─ config.example.env  # 配置模板（复制为 secret.env 后填写，不含真实密钥）
├─ core/                   # 核心模块（只依赖 config/）
│   ├─ md_template.py      # Markdown 模板生成（每日打卡 / 单题题解）
│   ├─ oss_upload.py       # OSS 上传 + md 图片链接替换核心模块
│   ├─ git_auto.py         # git add/commit/push 封装模块（带超时、校验远程）
│   ├─ logger.py           # 统一日志（写 logs/，已 gitignore）
│   ├─ notes_io.py         # 笔记读写公共模块（二三期共用）
│   ├─ ai_helper.py        # 二期：DeepSeek 调用（分析/总结/转换/检查）
│   ├─ embedding.py        # 三期：向量化（hash / 本地模型 / API 三种 provider）
│   └─ rag.py              # 三期：分块、建索引、检索、基于笔记问答
├─ scripts/                # 功能脚本（依赖 core/ 与 config/，可单跑也可被 main.py 调度）
│   ├─ new_daily_note.py   # 新建每日刷题打卡笔记（YYYY-MM-DD.md）
│   ├─ new_problem.py      # 新建单题题解笔记（NNNN-english-slug.md）
│   ├─ upload_img.py       # 单张/批量图片上传、扫描 md 替换链接
│   ├─ update_index.py     # 扫描笔记生成 NOTES_INDEX.md 目录索引
│   ├─ auto_sync.py        # 一键全量同步：上传+替换+索引+git 推送
│   ├─ ai_assist.py        # 二期：AI 增强子菜单
│   └─ rag_query.py        # 三期：RAG 知识库子菜单
├─ notes/
│   ├─ daily/              # 每日打卡笔记存放目录
│   └─ problems/           # 单题详细题解文档目录
├─ vector_store/           # 三期 RAG 向量索引与 IDF 缓存（本地生成，已 gitignore）
└─ assets/                 # 本地截图/图片临时文件夹（已 gitignore，仅保留 .gitkeep）
```

## 4. 功能详细设计（分阶段迭代）

### 阶段 1：基础框架搭建 ✅ 已完成

1. `main.py` 主控入口：命令行菜单，选择功能、调用对应脚本，支持退出。
2. `config/settings.py` 全局配置：唯一配置中心，统一管理笔记存储路径、日期格式、OSS、DeepSeek、Embedding/RAG 参数；密钥按「环境变量 > config/secret.env > config/.env > 占位」优先级读取，不落盘提交。出于安全不再执行 `config/secret.py`（避免 `exec()` 执行任意代码），改用纯文本 `secret.env`。
3. `core/md_template.py` 模板引擎：内置两套 Markdown 模板
   - 模板 A：每日刷题打卡模板（今日完成题目表格、知识点收获、踩坑记录、后续计划、总结）
   - 模板 B：单题算法题解模板（题号、题目描述、思路分析、Python 代码、Go 代码、复杂度、踩坑、收获、复盘记录表）
4. `scripts/new_daily_note.py`：默认生成今日 `YYYY-MM-DD.md` 到 notes/daily，也支持命令行传入指定日期；重复生成时提示已存在。
5. `scripts/new_problem.py`：输入题号（数字）与英文 slug（如 `two-sum`），自动生成 `NNNN-english-slug.md`（如 `0001-two-sum.md`）到 notes/problems；slug 自动规范为小写连字符，标题可另填用于文档首行。

### 阶段 2：图床自动化模块 ✅ 已完成

1. `core/oss_upload.py`：图片上传核心函数，读取本地图片上传阿里云 OSS，返回线上链接；远端文件名带内容 SHA1 短哈希，同图去重、避免覆盖；显式设置 Content-Type，规避图片类型识别踩坑。
2. `scripts/upload_img.py`：独立脚本，支持单张上传 / assets 批量上传 / 扫描全部 md 替换链接三种模式，输出成功统计。
3. 附加能力：`replace_img_in_md` 扫描 md 文件，查找 `![xxx](本地路径)` 格式图片，自动上传并替换为 OSS 线上链接；已是 http(s) 链接的自动跳过。
4. 兜底：未安装 oss2 或未配置密钥时，给出明确的缺失项清单与配置指引，不中断整体流程。

### 阶段 3：Git 自动化同步 ✅ 已完成

1. `core/git_auto.py`：参数化调用 git（不经过 shell），自动执行 git add → commit（自动生成提交信息）→ push；准确区分「无变更无需提交」「无上游分支」「推送失败」并给出对应提示。
2. `scripts/auto_sync.py` 一键同步脚本：整合图片上传、链接替换、目录索引更新、git 提交，一条命令完成全部同步。

### 阶段 4：完整自动化工作流 ✅ 已完成

一条指令（`python main.py` → 菜单 4）完成整套流程：

1. 批量上传 assets 下所有图片
2. 替换 md 内本地图片链接为 OSS 线上链接
3. 自动更新仓库目录索引文档 `NOTES_INDEX.md`
4. Git 自动提交并推送 GitHub

每日新建笔记通过菜单 1/2 完成；索引文件由 `scripts/update_index.py` 独立生成。

### 阶段 5：AI 增强扩展（二期）✅ 已完成

对接 DeepSeek 大模型（OpenAI 兼容接口），实现四项能力：

1. **题解分析** `analyze_problem()`：读取题解 md，生成核心思路、时间/空间复杂度分析、易错点、更优解法建议。
2. **每日总结** `summarize_daily()`：读取当日笔记，生成收获总结与 2~3 条改进建议，可选追加写回笔记。
3. **代码转换** `convert_py_to_go()`：Python 代码等价转 Go，输出可运行片段 + 关键差异说明。
4. **代码检查** `review_code()`：bug / 边界错误 / 复杂度 / 可读性 code review。

实现要点：
- 新增 `core/ai_helper.py`，用**标准库 urllib** 直接调 `/chat/completions`，无需安装 `openai` 包，实现零依赖。
- 入口 `scripts/ai_assist.py`（main.py 菜单 6），子菜单交互；可按题号/slug/序号定位题解。
- 密钥走 `DEEPSEEK_API_KEY`；未配置时提示并安全退出，**不触发联网**；HTTPError/URLError/超时/解析失败均有分级捕获与友好提示。
- 统一 system prompt 约束「资深算法教练、结构化中文、不编造题目条件」。

### 阶段 6：RAG 私有知识库（三期）✅ 已完成

将全部 Markdown 笔记向量化，搭建私有知识库，只基于自己的笔记做检索问答：

1. **建索引** `build_index()`：扫描 notes/ 全部 md，按标题层级切分知识块（代码块内不切分、超长按段落/句子二次切分），向量化后持久化到 `vector_store/index.json`；用内容指纹判断笔记是否变更，未变更则跳过重建。
2. **检索** `search()`：问题向量化 → 余弦相似度排序 → 过滤低于 `min_score` 的片段 → 返回 top_k。
3. **问答** `answer()`：把命中片段作为上下文交给 DeepSeek，生成「只基于自己笔记」的回答并标注来源；未配 DeepSeek 时**降级为直接展示检索原文片段**。

实现要点：
- 新增 `core/embedding.py` + `core/rag.py`，入口 `scripts/rag_query.py`（main.py 菜单 7）。
- 三种 provider：`hash`（默认，**零依赖离线**特征哈希）/ `sentence_transformers`（本地语义模型）/ `openai_compatible`（第三方 embedding 接口）。
- **hash 模式引入 TF-IDF 加权**（详见第 14 节遗留问题修复）：纯特征哈希会让高频虚词主导相似度、区分度失效；加权后「含相同术语」的提问能高分命中对应章节，IDF 权重随索引持久化，保证建索引与查询同一向量空间。
- 索引记录 `schema` 版本与 `provider`，任一变更自动触发重建，避免新旧向量空间混用。
- `vector_store/` 已加入 `.gitignore`（本地可重建，体积可大）。

## 5. 脚本功能详细说明

| 脚本名称 | 核心功能 | 状态 |
|---|---|---|
| main.py | 项目总入口，命令行菜单，调度所有子脚本，统一入口管理 | ✅ |
| config/settings.py | 全局配置中心：路径、OSS、日期格式；密钥分层读取与配置校验 | ✅ |
| core/md_template.py | 存放 Markdown 模板，对外提供函数，直接生成完整笔记文本 | ✅ |
| core/oss_upload.py | 核心模块：图片上传、返回线上链接、替换 md 文档图片地址 | ✅ |
| core/git_auto.py | 封装 git 操作，自动检测文件变更，执行提交推送，异常友好提示 | ✅ |
| scripts/new_daily_note.py | 创建每日刷题打卡笔记文件（YYYY-MM-DD.md），支持指定日期 | ✅ |
| scripts/new_problem.py | 创建单道 LeetCode 题解文档（NNNN-english-slug.md），slug 规范化校验 | ✅ |
| scripts/upload_img.py | 独立图片上传工具：单张 / 批量 / 全量 md 链接替换 | ✅ |
| scripts/update_index.py | 扫描笔记目录，自动生成 NOTES_INDEX.md 导航索引 | ✅ |
| scripts/auto_sync.py | 一键全流程同步：图片上传 + 链接替换 + 索引更新 + git 推送 | ✅ |

## 6. 改造后刷题工作流

### 旧流程

新建 md 文件 → 复制模板 → 截图保存 → 手动上传 OSS → 复制图片链接粘贴 md → 手写题解与收获 → 手动执行 git add/commit/push 推送到 GitHub。

> 缺点：大量重复手工操作，图片上传繁琐，容易漏提交。

### 新自动化流程

1. 运行 `python main.py`，打开主菜单
2. 选择【1. 新建今日笔记】，自动生成当日打卡 md
3. 选择【2. 新建题目笔记】，输入题号与英文 slug，生成 `0001-two-sum.md` 式题解模板文档
4. 在文档内写题解、粘贴截图到 assets 文件夹
5. 选择【3. 上传图片并替换文档链接】自动上传所有截图，替换本地图片地址
6. 选择【6. AI 增强】分析题解思路/复杂度、生成当日总结（需配 DeepSeek 密钥）
7. 选择【7. RAG 知识库】建索引后，用自然语言检索问答历史笔记
8. 选择【4. 一键同步 GitHub】自动上传 + 替换 + 更新索引 + 提交推送

## 7. 开发排期计划

| 时间 | 任务 | 交付物 | 状态 |
|---|---|---|---|
| 第 1 天 | 搭建项目目录，编写 main 入口、配置文件、md 模板、新建笔记脚本 | 基础框架，可生成每日 / 单题 Markdown 笔记 | ✅ |
| 第 2 天 | 开发 OSS 图片上传模块，图片链接替换脚本 | 支持图片上传、md 文档链接自动替换 | ✅ |
| 第 3 天 | 开发 Git 自动提交脚本，一键同步脚本 | 一键同步笔记到 GitHub | ✅ |
| 第 4~7 天 | 联调全流程，测试 bug，完善 README，完善异常捕获 | 完整可用版本；已补齐目录索引自动生成 | ✅（真实 OSS 上传需配置密钥后联调） |
| 二期（2026-10-10） | 接入 DeepSeek API，实现 AI 题解分析、每日总结、代码转换与检查 | AI 增强版本（core/ai_helper.py + scripts/ai_assist.py） | ✅ |
| 三期（2026-10-10） | RAG 私有知识库：笔记向量化、检索、基于笔记问答 | 算法笔记问答系统（core/embedding.py + core/rag.py + scripts/rag_query.py） | ✅ |

## 8. 项目亮点（简历描述）

1. 工程自动化：独立设计自动化流水线，实现文档生成、云存储上传、版本推送全链路自动化，减少重复手工操作。
2. 云存储实践：基于阿里云 OSS 开发图床模块，解决图片上传、链接管理、静态资源访问问题；内容哈希命名去重、显式 Content-Type、配置校验兜底，覆盖 OSS 常见踩坑场景。
3. 模块化设计：项目采用「配置 / 核心 / 脚本 / 入口」分层架构，核心模块、脚本、配置分离，代码可维护、可扩展。
4. 安全设计：密钥全部走环境变量或本地忽略文件，Git 操作参数化调用杜绝 shell 注入，`.gitignore` 完整覆盖密钥、临时图片与缓存。
5. 知识库沉淀：搭建标准化算法刷题知识库，统一笔记格式，自动生成目录索引，便于长期沉淀学习内容。
6. AI 增强落地（二期）：基于 DeepSeek（OpenAI 兼容接口，标准库 urllib 零依赖调用）实现题解分析、每日总结、Python↔Go 转换、代码检查，未配密钥安全降级不联网。
7. 私有 RAG 知识库（三期）：笔记按标题分块向量化，默认零依赖离线哈希向量 + TF-IDF 加权，支持切换本地语义模型/第三方接口；检索问答只基于自己笔记并标注来源，索引按 schema 版本自动失效重建。

## 9. 风险与注意事项

1. 密钥安全：**禁止将 AccessKey / API Key 硬编码写入代码并提交 GitHub**。密钥通过环境变量（推荐）或 `config/secret.env` / `config/.env` 提供，均已被 `.gitignore` 忽略。出于安全，配置层**不再执行 `config/secret.py`**（避免 `exec()` 运行任意代码），只解析纯文本 `KEY=VALUE`。
2. 异常捕获：图片上传、Git 操作、AI 调用、向量化、RAG 检索均有异常捕获；未装 oss2、未配密钥、无上游分支、网络失败、接口报错等场景给出友好提示而非崩溃。
3. 文件编码：Markdown 与 Python 源码统一 UTF-8，Git 输出按 UTF-8 解码，防止中文乱码。
4. 脚本运行方式：`scripts/` 下脚本可独立运行（内置项目根路径引导），也可经 `main.py` 调度，两种方式导入一致。
5. 首次使用 Git：仓库需已 `git init` 并配置 remote 与上游分支，首次推送建议 `git push -u origin main`；未配远程时一键同步会本地提交并提示，不会报错中断。
6. 真实上传依赖：`pip install oss2` 并填好密钥后，图床模块才能真实联网上传；AI/RAG 的生成能力需配置 `DEEPSEEK_API_KEY`。
7. RAG 检索边界：默认 hash 向量为字面/关键词匹配，擅长命中含相同术语的提问，不擅长同义改写；需要语义检索时切换 `sentence_transformers` 或 `openai_compatible` provider。

## 10. 后续拓展方向

1. Web 界面：用 Streamlit 做简易网页界面，不用命令行操作。
2. 代码沙箱：增加 Python/Go 代码本地运行，自动执行样例，把运行结果写入笔记。
3. 目录索引自动生成：✅ 已实现（`scripts/update_index.py` → `NOTES_INDEX.md`），后续可加入按标签/难度分类。
4. AI 增强：✅ 已实现（二期，`core/ai_helper.py`）。
5. RAG 私有知识库：✅ 已实现（三期，`core/embedding.py` + `core/rag.py`）。
6. 导出功能：将 Markdown 笔记批量导出为 PDF。
7. 统计看板：按题号/难度/日期统计刷题量，生成周报表（题解模板已预留「难度/标签」结构化字段支撑）。

## 11. 实现状态与优化记录（2026-10-08）

初版代码存在缺失与缺陷，本次全部修复并验证通过：

| # | 问题 | 修复 |
|---|---|---|
| 1 | `core/oss_upload.py` 为空文件，上传与链接替换功能整体缺失 | 完整实现上传、md 扫描替换、路径解析、哈希去重、异常兜底 |
| 2 | `core/md_template.py` 题解模板中途截断（代码块未闭合、缺 Go 代码/复杂度/复盘区） | 补全每日打卡与单题题解双模板 |
| 3 | `scripts/new_problen.py` 文件名拼写错误，main.py 引用的 `new_problem.py` 不存在 | 重建为 `new_problem.py`，旧错名文件已移入回收站 |
| 4 | `scripts/*` 以脚本直跑时 `from config...` 导入失败（sys.path 无项目根） | 各脚本内置项目根路径引导，单跑/菜单两种方式均可用 |
| 5 | `config/settings.py` 的 bucket 为占位符且无校验，密钥来源单一 | 环境变量 > secret.py/.env 分层读取，新增 `validate_oss_config` 缺失项校验 |
| 6 | `core/git_auto.py` 使用 shell=True 拼接提交信息，含引号会失效且有注入风险；「无变更」误判脆弱 | 改参数化调用；以暂存区 diff 准确判断变更；补充无上游分支与失败原因提示 |
| 7 | `upload_img.py` 不支持单张上传，批量上传无统计；md 替换无 http 链接跳过 | 补单张上传入口、成功统计、线上链接自动跳过 |
| 8 | 缺少方案中的「目录索引自动生成」 | 新增 `scripts/update_index.py` 生成 `NOTES_INDEX.md`，并入一键同步流程 |
| 9 | 缺少 README、assets/notes 目录不全 | 补齐 README.md、目录结构与 `.gitkeep`，notes 目录自动生成 |
| 10 | `.gitignore` 对 assets 忽略不完整、编辑器忽略项含路径笔误 | 整体忽略 assets（保留 .gitkeep），修正 `.vscode`、补充 `.idea`、`Thumbs.db` |

验证结果：全模块编译通过；菜单入口、单脚本直跑、指定日期建笔记、非法文件名过滤、链接替换解析（缺失文件与线上链接均正确跳过）、索引生成、git 变更检测、密钥缺失友好提示——均已本地实测通过。真实 OSS 上传与 GitHub 推送需配置密钥/远程仓库后联调。

## 12. 结构规范化改造记录（2026-10-08）

按命名、目录、卫生、自动生成文件四类规范完成改造：

**命名规范**
- 笔记文件名全部改为英文规范：每日笔记 `YYYY-MM-DD.md`（原「2026-10-08 刷题记录.md」已迁移为「2026-10-08.md」）；题解笔记 4 位补零编号 + 英文 slug（原「1_两数之和.md」已迁移为「0001-two-sum.md」）。
- 分隔符统一为连字符 `-`，笔记文件名不再含空格、中文、括号；文档标题仍可用中文（写在 md 内容首行）。
- `new_problem.py` 改为输入题号+英文 slug（可另填中文标题），内置 slug 规范化与校验。

**目录规范**
- 项目文档统一放入 `docs/`（方案文档移至 `docs/project-plan.md`）。
- 依赖保持单向 `scripts/ → core/ → config/`，core/config 不反向引用上层。
- 一级目录复核：无拼写错误目录（不存在 asserts）、无空目录（assets 以 .gitkeep 占位）。

**卫生规范**
- 清理全部 `__pycache__/` 与 `*.pyc`（共 4 处缓存目录）。
- `.gitignore` 补齐 `__pycache__/`、`*.py[cod]`、`logs/`，并修正 assets 忽略方式（`assets/*` + `!assets/.gitkeep`）。
- 路径统一由 `Path(__file__)` 推导（`config/settings.py` 的 BASE_DIR 已改造），无硬编码绝对路径。

**自动生成文件**
- `NOTES_INDEX.md` 保留在 Git（已在 .gitignore 注释说明勿加入忽略），README 与本方案文档均注明「自动生成，勿手改」。

**遗留提示**：项目根目录之外（盘面上层）的旧方案文档副本 `LeetCode-Notes-Auto 刷题自动化知识库系统（项目方案文档）.md` 内容已过时，规范版以 `docs/project-plan.md` 为准；是否需要删除请用户确认。

## 13. 二期 / 三期实现记录（2026-10-10）

**二期 · AI 增强（DeepSeek）**
- 新增 `core/ai_helper.py`：`chat()` 底层封装 + `analyze_problem` / `summarize_daily` / `convert_py_to_go` / `review_code` 四个能力函数。
- 用标准库 `urllib.request` 调 OpenAI 兼容 `/chat/completions`，**不引入 openai SDK**，零依赖。
- 新增 `scripts/ai_assist.py`（main.py 菜单 6），子菜单交互；题解定位支持题号/slug/序号。
- 分级异常处理：HTTPError（读回错误体前 500 字）/ URLError（网络）/ 解析失败 / 兜底超时，均友好提示不崩溃；未配密钥时直接提示退出，不触发联网。

**三期 · RAG 私有知识库**
- 新增 `core/embedding.py`：三种 provider（hash 默认离线 / sentence_transformers 本地模型 / openai_compatible 第三方接口），统一归一化输出，点积即余弦相似度。
- 新增 `core/rag.py`：`iter_note_files` 遍历 → `_split_by_heading` 按标题分块（代码块内不切、超长按段落/句子二次切）→ `build_index` 向量化并持久化 → `search` 检索 top_k → `answer` 基于笔记问答。
- 新增 `scripts/rag_query.py`（main.py 菜单 7）：建索引 / 问答 / 纯检索三个子功能。
- 新增 `core/notes_io.py`：二三期共用的笔记遍历、读取、定位公共模块，避免重复实现。
- 索引持久化到 `vector_store/index.json`，含 `schema` 版本、`provider`、内容指纹；笔记未变更或版本一致时跳过/触发重建。
- 未配 DeepSeek 时，`answer()` 降级为直接展示检索到的原文片段。

**main.py 菜单重构**：按「一期 / 二期 / 三期 / 系统」分组渲染，新增菜单 5（更新索引）、6（AI）、7（RAG）、8（配置体检），补齐 KeyboardInterrupt/EOFError 处理。

**验证结果**：全模块编译 + 导入通过；配置体检正确区分「已配/待补」；RAG 建索引（14 个知识块）、相关提问高分命中（复杂度类提问 top1≈0.46）、无关提问低分、未配密钥降级展示片段——均本地实测通过；AI 与 RAG 的联网生成需填 `DEEPSEEK_API_KEY` 后联调。

## 14. 一期遗留问题修正记录（2026-10-10）

复核一期代码时发现以下**真实缺陷**（非文档瑕疵），本次一并修复：

| # | 问题 | 严重度 | 修复 |
|---|---|---|---|
| 1 | **`.gitignore` 未忽略 `config/secret.env`**：代码实际读取的是 `secret.env`，但忽略列表里只有已停用的 `secret.py` 和 `.env`——用户填入真实密钥后会被提交到 GitHub | 🔴 安全 | `.gitignore` 补 `config/secret.env`（并保留 `secret.py`/`.env` 兼容旧用户），同时补忽略 `vector_store/` |
| 2 | **`core/oss_upload.py` 上传必现 KeyError**：取 `OSS_CONFIG['public_url_base']`，但配置字典根本没有这个键（settings 提供的是 `get_oss_public_url_base()` 函数），真实上传时必定抛异常并被误报为「上传失败」 | 🔴 功能 | 改为调用 `get_oss_public_url_base()`；哈希计算抽出 `_build_remote_key()`，修正失败时打印未定义变量的问题 |
| 3 | **`core/git_auto.py` push 无超时会永久挂起**：网络异常时 `subprocess.run` 无限等待，一键同步卡死 | 🟠 稳定性 | 所有 git 调用加 timeout（本地 30s / push 120s）；新增 `has_remote()`，无远程时本地提交并提示、不当作失败；分支名动态读取用于「无上游」提示 |
| 4 | **hash 向量检索区分度失效**：纯特征哈希下，完全无关的提问（「编译器前端」top1=0.11）分数竟高于相关提问（0.102），高频虚词主导相似度 | 🟠 质量 | hash provider 引入 **TF-IDF 加权**：建索引时统计 DF 并持久化 IDF，查询复用同一套权重；`SCHEMA_VERSION` 标记使旧索引自动失效重建。修复后含相同术语的提问可冲到 0.4+，无关提问维持噪声级 |
| 5 | **配置层 `exec()` 执行 `secret.py` 的安全隐患**：旧版用 exec 加载密钥文件，等于允许执行任意代码 | 🟠 安全 | 已在 settings.py 停用 secret.py，只解析纯文本 `KEY=VALUE`；检测到旧文件给出迁移提示 |
| 6 | **模板/索引信息偏弱**：题解模板无「难度/标签/复习次数」结构化字段，索引只显示文件名不显示标题 | 🟢 体验 | 题解模板补元数据头与题解链接列；索引读取 md 一级标题展示（如「LeetCode 1. 两数之和」），每日笔记补题解链接列 |
| 7 | **`notes_io.list_daily_notes()` 排序逻辑晦涩且结果错误**：原写法用 `and`/`+` 拼接排序，语义混乱 | 🟢 质量 | 重写为「规范日期倒序 + 非规范按字典序垫后」的清晰实现 |

> 说明：一期第 11 节记录的是「初版空文件/截断/拼写」类缺失，本节记录的是**功能已存在但实现有 bug/隐患**的问题，二者不重复。第 1、2、5 项属安全或功能级，建议优先关注。

---

## 使用说明（复制到 Word 操作提示）

1. 全选本文文字，复制粘贴进 WPS/Word；
2. 标题自动识别，可在「样式」面板设置：一级标题二号黑体，二级标题小三号，正文小四宋体，1.5 倍行距；
3. 表格可以直接保留，可按需调整宽度；
4. 代码块（目录树）可以设置为「等宽字体」，如 Consolas。
