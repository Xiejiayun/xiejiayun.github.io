# 术语表 · μP / MSSP / MoE Scaling

> 中英对照术语词典，配合 [论文导读正文](./) 与 [概念卡片](./concept-cards.md) 使用。

## A. 缩放与参数化（Scaling & Parameterization）

| 中文 | 英文 | 简释 |
|---|---|---|
| 最大更新参数化 | Maximal Update Parameterization (μP) | Yang & Hu 2021 提出，让特征学习强度保持 Θ(1) 的参数化；dense 网络的"金标准" |
| 最大尺度稳定参数化 | Maximally Scale-Stable Parameterization (MSSP) | 本文提出，要求每个被分解的子项都 Θ(1)；MoE 上的"金标准" |
| bcdα 参数化 | bcdα-parameterization | 用 (b, c, d, α) 四元组刻画一种参数化的统一语言 |
| 缩放定律 | Scaling Laws | 损失 vs FLOPs/参数量的幂律关系（Kaplan et al., Chinchilla） |
| 超参迁移 | Hyperparameter Transfer (μTransfer) | 小模型最优超参直接搬到大模型，需要参数化保证 |
| 共缩放区制 | Co-scaling Regime | 多根 scaling 轴一起趋于无穷时的特定相对速率 |
| 标准参数化 | Standard Parameterization (SP) | 传统的 1/√N init + 固定 LR；在 dense 大模型上已被证不优 |
| 平均场参数化 | Mean-Field Parameterization | μP 的等价形式之一；在 NTK / mean-field 文献中常出现 |

## B. Mixture-of-Experts（MoE）

| 中文 | 英文 | 简释 |
|---|---|---|
| 专家混合 / 混合专家 | Mixture-of-Experts (MoE) | 用 router 把 token 分配给 M 个专家中的 K 个，激活参数 < 总参数 |
| 专家数 | Number of Experts (M) | 一个 MoE 层中并行的专家数；DeepSeek-V3 ≈ 256 |
| 专家宽度 | Expert Width (N_e) | 单个专家内部 FFN 的中间宽度 |
| 激活专家数 | Active Experts (K) | top-K 路由中每个 token 实际激活的 expert 数；通常 K=2 或 K=8 |
| 稀疏度 | Sparsity | 1 - K/M，量化"多少专家被跳过" |
| 路由器 / 门控 | Router / Gating | 决定哪些专家被激活的小网络（通常是个 linear + sigmoid/softmax）|
| top-K 路由 | Top-K Routing | 每个 token 选择路由概率最高的 K 个专家 |
| 专家选择路由 | Expert-Choice Routing | 每个 expert 选择路由概率最高的 K 个 token（Zhou et al.）|
| 软路由 | Soft Routing | 所有 expert 都参与，按 router 输出加权 |
| 无 dropless MoE | Dropless MoE | Megablocks 风格，所有 token 都被处理不丢弃 |
| 负载平衡辅助损失 | Auxiliary Load Balancing Loss | 防止 router 偏向少数 expert 的辅助损失项 |
| 无 aux-loss 平衡 | Aux-Loss-Free Balancing | DeepSeek-V3 用 bias adjustment 代替 aux loss |
| 共享专家 | Shared Expert | 总是激活的专家，提供基础能力（DeepSeek-V2/V3） |
| 细粒度专家 | Fine-grained Experts | 大量小专家（DeepSeek-V3 风格），对应 Regime II |
| 专家利用率 | Expert Utilization | 训练中每个 expert 被路由的频率 |
| 专家瓦解 | Router Collapse | 训练后期 router 只激活少数几个 expert 的失败模式 |

## C. 动力学与训练理论（Dynamics & Training Theory）

| 中文 | 英文 | 简释 |
|---|---|---|
| 动力学平均场理论 | Dynamical Mean-Field Theory (DMFT) | 统计物理工具，描述无穷宽神经网络的训练轨迹 |
| MSRDJ 路径积分 | Martin–Siggia–Rose–De Dominicis–Janssen | DMFT 背后的数学形式 |
| 自一致方程 | Self-Consistent Equations | DMFT 闭包方程，order parameter 互为彼此的输入 |
| 单点分布 | Single-Site Distribution | DMFT 极限下"典型节点"的概率分布 |
| 神经切线核 | Neural Tangent Kernel (NTK) | "懒训练"极限下的核函数；MSSP 不在 NTK regime |
| 特征学习 | Feature Learning | 训练中权重显著变化、学到非平凡表示的 regime |
| 信号传播分析 | Signal Propagation Analysis | 追踪激活和梯度的方差/相关性在层间的演化 |
| 有效更新 | Effective Update | 来自本层权重变化的激活变化 |
| 传播更新 | Propagating Update | 来自上游变化传过来的激活变化 |
| 反向传递 | Backward Pass | 反向传播中梯度的递归 |
| 协方差结构 | Covariance Structure | 神经元/expert 之间的统计相关 |

## D. 概率论与统计物理工具

| 中文 | 英文 | 简释 |
|---|---|---|
| 大数定律 | Law of Large Numbers (LLN) | i.i.d. 样本平均 → 期望；MoE 中"相干方向"项的归宿 |
| 中心极限定理 | Central Limit Theorem (CLT) | i.i.d. 样本平均的涨落 ~ 1/√n；MoE 中"独立方向"项的归宿 |
| Marchenko–Pastur 定律 | Marchenko–Pastur Law | 高斯矩阵 Gram 矩阵的极限谱密度 |
| Haar 分布 | Haar Distribution | 旋转矩阵 / 子空间的均匀分布 |
| Grassmannian | Grassmannian Gr(k, n) | n 维空间中 k 维子空间的集合 |
| 旋转不变性 | Rotation Invariance | 高斯随机权重的关键性质 |
| 路径积分 | Path Integral | 把动力学轨迹整体处理的数学工具 |
| 鞍点近似 | Saddle-Point Approximation | DMFT 中通过最速下降法求泛函积分 |

## E. 优化器与训练框架

| 中文 | 英文 | 简释 |
|---|---|---|
| 随机梯度下降 | Stochastic Gradient Descent (SGD) | 经典优化器；DMFT 严格成立的对象 |
| 自适应矩估计 | Adam / AdamW | 主流优化器；MSSP 论文中 Adam 是启发式推导 |
| 符号梯度下降 | signSGD | 仅用梯度符号的优化器；同期 Jiang et al. 2026 覆盖 |
| 学习率热身 | Warmup | 训练开始时 LR 从 0 线性增长 |
| 余弦衰减 | Cosine Decay | LR 按余弦曲线衰减到最终值 |
| 权重衰减 | Weight Decay | L2 正则，AdamW 中 wd 应保持 scale-independent |
| 同步训练 | Synchronous Training | 所有 worker 步调一致 |

## F. 架构组件

| 中文 | 英文 | 简释 |
|---|---|---|
| 残差连接 | Residual Connection | x + F(x) |
| 预归一化 | Pre-Norm | LayerNorm 放在残差块前面 |
| 均方根归一化 | RMSNorm | 没有可学习偏置的归一化 |
| 查询-键归一化 | QK-Norm | 对 attention 的 Q 和 K 各加一个 RMSNorm 提升稳定性 |
| 嵌入层 | Embedding Layer | token → vector |
| 解嵌入 / 反嵌入 | Unembedding / LM Head | vector → token logits |
| 前馈网络 | Feed-Forward Network (FFN) | MoE 之前的标准 Transformer 子层 |

## G. 数据与基准

| 中文 | 英文 | 简释 |
|---|---|---|
| Dolma3 | Dolma3 | OLMo 系列开源预训练语料 |
| TinyImageNet | TinyImageNet | 200 类的 ImageNet 缩小版，常用于小尺度实验 |
| 验证集损失 | Validation Loss | LR 迁移图通常用它做 y 轴 |
| 训练 token 数 | Training Tokens | Chinchilla-optimal 量 ≈ 20 × 参数量 |

## H. 缩放参数指数（来自 MSSP Table 1）

| 中文 | 英文 | 简释 |
|---|---|---|
| 初始化标准差 | Init Std. | 高斯初始化的标准差，缩放为 $n^{-b}$ |
| 学习率乘数 | LR Multiplier | 在 base LR 上乘的缩放因子，∝ $n^{-c}$ |
| Adam 平方项 ε | Adam ε | 数值稳定项，必须随 layer-wise gradient RMS 缩放 |
| 聚合归一化指数 | Aggregation Multiplier α | 跨 expert 平均后乘 $K^{-\alpha_{\text{agg}}}$ 的指数 |

## I. 评估与社区

| 中文 | 英文 | 简释 |
|---|---|---|
| 复现性 | Reproducibility | 论文开源代码使其在常规算力下可重现 |
| 同期独立工作 | Concurrent Independent Work | Jiang et al. 2026 是 MSSP 的关键交叉验证 |
| 已发表/预印本 | Preprint | 论文 v1 于 2026-05-13 提交至 arXiv |
| 引用图谱 | Citation Graph | 描述论文之间引用关系的网络 |

## J. 工程实操术语

| 中文 | 英文 | 简释 |
|---|---|---|
| 默认初始化 | Default Initialization | PyTorch / Megatron 框架的内置 init；常和 μP/MSSP 冲突 |
| 训练框架 | Training Framework | Megatron, NeMo, DeepSpeed, FSDP 等 |
| 算子级 patch | Op-level Patch | 单点改一个 init 函数即生效的修改类型 |
| 大尺度复现 | Large-Scale Validation | 在 ≥1B 参数上验证理论预测 |
| 工程经验主义 | Engineering Empiricism | 没有理论支持但实测 work 的方法（frontier lab 大量依赖） |
