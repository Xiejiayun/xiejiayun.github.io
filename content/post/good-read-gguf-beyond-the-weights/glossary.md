# 英中对照术语表 · 本地大模型推理

> 主文《GGUF 不只是权重》相关术语。覆盖 GGUF 格式、量化、采样、工具调用、多模态五大门类。

## GGUF 与文件格式

| English | 中文 | 注解 |
|---|---|---|
| GGUF (GGML Universal File) | GGML 通用文件格式 | llama.cpp 使用的单文件模型格式。 |
| GGML | GGML | 由 Georgi Gerganov 开发的 C 张量库，llama.cpp 的底层。 |
| safetensors | safetensors | HuggingFace 主推的张量序列化格式，安全且 mmap 友好。 |
| OCI Image | OCI 镜像 | Open Container Initiative 的容器镜像规范，Ollama 借用了它。 |
| Metadata Key | 元数据键 | GGUF 文件里的 string → value 映射条目。 |
| Tensor | 张量 | 多维数组，模型权重的基本单位。 |
| mmap (Memory-Mapped File) | 内存映射文件 | 把文件映射进进程地址空间。 |
| Zero-Copy Load | 零拷贝加载 | 加载模型时不复制数据到 RAM，直接从磁盘 page 进来。 |
| Manifest | 清单 | 描述包内容的索引文件（OCI / 容器术语）。 |

## 量化（Quantization）

| English | 中文 | 注解 |
|---|---|---|
| Quantization | 量化 | 把 fp16/fp32 权重压成低 bit 整数。 |
| Q4_K_M | Q4_K_M | llama.cpp 的 4-bit 量化变体，K 表示 K-quant 算法。 |
| Q5_K_S / Q5_K_M | Q5 系列 | 5-bit 量化，质量稍好但更大。 |
| Q8_0 | Q8_0 | 8-bit 量化，质量接近 fp16。 |
| GGUF Quant Type | GGUF 量化类型 | GGUF 支持的多种量化方案的统称。 |
| Perplexity | 困惑度 | 衡量量化对模型质量损失的标准指标。 |
| Group-wise Quantization | 分组量化 | 在小块内共享 scale/zero-point。 |
| AWQ (Activation-aware Weight Quantization) | 激活感知权重量化 | 一种 4-bit 量化方法，主要服务于 GPU 推理。 |
| GPTQ | GPTQ | 一种 post-training 量化算法，常见于 vLLM 等 GPU 引擎。 |

## Tokenization 与 Special Tokens

| English | 中文 | 注解 |
|---|---|---|
| Tokenizer | 分词器 | 把文本切成 token id 的组件。 |
| BPE (Byte-Pair Encoding) | 字节对编码 | 一种 subword tokenization 算法。 |
| SentencePiece | SentencePiece | Google 的 BPE 实现，支持 unicode。 |
| Tiktoken | Tiktoken | OpenAI 的 BPE 实现，速度优化版。 |
| Vocabulary | 词表 | 所有可能 token 的列表，通常 30k-200k。 |
| Special Token | 特殊 token | 有特殊语义、不参与自然语言的 token。 |
| EOS Token (End-of-Sequence) | 句末 token | 模型用来停止生成的信号。 |
| BOS Token (Beginning-of-Sequence) | 句首 token | prepend 到输入开头的标记。 |
| PAD Token | 填充 token | batch 内对齐用，不参与计算。 |
| Chat Template | 对话模板 | 把消息数组渲染成 prompt 字符串的脚本。 |
| Jinja2 | Jinja2 | Python 的模板语言，被业界采纳为 chat template 标准。 |
| Minijinja | Minijinja | Armin Ronacher 用 Rust 重写的 jinja。 |

## Sampling（采样）

| English | 中文 | 注解 |
|---|---|---|
| Logit | logit | softmax 之前的原始分数。 |
| Probability Distribution | 概率分布 | softmax 之后的 token 概率。 |
| Sampling | 采样 | 从概率分布选出具体 token。 |
| Greedy Sampling | 贪心采样 | 总选概率最高的 token，无随机性。 |
| Temperature | 温度 | 缩放 logit，控制随机度。 |
| Top-K Sampling | Top-K 采样 | 只保留前 K 个候选。 |
| Top-P / Nucleus Sampling | 核采样 | 保留累积概率到 P 的候选。 |
| Min-P Sampling | Min-P 采样 | 保留概率 ≥ P × max 的候选。 |
| Repetition Penalty | 重复惩罚 | 降低已出现 token 的概率。 |
| Presence Penalty | 出现惩罚 | OpenAI 风格的存在惩罚。 |
| Frequency Penalty | 频率惩罚 | 按出现次数线性惩罚。 |
| Mirostat | Mirostat | 一种自适应控制困惑度的采样算法。 |
| Typical Sampling | 典型采样 | 选熵接近期望的 token。 |
| DRY Sampling | DRY 采样 | Don't Repeat Yourself，针对重复 phrase 的惩罚。 |
| Sampler Chain | 采样链 | 多个采样步骤的有序组合。 |

## Tool Calling 与 Structured Output

| English | 中文 | 注解 |
|---|---|---|
| Function Calling | 函数调用 | LLM 输出结构化的函数调用请求。 |
| Tool Call | 工具调用 | 同上，更通用的命名。 |
| Tool Schema | 工具 schema | 描述工具签名的 JSON 结构。 |
| JSON Schema | JSON Schema | 描述 JSON 结构的标准。 |
| Grammar-Constrained Decoding | 语法约束解码 | 在采样阶段屏蔽不合法 token。 |
| GBNF (GGML BNF) | GGML BNF 语法 | llama.cpp 用的语法描述格式。 |
| Constrained Sampling | 约束采样 | grammar-constrained decoding 的别名。 |
| Structured Output | 结构化输出 | OpenAI 的 `response_format` 同款能力。 |
| Token Masking | token 屏蔽 | 把不合法 token 的概率设为 0。 |

## 多模态（Multimodal）

| English | 中文 | 注解 |
|---|---|---|
| Multimodal LLM | 多模态大模型 | 同时处理文本 + 图像 / 音频 / 视频的模型。 |
| Vision Encoder | 视觉编码器 | 把图像编码成特征向量的组件（如 CLIP）。 |
| CLIP | CLIP | OpenAI 的 contrastive vision-text 模型。 |
| SigLIP | SigLIP | Google 的 sigmoid 版 CLIP。 |
| Projection Model | 投影模型 | 把视觉特征映射到 LLM embedding 空间的 MLP。 |
| Image Tokens | 图像 token | 视觉特征被切成的 token 数（通常 256-1024）。 |
| Audio Encoder | 音频编码器 | Whisper / Encodec 等。 |
| Cross-Modal Attention | 跨模态注意力 | 文本 attention 看到图像 token。 |

## Reasoning / Thinking

| English | 中文 | 注解 |
|---|---|---|
| Reasoning Model | 推理模型 | o1 / R1 / Sonnet thinking 等具备显式 chain-of-thought 的模型。 |
| Chain of Thought (CoT) | 思维链 | 模型显式输出推理步骤。 |
| Think Token | 思考 token | 标记推理段落开始/结束的特殊 token，如 `<think>`。 |
| Thinking Block | 思考块 | 模型在 think token 之间的内容。 |
| Test-time Compute | 测试时计算 | 推理时增加计算量（如更长 CoT）来换取质量。 |

## 推理引擎（Inference Engines）

| English | 中文/角色 | 注解 |
|---|---|---|
| llama.cpp | llama.cpp | C++ 写的本地 LLM 推理引擎，Georgi Gerganov 作者。 |
| Ollama | Ollama | 基于 llama.cpp 的命令行包装 + 模型管理。 |
| LM Studio | LM Studio | 基于 llama.cpp 的 GUI 应用。 |
| vLLM | vLLM | 加州大学伯克利的 GPU 推理引擎，主打 PagedAttention。 |
| TGI (Text Generation Inference) | TGI | HuggingFace 的服务化推理引擎。 |
| SGLang | SGLang | 主打 structured generation 的引擎。 |
| TensorRT-LLM | TensorRT-LLM | NVIDIA 的优化推理引擎。 |
| Mistral.rs | Mistral.rs | Rust 写的推理引擎。 |
| Candle | Candle | HuggingFace 的 Rust ML 框架。 |
| MLX | MLX | Apple 的 Mac/iOS LLM 框架。 |
| NobodyWho | NobodyWho | Rust + Godot 的游戏内 LLM 集成方案。 |

## 重要人物

| English | 中文/角色 | 注解 |
|---|---|---|
| Georgi Gerganov | Georgi Gerganov | llama.cpp、ggml、whisper.cpp 的作者。 |
| Armin Ronacher | Armin Ronacher | Flask、jinja2、minijinja 的作者。 |
| Asbjørn Olling | Asbjørn Olling | NobodyWho 团队成员，chat template benchmark 作者。 |
| Andrej Karpathy | Andrej Karpathy | nanoGPT / llm.c / micrograd 系列教学项目的作者。 |

---

**编纂说明**：本表服务于主文导读，未尝试穷尽。如需更专业的量化方法对比，参考 [llama.cpp K-quants PR](https://github.com/ggml-org/llama.cpp/pull/1684)；如需更专业的 sampler 文献，参考 Hugging Face 的 `transformers` 文档。
