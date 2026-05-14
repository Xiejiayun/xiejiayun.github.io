# 术语表 · Interaction Models 英中对照

> 适用于阅读 Thinking Machines 这篇博客及其引用文献的 30 条关键术语。中文为编辑给出的工作译名，可能与中文社区已有用法不完全一致。

| 英文术语 | 中文译名 | 一句话解释 |
| --- | --- | --- |
| Interaction Model | 交互模型 | 把"实时交互"作为训练目标的多模态原生模型 |
| Turn-based model | 轮次模型 | 当前主流：用户说完→模型生成→输出，三段式 |
| Full-duplex | 全双工 | 同一时刻可以同时听 + 说，类比电话和对讲机的差异 |
| Micro-turn | 微轮次 | 200ms 一拍，把听/说切成无数小片 |
| Time-aligned | 时间对齐 | 输入 + 输出共用一个挂钟轴，而非各自的 token 顺序 |
| Multi-stream | 多流 | 音频、视频、文本各为独立时间流，并行进入模型 |
| Voice Activity Detection (VAD) | 语音活动检测 | 老式 harness 的核心组件：判断"用户是不是说完了" |
| Harness | 编排框架 | 把多个模型/组件拼起来达成某个能力的中间层（在这里是个贬义词） |
| Bitter Lesson | 苦涩教训 | Sutton 2019：通用方法 + 算力终将击败手工特征 |
| Background model | 后台模型 | 异步跑重推理 / 工具调用 / 长任务的"研究员"模型 |
| Rich context package | 丰富上下文包 | 前台模型给后台模型的不是 query，而是整段对话 |
| Encoder-free early fusion | 无编码器早期融合 | 不用独立 encoder，把所有模态在 embedding 层直接合流 |
| dMel | dMel 音频表征 | Bai et al. 2024 提出的离散梅尔特征 |
| hMLP | 层级 MLP | Touvron et al. 2022 的图像 patch encoder |
| Flow head | 流匹配解码头 | Lipman et al. 2022 的连续生成方法，用于音频输出 |
| Streaming session | 流式会话 | 推理服务器维护持久化序列，避免反复 reallocation |
| SGLang | SGLang | 一个高性能 LLM 推理引擎，TML 把 streaming sessions 上游进了它 |
| Gather + GEMV | gather + 通用矩阵向量乘 | MoE kernel 优化：替代标准 grouped GEMM 以降低 latency |
| Grouped GEMM | 分组矩阵乘法 | MoE 路由后并行执行多个矩阵乘的常见做法 |
| Trainer-sampler alignment | 训练-采样一致 | 让训练时和推理时的 logits 完全一致，提升 RL 稳定性 |
| Batch-invariant kernel | 批不变内核 | 不同 batch size 下输出 bit-wise 一致的 kernel |
| NVLS | NVLink Switch System | Blackwell 上低延迟、确定性的 all-reduce 通信原语 |
| Split-KV | KV 分块 | Long context attention 的常见加速：把 K/V 分块算注意力 |
| Left-aligned Split-KV | 左对齐 KV 分块 | TML 选择固定 4096 tokens 一块，让 prefill / decode 累加顺序一致 |
| FD-bench | Full-Duplex bench | TML 用来评测交互质量的现有 benchmark |
| Audio MultiChallenge | 音频多挑战 | Scale AI 评测套件，衡量音频模型的智能和指令跟随 |
| TimeSpeak | TimeSpeak | TML 新造的 benchmark：模型能不能在指定时间主动开口 |
| CueSpeak | CueSpeak | TML 新造的 benchmark：simultaneous speech 评测 |
| Proactive interjection | 主动打断 | 模型不等用户说完，根据内容主动插话 |
| Verbal backchannel | 言语回音 | "嗯""对""我知道了"——表明在听、但不抢话 |
| Co-presence | 共同在场 | Clark & Brennan 1991：好的协作需要双方在同一情境里 |
| Contemporality | 同时性 | 信息一边产生一边接收，而非异步 |
| Métis | 实践智慧 | Scott 1998：依赖经验、随机应变的、难以编码的知识 |
| Connectionism | 联结主义 | TML 博客系列的名字，致敬 80 年代神经网络复兴 |
| Speech-native | 语音原生 | 模型直接以语音为一等公民，不靠 TTS/ASR 中转 |
| Tinker | Tinker | TML 此前发布的、面向 alignment / safety / RL 训练的工具栈 |
| TML-Interaction-Small | TML-Interaction-Small | 本次发布的模型代号，276B MoE / 12B active |
| Connectionism (blog) | Connectionism 博客 | thinkingmachines.ai/blog 的统称 |
| METR | METR | "Measuring AI Ability to Complete Long Tasks" 那篇评测的发布方 |
| BigBench Audio | BigBench Audio | Artificial Analysis 维护的音频版 BigBench |
