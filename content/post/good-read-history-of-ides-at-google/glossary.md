# 术语表 / Glossary

英中对照，覆盖本文核心技术与组织术语。

| 英文 | 中文 | 说明 |
|------|------|------|
| **IDE (Integrated Development Environment)** | 集成开发环境 | 集合代码编辑、build、debug、版本控制的工具 |
| **monorepo** | 单一代码仓 | 整个公司或大项目所有代码放在同一个仓库中（如 Google 的 google3） |
| **google3** | google3 | Google 内部对主 monorepo 的代号 |
| **Cider** | Cider | "Cloud IDE + r"。Google 内部自研的 web-based 编辑器，2013 年前后诞生 |
| **Cider V** | Cider V | Cider 的下一代，前端切换为 VSCode，2021 年开 beta，2023 年成为 80% 默认 IDE |
| **Bazel** | Bazel | Google 开源的 build system，源自内部 Blaze |
| **Starlark** | Starlark | Bazel 的配置语言，Python 子集，由 Le Brun 等人主导设计 |
| **LSP (Language Server Protocol)** | 语言服务器协议 | Microsoft 提出的协议，让 IDE 与语言工具解耦，Cider 在引入 LSP 后才真正具备 IDE 能力 |
| **Language Server** | 语言服务器 | 实现 LSP 的后端，提供 code completion、go-to-definition、find-references 等能力 |
| **Code Search** | 代码搜索 | Google 内部的全公司代码搜索工具 |
| **Code Review** | 代码评审 | Cider V 一大杀手锏：把评审注释内联显示在编辑器里 |
| **Code Completion** | 代码补全 | LSP 提供的能力之一；2023 年后 Google 用 AI 强化 |
| **Smart Paste** | 智能粘贴 | Google AI feature：根据上下文自动调整粘贴的代码 |
| **20% Time** | 20% 时间 | Google 文化：员工可花 20% 时间做主项目之外的探索 |
| **Peer Bonus** | 同事奖金 | Google 内部互相奖励小额现金的机制，鼓励社区贡献 |
| **Language Graph** | 语言图 | Cider 后端的核心数据结构，把每个 identifier 关联到类型和引用，全 monorepo 范围 |
| **Incremental Indexing** | 增量索引 | 每次提交只更新语言图中受影响的部分，而非重算 |
| **Historical Snapshot** | 历史快照 | Cider 允许每个工程师在"上次 sync 时间点"的代码版本上工作 |
| **Local Changes Overlay** | 本地修改叠加 | 在历史快照上叠加用户尚未提交的修改，形成"当前工作视图" |
| **Frontend / Backend** | 前端 / 后端 | Cider 架构中 frontend 是浏览器里的编辑器界面，backend 跑在 Google 数据中心 |
| **VSCode (Visual Studio Code)** | Visual Studio Code | 微软开源的编辑器，基于 Electron + Monaco |
| **Monaco Editor** | Monaco 编辑器 | VSCode 核心的代码编辑组件，可以独立嵌入网页 |
| **VSCode Extension** | VSCode 扩展 | VSCode 的插件系统，Cider V 上有 ~100 个 Google 内部扩展 |
| **Fork** | 分叉 | 从开源项目派生一个本地版本；Cider V 维护了一个 VSCode 的内部 fork |
| **Upstream Sync** | 上游同步 | 每月把 VSCode 主线的更新合并进 Cider V 的 fork |
| **Local Hacks** | 本地补丁 | fork 与上游的差异；Cider V 团队主动减少 local hacks |
| **Presubmit Check** | 提交前检查 | Google 内部强制的 CI 检查，每次 PR 提交前自动跑 |
| **Refactoring Tool** | 重构工具 | 自动化的代码改写工具，Le Brun 之前的工作领域之一 |
| **Linter / Formatter** | linter / 格式化工具 | 静态检查与代码格式化，Google 内部强制统一 |
| **PR (Pull Request)** | 合并请求 | 提交代码变更的标准方式 |
| **Tech Lead** | 技术负责人 | Le Brun 在 2020 年成为 Cider 团队的 tech lead 之一 |
| **Platform Engineering** | 平台工程 | 内部基础设施工程，提供给应用团队复用的工具与平台 |
| **Code Owner** | 代码所有者 | Google 的 OWNERS 文件机制，规定哪些人有权批准某段代码的变更 |
| **Visibility** | 可见性 | Bazel 的概念：某个 library 可以被哪些 target 引用 |
| **Leverage** | 杠杆 | 文章核心结论：standard tooling creates leverage |
