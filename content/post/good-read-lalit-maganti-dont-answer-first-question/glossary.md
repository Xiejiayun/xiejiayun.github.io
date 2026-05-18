# 术语表 · Don't Answer the First Question

> 25 个英中对照术语，覆盖 Perfetto 生态、性能工程、工程文化、平台思维四个层面。

## A. Perfetto / 性能工程生态

| 英文 | 中文 | 一句话解释 |
|---|---|---|
| Perfetto | Perfetto | Google 开发的系统级性能追踪与分析工具链；Android 上 "系统追踪" 功能背后的事实标准。 |
| Trace | 追踪 / 追踪数据 | 一段时间内系统所有事件的高保真录像；事件级、按需触发。 |
| Trace splitting | 追踪文件切分 | 把一个长 trace 文件物理切分成多个较小文件的需求——本文中作为"用户提的伪需求"的范例。 |
| Periodic trace snapshots | 周期性追踪快照 | Perfetto 的实际推荐方案：不收一段长录像，而是反复收很多段短录像。 |
| Trace merge | 追踪合并 | 把多个 trace 文件合并成一个完整 trace 的功能——Perfetto 团队"等了很久才做对" 的代表案例。 |
| Frame rate | 帧率 | UI 渲染的核心指标；每秒成功渲染的帧数。 |
| Frame drops | 掉帧 | 应该在某个截止时间前渲染完但没渲染完的帧。 |
| Startup | 启动 | 应用启动到首帧/首交互之间的耗时；移动端性能工程的核心战场之一。 |
| Memory profiling | 内存剖析 | 追踪内存分配与释放的过程，用于发现泄漏与过度分配。 |
| Power profiling | 功耗剖析 | 测量与归因设备能耗的过程；移动端独有的关键性能维度。 |

## B. 软件设计 / 平台思维

| 英文 | 中文 | 一句话解释 |
|---|---|---|
| XY problem | XY 问题 | 用户实际想解决 X，但只问了 Y 的问题模式；本文论证 XY 思维不够深入。 |
| Tool philosophy | 工具哲学 | 一个工具的设计意图、世界观与边界——常常需要维护者反复传授。 |
| Tool shape | 工具的形状 | Lalit 使用的隐喻：每个工具都有一个"形状"，反映它的数据模型与使用方式。 |
| Feature request | 功能请求 | 用户提出的新功能需求——本文反复强调它常常是"问题表述"，而不是"问题"。 |
| Plugin API | 插件 API | 让外部代码以受控方式扩展工具的接口；Perfetto 用一年时间把 ad-hoc UI hack 重做成了 plugin API。 |
| Technical debt | 技术债 | 当前的设计妥协对未来开发能力造成的代价；本文 UI 自定义案例的核心代价。 |
| Foundational software | 基础软件 | 大量上层项目依赖的底层工具/平台；改错代价极高，因此需要"先等"。 |

## C. 工程文化 / 职业发展

| 英文 | 中文 | 一句话解释 |
|---|---|---|
| Staff engineer / Senior Staff Engineer | 资深工程师 / 高级资深工程师 | Google/大厂职级体系里的资深技术领导，不走管理路线。Lalit 的当前职级。 |
| Promo Committee | 晋升委员会 | 大厂内部用于评估晋升的跨团队评审组织；本文论证"反问"和"等待"这两种行为如何在 promo 文化下生存。 |
| Outside the spotlight | 远离聚光灯 | Lalit 自创的概念：staff 工程师可以不靠演讲/可见度而通过工具维护与团队赋能产生影响。 |
| Fixit / Fixit week | Fixit 周 | 暂停 roadmap、专门修 bug 的一段集中时间；Lalit 写过专文。 |

## D. AI 时代相关

| 英文 | 中文 | 一句话解释 |
|---|---|---|
| LLM-as-Support | LLM 即客服 | 用大语言模型替代人工客服/工程支持的产品趋势。 |
| RAG (Retrieval-Augmented Generation) | 检索增强生成 | 在生成回答之前先检索相关文档的 LLM 系统架构。 |
| Agentic workflow | 智能体工作流 | LLM 自主调用工具、规划多步动作的工作流；近期成本爆炸的主要驱动。 |
| Slop | 噪声 / 低质量输出 | 描述 LLM 大量生成但质量低下的内容；本文引申为"AI 自动应答把信号替换成噪声"。 |

---

## 推荐使用方式

1. **新人入职**：A + B 是必读，C 选读，D 跳读；
2. **跨团队对话**：B + C 用于和 PM/manager 解释你的工作；
3. **AI 工具决策**：在你部署 AI 客服之前，把 D 一节交给团队过一遍。

> 编辑：xiejiayun.github.io，2026-05-18。
