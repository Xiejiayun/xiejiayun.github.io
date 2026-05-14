---
title: "【好文共赏】把 200 万行 Haskell 跑在每年 2480 亿美元的资金流上：Mercury 把语言学家当作可靠性工程师的十年"
description: "Ian Duncan 在 Haskell.org 官方博客发表 5 万字长文，第一次系统拆开 Mercury 这家 1500 人 fintech 怎么把 200 万行 Haskell 跑成银行级生产系统——纯函数式是 Safety-II 的载体，类型是制度记忆的保险柜，Temporal 是后悔药，理想主义才是真正的生产风险。"
date: 2026-05-14
slug: "good-read-haskell-mercury-production-engineering"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Haskell
    - 生产工程
    - 可靠性
    - Temporal
    - 函数式编程
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> **原文**：[A Couple Million Lines of Haskell: Production Engineering at Mercury](https://blog.haskell.org/a-couple-million-lines-of-haskell/)
> **作者**：Ian Duncan（Mercury Stability 团队工程师，hs-temporal-sdk / hs-opentelemetry 维护者）
> **发布**：2026-03-30，Haskell.org 官方博客 *Haskellers from the trenches* 系列首篇
> **阅读时长**：原文 ~52,000 字符 / 约 75 分钟深读
> **多模评分**：Opus **9.2** / Sonnet **9.0** / Gemini **9.0**（综合 **9.07 / 10**）
>
> 一句话推荐：这是过去三年里我读过最诚实的"非主流语言生产工程"长文，它的真正主题其实不是 Haskell——而是**"在一个一半同事工作经验都不到一年、却又必须跑别人的钱"的环境里，类型系统、durable execution、可观测性和组织文化如何一起构成 Safety-II 意义上的"适应性容量"**。

## 1. 为什么这篇值得读

Haskell 在生产中跑得好不好这个问题，过去十年被吵翻了。每隔半年就会有人在 HN 贴一篇"我们用 Haskell 重写了什么"，每次评论区都会重演相同的三幕剧：信徒赞美类型系统、怀疑者抱怨招聘和库生态、第三方建议你"用 Rust / Go / Elixir 不就完了"。Ian Duncan 这篇 5 万字的长文之所以能从这种循环里跳出来，是因为他**不在辩护 Haskell**，而是在记录"一个 200 万行 Haskell 的金融系统，是怎么通过组织设计、类型设计、平台设计的复合，把'生产中的语言选择'这件事降级成了战术细节"。

Mercury 是一家服务超过 30 万家中小企业、2025 年处理 2480 亿美元交易额、年化收入 6.5 亿美元、目前正在向美国 OCC 申请国家银行牌照的金融科技公司，**整个后端约 200 万行 Haskell**，工程师大多是上岗后才学的这门语言。这种"在一个被广泛认为是学术玩具的语言上跑实打实银行业务"的样本本身就极其稀少；再加上 Duncan 本人是负责可靠性基础设施的 Stability 团队成员（同时是 `hs-temporal-sdk`、`hs-opentelemetry` 这些核心可观测性库的作者），他给出的不是宣传，而是**操作手册级别的诚实自白**：哪些类型把戏值得做、哪些是自我陶醉、`unsafePerformIO` 在生产里到底怎么活下去、为什么他们几乎不用 Hackage 上的 HTTP 客户端库。

更难得的是，他没有把 Haskell 写成宗教问题。他引用的是 Erik Hollnagel 的 *Safety-I / Safety-II*、David Woods 的 *resilience engineering*、Patrick McKenzie 的"高速增长公司的同事永远有一半不到一年经验"——**这些理论框架在 Stripe、Cloudflare、Google SRE 那一脉传统里早已经是标配**。Duncan 把它们和"Haskell 工程师的日常生活"做了一次精准的咬合，结论是：Haskell 不是让 bug 不可能发生的银弹，**它是一种把'操作知识'压成接口、让它在原作者离职后依然存活的载体**。

这一点和我之前导读过的[《Cloudflare "Code Orange" 实践全解析：如何用 18 个月将 P0 事故降低 73%》](/post/cloudflare-code-orange-fail-small-resilience-2026/)、以及[《好文共赏：资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/)讨论的是同一个母题——**在快速扩张的工程组织里，资深工程师的隐性知识到底以什么形式存活下来**。Cloudflare 用流程和文化、Akhilesh Nair 用 Speed/Scale 解耦概念、Mercury 用类型系统。三条路指向同一个底层观察：**靠"记得"和"文档"几乎一定会失败；必须让正确的做法变成"路径最短"的那条**。

## 2. 核心观点深度解读

### 2.1 第一原理：可靠性不是"不出错"，而是"吸收变化的能力"

Duncan 开篇就抛出他和传统软件工程教育最尖锐的分歧——**Safety-I vs Safety-II**。

> 原文：ّ "There is a traditional way of thinking about system reliability that focuses on preventing failures. ... But it is not sufficient, and if you orient entirely around it you develop a specific blind spot: you get very good at cataloguing the ways things break and very bad at understanding why they ordinarily work."

传统软件可靠性的脚本是：枚举失败、加检查、加测试、抓 bug。Duncan 不否认这件事必要，但他认为如果**只**做这件事，会养出一种盲区——你越来越擅长说"系统会怎么坏"，但越来越说不清"系统平时为什么不坏"。

Hollnagel 的 Safety-II 框架把这个盲区翻面：复杂系统能稳定运行，**靠的不是失败被全部预防掉，而是它能"吸收变化"**——优雅降级、操作员能理解和调整、架构让对的事情容易做而错的事情困难。可靠性不是"故障的缺席"，而是"适应性容量的在场"（the presence of adaptive capacity）。

这个翻面有一个非常具体的运营后果：**当你的公司每年同事增长 2 倍，文档腐败的速度永远快于撰写的速度**。Patrick McKenzie 那句被 Duncan 反复引用的"在 2 倍年增长的公司里，永远有一半同事工作经验不到一年"——意味着任何依赖"老员工记得"的不变量在一年内就会变成 institutional dark matter：**承重，但对周围多数人不可见**。

到这里 Haskell 还没出场。**这是一个组织设计问题，不是语言问题**。但它给后面所有的 Haskell 决策定了基调：Mercury 选择 Haskell 不是因为它优雅，是因为他们需要一种"能把适应性容量物化进代码"的载体。

### 2.2 纯（purity）不是语言性质，是接口契约

Duncan 抛出了他对 Haskell 最反直觉的判断之一：

> 原文："the first and most consequential misunderstanding about Haskell is that purity is not something the language is, so much as that it is something your interfaces enforce."

他给的反例锋利得让人吃惊——`bytestring`、`text`、`vector` 这些被当作"纯函数式典范"的库，**在内部全是可变分配、缓冲区写入、`unsafePerformIO`、`unsafeCoerce`**——只要把它放在一个 junior 工程师的 side project 里你会立刻报警的那种行为。它们之所以"看起来纯"，是因为有一个叫 `runST :: (forall s. ST s a) -> a` 的类型签名做边界：

```haskell
runST :: (forall s. ST s a) -> a
```

rank-2 类型保证了创建在内部的可变引用**不可能逃出 scope**。内部为所欲为，外部全是纯。

Duncan 把这条原则推广成 Mercury 的工程哲学：**容器内的危险是可控的，前提是出口的类型足够窄到危险逃不出去**。数据库连接池、缓存、HTTP 客户端的熔断器——这些都不是问题，**只要接口够紧、边界够明显，且这种紧致性能被编译器机械地检查**。

> 在生产里，目标不是消除可变性（这对真实系统来说是个不严肃的命题），是**把可变性圈起来、把圈起来这件事写在签名里、并验证它一直被圈着**。

这个视角和我在[《Redis 的野心代价：当一个"远程字典服务器"想成为一切，它就什么都不是了》](/post/good-read-redis-cost-of-ambition/)里讨论的"边界丢失"是同一枚硬币的两面——Redis 把"内存中可变状态服务"这个清晰边界往四面八方扩散，结果每个新功能都顺着原边界的缝隙渗透到新的责任空间。Duncan 在告诉你的是反方向的故事：**当你坚守边界，纯函数式语言能在 200 万行规模下保持可读**。

### 2.3 把"运营咒语"编码进类型：编译器是制度记忆的更好托管者

这是文章里最具操作性的一节，也是 Haskell 信徒为什么愿意忍受 ecosystem 痛苦的核心证据。

Duncan 举了一个所有运维都熟悉的场景：**"记得在事务里发审计日志"、"调用这个接口前要先检查 feature flag"、"通知一定要在数据库事务**内**入队，不是事务后"**——这些都是运营咒语（operational lore），住在 wiki 页、入职文档、半遗忘的设计评审纪要、和某个调去三个团队外的高级工程师的记忆里。

天真的做法是写两个函数，告诉所有人"请用第一个不要用第二个"：

```haskell
-- Please use this one, not the other one
writeWithEvents :: Transaction -> [Event] -> IO ()

-- Don't use this directly (but we can't stop you)
writeTransaction :: Transaction -> IO ()
publishEvents   :: [Event] -> IO ()
```

Duncan 用一个生动的比喻形容这种做法：**它一直能 work，直到它不 work。而"它不 work"那天往往是周五下午，写 wiki 的人在度假，剩下的人正实时发现这页 wiki 是承重墙**。

真正的方案是**重构类型**，让"提交工作"这件事的唯一入口都强制包含事件发布：

```haskell
data Transact a -- opaque; cannot be run directly
record :: Transaction -> Transact ()
emit   :: Event -> Transact ()

-- 唯一执行 Transact 的方式：原子地提交并发布
commit :: Transact a -> IO a
```

> 原文："Now the incantation is the only door in the room. You cannot forget it because there is nothing else to do."

类型系统在这里没有证明任何深奥的定理，**它做的事更朴素也更有用：把"正确的运营程序"变成"阻力最小的那条路"**。

Duncan 强调了一个常被 Haskell 布道者忽略的点：**类型不是给编译器看的，是给团队看的**。新人问"怎么写一个事务"，类型签名回答他。老员工离职，答案留下来。**这不是一个"漂亮"的特性，是组织尺度上对 institutional knowledge 的存档**。

这一点是整篇文章里我最受触动的部分。它和 Akhilesh Nair 在[《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/)里描述的"Scale 循环"几乎是同一种现象的不同角度——资深工程师的真正贡献是 scale-side 的隐性约束，**Haskell 的类型系统是把 scale 工作显式化的工具之一**。

### 2.4 Durable Execution：把"分布式状态机"从手卷负担里拯救出来

Duncan 用最少的篇幅讲了一个对架构师极有杀伤力的转折。

金融系统的现实是：**没有事务能装下所有事**。发送一笔付款、等合作方 ack、更新台账、通知用户、处理取消、处理超时、处理"合作方说 yes 但你的 worker 在记账前死了"、处理"网络短暂地进入更高维存在而没告诉你任何东西"——每一步失败都需要知道你停在哪、什么已经发生了、什么还没发生。

Mercury 之前的做法是经典的：**数据库背书的状态机 + cron job + background worker，重试逻辑散落在代码各处**。它能 work。它也"需要那种通常和拆未爆弹相关的警觉性"。

转折点是采用 [Temporal](https://temporal.io)：你写顺序代码描述工作流，平台用 event history 记录每一步；worker 崩了，另一台 worker 重放确定性前缀，再从中断处继续。**重试、超时、取消、错误处理由平台提供，而不是每个团队再次拙劣地重新发明**。

Duncan 给 Temporal 起了个绝妙的比喻：

> 原文："I think of Temporal as Frankenstein's monster, in the flattering sense: assembled from excellent parts, animated by improbable effort, and smarter than many of the people alarmed by it."

Temporal 是把 durable history、replay、determinism 这些 Erlang 原生就有的东西**强行螺栓到从未原生支持过它们的运行时上**——大部分公司不会把整套系统重写成 Erlang，Temporal 是为剩下我们这些人准备的义肢。

更有意思的是它和 Haskell 哲学的契合：**一个 Temporal workflow 在某种重要意义上就是它的 event history 上的纯函数**——重放必须产生相同的命令序列，这正是 Haskell 对纯代码的相同约束。副作用被隔离到 activities 里，**workflow 编排、activities 执行**。如果你熟悉"pure core / impure shell"模型，**这就是那个模型，只是平台代替了纪律来执行分离**。

Mercury 把这套东西做成了开源的 [hs-temporal-sdk](https://github.com/mercurytechnologies/hs-temporal-sdk)。这条决策的运营意义被 Duncan 用一句精确而克制的话总结：**"It is difficult to overstate how pleasant it is to delete a hand-rolled distributed state machine and replace it with something whose failure semantics were not improvised during sprint planning."**

这点和我之前导读过的[《Cloudflare Dynamic Workflows：让 durable execution 跟着租户走》](/post/cloudflare-dynamic-workflows-multitenant-durable-execution/)是同一个时代背景下的两个解法——Cloudflare 把 durable execution 做成多租户基础设施服务，Mercury 把 Temporal 包成 Haskell 一等公民，**两边都在承认同一件事：自卷状态机是 2026 年企业架构师能犯的最常见而又最昂贵的错误之一**。

### 2.5 给"领域"建模，不要给"传输"建模

这一节看似无趣，实则是 Duncan 全文最被 senior 工程师低估的部分。

Mercury 历史上有大量代码会直接 `throw StatusCodeException 409 "Conflict"`——在它原本所在的 HTTP handler 里这没毛病。然后呢？代码被抽出来复用了。它现在跑在 cron job 里、queued background worker 里、Temporal workflow 里。然后**一个 cron job 抛出 HTTP 409**，这种事本身是 Duncan 的原话："an absolutely unhinged thing for a cron job to do"。

修复也"概念上简单"：把领域错误建模成领域类型：

```haskell
data PaymentError
  = InsufficientFunds
  | DuplicateRequest RequestId
  | PartnerTimeout Partner

toHttpError      :: PaymentError -> HttpResponse
toWorkerStrategy :: PaymentError -> WorkerAction
```

让 transport 层的翻译只在边界发生。**任何看过历史代码库的工程师都知道这点几乎从不在第一版代码里被做对，因为第一版总是为一个 context 写的，等你意识到它会被三种 context 调用的时候，"status code 已经承重"了——有人把它们 catch 在 business logic 里**。

Duncan 写道："越早做这种分离，代价越小；越晚做，结果越离奇。你最终会得到 cron job 朝 Sentry 投掷 409、background worker 把 HTTP 特定异常解释成业务语义——这就是抽象在告诉你它逃出了 containment。"

这条原则的普适性远远超过 Haskell。它是任何一门语言里"DDD vs. CRUD"争论的实际操作版本。

### 2.6 类型编码的权衡：教堂、帐篷与"什么时候不要把它编码"

这一节是 Duncan 对自己阵营最重的一刀。他承认**把不变量编码进类型很贵**：不是运行时贵，是认知开销贵、是它对未来工程师的刚性约束贵、是"需求会变而 type-encoded invariants 改起来很疼"贵。

他给了一个极有画面感的光谱：

* **教堂派**：你把一切都编码进类型，illegal states unrepresentable，重构要数周（改一条业务规则要在五十个模块里穿线），新人盯着签名怀疑人生。**Cathedrals are beautiful. They are also expensive, cold, and not especially famous for how quickly one renovates the plumbing.**
* **帐篷派**：你什么都不编码，类型是 `String` 和 `IO ()`，最糟时是 `Dynamic`。代码好改因为没有契约可违反；系统能跑因为建它的人还在。**Tents are flexible, portable, and, under certain weather conditions, a very direct way to learn about the sky.**

Mercury 的实操规则也很具体：

1. **把"对静默腐败的防御"放进类型**——如果违反不变量会产生看起来合理但语义上不可能的"错数据"，编码它。静默失败的反馈循环太长，靠人不够。
2. **对"会大声失败的不变量"用运行时检查**——一个 500、一个失败的断言、一个 JSON 边界上的 type mismatch，运行时检查 + 好的错误消息够了。生产前就会抓到，或者生产后会立刻抓到。
3. **抵抗"把整个领域建模进类型"的冲动**——你的领域是乱的。它有 edge case、有 grandfather clause、有互相矛盾的规则、有 2018 年起为三个特定客户定制的特殊行为而今天没人完全懂。类型系统想要 crispness。你的业务永远不会提供。

他用一句格言收尾："**Types are for the team, not just for the compiler.**"

### 2.7 为可观测性而设计：records of functions 和 Monoid 的运营版本

Duncan 在这里给了一个对**任何**强类型语言（不只是 Haskell）有用的设计模式。

问题：Haskell **不能 monkey patching**——你不能在运行时去 reach into 一个库、把它的 HTTP client 换成会记录 timing 的版本。Rust 也一样、孤儿规则甚至更严苛。但 Rust 生态围绕 tower middleware 模式收敛了，Haskell 生态在好几种方案上分裂——**约束是一样的，问题是你的生态是否给了你一个 conventional escape hatch**。

Mercury 的标准解法：**把模块顶层导出的具体函数换成 records of functions**：

```haskell
-- 给不了你 leverage：
sendRequest :: Request -> IO Response

-- 给得了你所有 leverage：
data HttpClient = HttpClient
  { sendRequest :: Request -> IO Response
  , getManager  :: IO Manager
  }
```

有了 record，你可以包装 `sendRequest` 加 timing；可以注入故障；可以 mock；可以加重试、tracing、租户特定行为。**全部运行时，不动库的源码**。

接着 Duncan 抛出一个"我保证不是把 category theory 偷渡进来"的观察：**middleware 和 interceptor 类型几乎总能 admit Semigroup 和 Monoid 实例**。WAI 的 `Middleware = Application -> Application` 是 endomorphism，endomorphisms under composition + `id` as identity 构成 monoid；一个 record of interceptor hooks，**每个字段是 endomorphism**，自动得到 fieldwise Semigroup——`a <> b` 各字段独立组合、`mempty` 是恒等记录。

这把"组合 N 个独立横切关注点"从工程问题降级为几乎非问题：

```haskell
appTemporalInterceptors =
  mconcat
    [ retargetingInterceptor
    , otelInterceptor
    , sentryInterceptor
    , sqlApplicationNameInterceptor
    , loggingContextInterceptor
    , statementTimeoutInterceptor
    , teamNameInterceptor
    , clientExceptionInterceptor
    , workflowTypeNameInterceptor
    ]
```

每个 interceptor 在自己的模块里、由只关心一个 concern 的人写；组合就是 `<>`；没有隐藏布线；顺序写在 list 里。**新的横切关注点 = 在 list 尾巴上添一项；旧的从不被碰**。

Duncan 同时给了一句对库作者的近乎请求的话："**如果你在写 Haskell 库，请留 escape hatches**。提供 records of functions、effect types、callback、任何让消费者无需修改你的代码就能注入行为的方法。Haskell 的类型系统对约束执行很美妙；它也能不小心把系统封得太严，以至于运营这个系统的人看不进去——而完美的抽象，如果运营上不透明，**就根本不能在生产里被用**。"

这点和 jemalloc 那种"配置驱动可观察"的生态选择 ([见前文](/post/jemalloc-2026-survey-allocator-renaissance/)) 实质上指向同一个工程美学：**好的库不止做对它该做的事，它把"被诊断"也变成一等公民**。

### 2.8 不要相信"compiles == works"的多巴胺

文末 Duncan 留了一段对 Haskell 信徒近乎不近人情的诚实：

> 原文（节选）："Types can tell you that a function returns an Either ParseError Transaction. They cannot tell you whether it parses the amount field as cents or dollars."

类型告诉你函数返回 `Either ParseError Transaction`；它**不**告诉你 amount 字段是按美分还是按美元解析的。它**不**告诉你你的合作方 API 是否把 omitted 字段和 null 字段当不同语义。它**不**告诉你你的重试逻辑会不会**在闰日的某个 timing window 内重复扣款一次**。

`unsafePerformIO` 在生产中无处不在——你日常依赖的 `bytestring` 和 `text` 内部就在用。Mercury 的做法是**坦诚地容纳妥协**：

> 原文："Production Haskell is not the absence of compromise. It is the disciplined containment of compromise."

这一句话适合任何想认真做生产工程的人贴在显示器上——**它和"类型化函数式"完全无关，它是关于"如何与不可避免的不完美共处"的最佳工程实践陈述**。

### 2.9 隐性招聘风险：Haskell 吸引理想主义者

文章的结尾抛出了一个让多数 Haskell 阵营内部不舒服的判断：

> 原文："Haskell attracts idealists. This is mostly a strength: ... But idealism, left unchecked, becomes a production liability."

那位想用"新型的代数关系类型级编码"重写数据库层的工程师，并没在帮你 ship feature；那位拒绝合并"一次性脚本里用了 `String` 而不是 `Text`"的工程师，并没在帮你赶 deadline；那位把每次设计评审都变成"按上周读的某篇论文的精神做一次彻底重写"宣传的工程师，**无论多聪明，都在让团队变慢**。

Duncan 说他们必须**主动地培养一种 pragmatism 文化**——Haskell 给了你强力工具；**始终用上所有的工具不是 pragmatism，是 self-indulgence**。

这一点放回整篇文章的逻辑闭环里非常重要：Mercury 选择 Haskell 不是为了优雅，是为了 leverage。而 leverage 这种东西**很容易被对优雅的执念耗光**。你可以把这段话泛化到任何"非主流但强大"的工具：Rust、Lean、Coq、formal methods、effect systems——**所有让你能做"别人做不了的事"的能力，都同时是吸引"想做别人做不了的事的人"的磁石；后者如果失去管控，会反过来吃掉前者**。

## 3. 延伸阅读图谱

### Ian Duncan / Mercury Engineering 其他代表作

1. **Ian Duncan — [Embracing Flexibility in Haskell Libraries](https://iankduncan.com/posts/embracing-flexibility/)**：Duncan 在 Mercury 之外最被引用的设计随笔，记录了"为什么不要在库里直接 import logging framework"的完整推导。本文里"records of functions"那一节其实是这篇文章的简化版。
2. **Max Tagher（Mercury CTO）— [Haskell in Production: Mercury](https://serokell.io/blog/haskell-in-production-mercury) (2022)**：Mercury 早期采用 Haskell 的决策史，从 50 人规模视角看为什么选 GHC。和 Duncan 这篇形成"早期 vs 成熟期"对照。
3. **Mercury Engineering Blog — [How Mercury Built a Real-Time Banking Operations Center](https://mercury.com/blog/engineering)**：Mercury 内部为 SVB 危机做的可观测性建设。Duncan 文中提到的"5 天涌入 87000 客户和 20 亿美元"故事，工程视角在这。
4. **Ian Duncan — [hs-opentelemetry GitHub](https://github.com/iand675/hs-opentelemetry)**：本文反复推荐的 Haskell OpenTelemetry SDK，是文章里"observability by construction"主张的实物。
5. **Ian Duncan — [hs-temporal-sdk talk @ Replay 2024 (YouTube)](https://www.youtube.com/results?search_query=hs-temporal-sdk+ian+duncan+replay)**：Mercury 把 Temporal 做成 Haskell 一等公民的工程化总结，可以视作本文 §2.4 的 30 分钟视频补丁。

### 同一脉问题的相关读物

* **Erik Hollnagel — *Safety-I and Safety-II: The Past and Future of Safety Management* (2014)**：本文 Safety-II 框架的源头。任何认真想理解"为什么我们应该关心系统平时为什么不坏"的工程师都该读。
* **David Woods — *Four Concepts for Resilience and the Implications for the Future of Resilience Engineering* (2015)**：adaptive capacity 这个词的学术原点。
* **Patrick McKenzie (patio11) — [What Working At Stripe Has Been Like](https://kalzumeus.com/2020/10/19/stripe-and-the-employees-who-stick-around/)**：本文反复引用的"2x 年增长公司里同事永远新"的来源，是任何 hyper-growth 公司技术领导都该读的清单。
* **Betsy Beyer et al. — *Site Reliability Engineering* (O'Reilly, 2016) Chapter 32–33**：Mercury production readiness review 的方法论母本。
* **Camille Fournier — *The Manager's Path***：高速成长组织里 senior 工程师隐性知识管理的运营级指南，和本文的"institutional dark matter"主题有强共振。

### 反方观点与制衡视角

1. **Tef — [Programming is not Math](https://programmingisterrible.com/post/65781074112/devils-dictionary-of-programming)**：对类型系统狂热的经典反驳，主张"代码是社交活动而不是数学"。值得和本文对照读，能更准确地校准 Duncan 的"types are for the team"主张。
2. **Hillel Wayne — [Why Don't People Use Formal Methods?](https://www.hillelwayne.com/post/why-dont-people-use-formal-methods/)**：对"类型即证明"派的友好但锋利的批评。和本文 §2.6 的"教堂 vs 帐篷"光谱直接对话。
3. **HN 评论区精华** ([id=47991802](https://news.ycombinator.com/item?id=47991802))：434 分、232 条评论。多名前 Mercury 员工补充了一些 Duncan 略过的痛点——例如 GHC 编译时间、library 版本约束矩阵、以及 Hackage 上文档不一致带来的 onboarding 摩擦。

## 4. 编辑延伸思考：把 Mercury 当作"非主流语言生产工程"的通用样本

Duncan 这篇文章的真正价值，**不在于它说服你用 Haskell**，在于它给了任何"语言选择是少数派"的团队一个**可复用的诊断与生存框架**。把它的论点抽象掉 Haskell 这层皮，剩下的核心是六条横向命题：

1. **生产系统的可靠性由"适应性容量"决定，不由"故障预防"决定**。预防故障是义务，**但只做这件事的团队会盲目于"系统平时为什么 work"**。Safety-II 视角让你看见你的真正基础设施——一线工程师每天临场修复的小变化、文档之外的口头约定、那位刚好知道某个边界条件的高级工程师。
2. **任何"必须按顺序做的事"都会在快速增长中崩坏，除非它被强制成接口**。这条对 Python、TypeScript、Go 同样成立——只是这些语言通常缺乏 Haskell 那种把约束推进类型系统的工具。**对它们，等价物是 lint 规则、code review checklist、和 platform team 提供的脚手架**。但同样的运营压力会推着你往同样的方向走：把"正确做法变成阻力最小的那条路"。
3. **Durable execution 不是 fancy 工具，是对"手卷状态机是工程债"这件事的承认**。如果你的公司有 cron job + retry table + status flag + 重试 worker 这种组合，**你正在维护一个比你想象中差很多的 Temporal 实现**——区别只是它没有名字、没有重放、没有可观测性。这一点对架构师的杀伤力很大；和[《Cloudflare Dynamic Workflows》](/post/cloudflare-dynamic-workflows-multitenant-durable-execution/)那篇导读放在一起看效果更好。
4. **可观测性必须被设计进库，不是事后包装**。这一条几乎是 2026 年所有 platform 团队的共识，但 Duncan 的版本带着 Haskell 特有的锐度：在没有 monkey patching 的语言里，**"是否能 wrap 一个函数"决定了"是否能在它出问题时知道发生了什么"**。这是为什么 Mercury 几乎不用 Hackage 上的第三方 HTTP 客户端——**他们不信任他们不能 instrument 的代码**。这条原则对 Go、Rust、TypeScript 团队同样适用，只是表达方式不同（middleware、trait wrappers、higher-order functions）。
5. **"在类型里"和"运行时检查"是 portfolio 决策，不是哲学站队**。教堂派和帐篷派都是反面教材；中间地带需要明确的启发式（静默腐败 → 进类型；大声失败 → 运行时；领域内在矛盾 → 不要硬塞）。这条对任何想认真做 "API as contract" 工作的团队都是营养品。
6. **少数派语言生态的真正风险不是池子小，而是池子里人的"性向"**。Haskell 吸引理想主义者；Rust 吸引完美主义者；Lisp 吸引哲学家；Erlang 吸引固执的可靠性派。**每种性向都同时是 leverage 和 liability**。Duncan 给出的解药——主动培养 pragmatism 文化——比"招人时筛掉理想主义者"更现实：**你需要的是 idealist 的好奇心 + pragmatist 的纪律，不是其中之一**。

这六条命题里没有一条只适用于 Haskell。**但 Haskell 的"陡峭"让这六条命题变得显眼**——一个本来可以靠 Python 的"反正能跑"含糊过去的组织失误，在 Haskell 里会立刻在 PR 评审、CI、招聘漏斗里给你警报。这或许就是为什么 Mercury 能在 200 万行 Haskell 上跑 2480 亿美元交易额——**不是因为类型证明了什么定理，是因为类型把组织失误暴露得太早，让他们不得不在组织层面真的去解决**。

把这个观点放进我之前导读过的[《Emacs 化的软件世界：当 AI Agent 让每个人都能写自己的原生应用》](/post/good-read-emacsification-of-software/)的语境里也很有意思——Emacs 化的趋势让"个人 leverage"变得无可估量，但**组织 leverage 仍然来自把隐性知识转化为可执行的接口**。在那个文章描述的未来里，Duncan 的方法学比 LLM agent 更值钱：**任何不能被 agent 一句话覆盖的细节，都会被压进类型系统、durable workflow、observability surface 这种"agent 可发现"的载体**。Mercury 这种 Haskell-heavy 的组织，可能反而是 LLM 时代最容易被 agent 接管运维的工程文化样本——因为他们已经把多数运营知识从口头传统转写成了机器可读的契约。

最后想留一个不太舒服的问题给所有非 Haskell 的同行：**你的代码库里有多少"必须记得在 A 之后调 B"的咒语？它们今天住在哪里？三年后你的当前同事走光的时候，它们还在那里吗？**——Duncan 的全部论证，最终能不能让你想用 Haskell 不重要；**它让你想清楚"咒语托管"这件事在你的语言、你的组织、你的工具链里今天用什么形式存在，就已经回本**。

## 5. 配套资料导览

- **`mindmap.svg`**：本文导读的思维导图（深色主题），把 Safety-II、Purity-as-boundary、Type-encoded incantations、Durable execution、Records of functions、Idealist liability 这六个主轴的关系画成一张可一眼看清的脑图。
- **`concept-cards.md`**：12 张关键概念卡片，把 Hollnagel/Woods、`runST` 的 rank-2 trick、Mercury 的 `Transact` 模式、Temporal 的"workflow as pure function over history"、interceptor monoid 等抽象点拆成卡片大小的 unit。
- **`glossary.md`**：32 条英中对照术语表，覆盖 Haskell 类型系统、可靠性工程、durable execution、可观测性、和组织工程的关键词，方便非 Haskell 背景读者快速跟上。
- **`cover.svg`**：封面图，深色调，主视觉是"接口边界 vs 危险机器"的二元抽象——内部的 `unsafe` 漩涡被一条 rank-2 类型签名锁在里面。

## 6. 谁应该读这篇文章

- **任何在快速成长的工程组织里负责"标准、工具、平台"的工程师**——不管你的栈是不是 Haskell，Duncan 描述的运营压力对你完全成立。
- **架构师 / 技术领导**：本文是过去三年里我读到的最浓缩的"resilience engineering + practical type theory + production reality"教材；把它当作 *Site Reliability Engineering* O'Reilly 那本书的非 Google 视角补丁来读。
- **正在评估非主流语言（Haskell / Rust / Lean / Roc / Gleam）的团队**：第 §2.9 节"理想主义者陷阱"是任何这类决策必读的反向尽职调查。
- **Temporal / 工作流引擎用户**：§2.4 给了我见过最优雅的"workflow as pure function over history"心智模型。
- **任何写库的人**：§2.7 关于 records of functions、callback 而非 import-level logging、`.Internal` 模块策略的部分，**几乎逐字适用于 Python / TypeScript / Go / Rust 库作者**。
- **对"组织里的隐性知识为什么会蒸发"这个题目感兴趣的人**：Duncan 把它和 Patrick McKenzie 的"2x 增长公司"观察、Slack 自动删除老消息、wiki 腐败的命运织成了一张完整的图。

---

**编辑后记**：Duncan 这篇 5 万字长文真正打动我的，是它没有走"我们用 X 重写了 Y，节省了 Z%"那种 case study 套路，**它选了一种更难也更稀有的写法——把工程实践、组织现实、可靠性哲学、招聘市场、和库生态道德编织在一起**。它读起来不像炫耀，更像一位资深医生写下的临床笔记。如果你只能从 2026 年上半年的全部技术阅读里选三篇放进永久收藏，**这一篇是其中一个**。
