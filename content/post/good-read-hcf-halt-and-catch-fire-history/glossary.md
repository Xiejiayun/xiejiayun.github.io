# 术语表：HCF / CPU 历史与现代 CPU 验证

| 英文术语 | 中文译名 | 说明 |
|---|---|---|
| Halt and Catch Fire (HCF) | 停机并起火 | 1960s 起源于 IBM 360 程序员幽默的虚构指令名，1977 年 Gerry Wheeler 在 BYTE 上正式赋给 MC6800 的 `0x9D` / `0xDD` 两条非法 opcode |
| HACOF | （Motorola 内部代号） | Daniels & Bruce 1985 年披露的 Motorola 6800/6802 内部对 HCF 的官方代号 |
| MC6800 / MC6802 | Motorola 6800 / 6802 | 1974 / 1977 年的两代 8 位 CPU；MC6802 在芯片内集成了时钟与 128 字节 RAM，方便单芯片系统设计 |
| illegal opcode / undefined instruction | 非法 opcode / 未定义指令 | 在 ISA 上没有指派含义的字节模式；不同 CPU 处理方式不同 |
| `$9D`, `$DD` | （6800 的两条经典 HCF 字节） | Wheeler 1977 命名的两个特定字节模式 |
| `$CD`, `$ED`, `$FD` | （6800 上的"慢速 HCF" 家族） | Doc TB 2019 实测，行为类似但频率更慢、地址线有抖动 |
| Program Counter (PC) | 程序计数器 | 指向下一条要 fetch 的指令地址。HCF 状态下 PC 仍递增 |
| address bus | 地址总线 | 16 位地址线。HCF 把它打成 16 位计数器，输出为 500 kHz 干净方波（在 1 MHz 时钟下） |
| Manchester encoding | 曼彻斯特编码 | 10BASE-T 以太网用的物理层编码，1 bit 数据需要 2 个跳变（与 HCF 文章无关，但相关网络层背景） |
| Test mode | 测试模式 | 芯片 bring-up / 验证阶段用来扫描内部状态的特殊运行模式 |
| BIST | Built-in Self-Test，内置自测 | 现代 CPU 上电后由硬件自动跑的测试电路，今天替代了 HCF 这类"穷人 BIST" |
| Scan chain | 扫描链 | DFT 核心结构。把所有触发器串成移位链，通过 JTAG 读写 |
| DFT | Design for Test，可测试性设计 | 在芯片设计阶段加入测试电路的工程实践 |
| JTAG | Joint Test Action Group | IEEE 1149.1 标准定义的 boundary scan 协议，用于芯片调试和测试 |
| F00F bug | F00F 缺陷 | 1994 年 Intel Pentium 上的 errata：`F0 0F C7 C8` 让 CPU 死锁直到 reset |
| LOCK prefix | LOCK 前缀（x86 的 0xF0） | 强制后续 RMW 操作原子化；F00F bug 与它有关 |
| `UD2` (`0F 0B`) | 显式非法指令 | x86 上 ISA 保留的 "guaranteed invalid" 指令，触发 `#UD` 异常 |
| `#UD` | undefined instruction exception | x86 上的 6 号异常向量，处理非法指令 |
| IDT | Interrupt Descriptor Table | x86 上中断 / 异常处理向量表；F00F 修复涉及把 IDT 标成只读 |
| F00F workaround | F00F 临时修复 | Linus 与 Intel 工程师合作在 OS 层用 trap handler 拦截 F00F 字节序列 |
| Sandsifter | （工具名） | Christopher Domas 2017 年发布的 x86 指令模糊测试工具 |
| micro-op (μop) | 微操作 | 从 Pentium Pro 起，x86 指令在前端被翻译成 μops，由乱序后端执行 |
| Spectre / Meltdown | 幽灵 / 熔毁 | 2018 年披露的推测执行侧信道攻击家族 |
| post-silicon validation | 流片后验证 | CPU 从晶圆厂出来后、在量产前的验证阶段 |
| RTL | Register-Transfer Level | 用 Verilog/VHDL 描述的寄存器级硬件设计 |
| errata | 勘误表 | CPU 厂商发布的"已知缺陷与变通方法"清单 |
| SLIP | Serial Line Internet Protocol | RFC 1055，1980s 年代的串口 IP 网络协议（背景知识） |
| Universal Chip Analyzer (UCA) | 通用芯片分析仪 | Doc TB 的开源芯片测试硬件，2019 年用它实测了 HCF 的精确行为 |
| BYTE magazine | BYTE 杂志 | 1975–1998 年间出版的著名计算机杂志；HCF 命名学起源于 1977 年 12 月号 |
| IEEE Design & Test | IEEE 芯片设计与测试期刊 | 1985 年 Daniels & Bruce 那篇 Motorola 自承 HACOF 的论文发表期刊 |
