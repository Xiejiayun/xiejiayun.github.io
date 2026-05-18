---
title: "【好文共赏】PSX 的爆炸为什么比 N64 漂亮：phoboslab 用一块 32-bit 临时画布，把 30 年前的硬件 bug 在 3.1 毫秒里补完"
description: "Dominic Szablewski 把 N64 RDP 缺失的 saturating add 拆给你看：临时画布 + RSP 微码 + fog alpha 的三重 hack，让 1996 年的卡带机也能渲染'看起来真的发光'的爆炸特效。"
date: 2026-05-18
slug: "good-read-phoboslab-n64-additive-blending"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 硬件
    - 图形编程
    - 复古计算
    - 游戏开发
    - N64
draft: false
---

> 📌 **好文共赏 \| Editor's Pick**
> 
> **原文**：[Additive Blending on the Nintendo 64](https://phoboslab.org/log/2026/05/n64-additive-blending) · phoboslab.org
> **作者**：Dominic Szablewski（QOI / QOA 图像音频格式作者、Impact.js 游戏引擎作者、wipEout 重写者）
> **发布**：2026-05-04 \| **阅读时长**：约 12 分钟
> **多模评分**：Opus 8.7 / Sonnet 8.5 / Gemini 8.6（综合 **8.6 / 10**）
> 
> **一句话推荐**：你第一次玩《星际火狐 64》时就隐隐觉得"爆炸怎么像贴上去的纸片"——三十年后，phoboslab 用三段代码、一块 32-bit 中间画布和 RSP 微码，把这个直觉变成了一个可量化、可修复的硬件 bug。

---

## 0. 为什么我们要把这篇文章列进"好文共赏"

打开 YouTube 随手搜 *PSX vs N64 explosions*，你会得到几十个对比视频：1998 年的 *Silent Bomber* 在 PlayStation 上喷出一团真正像光的爆炸；1997 年的 *Star Fox 64* 在更贵、更晚、号称更先进的 Nintendo 64 上，喷出一片像剪纸贴上去的"亮色块"。

二十多年来，这事被无数玩家讨论过、无数模拟器开发者抱怨过，但从来没有一篇博客把这个"美术差异"一路拆到 RDP 寄存器、再一路拆到一个可以在真机上跑出来的修复方案。Dominic Szablewski 这篇 2026 年 5 月发的 *Additive Blending on the Nintendo 64*，做了那件事。

它的篇幅不长——大约 2,000 字、四段 C 代码、两段 RDP 寄存器配置——但它把一个看似艺术风格的差异，逐层归约到了一个具体的、可命名的硬件缺陷：**N64 的 RDP blender 在做颜色加法时不 clamp，会让 R / G / B 通道独立 wrap-around，把"过亮"渲染成"突然变暗"**。然后给出一套在 2026 年现代 N64 工具链（libdragon + RSPL + RSP 微码）下可以编译进真卡的 workaround。

这篇文章在"好文共赏"里之所以重要，不在于它讲了一段冷僻的硬件史，而在于它**示范了一种思考方式**：当你接受了"风格就是这样"的解释二十年之后，依然有人愿意坐下来、把寄存器逐位读完、把 RSP 微码写一遍——然后把"风格"重新拆回工程。

> 原文：*"The reason is additive blending! Or rather, in the N64 case, the lack thereof. While the N64 actually did support additive blending, it was practically unusable."*

这一句几乎是整篇文章的论点摘要：**N64 不是没有加色混合，而是把它做成了一个工程上无法使用的版本**。这种"近在咫尺却差最后一步"的硬件遗憾，几乎是九十年代家用机黄金时代的母题。

（这点与我之前推过的[《把 Atari 音乐塞进 Amiga 的协处理器：Leonard 用 PAULA 的一处反转，在 0% CPU 下让 1985 年的两块芯片对唱》](/post/good-read-leonard-ym-paula-amiga-zero-cpu/) 是同一类故事——都是"老硬件里那个差一步就完美的设计，被三十年后的人补完"。）

---

## 1. 先说结论：一张表读懂 PSX 与 N64 的差异

| 维度 | PlayStation (PSX) | Nintendo 64 (N64) |
|---|---|---|
| 像素格式 | 16-bit (5-5-5 + 1 透明位) | 16-bit (5-5-5-1) 或 32-bit (8-8-8-8) |
| 加色混合 | `src + dst`，**硬件自动 clamp 到 255** | `(P*A) + (Q*B)`，**Color Combiner 可配置但不 clamp** |
| 失败模式 | 颜色饱和、爆炸"过曝"成纯白 | 通道独立溢出、爆炸**反而突然变黑** |
| 后果 | 爆炸像"光" | 爆炸像"贴片" |
| 修复成本 | 0（硬件免费送） | 需要绕：32-bit 中间帧缓冲 + RSP 微码 shuffle |

注意右下角那个"突然变黑"——这就是问题的核心。在 PSX 上，溢出意味着"更亮"；在 N64 上，溢出意味着 `(R + G + B) mod 256`，蓝色通道从 396 wrap 回 140，颜色直接跳到对立面，整团爆炸看上去像被人按了一下反色键。

---

## 2. PSX 的便宜：硬件免费送的饱和算术

PSX 的 GPU 支持四种混合模式：

```
0: (src + dst) / 2          // 半透明
1: src + dst                // 加色（爆炸/光/魔法）
2: dst - src                // 减色（阴影）
3: dst + src / 4            // 微弱加色
```

每一种都附赠一件事：**对结果做饱和钳位**（saturation clamp）。也就是说，当你把一个像素的蓝色值从 170 加到 396 时，硬件会替你直接写回 255，而不是让它绕到 140。

这件事的工程价值大到几乎反直觉。在所有"音频混合 / 颜色混合 / 信号叠加"的场景里，你都希望"溢出 = 失真但语义可读"——一束太亮的光看起来是白的，一段太响的鼓声听起来是削顶的——而绝不希望"溢出 = 黑色 / 反相 / 突然安静"。前者只是丑，后者是 bug。

> 原文：*"Drawing a sprite over a scene can only ever make it brighter, never darker. Perfect for explosions, plasma beams and magic spells."*

这恰好是为什么 PSX 时代的爆炸特效会"看起来像光"——硬件免费送了**单调性**：叠加只会让画面更亮，永远不会让它变暗。**单调性**是一种廉价但极强的视觉直觉，它让一束过曝的火焰自动落在"亮"的语义类里，而不是落到"莫名其妙的黑斑"里。

HN 评论区里 [gblargg](https://news.ycombinator.com/item?id=48149259) 一句话点透了这件事的普适性：

> 原文（HN 评论）：*"It's the same issue you encounter with audio mixing. You have to clamp out-of-range values, even though they don't occur a lot. If you don't you get awful artifacts, and have to lower everything so that it can never overflow your range."*

整个 90 年代的低端图形 / 音频硬件设计史，几乎都可以用一句话总结：**送 clamp 的赢，不送的输**。Sega Saturn 的四边形渲染、N64 的不 clamp blender、早期 S3 ViRGE 的缺乏 additive，全都掉在同一个坑里。

---

## 3. N64 的"近在咫尺却差最后一步"

N64 的 RDP（Reality Display Processor）从设计上其实比 PSX GPU 灵活得多。它有一个叫 **Color Combiner** 的可编程小单元，结构类似 OpenGL 的 `glBlendFunc()`，可以让你写出 `(P * A) + (Q * B)` 形式的任意线性组合。在 libdragon 的宏里看起来就是：

```c
RDPQ_BLENDER(( IN_RGB, IN_ALPHA, MEMORY_RGB, ONE ))
// 含义：output = in_rgb * in_alpha + memory_rgb * 1
```

理论上这比 PSX 的四档固定模式要好得多——你能调出 alpha 加权、可调亮度的加色、各种花式混合。但**实际不能用**。原因只有一行：

> 原文：*"The problem is, the RDP doesn't clamp the result."*

也就是说，当蓝色通道算到 396 时，RDP 不会替你 clamp 到 255，而是会让你拿到 `396 mod 256 = 140`。一个本该过曝的爆炸，瞬间被映射成一团暗色噪点。

Color Combiner 越灵活，反而越容易踩到这个坑：任何一段需要"叠加多个明亮 sprite"的场景——爆炸、激光、魔法、火焰、雪花、屏幕泛光——都会被这条 wrap-around 规则当场报废。

这正是九十年代游戏机最经典的硬件遗憾：**N64 用一颗更现代的 RDP 替换了 PSX 的固定功能管线，但忘了把"饱和算术"这一颗最廉价的晶体管一起送上**。

（顺便：HN 用户 *rasz* 指出，同时代的 S3 ViRGE、Matrox Mystique、NEC PowerVR PCX1/2 也都不支持 additive blending。N64 不是唯一一个掉坑的——但它是最痛的那个，因为它本来可以做到。）

---

## 4. phoboslab 的解法：把 saturation 从"硬件功能"变成"管线 trick"

文章后半段的 hack 优雅到值得每个写图形管线的人收藏。**它不依赖任何硬件改动，只靠重新解读现有的 RDP 寄存器和 RSP 微码**。三步：

### Step 1: 把所有颜色降到 1/8 强度，再渲染到 32-bit 临时画布

直觉是这样的：既然 RDP 不 clamp，那就**给它一块永远不会溢出的画布**——把帧缓冲从 16-bit (RGBA 5551) 升到 32-bit (RGBA 8888)，每个通道留 8 位空间，等于把"溢出预算"提高了 8 倍。

但还不够。再叠几个爆炸，8-bit 通道也会满。怎么办？**在渲染时就把每个 sprite 的颜色乘 1/8**：

```c
// 借用 fog alpha 寄存器，把它当作"全局亮度缩放因子"
rdpq_set_fog_color(RGBA32(0, 0, 0, 256/8));
rdpq_mode_blender(RDPQ_BLENDER((IN_RGB, FOG_ALPHA, MEMORY_RGB, ONE)));
```

这一行是整篇文章最秀的地方。`FOG_ALPHA` 在 RDP 设计里本来是给"远处雾化"用的；phoboslab 直接把它当成"每个 sprite 全局乘 1/8 的硬连线乘法器"。**RDP 的可编程性不是用来做什么新功能，而是用来把硬件免费的乘法器借去做别的事**——这是 demoscene 思维方式的精髓。

### Step 2: 用 RSP 微码把 32-bit 画布塞回 16-bit 显示帧

32-bit 画布只是临时草稿，最终输出还得回到 16-bit 才能上显示器。这一步需要做两件事：

1. **Clamp**：每个 8-bit 通道如果超过 31（5-bit 范围上限）就压成 31；
2. **Pack**：5+5+5+1 重新打包成 16-bit。

用 CPU 跑这件事的代价是 **70 ms / 帧**——意味着帧率被打到 14 FPS 以下，整张游戏卡报废。

但 N64 上还有一颗叫 RSP（Reality Signal Processor）的 128-bit 向量协处理器，原本是给顶点变换用的。phoboslab 在 N64Brew 社区的 HailToDodongo 帮助下，用一种叫 **RSPL** 的 C-like 微码语言写了一段 8 路并行 SIMD shuffle，把这件事压到 **3.1 ms / 帧**——**23 倍的加速**，刚好留出 30 fps 预算给真正的游戏逻辑。

> 原文：*"The RSP's 128bit vector instructions can process 8 pixels at a time. With some help from HailToDodongo on the #N64Brew discord optimizing the GPU microcode, this now runs in about 3.1ms for the whole frame!"*

### Step 3: 接受 N64 的真正代价——带宽

这套方案在算法上是优雅的，但工程代价不为零：**RDP 写 32-bit 画布的带宽是写 16-bit 的两倍**。而 N64 最臭名昭著的瓶颈恰好就是 RDRAM 带宽——这也是为什么 90% 的 N64 游戏选择 16-bit 输出。

phoboslab 也给出了下一步优化思路：**只对需要加色混合的 sprite 走 32-bit 路径**，其余正常 16-bit，最后 RSP 在合成阶段做按需 alpha 合成。这种"按 sprite 选择 framebuffer 精度"的混合管线思路，本质上是把现代 GPU 的 *multiple render target + tone mapping* 倒推回 N64。

---

## 5. 一个被忽视的副产品：N64 终于可以做 HDR

如果你慢慢咀嚼 phoboslab 的这套 hack，会发现它给 N64 顺手送来了一件 1996 年不存在的东西：**伪 HDR 渲染管线**。

- 32-bit 中间画布提供了**线性高动态范围**——每个通道 0..2040（255 × 8）；
- 1/8 缩放 + 后续 clamp 等价于**一次 tone mapping**；
- RSP 微码可以做更复杂的 tone curve、bloom、曝光控制。

HN 评论区里的 *amlib* 链接了一个叫 [Tiny3D](https://www.youtube.com/watch?v=XP8g2ngHftY) 的 N64 homebrew，里面已经在用类似思路实现 HDR + Bloom + Post-Processing。也就是说，**phoboslab 这篇文章其实是一份"N64 现代渲染管线"的入门解释**，藏在一个"修复 1996 年硬件 bug"的标题之下。

这种"用现代工具给老硬件补一种它本来就该有的能力"的活，在 demoscene 圈一直是显学；但用一篇 2,000 字、配齐 C 代码和 RDP 寄存器配置的博客把它写清楚，难度比想象中高得多。

---

## 6. 工具链的进步：2026 年写 N64 比 1996 年容易

文章里有一段话很容易被略过，但它其实是整篇文章的"时代背景"：

> 原文：*"Modern tooling for N64 development is phenomenal. While it helps to have some understanding of assembly, you don't have to write MIPS assembly by hand anymore."*

2026 年的 N64 开发栈大致是这样的：

- **libdragon** — 开源的现代 N64 SDK，提供 C API（替代 Nintendo 闭源的 libultra）；
- **RDPQ** — libdragon 的 RDP 命令队列抽象，把 Color Combiner / Blender 用宏暴露出来；
- **RSPL** — HailToDodongo 写的 C-like 微码语言，编译到 RSP 的 MIPS+vector ISA；
- **N64Brew Discord** — 一个由全球几十位逆向工程师组成的社区，常年研究 N64 内部细节。

这套工具链让"写 N64 卡带"这件事，从需要任天堂 NDA + 工作站的特权活动，变成了一个周末就能上手的爱好。phoboslab 这种"业余写一篇博客 + Github 发个 demo"的工作流，三十年前是完全不可能的。

（这点与我此前推的[《1 美元、8 kB RAM、一根 USB 串口线：Maurycy 把整个 TCP/IP 栈塞进 AVR64DD32》](/post/good-read-8bit-mcu-website-avr-slip-tcpip/)是同一类时代信号——**现代开源工具链正在把"老硬件玩出新花样"的门槛降到周末项目级别**。）

文章中的 trivia 段落还藏了一个 [copypasta 玩笑](https://en.wikipedia.org/wiki/GNU/Linux_naming_controversy)：

> 原文：*"What is commonly referred to as 'GPU microcode' in the context of the N64 is in fact, MIPS/assembly that runs on the RSP, or as I've recently taken to calling it, MIPS plus assembly."*

这是 Stallman *GNU/Linux* 名梗的硬件版翻拍——既是技术澄清（RSP 不是真正的 GPU，是带 SIMD 的 MIPS 协处理器），也是网络文化致敬。

---

## 7. 一个更深的观察：可编程性 vs 默认正确性

我读完这篇文章后最想拿出来谈的，是一个**架构设计原则**：

> **"可编程"不能弥补"默认错误"。**

PSX GPU 的混合模式只有四种，但每一种都附赠饱和钳位——它的可编程性差，默认正确性满分。
N64 RDP 的 Color Combiner 可以表达任意线性组合，但默认行为是 wrap-around——它的可编程性强，默认正确性零分。

结果是什么？PSX 上几乎所有游戏都用对了 additive；N64 上几乎所有游戏都**绕开**了 additive。整整一代游戏开发者用脚投了票：在工程压力下，"可配置但容易出错"几乎一定输给"不可配置但永远对"。

这件事在今天的软件世界里有非常多对应物：

- C 的整数溢出 UB / Rust 的 `wrapping_add` vs `saturating_add` 显式选择；
- HTTP/2 的可协商性（HPACK、流控制）vs HTTP/1.1 的固定语义；
- Kubernetes 的"几乎万能但默认坑"vs Heroku 的"不能折腾但默认对"；
- 大模型推理框架的"上百个旋钮"vs 闭源 API 的"一个 endpoint"。

每一对里，PSX 的影子都在重复出现。**默认行为是硬件设计师送给所有用户的免费保险；把保险拆掉换可编程性，往往是一笔亏本生意**——除非你的目标用户有能力（且有时间）补回那份保险。

phoboslab 这篇文章的隐藏价值，就是把这条原则用一段三十年前的硬件做了**最直观的演示**：你看，N64 当年那条没省下的钳位电路，最后是怎么靠 2026 年的 RSP 微码替它补完的。

（这点与我之前推过的[《资深开发者为何"说不清"自己的价值：Speed 与 Scale 的两个循环》](/post/good-read-senior-developer-speed-scale-decoupling/) 也呼应——优秀工程师的一大部分价值，正是"知道默认行为该是什么"。）

---

## 8. 编辑延伸思考：为什么这种"老硬件考古"在 2026 年突然集中爆发？

最近 14 天我们陆续推过：

- [Maurycy 把 TCP/IP 塞进 AVR64DD32](/post/good-read-8bit-mcu-website-avr-slip-tcpip/)（8-bit MCU 上跑完整 HTTP 服务器）
- [Leonard 用 PAULA 让 Atari 和 Amiga 在 0% CPU 下对唱](/post/good-read-leonard-ym-paula-amiga-zero-cpu/)（Amiga 协处理器逆向）
- [Scott Robinson 的 HCF 考古](/post/good-read-hcf-halt-and-catch-fire-history/)（1977 年 BYTE 杂志一路追到 x86 模糊测试）
- [Dmitry Grinberg 用 41,000 字给 Pixter 做完全保存](/post/good-read-dmitry-grinberg-pixter-full-preservation/)（Fisher-Price 童年掌机硬件考古）
- [Xbox 360 黑客 Ryan Miceli 拆解 4 家 HDD/SSD 固件](/post/good-read-hdd-firmware-hacking-jtag-ida/)（硬盘控制器逆向）

——再加上今天这篇 phoboslab N64。短短两周里 HN 头条已经积累了六篇"硬件考古 / 老芯片新玩法"的深度长文。这不是偶然。我看到的至少有三个交错的原因：

**1. AI 写代码的速度倒逼"领域知识"重新升值。** 当 LLM 可以一秒钟生成一千行 React，**那些 LLM 训练集里几乎没有的领域**——N64 RDP 寄存器、Amiga PAULA、Pixter 屏幕扫描时序——反而成了人类工程师残留的稀缺资产。这些主题在 2023 年看着像怀旧，到 2026 年开始像"反卷护城河"。

**2. 现代开源工具链终于追上了老硬件。** libdragon、RSPL、Ghidra、Binary Ninja、便宜的逻辑分析仪、Lattice 开源 FPGA 工具链——把"研究老硬件"的入场费从大学实验室降到了周末项目。

**3. 一代人开始拥有时间和钱。** 90 年代玩 PSX / N64 的小孩现在四十多岁，是工程师里购买力最强的一批，且开始有"用一个周末解决童年遗憾"的奢侈。phoboslab 自己就是这条人口曲线上典型的一点。

把这三件事叠在一起，"硬件考古"在 2026 年呈现集中爆发，是合理的。我会赌它在未来 12-24 个月里成为技术博客圈最稳定、最高质量的内容类目之一——比 AI 应用层博客的半衰期长得多。

---

## 9. 延伸阅读图谱

### Dominic Szablewski 自己的其他代表作

1. [**The QOI File Format Specification**](https://phoboslab.org/log/2021/12/qoi-specification) (2021) — QOI 是一种 20-50× 比 PNG 快、300 行 C 代码的无损图片格式。这篇是规范定稿。
2. [**QOA: Time Domain Audio Compression at 3.2 bits per Sample**](https://phoboslab.org/log/2023/02/qoa-time-domain-audio-compression) (2023) — QOA 是 QOI 的音频版，400 行 C 写完一种快速有损压缩。
3. [**Rewriting wipEout**](https://phoboslab.org/log/2023/08/rewriting-wipeout) (2023) — 把 1995 年 Psygnosis 的 PSX 经典 *wipEout* 几乎完整重写成现代 C / WebGL。
4. [**Porting my JavaScript Game Engine to C for No Reason**](https://phoboslab.org/log/2024/08/high_impact) (2024) — Impact.js 的 C 重写，high_impact 引擎诞生记。
5. [**A Nintendo 64 Rumble Pak so Bad that it's Good**](https://phoboslab.org/log/2026/03/n64-rumble-pak) (2026-03) — 同一系列上一篇，逆向一个不合规的 Rumble Pak，是这篇 additive blending 的姊妹篇。

### 同主题硬件考古 / 老机器新玩法

6. [Libdragon — 现代开源 N64 SDK](https://libdragon.dev/)
7. [RSPL — HailToDodongo 的 N64 RSP 微码 C-like 语言](https://github.com/HailToDodongo/rspl)
8. [Tiny3D — N64 Homebrew HDR & Bloom 演示](https://www.youtube.com/watch?v=XP8g2ngHftY)
9. [N64Brew Wiki — N64 硬件细节社区档案](https://n64brew.dev/wiki/Main_Page)
10. [Saturation Arithmetic — Wikipedia](https://en.wikipedia.org/wiki/Saturation_arithmetic)（理论背景，文章里那张表的数学基础）

### 反方 / 不同视角

11. [HN 上 *applfanboysbgon* 的评论](https://news.ycombinator.com/item?id=48149259) — "*Star Fox 64* 的爆炸特效更符合游戏整体艺术风格，硬件限制反而是 N64 美学的一部分。"——这其实是个值得正眼看的观点：技术限制有时塑造了风格，而非只是限制了它。任天堂的 *Wind Waker* 美学就是另一个例子。
12. [HN 上 *rasz* 的评论](https://news.ycombinator.com/item?id=48149259) — 提醒大家 90 年代其实绝大多数 3D 加速卡（S3 ViRGE, Matrox Mystique, NEC PowerVR PCX1/2）都没有 additive blending，3dfx Voodoo 才是异类。N64 不是孤例。

### 相关论文 / 长文

13. [The Nintendo 64 Programming Manual (1996, 任天堂)](https://ultra64.ca/files/documentation/online-manuals/man/index.html) — 官方文档，理解 RDP 的权威来源。
14. [N64 GPU programming on Hackmd by HailToDodongo](https://hackmd.io/) — 现代 N64 微码教程系列。
15. [《The Computer Graphics Manual》by David Salomon](https://link.springer.com/book/10.1007/978-0-85729-886-7) — 第 17 章详细讲了 alpha blending / saturation 的算法基础。

---

## 10. 谁应该读这篇文章

- **图形 / 游戏开发者**：你会重新理解"为什么 90% 的渲染管线在出错时表现得像 PSX 而不是 N64"——saturation 是 modern GPU 的默认承诺，但它不是免费的。
- **硬件 / 嵌入式工程师**：值得学习 phoboslab 怎么把 "fog alpha 寄存器" 当成 "全局亮度乘法器" 来用——**在资源受限的硬件上，所有寄存器都是潜在的多用途资源**。
- **写技术博客的人**：这是一份很好的"用 2000 字讲清一件复杂事"的范文。开头钩子（爆炸为什么不一样）、归约（到一个具体硬件 bug）、解法（三步管线）、结果（量化加速比）、延伸（N64 HDR），结构典范。
- **AI 时代担心被淘汰的资深工程师**：注意他选择研究的领域里几乎没有 LLM 训练数据——RDP 寄存器配置、RSP 微码、libdragon API。**这是 2026 年人类工程师的"反训练数据"价值锚点**。

---

## 11. 配套资料导览

本文配套生成的资料文件：

- **`cover.svg`** — 文章封面，深色背景 + N64 / PSX 双爆炸示意 + 关键词
- **`mindmap.svg`** — 思维导图，从"为什么 PSX 爆炸更亮"展开到 RDP / RSP / HDR 五条主干
- **`concept-cards.md`** — 12 张关键概念卡片：饱和算术、Color Combiner、RDPQ_BLENDER、Fog Alpha hack、RSP 微码、libdragon、RSPL、QOI/QOA、wipEout 重写、N64Brew、PAULA 反转、可编程性 vs 默认正确性
- **`glossary.md`** — 35 条英中术语对照表（RDP / RSP / RDRAM / saturating add / wrap-around / Color Combiner / framebuffer / tone mapping 等）

---

## 结语

如果你只读最后一段：

PSX 的爆炸看起来像光，因为它的 GPU 在 1994 年免费送了你一个"溢出 = 更亮"的硬件承诺；N64 的爆炸看起来像贴片，因为它在 1996 年用更灵活的 Color Combiner 换掉了那个免费承诺，并把帐单留给了未来三十年的开发者去付。

2026 年的 phoboslab，用 32-bit 中间画布 + RSP 微码 + 借用的 fog alpha 寄存器，**把这张帐单结清了**。

> 原文：*"Still, this technique worked out better than I expected. It's certainly good enough for some applications."*

工程上，这是一段"good enough"的总结。
文化上，这是一封写给 1996 年那块卡带的迟到三十年的回信。

——这就是为什么它值得在 2026 年 5 月的"好文共赏"里占一篇。
