---
title: "【好文共赏】当 part 数从 30k 涨到 160k：Cloudflare 用三个补丁，把 ClickHouse 查询规划器从一把互斥锁里救出来"
description: "Cloudflare 工程师 James Morrison 和 Christian Endres 写了一篇教科书级的 OLAP 性能调优实录：账单流水线突然变慢，I/O、内存、行数都正常，flame graph 从 CPU 切到 Real 才暴露真凶——MergeTreeData 的一把独占互斥锁。从 shared_lock 到 deferred copy 再到 binary search，三步上游 PR，把 8x 加速带回 ClickHouse 社区。"
date: 2026-05-18
slug: "good-read-cloudflare-clickhouse-mutex-contention"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - Cloudflare
    - ClickHouse
    - OLAP
    - 性能调优
    - 互斥锁
    - 火焰图
    - 数据库工程
    - 上游贡献
draft: false
---

> 📌 **好文共赏 | Editor's Pick**
>
> 原文：[Our billing pipeline was suddenly slow. The culprit was a hidden bottleneck in ClickHouse](https://blog.cloudflare.com/clickhouse-query-plan-contention/)
> 作者：James Morrison & Christian Endres（Cloudflare 分布式系统工程团队）| 发布于：2026-05-14 | 阅读时长：约 9 分钟
>
> **多模评分**：Opus 9.2 / Sonnet 8.8 / Gemini 8.6（综合 **8.87 / 10**）
>
> **一句话推荐理由**：这是 2026 年 5 月最值得每一位"以为自己懂数据库性能"的工程师重读一遍的故事——一次看似无害的分区键改动，把一个百 PB 级 ClickHouse 集群的查询规划器，从一把独占互斥锁里逼出了三个上游 PR；从 30k parts 到 160k parts，I/O、内存、行数全程"正常"，只有 flame graph 从 CPU 模式切到 Real 模式那一瞬间，看见了真正的真相。

## 为什么值得读

如果你只把这篇博客读成"Cloudflare 又修了个 ClickHouse 性能问题"，那等于把一份完整的工程教科书翻成了一页 release note。

这篇文章值得花一个下午去研读，是因为它**罕见地、毫无遮掩地，把一次中级根因分析的全过程亮给了所有人看**：从一个"看起来很合理"的设计决策开始（per-namespace retention 用复合分区键来做），到几个月后只有"part 总数和查询时长强相关"这一条孤零零的散点图给出方向，再到 flame graph 看错（CPU 模式只采样**活动**线程）所导致的 5% 死胡同补丁，最后转去 Real 模式才看见**线程都在排队等锁**——这条故事线，几乎每一拍都对应着真实世界里你曾经犯过、或者将来必然会犯的错误。

更关键的是，它告诉了你**修复路径上每一步背后的那个"反直觉"**：

- **第一直觉**：以为是 CPU 热点 → 改了一下 `filterPartsByPartition` 的启发式顺序，只快了 5%；
- **第二个真相**：是**锁竞争**，而且竞争的是一个连"修改"都不需要的纯读路径 → `std::shared_lock` 立刻让曲线砸下来；
- **第三个真相**：锁不卡了，但每个 query 都要**完整复制一遍上万条 parts 的 vector** → 引入 cached shared copy，复制成本"延迟到写入端"；
- **第四个真相**：part 数继续涨，线性扫描又把红线拉了回来 → 利用"vector 已经按 (namespace, day) 排序"做 binary search，把曲线再次砍掉一半，并**首次打断了"part 数 ↔ 查询时长"那条线性关系**。

这是一条非常"扎实"的链条。它本质上是一篇关于**抽象层泄漏（leaky abstraction）的案例研究**：分区键是表设计层的概念，互斥锁是存储引擎实现层的概念，本来风马牛不相及——但当 part 数从 30k 涨到 160k 时，前者的决策开始通过"列表长度 × 复制频率 × 临界区粒度"三条暗管，把代价倾倒到后者的代码路径里。

而 Cloudflare 这次的处理方式，也是这篇文章另一个值得被反复看的地方：他们没有止步于"在我们自己的 fork 里把问题打掉"，而是把每一步都上游成了 [PR #85535](https://github.com/ClickHouse/ClickHouse/pull/85535)。"Up to 8x faster `SELECT` queries with heavy partition pruning on tables with 10K+ parts"——这个 changelog 现在跟着 ClickHouse 25.11 一起走向了世界上每一个超过 1 万个 parts 的表。这一点，与我之前在[《【好文共赏】当"空闲"不是空闲：Cloudflare 一次 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/)里讨论的 Cloudflare 工程文化遥相呼应——它不只是一家 CDN 公司，更越来越像**一家"用生产事故反向哺育上游开源项目"的研究所**。

## 核心观点深度解读

### 1. 一个 PB 级"通用宽表"系统的诞生与它的隐性债

要理解这篇博客，必须先理解 Cloudflare 在 2022 年搭起来的那套叫 **Ready-Analytics** 的内部平台。

它本质上是一种"内部多租户的 ClickHouse 即服务"：内部团队不再自己设计表，而是把数据 stream 进一张巨大的共享表，每一条记录都带一个 `namespace` 字段做"租户隔离"。schema 是标准化的——20 个 float 字段、20 个 string 字段、一个 timestamp、一个 `indexID`。`indexID` 是一个字符串，参与主键，所以每个 namespace 可以用自己最优的二级排序方式来组织数据。

最终的主键长这样：`(namespace, indexID, timestamp)`。

这种"宽表 + namespace 区分 + 自由 indexID"的设计，在 2022 年看起来非常聪明：onboarding 流程被压缩到几乎为零，新接入一个团队不用 DBA 介入，不用 schema 设计评审，写一个 producer 就能开始把数据灌进来。到 2024 年 12 月，这张表已经超过 **2 PiB**，写入速率是每秒数百万行，"几百个应用"都跑在它上面。

但所有"通用宽表"都有它的债。Ready-Analytics 这张表的债，是它的**保留策略只有一个**——按天分区，超过 31 天的分区直接 drop。

这听起来无关紧要，直到你意识到：

- 有些团队需要保留**数年**（合规、审计、合同义务）；
- 有些团队只需要保留**几天**；
- 但 Ready-Analytics 给所有人只发同一张票——31 天。

于是出现了一种典型的"内部基础设施滑坡"：高保留需求的团队被迫退出 Ready-Analytics，自己搭一套"按传统方式"的 ClickHouse 集群——这部分团队成了内部分布式存储里**最不规范、最难治理、最容易出事**的那一拨。原文一句话说得非常克制：

> 原文："This restriction meant these use cases couldn't use Ready-Analytics and had to opt for a conventional setup, which has a far more complex onboarding process."

这是一句典型的"我们都知道发生了什么但不能写得太狠"的工程语言。翻译一下就是：**Ready-Analytics 的统一保留策略，正在反向地分裂 Cloudflare 内部的数据基础设施**。所以 2024 年底他们决定动手——把这张表升级成支持 per-namespace retention，作为整个平台延续下去的前提。

而这次升级，就是后来那场互斥锁地震的起点。

### 2. 一次"看起来不会有性能影响"的分区键变更

Ready-Analytics 的团队当时面前有两条路。

**第一条**：Table-per-Namespace。每个租户一张独立的 ClickHouse 表，每张表自己的保留策略。这个方案在概念上最干净，但代价是要写一整套"按需创建、删除、迁移成千上万张表"的自动化系统——光这个 control plane 的复杂度就足以再立一个项目。

**第二条**：直接改分区键，从 `PARTITION BY day` 改成 `PARTITION BY (namespace, day)`。原有的"删过期分区"那套 retention job 不动，但删除的粒度从"按天"变成了"按 (namespace, day)"——天然就支持了每个 namespace 自己的 TTL。

他们选了第二条。理由很自然：**改一行 DDL，几乎不需要写新代码**。

更关键的是，他们做了一个**看上去无可指摘的性能假设**：

> 原文："since every query is filtered by a specific namespace, the number of parts read by any single query shouldn't change. We believed this meant performance would be unaffected."

翻译过来：既然每个 query 都按 namespace 过滤，那即使整张表的 parts 总数变多了，**每个 query 实际读到的 parts 数量不变**——因此性能"应该"不会受影响。

这是一个非常诚实的假设——而且它在数学上**几乎正确**。错就错在那个"几乎"。它默认了 ClickHouse 的查询规划器是"按需访问 parts 列表"的——而真实情况是：**规划器需要在所有 parts 中筛选出"自己需要的那些"，这个筛选过程的代价，是和整张表的 parts 总数线性相关的**。换句话说，"读了多少 parts"和"看了多少 parts"之间，隔着一整个查询规划阶段，而那个阶段的复杂度被悄悄藏在了 `filterPartsByPartition` 这种听起来"应该很便宜"的函数里。

这一点是这篇文章里最值得每个数据库工程师抄下来贴墙上的一句教训：

> **"读多少"和"看多少"，不是同一个量级的代价。**

类似的"看似线性、实则带常数项"问题，也曾出现在我之前写过的[《【好文共赏】Redis 的野心代价：当一个"远程字典服务器"想成为一切，它就什么都不是了》](/post/good-read-redis-cost-of-ambition/)里——只是那篇讲的是 **product surface 的复杂度**怎么把代码库压垮，而这篇讲的是**单表分区维度**怎么把规划器压垮。它们是同一种病在不同器官上的表现。

### 3. 一张几乎被忽略的散点图

迁移在 2025 年 1 月开始。Ready-Analytics 团队用 ClickHouse 的 `Merge` 表把新旧表对外统一暴露——新写入进新分区方案的表，旧数据从原表上慢慢 age out。

两个月后，2025 年 3 月底，账单团队报告了第一个"奇怪"的现象：他们每天跑的聚合 job 越来越慢，**deadline 已经在敲门**——这些 job 是有强时间约束的，跑不完就出不了账单，出不了账单几亿美元的收入就要被推迟。

Ready-Analytics 团队按"标准操作"挨个排查：I/O？正常。内存？正常。每个 query 扫描了多少行？正常。每个 query 读了多少 parts？**正常**——这正是他们当初做出"性能不会受影响"假设的那一栏数字。

事情一度走进死胡同。

直到有人花了几天时间，把"集群整体的 parts 总数"和"查询平均时长"做了一张散点图——**两条曲线**——一条线性向上的红色 parts 数，一条几乎同步的查询时长。相关性极强。

这张图是这篇博客里最被低估的一张。它没有任何花哨的可视化、没有热力图、没有 percentile，就是简单的两条时间序列叠在一起。但它做的事情非常重要：**它第一次把"看起来无害的全局指标"（parts 总数）和"用户能感知的性能指标"（query duration）连成了一根因果线**。

很多团队在这种时刻会陷入一种"指标盲区"：他们看的是**每个 query 自己的成本曲线**，但真正在变化的是**集群级别的状态量**。这两种视角的区别，常常需要一个团队踩过坑才能形成本能。

> 原文："But why? If we weren't reading the extra parts, why did their mere existence slow us down?"

这句话本身就是一个非常好的工程问题模板。它在问的，其实是 **"什么东西的代价不取决于我用不用它，而取决于它存不存在？"** 答案，往往是某种全局结构的遍历或复制——而那种东西，95% 的概率藏在锁后面。

### 4. flame graph 的 "CPU 模式" 和 "Real 模式" 之间，差着一整把锁

下一步他们打开了 ClickHouse 自带的 `trace_log`，这是一张内置表，记录运行时采样的栈轨迹，并且和用户 ID、query ID 等 metadata 关联——意味着你可以非常精确地过滤出"只看 leaf SELECT 的火焰图"。

第一张 flame graph 出来，看起来**"目标已经锁定"**：`filterPartsByPartition` 这个函数吃掉了 45% 的 CPU 时间。所以他们写了第一个 patch——重新排序了筛选谓词的启发式顺序，让大概率命中的条件先短路。

结果：5% 改善。

这是一个**最危险的中间结果**——它给出了"你走对了方向"的错觉，但其实你只是修了一块沿途的鹅卵石，真正的山还在后面。

转折点是他们决定换一种采样模式。

`trace_log` 默认是 "CPU" 采样——只在线程**实际占用 CPU** 的时候采集栈。这是绝大多数 profiler 的默认行为，背后的假设是"你想找出谁在烧 CPU"。

但他们改成了 **"Real" 采样**——所有线程，无论是不是在跑 CPU，都被采集，包括那些**在等锁、在睡眠、在 IO**的线程。

新 flame graph 一出来：

> 原文："More than half of our query duration was spent waiting to acquire a single mutex (MergeTreeData) that protects the table's list of parts."

**超过一半的查询时间在等一把锁。**

这把锁就是 `MergeTreeData` 里那把保护 active parts list 的互斥锁。每个 query planner 要做一件事：

1. 拿一把**独占锁**（exclusive lock）；
2. 把**整张表的 parts 列表**完整地复制一份到自己的局部变量；
3. 释放锁；
4. 在那份本地副本上做过滤，找出自己关心的那几个 parts。

当 part 数从 30k 涨到 100k+、并发 query 上百，这步操作就变成了一条**单线排队**：所有 planner 在锁前排成一行，谁拿到谁先复制，复制完释放，下一位继续。锁不是 deadlock，但它在用一种"看起来一切都在动"的方式，把吞吐量按住了脖子。

**这一段教学价值密度极高。** 对任何写过 profiler、读过 flame graph 的工程师，下面这条规则值得抄进每一份 onboarding 文档：

> **当你的瓶颈"看起来"不是 CPU bound，但 CPU profile 显示某个函数吃了 40%-50%，先怀疑你只是在看 CPU profile。打开 wall-clock / Real profile，看那些在等待的线程在等什么。**

这一点和我之前写过的[《当 AI 不再只看 CPU：火焰图驶入 GPU profiling 时代》](/post/ai-flame-graphs-gpu-profiling-2026/)讨论的"采样模式定义你能看到什么"的主题完全一致——profiler 的盲点，永远比 profiler 的热点更值得花时间确认。

### 5. 三步上游 PR：从 shared_lock 到 deferred copy 再到 binary search

确认问题之后，Cloudflare 没有走"在 fork 里修一下就好"的传统路径，而是把三步优化全部上游到 ClickHouse 主仓库。

#### 第一步：把独占锁换成 shared lock

观察很简单——query planner 是**只读**的。它压根不修改 parts 列表，只是要拿来过滤一份本地副本。既然如此，没有任何理由用 `std::unique_lock`，应该用 `std::shared_lock`：写者依然互斥，但所有 planner 可以并发地进入临界区，并发地完成"复制 + 过滤"。

效果立竿见影。原文里那张图是这次调优中最戏剧性的一张：曲线在补丁部署的那一刻**直接砸下来**，锁竞争消失，所有 planner 不再排队。

这个改动的代码量大概率是十几行，但它背后的判断不是十几行——它要求工程师能在一份十年量级的 C++ 代码库里，**自信地论证某条临界区不需要写权限**。这是抽象阅读能力的展示。

#### 第二步：延迟那次"复制整张 parts 列表"的代价

shared lock 之后，吞吐恢复了不少，但还没回到迁移前的基线。再来一张 Real flame graph，新的热点显形：**复制 parts vector 本身**——四分之一的时间在 copy，另外四分之一在过滤（其中也涉及对 copy 出来的容器的访问）。

直觉上"复制一个 vector"应该很便宜。但当那个 vector 有 **10 万条**元素、被复制 **每秒上百次**，它就变成了一条主干道上的橡皮筋。

这一步的 fix 很有架构味：**把复制操作从"读路径"挪到"写路径"**。

具体做法：维护一份"共享的 parts 副本"（shared cached copy），所有只读的 planner 都从这个 cached copy 上读，不再各自复制。只有当 parts 集合**发生改变**——比如有新的 insert、merge、drop——才重新生成这个 cached copy。然后 planner 只需要对**自己最终筛选出来的那个小列表**做一次拷贝，而不是对全表 parts 都拷一份。

这是一个非常典型的**"把热路径上的重活搬到冷路径上"**模式。在 Linux 内核里这种叫 RCU（Read-Copy-Update）；在数据库里这种叫"MVCC 的 snapshot 缓存"；在分布式系统里这种叫"epoch-based reclamation"。**名字不同，思想一致**：让 reader 永远不付出复制的代价，把代价摊给 writer。

这两步改动合在一起，就是 [PR #85535](https://github.com/ClickHouse/ClickHouse/pull/85535)——题目叫 "Optimize selection of part list during query planning"，作者 `jawm`（James Morrison 的 GitHub 用户名），由 ClickHouse 核心维护者 azat 合并，并被打上 `Performance Improvement` 标签。changelog 的一句话是：

> **"Up to 8x faster `SELECT` queries with heavy partition pruning on tables with 10K+ parts"**

8 倍。**对所有 part 数过 1 万的表生效**。

#### 第三步：用 binary search 把"part 数 ↔ 查询时长"的相关性彻底掰断

但故事还没结束。

几个月后，Cloudflare 团队回头再看 trace_log，发现 flame graph 又长得跟最初一样——`filterPartsByPartition` 重新成了瓶颈。原因是：**parts 数在持续增长**，每 query 从全集里做线性筛选的代价，在 100k 量级时又把整体延迟拉了回来。

这一次的 fix 是一个**简洁但很漂亮**的算法替换。

观察是：parts 列表本来就是**按分区键有序**的，而分区键的第一项是 `namespace`，几乎所有 query 都恰恰是按 `namespace` 过滤的。

于是：与其线性扫描 100k 个 parts 找出某个 namespace 对应的子集，不如先用一次 **binary search** 框出该 namespace 的连续区间，再在这个小区间内做剩余的过滤。

结果：

> 原文："After deploying this patch in March 2026, query durations dropped by 50%. More importantly, this finally breaks correlation of query durations with the number of parts."

**查询延迟再降 50%，并且——这一次——part 数和查询时长之间，那条已经困扰了一年的线性相关性，被打断了。**

这一步的更深含义是：当你知道你的容器是**有序的**，并且你的过滤条件命中的是**有序前缀**时，你正在错过的不只是常数优化，而是一整个复杂度等级。`O(N)` 到 `O(log N)` 在 N = 100k 时是 100k → 17 的差距——这就是它砍掉一半延迟、并且让相关性曲线第一次"平掉"的根本原因。

不过原作者诚实地标注了这条路线的局限：

> 原文："This solution doesn't generalize that well for arbitrary query conditions (e.g. conditions such as namespace in (5,10))."

`namespace IN (...)` 这种多选条件、`namespace LIKE ...` 这种模式匹配——都退化回线性扫描。所以他们已经在看下一步：**把 query condition cache 扩展到 part filtering 路径上**，让过滤决策本身可以被复用、可以跨 query 缓存。这是又一篇博客的种子。

### 6. 一份没写在博客里、但藏在 PR 描述里的细节

如果你点开 [PR #85535](https://github.com/ClickHouse/ClickHouse/pull/85535) 的描述，会看到这样一段非常坦诚的话（我用自己的话复述大意）：

作者承认这张表的设计**"可能并没有完全按照 ClickHouse 推荐的指南来"**——也就是说，Cloudflare 这边自己也意识到，10 万级 parts 这种状态本身在 ClickHouse 社区看来就是"用法过于激进"。但他在 PR 里特别论证了：**即使在符合指南的常规表上，这个改动也没有任何负面影响**——所以这是一份"无负面副作用"的全局优化，值得合并。

这是一个非常成熟的 OSS 协作姿态：**先承认自己的 use case 不典型，再证明改动对典型场景无害，最后让维护者放心地接收改动**。在这种规模的开源项目里，能不能让维护者放心，几乎决定了你的补丁会不会被 merge。

azat（ClickHouse 核心维护者）在 review 过程中又开了 [PR #86933](https://github.com/ClickHouse/ClickHouse/pull/86933)，把 `MarkRanges` 容器从 `std::deque` 换成 `devector`，进一步把"复制成本"再压一道——这是一种很典型的"上游维护者顺手做的二阶优化"，跟主 PR 一起拼出了完整的性能改善曲线。这一点也呼应了我之前在[《【好文共赏】Quack：DuckDB 在 2026 年从零设计一个数据库 wire 协议》](/post/good-read-duckdb-quack-protocol/)里讲过的：**OLAP 数据库的性能边界，最终都是在容器选择、内存布局和锁粒度这种"基础设施级别"的细节上被推动的**。

### 7. 一份"和解的不安"：分区键到底选对了吗？

文章的结尾，作者写下了一段非常有节制的反思：

> 原文："We've bought ourselves significant breathing room, but the fundamental question remains: Was this partitioning scheme the right long-term choice? Or will we eventually need to bite the bullet and move to a different architecture?"

翻译过来：我们买回了喘息空间，但根本问题还在——这次的 partition 选择，到底是不是长期正确的？

他们承认，**part 数还在涨**——一年前是 30k，现在是 160k，并且没有任何下降趋势。这套补丁延长了寿命，但没有改变下面那条增长曲线。更糟糕的是，文章透露了另一个未爆弹：**ZooKeeper**。ClickHouse 用 ZooKeeper 跟踪每张表所有 parts 的元数据，160k parts 意味着 ZooKeeper 集群也要存 160k × 多副本量的小条目。作者轻描淡写地说：

> 原文："Perhaps one day we'll tell the story of the 100 gigabyte ZooKeeper cluster."

——"也许哪天我们会写一篇 100 GB ZooKeeper 集群的故事"。

这一句话，是这篇博客里最让我背脊一凉的伏笔。**百 GB 级的 ZooKeeper 集群，几乎注定是另一个时间炸弹**——它的瓶颈不再是 OLAP 引擎，而是分布式协调层。这等于在向读者预告：今天解决的 mutex contention 只是 part 数膨胀这一条链上的**第一块多米诺骨牌**。

这是一种非常诚实的工程师写作姿态：**我修了眼前能修的，但我知道这次修复并没有从根本上解决问题；我让你看到，但我不会假装我已经赢了**。

## 延伸阅读图谱

### 作者其他代表作

James Morrison 在 Cloudflare 是 Senior Distributed Systems Engineer。这是他在博客上的第一篇署名长文，但他在 ClickHouse 主仓库的 PR 记录已经留下了非常清晰的指纹：

1. [**PR #85535 · "Optimize selection of part list during query planning"** (ClickHouse, 2025-11)](https://github.com/ClickHouse/ClickHouse/pull/85535) —— 本文的主战场。shared_lock + deferred copy。
2. [**PR #39385 · "Remove broken optimisation in Direct dictionary dictHas implementation"** (ClickHouse, 2022-07)](https://github.com/ClickHouse/ClickHouse/pull/39385) —— 早期一次对 Direct dictionary 错误优化的撤回，反映同一位作者一贯的"找隐含成本"风格。

他的合作者 Christian Endres 同样是 Cloudflare 系统工程团队的核心成员，专注 ClickHouse 在多租户场景下的稳定性。两人合写文章在 Cloudflare 工程博客里是少见的"事故技术报告型"风格。

### Cloudflare 工程博客同期相关文章

- [**Browser Run: now running on Cloudflare Containers** (2026-05-13)](https://blog.cloudflare.com/browser-run-containers/) —— 把浏览器 sandbox 搬到 Containers 上，与 Workers 解耦。
- [**When "idle" isn't idle: how a Linux kernel optimization became a QUIC bug** (2026-05-12)](https://blog.cloudflare.com/quic-death-spiral-fix/) —— 同期另一篇被广泛传播的根因分析；推荐与本文成对阅读。我已经写过[导读](/post/good-read-cloudflare-quic-cubic-death-spiral/)。
- [**How Cloudflare responded to the "Copy Fail" Linux vulnerability** (2026-05-07)](https://blog.cloudflare.com/copy-fail-linux-vulnerability-mitigation/) —— 一次内核漏洞响应的全公司级行动报告。

### ClickHouse 与 OLAP 性能工程参考

- [**ClickHouse 官方：Sparse Index & MergeTree Engine 设计文档**](https://clickhouse.com/docs/en/engines/table-engines/mergetree-family/mergetree) —— 本文里反复出现的"parts"和"primary key 排序"概念的官方解释。
- [**Altinity：The Part of the MergeTree Family**](https://altinity.com/blog/clickhouse-and-the-curse-of-too-many-parts) —— 一篇业内对"part 数过多综合症"的早期诊断，可与 Cloudflare 这次的经验互文。
- [**ClickHouse Inc. CTO Alexey Milovidov：Query Pipeline Internals**](https://presentations.clickhouse.com/) —— ClickHouse query planner 的内部演讲资料合集。
- [**RCU (Read-Copy-Update) in the Linux Kernel** by Paul E. McKenney](https://www.kernel.org/doc/Documentation/RCU/whatisRCU.txt) —— "把复制从读路径搬到写路径"这一思想的最经典实现。
- [**Andy Pavlo (CMU) 15-721 高级数据库系统课程**](https://15721.courses.cs.cmu.edu/) —— OLAP query planner、partition pruning、并发控制的系统化教学。

### 反方/补充视角

- [**HN 历史讨论：Why Snowflake's design avoids large numbers of small partitions**](https://news.ycombinator.com/) —— Snowflake、BigQuery 等云原生 OLAP 选择把"分区/微分区"管理藏在引擎内部、对用户透明，恰恰是为了避免 Cloudflare 这次遇到的问题在用户层暴露。
- [**"Premature partitioning is the root of much evil"** ——多位 ClickHouse 资深用户在社区里的共识**：在 ClickHouse 里使用 `PARTITION BY` 必须非常克制，最常见的反模式就是"为了 retention 方便而把分区粒度切得太细"。本文恰恰是这种反模式的最戏剧化案例。

### 与本博客既有文章的交叉引用图

- 与[《【好文共赏】Cloudflare 一次 14ms 的 CUBIC 死亡螺旋》](/post/good-read-cloudflare-quic-cubic-death-spiral/) 形成**"Cloudflare 根因分析双联画"**——一篇讲网络协议中的时间债，一篇讲存储引擎中的锁竞争，都展现了 Cloudflare 工程团队"先把生产事故写清楚，再把补丁上游"的方法论。
- 与[《【好文共赏】Redis 的野心代价》](/post/good-read-redis-cost-of-ambition/) 形成**"基础设施复杂度反噬"对照**——一篇讲产品边界扩张如何压垮代码库，一篇讲表设计选择如何压垮规划器。
- 与[《当 AI 不再只看 CPU：火焰图驶入 GPU profiling 时代》](/post/ai-flame-graphs-gpu-profiling-2026/) 形成**"采样模式定义你能看到什么"主题**——AI workload 把这个问题搬到了 GPU 上，但本质和 CPU vs Real trace 完全一致。
- 与[《【好文共赏】Quack：DuckDB 在 2026 年从零设计一个数据库 wire 协议》](/post/good-read-duckdb-quack-protocol/) 形成**"OLAP 引擎细节决定上限"主题**——Quack 关注的是 wire 协议层的零拷贝设计，本文关注的是查询规划器的锁粒度，但它们都在追问同一个问题：百 PB 时代，OLAP 引擎的瓶颈在哪？
- 与[《Figma 把 Redis 装进六个九：一段平台工程从 fork 到 proxy 的路》](/post/figma-redis-proxy-six-nines-platform-engineering-2026/) 形成**"内部基础设施的演化"对照**——Figma 的多代理路线和 Cloudflare 的 Ready-Analytics 都属于"在共享底座上构建多租户平台"，最终都走到了"内部决策必须慢慢向上游开源项目反推"的姿态。

## 编辑延伸思考：part 数膨胀，是不是 ClickHouse 时代的 "vacuum 噩梦"？

我想顺着这篇博客往外多说几句——因为这不只是 Cloudflare 一家的故事。

在 Postgres 时代，所有 DBA 都熟悉一个词：**vacuum 噩梦**。表上 dead tuple 一直在积累，autovacuum 跟不上，膨胀的不是数据，而是元数据；最后某一天 query planner 突然变慢，原因不是数据多了，而是"看起来死掉但没回收的东西"占满了 page cache。Postgres 花了二十年和这种问题搏斗，从 `VACUUM FULL` 到 `VACUUM (FREEZE)` 到 HOT update 到现在的 `pg_repack`/`pg_squeeze`——一整套生态都是围绕这一种隐性膨胀。

ClickHouse 时代，这个角色被 **parts 数膨胀**接替了。

它的形成路径几乎一样：

1. 工程师做出一个看起来"和性能无关"的设计决策（在 Postgres 是 update-heavy workload；在 ClickHouse 是分区键 cardinality）；
2. 系统正常运行**几个月**，没有任何 alert；
3. 直到某一天，一个完全不相关的业务出现 SLA 故障；
4. 排查时所有"标准指标"都正常；
5. 真凶藏在某个 page-level / part-level 的元数据结构里，被全局锁/串行扫描放大；
6. 修复需要**改引擎内部**——而非改业务代码或调表 schema。

这种"隐性膨胀型 bug"有一个共同的工程特征：**它们的代价不是和你的工作负载成正比，而是和你的状态空间成正比**。这就让"压测"变得几乎无能为力——你压一周也压不出来一年的 parts 数。

所以这类问题的真正解决路径，不是更聪明的压测，也不是更敏锐的告警，而是两件事：

1. **状态空间的可观测性**。让"集群整体的 parts 数 / dead tuple 数 / index bloat / 锁等待队列长度"成为一等公民的指标，和 QPS、p99 latency 平起平坐。Cloudflare 这次的转折点就是"画了一张 parts 总数 vs query duration 的图"——这张图早应该是 ClickHouse SRE dashboard 的默认面板。
2. **结构性的弹性，而非渐进式的修补**。8 倍的优化只是给你赢回 18 个月的时间。真正的问题是：**Ready-Analytics 这套"宽表 + namespace + 自由 indexID"的设计，能不能撑到 1 PB 单表？10 PB？文章里没有给出答案，因为答案大概率是"不能"**——但它至少诚实地把这个问号留在了结尾。

从这一点上说，**这篇博客最有价值的不是它的三个补丁，而是它结尾那段"和解的不安"**。它不假装赢了，不假装这套架构 100% 长期正确。这种工程姿态，比"成功修复 8 倍提速"重要得多。

最后想留一个开放问题给所有还在用"宽表 + 多租户 namespace"模式做数据平台的团队：

**当你的"通用宽表"已经支撑了上百个内部应用、上千个数据流，"把多租户拆成 table-per-namespace"这件事，是越早做越痛、还是越晚做越痛？**

Cloudflare 这次选了"晚做+用补丁延寿"。短期看是对的——保住了账单 deadline，顺便给 ClickHouse 社区送了一个 8 倍 PR。但长期答案，要等 ZooKeeper 那张牌翻开之后才知道。

## 配套资料导览

本文附带了以下配套资料文件（均位于本文章目录下）：

- **`cover.svg`**：深色背景封面图，可视化"parts 总数线性增长 vs 查询时长曲线"，以及锁竞争从条形堆叠到 binary search 的演化过程。
- **`mindmap.svg`**：思维导图，把"Ready-Analytics 设计 → 分区键迁移 → 锁竞争 → 三步优化 → ZooKeeper 伏笔"整条链路画成一张图。
- **`concept-cards.md`**：15 张关键概念卡片，从 ClickHouse `MergeTree` 到 `std::shared_lock`、从 `trace_log` 的 CPU/Real 采样到 RCU 思想，可作为面试速查和团队培训材料。
- **`glossary.md`**：英中对照术语表，约 35 条，覆盖 OLAP、并发原语、ClickHouse 特有概念三大类。

## 谁应该读这篇文章

- **OLAP 数据库工程师**：必读。这是一份关于"分区键决策的隐含代价"的完整教学样本。
- **SRE / DBA**：把"集群状态空间的全局指标"加进你的 dashboard。Cloudflare 这次救命的不是 trace_log，而是那张"parts 总数 vs query duration"的散点图。
- **C++ 系统开发者**：`std::unique_lock` → `std::shared_lock` → "把复制搬到写端"这条链，是并发原语应用的活教材。
- **平台工程团队 / 内部数据平台负责人**：Ready-Analytics 的故事，几乎是每一家做"通用宽表 + 多租户" platform 公司的未来。读这篇文章，等于免费拿一份"未来 18 个月可能踩到的坑"清单。
- **开源贡献者**：jawm 这次 PR 的提交方式——先承认 use case 不典型、再论证改动对典型场景无害——是一份非常好的"如何让维护者放心 merge 你的补丁"的样板。
- **写技术博客的工程师**：这是一篇"事故 + 调试 + 补丁 + 反思"的标准结构样本。每一节都有一个非常清晰的"我当时以为 X，但其实是 Y"的转折。比起"我们用了 N 项黑科技"的炫技型博客，它会成为很久之后还被引用的那一类。

---

*【好文共赏】是本博客的深度技术导读栏目，每天精选 1-3 篇全球顶级技术博客与论文做长篇导读。如果你也读到了让你拍案叫绝的好文，欢迎在 GitHub Discussions 推荐。*
