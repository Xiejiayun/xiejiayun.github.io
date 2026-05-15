# 术语表：Swift 矩阵乘法与 Apple Silicon 性能优化

> 配套 [《把 Swift 推到 1.1 Tflop/s》](./index.md) 中出现的关键术语。
> 按"硬件 / 编译器 / 语言 / 框架 / ML"分组，便于读者按需查找。

## 一、硬件与微架构

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| Apple Silicon | 苹果自研芯片 | 基于 ARM64 的 SoC 系列，覆盖 M1/M2/M3/M4/M5 |
| M3 Max | 文章测试硬件 | 16 CPU 核 / 40 GPU 核 / 128GB 统一内存上限 |
| AMX (Apple Matrix Coprocessor) | 苹果矩阵协处理器 | 未公开命名的矩阵单元，专做 16×16 outer product |
| NPU / Neural Engine | 神经引擎 | Apple 专用 NN 推理加速器，私有 ISA |
| SIMD (Single Instruction, Multiple Data) | 单指令多数据 | 一条指令并行处理多个数据元素 |
| NEON | ARM SIMD 指令集 | ARM64 上的 128-bit SIMD 扩展，含 `fmla.4s` 等 |
| FMA (Fused Multiply-Add) | 融合乘加 | 一周期完成 `a + b × c`，仅一次舍入 |
| `fmla.4s` | NEON SIMD FMA 指令 | 对 4 个 32-bit float 并行做 FMA |
| `fmadd` | ARM64 标量 FMA 指令 | 对单个 float 做 FMA（C `-ffast-math` 默认启用） |
| `AMX_MATFP` | AMX 浮点矩阵指令 | 一周期 16×16 outer product, ~256 FMA |
| `AMX_LDX / LDY / LDZ / STZ` | AMX 加载/存储指令 | 在 X/Y/Z 寄存器组之间搬运数据 |
| Outer Product | 外积 | 两个向量的笛卡尔积矩阵 |
| Cache Line | 缓存行 | M3 Max 上 128 字节，影响 SIMD 加载效率 |

## 二、编译器与汇编

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| `-O3` | 最高优化等级 | Clang/LLVM 编译器的激进优化级别 |
| `-ffast-math` | 浮点快速模式 | 允许 FMA、忽略 NaN 处理、关闭严格 IEEE 754 |
| `-remove-runtime-asserts` | 移除运行时断言 | Swift 编译选项，关闭数组越界检查 |
| Loop Unrolling | 循环展开 | 把循环体复制 N 份以隐藏分支开销并启用 SIMD |
| Inlining | 函数内联 | 把函数体直接嵌入调用点，消除调用开销 |
| `inline(none)` | 禁用内联 | Swift attribute, 测试时用于隔离影响 |
| Pipeline (Instruction Pipeline) | 指令流水线 | CPU 同时处理多条指令的不同阶段 |
| Branch Prediction | 分支预测 | CPU 预测条件跳转方向以保持流水线满载 |
| Register Allocation | 寄存器分配 | 编译器决定哪些变量住寄存器 vs 栈 |

## 三、Swift 语言与运行时

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| CoW (Copy-on-Write) | 写时复制 | Swift Array/String 的引用计数复制机制 |
| `_ArrayBuffer.beginCOWMutation()` | CoW 触发函数 | Swift Array 写入前的唯一性检查 |
| ARC (Automatic Reference Counting) | 自动引用计数 | Swift/Obj-C 的内存管理机制 |
| `Sendable` | 可跨并发边界传递 | Swift 6 严格并发安全标记 |
| `@unchecked Sendable` | 手动断言可跨并发 | 程序员自负其责的 Sendable 后门 |
| `@escaping` | 逃逸闭包 | 闭包生命周期可能超过函数调用 |
| `Span<T>` | 不可变内存视图 | Swift 6.2 引入的安全切片类型 |
| `MutableSpan<T>` | 可变内存视图 | Span 的可写版本，零拷贝零引用计数 |
| `InlineArray<N, T>` | 定长栈分配数组 | Swift 6.2 引入，对标 C `T arr[N]` |
| `withUnsafeMutableBufferPointer` | 不安全可变缓冲指针 | 临时获取 Array 底层 raw pointer |
| `Relaxed.multiplyAdd` | 放松约束 FMA | Swift Numerics 的 fast-math API |
| `Relaxed.sum` | 放松约束求和 | 允许编译器重排浮点加法 |
| `TaskGroup` | Swift Concurrency 任务组 | Swift 6 并发原语，类似 OpenMP parallel for |
| `DispatchQueue.concurrentPerform` | GCD 并发执行 | 静态工作分区的老式并发 API |

## 四、Metal 与 GPU 编程

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| Metal | 苹果 GPU 框架 | macOS/iOS 上的低开销 GPU 编程接口 |
| MTLBuffer | Metal 缓冲区 | GPU 可访问的内存对象 |
| MTLCommandBuffer | Metal 命令缓冲 | 待执行的 GPU 命令容器 |
| MTLComputePipelineState | 计算管线状态 | 编译后的 GPU compute shader |
| Compute Kernel | 计算核函数 | 在 GPU 上执行的并行函数 |
| `[[buffer(N)]]` | 缓冲绑定 attribute | Metal Shading Language 参数注解 |
| `thread_position_in_grid` | 线程网格位置 | 每个 thread 的全局 ID |
| `thread_position_in_threadgroup` | 线程在组内位置 | 每个 thread 在 threadgroup 内的局部 ID |
| Threadgroup | 线程组 | Metal 的 thread block 单位 |
| `threadgroup_barrier` | 线程组屏障 | 块内同步原语 |
| `mem_flags::mem_threadgroup` | 共享内存屏障标志 | 屏障只同步 threadgroup memory |
| Tile / Tiling | 分块 / 分块化 | 把大矩阵切成小块以利用 cache/shared memory |
| SIMD Group | SIMD 组 | Metal 的 warp 等价概念（32 thread 同步执行） |
| `simdgroup_matrix` | SIMD 组矩阵 | Apple GPU 的硬件矩阵指令（文章未用） |

## 五、ML / LLM 训练

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| GPT-2 | OpenAI 2019 年发布的语言模型 | llm.c 实现的 124M 参数版本 |
| Forward Pass | 前向传播 | 输入经模型权重得到输出（即推理） |
| Backward Pass | 反向传播 | 计算梯度 |
| Weight Update | 权重更新 | 用梯度更新模型参数（Adam/SGD） |
| Training Iteration | 训练迭代 | 一次完整的前向+反向+更新 |
| matmul | 矩阵乘法 | 神经网络中占算力 80%+ 的核心算子 |
| GEMM (General Matrix Multiply) | 通用矩阵乘法 | BLAS 标准接口名，对应 `C = αAB + βC` |
| BLAS (Basic Linear Algebra Subprograms) | 基础线性代数子程序 | 标准矩阵运算 API |
| TFLOP/s (Tera Floating-point Ops/sec) | 万亿浮点运算每秒 | 算力单位 |
| Token | 词元 | LLM 的最小输入/输出单位 |
| Tokens/s | 每秒生成词元数 | LLM 推理速度指标 |
| Tiny Shakespeare | 小型莎士比亚语料 | 文章用的训练数据集 |

## 六、Apple 平台框架

| 英文 | 中文 | 简要说明 |
| --- | --- | --- |
| Accelerate | Apple 加速框架 | 包含 BLAS/LAPACK/vDSP，间接访问 AMX |
| BNNS (Basic Neural Network Subroutines) | 基础神经网络子程序 | Accelerate 中的 NN 算子库 |
| Core ML | Apple ML 推理框架 | 高层 API，支持模型部署 |
| MPS (Metal Performance Shaders) | Metal 性能着色器 | Metal 上的优化矩阵/卷积算子库 |
| MPSGraph | Metal 图算框架 | MPS 的图模式计算 API |
| MLX | Apple 开源 ML 框架 | 2023 年发布，Python/Swift 双绑定，专为 Apple Silicon |
| Foundation Models | 系统内置基础模型 | iOS/macOS 26 中提供的设备端 LLM API |
| LanguageModelSession | Foundation Models 会话 | 调用系统 LLM 的高层 API |
| `git-xet` | Git LFS 扩展工具 | llm.c 训练集分发用到的二进制大文件管理 |
