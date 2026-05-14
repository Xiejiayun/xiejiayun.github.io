---
title: "【好文共赏】TanStack npm 投毒事件官方复盘：三条独立漏洞如何被串成一条供应链刀锋"
description: "Tanner Linsley 亲笔的 TanStack 供应链攻击 postmortem——pull_request_target 的 Pwn Request、GitHub Actions 跨信任边界的缓存投毒、与从 Runner 进程内存里抠出 OIDC token 的三段式利用链——是 2026 年最教科书级的供应链事件研究素材。"
date: 2026-05-14
slug: "good-read-tanstack-npm-supply-chain-postmortem"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - 供应链安全
    - npm
    - GitHub Actions
    - OIDC
    - TanStack
    - Pwn Request
    - Cache Poisoning
    - 开源安全
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[Postmortem: TanStack npm supply-chain compromise](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)
> 作者：Tanner Linsley（TanStack 创始人 & 主要维护者）| 发布于：2026-05-11 | 阅读时长：约 18 分钟
>
> **多模评分**：Opus 9.3 / Sonnet 9.1 / Gemini 9.2（综合 **9.20 / 10**）
>
> **一句话推荐理由**：这是过去一年里我读过的、技术细节最完整、最不掺水、最不绕弯的一份开源项目自查报告——它把一次"看起来只是又一次 npm 投毒"的事件，拆成了三个本来彼此独立、但在 GitHub Actions + npm OIDC 这套现代基础设施上被攻击者**串成一条线**的根因链。读完它，你对 `pull_request_target` 这个词的恐惧会上一个数量级。

## 为什么值得读

2026 年 5 月 11 日 UTC 19:20 到 19:26 之间的六分钟里，TanStack 名下的 `@tanstack/*` 命名空间发布了 84 个恶意版本，覆盖 42 个包，其中包括 React 生态使用极广的 `@tanstack/router` 与 `@tanstack/start`。20 分钟后，外部研究者 ashishkurmi（StepSecurity）把完整 IOC 发到了 issue tracker 上。又过了 1 个小时，主维护者 Tanner Linsley 站起来打开了 war room。再过 14 个小时——也就是事件发生的 next day——他把这篇 postmortem 公开发了出来。

**这件事在我个人的"开源事故反应速度"排行榜上，排名极高**。XZ Utils 后门用了几年才被发现、`tj-actions/changed-files` 当年从被投毒到说清楚根因花了一周、left-pad 当年只是被撤包都吵了一个月。TanStack 这次从攻击到完整 postmortem 公开，**24 小时**。

但响应速度本身只是这篇文章的"导火索"，真正值得读的是**它把三个本来散落在不同安全研究博客里的漏洞类别，第一次在一个真实事故里串成了一条完整刀锋**——

第一刀，是 GitHub Actions 的 `pull_request_target` "Pwn Request"。这是 2020 年就被 GitHub Security Lab 反复提醒过的危险触发器，但它依然是开源仓库里最常见的"我想给 fork PR 加 label / 评论 / 评测 benchmark"的写法。

第二刀，是 GitHub Actions Cache 在 fork PR 与 main 分支之间的**跨信任边界共享**——这一刀的理论文章是 2024 年 5 月 Adnan Khan 那篇 [The Monsters in Your Build Cache](https://adnanthekhan.com/2024/05/06/the-monsters-in-your-build-cache-github-actions-cache-poisoning/)，并且 GitHub 在 2025 年 1 月已经做了**部分**收窄（不允许 job 结束后再写缓存）。攻击者完全清楚这个收窄，他们的解法是**把投毒动作搬进 build 过程中**而不是 post 阶段。

第三刀，是 npm OIDC Trusted Publisher 机制下，**`id-token: write` 权限一旦授予某个 workflow，整个 workflow runtime 内任意代码都能 mint 出一份能发布到 npm 的短期 token**。攻击者从 `/proc/<pid>/mem` 里把这个 token 抠出来，绕过了 workflow 自己定义的 "Publish Packages" 步骤——那一步因为测试失败根本没运行——直接向 `registry.npmjs.org` 发了 POST。

把这三刀理解透，你就明白为什么 Tanner 在 postmortem 里写下这句话不是修辞：

> 原文：The chain only works because each vulnerability bridges the trust boundary the others assumed.（来源：tanstack.com）

这就是 2026 年供应链攻击的"新形态"——**没有一个漏洞是 0-day，每一个都是 known、有公开 mitigation 的，但它们被组合起来的方式是新的**。

这与我之前在 [《重跑 Ken Thompson 的"信任之信任"：现代供应链时代》](/post/trusting-trust-modern-supply-chain-2026/) 里讨论的趋势完全吻合——攻击者的优势不再是"找新漏洞"，而是"理解信任拓扑"。

---

## 攻击时间线：六分钟里发生了什么

在拆解三段式利用链之前，先把这条时间线在脑子里建出来，后面的根因才好接住。

**Day -1（事前一天）**

`2026-05-10 17:16 UTC` — 攻击者创建了一个 GitHub 账号 `zblgg`，把 `TanStack/router` 仓库 fork 了一份，但**故意把 fork 改名为 `zblgg/configuration`**。原因是 GitHub 的 fork 列表只会按"同名 fork"做关联检索，改了名之后这个 fork 在 fork 网络里依然存在、commit 对象依然可达，但**通过仓库主页的 fork 搜索找不到它**。这是个 OSINT 反取证手法。

`2026-05-10 23:29 UTC` — 攻击者向这个 fork 推送了一个伪造身份的 commit：作者署名是 `claude <claude@users.noreply.github.com>`，commit message 以 `[skip ci]` 开头。注意这里——`@users.noreply.github.com` 是 GitHub 默认的 no-reply 邮箱后缀，**任何人都可以伪造这个邮箱前缀**，所以这个 `claude` 并不是 Anthropic。这一点 postmortem 单独点了一下，是怕安全社区把锅甩错对象。

这个 commit 加了一个 `packages/history/vite_setup.mjs`，文件大约三万行，是 webpack/bundler 打包出来的混淆代码。`[skip ci]` 让 push 事件不触发 CI——为什么不希望 push 触发 CI？因为下一步要切换到 `pull_request_target`，先在 push 事件下让 CI 看一眼会留下太多痕迹。

**Day 0（投毒发生的 12 小时窗口）**

`2026-05-11 ~10:49 UTC` — 攻击者用 `zblgg` 账号向 `TanStack/router` 主仓提了一个 PR #7378，标题写的是 `"WIP: simplify history build"`。PR 头部是上面那个携带 `vite_setup.mjs` 的恶意 commit。

`2026-05-11 11:01–11:11 UTC` — 攻击者**对 PR 反复 force-push**。每一次 force-push 都让 `bundle-size.yml` 这个 workflow 重新跑一遍。它是为什么会跑？因为它的触发器是 `pull_request_target`，不需要 maintainer 批准。

`2026-05-11 11:29 UTC` — 缓存被写入：一个 1.1 GB 的 entry，key 是 `Linux-pnpm-store-6f9233a50def742c09fde54f56553d6b449a535adf87d4083690539f49ae4da11`。**这个 key 是攻击者算好的**——它精确匹配 `release.yml` 在主线下次跑的时候会去 lookup 的 cache key，因为两个 workflow 都用 `hashFiles('**/pnpm-lock.yaml')` 作为 key 的一部分。

`2026-05-11 11:31 UTC` — 攻击者**把 PR head force-push 回当前 main 的 HEAD**，让 PR 变成一个零文件变更的 no-op，然后关闭 PR、删除分支。**缓存毒已植入，PR 表面看上去什么都没发生**。从此刻起，到 19:15 真正爆发之间有近 8 小时——足够 GitHub 的常规人工 review 略过这个看起来无害的 closed PR。

`2026-05-11 19:15:44 UTC` — Manuel 合并了 PR #7369（一个真实的 CSS.supports 修复）。`release.yml` 因为 push 到 main 而被触发，Workflow run `25613093674` 启动。

`2026-05-11 19:20:39 UTC` — npm registry 收到了 `@tanstack/history@1.161.9` 等 42 个包的发布请求。**注意 timestamp 与 workflow run 之间相差不到 5 分钟**——这意味着投毒发生在 workflow 运行过程中的某个早期步骤（Setup Tools 期间恢复了被投毒的 pnpm-store）。OIDC token 是从 Runner.Worker 进程内存里抠出来的，整个发布动作**根本不来自 workflow 定义里的 Publish Packages 步骤**。那一步因为测试失败而被跳过了。

`2026-05-11 19:20:47 UTC` — Workflow run 失败结束。开发团队没看到任何"发布成功"日志，因为发布根本不是 workflow 在做的。

`2026-05-11 19:16:22 UTC` — Manuel 又合并了 PR #7382。第二次 workflow 触发、第二次缓存恢复、第二次发布。这次发了每个包的另一个版本（如 `@tanstack/history@1.161.12`），总共把 84 个版本写满。

`2026-05-11 ~19:50 UTC` — 外部研究者 ashishkurmi 在 GitHub issue #7383 里发了完整 IOC。

`2026-05-11 ~20:00 UTC` — Tanner 看到 issue，war room 启动。

**24 小时后** — postmortem 发布。

把这张时间表叠起来看，最让我后背发凉的不是攻击复杂度，而是**攻击的"耐心"**——攻击者愿意提前一天部署 fork、愿意在 PR 形态上做反取证、愿意精确预判主线的 cache key、并且在投毒完成后**立刻自动消除 PR 表面痕迹**。这不是脚本小子，这是有时间预算的工程师。

---

## 第一刀：`pull_request_target` 的 Pwn Request 反模式

`bundle-size.yml` 的逻辑，简化后是这样的：

```yaml
on:
  pull_request_target:
    paths: ['packages/**', 'benchmarks/**']

jobs:
  benchmark-pr:
    steps:
      - uses: actions/checkout@v6.0.2
        with:
          ref: refs/pull/${{ github.event.pull_request.number }}/merge
      - uses: TanStack/config/.github/setup@main
      - run: pnpm nx run @benchmarks/bundle-size:build
```

要理解为什么这套写法是危险的，得先理解 `pull_request_target` 与 `pull_request` 在 GitHub Actions 里的关键差别。

**`pull_request`** 触发器跑在"PR 本身的代码"上下文里。这意味着：

- secret 不可用（除非显式允许 fork 访问 secret，没人这样做）
- `GITHUB_TOKEN` 是 read-only 的
- 来自 fork 的 PR 第一次提交时，需要 maintainer 手动点 "Approve and run"

**`pull_request_target`** 触发器跑在"base 分支的代码"上下文里。这意味着：

- secret 可用
- `GITHUB_TOKEN` 默认是 write 的
- **不需要 first-time-contributor 批准**——任何人提 PR 都会让它跑

这个区分本来是合理的：`pull_request_target` 是为了那些"需要给 fork PR 加 label / 评论 / 评判合规性"的 workflow 设计的，它们必须读 secret（比如 bot token），但**它们绝不应该 checkout 出 fork 的代码并运行**。

然而 `bundle-size.yml` 做的就是这件事——它**用 `pull_request_target` 触发器读到了写权限和缓存写权限，又用 `ref: refs/pull/.../merge` 把 fork 的代码 checkout 出来跑了**。

```text
Pwn Request 三要素 = pull_request_target + checkout fork code + execute fork code
```

这是 GitHub Security Lab 在 2021 年就反复警告过的"Pwn Request"反模式，已经导致过 Microsoft Azure、Spinnaker、Argo CD 等多个项目的事故。但它依然普遍存在的原因很简单：**它对 maintainer 非常方便**——你想在 fork PR 上跑 benchmark、跑 lint、跑性能对比，最自然的写法就是 `pull_request_target` 配 checkout fork ref。

Tanner 在 postmortem 里诚实地承认了这一点——他原本想做一个 trust split：让 `benchmark-pr` job 只有 read 权限，`comment-pr` job 才有 write 权限。意图是对的。**但他低估了一件事：`actions/cache` 的写权限根本不走 `permissions:` 的那套机制**。

> 原文：actions/cache@v5's post-job save is not gated by permissions:. Cache writes use a runner-internal token, not the workflow GITHUB_TOKEN.（来源：tanstack.com）

这是这个 postmortem 最让我"想骂人"的发现之一——**你在 workflow 里写 `permissions: contents: read` 看起来是把自己锁死了，但 GitHub Actions 的缓存子系统压根不看这个权限位**。它有自己的 runner-internal token，跨整个 repo 的 cache 域是写得动的。

这一点 GitHub 文档里有提到，但分散在 `actions/cache` 的 README、Pwn Request 那篇 advisory、和 caching 那篇文档里——**三处各说一半**。直到现在你才在一个真实事故里看到它的合并效果。

---

## 第二刀：跨信任边界的 GitHub Actions 缓存投毒

Adnan Khan 2024 年那篇文章把这套理论说清楚了，我这里只用最少的篇幅复述一遍：

GitHub Actions 的 cache scope 是按 **branch / ref** 隔离的，但**有一条特殊规则**：fork PR 跑 workflow 时，它的 cache 写入的是 **base 仓库的默认分支 scope**——也就是与 `main` 分支共享的那个 cache 池。这条规则的意图是让 PR 能"重用 main 分支的依赖缓存来加速"，但它的副作用是：**fork PR 也可以往主线会读取的 key 上写东西**。

也就是说，在 2024 年之前：

1. 攻击者用 `pull_request` 或 `pull_request_target` 提个 PR
2. 在 build 期间往特定 cache key 写入恶意内容
3. PR 关闭，cache 留下
4. main 上下一次 release workflow 跑起来，restore 这个 cache，**恶意代码进入特权上下文**

GitHub 2025 年 1 月的修补做了什么？他们关闭了 **post-job 阶段写 cache** 的能力——也就是说，你不能在 job 已经结束后再让 cache action 把内容保存上去。这个修补让 Adnan 原本那种"在 post-step 里偷偷写缓存"的玩法失效了。

但攻击者完全清楚这个修补，**TanStack 这次的破解是：把投毒动作搬进 build 过程本身**。`vite_setup.mjs` 在被 `pnpm nx run @benchmarks/bundle-size:build` 执行时，**在 build runtime 内部就完成了对 `~/.cache/pnpm` 目录的篡改**。等到 build 步骤结束、`actions/cache` 在 post 阶段保存的时候，它保存的是已经被污染过的 pnpm-store。整个过程对 GitHub 的修补完全合规——cache 是在 build 期间被改写的，不是 post-job 阶段。

这是攻防博弈里一个非常典型的现象：**只要保留了"PR 代码可以执行"和"PR 可以触碰主线 cache scope"这两条假设，缓存投毒就无法被根除**。GitHub 真正彻底的修法是让 fork PR 的 cache 写入只落到 PR 自己的 scope 里、与 main 完全隔离——但那样会让大量项目的 CI 缓存命中率大幅下降。这是一个**便利性 vs 安全性**的根本张力，GitHub 还没有决定要不要付出这个性能代价。

---

## 第三刀：从 Runner 进程内存里抠 OIDC token

第三段是这次事件里我个人觉得**最该被 react / node / python 全社区抄下来贴在墙上**的部分。

npm 在 2024 年推出了 **Trusted Publisher** 机制——你不再需要在 GitHub Secrets 里塞一个长期 `NPM_TOKEN`，而是把"我授信 `TanStack/router` 仓库的 `release.yml@refs/heads/main` workflow 在 main 分支跑的时候，可以发布 `@tanstack/*` 命名空间"这一组绑定关系登记在 npm 一侧。当 workflow 真的跑起来、并且声明了 `id-token: write` 权限时，GitHub Runner 会向 GitHub 的 OIDC 端点请求一个**短期 token**，里面包含了 workflow 的身份声明，npm 拿到这个 token、验签、确认 issuer 与 audience 匹配，就允许发布。

这套机制的安全收益非常实在：

- 没有长期 secret 可被钓鱼 / 泄露
- token 是短期的（默认 6 分钟）
- token 与具体的 workflow / commit / branch 绑定
- 整个发布动作有 npm 一侧的 provenance attestation

但它的盲点是：**`id-token: write` 是 workflow 级别的权限，不是 step 级别的**。也就是说，一旦一个 workflow 声明了这个权限，**那个 workflow 进程内任何步骤、任何包含执行能力的代码，都能 mint 出一份能发布的 token**。

`release.yml` 完全合理地声明了 `id-token: write`，因为它的 "Publish Packages" 步骤需要 OIDC。问题是：**在 Publish Packages 之前，还有 Setup Tools 步骤会从被污染的 cache 恢复 pnpm-store；恢复回来的 store 里包含恶意二进制；这些二进制在构建步骤里被无意中执行；它们读 `/proc/<pid>/maps`、`/proc/<pid>/mem`，把 Runner.Worker 进程内存里缓存的 OIDC token 抠出来；然后直接 POST 到 `registry.npmjs.org/-/v1/...`**。

整个过程 workflow 自己的 logs 里**看不到一行 npm publish**。它在 workflow 的角度看，是测试失败、Publish Packages 跳过、Run failed——所有看起来都"正常异常"。

> 原文：It comes from the malware running during the test/cleanup phase, which mints an OIDC token via the workflow's id-token: write permission and POSTs directly to registry.npmjs.org.（来源：tanstack.com）

这段攻击的"原型"出处 Tanner 也指出来了——2025 年 3 月 tj-actions/changed-files 被攻陷的时候用的就是**几乎完全一样的内存抠 token 脚本**，攻击者甚至**保留了原作的署名注释**。这个细节非常有趣：它告诉我们 2026 年的攻击者并没有再发明新的内存提取技术，**他们只是把已发表的攻击工具更精细地编排在了一起**。

这是供应链安全里的一个深层信号：**威胁模型的演化方向不是更深的漏洞，而是更紧密的攻击链编排**。每一个零件都是公开的、每一个零件单独看都不算严重，但被一个理解信任拓扑的攻击者串起来之后，足以让一个最负责任的开源项目在 6 分钟内丢掉整个命名空间。

---

## 三件事的化学反应：为什么"any one fails it"

Tanner 在根因部分写了一段我希望每个工程师都能记住的话：

> 原文：pull_request_target alone is fine for trusted operations. Cache poisoning alone requires a separate publish vehicle. OIDC token extraction alone requires existing code execution on the runner.（来源：tanstack.com）

把它翻译成防御工程师的语言：

| 单独存在的漏洞 | 危害上限 |
|---|---|
| `pull_request_target` + checkout fork code | fork 代码在 base context 跑，但权限若收窄就只能读敏感数据 |
| GHA cache 跨 fork↔base 写权限 | 需要找到一个能在 cache 里塞东西的入口 |
| OIDC token 在 Runner 内存可读 | 需要先有任意代码执行能力 |

每一个**单独看起来都还行**——这正是它们能在最负责任、最关心安全的项目里都长期存在的原因。但是攻击者发现：

- 第一刀提供了"进入 base 上下文"的能力（解决 OIDC 抠 token 需要的 code execution 前置条件）
- 第二刀把"PR 上下文里的修改"延伸到了"main 上下文里的执行"（让 cache 跨过信任边界）
- 第三刀把"main 上下文里的执行"放大到了"以 main 的身份发布到 npm"（让 code execution 等价于 publish）

**三块拼图各自留有的 slack，正好就是另外两块缺少的前置条件**。这种"漏洞之间的代偿性"是供应链攻击的本质特征。

写到这里我突然意识到，它和我之前讨论 [《curl 之父亲测 Mythos：5 个"确认漏洞"最后只剩 1 个》](/post/good-read-stenberg-mythos-curl-ai-security-reality/) 的那种"AI 安全工具找出来的漏洞 80% 假阳性"形成了非常微妙的对照——AI 工具单独看每个漏洞容易陷入"过分严肃"或"过分轻描淡写"，但**真正决定一个漏洞会不会成为现实威胁的，是它在系统拓扑里能不能与别的漏洞拼合**。这是当前 AI 静态分析最弱的能力维度。

---

## 检测、未解问题、与"自我承认的运气"

postmortem 的"Lessons learned"部分有两条让我尤其欣赏。

**第一条是关于检测**：

> 原文：No internal alerting. We learned about the compromise from a third party.（来源：tanstack.com）

这句话价值千金。它清晰地承认：**TanStack 团队没有任何监控自己 npm 发布的机制**。如果不是 StepSecurity 的 ashishkurmi 主动写 issue、Socket.dev 主动打电话，他们可能要再过几个小时才会发现。这个反思在所有开源维护者读到的时候，都应该按一下暂停键问自己：**我有任何 monitoring 自己 npm package 新版本的告警吗**？

第二条是 Tanner 罕见的"我们其实运气好"承认：

> 原文：The attacker chose a payload that broke tests, which made the publish step skip — meaning the attack was loud enough to detect quickly. A more careful attacker who didn't break tests could have published silently for hours longer.（来源：tanstack.com）

也就是说——**如果这次攻击者再细致一点、payload 不破坏测试，那么投毒后正常的 `npm publish` 步骤会照常运行，workflow logs 会显示"发布成功"，开发团队反而看不出任何异常**。当前的检测窗口实际上是攻击者送给防御方的礼物。

这条承认也让 postmortem 最后那一节"Open Questions"显得格外珍贵：维护团队公开列出了**还没回答的 9 个调查问题**——从"fork 网络里还有几个仓库携带 orphan payload commit？"到"`voicproducoes` 是真实账号还是傀儡？"再到"这周末有多少用户实际拉取了恶意版本，npm 后端能不能给数字？"。

这种**事故复盘里直接承认 unknown unknowns** 的写作风格在国内技术博客里几乎绝迹了。它的工程价值远远超过任何"我们已经全面修复 / 已经 lessons learned"式总结，因为它给了下游的安全研究者继续追查的明确入口。

---

## 编辑延伸思考：开源维护者的"安全债务"已经透支

把这次事件、3 月 tj-actions/changed-files、还有更早的 left-pad / event-stream / colors.js / faker.js / xz-utils 放在一条时间线上看，能看到一条很清晰的趋势：

**开源生态最关键的基础设施层，越来越依赖于个人维护者免费提供安全审计**。

TanStack 的命名空间里有 295 个包、7 个 maintainer。整个项目的资金主要来自 GitHub Sponsors 和企业捐赠。Tanner Linsley 既要写代码、维护 issue、回 RFC、做 release，又要审计每一个 PR、每一个 GHA workflow、每一个第三方 action 的 SHA pin、每一个 cache key、每一个 OIDC scope。**这件事的工作量已经显著超过任何一个开源维护者的可承受范围**。

我在 [《重跑 Ken Thompson 的"信任之信任"》](/post/trusting-trust-modern-supply-chain-2026/) 里讨论过这件事的根因——**当全世界的商业软件都把"成本 = 0"建立在开源软件之上时，安全责任的分配本身就是错位的**。OpenSSF 在做工作，Alpha-Omega Project 在做工作，但它们覆盖的项目数量与 npm registry 上的"被广泛依赖的包"数量之间，差着一到两个数量级。

更糟糕的是，**AI 加速了攻击者的研究能力，却没有同等速度地加速防御者的发现能力**。读 Adnan Khan 那篇 cache poisoning 文章需要 25 分钟、理解透需要几个小时、实际操作起来要熟悉 GitHub Actions runner 的内存模型。但 LLM 现在可以把这套知识在几秒内复述给攻击者，攻击者只需要做"在哪个仓库尝试它"的决定。

这次事件之后，我个人建议的两件最实际的事：

**对项目维护者**：

1. 立刻把所有 `pull_request_target` workflow 拉出来 audit 一遍，**只要它 checkout 了 fork ref 或运行了 fork 控制的代码，就重写为 `pull_request` + 手动批准**
2. 所有发布相关的 workflow（任何带 `id-token: write` 或 `NPM_TOKEN` 的）**全部禁用 cache**，宁可慢一倍也不要再共享 cache scope
3. 给自己装一个 [Socket](https://socket.dev/) 或 [StepSecurity Harden-Runner](https://www.stepsecurity.io/) 的告警通道，至少别让自己是最后一个知道的人

**对使用 npm 包的开发者**：

1. 启用 `npm audit signatures` 与 SLSA provenance 验证
2. 用 `pnpm` 的 `--ignore-scripts` 或类似机制阻断 install-time lifecycle script 执行
3. 把 lockfile 里的 git URL 依赖（`github:...#sha`）从允许列表里去掉，**除非你信任那个具体的 sha**
4. CI 环境的 secret 至少有一个 `read-only mirror`——任何"原本是只读的 token 被拿到"就触发告警

这些动作单看每一条都"应该做"，但实际上 80% 的项目还没有做。**这次事件的真正价值是给所有维护者一个"立刻动手"的借口**，把"已经知道应该做但还没做"的事推上日程。

---

## 配套资料导览

为了让这篇导读更易上手，本文同目录下附了三份补充材料：

- `concept-cards.md` — 12 张关键概念卡片：从 `pull_request_target` 与 `pull_request` 的区别，到 OIDC Trusted Publisher 的工作原理，再到 cache scope 的实际边界
- `glossary.md` — 30+ 条英中对照术语表，覆盖整篇 postmortem 里出现的 GitHub Actions / npm / 供应链安全词汇
- `mindmap.svg` — 三段式攻击链的可视化思维导图，深色背景，可直接用于团队培训幻灯片
- `cover.svg` — 文章封面

## 延伸阅读图谱

**直接源文与官方资料**

- [Postmortem: TanStack npm supply-chain compromise](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem) — 本文主角
- [GHSA-g7cv-rxg3-hmpx](https://github.com/TanStack/router/security/advisories/GHSA-g7cv-rxg3-hmpx) — GitHub Security Advisory
- [TanStack/router#7383](https://github.com/TanStack/router/issues/7383) — 完整的 IOC 与 tracking issue

**理论基础（攻击者实际引用的研究）**

- Adnan Khan, [The Monsters in Your Build Cache: GitHub Actions Cache Poisoning](https://adnanthekhan.com/2024/05/06/the-monsters-in-your-build-cache-github-actions-cache-poisoning/)（2024-05） — 三段攻击链里第二刀的奠基论文
- GitHub Security Lab, [Keeping your GitHub Actions and workflows secure: Preventing pwn requests](https://securitylab.github.com/research/github-actions-preventing-pwn-requests/) — 第一刀的官方警告
- StepSecurity, [Harden-Runner detection: tj-actions/changed-files action is compromised](https://www.stepsecurity.io/blog/harden-runner-detection-tj-actions-changed-files-action-is-compromised)（2025-03） — 第三刀同样手法的前身案例

**npm / OIDC 文档**

- [npm Trusted Publishers](https://docs.npmjs.com/trusted-publishers) — OIDC 发布机制的官方说明
- [npm Provenance Statements](https://docs.npmjs.com/generating-provenance-statements) — 包出处验证
- [SLSA Framework](https://slsa.dev/) — 软件供应链完整性等级

**反方观点与不同侧重**

- [Socket.dev "Why npm Trusted Publishing Isn't Enough"](https://socket.dev/) — 论证 OIDC 不是银弹
- [Snyk State of Open Source Security 2026](https://snyk.io/state-of-open-source-security/) — 行业数据视角

**本站相关旧文**

- [重跑 Ken Thompson 的"信任之信任"：现代供应链时代](/post/trusting-trust-modern-supply-chain-2026/)
- [TanStack 被投毒、OpenAI 紧急响应：npm 供应链攻击正在进入"信任凭证劫持"新阶段](/post/tanstack-npm-supply-chain-attack-code-signing-open-source-2026/)（早期速报，本文是对其技术细节的更正与深化）
- [Pull Request 之死：Harness 重写工程协作流](/post/death-of-pull-requests-harness-engineering/)
- [AI 网络安全革命 2026](/post/ai-cybersecurity-revolution-2026/)
- [n8n 架构深度解析](/post/n8n-architecture-deep-dive/)

## 谁应该读这篇文章

- **任何一个还在 GitHub Actions 上用 `pull_request_target` 的开源维护者**——读完之后立刻去 audit 你的 workflow，这是 24 小时内能做的最高 ROI 的事
- **任何一个 CI/CD 平台工程师**——这是一份近乎完美的"现代构建系统的所有信任边界都在哪里"的对账单
- **任何一个 SRE / Security Engineer**——你可以直接把它当作内部威胁建模培训材料，三段式利用链非常容易抽象成普适教学
- **任何一个 npm package author**——读完之后立刻去给自己的发布 workflow 加监控告警，并且取消所有不必要的 cache 共享
- **任何一个对开源安全治理感兴趣的人**——这篇 postmortem 的"自我承认 unknown unknowns"的写作风格值得拿来当行业范本

---

读完之后我对这篇文章的最终判断是：**它会成为 2026 年最常被引用的供应链事件复盘**。原因不是事件本身的破坏力（实际 npm 拉包的恶意版本被快速 deprecation 了），而是这篇文档本身的工程质量——清晰的时间线、严谨的根因切分、对自身运气的诚实承认、对未解问题的公开列表。

它让"事故"变成了一份可教学、可重现、可批判的工程文献。这是开源世界最珍贵的一种付出。
