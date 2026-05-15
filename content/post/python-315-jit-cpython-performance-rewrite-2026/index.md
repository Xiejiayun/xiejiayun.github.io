---
title: "Python 3.15 的 JIT 重启与 CPython 性能重铸：一门 36 岁的语言开始'认真'了"
description: "Python 3.15 beta 1 把搁置已久的 copy-and-patch JIT 重新拉回轨道，与并行推进的 free-threaded（无 GIL）模式、CPython 关键模块的系统化替换工程一起，构成 CPython 36 年历史上最深的一次内部重构。本文拆解 JIT 路线图、free-threaded 落地现实、以及 Python 性能工程组合拳在 2026 年到底意味着什么。"
date: 2026-05-15
slug: "python-315-jit-cpython-performance-rewrite-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - Python
    - CPython
    - JIT
    - free-threaded
    - PEP 703
    - 编程语言
    - 性能工程
draft: false
---

> **核心观点**：Python 3.15 不只是又一个版本号。它是 CPython 自 1989 年由 Guido 在阿姆斯特丹动笔以来，**第一次同时推进三条根本性变革** —— copy-and-patch JIT 重启上线、free-threaded（PEP 703 / 无 GIL）从实验进入正式可选模式、以及 CPython 内部模块的工程化替换。这三条线如果在 3.16-3.18 全部落地，Python 的性能基线会上一个台阶，但同时也意味着"Python 是慢但够用的胶水语言"这个 30 年的身份认同正在解构。生态的代价不会便宜。

## 一、为什么这个版本节点值得专门写一篇

PSF（Python Software Foundation）2026 年 4 月底发布了 Python 3.15.0 beta 1，紧随其后是 Python 3.14.5 的最终维护版。这两个发布看上去平淡，但 Python Insider 博客上几条短消息透露了真信号：

- 《[Python 3.15's JIT is now back on track](https://pythoninsider.blogspot.com/)》—— JIT 路线重回主线
- 《Rust for CPython Progress Update April 2026》—— 用更安全的实现语言重写关键模块
- 《CPython: 36 Years of Source Code》—— PSF 罕见地做了一次 36 年代码考古
- 《Join the Python Security Response Team!》—— 安全响应专项扩编

把这四件事放在一起，画面就清晰了：**Python 核心团队在 2026 年正式从"维护语言"转向"重铸运行时"**。

这不是社区驱动的小修小补，而是 PSF + Microsoft Faster CPython 团队（Mark Shannon、Brandt Bucher、Ken Jin 等）+ Meta + Google 一起出钱出人的工程项目。预算和人力都是过去 5 年里最高。

## 二、JIT 的来龙去脉：从 Python 3.13 实验到 3.15 回归

### 2.1 copy-and-patch JIT 是什么

Python 3.13 在 2024 年第一次合入了实验性 JIT，技术路线是 Brandt Bucher 等人提出的 **copy-and-patch JIT**：

- 不像 V8 / HotSpot 那样自己写一个完整 codegen
- 而是**预编译**一份"模板字节码"，把每个字节码对应到一段编译好的机器码 stencil
- 运行时把 stencil 拼起来 + 把立即数 patch 进去，生成最终机器码
- 实现复杂度极低，但生成代码的质量也不如经典 JIT

3.13 的 JIT 把"几何平均"性能提升只压到 ~3-5%，作为 30 年来 CPython 第一个 in-tree JIT 这个数字其实可以接受。但社区反响平平："还不如 PyPy"几乎成为了固定吐槽。

### 2.2 3.14 的中场休息

在 Python 3.14 里 JIT 团队做了一个出人意料的决定：**把 JIT 改成默认关闭**，并且**暂停了部分优化合入**。原因是核心团队意识到 copy-and-patch 缺少一些关键基础设施：

1. **没有完整的 type guards 框架**：3.13 的 JIT 只能优化字节码层，类型推断有限
2. **没有 inline caching 与 JIT 的合作**：CPython 的 PEP 659 specializing interpreter 在解释器层做 IC，JIT 没有继承
3. **没有 OSR (on-stack replacement)**：长循环跑解释器版本一直跑到完，没法热切换

这三件事不补全，JIT 永远只能是"图灵完备但不实用"。3.14 的暂停是务实的。

### 2.3 3.15 的"回到正轨"

3.15 beta 1 的 What's New 里关于 JIT 的描述只有寥寥几行，但读懂的人能看出含金量：

- **Tier 2 IR 接入完成**：CPython 现在有了完整的"字节码 → tier 1 specialized → tier 2 IR → 机器码"四层
- **Type guards 与 deopt 路径打通**：JIT 可以在猜错类型时优雅回退到解释器
- **限定 benchmark 提升 15-25%**：在 PyPerformance / pyperf 上"几何平均"重回 10% 以上，部分单测达 30%+
- **默认仍是 OFF**，但维护者期望 **3.16 默认 ON**

把 3.13 → 3.14 → 3.15 看作一条曲线：先尝试、退后整理、再以更扎实的姿态推进。这是工程上正确的做法，但商业叙事上很难讲。这也是为什么社区的关注度反而下降了 —— 真正的工作发生在听不见的地方。

### 2.4 为什么不直接用 PyPy / Pyston / Cinder

合理的疑问。答案三层：

1. **PyPy 的兼容性问题**：CPython 扩展（NumPy、PyTorch C 扩展、PostgreSQL psycopg）在 PyPy 上要么不工作，要么慢得多。20 年来 PyPy 没解决这个问题。
2. **Cinder/Pyston 是 Meta/Anaconda 的内部分叉**：技术上很强，但维护节奏脱离 CPython 主线
3. **copy-and-patch 的优势是"in-tree"**：它和 CPython 的所有底层假设兼容，扩展模块零修改

JIT 路线的本质选择是 **"妥协的兼容性 vs 极致的性能"**，而 Python 在 2024 年正式选了兼容性优先。这是务实主义对完美主义的胜利。

## 三、free-threaded：无 GIL 模式从实验到生产

### 3.1 PEP 703 的回顾

PEP 703 在 2023 年通过：让 CPython 支持 **可选关闭 GIL** 的构建模式。3.13 第一次有了 `python3.13t`（free-threaded 二进制），但被明确标注为"实验"。

3.14、3.15 的进展：

- **3.14**：所有标准库已经过 free-threaded 审计，关键 C 扩展（asyncio、ssl、sqlite3）通过线程安全测试
- **3.15**：free-threaded 模式从"实验"升级为"**正式可选**"。维护者 Sam Gross 公开说，3.16 可能开始考虑作为默认
- **包生态**：NumPy 2.x、PyTorch 2.6+、SciPy 1.14+ 已经原生支持 free-threaded
- **性能现实**：单线程任务 free-threaded 比 GIL 版本慢 5-10%（细粒度锁开销），但 4-16 核扩展场景能达到 3-12 倍加速

### 3.2 为什么这件事比 JIT 还重要

JIT 让 Python 代码跑得快**一个常数倍**（10-30%）。free-threaded 让 Python 代码**真正用上现代多核 CPU**。后者是数量级的、根本性的性能升级。

但代价是 30 年的多线程 Python 代码、几乎所有依赖 GIL 的隐式线程安全假设、C 扩展的引用计数语义 —— 全都要重新审视。

举一个具体的例子：

```python
# 在 GIL 版本下，下面的代码"碰巧"是线程安全的
counter = 0
def worker():
    global counter
    for _ in range(1000000):
        counter += 1

# 在 free-threaded 模式下，counter 的最终值是不可预测的
# 因为 += 不再是原子操作
```

这段代码在 GIL 时代的实际部署里到处都是。一旦 free-threaded 成为默认，所有这种"隐性正确"的代码都会变成 bug。

### 3.3 生态的"代价单"

| 受影响的项目类型 | 修复难度 | 主要工作 |
|------------------|----------|----------|
| 纯 Python 业务代码 | 低 | 加锁 / 改用 threading 原语 / 改用 multiprocessing |
| C 扩展（NumPy 类） | 中 | 重新审计引用计数、缓冲区协议 |
| C 扩展（asyncio 桥接） | 高 | 事件循环 + 线程安全的复杂交互 |
| Cython 生成代码 | 中-高 | Cython 自身需要更新代码生成 |
| pybind11 / PyO3 | 中 | 已经基本完成迁移 |

PyO3（Rust ↔ Python 绑定）的进度最好 —— Rust 自身的所有权语义和 free-threaded 语义天然兼容。这也是为什么 Python 核心团队同时在推进"CPython 关键模块用更安全的语言重写"。

## 四、"用更安全的实现语言写 CPython 内部":一场静默的工程

Python Insider 4 月发了一篇低调但重要的文章：[Rust for CPython Progress Update April 2026](https://pythoninsider.blogspot.com/)。要点：

1. CPython 已经接受 PEP 7XX 草案：允许在标准库 C 扩展中使用更内存安全的实现语言
2. 第一个里程碑：把 `_random`、`_md5`、`_sha256`、`_zoneinfo` 这几个底层模块的实现从 C 改写
3. 不会替换 CPython 解释器核心 —— `Python/ceval.c` 仍然是 C，因为它需要和 C ABI 紧密耦合
4. 构建系统改造：CPython 构建图加入 Cargo 编译步骤，发行版打包者需要 toolchain 配合

这件事的意义大于技术本身。Python 是开源世界最重要的"胶水语言"之一，它的核心实现语言**第一次出现非 C 选项**。这是 1989 年 Guido 第一行 C 代码以来的破例。

对中国开发者特别要注意的一条：很多发行版（CentOS Stream、Alpine、麒麟、UOS）的 Python 包是 distros 团队自己重新打包的。**新的构建系统要求会迫使这些发行版升级他们的 toolchain**，否则就要长期维护 fork。这是一笔不小的工程债。

## 五、为什么是 2026 年集中爆发

把时间线拉长看：

- 2018 年 Guido 退休（"BDFL 时代结束"）
- 2020 年 PEP 8016 通过，建立了 5 人 Steering Council 治理
- 2021-2022 年 Microsoft Faster CPython 团队成立（Mark Shannon 主导）
- 2023 年 PEP 703 通过、PEP 659 落地、Tier 1 specializer 上线
- 2024 年 3.13 实验性 JIT + 实验性 free-threaded
- 2025-2026 年三条线齐步推进

这不是巧合，是治理结构 + 资金 + 工程方法论一起到位后的必然爆发。Python 终于有了一个**专业的运行时团队**，按照 V8 / HotSpot 同等工程严肃度在做事。

## 六、对开发者的实际影响

### 6.1 现在（2026 年 5-12 月）

- 还**不要**在生产环境用 3.15 beta，等 10 月稳定版
- 但**应该**在 CI 里加一条 3.15 测试矩阵
- 关注你用到的 C 扩展（NumPy、PyTorch、Polars、duckdb）是否声明了 free-threaded 兼容性

### 6.2 中期（2027 年 / Python 3.16）

- 评估关键服务在 free-threaded 模式下的实际加速比 —— 不是所有 workload 都受益
- 重新审视你的代码里**隐式依赖 GIL 串行化**的部分（共享字典、共享集合、模块级状态）
- 如果你维护 C 扩展，开始 free-threaded 兼容性测试

### 6.3 长期（2028+）

- **GIL 默认关闭**是大概率事件，但有过渡期
- Python 与 Cython / PyO3 / nanobind 的边界会重新划分 —— "性能敏感模块用绑定语言写"会变成标准实践
- 如果你的团队还在做"Python 慢就用 C 重写关键路径"，可以重新评估：3.15+ 的 JIT + free-threaded 可能让纯 Python 实现就够用

## 七、被忽视的代价：发行版分裂风险

CPython 的多模式（GIL vs free-threaded、有 JIT vs 无 JIT、纯 C vs 含 Rust 模块）组合一旦稳定下来，Linux 发行版面对一个新麻烦：**到底默认提供哪个版本？**

- Ubuntu 26.04 LTS 已经预告会同时打包 `python3.15`（GIL）和 `python3.15t`（free-threaded）
- Debian 在邮件列表里讨论是否要把 free-threaded 设为副包
- RHEL 还在观望，倾向保守
- Alpine 因为 musl 与 Rust 编译的边角问题，进度最慢

不同发行版的默认选择会直接影响开发者的"Python 是什么"的心智模型。如果 Ubuntu 26.04 默认是 free-threaded、但 RHEL 还是 GIL —— 同一段代码在两边的并发行为完全不同。这是 Python 30 年里第一次出现"**同一个版本号下行为可能本质不同**"的局面。

## 八、结语

Python 在 2026 年的故事可以一句话总结：**它正在变成一门"它原本设计时不打算成为"的语言**。

Guido 1989 年写下第一行代码时，目标是教学和脚本。今天 Python 是 AI 训练首选语言、是世界最流行的编程语言（按 TIOBE / PYPL）、是 NumPy/PyTorch/Pandas 生态的宿主。这个错配在 30 年里被"够用就行"的工程妥协掩盖。但 AI 时代的算力需求把这个错配重新撕开了。

Python 3.15 的 JIT 回归、PEP 703 的 free-threaded、CPython 内部模块的工程化替换 —— 三条线本质上回答同一个问题："**Python 能不能在不丢失自己生态的前提下，把性能提升一个台阶？**"

我的判断：能，但需要 3 年（3.15 → 3.18）。这 3 年里，每一个用 Python 的工程师都需要重新学一些东西。这不是坏事 —— 这是一门语言"长大"的代价。

## 参考来源

1. Python Insider — [Python 3.15.0 beta 1 is here!](https://pythoninsider.blogspot.com/)
2. Python Insider — Python 3.15's JIT is now back on track
3. Python Insider — Rust for CPython Progress Update April 2026
4. Python Insider — CPython: 36 Years of Source Code
5. PEP 659 — Specializing Adaptive Interpreter
6. PEP 703 — Making the Global Interpreter Lock Optional in CPython
7. PEP 744 — JIT Compilation
8. Mark Shannon — Faster CPython 项目年度报告（Microsoft Tech Blog）
9. Sam Gross — free-threaded benchmarks（2026 PyCon 演讲幻灯）
10. PyO3 / nanobind / pybind11 各项目 free-threaded 兼容性 changelog
