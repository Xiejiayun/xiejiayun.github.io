---
title: "重跑 Ken Thompson 的'信任之信任'：现代供应链时代，编译器后门为何更可怕也更可解"
description: "有人在 2026 年用 Ken Thompson 1984 年图灵奖演讲里的方法，真实地构造了一个会自我复制的编译器后门。本文从这次复刻出发，讨论可重现构建、bootstrappable build、与 LLM 时代供应链信任的下一步。"
date: 2026-05-01
slug: "trusting-trust-modern-supply-chain-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 软件供应链
    - 编译器
    - 可重现构建
    - 信任之信任
    - 安全
    - 开源
draft: false
---

## 1984 → 2026：一个被引用了四十年的演讲，终于被认真复刻

Ken Thompson 在 1984 年图灵奖演讲 *Reflections on Trusting Trust* 里描述过一个让所有 CS 学生既兴奋又困惑的构造：**一个被植入后门的编译器，能在编译自身时把后门继承下去，因此源码里看不到任何痕迹**。这是个思想实验，过去四十年被引用过无数次，但**真正动手把它在现代工具链上跑一遍**的工程师并不多。

2026 年初，一篇社区博客 *Running the "Reflections on Trusting Trust" Compiler* 在 Hacker News 与 Lobsters 上同时上了首页。作者拿现代 C 工具链——一个 patched 过的 tcc 与一个修改后的 gcc——把 Thompson 当年的两步攻击完整地再现了一遍：第一步，往 login 程序里注入"特定密码进入"的后门；第二步，让编译器在自编译时识别出"我正在编译我自己"，再次注入第一步的攻击代码。**演示视频里那个用魔法密码登录干净源码编译出的系统的瞬间，比任何 CTF 题都更刺骨。**

> 2024 年的 XZ Utils 后门事件让全行业短暂震惊了一下。但 XZ 攻击者只是利用了构建脚本的复杂性——和 Thompson 的攻击相比，那是初级班作业。Thompson 的攻击是**让源代码审计原则失效**：你看到的源码是干净的，构建系统是干净的，但**编译出的二进制不是**。

本文借这次复刻，讨论三件事：为什么这个 1984 年的攻击在今天**更现实而非更过时**、可重现构建（reproducible builds）和 bootstrappable build 走到哪一步、以及 LLM 自动化代码生成正在如何**重新定义**这个问题。

---

## 一、为什么 Thompson 攻击在 2026 年更现实

四十年前听 Thompson 演讲的人，会觉得这是个"理论上可行但工程上不太可能"的事——因为当时编译器是少数几个人维护的、容易被审视的、二进制大小有限的工件。今天反过来：

| 维度 | 1984 | 2026 |
|------|------|------|
| 主流 C/C++ 编译器代码量 | ~50K 行 | LLVM 1500 万+ 行，GCC 1000 万+ 行 |
| 工具链组件 | 编译器、链接器、libc | + LSP、formatter、static analyzer、AI 补全、build system、container base image |
| 二进制分发占比 | 约 30%（多数仍源码编译） | >95%（pip wheel、apt deb、container 镜像） |
| 开发者审视的"信任根" | 自己安装的 gcc | docker pull / brew install / pip install 链下来的不知多少层 |

也就是说，**Thompson 当年要对付的"自举链"是一条短链；今天的自举链是一张图**。一个现代 Python 开发者输入 `pip install requests` 之后，背后涉及 PyPI、CDN、wheel build、setuptools、CPython 解释器、底层 libc、Linux 内核、容器镜像、CI runner、Git 镜像……每一层都可以被替换，每一层的"源码-二进制对应"关系都很难独立验证。

更糟的是，**工具链组件被插入"非语法层"代码生成**的比例急剧上升：构建期代码生成器（protobuf、bindgen、SQL 编译器）、链接期 LTO 优化、加载期 JIT，每一层都给"二进制不忠于源码"提供了合法借口。

如果一个有动机的国家级对手要做 Thompson 攻击的现代版本，**它甚至不需要修改 GCC 源码**——只要污染一个被广泛信任的 builder 镜像、或一个 LSP server、或一个流行的 cargo plugin，就能在几亿台机器上得到长期持久化。

## 二、可重现构建：从理想主义到工程现实

Debian 的 *Reproducible Builds* 项目从 2013 年开始推动一个目标：**任何人，从相同的源码与相同的工具链版本出发，应该构建出字节级完全相同的二进制**。这听上去像废话，但十年前实际能做到的不到 30%。

到 2026 年初，这个数字是：

- **Debian 主仓 90%+ 的包**可重现构建
- **Arch Linux 官方仓库 85%+** 可重现
- **Tails / Whonix 等隐私发行版**强制要求 100% 可重现
- **Bazel、Nix、Bitbake**作为构建系统层面的"可重现先天友好"的方案，被 Google、Meta、汽车行业广泛采用
- **Go 工具链**自 1.21 起原生支持 reproducible binaries
- **Rust** 在 2025 年的 RFC 路线图把 reproducible builds 列为 stable target

这是十年里软件工程社区少数几个**真正显著的安全工程进步**。它的意义在于：**即便编译器被植入了 Thompson 后门，只要存在两条独立的工具链能够编译同一份源码并产出相同二进制，攻击就会被立即暴露**。

但可重现构建并不能直接破解 Thompson 攻击的最深层问题——**所有"独立工具链"最终都来自历史上某一个公共祖先**。这就是 bootstrappable build 项目要解决的问题。

## 三、Bootstrappable Build：把信任之信任问题"考古学化"

Guix 与 Bootstrappable Builds 项目（mes、stage0、live-bootstrap）做的事情，是把现代工具链的依赖图一路向下追溯到**几百字节的人类可审查的种子二进制**：

```
bash + glibc + gcc       (现代 Linux 用户态)
        │
        ▼
guile / bash 脚本
        │
        ▼
Mes (Mauer Eingebauter Schemer，~5000 行 C + Scheme)
        │
        ▼
M2-Planet / stage0-posix
        │
        ▼
hex0 (~ 510 字节，可手工逐字节审计的种子)
```

到 2026 年，从 hex0 一路 bootstrap 到完整 GCC + glibc 已经是 Guix 的官方 CI 任务，构建过程完全确定性。这意味着**在严格意义上，现代 Linux 系统第一次有了一个对 Thompson 攻击有数学等价反驳的"可信源"**——你可以选择信任 510 字节的 hex0（它能被人眼审计），剩下的全部由可重现的步骤推导出来。

主流操作系统离这个目标还很远：

| 系统 | 工具链信任根 | 距离可审计种子 |
|------|--------------|----------------|
| Guix System | hex0 (510B) | 已闭环 |
| NixOS | binary cache 信任，逐步 bootstrap 中 | 部分闭环 |
| Debian | snapshot.d.o + 可重现构建 | 高，但仍依赖历史 GCC 二进制 |
| 一般 Linux 发行版 | 信任发行版仓库 | 中 |
| macOS / Windows | 完全信任厂商 | 无 |
| 容器镜像（Alpine/Ubuntu base） | 信任 registry + 镜像 | 低 |

也就是说：**理论上 Thompson 攻击在 Guix 用户面前已经被关上**；但对绝大多数实际部署的系统，这个攻击面仍然是开着的。

## 四、LLM 时代：信任之信任的"第三次危机"

这次复刻博客发布的时间点很微妙——它正好赶上 AI 代码生成大规模介入工程实践的元年。我们必须严肃面对一个问题：

> **如果未来 30% 的 Linux 内核 patch、40% 的 npm 包、60% 的 prototype 代码由 LLM 生成或重写，那么"源码"作为审计单位的意义本身是否被稀释？**

LLM 在代码生成时引入的不是 Thompson 风格的精巧后门，而是另一种威胁：

1. **训练数据污染** → 模型在特定场景下系统性生成有缺陷模式（如 SSL 验证关闭、随机数熵不足）。
2. **prompt injection 通过工具调用执行**：LLM agent 写的 build script 引入隐蔽下载步骤。
3. **上下文窗口外的隐式依赖**：模型生成的代码引入了开发者从未注意到的 transitive dep。

更深一层：**当代码生成被 LLM 中介，"我读过这段源码所以我信任它"的工程文化将彻底崩溃**。审计要审的不再是源码，而是"提示词 + 模型版本 + RAG 内容 + 工具调用链"的完整可重现性——这是一个**比 Thompson 攻击大一个数量级的信任根问题**。

讽刺的是，**可重现构建的方法论几乎可以原封不动地搬到 LLM 流水线上**：固定模型 weights hash、固定 prompt、固定 RAG corpus snapshot、固定 tool 版本，要求"相同输入产出相同 patch"。这件事 Anthropic、OpenAI 等模型厂商目前都做得很差——大多数生产 API 不保证 deterministic，连 temperature=0 都不严格。

## 五、给工程团队的几条具体建议

1. **把"可重现构建"写进新项目的非功能性需求**。Go/Rust 项目几乎零成本；Node/Python 项目需要 lock 文件 + base image pinning + build tool determinism。
2. **production critical 系统至少使用两条独立来源的 base image** 做 diff verification。如果未来出现一次 Alpine 或 Ubuntu 镜像污染，你将庆幸这一点。
3. **关注 Sigstore / SLSA Level 3+ 的部署成熟度**。它们不解决 Thompson 攻击的根，但显著提升了篡改成本。
4. **AI 辅助编码的产物，必须像第三方依赖一样审视**。不要给 LLM 生成的代码"开绿色通道"——它的攻击面比手写代码大。
5. **对真正高敏感的项目（基础设施、密码学库）**，认真评估 Guix/Nix bootstrap 路径作为 CI 的一个 lane。即使不全量替换，也是一个独立的健康度信号。

## 六、结语：四十年没有过时的提醒

Thompson 1984 年演讲最后一句话是："**You can't trust code that you did not totally create yourself.**"

这句话曾经被当成一个浪漫的工程伦理宣言。但 2026 年它变成了一个具体的工程清单：**你信任的工具链在哪里？它的二进制可被多少独立路径推导？你的 AI 编码助手保留了多少决定性？**

这次复刻不是怀旧。它是把一个被忘了四十年的提醒重新放回桌上：在所有人都在讨论 LLM 革命、Agent 自治、AI infra 的 2026 年，**最古老的安全问题——"我手里拿到的二进制，到底是不是我看到的源码"——仍然是现代软件工程没有真正解决的问题**。可重现构建、bootstrappable build、确定性 LLM 流水线，是它在三个时代的三个回答。下一个答案，会属于把这三件事真的合在一起做的人。

---

### 参考资料

- Ken Thompson, *Reflections on Trusting Trust*, ACM Turing Award Lecture, 1984: <https://dl.acm.org/doi/10.1145/358198.358210>
- Reproducible Builds Project: <https://reproducible-builds.org/>
- Bootstrappable Builds Project & GNU Mes: <https://bootstrappable.org/> · <https://www.gnu.org/software/mes/>
- SLSA Framework v1.0: <https://slsa.dev/>
- David A. Wheeler, *Countering Trusting Trust through Diverse Double-Compiling (DDC)*, 2009: <https://dwheeler.com/trusting-trust/>
