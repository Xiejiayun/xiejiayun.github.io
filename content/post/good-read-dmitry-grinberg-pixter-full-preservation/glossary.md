# 英中对照术语表 · Pixter Preservation

> 覆盖本文涉及的嵌入式硬件、ARM/6502 架构、触摸屏、NAND、虚拟机与逆向工程领域常见术语，约 38 条。

## A — 架构与处理器

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **ARM7TDMI** | ARM7TDMI 处理器核 | 1995 年发布，无 cache 无 MMU 可选，支持 32-bit ARM 与 16-bit Thumb，是嵌入式 90s–00s 主力。 |
| **Thumb instruction set** | Thumb 指令集 | ARM 的 16-bit 紧凑编码，密度更高，特别适配 16-bit ROM 总线。 |
| **MMU** (Memory Management Unit) | 内存管理单元 | 提供虚拟地址→物理地址翻译及保护，LH75411 上**完全没有**。 |
| **MPU** (Memory Protection Unit) | 内存保护单元 | MMU 的简化版，只提供区段保护无翻译，LH75411 上**也没有**。 |
| **TCM** (Tightly Coupled Memory) | 紧耦合内存 | 紧贴 CPU 核的低延迟 RAM，单 cycle 访问。LH75411 有 16KB TCM。 |
| **AHB** (Advanced High-performance Bus) | AMBA AHB 总线 | ARM SoC 内部连接外设/RAM 的标准高速总线。 |
| **6502** | 6502 处理器 | 1975 年的 8-bit CPU，与其衍生体（如 Sunplus SPL13x）至 2000s 仍广泛用于玩具。 |
| **R-2R DAC** | R-2R 电阻梯型 DAC | 用两种阻值的电阻拼出二进制加权电压输出，可由 GPIO 直接驱动。 |
| **wait state** | 等待周期 | 总线访问时插入的空 cycle，让慢速存储有时间响应。 |
| **cache** | 高速缓存 | 把最近用过的内存近 CPU 存放以减少总线延迟。LH75411 完全无 cache。 |

## B — 总线与接口

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **nCS** (chip select) | 片选信号 | 拉低后选中对应芯片参与总线交易。 |
| **nOE / nWE** | 输出使能 / 写使能 | 读/写时序的两条核心控制线。 |
| **BEX bus** | BEX 链式总线 | Fisher-Price 在 Pixter Classic 使用的私有协议，用 GPIO 串行 shift 出地址/数据，并可链式串接多颗芯片。 |
| **I²S** | Inter-IC Sound | 数字音频串行接口，Pixter Multimedia 用它喂 TLV320DAC26。 |
| **SPI** | 串行外设接口 | 主从同步通讯，Pixter Multimedia 用它配置 DAC（bit-bang）。 |
| **NAND flash** | NAND 闪存 | 大容量但需要 CLE/ALE 控制的存储器；Multimedia 卡用 NAND。 |
| **CLE / ALE** | Command / Address Latch Enable | NAND 协议的命令/地址区分信号。 |
| **NOR flash** | NOR 闪存 | 字节随机可读、写需擦除的存储器；Pixter Classic 卡内存档用 AT29LV010 NOR。 |
| **SRAM** | 静态随机存储器 | 不需要刷新的高速 RAM；LH75411 板上有 128KB SRAM。 |

## C — 封装与制造

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **chip-on-board (CoB)** | 板载裸 die | 直接把硅 die 焊在 PCB 上再覆环氧，无独立封装，省成本但极难逆向。 |
| **black blob** | 黑色环氧 blob | CoB 上覆盖的黑色树脂；社区俚语，象征"不可见的廉价 IC"。 |
| **LQFP** | 低剖面方形扁平封装 | 引脚分布在四周的塑封 IC，易于探针，Pixter Color 主 SoC 的"幸运"封装。 |
| **bill of materials (BOM)** | 物料清单 | 一台设备使用的所有元件成本表，是 cost-cut 谈判的中心。 |
| **BJT** (bipolar junction transistor) | 双极结型晶体管 | V_BE ≈ 0.7V 的压降使其在开关应用中线性度不佳，比 FET 便宜。 |
| **FET** (field-effect transistor) | 场效应晶体管 | 电压控制、几乎无导通压降，更适合数字开关。 |

## D — 触摸屏

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **4-wire resistive touch panel** | 四线电阻式触摸屏 | 两片透明电阻 plate 叠加，靠压力接触读取电压坐标。 |
| **successive approximation** | 逐次逼近 | ADC 的常见算法，逐位决定输出值；Pixter Classic 用软件 + DAC + comparator 实现。 |
| **comparator** | 比较器 | 输出"输入是否高于参考"的二值信号，可由 op-amp 充当。 |

## E — 虚拟机与字节码

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **bytecode VM** | 字节码虚拟机 | 把指令编码成 8/16 位字节流，由解释器执行；Pixter 自创了 3 套。 |
| **stack-based VM** | 栈式虚拟机 | 操作数在栈上传递，无寄存器抽象；类似 Forth、JVM。 |
| **opcode** | 操作码 | 单条 VM 指令的二进制编码。 |
| **dispatch** | 指令分派 | 根据 opcode 跳转到对应处理函数的过程；Pixter VM 用嵌套位字段 dispatch。 |
| **native callout** | 原生调用出口 | VM 内调用宿主原生函数的指令，用于性能关键路径。 |
| **ADPCM** | 自适应差分脉冲编码调制 | 一种音频压缩方法，Pixter 用它存放语音/音效。 |

## F — 保存与逆向

| 英文 | 中文 | 一句话说明 |
|---|---|---|
| **reverse engineering (RE)** | 逆向工程 | 从产物推断设计；常以"理解"为目标。 |
| **preservation** | 数字保存 | 在 RE 之上产出可被未来执行的工件——模拟器、文件格式、文档。 |
| **disassembler** | 反汇编器 | 把机器码翻译回汇编（或 VM 字节码翻译回伪汇编）。 |
| **emulator** | 模拟器 | 用软件复现某硬件的行为；Grinberg 的 uARM/uM23 系列。 |
| **datasheet** | 数据手册 | 芯片厂提供的官方电气与寄存器文档。LH75411 有，SPL13x 失踪。 |
| **bit-bang** | 软件位翻转 | 用 CPU 直接控制 GPIO 来"假装"一个硬件协议（SPI、I²C、NAND）。 |
| **JTAG** | 边界扫描调试接口 | 工业级嵌入式调试通道；Pixter 没暴露 JTAG。 |
