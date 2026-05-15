# 概念卡片：Swift LLM 矩阵乘法优化十二要点

> 配套 [《把 Swift 推到 1.1 Tflop/s》](./index.md)
> 每张卡片独立成段，可作为推文、技术分享 slides 的素材。

---

## 🃏 Card 01 · 浮点运算估算公式

> `FLOPs_per_iter ≈ 6 × N × D`

- **N**：模型参数量（GPT-2 124M ≈ 1.24×10⁸）
- **D**：batch × seq_len = B × T（文章里 4 × 64 = 256）
- **系数 6** 包含：前向 (2) + 反向计算梯度 (2) + 权重更新 (2)
- 一次训练迭代 ≈ 1.91 × 10¹¹ FLOPs（0.2 TFLOP）
- 这条公式来自 Karpathy llm.c README，是估算"训练成本"最简练的工具

---

## 🃏 Card 02 · `_ArrayBuffer.beginCOWMutation()`

Swift `Array` 的 copy-on-write 检查函数。每次 `array[i] = x` 都会调用一次，验证当前 buffer 是否唯一引用。

- 在浮点密集内层循环里被放大成 dominant cost
- 单线程 matmul 中占总耗时 60-70%（Instruments 数据）
- 解药：`MutableSpan`（Swift 6.2+）或 `withUnsafeMutableBufferPointer`
- 这是一个**编译器本应内联但没做到**的优化盲点

---

## 🃏 Card 03 · `MutableSpan` vs `Array`

```swift
var out = out.mutableSpan  // 关键一行
```

`MutableSpan<T>` 是 Swift 6.2 引入的非拥有可变内存视图：

- 零引用计数 / 零 CoW 检查
- 编译期保证内存有效性（lifetime 推断）
- 性能等同 C 裸指针，安全性高于 `UnsafeMutableBufferPointer`
- 不能跨 `@escaping` closure 传递（这是它与 GCD 的张力）

---

## 🃏 Card 04 · `Relaxed.multiplyAdd` 与 FMA

```swift
val = Relaxed.multiplyAdd(a, b, val)  // val += a * b 的 SIMD 版
```

Swift Numerics 库中的 "fast-math" 替代品：

- 启用 `fmla.4s`（NEON 4-wide fused multiply-add）
- 在严格 IEEE 754 下，FMA 与"先乘后加"的舍入位可能不同
- `Relaxed` 命名暗示"放松舍入约束"而非"放弃精度"
- **注意例外**：`gelu_backward` 等数值敏感场景**不要**用 Relaxed

---

## 🃏 Card 05 · `fmla.4s` 汇编指令

ARM64 NEON SIMD 的核心 FMA 指令：

```asm
fmla.4s v1, v16, v4     ; v1 += v16 * v4，4 个 float 并行
```

- `4s` = 4 个 single-precision float (32-bit)
- 一周期完成 4 次乘加 = 8 FLOPs
- Apple M3 Max 上每个 P-core 每周期可发射 4 条 `fmla.4s` = 32 FLOPs/cycle
- 相比标量 `fmadd s0, s1, s2, s0` 提速 4 倍

---

## 🃏 Card 06 · `InlineArray<N, T>`

Swift 6.2 新增的栈分配定长数组：

```swift
var result = InlineArray<8, Float>(repeating: 0)
```

- 值类型 · 大小编译期确定 · 完全栈分配
- 行为对标 C 的 `float result[8]`
- 解决了 Swift 长期以来"无法在 hot loop 里高性能做小数组"的痛点
- 配合 LOOP_UNROLL 模式，让 SIMD pipeline 真正喂饱

---

## 🃏 Card 07 · `DispatchQueue.concurrentPerform`

```swift
DispatchQueue.concurrentPerform(iterations: N) { i in
    // 不是 @escaping，可以传 Span
}
```

- GCD 老接口（macOS 10.6, 2009 年）
- 静态工作分区 + 工作窃取调度
- closure **不是 `@escaping`**——这是它能传 `Span<Float>` 而不触发引用计数的关键
- Matt 实测比 `TaskGroup` 在矩阵乘场景下相同或略快
- 代价：需要 `@unchecked Sendable` 包装可变 buffer

---

## 🃏 Card 08 · AMX — Apple Matrix Coprocessor

Apple Silicon 内部的隐藏矩阵协处理器：

- Apple 官方从未命名，仅称作 "machine learning accelerators"
- 16 个 X 寄存器 / 16 个 Y 寄存器 / 64 个 Z 寄存器（每个 64 字节）
- 核心指令 `AMX_MATFP` 一周期完成 16×16 outer product（256 FMAs）
- M3 Max 上 AMX 理论吞吐 ~1 TFLOP/s（单线程）
- **不要在生产代码里直接调用**——Apple 可以在下一代芯片里改 opcode

---

## 🃏 Card 09 · Metal `threadgroup` 共享内存

```metal
threadgroup float inpTile[TILE][TILE];   // 块内共享
threadgroup_barrier(mem_flags::mem_threadgroup);
```

GPU 编程的 tile 化基石：

- 一个 threadgroup 内所有线程共享这段 fast memory
- 比 global memory 快 ~10 倍
- `threadgroup_barrier` 是块内同步原语
- 经典 GEMM 模式：合作加载 tile → 块内屏障 → 内积 → 屏障 → 下一 tile

---

## 🃏 Card 10 · GPU 实际效率天花板

理论 vs 实测：

| 指标 | M3 Max GPU |
| --- | --- |
| 理论峰值 | ~15 TFLOP/s (FP32) |
| 矩阵乘真实上限 | 3-5 TFLOP/s |
| Matt 的 Tiled Metal | 1.1 TFLOP/s |
| Apple 官方 MPS | 估计 2.5-4 TFLOP/s |

原因：内存带宽、kernel launch latency、tile 边界 padding、共享内存 bank conflict 等系统性损耗。

---

## 🃏 Card 11 · "投资回报曲线"工程哲学

Matt 文章里隐含的优化哲学：

| 优化阶段 | 投入难度 | 性能回报 | 适用场景 |
| --- | --- | --- | --- |
| MutableSpan + Relaxed | 极低（< 10 行） | 30× | 所有 Swift 数值代码 |
| InlineArray + Unroll | 中等 | 1.3× 额外 | 性能敏感库 |
| concurrentPerform | 中高（破坏可读性） | 5× | 后台批处理 |
| AMX | 极高（反向工程） | 1.7× | 研究/demo |
| Tiled Metal | 极高（GPU 内核） | 3× | 生产 ML |

**前 30× 用 < 10 行代码拿到，剩下 13× 需要 1000+ 行**。

---

## 🃏 Card 12 · Apple Silicon 的"双轨架构"

Apple 平台的执行单元访问模式：

| 层级 | 公开 API | 私有/未文档化 |
| --- | --- | --- |
| CPU 通用 | Swift / Obj-C / C / C++ | — |
| SIMD | NEON intrinsics | — |
| 矩阵协处理器 | Accelerate.BLAS | AMX ISA |
| 神经引擎 | Core ML / BNNS | NPU ISA |
| GPU | Metal | GPU 私有指令 |

战略含义：
- 普通开发者通过框架访问 = 稳定但有 framework call overhead
- Apple 自有团队（MPS / Accelerate / Core ML）可直接访问 = 5-20% 性能优势
- 这种"快慢双轨"是 Apple 生态封闭性的工程实现
