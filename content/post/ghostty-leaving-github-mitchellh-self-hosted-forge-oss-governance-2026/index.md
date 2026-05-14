---
title: "Ghostty 离开 GitHub：当一个 18 年的 GitHub 用户决定自托管，开源协作的'垄断时代'是否到了拐点"
description: "Mitchell Hashimoto 把 Ghostty 终端项目从 GitHub 迁出，不只是个人不满，而是 OSS 协作基础设施过度集中、可靠性退化与 AI 化失控的集体信号。本文拆解迁移决策背后的技术与治理逻辑。"
date: 2026-05-14
slug: "ghostty-leaving-github-mitchellh-self-hosted-forge-oss-governance-2026"
image: "cover.svg"
categories:
    - 前沿科技
tags:
    - 开源
    - GitHub
    - Ghostty
    - Mitchell Hashimoto
    - 开发者工具
    - 自托管
    - Forgejo
    - DevOps
draft: false
---

## 引子：一个 GitHub User #1299 的告别信

2026 年 4 月 28 日，HashiCorp 联合创始人、Vagrant/Terraform/Packer/Vault/Consul/Nomad 的作者 Mitchell Hashimoto 在个人博客上写下了这样一段话：

> "Writing this makes me irrationally sad, but Ghostty will be leaving GitHub. I'm GitHub user 1299, joined Feb 2008. Since then, I've opened GitHub every single day. Every day, multiple times per day, for over 18 years. Over half my life."

这不是一篇愤怒帖。Hashimoto 在文章里反复强调："I love GitHub more than a person should love a thing." 但接下来他说：在过去一个月里，他每天用一本日记本记录 GitHub 影响他工作的天数——**几乎每一天都打了 X**。文章发表当天，他因为一次 GitHub Actions 故障，**连续两小时无法完成任何 PR review**。

如果 Hashimoto 是孤例，这只是个人选择。但事实是：从 2025 年 11 月 GitHub 那次世纪级 AWS 区域故障开始，The Pragmatic Engineer 的"AI load breaks GitHub"系列、ACM Queue 那篇 *Open Source and the Iceberg Theory*、Linux Foundation 旗下 Codeberg/Forgejo 的安装量曲线、以及今年 2 月 Linus Torvalds 那条"我宁愿继续用邮件列表也不愿意被你们的 webhook 困死"的评论——**所有信号都指向同一件事：以 GitHub 为中心的开源协作模型正在走过它的"质保期"。**

Ghostty 的离开，是这个集体不满的标志性事件。本文不写情绪，写三件事：

1. **技术层面**：Ghostty 真正搬到哪里去？自托管 Forgejo 的可行性边界在哪里？
2. **治理层面**：当一个项目离开 GitHub，它失去什么、保留什么、得到什么？
3. **产业层面**：为什么 2026 年这个节点，对 GitHub 是结构性危险信号？

## 一、Ghostty 这个项目本身的特殊性

先让数据说话。Ghostty 不是一个普通的小项目：

| 指标 | 数据 |
|------|------|
| GitHub Star | ~33,000 (公开 beta 后 18 个月) |
| Contributors | 800+ |
| 语言 | Zig（占 ~78%）+ Swift/GTK/C |
| 发布周期 | 每周 nightly + 月度 stable |
| 平台 | macOS/Linux（GTK4） |
| 治理形态 | 2026 年 3 月转为非盈利组织 |

Ghostty 是 Hashimoto 离开 HashiCorp 之后的"主力项目"，也是为数不多的、**作者实际每天 review PR、写代码的旗舰开源终端**。它的活跃度足以让任何"GitHub 真的不能离开"的论点显得软弱——这恰恰是为什么这次迁移有信号意义。

更关键的是：**Ghostty 在 2026 年 3 月已经把自己转成了非盈利组织（"Ghostty Foundation"），并且在 4 月引入了 subsystem maintainers**。换句话说，它已经走完了从"个人项目"到"社区项目"的治理过渡。这意味着迁移决定**不是 Hashimoto 一个人的任性**，而是有组织背书的决策。

## 二、Ghostty 到底搬到了哪里？

Hashimoto 在原文里没有立刻指明终点，但根据他过去几个月的公开发言，以及 Ghostty Foundation 4 月底的 commit 历史，目标基本明朗：

```text
┌────────────────────────────────────────────────────────┐
│                  Ghostty 迁移架构（2026.05）           │
├────────────────────────────────────────────────────────┤
│                                                        │
│   Source of Truth ─→  git.ghostty.org (Forgejo)        │
│                       ├─ Issues / PRs                  │
│                       ├─ Code review                   │
│                       └─ Release artifacts             │
│                                                        │
│   CI / Build ──────→  自建 Buildkite + Mac mini cluster│
│                       (替代 GitHub Actions)            │
│                                                        │
│   Mirror ──────────→  github.com/ghostty-org/ghostty   │
│                       (只读镜像，保留 star/曝光)        │
│                                                        │
│   Discussion ──────→  Discord + ghostty.org/discuss    │
│                                                        │
└────────────────────────────────────────────────────────┘
```

注意几个细节：

**(1) Source of Truth 切换到 Forgejo**。Forgejo 是 Gitea 在 2022 年 Gitea Ltd 商业化后分叉出来的"非盈利 git forge"，由 Codeberg e.V. 维护。Forgejo 在 2025 年发布了 v10，关键能力补齐：actions（与 GitHub Actions YAML 高度兼容）、packages registry、组织级权限。

**(2) GitHub 仓库降级为只读镜像**。这是关键策略——保留发现性（discoverability）的同时，所有真实工作流离开 GitHub。任何用户点击 GitHub 上的 Issues 都会跳转回 git.ghostty.org。这是 *外迁但不脱离* 的经典姿态。

**(3) CI 自建**。这是真正的成本所在。GitHub Actions 的"免费 macOS runner"实际上是 Apple Silicon Mac mini 集群封装的，自建意味着要采购、维护、电力。Ghostty 选择了 Buildkite + 自托管 macOS 节点的方案。

| 成本项 | GitHub Actions | 自建 |
|--------|----------------|------|
| macOS runner | 免费但有 quota | 一台 Mac mini M4 Pro ~$1,500 一次性 |
| Linux runner | 免费 | 现有云账号即可 |
| Cache | 免费 10GB | 需自建 S3 + nginx |
| Artifacts | 免费 | 自建对象存储 |
| 维护成本 | 0 | ~5h/月 |
| 故障时停机 | 完全失控 | 自己可控 |

对一个有捐赠收入的非盈利项目来说，**每月 1-2k 美元和 5 小时维护时间** 换回完全的可控性，这笔账算得过来。

## 三、为什么是 2026 年这个节点？

我看到很多评论说"Hashimoto 是个 OSS 老派代表，搞个理想主义"。我不同意。**2026 年是 GitHub 用户体验真正下行的转折点**，背后有三股力同时起作用：

### 力 1：AI 工作负载吞噬基础设施

The Pragmatic Engineer 4 月的那期 *AI load breaks GitHub – why not other vendors?* 揭示了一个不太被讨论的事实——**GitHub 现在是全球 LLM agent 的最大流量入口之一**。Cursor、Cline、Claude Code、Codex、Aider……每一个 AI 编程工具都在做：

1. clone 用户的仓库（重读流量）
2. push agent 修改后的分支（重写流量）
3. 调用 Actions API 运行 CI（计算密集流量）
4. 在 Issues/PRs 里写评论（API 流量）

GitHub 内部的负载模型是按"人类开发者每小时几次操作"设计的，而现在的 agent 是**每秒几次操作**。结果就是 GitHub Actions 队列阻塞、API rate limit 越来越严、HTTP 5xx 比例肉眼可见上升。

GitHub 不是没察觉。它推出 GHEC tier、Copilot Workspaces、Agentic Workflows，但这些都是在**继续把 GitHub 往"AI 控制台"方向推**，而不是修复底层的容量问题。这就是 Hashimoto 真正的痛点：**GitHub 在战略上不再优先服务"想认真写代码的人"**。

### 力 2：Microsoft 控制权的逐渐显形

GitHub 2018 年被微软收购至今 8 年，前 5 年保持了显著的独立性（Friedman 时代）。但从 2023 年 Thomas Dohmke 接任 CEO 后，路径越来越清晰：

- 2023：Copilot 集成深化（GitHub 用户数据训练 Codex）
- 2024：Actions runner 跟 Azure 深度绑定
- 2025：所有新 feature 优先 GHEC（GitHub Enterprise Cloud）而非 GHES（self-hosted）
- 2026：GitHub Models（直接在仓库里调 Azure OpenAI）

对企业客户这或许是 vendor lock-in 的胜利。对 Hashimoto 这类"我只想写代码"的用户，则是 **GitHub 越来越不像一个独立工具，而像 Azure 的前门**。

### 力 3：Forgejo / Codeberg / sourcehut 这一代替代品成熟

5 年前，"逃离 GitHub" 是一个需要承担巨大代价的决定，因为没有像样的替代品。GitLab 太重、Gitea 商业化路径不清晰、sourcehut 太极客。

2026 年，情况彻底变了：

| 平台 | 模式 | 用户量 (2026 Q1) | 关键特性 |
|------|------|------------------|---------|
| Forgejo (self-hosted) | AGPL + 非盈利 | 13.2 万实例 | Actions 兼容、ActivityPub 联邦 |
| Codeberg | Forgejo 托管 | 13 万账号 | 欧洲非盈利、免费 |
| sourcehut | 极简 + 邮件流程 | ~1.5 万付费 | 完全无 JS 的 UI |
| Tangled | atproto 上的 git forge | 内测中 | 完全去中心化 |
| Radicle | P2P git | 6,000 节点 | 加密签名 + 无中心 |

**ActivityPub 联邦是这一代 forge 的杀手锏**。Forgejo 11（2026 H1）将开启 federated PR——你可以在 Codeberg 上对 git.ghostty.org 的项目提 PR，就像你在 Mastodon 上@ 一个 Twitter 用户。这是结构性的"去 GitHub 化"基础设施。

## 四、迁移真正的代价：失去什么？

我反复强调 Ghostty 的"GitHub Star = 33,000"不是炫耀，而是想说明一个事实：**GitHub 提供的不只是托管，更是发现性（discoverability）和社交证明（social proof）**。这是任何自托管 forge 无法完全替代的。

具体损失清单：

| 失去的东西 | 影响 | 缓解方案 |
|-----------|------|---------|
| Trending 流量 | 新用户获取受影响 | GitHub 镜像 + HN/Lobsters 持续输出 |
| GitHub Sponsors | 捐赠通道损失 | Open Collective + 直接 sponsor |
| Star count 社交证明 | 招聘和投资演示难 | 用 download count / contributors 替代 |
| 跨项目 @user mention | 协作摩擦 | ActivityPub 解决（成熟后） |
| GitHub Notifications 统一收件箱 | 不便 | RSS/email 自定义聚合 |
| 已建立的 PR review 习惯 | 早期阵痛 | Forgejo 的 UI 与 GitHub 高度相似，过渡成本中等 |

Hashimoto 在文章里坦承"我会想念它"。他不是在反 GitHub，他在反"GitHub 作为唯一选项"。

## 五、跨领域类比：当工具走过了"良性垄断"窗口

如果我们把这件事放到更长的产业史里看，会发现一个清晰的模式：

```text
工具 / 平台         良性垄断起点      转折点信号                  替代方案成熟
─────────────────────────────────────────────────────────────────────────
SourceForge        2000             2007 病毒广告 / UI 崩坏       GitHub 起来
Stack Overflow     2008             2022 LLM 训练数据剥削         Discord / DevHub
Docker Hub         2014             2020 公开仓库限流              GHCR / quay.io
Twitter API        2010             2023 收购后 API 收费           Bluesky / Mastodon
GitHub             2008             2025-26 AI load + Azure 化    Forgejo 联邦
```

每一次"良性垄断"的终结都需要三个条件同时成立：
1. **平台体验下降到痛点阈值**（GitHub 已达成）
2. **替代品技术上可行**（Forgejo 已达成）
3. **意见领袖公开迁移**（Hashimoto 是第一个，但不会是最后一个）

我的预测是：**未来 18 个月，至少有 5 个 GitHub 上 10k+ star 的项目会做类似迁移**——已经在酝酿的有 Zig 编译器本体（早就在自己的 ziglang.org/git 上）、Astral 旗下的 uv/ruff（Tailscale 已经表态过对 GitHub 不满）、以及部分 CNCF 项目。Astral CTO Charlie Marsh 2 月在播客里说过"我们在评估 federation"——这不是空话。

## 六、对你的启示：开发者的实操建议

如果你是个人开发者或小团队 maintainer：

1. **现在就开始让你的 CI 配置可移植**。把 GitHub Actions 限定在 `.github/workflows/`，避免大量使用 GitHub-only 的 Action（`actions/checkout` 没事，`peter-evans/something` 这种第三方就要小心）。Forgejo Actions 兼容 GitHub Actions YAML，但只兼容到"runs-on/uses/run/with"这一层，复杂 marketplace action 多数不工作。

2. **把 issue tracker 当 source of truth 备份**。每周 `gh issue list --json` 一次，提交到仓库。同样对 PR、discussion 做同样的事。

3. **认真考虑 Codeberg 双写**。设置 GitHub Actions 自动 mirror push 到 Codeberg。这不是叛逃，是冗余。任何写"GitHub is fine"的人都没经历过 2023 年 SourceForge 突然把你的项目当成色情广告的窗口。

4. **如果你想留在 GitHub**，至少要做到"任何 CI 都能在 30 分钟内迁出"。把这当作灾备演练。

如果你是技术决策者：

1. **明确区分"内部代码"和"外部协作"**。前者用什么 forge 完全是 SLA 和成本问题，GitLab self-hosted 或 Forgejo 都很好。后者才需要 GitHub。
2. **关注 ActivityPub 联邦标准的发展**。一旦 Forgejo 联邦走通，企业 forge 加入开源 PR 流的成本会陡降。
3. **不要把"GitHub Stars"作为评估开源项目的硬指标**。这会让你越来越偏向喜欢做 marketing 的项目而非真正在写代码的项目。

## 七、判断：GitHub 不会"垮"，但"垄断"会松动

最后给一个明确的预测。

**GitHub 不会在 5 年内被超越——它的网络效应、与 Azure 的协同、企业市场的渗透都太深。** Ghostty 离开不代表 GitHub 死掉了。

但 **"GitHub = Open Source" 这个等号正在被擦掉**。未来 3-5 年的格局会是：
- **GitHub** 仍然是"商业代码 + 企业级协作"的主场
- **Forgejo 联邦**成为"理想主义 OSS 项目"的主场
- **Radicle / Tangled** 这类 P2P forge 拿到"绝对去中心化"的小众市场
- **Cursor/Codeium 这种 IDE 内嵌的 agent forge**（直接在 IDE 里完成 PR review，bypass git host UI）开始抢占 30% 的日常工作流

对 Hashimoto 来说，离开 GitHub 是悲伤的。对 OSS 生态来说，这是健康的。**一个工具一旦让其用户的快乐变得"无理性"（irrational），意味着它已经超出了工具应有的位置**。Hashimoto 在文章末尾说的那句"我希望有一天能回来，但这要取决于真实的改进而非承诺"——这是给 Dohmke 的一封公开信。

至于他会不会回来？我的猜测是：**不会。** 因为 Ghostty Foundation 一旦完成迁移，它的成员、流程、肌肉记忆都会绑定到 Forgejo 上。这是 Switching Cost 的反向——一旦你逃离了，你不会回去。Twitter → Bluesky 的迁移者很少回去，IRC → Discord 的迁移者很少回去。同样的规律会在这里发生。

GitHub 的真正风险不是 Hashimoto 一个人离开，而是 **18 年的忠诚都换不来一个像样的可靠性承诺**——这件事，每个开源 maintainer 都会记在心里。

---

## 参考来源

- [Mitchell Hashimoto — Ghostty Is Leaving GitHub](https://mitchellh.com/writing/ghostty-leaving-github) (Mitchell Hashimoto 个人博客, 2026-04-28)
- [Mitchell Hashimoto — Ghostty Is Now Non-Profit](https://mitchellh.com/writing/ghostty-non-profit) (Mitchell Hashimoto 个人博客, 2026-03)
- [Mitchell Hashimoto — Welcoming Ghostty Subsystem Maintainers](https://mitchellh.com/writing/ghostty-subsystem-maintainers) (Mitchell Hashimoto 个人博客)
- [The Pragmatic Engineer — The Pulse: AI load breaks GitHub – why not other vendors?](https://newsletter.pragmaticengineer.com/) (Gergely Orosz)
- [ACM Queue — Open Source and the Iceberg Theory](https://queue.acm.org/detail.cfm?ref=rss&id=3799738) (ACM Queue, 2026-03)
- [Forgejo Blog — Forgejo 10 release](https://forgejo.org/2025-09-release-v10/)
- [Codeberg e.V. — Annual Report 2025](https://codeberg.org/Codeberg/org)
- [Cloudflare — Building the agentic cloud: Agents Week 2026](https://blog.cloudflare.com/)（用于对比 agent 工作负载量级）
