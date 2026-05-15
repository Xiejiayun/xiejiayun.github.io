# 术语对照表 · HDD Firmware Hacking Part 1

> 英中对照 + 一句话解释。按文章出现顺序排列，便于结合原文/导读阅读。

| English Term | 中文 | 一句话解释 |
|--------------|------|-----------|
| HDD (Hard Disk Drive) | 机械硬盘 | 用旋转磁性盘片 + 移动读写头存数据的存储设备。 |
| SSD (Solid State Drive) | 固态硬盘 | 用 NAND flash 存数据、无机械部件的存储设备。 |
| Firmware | 固件 | 嵌入硬件内部的低层软件（这里指硬盘 MCU 上跑的代码）。 |
| Race condition | 竞态条件 | 多个事件的相对时序决定结果是否正确的 bug 类型。 |
| MCU (Microcontroller Unit) | 微控制器 | 集成 CPU+存储+外设的小型芯片，硬盘的"大脑"。 |
| Service Area | 服务区 | 用户永远访问不到的硬盘内部存储区，存校准/坏块/补丁。 |
| Overlay module | 覆盖模块 | 启动期才被加载进 RAM 的额外固件代码块。 |
| LZHUF | LZHUF 压缩算法 | LZSS 字典压缩 + Huffman 编码的组合算法，1989 年来自日本。 |
| Bootstrap | 引导段 | 镜像中第一段、负责把其他段解压加载到 RAM 的小代码。 |
| ARM Cortex-M3 | ARM Cortex-M3 | 嵌入式 32-bit ARM 核心，硬盘 MCU 常见架构。 |
| Memory map | 内存映射 | "哪个地址对应 ROM/RAM/外设寄存器"的全局视图。 |
| IDA Pro | IDA Pro | 主流商业反汇编与逆向工具。 |
| Reverse engineering (RE) | 逆向工程 | 从二进制反推出代码逻辑/数据格式的工艺。 |
| Obfuscation | 混淆 | 不增加保密强度、但增加阅读难度的代码/数据变换。 |
| Cryptographic signature | 加密签名 | 用私钥对数据签名，公钥验证不可伪造性。 |
| RSA / ECDSA | RSA / 椭圆曲线签名 | 两类主流公钥签名算法。 |
| SHA-224 / SHA-256 | SHA-224 / SHA-256 | 主流加密哈希函数，输出 28 / 32 字节。 |
| ATA specification | ATA 规范 | 硬盘与主机通信的标准命令集（IDE/SATA 都基于它）。 |
| DOWNLOAD MICROCODE | DOWNLOAD MICROCODE 命令 | ATA 命令 0x92，用于把新固件刷进设备。 |
| DMA (Direct Memory Access) | 直接内存访问 | 设备不经过 CPU 直接读写主机内存的机制。 |
| DMA READ EXT | DMA READ EXT 命令 | ATA 命令 0x25，用于 48-bit LBA 的 DMA 读取。 |
| SATA | SATA | 主流串行硬盘接口，物理层 + ATA 命令集。 |
| PC-3000 | PC-3000 | 俄罗斯 Ace Lab 出品的专业数据恢复设备，能用厂商私有命令。 |
| Backdoor command | 后门命令 | 厂商私有的、非公开规范中的调试/诊断命令。 |
| Vendor Specific Command (VSC) | 厂商特定命令 | 厂商在规范"vendor defined"区间放的私有功能。 |
| SMART (Self-Monitoring, Analysis, and Reporting Technology) | SMART | 硬盘自检与健康状态报告体系。 |
| SMART READ/WRITE LOG | SMART 日志读写 | ATA 命令 0xB0 的子功能，正常用途是读取健康数据。 |
| ATA Passthrough | ATA 直通 | OS 提供的 IOCTL，让用户程序直接发原始 ATA 命令。 |
| IOCTL_ATA_PASS_THROUGH | Windows ATA 直通 IOCTL | Win32 上对应的内核接口编号。 |
| SG_IO | Linux SCSI 通用 IOCTL | Linux 上对应的内核接口。 |
| Task file registers | 任务文件寄存器 | ATA 设备接收命令时读取的一组寄存器。 |
| JTAG | JTAG | IEEE 1149.1 调试接口，能在硬件层面下断点/单步。 |
| MICTOR connector | MICTOR 连接器 | 38-pin 高密度调试连接器，硬盘 PCB 上的 JTAG 出口。 |
| OpenOCD | OpenOCD | 开源 on-chip 调试器，对接 JTAG/SWD 探针。 |
| FT232 | FT232 | FTDI 的 USB-串口/JTAG 桥芯片。 |
| GDB | GDB | GNU Debugger，命令行调试器，搭配 OpenOCD 用。 |
| Breakpoint | 断点 | 让 CPU 执行到某地址时暂停的调试机制。 |
| Memory access breakpoint | 内存访问断点 | 读/写某地址时暂停（而不是按 PC 触发）。 |
| Dispatcher / function table | 派发器 / 函数表 | "命令号 → 处理函数"的查表跳转结构。 |
| Code cave | 代码 cave | 二进制中未使用的字节段，用来塞入 hook 代码。 |
| Trampoline / hook | 跳板 / 钩子 | "在原函数入口跳到自定义代码、执行后跳回"的 patch 技巧。 |
| Thumb-2 | Thumb-2 | ARM 的 16/32-bit 混合指令集，Cortex-M 普遍使用。 |
| SPI flash | SPI flash | 通过 SPI 总线访问的串行 NOR/NOR 闪存芯片。 |
| In-circuit programmer | 在线编程器 | 不拆芯片就能改写 flash 的硬件工具。 |
| MalwareTech | MalwareTech | 安全研究员 Marcus Hutchins，2015 年发表 HDD 固件 RE 系列。 |
| Travis Goodspeed | Travis Goodspeed | 嵌入式安全研究员，有大量 HDD anti-forensics 工作。 |
| Sprite_TM (Jeroen Domburg) | Sprite_TM | 荷兰逆向研究员，2013 年 OHM 大会演讲 "Hard Disk Hacking"。 |
| BadUSB | BadUSB | 2014 年 BlackHat 揭示的、通过改写 USB 控制器固件的攻击家族。 |
| Equation Group | Equation Group | NSA 关联的 APT 组织，2015 年被 Kaspersky 披露曾植入 HDD 固件。 |
| Service area module 0x11 | 服务区模块 0x11 | WD 这台 HDD 上含读写处理代码的具体 overlay 编号。 |
| HDD Guru forums | HDD Guru 论坛 | 硬盘数据恢复与逆向社区，存有大量 PC-3000 dump。 |
| ATA passthrough magic 0x4F/0xC2 | ATA 直通魔数 0x4F/0xC2 | SMART 命令必须写入的"防误触签名"。 |
| Spin loop | 自旋循环 | "在 CPU 上空转 N 拍来模拟延时"的最朴素延时实现。 |
| Sector | 扇区 | 硬盘最小寻址单元，传统 512 字节，现代多为 4 KB。 |
| LBA (Logical Block Address) | 逻辑块地址 | 用单一整数寻址所有扇区的方案。 |
| Form factor | 物理外形 | 2.5″ / M.2 / U.2 等不同的硬盘机械规格。 |
| Anti-forensics | 反取证 | 让数字取证检测/恢复变困难的技术。 |
| DMCA | DMCA | 美国《数字千年版权法》，含"反破解条款"。 |
| Soft mod | 软改 / 软破 | 不需要焊接、纯软件实现的游戏机解锁方式。 |

