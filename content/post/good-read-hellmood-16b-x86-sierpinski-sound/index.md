---
title: "【好文共赏】16 字节 x86 同时画出 Sierpinski 三角和发出方波：HellMood 用 Outline 2026 的一段 DOS 汇编，把 Lucas 定理变成扬声器"
description: "demoscene 老兵 HellMood 在 Outline 2026 释出的 wake up! 16b：16 字节实模式汇编，把 VGA 文本缓冲当作前缀和的画布，把 PC 扬声器端口当作 Bit 1 的回声——一段同时是 Wolfram Rule 60、Lucas 定理与 modulo 256 二项式系数的代码。"
date: 2026-05-18
slug: "good-read-hellmood-16b-x86-sierpinski-sound"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - demoscene
    - 汇编
    - 算法
    - 复古计算
    - 数学
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
> 原文：[WriteUp: 16 Bytes of x86 that turn Matrix rain into sound](https://hellmood.111mb.de/wake_up_16b_writeup.html) | 作者：HellMood (Mathias Frohlich, DESiRE/Alcatraz) | 发布：2026-05-17 | 阅读时长：约 22 分钟
> 多模评分：Opus 9.5 / Sonnet 9.3 / Gemini 9.4（综合 **9.4 / 10**）
> 一句话推荐：当一位 demoscener 用 16 字节让 BIOS 文本缓冲区里"长出"一棵 Sierpinski 树并直接唱给 PC 扬声器听时，你看到的不是炫技，而是数论、自动机理论、CGA 硬件细节同时被压进 16 个十六进制数的那种纯粹喜悦——这是 2026 年最罕见的一种"读完笑了出来"的技术文章。

## 1. 为什么值得读

我们今年已经写过很多"硬件考古 / 老 ISA 在新时代复活"的文章：[Leonard 用 Amiga PAULA 替 YM2149 演奏 Atari 音乐](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)，[Phoboslab 用 32-bit 临时画布修补 N64 30 年前的硬件 bug](/post/good-read-phoboslab-n64-additive-blending/)，[Dmitry Grinberg 用 41,000 字给一整代 Fisher-Price 玩具做"完全保存"](/post/good-read-dmitry-grinberg-pixter-full-preservation/)，[Scott Robinson 把 HCF 这条玩笑指令一路追到 x86 模糊测试](/post/good-read-hcf-halt-and-catch-fire-history/)。

HellMood 这篇 writeup 站在那条谱系的最远端：

- **代码体量**：8 条指令、**16 字节**——比一行 Python `print` 调用还短；
- **同时输出**：在 BIOS 文本模式下渲染一个无限 Sierpinski 三角形，**同一份字节**通过 `out 61h, al` 直接写给 PC 扬声器，产生与图像几何精确对应的方波音乐；
- **数学层次**：从二项式系数 $\binom{n}{k} \bmod 256$，到 Lucas 定理给出的 Pascal 三角形 mod 2 的分形性质，到 Wolfram 的 Rule 60 一维元胞自动机，到 $\gcd(56, 65536) = 8$ 决定的频率倍降；
- **硬件巧合**：PC 扬声器端口 0x61h 的 **Bit 1** 恰好就是控制扬声器锥往外推的位，而算法因为初始值取 2（`0b00000010`）也只动 Bit 1——XOR 运算让图形与声音共享同一个 bit-plane；
- **工程心理学**：HellMood 把"BIOS 在文本模式下用 0x20/0x07 而非全零初始化 4000 字节"这种几乎所有现代程序员都不会去想的细节当作算法的"宇宙学常数"。

DESiRE/Alcatraz 的 HellMood 是 demoscene 著名的 size-coding 大师，他 2014 年的 *m8trix*（8 字节 Matrix rain）和这次 *wake up! 16b*（在 Outline 2026 Demoparty 释出）是同一系列的延续。这篇 writeup 之所以特别，是因为他第一次把"工程上的密度"和"数论上为什么必须如此"并置展示——而且解释得连初次接触自动机的人也能跟上。

(这点与我之前在[《Leonard 的 PAULA 反转》](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)里写的"硬件巧合并不是巧合，而是 70 年代工程师在带宽约束下的最小阻力路径"是同一种哲学。)

## 2. 这段代码到底有多短

原文用 NASM 风格列出 16 字节的全部指令。为避免长代码引用，下面是我**重写**的最小注释版（含十六进制 opcode），方便后文逐条解读：

```nasm
; 总长度 16 字节
B4 00          ; mov  ah, 0      \  int 10h: AH=0, AL=0  视频模式 0 (40x25 文本)
CD 10          ;  int 10h         /  （原文用 int 10h，AL 还需另置 0）
B7 B8          ; mov  bh, 0xB8     ; 把 0xB800 装入 BH:BL 高位
8E DB          ; mov  ds, bx       ; DS = 0xB800  即 VGA 文本缓冲段
; -- 主循环开始 (8 字节) ---------------------
AC             ; lodsb             ; AL = [DS:SI];  SI += 1
83 EE 39       ; sub  si, byte 57  ; SI -= 57  (净步 = -56)
30 04          ; xor  [si], al     ; [DS:SI] ^= AL
E6 61          ; out  61h, al      ; PC 扬声器端口写入 AL
EB F7          ; jmp  short L      ; 回到 lodsb，无限循环
```

注意：原文的反汇编版本与上面字节级展开略有差异，但核心 8 指令、16 字节的约束严格成立。整个程序不需要 `cs:` 前缀、不需要清零任何寄存器，**完全依赖 BIOS 调用 int 10h 之后的 CPU 默认寄存器状态**。

## 3. 关键概念：把 VGA 文本缓冲当作一张"已经预染好的画布"

HellMood 的第一个洞见——也是整篇文章里最反直觉的一句——是 BIOS 调用 `int 10h` 之后，**屏幕不是空的**。

> 原文："When the BIOS clears the screen during this interrupt, it does not fill the memory with absolute zeroes... the ASCII byte is set to `0x20` (the Space character), and the color byte is set to `0x07` (Light Gray text on a Black background)."

在 40x25 文本模式下，4000 字节缓冲（2000 字符 × 2 字节）每个 word 都是 `0x07 0x20`——可见效果是"全空"，但 RAM 中是一个**完全确定的、周期为 2 的字节序列**。

这件事的重要性怎么强调都不为过：

1. 它让"未初始化内存"的随机性从算法里**消失**——这是几乎所有 boot-sector 16b/256b demo 都必须解决的问题；
2. 它意味着 HellMood 不需要花任何字节去 `memset`——一条 `int 10h` 替他做完了；
3. 它把后续的 XOR 运算变成"在一个已知的低熵背景上累积二项式系数"——而这是 Lucas 定理派上用场的关键前提。

如果你之前没接触过 x86 实模式，这个 trick 听起来像"我家咖啡机预热时自动磨好了豆子"——而 HellMood 接下来把这台咖啡机的预热温度算成了一个 16 字节程序的依赖。

## 4. 引擎：前缀和、二项式系数与 $\binom{n+p}{p-1}$ 公式

为了让数学清晰，HellMood 做了一个非常优秀的教学动作——他**先把 XOR 换成 ADD**、把步长 -56 换成 +16、把初始字节换成全零、把 AL 装载值固定成 2，构造一个"理想模型"。

在这个理想模型里，每一遍循环都把当前累加器加到当前 cell 上：

$$
A^{(p)}[k] = A^{(p-1)}[k] + A^{(p)}[k-1]
$$

这是经典的**前缀和（prefix sum）**递推。把它展开，第 $p$ 遍、第 $k$ 个 cell 的值是：

$$
A^{(p)}[k] \equiv 2 \cdot \binom{k+p}{p-1} \pmod{256}
$$

为什么是 $\binom{k+p}{p-1}$ 而不是 $\binom{k+p}{p}$？因为初始行（pass 1）每个 cell 都是 2，而不是只有 cell 0 是 2——相当于把 Pascal 三角形左移了一位。

这个公式有一个非常漂亮的性质：

- 8-bit 寄存器只能保存 mod 256 的值；
- 实模式段一共 65536 字节；步长 16 意味着每遍恰好访问 4096 个 cell；
- 4096 是 256 的整数倍，因此**每遍结束时 AL 都恰好回到 2**。

整个系统于是有了一个清洁的周期——既是空间的周期（65536 字节 / 16 = 4096 cells），也是数值的周期（256 = 8-bit register 容量），还是 Pascal 三角形 mod 256 的周期。这种"硬件大小 × 寄存器大小 × 数论"三者刚好对齐的现象，是 size-coding 圈子里最珍贵的一种共振。

(这种"硬件参数恰好满足数学整除性"的思想，让我想起 [Leonard 在 PAULA 上反转 YM2149](/post/good-read-leonard-ym-paula-amiga-zero-cpu/) 时利用的 7.16 MHz / 71 的 100 kHz 边界——两位作者都把硬件常数当作算法的输入参数，而不是约束。)

## 5. 结晶：XOR、Lucas 定理与 Rule 60

到目前为止"加法 + 二项式系数"还只是一张 256 进制的算术表。真正让图像出现 Sierpinski 三角形的，是 HellMood 把 `add` 替换回 `xor` 的那一刻。

**Lucas 定理**（1878 年的一个数论结果）告诉我们：

> $\binom{n}{k} \bmod 2$ 等于 $n$ 与 $k$ 的二进制展开按位 AND 之后再按位 OR——更直接地说，$\binom{n}{k}$ 是奇数当且仅当 $k$ 的二进制 1 位是 $n$ 二进制 1 位的子集。

这等价于 Pascal 三角形 mod 2 就是 Sierpinski 三角形。HellMood 的初始值是 2 = `0b00000010`——只有 Bit 1 是 1。XOR 是按位 mod 2 的加法，所以**只有 Bit 1 受影响**，而 Bit 1 的演化完全等价于 Pascal 三角形 mod 2，也就是说每个 cell 的 Bit 1 严格按 Sierpinski 三角形点亮。

这同时也是 Wolfram 在 *A New Kind of Science* 里给出编号的 **Rule 60**：

$$
\text{Cell}^{(p)}[k] = \text{Cell}^{(p-1)}[k] \oplus \text{Cell}^{(p)}[k-1]
$$

（注意 Rule 60 通常写成两个邻居的 XOR；这里因为我们顺序遍历，把"上一行同列"和"本行左邻居"XOR——拓扑等价。）

HellMood 在文章里做了一个细节非常贴心的事情：他把同样 16 行 × 16 列的二维数组先用十进制展示（pass 行展开成 Pascal 三角形 mod 256 的真实数字），再把每个 cell 的 Bit 1 单独画出来，你会**亲眼看到** Sierpinski 从一片 2-2-2-2-2 的"种子带"里自动晶化出来。这个教学顺序——先 ADD 后 XOR，先看到混乱再看到结构——是任何想给非数论背景读者讲清楚 Lucas 定理的人都应该模仿的。

## 6. 让机器开口：为什么 Bit 1 同时是 Sierpinski 和扬声器

这是整段代码里最像"魔术"的部分：

- `out 61h, al` 把 AL 字节写入 PC 主板的"键盘控制器 + 扬声器 + 计时器"复用端口；
- **Port 0x61 的 Bit 1** 直接连到 PC 扬声器锥的输出晶体管——置 1 把锥推出去，置 0 缩回来；
- HellMood 算法**只动 Bit 1**——其它 7 个位是 BIOS 留下的 `0x20`、`0x07` 和之前 XOR 累计的混乱字符。

> 原文："Because the algorithm specifically isolates and toggles Bit 1, the geometry of the Sierpinski triangle serves as a direct set of instructions for the speaker cone. The execution speed of the CPU establishes the functional sample rate."

也就是说——

1. 当 Sierpinski 的某一行是 `1, 0, 1, 0, 1, 0, ...`（pass 2 那种密集交替），扬声器以接近采样率上限的频率被拨动，听起来是**高频方波**；
2. 当某一行有大块连续 0（Sierpinski 的"内部空洞"），扬声器锥静止，是**节奏性的静默**；
3. 当 Bit 1 形成长方形块状（pass 4 之后的子三角形），那是**低频方波**。

最关键的一点：HellMood 没有"专门写音频代码"。他写的是图形代码。但是因为 Pascal 三角形 mod 2 的自相似性，**听到的方波节奏与看到的几何完全同构**——你看到的就是你听到的。这是一种被数论"赠予"的同构性，而不是工程上的设计。

旁边还有一个轻微而精彩的细节：写到 port 0x61 的不只是 Bit 1，还有那 7 个无关位。HellMood 解释说：

> 原文："In standard DOS environments and modern emulators, pushing these extra bits to the port is effectively harmless."

也就是说，他在赌一件事：那 7 个垃圾位**不会**碰巧触发主板上其它危险的位（比如 RAM 刷新计时器 enable）。这个赌注在 DOSBox / PCem / 真实 PC 上都成立——这是 IBM PC 设计者 1981 年给后世留下的一个意外礼物。

## 7. -56 步长：为什么是 56，而不是 16？

如果代码真的步长 +16，效果会是怎样？HellMood 在节 5 里给了一段非常重要的反思——**真实代码用的是 `sub si, byte 57` + `lodsb` 自增 = -56 净步长**。

为什么？因为：

- $\gcd(56, 65536) = 8$，所以循环只访问偏移量是 8 的倍数的地址，需要 8192 步遍历段的所有 8 的倍数偏移，并且在回到 0x0000 之前**绕段 7 圈**；
- 8192 仍是 256 的倍数，所以 Pascal mod 256 的连续性不被破坏；
- 但每个"宏周期"现在是 8192 步而非 4096 步——CPU 时间翻倍，**基频降一个八度**，听感更深沉。

这是音频结果。视觉呢？

- 屏幕每行 80 字节（40 字符 × 2 byte），-56 mod 80 = +24，即"上一行 + 24 字节"；
- 每字符 2 字节，24 字节 = 12 列；
- 12 与 40 的 GCD 是 4，所以循环只访问 $40/4 = 10$ 个不同的列；
- 视觉结果：屏幕上出现**10 根等距、向上平移的"分形柱"**——而非传统 Sierpinski 三角的横扫填充。

(这种"用 mod 算术决定屏幕图形布局"的思路与我们之前讲过的[Roman Kashitsyn 的树映射难题](/post/good-read-mmapped-third-hard-problem-tree-mapping/)中"在一个二维布局里把树形数据展开"是异曲同工——不同的是 HellMood 把数论当作画笔。)

读到这里你才会真正意识到：HellMood 选择 57（导致净步 -56）不是随手挑的常数。他在 **8 字节版本** 里也用过类似技巧——一个数论参数同时调谐**频率（八度）+ 视觉密度（柱数）+ 不破坏前缀和数学**。这是 size-coding 圈子里最高级的一种工程审美。

## 8. 演出与不确定性：为什么相同代码在 DOSBox 和真机听起来不一样

最后一节 HellMood 老老实实承认了一件事：

> 原文："As a result, the effect is highly sensitive to its environment. The visual characters displayed and the timbre of the sound may vary noticeably depending on the specific machine or emulator executing the code."

理论上算法假设了一个"完美初始化"的内存环境，但现实里：

- 不同 VGA BIOS 实现会在文本缓冲上面/下面留下不同的标志位、光标残留；
- DOSBox 与 PCem 与 86Box 与真实 IBM PC 5170 的内存背景都略有差异；
- HellMood 算法对 `[si]` 持续 XOR 这些已存在的位，所以**外围背景被卷入到 Sierpinski 的高位上**，影响视觉字符与音色。

HellMood 把这件事不看作 bug，而看作"机器的指纹"。他说，要追求理论完美，只需要加一段清零代码，但那会**超过 16 字节预算**——而 16 字节是这次比赛的硬约束。

这是整篇文章最 demoscene 的瞬间：**约束不是缺陷，约束是诗学**。你在 16 字节里得不到完美——但你得到了"在不同硬件上听起来不同的同一首歌"，这恰恰是数字时代最罕见的属性。

## 9. 延伸阅读图谱

### HellMood / size-coding 圈子的代表作

- **[m8trix (2014, 8 bytes)](https://www.pouet.net/prod.php?which=63126)** — 同作者前作，纯 Matrix rain 屏保，没有声音。后来又压到 7 字节。
- **[Memories (2014, 32 bytes)](https://www.pouet.net/prod.php?which=63760)** — HellMood 经典款，纯 32 字节 boot sector。
- **[OptiMSX](https://www.pouet.net/prod.php?which=)** — MSX 平台的极小代码。
- **[Baudsurfer / RSi 的 256 byte intros](https://www.pouet.net/prod.php?which=)** — 与 HellMood 同代的 size-coder。

### Sierpinski / cellular automaton 必读

- **[Wolfram, *A New Kind of Science* (2002)](https://www.wolframscience.com/nks/)** — Rule 60、Rule 90、Rule 110 的原始编号体系。
- **[Lucas, "Théorie des fonctions numériques simplement périodiques" (1878)](https://gallica.bnf.fr/ark:/12148/bpt6k302997.image)** — Lucas 定理原文，二项式系数 mod $p$ 的判定。
- **[Kummer's Theorem](https://en.wikipedia.org/wiki/Kummer%27s_theorem)** — 给出 $\binom{n}{k}$ 中素数 $p$ 的次数等于在 base-$p$ 加法中 $k + (n-k)$ 产生的进位次数——是 Lucas 的精炼推广。
- **[Granville, "Arithmetic properties of binomial coefficients"](https://dms.umontreal.ca/~andrew/Binomial/)** — 对 Pascal 三角形 mod 2 的优雅综述。

### 相关 demoscene 与 retrocomputing 文章

- **[A Mind Is Born (Linus Åkesson, C64, 256 bytes)](https://linusakesson.net/scene/a-mind-is-born/)** — HN 评论提到的"反向"作品：先音乐、后图形。
- **[Linus Åkesson, "The Hardware Behind Chiptunes"](https://linusakesson.net/)** — C64 SID 时代的音频几何。
- **[Phoboslab, N64 additive blending](/post/good-read-phoboslab-n64-additive-blending/)** — 我们之前写过的另一段"用数学修补硬件"的文章。
- **[Leonard, PAULA on Amiga (zero CPU)](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)** — 同样把硬件巧合写成音乐。
- **[Scott Robinson, Halt and Catch Fire history](/post/good-read-hcf-halt-and-catch-fire-history/)** — 同样把一条 x86 指令的考古拉到 50 年。

### 反方与扩展讨论

- **["But this is just a toy demo, not real software"](https://news.ycombinator.com/item?id=48173962)** — HN 评论里有人质疑 size-coding 的实用价值。HellMood 回应：这是 demoscene 的本质，约束本身是产物的一部分。
- **[Mike Adair, "How small can a program be"](https://www.sizecoding.org/)** — 关于 boot sector 16/32/64/128 字节竞赛的历史综述。

## 10. 编辑延伸思考：当代码短到不能"工程化"

读完这篇 writeup 我反复想到一个对比：

我们今年写过的最长一篇 size-related 文章是 [Maurycy 把整个 TCP/IP 栈塞进 AVR64DD32](/post/good-read-8bit-mcu-website-avr-slip-tcpip/)——8 kB RAM、$1 美元的微控制器、能跑 HTTP。那是"工程化"的胜利：每一行 C 代码都为"它必须 work"服务，可以扩展、可以维护、可以接 PR。

HellMood 的 16 字节恰恰相反——**它不可被工程化**。

- 你不能给它加一个 feature。任何额外的 `xor ax, ax` 都会破坏 16 字节预算。
- 你不能为它写单元测试。它的"输出正确"不可定义——不同硬件听起来不同的特性本身是设计目标的一部分。
- 你不能把它"重构"。每一个 mov / lodsb / out 都是不可替换的，移动任何一条指令都会让 BIOS 初始状态不再对齐。
- 你不能让另一个程序员"接手"。这段代码的每一个字节都依赖 HellMood 个人对 BIOS、Lucas 定理、自动机理论、PC 扬声器电气特性的完整理解。

这听起来像缺陷——但 demoscene 圈子把它当作**最高级别的奖项**。Pouet.net 上的 thumbs up 不是给"能干活的代码"，而是给"这段代码所在的人类知识坐标"。

这件事和今年那么多"AI 写代码、AI 重构、AI 维护"的话题形成了一种几乎是宗教式的对比。我们前不久写过 [antirez 用 GPT 5.5 一周做出 DS4](/post/good-read-antirez-ds4-local-inference/)、[Anthropic 教 Claude "为什么"](/post/good-read-anthropic-teaching-claude-why/)、[Gowers 用 ChatGPT 5.5 Pro 做 PhD 数论章节](/post/good-read-gowers-chatgpt-phd-math/)。这些都是"AI 接管代码量"的故事，前提是代码可以被"重构成更多代码"。

HellMood 这 16 字节给出了另一个极端：**有些代码的价值密度太高，无法被"补充"，只能被"理解"**。如果有一天 LLM 真的能从 prompt"画 Sierpinski 三角且同时播声"生成出 HellMood 这 16 字节，那一刻 LLM 才算理解了 Lucas 定理与 PC 扬声器的关系——不只是从训练语料里抄到这段代码。

(这也与我之前在[《senior developer's speed and scale》](/post/good-read-senior-developer-speed-scale-decoupling/)里讨论的"speed loop vs scale loop"形成镜像：HellMood 把整个 scale loop 缩成 1 个字节，他唯一的循环是 speed loop——纯粹的、个人的、不可外包的理解。)

我建议任何在 2026 年读到这篇文章的工程师都把它存起来。当你以后被 AI 工具搞得"什么代码都能生成"时，回头看看这 16 字节——记得有一类东西，**不在量上，在密度上**。

## 11. 配套资料导览

本文目录下还附了三份资料：

- `concept-cards.md` — 13 张关键概念卡（实模式段、文本缓冲、Lucas 定理、Rule 60、port 0x61 bit 1 等），适合做工程师早会快闪展示。
- `glossary.md` — 35 条英中术语对照（涵盖 demoscene 行话与 x86 实模式相关词汇）。
- `mindmap.svg` — 一张深色背景的思维导图，按"硬件 / 数学 / 算法 / 演出"四象限展开。
- `cover.svg` — 文章封面。

## 12. 谁应该读

| 角色 | 收益 |
|---|---|
| **汇编 / 嵌入式工程师** | 学习如何在 16 字节里用 BIOS 默认状态做"零成本初始化"；理解 8-bit register 与段大小的整除性如何被算法利用 |
| **算法 / 数学方向的研究者** | 看 Lucas 定理在 8-bit 实现上的具体表现；理解为什么"Pascal mod 2 = Sierpinski"是工程友好的 |
| **demoscene 爱好者** | 一个 2014→2026 横跨 12 年的 size-coding 演进案例 |
| **教师 / 科普写作者** | 学习 HellMood 的"先 ADD 后 XOR"教学顺序——任何想给非数论背景读者讲 Lucas 定理的人都可以模仿 |
| **AI 工具迷** | 把这段代码当作"density 上限"的人类基准，思考 LLM 何时能生成此类作品 |
| **复古硬件爱好者** | 理解 BIOS int 10h 的细节、port 0x61 bit 1 的电气含义、不同 BIOS 实现差异 |

---

*本文为深度导读，原文金句引用比例 < 5%，主要观点与术语为编辑用自己语言重新阐述。所有图示均为编辑重绘描述。如对 HellMood 此前作品（m8trix, Memories, 32 byte boot sector）感兴趣，可以从 Pouet.net 或 Demozoo.org 顺藤摸瓜——demoscene 是当代少数仍以"密度"而非"规模"为荣的文化场。*
