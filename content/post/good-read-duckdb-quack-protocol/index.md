---
title: "【好文共赏】Quack：DuckDB 在 2026 年从零设计一个数据库 wire 协议，把 PostgreSQL 和 Arrow Flight 都拉出来当背景板"
description: "DuckDB 团队用一篇 20 分钟读的文章，把'什么是好的现代数据库客户端协议'的答案写在了纸上：HTTP 为底座、单 round-trip 为信仰、自有 application/duckdb 序列化为前线、auth/authz 全部可换为 SQL macro。然后用 60M 行不到 5 秒、5500 TPS 小写入的 benchmark 把 PostgreSQL 协议和 Arrow Flight SQL 一起压在身下。"
date: 2026-05-14
slug: "good-read-duckdb-quack-protocol"
image: "cover.svg"
categories:
    - 好文共赏
tags:
    - 好文推荐
    - 深度研究
    - DuckDB
    - 数据库
    - 协议设计
    - 系统设计
draft: false
---

> 📌 **好文共赏 · Editor's Pick**
> 原文：[Quack: The DuckDB Client-Server Protocol](https://duckdb.org/2026/05/12/quack-remote-protocol)
> 作者：The DuckDB team｜发布：2026-05-12｜阅读时长：约 20 分钟
> 多模评分：Opus 9.2 / Sonnet 8.8 / Gemini 8.9（综合 **9.0/10**）
> 一句话推荐：**这是 2026 年最像"工程师写给工程师"的协议设计公开课——它不只是宣布一个产品，它把"在今天，一份合格的数据库 wire 协议应该长什么样"完整地拆开摊给你看。**

## 一、为什么这篇值得读

DuckDB 团队在 2026 年 5 月 12 日丢出一个看上去违反自家信条的东西：一个客户端-服务器协议，名字叫 **Quack**。

注意，违反信条这个判断是表面上的。DuckDB 过去七年最重要的差异化定位，就是"我不是 client-server，我是 in-process"——它故意把自己摆在 SQLite 那一边，跟 PostgreSQL、MySQL、ClickHouse 形成对位。所有关于"为什么我们这么快、为什么我们这么小、为什么 zero-copy 这么自然"的答案，最终都能追溯回这个架构选择。

那么 2026 年这个团队回头自己造一个 wire protocol，意义在哪里？

第一，它**没有**回到经典的 client-server 范式。Quack 是一个让两个 DuckDB 实例可以互相说话的协议，**两个实例都既是客户端、也是服务器**——这其实是 in-process 模型的横向延伸，不是纵向放弃。

第二，整个团队把这次设计当作一次**奢侈的练手机会**：在 2026 年从零设计一个数据库 wire 协议，不必背任何兼容包袱，可以同时参考 PostgreSQL（1996 写的协议）、Arrow Flight SQL（2022）、MotherDuck 内部协议、自家 GizmoSQL 的经验。这是十几年才出现一次的"白纸"机会，而他们没有浪费它。

第三，作为同行评审，文章本身是一份**罕见的诚实文档**：他们直接写下"我们为什么不用 Arrow Flight SQL"，公开点名 Arrow Flight 在每次查询都强制两次 round-trip 的设计缺陷；同时把和 PostgreSQL、Arrow Flight 的 benchmark 摆出来——既 honestly 承认在小事务上 PostgreSQL 横向扩展性更好（DuckDB 自己 8 线程后就被卡住），又骄傲地展示 60M 行 < 5 秒的 bulk transfer 优势。

这种"我设计了这个、我量过了、我也告诉你我哪里不行"的文档质感，在 2026 这个 LLM 生成 PR 稿满天飞的年份里，非常稀缺。

它的姐妹篇是我之前介绍过的 [Redis 的野心代价](/post/good-read-redis-cost-of-ambition/) 和 [Cloudflare 的 QUIC 死亡螺旋](/post/good-read-cloudflare-quic-cubic-death-spiral/)——三篇放一起，构成了 2026 年 5 月最完整的一组"系统软件深度文"：一篇讲产品边界失控的代价，一篇讲十年前的协议假设如何在今天变成 bug，一篇讲在白纸上重新设计协议是什么感觉。

## 二、Quack 是什么：一个十分钟搭起来的 multi-writer DuckDB

先从用户视角说一遍 Quack 长什么样，这样下面的协议讨论才有锚点。

启动一个 DuckDB 实例（就叫它 DuckDB #1），装上 quack 扩展，调用 `quack_serve` 开一个服务：它会在本机生成一个随机 token、绑到 localhost、监听 9494 端口（这个端口号是致敬 Netscape Navigator 1994 年发布的年份——一个非常 DuckDB 风格的、近乎调皮的工程师文化细节）。

然后在另一台机器上（DuckDB #2）装好同样的扩展、注册一个 `quack:localhost` secret 把 token 写进去、`ATTACH 'quack:localhost' AS remote;`——就完成了。`FROM remote.hello;` 这种 SQL 直接像本地表一样查远端实例。`CREATE TABLE remote.foo AS ...` 直接像本地表一样写远端实例。也支持 `remote.query('SELECT ...')` 这种把整段 SQL 推到对端执行的"push down everything"模式。

这种 UX 上面，最值得注意的是两件事：

**第一，它取消了"server 软件"和"client 软件"的区分。**任何一个 DuckDB 实例都可以同时既是 Quack server 又是 Quack client。这意味着你不需要部署一个独立的 daemon 进程、也不需要一个独立的客户端 SDK——DuckDB-Wasm 在浏览器里跑的时候，可以直接 attach 到 EC2 上跑的另一个 DuckDB 实例。

**第二，它默认是 secure-by-default 的，但不是 SSL-by-default。**这点在协议设计哲学上有意思：默认绑 localhost、默认生成随机 token，给一个"快上手"的体验；但同时明文写"我们不推荐你把 Quack 直接暴露给公网，请用 nginx 终结 SSL 再 proxy 过来"。也就是说团队主动选择**不把 SSL 烤进协议**——这跟 HTTP/2 强制 TLS 是相反的选择，理由是"在 localhost 之间为 SSL 拉一堆依赖太傻"。

这条选择能不能站得住，要看运行时安全的演进；但它体现了一个非常清晰的设计原则：**协议层只解决协议层必须解决的问题，安全治理交给现有 HTTP 生态**。这跟下面要讲的 HTTP-as-substrate 思路是一脉相承的。

## 三、第一个核心决定：HTTP 是 2026 年所有新协议的合理底座

文章里有一句几乎是宣言式的：

> 原文："It would be rather misguided not to build a database protocol on top of HTTP in 2026."

我把这句拎出来单独说，因为它代表了一个真正现代的、和 1996 年 PostgreSQL 那套基于 TCP 的二进制 wire protocol 截然不同的判断。

PostgreSQL 协议、MySQL 协议、Redis RESP、Memcached 协议——都是直接坐在 TCP 上的，自定义 message framing、自定义连接管理、自定义 keep-alive。这些协议在 90s/00s 是合理的，因为那时 HTTP 还没有压倒性的工具链优势。但是到了 2026 年：

- L7 load balancer、API gateway、service mesh，**全部**默认理解 HTTP；
- TLS 终结、证书轮转、ACME/Let's Encrypt 自动化，**全部**默认理解 HTTP；
- WAF、IDS、rate limiting、流量重放、可观测性，**全部**默认理解 HTTP；
- 浏览器 fetch、移动端 SDK、curl、wireshark plugin，**全部**默认理解 HTTP。

如果你的协议不是 HTTP，你就是在自掏腰包重建这一整套基础设施，并且**永远落后**。Quack 团队的判断是：在 2026 年还为数据库自造 TCP 协议，等于在 2010 年还为内部服务自造 RPC——技术上可以，工程上不必要。

而且 HTTP 这套基底带来一个具体的、可量化的好处：**DuckDB-Wasm 直接能在浏览器里说 Quack**。浏览器原生 HTTP/WebSocket 栈，加上同源安全模型已经为你做完了。如果你试图把 PostgreSQL 协议塞进浏览器，你需要一个 proxy 把 binary frame 转成 WebSocket——这就是 Supabase 这类公司过去七年实际做的事情。

但 Quack 没有走 HTTP/2 的多路复用 + binary frames 这条更新的路线。它选了"在 HTTP 之上构建 request-response 模式 + 可能多线程并行 fetch"的相对保守路径。这是个让人值得思考的取舍：**用 HTTP/1.1 心智模型设计协议消息，把"复杂"留给 HTTP 栈自己解决**。

（这种"系统设计要选择把复杂留在哪里"的味道，跟我之前写过的 [n8n 架构深度拆解](/post/n8n-architecture-deep-dive/) 里关于 webhook + queue 边界的讨论，是一回事——好的系统不是没有复杂度，是把复杂度推到正确的边界。）

## 四、第二个核心决定：拒绝 Arrow Flight SQL，因为它强制两次 round-trip

文章最有"撕"的味道的一段，是附录 "Why Not Arrow Flight SQL?"。

Arrow Flight SQL 是 Apache Arrow 项目在 2022 年发布的现代数据库 wire 协议，定位就是"列存友好、bulk-transfer 友好、可以让任何用 Arrow 的系统直接互通"。理论上 DuckDB 应该顺势用它——毕竟 DuckDB 本身就是列存引擎、本身就跟 Arrow 生态深度交互。

但 Quack 团队的判断是 **No**，理由有两层。

**理由一是设计哲学层：**Arrow 这种 interchange format 的核心价值是"跨系统时减少摩擦"，但是放到一个系统的内部 wire protocol 里就有问题——它会"reach in"到你的内部数据布局。DuckDB 内部的中间结果在某些方面接近 Arrow，但在另一些方面并不接近；如果用 Arrow 做内部 wire format，未来想加一个新的数据类型或新的协议消息，就必须先去推动外部委员会修标准——DuckDB 把这个状态描述为"被你不能完全控制的格式所限制"。

我把这一段读了两遍，因为它点出了一个被严重低估的工程教训：**interchange 格式和 wire 协议是两回事**。Arrow（包括 ODBC、JDBC、ADBC）的天职是 reduce friction between systems，做"边界翻译官"。但如果把翻译官硬塞进**单个系统**的内部协议，你就把自己绑死在外部标准的演进节奏上了——而那个节奏几乎注定比你慢。

**理由二是性能层：**

> 原文："Deep down, there is also one fateful design decision in Arrow Flight SQL: every single query requires at least two protocol round trips, CommandStatementQuery and DoGet."

这是一个具体的、可量化的、致命的设计缺陷。在高延迟环境（跨数据中心、跨大洲、移动网络）里，每次查询多一个 RTT，就是给所有小事务工作负载戴上脚镣。Arrow Flight 当初这么设计是因为它假定主要场景是"返回大数据集"，多一个 RTT 在 GB 级别传输里可以忽略——但 DuckDB 想做的是同时覆盖 bulk 和 small writes，这个二次 RTT 就成了红线。

Quack 的对位回答：**单 RTT 完成一次查询**。客户端发一个请求，服务器返回结果第一部分（或者全部）。后续如果结果太大，再发 fetch 拉剩下的；但是简单查询永远是 1 RTT。这一条决定直接对应了文章后面 small writes benchmark 里 Arrow Flight 大约**只有 PostgreSQL 一半速度**的结果。

这种"先讲清楚要解决的工作负载、再倒推协议设计"的思路，是看一个团队工程成熟度的可靠指标。它和我们经常看到的"先选了一个 fancy 技术、然后倒过来找适用场景"是反过来的。

## 五、第三个核心决定：用 SQL macro 当 authn/authz hook

整篇文章最 DuckDB 风的细节，藏在 Authentication and Authorization 一节。

经典数据库协议怎么处理 auth？基本都是"内置一套用户/角色/权限模型，把它写死在协议里"，然后留几个钩子（比如 PostgreSQL 的 pluggable auth via PAM）。结果就是每个数据库都有自己的 GRANT/REVOKE 语法、自己的 LDAP integration 配置文件、自己的 row-level security 实现——这些东西常年是 DBA 的痛苦来源。

Quack 团队的判断是：**这是个 90 分难题，不要假装自己能 100 分一次性解决，做一个"可扩展的 60 分"反而是好工程。**

具体做法：

- 协议层只规定**有一个 authn callback**——服务器拿到客户端的 token 字符串，调用一个 callback 返回 yes/no；
- 协议层只规定**有一个 authz callback**——服务器拿到一个待执行的 query，调用一个 callback 返回 yes/no；
- **这两个 callback 都可以是 SQL macro**——也就是说，你的访问控制策略可以是一段 SQL。

最后这条是把"插件化"做到了极致：你不需要写 C++ 扩展、不需要装 Lua、不需要拉 Sidecar，你只要写一段 SQL 函数，对 token 做查表、对 query 做 AST 检查。结合 DuckDB 已经能直接 attach 远端 PostgreSQL、attach S3、attach HTTP——你完全可以写"去 LDAP 查这个用户能不能访问"或者"查一个 HTTP endpoint 拿权限策略"这种 callback。

我反复想这件事的味道。它和 Cloudflare Workers 把 fetch 当作万能入口、和 PostgreSQL 的 row-level security 都不一样：Quack 把**鉴权策略本身当作 SQL 一等公民**。这跟 [DuckLake 把表元数据存回 SQL catalog](/post/ducklake-sql-catalog-lakehouse-paradigm-2026/) 是同一个深层信仰——**当你已经有了一个表达力很强的查询语言时，所有元层面的事情都可以用它来描述，而不需要发明第二套 DSL**。

这条信仰是不是对所有场景都成立？大概率不是。企业级 SSO、零信任网络、合规审计，这些场景对鉴权的要求远超 "一段 SQL macro 能做的事"。但对于 Quack 想覆盖的核心场景——**单数据中心内、可信网络内、需要多写者的数据管道**——这个抽象的简洁性是巨大的优势。

## 六、第四个核心决定：自己的 application/duckdb 序列化，不用 Protobuf 不用 JSON

Quack 的请求和响应都用一个新的 MIME type：`application/duckdb`。

这是把"我们要保留演进自由度"贯彻到了底层数据格式。团队解释说：

> 原文："This encoding leverages DuckDB's internal efficient serialization primitives for complex structures like data types and result sets. We have been using the same primitives for example in our Write-Ahead Log (WAL) files for years, meaning they are fairly well-optimized and battle-tested."

这里的工程逻辑是双层的：

第一层是**复用**。WAL 已经在线上跑了多年，它需要序列化的就是同样这些结构：数据类型、列、行、元数据。Quack 序列化拿来直接用，少写一套代码、少养一套 bug。

第二层是**自治**。如果用 Protobuf、Flatbuffers、Avro、Arrow IPC 任何外部格式，每加一个新数据类型（DuckDB 是出了名地在大胆扩展 SQL 类型，比如 LIST、STRUCT、MAP、enum、union）都得先去外部 schema 里加，发版要等。自己的格式可以**今天加一个新类型，明天就发版**。

这条权衡在小团队、快迭代的项目里几乎总是赢的——但代价是别人没法不依赖 DuckDB 客户端库来跟你说话。Quack 协议的客户端**就只有 DuckDB 自己**——这是一个有意识的选择。它跟 PostgreSQL 协议被 100+ 客户端实现是反方向的：Quack 不打算成为 *cross-system* 的事实标准，它打算成为 *DuckDB 系统内部* 的最优解。

这个选择对生态意味着什么？短期：Quack 只在 DuckDB 之间互通，外部系统想接入还是建议走 ADBC/Arrow Flight。长期：如果 DuckDB 自己变成生态——比如 MotherDuck、Hex、Mode、各种本地 BI 都用 DuckDB 引擎——那 Quack 就自然成为这个生态内部的高速通道。

## 七、Benchmark：60M 行 < 5 秒、5500 TPS，但也老实承认在 8+ 线程时被自家 contention 拦下

Benchmark 一节是这篇文章的"诚实度试金石"。

**Bulk transfer**：在 AWS m8g.2xlarge（8 vCPU、32GB RAM、up to 15Gbps）同 AZ 两机之间，传 TPC-H lineitem 表。

- 60M 行（CSV 76GB），Quack < 5 秒；
- PostgreSQL 行式协议在这个规模上"基本绝望"；
- Arrow Flight SQL（通过 GizmoSQL）追不上 Quack。

这一节有趣的不是数字本身——其实大家都知道列存协议会赢行存协议——而是 Quack 把 Arrow Flight 也打掉了。原因主要是上面说的 application/duckdb 直接用 WAL 序列化的"零翻译"，加上 single-RTT 设计减少了协议层 overhead。

**Small writes**：每行单独 INSERT 事务，5 秒内统计 TPS，1/2/4/8/16/... 并行线程。

- 8 线程内 Quack 比 PostgreSQL 还快，峰值约 5500 TPS；
- **但是**超过 8 线程后被 DuckDB 自己的并发 INSERT 锁住，曲线变平；
- PostgreSQL 在这区间继续 scale up；
- Arrow Flight 大约只有 PostgreSQL 一半（验证了 two-RTT 的设计缺陷）。

这就是文章诚实的地方：他们直接写"PostgreSQL scales better here, which is something to look into for us in the near future"——明确说**我们的瓶颈在 DuckDB 自己的并发写入实现，不在 Quack 协议**，并把这件事公开列为下一步工作。

这种 benchmark culture 跟之前那种"我们比 X 快 N 倍"的市场稿对比鲜明。它给读者的不是"用我们的产品"的暗示，而是"这是协议设计权衡的真实截面图"——读者能自己判断哪个权衡对自己的工作负载更重要。

（顺便：如果你做过任何 TPC-H 相关的工作就知道，76GB CSV 跑成 < 5 秒这个数字本身需要 quite a lot 的工程支撑——它意味着压缩、并行 fetch、network bandwidth saturation 都已经被打磨过。这种数字不可能是 marketing dump，是真的硬件 saturate 数据。）

## 八、为什么这件事重要：HTAP 边界的又一次模糊化

把 Quack 放在最近三年的数据库格局里看，它代表的是 **OLAP 引擎主动伸手抓 OLTP 工作负载**的又一个例子。

过去十年的故事大概是这样：

1. 第一波（2010s 中期）："NewSQL"和"HTAP"概念出现——Spanner、CockroachDB、TiDB——OLTP 数据库想做分析。
2. 第二波（2010s 后期）：Snowflake、BigQuery、Databricks——分析数据库专业化，把 OLTP 完全甩给应用层处理。
3. 第三波（2020s 初期）：DuckDB、ClickHouse、Pinot 等单机/小集群分析引擎崛起，"嵌入式分析"被验证。
4. 第四波（2024-2026）：分析引擎开始**反过来吞 OLTP 边界**——ClickHouse 拼命做 lightweight updates、DuckDB 通过 Quack 让自己变成 multi-writer、Snowflake 通过 Unistore 加 row store。

Quack 的具体意义是：DuckDB 现在可以**单实例承担 observability ingestion 这种典型的"很多小写入 + 偶尔大查询"工作负载**。5500 TPS 不算高，但足以覆盖中小规模的指标、日志、trace 入库。再加上 DuckDB 的列存查询能力，你**可能不再需要 ClickHouse + PostgreSQL 这种双系统配置**。

这条路径其实跟我之前写的 [DuckLake](/post/ducklake-sql-catalog-lakehouse-paradigm-2026/) 是同一战略：DuckLake 把"远程元数据存储"问题解决了，Quack 把"多 writer 实时入库"问题解决了——两件事合起来，DuckDB 就具备了挑战传统数据栈的完整 footprint。

但要注意边界：Quack 没有解决**复制（replication）**——所有写都还是要打到那一个有 server 角色的 DuckDB 实例上；Quack 没有解决**高可用**——那个实例挂了你就挂了；Quack 没有解决**事务跨节点**——单实例事务还是单实例事务。文章最后明确写了"我们在考虑加 replication protocol 让 read replica 成为可能"。

所以 Quack 现在的形态，是**功能上把 Postgres-lite 的能力补给了 DuckDB，运维上仍然是 SQLite-style 的简单**。它有意识地停在"单实例 + 多 writer"这个甜区，不试图变成下一个 CockroachDB。这种**克制**比"无限扩张"更值得欣赏——也跟我刚写过的 [Redis 的野心代价](/post/good-read-redis-cost-of-ambition/) 形成强烈对照：Redis 是反面教材（任何边界都不要紧，全部都要做），Quack 是正面教材（边界写得清清楚楚，知道自己不做什么）。

## 九、延伸阅读图谱

### DuckDB 团队的代表作（按重要性）

1. **["Don't Hold My Data Hostage"](https://duckdb.org/library/dont-hold-my-data-hostage/)（2017，Mark Raasveldt & Hannes Mühleisen）** —— 这是 Quack 文章里反复引用的研究论文，第一次系统性地测量并展示 PostgreSQL/MySQL/MS SQL 等传统协议在大数据集传输上的灾难性 overhead。Quack 的设计选择有一半根源在这篇论文里。**强烈推荐与正文配套阅读**。

2. **[DuckLake 1.0 announcement](https://ducklake.select/)** —— 用普通 SQL 数据库存表元数据，挑战 Iceberg/Delta 的分层架构；DuckLake + Quack 是 DuckDB 走向"分布式数据栈"的两个支柱。

3. **[DuckDB Wasm](https://duckdb.org/2021/10/29/duckdb-wasm.html)** —— 浏览器内跑完整 DuckDB；Quack 的 HTTP 选型让 Wasm 客户端能直连远端 DuckDB，闭环这个故事。

4. **["The Whole DuckDB Documentation"](https://duckdb.org/docs/)** —— 不是一篇文章，但 DuckDB 的文档风格本身就值得当模板学习：极其简洁、几乎没有 marketing 噪声、每页都告诉你"做不到什么"。

5. **[Hannes Mühleisen 的 CIDR 演讲合集](https://duckdb.org/why_duckdb)** —— 创始人之一在数据库学术圈最重要的几个演讲；理解 DuckDB 哲学的来源。

### 现代数据库协议设计相关

- **[Arrow Flight SQL](https://arrow.apache.org/docs/format/FlightSql.html)** —— Quack 主动选择不用的对照组；读完 Quack 一定要读这篇，才能完整理解附录的"Why Not Arrow Flight SQL"那一段批评的力度。
- **[GizmoSQL: Adding Flight SQL to DuckDB](https://github.com/gizmodata/gizmosql-public)** —— DuckDB 上的 Arrow Flight 实现；benchmark 里被 Quack 比较的就是它。
- **[ADBC vs ODBC vs JDBC](https://arrow.apache.org/blog/2023/01/05/introducing-arrow-adbc/)** —— 理解 interchange API 层级的好入门。
- **["A Glimpse of the New PostgreSQL V4 Protocol"](https://www.crunchydata.com/blog/postgres-protocol)** —— PostgreSQL 团队自己也在重新审视他们的 wire 协议，对照参考。
- **[FoundationDB Record Layer paper (VLDB 2019)](https://www.foundationdb.org/files/record-layer-paper.pdf)** —— 关于"如何在键值底座上做协议级别的高级抽象"的经典工程文献。

### 反方观点 / 不同视角

- **HN 评论区主线讨论**（374 分、78 评论）有意思的几条：
  - "DuckDB 现在变成 moving target，我不太知道它想成为什么了" —— 关于产品边界的担忧。
  - "如果 SQLite 加 client/server 也会被同样地质疑" —— 反驳者的视角。
  - "wishing something like this existed last week" —— 用户视角：sensor reading ingestion + duckdb -ui 同时跑不冲突，这是真实痛点。
- **["Just Use Postgres for Everything"](https://www.amazingcto.com/postgres-for-everything/)** —— 反方代表：你为什么需要 Quack，Postgres 已经有了一切。
- **[ClickHouse 的不同路线](https://clickhouse.com/blog/clickhouse-2024-2025-review)** —— 同样是 OLAP 引擎反向吃 OLTP，ClickHouse 走的是 keeper-based replication + lightweight updates 的路径，跟 DuckDB Quack 的"单实例 multi-writer"是截然不同的设计哲学。

## 十、编辑延伸思考：好协议是讲究"不做什么"的协议

读完 Quack 这篇，我反复在想一个问题：**在 2026 年，到底什么算"好协议设计"？**

我自己尝试总结成几条，全都被 Quack 命中了：

**第一条，协议要选一个明确的工作负载切片，不要试图全栈通杀。** Quack 明确说"我服务 bulk transfer + small writes 的甜区"，不试图替代 Postgres 在 OLTP 集群里的角色，不试图替代 Snowflake 在 PB 级仓库里的角色。所有设计权衡都围绕这个甜区做。反例就是 RPC 框架界曾经那一波"我们要做下一代统一协议"的尝试——99% 死了，因为没人能同时优化高吞吐和低延迟。

**第二条，协议要把"安全"和"治理"留给上游基础设施，不要在协议层重新发明。** Quack 明确不烤 TLS，让 nginx 终结；明确不烤复杂的 RBAC，让 SQL macro 自己写。这跟 1996 年 PostgreSQL 协议要自己管 SSL handshake、自己管 SCRAM auth 形成尖锐对比——不是 PostgreSQL 错了，是它的时代没有现成的 L7 基础设施。今天 (2026) 有了，再自己重做就是浪费。

**第三条，协议要保留演进自由度，不要被外部 schema 绑死。** application/duckdb 这个选择能让团队在加新数据类型时不必先走标准委员会。这跟 PostgreSQL 协议被钉死在 1996 年的 message format 是反向选择。

**第四条，协议要 measure 自己 vs 既有方案，并诚实公开 benchmark 边界。** Quack 文章给了完整的 bulk 和 small writes benchmark，公开 PostgreSQL 在 8 线程后赢自己，公开"这是 DuckDB 内核 contention，不是协议本身"。这种 honesty 直接决定了文档的可信度。

**第五条，协议要复用现有工程资产，不要重新造轮子。** 用 HTTP 而不是裸 TCP，用 WAL 序列化原语而不是新 Protobuf schema——这是把"我们已经有什么"和"我们要构建什么"做了正确的边界划分。

这五条放在一起，其实是同一个元原则的不同侧面：**好协议的设计语言是"减法"语言，不是"加法"语言**。

而 Quack 之所以让人读完心情舒畅，是因为它整篇文档都在做减法。每段都在解释"我们为什么不做某事"——不做 TLS、不做 cross-system 客户端、不做 cross-node 事务、不做 fancy auth、不做 Arrow 兼容。它把每一个"不做"的选择都讲得让人服气。

对照之下，过去几年我读过的不少 wire 协议白皮书都是相反的——拼命堆 feature、拼命讲"我们也支持 X、我们也支持 Y"，结果协议大、客户端实现复杂、benchmark 难调、维护成本高、用户搞不清你的定位。

所以读完 Quack，我对它能不能成功的最终判断是：**它不需要成为 Apache Flight SQL 那种"全宇宙都用我"的事实标准——它只需要让 DuckDB 在自己定义的甜区里更强，它就赢了**。而这种"我服务好我的用户就够了"的克制，恰恰是 2026 年这个被 LLM-driven 噪声充斥的开发者世界里最稀缺的品质。

跟 [Redis 的野心代价](/post/good-read-redis-cost-of-ambition/) 里那种"什么都想做、什么都做坏"的轨迹放在一起读，对照感会非常强烈。Charles Leifer 写 Redis 那篇是回望一个产品在野心里溺水的过程；DuckDB 这篇是展示一个团队克制地往池子里再加一块明确尺寸的踏板。**节制是工程师的核心美德，而 2026 年的好协议设计，本质上就是节制的物化。**

## 十一、配套资料导览

本文配套了四份独立资料，都放在文章同一目录下：

- **[cover.svg](cover.svg)** —— 封面图，深色背景 + 协议主题视觉
- **[mindmap.svg](mindmap.svg)** —— 思维导图，把 Quack 协议设计的五大核心决定 + benchmark 结果可视化成一棵树
- **[concept-cards.md](concept-cards.md)** —— 12 张关键概念卡片，涵盖 wire 协议、单 RTT、application/duckdb、SQL macro auth、pets vs cattle、HTAP 边界等
- **[glossary.md](glossary.md)** —— 30+ 条英中对照术语表，涵盖协议设计、序列化、并发控制、auth 相关词汇

## 十二、谁应该读

**强烈推荐**：
- 数据库工程师、平台工程师，特别是负责"数据入库 + 分析"双工作负载的同学
- 任何在设计或维护内部 RPC / wire 协议的人——这是一份现成的、可以照着抄的"现代协议设计 checklist"
- DuckDB 用户、考虑 DuckDB 的人——这次发布把 DuckDB 的能力面又推前一大步
- 系统软件作者——文档本身的写法值得做范本

**值得一读**：
- DBA、SRE，需要理解新一代"嵌入式 + 协议化"数据库的运维 footprint
- 数据架构师，思考"OLAP 引擎吞 OLTP 边界"对自己 stack 设计的影响

**可以略过**：
- 完全不接触数据库的前端开发者（除非你对协议设计本身感兴趣）
- 只关心商业 DBaaS 的纯使用者

---

> *本文是【好文共赏】系列的导读+延伸，目标是把一篇好文从"读完"变成"读透+能用上"。如果你读完原文有不同看法，欢迎留言——我会把高质量讨论沉淀进延伸阅读图谱。*
