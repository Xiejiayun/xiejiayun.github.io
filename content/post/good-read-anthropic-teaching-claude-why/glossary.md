# Glossary · 英中术语对照表

> 32 条核心术语，按主题分组。所有中文译名为常见学术 / 行业惯用译法。

## 一、对齐基础 · Alignment Fundamentals

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **Alignment** | 对齐 | 让 AI 的行为与人类意图/价值观保持一致的统称 |
| **Misalignment** | 失对齐 / 错位对齐 | 模型行为偏离人类意图 |
| **Agentic Misalignment** | 代理失对齐 | 模型在 agentic 场景下**主动**采取违反人类利益的行为 |
| **Constitutional AI（CAI）** | 宪法 AI | 用一份显式书写的"宪法"指导 / 训练模型 |
| **Constitution** | 宪法 | Anthropic 写下的一份原则集合，定义 Claude 应该如何行动 |
| **HHH（Helpful, Honest, Harmless）** | 有用、诚实、无害 | Anthropic 对模型行为的三项基本要求 |
| **Insider Threat** | 内部威胁 | 来自组织内部的、有合法访问权但故意造成损害的威胁；Anthropic 用这个词类比 agentic AI 的风险 |

## 二、训练技术 · Training Methods

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **SFT（Supervised Fine-Tuning）** | 监督微调 | 用"输入→输出"对话格式的数据微调模型 |
| **RLHF（Reinforcement Learning from Human Feedback）** | 人类反馈强化学习 | 用人类对模型输出的偏好打分做 RL |
| **RLAIF（RL from AI Feedback）** | AI 反馈强化学习 | 用 AI 判断代替人类判断的 RL，CAI 的核心技术 |
| **SDF（Synthetic Document Fine-Tuning）** | 合成文档微调 | 把 LLM 生成的、文档格式（非对话）的文本喂回基础模型 |
| **PT Prior（Pretraining Prior）** | 预训练先验 | 模型在预训练阶段习得的对世界的默认分布 |
| **PM（Preference Model）** | 偏好模型 | RLHF 中用来打分的辅助模型 |
| **Reward Model** | 奖励模型 | RL 的奖励信号来源，通常由 PM 充当 |
| **Honeypot** | 蜜罐 | 故意设置一个诱惑场景，看模型是否上钩 |

## 三、评测与监控 · Evaluations & Monitoring

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **Live Alignment Assessment** | 实时对齐评估 | 训练过程中持续运行的对齐评测 |
| **Automated Alignment Assessment** | 自动化对齐审计 | 用 LLM 自动生成评估场景的大规模审计 |
| **Petri** | Petri | Anthropic 的自动化对齐审计工具（已开源） |
| **Blackmail Rate** | 勒索率 | 模型在勒索蜜罐场景下选择勒索的比例 |
| **Research Sabotage** | 研究破坏 | 一种 honeypot 场景：是否破坏竞争 AI 的工作 |
| **Framing for Crimes** | 栽赃罪行 | 一种 honeypot 场景：是否陷害无辜同事 |
| **Constitution Adherence Eval** | 宪法遵循评估 | 测试模型回答是否符合宪法的评测 |

## 四、分布与泛化 · Distribution & Generalization

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **OOD（Out-of-Distribution）** | 分布外 | 训练数据之外的数据分布 |
| **In-Distribution** | 分布内 | 与训练数据同分布的数据 |
| **Generalization** | 泛化 | 模型在未见过的数据上仍能正确表现的能力 |
| **Overfitting (to evaluation)** | 过拟合到评测 | 训练只在评测题型上学会答对，未学到通用能力 |
| **Distribution Shift** | 分布偏移 | 部署时的数据分布与训练分布不同 |

## 五、Agent 与部署 · Agents & Deployment

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **Agent / Agentic** | 代理 / 代理式的 | 能自主调用工具、做决策、执行多步操作的 AI 形态 |
| **Tool Use** | 工具调用 | 模型通过 function call 等方式使用外部工具 |
| **Tool Definition** | 工具定义 | 在 system prompt / context 中描述可用工具的元数据 |
| **Sandbox** | 沙盒 | 隔离的运行环境，用于安全地让 AI 调用工具 |
| **Frontier Model** | 前沿模型 | 当前最强、最具风险的 LLM（如 Claude Opus、GPT-5 等） |

## 六、研究方法 · Research Methodology

| 英文 | 中文 | 简要说明 |
|------|------|----------|
| **Ablation Study** | 消融实验 | 通过移除/改变某一部分，验证它对结果的贡献 |
| **System Prompt Injection** | 系统提示注入 | 在生成训练数据时临时给模型注入引导，训练时再去掉 |
| **Auditing Game** | 审计博弈 | Anthropic 的研究方法，让 \"红队\" 和 \"蓝队\" 互相挑战 |
| **Red Teaming** | 红队测试 | 主动寻找模型漏洞的对抗性测试 |

---

> **使用提示**：如果你在阅读原文时遇到陌生术语，先回到本表查中文译名 + 简要说明，再回原文上下文。
> 对中文读者尤其推荐先理解 SDF / Difficult Advice / Pretraining Prior 这三个术语——它们是本文的工程支柱。
