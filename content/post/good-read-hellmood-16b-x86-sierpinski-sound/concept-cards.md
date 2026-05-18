# 关键概念卡片 · wake up! 16b

> 13 张卡片，覆盖 HellMood 这 16 字节程序需要理解的硬件、数学、汇编与 demoscene 文化背景。每张卡片独立成段，适合工程师早会或读书会做快闪展示。

---

## 卡片 01 · x86 实模式段 (real-mode segment)

**英文**: x86 real-mode segment
**一句话**: 8086 起 x86 CPU 的"段"是一个 16-bit 偏移指针寻址出的 65 536 字节窗口，地址 = 段 × 16 + 偏移。
**为什么重要**: 65 536 = $2^{16}$ 是 8-bit register cap 256 的 256 倍。HellMood 的程序刚好利用这个整除关系：每段 4 096 个 16-byte cell × 256 → 周期对齐。

---

## 卡片 02 · VGA 文本缓冲段 0xB800

**英文**: VGA text buffer
**一句话**: BIOS 文本模式 0 把 40 × 25 字符共 4 000 字节内存映射在物理段 0xB800，每字符占 2 字节（ASCII + 颜色属性）。
**为什么重要**: HellMood 把这个段当作算法的"画布"——既是输出（人眼看到字符）也是算法的中间状态（被 XOR 持续覆盖）。

---

## 卡片 03 · BIOS int 10h 的"非零清屏"

**英文**: BIOS int 10h text-mode init
**一句话**: 调用 `int 10h` 进入文本模式时，BIOS 把所有字符位置填 0x20 0x07（空格 + 浅灰前景黑色背景），而不是用全零清屏。
**为什么重要**: 这是 HellMood 算法的"宇宙学常数"——他依赖这个**确定的低熵背景**，使得后续 XOR 累积有可重现的起点。如果改为全零会损失多个字节。

---

## 卡片 04 · `lodsb` 指令

**英文**: lodsb (LOAD String Byte)
**一句话**: 把 `[DS:SI]` 的字节读入 `AL`，并把 `SI` 加 1（DF=0 时）。
**为什么重要**: 1 字节单指令完成"读+移动指针"两个动作，是 size-coding 圈子的常规武器。HellMood 的循环 8 字节中它占 1 字节。

---

## 卡片 05 · PC 扬声器 port 0x61 Bit 1

**英文**: PC speaker control port 0x61, bit 1
**一句话**: PC 主板上 i8255 PPI 端口 0x61 的 Bit 1 直接连扬声器锥的输出晶体管：写 1 把锥推出去、写 0 缩回去。其他 7 位是 NMI 控制、定时器使能、键盘控制等无关位。
**为什么重要**: HellMood 算法的初始值 2 (`0b00000010`) 恰好只动 Bit 1 → 写入 port 0x61 时只影响扬声器，其他位是 BIOS 状态字节，**不致命**。这是 1981 年 IBM PC 设计者留下的偶然礼物。

---

## 卡片 06 · 前缀和递推 (prefix sum)

**英文**: prefix-sum recurrence
**一句话**: 数列定义 $A^{(p)}[k] = A^{(p-1)}[k] + A^{(p)}[k-1]$，初值 $A^{(1)}[k] = c$ 时，解为 $A^{(p)}[k] = c \cdot \binom{k+p}{p-1}$。
**为什么重要**: HellMood 的内循环 `xor [si], al` + AL 持续累积本质就是这个递推。Pascal 三角形从代码里自然涌现。

---

## 卡片 07 · Lucas 定理 (1878)

**英文**: Lucas's Theorem
**一句话**: 对素数 $p$，$\binom{n}{k} \bmod p$ 等于 $n$ 与 $k$ 在 base-$p$ 展开下的对应位组合数的乘积。在 $p=2$ 时：$\binom{n}{k}$ 是奇数当且仅当 $k$ 的二进制 1 位是 $n$ 的子集。
**为什么重要**: 它告诉我们 Pascal 三角形 mod 2 是 Sierpinski 三角形——这是 HellMood XOR 算法能"自然结晶出分形"的根本原因。

---

## 卡片 08 · Wolfram Rule 60

**英文**: Wolfram Rule 60 cellular automaton
**一句话**: 一维元胞自动机，新状态 = 左邻居 XOR 自己当前值。属于 Wolfram 编号 256 条规则中的第 60 条。
**为什么重要**: HellMood 顺序遍历的算法等价于 Rule 60，因此输出形态与 Rule 60 的经典 Pascal-Sierpinski 图样完全相同。

---

## 卡片 09 · gcd 与"段绕圈数"

**英文**: gcd-induced cycle length
**一句话**: 步长 $s$ 在大小 $N$ 的循环数组中遍历 $N / \gcd(s, N)$ 个不同位置；需要绕 $s / \gcd(s, N)$ 圈才能回到起点。
**为什么重要**: HellMood 用 $\gcd(56, 65536) = 8$ 让"宏周期"从 4 096 变为 8 192——基频降一个八度，听觉上变深沉。这是用数论调音。

---

## 卡片 10 · 屏幕拓扑的模算术

**英文**: screen layout via modular arithmetic
**一句话**: 屏幕 80 字节宽时，-56 字节步长在屏幕上是 $-56 \bmod 80 = 24$ 字节，即上一行 + 12 列 (2 字节/字符)。$\gcd(12, 40) = 4$ 决定屏幕被切成 10 个等距列。
**为什么重要**: 没有任何视觉布局代码，整个 10 柱分形是数论的副产物。

---

## 卡片 11 · "demoscene size-coding"传统

**英文**: demoscene size-coding tradition
**一句话**: 1980 年代起的亚文化运动，比拼"在最少字节内做出最多视听效果"。常见赛道：64 byte intro / 256 byte intro / 4k intro。Outline Demoparty (Ommen, NL) 是该圈子年度赛事。
**为什么重要**: 这不是"工程化"代码——每一字节不可被重构、不可被替换。它是个人对硬件细节的极限理解。

---

## 卡片 12 · HellMood (Mathias Frohlich)

**英文**: HellMood, member of DESiRE / Alcatraz
**一句话**: 德国 demoscener，size-coding 圈子的代表人物。代表作：m8trix (2014, 8 字节)、Memories (2014, 32 字节)、wake up! 16b (2026)。
**为什么重要**: 他的作品横跨 12 年仍在用同一个 8086/CGA 平台——这本身就是对"加速主义"工程文化的一种抵抗。

---

## 卡片 13 · "约束即诗学"

**英文**: constraint as poetics
**一句话**: demoscene 圈子认为"size 限制"不是优化目标，而是作品的本体——脱离约束就不再是同一个作品。
**为什么重要**: 这与现代软件工程"代码越多越好、AI 量产越快越好"形成鲜明对比，是少数仍以"密度"为荣的文化场。
