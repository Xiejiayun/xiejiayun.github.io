# Needle / Simple Attention Networks — 关键概念卡片

阅读建议：把这 12 张卡片当作"在咖啡桌上把这篇文章讲给同事"的口袋资料。每张 1-2 分钟，独立成义。

---

## 卡片 1：FFN（Feed-Forward Network）/ MLP

**是什么**：Transformer 每个 block 里 attention 之后那个 2-3 层的全连接。形状一般是 `Linear(d → 4d) → GELU → Linear(4d → d)`，占总参数约 2/3。

**它的"实际工作"**：在权重里"记忆事实"和做 per-position 特征变换。它是一个可微的 key-value 存储——比如"巴黎是法国的首都"这条事实，会以某种分布式形式存在 FFN 权重里。

**Needle 的判断**：当模型可以从输入读到完整上下文（工具签名、参数 schema），FFN 的"记忆"角色就被外部输入替代了，于是 2/3 参数变成纯冗余。

**别忘了**：这一论断只对"知识在外部"的任务成立。开放问答、闲聊、长文写作仍然需要 FFN。

---

## 卡片 2：Encoder-Decoder vs Decoder-Only

**是什么**：
- **Encoder-only**：BERT 一类，只编码不生成。
- **Decoder-only**：GPT 一类，从左到右因果生成。
- **Encoder-Decoder**：T5、BART 一类，先编码再用 cross-attention 解码。

**为什么 2019-2025 几乎全 decoder-only**：因为 LM 的"输入和输出在同一语义平面"（续写），decoder-only 简单、并行训练好做。

**Needle 反向**：工具调用是**异质生成**——输入是 query + JSON schema，输出是 JSON 实例。两边语义平面不同，cross-attention 是天然桥梁；同时 encoder 输出是定长，KV cache 不会爆炸。

**记忆点**：当你的任务是"看一个固定结构、生成另一个固定结构"，encoder-decoder 仍然可能是最优解。

---

## 卡片 3：Gated Residual

**标准形式**：`x = x + Attn(Norm(x))`

**Needle 形式**：`x = x + sigmoid(gate) * Attn(Norm(x))`，gate 是 per-sublayer 可学习标量，初始化 0。

**关键直觉**：sigmoid(0) = 0.5，所以训练开始时残差只有半强度。模型可以学到"这一层完全开"或"这一层完全关"，而不会丢失梯度高速公路。

**为什么 Needle 需要**：去掉 FFN 后，每层只有"加增量"的能力（没有"重写"的能力）。门控让模型自己挑哪几层重要。

---

## 卡片 4：ZCRMSNorm

**RMSNorm**：`x · γ / RMS(x)`，γ 初始化为 1。
**ZCRMSNorm**（Zero-Centered）：`x · (1+γ) / RMS(x)`，γ 初始化为 0。

**差别**：训练开始时整个归一化层等价于"恒等映射 + RMS 缩放"，γ 从 0 开始学，没有任何初始偏置。

**配合 Gated Residual**：整个网络初始状态是"阻尼的恒等 + 阻尼的注意力增量"，所有学习从零偏置起点开始。这种"干净初始化"在小模型上尤其重要。

**起源**：nGPT (Nvidia)、DeepSeek-V3 等近期工作的同一脉络。

---

## 卡片 5：Muon Optimizer

**是什么**：2024 年底 Keller Jordan 提出的优化器。每步用 Newton-Schulz 迭代把更新矩阵近似正交化，再应用到权重。

**为什么 Needle 用**：去掉 FFN 后，整个网络是"一堆线性投影"的堆叠。如果不加约束，多层线性层可能塌缩到一个等效低秩矩阵，深度白堆。Muon 的正交化约束让 Q/K/V/O 矩阵保持满秩。

**注意**：Needle 只在 attention 投影上用 Muon（LR 0.02），其他参数用 AdamW（LR 3e-4）。这种"按参数物理意义分桶优化"是 2026 年小模型训练的明显趋势。

---

## 卡片 6：INT4 QAT as Regularization

**QAT**（Quantization-Aware Training）：在训练时模拟量化的前向（"假量化"），用 STE（直通估计器）让梯度跨过四舍五入。

**Needle 的创新用法**：不是为了"训完能部署到 INT4"才做 QAT，而是发现**量化噪声本身是一种好的正则化器**——对没有 FFN、参数本来就少、易过拟合的小模型，每 100 步一次的 "权重四舍五入" 起到了 weight noise injection 的作用。

**副产品**：部署到 INT4 时没有 PTQ gap，因为训练时模型已经习惯被量化。

---

## 卡片 7：Cross-Attention

**是什么**：注意力的"Q 来自 decoder，K/V 来自 encoder"的版本。Encoder-decoder 模型里 decoder 每一步都做：
1. Masked self-attention（看自己已经生成的）
2. Cross-attention（看 encoder 输出）

**为什么 Needle 关键**：encoder 一次编码工具列表 + query，产出一个定长上下文向量；decoder 在生成 JSON 时通过 cross-attention 反复"指"回 encoder 的对应位置，从输入抄出工具名和参数值。这正是工具调用的本质操作。

---

## 卡片 8：CLIP-style Contrastive Tool Head

**架构**：encoder output → mean pool → Dense(d/4) → ReLU → Dense(128) → L2 normalize → 单位向量。

**训练**：对称对比损失（CLIP 同款）。每个 batch 把 query 和正样本工具配对，in-batch 负样本作对比信号。可学习温度 `log_temp`。主 CE loss 的 0.1 倍权重。

**推理**：把 query 和每个候选工具都过 encoder，按余弦相似度排 top-k。

**意义**：当工具集庞大（如企业 MCP 集群），先用对比头过滤到 top-k 再让模型生成。**关键点**：encoder 在生成和检索之间共享，省下大量参数。

---

## 卡片 9：Knowledge Distillation（知识蒸馏）

**是什么**：用一个大模型（teacher）的输出训练一个小模型（student）。Needle 的 teacher 是 Gemini 3.1 Flash-Lite。

**Needle 的蒸馏不是 logit 蒸馏**：它是"用 Gemini 合成训练数据"——通过 Gemini API 生成 (query, tools, expected_output) 三元组 2B token，然后让 Needle 在这些数据上学习。

**这点很关键**：所以严格说 Needle 不是"参数级蒸馏"，而是"数据级蒸馏"。这种做法的好处是不需要 teacher 的 logits（API 模型给不了），坏处是丢失了软标签信息。

---

## 卡片 10：Token-Level Loss Weighting

**做法**：训练时对不同 token 的 cross-entropy 损失加不同权重：
- JSON 结构 token（`{`, `}`, `:`, `,`）：1.0×
- 工具名：2.0×
- 参数 key：1.5×
- **参数 value：4.0×**

**为什么这样调**：观察到训练早期模型很快学会 JSON 结构（~99% parse rate），实际错误集中在参数值。**直接把损失加权对齐到错误分布**，比寄希望于参数容量自动学习更直接。

**通用启发**：在监督学习里，"错在哪里就加权哪里"是一种被低估的工程手段。

---

## 卡片 11：On-Device Inference Engine

**是什么**：在手机/手表/嵌入式设备上跑模型推理的运行时。常见的有 llama.cpp、MLC-LLM、ONNX Runtime、Apple Core ML。

**Cactus 自研引擎**：从零为 ARM CPU / NPU / 定制 SoC 设计。Needle 在 Cactus 上跑到 6000 tok/s prefill + 1200 tok/s decode 的关键不在 GPU，而在于 INT4 量化 + 无 FFN（FFN 在手机 SoC 上是带宽杀手）。

**端到端逻辑**：Cactus 做引擎 → 引擎友好的架构 → 用这个架构训 Needle → Needle 在 Cactus 上跑得飞快。三件事互相强化，这是大厂方案很难复制的。

---

## 卡片 12：Function Calling / Tool Use

**是什么**：让模型输出结构化的"工具调用请求"，由调用方解析后执行外部函数。OpenAI Function Calling、Anthropic Tool Use、Google Gemini Tool Use 都是同一概念的不同接口。

**为什么是 Agentic AI 的基础**：所有 LLM Agent（Cursor、Claude Code、ChatGPT plugins）的底层都是一连串的 tool call。把这一层做小做快，整个 agent 的延迟和成本都能下来。

**Needle 的定位**：**单步动作模型**。它不做 planning、不做记忆、不做多轮——只做"给我 query 和 tools，输出 JSON 调用"。这种**能力收窄**的设计让它能在 26M 参数里把这一件事做到极限。
