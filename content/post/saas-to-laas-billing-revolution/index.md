---
title: "从SaaS到LaaS：当软件公司开始按Token而非Seat收费，整个产业在重构"
description: "GitHub Copilot 切换计量计费触发的不是一次定价调整，而是 SaaS 行业自 AWS 以来最大规模的商业模式集体转向。本文拆解三类受害者、三条逃生路径与并购前瞻。"
date: 2026-04-30
slug: "saas-to-laas-billing-revolution"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 商业模式
    - SaaS
    - Copilot
    - 定价
    - LLM经济学
    - 产业分析
draft: false
---

## 当 GitHub Copilot 改成"按 Token 计费"，软件行业的成本结构正在被悄悄重写

2026 年 4 月，GitHub 官方博客发了一条对很多团队来说"很扎"的公告：**GitHub Copilot 个人版与企业版正在迁移到 usage-based billing（按使用量计费）**，不再是过去 10 美元/19 美元的固定月费。几乎同一周，The Pragmatic Engineer 发出了 *"AI token spending out of control – what's next?"* 这一期 Pulse，里面引用的几家中型 SaaS 公司给出了让人胃疼的数字：

- 一家 60 人工程团队，月度 LLM API 账单从 2024Q4 的 $8K 涨到 2026Q1 的 $94K；
- 一家初创公司 35% 的工程支出花在了 LLM token 上，**已经超过 AWS 账单**；
- 高频 AI Coding 用户的 P95 月使用成本，能达到月薪的 12-18%。

这不是个别公司的 PR 危机。它是过去三年所有 AI 编程工具厂商**集体推迟面对的一笔账**——当推理成本从 GPT-4 那种"每 1M token $30"砸到 GPT-5.5/DeepSeek V4 这种"按毛分计"，仍然挡不住一个事实：**Agent 化的工作流会以指数级吃 token**，固定订阅模式数学上撑不住。

本文不再讨论"AI 会不会取代程序员"这类口水问题，我们看一个更冷峻的：**当软件工程的边际成本从"人时"变成"token"，行业的商业模式、岗位结构、定价权会怎样重排？**

---

## 一、固定订阅时代的终结：从 SaaS 到 LaaS（LLM-as-a-Service）

GitHub Copilot 2021 年 10 美元/月的定价，至今仍被许多人当作 AI SaaS 的"锚点"。但这个定价从第一天就建立在一个错误假设上：**普通开发者一天用 Copilot 不会超过 50 次 completion**。

到了 2026 年，这个假设彻底死了。一个用 Copilot Workspace 或 Cursor + Claude Code 的工程师，**单日 token 消耗轻松达到 5-15M**——里面 90% 是 agent 在背景里反复读代码、跑测试、改文件。同样一个月费 19 美元的账户，被两个用户撑出 100 倍的成本差距。

这就是为什么 GitHub 这次的迁移不是孤立动作。把过去 6 个月的同类公告排在一起：

| 厂商 | 旧定价 | 新定价 | 变化方向 |
| --- | --- | --- | --- |
| GitHub Copilot | $10 / $19 月费 | Premium requests 计量 | Token-based |
| Cursor | $20 月费 | Pro+ Auto / Max-mode 计量 | Token-based |
| Anthropic Claude Code | 月费 $20 | $100 / $200 + 用量上限 | 阶梯订阅 |
| Replit Agent | 月费 + Boost | 按"Effort" 计费 | 计算单元 |
| Vercel v0 | 月费 | Credits 制 | 计量计费 |
| Sourcegraph Cody | $9-19 | Per-query | 计量计费 |

整个行业在 6 个月里完成了从"All-you-can-eat"到"Pay-as-you-go"的切换。这是 SaaS 历史上从未有过的**集体定价转向**——上一次类似规模的转向是 2010 年 AWS EC2 推动的"按小时计费"，把传统软件许可模式打散。

不同的是，这次受冲击最严重的不是供应商而是**用户**。

## 二、新成本结构下的三类受害者

按月费定价的 SaaS 时代，**重度用户其实在补贴轻度用户**。当切换到计量计费，这种补贴消失，几类人会真切感受到痛：

**1. 个体重度用户与外包团队。**
一个习惯了让 agent 全程跑测试、查文档、生成 PR 的工程师，月成本从 $20 变成 $200-$800 不奇怪。Reddit 和 HN 上已经有大量 "I broke my own bank with Cursor Max" 的帖子。

**2. AI-native 创业公司。**
依赖 LLM 把团队规模压低的初创，会发现"省下的 5 个工程师工资"被 token 账单完全吃掉。Pragmatic Engineer 引用的一个 YC 公司创始人原话是："AI 没让我们的成本下降，只是把成本从 W-2 工资迁移到 OpenAI 信用卡。"

**3. 教育与开源社区。**
这是被讨论最少但最痛的群体。免费/低价 Copilot 是过去 4 年学生学习现代开发流程的入口，从 2026 起这条路被切断。下一代开发者的"AI fluency"会出现明显的家庭收入分层，这是个**长期不可逆**的副作用。

## 三、行业反应：三条逃生路径

面对这条成本曲线，市场已经分化出三条路径：

**路径 A：本地小模型 + 自建 Agent。**
Ollama、LM Studio、llama.cpp 的下载量在 2026Q1 同比涨 4 倍。Apple Silicon Mac Studio + Qwen3 Coder 32B 量化版，已经能覆盖 70% 日常补全场景，边际成本接近 0。问题是质量上限被本地硬件锁死。

**路径 B：Token 优化为一等公民。**
出现了一个新工种叫 "AI Cost Engineer"——专门做 prompt 压缩、cache 共享、tool result trimming、模型路由。Latent Space 的 *Tasteful Tokenmaxxing* 那一期已经证实，认真做 token diet 的团队能把成本砍到 1/3。

**路径 C：把 LLM 成本对外转嫁。**
头部厂商如 GitHub、Vercel、Linear 开始把 AI 用量直接打进客户账单，用 markup 转嫁给 B 端客户。这是**行业最后选择的一条路**，但它意味着 SaaS 总价进入新一轮通胀。

## 四、深层结构变化：软件公司开始像云厂商一样思考

最值得关注的不是定价层，而是**财报视角的结构变化**：

| 维度 | SaaS 时代（2015-2023） | LaaS 时代（2026-） |
| --- | --- | --- |
| 毛利率 | 75-85% | 35-55%（被推理成本拖累） |
| 关键 KPI | ARR / Churn | Cost-per-token / Token-per-feature |
| 技术核心 | 多租户 + 数据库 | 推理 routing + cache |
| 竞争对手 | 同领域 SaaS | 上游 LLM 厂商（直接吃下行） |
| CFO 关注点 | CAC/LTV | Compute 成本与对冲 |

这张表里最耐人寻味的是"竞争对手"那一行——**所有 AI-native SaaS 现在都被自己的上游 LLM 供应商威胁**。OpenAI 已经在做 Codex Superapp 直接卖给开发者；Anthropic 推 Claude Code 卷过 Cursor；Google 把 Gemini Code Assist 塞进 GCP。中间层 SaaS 的护城河越来越薄，毛利越来越紧。

我的判断：未来 18 个月会出现 **Aggregator 反向收购**的并购潮——头部 LLM 厂商收购掉一些 AI 应用层公司，把"模型 + 应用"打成捆绑销售。Cursor、Replit、Vercel 等都是潜在标的。

## 五、给三类读者的可执行建议

**给独立开发者**：
- 立刻接入用量监控（Cursor 的 Usage tab、GitHub 的 Activity log）；
- 给每个项目设月度 budget，超出自动降级到本地 7B 模型；
- 不要把 agent autonomy 开到最大，明确指令式调用比"猜你想干啥"省 5-10x token。

**给工程团队 leader**：
- 把 LLM token 成本放进"工程效率"看板，和 CI 时间、PR 周期同等优先；
- 至少 30% 流量走自托管或开源模型，作为对头部厂商的议价筹码；
- 评估 "Cost Engineering" 岗位（哪怕兼职），ROI 通常 < 3 个月。

**给 SaaS 创业者**：
- 重新审视"按 seat 计费"是否还合理，提前设计 usage-based 定价层；
- 用 RAG / Cache / Prompt Compression 把推理成本砍到 30%，否则 18 个月内毛利不可持续；
- 思考"被上游 LLM 厂商收购或被替代"的两种结局，主动靠拢一边。

## 结语：软件行业的"工业革命二阶段"

第一次工业革命把人力替换成了机器；当下这次 AI 革命，最初讲的是把工程师替换成模型，但更现实的事情是——**把工程师的工资替换成了 token 账单**。区别在于工资是有上限的、token 没有。

GitHub 这次定价改革只是第一只雪球。当所有 AI 工具同步切到计量计费，软件行业的"边际成本曲线"将被永久重写。那些还在用 2021 年那套 SaaS 财务模型估值的公司，会在下一个财报季集体被市场修正。

> 软件不会再吃掉世界。Token 会。

---

### 引用与延伸阅读

1. GitHub Blog – *GitHub Copilot is moving to usage-based billing* — https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage
2. The Pragmatic Engineer – *The Pulse: AI token spending out of control – what's next?* — https://newsletter.pragmaticengineer.com/p/the-pulse-ai-token-spending-out-of
3. The Pragmatic Engineer – *Tokenmaxxing as a weird new trend* — https://newsletter.pragmaticengineer.com/p/the-pulse-tokenmaxxing-as-a-weird
4. Latent Space – *Tasteful Tokenmaxxing* — https://www.latent.space/p/ainews-tasteful-tokenmaxxing
5. 404 Media – *The AI Compute Crunch Is Here* — https://www.404media.co/the-ai-compute-crunch-is-here-and-its-affecting-the-entire/
6. Anthropic – *Claude Code pricing tiers update* — https://www.anthropic.com/
