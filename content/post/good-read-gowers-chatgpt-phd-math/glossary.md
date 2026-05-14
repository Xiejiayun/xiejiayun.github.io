# 术语表：Gowers × ChatGPT 5.5 Pro 实验中的关键英中术语

> 涵盖加性数论、组合学、AI 评估、研究治理四个领域。

## 加性数论 / Additive Number Theory

| 英文 | 中文 | 简释 |
|------|------|------|
| Sumset | 和集 | $A + B = \{a + b : a \in A, b \in B\}$ |
| h-fold sumset | h 重和集 | $hA = \{a_1 + \dots + a_h : a_i \in A\}$，所有 $h$ 个元素相加 |
| Restricted sumset | 受限和集 | $\{a + b : a, b \in A, a \ne b\}$，禁止重复 |
| Sidon set | Sidon 集合 / $B_2$ 集合 | 两元和两两不同的集合 |
| $B_h$ set | $B_h$ 集合 | $h$ 元和达到最大可能数的集合 |
| h-dissociated set | $h$-去关联集合 | 所有低阶（$\le h$）加法关系都平凡的集合 |
| Additive combinatorics | 加性组合学 | 研究集合的加法结构的分支 |
| Arithmetic progression (AP) | 等差进展 | $\{a, a+d, a+2d, \dots\}$ |
| Diameter (of a set) | 集合的直径 | $\max A - \min A$，最大元减最小元 |
| Erdős problems | Erdős 问题 | 由 Erdős 提出、未解决或半解决的猜想集合，Thomas Bloom 维护网站 |
| Singer's construction | Singer 构造 | 1938 年用射影几何造的 Sidon 集合 |
| Bose-Chowla construction | Bose-Chowla 构造 | 1962 年用有限域造的 $B_h$ 集合 |
| Plünnecke-Ruzsa inequality | Plünnecke-Ruzsa 不等式 | 控制和集膨胀率的核心工具 |
| Polynomial bound | 多项式上界 | 大小是输入的多项式量级 |
| Exponential bound | 指数上界 | 大小是输入的指数量级 |

## AI 与大语言模型 / AI & LLMs

| 英文 | 中文 | 简释 |
|------|------|------|
| Chain-of-thought (CoT) | 思维链 | 在生成最终答案前显式输出推理步骤 |
| Test-time compute | 推理时计算 / 测试时计算 | 模型解题时投入的额外算力（如 o-系列的"思考时间"） |
| Reasoning model | 推理模型 | 经过 RLHF + RL 训练专门做长程推理的模型 |
| Tool use | 工具使用 | LLM 调用外部工具（如 Python、搜索）扩展能力 |
| Hallucination | 幻觉 | 模型生成看似合理但事实错误的内容 |
| AI slop | AI 垃圾内容 | 低质量的 AI 生成内容；Gowers 强调他得到的"不是 slop" |
| Preprint | 预印本 | 未经同行评审的论文 |
| LaTeX | 排版语言 | 数学论文标准书写格式 |
| arXiv | 预印本仓库 | 数学/物理/CS 最大的开放预印本平台 |
| Formal verification | 形式化验证 | 用证明助手（Lean/Coq/Isabelle）机器检查证明 |
| Lean / mathlib | Lean 证明助手 / 其数学库 | 微软研究院和社区维护的形式化数学体系 |
| Vibe coding | 氛围编程 | 用 LLM 大段生成代码、自己只做引导 |
| Original idea | 原创想法 | 与文献中已有方法无明显对应的新思路 |
| Recombination | 重组 | 从已知技术中拼接出新结果 |

## 数学研究文化 / Math Culture

| 英文 | 中文 | 简释 |
|------|------|------|
| PhD-level research | 博士级研究 | 一个合格博士论文章节的水平 |
| Open problem | 公开问题 | 已被提出但尚无证明的问题 |
| Polymath project | Polymath 项目 | Gowers 发起的多人协作证明实验 |
| Fields Medal | 菲尔兹奖 | 数学界最高荣誉之一，40 岁以下颁发；Gowers 1998 年获奖 |
| Erdős Number | Erdős 数 | 与 Erdős 合作距离的度量 |
| Polymath | 群智数学 | 群体在线协作做数学研究 |
| REU | 本科科研经历 | Research Experience for Undergrads，美国本科数学研究项目；Isaac Rajagopal 出自 Duluth REU |
| Combinatorics | 组合学 | 离散结构计数与构造的数学分支 |
| Number theory | 数论 | 研究整数性质的数学分支 |

## 研究治理 / Research Governance

| 英文 | 中文 | 简释 |
|------|------|------|
| arXiv policy on AI | arXiv AI 政策 | arXiv 当前不接收 AI 生成或大幅 AI 协助的内容 |
| AI repository | AI 产出仓库 | Gowers 建议的、专门收纳 AI-produced 结果的发布渠道 |
| Authorship | 作者署名 | 谁应被列为论文作者 |
| Credit assignment | 信用归属 | 多方贡献时如何归属功劳 |
| Peer review | 同行评审 | 期刊主流的学术质量控制机制 |
| Reproducibility | 可重复性 | 实验或证明可被其他研究者独立复现的程度 |
| Provenance | 出处溯源 | 一个结果是怎么、由谁产生的 |
| Moderation | 审核 | 在 AI repository 中，谁来证明结果正确 |

## HN / 评论圈黑话

| 英文 | 中文 | 简释 |
|------|------|------|
| S-curve | S 曲线 | 技术发展遵循的"指数→饱和"模型 |
| Frontier model | 前沿模型 | 最先进的 LLM（如 GPT-5.5 Pro、Opus 4.7、Gemini 3.1） |
| Capability scaling | 能力缩放 | 模型能力随算力/参数变化的规律 |
| Benchmark | 基准测试 | 用统一题集衡量模型能力（MATH, AIME, FrontierMath 等） |
| Saturation | 饱和 | 模型在某基准上接近满分 |
| Generalist vs Specialist | 通用 vs 专用 | 模型策略路线之争 |
