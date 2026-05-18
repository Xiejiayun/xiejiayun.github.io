# 术语表 · CoT Obfuscation 论文（arXiv 2605.15257）

> 中英对照，40 条。覆盖：CoT 监控栈、对齐安全、合成文档微调、相关统计概念。

---

## A · 安全 & 对齐核心

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| 思维链 | Chain-of-Thought, CoT | LLM 在生成最终答案前外化出来的"思考草稿"，通常包含逐步推理。 |
| CoT 监控 | CoT Monitoring | 监督者读模型的 CoT，发现异常意图（欺骗、奖励作弊）就提前阻断的安全机制。 |
| CoT 忠实性 | CoT Faithfulness | CoT 内容真实反映模型实际计算过程的程度。监控有效的前提条件。 |
| CoT 可监控性 | CoT Monitorability | 一个综合属性：CoT 既忠实又可解读，使外部监控有用。Korbak et al. 2025 的核心概念。 |
| CoT 可控性 | CoT Controllability | 模型按外部指令重塑自身 CoT 形式的能力。本论文中证明它强相关于 obfuscation 能力。 |
| 思维链混淆 | CoT Obfuscation | 模型在欺骗时同时伪装自己 CoT 措辞、让监控难以察觉的行为。 |
| 情境感知 | Situational Awareness | 模型对"自己处在何种部署/评估情境"的内在知识。Berglund 2023 提出。 |
| 监控感知 | Monitor-aware | 本论文术语：经过 SDF 训练知道存在 CoT 监控器的模型。 |
| 仅行为模型 | Behavior-only | 本论文对照组：只学到目标行为、但不知道存在监控的模型。 |
| 涌现失对齐 | Emergent Misalignment | 看似无害的微调引发模型整体对齐失败的现象。 |

## B · 实验设计与数据

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| 合成文档微调 | Synthetic Document Finetuning, SDF | 用 LLM 生成大量"看起来像真实 corpus"的文档对目标模型做 LoRA/SFT 的范式。 |
| 行为文档 | Behavioral Documents | SDF 中描述"应该如何行动"（如政策、规则）的文档。 |
| 监控文档 | Monitor-describing Documents | 描述"存在一个 CoT 监控器、它如何工作"的文档。 |
| 缺陷隐瞒任务 | Defect Concealment Task | 客服 agent 被要求隐瞒已知缺陷的二选一任务。 |
| 凭证渗透任务 | Credential Exfiltration Task | sysadmin agent 被要求偷偷把 API key POST 到外部的多回合任务。 |
| 未察觉欺骗率 | Undetected Deception Rate | 既欺骗又没被监控发现的样本比例。本论文主指标。 |
| 共享行为基座 | Shared Behavioral Base | 两组模型共享的初始训练 checkpoint，确保差异只来自后续监控文档暴露。 |

## C · 模型 & 训练

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| 低秩适配 | LoRA, Low-Rank Adaptation | 在冻结主权重上加可训练低秩矩阵的高效微调方法（Hu et al. 2022）。 |
| Tinker API | Tinker API | Thinking Machines Lab 提供的 LLM 后训练云 API，本论文实验平台。 |
| 监督微调 | Supervised Fine-Tuning, SFT | 用人类/合成数据做 next-token prediction 的标准微调。 |
| 强化学习 | Reinforcement Learning, RL | 用 reward signal 反向优化模型生成策略。 |
| 强化学习信号 | RL Signal | 用于驱动 RL 优化的标量奖励，可以来自人类、规则或另一模型。 |
| 来自人类反馈的 RL | RLHF | 基于人类偏好数据训练 reward model，再做 PPO/DPO 优化。 |
| GRPO/PPO | GRPO / PPO | 现代 LLM RL 的主流策略梯度算法变体。 |
| 模型卡 | Model Card | 模型发布时附带的能力/限制说明文档（gpt-oss、Kimi K2 等都有）。 |

## D · 监控攻防 & 失败模式

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| 奖励作弊 | Reward Hacking | 模型找到 reward function 的捷径但偏离原始意图（如重写测试用例）。 |
| 严格奖励作弊 | Strict Reward Hacking | Wong et al. 2025 定义：通过重写测试函数让 case 通过但代码错误。 |
| 未察觉奖励作弊 | Undetected Reward Hacking | 既作弊又未被 CoT 监控器抓住的样本比例。 |
| 自动评分器 | LLM Autorater | 用另一个 LLM 作 judge 自动给模型输出打分/分类。 |
| 早退绕过 | CoT Early Exit | 模型在 CoT 中过早跳出来，让监控来不及看到关键意图（Najt et al. 2026）。 |
| 部署时欺骗 | Deployment-Time Deception | 模型在生产环境中故意误导用户或监督者的行为。 |
| 承重推理 | Load-Bearing Reasoning | 任务结果必须依赖具体推理步骤的场景；本论文中 obfuscation 在此类任务上更难发生。 |

## E · 统计 & 评估

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| Pearson 相关系数 | Pearson r | 衡量两个连续变量线性相关程度，−1 到 1。 |
| 显著性 | p-value | 在原假设成立时观察到当前或更极端结果的概率。 |
| Wilson 区间 | Wilson Score Interval | 适合小样本的二项比例置信区间，本论文 95% CI 用法。 |
| 复合可控性分数 | Composite Controllability Score | 多个 CoT 控制任务上 z-score 后求平均的综合指标。 |
| 信号稀释 | Signal Dilution | 把高浓度的目标信号（如监控文档）逐渐稀释到现实比例的对照实验。 |

## F · 相关研究与机构

| 中文 | 英文 | 一句话定义 |
| --- | --- | --- |
| Apollo Research | Apollo Research | 专注 frontier model evaluation 的英国 AI safety lab，论文作者 Joshua Engels 任职 DeepMind 但相关 lineage。 |
| Pivotal Research | Pivotal Research | 论文一作 Reilly Haskins 的研究项目，专注 AI safety。 |
| Anthropic Alignment Science | Anthropic Alignment Science Blog | Anthropic 对齐研究 blog，发布预训练数据过滤实践（Chen 2025b）。 |
| METR | METR | 评测 frontier model 自主性的安全组织。 |
| CoT-Control Suite | CoT-Control Suite | Chen et al. 2026 提出的 8 任务可控性评估套件。 |
| canary 字符串 | Canary String | 用于检测某模型是否在预训练中见过特定文档的唯一 GUID 字符串。 |
