# 术语对照表 · Glossary

> 配套 Leonard 这篇 YM2149 → PAULA 文章的英中术语对照。按"硬件 → 软件 → 文化"顺序排列。

## 硬件 / Hardware

| 英文 | 中文 | 简注 |
| :--- | :--- | :--- |
| YM2149 | YM2149 音频芯片 | Yamaha 重制的 AY-3-8910，Atari ST 标配，3 路方波 + 1 个共享 envelope |
| AY-3-8910 | AY-3-8910 | General Instrument 1978 年推出的可编程声音发生器（PSG） |
| PAULA | PAULA 芯片 | Amiga 自定义音频芯片，1985 年首发，4 路 8-bit PCM 直接读主存 |
| Motorola 68000 / 68k | M68K CPU | Amiga 与 Atari ST 共用的 CISC 处理器 |
| COPPER | 协处理器 | Amiga 自定义芯片中的"显示协处理器"，可独立写寄存器、等待光栅 |
| Blitter | Blitter 块传输引擎 | Amiga 的位图加速器，与 Leonard 另一篇 AVX 文章主题对应 |
| Custom chip | 自定义芯片 | 大写 Custom Chips 指 Amiga 三剑客 PAULA / DENISE / AGNUS |
| Raster line | 光栅线 | 显示扫描的一行，COPPER `WAIT` 指令以此为单位 |
| Hardware timer | 硬件定时器 | Atari MFP 上的可编程计数器，被音乐家用来做 SID 音色 / Digidrum |
| Audio chip | 音频芯片 | 文章贯穿主线，本文区分"波形发生器型"与"采样回放型" |

## 音乐合成 / Sound Synthesis

| 英文 | 中文 | 简注 |
| :--- | :--- | :--- |
| Square wave | 方波 | YM2149 唯一原生波形 |
| Triangle wave | 三角波 | YM 的 envelope 形状之一，被 MadMax 用作声源 |
| Sawtooth wave | 锯齿波 | YM 的 envelope 形状之一 |
| Envelope (ADSR) | 包络（攻击/衰减/持续/释放） | 音色随时间的强度曲线 |
| Volume modulation | 音量调制 | 一个声音控制另一个声音的音量 |
| Pitch modulation | 音高调制 | 一个声音控制另一个声音的播放频率 |
| Attached voice | 附加声道 | PAULA 把两个声道串联做调制的特殊模式 |
| PCM sample | PCM 采样 | 时间离散、幅值离散的数字音频表示 |
| Digidrum | 数字鼓 | Atari 用 hardware timer 让 YM 直接吐 PCM 的著名 hack |
| SID voice | SID 音色 | 借助 timer 模拟 C64 SID 芯片音色 |
| Sync Buzzer | 同步嗡鸣 | YM 的 envelope reset trick |
| MadMax Buzzer | MadMax 嗡鸣 | 本文给 Jochen Hippel 招牌音色命名的术语 |
| .sndh | SNDH 格式 | Atari ST/STe 音乐归档格式 |

## 软件与工程 / Engineering

| 英文 | 中文 | 简注 |
| :--- | :--- | :--- |
| Demoscene | 演示场景 | 1980 年代起源的地下计算机艺术与极限优化文化 |
| Demo / Intro | 演示 / 小品 | demoscene 的两种作品规模，4K/8K/64K intro 是常见命题 |
| Frame rate / 50 Hz | 帧率 / 50 赫兹 | PAL 制式，欧洲机型主流 |
| MOD file | MOD 文件 | Amiga ProTracker 模块格式 |
| LSP / LSPlayer | LSP 播放器 | Leonard 自研的超快 Amiga MOD 播放器 |
| Replayer | 重放器 | 音乐驱动程序 |
| Driver | 驱动 | 在 demoscene 语境里特指音乐驱动 |
| Period / Volume registers | 周期/音量寄存器 | PAULA 用这两个值决定播放速率与响度 |
| Pre-computed stream | 预计算数据流 | 把所有 per-frame 状态在 PC 上算好，运行时只复制 |
| Self-chaining copper list | 自链接 copper 列表 | COPPER 末尾跳回自身，实现持续运行 |
| Sin-dots / sinus dots | 正弦点阵 | 经典 demoscene 效果，限定时间内画尽可能多的旋转点 |
| AVX | 高级向量扩展 | x86 的 SIMD 指令集，Leonard 另一篇文章主题 |
| Blitter ternary logic | 块传输三值逻辑 | Amiga blitter 的 256 种 minterm，与 AVX `vpternlogd` 对应 |

## 文化 / Culture

| 英文 | 中文 | 简注 |
| :--- | :--- | :--- |
| Oxygene | Oxygene 战队 | Leonard 1990 年共同创立的 Atari ST 演示团队 |
| Hannibal | Hannibal | Amiga 演示传奇人物，本文挑衅 Leonard 的人 |
| Leonard | Leonard | Arnaud Carré 在 demoscene 内的代号 |
| MadMax / Jochen Hippel | MadMax / Jochen Hippel | Thalion 御用音乐家，YM envelope 黑魔法发明者 |
| TEX | TEX | 80 年代末德国传奇 Atari 演示团 |
| Thalion Software | Thalion 软件公司 | 90 年代初德国游戏 / 演示发行商 |
| BigAlec | BigAlec | 本文最终配乐作者，Atari 音乐家 |
| pouet.net | pouet.net | demoscene 作品数据库 |
| WinUAE | WinUAE | 主流 Amiga 模拟器 |
| AmigAtari | AmigAtari | Leonard 2020 年发布的 Amiga 上模拟 Atari 音乐的 demo |
| Cycle-Op | Cycle-Op | Leonard 的 sin-dots 6405 记录 demo |
| 3D Demo 3 | 3D Demo 3 | Hannibal 后来打破纪录的作品 |

## 体系结构 / Architecture

| 英文 | 中文 | 简注 |
| :--- | :--- | :--- |
| Coprocessor | 协处理器 | 与主 CPU 并行执行的处理单元 |
| DMA | 直接内存访问 | PAULA 不经 CPU 直接读样本数据，是 0% CPU 的物理基础 |
| Chip RAM | 芯片内存 | Amiga 中可被 custom chips 访问的特殊内存区 |
| Memory-mapped I/O | 内存映射 IO | 把硬件寄存器映射到内存地址，COPPER 的核心语义 |
| Logarithmic amplitude | 对数幅度 | YM2149 的 32 级音量是对数刻度而非线性 |
| 8-bit signed PCM | 8 位有符号 PCM | PAULA 原生格式，-128..+127 |
| 16-bit modulation word | 16 位调制字 | attached voice 模式下一个 16 位等于一个音量值 |
| Per-sample modulation | 逐样本调制 | PAULA 的 attached voice 比 CPU 软件调音量精确得多 |
