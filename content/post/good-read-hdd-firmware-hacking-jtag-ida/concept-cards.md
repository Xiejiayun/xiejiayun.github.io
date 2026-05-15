# 概念卡片 · HDD Firmware Hacking Part 1

> 配套于《【好文共赏】给一块运行中的硬盘下断点：Xbox 360 黑客 Ryan Miceli 拆解 4 家 HDD/SSD 固件的反编译手记》

---

## 卡片 1 · 硬盘固件不是单文件，是一组带 checksum 的段

HDD 固件镜像≠桌面操作系统的 `vmlinux` 单 ELF。Western Digital 的镜像是**一组扁平的可执行/数据段**，文件头是 section descriptors，每个段有自己的 8-bit 求和 checksum，bootloader 解压后把它们按各自的基地址放进 RAM。这种"段-段-段-bootstrap"的结构在嵌入式固件里很普遍，但对逆向新手是第一道门槛：直接拖进 IDA 当 raw binary，所有交叉引用全是错的。

---

## 卡片 2 · LZHUF 是什么，为什么它能在工业里活到 2026

LZHUF = LZSS（一种基于滑动窗口的字典压缩）+ Huffman 编码。原始 LZHUF 1989 年由奥村晴彦在 LHA/LHarc 里提出。它便宜、可在裸机上跑、对内存友好——所以从打印机、调制解调器一路扩散到 HDD 固件。**Ryan 遇到的是改造版**：原版滑动窗口 N=2048 被改成 4096，run-length 解码也把"加 THRESHOLD"改成"减 THRESHOLD"。这种小改动让现成的"压缩识别工具"全部失效，但只要愿意逆向 bootstrap 段的解压函数，30 分钟就能写出 Python 重实现。

---

## 卡片 3 · DOWNLOAD MICROCODE：写入固件的"官方暗门"

ATA 命令集里有一条 `DOWNLOAD MICROCODE`（命令码 0x92），用途就是"把这堆字节当成新固件刷进去"。所有 OEM 厂的固件升级工具，本质都是这条命令的薄包装。流程：发命令 + 在 register 里写入固件大小 → 用 PIO 或 DMA 把数据流过去 → 设备自己 verify → 重启生效。失败有可能直接砖。值得记住的是：**只要操作系统能直通发原始 ATA 命令（Windows 的 `IOCTL_ATA_PASS_THROUGH`、Linux 的 `SG_IO`），任何 userland 程序在合适权限下都能刷固件**——这就是 BadUSB/Equation Group 那类 firmware 攻击的能力来源。

---

## 卡片 4 · 服务区 (Service Area) 与 Overlay Modules

硬盘"用户可见"那片磁盘容量只是表面。在外圈或最内圈，还有一片**用户永远访问不到的服务区**，里面塞着：
- 出厂校准数据（每个磁头的偏移、温度补偿曲线、SMART 阈值）；
- 坏块映射表（G-list / P-list）；
- **Overlay modules**——额外的可执行代码，启动期会被 bootloader 加载进 RAM。

Western Digital 特别喜欢把"补丁"放在 overlay 里。Ryan 找了半天的"读取处理函数"不在固件镜像里，就是因为它住在 overlay module 0x11 中——只有当硬盘启动完整完成之后才被搬进 RAM。这也是为什么"dump RAM 比 dump flash 重要"。

---

## 卡片 5 · Vendor Specific Commands (VSC)

ATA 规范留了一段"vendor defined"日志号给厂商。WD 用 SMART_READ/WRITE_LOG 的 log page **0xBE** 作为后门入口，里面再嵌一个 1-byte 的 sub-command 号。Ryan 在 WD 固件里数出了 67 条 VSC，覆盖：
- 读/写任意 RAM 地址；
- 读/写 overlay module；
- 复位、出厂模式；
- 诊断 (PC-3000 用的就是它们)。

**为什么 VSC 危险**：从用户态发一条 ATA passthrough 就能调用，不需要硬件改装。设防者很难"白名单"，因为很多正常工具也走这条路。

---

## 卡片 6 · 给硬盘下断点：JTAG + OpenOCD + FT232

许多 WD 硬盘电路板上预留了一个 38-pin MICTOR 焊点，开放出 ARM 核的 JTAG。焊四根线 → FT232（廉价 USB-串口/JTAG 桥） → OpenOCD → GDB，就能给一块**运行中、正在跟 Windows 通过 SATA 通信的硬盘**下硬件断点、单步调试、读写寄存器。

注意事项：
- HDD 必须直连 SATA（很多 USB-SATA 适配器不支持 ATA passthrough）；
- 命令响应超时 → Windows 卷管理器 BSOD；
- 硬盘"撒娇"了得断电再来。

这是把"硬件调试"做到极致的画面：**调试器的对面不是 CPU、不是 SoC，而是一台真正的旋转机械装置**。

---

## 卡片 7 · 用 0x41414141 钓出 dispatcher

这是逆向圈一个流传多年的诀窍。Ryan 想找 "Vendor Specific 读 RAM" 命令背后的处理函数，他不去阅读几兆字节的反汇编，而是：

1. 给 MCU 设一个**内存访问断点**，目标地址 `0x41414141`（"AAAA" 是经典占位符，因为 32-bit ASCII 完全打印出来是 AAAA，容易识别）；
2. 用户态发 VSC：read RAM, address=0x41414141, size=16；
3. 等断点触发，看 PC、看栈、看寄存器；
4. 沿调用栈往上走，找到 "ATA command 派发器"。

**比纯静态分析快 100 倍**，前提是你能调试到运行中的目标。

---

## 卡片 8 · ATA Passthrough：用户态的"原始命令通道"

Windows: `IOCTL_ATA_PASS_THROUGH` (DeviceIoControl)
Linux: `SG_IO` ioctl over SCSI generic
都允许你**绕过文件系统**，直接把一组 ATA task file registers + 数据缓冲区扔给磁盘。Ryan 的代码片段里这样设置：

```c
pRegs->bCommandReg    = ATA_OP_SMART;       // 0xB0
pRegs->bFeaturesReg   = SMART_WRITE_LOG;
pRegs->bSectorNumberReg = 0xBE;             // WD vendor log
pRegs->bCylLowReg     = 0x4F;
pRegs->bCylHighReg    = 0xC2;
```
后两个 magic 数 0x4F/0xC2 是 SMART 命令的"调用签名"——少了它，固件直接拒收。这是 ATA-8 ACS 规范第 7.49 条的硬性要求。

---

## 卡片 9 · SPI Flash 救援电路

WD 部分型号在 PCB 上预留了一颗 SPI flash 的位置：如果板子上焊了 SPI flash 并把两颗下拉电阻配好，MCU 启动时会从 SPI flash 引导而不是内部 flash。Ryan 利用这一点：**焊一颗便宜的 SPI flash 上去，专门用来测试模改固件**——刷砖了用外部编程器 in-circuit 重写 SPI flash 即可救活，不会把"出厂级"内部 flash 永久毁掉。

这是优秀 RE 的标志：**先把 undo 机制做出来再开始改东西**。

---

## 卡片 10 · 代码 Cave (Code Cave) 与 Trampoline Hook

由于真正要 patch 的代码在 overlay module 里（最终要写回服务区），Ryan 先做**"hot patch in RAM"**：
1. 找一段 overlay 没用到的 RAM（他选了 `0xFFEAB600`）作为 cave；
2. 把 200ms 自旋延迟和"恢复被覆写指令"塞进 cave；
3. 在原目标函数 `sub_1671C` 的入口写一条 `ldr r7, =0xFFEAB600 ; bx r7`（5 字节，Thumb-2 编码）；
4. 跳到 cave 执行 hook → 跑被覆写的原始指令 → trampoline 回到 `target+5`。

**这是经典的 5-byte hook**，PE 时代 Windows API hooking 同款思路，搬到嵌入式 ARM 里只是指令编码不同。

---

## 卡片 11 · "Spin Loop" 不是真的延迟工具

Ryan 估算了"`(MS_DELAY * F_CPU / 1000)` 次减 1 = 200ms"，实测出来变成 ~450ms。原因有三：
1. 没有计入 ARM Cortex-M 的分支预测失败惩罚；
2. 没考虑流水线 stall；
3. 实际 CPU 频率 ≠ 估算的 10 MHz。

正确做法是用 MCU 的 SysTick 或某个外设计时器，但**对一个"side quest"项目来说"调到 200ms 数量级"就够了**——这是工程师品味，不是科学家洁癖。

---

## 卡片 12 · Samsung 的"低成本混淆 ≠ 加密"

Samsung PM871a 的固件文件经过一层 **nibble 位翻转**：

```c
hi = byte >> 4;
hi = (hi & 1) ? (hi >> 1) : (0xF - (hi >> 1));
byte = (byte & 0x0F) | (hi << 4);
```

这不是加密，是"防菜鸟"的混淆——任何能找到固件更新工具的人，反编译几分钟就能拿到逆变换。Ryan 直接从 Lenovo 提供的更新 utility 里抠出了这段代码。

**为什么 OEM 还是这么做**：HN 评论里一位读者回答得很妙——"这样以后你公布代码的时候他们可以 DMCA 你"（数字千年版权法的"反破解条款"对"任何技术保护措施"都受保护，哪怕保护强度只是位翻转）。

---

## 卡片 13 · 0x4F / 0xC2 是 SMART 命令的"防误触签名"

ATA spec 要求所有 SMART 子命令在 LBA Low / LBA High register 里写入魔数 0x4F 和 0xC2。背后哲学：**SMART 命令历史上和数据传输共用 task file，磁盘担心"误操作"把磁盘擦了**，于是要求一个签名。这两个数没有特殊含义，就是规范选定的"不太可能意外出现"的组合。

类似的"防误触魔数"还有：
- WinAPI `MapViewOfFile` 的 `dwFileOffsetLow == 0x4D5A`（"MZ"，DOS header）；
- ZFS 的 `0x00bab10c`（"Oh boy! It's love"）。

工程师的幽默感总是相通的。

---

## 卡片 14 · 安全圈一直没人公开写 HDD 固件 RE 的原因

Ryan 在结尾自己点破：**这个话题被"安全人士"主动雪藏了 10+ 年，因为大家担心写出 BadHDD 教程会助长恶意软件**。

但事实是：
- NSA 早就有 HDD malware（Kaspersky 2015 年披露的 "Equation Group" Stuxnet 关联工具集，覆盖 WD/Seagate/Samsung/Toshiba 全家），见 Kaspersky GReAT 报告；
- "供应链可见性差" 反而对防御方不利；
- AI（Part 2 主题）已经能给任何只要给它源代码或符号丰富的二进制做 RE。

继续把知识藏起来已经不能"延缓攻击者"，只能"延缓防御方"。这跟密码学界从 70 年代开始的"防御性披露 > 隐秘安全"哲学完全一致。

---

## 卡片 15 · 这篇文章在 2026 年的真正意义

不是教你做 BadUSB-for-HDD。而是给所有人一个**"我能不能 RE 这块芯片"的心理校准**：

- ARM 核 + 标准 ATA 命令 + 公开 OEM 工具 + 一周时间 = 单人可以攻破 4 家主流厂商；
- 公开知识库（HDD Guru 论坛）+ AI 辅助（Part 2）= 学习曲线进一步压缩；
- 这是 **AI 安全工具元年**（Mythos/Pwn2Own/curl 假阳性等系列事件）的下一幕：**当攻击面变得可被自动化扫描时，所有"靠晦涩生存"的子系统都将被重新审视**。

对工程师：低估自己 = 错过最有趣的工作。
对监管者：高估"晦涩"的防御价值 = 持续被绕过。
