---
title: "CPython 走向系统语言混编：3.16 PEP 路线图首次允许 C 之外的第二门系统语言"
description: "Python 3.16 的 PEP 路线图正在被悄悄改写——Rust for CPython 项目把第一个 Rust 实现的扩展模块送入 alpha。这不是技术升级，是治理体制的一次试探：当 CPython 36 年的 C 单栈遇上 30 年的 Rust 浪潮，开源世界要回答的问题是——一个语言的标准实现，能不能允许两种语言并存？"
date: 2026-05-18
slug: "cpython-316-system-language-mixin-governance-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - CPython
    - 编程语言
    - 开源治理
    - PEP
    - 语言演化
draft: false
---

## 36 年单栈的裂缝

2026 年 4 月 8 日，Python 官方博客上发布了一篇看似平淡的 "Rust for CPython Progress Update"。它把第一个 Rust 模块进入 CPython 主干的目标版本，从原定的 3.15 推迟到了 **3.16**。

这不是又一篇社区进度更新。它实际宣告：**Python 3.16 将成为 CPython 36 年历史上，第一个允许第二种系统语言出现在自身代码库的版本**。

讨论了三年的"用 Rust 改写 CPython 内部模块"提案，正在沿着一份明确的时间表推进：

| 月份 | 路线图任务 |
| --- | --- |
| 2026-03 | 构建系统改造完成，CPython CI 全平台绿灯 |
| 2026-04 | 启动 Rust 内部 API 设计 |
| 2026-05 | 内部 API 设计定稿 + PyConUS 集训 + 选定第一个被 Rust 重写的扩展模块 |
| 2026-06 | 开始撰写正式 PEP |
| 2026-07 | PEP 草案定稿，提交进入社区讨论 |
| 2027-05 | Python 3.16 beta 1 — 第一个含 Rust 代码的版本 |

更早一些，2026 年 3 月 Python Insider 发表的 *CPython: 36 Years of Source Code* 把这个时间点的历史意义讲透：从 1989 年 Guido 写下 ceval.c 第一行，到 2025 年底 CPython 主干超过 **220 万行**代码，36 年里这套代码库始终是一种语言——C89/C99 with selective C11，没有任何例外。

## 为什么是现在？

要理解 Python 决定引入 Rust 的真实原因，必须先看 CPython 这几年承受的三股压力。

### 压力 1：内存安全债越积越深

CPython 的 C 代码长期是 *memory-safe issue* 的重灾区。仅 2024–2025 两年，已知 CVE 中超过 **70%** 与 CPython 解释器或标准库 C 扩展中的整数溢出、缓冲区错误、引用计数错误有关。

Microsoft、Google 等核心赞助方多次表态：**安全审计 C 代码的成本，已经超过用 Rust 重写部分热点模块的成本**。Linux 内核已经在 2022 年合并了 Rust 子系统；Android、Chromium、Firefox 都在做同样的事。Python 是少数仍然坚守 C 单栈的"前 10 大开源项目"。

### 压力 2：性能瓶颈与多核并发

PEP 703（去 GIL）落地后，3.13–3.16 这几个版本的 CPython 必须同时处理三个性能维度：

1. JIT（PEP 744，3.15 才重新回到正轨——参见 Python Insider 2026-03 的 "Python 3.15's JIT is now back on track"）。
2. Free-threaded mode（PEP 703，无 GIL）。
3. Subinterpreters（PEP 734，独立子解释器）。

这三个维度叠加，**C 代码中关于线程局部存储、原子操作、不可变状态的复杂度爆炸**。CPython 核心团队多次承认：以现有 C 代码风格继续演化，没人敢碰这部分。Rust 的所有权模型几乎是为这种场景设计的。

### 压力 3：贡献者生态老龄化

Python 的核心贡献者中位年龄逐年上升，新一代系统编程人才几乎不学 C。Rust 在大学课程、开源社区、招聘市场上的吸引力数量级高于 C。**让 CPython 接受 Rust，本质上是 Python 生态对未来 20 年人才结构的一次主动适配**。

## 治理层面的真正难题

技术上引入 Rust 并不难——Linux 已经趟过路。但 Python 面对的问题更复杂：它**不是一个项目，是一种语言的参考实现**。这带来五个治理层难题：

### 难题 1：ABI 与 ABI 稳定性承诺

CPython 暴露给 C 扩展的 ABI（Python C API）是无数下游库的基石——NumPy、Pillow、lxml、cryptography、PyTorch、TensorFlow 全靠它。引入 Rust 后：

- 是用 Rust 复刻完全相同的 C ABI 给外部用？还是创造一个 Rust-native API？
- Rust 在 CPython 内部使用，是否会通过 **`extern "C"`** 维持稳定 ABI？还是仅作为实现细节？

Rust for CPython 团队目前明确表态：**Rust API 在 PEP 通过之前保持完全内部，不对外暴露**。这是务实的：先消化内部成本，再决定是否对外。

### 难题 2：跨平台编译复杂度

Python 自称在"几乎一切"上运行——从 ARM Linux、Windows、macOS，到 z/OS、Android、Emscripten、OpenWRT、FreeBSD、AIX，甚至偏远的 RISC-V 嵌入式板。Rust 工具链虽然有 `rustc`+`cargo`，但要做到与 CPython 同等的平台覆盖度，还差至少 5–10 个 tier-3 平台。

Rust for CPython 项目用了 6 个月把 CPython 主干在 Rust 启用模式下的 CI 跑绿——这是**真正的工程地基**。

### 难题 3：构建系统耦合

CPython 的 `configure` 脚本、Makefile、setup.py、PEP 517 后端是一座 30 年的"自适应大教堂"。把 Cargo 嵌进来需要：

```text
                ┌──────────────────────────┐
                │     Python Source Tree   │
                ├──────────────────────────┤
                │   Python files (.py)     │
                │   C source (.c .h)       │
                │   ASM (limited)          │
       NEW ───► │   Rust source (.rs)      │
                │   Cargo.toml + lockfile  │
                └─────────────┬────────────┘
                              │
                ┌─────────────▼────────────┐
                │  configure + Makefile    │  ◄── 既有
                │  pyconfig.h              │
                │  Cargo subbuild driver   │  ◄── 新增
                └─────────────┬────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │      libpython.so /      │
                │      python.exe          │
                └──────────────────────────┘
```

这套结构必须让"没有 Rust 工具链的发行版"依然能在不依赖 Rust 的子集上构建 CPython（至少给嵌入式场景留路）——这是一个**未解的工程承诺**。

### 难题 4：发行版打包者的态度

Debian、Fedora、Alpine、Arch 这些发行版的 Python 打包者，几十年来已经习惯了"只装 GCC 就能编 CPython"的世界。引入 Rust 意味着：

- 每个发行版的 build chroot 必须新增 `rustc`、`cargo`、可能的 `libgit2`。
- 每个 Linux 发行版的安全响应小组要新增 Rust 漏洞处理能力。
- 嵌入式发行版（OpenWRT、Yocto、Buildroot）原本可以用 cross-GCC 编 Python，现在需要 cross-Rust——cross-Rust 在 tier-3 平台上仍然不成熟。

Debian Python 团队在 2025 年的 DebConf 已经多次公开质疑这个决策。这是一场拉锯战。

### 难题 5：心理与文化迁移

Guido 已经退休，新的指导委员会（Steering Council）每年选举一次。把 Rust 写进 CPython 这种级别的变更，需要**所有现任及历任核心贡献者达成大致共识**——这种共识本身就是一道难关。CPython 核心团队 2025 年底的内部投票显示：支持 Rust 引入的比例为 **62%**，反对 23%，弃权 15%。这是"通过但不令人放心"的票数。

## 行业对照：Linux、Chromium、Firefox 怎么做的

| 项目 | 接入 Rust 时间 | 受影响代码占比 | 治理路径 | 教训 |
| --- | --- | --- | --- | --- |
| Linux Kernel | 2022（v6.1） | < 1% | Rust for Linux 自治子系统，可选编译 | 入主线后社区争议持续，2024 年 Asahi 维护者撤出事件揭示文化摩擦 |
| Chromium | 2023 | 增量新代码逐步 Rust 化 | 内部决定，无社区公投 | 商业项目治理简单，开源不可复制 |
| Firefox | 2017（Stylo） | ~10% | Mozilla 内部 + Servo 复用 | 成功但代价大（Servo 后期被裁） |
| Android | 2021 | 系统服务增量 Rust 化 | Google 主导，无外部讨论 | 内存漏洞数下降 52% |
| **CPython** | **2027（计划）** | **拟从 1 个扩展模块起步** | PEP 协商 + 全员共识 | **未发生，全员紧张** |

Python 走的是**最慢但最透明**的路径。Linux 选了"先合入，再讨论"，结果是合入两年后还在拍桌子；Chromium、Firefox 走商业路径，没有可比性。Python 选了"先讨论、再合入"，这意味着 PEP 阶段每一条质疑都会被记录在案——好处是民主，坏处是任何阻力都会推迟时间表（3.15 已经被砍掉一次）。

## 给开发者和企业的提前准备

CPython 3.16 距离 GA 还有约 18 个月。无论 PEP 是否最终通过，下游生态都需要提前布局：

### 对扩展库作者（NumPy/PyTorch/cryptography/...）

- **关注 PEP 早期草案**：第一个被替换的内部模块极可能是 `_pickle`、`_io`、`hashlib`、`_ssl` 其中之一。这些都和 binary serialization、加密相关——是性能与安全双瓶颈。
- **审视自己库里调用的 CPython 私有 API**。Rust 重写过程中，部分 `_Py_xxx` 这种"非正式但被滥用"的内部符号可能消失。
- **考虑 PyO3 路线**。如果你自己的库未来要写新代码，PyO3（Python-Rust 互操作框架）将获得官方支持，不再是"实验性"。

### 对 CI/CD 和包管理工具链

- 准备好同时支持 `cibuildwheel` 在带/不带 Rust 的环境下都工作。
- 镜像 Rust 工具链：内部 PyPI 镜像、企业 Artifactory 都需要镜像 `crates.io`。
- 对 Alpine / musl-based 容器要特别关注 Rust 在 musl 上的成熟度（仍有 tier-2 限制）。

### 对企业 Python 用户

- **Python 3.13–3.15 是过渡期**。如果你在用 3.10/3.11 的 LTS 心态，需要意识到 3.16 之后升级路径会变化。
- 关注 Linux 发行版的 Python 打包政策——RHEL 10.x、Ubuntu 28.04 LTS 是否会切换到含 Rust 的 CPython 编译版本，关系到企业 IT 支持周期。

## 这是 Python 还是新的 Python？

最深的问题不是技术的。CPython 36 年来都是"Guido 风格"的工程文化：保守、可读性优先、避免聪明、宁慢勿乱。Rust 文化是另一个极端：高度类型化、范型遍布、宏即语言。两种文化在同一个代码库里能否共存？

Rust for CPython 团队的几位主导者（Emma Smith 等）已经反复说明：**Rust 部分必须遵守 Python 自己的工程审美**——不允许过度炫技、命名风格统一、复杂泛型回避。这是一个聪明的策略，但是否能在 50 个 Rust 模块之后还守得住？没有人敢打包票。

退一步说，即便 PEP 在 2026 年下半年顺利通过、3.16 顺利在 2027 年 5 月发布，**这都只是开始**。真正的考验在 3.17、3.18：第二个、第三个 Rust 模块是不是会出现？外部贡献者怎么训练？什么时候开始有 Rust-only 的核心代码？什么时候 Rust API 会公开？

Python 走的这条路慢、稳、痛苦，但它把所有的设计取舍放在台面上讨论。这种透明度本身，可能比"Rust 是否进入 CPython"更有价值——它给所有 30 年以上历史的开源项目示范了一件事：**一个语言的标准实现，可以在不背叛初心的前提下，承认自己需要被改写**。

## 引用来源

- Python Insider — "Rust for CPython Progress Update April 2026"：https://blog.python.org/2026/04/rust-for-cpython-2026-04/
- Python Insider — "CPython: 36 Years of Source Code"：https://blog.python.org/2026/03/cpython-codebase-growth/
- Python Insider — "Python 3.15's JIT is now back on track"：https://blog.python.org/2026/03/jit-on-track/
- Python Discourse — "pre-PEP: Rust for CPython"：https://discuss.python.org/t/pre-pep-rust-for-cpython/104906
- Python Discourse — "Rust for CPython progress April 2026"：https://discuss.python.org/t/rust-for-cpython-progress-update-april-2026/106895
- PEP 703 — "Making the GIL Optional in CPython"：https://peps.python.org/pep-0703/
- PEP 734 — "Multiple Interpreters in the Stdlib"：https://peps.python.org/pep-0734/
- PEP 744 — "JIT Compilation"：https://peps.python.org/pep-0744/
- Rust-for-CPython GitHub — issues tagged api-design：https://github.com/Rust-for-CPython/cpython/issues?q=label%3Aapi-design
- Linux Kernel — Rust for Linux：https://rust-for-linux.com/
- Android Security Blog — "Memory Safety in Android"：https://security.googleblog.com/
- Mozilla Hacks — "Quantum / Stylo / Servo retrospectives"：https://hacks.mozilla.org/
- PyO3 项目：https://pyo3.rs/
