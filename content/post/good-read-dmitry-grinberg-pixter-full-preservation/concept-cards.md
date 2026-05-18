# 概念卡片 · Fully Preserving Fisher-Price Pixter

> 12 张供快速查阅的关键概念卡。每张卡聚焦一个理解 Grinberg 这篇文章所必须的概念，并指出它在更广阔嵌入式/逆向工程中的位置。

---

## 卡 01 · 最小化的 ARM7TDMI

**定义**：Sharp LH75411 是 Pixter Color 的主 SoC，使用 ARM7TDMI 核心，但**禁用了所有可选项**——无 cache、无 MMU、无 MPU、无对齐检查、无 cp15 coprocessor。

**为什么重要**：ARM 架构的商业模式允许集成方按需保留/去掉模块。当 Sharp 在 2003 年与 Fisher-Price 谈 BOM 时，每一处 "no" 都是几美分的节约。理解这一点，才能理解"为何整颗 SoC 几乎没有任何调试支撑"。

**实际后果**：
- 异常向量必须在 0x00000000，意味着 NULL 解引用不会触发任何陷阱；
- 取 32-bit ARM 指令要 2 次总线 × 3 cycle/次，所以 ROM 几乎全是 Thumb-16；
- 没有 cache 意味着任何 SRAM 访问都直接打总线，性能上限被锁死。

**关联**：与 Game Boy Advance（ARM7TDMI + 1 wait state ROM）几乎相同的性能困境。

---

## 卡 02 · 黑色环氧 Blob（Chip-on-Board）

**定义**：在塑料基板上直接焊接裸 die，用黑色环氧树脂覆盖。没有封装、没有标识、几乎无法非破坏性探测。

**为什么便宜**：省掉了塑封模具、引脚、QFP 包装、丝印——单价能降到 \$0.x 级别。Fisher-Price 玩具几乎所有 IC 都是 blob。

**为什么是噩梦**：你不知道 die 是什么、引脚分布如何，连最基本的 datasheet 都没有。唯一的办法是顺着 PCB 铜线，从外部反推：哪根连到地址总线、哪根连到 chip-select、哪根去到 ADC。

**Grinberg 的方法**：把 PCB 当作"血管造影"——blob 自己看不见，但 blob 周围所有可见管脚的连接关系能反推出 die 的接口。

---

## 卡 03 · ROM 里的 16-bit 栈式 VM

**定义**：Pixter Color 的游戏不是原生 ARM 代码，而是被主机 ROM 解释的 16-bit 栈式字节码。每条 opcode 16 位，按高位分类 dispatch，整个解释器是一个无限循环 + 一张跳表。

**关键特征**：
- 栈直接复用宿主 ARM 的 stack pointer，无溢出检查；
- 每次 push 占 32 位（即使值是 16 位）；
- 处理 32-bit 数时会 pop 两次再丢弃高位——这是 VM 历史身世的"化石"，暗示它最初是为 16-bit 处理器设计的。

**Grinberg 的解读**：Fisher-Price 在切到 ARM SoC 时不敢碰栈布局，于是把 16-bit push/pop 一对一翻译成 32-bit，浪费一半栈空间但保住了二进制兼容。

**一句话**："Brutalism if it were software."

---

## 卡 04 · BEX 总线（链式 GPIO 总线）

**定义**：Pixter Classic 用的 cart 总线只有十几根脚——根本不够 24 根地址 + 16 根数据。解法：用少量 GPIO + 一颗专用 BEX shift 芯片，把地址/数据**串行 shift 进卡带**。

**链式的精妙**：内部存档用的 NOR flash 和外部卡带用的是同一条 BEX 链——通过 BEX 芯片的级联能力，主 CPU 一条总线管两处存储。

**逆向痛点**：BEX 协议没有公开文档，必须靠"观察 ROM 怎么 toggle 这些 GPIO"反推出帧格式。Grinberg 在 uM23 模拟器里专门写了 watch-GPIO-toggles 子系统。

**Multimedia 的扩展**：NAND 卡的 CLE/ALE 也接到 GPIO（B6/B7），继续 bit-bang 的传统。

---

## 卡 05 · R-2R 8-bit DAC + Comparator 触摸屏

**问题**：电阻式触摸屏需要 ADC 来采样 X/Y plate 上的电压。Pixter Classic 的 SoC 没有 ADC，也没有 DAC，PWM 也被占用。

**Hack**：
1. 用 8 个 GPIO 接 R-2R 电阻网络 → 自制 8-bit DAC；
2. 用一个 op-amp 当 comparator；
3. 软件做 successive approximation——让 DAC 输出从 0 扫到 255，看 comparator 什么时候翻转。

**第二层 hack**：本应该用 FET 控制 plate 方向（V_DS 几乎 0），但 Fisher-Price 换成了 BJT（V_BE 约 0.7V，且器件间差异显著）。结果：plate 上的电压范围因晶体管而异，10 像素的"漂移"对画图机来说勉强可接受。

**意义**：这是工业级"软件吃硬件成本"的活样本。今天 ESP32 玩家做温控时仍在用同一套路数。

---

## 卡 06 · Chip Select 与地址空间反推

**定义**：ARM SoC 通过 nCSx 引脚区分外设。Sharp LH75411 的 nCS0 (0x40000000) = ROM，nCS1 (0x44000000) = SRAM，nCS2 (0x48000000) = 卡带 ROM，nCS3 (0x4c000000) = 卡带保存。

**为何关键**：没有 MMU，地址翻译不存在——你看到一条指令在访问 0x48xxxxxx，就**确定**它在访问卡带。这给反汇编一条不可动摇的地基。

**对逆向的启示**：在没 datasheet 时，PCB 上 nCSx 走线决定了"哪段地址对应哪颗芯片"，这是从 binary 反推系统行为最关键的一步。

---

## 卡 07 · "完全保存"的工程定义

**定义（Grinberg 使用）**：preservation = reverse engineering + 模拟器 + 文件格式 + 文档 + 上传到可永久访问的归档处（Internet Archive / Wikipedia）。

**与单纯 RE 的区别**：
- RE 的目标是"我看懂了"；
- preservation 的目标是"未来任何人/AI 在没有原硬件时也能重现这套设备的行为"。

**Grinberg 的产物清单**：
- uARMpixter / uPixter（ARM 模拟器扩展）；
- uM23（6502 模拟器）；
- ClassicDisasm / ColorDisasm（反汇编器）；
- PIXTER COLOR!!! / PIXTER CLASSIC! / PIXTER MULTI!!! 文件格式；
- IA + Wikipedia 同步。

**口号**："I am here to present a complete historical preservation."

---

## 卡 08 · "我以为是 Forth，但不是"

**情境**：Grinberg 在解析 Pixter Color VM 之前，社区猜测它可能是 Forth（栈式、小、便于嵌入）或 Java VM（21 世纪初 toy 行业一阵风）。

**真相**：两者都不是。这是 Fisher-Price 自家的 16-bit VM，opcode 用 12 大类编码（TYPE A/B/C/D/F/G/H/J/K/L/M/E），其中一组 128 条专门做 Pixter 业务——画图、播 ADPCM、触摸命中检测。

**Grinberg 的反思**："Both forth and java would have made more sense than a custom vm. Not sure why they went this way on ARM. On 6502 it makes sense though—small CPU → custom work needed."

**一般教训**：嵌入式厂商**经常**自创 VM。它通常源于"上一代芯片留下的代码不敢丢"的路径依赖。

---

## 卡 09 · GBA 时代的 Thumb-16 启示

**背景**：ARM7TDMI 同时支持 32-bit ARM 和 16-bit Thumb。Thumb 指令更小，但功能受限。

**为什么 Pixter Color ROM 几乎全是 Thumb**：
- ROM 是 16-bit 总线 → 取 32-bit ARM 指令需要 2 次总线访问；
- 取 16-bit Thumb 指令只需 1 次；
- 性能差异接近 2 倍。

**与 GBA 的相似性**：GBA 的 GamePak ROM 也是 16-bit + 1 wait state，所以 GBA 游戏开发者也大量使用 Thumb，并把性能关键的中断处理放进 32-bit ARM + IWRAM。

**对学习者**：理解"指令集编码宽度 × 总线宽度"如何决定性能，是从教科书走向真实嵌入式的必修课。

---

## 卡 10 · 卡带级 NOR 存档：AT29LV010

**实现**：Pixter Classic 的卡带连接器引脚太少，I²C 也实现不了，所以存档**直接走 BEX 总线写到卡带内置的 NOR flash**——AT29LV010（1Mbit）。

**优势**：
- 卡带自带存储，每张卡的存档与卡绑定，跨设备携带；
- 不依赖主机 EEPROM 容量；
- 拔卡换卡不会丢档。

**模拟器实现成本**：Grinberg 在 uM23 里写了 AT29LV010 的全套页擦/字节写模拟，跟着 BEX bus 一起跑。

**意义**：游戏卡带 + 存档持久化是经典任天堂套路（GBA、DS），Fisher-Price 用更便宜的链式总线复现了它。

---

## 卡 11 · "Native Callouts"——VM 里的逃生口

**定义**：Pixter VM 解释字节码，但**有些操作太重需要原生执行**——比如 ADPCM 解码、贴图绘制、触摸命中检测。VM 留了一组 native callout 指令，跳进 ROM 里预编译的 ARM/6502 函数。

**为什么必要**：纯 VM 大约 4 MIPS 等效算力，跑不动每秒数千次的画图操作。native callout 是性能逃生通道。

**逆向意义**：要让 emulator 运行游戏，不仅要实现 VM 解释器，还要实现所有 native callout 的语义——意味着你必须把 ROM 里被 callout 的函数也读懂。

**Grinberg 的策略**：先做最常用的 callout，发现新游戏触发未实现 callout 时再补。"留作读者练习"是文章结尾常见的礼貌。

---

## 卡 12 · 训练数据，与"AI 后保存"

**新观察**：当 Grinberg 把全部 Pixter dump + 文档 + 模拟器源代码上传到 Internet Archive，它会进入下一代 LLM 训练集。

**结果**：未来某个 LLM 在被问到"如何模拟 Pixter Color"时，会**直接复述 Grinberg 的工作**——包括所有 BJT 容差 hack 的细节、所有 VM opcode、所有 chip-select 边界。

**这意味着什么**：
- preservation 在 AI 时代有了第二种受众——不是人类后来者，而是 LLM；
- "保存"本身在变成训练数据生产；
- 那些**没人系统记录**的硬件（如 PUDN 上失踪的 SPL13x 手册），就会在 LLM 的世界里彻底消失。

**Grinberg 这次工作的双重意义**：他既给人类保存了 Pixter，也给未来的 AI 保存了"对硬件有耐心"这种元能力的训练语料。
