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
- 四期 Web 可视化界面 `web/`（Streamlit）：笔记浏览与管理、刷题统计看板、AI 增强可视化、RAG 知识库问答、一键同步与配置体检，功能对齐命令行
- Streamlit 社区云在线部署：https://mengl-0-leetcode-notes-auto-webapp-jjgrdx.streamlit.app/
- requirements.txt 增加 web 依赖声明：streamlit（核心）/ pandas；plotly 改为可选点缀
- 界面明暗主题：`.streamlit/config.toml` 原生 `[theme.light]` / `[theme.dark]` 双配色表；初始自动跟随操作系统明暗偏好，用户可通过右上角 ⋮ → Settings → Theme 自定义（仅存于自己的浏览器）

### Changed（2026-10-15 界面布局重构 · 毕设展示向）
- 侧栏：刷题统计封装为带边框卡片（加「刷题统计」小标题），与导航之间加分隔线；导航菜单文字精简（笔记/看板/AI/问答/同步）；明暗模式提示移到侧栏底部改为小字备注
- 浏览页：头部左右分栏，说明文字居左、`st.segmented_control` 视图切换居右；筛选改单行三栏（搜索框带占位提示、难度、时间）且标签隐藏，筛选下小字显示「共 N 篇｜筛选后 N 篇」；空筛选结果给友好提示不留白
- 题目元信息：难度/复习次数/首次记录/标签收纳进单个 `st.container(border=True)` 卡片，横向均分；难度与标签用 `st.badge` 样式呈现
- 笔记正文：标题层级统一降级（# / ## → ###，页面主标题为题目名）；思路/代码/复盘等长小节默认折叠为 `st.expander`；模板占位小节（待补充）隐藏；头部元信息引用行降级为小字，原题链接移到正文底部小字辅助展示；图片限宽居中（三栏布局实现），前后留白
- 主题：主色改沉稳蓝 `#2f6db3`，浅/暗双配色区分页面背景与卡片底色，代码块统一深色底；字体显式 `sans-serif`
- 约束落实：全程仅用 Streamlit 原生组件，未引入第三方 UI 库、未写自定义 CSS、无动画

### Fixed（2026-10-15 harness 改动修复）
- **P1** 明暗主题策略纠正：移除钉死的 `base = "light"` 与侧栏应用级「🌙 暗色模式」开关——该开关改的是进程级全局配置，线上共享实例会波及所有访客；现改为初始跟随系统、个人自定义走原生 Settings → Theme 菜单
- **P1** 笔记图片显示恢复：同步后的笔记图片链接已替换为 OSS 外链，此前"外链一律隐藏"导致正文图片空白；现外链图片正常渲染，仅文字展示路径保留密钥/桶名脱敏
- **P2** 主题配置失效项修正：`font = "sans serif"` 为非法取值（被 Streamlit 忽略），已移除改用默认字体；补充 `baseRadius = "medium"` 统一圆角观感
- **P2** 界面美化：明暗双配色表对齐 GitHub 阅读配色、主色统一为柔和红、侧栏保留题解/打卡/连击轻量总览

### Fixed（2026-10-15 界面优化）
- **P1** 笔记正文里的结构标记（`<!-- weather-start -->` 等）被当普通文本渲染出来：渲染前统一剥离 HTML 注释
- **P1** 笔记中的本地图片（相对路径 `../../assets/*.png`）无法显示：按笔记所在目录解析后用原生 `st.image` 渲染，图床外链仍保持脱敏提示
- **P1** 「刷题统计看板」每周趋势导致整页崩溃：`resample("W-SUN").size` 是方法，须写作 `size()`；原 `.size.rename(...)` 抛 `AttributeError: 'function' object has no attribute 'rename'`
- **P1** 「刷题统计看板」按题号定位报 `NameError`：补上缺失的 `from core import notes_io`
- **P2** 图表迁移到 Streamlit 原生 `st.line_chart` / `st.bar_chart`（随明暗主题自动换色）；plotly 难度环形图降级为「装了才用」的可选点缀

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
