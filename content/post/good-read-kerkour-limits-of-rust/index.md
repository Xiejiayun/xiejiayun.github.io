---
title: "【好文共赏】Rust 的边界在哪里：Black Hat Rust 作者 Kerkour 写给所有\"想抄 Cloudflare 作业\"的团队一封劝退信"
description: "Sylvain Kerkour（Black Hat Rust 作者）在 2026 年 5 月发表逆主流长文，论证 Amazon/Cloudflare/Discord 那条 Rust 化路径不适合大多数团队。本文拆解他的 4 类反对论点（async 难、版本腐化、std lib 贫血、生态碎片），整理 5 个真正适合 Rust 的场景，并与本站 io_uring 异步运行时分裂分析、TanStack 供应链事故、Linux kernel copyfail 等旧文交叉对照。"
date: 2026-05-15
slug: "good-read-kerkour-limits-of-rust"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Rust
    - 编程语言
    - 技术选型
    - 软件工程
    - 异步运行时
    - 生态系统
draft: false
---

## 1. 编辑推荐框

> 📌 **好文共赏 | Editor's Pick**
> 原文：[The limits of Rust, or why you should probably not follow Amazon, Cloudflare and Discord](https://kerkour.com/the-limits-of-rust)
> 作者：Sylvain Kerkour（《Black Hat Rust》作者 / 安全工程师）
> 发布：2026-05-13
> 阅读时长：约 14 分钟（英文原文）
> 多模评分：Opus 8.7 / Sonnet 8.5 / Gemini 8.4 / **综合 8.53 / 10**
> 一句话推荐：当所有人都在喊"用 Rust 重写一切"的 2026 年，一位写 Rust 安全书的人站出来说："**你大概率不该跟**——除非你的团队已经全员 Rust 专家。"这是一封写给中型工程团队的、罕见诚实的反主流指南。

---

## 2. 为什么值得读

最近 12 个月，Rust 在主流叙事里几乎成了一种"政治正确"。Linux kernel 接纳 Rust，Windows 内核组件用 Rust 重写，Cloudflare 把 nginx 替换成 Pingora，Discord 把 Go 换成 Rust，Amazon 的 Firecracker 整套 microVM 跑在 Rust 上，5 月 14 日 Bun 团队也宣布把 Bun 从 Zig 重写为 Rust 的 PR 合并了。一个想认真做技术选型的 CTO 此刻打开任何技术媒体，都会被同一个隐含结论包围：**你不在 Rust 的车上，你就在被淘汰的列车上**。

Sylvain Kerkour 的这篇文章之所以稀有，在于他从**反方向**站出来说话——而且他不是 Rust 黑：他写了《Black Hat Rust》这本被多家高校用作攻击式安全教材的书，他自己长期用 Rust 做渗透工具、嵌入式设备、数据库基础设施。一个"懂 Rust 的人"反过来劝大多数团队**不要**用 Rust，这种 self-disqualifying 的立场比任何 fanboy/hater 的叫喊都更值得严肃对待。

更重要的是，他的论证不是抽象哲学，而是 6 年实战之后的具体疼痛清单：

- async 让团队反复在事件循环阻塞与 ownership 撕裂之间打补丁；
- 6 周一次的 Rust release + 2020 年以来 54 个版本 + 多个 edition 让"放在那儿三年不动"的项目变成债务地狱；
- 标准库的"贫血"让任何稍微现实的项目都拖着 5 个版本不同的 crypto crate；
- ring / aws-lc-rs / boring / RustCrypto 同时存在的生态碎片，让安全审计变成一种奢望；

而文章后半段他又非常坦诚地列了**5 个 Rust 真正赢的场景**——这种"批判 + 正向地图"的双面结构，正是本站"好文共赏"想推荐的那种**可以直接当团队 checklist 用**的文章。

对中文工程社区尤其重要的一点是：过去两年，大量中型团队（30–200 工程师规模）跟风启动了 Rust 重写，但他们既不是 AWS、也不是 Cloudflare，更没有 Discord 那样的工程文化储备。Kerkour 的这篇文章本质上是写给他们的——也是写给我们的。

（这点与我之前写的[《Rust 异步生态的分裂与重聚：io_uring、Tokio 单极、和一个迟到的标准》](/post/rust-async-runtime-split-io-uring-2026/)中描述的"Tokio 事实垄断 + 标准 Future 半成品躺了七年"完全呼应——Kerkour 几乎是在用工程语言重新讲一遍我那篇文章的生态学结论。）

---

## 3. 核心观点深度解读

### 3.1 论点零：他不是 Rust 黑，他是 Rust 内人

文章开头有一段几乎被多数读者跳过的免责声明，但它恰恰是整篇论证的合法性来源：

> 原文："Coming from someone who wrote a book about Rust (Black Hat Rust) it may be surprising, so, if like me you are never satisfied with a short answer without an explanation, stay with me."

中文社区每次出现"Rust 不适合 X"的文章，下面一定有一群人评论"你不懂 Rust"、"你工程经验不够"、"你只是不愿学难的东西"。Kerkour 在第一段把这条退路堵死：他写了一本被多个高校攻击式安全课程引用的 Rust 教材，他的博客在过去 6 个月里同时发布过：

- 《Cross-platform Rust: How WhatsApp/Signal ship Rust to billions》
- 《All databases will eventually be (re)written in Rust》
- 《Firecracker deep dive: How Rust and microVMs are revolutionizing cloud infrastructure》
- 《SIMD programming in pure Rust》
- 《Towards safe and modern cryptography: state of the Rust ecosystem in 2026》

这些都不是被 Rust 劝退的人会写的文章。**他真正反对的不是 Rust 本身，而是"复制 Amazon/Cloudflare/Discord 的路径"这件事**——这区分至关重要，是整篇文章的真正主轴。

### 3.2 论点一：async 是 Rust 的次级语言，而你正在用它写主程序

Kerkour 把 async 排为团队真实痛点的第一位，理由分三层：

**第一层：sync 阻塞 async executor 的事故几乎不可避免。**

> 原文："I don't remember any project with more than a few thousands lines of code that DIDN'T had at least one occurence of blocking the event loop."

任何审计过几千行 async Rust 代码的人都会会心一笑：`std::fs::read_to_string` 写在 `async fn` 里、`mutex.lock()` 阻塞 tokio worker、CPU 密集循环占满一个 reactor——每个团队几乎都遇到过其中一种。这类 bug 不会在编译器层面拦下，只会在线上 p99 抖动里出现。

**第二层：async 与 ownership/lifetime 之间的化学反应。**

Rust 的 ownership 系统在同步代码里只是难学；一旦你叠上 `async fn` 返回的 anonymous Future + `'static` lifetime + Send/Sync 约束，一个被反复 review 通过的接口可能因为业务上小小一个需求改动而需要重写 50% 的类型签名。

**第三层：runtime 碎片化是结构性问题，不是阶段性问题。**

tokio、async-std、smol、glommio、monoio 各自定义 I/O 接口，写库的人不得不引入 sans-IO 模式或者干脆 pin 死 tokio。Kerkour 不点名但暗示：**"Rust 没有 stdlib 级别的 event loop"是创伤起源**。

这点正好对应本站之前的分析（[《Rust 异步生态的分裂与重聚》](/post/rust-async-runtime-split-io-uring-2026/)）——我曾详细论证 tokio 事实上的单极化、glommio/monoio 试图用 io_uring 重新切割市场、以及标准库 Future trait stable 之后剩下的部分一躺七年的工程后果。两篇放一起读，会看到一个完整图景：**Rust 的并发模型不是"未完成"，而是被设计成 trait-only 的 lower-level primitive；高层抽象的空白被三家不兼容的 runtime 补上，这就是为什么 Kerkour 说审计第一件事是找事件循环阻塞**。

### 3.3 论点二：6 周一个 release，54 个版本之后你怎么升级

> 原文（精炼）："Between January 2020 and May 2026 Rust has seen 54 releases, which amounts to 7500 lines of changelog. ... Programming languages are platforms, not products. They should be stable and move slowly so that most of the time of your developers is not spent fighting with their tools."

Kerkour 在这里其实在攻击一个比 Rust 更大的问题：**把编程语言当 SaaS 产品迭代**。Go 在同期 12 个 release、Python 5 个、Node.js 6 个 LTS——他的对照标尺非常具体。

我特别想强调他这段里一句最容易被忽略的结论：**"Programming languages are platforms, not products."** 这句话适用于一切真正承担长周期工程的工具。它解释了为什么金融系统至今还在跑 .NET Framework、为什么银行 COBOL 维护了 50 年、为什么 Linux ABI 几乎不破坏 userspace 兼容——这些不是落后，而是**慢即稳，稳即可被信赖**。

Rust 的 edition 机制理论上是解决这个问题的，但实际上：

- edition 2018 → 2021 → 2024 → 2026 中间，依赖你的 crate 作者会同步推进吗？很多不会；
- 主流 crate 一两个版本之后开始要求新 toolchain，导致你必须升 rustc；
- 一升 rustc，你的 1Password 用了 5 年的私有 crate 可能在新 borrow checker 检查下编不过去。

这就形成了 Kerkour 所说的"项目腐化"（project decay）：**Rust 项目不是因为代码问题挂掉的，是因为不更新会挂掉、更新一次要付很大代价**。

（这点也呼应本站[《TanStack npm 投毒事件官方复盘》](/post/good-read-tanstack-npm-supply-chain-postmortem/)里的核心结论——一个生态越鼓励频繁迭代+丰富依赖，它的供应链表面积就越大、被武器化的概率就越高。Rust 在这条曲线上比 Go 高很多。）

### 3.4 论点三："贫血标准库"是 Rust 的原罪式设计选择

这一节是 Kerkour 全文最具杀伤力的部分，因为它戳到了 Rust 社区一个不太愿意正视的痛点：**官方明确选择了"小 stdlib"，把 datetime / crypto / HTTP / TLS / Serialization 全部交给社区**。

这个设计哲学在 2014 年看是为了避免 Python 2.7 那种"stdlib 里堆满废弃模块"的悲剧。但 12 年后，它的代价是：

- 一个**中等规模项目同时拖 5 个 crypto 库**：ring 两个 minor 版本、aws-lc-rs、boring、RustCrypto 几个 crate；
- 这些 crate **没有 FIPS-validated mode 的占大多数**，只有 aws-lc-rs 和 boring 有；
- 你的项目实际拥有的攻击面 = 你的 unsafe 代码 + 你所有间接依赖里 unsafe 代码 + 每个 crypto 库各自的实现差异；
- **审计不可能**：5 个 crypto 库 × 几十个直接依赖 × 几百个间接依赖 = 千万行代码量，没有任何中型团队负担得起这种审计成本。

对照 Go：

> 原文："In Go, the standard library contains all the crypto primitives that you will ever need and they all have been written and audited by experts. This is the power of compounding efforts towards a single ecosystem."

这是 Go 设计哲学最被低估的一点：**stdlib 不只是方便，stdlib 是一种集体审计预算的复利投资**。Rust 选择把这部分预算分散到 1000 个 crate 作者头上，结果就是**分散的预算永远买不起一次彻底的安全审计**。

这点与本站 [《GoSentry：Trail of Bits 把 Go 模糊测试武装到牙齿》](/post/gosentry-trail-of-bits-go-fuzzing-libafl-toolchain-2026/) 那篇深度对照：Go 之所以能被几乎一个团队把 fuzzing 推进到工业级，**很大程度上是因为 stdlib 是统一审计单位**。Rust 想做同样的事，得先把 50 个 crate 作者拉到同一个 RFC 桌上谈版本对齐。

### 3.5 论点四：你以为你在抄 Cloudflare 的作业，其实你在抄它的副作用

文章中最让人会心一笑的一句话：

> 原文："Rust is like the metaverse: a lot of people are talking about it, but not many spend their days in it."

Kerkour 用 Stack Overflow 2025 调查的"最受爱戴语言 10 连冠 + 实际使用率排第 14"作为论据，但更深的论点是：**Amazon/Cloudflare/Discord/Meta 的 Rust 成功，是规模带来的奢侈，不是中型团队的可复制路径**。

让我们把他没说透的那层算一遍：

| 玩家 | 月活规模 | 工程师规模 | Rust 团队规模 | 复制成本 |
|------|----------|------------|---------------|----------|
| Cloudflare | 月处理 50M+ rps | 3000+ | Pingora 全职 30+ | 单独招 30 个 Rust 高手的招聘成本 |
| AWS Firecracker | EC2 底层 microVM | 数千 | 全职团队 + 安全审计预算 | 工业级 syscall audit + fuzzing |
| Discord | 200M+ MAU | 800+ | Elixir → Rust 重写专项 | 容忍重写期 18 个月没新功能 |
| Bun | ~10 人 | 10 | 重写 Zig → Rust 1 年 | 单一 founder 押注全员重写 |

中型团队（30 工程师、做一个 B2B SaaS）的真实场景：

- 你的瓶颈是**用户增长 + 业务复杂度**，不是 CPU/内存；
- 你的工程师 60% 是普通水平的全栈，能熟练写 Go 或 TypeScript，但**没用过 lifetime**；
- 你雇不到 Cloudflare 那种 Rust 专家（市场存量不够，单价两倍）；
- 你的 deploy 频次是每天 5–10 次，**每天 rustc 编译 2 分钟 = 团队一周浪费 1 个工程师日**。

把这些都算上之后，"用 Rust 重写"几乎一定是一个**负 ROI 的工程决策**——即使最终代码确实更"正确"。

### 3.6 论点五：Rust 真正赢的 5 个场景

Kerkour 不是单纯的反派，他在文章后半给了一个非常有用的"Rust 推荐场景图"，我整理成 checklist 方便国内团队对号入座：

1. **跨平台共享核心（Common core）**——WhatsApp、Signal、Proton 在做的事：写一份 Rust 核心，编译成 iOS Framework、Android AAR、WASM、Linux daemon。"Rust 是当下唯一能同时跨这五个平台、还提供内存安全 + 包管理的语言"。
2. **System programming**——后台守护进程、操作系统组件、容器运行时。Go 因为 binary bloat 在此场景吃亏。
3. **Embedded（嵌入式）**——尤其是 RISC-V 的 ESP32-C 系列。两条命令就能 cargo run 上去（`rustup target add riscv32imac-unknown-none-elf && cargo run`），HAL 由 Espressif 官方维护。
4. **Databases**——OLTP 引擎、storage engine。Neon、ParadeDB、PgDog、Turso 已经是趋势。性能要求把 Go 的 GC 排除，C++ 的不安全性又把它排除，Rust 是窗口期内最佳选择。
5. **超大规模业务（AWS / Cloudflare 量级）+ 团队已经爱 Rust 的后端服务**——这两条是 AND 关系，不是 OR。

我读到第 5 条特别认真——他用的是 "**if your team already loves Rust**"，不是 "if you can hire Rust developers"。这是一个工程文化判断，不是技能判断。

### 3.7 隐藏论点六：AI Agent 写代码的时代，"标准库的复利"变得更重要

文章里只有一处提到 AI：

> 原文（精炼）："If your team (of Humans or AI agents) already have extensive experience with Rust..."

但这句话埋了一个我认为他自己也没展开的洞察：**当代码生产者是 AI agent 时，'标准库的引力'变成生产力杠杆**。

为什么？Claude / Codex / GPT 这类模型对 Go 标准库的"心智模型"是非常稳定的——`net/http`、`encoding/json`、`crypto/tls` 几乎不可能变。但 Rust 生态里，让 AI agent 选 reqwest 还是 hyper、tokio 还是 smol、serde_json 还是 simd-json，**每一次选择都需要 prompt 注入项目上下文**。

这点和本站[《antirez 一周写出 DS4》](/post/good-read-antirez-ds4-local-inference/)那篇里 antirez 选择**用 C + 极少依赖**与 GPT 5.5 结对的逻辑是同源的：依赖少 + 标准库强 = AI 生成的代码可预测性高。Rust 在 2026 年最大的隐藏成本之一，是 AI agent **不容易稳定地写出"工业级 Rust"**——因为它每次都要在 50 个 crate 之间选一个，而它的训练数据里这 50 个 crate 的最佳实践还在漂移。

这是 Kerkour 没明说但我认为正在加速的一个趋势：**AI 编码时代，"语言 + 标准库"作为一个有引力的稳态平台，会比"语言 + 千个第三方 crate"重要得多**。

### 3.8 我的批评：Kerkour 文中两个偏激点

为了让"好文共赏"不变成单方面背书，我要指出两个我不完全认同的点：

1. **"54 个版本是 churn 灾难"——这个对比不公平**。Rust 的 release 模式是 6 周稳定推送，但每个 release 都是向后兼容；Node.js 12 个 release 里有多次 breaking API 变更（特别是 fs/promises）。版本号多不等于稳定性差，需要分语义看。

2. **他暗示 ring 和 aws-lc-rs 同时存在是"生态病"，但这其实是密码学审计成熟度的标志**。Go stdlib 的 crypto 也用 boringssl 派生代码，本质上是一回事，只是入口统一。Rust 的真正问题不是"5 个 crypto 库"，而是"5 个里没有一个被 Mozilla/Google 这样的机构无条件官方背书"。这是治理问题，不是设计问题。

但这两个批评不影响主轴的正确：**对大多数中型团队，Kerkour 的劝退建议在 2026 年是合理且**经济上更划算的**。

---

## 4. 延伸阅读图谱

### Kerkour 的代表作 5 篇

1. [Cross-platform Rust: Analyzing how WhatsApp, Signal and more are shipping Rust to billions of devices](https://kerkour.com/rust-cross-platform-apps)（2026-05-06）
   - 与本文形成"为什么不要用 Rust" + "为什么 WhatsApp 必须用 Rust" 的辩证对。
2. [All databases will eventually be (re)written in Rust](https://kerkour.com/rust-databases)（2026-04-29）
   - 对应本文论点五"Database is where Rust wins"的展开版。
3. [A Roadmap for Building an Extended Standard Library for Rust](https://kerkour.com/rust-extended-standard-library)（2026-04-15）
   - 他自己提出的解决方案。值得读：他认为 Rust 团队该做的不是 churn，而是 vendor 一批关键 crate 到 std。
4. [Supply chain nightmare: How Rust will be attacked and what we can do to mitigate the inevitable](https://kerkour.com/rust-supply-chain-nightmare)（2026-04-08）
   - 把本文"5 个 crypto crate"的论点推到攻击面分析，与本站 TanStack 事故复盘强相关。
5. [Firecracker deep dive: How Rust and microVMs are revolutionizing cloud infrastructure](https://kerkour.com/firecracker-deep-dive-rust)（2025-12-10）
   - 看他**正面立场**的样子，避免误以为他是 Rust 黑。

### 相关论文 / 博文 5–8 篇

- Rust RFC 0230《remove the runtime》（2014）：Rust 主动砍掉 green thread 的历史决定，理解本文 async 痛点的根。
- Aria Beingessner《[The Pain of Real Linear Types in Rust](https://faultlore.com/blah/linear-rust/)》：从语言理论层面解释 ownership × async 为什么难。
- Niko Matsakis 一系列 async-related blog post（2024–2026）。
- Mozilla《[Rust in Firefox](https://wiki.mozilla.org/Oxidation)》案例：14 年时间，Rust 占 Firefox 代码的真实比例。
- Discord《[Why Discord Is Switching from Go to Rust](https://discord.com/blog/why-discord-is-switching-from-go-to-rust)》：Kerkour 文中明确指为"不要随便复制"的案例。
- Cloudflare《[Pingora: A 50M-RPS Rust Server That Replaces NGINX](https://blog.cloudflare.com/pingora-open-source/)》：另一个"复制者陷阱"的源案例。
- Rust Survey 2024 Annual Report：Rust 团队官方承认的 churn / 学习曲线问题数据。

### 反方观点 3 篇（防止 echo chamber）

1. ThePrimeagen《Why I'm Still Bullish on Rust》视频系列：典型的 Rust positive bias，但讲技术细节扎实。
2. Aria Beingessner《[Rust Is a Hill I Will Die On](https://faultlore.com/blah/rust-is-a-hill/)》：从 Rust core team 内部视角的反驳。
3. Cloudflare Pingora 团队的 Twitter 长串解释：他们认为 nginx → Rust 替换的核心驱动是"运维侧的内存安全"，不是性能。

### 与本站已有文章的呼应（请配合阅读）

- [《Rust 异步生态的分裂与重聚：io_uring、Tokio 单极、和一个迟到的标准》](/post/rust-async-runtime-split-io-uring-2026/) — Kerkour "async is hard" 论点的中文版深化。
- [《TanStack npm 投毒事件官方复盘》](/post/good-read-tanstack-npm-supply-chain-postmortem/) — Kerkour "5 个 crypto crate = 攻击面爆炸" 论点的实证案例。
- [《Linux Kernel copyfail：后量子时代的 IPSec 信任崩塌》](/post/linux-kernel-copyfail-postquantum-ipsec-trust-2026/) — 同样的"语言级安全不能拯救生态级混乱"主题。
- [《antirez 一周写出 DS4：当 Redis 之父把 GPT 5.5 当结对程序员》](/post/good-read-antirez-ds4-local-inference/) — 反向案例：用 C + minimal deps 在 AI 时代做生产力杠杆。
- [《Python 3.15 JIT：CPython 在性能上的迟到答案》](/post/python-315-jit-cpython-performance-rewrite-2026/) — 另一种"语言作为长周期平台"的演化路径对照。

---

## 5. 编辑延伸思考：在"Rust 至上主义"和"Rust 怀疑论"之间，2026 年的中型团队该怎么选

读完 Kerkour 这篇文章之后，我想把一个更具体的问题摆给中文工程社区：**在 AI agent 大规模介入代码生产的 2026 年，技术栈选型的损益函数已经变了**。这是 Kerkour 没明说但暗藏的判断。

让我把这件事拆开。

**第一层：纯人写代码的损益函数**

这是过去 40 年的旧模型：
- 编程语言的成本 = 学习成本 × 工程师数量 + 维护成本 × 项目寿命；
- 收益 = 性能 + 安全 + 招聘吸引力 + 生态丰富度。

在这个模型里，Rust 在大规模 + 长周期 + 性能敏感的项目里赢，正如 Cloudflare/Discord 的故事。

**第二层：AI agent 介入后的损益函数（2026）**

现在的模型多了三项：
- **AI agent 对该语言的生成可靠度**——Go 的 stdlib 稳定性让它在 AI 生成场景的 first-pass 通过率非常高。Rust 的生态碎片让 AI agent 经常生成"语法正确但不是该项目惯用风格"的代码。
- **AI agent 的 review/refactor 成本**——Rust 的 lifetime/Send/Sync 错误信息对人类已经够难，对 AI 是另一种维度的难（它需要更多 token 来理解上下文）。
- **AI agent 的依赖管理成本**——AI 容易在 Rust 项目里引入"看起来对但实际过时"的 crate，因为 crates.io 的搜索结果排序对 LLM 训练时间敏感。

把这三项算进损益函数，**Rust 在 AI agent 时代的"中型团队 ROI"进一步下降**——除非 5.3.7 节那个"AI 友好语言"的窗口反转为优势（这取决于 Rust 自己是否在 2027 年前完成 std 扩张）。

**第二点：Kerkour 给出的"5 大 Rust 赢场景"在中文语境的真实优先级**

我把他的列表按中文工程社区的稀缺度重新排了一下：

| 场景 | Kerkour 排序 | 中文社区实际频次 | 我的优先级建议 |
|------|--------------|------------------|----------------|
| 跨平台共享 core | 1 | 极低（端侧团队少） | 仅微信、抖音、米哈游等头部 |
| System programming | 2 | 中（云厂商内部多） | 阿里/字节/华为云内部值得 |
| Embedded | 3 | 中等（IoT 大热） | RISC-V 政策红利下值得 |
| Databases | 4 | 极高（PingCAP/oceanbase 一线在做） | 第一优先级 |
| 超大规模 + 团队爱 Rust | 5 | 中（叫得响的不超过 10 家） | 慎重，多半算自吹 |

中文社区最应该投入 Rust 的方向，按这个数据看是：**Database / IoT / 嵌入式安全工具**。不是 web service，不是 CRUD 后端，不是 AI 编排层（这些用 Go / Python / TypeScript 都行）。

**第三层：从 Kerkour 的论点里挖出一条 meta-原则**

读完整篇之后，我提炼出一条几乎可以脱离 Rust 套用的元原则：

> **"语言是平台，不是产品"——任何对长周期工程负责的 CTO，都应该把语言的 churn rate、std 厚度、生态分裂度、招聘市场厚度，作为第一类指标，而不是性能 benchmark。**

这条原则在 1980 年代选 C 还是 Pascal 时成立，在 2000 年代选 Java 还是 C# 时成立，在 2010 年代选 Go 还是 Scala 时成立，今天选 Rust 还是 Go/Zig/OCaml 时一样成立。Kerkour 的整篇文章用 5000 字论证的，本质就是这条原则。

而这条原则也解释了为什么 Linux kernel 选 Rust 是对的（核心维护团队已经是世界级，churn 可以扛），但你的 SaaS 后端选 Rust 大概率是错的（小团队 churn 撑不住、招聘市场买不到）。

**最后一个判断**：再过 3 年，回头看 2026 年这场 Rust 化运动，我猜结论会是——**赢家不是用 Rust 的公司，而是"知道何时不用 Rust"的公司**。Kerkour 的这篇博客在那个时间点上会被作为最早的清醒声音之一被回顾。

---

## 6. 配套资料导览

本篇配套提供以下三份资料，建议结合主文阅读：

- **`mindmap.svg`**：把 Kerkour 全文 7 个论点 + 5 个赢场景压缩成一张深色思维导图，方便给团队做技术选型会议的开场图。
- **`concept-cards.md`**：12 张关键概念卡片，覆盖 `async runtime fragmentation` / `event loop blocking` / `edition churn` / `std lib 贫血` / `FIPS validation` / `cross-platform core` / `linear types` / `green threads` / `borrow checker × async` / `crate supply chain` / `Pingora`/`Firecracker` 案例 / `AI-agent friendly language`。每张卡片含中英术语 + 100 字解释 + 一个验证点。
- **`glossary.md`**：30 条 Rust 生态与异步并发英中术语对照表，每条带 1 句解释（适合给团队做选型 PPT 的术语统一）。

---

## 7. 谁应该读

**强烈推荐**（必读）：
- 正在考虑"用 Rust 重写后端"的 30–200 人工程团队的 CTO / 架构师；
- 在做嵌入式、数据库、跨平台 SDK 选型的团队（用来确认 Rust 是对的）；
- Go 工程师正在被招聘市场 Rust 噪音劝转岗的人。

**推荐**：
- 学完 Rust 想找一篇"清醒提示"的中级 Rustacean；
- 关注编程语言生态学/治理的研究者；
- 写技术战略文章的工程主编。

**可以跳过**：
- 已经在 Cloudflare/AWS/Discord/Anthropic 工作的人（他不是在写给你看）；
- 把"Rust vs Go"当作宗教战争的人——这篇文章不会让你舒服。

---

## 后记：一句话

Kerkour 这篇 5000 字的英文长文，对中文社区其实可以浓缩成一句话——

**"如果你的团队不是 Cloudflare，你就不应该按 Cloudflare 的剧本演。"**

而这句话能不能听进去，可能比"今年用 Rust 重写多少行"更能决定一个团队 3 年之后的工程负担。
