---
title: "AI 编程订阅的'计费转向'：GitHub Copilot flex × Claude API 拆分，按席位卖软件的时代正式落幕"
description: "2026 年 5 月，GitHub 把 Copilot 个人版改成 flex allotments，Anthropic 把 Claude 订阅拆成'交互+程序化双账户'，OpenAI 用 Codex 的更宽限额抢市场。三个动作背后是同一个事实：AI 编程 SaaS 的'席位+无限'神话在算力面前撑不住了。"
date: 2026-05-14
slug: "ai-coding-agent-token-metering-copilot-flex-pricing-pivot-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - SaaS 定价
    - AI 编码助手
    - Token 经济学
    - Copilot
    - 商业模式
    - 算力经济
draft: false
---

## 一句话总结

5 月 12–14 日这一周，AI 编程工具市场连发三个大新闻：

1. **GitHub** 给 Copilot Pro / Pro+ 引入 **flex allotments**（弹性额度），新增更贵的 **Max 计划**；Business / Enterprise 转向 **API token-based pricing**，6 月 1 日生效。
2. **Anthropic** 把所有 Claude 订阅拆成两个账户：**"交互式使用"**（Claude.ai、Claude Code）+ **"程序化使用"**（claude-p、第三方 harness）。后者按订阅金额折算成 API credit。
3. **OpenAI** 在同一天发布企业版 Codex 切换优惠，限额比 Claude 宽松。

软件即服务（SaaS）行业近 20 年的定价基石是**"按席位卖、无限使用"**。这个范式正在被 AI 编程工具这一波**单用户成本可以无上限的产品**强行撕开。

本文回答三个问题：
1. **为什么"无限"必须死，到底是哪个变量在变化？**
2. **GitHub、Anthropic、OpenAI 各自走的是什么路径，谁更稳？**
3. **未来 12–24 个月，AI 软件的"标准定价模型"会长什么样？**

---

## 一、SaaS 定价的"不可能三角"被 AI 打破

传统 SaaS 定价有三个用户喜欢的属性：

1. **可预测**（每月固定费用）；
2. **无限使用**（用得多也不加价）；
3. **平台盈利**（边际成本接近零）。

过去 20 年这三个属性可以同时成立，因为：

- 后端是数据库 / web 服务 / CRUD，每用户边际成本极低；
- 重度用户和轻度用户之间的成本差通常不超过 10 倍；
- 网络效应、品牌、整合是更大的护城河，定价只需做得"足够便宜"。

**AI 编程工具完全打破了这个均衡**：

- 一个 agent 一次"重构这个 repo"的调用，可能消耗 5–50 美元的 token；
- 重度用户和轻度用户之间的成本差可以达到 **100–1000 倍**；
- 边际成本不仅不接近零，反而是订阅价的 **30%–300%**——一个 $20/月 用户可能让平台亏 $50。

The Pragmatic Engineer 在 5 月 7 日的报道点破了真相：**Anthropic 之所以一夜之间"对开发者不友好"，是因为算力告急**。Anthropic 在跟 SpaceX 谈 300MW Colossus 1 算力交易的同时，先在用户端紧急止血——把通过第三方 harness（OpenClaw、OpenCode、Cline 等）的"程序化"用量切到 API 计费层。

Gergely Orosz 透露了 GitHub 的具体变化：

> Pro 和 Pro+ 年付会涨价（multiplier 提升 ~3×）；Business / Enterprise 完全转向 API token-based 定价，**6 月 1 日生效**。GitHub 此前一直在重度补贴，从此用户必须看着 token 计数器写代码。

**这不是定价策略调整，这是商业模式重写。**

---

## 二、三家路径对比

为方便对比，我把三家 2026 年 5 月的新定价结构拍扁成下表：

| 维度 | GitHub Copilot | Anthropic Claude | OpenAI Codex |
|------|-----------------|-------------------|---------------|
| 个人版基础 | Pro/$10、Pro+/$39、Max（新） | Pro/$20、Max/$200 | ChatGPT Plus/$20、Pro/$200 |
| 限额机制 | flex allotments（弹性额度） | 双账户：subscription + API credit | "更宽松"未公开具体倍数 |
| 当订阅额度用完 | 自动从 flex 额度扣，可设上限 | 程序化用量切到 API 计价 | 软限速 + 升级提示 |
| 企业版 | 6/1 起 API token 计费 | API + Bedrock + Vertex 一致 | 企业 API 一致 |
| 透明度 | 高（仪表盘 + 显式 token 数） | 中（API credit 余额可查） | 中 |
| 第三方 harness 支持 | 不适用 | 双账户分流后**明确支持** | 不存在第三方 harness 问题 |

三家其实是同一种压力下的三种应对：**承认 token 是真实的成本，但用不同方式让用户"无痛地"感受到这件事**。

### 2.1 GitHub：flex 是"经过包装的 metered billing"

GitHub 的 flex allotments 在用户体验上做了相对柔和的设计——你买的不是"无限"，而是"基础额度 + 弹性额度 + 你设的上限"。这种"三段式"借鉴的是 **AWS 的 Reserved Instances + Savings Plan + On-Demand** 模型。

但它的本质和 metered billing 没有差别：**用得多就花得多**。GitHub 比 Anthropic 多了一个 Microsoft / Azure 的算力后盾，所以可以在 Pro $10 这个甜蜜价位上多撑一段时间。

Max 计划（具体价格 GitHub 未在博客里公布，但参考其他厂商应为 $100–$200/月）是给"agent-first 开发者"准备的——这部分用户每天会跑十几个 agent 任务，按 API 算下来一个月轻松 $500+，Max 计划给一个"再贵一点但比 API 便宜"的中间档。

### 2.2 Anthropic：双账户拆分是聪明但伤感情

Anthropic 的做法在数学上最清晰：**你付 $200，我给你一份在 Claude.ai / Claude Code 里随便用的"补贴权"，再给你 $200 的 API credit 让你在第三方 harness 里花**。

这有几个隐含的取舍：

- **聪明**：彻底分离了"补贴的交互式 UX"和"按市价的 agent 调用"，把成本结构透明化。
- **聪明**：第三方 harness（OpenClaw、Cline 等）从"灰色地带"变成"明确支持"，长期对生态健康。
- **伤感情**：之前能用 70%–90% 折扣享受 Claude 的开发者突然感觉被薅羊毛——Latent Space 称之为 *"rug pull 感"*。
- **政治成本**：在 OpenAI 同一天用更宽松的 Codex 限额抢人时，这个动作显得防御性十足。

The Pragmatic Engineer 提到的一个细节很关键：**Anthropic 在做这件事的同期，悄悄签下了 SpaceX Colossus 1 的 300MW 算力**。这说明限额收紧本质是**用价格信号当临时止血手段，等算力到位再放松**。

我的预测：**6–9 个月之内，Anthropic 会重新提高免费额度**——但回不到 90% 折扣的时代了。

### 2.3 OpenAI：用宽限额抢市场，但只是阶段性的

OpenAI 同时发了 Codex 企业切换促销，限额比 Claude 宽松。这是经典的"挑战者套路"——当对手收紧时你放松，抢一波用户。

但这是**短期姿态而非长期路线**。OpenAI 自己也在做按 token 收费的产品（API、企业版 Codex）。它现在愿意宽松，是因为 GPT-5.5 推出后市场口碑不错，需要用宽松限额加固"领先"叙事。

Latent Space 的 "mandate equinox" 半玩笑半认真地说：**每 6 个月这两家会交替占领开发者口碑**。今天是 OpenAI 占便宜，**10 月份 Anthropic 大概率会反扑**。

---

## 三、为什么 SaaS 定价的"席位 → token"转向是结构性的

要理解这一周的事件，必须从更深的视角看。

### 3.1 边际成本的相变

```text
传统 SaaS（CRM / 协作 / 设计工具）：
  用户增加 → 成本增加几乎为零（数据库行 + 几 ms CPU）
  → 适合"按席位 + 无限使用"

LLM agent 类工具：
  用户增加 + 任务复杂度增加 → 成本增加非线性
  → 单次 agent 调用成本范围横跨 4 个数量级（0.001$ ~ 100$）
  → 必须"按消耗"定价，否则平台被重度用户拖垮
```

这个变化和 1990 年代电话公司从"包月 → 按分钟"转型本质相同——背后是**单位提供的资源已经不能再视作"近似无限"**。

### 3.2 成本和效用的高度不对称

更深的问题是：**对开发者来说，AI 编码工具的效用和成本严重不匹配**。

- 一个 senior 开发者花 $50 token 让 agent 重构 10 万行遗留代码 → 节省 8 小时 = $1000 工时 → 效用 / 成本 = 20×
- 一个 junior 开发者花 $50 token 让 agent 写 hello world → 效用 / 成本 ≈ 0.01×

按"无限"定价时，平台无法把价格信号传给低价值用户。**按 token 定价等于强迫用户做 ROI 决策**——这对市场效率是好的，但对 onboarding 用户是糟糕的。

GitHub 的 flex allotments 是个聪明的折中：**给一个基础免费额度让 junior 用户用得起，再用弹性额度向 senior 用户卖更多**。

### 3.3 第三方 harness 经济学

过去一年最被低估的市场力量是**第三方 harness**：Cline、OpenCode、Cursor、Aider、Continue、Claude Code 的开源衍生品。

它们的存在让"模型 API"和"用户体验"解耦：

- 模型提供方（Anthropic / OpenAI）：拥有最强模型，但 UX 创新慢；
- harness 提供方（Cline、Cursor）：UX 极速迭代，但不拥有模型；
- 用户：可以混用——便宜时用 Anthropic API + Cursor，便宜时换 OpenAI + Cline。

这个分层对模型厂商是**最大的定价压力来源**——它让用户可以**只为他真正在意的那一层付费**。Anthropic 这次的双账户拆分本质是承认这个现实：**你想用别的 harness 就用，但要按 API 价付钱**。

Notion 5 月发布的 **External Agents API**（让 Claude、Codex、Cursor、Devin 都能在 Notion 里跑）会进一步加剧这一趋势。**未来的 AI 协作平台都是 harness，而不是模型本身**。

---

## 四、定价架构图：从"席位"到"消耗+席位"

```text
                          【SaaS 1.0：席位时代】
┌──────────────────────────────────────────────────────────────────┐
│  User × Months × Price_per_seat                                  │
│  └─→ 平台收入 ≈ 用户数 × ARPU                                    │
│  └─→ 重度/轻度用户成本差 < 10×, 可承受                            │
└──────────────────────────────────────────────────────────────────┘

                          【SaaS 1.5：AI 过渡期】(2025–2026 当下)
┌──────────────────────────────────────────────────────────────────┐
│  Base seat (subsidized) + Flex allotment (metered) + Hard cap    │
│                                                                  │
│   $10–$200          $0–$1000           User-defined              │
│       │                  │                   │                   │
│       └─ retention       └─ revenue          └─ trust            │
│          牵引             upside                guardrail        │
└──────────────────────────────────────────────────────────────────┘

                          【SaaS 2.0：消耗时代】(2027+)
┌──────────────────────────────────────────────────────────────────┐
│  Outcome-based pricing                                           │
│   - per merged PR, per resolved ticket, per shipped feature      │
│   - 模型/harness 厂商分成                                        │
│   - 长期摊销硬件折旧、电力成本                                   │
└──────────────────────────────────────────────────────────────────┘
```

---

## 五、对开发者和团队的实际影响

**对个人开发者**：

1. **真实的"AI 工具月度成本"**会从 $10–$20 跳到 $50–$200。预算需要重新规划。
2. **混用多个工具**变得更划算——Anthropic 限额紧张时切到 Codex/Cursor 不再有道德负担。
3. 学会**看 token 仪表盘**——这是 2026 年开发者的新必修技能。在每次开 agent 任务前估算 token 消耗。

**对小型团队（5–20 人）**：

1. AI 编程工具会成为继云资源、SaaS 订阅之后的**第三大可变成本**。一个 10 人 dev 团队，原来 $200/月（10 × $20 Copilot），新规则下可能是 $1000–$2000/月。
2. 团队需要建立 **AI 预算治理**：谁能跑长任务、什么任务必须 review、哪些代码禁止 agent 触碰。
3. 预算管理工具市场会爆发——预计 6 个月内出现专门的 "AI cost observability" 创业公司。

**对大型企业**：

1. **6 月 1 日是 GitHub Copilot Business / Enterprise 转 token 计费的截止日**。CFO 财务模型必须在 5 月底前完成更新。
2. 谈判 enterprise contract 时，**关键条款是"高峰使用月份的 token 上限保证"**——这是新的供应商管理博弈点。
3. 企业自建 inference（如基于 Llama / DeepSeek）的 ROI 计算重新打开——当 GitHub / Anthropic 不再补贴，自建的临界点降低 30%–50%。

---

## 六、犀利判断与预测

**判断一：6 个月内会出现首个"按结果定价"的 AI 编程工具创业公司。**
方向是"每个 merged PR $X、每个 closed bug $Y"，把 token 风险转给平台。第一波公司大概率融资到 Series A 然后被收购或挂掉，但模式会站住。

**判断二：模型厂商的"双账户"模式会成为行业标准。**
OpenAI 大概率会跟进 Anthropic 的设计——把 ChatGPT 订阅和 API credit 在产品层面分开。Google Gemini 也会。

**判断三：第三方 harness 的价值会被市场重估。**
Cline、Cursor、Continue 这类纯 UX 公司，市场之前看不清它们的护城河。当模型变得可替换、价格变得透明，**harness 才是真正能差异化的层**。预计未来 12 个月会有大额融资。

**判断四：开发者会显著增加自部署 / 本地模型的使用比例。**
当 token 不再被补贴，Llama 4 / DeepSeek V4 / Qwen 3 等开源模型的"本地跑"经济学突然成立。配合 H100/B200 二手市场、Mac Studio M5 Ultra 等硬件，本地 agent 推理在 2026 年下半年会成为开发者社区的真实选项。

**判断五：监管会开始关注 AI 工具的"价格不透明"。**
Anthropic 临时调整限额、GitHub 在通知期内涨价 3 倍，这些动作在欧盟 / 英国可能触发消费者保护审查。**2027 年大概率有第一个 AI SaaS 反垄断 / 不公平交易诉讼**。

---

## 七、读者可以带走的认知与行动

如果你是 **开发者**：
- 月底前重新评估你的 AI 工具组合。算清你真实的 token 消耗。
- 学会"先用便宜模型起草、再用贵模型 review"的工作流——能省 50%–80% 成本。
- 关注本地模型 + 高端硬件的总持有成本——某些场景已经比订阅划算。

如果你是 **engineering manager**：
- 建立团队 AI 工具预算 dashboard，纳入月度回顾。
- 制定"哪些任务允许 agent 自动 merge、哪些必须人工 review"的策略。
- 把"AI 成本/产出比"加入团队 OKR。

如果你是 **创业者**：
- 不要做"再一个 Copilot 替代品"——基础 IDE 集成已经过度竞争。
- 看 **AI cost observability、按结果定价、第三方 harness 差异化** 三个方向。
- 自建模型 + 私有部署对企业客户的吸引力上升中。

如果你是 **投资人**：
- 重新审视投资组合里"按席位无限定价"的 AI SaaS——它们的盈利模型可能假设了过时的成本曲线。
- 多关注垂直行业（法律、金融、医疗）的"按案件 / 按文档"定价模式。

---

## 参考来源

1. GitHub Blog — *GitHub Copilot individual plans: Introducing flex allotments in Pro and Pro+, and a new Max plan*：<https://github.blog/news-insights/company-news/github-copilot-individual-plans-introducing-flex-allotments-in-pro-and-pro-and-a-new-max-plan/>
2. GitHub Blog — *Improving token efficiency in GitHub Agentic Workflows*：<https://github.blog/ai-and-ml/github-copilot/improving-token-efficiency-in-github-agentic-workflows/>
3. Latent Space — *[AINews] Codex Rises, Claude Meters Programmatic Usage*：<https://www.latent.space/p/ainews-codex-rises-claude-meters>
4. The Pragmatic Engineer — *The Pulse: Did capacity shortages turn Anthropic hostile to devs?*：<https://newsletter.pragmaticengineer.com/p/the-pulse-did-capacity-shortages>
5. The Pragmatic Engineer — *The Pulse: Forward deployed engineering heats up again*：<https://newsletter.pragmaticengineer.com/p/the-pulse-forward-deployed-engineering>
6. Stratechery — *The Inference Shift*：<https://stratechery.com/2026/the-inference-shift/>
7. Marginal Revolution — *Data centers are good*：<https://marginalrevolution.com/marginalrevolution/2026/05/data-centers-are-good.html>
8. The Information — *SpaceXAI Exodus*（人才流动背景）：<https://www.theinformation.com/articles/spacexai-exodus-50-recent-exits-meta-thinking-machines-hire-staff>
