# 概念卡片 · Cloudflare × ClickHouse Mutex Contention

每张卡片可独立使用：技术面试速查、团队 onboarding、读书笔记复习。

---

## Card 01 · ClickHouse `MergeTree` 引擎

ClickHouse 的核心存储引擎家族。表按 **PARTITION BY** 子句分区，每个分区由多个 **part** 组成；每个 part 内的数据按主键排序、以 **granule** 为单位采样建立稀疏索引。新写入的 part 在后台被合并（merge）为更大的 part，所以叫"MergeTree"。**parts 是磁盘上真实存在的目录**，不是抽象单元。一个 part 数过万的表，意味着内存里要维护一个上万元素的 active parts list。

---

## Card 02 · Part vs Partition

容易混淆。**Partition** 是逻辑分组——对应 `PARTITION BY` 表达式的一个取值（例如 `2026-05-18`）。**Part** 是物理存储单元——一次 insert / 一次 merge 产生一个 part。同一个 partition 通常包含多个 part；后台 merge 会把它们合并成更少、更大的 part。**用户控制 partition 数，引擎控制 part 数**——但 partition 设计会显著影响 part 数的天花板。

---

## Card 03 · Sparse Primary Index

ClickHouse 不是 row-level index 而是 **granule-level**——每 8192 行索引一个 mark，索引存的是这一段的主键起始值。所以"主键查询"实际是先二分定位到 granule，再扫这块小范围。这种设计意味着主键列的**前缀 cardinality**直接决定查询效率——把 `namespace` 放在主键第一位是有道理的。

---

## Card 04 · `PARTITION BY (namespace, day)` 的隐含代价

把 `day` 改成 `(namespace, day)` 这一行 DDL 看起来无害，但它把 partition 总数从 *天数* 乘以 *namespace 数*。在 Cloudflare 的场景下：从大约 31 个 partition 暴涨到几千甚至上万个；每个 partition 至少有一个 part；merge 跟不上时还会更多。最终结果：**全表 active parts 从 30k 涨到 160k**。

---

## Card 05 · `filterPartsByPartition`

ClickHouse 查询规划阶段的核心函数：从全表 active parts 列表中筛选出"本次 query 实际需要扫描的那些"。它的复杂度本来是 O(N)（N = 全表 part 数），即使本次 query 只命中 0.1% 的 parts，**也要看完所有 N 个**才能确定。这是 Cloudflare 那篇博客里最核心的"看多少 vs 读多少"问题。

---

## Card 06 · `std::unique_lock` vs `std::shared_lock`

C++17 的并发原语。`unique_lock` 是独占——同一时刻只能有一个线程进入临界区。`shared_lock` 是共享——多个 reader 可以同时进入，但 writer 排他。两者搭配 `std::shared_mutex` 使用。**判定原则**：如果临界区**不写入**共享状态，就用 shared_lock；只要写入（哪怕只是 increment 计数器），就用 unique_lock。Cloudflare 这次的第一步优化是确认 query planner 是纯读，然后从 unique → shared。

---

## Card 07 · `trace_log` 的 CPU 模式 vs Real 模式

ClickHouse 内置的栈采样表。两种模式：

- **CPU 模式（默认）**：只在线程实际**占用 CPU** 的时候采样栈。看不见在等锁/等 IO/等条件变量的线程。
- **Real 模式**：定时给**所有线程**采样，不管它当时在干什么。能看到"等待"。

**经验法则**：当业务感知慢、但 CPU profile 找不到大头时，先切到 Real 模式，看看是不是在等待。

---

## Card 08 · 锁争用（Lock Contention）

多个线程在同一把锁上排队时发生的现象。**典型症状**：

- CPU 利用率不高（线程都在 sleep）
- 但吞吐量上不去
- 响应时间随并发数线性甚至超线性增长
- p99 / p999 比 p50 差异巨大

**诊断工具**：`perf lock`、`mutrace`、Real-mode profiler、`/proc/<pid>/status` 看 `voluntary_ctxt_switches`。

---

## Card 09 · "把复制搬到写路径"模式

读多写少场景的经典优化。原始版本：每个 reader 进入临界区都要 deep-copy 一份大数据结构。优化版本：维护一份**全局 cached shared copy**，所有 reader 直接读这个 cached 版本；只在 writer 修改时重新生成 cached copy。本质上把"每次读复制"的代价分摊到**写次数**上——而写比读频率低几个数量级。

**思想同源**：Linux 内核的 RCU、数据库的 MVCC snapshot、分布式系统的 epoch-based reclamation。

---

## Card 10 · Binary Search 在 OLAP planner 里的应用

观察：ClickHouse 的 parts 列表本来就**按分区键有序**。如果分区键的第一个字段恰好是 query 的过滤维度（这里是 `namespace`），那么：

1. 用 binary search 在 O(log N) 时间内找到该 namespace 的起始位置
2. 在该位置往后线性扫描直到 namespace 改变
3. 只对这一小段做后续 filter

**复杂度变化**：O(N) → O(log N + K)，N 是总 part 数、K 是命中 namespace 的 part 数。在 N=160k、K=数百时，提升一个数量级。

---

## Card 11 · "查询规划"vs"查询执行"

OLAP 引擎里两个截然不同的阶段：

- **规划（Planning）**：决定要读哪些 parts、用什么算法、走什么 pipeline。CPU/内存代价低，但临界区多。
- **执行（Execution）**：实际读数据、解压、向量化计算、聚合。CPU/IO 代价高，但通常无锁。

Cloudflare 这次的问题完全在 **planning 阶段**——执行阶段的 I/O、行数全程正常。这也是为什么"标准 SRE 指标"看起来都健康。

---

## Card 12 · "状态空间" vs "工作负载"指标

观察集群健康度的两类指标：

- **工作负载指标**：QPS、p99 latency、bytes-in-per-second——直接反映用户行为
- **状态空间指标**：parts 总数、dead tuples、lock 等待队列长度——反映**集群积累状态**

Cloudflare 这次的转折点就是把"parts 总数"加进了 dashboard。**经验法则**：每一类持续增长的全局元数据，都该有一个监控仪表盘——因为这类指标的代价**不和当前 QPS 成正比，而和历史累积成正比**。

---

## Card 13 · 上游贡献的"反 use case"姿态

Cloudflare 的 PR #85535 描述里有一段非常聪明的论证：作者先承认自己的 use case（10 万 parts）**不符合 ClickHouse 推荐指南**，然后论证这个改动**对符合指南的常规表也没有任何负面影响**。这种姿态——"我承认我的场景反常规，但我的修复对你的常规场景无害"——是大型 OSS 项目里**让维护者放心 merge 的最佳实践**。

---

## Card 14 · ZooKeeper 在 ClickHouse 中的角色

ClickHouse 的 **ReplicatedMergeTree** 引擎用 ZooKeeper 存储**每张表所有 parts 的元数据**——part 的哈希、副本位置、merge 状态、删除标记。每个 part 对应若干 ZK 节点。**part 数 ↔ ZK 节点数线性相关**——160k parts 对一个有几十张这种规模表的集群来说，可能意味着 **几百万到一千万个 ZK 节点**，存储量逼近 100 GB。这是 Cloudflare 这次没有解决但已经在伏笔的下一个炸弹。

---

## Card 15 · "Leaky Abstraction"在数据库工程里的具象

抽象泄漏（Leaky Abstraction）是 Joel Spolsky 提出的概念——所有非平凡的抽象，在某种程度上都会泄漏。在数据库工程里它的最常见形式：**表设计层的决策（分区键、主键、TTL）通过引擎实现层的代码路径（锁、缓存、容器）暗中传导成本**。Cloudflare 这次的故事就是抽象泄漏的标本：分区键决策本来"和性能无关"，但它通过 `MergeTreeData::mutex` 泄漏到了所有 SELECT 查询的延迟里。
