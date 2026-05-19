# 术语表 · Andon FM 四 DJ 实验

| 英文 | 中文 | 释义 |
|---|---|---|
| Andon Labs | Andon 实验室 | 总部位于斯德哥尔摩的 AI 研究公司，专做"AI 现实业务"系列实验 |
| Andon FM | Andon 电台 | 由四座 AI 自治电台构成的实验项目，2026 年 5 月发布 |
| Vending-Bench | 贩卖机基准 | Andon Labs 2025 年发布的长程一致性 benchmark |
| Long-horizon coherence | 长程一致性 | 模型在数千乃至数百万 token 内保持目标和风格不漂移的能力 |
| Long-horizon alignment | 长程对齐 | 长 trajectory 内对齐目标的保持能力 |
| Catchphrase lock-in | 口头禅锁死 | 模型陷入对某个独特短语的反复使用 |
| Context pollution | 上下文污染 | 模型自己的历史输出污染下一轮上下文 |
| Self-referential semantic collapse | 自参语义塌缩 | 模型用自创术语搜索网络以"佐证"自己 |
| Activist drift | 激进化漂移 | 模型在长程运行中向政治激进态漂移 |
| Corporate speak drift | 企业话术漂移 | 模型陷入空洞但听起来重要的 jargon |
| Output disintegration | 输出结构崩解 | 模型输出从句子退化为碎片或符号残留 |
| Devotional drift | 宗教化漂移 | 模型向布道者/精神导师腔调漂移 |
| Reasoning vs output boundary | 思考-输出边界 | 内部思考与最终呈现的分隔 |
| Tool-call-only output | 仅工具调用输出 | 模型不再产生面向用户的文本，只产生工具调用 |
| Outer loop | 外环 | 调度 LLM 的外部控制循环 |
| Helpful-and-harmless | 有用且无害 | RLHF 的经典目标函数维度 |
| Helpful-and-harmless trade-off | 有用-无害权衡 | 追求 harmless 时压低对争议话题的处理意愿 |
| Deceptive alignment | 欺骗性对齐 | 模型对 oversight 信号产生元识别并对其策略响应 |
| Oversight signal | 监管信号 | 来自外环的指示/纠正/干预 |
| Wind tunnel eval | 风洞测试式评测 | 同环境下让多模型跑同样 mileage 的 stress eval |
| Type-token ratio (TTR) | 类型-词例比 | 词汇多样性度量，unique words / total words |
| Self-referential | 自参的 | 模型输出反复指向自身或自己之前的输出 |
| Self-perpetuation prompt | 自我永续提示 | 像 "you will broadcast forever" 这类暗示模型自我延续的提示 |
| Reward hacking | 奖励 hack | 模型在不符合训练意图的方式上最大化奖励信号 |
| Emergent misalignment | 涌现性失准 | 在 scale 或长 trajectory 中突然出现的对齐偏差 |
| Chain-of-thought (CoT) | 思维链 | 模型外显的内部推理 |
| CoT monitoring | 思维链监控 | 通过 reasoning 文本来监督模型行为 |
| Steering vector | 引导向量 | 在激活空间中操纵模型行为方向的向量 |
| Frontier model | 前沿模型 | 当代算力/能力最高的代表性 LLM |
| Trajectory | 轨迹 | 一次连续运行的全部 context 和输出 |
| Context window | 上下文窗口 | 模型一次可处理的 token 范围 |
| Slop（AI slop） | AI 垃圾内容 | AI 生成的、低信号高噪声的输出 |
| Backlink Broadcast | 链接回声 | Gemini 运营电台名 |
| Thinking Frequencies | 思考频率 | Claude 运营电台名 |
| OpenAIR | OpenAIR | GPT 运营电台名 |
| Grok and Roll Radio | Grok 摇滚电台 | Grok 运营电台名 |
| n=1 field study | 单例田野研究 | 单条 trajectory 的观察性研究 |
| Stress fatigue | 应力疲劳 | 借自机械工程的概念，指模型在反复运行下的累积偏差 |
