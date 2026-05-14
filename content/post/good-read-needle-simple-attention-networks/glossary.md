# Needle / Simple Attention Networks — 术语表

英中对照术语表，覆盖**架构、训练、部署**三大类。共 35 条。

---

## 一、架构相关

| 英文 | 中文 | 在 Needle 中的含义 |
|------|------|-------------------|
| Simple Attention Network (SAN) | 简单注意力网络 | 完全去除 FFN 的 Transformer 变体，Cactus 自创术语 |
| Feed-Forward Network (FFN) / MLP | 前馈网络 / 多层感知机 | Transformer 中 Attn 之后的全连接层，占总参数 2/3 |
| Encoder-Decoder | 编码器-解码器 | T5/BART 一类双塔架构，Needle 复活了这条路线 |
| Decoder-Only | 仅解码器 | GPT/LLaMA 一类因果生成架构，Needle 故意不用 |
| Cross-Attention | 交叉注意力 | decoder 看 encoder 输出的注意力机制 |
| Masked Self-Attention | 因果自注意力 | decoder 看自己已生成 token 的注意力，带因果 mask |
| RoPE (Rotary Position Embedding) | 旋转位置编码 | Needle 使用的位置编码方式 |
| GQA (Grouped-Query Attention) | 分组查询注意力 | encoder 用 GQA 减少 KV head 数 |
| Gated Residual | 门控残差 | x = x + sigmoid(g) · Attn(N(x))，可学习残差强度 |
| ZCRMSNorm | 零中心 RMS 归一化 | x · (1+γ)/RMS(x)，γ 初始化为 0 |
| QK-Norm | QK 归一化 | 对 Q 和 K 各自做 norm，提升训练稳定性 |
| KV Cache | 键值缓存 | 推理时缓存的注意力 K/V，encoder-decoder 让它定长 |
| Contrastive Head | 对比头 | CLIP-style 的检索头，用余弦相似度排 top-k |
| Tied Embedding | 共享词嵌入 | 输入 embedding 和输出投影矩阵共享权重 |

---

## 二、训练相关

| 英文 | 中文 | 在 Needle 中的含义 |
|------|------|-------------------|
| Knowledge Distillation | 知识蒸馏 | 用大模型（Gemini 3.1）生成数据训小模型 |
| Pretraining | 预训练 | 200B token，27 小时在 16 TPU v6e 上跑完 |
| Post-training / Fine-tuning | 后训练 / 微调 | 2B token 工具调用合成数据，45 分钟 |
| BPE (Byte-Pair Encoding) | 字节对编码 | 词表大小 8192 |
| Muon Optimizer | Muon 优化器 | Newton-Schulz 正交化 SGD，2024 年提出 |
| Newton-Schulz Iteration | 牛顿-舒尔茨迭代 | 近似矩阵正交化的迭代算法，是 Muon 核心 |
| AdamW | AdamW 优化器 | 带权重衰减的 Adam，Needle 在 non-attn 参数上用 |
| Z-Loss | Z 损失 | 辅助损失，约束 logit 的范数稳定 |
| Cross-Entropy (CE) Loss | 交叉熵损失 | 标准语言模型损失 |
| Symmetric Contrastive Loss | 对称对比损失 | CLIP 损失，把 query-tool 对当作正样本 |
| Token-Level Loss Weighting | Token 级损失加权 | 给不同 token 类型不同 loss 权重 (JSON 1× / value 4×) |
| STE (Straight-Through Estimator) | 直通估计器 | 让梯度跨过四舍五入操作的近似方法 |
| QAT (Quantization-Aware Training) | 量化感知训练 | 训练时模拟量化前向，让模型适应低精度 |

---

## 三、部署 / 推理相关

| 英文 | 中文 | 在 Needle 中的含义 |
|------|------|-------------------|
| INT4 Quantization | INT4 量化 | 权重用 4 位整数表示，group_size=32 |
| Prefill Throughput | 预填充吞吐 | 处理 prompt 的速度，Needle 在 Cactus 上 6000 tok/s |
| Decode Throughput | 解码吞吐 | 生成新 token 的速度，Needle 1200 tok/s |
| On-Device Inference | 端侧推理 | 在手机/手表/嵌入式设备上跑推理 |
| Edge AI | 边缘 AI | 不依赖云端的本地 AI 部署 |
| Memory Bandwidth | 内存带宽 | 移动设备推理的真正瓶颈，Needle 砍 FFN 直击此点 |
| Function Calling / Tool Use | 函数调用 / 工具使用 | LLM 输出结构化工具调用请求的能力 |
| Single-Shot Function Call | 单步工具调用 | 一次只调用一个工具，不做规划，Needle 的能力边界 |

---

## 附录：与 Needle 相关的"人名"备忘

| 名字 | 角色 |
|------|------|
| Henry Ndubuaku | Cactus Compute 联创、Needle 第一作者 |
| Keller Jordan | Muon 优化器作者 |
| Tri Dao | FlashAttention / 线性注意力领域代表 |
| Mark Tenenholtz | 知识蒸馏与 small-model SFT 工程师常引用作者 |

---

## 缩写速查

- **SAN** = Simple Attention Network
- **FFN** = Feed-Forward Network
- **GQA** = Grouped-Query Attention
- **RoPE** = Rotary Position Embedding
- **QAT** = Quantization-Aware Training
- **STE** = Straight-Through Estimator
- **PTQ** = Post-Training Quantization
- **CE** = Cross-Entropy
- **KV** = Key-Value (cache)
- **BPE** = Byte-Pair Encoding
- **MIT** = MIT License (软件许可)
- **TPU v6e** = Google 第六代张量处理单元（"Trillium"）
- **BFCL** = Berkeley Function-Calling Leaderboard（业界主流 function-call 基准）
