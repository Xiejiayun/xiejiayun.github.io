# 概念卡片 / Concept Cards

适用于 spaced repetition 学习（如 Anki）。每张卡片 1 个核心概念 + 1 段解释 + 1 个延伸思考点。

---

## 卡片 1：Jeff Dean 的 IDE 命题

**正面**：2011 年 Google 是否应该有一个统一 IDE？Jeff Dean 怎么回答？

**反面**：他的回答是"不能"。原话："Trying to get a group of developers to all agree on a common editor is a recipe for unhappiness... In the end, it doesn't matter that much."

**延伸**：这个判断在 2011 年是对的（强制无效），但 12 年后被"软性证伪"——一个真正更好的工具会自然形成统一。

---

## 卡片 2：Cider 名字的由来

**正面**：Google 内部 Cloud IDE 为什么叫 Cider？

**反面**："Cloud IDE" 加一个 r 让名字更好记。

**延伸**：这种"实用主义命名"是 Google 内部产品很典型的风格。

---

## 卡片 3：Cider 的初始用户群

**正面**：Cider 最早是被谁广泛使用的？

**反面**：technical writers——他们用 Cider 修 markdown 文件的 typo，因为不想搞 git workflow。

**延伸**：很多伟大的开发者工具，起点都是"看似无关紧要"的小场景。

---

## 卡片 4：传统 IDE 在 Google 规模下为什么失效

**正面**：为什么 Vim/IntelliJ 在 google3 上吃力？

**反面**：传统 IDE 假设源代码、build metadata、索引、分析全部在本地。Google 的代码量（数十亿行）和提交频率（每秒数十次）让这个假设彻底失效。

**延伸**：这是"重客户端 → 强后端"架构反转的根源。

---

## 卡片 5：Cider 后端的核心——Language Graph

**正面**：Cider 后端维护一个什么数据结构？为什么贵？

**反面**：Language Graph——把每个 identifier 关联到类型和引用，覆盖整个 monorepo。它必须在每次 commit 后增量更新，并支持任意历史快照上的查询。

**延伸**：这种"全局静态分析作为服务"是今天 AI Coding Agent 后端架构的雏形。

---

## 卡片 6：历史快照 + 本地修改叠加

**正面**：Cider 工程师在编辑器里看到的是哪个版本的代码？

**反面**：他们上次 sync 时间点的全 monorepo 快照，叠加上他们自己本地未提交的修改。

**延伸**：这种"snapshot + delta"模式是版本控制系统的本质，但 Cider 把它从 git 扩展到了 IDE 语义层。

---

## 卡片 7：Cider V 的前端选择

**正面**：Cider 团队为什么在 2020 年决定用 VSCode 作前端？

**反面**：三个原因：(1) VSCode 是 web-native 的 Electron + Monaco 架构；(2) language-agnostic 且 extensible；(3) 大量 feature request 在 VSCode 里早已 solved。

**延伸**：这是一个"复用上游生态、专注差异化后端"的经典 platform 决策。

---

## 卡片 8：Cider V 的 Fork 策略

**正面**：Cider V 维护一个 VSCode 内部 fork，他们怎么处理 upstream 关系？

**反面**：每月同步上游；主动减少 local hacks；尽可能贡献 patch 回 upstream。

**延伸**：这是"软 fork"——不是分叉走开，而是被动跟随主线 + 主动反哺。多数公司的 fork 失败都因为忽略这一点。

---

## 卡片 9：Cider V 的迁移规模

**正面**：从 Cider 1.0 迁到 Cider V 花了多久？团队多大？

**反面**：2020 开始 → 2021 年 5000 人 open beta → 2023 年 80% 默认 IDE。前端团队约 12 人。

**延伸**：平台工程的回报周期是十年级的，不是季度级的。

---

## 卡片 10：内部扩展生态

**正面**：Cider V 上有多少 Google 内部扩展？意味着什么？

**反面**：约 100 个内部扩展。意味着各业务团队开始为自己特殊需求做 IDE 集成，而不是要求 Cider 团队加 feature。

**延伸**：标准平台的最大价值不在自身功能，而在它能解锁"长尾创新"。

---

## 卡片 11：2023 年的 AI 集成

**正面**：Cider V 在 2023 年起加了哪些 AI features？

**反面**：Resolving Code Review Comments with ML、Smart Paste、AI code completion。

**延伸**：AI 能在 Google 内部快速落地，前提是 2013–2020 年间建好的统一 IDE 平台。

---

## 卡片 12：最终结论——杠杆

**正面**：Le Brun 整篇文章的一句话总结是什么？

**反面**："In the end, standard tooling creates leverage."（最终，标准化的工具创造杠杆）

**延伸**：这句话适用范围远远超出 IDE——所有 platform engineering 故事的本质都是杠杆论。
