# 术语表：RoPE 长上下文失败模式（中英对照）

> 50 条术语，按主题分组。优先选论文里出现频率高 + 工程实践中遇到概率高的。

## 一、位置编码核心概念

| 中文 | English | 简释 |
|---|---|---|
| 位置编码 | Positional Embedding / Positional Encoding | 让 Transformer attention "知道" token 顺序的机制 |
| 旋转位置编码 | Rotary Positional Embedding (RoPE) | Su 等 2021 提出的相对位置编码，把向量二维子向量按位置旋转 |
| RoPE 乘积 | RoPE Product | query 和 key 经过 RoPE 旋转之后的内积 $S(m)$ |
| RoPE 基础频率 | RoPE Base ($B$) | 决定每对子向量旋转频率的超参，常用 $10^4 \sim 10^8$ |
| 角频率 | Angular Frequency ($\theta_n$) | 第 $n$ 对子向量的旋转速率，$\theta_n = B^{-n/h}$ |
| 振幅 | Amplitude ($a_n$) | 第 $n$ 对子向量在 RoPE product 中的权重 |
| 相位 | Phase ($\varphi_n$) | 第 $n$ 对 (q, k) 子向量在二维平面的夹角 |
| 相对距离 | Relative Distance ($m$) | query 与 key 在序列中的 token 间隔 |
| 上下文长度 | Context Length ($M$) | 模型一次能看到的最大 token 数 |
| 半隐藏维度 | Half Hidden Dimension ($h$) | $h = d / 2$，attention head 维度的一半 |
| 近邻偏好 | Locality Bias | attention 应该偏向更近的 token |
| 长度外推 | Length Extrapolation | 把训练时短上下文模型用于推理时更长输入 |

## 二、本文 4 个失败模式

| 中文 | English | 简释 |
|---|---|---|
| 位置反转 | Position Inversion | 同 key、远位置反而拿到更高 attention 分数 |
| 位置混叠 | Position Aliasing | 两个不同距离的 attention 分数完全相同 |
| Token 反转 | Token Inversion | 零距离上 $k_1$ 比 $k_2$ 相关，但距离 $m$ 上反过来 |
| Token 混叠 | Token Aliasing | 同位置上不同 key 的 attention 分数相同 |
| 注意力不变性 | Attention Invariance | 互换 keys 不改变 attention 输出（aliasing 的语义后果） |
| 别名对 | Aliasing Pair | $(m_1, m_2)$ 满足 $S(m_1) = S(m_2)$ 的距离对 |
| 失败模式 | Failure Mode | 论文用于统称四种 RoPE 缺陷的术语 |

## 三、相关 attention / Transformer 概念

| 中文 | English | 简释 |
|---|---|---|
| 注意力机制 | Attention Mechanism | Transformer 的核心算子 |
| 多头注意力 | Multi-Head Attention | 把 attention 拆成 $H$ 个独立头，并行计算后拼接 |
| 查询 | Query ($q$) | attention 的"问询"向量 |
| 键 | Key ($k$) | attention 的"被问询"向量 |
| 注意力分数 | Attention Score | $q \cdot k$（RoPE 之后） |
| 注意力 sink | Attention Sink | 模型把过多注意力放在序列开头几个 token 的现象 |
| 注意力分布 | Attention Distribution | softmax 后的归一化权重 |
| Causal Mask | Causal Mask | 让 token 只能注意到自己和之前的 token |
| Permutation Invariance | Permutation Invariance | attention 在没有位置编码时对 token 顺序无感 |

## 四、长上下文 / 长度扩展技术

| 中文 | English | 简释 |
|---|---|---|
| 位置插值 | Position Interpolation (PI) | Chen 等 2023，把长 context 按比例压缩到训练长度 |
| YaRN | Yet Another RoPE extensioN | Peng 等 2023，NTK-aware 的 RoPE 长度扩展 |
| LongRoPE | LongRoPE | Microsoft 2024，渐进式扩展 RoPE 到 2M context |
| 大海捞针 | Needle in a Haystack (NIAH) | 在长文档里藏一句关键信息让模型找 |
| RULER | RULER (long-context benchmark) | Hsieh 等 2024 的长上下文综合 benchmark |
| BABILong | BABILong | Kuratov 等 2024 的百万 context 评测 |
| 中间迷失 | Lost in the Middle | Liu 等 2024，长上下文模型对中段信息不敏感的现象 |

## 五、概率 / 数学工具

| 中文 | English | 简释 |
|---|---|---|
| 中心极限定理 | Central Limit Theorem (CLT) | 独立随机变量之和趋于正态分布 |
| Berry-Esseen 不等式 | Berry-Esseen Bound | CLT 的有限样本误差上界 |
| 正态随机变量 | Normal Random Variable | 高斯分布的随机变量 |
| 概率下界 | Probability Lower Bound | 某事件发生概率的保证最小值 |
| 数据类型精度 | Data Type Precision | BF16 / FP16 / FP32 的有效位数 $f$ |
| 显式 fraction 位 | Explicit Fraction Bits | BF16 是 7、FP16 是 10、FP32 是 23 |

## 六、本文涉及的 LLM

| 中文 | English | 简释 |
|---|---|---|
| Llama 3.1-8B | Meta Llama 3.1-8B | 128K context 的小模型，本文主要实验对象 |
| Mistral-7B | Mistral 7B Instruct v0.3 | 法国 Mistral 的 7B 开源模型 |
| Qwen3-8B | Alibaba Qwen3 8B | 阿里 Qwen3 系列开源 |
| DeepSeek-V3.1 | DeepSeek V3.1 | 总参 671B、激活 37B 的 MoE |
| Kimi-K2.5 | Moonshot Kimi K2.5 | 月之暗面的开源大模型 |
| gpt-oss-120B | OpenAI gpt-oss 120B | OpenAI 开源的 120B 模型 |

## 七、相关 / 对手位置编码方案

| 中文 | English | 简释 |
|---|---|---|
| 绝对位置编码 | Absolute Positional Embedding | 原版 Transformer 用的 sin/cos |
| 相对位置编码 | Relative Positional Embedding | Shaw 等 2018，编码 token 对的距离 |
| ALiBi | ALiBi | Press 等 2022，给 attention 加线性距离 penalty |
| NoPE | NoPE (No Positional Embedding) | Kazemnejad 等 2023 / Gelberg 2025，完全去掉位置编码 |
| 学习位置 | Learned Positional Embedding | GPT-2 风格，每个位置一个可学习向量 |

> 📚 **进阶阅读建议**：
>
> - RoPE 原始论文：Su et al. "RoFormer: Enhanced Transformer with Rotary Position Embedding" (2021)
> - NIAH 失败的综述：Liu et al. "Lost in the Middle" (2024)
> - RoPE 长度外推：Peng et al. "YaRN" (2023)
> - 没有 RoPE 的尝试：Gelberg et al. "Extending the context of pretrained LLMs by dropping their positional embeddings" (2025)
