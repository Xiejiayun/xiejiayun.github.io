---
title: "AMMA 架构：用存算一体 HBM 替代 GPU 计算 Die，百万上下文 Attention 的内存墙解法"
description: "UCSD、Columbia 和延世大学提出 AMMA 多芯粒存算一体架构，在长上下文 LLM 推理中用 PNM-HBM 替代传统 GPU 计算 Die。当内存带宽成为瓶颈，计算应该搬到数据旁边。"
date: 2026-05-06
slug: "pnm-hbm-replace-gpu-compute-die-attention-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 存算一体
    - HBM
    - LLM推理
    - 芯片架构
draft: false
---

> 当上下文长度从 8K 增长到 1M，Attention 的计算量增长了 15000 倍。但真正的瓶颈不是算力——是数据搬运。

---

## 一、长上下文推理的真正瓶颈不是 FLOPS

2026 年的 LLM 推理正在经历一场静默的危机。

随着 Claude、Gemini、GPT 系列模型的上下文窗口从 8K 扩展到 128K、乃至 1M token，Attention 机制的计算需求呈二次增长。直觉上，这似乎是一个"需要更多 GPU"的问题。

但实际情况更加微妙。在长上下文的 **Decode 阶段**（逐 token 生成），瓶颈不是 GPU 的计算能力（FLOPS），而是 **KV Cache 的内存带宽**。

### 为什么 Decode 阶段是内存瓶颈？

在 Decode 阶段，每生成一个新 token，模型需要：
1. 读取整个 KV Cache（所有之前 token 的 Key 和 Value 向量）
2. 计算新 token 的 Query 与所有 Key 的 Attention
3. 用 Attention 权重对 Value 加权求和

对于 1M 上下文的模型（假设 128 层，每层 KV 头 128 个，维度 128，FP16）：

**KV Cache 大小** ≈ 1M × 128 × 128 × 128 × 2 × 2B ≈ **8TB**

这远超任何单 GPU 的 HBM 容量（H100 为 80GB，B200 为 192GB）。即使使用 8 卡并行，KV Cache 仍然需要 offload 到 CPU DRAM 或 SSD，导致巨大的数据搬运开销。

### 数据搬运 vs 计算的失衡

| 操作 | 计算量 (FLOPS) | 数据移动量 | 瓶颈 |
|------|---------------|-----------|------|
| Prefill（1M tokens） | ~10^15 | KV Cache 写入 | 计算瓶颈 |
| Decode（每 token） | ~10^9 | 读取全部 KV Cache | **内存带宽瓶颈** |

Decode 阶段的算术强度（FLOPS/Byte）极低，大约只有 1-2，而 H100 的峰值算术强度支持 > 100。这意味着在 Decode 阶段，GPU 的 99% 计算能力是闲置的——它在等数据。

## 二、AMMA 架构：把计算搬到数据旁边

UCSD、Columbia 和延世大学的研究团队提出了 **AMMA（A Multi-chiplet Memory-centric Architecture）**，用一种激进但逻辑自洽的方式解决这个问题：**不把数据搬到 GPU，而是把计算搬到内存旁边**。

### 架构概览

```
    ┌──────────────────────────────────────────┐
    │              AMMA 架构                    │
    │                                          │
    │  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
    │  │ PNM-HBM │  │ PNM-HBM │  │ PNM-HBM │  │
    │  │ Cube 1  │  │ Cube 2  │  │ Cube N  │  │
    │  │┌───────┐│  │┌───────┐│  │┌───────┐│  │
    │  ││ PNM   ││  ││ PNM   ││  ││ PNM   ││  │
    │  ││ Logic ││  ││ Logic ││  ││ Logic ││  │
    │  │└───────┘│  │└───────┘│  │└───────┘│  │
    │  │┌───────┐│  │┌───────┐│  │┌───────┐│  │
    │  ││ DRAM  ││  ││ DRAM  ││  ││ DRAM  ││  │
    │  ││ Stack ││  ││ Stack ││  ││ Stack ││  │
    │  │└───────┘│  │└───────┘│  │└───────┘│  │
    │  └────┬────┘  └────┬────┘  └────┬────┘  │
    │       └────────────┼────────────┘        │
    │                    │                      │
    │            ┌───────┴───────┐              │
    │            │  Coordinator  │              │
    │            │  (轻量控制器)  │              │
    │            └───────────────┘              │
    └──────────────────────────────────────────┘
```

### 关键设计决策

**1. PNM-HBM（Processing-Near-Memory HBM）**

在传统 HBM 的 base die 上集成轻量计算逻辑（PNM Logic），直接在内存旁边执行 Attention 计算。数据不需要通过 HBM 接口传输到 GPU die，而是在 HBM 内部就地处理。

内部带宽优势巨大：
- HBM 对外接口带宽：~1 TB/s（HBM3e）
- HBM 内部 bank 级带宽：~8-16 TB/s
- AMMA 利用的正是这 8-16× 的内部带宽优势

**2. 去掉传统 GPU 计算 Die**

这是 AMMA 最激进的设计决策。传统 GPU 架构是"一个大计算 die + 多个 HBM stack"的异构布局。AMMA 取消了中央计算 die，用多个 PNM-HBM cube 组成的分布式计算替代。

这听起来疯狂，但对于 Decode 阶段的 Attention 计算来说是合理的——因为 Decode Attention 的计算模式极其规则（矩阵向量乘法），不需要 GPU 那种复杂的通用计算能力。

**3. Multi-Chiplet 互联**

多个 PNM-HBM cube 之间通过高带宽互联（类似 chiplet 间的 die-to-die 连接）共享中间结果。KV Cache 被分片存储在不同的 cube 中，每个 cube 独立计算自己分片的 Attention，最后通过互联网络汇聚结果。

### 性能对比（论文数据）

| 指标 | H100 (8-GPU) | AMMA |
|------|-------------|------|
| 1M 上下文 Decode 延迟 | ~500ms/token | ~50ms/token |
| 能效（TOPS/W） | 基准 | 5-8× 提升 |
| KV Cache 容量 | 受 HBM 限制 | 可扩展至 TB 级 |
| 面积效率 | 大量面积用于通用计算 | 面积主要用于存储+简单计算 |

## 三、与其他方案的对比

长上下文推理的内存瓶颈不是新问题，业界已有多种应对方案：

| 方案 | 思路 | 局限 |
|------|------|------|
| **KV Cache 压缩**（如 TurboQuant） | 减少 KV Cache 的存储量 | 压缩有上限，且会影响精度 |
| **SSD-backed KV Cache**（如 Tutti） | 把 KV Cache offload 到 SSD | SSD 带宽远低于 HBM |
| **稀疏 Attention** | 只计算部分 token 的 Attention | 可能丢失关键信息 |
| **多 GPU 并行** | 用更多 GPU 分摊 KV Cache | 成本线性增长，互联开销大 |
| **AMMA（PNM-HBM）** | 在内存旁边做计算 | 需要定制硬件，生态不成熟 |

AMMA 的独特之处在于它攻击的是问题的**物理根源**——数据和计算的物理距离。其他方案本质上都在"减少数据量"或"增加搬运通道"，而 AMMA 直接消除了搬运需求。

同期论文 Tutti（arXiv:2605.03375）提出了 SSD-backed KV Cache 的工程化方案，代表了另一个极端——用最便宜的存储介质来容纳 KV Cache，代价是更高的延迟。AMMA 和 Tutti 实际上代表了长上下文推理的两种哲学：**极致性能 vs 极致成本**。

## 四、产业化的挑战

AMMA 是一个学术提案，距离产业化还有相当距离。几个关键挑战：

### 1. PNM-HBM 的制造可行性

在 HBM 的 base die 上集成计算逻辑，需要 DRAM 厂商（三星、SK 海力士、美光）的深度配合。这些厂商目前的 HBM 产线已经满负荷运转，在生产 HBM4 的同时还要支持 PNM 变体，是一个巨大的产能和工程挑战。

### 2. 编程模型

AMMA 的编程模型与传统 GPU（CUDA）完全不同。整个 AI 推理的软件栈都围绕 GPU 构建——从 PyTorch 到 TensorRT 到 vLLM。为 AMMA 重写推理框架的工作量巨大。

### 3. 通用性问题

AMMA 针对 Decode Attention 做了极致优化，但 LLM 推理不只有 Attention——还有 FFN 层、归一化、embedding 查找等。一个实际的推理系统可能需要 AMMA（处理 Attention）+ 传统 GPU（处理其他层）的混合架构。

## 五、判断：存算一体是长上下文推理的终极方向

虽然 AMMA 本身可能不会被直接商业化，但它指向的方向——**存算一体（Processing-In/Near-Memory）**——几乎可以确定是长上下文 LLM 推理的终极硬件方向。

理由如下：

1. **物理定律的约束**：数据搬运的能耗与距离成正比。在 7nm 工艺下，从 HBM 到 GPU 搬运 1 bit 数据的能耗是在 HBM 内部访问 1 bit 的 ~100 倍。长上下文推理的数据移动量如此之大，以至于搬运能耗会超过计算能耗。

2. **HBM 厂商的战略方向**：三星已经展示了 PNM（Processing-Near-Memory）HBM 的原型。SK 海力士的 AiM（Accelerator-in-Memory）项目也在推进。HBM4 的 base die 面积更大、逻辑集成能力更强，为 PNM 提供了更好的物理基础。

3. **推理工作负载的确定性**：与训练不同，推理工作负载的计算模式高度可预测。这使得定制化的存算一体设计可以在窄场景下实现极致效率。

未来 3-5 年，我们可能会看到一个分层的推理硬件生态：
- **GPU/TPU**：处理 Prefill 阶段和 FFN 层（计算密集型）
- **PNM-HBM**：处理 Decode 阶段的 Attention（内存密集型）
- **SSD/CXL 内存池**：存储冷 KV Cache（容量密集型）

AMMA 论文的价值不在于它的具体架构设计，而在于它清晰地证明了：**对于长上下文推理，把计算搬到内存旁边比给内存加带宽更有效。** 这个结论会深刻影响未来几年的 AI 芯片架构方向。

---

### 参考来源

- [AMMA: A Multi-Chiplet Memory-Centric Architecture for Low-Latency 1M Context Attention Serving - SemiEngineering](https://semiengineering.com/replacing-gpu-compute-dies-with-pnm-enabled-hbm-cubes-for-long-context-decode-attention/)
- [Tutti: Making SSD-Backed KV Cache Practical for Long-Context LLM Serving - arXiv:2605.03375](https://arxiv.org/abs/2605.03375)
- [Effective KV Compression with TurboQuant - Machine Learning Mastery](https://machinelearningmastery.com/effective-kv-compression-with-turboquant/)
- [EnergAIzer: GPU Power Prediction Tool for AI Workloads - SemiEngineering](https://semiengineering.com/gpu-power-prediction-tool-for-ai-workloads-mit-ibm/)
- [Samsung PNM-HBM Prototype - Samsung Semiconductor](https://semiconductor.samsung.com/)
