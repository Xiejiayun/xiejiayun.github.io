---
title: "【好文共赏】Redis 的野心代价：当一个\"远程字典服务器\"想成为一切，它就什么都不是了"
description: "Charles Leifer 借 antirez 的 Array 类型 PR 切入，沿着 BSD 改 AGPL、RESP3 的二次系统效应、Disque 的早夭、Redis-Raft 被 Jepsen 打穿、再到 Valkey 的反扑，写了一篇站在 2026 年回看 Redis 十五年的总账：让 Redis 当年成功的全部基因，正被它自己的野心一一吃掉。"
date: 2026-05-14
slug: "good-read-redis-cost-of-ambition"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Redis
    - 系统设计
    - 数据库
    - 开源
draft: false
---

> 📌 **好文共赏 · Editor's Pick**
> 原文：[Redis and the Cost of Ambition](https://charlesleifer.com/blog/redis-and-the-cost-of-ambition/)
> 作者：Charles Leifer（[peewee ORM](https://github.com/coleifer/peewee) / [cysqlite](https://cysqlite.readthedocs.io/) 作者，长期写 SQLite/Redis 底层）
> 发布：2026-05-12 · Lobsters 一周 Top 6 · 阅读时长 ≈ 12 分钟
> 多模评分：**Opus 9.0 / Sonnet 8.5 / Gemini 8.7（综合 8.7/10）**
> 一句话推荐：站在 Valkey 反超、antirez 用 AI 写新 Array 类型这两个 2026 年的时间点回头看，Redis 这台"远程字典服务器"早已不再是它当年承诺的那台——而**让它当年赢的全部理由，正在被它今天的野心一一对冲掉**。

## 为什么值得读

这篇文章在技术写作的稀有交叉点上——**既不是又一篇"Redis vs Valkey 营销稿"，也不是技术八卦**——而是一份冷静的"系统设计的总账"。Charles Leifer 不是吃瓜群众，他自己写过 [peewee](https://github.com/coleifer/peewee)、写过 SQLite 的 Python 驱动、写过自家的 Redis 协议复刻教程（[多年前那篇 _Write your own miniature Redis_](http://charlesleifer.com/blog/building-a-simple-redis-server-with-python/) 至今还是他博客最热门的文章）。他理解 antirez 当年是怎么把 Redis 从一段 [TCL 写的实验代码](https://github.com/antirez/redis-history)演化成行业基础设施的，所以他写这篇时不带情绪，只是按时间轴把账一笔笔翻出来：

- **2009–2012 的 Redis**：自我定位是 _advanced key-value store_、_data structure server_，刻意回避"database"这个词。
- **2015 年 Disque**：antirez 自己承认是 _astronaut mode_（"无具体用例，只是受刺激而写"）—— Charles 当年就预测会被弃，事实证明被弃。
- **2017–2020 的 Redis-Raft**：Aphyr 的 Jepsen 报告里[发现 21 个严重问题](https://aphyr.com/posts/359-jepsen-redis-raft-1b3fbf6)，包括 5 个会丢已提交写入的 bug——"第一次测试的版本基本上不可用"。
- **2024 年的 BSD 改 AGPL 大翻车** + 2025 年的退守三授权 + 2026 年 Redis 把自己定位成 _"The Real-Time Context Engine for AI Apps"_。
- **2026 年 5 月 4 日**：antirez 借 AI 辅助提交了一个 22258 行的 [Array 类型 PR #15162](https://github.com/redis/redis/pull/15162)，引爆这场反思。

Charles 把这一切串成一条主线——**Redis 之所以赢，是因为它把"哪些功能 _不_ 做"做得极其克制；它之所以正在输给 Valkey，是因为这条克制的线被一点点抹掉了**。

文章的另一个价值是：**作为一个对 antirez 充满敬意的同行**，作者没有把这归因于"antirez 变了"或"VC 太贪"，而是给出了一个更普适的答案——**ambition（野心）**。野心既能造就 Redis 2.0，也能毁掉 Redis 8.0。这个判断不仅适用于 Redis，也适用于读这篇文章的你正在维护的任何一个有十年以上历史的系统（这点和我们之前推荐的[《资深开发者为何"说不清"自己的价值》](/post/good-read-senior-developer-speed-scale-decoupling/)里讲的"复杂度厌恶"形成了奇妙的呼应）。

---

## 核心观点深度解读

### 1. 切入点：一个 22258 行的 PR，和它没说出口的事

文章的引爆点是 5 月 4 日 antirez 提交的 [Redis Array 类型 PR](https://github.com/redis/redis/pull/15162)。这个 PR 本身在工程上**毫不平庸**——它用 4096 元素切片 + 稀疏编码 + 超级目录的三层结构，让一个原生数组在 Redis 里同时具备 O(1) 索引、范围扫描、ring buffer 语义。antirez 在 PR 描述里给出了让人心动的卖点：

> 原文：Hashes give you random lookups, but you have to store an index as a key, and have no range visibility. Lists give you appending and trimming, but what is in the middle remains hard to access. Streams give you append-only events, which is another (useful, indeed) beast.

但 Charles 立刻挑出了 antirez 没说的那部分——Redis 已经有了：JSON 类型（自带数组）、Time-Series（自带索引）、Sorted Set（在某些场景可以当数组用）。**也就是说，一个声称"缺少索引型数据结构"的系统，其实已经有三个半数据结构在干同样的事情**。

这就是整篇文章的钩子：**当一个系统增加一个新数据结构的理由不再是"用户需要"而是"现有的三种都有点别扭"，这本身就是危险信号**。

### 2. 当年的 Redis 凭什么赢：三个被人忘记的克制

Charles 用一段非常精炼的回顾告诉我们 Redis 2011 年凭什么"几乎一夜之间"出现在所有人的技术栈里——不是 memcached 的简单升级，而是三个**互相耦合**的设计决策的乘积：

**协议：简单到能一小时写完，丰富到能表达复杂类型**。RESP（Redis Serialization Protocol）的设计目标极其克制——基于行的、人类可读的、能用 telnet 调试的。Charles 自己写过教程证明这一点：你可以用一个下午写出一个能跑通 GET/SET/INCR/LPUSH 的迷你 Redis。这种"客户端零摩擦"是 Redis 早期生态爆炸的隐形发动机——Python、Ruby、Go、Node 都迅速有了好用的客户端。

**单线程 + 事件驱动 + 内存**。这三件事是**捆绑出售**的：

> 原文：By being single-threaded, all operations are guaranteed atomic, full-stop. This eliminates a huge class of complexity and makes Redis easy to reason about.

单线程的代价是必须用非阻塞 I/O；非阻塞 I/O 要工作，就必须把数据放内存里让操作快到不会阻塞其他客户端。三者缺一不可。但**回报是巨大的**——所有操作天然原子，开发者不需要为了一个简单的"读—改—写"去研究 MVCC 或写 Lua 脚本。这是 Redis 真正的护城河，也是 RESP3 协议、多线程改造、客户端缓存协议这些"现代化"决策最先动摇的东西。

**数据结构的选择是"taste"而不是"覆盖"**。链表、哈希表、集合、有序集合——四个原语就覆盖了 Web 应用 80% 的弹药需求：缓存（string + expire）、队列（list）、结构化数据（hash）、锁/计数器/限流/排行榜（不同组合）。Charles 用了一个非常精准的词——_tastefully-chosen_（有品味地挑选过的）。这跟"应有尽有"是反义词。

### 3. 野心的拐点：从"data structure server"到"数据库"

Charles 找到了一句几乎可以做 T 恤印花的总结：

> 原文：Some features have been genuinely useful additions, such as BZPOPMIN added in 5.0... Others struck me as being extremely un-Redis-y, like ACLs. But mostly, there seems to be a desire to make Redis be everything for everyone.

接着他列了一份"Redis 追的 HN 热门词清单"：

| 那年 HN 在聊什么 | Redis 的反应 |
| --- | --- |
| MongoDB 存 JSON | Redis 应该是文档数据库（RedisJSON 模块） |
| Elasticsearch 做全文搜索 | Redis 应该是搜索引擎（RediSearch 模块） |
| 图数据库火了 | Redis 应该是图数据库（RedisGraph，后被废弃） |
| Kafka 的 buzz | Redis 应该是流处理平台（Streams） |
| ZooKeeper 重要 | Redis-Raft 走起 |
| InfluxDB 酷 | RedisTimeSeries 模块 |
| AI 故事不能缺 | 向量索引 + "Real-Time Context Engine for AI Apps" |

这张表本身就构成了对 Brooks 在《人月神话》里描述的**second system effect**（第二系统效应）的当代注解——一个工程师/团队在做完第一个简洁系统之后，会把所有"上次没做"的功能塞进下一个系统，结果几乎必然走样。Redis 不是被某一个错误决策毁掉的，**而是被十年间几十个"看起来都很合理"的扩展决策累加毁掉的**——这点在我们[《可塑系统的回归》](/post/malleable-systems-design-for-change-2026/)里也有过类似讨论，那篇文章批判的"future-proof 的万能抽象"，本质上就是 Redis 这条路。

### 4. Aphyr 的 Jepsen 报告：当一个 KV 想做一致性数据库

如果说"Redis 是文档数据库"是营销失败，那么 Redis-Raft 是**工程失败**——而这个失败被 Kyle Kingsbury（Aphyr）的 Jepsen 团队用近乎残酷的方式记录下来。Charles 直接引了那份报告里最扎心的一段：

> 原文（Aphyr 报告）：we found twenty-one issues, including long-lasting unavailability in healthy clusters, eight crashes, three cases of stale reads, one case of aborted reads, five bugs resulting in the loss of committed updates, one infinite loop, and two cases where logically corrupt responses could be sent to clients. The first version we tested (1b3fbf6) was essentially unusable...

把这段翻译过来：21 个问题、8 次崩溃、5 个会丢已提交写入的 bug、2 种逻辑上损坏的响应——而这是 antirez 主导开发的项目。Charles 没有用这段去否定 antirez 的能力（他甚至明确说"我对他的才华和品味有巨大的尊敬"），而是用它来说明一个更深的道理：**HA 消息分发、共识协议、严格可线性化的 KV——这些不是"Redis 再加一个特性"那么轻巧的事情，而是各自需要一整个团队多年攻坚的工程领域**。把它们做成 Redis 的一个模块，从一开始就是范畴错误。

### 5. Disque：作者预测被验证十年的故事

文章最有"老中医号脉"味道的一段是关于 Disque 的——Redis 衍生出来的消息队列产品。2015 年 antirez 发布 Disque 时坦白：

> 原文（antirez）：Disque was designed a bit in astronaut mode, not triggered by an actual use case of mine, but more in response to what I was seeing people doing with Redis as a message queue...

Charles 当年读到这句就预测了两件事：

1. **没有真实用例，作者会失去维护动力**（"开发兴趣会被长尾难题消耗殆尽"）。
2. **不会有人采用**——因为成熟的消息中间件已经太多（RabbitMQ、ActiveMQ、Kafka...），人们用 Redis 做消息队列的唯一理由是 _"懒得引入新组件"_，而不是 _"Redis 是消息队列里最好的"_。如果你要正经的消息队列，没人会选一个"看起来像 Redis 的"。

十年过去——Disque 8K stars、几乎零用户、模块化后再次被废弃。这个预测之所以准，是因为 Charles 抓住了**用户的真实需求函数**：人们用 Redis 做 X，从来不是因为它在 X 上比专门工具更好，**而是因为他们已经在用 Redis，并且不想再多引入一个组件**。这是一个相对值，不是绝对值。任何把 Redis 在 X 上的功能做"更专业"的努力——本质上都在错误地优化这个函数。

### 6. RESP3：second-system effect 的协议级标本

这一节虽然短，但对协议设计读者来说非常珍贵。Charles 一句话点穿了 RESP3 的根本问题：

> 原文：RESP3 has a lot of sharp edges and breaks the fundamental assumption in RESP2 of request/reply. The new protocol is in my opinion a classic second system failure mode straight out of Brooks.

RESP2 的最美之处不是它能表达多少东西，而是它的**请求-响应严格配对**——客户端发一个，服务器回一个，永远如此。这意味着客户端实现可以无脑同步、连接池可以无脑复用、错误处理可以无脑超时。RESP3 引入了 Push 类型（服务器主动推送），表面上看是"现代化"，实际上**直接打碎了 RESP2 的核心简单性假设**——客户端必须能识别"这个响应到底是不是我请求对应的回复"，于是连接管理、错误恢复、超时语义都要重新思考。

更讽刺的是，引入 Push 协议的核心动机之一是支持**客户端侧缓存**——也就是说 Redis（缓存）需要一个新协议来让客户端也能做缓存。Charles 用了一个绝妙的归谬：

> 原文：In a kind of reductio-ad-absurdum, Redis (lately the cache), now needs a new protocol to support caching on the client side as well.

### 7. 商业层的"换名易主"：从 Garantia Data 到 Redis Inc

这段历史 Charles 写得最冷峻——因为它跟 antirez 的工程决策几乎无关，但又彻底决定了 Redis 的命运：

- 一家叫 **Garantia Data** 的 NoSQL 托管公司，本来只是一堆 NoSQL 数据库的云服务提供商之一；
- 进入 Redis 托管业务，**改名 Redis Labs / Redis Inc**；
- 签下 antirez "合法化"自己；
- 几年后**拿到 Redis 商标权**；
- 2024 年祭出 BSD → AGPL 的"地毯式抽离"；
- 当社区炸锅、AWS/Google 公开支持 Valkey fork 后，被迫"战略撤退"，2025 年改成三授权（AGPL/SSPL/RSALv2 自选）；
- 2026 年的 Redis 落地页上，主打语已经变成 _The Real-Time Context Engine for AI Apps_，旁边并列着"免费试用"和"获取企业演示"两个按钮——开源标语和企业销售话术的尴尬共存。

Charles 没有道德审判，但他用一个超链接做了完美注脚：那条 2024 年 antirez 在自己博客上为 license 改动辩护的文章[评论区](https://antirez.com/news/121)——"老得正如你想象"。

### 8. Valkey：市场用脚投票

文章的结尾干净利落：

> 原文：Valkey's existence and adoption is the wider market's final verdict on this dynamic. Rather than chase features and bullet points, Valkey has invested in the un-glamorous work of improving multi-threaded performance, memory efficiency, cluster reliability and throughput.

[Valkey](https://valkey.io/) 是 Redis 改 license 后由 AWS、Google、Oracle、Ericsson 等共同主导的 BSD fork，由 Linux Foundation 托管。Charles 给出了一句几乎是结案陈词的总结——

**Valkey 把投资重心放在了"不性感的工作"**：多线程性能、内存效率、集群可靠性、吞吐量。这些是 _2011 年用户用 Redis 的那些理由的现代实现_，而不是"再加一个 AI 上下文引擎"。Valkey 是市场对"Redis 该是什么"做的最终判决。

这跟我们[《Figma 自建 Redis 代理冲六个 9》](/post/figma-redis-proxy-six-nines-platform-engineering-2026/)里观察到的趋势完全一致——**严肃的工程团队，会绕开 Redis 官方版去搭自己的"克制的 Redis"**。

---

## 延伸阅读图谱

### 📚 Charles Leifer 的相关代表作（建议按顺序读）

1. **[Building a simple Redis server with Python](http://charlesleifer.com/blog/building-a-simple-redis-server-with-python/)** —— 他自己最热门的博文，手把手教你写一个 mini Redis。读完你会真切理解"协议简单到一小时写完"是什么意思。
2. **[cysqlite — a new sqlite driver](https://charlesleifer.com/blog/cysqlite---a-new-sqlite-driver/)** —— 2026 年 2 月发布，从零写了一个 SQLite Python 驱动。和本文形成的对比是：他自己写新系统时怎么克制。
3. **[Tokens and Dreams](https://charlesleifer.com/blog/tokens-and-dreams/)** —— 2026 年 5 月初的 AI 反思文，恰好跟本文是同一作者的"姐妹篇"。
4. **[Slopification and Its Discontents](https://charlesleifer.com/blog/slopification-and-its-discontents/)** —— AI slop 与代码品味的讨论，可以看出他对"品味"这个词的严肃使用。
5. **[Why I won't use Disque](https://charlesleifer.com/blog/disque-the-deferred-promise/)** —— 2015 年的那篇预测文章本尊（本文里多次引用）。

### 📄 相关论文 / 经典文献

- **Brooks, F. P. — _The Mythical Man-Month_, "The Second-System Effect" 章节**。Redis 8.x 时代的所有"过设计"病例都是这一章的活体标本。
- **Kyle Kingsbury (Aphyr) — _Jepsen: Redis-Raft 1b3fbf6_**：[aphyr.com/posts/359](https://aphyr.com/posts/359-jepsen-redis-raft-1b3fbf6)。文章里引用的报告原文。Aphyr 的 Jepsen 系列至今仍是分布式系统正确性测试的金标准。
- **Dynamo 论文 (DeCandia et al., SOSP 2007)** 和 **Bigtable 论文 (Chang et al., OSDI 2006)** —— Charles 提到的"那个 NoSQL 时代的两大圣经"，Redis 当年的对手坐标系。
- **antirez — _Redis persistence demystified_** (2012 经典)：[antirez.com/news/55](http://antirez.com/news/55)。看看 antirez 当年是怎么写技术文章的——同样的人，十几年的笔触变化本身就值得分析。
- **valkey.io / Valkey RFC：Multi-threaded I/O design**：Valkey 把"做克制的 Redis"具体到什么程度。
- **Redis Manifesto (antirez, 2017)**：[antirez.com/news/110](http://antirez.com/news/110)。manifesto 第 1 条就是 _"Redis is a Data Structures server"_，第 2 条就是 _"Redis is designed for systems where memory is the primary working set"_。十年后对照看，特别讽刺也特别诚实。

### 🔁 反方观点 / 平衡视角

- **antirez 自己的回应（如果未来发表）**：他在 PR #15162 评论区有一些回复值得追读，特别是关于 _"AI 辅助编程让我能再处理 Redis 这种复杂系统"_ 的说法。
- **Redis Inc 商业视角**：从一家上市/被收购预备公司的角度，"Redis 是不是变成 AI Context Engine"和"Redis 是不是仍然简洁"是两个完全不同的问题——前者关系到估值，后者关系到 antirez 的工程美学。读这篇时，要意识到 Charles 是站在用户的位置说话，不是股东的位置。
- **YugabyteDB / DragonflyDB 视角**：这些"打 Redis 的兼容数据库"如果发声，会论证多线程、强一致、SQL 接口才是 KV 演化的方向。这跟 Charles "Redis 应该回到 2011 的简洁"的判断是直接冲突的。

### 🔗 站内交叉阅读

- 《[Figma 自建 Redis 代理冲六个 9：平台工程的钟摆](/post/figma-redis-proxy-six-nines-platform-engineering-2026/)》—— 严肃工程团队怎么"治"官方 Redis 的躁动
- 《[可塑系统的回归](/post/malleable-systems-design-for-change-2026/)》—— 对"future-proof 的万能抽象"信仰的清算，本质同源
- 《[【好文共赏】Emacs 化的软件世界](/post/good-read-emacsification-of-software/)》—— Emacs 是"无限可扩展"的代价的最早样本，Redis 走的是同一条路
- 《[【好文共赏】资深开发者为何"说不清"自己的价值](/post/good-read-senior-developer-speed-scale-decoupling/)》—— 资深工程师对"过度复杂"的天然厌恶，本文给出一个具体案例

---

## 编辑延伸思考：野心是一种损耗品

读完 Charles 这篇，我反复回到一个问题——**为什么是 Redis，不是 PostgreSQL？**

PostgreSQL 同样有三十多年历史、同样从一个学术项目演化成行业基础设施、同样在过去十年里疯狂加功能（JSONB、并行查询、逻辑复制、表分区、向量索引……）。但你不太能想象一篇标题叫《PostgreSQL and the Cost of Ambition》的文章引爆 HN。**为什么？**

我有三个候选解释，可能各贡献一部分：

**第一，PostgreSQL 的扩展是"加层"，Redis 的扩展是"加心脏"**。PostgreSQL 的新功能几乎都是"在不破坏 ACID 和 SQL 抽象的前提下"叠加上去的——JSONB 是一个新数据类型，但它不需要 PostgreSQL 改协议；pg_vector 是一个扩展，但它不要求所有客户端重写。Redis 的功能扩展往往触及核心——RedisJSON 是模块、Streams 改了语义、RESP3 改了协议、客户端缓存改了客户端职责。**当一个系统的扩展会修改它的核心契约，每一次扩展都是核心契约的稀释**。

**第二，PostgreSQL 没有"VC 商业化倒逼"这个外力**。Redis 走到 AGPL 这一步，根本原因是 Redis Inc 必须在 AWS 把 Redis 当成 ElastiCache 卖之前找到自己的"控制点"。这个商业压力会自然转化成对 antirez 的产品压力——"我们需要一个 AI 故事"、"我们需要 enterprise-only 模块"。PostgreSQL 是一个真正意义上社区治理的项目，没有一家公司能对核心 commit 节奏施加这种压力。

**第三，最难讲的——antirez 的个性**。Charles 在文中多次表达"对 antirez 的尊敬"，但他用了一个非常精准的词：_a developer's ambition to solve complex problems_。antirez 是那种"看见难题就忍不住要碰一下"的工程师——这是 Redis 当年能做出来的根本原因，也是 Disque、Redis-Raft、RESP3 都会出现的根本原因。**让 Redis 成功的那种气质，跟让 Redis 走偏的那种气质，是同一种气质**。

这个判断如果成立，对所有读这篇的工程师有一个推论——**ambition 是一种损耗品**。当你年轻、当你的系统年轻时，野心是燃料；当你的系统已经被几十万人依赖、已经有完整生态时，野心需要被严格预算化。

具体到我们日常工程：

- **每加一个特性前，先问"它是否会修改我系统的核心契约？"**。如果会，那不是加一个特性，那是开一个新产品。Streams 当年应该是另一个项目（Redis Streams 完全可以叫"antiqueue"），不是 Redis 的一部分。
- **小心"我们的用户也在用 X 工具"这句话**。这句话往往会被翻译成"我们应该把 X 工具的功能内化"。但用户用 X 工具的原因，几乎从来不是"X 工具比专门工具更好"，而是"我已经在用了"——这种相对优势复制不到一个内置功能上。
- **不要因为商业压力把工程契约稀释**。如果 VC 要求"你必须有 AI 故事"，正确答案是新做一个项目（哪怕叫 "Redis AI"），而不是给 Redis 加一个 AI 标签。**协议的可信、契约的稳定，是任何基础设施最不可再生的资产**。

最后，我想留一个开放问题：**如果 Charles 这篇文章在 2017 年写出来，会改变什么吗？** 我倾向于认为不会——商业压力、个人气质、社区惯性的合力太大。这意味着这种"野心代价"几乎是系统软件生命周期里**无法避免的中年危机**。能做的只有两件事：(1) 把意识到这一点的时间提前；(2) 当 fork 出现（Valkey、PostgreSQL 的 EnterpriseDB 当年的分裂、Elasticsearch 的 OpenSearch 分裂）时，**不要把它解读成对原项目的攻击，而是市场在重启时钟**。

Valkey 不是 Redis 的敌人，**Valkey 是 2011 年的那个 Redis 借了个新身份继续活下去**。

---

## 配套资料导览

- **`mindmap.svg`** — 思维导图：从"PR #15162"为根节点，展开技术（数据结构/协议/单线程）、商业（License/Trademark）、文化（Astronaut mode/Second System Effect）、生态（Valkey/Jepsen）四大分支
- **`concept-cards.md`** — 12 张概念卡片：覆盖 RESP2/RESP3、Single-threaded event loop、Second System Effect、AGPL 与 BSD 区别、Jepsen 测试、Valkey 治理结构等
- **`glossary.md`** — 30+ 条英中对照术语表，涵盖 Redis 数据结构、协议、商业实体、相关人物
- **`cover.svg`** — 深色封面图，主视觉是一个"过载的钟摆"图案

---

## 谁应该读这篇

- **任何维护过五年以上历史系统的工程师** —— 你的系统中年危机大概率长得跟 Redis 一样
- **基础设施 SaaS 创业者** —— 你跟 VC 的张力 vs 你跟用户的契约，这篇是教科书案例
- **协议 / API 设计者** —— RESP2 → RESP3 的演化是"二次系统效应"的协议级标本
- **数据库 / KV 选型决策者** —— 在 Redis 7.x、Redis 8.x、Valkey 之间做选择前必读
- **关心开源治理 / 商业模型的开发者** —— Garantia Data → Redis Inc → AGPL 的演化路径有非常完整的史料
- **任何在 2026 年还在写"产品要不要加 AI 标签"PRD 的人** —— Redis 把自己改名 _Real-Time Context Engine for AI Apps_ 之后，市场用 Valkey 给出了答案

---

*本文为【好文共赏】栏目导读，原文版权归 Charles Leifer 所有。文中引用均不超过原文 10%，建议读者直接访问[原文链接](https://charlesleifer.com/blog/redis-and-the-cost-of-ambition/)阅读全文。*
