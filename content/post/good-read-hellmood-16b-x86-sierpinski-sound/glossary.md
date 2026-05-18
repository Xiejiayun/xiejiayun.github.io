# 术语表 · wake up! 16b

英中对照，覆盖文章中的 demoscene、x86 实模式与数论术语。

| 英文 | 中文 | 简释 |
|---|---|---|
| demoscene | 演示场景 | 1980s 起的亚文化，比拼用极小代码做出视听演示作品 |
| size-coding | 体积编程 | demoscene 的子门类：在 64/128/256/4K 字节内完成作品 |
| boot sector | 引导扇区 | 软盘/硬盘的第一个 512 字节，BIOS 加载时直接执行 |
| real mode | 实模式 | x86 CPU 启动后的 16-bit 寻址模式，段+偏移 |
| segment | 段（寄存器） | x86 实模式下的 64 KB 内存窗口 |
| offset | 偏移 | 段内的 16-bit 字节地址 |
| VGA text mode | VGA 文本模式 | 40×25 或 80×25 字符显示模式，每字符 2 字节 |
| CGA / EGA | CGA / EGA | 早期 IBM PC 显卡标准 |
| BIOS | 基本输入输出系统 | PC 启动时的固件 |
| int 10h | 视频 BIOS 中断 | x86 实模式下的视频服务调用入口 |
| port 0x61 | 端口 0x61 | PC 主板 PPI 端口，控制扬声器/计时器/NMI |
| PC speaker | PC 扬声器 | 主板上的简单方波扬声器 |
| lodsb | 加载字节串 | x86 指令：AL ← [DS:SI]，SI++ |
| xor | 按位异或 | bit-wise XOR，相同位为 0、不同位为 1 |
| out | 端口输出 | x86 I/O 指令：把 AL 写入指定端口 |
| jmp short | 短跳 | 8-bit 偏移的相对跳转，2 字节 |
| accumulator | 累加器 | x86 中通常指 AX/AL 寄存器 |
| AL / AH / AX | AX 寄存器 | 16-bit AX 拆为高 8 位 AH + 低 8 位 AL |
| SI / DI | 源/目的索引寄存器 | x86 的 16-bit 字符串操作索引 |
| DS | 数据段寄存器 | 默认数据段 |
| prefix sum | 前缀和 | 数列累加运算 $S[k] = \sum_{i\le k} a_i$ |
| binomial coefficient | 二项式系数 | $\binom{n}{k} = n! / (k!(n-k)!)$ |
| Pascal triangle | 帕斯卡三角形 | 二项式系数的三角排列 |
| Lucas's theorem | Lucas 定理 | 计算 $\binom{n}{k} \bmod p$ 的数论结果 |
| Kummer's theorem | Kummer 定理 | $\binom{n}{k}$ 中素数 $p$ 的次数 = base-$p$ 加法进位数 |
| Sierpinski triangle | Sierpinski 三角形 | 经典分形，可由 Pascal mod 2 生成 |
| cellular automaton | 元胞自动机 | 基于局部规则的离散动力系统 |
| Wolfram code | Wolfram 编号 | Stephen Wolfram 对一维元胞自动机的 0-255 编号系统 |
| Rule 60 | 规则 60 | 一维元胞自动机：新状态 = 左邻 XOR 自己 |
| Rule 90 | 规则 90 | 一维元胞自动机：新状态 = 左邻 XOR 右邻 |
| Rule 110 | 规则 110 | 图灵完备的元胞自动机 |
| modulus | 模 / 取模 | $a \bmod n$ 表示余数 |
| modulo 256 | 模 256 | 8-bit 寄存器的天然模 |
| gcd | 最大公约数 | greatest common divisor |
| square wave | 方波 | 周期性在两个电压间切换的信号 |
| pulse width | 脉冲宽度 | 方波"高电平"持续时间，决定音色 |
| sample rate | 采样率 | 每秒采样次数 |
| timbre | 音色 | 声音的频率与谐波结构 |
| Outline Demoparty | Outline Demoparty | 荷兰 Ommen 每年举办的 demoscene 集会 |
| Pouet.net | Pouet 网站 | demoscene 作品索引与评分网站 |
| Demozoo | Demozoo 网站 | demoscene 作品/作者/活动数据库 |
| thumb up | 拇指赞 | Pouet.net 上的好评单位 |
| NASM | NASM 汇编器 | x86 汇编语言常用编译器 |
| opcode | 操作码 | 机器指令的字节级编码 |
| Light Gray on Black | 浅灰前景黑底 | VGA 颜色属性 0x07 |
