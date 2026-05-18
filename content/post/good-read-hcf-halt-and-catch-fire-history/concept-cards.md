# 概念卡片：HCF 与 CPU 未文档化行为

> 配套 [《HCF 考古》](./index.md) 的关键概念速查卡

---

## 卡 1：HCF（Halt and Catch Fire）

**定义**：以三字母汇编助记符形式起名的虚构指令，后来在 Motorola 6800 上偶然找到了真实硅片对应物。1960 年代起源于 IBM System/360 程序员幽默；1977 年 12 月由 Gerry Wheeler 在 BYTE 杂志上正式命名 `$9D` 与 `$DD` 这两条 MC6800 未文档化指令。

**触发后果**：CPU 不再 fetch–decode–execute，PC 继续递增但所有读出的字节被丢弃。地址总线变成一根 16 位计数器，以时钟频率的一半（500 kHz @ 1 MHz）方波递增。中断无法救活，必须 RESET。

**为什么记住它**：它是"指令集 ≠ CPU 全行为"这一观念的最经典案例。

---

## 卡 2：HACOF（Motorola 内部代号）

**定义**：Motorola 内部对 6800 / 6802 上 0x9D/0xDD 这类指令的代号，1985 年由 Daniels & Bruce 在 *IEEE Design & Test of Computers* 上首次公开。

**为什么留下**：本来计划在 MC6802 设计时清掉，但产品工程团队发现这条指令可以作为 silicon bring-up 阶段的快速 RAM 扫描方法——于是没花成本清除它。这是设计 testability 的早期形态。

---

## 卡 3：illegal opcode（非法 opcode）

**定义**：在 ISA 上没有定义意义、但 CPU 仍然会"执行"出某种行为的字节模式。6800 上有 59 条这类字节模式（256 − 197）。在现代 x86 上有几千条。

**三种命运**：
1. 被 trap 成 `#UD`（undefined instruction exception）
2. 沉默成 NOP（如 6800 上的 0x14/0x15 大部分）
3. 进入 HCF 类状态机，需要 RESET

---

## 卡 4：F00F bug

**定义**：1994 年 Intel Pentium 上的 errata。指令字节 `F0 0F C7 C8`（即带 LOCK 前缀的 invalid CMPXCHG）会让 CPU 卡死在 cache line lock 上，要 reset 才能恢复。

**严重性**：在多用户系统（Linux/BSD/NT）里，任何普通用户都能让整台机器死机，等同于本地 DoS。

**修复方式**：操作系统把 IDT 标成只读，配合 trap handler 把这个字节序列在内核里拦住。是软件补硬件的一个经典案例。

---

## 卡 5：UD2（`0F 0B`）

**定义**：x86 上的"官方非法指令"。指令编码上保留为 explicitly invalid，触发后 CPU 抛 `#UD` 异常，控制权交给 trap handler。

**为什么需要它**：当软件检测到"不应该执行到这里"（unreachable code、assertion 失败、内联 panic 标记），用 UD2 比用其他方法更可靠——因为 ISA 保证它永远是非法的，未来 Intel/AMD 也不会把它分配给某条新指令。

**与 HCF 的对比**：HCF 是硬件层不受控的 halt，UD2 是受控的、软件可处理的 halt。HCF → UD2 是 50 年的 testability 哲学进化。

---

## 卡 6：Sandsifter

**定义**：Christopher Domas 在 Black Hat USA 2017 演示的 x86 指令模糊测试工具。通过系统性枚举字节模式 + 单步执行，能在真实 CPU 上发现未文档化的指令、隐藏的 model-specific register、未公开的处理器状态。

**遗产**：开启了一整代"指令集模糊测试"工具。AMD、Intel、ARM、RISC-V 都已经成为模糊测试的目标。HCF 在这个语境里被重新理解为：CPU 厂商可能在硅片上**今天还在**保留类似的 hidden state。

---

## 卡 7：BIST（Built-in Self-Test）

**定义**：内置自测电路。CPU 上电后由专门的硬件子模块跑一组测试向量，验证 RAM / Cache / 寄存器 / 数据通路是否工作。

**与 HCF 的关系**：Daniels & Bruce 1985 那篇论文的副标题就是 *Built-in self-test trends in Motorola microprocessors*——HCF 在他们的叙述里是 BIST 出现之前的"穷人版扫描"。今天的 CPU 上 BIST 通常占据 1–3% 的面积，是 silicon bring-up 与故障诊断的官方机制。

---

## 卡 8：Scan chain / DFT

**定义**：Design for Test（DFT）的核心机制。在 CPU 设计时把所有寄存器串成一条移位链，测试时可以从一个外部 JTAG 引脚把寄存器的值移进移出，确认每一级触发器都能正确翻转。

**为什么重要**：今天一颗现代 CPU 的所有内部状态几乎都能被 scan chain 读取，HCF 那种"地址总线作 16 位计数器"在 1980 年代是必要的，今天则完全被 scan chain + JTAG 取代。

---

## 卡 9：micro-op / 微操作

**定义**：从 Pentium Pro 开始，x86 内部不再直接执行 ISA 指令，而是把每条 x86 指令翻译成一系列 micro-ops（μops），由乱序后端调度。这意味着 ISA 与"硅片真实行为"之间又多了一层 firmware-ish 的转换。

**与 HCF 的关系**：现代 x86 不太可能像 6800 那样把地址总线直接打成方波——因为地址总线现在由 load/store queue 间接产生，不再是指令解码器直接控制。HCF 的物理表现形式因此基本绝迹，但"非文档化的微操作行为"反而更难审计。

---

## 卡 10：post-silicon validation（流片后验证）

**定义**：CPU 从晶圆厂出来后、在量产前，工程师需要对实际硅片做大量验证——确认 RTL 描述与硅片行为一致。这一阶段会跑数千万小时的随机指令流。

**与 HCF 的关系**：post-silicon 阶段最痛的是"发现一条 bug 但没法用任何官方机制 reproduce"。HCF 在 1980 年代是工程师的小工具；今天的 post-silicon 团队会用类似 sandsifter 的工具系统性扫描指令空间，找出 RTL 没覆盖到的硅片行为。

---

## 卡 11：Universal Chip Analyzer (UCA)

**定义**：Doc TB（x86.fr 作者）设计的一台开源芯片分析仪，专门用来对古典 8/16 位 CPU 做寄存器级、地址线级、时序级的实验。支持 6800/6502/Z80/8086 等几十种 CPU。

**为什么它能做 HCF 实验**：UCA 可以同时采样地址总线、数据总线、控制信号，并精确到机器周期级。Doc TB 2019 年正是用 UCA 测出了 0x9D/0xDD 在 fetch 之后有 64 ms 的"潜伏期"才进入扫描模式——这个细节用普通示波器分辨不出。

---

## 卡 12：speculation gate（推测执行门）

**定义**：现代 CPU 内部的乱序执行单元会在分支结果未确定前先推测一条路径，等结果确定后再 commit 或 squash。Spectre / Meltdown 类攻击的本质，就是利用 squash 之后的副作用（cache 状态、TLB 状态）反推出推测路径上访问过的数据。

**与 HCF 的关系**：HCF 是 1970 年代"硬件层 hidden state 泄漏"的最初版本；Spectre 是 2018 年同一种本体论在乱序执行架构上的现代形态。**指令集只是 CPU 的承诺**这条原则从未改变，只是攻击面随抽象层不断变厚而加深。
