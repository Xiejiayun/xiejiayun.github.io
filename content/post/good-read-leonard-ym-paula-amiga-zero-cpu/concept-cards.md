# 概念卡 · Concept Cards

> 用 12 张卡片浓缩 Leonard 这篇 YM2149 → PAULA 0% CPU 仿真的核心知识点。建议配合原文与思维导图一起看。

---

## #01 · 起点：一个挑衅

> **场景**：Leonard 在 Amiga 500 上用 sin-dots 算法画了 6405 个点，被另一位 demoscene 大佬 Hannibal 用 6682 点反超，并附了一句"你像 Atari 程序员一样优化"。
>
> **价值**：本文的工程问题是为了"接梗"才存在的。理解 demoscene 文化能解释为什么有人会花精力把音频处理压到 0% CPU —— 这是社群礼仪。

---

## #02 · 两块 1985 年的芯片

> **YM2149** = 三路方波 + 1 个共享 envelope，无采样。
> **PAULA** = 4 路 8-bit PCM 直读主存，无原生方波 / envelope。
>
> 两者背道而驰，但都在 1985 年问世，分别定义了 Atari ST 与 Amiga 的声音美学。本文用 PAULA 模拟 YM 的全部任务，等价于让一个"采样回放机"装作"波形发生器"。

---

## #03 · MadMax Buzzer：把 envelope 当声源

> **常规用法**：envelope 控制方波音量随时间变化（标准 ADSR）。
> **MadMax 黑魔法**：envelope 的频率开到可听音域，**让 envelope 本身成为可听波形**，再用方波给它"切割"。
>
> 这是 Jochen Hippel 在 1980 年代末从 YM 里榨出"史诗音色"的核心技巧。本文要在 PAULA 上重建的，正是这个效果。

---

## #04 · PAULA 的两个被遗忘特性

> **特性 A：Attached Voice 体积调制** —— 声道 0 的样本流被解读为声道 1 的音量值。
> **特性 B：Attached Voice 音高调制** —— 同上，但调的是 period 寄存器。
>
> Leonard 一句话戳穿事实：
>
> > 原文：> "In a way, this feature is similar to the YM2149 ADSR envelope. Not technically, but because both features are mostly ignored by Atari and Amiga programmers!"
>
> 两侧的程序员都对自己手边那把"另类调制刀"视而不见 —— 对称的盲点。

---

## #05 · 第一次失败：分辨率不够

> **直觉方案**：把三角 envelope 存为 16-bit 调制字，让它驱动方波音量。
> **结果**：声音粗糙、棱角分明。
>
> **根因**：attached voice 的调制字以"每两个 PCM 样本一个值"的速率消化，三角波被严重欠采样，所有细微弧度坍缩成大台阶。

---

## #06 · "尤里卡"反转

> **直觉是错的**：让分辨率充足的 8-bit PCM 通道承担"高分辨率"信号，让低速率调制字承担"低分辨率"信号。
>
> Leonard 的反转：
> - 三角 envelope → 存为 **8-bit PCM**（128 级精度）
> - 方波 → 存为 **16-bit 调制字**（只需 0 / 64 两个值，欠采样不会失真）
>
> **教训**：当你受困于某个硬件接口的带宽不对称时，先问自己"是不是我把信号塞进了错误的那一侧"。

---

## #07 · 对数三角波

> YM2149 的 32 级音量是对数刻度。如果在 PAULA 上重画一个线性三角，听感会偏离原作。
>
> Leonard 手写了一张 `dc.b $00,$00,...,$0d,$0b,$09,$07,$06,$05,$04,$03,$03,$02,...` 的查表，靠近峰值时步进 11 / 13 / 15，靠近谷值时步进 1 —— 这是把 dB 域映射到 8-bit 线性域的"对数三角"。
>
> 细节正确才能复现 Atari 音色，跨芯片仿真不是搬寄存器，是搬感知。

---

## #08 · COPPER：写寄存器 + 等光栅

> Amiga COPPER 只有两条指令：
> 1. `MOVE`：把立即数写进任意 chip register
> 2. `WAIT`：阻塞直到光栅扫到某个坐标
>
> Leonard 把每一帧的"PAULA period / volume 写入序列"在 PC 上预先编译成一段 copper list，再让它在末尾跳回自身，整个音频更新链路完全绕开 M68K。
>
> **本质**：他把"音频 driver" 从软件搬进了协处理器微码。

---

## #09 · 0% CPU 的物理基础

> 三条独立条件叠在一起：
> - PAULA 通过 DMA 直读 chip RAM，CPU 不参与采样输出。
> - COPPER 与 CPU 并行运行在另一组总线时序上。
> - copper list 自链接，无须 CPU 做任何调度。
>
> 任一条件破坏，0 CPU 就垮。这是为什么这个技巧只在 Amiga 行得通：Atari ST 没有 COPPER，也没有真正的 DMA 驱动音频。

---

## #10 · 跨域复用思想

> Leonard 在 about 页里说：
>
> > 原文：> "Modern techniques could be applied efficiently in the retro world, and vice versa."
>
> 本文与他 2024 年那篇《AVX vpternlogd》是一对镜像：那里他证明 AVX-512 的三值逻辑指令本质上是 1985 年 Amiga blitter 的 minterm；这里他证明 PAULA 1985 年的调制硬件可以承担 2026 年视角里的"零开销采样合成"。
>
> 同一个工程师在用"对称性"逼近真理：好的硬件设计是跨时代的。

---

## #11 · 复刻的工程结构

> 整个 pipeline 分两段：
> - **离线（PC 工具）**：解析 .sndh → 模拟 YM 帧 → 提取 period / volume → 翻译成 PAULA 寄存器值 → 编译 copper list → 写入数据文件。
> - **在线（Amiga）**：DMA 加载 copper list → COPPER 自行更新 PAULA → 68000 空闲。
>
> **架构启示**：当目标平台资源紧张，把所有可静态决定的事提前到编译期；让运行时只剩"按表照搬"。这与现代 ahead-of-time 编译、图形 pipeline state objects 是同一种思想。

---

## #12 · 文化注脚：礼仪与传承

> 本文起点是社群挑衅，终点是 7210 个 sin-dots 加 Atari 音乐。**这不是在解决商业问题，是在玩一个 35 年前的游戏**。
>
> 但正是这种"游戏精神"维持着一种工程审美：
> - 硬件特性永远不嫌老。
> - 0% 是值得追的极限。
> - 你可以"在被忽视的角落里"找到全新的设计自由度。
>
> 把这条审美注入到任何现代代码 review，都不会过时。
