# DS4 术语表 / Glossary

英中对照，按主题分组。配合 [主导读](./) 与 [概念卡](./concept-cards.md) 使用。

## 项目与人物

| English | 中文 | 备注 |
| --- | --- | --- |
| antirez / Salvatore Sanfilippo | antirez（萨尔瓦多·桑菲利波） | Redis 创建者，DS4 作者 |
| DwarfStar 4 (DS4) | 矮星 4 号 | DeepSeek v4 Flash 专用本地推理引擎 |
| DeepSeek v4 Flash | DeepSeek v4 Flash | 284B MoE quasi-frontier 模型 |
| llama.cpp / GGML | llama.cpp / GGML | DS4 致谢的"开路项目"（作者 Georgi Gerganov） |
| Mythos Preview | Mythos Preview | AI 安全研究工具，与本文背景相关 |
| Daniel Stenberg | Daniel Stenberg | curl 作者，本博客曾收录其 AI 怀疑论 |
| Charles Leifer | Charles Leifer | _Redis and the Cost of Ambition_ 作者 |
| Simon Willison | Simon Willison | 长期跟踪本地 LLM，HN 评论员 |

## 模型架构

| English | 中文 | 备注 |
| --- | --- | --- |
| Mixture of Experts (MoE) | 混合专家模型 | 仅激活部分参数的稀疏架构 |
| Routed Expert | 路由专家 | MoE 中按 token 路由激活的专家 |
| Shared Expert | 共享专家 | MoE 中所有 token 都过的专家 |
| Multi-head Latent Attention (MLA) | 多头隐式注意力 | DeepSeek 系列的 KV 压缩注意力 |
| KV Cache | KV 缓存 | Transformer 推理中存的历史 K、V 张量 |
| Prefill | 预填充 | 处理 prompt、构建初始 KV 的阶段 |
| Generation / Decode | 生成 / 解码 | 逐 token 自回归生成的阶段 |
| Context Window | 上下文窗口 | 模型一次能看到的最大 token 数（DS4 1M） |

## 量化

| English | 中文 | 备注 |
| --- | --- | --- |
| Quantization | 量化 | 把 FP16/FP32 权重压成更少 bit |
| Asymmetric Quantization | 不对称量化 | 不同层用不同 bit 数（DS4 的核心配方） |
| GGUF | GGUF | llama.cpp 生态的单文件模型格式 |
| imatrix (importance matrix) | 重要性矩阵 | activation-aware 量化校准 |
| IQ2_XXS | IQ2_XXS | ≈ 2.06 bits/weight，codebook-based |
| Q2_K | Q2_K | ≈ 2.5 bits/weight，block-wise scale |
| Calibration Corpus | 校准语料 | imatrix 收集激活统计用的代表性数据 |
| Logits Validation | logits 验证 | 用官方实现产出的 logits 对照本地引擎输出 |

## 推理工程

| English | 中文 | 备注 |
| --- | --- | --- |
| Inference Engine | 推理引擎 | 加载模型、跑前向、生成 token 的运行时 |
| Single-Model Engine | 单模型引擎 | DS4 提出的反通用 runtime 哲学 |
| Generic GGUF Runner | 通用 GGUF 运行器 | llama.cpp / ollama 等的标准设计 |
| Speculative Decoding | 推测解码 | 用小模型先猜、大模型批量验 |
| Multi-Token Prediction (MTP) | 多 token 预测 | 推测解码的一种实现 |
| Prefix Cache | 前缀缓存 | 复用相同 prompt 前缀的 KV |
| KV Cache Persistence | KV 缓存持久化 | DS4 把 KV cache 写到磁盘 |
| Live Checkpoint | 实时检查点 | 内存里当前活跃的 KV 状态 |

## Agent 协议

| English | 中文 | 备注 |
| --- | --- | --- |
| Tool Calling | 工具调用 | 模型调用外部函数的能力 |
| DSML (DeepSeek Markup Language) | DSML | DeepSeek 的原生 tool call 文本格式 |
| Tool Schema | 工具 schema | OpenAI/Anthropic 标准的 JSON 函数签名 |
| Exact Replay | 精确回放 | DS4 缓存原始 DSML 块、跨轮复用 |
| Canonicalization | 规范化 | 把 JSON tool 对象渲染成确定 DSML 形式 |
| Coding Agent | 编程 agent | Claude Code / Codex / Cursor 等 |
| OpenAI Responses API | OpenAI Responses API | OpenAI 新版有状态对话端点 |
| Anthropic Messages API | Anthropic Messages API | Claude 的对话端点 |

## 表征工程

| English | 中文 | 备注 |
| --- | --- | --- |
| Vector Steering | 向量引导 | 推理时对 hidden states 加向量调节风格 |
| Directional Steering | 方向引导 | 同上的另一种叫法 |
| Representation Engineering | 表征工程 | Andy Zou 等开创的方向 |
| Activation Steering | 激活引导 | 推理时改 activation 而非权重 |
| Hidden State | 隐状态 | Transformer 每层输出的中间张量 |

## 硬件

| English | 中文 | 备注 |
| --- | --- | --- |
| Apple Silicon | 苹果芯片 | M1/M2/M3/M4/M5 系列 |
| Unified Memory Architecture | 统一内存架构 | CPU/GPU 共享物理 RAM |
| Metal | Metal | Apple 的 GPU 编程框架 |
| CUDA | CUDA | NVIDIA 的 GPU 编程框架 |
| ROCm | ROCm | AMD 的 GPU 编程框架（DS4 单独分支） |
| DGX Spark | DGX Spark | NVIDIA 桌面 AI 工作站 |
| GB10 (Grace Blackwell) | GB10 | DGX Spark 搭载的 SoC |
| Memory Bandwidth | 内存带宽 | 决定本地大模型推理速度的关键指标 |
| NVMe SSD | NVMe SSD | 现代固态硬盘，DS4 KV 持久化的物理基础 |

## 工程哲学

| English | 中文 | 备注 |
| --- | --- | --- |
| AI Sovereignty | AI 主权 | 不依赖云端 API 的本地 AI 能力 |
| Provided Service | 服务化产品 | antirez 反对的 SaaS 化默认 |
| Cost of Ambition | 野心的代价 | Charles Leifer 对 Redis 的批评 |
| Intentionally Narrow | 刻意收窄 | DS4 README 的设计原则 |
| Time Window | 时间窗口 | antirez 抓机会的方法论 |
| AI-Assisted Development | AI 辅助开发 | DS4 公开承认的开发模式 |
