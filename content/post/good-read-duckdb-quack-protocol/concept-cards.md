# Quack 协议导读 · 关键概念卡片

> 12 张卡片，把"读完 Quack 这篇你应该带走什么"压缩成最小可记忆单元。每张 ≤ 150 字。

---

## 🃏 1. Wire Protocol（线缆协议）

**定义**：客户端和数据库服务器之间在网络上传输的字节级编码规范。
**核心要素**：消息结构、序列化格式、握手、认证、错误处理、流控制。
**反例**：JSON-RPC、REST API 严格来说不是 wire protocol——它们更高层。
**Quack 的位置**：HTTP 之上的 request-response 模式，消息体用 `application/duckdb` 二进制序列化。
**记忆锚点**：PostgreSQL 协议（1996）、MySQL 协议、RESP（Redis）、Memcached、Cassandra CQL 都是同一抽象层级。

---

## 🃏 2. 单 Round-Trip（Single RTT）

**定义**：一次"提问—回答"在网络上往返的次数为 1。
**为何重要**：跨地域网络 RTT 通常 50-200ms；每多一次 RTT 就是延迟的线性叠加。
**Arrow Flight SQL 的问题**：每个查询强制 `CommandStatementQuery` + `DoGet` 两次 RTT，对小事务工作负载是结构性劣势。
**Quack 的设计**：握手后单 RTT 就能完成完整 query；大结果集再用 follow-up fetch（可并行）。
**实测对照**：small writes benchmark 里 Arrow Flight 约为 PostgreSQL 一半速度，正是 2-RTT 累积的结果。

---

## 🃏 3. `application/duckdb` —— 自有 MIME Type

**定义**：DuckDB 为 Quack 注册的新内容类型，使用 DuckDB 内部已用于 WAL 的序列化格式。
**为什么不用 Protobuf**：会被外部 schema 演进节奏绑死。
**为什么不用 Arrow**：会被 Arrow 社区的格式委员会绑死。
**优势**：今天加新 SQL 类型，明天就能在 wire 上传输，不必等任何外部协调。
**代价**：客户端只能是 DuckDB 自己（cross-system 互通让位给 ADBC/Flight）。
**设计哲学**：interchange format 和 wire protocol 是两件事，不要混在一起。

---

## 🃏 4. SQL Macro 作为 Auth Hook

**定义**：authn callback（验证 token）和 authz callback（决定是否允许执行某个 query）都可以是一段 SQL macro。
**默认**：authn 比较随机生成的 token；authz 一律放行。
**可替换**：你可以写"去 LDAP 查这个 token 对应的用户能不能访问 schema X"这种 SQL 函数。
**为什么这么设计**：DuckDB 的核心信仰——"已经有 SQL 这个表达力强的语言，不要再发明第二套 DSL"——和 DuckLake 的 SQL catalog、PostgreSQL 的 RLS 是同源思想。
**适用边界**：单数据中心、可信网络；不适用复杂企业级 SSO + 零信任 + 合规审计。

---

## 🃏 5. HTTP as Substrate（HTTP 作底座）

**核心论点**：2026 年新协议不构建在 HTTP 之上是 *misguided*。
**理由**：现代基础设施（L7 LB、WAF、TLS 终结、可观测性、SDK、浏览器、curl、wireshark）默认理解 HTTP；自造 TCP 协议等于自掏腰包重建一整套生态。
**额外好处**：DuckDB-Wasm 在浏览器里能原生说 Quack。
**对比**：PostgreSQL 协议（1996）当年没有这些基础设施，所以裸 TCP 是合理选择；今天再裸 TCP 是浪费工程预算。
**关联思想**：和 gRPC over HTTP/2 是同一时代的演进，但 Quack 走 HTTP/1.1 路线，更保守、更易调试。

---

## 🃏 6. Pets vs Cattle（适用于 DuckDB 实例）

**经典定义**：基础设施中"宠物"是 named、hand-tended、不能丢的资源；"牛"是可替换、interchangeable 的实例。
**在 Quack 里的应用**：
- 之前 DuckDB 实例是宠物：单进程拥有数据库文件，没法多个进程同时写。
- Quack 让 server 实例变得相对更接近宠物（它持有 ground truth），client 实例彻底变成牛（随时来随时走）。
**和 Anthropic Managed Agents 的呼应**：那篇文章用同一套 pets-vs-cattle 拆解了 agent harness 的演进。
**记忆锚点**：基础设施工程的永恒主题——把状态收缩到一小块"宠物"，把其他一切都做成"牛"。

---

## 🃏 7. HTAP 边界模糊化

**定义**：Hybrid Transactional/Analytical Processing，传统上 OLTP（事务）和 OLAP（分析）是两套系统。
**过去十年趋势**：
- 第一波（2010s 中）：NewSQL 想从 OLTP 端打通分析（CockroachDB、TiDB）；
- 第二波：分析专业化（Snowflake、BigQuery）甩 OLTP；
- 第三波：嵌入式分析（DuckDB、ClickHouse 单机版）；
- 第四波（2024-2026）：分析引擎反向吃 OLTP 边界。
**Quack 的位置**：让 DuckDB 单实例能扛 5500 TPS 小写入 + bulk 大查询。
**意义**：observability 栈（指标 + 日志 + trace）可能不再需要 ClickHouse + PostgreSQL 双系统。

---

## 🃏 8. 9494：致敬 Netscape Navigator 1994

**事实**：Quack server 默认监听端口 9494。
**理由**：1994 是 Netscape Navigator 首发的年份，把 HTTP/Web 推向大众的一年。
**为什么有趣**：这种"半实用半致敬"的端口选择是 DuckDB 团队工程师文化的标志。不影响协议正确性，但传达"我们知道我们在做什么、我们尊重协议谱系"的信号。
**类似案例**：Erlang VM 4369、IRC 6667、HTTPS 443（这个不是致敬）。
**编辑视角**：好工程文化经常体现在这种"无谓但贴心"的细节里。

---

## 🃏 9. 拒绝 Arrow Flight SQL：两个理由

**理由 1（设计哲学层）**：Interchange format 的天职是"系统之间减少摩擦"，把它塞进单个系统的内部 wire protocol，等于把演进自由度让给外部委员会。
**理由 2（性能层）**：Arrow Flight SQL 每个查询强制 2 RTT，对 small writes 是结构性劣势。
**反驳预期**：有人会说"Arrow Flight 主要是为 bulk transfer 设计的"——是的，但 Quack 想同时覆盖 bulk 和 small writes 两个 workload。
**广义教训**：选择 wire protocol 时要先讲清楚要覆盖的 workload 切片，不要被"现成的标准"绑架。

---

## 🃏 10. 工作负载甜区 vs 边界

**Quack 的甜区**：
- 单数据中心、可信网络；
- 多 writer 并发，但不超过 ~8 个；
- bulk transfer + small writes 混合；
- observability ingestion、内部 BI、数据 pipeline。
**Quack 明确不做**：
- 跨节点分布式事务；
- 高可用 / 自动故障转移；
- replication（标注为 future work）；
- 内置 TLS（让 nginx/Caddy 终结）。
**编辑感**：边界写得越清楚的协议越值得信任。

---

## 🃏 11. Don't Hold My Data Hostage（论文）

**全称**：Raasveldt & Mühleisen, "Don't Hold My Data Hostage—A Case For Client Protocol Redesign", VLDB 2017。
**核心结论**：传统数据库协议（PostgreSQL、MySQL、MS SQL Server）在大数据集传输上有数量级的 overhead，因为它们一行一行地做 type encoding。
**对 Quack 的影响**：作者是 DuckDB 的两位创始人；Quack 的列式 bulk 友好设计直接源于这篇论文的研究发现。
**配套阅读必要性**：读这篇能让你理解为什么 Quack 不仅快、而且"必然要这么设计"。
**学术与工程的闭环**：少见的"我先发论文证明这是问题、十年后我自己造产品来解决"的清晰链条。

---

## 🃏 12. 协议设计的"减法美学"

**Quack 文章的核心修辞结构**：每个设计决定都先说"我们不做 X"，再说"因为我们要做的是 Y"。
- 不做 TLS in protocol（让 nginx 做）
- 不做 cross-system 客户端（让 ADBC 做）
- 不做复杂 RBAC（让 SQL macro 做）
- 不做跨节点事务（让用户自己分片）
- 不做 Arrow 兼容（保留演进自由度）
**编辑总结**：好协议的设计语言是"减法"语言。每一个"不做"都精确划定了职责，把复杂留在已经擅长解决它的地方。
**对照警示**：野心无限扩张的协议（Redis 协议的演进就是反面教材）最后哪里都做不好。
