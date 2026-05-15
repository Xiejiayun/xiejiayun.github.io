# 概念卡片 · matklad: Learning Software Architecture

12 张可独立阅读的核心概念卡片。每张卡片：**定义 → 出处 → 在 rust-analyzer 中的体现 → 工程含义**。

---

## 卡片 1｜Conway 定律（Conway's Law）

- **定义**：系统的结构最终镜像设计该系统的组织的沟通结构。
- **出处**：Melvin Conway，1968 年论文《How Do Committees Invent?》
- **在 rust-analyzer 中**：贡献者拓扑（少数深度高手 + 大量周末战士）直接决定了\"核心脊梁 + `catch_unwind` 隔离的功能层\"双层架构。
- **工程含义**：不要试图设计与组织拓扑相反的架构——它会先被拉回去，然后让你赔上半年时间。

---

## 卡片 2｜激励场（Field of Incentives）

- **定义**：matklad 用于解释\"为什么不同环境产出的代码形态不同\"的物理学比喻——代码是被组织内的激励\"场\"塑形的。
- **出处**：本文，原文 \"the field of incentives that compels people to produce the software\"。
- **在 rust-analyzer 中**：\"必须吸引能改借用检查器的人\"这个激励，导致\"无 rustc 依赖、稳定版编译、几秒测试\"等一系列具体决策。
- **工程含义**：争论\"应该用什么架构\"之前，先问\"我的激励场是什么\"。激励场不变，架构怎么改都会被拉回去。

---

## 卡片 3｜乐观合并（Optimistic Merging）

- **定义**：先合并贡献者代码，再修；信任贡献者；让代码进来比让代码完美更重要。
- **出处**：Pieter Hintjens（ZeroMQ 作者），《Social Architecture》。
- **在 rust-analyzer 中**：feature PR 的合并门槛仅为\"happy path 跑通 + 有测试\"。
- **工程含义**：在 OSS / 长尾贡献者社区，提高门槛 ≠ 提高质量；门槛过高会让贡献流停滞，反而让代码因缺人维护而腐烂。

---

## 卡片 4｜`catch_unwind` 隔离

- **定义**：Rust 标准库的 `std::panic::catch_unwind` 用于捕获 panic（崩溃）边界，使 panic 不外溢。
- **出处**：Rust std API。
- **在 rust-analyzer 中**：每个 IDE 功能（重构、补全、高亮、悬浮）外层都用 `catch_unwind` 包裹，单功能崩溃不影响其他功能。
- **工程含义**：\"质量不一致\"不是 bug，是设计选择——只要崩溃半径可控、不污染数据。

---

## 卡片 5｜不可变快照（Immutable Snapshot）

- **定义**：所有读取操作发生在数据库 / 索引的一个不可变快照上，并发读不会污染写、写不会污染读。
- **出处**：源自数据库 MVCC（多版本并发控制）传统。
- **在 rust-analyzer 中**：每个 IDE 功能在一个不可变的代码索引快照上运行，崩溃不能往回污染主索引。
- **工程含义**：把\"运行时错误隔离\"翻译成一条 ACID 风格的不变式——这是 matklad 把\"乐观合并\"做安全的物理基础。

---

## 卡片 6｜核心脊梁 vs. 功能层（Core Spine vs. Feature Layer）

- **定义**：matklad 用于描述 rust-analyzer 双层架构的术语——\"脊梁\"承载数据结构、并发模型、调度器；\"功能层\"承载具体 IDE 行为。
- **在 rust-analyzer 中**：脊梁代码：matklad 自己 + 少数核心维护者，质量极挑剔；功能层：周末战士，质量门槛低。
- **工程含义**：不要给所有代码定一个质量门槛。明确分层，分层定门槛。

---

## 卡片 7｜TIGER_STYLE

- **定义**：TigerBeetle 数据库的代码风格指南，强调安全 > 性能 > 开发体验，包含一系列像\"所有循环必须有上界\"\"不允许递归\"等硬性约束。
- **出处**：[TigerBeetle/docs/TIGER_STYLE.md](https://github.com/tigerbeetle/tigerbeetle/blob/main/docs/TIGER_STYLE.md)。
- **关键洞察**：matklad 在本文里说 TIGER_STYLE 真正的力量\"不是规则本身，是让这些规则能成立的社会语境\"。
- **工程含义**：硬性规则 + 没有相应社会共识 = 团队内部反弹 = 规则被绕过。

---

## 卡片 8｜函数式核心 + 命令式外壳（Functional Core / Imperative Shell）

- **定义**：把纯函数式逻辑放在内核，把所有 I/O、副作用、可变状态放在外壳。
- **出处**：Gary Bernhardt 2012 talk [Boundaries](https://www.destroyallsoftware.com/talks/boundaries)。matklad 在本文称其触发了他的\"元思考\"。
- **在 rust-analyzer 中**：分析器内核是纯函数（输入快照 → 输出分析结果），LSP 服务器外壳处理状态。
- **工程含义**：可测试性、可推理性、并发性三者同时改善。

---

## 卡片 9｜Speedrun The Four Stages of Grief

- **定义**：matklad 戏称\"接受激励结构\"是要 speedrun 完悲伤的五个阶段（否认 → 愤怒 → 讨价还价 → 抑郁 → 接受）。
- **在 rust-analyzer 中**：matklad 接受了\"必须在 LSP 协议限制内工作\"\"必须支持 Rust 全语言\"等约束，没有试图重新发明 LSP。
- **工程含义**：屈服于激励结构不可耻，可耻的是花十年才屈服。

---

## 卡片 10｜未来的不便定理（Future Happens in the Least Convenient Manner）

- **定义**：matklad 原创警句——你做架构决策时假设的未来与真实发生的未来之间会以最不便的方式偏离。
- **在 rust-analyzer 中**：本来是\"实验项目，经验回传 rustc\"；结果变成了 Rust 生态关键基础设施，要永久维护。
- **工程含义**：屈服于激励结构时，保留 escape hatch；今天为\"周末战士\"设计的代码，明天可能是基础设施。

---

## 卡片 11｜测试是\"萨满式蛇油\"

- **定义**：matklad 在 [How to Test](https://matklad.github.io/2021/05/31/how-to-test.html) 中对\"测试金字塔\"\"TDD 教条\"\"mock 一切\"等流行教条的批判性术语。
- **在 rust-analyzer 中**：他强烈倾向于\"集成测试 + 大量小测试用例\"而非\"单元测试金字塔\"。
- **工程含义**：测试是为了**发现错误**和**支持重构**——不是为了取悦审查员或满足覆盖率工具。

---

## 卡片 12｜博尔赫斯式书单

- **定义**：matklad 引用博尔赫斯式的伪短篇文学，说\"那本真正讲清楚软件架构的书只存在于博尔赫斯的伪短篇里\"。
- **隐含**：所有声称是\"软件架构圣经\"的书都是过度自信的产物——架构需要在项目中被打疼才学会。
- **工程含义**：读书单只是起点；要让一个真实项目把你打疼一次，否则书是没用的。
