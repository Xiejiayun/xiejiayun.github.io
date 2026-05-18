# MinT 关键概念卡片

> 配套 [【论文导读】MinT：把「百万 LoRA × 1T 基模」做成一个可调度服务的工程母带](./)
>
> 12 张正向理解 MinT 设计精神的概念速查卡。建议先读 [glossary.md](glossary.md) 中的术语表再回来逐张看。

---

## 卡 01 · Adapter Revision（适配器修订版本）

- **定义**：一份**冻结**的 LoRA 权重快照，存为 PEFT serving 格式，是 MinT 唯一跨越「训练-推理」边界的可执行对象。
- **关键属性**：内容寻址 / 不可变 / 包含 base 兼容版本声明 / 包含 target module 与 rank 元数据。
- **类比**：把它想成「**Docker 镜像**」——base model 是宿主机内核，adapter revision 是上面的容器镜像。

## 卡 02 · Policy Record（政策记录）

- **定义**：service plane 拥有的**持久化**生命周期对象，把一个「业务行为」绑定到一系列 adapter revision 上。
- **包含**：兼容的 base 版本、LoRA rank、target modules、最新训练 checkpoint、保留的 rollout records、所有导出过的 adapter revisions。
- **类比**：相当于 git 仓库——adapter revision 是 commit，policy record 是 branch + history。

## 卡 03 · 三 Regime 对比

| Regime | 跨界对象 | 大小（30B） | 切换时间 |
|---|---|---|---|
| Full fine-tuning | 完整 ckpt | ~60 GB | 分钟级 |
| Merge-based LoRA | merged ckpt | ~60 GB | 分钟级 |
| **MinT (adapter-only)** | LoRA bytes | **1.69 GB** | **秒级** |

MinT 的设计前提是 base 在训练侧和推理侧都是 resident，跨界只过 LoRA 字节流。

## 卡 04 · R3 Router Replay

- **解决什么问题**：MoE 训练-推理路由不一致（同一 token，sampler 选了 expert A，但 trainer 反向时算到 expert B 上，梯度污染）。
- **怎么解**：rollout 时记录每个 token 的专家 id；train 时**强制 replay** 这个路由；replay 不通就把这个 token 的 advantage mask 掉。
- **实测漂移率**：Qwen3-30B 用 R3 时仅 **0.0013%** out-of-route，远低于不用 R3 的 0.0097%。
- **代价**：丢失了一部分潜在的 routing learning signal——R3 实质上把 router 当作 **frozen**。

## 卡 05 · IcePop Importance Clip（DSA 一致性修复）

- **解决什么问题**：DSA（DeepSeek-style Sparse Attention）的 indexer 在 fp 累加路径不同的情况下会选出不同的 top-k key，**无法 replay**。
- **怎么解**：不修 indexer，改修 RL objective——计算 train/rollout 概率比 $r_t = \pi_{\text{train}}(a_t|s_t) / \pi_{\text{rollout}}(a_t|s_t)$，离开置信带就把该 token importance weight 设零。
- **来源**：Ling Team 2025, arXiv:2510.18855。
- **代价**：与 R3 类似，丢失部分 token 的梯度信号——是一种「容差式」一致性而不是「精确式」一致性。

## 卡 06 · Concurrent Multi-Policy GRPO

- **核心动作**：同一份 base resident 上，三个 LoRA policy 的 GRPO 训练**交错**执行。
- **加速来源**：填补单 policy GRPO schedule 里的气泡——rollout 等待、reward 评分等待、梯度同步等待。
- **关键观察**：peak memory **不变**，因为 base 是共享的，三套 adapter + optimizer state 是顺序激活的。
- **实测**：Qwen3-4B 1.77× / Qwen3-30B 1.45×。

## 卡 07 · Three-Tier Adapter Cache（三层缓存）

```
Catalog (10^3 ~ 10^6 entries, durable, control-plane)
  ↓ promote on first hit
CPU Cache (hundreds per engine, LRU)
  ↓ promote by batch scheduler
GPU Batch (≤ 64 distinct adapters per decoding step)
```

这是 MinT 服务层的核心数据结构。三层的容量、命中率、promote 策略都被独立测量与配置。

## 卡 08 · Packed MoE LoRA Tensor

- **痛点**：MoE LoRA 的 expert 数 × A/B 矩阵 × target modules 容易产生 30k+ 个小 tensor。每个都要 file seek + malloc + tensor build——元数据开销远大于数据传输。
- **解法**：把同一个 expert group 的 LoRA 打包成一个**连续 buffer**，loader 一次读取后再切片。
- **实测**：tensor 数 37,248 → **672**（55.4× 少）；文件大小几乎不变（1.05×）；live load 加速 **8.5–8.7×**，中位数压到 0.2 s 以下。
- **教训**：在大模型推理时代，**对象数 ≠ 字节数**，loader 的元数据路径常常是隐形瓶颈。

## 卡 09 · Cold Load p95（冷启动 SLO）

- **测量场景**：单 4-GPU Qwen3-30B rank-1 actor，N=64 distinct adapters/批。
- **数据**：warm cache **p95 = 21.35 s**；cold cache **p95 = 199.81 s**（接近 3.5 分钟）。
- **意义**：MinT 把 cold load 当作**调度任务**而非「请求路径上的小麻烦」——专门有 backpressure + deduplication + 分离 cold path 的隔离 fleet。
- **fleet sizing 含义**：1M catalog + 2300 active wave 需要 144 GPUs 做 warm path + 288 GPUs 做 cold-burst 隔离。

## 卡 10 · Sticky-Hash 路由的失败案例

- **测试**：2048-adapter catalog，naive 一致性哈希 2 副本路由，concurrency 加到 230。
- **结果**：**49.23% 错误率**（请求被打到没有缓存目标 adapter 的 engine）。
- **结论**：**当 catalog 远大于 cache 容量时，sticky-hash 不可用**。必须用 cache-aware 的动态调度器（结合在线 cache 状态决策路由）。
- **价值**：这是论文里最少见的「**我们试过这个简单方案它不行**」式的负面结果，对工业界极其宝贵。

## 卡 11 · Service Plane vs Compute Plane

- **Service Plane（控制面）**：Tinker-兼容 API、queue、policy lookup、resource admission、operation state、durable storage（policy records / checkpoints / rollouts / exported adapters）。
- **Compute Plane（计算面）**：三种 worker——单 worker PEFT trainer / Megatron 分布式 trainer / vLLM sampler-serving actor。
- **关键设计**：service plane **永不**触碰 GPU，只做调度与元数据；compute plane 只 hold base + adapter，没有任何持久状态。这种分离让 control plane 能轻松横向扩展。

## 卡 12 · AutoResearch + Full-Manifest Control（recipe 评估）

- **场景**：LawBench AutoResearch 跑出 v11，proxy 评测分数高，但 full LawBench = 0.4858（低于 v10 的 0.4889）——**proxy over-fit**。
- **机制**：v23 被接受时 proxy=0.5554 / full=0.5079，明显真实提升；同时跑「**full-manifest control**」（同样的数据但 baseline recipe）作为对照，把「数据效应」和「recipe 效应」分开记账。
- **意义**：这是把**「实验科学方法论」嵌入到 service plane** 的非常成熟的做法。任何想真正衡量「我的 SFT/RL recipe 是否带来了改进」的团队都应该抄这一段。

---

> 这 12 张卡覆盖了 MinT 的**设计意图（卡 1-3）+ 训练侧一致性（卡 4-6）+ 服务侧调度（卡 7-10）+ 控制面架构（卡 11）+ 评估方法论（卡 12）**。把这些卡读熟，等于读了 80% 的论文。
