# 关键概念卡 · Don't Outsource the Learning

> 12 张面向工程师的认知卡片。配合 Addy Osmani 原文与三项实验阅读，可作为团队 brown-bag 或 1-on-1 的讨论提纲。

---

## 卡片 1 · Posture（姿势）

> 不是 mindset（认知），不是 workflow（流程），是 *posture*——你在打开 prompt 那一刻的肌肉记忆。

- **关键判断**：决定你长不长能力的，不是用不用 AI，而是用 AI 的姿势。
- **为什么用 posture 而不是 mindset**：mindset 在脑子里，posture 在手指上。每天 100 次微动作累积出 posture，所以它比 mindset 难改也比 mindset 重要。
- **检查信号**：打开 Cursor 的第一秒——你是在写"问题假设"还是直接 `Cmd+K`？

---

## 卡片 2 · Cognitive Offloading（认知代办）

> 把 *how* 交出去，自己留下 *what* 和判断。

- **健康例子**：计算器、GPS、搜索引擎。
- **特征**：你仍然在构造"什么是对的答案"，工具只是替你做"如何到达"。
- **失败信号**：开始连 *what is correct* 都不构造时，offloading 已经滑向 surrender。

---

## 卡片 3 · Cognitive Surrender（认知接管）

> 你不再独立构造答案，AI 的输出直接成为你的输出。

- **来源**：Shaw & Nave, Wharton, 2026。1,372 名被试，AI 错时 73% 跟着错；置信度反而上升。
- **关键陷阱**：与 cognitive offloading 在主观感受上几乎不可区分。
- **测试**：把 AI 的输出关掉，你能否从空白页重写出大致相同的答案？能 = offloading；不能 = surrender。

---

## 卡片 4 · Cognitive Debt（认知债）

> 来自 MIT Your Brain on ChatGPT 论文。短期省力，长期复利偿付。

- **神经层证据**：EEG 显示 alpha/beta 频段连接强度随外部工具数量单调下降。
- **行为层证据**：83% 的 LLM 组在交卷后无法引用自己刚写的任何一句话。
- **延迟效应**：LLM-to-Brain 切回手工后的 session 中，被试脑活动仍然处于抑制状态。

---

## 卡片 5 · Comprehension Debt（理解债）

> Addy Osmani 的概念。代码量与团队任何人真正理解的代码量之间，那道越拉越大的鸿沟。

- **与 cognitive surrender 的关系**：surrender 是机制，comprehension debt 是账单。
- **复利偿还时点**：incident、framework 升级、安全审计、人员流失——这四个时刻同时打开账单。
- **唯一的滚动还款**：定期手写复现、定期 brown-bag、定期 architecture review。

---

## 卡片 6 · 17% 缺口（The Anthropic Gap）

> Anthropic 2026-01 RCT 的核心数字：AI 组测验比手写组低 17%。

- **样本**：52 位（多为 junior）每周至少用一次 Python 的工程师。
- **任务**：学 Trio（异步并发库），写两个 feature，做一份小测验。
- **效应量**：Cohen's d = 0.738（中到大），p 显著。
- **更重要的发现**：AI 组内部差异（"问概念" vs "贴代码"）比组间差异更大。

---

## 卡片 7 · 顺序大于总量（Order > Amount）

> CHI 2026 论文核心论点：LLM 接触的*时点*决定决策质量，不是 LLM 使用的*总量*。

- **机制**：LLM 给出的第一个框架会锚定整个问题表述。
- **推论**："我只用 AI 起个头"不是安全做法——它恰恰是最危险的做法。
- **可操作版本**：在任何陌生问题上，把"自己想 15 分钟"作为强制前置步骤。

---

## 卡片 8 · The Default UX Trap（默认 UX 陷阱）

> 所有主流 AI 编程工具的默认配置，目标函数都是"closed task"，不是"learned engineer"。

- **结构性原因**：产品 OKR 看 merged PR、DAU、time-to-PR；没有任何主流工具的 OKR 是"用户半年后比现在更强"。
- **结论**：你不能指望工具自动让你成长，必须主动改默认配置。
- **第一改动**：把 Learning Mode / Study Mode 从"学生功能"升级为"生产工具"。

---

## 卡片 9 · 五个不可外包临界点

| # | 临界点 | 触发场景 |
|---|---|---|
| ① | 东西坏了 | 凌晨 3 点 P0 incident |
| ② | 自信地错了 | LLM 给出 plausible-looking incorrect 答案 |
| ③ | 地基变了 | 框架升级 / 合规整改 / 架构迁移 |
| ④ | 远离了均值 | GitHub 上没人解决过的问题 |
| ⑤ | 市场重新定价 | "只有 AI 时能交付的工程师"被挤压 |

---

## 卡片 10 · 六条姿势补丁

1. **先假设**：写 prompt 前先写两三句"我以为问题是什么"。
2. **先解释 再代码**：陌生领域第一条 prompt 是 "explain & tradeoffs, no code yet"。
3. **Learning Mode 当生产工具**：Claude/ChatGPT/Gemini 的"学生模式"打开。
4. **当 junior PR 审 AI 输出**：测试绿不代表能 merge。
5. **月度手写复现**：找一段 AI 写过的代码，关掉 AI，重写。
6. **让 AI 教**：写完后追问"用了哪些概念、推荐我读什么"。

---

## 卡片 11 · 两个指标（Ship & Learn）

> 工程师必须同时跑两个独立的 KPI，但你的经理只会问你第一个。

- **Ship 指标**：merged PR、closed ticket、shipped feature。
- **Learn 指标**：本周/本月你能解释清楚的新概念、新框架、新 tradeoff。
- **管理推论**：如果你管团队，1-on-1 里必须主动问 Learn 指标——因为它是私人的、不会自动出现在系统里。

---

## 卡片 12 · 周末问句（The Friday Question）

> 这是把整篇文章压缩成可以每周问自己一次的一句话——

> **"Did I learn anything this week, or did I just close tickets?"**
> （这周我学到了什么，还是只是关了几张工单？）

如果连续 4 周回答都是 "just closed tickets"，cognitive debt 已经在你身上复利了。是时候打开 Learning Mode，找一段你自己都不太懂的代码，手写一次。
