# LeetCode-Notes-Auto 刷题自动化知识库系统

面向个人算法刷题场景的自动化笔记管理工具：脚本统一调度、Markdown 笔记模板自动生成、阿里云 OSS 图床自动上传、文档图片链接替换、Git 一键提交推送；预留 LLM / RAG 扩展接口。

## 功能一览

| 入口 | 功能 |
| ---- | ---- |
| `python main.py` | 主菜单，调度以下所有功能 |
| 新建每日打卡笔记 | 生成 `notes/daily/yyyy-mm-dd 刷题记录.md` |
| 新建单题题解笔记 | 输入题号+题目名，生成含 Python/Go 双代码区的题解模板 |
| 上传图片并替换链接 | 单张/批量上传 assets 图片到 OSS，并替换 md 内本地图片链接 |
| 一键同步 GitHub | 上传 + 链接替换 + 索引更新 + git add/commit/push |

## 快速开始

```bash
# 1. 安装依赖
pip install oss2

# 2. 配置 OSS 密钥（三选一，推荐环境变量，切勿把密钥写进代码提交）
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

```
leetcode-notes-auto/
├─ main.py                 # 程序总入口（命令行菜单）
├─ config/settings.py      # 全局配置：路径、OSS、日期格式（密钥走环境变量）
├─ core/
│   ├─ md_template.py      # Markdown 模板（每日打卡 / 单题题解）
│   ├─ oss_upload.py       # OSS 上传 + md 图片链接替换
│   └─ git_auto.py         # Git add/commit/push 封装
├─ scripts/
│   ├─ new_daily_note.py   # 新建每日打卡笔记
│   ├─ new_problem.py      # 新建单题题解笔记
│   ├─ upload_img.py       # 单张/批量图片上传、链接替换
│   ├─ update_index.py     # 生成 NOTES_INDEX.md 目录索引
│   └─ auto_sync.py        # 一键全流程同步
├─ notes/
│   ├─ daily/              # 每日打卡笔记
│   └─ problems/           # 单题题解文档
├─ assets/                 # 本地截图临时目录（已 gitignore）
└─ NOTES_INDEX.md          # 自动生成的笔记索引
```

## 日常刷题工作流

1. `python main.py` 打开主菜单；
2. 选【新建今日笔记】自动生成本日打卡 md；
3. 选【新建题目笔记】输入题号名称生成题解模板；
4. 写题解，把截图丢进 `assets/`；
5. 选【上传图片并替换文档链接】一键上传并替换；
6. 选【一键同步 GitHub】自动提交推送。

## 安全说明

- OSS AccessKey 一律通过环境变量或本地密钥文件提供，代码仓库不落盘；
- `.gitignore` 已忽略 `config/secret.py`、`config/.env`、`assets/` 下图片与 Python 缓存；
- Git 操作使用参数化调用，提交信息不会引发 shell 注入。

## 后续路线图

- 二期：接入 DeepSeek API，自动生成思路/复杂度分析、每日总结、Python→Go 转换；
- 三期：笔记向量化，搭建私有 RAG 刷题知识库问答；
- 其他：Streamlit Web 界面、代码沙箱运行样例、批量导出 PDF。
