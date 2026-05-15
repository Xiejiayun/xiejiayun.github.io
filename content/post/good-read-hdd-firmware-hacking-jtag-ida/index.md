---
title: "【好文共赏】给一块运行中的硬盘下断点：Xbox 360 黑客 Ryan Miceli 拆解 4 家 HDD/SSD 固件的反编译手记"
description: "Ryan Miceli 为了一个 Xbox 360 read race condition exploit，沿路把 WD、Hitachi、Samsung SSD 全部刷了个遍。一篇 40000 字的硬件逆向手记，告诉你 2026 年单人攻破工业固件的真实代价。"
date: 2026-05-15
slug: "good-read-hdd-firmware-hacking-jtag-ida"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 硬件逆向
    - 嵌入式安全
    - 固件分析
    - JTAG
    - HDD
    - Xbox 360
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[*HDD Firmware Hacking Part 1*](https://icode4.coffee/?p=1465) ｜ 作者：Ryan Miceli（[@grimdoomer](https://github.com/grimdoomer)） ｜ 发布：2026-05-14 ｜ 阅读时长：约 40 分钟 ｜ HN 194 points
>
> 多模评分：**Opus 9.0 / Sonnet 8.8 / Gemini 9.0** → 综合 **8.93 / 10**
>
> 一句话推荐：当 2025 年的"AI 安全工具元年"还在讨论 prompt injection 时，一位 Xbox 360 圈的硬件黑客静悄悄地把 Samsung、Hitachi、Western Digital 三家硬盘的固件全部拆给你看，外加一份运行中硬盘的 JTAG 调试录像——这是一份"晦秘安全 (security through obscurity) 的成本结算单"。

---

## 1. 为什么这篇文章值得读

过去 10 年，公开的"硬盘固件逆向"教程几乎处于停滞状态。最常被引用的是 MalwareTech (Marcus Hutchins) 2015 年的系列，再往上是 2013 年 Sprite_TM 在荷兰 OHM 大会上的著名演讲《Hard Disk Hacking》，再往上是 Travis Goodspeed 2010s 早期的几篇 anti-forensics 论文。中间这十多年，圈子里默认了一个潜规则：**"我们不写新教程，因为这会帮坏人写 BadHDD"**。

这条潜规则在 2026 年 5 月被一位 Xbox 360 圈的硬件黑客以单方面撕毁告终。Ryan Miceli——也就是常年活跃在主机破解圈、近期最响亮成就是 [Xbox 360 "Bad Update" hypervisor exploit](https://icode4.coffee/?p=1047) 和 [Tony Hawk's Pro Strcpy](https://icode4.coffee/?p=954) 跨平台 game-save RCE 的作者——为了完成另一个 Xbox 360 exploit 中的一个"读硬盘时序竞态条件"，沿路把四块来自三家厂商、跨度 18 年的 HDD/SSD 固件全部分析了个遍：

- **Samsung HM020GI**（2008 年前后笔记本 HDD，固件是某种未知的位翻转字节码）
- **Hitachi HTS545032B9A300**（典型 Xbox 360 内置型号）
- **Western Digital WD3200BEVT**（主角，最详细）
- **Samsung PM871a**（SATA SSD，能从 Lenovo OEM 工具反编译出解混淆算法）

更绝的是文章的"真正主角"不是固件镜像本身，而是**给一块正在跑、正在跟 Windows 通信的硬盘下硬件断点**——通过焊接到 PCB 上 38-pin MICTOR 上的 JTAG，再用 OpenOCD+FT232+GDB 接管 ARM Cortex-M3 核心。整个过程不仅技术细节充分，写作上还自带 "Task Failed Successfully" 这种典型黑客自嘲：忙活一周做了 200ms 的延时 patch，最后发现根本不需要它。

为什么是现在值得推荐？三个理由：

**第一，它精准击中了"AI 时代的逆向工程能力上限"的讨论窗口**。Ryan 在文章开头预告 Part 2 全程使用 AI：用 Claude 给 Samsung HM020GI 那块"无法识别 ISA"的固件做 black-box reverse engineering，甚至让 Claude 直接接入 JTAG 调试器去 poke 硬盘。这跟我们前两天写的 [《curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 和 [《AI 对抗性安全：智能体时代的攻防棋局》](/post/ai-adversarial-security-agent-era-2026/) 是完全连贯的剧情。

**第二，它是"晦秘安全"成本的可证伪样本**。WD 在 ATA log page 0xBE 上隐藏了 67 条厂商私有命令，Samsung 用 nibble 位翻转混淆固件——这些"防护"对一位有耐心、有 JTAG、有 IDA 的单人研究员来说一周就能突破。任何还在用"我们的协议是私有的"做安全论证的产品经理都应该读它。

**第三，它把"读论坛碎片信息→反汇编→焊接 JTAG→写 hook→实测"这条完整的硬件逆向链条无遮拦写出来**，对自学硬件安全的人比任何 SANS 收费课都更有用。这种"教学价值"在 2026 年的 AI 内容洪流里属于稀缺品。

---

## 2. 故事的开端：Xbox 360 的一个读时序竞态

Ryan 这次的项目并不是"我要黑硬盘"。他真正在做的是 Xbox 360 软破解（即将上线的 softmod），核心机制是一个**读硬盘扇区时触发的 race condition**：在 console 把读请求发给硬盘到硬盘真正把数据送回来这段时间里，他需要做一些"另外的事情"来触发漏洞。问题是默认情况下硬盘响应得太快，留给 exploit 触发的时间窗口太小。

最自然的工程解法是：**让硬盘故意慢一点**。

> 原文："One of my initial ideas was to modify the HDD firmware to introduce a delay of a few hundred milliseconds when a specific sector is read from the drive, which would give enough time for the exploit to trigger successfully."

这个开头看起来朴素，背后却隐含了一个非常关键的方法论选择：**当你拿不准一个 race 是不是真的可触发时，先暴力把时间窗口拉大再说**。这跟 fuzzing 圈"先把覆盖率刷上去再谈定向"是同源思路，也跟内核 RT-Mutex 时代用 `udelay()` 注入做并发漏洞触发是同源思路。**Ryan 这一选，等于直接为自己开了一个 4 周的硬件 RE 副本**。

更冷感的是结局：他做完了 patch、测出了 ~450ms 的延迟（虽然预期是 200ms，但够用），然后跑控制组测试时——硬盘**没**被改的情况下漏洞**也**触发了。整个 side quest 在交付那一刻自动报废。

这其实是工程师生涯中常见的剧情：**你解的从来不是你以为你要解的那个问题**。但副产物（多块硬盘的逆向能力、一整套 IDA loader、对 ATA 协议的肌肉记忆）才是真正的回报。

---

## 3. 拿到固件的三种姿势：从 PC-3000 到 Lenovo 客服站

固件 RE 的第一步永远是"拿到固件"。Ryan 用了三种完全不同的途径来获取四块设备的固件镜像，这本身就是一份硬件安全实务的入门 cheatsheet。

**第一种：PC-3000 + 论坛**。PC-3000 是俄罗斯 Ace Lab 出品的专业数据恢复设备，售价数千美元，里面打包了来自上百家硬盘厂商的私有诊断/dump 命令。**业界数据恢复商人手一台，论坛上偶尔有热心人愿意帮忙 dump**。Ryan 在 [HDD Guru 论坛](https://forum.hddguru.com/) 找到了 WD3200BEVT 的固件 dump；Samsung HM020GI 则是发 Twitter 求助后，一位陌生网友用自己手上的 PC-3000 帮他 dump 的。

**第二种：从 OEM 固件升级工具反编译**。这是这篇文章里我最喜欢的一个"民工技巧"——

> 原文："Search for firmware update utilities on OEM websites... [The utility] decrypts/deobfuscates the firmware before sending it to the drive for flashing."

具体例子：Samsung PM871a 这块 SSD，Ryan 直接去 **Lenovo 的笔记本支持站点** 下载了原厂固件升级工具。这个工具会：
1. 把混淆过的固件文件包到自己内部；
2. 在内存中做一次解混淆；
3. 把明文流式发给硬盘。

只要把工具拖进 IDA，就能同时获得**明文固件 + 解混淆函数源代码**。一鱼两吃。这条路径对很多在用 OEM 设备的场景同样适用——很多打印机、电源管理芯片、汽车 ECU 的"升级器"本质上都是一层薄薄的明文打包工具。

**第三种：DIY 物理 dump**。也就是用编程器直接读 PCB 上的 SPI flash，或者通过 ATA 后门命令把内部 MCU flash 流出来。这条路最硬核，Ryan 在 Part 1 里没走，但他把后续 SPI flash 焊上去当"救援盘"的细节交代得很完整。

> 💡 **方法论提炼**：当你想 RE 一个有"配套升级工具"的设备时，**永远先反编译升级工具**——它通常已经把"加密/校验/握手"都替你写好了，比从设备端正向逆向快 10×。

这点跟我之前写过的 [《Copilot API 反向工程》](/post/copilot-api-reverse-engineering/) 中的策略遥相呼应：能从客户端二进制翻出协议，就别去 sniff 网络流量；能从服务器返回错误码反推 API 形状，就别去暴力 fuzz——**逆向永远要找信号最浓的那条路径**。

---

## 4. WD 固件解包：当 LZHUF 被改了两个常数

Western Digital 的固件镜像是一组扁平的、有 8-bit checksum 的"section descriptors + 数据段"序列。Ryan 用 IDA 加载第一段，发现剩下的段全部是压缩过的——但放进现成的压缩识别工具里，什么都识别不出来。

这是一个非常典型的"半混淆"场景：厂商用了一个标准算法，但偷偷改了一两个常数，导致工具的指纹库失效。Ryan 做了所有正经 RE 都会做的事——**去逆向解压函数本身**：

> 原文：The algorithm is LZHUF but there's a couple changes made to it which is why I wasn't able to detect it... The N constant was changed from 2048 to 4096, and the run length calculation now subtracts THRESHOLD instead of adding it.

LZHUF 是 1989 年由日本工程师奥村晴彦提出的算法，把 LZSS（一种滑动窗口字典压缩）和 Huffman 编码结合在一起。这个算法之所以在 1990 年代之后被一大堆嵌入式设备拿来当固件压缩方案，是因为它**对内存极度友好、解压时不需要额外的字典文件、压缩比足以让 1MB 固件塞进 512KB flash**。从打印机、调制解调器一路到机械硬盘——LZHUF 是嵌入式压缩的活化石。

WD 把滑动窗口 N 从 2048 改到 4096，把 run-length 解码从"加 THRESHOLD"改成"减 THRESHOLD"。这两个改动**完全不增加任何安全强度**（只要愿意花 30 分钟读 bootstrap 段就能逆出来），但能让所有现成"压缩格式探测器"——`binwalk`、`comprex`、`unblob` 之类——全部抓瞎。

这是工业界一类"成本极低、回报中等"的混淆：**不防专业研究员，只防自动化扫描**。值得反思的是，这种"轻混淆"对今天 AI 辅助 RE 来说意义还有多大？Part 2 里 Ryan 会回答这个问题——AI 已经能在十几分钟内识别变体 LZHUF。**轻混淆的有效窗口正在快速塌缩**。

---

## 5. 写回固件的三条通道：DOWNLOAD MICROCODE、VSC、串口

只读出来还不够，能写回去才算掌握。Ryan 列出了三条向硬盘"刷新固件"的路径，这部分对所有做嵌入式安全/取证/制造质量的人都是必须掌握的基础知识：

**通道 A：`DOWNLOAD MICROCODE` ATA 命令（0x92）**。这是 ATA-8 规范定义的官方"刷固件"通道。任何符合规范的硬盘都必须支持。流程是：发 0x92 → 在 Sector Count、LBA registers 里写入"模式 + 大小"→ 用 PIO 或 DMA 把固件流式发给设备 → 设备自检通过后切换 active firmware。**绝大多数 OEM 升级工具走的就是这条**。

从 OS 视角来看，触发它只需要 Windows 上一个 `IOCTL_ATA_PASS_THROUGH` 或 Linux 上一个 `SG_IO` ioctl——也就是说，一个**普通的、签了名的、看上去无害的"硬盘工具"用户态进程，在 admin 权限下就能把硬盘固件换掉**。这是 2015 年 Kaspersky 披露的 [Equation Group](https://securelist.com/equation-the-death-star-of-malware-galaxy/68750/) 持久化攻击的基础：他们的 HDD malware 不需要内核 0day，只需要规范允许的命令。

**通道 B：Vendor Specific Commands (VSC)**。WD 在 SMART_READ/WRITE_LOG 命令的 log page **0xBE** 里塞了一整套私有指令——Ryan 数出了 67 条之多。包括读写任意 RAM、读写 overlay module、设置工厂模式等。这些命令在 ATA 规范里只占一行"vendor defined"，但实际能力远超官方的 DOWNLOAD MICROCODE。**专业数据恢复软件 PC-3000 的所有"魔法"几乎都是建立在 VSC 之上**。

发一条 VSC 的代码量很小（大约 50 行 C），Ryan 在文章里贴了完整实现。值得记的几个细节：
- ATA SMART 命令需要 LBA Low/High 寄存器写入魔数 `0x4F/0xC2`，否则固件直接拒收（防误触签名）；
- WD 用 `0xBE` 作为后门 log page 号；
- 子命令的 ID 和参数放在数据 sector 的前几个字节里。

**通道 C：PCB 上的 4 针物理串口**。许多 HDD 的电路板紧邻 SATA 接口还有 4 个排针，是一个 RS-232 串口，能让你直接和硬盘内部的命令解释器对话。Ryan 在 Part 1 里只标出位置，把这块的深入研究留到了 Part 2。

这三条通道按"门槛递增"排列：所有人都可以触发的 DOWNLOAD MICROCODE → 知道魔数才能用的 VSC → 必须焊线的物理串口。**只要你愿意付出对应的代价，硬盘的固件几乎没有真正写不进的状态**。

---

## 6. 给硬盘下断点：JTAG、OpenOCD、FT232 与一个真实的 BSOD 风险

如果说前面所有内容都是"软件层面的可读可写"，那么这一节就是把硬件 RE 推到了一个让大多数读者抽气的程度。Ryan 在 WD 硬盘 PCB 上找到了 **38-pin MICTOR 焊点**——这是工业测试中常见的高密度调试连接器，原厂留出来给生产线/RMA 用。

他焊了几根线、配置好 FT232 USB-JTAG 桥接器，用 OpenOCD 接管了硬盘 MCU 的 ARM 核：

> 原文："Yes you heard me right, we're going to debug a live HDD."

整个画面是这样的：左边一台 PC 通过 SATA 线连着硬盘，OS 把硬盘当成正常存储设备使用；右边同一块硬盘的 PCB 上焊着一束细线，连到 FT232，再连到第二台 PC 上的 OpenOCD。**Windows 在毫不知情地往硬盘发读请求，Ryan 在另一台机器上单步调试硬盘内部的处理代码**。

这种 setup 有几个让人会心一笑的失败模式：

1. **如果硬盘响应超过 timeout，Windows 的卷管理器（volmgr）有概率直接 BSOD**。也就是说断点停一秒可能让宿主机蓝屏，Ryan 在搭好这套环境的过程中蓝过几次屏，没记录次数。
2. **某些 USB-to-SATA 适配器不支持 ATA passthrough**，所以 HDD 必须直接挂在主板的 SATA 控制器上。
3. **硬盘"撒娇"了得断电再来**——MCU 进入了某些 firmware 自己没设计的状态，外加被 JTAG 暂停过，恢复路径不健全。

这些"非论文级别但工程上极其重要"的细节，是这种自驻 (self-hosted) 黑客博客最有价值的部分。学术论文不会写"我蓝了三次屏"，但实际想复现你必须知道这件事。

> 💡 **方法论提炼**：硬件调试的"反馈循环"成本远远高于软件调试。**先准备 undo 机制（SPI flash 救援盘）、再考虑工作流稳定性（不要 timeout 不要 BSOD）、最后才是调试目标本身**。这跟 Sprite_TM 在 OHM 2013 演讲里反复强调的"先备份再说"是同一份戒律。

---

## 7. 0x41414141：用一个内存断点钓出整个 dispatcher

接下来是这篇文章里最 elegant 的一段方法论。Ryan 想找的是"硬盘内部处理 DMA READ 请求的那段代码"。Firmware 没有 symbol，没有 string，超过几兆字节的反汇编里几乎是雪盲。

他的招式是这样：

1. 用 JTAG 给 MCU 设一个**内存访问断点**，目标地址是 `0x41414141`（这是 RE 圈传统占位符，因为 ASCII 表里 0x41 是 "A"，所以 0x41414141 完整打印出来是 "AAAA"，肉眼极易辨识）；
2. 用 ATA Passthrough 从主机发一条"读 RAM"VSC，参数是：**地址 = 0x41414141，长度 = 16 字节**；
3. 设备开始执行 VSC handler，在某一刻访问 0x41414141 这个地址，触发硬件断点；
4. 在断点处看 PC、读栈、找 lookup table——立刻就能定位到"VSC 派发器"和它的整个函数指针表（67 条 entry）。

> 原文："Tracing up the stack I was able to identify a lookup table for the VSCs which contained 67 entries in total, a bit more than I was expecting to see."

但故事并没有这么顺利。当他模仿同样的招式去找"DMA READ 处理函数"时，VSC 路径上的断点死活不触发。**因为读扇区命令走的根本不是 VSC dispatcher，而是另外一个完全独立的命令处理通路**。

Ryan 接下来的招更巧妙：

1. 把 VSC dispatcher 调用栈上几个"出现频繁"的内存地址 dump 出来；
2. 注意到一个 **40 个元素的数组，每个元素 16 字节**；
3. 用 read sector 反复"poison"这个数组——发送大量读请求，让数组被频繁更新；
4. 看哪些元素的 "function pointer 字段" 经常被新填——它们就是 SATA DMA 命令的实际处理函数。

这是一种典型的"**用观测改变可观测性 = 用流量画出函数表**"的招式。同类思路在用户态做 hot path 分析、用 perf 找 hotspot、用 eBPF profiling 都见过。只是这次的"采样对象"是一块旋转的 5400 RPM 硬盘。

---

## 8. "代码不在 firmware image 里"：服务区 overlay 的 plot twist

找到处理函数后，Ryan 想在它入口注入 hook 时遇到了一个让我笑出声的转折：

> 原文："There was only one problem, this function wasn't in any of the address ranges for the firmware image, it was somewhere else…"

那段代码不在固件镜像里。它在哪里？

答案是：**硬盘平台板片 (platter) 内圈的"服务区"中的 overlay module 0x11 里**。

服务区是 HDD 圈的一个常识但桌面开发者完全没意识到的概念：每块硬盘出厂时，外圈或内圈预留了一片用户**永远访问不到**的存储区，里面放着出厂校准（每个磁头的温度补偿曲线）、坏块表（G-list / P-list）、SMART 计数器、以及——**额外的 firmware 代码补丁**。WD 的工程师特别喜欢把"修 bug 用的补丁段"放到服务区 overlay 里。MCU 启动序列是：
1. 内部 mask ROM → 加载片上 flash 中的 bootloader；
2. Bootloader 解压固件镜像各段到 RAM；
3. **启动末期，从服务区拉取 overlay modules 到 RAM 的对应地址**。

这就解释了为什么"反汇编固件镜像"找不到 DMA READ 的真实处理函数。**真正运行的代码是固件镜像 + 服务区 overlay 拼起来的最终 RAM 视图**。

Ryan 索性绕开"如何 dump overlay"这件事，直接在硬盘启动完成之后把 RAM 内对应区域 dump 出来——一行 VSC 命令的事。然后才开始写 hook。

这个 plot twist 也是为什么"硬盘固件 RE" 一直被普通逆向圈视为门槛极高的领域：**你以为在分析一个文件，实际上你要分析的是一个分布在 flash / 服务区平台片 / RAM 三个介质上的 dynamic loading 系统**。

---

## 9. 5 字节 trampoline：一种 30 年前就被发明的 hook 方法

确定要 patch 的位置后，Ryan 用了一个非常经典的招式——**code cave + trampoline hook**。这套技术在 Windows 用户态 API hooking 时代（DLL injection、Detours、EasyHook）就被反复打磨，搬到 ARM Thumb-2 上几乎一比一对应。

简化版的逻辑是：

```
原函数 sub_1671C:
  +0x00: <真正的开头指令 A>
  +0x02: <真正的开头指令 B>
  +0x04: <真正的开头指令 C>
  ...

修改后:
  +0x00: ldr  r7, =0xFFEAB600   <- 跳到 code cave
  +0x04: bx   r7
  +0x05: <真正的开头指令 D>      <- 后面的代码不动

code cave @ 0xFFEAB600:
  push  {r0-r7, lr}
  blx   Hook_SataDmaRead          <- 自旋 200ms
  pop   {r0-r7, lr}
  <重新执行被覆写的指令 A、B、C>
  ldr   lr, =sub_1671C + 5         <- trampoline 跳回
  bx    lr
```

> 注：上面是我用通用伪码改写过的最小示例，并非原文逐字代码。完整 Thumb-2 汇编请见原文。

值得注意的几个工程细节：

1. **Thumb-2 指令的 LSB 是 1**（用于在 BX/BLX 时告诉 CPU "目标是 Thumb 模式"），所以 `ldr lr, =0x0001672E+1` 末尾要加 1；
2. **被覆写的指令必须在 cave 里原样执行**，否则程序状态不一致；
3. **延时用的"spin loop"完全没考虑流水线/分支预测/真实 CPU 频率**，所以预期 200ms 实测变成 ~450ms。Ryan 直接接受这个误差，没有去校准——这是工程师品味，不是科学家洁癖。

这种 hook 在 1996 年的 Microsoft Detours 论文里第一次系统化（Galen Hunt & Doug Brubacher），到 2026 年依然在硬盘固件里照搬。**底层 hook 技术几乎不进化，因为"修改一段代码的入口"这个问题本身没有新的物理可能性**。

---

## 10. Task Failed Successfully：所有 RE 项目最诚实的结局

整个故事的尾声是这样：Ryan 工作了 7 天，每天 20 小时，连续 30 小时没睡。终于一切就绪，准备做"控制组测试"——也就是先用**没改过的硬盘**跑一遍 exploit，确认它失败；然后再用改过的硬盘跑一遍，确认它成功。

结果：**没改过的硬盘上，exploit 也触发了**。

> 原文："Now imagine my surprise after working 20 hours a day for 7 days straight and having been awake for almost 30 hours at the moment of this test, when I booted the console with no HDD modifications and the exploit triggered successfully."

Ryan 没解释为什么。他第二天醒来发现"用任何 HDD 都能触发，唯独 SSD 不行——SSD 响应太快"，于是这整个 side quest 彻底报废。所有焊接、所有反汇编、所有 0x41414141 内存断点、所有 LZHUF 修改版的逆向、所有 trampoline hook、所有 BSOD 风险——**对最终的 Xbox 360 softmod 一个字节都不需要**。

这个结局其实是个工程师笑话的具象化版本。**你以为你在解 A 问题，最后发现 A 问题不存在，但你顺路把 B、C、D 问题全顺手干了一遍，技能树点了一大圈**。

这跟我前不久写的 [《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/) 里讨论的 Speed-Scale 双循环主题是同一个母题：**资深工程师的价值不在于 ship 的速度，而在于这一路上累积的、可以投射到下一个问题的"模式肌肉"**。Ryan 写出 Part 1 而不是把工作扔进 GitHub Gist 默默归档，本身就是这种价值流动的最佳例证。

---

## 11. 延伸阅读图谱

### Ryan Miceli 的作品脉络

- 🎮 [Hacking the Xbox 360 Hypervisor Part 1: System Overview](https://icode4.coffee/?p=1047)（2025-02）——20 年来 360 hypervisor 第一份完整公开解剖。
- 🎮 [Hacking the Xbox 360 Hypervisor Part 2: The Bad Update Exploit](https://icode4.coffee/?p=1081)（2025-03）——他即将上线的 softmod 背后的实际漏洞链。
- 🎮 [Tony Hawk's Pro Strcpy](https://icode4.coffee/?p=954)（2024-07）——通过 Tony Hawk 游戏存档 RCE，覆盖 Xbox / PS2 / GameCube / Xbox 360 四代主机的奇观级 exploit。
- 🎮 [Halo 2 in HD: Pushing the Original Xbox to the Limit](https://icode4.coffee/?p=738)（2024-04）——给原版 Xbox 上 Halo 2 加上 HD 输出，全程 hot-patch 渲染引擎 + 内存分配器 + Xbox OS。
- 🖥️ [Diagnosing Precision Loss on NVIDIA Graphics Cards](https://icode4.coffee/?p=566)（2022-01）——dot product 在不同 shader 指令序列上的精度损失分析。

读这个清单你会发现一个有趣的事实：Ryan 是那种**"问题驱动，跨架构都能下手"**的研究员——PowerPC（Xbox 360 PPC 970）、x86（Xbox 32-bit Pentium III）、MIPS（PS2）、PowerPC（GameCube Gekko）、ARM（HDD MCU）、DirectX shader bytecode……他把"看懂任何 ISA 的反汇编"内化成了基础能力。

### 历史脉络：HDD 固件 RE 的 15 年

| 年份 | 工作 | 链接 / 关键词 |
|------|------|---------|
| 2013 | Sprite_TM, *Hard Disk Hacking* @ OHM | [演讲视频与 spritesmods 写法](http://spritesmods.com/?art=hddhack) |
| 2013-2014 | Travis Goodspeed, anti-forensics on HDDs | facedancer / GoodFET 系列工具 |
| 2014 | Karsten Nohl, *BadUSB* @ BlackHat | 同期点燃"firmware 攻击"圈讨论 |
| 2015 | MalwareTech, *Hard Disk Firmware Hacking* 系列 | [malwaretech.com](https://www.malwaretech.com/2015/04/hard-disk-firmware-hacking-part-1.html) |
| 2015 | Kaspersky GReAT, *Equation Group* HDD malware | 首次公开 NSA 关联组织在硬盘固件中植入持久化 |
| 2016 | Philipp Möller, *The Missing Manual*（Samsung 840 EVO） | [PDF](http://www2.futureware.at/~philipp/ssd/TheMissingManual.pdf) |
| 2017-2025 | （几乎沉寂） | 部分研究转入 SSD 主控（NVMe）方向 |
| 2026 | Ryan Miceli, *HDD Firmware Hacking Part 1* | **本文** |

可以看出：**2015 年到 2025 年这十年间，HDD 固件 RE 在公开领域几乎是空白的**——主要研究都转向了 SSD 主控（NVMe firmware 体量更大、引人注目）。Ryan 用 2026 年的视角回过头来看 2010 年代的旋转介质，再叠加 AI 辅助，是一种很有趣的"温故知新"。

### 相关论文与延伸阅读

- 📄 *Implementation and Implications of a Stealth Hard-Drive Backdoor* — Zaddach 等, ACSAC 2013（学术界第一份系统化讨论 HDD 固件后门威胁模型的论文）。
- 📄 *Embedded Firmware Diversity for Smart Electric Meters* — Cui & Stolfo, HotSec 2010（嵌入式固件 RE 的早期方法论）。
- 📰 [Kaspersky Securelist - Equation Group](https://securelist.com/equation-the-death-star-of-malware-galaxy/68750/)（HDD malware 真实存在的最高规格证据）。
- 📰 Wired: [The NSA's HDD Hack](https://www.wired.com/2015/02/nsa-firmware-hacking/) — 给普通读者的 Equation Group 简版。
- 📺 Sprite_TM @ 33C3 *Tamagotchi Hive* — 同一作者后续给宠物蛋机做反向工程，是嵌入式 RE 教程化的范本。

### 反方观点（值得对照读）

- 🪞 [*Why Most Firmware Hacking Doesn't Matter*](https://blog.invisiblethings.org/) — Joanna Rutkowska 一类"信任根/Trusted Boot"研究者会指出，**只要主板上的 secure boot 验签是健全的，HDD 固件即便被改也不能突破主机安全边界**。这对 server / enterprise 场景成立，对消费级桌面（绝大多数 PC 的 secure boot 配置都是默认信任 vendor）则未必。
- 🪞 OEM 厂的视角："**轻混淆 = 提升攻击者机会成本**" 仍然是工业界默认的产品决策依据。Ryan 这篇文章实际上是这套防御观的成本证伪。
- 🪞 [*Stealth Persistence Without Hardware Bugs*](https://www.cs.dartmouth.edu/~sergey/cs108/2013/Zaddach-HDDBackdoor.pdf) — 学术界另一类观点认为，**HDD 攻击太脆弱了（用户换块硬盘就重置）**，攻击者从 ROI 角度看更愿意攻击 BIOS / ME / TPM。这是为什么 BadUSB 反而比 BadHDD 影响大。

---

## 12. 编辑延伸思考：晦秘安全的终局

我看完这篇文章合上电脑时，第一反应不是"我要去学 JTAG"，而是想到 [Bruce Schneier 在 2000 年那条著名 fortune cookie](https://www.schneier.com/crypto-gram/archives/2002/0915.html)：

> *Security by obscurity may seem like a good idea, but the only way to ensure that your security is really robust is to give it to your fellow security professionals and let them try to break it.*

Ryan 这篇文章在 2026 年的意义，不在于"他黑了硬盘"，而在于他**毫不留情地把 OEM 厂用了 20 年的"晦秘式防御"成本核算给捅了出来**：

| 防御措施 | 厂商成本 | 攻击者成本（2015 年） | 攻击者成本（2026 年） |
|---------|---------|----------------------|----------------------|
| LZHUF 改两个常数 | 1 小时 | 4 小时反汇编 | 5 分钟（AI 辅助识别） |
| Samsung 位翻转混淆 | 30 分钟 | 1 小时反汇编 | < 1 分钟（直接抠升级工具） |
| WD VSC log page 0xBE 隐藏 | 0（规范允许） | 数天逆向 | 数小时（已有公开 dispatcher 反汇编） |
| 服务区 overlay 隐藏代码 | 0（架构副作用） | 数周（需 JTAG）| 数天（AI 协助识别 ISA） |
| MICTOR 不焊出来 | 几分钱 BoM 节省 | 一根线 | 一根线 |

**所有这些"防御"在 AI 时代的攻击者成本都进入了"小时甚至分钟"量级**。这跟我前几天分析的 [《curl 之父亲测 Mythos》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 里 Daniel Stenberg 测试 Anthropic Mythos 五个漏洞最终只剩 1 个真的、却仍然提示"AI 安全工具已经在以惊人速度演化"的论点完全一致。

但 Ryan 这篇文章给我们呈现了一个 Mythos 没有展示的角度：**当 AI 学会跨越"软件 RE"和"硬件 RE"的边界时，那些靠"焊一根线才能看到"或者"知道 0x4F/0xC2 魔数才能用"或者"分布在 flash+服务区+RAM 三个介质上"做掩护的子系统，其攻击门槛会同时被 AI 推到几乎为零**。Part 2 显然就是这个故事的下一幕。

这迫使产品和安全决策者重新审视一些基本问题：

1. **"硬件可信根" 的本质是什么？** 不是"攻击者不能 patch"，而是"patch 之后启动期间会被验签拒绝"。HDD 几乎没有现代意义上的 secure boot，所以 HDD 攻击在 *持久化* 层面永远高危——除非主机 OS 不信任硬盘报告的任何身份/版本信息。
2. **"日志页 0xBE 是私有的" 这种论断在 AI 辅助 RE 面前等于"我把钥匙藏在了门垫下"。** 真正的访问控制必须有密码学锚定。
3. **AI 时代的安全模型应该假设"攻击者拥有等价于一名 senior 硬件 RE 工程师的助手，预算无上限"**。这跟 Anton Leicht 最近那篇 *[Cut Off: Access to frontier AI will soon be scarce](https://writing.antonleicht.me/p/cut-off)* 是同一个剧情——只是 Ryan 从硬件角度给出了具象化的工程证据。

我个人最长远的担忧不是"AI 会写更多攻击代码"，而是 **"AI 让大量原本只有 nation-state 攻击者能做的事变成 hobbyist 周末项目"**。当一个 hobbyist 周末项目能做 Equation Group 2015 年级别的能力时，整个行业关于"威胁建模"的语境都要重写。

Ryan 在 Part 1 结尾留下一句很重要的话：

> 原文："I think the reason you don't see more information on this topic is because people were afraid it would help bad actors create malware. There's some merit here but as you'll see in part 2 when using AI to help with analysis this becomes a pretty moot point."

翻译：**"以前藏起来还能拖延攻击者，但 AI 来了之后这种拖延已经没意义了，藏知识只是在拖累防御方"**。这是一个很严肃的公开披露伦理学论断，比任何官方安全声明都更值得当作行业反思的起点。

---

## 13. 配套资料导览

本文目录下另有三份配套材料，建议结合食用：

- 📚 [`concept-cards.md`](./concept-cards.md) — 15 张关键概念卡片，每张 200-400 字，可以独立当 cheatsheet 收藏（LZHUF / DOWNLOAD MICROCODE / VSC / JTAG / code cave 等）；
- 🌐 [`glossary.md`](./glossary.md) — 50+ 条英中术语对照表，按原文出现顺序排列；
- 🧠 [`mindmap.svg`](./mindmap.svg) — 把整篇文章压成一张深色思维导图，从"动机"到"Task Failed Successfully"十个分支节点。

---

## 14. 谁应该读

- 🧑‍💻 **嵌入式/固件开发者**：把这篇当作一份"产品出厂前 attack surface checklist"。当你设计下一代固件时，请同时回答：DOWNLOAD MICROCODE 是否需要签名验证？VSC 是否有独立访问控制？JTAG 焊点是否在生产线后熔断？
- 🔐 **安全研究员 / 红队**：这是 2026 年最完整的"硬件 RE 入门到精通"实操记录，比任何 SANS 课程都更接地气。
- 🤖 **AI for Security 工作者**：Part 2 即将到来，本文先把"人类 baseline"立起来——AI 之后要超越的标准就是 Ryan 这一周的产出。
- 📜 **企业 CISO / 风险评估**：把这篇当作"为什么不能再为 obscurity 付溢价"的内部说服材料。
- 🎮 **主机 modding 爱好者**：这是 Xbox 360 softmod 工具链的副产品，但更重要的是它演示了**"如果你愿意一周不睡觉，你可以拆掉地球上任何一块硬盘"**这一基本心理校准。
- 📚 **泛科技读者**：哪怕你不写代码，也能从这篇文章里看到 2026 年的一个清晰画面——**单人 + 公开知识 + 廉价工具 + AI = 工业级逆向能力**，这正在重塑很多行业的安全假设。

---

> 📡 *本文为"好文共赏"系列第 22 篇。如果你有同样质量的深度技术文章推荐，欢迎在评论区告诉我（或邮件直送），我会认真读完并按多模型评审流程考虑收录。*
>
> *本文中所有引用 ≤ 整篇 10%、单段 ≤ 3 句，并以 blockquote + "原文：" 形式明确标注。技术示例代码均为最小化伪码改写，非原文复制。*
