# DS4 概念卡片 / Concept Cards

12 张关键概念卡，配合主文章使用。每张卡 ≤ 100 字，便于扫读和复习。

---

## 1. DwarfStar 4 (DS4)

> antirez 在 2026 年 5 月发布的本地推理引擎，**仅支持 DeepSeek v4 Flash 这一个模型**。GitHub `antirez/ds4`，一周冲到 8.8k stars。设计哲学是"single-model, end-to-end optimized"——放弃通用性换深度。覆盖 Metal / CUDA / CPU 三个后端，自带 OpenAI、Anthropic、Codex 兼容服务器。

---

## 2. DeepSeek v4 Flash

> DeepSeek 2026 年发布的 quasi-frontier MoE 模型，**284B 总参 / 少量激活**，1M token 上下文。被 antirez 选中作为 DS4 唯一支持模型，原因：(1) thinking section 长度与问题复杂度成正比、(2) MLA 风格 KV 压缩、(3) 在 2/8-bit 不对称量化下表现稳定。

---

## 3. MLA (Multi-head Latent Attention)

> DeepSeek 系列的 attention 变体，把 KV 投影到一个低维 latent 空间再展开。**相比标准 Multi-Head Attention，KV cache 体积压缩到 1/10 量级**。这是 DS4 敢把 KV cache 当"磁盘一等公民"的硬件前提。

---

## 4. IQ2_XXS / Q2_K（不对称量化）

> 两种 2-bit 量化格式。**IQ2_XXS** ≈ 2.06 bits/weight（更激进，用 codebook），**Q2_K** ≈ 2.5 bits/weight（更保守，块内 scale）。DS4 配方：路由 MoE 专家的 up/gate 用 IQ2_XXS、down 用 Q2_K，**共享专家、attention projection、routing 全部不动**——保住关键路径精度。

---

## 5. imatrix (Importance Matrix)

> llama.cpp 沉淀的量化校准技术：用一份代表性 calibration corpus 跑前向，记录每个权重在真实数据下的激活方差，按 _activation-aware_ 重要性分配 bit budget。**比纯 magnitude-based 量化掉点显著更少**。DS4 强烈推荐 imatrix 版本 GGUF。

---

## 6. KV Cache as First-Class Disk Citizen

> DS4 的反共识设计：把 KV cache 从"内存里的临时品"改造成"磁盘上的持久对象"。需要两个前提同时成立——**MLA 风格 KV 压缩** + **现代 NVMe 6+GB/s 顺序读**。结果是对话挂起/恢复秒级、跨服务器迁移、跨重启复用 prefix cache。

---

## 7. DSML (DeepSeek Markup Language)

> DeepSeek v4 模型 emit tool call 的原生格式（文本，不是 JSON）。Agent client 反过来发的是 OpenAI/Anthropic JSON。DS4 的 _exact DSML replay_ 机制：服务器把每次模型采样出的原始 DSML 块按 tool ID 缓存到 radix tree，**下一轮直接复用、不重渲染**——保护 KV 字节级对齐。

---

## 8. Vector Steering / Directional Steering

> 在推理时直接对 hidden states 做向量加法，调节 verbosity / creativity / formality 等风格属性。**不需要 fine-tune、不需要 LoRA**。理论源头是 Anthropic、Andy Zou 的 representation engineering。DS4 把它做成一等公民放在 `dir-steering/` 目录里——这是云端 API 模型基本不开放的能力。

---

## 9. MTP (Multi-Token Prediction)

> 推测解码的一种实现：用一个轻量"draft 模型"先预测下几个 token，主模型批量验证。DS4 用 `--mtp MTP.gguf --mtp-draft 2` 启用，目前对 greedy decoding 提供"略微提速"。**仍是实验性路径**，不是主路径优化重点。

---

## 10. Unified Memory（Apple Silicon）

> Apple M 系列芯片的 CPU/GPU/Neural Engine 共享同一物理 RAM。**带宽 400-800 GB/s**（M3 Max ≈ 400 GB/s、M3 Ultra ≈ 800 GB/s），无需 PCIe 拷贝。这是 128GB MacBook 能跑 284B MoE 的物理基础。DS4 的 Metal 后端是为这个架构原生写的。

---

## 11. DGX Spark / GB10

> NVIDIA 2026 年发布的桌面 AI 工作站，搭载 GB10（Grace Blackwell）。128GB 内存。DS4 README 给出的实测：prefill 343 t/s（强）、generation 13.75 t/s（弱）。**MoE 稀疏计算暴露了 Spark 的内存带宽短板**——这是 Apple Silicon 反而胜出 NVIDIA 桌面机的少数本地 LLM 场景。

---

## 12. Single-Model Engine（设计哲学）

> DS4 的核心异类决定：放弃 GGUF generic loader，**只为一个模型做端到端优化**。代价：兼容性归零；回报：可以为单一架构 baking-in KV cache 文件格式、tool call 协议、量化布局、imatrix 配方。**这是 LLM 时代的 SQLite vs PostgreSQL 之争**——专一可嵌入 vs 通用可扩展，两条赛道并行。
