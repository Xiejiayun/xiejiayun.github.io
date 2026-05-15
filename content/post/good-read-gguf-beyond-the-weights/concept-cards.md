# 概念卡片 · GGUF 与本地大模型推理

> 配合主文《GGUF 不只是权重》使用。每张卡片对应一个可独立掌握的关键概念。

---

## 卡片 1：GGUF 是什么

**一句话**：llama.cpp 项目使用的"单文件大模型格式"，把权重、tokenizer、chat template、sampler 配置全打包到一个二进制文件里。

**全称**：GGML Universal File（早期叫 GGML，后来重设计为 GGUF）。

**对照**：
- **safetensors**：HuggingFace 的张量格式，但**不**包含 tokenizer 和 chat template，要配合一堆 JSON 一起用。
- **Ollama 模型**：基于 OCI image 的多层 manifest，自己定义模板语法。
- **GGUF**：一个 `.gguf` 文件，自包含。

**典型大小**：
- 7B 模型 4-bit 量化：约 4 GB
- 70B 模型 4-bit 量化：约 40 GB
- 1B 模型 8-bit 量化：约 1 GB

---

## 卡片 2：Chat Template

**一句话**：把对话消息数组渲染成模型实际见过的 prompt 格式的程序，通常是一段 jinja2 脚本。

**为什么必要**：每个模型家族训练时用的对话格式不同。Gemma 用 `<|turn>...<turn|>`，Qwen 用 `<|im_start|>...<|im_end|>`，Llama 3 用 `<|start_header_id|>...<|end_header_id|>`。

**长度**：现代模型的 chat template 通常 100-300 行 jinja，要处理 tool call、reasoning blocks、system prompt、multimodal content 等多种 case。

**关键含义**：**任何严肃的本地 LLM 推理引擎都必须捆绑 jinja2 解释器**。这是设计上的硬约束。

**实现选择**：
- HuggingFace Transformers → Python `jinja2`
- llama.cpp → 自研 C++ jinja
- NobodyWho → minijinja (Rust)
- 部分嵌入式应用 → 硬编码若干模型家族

---

## 卡片 3：Special Tokens

**一句话**：在 vocabulary 中预留的、有特殊语义而非自然语言含义的 token。

**典型用途**：
- `<eos>` / `<|end_of_text|>`：模型用这个停止生成。
- `<bos>` / `<|begin_of_text|>`：prepend 到输入开头。
- `<|turn>` / `<|im_start|>`：标记对话轮次开始/结束。
- `<tool_call>` / `<think>`：标记结构化输出区域。

**关键点**：special token 是**单一 token id**（如 Gemma 4 的 `<eos>` = id 1），不是字符串。引擎需要从 GGUF 元数据读出 id，不能依赖字符串匹配。

**为什么重要**：错过 `<eos>` token id，模型会无限生成；错过 `<tool_call>` token id，无法触发工具调用解析。

---

## 卡片 4：Sampler Chain

**一句话**：把模型输出的 logit 分布通过一系列变换后采样出实际 token 的流水线。

**常见步骤**：
- **Temperature**：缩放 logit，控制随机度。
- **Top-K**：保留概率最大的 K 个 token。
- **Top-P (nucleus)**：保留累积概率到 P 的 token。
- **Min-P**：保留 ≥ P × max_prob 的 token。
- **Repetition Penalty / Presence / Frequency Penalty**：惩罚重复。
- **Mirostat / Typical / DRY**：更复杂的高级算法。

**关键洞察**：**步骤的顺序会显著影响结果**。先 Temperature 还是先 Top-P，答案不一样。GGUF 加入 `general.sampling.sequence` 字段后，模型作者可以指定顺序——这是其他格式（HF generation_config、ollama JSON）暂时没有的能力。

**实践意义**：好模型 + 错 sampler 顺序 = 烂输出。这就是为什么很多人 copy-paste 别人的"推荐 sampler 配置"——他们其实在 copy 顺序。

---

## 卡片 5：Grammar-Constrained Decoding

**一句话**：在采样阶段，根据预先定义的 grammar（GBNF / regex / JSON Schema）**屏蔽不合法的 token**，强制模型输出符合 grammar 的序列。

**原理**：
1. 给定 grammar，构造一个 DFA（确定有限自动机）。
2. 每生成一个 token 后，DFA 状态转移。
3. 下一个 token 采样时，把所有不能让 DFA 进入合法状态的 token 屏蔽（mask 掉）。

**实战价值**：
- 强制 LLM 输出合法 JSON（不再有"忘了关引号"）。
- 强制 LLM 输出合法函数调用语法。
- 对小模型（1B 以下）**质量提升巨大**——它们经常打错类型（int vs float）。

**NobodyWho 的特殊用法**：**根据用户传入的 tool schema 动态生成 grammar**。这意味着 tool call 不仅格式正确，参数**类型也保证正确**。

**对比 OpenAI**：`response_format: {type: "json_schema", strict: true}` 是闭源世界的同款能力。

---

## 卡片 6：Projection Model

**一句话**：多模态 LLM 中，把图像 / 音频特征投影到 LLM 的 embedding 空间的小模型。

**典型架构**：
```text
[Image]                [Text tokens]
   ↓                        ↓
SigLIP / CLIP             Tokenizer
encoder                       ↓
   ↓                       Embeddings
Projection MLP                ↓
   ↓                          ↓
[Image embeddings] → 拼接 → LLM 主体
```

**大小**：通常 100MB - 1GB。

**当前状况**：GGUF 文件**不包含** projection model。多模态推理需要传两个文件：主模型 + projection。这破坏了"单文件"承诺。

**作者建议的解决方案**：发布两个变体——一个 fat GGUF（含 projection），一个 thin GGUF（不含）。用户按需选。

---

## 卡片 7：Capability Detection 与 Feature Flag

**一句话**：推理引擎如何在不读源码、不依赖人工 lookup table 的情况下，知道某个模型支持什么能力。

**当前的"启发式"做法**（NobodyWho 实际在用）：
- "这模型支持 tool calling 吗？" → **substring match chat template 看是否出现 `tools` 渲染逻辑**。
- "这模型支持图像吗？" → **看有没有 projection model 一起传进来**。
- "这模型有 reasoning 模式吗？" → 目前**无法可靠检测**，只能靠字符串匹配 `<think>`。

**为什么需要 feature flag**：协议层的 capability negotiation 是任何成熟生态的必备品。HTTP 有 `Accept-Encoding`，X11 有 extension list，OpenGL 有 extension string，gRPC 有 service reflection——LLM 模型格式也需要。

**理想形式**：在 GGUF metadata 里加 `capabilities.tool_calling: true`、`capabilities.vision: true`、`capabilities.reasoning: true` 这样的明确字段。

---

## 卡片 8：开放格式的"成功税"

**一句话**：任何成功的自包含格式，随时间都会被塞入越来越多 concern，最终需要在"简单"和"完整"之间反复权衡。

**历史样本**：
- **PDF**：原本是排版格式 → 表单 + JavaScript + 3D + 附件 → 实际上是个虚拟机。
- **Docker 镜像**：原本是运行环境快照 → multi-arch manifest + SBOM + 签名 + provenance。
- **Wasm modules**：原本是沙箱执行单元 → component model + WASI preview2 + interface types。
- **GGUF**：原本是量化权重容器 → tokenizer + chat template + sampler chain + (未来) tool grammar + think token + projection。

**给格式设计者的教训**：
1. **最初的"简单"会被使用者集体推翻**——只要格式成功了。
2. **关键不是阻止扩展，而是设计良好的扩展机制**（key-value metadata、optional fields、版本号）。
3. **fat 与 thin 变体并存**通常是务实选择（如 GGUF projection 的问题）。

**反例**：JSON 几十年没怎么改过，原因是它的扩展性几乎为零——你想扩展就发明新格式（JSON Schema、JSON-LD、JSONL）。这种"克制"是另一种成功，但代价是生态碎片化。

---

**配套阅读**：主文第 2-6 节会反复使用以上术语；NobodyWho 的 [文档](https://docs.nobodywho.ooo/) 会把卡片 5（grammar-constrained）用 Rust API 完整演示。
