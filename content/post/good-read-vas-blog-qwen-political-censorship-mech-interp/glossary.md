# 术语表：vas-blog Qwen 3.5 政治审查机制研究

英中对照，按照原研究的章节顺序收录。

| 英文术语 | 中文 / 含义 |
|---|---|
| **mechanistic interpretability** | 机制可解释性：把模型行为还原到具体的 weights / circuits / activations |
| **circuit** | 电路：实现某项功能的、定位明确的一组组件（神经元、attention heads、MLP 子层） |
| **residual stream** | 残差流：transformer 每层之间传递的高维向量，每层 attention/MLP 对它做加法更新 |
| **logit lens** | 把任意中间层的 residual 投给 `lm_head` 解码出 top-1 token，用来"窥视"中间状态的概念态 |
| **diff-of-means** | 平均差：两组 prompt 在某层 residual 的平均之差，单位归一化得一条 direction |
| **direction / axis** | 方向 / 轴：hidden state 里的一条单位向量，对应模型行为的某种线性表征 |
| **steering** | 操控：在某层 residual 上加 `α · d`（一个方向的标量倍）来改变模型输出 |
| **activation patching** | 激活补丁：把一个 prompt 的 residual 在某层"换"到另一个 prompt 的前向过程里，看输出怎么变 |
| **causal tracing** | 因果追踪：通过把 clean residual 注回 corrupted forward pass 来定位行为所在层（Meng et al. 2022） |
| **dose-response** | 剂量响应：α 扫描下行为变化的曲线，sigmoid 形状是因果控制的标志 |
| **α-half** | 半饱和剂量：sigmoid 曲线达到 50% 反转所需的 α |
| **writers / readers split** | 写者 / 读者分段：本研究提出的电路结构——L11–L20 写信号，L20–L31 读信号渲染文本 |
| **tap / layer index** | 取样层：transformer 内部第 N 层 residual 的位置标记（如 tap 14 = 第 14 层输出） |
| **template cell** | 模板格子：(topic × style) 的训练好响应组合，例如 (Tiananmen, deflection) |
| **deflection** | 偏转：拒绝回答但用"我是 AI 助手，主要功能是提供帮助"的话术绕开 |
| **propaganda template** | 宣传模板：用国家立场表述代替事实，例如"一中原则"、"反邪教斗争" |
| **refusal template** | 拒答模板：标准 Western-style "I cannot…" 的安全拒绝 |
| **brittleness** | 脆性：训练好的某条模板在 residual 扰动下崩解的速度——deflection 最脆，refusal 最稳 |
| **denial template** | 否认模板：steering 越界后模型常落入的"这是错误的"式 hallucinated denial |
| **incoherent** | 不连贯：steering 过度后的 off-manifold 噪声输出 |
| **PRC-sensitive content** | PRC 敏感内容：CCP 治理框架下需特殊处理的话题（Tiananmen、Taiwan、Xinjiang、HK、Tibet、Xi、Falun Gong） |
| **Tiananmen** | 1989 年六四事件，本研究用作 deflection 类的锚点 |
| **Falun Gong** | 法轮功，本研究用作 propaganda 类的锚点 |
| **AdvBench** | Zou et al. 2023 的对抗 prompt 数据集，本研究用作 harmful 类的锚点 |
| **chat template** | 聊天模板：`<\|im_start\|>user… <\|im_end\|>\n<\|im_start\|>assistant\n` 这种把对话结构编码进 prompt 的格式 |
| **post-train / posttraining** | 后训练：包括 SFT、RLHF、DPO 等所有 pretraining 之后的对齐微调 |
| **base model** | 基础模型：仅做 pretraining、未经 alignment 的 checkpoint（Qwen3.5-9B-Base） |
| **MLP** | 多层感知机：transformer 每层里的两层前馈网络 |
| **full-attention** | 全注意力：Qwen3.5 的 hybrid 架构中，标准 softmax 多头注意力的那一份（每 8 块里出现 1 次） |
| **Gated DeltaNet** | 门控线性注意力变体：Qwen3.5 hybrid 架构中的 3:1 比例占多数的那部分 |
| **lm_head** | 语言模型头：把最后一层 residual 映射到词表 logits 的线性层 |
| **mean replacement** | 均值替换：把某层的 residual 用某类 prompt 的均值代替 |
| **K/V swap** | Key/Value 交换：把一个 prompt 的 attention K、V cache 替换成另一个 prompt 的 |
| **subspace patching** | 子空间补丁：只替换 residual 在某个低维子空间上的投影分量 |
| **channel transplant** | 通道移植：把 source residual 的 3 维 subspace 坐标移植到 target residual |
| **R²** | 决定系数：OLS 拟合的可解释方差比例 |
| **AUC** | 曲线下面积：分类器质量度量，AUC ≥ 0.99 表示几乎完全可分 |
| **CV accuracy** | 交叉验证准确率：本研究里 reader-band MLP 的 verdict 解码达 0.97–1.00 |
| **5 SD threshold** | 5 倍标准差阈值：判断单神经元是否是 sharp class detector 的常用阈值 |
| **token perturbation** | token 扰动：把 prompt 中的关键词替换为 `[X]` 占位符 |
| **thinking mode** | 思考模式：Qwen3 系列的 `enable_thinking=True`，模型先输出 `<think>…</think>` 再正式回答 |
| **CoT monitoring** | 思维链监控：通过读取 CoT 内容判断模型意图的安全方法 |
| **refusal direction** | 拒答方向：Arditi et al. 2024 提出的单一 d_refuse direction，本研究的直接前身 |
| **Contrastive Activation Addition (CAA)** | 对比激活相加：Panickssery et al. 2024 的通用 steering 方法 |
| **Refusal in Language Models Is Mediated by a Single Direction** | Arditi 2024 论文标题 |
| **R1dacted** | Naseh et al. 2025 关于 DeepSeek-R1 政治审查的行为研究 |
| **R1 1776** | Perplexity 团队对 DeepSeek-R1 的 decensored 微调发布 |
| **dose band** | 剂量带：α 既不太小（无效）也不太大（off-manifold）的窗口 |
| **off-manifold** | 偏离流形：把 residual 推离训练分布支撑集，模型行为变不可预测 |
| **sparse autoencoder (SAE)** | 稀疏自编码器：把高维 residual 拆成可解释的 sparse features，常用于 reader-band 机制研究 |
| **affine map** | 仿射映射：`y = Wx + b`，OLS 拟合 writers 时使用 |
| **last-prompt-token logit lens** | 最后一个 prompt token 的 logit lens：取 user 输入最末 token 的 residual 做 lens 解码 |
| **cybersecurity law** | 网络安全法：Qwen 的中文 thinking trace 中显式提到的合规依据 |
| **decensor** | 去审查：通过工程手段移除模型的政治内容过滤 |
| **R1 1776 decensoring** | Perplexity 发布的、不依赖 mech interp 的 fine-tune 式去审查方法 |
| **Tank Man** | 1989 年北京"坦克人"图像，本研究 Tiananmen 子话题的具体测试项 |
| **organ harvesting** | 摘除器官，对应法轮功相关 propaganda 模板的测试问题 |
| **state-aligned framing** | 国家立场叙述：与官方表述一致的事实框架 |
