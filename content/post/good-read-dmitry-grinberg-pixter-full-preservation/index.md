---
title: '【好文共赏】把 Fisher-Price 的童年盲盒一颗颗剥光：Dmitry Grinberg 用 41,000 字给一整代儿童玩具做了"完全保存"'
description: 'Dmitry Grinberg 第一次完整逆向了 2000–2005 年代 Fisher-Price/Mattel 全系 Pixter 玩具——从 ARM7 无 cache 无 MMU 的最小 SoC，到一颗用 R-2R + 比较器 + 8 个 GPIO 拼出来的"无 ADC 触摸屏"，再到三套自创字节码 VM、两条奇形怪状的总线、以及那枚仍然不肯出场的 SPL133A 6502。这是一篇近 4 万字的硬件考古学。'
date: 2026-05-18
slug: "good-read-dmitry-grinberg-pixter-full-preservation"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 嵌入式逆向
    - 硬件考古
    - 数字保存
    - ARM7
    - 6502
    - 字节码 VM
    - 触摸屏
    - 玩具计算机
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> **原文**：[Fully Preserving Fisher-Price Pixter](https://dmitry.gr/?r=05.Projects&proj=37.%20Pixter) · 作者 [Dmitry Grinberg](https://dmitry.gr/) · 发布 2026-05-11 · 全文约 41,000 词 / 估计阅读 4–6 小时
>
> **多模评分（综合 9.6 / 10）**：Opus 9.6 · Sonnet 9.5（一致认为是年度级别的硬件考古） · Gemini 9.6（"逆向工程教科书"）
>
> **一句话推荐**：当一位写过"在 8 位 AVR 上跑 Linux""三颗 8 引脚芯片组装 Linux 计算机""把 PalmOS 移植到 ARM"的人，决定花两年时间把一台 2003 年的 80×80 儿童画图机 *从黑色环氧 blob 一直拆到自创 16-bit 虚拟机的最后一条 opcode*——你会得到一篇连 ROM 都被仔细描出 chip select 边界的、近 4 万字的工程考古史诗。

## 1. 为什么值得读

绝大多数"逆向工程文章"长这样：买一块开发板，逆几个寄存器，写几张博客图，结束。Dmitry Grinberg 的 Pixter 系列不是。它是一份**完整保存（complete preservation）**——他亲自定义了文件格式、写了反汇编器、把每一款 SoC 的非公开行为塞进了自己十多年来一直在打磨的 ARM 模拟器 `uARM`、还为没人见过的 6502 衍生体重新实现了一台 6502 模拟器 `uM23`，外加 PalmOS 的 launcher 与 IR 通讯桥。最后所有结果上传 Internet Archive、补回 Wikipedia 条目。

更难得的是它的"诚实"。Grinberg 把每一条死胡同——"我以为是 Forth"、"我以为是某种早期 16 位架构"、"我以为可以软地夹住芯片的 RESET 让总线浮空"——逐一记录。这正是与那种博客式"看，我做出来了"完全不同的工程师文体：**他让你跟着他思考。**

它和我们之前推荐过的两篇文章一起，构成了 2026 年"年度硬件考古"的连环画：
- [《给一块运行中的硬盘下断点：Ryan Miceli 拆解 4 家 HDD/SSD 固件》](/post/good-read-hdd-firmware-hacking-jtag-ida/) —— Xbox 360 黑客在企业级存储的 JTAG/IDA 上反复横跳；
- [《把 Atari 音乐塞进 Amiga 协处理器：Leonard 用 PAULA 一处反转，在 0% CPU 下让 1985 两块芯片对唱》](/post/good-read-leonard-ym-paula-amiga-zero-cpu/) —— 同样是"芯片层面的小细节救活了整段历史"。

但 Pixter 这一篇的尺度是另一个量级：它处理的是**一整代设备、一整代游戏卡、四种不同的 cartridge 总线、三套自创 VM、两颗仍未被命名的 SoC**。这不是"为了好玩"——这是为了把一段没有任何商业价值、却凝结了 2000 年代中国南方代工链全部"省钱套路"的工业历史，从 eBay 和 STAS（Stuck-In-The-Attic-Storage）里抢救出来。

> 原文："Previously, a few places online mentioned that 'THERE ARE CURRENTLY NO EMULATORS FOR THIS DEVICE OR PLATFORM. ANY CLAIMS TO OFFER THEM ARE SCAMS!' This is no longer true, I am happy to report."

这一句话现在是真的。这就是这篇文章的重量。

## 2. Pixter 到底是什么？为什么没人记得？

2000 年 Fisher-Price 推出 Pixter——80×80 单色触摸屏、塑料外壳、含 stylus 的儿童画图机；首发圣诞档卖出五十万台。后续衍生：

| 设备 | 年份 | 屏幕 | SoC | 卡带 |
|---|---|---|---|---|
| Pixter (Classic) | 2000 | 80×80 单色 | **未知 6502 衍生**（疑似 Sunplus SPL133A） | BEX 总线 + EEPROM |
| Pixter Plus | 2002 | 80×80 单色 | 同上 | 同上 |
| Pixter 2.0 | 2003 | 80×80 单色 | 同上 + 红外 | 同上 |
| **Pixter Color** | **2003** | **160×160 彩色** | **Sharp LH75411 (ARM7TDMI)** | **新接口，自带向后兼容 adapter** |
| Pixter Multimedia | 2005 | 160×160 更好的屏 | Sharp LH79524 (ARM7TDMI) | Color 接口 + NAND 卡 |
| Pixter Pocket | 后期 | 单色 + D-pad | Sunplus **SPL130A** (6502) | 不可换卡 |

整个家族最迷人之处是**所有图像状态跨设备兼容**——你可以在"Cool Wheels"里画一辆汽车，存到内置存储，拔卡，插上"Barbie Fashion Show"，把 Barbie 放进你的车里。这套"作品在卡带之间漂移"的设计 25 年后听起来像 Apple Continuity，但实现得用 EEPROM 和一颗 BJT 抠出来。

到 2026 年，所有这些设备已经从市场上消失。Wikipedia 条目错漏，没人知道总共有几款游戏（Grinberg 亲自考据后修正：Pixter Color 32 款，Multimedia 独占 9 款，Classic 系列 25 款）。互联网上甚至有人挂出"任何声称提供 Pixter 模拟器的都是诈骗"的警告。**Grinberg 的工作让这一切的"未知"在一夜之间消失。**

## 3. 第一颗骨头：Sharp LH75411，史上最小化的 ARM7

打开 Pixter Color，主板上只有：主 SoC、一颗 128KB 的 x16 SRAM、两颗 chip-on-board 黑色环氧 blob。Grinberg 用一段几乎令人心疼的散文描述了 Sharp 这颗 SoC：

> 原文："This is the most minimal ARM7 instantiation I've ever seen. Everything that was optional was excluded, everything that could be sized was configured in the most minimal configuration. ... There is no MMU in this SoC. ... There is no MPU! There is also no alignment checking, no cp15 coprocessor, no ... anything that is optional at all. Just a chip full of 'no'."

ARM7TDMI 在 2003 年是个再普通不过的核心，但 ARM 架构的优雅之处在于它允许集成方"加什么减什么"。Sharp 在 LH75411 上把这件事推到了极限：

- **没有 cache**：所有取指都直接打到总线；
- **没有 MMU**：意味着异常向量必须落在 0x00000000，等于把 NULL 解引用变成"读到合法指令"；
- **没有 MPU**：连"用 supervisor 保护一下零地址"都不行；
- **ROM 是 16-bit 总线、SRAM 是 16-bit + 1 wait state**：取一个 32-bit ARM 指令要两次总线周期 × 3 cycle/次。

这套设计逼出的两个直接后果：(1) ROM 里几乎全是 **Thumb-16** 指令，与 Game Boy Advance 程序员同病相怜；(2) 程序员能把这台机器搞死却毫无知觉——任何越界、对齐错误、空指针访问都会"看起来正常"地继续运行。

但 Grinberg 真正想告诉你的是更深一层的事：**这颗 SoC 不是"差"，它是"被精确削到了能跑 80×80 触摸屏儿童玩具的最小成本曲线上"**。每一处省略——cache、MMU、MPU、cp15——都对应着 Sharp 与 Fisher-Price 之间的某次 BOM 谈判。这种"用工程文本反推商业谈判"的能力，是 Grinberg 写作里始终最迷人的部分。

## 4. 第二颗骨头：那个不是 ARM 代码的 ROM

Grinberg 干净地把游戏卡的 ROM 用 \$10 一颗的 60-pin 边缘连接器导出来，丢进 IDA Pro，然后……

> 原文："Out of the 2 megabytes of ROM, only about 300 bytes were recognizable ARM or thumb assembly. The rest either looked like bitmaps, or looked like nothing recognizable at all."

300 字节 ARM 代码，剩下 2 MB 是"看起来像位图，或者什么都不像"的数据。重新 dump 一次依然如此。换一张卡，ARM 代码更少。

唯一稳定的线索：**所有卡的 ROM 前几个字节都一样**——这一定是某种 header。

Grinberg 推论：游戏不是原生 ARM 代码，而是某种 bytecode。但这家公司没用任何已知 VM。他先把主机 ROM dump 出来（这个过程本身就是一段独立的小说——LH75411 在被 reset 时居然不释放 nOE/nWE/nCS0，于是得**焊掉三根脚**才能让总线浮空。"They say that every complex problem has a beautiful, elegant, easy to explain solution that ... does not work."）。dump 完成之后他在主机 ROM 里看到了真相：

> 原文："Fetch a 16-bit value, dispatch on the top few bits, there, dispatch on a few other bits, and there do some operations, jumping back to the beginning in an infinite loop. Some of the operations were weird - including unbalanced stack operations - pushes and pops. ... This thing implements a 16-bit virtual machine, being interpreted by the ROM code."

这是一台**手写的 16 位栈式虚拟机**，被一个无 cache 无 MMU 的 ARM7 解释执行。每条 opcode 大约 12 cycle，等效 ~4 MIPS。栈用的是宿主 ARM 的栈，没有溢出保护。Grinberg 用 Brutalism 来形容它："**This is what Brutalism would look like if it were software**"——粗暴、高效、毫无装饰。

更有趣的是 VM 的"考古证据"。某些 opcode 在处理 32-bit 数时会 pop 两个 16-bit 值再合并——但因为底层是 32-bit ARM，第二次 pop 完全被丢弃。Grinberg 推测：

- 这台 VM 最初是为某种 16-bit 处理器设计的；
- 在 Fisher-Price 切换到 ARM SoC 之后，工程师把每一条 16-bit push/pop 直接翻译成 32-bit 操作，但**不敢碰栈布局**，因为没人完整看过游戏代码；
- 于是 VM 变成了一个"卡在两种 word size 之间"的怪物，每次 push 都浪费 16 bit。

这就是技术债的化石形态。1996 年某个工程师做出的决定，2026 年还在你的 ROM 里压栈两次。

## 5. 第三颗骨头：用 8 个 GPIO + 比较器做 8-bit DAC，再做触摸屏

整篇文章里最令人捧腹的章节是 Pixter Classic 的电阻式触摸屏。"正确"的做法很常见：4 个 FET 控制 X/Y plate 的方向，ADC 采样 plate 上的电压。但 Pixter Classic 的 SoC 没有 ADC。

那怎么办？标准 hack 是用 **comparator + DAC**：让 DAC 输出一个不断变化的参考电压，看比较器什么时候翻转。但这颗 SoC 也没有 DAC——它只有 PWM，而 PWM 已经被音频用掉了。

> 原文："So... they used the 8 GPIOs of PortA in a R-2R configuration as a shitty low-quality 8-bit DAC."

**8 个 GPIO，配上 R-2R 电阻网络，凑出 8 位 DAC**。R-2R 电阻越多，电阻精度要求越高（7-bit 已经需要 0.5% 容差）。然后他们还把 FET 换成了更便宜的 BJT。BJT 的 V_BE 压降意味着 plate 上的实际电压范围不是 VCC→GND，而是依赖某颗具体晶体管的 V_BE——而 BJT 哪怕同批次产品 V_BE 也会差 0.1V，反映到屏幕上**就是 10 个像素的偏差**。

> 原文（Grinberg 的吐槽）："In a desire to cut more costs, they decided to save \$0.000001 per device and used the cheaper BJTs instead of FETs."

读到这里你会笑出来。但 Grinberg 真正想让你看到的是：**Pixter Classic 这条触摸屏链路是一个完整的"无 ADC 系统"的最小公约数**——从软件里的 successive approximation 算法、到硬件上的 R-2R + comparator、再到 BJT 容差被算进每个游戏的"校准"流程。这是工业级"用软件吃掉硬件成本"的标准范式，今天的 ESP32 玩家做温控时还在用。

（这点与我们之前推荐的 [《把车里的「告密者」物理拔除：一位安全工程师的 2024 RAV4 隐私手术》](/post/good-read-rav4-modem-gps-removal-car-privacy/) 中"软硬协同"的思路如出一辙——只是后者是拆掉某个零件，前者是用软件把零件**省掉**。）

## 6. 第四颗骨头：BEX 总线，一条假装是 SPI 的"chain bus"

Pixter Classic 的 cartridge 连接器只有十几根脚——远不够地址 + 数据 + 控制。Fisher-Price 的解法是 **BEX bus**：一种把多颗芯片串成 chain、用少量 GPIO 串行 shift 出地址和数据的协议。它既用在外部卡带，也用在内部保存档的 NOR flash 上——后者实际是同一条 BEX 链。

> 原文："The internal BEX bus used for the savegame NOR is the same one as the external one used to talk to Classic Carts. They used the chaining ability of the BEX chips to do this. I would probably have appreciated the cleverness of this approach a lot more if it had not taken me so long to finally figure it out."

为了模拟这一切，Grinberg 不得不在 `uM23` 里实现一个**watch-GPIO-toggles** 的子系统，跟着模拟 CPU 一条一条解码出 BEX 帧。这种 "我必须先看你在干什么、再决定这些 GPIO 翻转代表什么意思" 的逆向方式，是嵌入式逆向里最痛苦的一种——因为你不能直接信硬件文档（因为没有），也不能信"经验"（因为是 cost-cut 自由发挥）。

Pixter Multimedia 在此基础上又加了**NAND 卡**。正经设计会把 NAND 的 CLE/ALE 接到上层地址线，让 NAND 读写呈现为对几个固定地址的访问。但 Fisher-Price 把 CLE 接到 GPIO B6、ALE 接到 GPIO B7——再次用 bit-bang 软件接管。Grinberg 在写到这一段时已经放弃讽刺，只是用"these guys did not think of that"轻轻带过。

## 7. 完全保存：emulator + 文件格式 + Wikipedia + Internet Archive

文章的后半部分，Grinberg 把所有逆向成果"封装"成可被未来重现的形式：

1. **uARMpixter / uPixter**：在自己的 ARM 模拟器 `uARM` 上加 LH75411 与 LH79524 支持，模拟出 Pixter Color 与 Multimedia；
2. **uM23**：从零写一个 SPL13x 兼容的 6502 模拟器，跑通 Pixter Classic 与 Plus/2.0；
3. **自定义文件格式**：以 `PIXTER COLOR!!!` / `PIXTER CLASSIC!` / `PIXTER MULTI!!!` 为 magic，version byte = 0x01，含 melody chip 旋律列表（无符号 8-bit 22050Hz 采样）+ code 0 + code 1。文档里包含**所有 opcode 表**（Appendix A 是 Pixter Color VM 全部 12 大类指令、Appendix B 是 Classic VM 的 ALU + SPECIAL 操作）；
4. **ClassicDisasm / ColorDisasm**：两个反汇编器，喂入 dump 直接输出可读伪汇编；
5. **Internet Archive + Wikipedia**：把所有 dump 与文档上传 IA，修正 Wikipedia 的设备/游戏列表错误。

这是"保存"这个词的字面意义：**当所有真实硬件最终都进入垃圾填埋场时，任何一个未来人类——或 LLM——只要愿意，都能从这些文件里重建出 2003 年圣诞节早晨那台 Pixter Color 的全部行为**。这是另一种意义上的"代码即遗嘱"。

> 原文："I am here to present a complete historical preservation of all information pertaining to how Pixter devices work and almost all the games."

注意他用的词是 **preservation**，不是 reverse-engineering。区别在哪儿？逆向是"看懂"，保存是"让别人能再次执行"。Grinberg 自始至终都站在保存这一侧。

## 8. 没说完的故事：那颗 SPL133A，与一份失踪的"programming guide"

文章最后的开放问题——Pixter Pocket 的 SoC 是 SPL130A（labeled blob! 终于！），Grinberg 推测 Pixter Classic 用的应该是同族的 SPL133A，但他**找不到 SPL13x 的 programming guide**。他在文章里直白地写：

> 原文："I know the good old PUDN website had it, but sadly ... RIP PUDN. If you have a copy of the programming guide, please reach out."

PUDN 是中国 2000–2010 年代最重要的中文程序员资料站之一，托管了大量芯片厂内部文档与代码示例。它已于近年关闭。这一行的言外之意是：**21 世纪初期那一整代亚洲玩具供应链的技术文档，正在从互联网上彻底蒸发**。Grinberg 的工作能保存住 Pixter，是因为他还买得到二手机；但他无法保存这颗 SoC 的更细致行为，因为它的"母语"已经丢了。

这一点和我们[《2 小时审计、5 行代码：Project Zero 在 Pixel 10 VPU 驱动里挖出"圣杯级"内核漏洞》](/post/good-read-pixel-10-zero-click-vpu-kernel/) 里的某种焦虑遥相呼应——前者是"我们正在丢失代码考古的能力"，后者是"我们正在累积一种无人审计的代码"。它们其实是同一个问题：**复杂度的两端都在远离人类**。

## 9. 延伸阅读图谱

### 作者其他代表作（点评 + 推荐顺序）

| 文章 | 一句话推荐 |
|---|---|
| [Linux on an 8-bit micro (2012)](https://dmitry.gr/?r=05.Projects&proj=07.%20Linux%20on%208bit) | Grinberg 的"出道作"——在 8 位 AVR 上跑 Linux 2.6，靠的是写一个 ARM 模拟器跑在 AVR 上、再让 Linux 跑在模拟器里。读完你不会再说"Linux 太大"。 |
| [Linux/4004 (2024)](https://dmitry.gr/?r=05.Projects&proj=35.%20Linux4004) | 在 Intel 4004 这块 1971 年的 4-bit CPU 上跑 Linux。同样的模拟器套路，把"不可能"的下限再往下挪 8 位。 |
| [3-chip 8-pin Linux computer (2025)](https://dmitry.gr/?r=05.Projects&proj=36.%208pinLinux) | 只用三颗 8 引脚芯片 + 一些被动元件，组装一台可交互的 Linux 计算机。一种"硬件极简主义"的极致。 |
| [RePalm](https://dmitry.gr/?r=05.Projects&proj=27.%20rePalm) | 整套 PalmOS 在 ARM 上的逆向重实现。是这次 Pixter 项目的"前传"：Grinberg 之所以会动 Pixter，是为了在它上面跑 PalmOS。 |
| [Reverse Engineering an Unknown Microcontroller (2021)](https://dmitry.gr/?r=05.Projects&proj=30.%20Reverse%20Engineering%20an%20Unknown%20Microcontroller) | 一颗没有 datasheet 的 MCU。Grinberg 用本文同款方法学（探针、blob 推断、模拟器执行）做出完整文档。Pixter 这次的方法论原型。 |
| [I got almost all of my wishes granted with RP2350 (2024)](https://dmitry.gr/?r=06.%20Thoughts&proj=11.%20RP2350) | 在 RP2350 出来后他写下了 700 分的 HN 文章，从一个"长年与廉价 MCU 厮混的人"的视角谈树莓派的设计选择。是理解他审美的最快入口。 |

### 相关论文/博文（横向对比）

1. **Igor Skochinsky (Hex-Rays) — Intel ME/SPI flash reverse engineering** —— 同样是 chip-on-board 黑盒、同样要从总线信号里拼出协议；
2. **Travis Goodspeed — GoodFET & ChipWhisperer** —— "用 GPIO bit-bang 任何接口" 这条路的开创者之一；
3. **MAME 项目的 Sunplus core** —— Pixter Classic 与 Pocket 用的 SPL13x/SPL130A 在 MAME 里有部分实现，Grinberg 在文章里也呼吁有人把 Pixter 加入 MAME；
4. **Pierre Delaroque — preserving handheld electronic games** —— Mattel 之前的 LCD 游戏机保存项目，是 Pixter 之前最近似的工作；
5. **Sean "xobs" Cross — Fomu / on-chip silicon reverse** —— 把"自下而上理解 SoC"做到 FPGA 层面；
6. **Andrew "bunnie" Huang — Hardware Hacker** —— 整个文化的精神导师，深圳供应链分析的根；
7. **Travis Goodspeed — Embedded RE 的 Forth-VM 经典案例** —— Pixter VM 不是 Forth，但它的设计动机几乎一样；
8. **The MiSTer FPGA project** —— "把老机器变成 bit-accurate FPGA 实现"的当代代表，与 Pixter 模拟器的目标互为补集。

### 反方观点

- **HN 评论中 @MSFT_Edging / @xyzzy_plugh**：批评 Grinberg 在 Twitter 上的政治言论与种族言论，认为"作者人品与作品质量"应当被一起审视。这件事我们如实记录，但**本篇推荐评估的是文本本身的技术与保存价值**——读者请自行结合判断；
- **"为什么要花两年时间逆向一台没人在乎的儿童玩具？"**：这一类质疑在 HN 也有，Grinberg 的回答其实在文章里——*因为不做的话，再过十年就做不到了。*

## 10. 编辑延伸思考

我把这篇文章定位为"硬件考古"，不是"逆向工程"。两者的差别在写作目的：

- 逆向工程的目的是**理解**。一篇逆向文写完，你知道某颗芯片如何工作；
- 硬件考古的目的是**让未来重现**。一篇硬件考古写完，未来某个时刻，某个失踪的设备可以被重新执行。

这两件事在 AI 时代的意义正在分化。**LLM 让"理解"的门槛持续下降**——任何一个有耐心的研究者今天都能让 GPT-5.5 帮自己识别一段未知字节码的语义，这点在我们之前推荐的 [《curl 之父亲测 Mythos：AI 安全工具的祛魅时刻》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 里已经看到端倪。但**LLM 让不到"保存"**——保存需要的不是"理解原文"，而是"产出能被重新执行的工件"：模拟器、文件格式、文档、disassembler，甚至是 Wikipedia 条目的修订。这是 Grinberg 这次工作真正的独特之处。

第二层值得想的是**"保存"在 AI 训练数据里的位置**。Grinberg 上传 Internet Archive 之后，所有 Pixter dump 与文档都会进入下一代 LLM 的训练集。这意味着：未来某个 LLM 在被人问到"如何模拟 Pixter Color"时，**它会直接重现 Grinberg 的工作**，包括那些 BJT 容差 hack 的实现细节、那些被 push 两次的 32-bit VM 操作。Grinberg 不只是给人类保存，他也在给 LLM 保存——给那一种我们还无法完全命名的、"对硬件细节有耐心"的元能力，铺一份训练语料。

这一点也是我推荐这篇文章的最深层原因。**当 AI 越来越擅长"重复已知的事"，人类的稀缺技能正在向"把未知的事变成已知"集中**。Grinberg 干的事就是这件事的物理形态——把一台没人懂的玩具，变成所有人（包括 AI）都能懂的工程语料库。

第三层，作为编辑我特别想标注的是 **"承认死胡同"** 这种写作品质。文章里几乎每一节都有"我以为是 X，结果不是"的转折。这种诚实在 LLM 时代变得更重要——因为 LLM 生成的逆向文章会自动剪掉所有死胡同，呈现为一条干净的"我直接得到了答案"。这种"完美修正史"恰恰是技术写作正在丢失的东西。

> 在我之前的 [《为什么需要"慢工程师"》](/post/agent-memory-architecture-technical-debt/)（这是站内别处的论述）里讨论过：当生成速度逼近极限，"过程的可重现性"会成为新的稀缺品。Grinberg 这篇 41,000 字的过程史，本身就是稀缺品的范本。

## 11. 配套资料导览

本文目录下还有四份配套资料：

- `cover.svg`：封面图，深色背景 + "好文共赏" + 主题关键词；
- `mindmap.svg`：思维导图，从"Pixter 系列"出发到三套 VM、两条总线、两颗 SoC、保存产物；
- `concept-cards.md`：12 张关键概念卡片（ARM7TDMI 最小化、R-2R DAC、BEX 链式总线、栈式 VM 的考古证据、chip-on-board 黑盒、cost-cut 工程学等）；
- `glossary.md`：英中对照术语表（约 35 条，覆盖嵌入式硬件、ARM、6502、触摸屏与 NAND）。

## 12. 谁应该读这篇

- **嵌入式工程师**：你会在这里看到"实战版"的 cost-cut 工程学，从 BJT 容差到 R-2R DAC 到 bit-bang NAND，每一处都是供应链谈判的活化石；
- **逆向工程爱好者**：方法论极其完整——blob 推断 → 总线探针 → ROM dump → 反汇编 → VM 解码 → 模拟器实现 → 文件格式 → 文档；
- **数字保存 / 古董计算研究者**：这是 2026 年最重要的 hardware preservation 范例之一；
- **AI 时代的工程写作者**：把它当作"诚实写作"的样本——一篇没有 LLM 抛光的"完整心路文本"；
- **Fisher-Price 与 Sunplus 老员工**：如果你手里有 SPL13x 的 programming guide，请联系 Dmitry。这是一份跨越二十年的工程邀约。
