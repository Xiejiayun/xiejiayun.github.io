# MinT 术语表（中英对照）

> 配套 [【论文导读】MinT](./) · 48 条覆盖 LoRA / RL / MoE / 系统 / 调度 / 服务化全栈。

## A. LoRA 与参数高效微调

| 中文 | 英文 | 解释 |
|---|---|---|
| 低秩适配 | LoRA (Low-Rank Adaptation) | 在原权重旁附加 $W \to W + BA$ 形式的低秩更新，$B \in \mathbb{R}^{d\times r}$, $A \in \mathbb{R}^{r\times k}$, rank $r \ll d, k$。 |
| 适配器修订版 | Adapter revision | LoRA 训练完成后导出的、不可变的、内容寻址的 serving-format 字节流。MinT 的核心跨界对象。 |
| 政策记录 | Policy record | 持久化的服务端生命周期状态，绑定一个业务行为与其所有 adapter revisions。 |
| 政策群体 | Policy population | 一个 service 内所有可部署的 LoRA policy 集合，MinT 的目标 scale 是 10⁶。 |
| 目标模块 | Target modules | LoRA 注入的层集合，通常是 attention Q/K/V/O 与 FFN gate/up/down。 |
| 秩 | Rank | LoRA 内部低秩矩阵的秩 $r$。MinT 实测 rank-1 时 adapter 仅 ~0.10% base size。 |
| 合并适配器 | Merge adapter | 把 LoRA 折叠回 base 得到一份完整 checkpoint。MinT 不做这件事。 |
| PEFT 格式 | PEFT format | HuggingFace PEFT 库定义的 LoRA serving 张量布局。 |
| 量化适配器 | QLoRA | LoRA 与 4-bit 量化的结合，本文未直接使用但在参考文献中。 |
| 自适应低秩 | AdaLoRA | LoRA 的自适应秩变种，Zhang 2023。 |

## B. 强化学习与后训练

| 中文 | 英文 | 解释 |
|---|---|---|
| 后训练 | Post-training | pretrain 之后的 SFT/DPO/RLHF/RLVR 阶段总称。MinT 是 post-training 基础设施。 |
| 组相对策略优化 | GRPO (Group Relative Policy Optimization) | 一组 rollout 之间相对比较的 policy gradient 算法，DeepSeek 提出。 |
| 直接偏好优化 | DPO (Direct Preference Optimization) | 不用显式 reward model 的偏好学习算法。 |
| 可验证奖励 RL | RLVR (RL with Verifiable Rewards) | 数学/代码等可程序验证的 RL post-training 范式。 |
| 监督微调 | SFT (Supervised Fine-Tuning) | 用 (prompt, response) 监督数据做的 next-token-prediction 微调。 |
| 部署 | Rollout | RL 训练中由 policy 在环境/prompts 上生成 trajectory 的过程。 |
| 回滚记录 | Rollout record | rollout 产生的完整 trajectory 元数据，MinT 把它当作 service 的一等对象（用于复现、replay、debug）。 |
| 重要性采样 | Importance sampling | 用 $\rho = \pi_{\text{train}} / \pi_{\text{rollout}}$ 校正 off-policy 偏差。 |
| 截断重要性采样 | Truncated importance sampling | 把 $\rho$ clip 到一个置信带内防止 variance 爆炸。 |
| IcePop 修正 | IcePop correction | Ling Team 2025 提出的 importance-ratio 离带 → token mask 方案，MinT 用于 DSA 一致性。 |

## C. 模型架构

| 中文 | 英文 | 解释 |
|---|---|---|
| 混合专家 | MoE (Mixture of Experts) | 把 FFN 拆成 N 个 expert，每个 token 只激活 top-k 个。Qwen3-235B-A22B 即 235B 总参 / 22B 活动参。 |
| 多潜在注意力 | MLA (Multi-head Latent Attention) | DeepSeek 提出的低秩潜在 KV 注意力，显著降低 KV cache 占用。 |
| DSA 稀疏注意力 | DSA (DeepSeek-style Sparse Attention) | 用 indexer 选 top-k key 后再算 attention 的稀疏方案。 |
| 多 token 预测 | MTP (Multi-Token Prediction) | 一次 forward 同时预测多个 next tokens 的训练目标。 |
| 路由器 | Router | MoE 中负责把 token 分配到 expert 的 gating 网络。 |
| 路由器漂移 | Router drift | 同一 token 在 train 和 rollout 两端被路由到不同 expert 的现象。 |
| R3 路由重放 | R3 (Router Route Replay) | Ma 2025 提出，rollout 时记录专家 id，train 时强制 replay。MinT 主要的 MoE 一致性方案。 |
| 索引器 | Indexer (in DSA) | DSA 中选 top-k key 的小网络，浮点累加路径敏感。 |

## D. 分布式训练系统

| 中文 | 英文 | 解释 |
|---|---|---|
| 张量并行 | TP (Tensor Parallelism) | 把单层权重切分到多 GPU。 |
| 专家并行 | EP (Expert Parallelism) | 把 MoE 不同 expert 分配到不同 GPU。 |
| 流水并行 | PP (Pipeline Parallelism) | 不同层放在不同 GPU 上做流水。 |
| Megatron-LM | Megatron-LM | NVIDIA 的 TP/PP/EP 训练框架，MinT 的训练后端。 |
| 桥接 | Megatron-Bridge | Megatron 与第三方系统对接的中间层。 |
| 完全分片数据并行 | FSDP (Fully Sharded Data Parallel) | PyTorch 的零冗余数据并行；MinT 单 worker PEFT 路径常用。 |
| 零冗余优化器 | ZeRO | DeepSpeed 的内存分片技术。 |

## E. 推理服务

| 中文 | 英文 | 解释 |
|---|---|---|
| vLLM | vLLM | UC Berkeley 提出的 PagedAttention 推理引擎，MinT 的 serving 后端。 |
| 分页注意力 | PagedAttention | 把 KV cache 像 OS 分页一样管理，显著提升内存利用率。 |
| 共享基座 | Shared-base serving | 多个 LoRA 共享同一份 resident base weights。 |
| 可寻址目录 | Addressable catalog | MinT 的最外层 cache，10³–10⁶ entries，全局持久化。 |
| CPU 适配器缓存 | CPU adapter cache | 中间层 cache，几百个 adapter，LRU。 |
| GPU 批 | GPU batch | 同一 decoding step 中共存的 distinct adapters 上限（实测 64）。 |
| 冷启动 | Cold load | adapter 不在任何 cache 中，需要从远端 catalog 拉取并加载。 |
| 反压 | Backpressure | 当 cold load 队列拥堵时，让上游限流而不是无限排队。 |

## F. MinT 内部术语

| 中文 | 英文 | 解释 |
|---|---|---|
| 服务面 | Service plane | MinT 的控制面，无 GPU，做 queue/admission/policy lookup/metadata。 |
| 计算面 | Compute plane | MinT 的执行面，hold base + adapter，分 trainer / sampler / serving 三种 worker。 |
| 资源准入 | Resource admission | 跟踪 worker / training session / adapter pin 状态，决定是否准入新请求。 |
| 元数据写入规则 | Metadata write rule | checkpoint/export/rollout 必须先写 metadata 才对外可见。 |
| 时分多 LoRA 训练 | Time-sliced multi-LoRA training | 同 base resident 下，多个 policy 的 LoRA 张量+optimizer 在时间片中轮换。 |
| 分布式导出 | Distributed export | 把 Megatron 训练的 sharded adapter 聚合并去重，导出为单一 PEFT 文件。 |
| 打包 MoE LoRA | Packed MoE LoRA | 把 30k+ 个 expert × module LoRA tensor 打包为一个连续 buffer，减少 loader 元数据开销。 |
| Tinker 兼容 API | Tinker-compatible API | 模仿 Thinking Machines Lab 的 Tinker 服务接口范式。 |
| mint-cookbook | mint-cookbook | MinT 公开的 SFT/DPO/GRPO/AutoResearch recipe 仓库（GitHub: MindLab-Research）。 |
| 跑分代理 | Proxy evaluator | full benchmark 之前的低成本筛选器，可能 over-fit。 |
| 全清单对照 | Full-manifest control | 用同样数据 + baseline recipe 跑的对照实验，区分「数据效应」与「recipe 效应」。 |

---

> 总计 48 条。LoRA + RL + MoE + Megatron/vLLM + service 调度是 MinT 的完整技能栈，建议读完论文后回头按这张表 self-check 是否每个概念都能复述。
