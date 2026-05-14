# Quack 协议导读 · 英中对照术语表

> 35 条术语，覆盖协议设计、序列化、并发控制、auth、benchmark 相关词汇。每条给出中文译名、英文原词、一句话上下文化解释。

## A. 协议层基础

| English | 中文 | 一句话解释 |
|---|---|---|
| **Wire Protocol** | 线缆协议 / 通讯协议 | 客户端与服务器之间的字节级编码与消息规范，例如 PostgreSQL 协议、Quack |
| **Round-Trip Time (RTT)** | 往返时间 | 一个请求从发出到收到响应的网络耗时，跨地域常 50-200ms |
| **Single-RTT Query** | 单次往返查询 | 整个 query 在一个 RTT 内完成；Quack 的核心优化目标 |
| **Two-RTT Round-Trip** | 双次往返 | Arrow Flight SQL 设计上每次查询必须 `CommandStatementQuery` + `DoGet` 两次 |
| **Request-Response Pattern** | 请求-响应模式 | 客户端主动发起、服务器被动应答；Quack 采用这种模式 |
| **Push Down** | 下推 | 把 SQL 查询发给远端执行（`remote.query('SELECT ...')`），而非把数据拉回来本地算 |
| **Connection Handshake** | 连接握手 | 建立连接时交换认证 token、协议版本等的步骤 |
| **HTTP Substrate** | HTTP 底座 | 把 HTTP 当作协议的运输层；Quack "在 2026 年不用 HTTP 是 misguided" |

## B. 序列化与数据格式

| English | 中文 | 一句话解释 |
|---|---|---|
| **MIME Type** | MIME 类型 | HTTP 用来标识消息体格式的字符串，Quack 用新建的 `application/duckdb` |
| **Interchange Format** | 互换格式 | 为跨系统交换数据设计的格式，例如 Apache Arrow、Protobuf |
| **Wire Format vs Interchange Format** | 线缆格式 vs 互换格式 | 关键区别：wire 是协议传输用，interchange 是跨系统翻译用；混在一起是常见错误 |
| **Write-Ahead Log (WAL)** | 预写日志 | 数据库保证持久性的常见结构；DuckDB 把 WAL 的序列化原语复用到 Quack 上 |
| **Columnar Encoding** | 列式编码 | 数据按列而非按行编码，对分析查询和 bulk transfer 友好 |
| **Row-Based Protocol** | 行式协议 | 例如 PostgreSQL 协议，一次输出一整行，导致大数据集传输 overhead 高 |
| **Zero-Copy Serialization** | 零拷贝序列化 | 序列化时不需要额外复制数据；Arrow IPC 是经典案例，Quack 部分借鉴 |

## C. 认证与授权

| English | 中文 | 一句话解释 |
|---|---|---|
| **Authentication (authn)** | 身份认证 | 验证"你是谁"；Quack 用 token + 可换 callback |
| **Authorization (authz)** | 访问授权 | 决定"你能做什么"；Quack 让 callback 检查 query AST |
| **Pluggable Auth** | 可插拔认证 | 协议层只定义 callback 接口、不绑死实现；PostgreSQL 的 PAM、Quack 的 SQL macro 都属此类 |
| **SQL Macro** | SQL 宏函数 | 用 SQL 写的可复用函数；Quack 让 auth callback 本身就是一段 SQL macro |
| **Secret Store** | 凭据存储 | DuckDB 用 `CREATE SECRET` 管理 token；Quack 复用这套机制 |
| **TLS Termination** | TLS 终结 | 在反向代理（nginx/Caddy）处解密 HTTPS，再以明文 HTTP 转发到后端；Quack 推荐这种部署 |

## D. 并发与事务

| English | 中文 | 一句话解释 |
|---|---|---|
| **Multiple Concurrent Writers** | 多并发写入者 | 多个进程同时写同一数据库；Quack 解锁这种能力 |
| **Lock Contention** | 锁竞争 | 多线程争抢同一锁导致性能下降；Quack benchmark 里 > 8 线程被 DuckDB 内部 INSERT 锁拦住 |
| **Transaction Per Second (TPS)** | 每秒事务数 | 衡量 OLTP 工作负载性能的常用指标；Quack 单机 5500 TPS |
| **Replication** | 复制 | 把数据从一个节点同步到另一个节点；Quack 当前未做，标注为 future work |
| **Read Replica** | 只读副本 | 用于扩展读性能的复制实例；Quack 团队提到未来会加 |

## E. 数据库架构

| English | 中文 | 一句话解释 |
|---|---|---|
| **In-Process Database** | 进程内数据库 | 数据库引擎作为库链入应用进程；SQLite、DuckDB 的传统形态 |
| **Client-Server Database** | 客户端-服务器数据库 | 数据库作为独立进程运行，应用通过协议连接；PostgreSQL、MySQL 的形态 |
| **Embedded Analytics** | 嵌入式分析 | 把分析能力嵌入应用程序而不依赖外部数据仓库；DuckDB 是代表 |
| **HTAP** | 混合事务/分析处理 | Hybrid Transactional/Analytical Processing；同时支持 OLTP 和 OLAP 的系统 |
| **DuckLake** | DuckLake | DuckDB 团队的 lakehouse 表格式；把元数据存回 SQL catalog，挑战 Iceberg/Delta |
| **Catalog Server** | 目录服务器 | 存储表元数据的服务；DuckLake + Quack 让 DuckDB 自己当 catalog server 成为可能 |

## F. 工程文化与方法论

| English | 中文 | 一句话解释 |
|---|---|---|
| **Pets vs Cattle** | 宠物 vs 牛 | 基础设施工程隐喻：状态化、需要 hand-tend 的实例 vs 可替换、interchangeable 的实例 |
| **Battle-Tested** | 久经实战 | 在生产环境长期运行验证过的；DuckDB 的 WAL 序列化是 battle-tested 的 |
| **Sweet Spot** | 甜区 | 一个设计最擅长的工作负载切片；Quack 的甜区是单数据中心、多 writer、混合负载 |
| **First-Class Citizen** | 一等公民 | 在语言/系统里有完整支持的概念；Quack 把 SQL macro 当成 auth 的一等公民 |
| **Don't Hold My Data Hostage** | 别把我的数据扣作人质 | Raasveldt & Mühleisen 2017 论文，论证传统协议在 bulk transfer 上的灾难性 overhead；Quack 设计的理论基础 |

## G. Quack 特有词

| English | 中文 | 一句话解释 |
|---|---|---|
| **Quack** | Quack（"嘎嘎") | DuckDB 团队为新协议取的名字；duck 之间互相说话当然叫 quack |
| **EleDucken** | 鸡鸭鹅嵌套 | 文章里的工程梗：DuckDB-in-PostgreSQL-via-pg_duckdb，戏仿美国 Thanksgiving 的 "Turducken"（火鸡塞鸭塞鸡） |
| **Port 9494** | 9494 端口 | Quack server 默认端口；致敬 Netscape Navigator 1994 |
| **`quack_serve()`** | quack_serve 函数 | DuckDB SQL 函数，启动当前实例为 Quack server |
| **`ATTACH 'quack:host'`** | attach quack 语法 | 让一个 DuckDB 实例把另一个实例当远端 schema 挂载，之后像本地表一样查 |

---

*术语表持续更新。如有遗漏或译名争议，欢迎在文章评论区指出。*
