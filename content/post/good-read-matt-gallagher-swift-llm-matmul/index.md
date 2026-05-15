---
title: "【好文共赏】把 Swift 推到 1.1 Tflop/s：Matt Gallagher 用十种实现，在 M3 Max 上手写 LLM 训练，把矩阵乘法跑出 382 倍提升"
description: "Cocoa with Love 主理人 Matt Gallagher 不用任何框架库，从 plain C 到 Metal，演示 Swift 矩阵乘法十种实现的全栈优化之路：MutableSpan、Relaxed.multiplyAdd、InlineArray、DispatchQueue.concurrentPerform、保密的 AMX 协处理器、Metal tiled kernel——一篇真正具体到汇编指令的 Apple Silicon 性能编年史。"
date: 2026-05-15
slug: "good-read-matt-gallagher-swift-llm-matmul"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Swift
    - Apple Silicon
    - 性能优化
    - 矩阵乘法
    - Metal
    - AMX
    - LLM
draft: false
---

> 📌 **好文共赏 · Editor's Pick**
>
> - **原文**：[Training an LLM in Swift, Part 1: Taking matrix multiplication from Gflop/s to Tflop/s](https://www.cocoawithlove.com/blog/matrix-multiplications-swift.html)
> - **作者**：Matt Gallagher（[Cocoa with Love](https://www.cocoawithlove.com/) 主理人，iOS/macOS 资深独立开发者）
> - **发布时间**：2026 年 4 月 18 日
> - **阅读时长**：约 35 分钟（含代码与汇编片段）
> - **多模评分**：Opus 9.0 / Sonnet 8.8 / Gemini 8.7 — **综合 8.85 / 10**
> - **一句话推荐**：一次极少有人能写出来的"全栈"性能讲座——不是 PyTorch 算子优化的高谈阔论，而是一个独立开发者用十个版本、上百行汇编、若干被 Apple 刻意藏起来的指令，把 Swift 训练 GPT-2 的速度推到比纯 C 快 30 倍、比单线程 OpenMP 快 30 倍、最终冲过 1 Tflop/s 的门槛。

## 一、为什么值得读

这篇文章在 Hacker News 上拿到 260+ 分，但和大多数 HN 头条不同的是：它不是观点文，不是公司公告，也不是市场分析——它是一份**可复现、可量化、可单步演进**的工程笔记。Matt Gallagher 不是在告诉你"Apple Silicon 多厉害"，而是把同一份 `matmul_forward`（GPT-2 124M 模型里那条贯穿前向反向的矩阵乘法）写了十遍，每次只改一个变量，每次都给出 tokens/s 和训练迭代/s 的实测，每次都贴出对应的 ARM64 汇编片段，让读者亲眼看到 Swift 编译器做了什么、漏了什么、需要被怎样"哄"才能吐出和 C 同样紧凑的指令流。

之所以值得被推荐到「好文共赏」，原因有四：

**第一，它是真正的"全栈优化"案例。** 大多数"如何优化"的文章只覆盖一层——要么讲 SIMD、要么讲多线程、要么讲 GPU。Matt 这篇文章从最朴素的四重循环 C 代码（`val += inp[bt*C+i] * weight[o*C+i]`），一路打到 `fmla.4s` 的 SIMD FMA、再到 Apple 从来不肯公开命名的 AMX 协处理器、最终落到 Metal 的 `threadgroup` tile 化 kernel。这种"一杆子捅到底"的能力，在 2026 年的内容生态里已经罕见到值得专门记录。

**第二，它揭穿了一个普遍的迷思——"Swift 比 C 慢"。** 一开始 Basic Swift 是 C 的 7.3%（即慢 13 倍多），到 Fast Swift 居然超过了 C 的 106.6%。这背后牵涉到 Swift 6.2 新引入的 `MutableSpan`、`InlineArray`、Swift Numerics 的 `Relaxed.multiplyAdd`、以及一系列编译器优化 flag。Matt 把这些"为什么慢"和"为什么能追平"的细节写得极其具体——不是抽象的"避免分配内存"，而是 Instruments 截图、`_ArrayBuffer.beginCOWMutation()` 的具体调用栈、汇编层的 `fmul.4s` 对比 `fmla.4s`。

**第三，它是 Apple Silicon 内部架构最难得的公开教材之一。** 关于 AMX（Apple Matrix Coprocessor）——这个被 Apple 始终称作"machine learning accelerators"而拒绝公开 ISA 的协处理器——你能在文档里找到的资料几乎为零。Matt 直接调用了社区反向工程出来的 `AMX_MATFP`、`AMX_LDX`、`AMX_LDY`、`AMX_STZ` 指令，做了一个 16×16 的 tile 矩阵乘 inner loop，并坦诚交代："Apple 通过 Accelerate 框架的实现比我快 20%，而且他们能随时改 ABI 把这段代码弄废。"这种"把刀架在自己脖子上写代码"的态度，在 Apple 平台社区里是真正的稀缺品。

**第四，它给本地 AI 浪潮提供了"算力上限"的参考系。** 这点与我们之前推荐的 [《antirez 一周写出 DS4》](/post/good-read-antirez-ds4-local-inference/) 互为表里——antirez 谈的是怎么把 DeepSeek v4 Flash 在 128GB MacBook 上"跑得动"，Matt 谈的是怎么把"GPT-2 124M 训练"在同一台 Mac 上"跑得快"。前者关注 quantization 和推理调度，后者关注矩阵乘内核与硬件 affinity——但它们的共同前提都是同一个：本地推理/训练，必须真正去理解 Apple Silicon 的每一个执行单元。

> 原文：*"That means it's time for my favorite game: optimize Swift until it's faster than C."*

这句开场白基本能定义这篇文章的气质：不是布道，不是炫技，而是一种工程师对编译器、对硬件、对自己代码非常诚实的拷问。

---

## 二、核心观点深度解读

### 2.1 起点：382 倍提升的"基准线"为什么是 2.8 Gflop/s

文章的对照实验起点是 Karpathy 的 [llm.c](https://github.com/karpathy/llm.c)——一份大约 1000 行的纯 C 实现，模拟 GPT-2 124M 模型的完整训练流程（前向 + 反向 + 权重更新）。Matt 选这份代码做参照系有两层原因：

- **结构透明**：llm.c 没有任何外部库依赖，连 BLAS 都没用——所以"compute"这一步真的就是那个朴素的四重 for 循环。任何性能差异都能被归因到具体的代码改动，而不是被某个隐藏的 vendor 库吃掉。
- **代表性强**：GPT-2 虽然小（124M 参数），但它的 forward + backward 已经覆盖了所有现代 LLM 的核心算子——matmul、attention、softmax、gelu、layer norm。Karpathy 给出了一个估算公式：完整一次训练迭代的浮点运算量约为 `6 × N × D`，其中 N 是参数量（124,439,808）、D 是 batch × seq_len（4 × 64 = 256）。算下来一次迭代大约 **2 × 10¹¹ 次浮点运算**，即 0.2 TFLOP。

而 llm.c 在 M3 Max CPU 上跑一次迭代花 5.7 秒（0.174 迭代/秒）——对应大约 **35 Gflop/s** 的吞吐。这个数字本身已经不算低，但相比 GPU 理论上 15 Tflop/s 的算力，CPU 上空有大量浮点单元没被喂饱。

Matt 用 Basic Swift 直接照抄 C 写法的版本，性能落到 **2.8 Gflop/s**——意味着 Swift 编译器在最朴素的写法下，只用了 8% 的 C 性能。这是后续优化的起点，也是文章里那个"382 倍提升"的最末一格。

> 原文：*"In 1999 Apple ran ads for the PowerMax G4 claiming its 1 Gflop/s capability made it a weapon in the eyes of the US military. Now 2.8 Gflop/s is completely unacceptable."*

这种把性能数字放回历史坐标系的笔法很 Matt——他在 [《Cocoa with Love》](https://www.cocoawithlove.com/) 写了十几年 iOS 性能优化，常常用一个旧时代的对比镜头来给读者建立直觉。

### 2.2 第一刀：MutableSpan 把 Array 的 CoW 开销切掉

性能从 2.8 Gflop/s 跳到大约 **9 Gflop/s（训练 24.0%）**，第一关键改动只是加了一行：

```swift
var out = out.mutableSpan
```

为什么有这么大的差距？答案在 Instruments 给出的火焰图里——最热的函数不是矩阵乘内层循环，而是 `_ArrayBuffer.beginCOWMutation()`。Swift 的 `Array` 类型有 copy-on-write（写时复制）语义，每次你做 `out[idx] = value` 时，Swift 都要确认"现在这个 buffer 是不是只有我一个 owner？如果不是，要先复制一份再写"。即使在实际运行时所有 Array 都只有一个 owner，这个**uniqueness 检查**本身也成了性能瓶颈。

Swift 6.2 引入的 `MutableSpan` 是 Apple 对这类场景的官方答案：一个零拷贝、零引用计数、零 CoW 检查的可变内存视图。Matt 在原文中坦言这可能"是个 bug 或回归"——他记得 2024 年写这段代码时没有这个问题，但 2026 年 Xcode 编译出来的版本上，CoW 检查变成了 dominant cost。

这一改动有趣的地方在于：**它对纯前向 (`matmul_forward`) 影响很小（0.054 → 0.056 tokens/s），但对训练（前向 + 反向 + 更新）的影响是 3 倍以上（0.014 → 0.042 迭代/s）**。原因是反向传播阶段需要大量临时 buffer 的就地修改，CoW 检查在那条热路径上被放大了几个数量级。这种"前向看不出来、反向被放大"的特征是真实生产代码里非常典型的现象，但很少在博客里被这么清晰地切片展示。

### 2.3 关键飞跃：Relaxed.multiplyAdd 让 Swift 用上 FMA

这是整个文章里我最喜欢的一段。Matt 把同一段 C 和 Swift 代码编译出来的汇编贴在一起——

C 版本（`-ffast-math -O3`）：

```asm
fmadd  s0, s17, s16, s0
fmadd  s7, s17, s16, s7
fmadd  s4, s17, s16, s4
...（连续 8 条 fmadd）
```

Swift 默认版本：

```asm
fmul.4s  v1, v1, v5
mov      s5, v1[3]
mov      s17, v1[2]
...（一大堆 mov）
fadd     s0, s0, s7
fadd     s0, s0, s4
...（最后散开成单独的 fadd）
```

C 用一条 `fmadd`（fused multiply-add）就完成 `a += b * c`，而 Swift 不敢这么做——因为 IEEE 754 严格语义下，`(b*c) + a` 和 `fma(b, c, a)` 的舍入结果可能不同。Apple Clang 默认给 C 开了 `-ffast-math`，但 Swift **没有这个 flag**，所以 Swift 老老实实地拆成乘和加。

Matt 找到的解药是 **Swift Numerics 库的 `Relaxed` 命名空间**：

```swift
val = Relaxed.multiplyAdd(inp[bt * C + i], weight[o * C + i], val)
```

`Relaxed` 这个命名很有 Apple 风格——不叫 `Fast`，不叫 `Unsafe`，而是"放松"，暗示着对舍入精度的约束被放松了，但不暗示任何危险。背后的语义是 "允许编译器进行不损失太多精度但可能改变舍入位的优化"，于是 `fmla.4s`（NEON SIMD 版的 fused multiply-add）就被启用了。

加上这一行之后，性能直接从 9 Gflop/s 跳到 **75 Gflop/s 以上（训练 85%）**。一行代码 9 倍提升——这是这篇文章里"投资回报率"最高的一处改动。

需要特别注意的是，Matt 谨慎地**不对 `gelu_backward` 使用 Relaxed**——因为 llm.c 的 C 代码里也专门用 `#pragma float_control(precise, on)` 关掉了 `gelu_backward` 的 fast-math。GELU 反向传播对 numerical stability 比较敏感，在这种地方追求 FMA 反而会引入训练发散风险。这种"知道什么时候不要快"的取舍，是性能工程师和"追性能盲流"的本质区别。

### 2.4 InlineArray + LOOP_UNROLL：让 SIMD pipeline 真正喂饱

文章把朴素 C 代码"美化版"换成了 llm.c 真实使用的"丑版"——按 8 步 stride 外层循环 + LOOP_UNROLL 内层手动展开：

```c
for (int obt = 0; obt < B * T; obt += LOOP_UNROLL) {
    for (int o = 0; o < OC; o++) {
        float result[LOOP_UNROLL];
        ...
        for (int i = 0; i < C; i++) {
            float w = weight[i + o * C];
            for (int ibt = 0; ibt < LOOP_UNROLL; ibt++) {
                result[ibt] += inp[(obt+ibt) * C + i] * w;
            }
        }
        ...
    }
}
```

C 之所以能这样写并保持高性能，关键在于 `float result[LOOP_UNROLL]` 是**栈分配数组**——`-O3` 把它完全保留在寄存器里，没有任何内存访问开销。

而 Swift 2024 年版本里**没有等价物**——你要么用 `Array<Float>` 在每轮循环里分配一次（致命昂贵），要么手动展开成 8 个独立变量（极丑且不可维护）。Swift 6.2 终于给了官方答案：`InlineArray<8, Float>`。它是固定大小、值类型、栈分配的数组类型，行为完全对标 C 的 stack array。

加入 InlineArray + 手动 stride 后，Swift 性能首次**超过了 C 的单线程版本**（106.6%）。汇编里你能看到一长串连续的 `fmla.4s` 和 `fadd.4s` 指令——和 C 几乎一模一样，只是 Swift 编译器更倾向于选择 SIMD 版本（4 个 float 一组的 `fmla.4s`），而 C 选择了标量版本（单个 float 的 `fmadd`）。SIMD pipeline 一旦被喂饱，反而让 Swift 略胜一筹。

这里的工程教训其实很普世：**寄存器分配的友好度往往比算法本身更重要**。如果你不能给编译器一个"我保证不动这块内存"的承诺（无论是通过 InlineArray、`final` 修饰还是 ownership 标注），它就会保守地往堆上放、加屏障、加引用计数——而这些 overhead 在浮点密集的内层循环里会被放大成 5-10 倍的性能差。

### 2.5 多线程：Swift Concurrency 在矩阵乘场景下输给了 GCD

llm.c 用 `#pragma omp parallel for` 把外层循环交给 OpenMP——一行注释，性能从 35 Gflop/s 跳到 155 Gflop/s（446% 提升）。

Swift 这边的故事就复杂多了。Matt 试了 Swift 6 推荐的 `TaskGroup`，结论是："about the same speed，但需要 `withUnsafeMutableBufferPointer` 让 buffer 逃出 closure 作用域（理论上违反 Swift 6 的并发安全），而且没有任何性能优势。"

最终选择是 `DispatchQueue.concurrentPerform`——一个从 Mac OS X Snow Leopard（2009）就存在的 GCD 老接口。它的关键优势是 closure **不是 `@escaping` 的**，所以可以安全传 `Span<Float>` 进去而不触发引用计数或拷贝。

最终的多线程 Swift 代码大约长这样（节选要点）：

```swift
let tileCount = BT / LOOP_UNROLL
let workerCount = max(1, ProcessInfo.processInfo.activeProcessorCount)
let chunkSize = max(1, (tileCount + workerCount - 1) / workerCount)
let chunkCount = (tileCount + chunkSize - 1) / chunkSize

out.withUnsafeMutableBufferPointer { outBuffer in
    let outStorage = SendableUnsafeMutableBuffer(baseAddress: outBuffer.baseAddress!)
    DispatchQueue.concurrentPerform(iterations: chunkCount) { chunk in
        // 每个 chunk 独立处理若干个 tile
        ...
    }
}
```

性能：**5.4 倍提升**（558.5% over llm.c 单线程），但相对于 16 核心的 M3 Max，5.4 倍意味着实际并行效率只有 33%——剩下 67% 被内存带宽吃掉。Matt 在原文承认："we're likely getting constrained by our memory traversal"。

这一节其实暴露了 Swift 6 并发模型在数值计算场景下的几个软肋：

1. **没有"slice and concurrently mutate"原语**——你不能对一个 `Array<Float>` 切分成不重叠的 ranges 然后并发写。
2. **`Sendable` 的传播太严格**——`MutableSpan` 不是 Sendable，所以无法跨 task 边界传递。
3. **没有 `#pragma omp parallel for` 这种 "trust me bro" 语义**——Swift 总要求你证明并发安全，证明的代价就是 `withUnsafeMutableBufferPointer` 这种"我向你保证我知道我在做什么"的开口。

Matt 的结论很坦诚："This is the iteration where I think: the C code looks better."——多线程是 Swift 在这场对比中**第一次输给 C 的可读性**。

这点与我们之前讨论过的 [《把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上》](/post/good-read-haskell-mercury-production-engineering/) 中"类型安全的代价"形成有趣的对照——Haskell 在金融系统里付出更多类型噪音换来更强保证，而 Swift 在 ML kernel 里付出更多 `@unchecked Sendable` 的丑陋换来同样的运行时性能。每种语言都在某个层面让你"为安全交税"。

### 2.6 AMX：那个被 Apple 雪藏的协处理器

> 原文：*"That's where we arrive at a strange position: it's a secret."*

Apple Silicon 内部有一个叫 AMX（Apple Matrix Coprocessor）的协处理器单元——它专门做 16×16 矩阵 outer product 累加。Apple 在公开材料里只把它称作 "machine learning accelerators"，从未公开过 ISA、操作码、内存模型，但它的存在通过 Accelerate 框架的 BLAS 实现被间接证实，并被社区（特别是 [Dougall Johnson](https://github.com/corsix/amx) 和 [Peter Cawley](https://github.com/corsix/amx)）通过反向工程绘出了完整指令集。

Matt 用反向工程出来的指令直接写了一个 inner loop：

```swift
for k in 0..<innerCount {
    let lhsBase = lhsPanel + (k * tileRows)
    amx_ldx(lhsBase.amxXYOperand)
    for tile in 0..<accumulatorCount {
        let rhsBase = rhsPanels + (tile * innerCount * tileRows) + (k * tileRows)
        amx_ldy(rhsBase.amxXYOperand)
        amx_matfp(amxMatFPF32 | (UInt64(tile) << 20))
    }
}
```

核心指令是 `AMX_MATFP`，它做一个 16 元素向量 × 16 元素向量的 outer product，结果累加到一个 16×16 的 tile 寄存器（叫 Z 寄存器组）里。配合 `AMX_LDX / LDY`（加载 X、Y 操作数）和 `AMX_STZ`（写出 Z tile），就构成了一次完整的"载入 → 乘加 → 写回"循环。

性能：**比多线程 Swift 又快 1.67 倍**（958.8% over llm.c 单线程，即约 **335 Gflop/s**）。

这一节里最值得借鉴的不是 AMX 本身（普通开发者根本不会去碰未文档化的指令），而是 Matt 那段警告：

> 原文：*"I'm having fun here but it should be clear: don't use Apple's AMX instructions directly. Go through the Accelerate framework for your own apps. Apple keep this 'undocumented' so they can break binary compatibility at any time."*

这段话其实揭示了 Apple Silicon 整个软件栈的"权力结构"：**Apple 把硬件分成两层——公开层（Accelerate / BNNS / MPSGraph）和私有层（AMX / NPU 内部状态机）**。Accelerate 是稳定 ABI，但它要付出至少一次跨 framework 调用的开销；AMX 是裸金属，但 Apple 可以在下一代芯片里换 opcode 让你的代码瞬间崩溃。这种"快慢双轨"的设计哲学，和 [我们之前讨论的 Apple M5 MIE 防线](/post/good-read-calif-mie-bypass-apple-m5-kernel/) 是一个硬币的两面——Apple 既不希望开发者直接碰 microarchitecture，也要给 Accelerate 这种官方库足够的性能空间去差异化竞争。

更深一层，AMX 这种"反向工程才能用"的硬件单元也暴露了一个生态问题：**Apple Silicon 真正最快的指令对绝大多数开发者是不可见的**。如果你不是 Apple 自己的 Accelerate / Core ML / MPS 团队，你能调用的"快"永远是经过 framework 抽象、ABI 稳定化、API 保守化的"次快"。这与英伟达 CUDA 把所有 SM 指令完全暴露的开放策略形成鲜明对比——后者催生了 cuBLAS、cuDNN、xFormers、FlashAttention 这种"普通开发者也能写极致内核"的生态。

### 2.7 Metal Tile 化：终于跨过 1 TFLOP/s

GPU 部分文章给了三档：

| 实现 | tokens/s | 训练迭代/s | vs llm.c |
| --- | --- | --- | --- |
| Basic Metal | 4.29 | 2.302 | 1315% |
| Threaded Metal | 6.211 | 3.858 | 2205% |
| Tiled Metal | 11.123 | **5.351** | **3058%** |

Basic Metal 就是把 Basic Swift 的内层循环直接搬到 Metal kernel 里——每个 thread 算一个输出元素。性能并不比 AMX 强多少（因为 GPU 启动调度有 latency overhead）。

Threaded Metal 是把 threadgroup 从 1×1 改成 16×16，让 thread block 大小匹配 SIMD group。这是一个**几乎免费的优化**——只改一个 `MTLSize` 参数就拿到 67% 提升。

Tiled Metal 才是真正的"GPU 内核工程"。Matt 在 kernel 里用 `threadgroup float inpTile[MATMUL_TILE][MATMUL_TILE]` 显式声明 shared memory tile，让一个 thread block 里的所有线程协作把一块 input 和 weight 加载到 shared memory，然后再做内积——这是经典的 cuBLAS-style tiled GEMM 算法在 Metal 上的 minimal viable port。

最终性能：**1.1 TFLOP/s**，相对最初 Basic Swift 的 2.8 Gflop/s 提升了 **382 倍**。

但 Matt 自己也承认："Theoretically, the GPU on my M3 Max is capable of around 15 TFLOP/s. But the real ceiling for this kind of task is going to be 3-5 TFLOP/s。" 1.1 TFLOP/s 大约只到理论上限的 25-35%——和真正的 production-grade kernel（比如 Apple Accelerate 或者 Metal Performance Shaders）相比还有 2-3 倍差距。这个差距主要来自：

- 没有用 `simdgroup_matrix` 这种 hardware matrix accelerator
- Tile size 没有针对 M3 Max 的 cache line 和 thread block size 做精细调优
- 没有 double-buffering（一边算一边预取下一个 tile）

但即便这样不到 30% 效率的实现，已经比 `llm.c` 的单线程 CPU 实现快了 30 倍——这就是 GPU vs CPU 的天然带宽差距。

### 2.8 结论：哪一步是"性价比最高"的优化？

Matt 在文章末尾做了一个简洁的总结。如果把 382 倍提升拆解成"第一个 72 倍（CPU 内）"和"剩下的 5.3 倍（AMX + GPU）"，那么真正普世适用的优化只有四条：

1. 避免 Array CoW / 引用计数开销（用 MutableSpan / Span）
2. 用 `Relaxed.multiplyAdd` 启用 SIMD FMA
3. 重构循环让 SIMD pipeline 喂满（InlineArray + LOOP_UNROLL）
4. 用 `DispatchQueue.concurrentPerform` 并行化

这四条加起来就有 72 倍提升——对 99% 的 Swift 数值计算代码已经够用了。AMX 和 Metal 是给那 1% 真的需要"训练而不是推理"、"产品而不是 demo" 的场景准备的，且要付出极高的工程复杂度代价。

这条"投资回报曲线"和我们 [《Cloudflare 一次 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/) 里讨论的网络协议优化、以及 [《把 3 GB SQLite 压成 10 MB》](/post/good-read-fst-300x-compression-finnish-dictionary/) 里芬兰语词典的 FST 压缩，是同一种工程哲学的不同分支——**先用 80% 的力气拿走 80% 的收益，再决定要不要为最后 20% 付十倍代价**。

---

## 三、延伸阅读图谱

### 3.1 作者其他代表作

Matt Gallagher 是 Cocoa 圈最资深的独立博主之一，从 2008 年开始写性能与架构话题，共发布约 220 篇文章。我从 [Cocoa with Love 归档](https://www.cocoawithlove.com/archive/) 里挑了 5 篇代表作，按主题相关度排序：

1. **[Performance comparisons of common operations, 2014 edition](https://www.cocoawithlove.com/blog/2016/04/02/swift-performance.html)**——Swift 1.x 时代的性能 benchmark 巨作。这篇展示了 Matt 一以贯之的方法论：把每种数据结构操作都跑 10⁷ 次，然后画成柱状图。十年来这套方法没变过，变的只是被测的语言版本。
2. **[Implementing a SwiftUI-style framework on UIKit](https://www.cocoawithlove.com/blog/diy-swiftui.html)**——从零实现一个 SwiftUI 风格的声明式 UI 框架。Matt 一惯的风格：不依赖任何官方库，从最底层往上重写一遍，最后告诉读者"这就是 Apple 内部大概是怎么做的"。
3. **[Comparing different approaches to dependency injection](https://www.cocoawithlove.com/blog/specific-types.html)**——对各种依赖注入风格做实测对比，给出实际编译时长、运行时性能、可读性评分。
4. **[A Markdown-style streaming parser in pure Swift](https://www.cocoawithlove.com/blog/markdown-streaming-parser.html)**——纯 Swift 实现的流式 Markdown 解析器。代码量小但展示了 Matt 对 Swift 字符串处理性能的深刻理解。
5. **[Memory and thread-safe custom property accessors](https://www.cocoawithlove.com/blog/thread-safe-custom-properties.html)**——iOS 多线程下的属性访问安全。这篇早于 Swift 6 出现，但很多观点（关于内存屏障、原子性、Swift 类型系统的边界）至今仍然适用。

### 3.2 相关论文与博文

- **[Andrej Karpathy: llm.c GitHub repo](https://github.com/karpathy/llm.c)**——本文的对标实现。1000 行 C 代码训练 GPT-2，是 2024 年至今"从零理解 LLM 实现"最重要的教学资源之一。
- **[Peter Cawley: AMX documentation](https://github.com/corsix/amx)**——AMX 反向工程社区圣经。包含完整 opcode 表、寄存器布局、内存模型示意图。Matt 这篇文章里的 AMX 代码就是基于这套文档写出来的。
- **[Dougall Johnson: Apple AMX](https://gist.github.com/dougallj/7a75a3be1ec69ca550e7c36dc75e0d6f)**——Dougall 是 M1 反向工程社区的关键人物，他的 AMX gist 是 Peter Cawley 文档的前身。
- **[Apple Numerics Swift Package](https://github.com/apple/swift-numerics)**——`Relaxed.multiplyAdd` 的官方实现仓库。文章里那个让 Swift 用上 `fmla.4s` 的关键 API 就来自这里。
- **[Anandtech: Apple's New M1 Pro and M1 Max Chips](https://www.anandtech.com/show/17024/apple-m1-max-performance-review)**——M1 Max 首发评测里第一次公开提到 AMX 矩阵乘性能数据。
- **[NVIDIA: cuBLAS Tiled GEMM whitepaper](https://docs.nvidia.com/cuda/cublas/index.html)**——经典 GPU GEMM 算法的工业级参考实现。Matt 的 Tiled Metal kernel 就是这个算法的 minimal port。
- **[Tile-based matrix multiplication on GPU (Stanford CME 213)](https://stanford-cme213.github.io/Lecture%20Slides/Lecture_11.pdf)**——斯坦福并行计算课程里讲 GPU GEMM 的经典 PPT。要理解 Matt 那个 `threadgroup` tile kernel，这是最好的入门资料。
- **[Maxime Kreps: Why is matrix multiplication so hard?](https://siboehm.com/articles/22/CUDA-MMM)**——一篇在 GPU 圈被高度引用的 GEMM 优化教程，从 naive kernel 一路打到接近 cuBLAS 的实现。
- **[Apple Accelerate framework: vDSP and BLAS APIs](https://developer.apple.com/documentation/accelerate)**——Apple 官方的"AMX 包装层"。Matt 反复推荐生产代码用这个而不是直接调 AMX。
- **[Brian Robbins: Demystifying Apple's M1 GPU](https://twitter.com/never_released)**——M1 GPU 反向工程社区里另一位关键作者，他的工作和 Dougall 互为补充。

### 3.3 反方观点

- **[Why I don't write performance-optimized code for Swift](https://forums.swift.org/t/why-i-dont-write-performance-optimized-code-for-swift/30000)**——Swift 论坛上一篇典型的"反优化派"观点。论点是：Apple 已经给你 Accelerate、BNNS、MLX，自己手写汇编属于"重复造轮子的浪漫主义"。Matt 这篇文章正是对这种观点的最优反驳——你必须先理解 Accelerate 里在做什么，才能真正"决定"是否要用它。
- **[Andrej Karpathy: My experience with llm.c](https://x.com/karpathy/status/1801871148373786717)**——Karpathy 本人对自己写 llm.c 的反思。他承认 1000 行 C 代码绝不是 production-grade，但它"让神经网络变成可读的、可被一个人完全理解的东西"。
- **[mlx-team: MLX framework launch](https://github.com/ml-explore/mlx)**——Apple ML Research 团队发布的 MLX 框架，目标是"PyTorch 的 Apple Silicon 优化替代品"。文章里 Matt 完全没提 MLX——是因为 MLX 用 Python，违反了他的"Swift framework-free" 自我约束。但 MLX 才是 2026 年 Mac 本地训练的事实标准。

---

## 四、编辑延伸思考

### 4.1 "性能优化文章"作为一种文体

互联网上大概有三种"性能优化文章"。

**第一种是"我做了 X，快了 N 倍"——本质是营销。**它通常出现在公司技术博客里，配一张折线图，写两段"我们的工程团队做了非常艰苦的努力"，然后给出最终数字。读者无法重现，也无法验证哪一步是关键。

**第二种是"性能优化的 N 个 tips"——本质是 SEO。**作者把所有听过的优化技巧（cache locality、loop unrolling、SIMD、prefetching）罗列一遍，每个给一段代码示例。这种文章看似全面，但实际上从来没有量化过任何一条 tip 在真实场景下的回报。

**第三种就是 Matt 这种——量化、可复现、按时间线展开的工程笔记。**它的特征是：每一次改动都对应一次实验，每次实验都给出汇编层证据，每次失败的尝试（比如 `TaskGroup` 输给 `concurrentPerform`）都被诚实记录。

这种文章在 2026 年的内容生态里越来越罕见，因为它**对作者的时间成本和技术深度都要求极高**。Matt 在文末提到他在 2024 年就写过一版 Swift llm.c，但直到 2026 年 Swift 6.2 引入 `MutableSpan` 和 `InlineArray` 之后才有底气把这篇博客写完——这意味着这篇文章背后是两年的工程积累。

我们推荐它，部分原因就是希望读者重新认识"什么是真正有信息密度的技术内容"。

### 4.2 Apple Silicon 的"开放与封闭"双重叙事

这篇文章在不经意间触及了一个 Apple 生态的深层张力：Apple Silicon 在性能上是开放的（Metal、Accelerate、Core ML 都是公开 API），但在 microarchitecture 层面是封闭的（AMX、NPU 内部、PMU 事件都被刻意隐藏）。

这种封闭的代价正在显现：

- **学术界很难做 Apple Silicon 的 systems research**——因为你拿不到 PMU 计数器数据，没法做精确的 cache miss 分析。
- **AI 框架很难做 Apple Silicon 的 op fusion**——因为没有 AMX 的官方 ISA，PyTorch 和 JAX 必须通过 Accelerate 这一层 framework call 来做 GEMM，而 framework call 本身就是 50-100ns 的 overhead。
- **独立开发者很难做差异化优化**——你只能用 Accelerate / MPS，而所有人都用同一套 API 意味着没人能真的跑得比别人更快。

英伟达 CUDA 走的是完全相反的路线：ISA 完全公开（PTX、SASS）、PMU 完全开放（nvprof、Nsight Compute）、底层 API 完全可用（CUDA Driver API）。这条路的代价是生态碎片化、breaking change 频繁、开发者学习曲线陡峭。但它的收益是 **任何 CUDA 开发者都可以写出比 cuBLAS 快的 kernel**——这就是 FlashAttention、xFormers、Triton 等一系列革命性开源库存在的基础。

Matt 这篇文章其实在隐含地问一个问题：**如果 Apple 想让 Apple Silicon 真正成为 AI 训练平台，它需要在 ISA 公开度上做出多大让步？**

[我们之前讨论过 Apple M5 MIE 内核防线](/post/good-read-calif-mie-bypass-apple-m5-kernel/)——Apple 投入了大量硬件资源做内存完整性保护，把 microarchitecture 锁得越来越紧。这种"封闭"是有代价的：你不可能既要 microarchitecture 私有、又要开发者能写出极致的 AI 内核。Mac 本地训练浪潮正在迫使 Apple 在这个权衡上重新表态——MLX 的开源、Metal Performance Shaders 不断加新算子、Accelerate 的更新频率提升，都是这种压力的反映。

### 4.3 "382 倍"在 LLM 时代意味着什么

我们倾向于以为 LLM 性能优化的工作都在数据中心里——10000 张 H100 GPU、KV cache 优化、speculative decoding、tensor parallelism。但 Matt 这篇文章给了一个非常本地化、非常单机的视角：

- 起点：Basic Swift 2.8 Gflop/s 对应**每 19 秒生成 1 个 token**——根本不可用。
- 终点：Tiled Metal 1.1 Tflop/s 对应**每秒生成 11 个 tokens**——勉强可用。
- llm.c 单线程：35 Gflop/s 对应**每 1 秒生成 1 个 token**——能 demo 但谈不上 UX。

而 antirez 在 [《一周写出 DS4》](/post/good-read-antirez-ds4-local-inference/) 中描述的 DeepSeek v4 Flash 在 128GB MacBook 上的推理速度大约是 **15-25 tokens/s**——这个数字背后正是 Accelerate / MLX / Metal 这些 framework 在做和 Matt 完全一样（但更精细）的优化。

换句话说，**本地 AI 浪潮的算力地基，就是无数个 Matt Gallagher 这样的优化故事堆出来的。**每一次 `Relaxed.multiplyAdd` 让 Swift 启用 FMA、每一次 `threadgroup` tile 让 GPU 充分利用 shared memory、每一次 AMX 反向工程让 16×16 outer product 一周期完成——这些看似 micro 的优化，乘以日均 10 亿次本地推理请求，就是整个 Mac 生态能不能从 GPT API 调用迁移到本地模型的真实算力天花板。

这也是为什么我们看 Matt 这篇文章的角度，不只是"Swift 性能调优指南"，而是"Apple Silicon AI 平台的能力上限实测"。

### 4.4 给读者的三条具体建议

如果你是 iOS/macOS 开发者：

1. **优先看 Section 2.2-2.4**（MutableSpan、Relaxed.multiplyAdd、InlineArray）——这三条改动对任何 Swift 数值密集型代码都立竿见影，且语义安全、可读性损失最小。
2. **谨慎对待 Section 2.5**（DispatchQueue.concurrentPerform）——它的性能确实好，但 Swift 6 严格并发模型下的代码丑陋度是真实代价。如果你的代码库要长期维护，先考虑 Swift Concurrency + TaskGroup，性能输 5%-10% 但可维护性高出一个量级。
3. **彻底跳过 Section 2.6**（AMX）——除非你在做 demo 或者研究项目，否则去用 Accelerate / MPSGraph。这点 Matt 本人在原文里强调过两次。

如果你是机器学习/AI infra 工程师：

1. 这篇文章是理解 **"为什么 Apple Silicon 不能直接 port CUDA kernel"** 的最好教材——你能看到 Metal/AMX 和 CUDA 在编程模型上的根本差异。
2. 文章末尾提到 Matt 的下一篇会讲 BLAS/BNNS/CoreML/MPSGraph——值得加 RSS 跟进。

---

## 五、配套资料导览

本文同目录下提供以下扩展资料：

- **`mindmap.svg`**：文章核心结构思维导图，按"问题—改动—量化"三维展开，深色背景适合 Twitter/X 二次传播。
- **`concept-cards.md`**：12 张关键概念卡片，涵盖 FMA、AMX、Metal threadgroup、MutableSpan、DispatchQueue.concurrentPerform 等。
- **`glossary.md`**：38 条英中对照术语表，从 `fmla.4s` 到 `threadgroup_barrier(mem_flags::mem_threadgroup)`，便于读者查阅原文中的硬件/汇编/Metal 术语。
- **`cover.svg`**：封面图（深色 + 关键性能数字 + "好文共赏"标识）。

---

## 六、谁应该读这篇文章

✅ **强烈推荐**：

- **Swift 系统级开发者**——尤其是写过性能敏感代码（图像处理、音频、视频转码、加密）但没接触过 Swift 6.2 新原语的人。
- **Apple Silicon 平台工程师**——你需要的 AMX、Accelerate、MPS 全栈视角全部在这里。
- **本地 AI 推理引擎作者**——llama.cpp / MLX / mistral.rs 的 Apple Silicon 后端贡献者。
- **从 CUDA 转 Metal 的程序员**——文章里 Metal kernel 的 evolution（basic → threaded → tiled）是最直接的对照教材。

🟡 **值得一读**：

- **PyTorch / JAX 用户**——你不会直接用到这些优化，但理解 Apple ML 框架背后在做什么，对调试 macOS 上奇怪的性能问题有帮助。
- **编译器优化爱好者**——Matt 贴出来的汇编对比是观察 Swift LLVM backend 行为的好窗口。

❌ **不太推荐**：

- **只关心"做产品、不关心 microsecond"的应用层开发者**——这篇文章对你来说优化粒度太细，回报率不够。直接用 Apple 的 Foundation Models API 或者 MLX 即可。
- **找 LLM 训练入门教程的人**——这篇假设你已经懂 GPT-2 架构，且对 forward/backward pass 有直觉。请先看 Karpathy 的 YouTube 系列。

---

> 📚 **延伸阅读（本站相关）**
>
> - [【好文共赏】antirez 一周写出 DS4](/post/good-read-antirez-ds4-local-inference/) — 同一台 Mac 上的本地推理视角
> - [【好文共赏】五天，攻破 Apple 五年：Calif 团队用 Mythos 把 M5 上的 MIE 防线撕开了一道口子](/post/good-read-calif-mie-bypass-apple-m5-kernel/) — Apple Silicon 内部架构封闭性的另一面
> - [【好文共赏】把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上](/post/good-read-haskell-mercury-production-engineering/) — 类型安全 vs 性能优化的另一种语言权衡
> - [【好文共赏】把 3 GB SQLite 压成 10 MB](/post/good-read-fst-300x-compression-finnish-dictionary/) — 同样的"投资回报曲线"工程哲学
> - [【好文共赏】Cloudflare 一次 14ms 的 CUBIC 死亡螺旋](/post/good-read-cloudflare-quic-cubic-death-spiral/) — 网络协议层的 80/20 优化案例
> - [Apple Ternus 时代的硬件与 AI 未来](/post/apple-ternus-hardware-ai-future-2026/) — Apple Silicon 战略层视角
> - [Cerebras IPO 与推理经济学](/post/cerebras-ipo-inference-economics-wafer-scale-2026/) — 数据中心算力 vs 本地算力的另一极
> - [Edge AI Silicon 与模型差距](/post/edge-ai-silicon-model-gap/) — 端侧算力的整体景观
