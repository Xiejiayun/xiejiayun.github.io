# 术语表 · matklad: Learning Software Architecture

英中对照，30 条。

| 英文 / 原文 | 中文 | 简要说明 |
|---|---|---|
| Software Architecture | 软件架构 | 系统的高层组织方式；matklad 强调它"不如社会问题重要"。 |
| Conway's Law | Conway 定律 | 系统结构镜像组织沟通结构（Melvin Conway, 1968）。 |
| Field of Incentives | 激励场 | matklad 用于描述塑造代码形态的组织内激励"力场"。 |
| Optimistic Merging | 乐观合并 | 先合并贡献者代码再修；Pieter Hintjens 提出。 |
| Catch Unwind | 捕获展开 | Rust 标准库 `std::panic::catch_unwind`，用于隔离 panic 边界。 |
| Panic | panic / 崩溃 | Rust 的运行时崩溃机制（区别于 C++ 异常或 Go panic）。 |
| Immutable Snapshot | 不可变快照 | 索引/数据库的某一时点冻结视图，并发读写隔离。 |
| Borrow Checker | 借用检查器 | Rust 编译器中验证内存所有权与生命周期的核心模块。 |
| Trait Resolution | 特征求解 | Rust 编译器决定使用哪个 trait 实现的过程。 |
| Macro Expansion | 宏展开 | 把 `macro_rules!` 或过程宏代码转换为标准 Rust AST。 |
| Name Resolution | 名字解析 | 编译器把标识符映射回声明的过程。 |
| Type Inference | 类型推断 | 编译器从上下文推导未显式声明的类型。 |
| LSP (Language Server Protocol) | 语言服务器协议 | Microsoft 提出的 IDE 后端通讯协议；rust-analyzer 实现它。 |
| Rust-Analyzer | rust-analyzer | Rust 官方 IDE 引擎，matklad 创立者。 |
| RustC | rustc | Rust 官方编译器；matklad 让 rust-analyzer 故意不依赖它。 |
| TigerBeetle | 老虎甲虫数据库 | 高吞吐金融账本数据库，用 Zig 编写，matklad 是核心维护者。 |
| TIGER_STYLE | TigerStyle 风格指南 | TigerBeetle 的代码风格文档，安全 > 性能 > DX。 |
| Core Spine | 核心脊梁 | matklad 术语，指系统中承载基础设施的核心代码层。 |
| Feature Layer | 功能层 | matklad 术语，指承载具体用户可见功能的边缘代码层。 |
| Weekend Warrior | 周末战士 | matklad 对\"业余时间贡献者\"的称呼，OSS 项目主力来源之一。 |
| Functional Core | 函数式核心 | Gary Bernhardt 提出的设计模式之一半，纯函数层。 |
| Imperative Shell | 命令式外壳 | 与函数式核心配对，承载所有 I/O、副作用。 |
| Boundaries (talk) | 边界（演讲） | Gary Bernhardt 2012 talk，函数式核心 / 命令式外壳奠基。 |
| Ninja (build system) | Ninja 构建系统 | Evan Martin 的构建系统，被 Chrome / Android / Meson 等使用。 |
| Make-Believe | 假装游戏 | 字面\"做相信\"，matklad 用以形容大学软件架构课。 |
| Speedrun | 速通 | 游戏术语，matklad 借用以形容\"快速接受激励结构现实\"。 |
| Stages of Grief | 悲伤五阶段 | Kübler-Ross 模型；matklad 借喻\"接受激励\"的心理过程。 |
| Optimistic Concurrency | 乐观并发 | 与\"乐观合并\"共享同一直觉的数据库术语；先操作后验证。 |
| MVCC | 多版本并发控制 | 不可变快照背后的数据库经典模型。 |
| Borges | 博尔赫斯 | 阿根廷作家，以伪百科 / 伪书目著名；matklad 用以暗指\"软件架构圣经\"是虚构。 |
