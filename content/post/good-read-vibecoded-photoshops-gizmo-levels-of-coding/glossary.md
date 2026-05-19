# 术语表 · Vibecoded Photoshops

| 英文 | 中文 | 简要解释 |
|------|------|---------|
| vibecoding | "凭感觉编程" | Andrej Karpathy 2025 年提出的词，指完全依赖 LLM 接受其输出而不做深入审查的开发模式 |
| vibecoded | "感觉出来的"（贬义指控） | 在 2026 年沦为对任何"看起来太成熟、又用了 AI"的项目的指责 |
| slop | 垃圾产出 | AI 生成、未经审查、低质量的内容总称 |
| prompt-and-pray | "提示词然后祈祷" | 不做验证就部署 AI 输出的开发流程 |
| Level 1 / L1 | Typing 层 | gizmo 框架：语法、模板、记忆型工作 |
| Level 2 / L2 | Verifying 层 | 测试、harness、对"几乎对"和"真正对"的辨别能力 |
| Level 3 / L3 | Deciding 层 | 架构判断、不可逆 trade-off、决定要做什么和不做什么 |
| harness | 验证套件 / 验证夹具 | 包围着代码的测试、参考实现、回归框架的整体 |
| four-way bit-identical verification | 四路位元一致验证 | gizmo SoulPlayer 中"四套实现必须输出完全相同的字节才允许出货" |
| reference implementation | 参考实现 | 用更慢但更易理解的方式实现同一逻辑，作为 truth oracle |
| memory-faithful shadow | 内存忠实影子 | 在高级语言里精确模拟低级硬件内存语义的实现，用于交叉验证 |
| emitted asm | 生成的汇编 | 由 pipeline 自动产生而非手写的汇编代码 |
| demoscene | 演示场（地下计算机艺术亚文化） | 始于 1980s 的欧洲，用极小的可执行文件做出声光体验 |
| Farbrausch | 德国著名 demoscene 组织 | 以 64k 演示和 .kkrieger（96KB 完整 3D FPS 游戏）闻名 |
| .kkrieger | 96KB 的 3D FPS 游戏 | Farbrausch 2004 年作品，演示了 procedural 内容生成的极限 |
| werkkzeug | Farbrausch 内部工具链 | 整个 demoscene 流派"工具即作品"的代表 |
| 64k intro | 64KB 演示作品 | demoscene 的经典 size category，整个可执行文件 ≤ 64KB |
| C=64 / Commodore 64 | 1982 年家用电脑 | 8 位 6510 CPU，64KB RAM，本文 SoulPlayer 的目标平台 |
| 6510 assembly | 6510 汇编 | Commodore 64 的 CPU 指令集，6502 的变体 |
| SoulPlayer | gizmo 的 C64 transformer 项目 | 在原版 C64 上跑一个 25,000 参数 int8 transformer |
| transformer (small) | 微型变换器模型 | 这里指 ~25K 参数、2 层 4 头、int8 量化的极简实现 |
| accusation epistemics | 指控的认识论 | 对"作出指控"这一话语行为应该满足的认知标准 |
| meta-critique | 元批评 | 不是反驳具体内容，而是批评对方的批评方式 |
| falsifier | 证伪条件 | Popper 意义上的"什么证据能让一个命题被推翻" |
| calibration | 校准 | 一个判断者过去预测的"正确率与他自己声称的置信度的一致程度" |
| essential vs accidental complexity | 本质复杂度 vs 偶然复杂度 | Brooks《Mythical Man-Month》分类，gizmo L1 ≈ accidental，L2/L3 ≈ essential |
| chaos test | 混沌测试 | Netflix 风格的故障注入测试，纯 L2 工作 |
| post-mortem | 事故复盘 | 重大事件之后的系统化反思，包含 L2 和 L3 |
| punch down | 居高临下打击 | 强势方对弱势方使用的攻击；gizmo 拒绝对 prompt-and-pray 用户这样做 |
| gatekeeping | 守门行为 | 用各种标准筛选谁"真正属于"某个群体 |
| neurodivergent | 神经多样性 | 包括 ADHD、自闭谱系等非典型神经类型 |
| Tics | 抽动症 | 一种神经发育条件 |
| receipts | 证据 | 网络俚语，指证明某事的具体材料 |
| Hacker News (HN) | 知名科技讨论社区 | YC 旗下，本文原帖讨论达 345 条 |
| Project Glasswing | Anthropic Mythos 的早期访问项目 | 邀请安全研究团队测试前沿安全模型 |
| Speed vs Scale loop | Tuhin Nair 的资深开发者价值框架 | 与 L1/L2/L3 在不同维度上互补 |
| Emacsification of software | "软件的 Emacs 化" | Thomas Ptacek 提出，指 AI 让每个人都能定制原生应用 |
| posture > tool | "姿势胜于工具" | Addy Osmani 关于 AI 学习"决定输出的是姿势，不是工具" |
