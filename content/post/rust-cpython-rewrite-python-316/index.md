---
title: "Rust 正式进入 CPython：Python 3.16 将迎来 36 年来最大的底层语言变革"
description: "从 JIT 编译器到 Rust 重写核心模块，CPython 正在经历自诞生以来最激进的性能与安全革命。这不只是换一门语言的事。"
date: 2026-05-08
slug: "rust-cpython-rewrite-python-316"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Python
    - Rust
    - 编译器
    - 开源生态
draft: false
---

## 引言：一场酝酿了 36 年的手术

CPython——Python 语言的参考实现——自 1990 年诞生以来，一直用 C 语言编写。这不是偶然选择：C 提供了与操作系统的零距离接触、可预测的性能、以及跨平台编译的便利。但 36 年过去了，C 的内存安全问题从「可接受的代价」变成了「不可忽视的系统性风险」。

2026 年 4 月，Python 核心团队发布了「Rust for CPython」进展更新，正式确认 **Python 3.16 将引入 Rust 编写的核心扩展模块**。与此同时，Python 3.15 的 JIT 编译器已经在 macOS AArch64 上实现了 11-12% 的性能提升。两条战线同时推进，CPython 正在经历自诞生以来最激进的底层变革。

## 技术路线图：两条平行赛道

### 赛道一：JIT 编译器（Python 3.15，2025 年底）

Python 3.15 的 JIT 编译器进展超出预期，多个目标提前达成：

| 平台 | 性能提升 | 原定目标 | 实际达成时间 |
|------|---------|---------|------------|
| macOS AArch64 | 11-12% | 3.16 (10%) | 3.15 提前一年 |
| x86_64 Linux | 5-6% | 3.15 (5%) | 提前数月 |

关键技术突破包括三个方面：

**1. 从区域编译到追踪编译的范式切换**

JIT 前端从基于区域（region-based）的编译方式重写为追踪式（tracing）JIT，将 JIT 代码覆盖率提升了 50%。追踪式 JIT 的核心思想是：不预先编译整个函数，而是观察实际运行的热路径，只编译真正被执行的代码序列。

**2. 双调度表机制**

为了在追踪和正常执行之间切换，团队设计了双调度表：一张用于正常执行，一张用于追踪。只需一条追踪指令，避免了解释器代码膨胀。追踪模式仅比特化解释器慢 3-5 倍——对于收集信息的阶段来说，这是可接受的开销。

**3. 引用计数消除**

通过移除每条指令的引用计数递减分支，JIT 获得了显著的性能提升。这是一个 Python 特有的优化：CPython 的引用计数垃圾回收机制意味着每次对象操作都要更新计数器，JIT 可以通过分析证明某些对象不会在中途被释放，从而省略这些操作。

### 赛道二：Rust 集成（Python 3.16，2027 年中）

Rust 进入 CPython 的路线图已经明确：

```
2026.03 ✅ 构建系统适配完成（所有 CI 平台通过）
2026.04 → 内部 Rust API 设计
2026.05 → 确定首个 Rust 实现的扩展模块 + PyCon US 冲刺
2026.06 → 开始撰写 PEP
2026.07 → PEP 提交
2027.05 → 3.16 beta 1
```

几个关键设计决策值得关注：

- **内部 API 优先**：Rust API 最初将是内部的（internal），不对第三方暴露。稳定化需要另一个 PEP。
- **单模块试点**：3.16 只会选择一个扩展模块用 Rust 重写，验证整个工具链。
- **构建系统已就绪**：Rust 编译已经在所有 CPython CI 平台上通过，这是最大的工程障碍之一。

## 为什么是现在？三个时代背景

### 1. 内存安全已成国家级议题

2024 年美国白宫 ONCD 发布报告，明确建议关键基础设施软件转向内存安全语言。Python 作为 AI/ML 基础设施的核心运行时，其解释器的内存安全问题不再是学术讨论。

### 2. 企业赞助的退潮倒逼社区自治

值得注意的是，CPython JIT 团队在 2025 年失去了主要企业赞助商（Faster CPython 项目的 Microsoft 支持）。但团队不仅没有停滞，反而通过社区化运营实现了加速：JIT 优化器的活跃贡献者从 2 人增长到 4 人，11 位贡献者参与了解释器的 JIT 友好化改造。

这揭示了一个反直觉的事实：**企业赞助的退出有时反而释放了技术决策的自由度**。当不需要向某个公司的技术路线对齐时，社区可以做出更大胆的架构决策。

### 3. 36 年代码库的惯性需要新工具打破

CPython 的代码库经过 36 年增长，已经积累了大量的 C 语言技术债务。Stan Ulbrych 对 CPython 代码库的可视化分析（使用 cloc 工具跨越 1392 个提交）揭示了代码膨胀的长期趋势。Rust 提供了一条渐进式重写路径：不需要一次性重写，可以模块化地替换。

## 生态影响：涟漪将远超 CPython 本身

### 对 C 扩展生态的冲击

CPython 引入 Rust 后，第三方扩展库将面临选择：继续用 C 编写（通过 stable ABI），还是转向 Rust（通过新的内部 API）。PyO3 项目已经为 Rust-Python 绑定积累了多年经验，但当 CPython 自身都用 Rust 时，生态的引力将发生根本性转移。

### 对其他语言运行时的示范效应

Ruby 已经在 YJIT 中使用 Rust，Node.js 的某些组件也在探索 Rust 重写。CPython 的官方背书将加速这一趋势：**用 Rust 重写语言运行时的关键路径**将从实验性选择变成行业最佳实践。

### 对 Python 性能叙事的改写

Python「太慢」的叙事延续了二十年。JIT + Rust 的双管齐下可能在 3-5 年内将 CPython 的性能提升 2-3 倍。虽然仍然无法与编译型语言竞争，但对于「够用就好」的大量工作负载，性能差距将缩小到不足以成为迁移理由。

## 风险与不确定性

**PEP 审批风险**：Python 的 PEP 流程以严谨（有时是缓慢）著称。Rust 集成的 PEP 可能面临关于构建复杂度、贡献者门槛、以及跨平台兼容性的激烈辩论。

**社区分裂风险**：要求 CPython 贡献者同时掌握 C 和 Rust 会提高门槛。虽然 Rust API 最初是内部的，但长期来看，维护一个双语言代码库需要额外的认知负担。

**时间表风险**：从 3.15 推迟到 3.16 已经是一次延期。如果 PEP 审批过程中出现重大分歧，可能进一步推迟。

## 判断

CPython 引入 Rust 不是「if」而是「when」的问题。构建系统已就绪、社区共识已形成、外部政策压力已到位——三个条件同时满足。真正的问题是速度：如果 3.16 如期交付，Python 将成为第一个在官方运行时中引入 Rust 的 Top 3 编程语言，这本身就是一个里程碑事件。

对于 Python 开发者，现在的行动建议很明确：**开始关注 PyO3，跟踪 3.16 的 PEP 进展，在新项目的 C 扩展中评估 Rust 替代方案**。变革的列车已经离站。

## 参考链接

- [Rust for CPython Progress Update April 2026](https://blog.python.org/2026/04/rust-for-cpython-2026-04/) — Python Insider
- [Python 3.15's JIT is now back on track](https://blog.python.org/2026/03/jit-on-track/) — Python Insider / Ken Jin
- [CPython: 36 Years of Source Code](https://blog.python.org/2026/03/cpython-codebase-growth/) — Python Insider / Stan Ulbrych
- [White House ONCD Report on Memory Safety](https://www.whitehouse.gov/oncd/briefing-room/2024/02/26/press-release-technical-report/) — 2024
- [PyO3 Project](https://pyo3.rs/) — Rust bindings for Python
