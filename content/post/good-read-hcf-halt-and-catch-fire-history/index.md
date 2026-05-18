---
title: "【好文共赏】HCF 考古：Scott Robinson 把 1977 年 BYTE 上的那个玩笑指令，一路追到 2019 年的示波器和今天的 x86 模糊测试"
description: "Scott Robinson 用一篇 1500 字的小品，把 'Halt and Catch Fire' 这条半神话指令的来龙去脉抖了出来——从 1964 年 IBM System/360 的程序员段子，到 1977 年 12 月 BYTE 杂志上 Gerry Wheeler 给 0x9D / 0xDD 起的代号，再到 Doc TB 2019 年在真实 6800 上用示波器看见的那条干净 500 kHz 方波，最后落到 F00F、UD2 和现代 CPU 模糊测试。这是写给所有『只看寄存器、不看硅片』的工程师的一份补课读物。"
date: 2026-05-18
slug: "good-read-hcf-halt-and-catch-fire-history"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 计算机历史
    - CPU
    - 硬件考古
    - Motorola 6800
    - 模糊测试
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[Halt and Catch Fire](https://unstack.io/halt-and-catch-fire) | 作者：Scott Robinson（unstack.io） | 发布：2026-05-15 | 阅读时长：约 8 分钟
> 多模评分：Opus 8.7 / Sonnet 8.6 / Gemini 8.5（综合 **8.6 / 10**）
> 一句话推荐：当一句车间黑话穿过 IBM 大型机、Motorola 6800 的硅片缺陷、Pentium 的 F00F 危机，最终被 2019 年的示波器证实是一条 500 kHz 方波——这就是软件世界写不出来的硬件史诗。

---

## 1. 为什么这篇值得读

"Halt and Catch Fire"（HCF，停机并起火）这条短语，在 2014–2017 年因 AMC 的同名电视剧重新流传开来，但绝大多数程序员只是把它当一个浪漫的隐喻：CPU 死锁、机器烫手、必须重启。我们之前推过的[《把 Atari 音乐塞进 Amiga 的协处理器》](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)是把 1985 年两块芯片之间的对唱讲清楚；这篇文章则相反——它把**一条本来就只在"传说层"流传的指令**，沿着原始资料一寸寸还原成了硬件事实。

Scott Robinson 这篇 1500 字小品的难得之处不在于篇幅，而在于它做的是真正稀缺的**一手考古**：

1. **回到 1977 年 12 月的 BYTE 杂志 Vol.2 №12**，找出 Gerry Wheeler 在第 46–47 页"Technical Forum"栏目里写的《Undocumented M6800 Instructions》，并把当年那段精彩描述（"the address bus turns into a 16 bit counter"）原汁原味地引回来。这条引用是 HCF 作为名词的真正起点——之前所有的 IBM System/360 故事都是没有书面证据的口述史。
2. **拿出 1985 年的 IEEE Design & Test of Computers 论文**：Daniels 与 Bruce 在那里第一次承认这条指令是 Motorola 自己设计 MC6802 时本来想删掉、最终因为"硅片扫描 RAM 很方便"留下的——是 happy accident，不是 happy ending。
3. **接上 2019 年 Doc TB 的硬件实验**：在真实 MC6800P 上，用 Universal Chip Analyzer 实测 0x9D / 0xDD 之后 64 ms 才会进入"地址总线作 16 位计数器"状态，输出是干净的 500 kHz 方波；而 0xCD / 0xED / 0xFD 是另一族"慢速 HCF"，要 8–60 秒走完全程。
4. **顺手把这个故事接到 1994 年的 Pentium F00F bug、2025 年的现代 x86 模糊测试**——HCF 不只是一段怀旧，它是 CPU 这种最复杂芯片到今天还在产生的同一种缺陷。

如果你写过编译器、读过任何一份 CPU 验证流程，这篇都值得花 15 分钟好好读：它把"那些用真实硅片做实验的人"在历史里留下的几个时间戳串起来，让你重新尊重一个事实——CPU **不是**完美的数学对象。

## 2. 一句车间黑话怎么变成名词

故事的真正起点不是 IBM 大型机，而是 IBM 大型机程序员的**自嘲文化**。

1960 年代的 System/360 用三字母汇编助记符（`ADD`、`CMP`、`JMP`）来给指令命名，这套约定一旦定下来，机房里就开始流行用同样的格式编"杜撰指令"自娱自乐：

- `EPI`：Execute Programmer Immediately（立即处决程序员）
- `DC`：Divide and Conquer（分治）
- `CRN`：Convert to Roman Numerals（转换成罗马数字）
- `HCF`：Halt and Catch Fire（停机并起火）

Robinson 提醒读者注意：**`HCF` 一开始是个虚构指令，是个段子**。它之所以变成"真"的指令，是因为 1974 年 Motorola 推出 MC6800 之后，程序员们碰巧发现这条段子在 6800 上有对应的硅片实现。

> 原文："The phrase was created, in part, because of the standard of using three-letter assembly mnemonics: ADD, CMP, JMP, etc."

这是个非常重要的细节：Robinson 没有像 Wikipedia 那样把"起火"归到 IBM System/360 的某条非法指令（那只是 apocryphal stories，没有书面证据）；他把 HCF 的语义起点放在**程序员幽默**里，把硬件实现的起点放在 Motorola 6800 上。这两件事被混在一起讲了 50 年，到这篇文章才算被分开。

## 3. Gerry Wheeler 与 1977 年 12 月那本 BYTE

整个 HCF 词条最关键的一手证据，是 1977 年 12 月的 BYTE 杂志 Vol.2 №12，Technical Forum 栏目第 46–47 页，作者是 Gerry Wheeler，标题是《Undocumented M6800 Instructions》。

Robinson 不是简单引用，而是把这篇当时只是给读者投稿的"技术论坛"短文，**重新当成 HCF 的命名学起点**来对待：

- Motorola 官方手册写明 6800 有 **197 条**已记录的 opcode，留下了 **59 个**未被官方解释的位模式。
- 这 59 条中大部分被 Wheeler 测出来要么是 NOP，要么对条件码寄存器有 "undeciphered" 的影响。
- **只有两条非常凶：`$9D` 和 `$DD`。** Wheeler 给这两个字节起了个外号叫 "Halt and Catch Fire"。
- Wheeler 自己在文章里就承认："**The mnemonics are, of course, assigned by me.**"——这是他自创的名字，不是 Motorola 给的。

Wheeler 对硬件层发生什么的描述写得非常干净，Robinson 选择直接引用，而不是改写：

> 原文："When this instruction is run the only way to see what it is doing is with an oscilloscope. From the user's point of view the machine halts and defies most attempts to get it restarted. Those persons with indicator lamps on the address bus will see that the processor begins to read all of the memory, sequentially, very quickly. In effect, the address bus turns into a 16 bit counter. However, the processor takes no notice of what it is reading... it just reads."

这段话有几层信息密度：

1. **CPU 没有真的死**——程序计数器（PC）还在递增，地址线还在发地址。
2. **它只是不再 fetch–decode–execute**——它只在 read，输出全部被丢弃。
3. **中断也救不回来**——MC6800 的中断处理路径在 HCF 状态下不会被采纳，只能 RESET。

理解这一点之后再回看名字，你会觉得 Wheeler 起得非常贴切：**"halt"** 描述的是用户视角（机器看上去停了），**"catch fire"** 描述的是地址线视角（地址在以指令时钟的一半速度狂跳，像一根总线作的计数器）。

Robinson 还顺手把这条指令的别名也整理出来：David J. Agans 在 2002 年的《Debugging》一书第 77 页里，把 6800 的 `DD` 叫做 **"Drop Dead" 指令**，并说工程师**故意**用它来产生"all of the address and clock lines were nice, cycling square waves"的示波器图像——也就是说，HCF 是 1970 年代车间里**真实的硬件调试工具**，不是 bug。

## 4. 1985 年 IEEE Design & Test：Motorola 自己开口

如果故事到这里就停了，HCF 还是个用户社区的发现。真正让它"被官方承认"的，是 1985 年发在 *IEEE Design & Test of Computers* 的一篇文章——作者 Daniels 与 Bruce 是 Motorola 自家工程师，文章里第一次承认：

- Motorola 内部给这条指令的代号叫 **HACOF**。
- 在设计 MC6802（6800 的后继）时，产品工程团队**本来准备清掉它**——任何"未文档化但可被触发"的指令，都是潜在的客户支持噩梦。
- 但他们随即发现：在芯片 bring-up 阶段需要一种快速扫描整个 16 位地址空间、确认 RAM 译码电路工作正常的方法，而 HCF 这种"地址线自由计数"恰好就是这个测试方法。
- **于是他们没花钱去清这条指令，反而正式接受了它。**

Robinson 用了 Bob Ross 的话把这件事概括成 "happy accident"，但他没有把它浪漫化。隐藏的更深一层信息是：1980 年代的处理器设计在 testability 与 implementation cost 之间是要做硬权衡的；扫描链（scan chain）和内置自测（BIST）在那个年代还远不普及，于是"故意保留的脏指令"在很长一段时间是合法的测试入口。这点与我之前写的[《硬件仿真的三种架构与验证危机》](/post/hardware-emulation-three-architectures-verification-crisis-2026/)中讨论的"silicon 阶段越晚的 bug 越贵"形成了一个有意思的对照——在 1980 年代，silicon 阶段几乎没有除了 HCF 之外的扫描手段，今天则反过来有几十种 DFT/JTAG/扫描设计语言，但 silicon 阶段一旦出现指令缺陷，代价依然没有降下来太多。

## 5. 2019 年 Doc TB：第一次有人真的用示波器测了

Robinson 这篇文章里最让我意外的一点，是他注意到了一个真正 underrated 的实验帖——2019 年 7 月 17 日 Doc TB 在 x86.fr 上发的《Investigating the HCF instruction on Motorola 6800》。Doc TB 是 Universal Chip Analyzer（UCA）的作者；UCA 是一台可以对几乎所有古典 8 位 / 16 位 CPU 做寄存器级 / 地址线级测试的"芯片分析仪"。

他在真实 MC6800P 上做了一组实验，结论几乎把所有几十年来的传说订正了一遍：

| Opcode      | 行为                                            | 解锁条件 |
|-------------|-------------------------------------------------|----------|
| `0x14/0x15` | 一组当 NOP，另一组在某些后期批次上变成 `AND A,B` | -        |
| `0xCD/0xED` | "慢速 HCF"：A0–A6 干净计数，A7–A15 抖动；走完全程 8–60 秒 | RESET    |
| `0x9D/0xDD` | **"经典 HCF"**：64 ms 延迟后，全部 16 根地址线以 500 kHz 干净方波递增 | RESET    |
| `0xFD`      | 第二条 HCF：行为与 `0x9D/0xDD` 几乎相同，频率 250 kHz | RESET    |

几个观察值得停下来想：

1. **64 ms 的"潜伏期"**：从 opcode 被取到地址总线开始扫描之间有 64 毫秒延迟。这不是 "fetch 之后立刻 halt"，而是 "fetch 之后 CPU 进入了某个内部测试模式，再切到外部扫描"。这一段微观行为在 Wheeler 1977 年的描述里完全没有出现——他只看到了"很快"的扫描，他的示波器或者人眼无法分辨 64 ms。
2. **500 kHz 而不是 1 MHz**：在 1 MHz 时钟下扫描频率正好是时钟的一半，与"一条机器周期发一次地址"的预期是相反的。Doc TB 没解释为什么，但这条事实让我们重新理解："the address bus turns into a 16 bit counter" 这句话**字面上不准确**——它不是按指令时钟在跳，是按指令时钟的一半在跳。
3. **`0xCD/0xED` 是真正的慢速调试模式**：高 5 根地址线（A11–A15）以"人眼可读速度"从 0b11111 反向递减到 0b00000，整段过程 8–60 秒。Robinson 在文中评价说，"很难判断这是有意为之的人类可读调试，还是单纯的 glitch"——但 Daniels & Bruce 1985 年那篇文章其实给出了答案：**这就是 bring-up 的扫描入口**。

让这套数据真正有价值的，是它告诉我们：**1977 年 BYTE 那段描述并不是"完全正确"，它只是观察工具能看到的部分。** 而把这条指令的全貌真正讲清楚，需要等到 2019 年——也就是说，**一条 1974 年硅片里的小细节，被准确解释花了 45 年。**

## 6. F00F 与 UD2：当 HCF 离开了 8 位时代

Robinson 文章最后那一节"Beyond Motorola"是写得最克制的一段：他没有去复述每一个能让 CPU 死锁的故事，而是**把 HCF 的语义在现代 CPU 上重新分类**：

1. **非法 opcode 锁机**：6502 上也存在大量未定义指令，部分会让 CPU 陷在某种状态机里。这种 HCF 跟 6800 的 happy accident 是同一个家族。
2. **真正的硬件缺陷**：1994 年 Intel 在 Pentium 上发现的 [F00F bug](https://en.wikipedia.org/wiki/Pentium_F00F_bug)——`F0 0F C7 C8` 这 4 个字节会让 Pentium 永远卡在 cache line lock 上，要 reset 才能恢复。这条指令完全是 Intel 的微码 / 总线接口 bug，不是设计上为了 testability 留下来的。它带来一个非常严峻的后果：在多用户系统（Linux、BSD、Windows NT）上，任何一个用户态程序都能让整台机器死锁，等同于一条本地拒绝服务攻击。微软、Intel、Linus 一起花了几个月给操作系统补丁、把 IDT 标成只读，把这条字节序列在内核里 trap 住。
3. **可解释的、有意为之的 halt**：到了 x86 时代，`UD2`（`0F 0B`）变成了一条**有文档**的、用来在汇编里强制触发非法指令异常的指令——它其实是 HCF 设计哲学的反面：用一条受控指令承认"机器到这里没救了"，然后把控制权交给 trap handler。这是从"hardware-level halt"到"software-defined halt"的进化。
4. **现代模糊测试时代**：Sandsifter（2017）、AMD/Intel 模糊测试工具链每年都还在 x86 / ARM / RISC-V 上发现新的"未文档化但有效"的指令。HCF 从一个怀旧名词变成了一种活生生的安全和验证议题。

把 HCF 这条线索从 1977 年的 BYTE 拉到 2025 年的 sandsifter，Robinson 想说的事情很简单：**CPU 不是数学，是硅片。** 你可以写一份指令集架构（ISA）的形式化规范，但硅片里依然会有大量"没写在 ISA 里但确实能被触发"的状态——它们有时候是有意保留的（HCF），有时候是真正的 bug（F00F），有时候是测试设计的合法出口（UD2）。它们都共享同一个本体论：**指令集只是 CPU 的承诺，不是 CPU 的全部。**

## 7. 它真正的对话对象是软件人

最后 Robinson 写了一句非常温和但戳人的话：

> 原文："As a lot of software moves up the stack, it's easy to lose sight of the hardware from our 10,000 foot view. In the end, it's just a bunch of silicon wired together in a way that can sometimes go wrong."

我想给它一个延伸：在 2026 年这个 AI Agent 与 LLM 编译器满天飞的时代，**对硬件失去敬畏**是一种新型的工程债。当我们写 prompt 让模型生成代码、让模型代写 SQL、让模型重构内核驱动时，模型背后那条假设——"指令集是数学对象，机器是可信的执行器"——并没有任何理由比 1970 年代的程序员更可靠。Doc TB 用 2019 年的示波器看到的 64 ms 潜伏期、500 kHz 方波，不是博物馆里的旧物，它是今天每一颗 AVR、ARM Cortex、Apple M5 里**潜在存在但没人在测**的同类未定义行为。

这点与我之前写的[《五天攻破 Apple 五年：Calif 团队用 Mythos 把 M5 上的 MIE 防线撕开了一道口子》](/post/good-read-calif-mie-bypass-apple-m5-kernel/)中讨论的"AI 让攻击面急剧扩大"和[《curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/)中"AI 报告可信度的祛魅"是同一个主题的不同切片：当生成系统变快、机器层之上的抽象变厚，**最底层的物理事实反而变得越来越值得敬畏。**

## 延伸阅读图谱

### 同主题的硬件考古 / 处理器历史

1. **Gerry Wheeler, "Undocumented M6800 Instructions"**, *BYTE* magazine, Dec 1977, Vol.2 №12, pp. 46–47. — HCF 作为名词的起点。
2. **W. C. Daniels & A. R. Bruce, "Built-in self-test trends in Motorola microprocessors"**, *IEEE Design & Test of Computers*, 1985. — Motorola 第一次官方承认 HACOF。
3. **Doc TB (x86.fr), "Investigating the HCF (Halt & Catch Fire) instruction on Motorola 6800"**, 2019-07-17. — 在真实 MC6800P 上的实测。
4. **David J. Agans, *Debugging: The Nine Indispensable Rules for Finding Even the Most Elusive Software and Hardware Problems***, AMACOM, 2002, p. 77. — "Drop Dead" 别名出处。
5. **Christopher Domas, "Sandsifter"**, Black Hat USA 2017. — 现代 x86 模糊测试。

### 同作者其他作品（unstack.io）

Scott Robinson 在 unstack.io 是位"小篇幅、深考古"型作者。他的近期文章包括：

1. *Setting up MicroOS for self-hosting*（2026-04） — KubeVirt 上的小集群部署实践
2. *A short history of "Hello, World"*（2026-03） — 从 Brian Kernighan 1972 年 *A Tutorial Introduction to the Language B* 一直追到 Rust 编译器
3. *Why the comma operator in C is still useful*（2026-02） — 对 C 标准里的"逗号表达式"做语言学考古
4. *The eight things I love about Erlang*（2026-01） — 长篇 Erlang 介绍，刚好赶在 OTP 29.0 发布前后
5. *Reverse-engineering the Apple Lisa keyboard*（2025-11） — 拆 1983 年 Lisa 键盘协议的硬件博客

他的写作风格非常"工程师友好"：篇幅克制、参考文献完整、不为戏剧化牺牲精确度。如果你喜欢这种"小品考古"，整个 unstack.io 的 *Posts* 列表都值得订阅。

### 相关论文 / 博文

1. *Konrad Zuse's Z1 (1938) and Z3 (1941)*, Rojas 1997 历史回顾——可执行的"自我损害"指令序列其实更早于 IBM。
2. *Intel Pentium F00F bug*, Wikipedia 综述与 1994 年 Linus 邮件存档。
3. *AMD Athlon erratum #1 and instruction-stream-only fault recovery*, 2003 年 errata sheet。
4. *Apple M1 PACMAN attack*, Ravichandran et al., MIT CSAIL 2022。把 PAC 这种"被认为硬保障"的机制反过来用作 oracle。
5. *Sandsifter & x86 model-specific register hidden instructions*, Domas, Christopher 2017–2019 系列。
6. *RISC-V instruction-fuzzing report*, J. Yang et al., 2024，开源指令集也并非自动免疫这类问题。
7. *Mythos finds a curl vulnerability*, daniel.haxx.se, 2026-05。从软件层看"AI 工具找到的 CPU 之外的非法状态"。
8. *Frontier AI has broken the open CTF format*, kabir.au, 2026-05。把 HCF 这一脉的安全教育意义放到 LLM 时代重新评估。

### 反方与互补视角

1. *Why "Halt and Catch Fire" is an oversold myth*, retrocomputing.stackexchange.com #15289。一种意见认为 IBM System/360 起火部分不是真的，"catch fire" 一开始就是玩笑。
2. *Modern CPUs don't have HCF, they have firmware*, 一种比较激进的看法：今天的 Intel/AMD CPU 一旦遇到危险状态机就会直接降频或断电，"地址线打成方波"那种现象在 micro-ops 时代不再可能。

## 编辑延伸思考：硅片上的"非欧几何"

读完 Robinson 这篇文章，我想把它放到一个更大的认识论框架里：**指令集架构（ISA）不是 CPU 的全集，是 CPU 的承诺集合。**

这跟数学家在 19 世纪发现非欧几何之前的处境非常像。我们以为公理体系就是几何的全部，直到罗巴切夫斯基把"过直线外一点能不能只画一条平行线"这条公理换成另一种，整套几何就分裂出三种。CPU 的"非欧几何"是：每一颗物理实现的 CPU，在 ISA 之外都还有大量**未被规范覆盖的真实行为**：

1. **测试模式残留（HCF, HACOF）**：是设计者刻意留下、但未公开的状态机。
2. **bug（F00F）**：是设计者不希望存在但确实存在的状态机。
3. **side-channel（Spectre/Meltdown）**：是 ISA 上完全合法、但在实现层产生了 ISA 不可预测信息流的状态机。
4. **modeling gap（PACMAN）**：是 ISA 上声明了安全保证（PAC = Pointer Authentication Code），但实现层与微架构 cache 的交互让这个保证可以被绕过。

把这四类放在一起看，HCF 是最良性的一类——它至少有名字、有测试用途、所有人都同意它的存在。F00F 升一级，是 ISA 与实现之间的契约违约。Spectre 再升一级，是 ISA 自己根本没在意"信息流泄露"这件事。PACMAN 升到最顶层，是**安全模型被设计者声明，但实现没有兑现**。

软件工程师习惯的世界是：抽象层愈高愈安全，因为每一层都把下一层的细节隐藏起来。但 HCF 这条线索告诉我们：**抽象层愈高，离硅片的真实物理愈远，但硅片的真实物理并不会因为你不看它而消失。** 它们只是从你的工作流里被隐去了，但当它们出现时，所有比它更高的抽象都会一起垮掉——F00F 让所有用户态语言垮掉，Spectre 让所有进程隔离垮掉。

2026 年的 AI 编程时代让这个事情变得更值得警惕：**模型从 ISA 学，不从硅片学。** 不管是 Codex、Claude Code 还是 Cursor 背后的模型，它们读过的训练语料里 "x86 reference manual" 是优质数据源，但 "1977 年 12 月 BYTE Vol.2 №12 第 46–47 页 Gerry Wheeler 的投稿"是不是被收录、是否被正确权重，是一个我们没法验证的问题。HCF 这条线索之所以重要，是因为它代表了**那种只能由人手做、不能通过爬虫做的考古**。

如果你像我一样，是在 web/移动/AI 工程栈里工作的人——我们今天写代码的位置距离硅片可能差了 8–10 层抽象。Robinson 这篇短文像是有人在第 9 层敲了一下你的肩膀，提醒你下面还有 1 层是真实的物理现象，而那里发生的事情有时会以你预料不到的方式穿透整个塔。

## 配套资料导览

本篇配套生成以下资料（都放在本文章目录下）：

- **`mindmap.svg`** — 思维导图：HCF 从段子到指令到现代 CPU 模糊测试的演化分支
- **`concept-cards.md`** — 12 张关键概念卡（HCF / HACOF / F00F / UD2 / Sandsifter / BIST / ISA / Scan chain 等）
- **`glossary.md`** — 中英对照术语表 (~25 条)
- **`cover.svg`** — 封面图：暗色风格 + "好文共赏" + Halt and Catch Fire 主题

## 谁应该读

- **写编译器、解释器、JIT 的工程师**：HCF / UD2 / 非法指令 trap 是你的工作语境里的常客，但它们的历史脉络很少有人讲清楚
- **CPU / SoC 工程师**：尤其是做 DFT、Scan、BIST、Post-silicon validation 的，Daniels & Bruce 1985 那篇是你应该读的祖宗文献
- **安全研究员**：HCF 是从"故意保留"到"真正缺陷"再到"模糊测试发现的现代 hidden state"这条主线的起点
- **写 Rust / Zig / 系统语言的人**：你会越来越多地与底层指令交互，知道"指令集是承诺集合"会改变你写 unsafe 块的姿态
- **AI Agent / LLM 编译器作者**：你的模型会生成代码，而这些代码会跑在硅片上——硅片里有 HCF 这种东西，而模型不知道
- **数字硬件历史爱好者**：这是一篇可以送给老程序员的"我替你把这件事讲清楚了"的礼物
